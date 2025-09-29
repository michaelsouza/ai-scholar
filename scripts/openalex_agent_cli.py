#!/usr/bin/env python3
"""Run the OpenAlex research orchestrator from the command line."""

from __future__ import annotations

import argparse
import json
import os
import sys
from contextlib import nullcontext
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:  # pragma: no cover - convenience import for CLI usage
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - fallback when dotenv is absent
    def load_dotenv(*args, **kwargs):
        return False

try:  # pragma: no cover - optional rich integration
    from rich import box
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except ImportError:  # pragma: no cover - graceful fallback when rich is unavailable
    Console = None  # type: ignore[assignment]
    Panel = None  # type: ignore[assignment]
    Table = None  # type: ignore[assignment]
    box = None  # type: ignore[assignment]

from codes.agent_openalex import (
    CachedOpenAlexService,
    JsonFileCache,
    LLMThemeRelevanceAgent,
    OpenAlexHttpClient,
    OpenAlexResearchOrchestrator,
    SimpleThemeRelevanceAgent,
    WorkDecision,
    Work,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect references/citations from OpenAlex and score them against a theme.",
    )
    parser.add_argument("seed", help="OpenAlex work identifier (e.g. W2002097905 or doi:...)")
    parser.add_argument("theme", help="Research theme used to evaluate related works")
    parser.add_argument(
        "--cache",
        default="./data/openalex_cache.json",
        help="Path to JSON cache file (default: %(default)s)",
    )
    parser.add_argument(
        "--mailto",
        default=None,
        help="Email reported to OpenAlex (defaults to OPENALEX_MAILTO env or michael@ufc.br)",
    )
    parser.add_argument(
        "--max-citations",
        type=int,
        default=50,
        help="Maximum number of citing works to retrieve (default: %(default)s)",
    )
    parser.add_argument(
        "--citation-page-size",
        type=int,
        default=50,
        help="Results per request when pulling citations (default: %(default)s)",
    )
    parser.add_argument(
        "--llm-model",
        default=None,
        help="OpenRouter model identifier used for relevance decisions (defaults to OPENROUTER_MODEL)",
    )
    parser.add_argument(
        "--llm-temperature",
        type=float,
        default=0.0,
        help="Temperature for the LLM classifier (default: %(default)s)",
    )
    parser.add_argument(
        "--llm-max-retries",
        type=int,
        default=2,
        help="Retries for LLM classification before falling back (default: %(default)s)",
    )
    parser.add_argument(
        "--llm-app-url",
        default=os.getenv("OPENROUTER_APP_URL"),
        help="Optional Referer header reported to OpenRouter",
    )
    parser.add_argument(
        "--llm-app-title",
        default=os.getenv("OPENROUTER_APP_TITLE"),
        help="Optional X-Title header reported to OpenRouter",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM relevance classifier and use heuristic matching",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    load_dotenv()

    console = Console() if Console else None

    client = OpenAlexHttpClient(
        mailto=args.mailto,
        max_citations=args.max_citations,
        citation_page_size=args.citation_page_size,
    )
    cache = JsonFileCache(Path(args.cache))
    service = CachedOpenAlexService(client=client, cache=cache)
    interaction_logs: List[Tuple[Work, List[Dict[str, str]], str]] = []
    status_ref: Dict[str, object | None] = {"obj": None}
    llm_counter: Dict[str, int] = {"count": 0}
    model_label_holder: Dict[str, str | None] = {"value": None}

    def _shorten(text: str, limit: int = 600) -> str:
        text = text.strip()
        if len(text) <= limit:
            return text
        return text[: limit - 1] + "…"

    def interaction_logger(work: Work, messages: List[Dict[str, str]], response: Dict[str, object]) -> None:
        llm_counter["count"] += 1

        response_text = json.dumps(response, indent=2, ensure_ascii=False)
        interaction_logs.append((work, messages, response_text))

        request_preview = [f"[{msg.get('role', '?')}] {_shorten(msg.get('content', ''))}" for msg in messages]
        response_preview = _shorten(
            response.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            if isinstance(response, dict)
            else response_text,
            400,
        )

        label = model_label_holder["value"] or "LLM"

        if console:
            console.log(f"LLM request #{llm_counter['count']} for [bold]{work.openalex_id}[/] · {work.title}")
            for preview in request_preview:
                console.log(f"    {preview}")
            console.log(f"    [green]Response:[/] {response_preview}")
        else:
            print(f"LLM request #{llm_counter['count']} for {work.openalex_id} · {work.title}")
            for preview in request_preview:
                print(f"    {preview}")
            print(f"    Response: {response_preview}")

        status = status_ref.get("obj")
        if status is not None:
            try:
                status.update(
                    f"[cyan]{label}: processed {llm_counter['count']} works (last: {work.openalex_id})[/]"
                )
            except Exception:  # pragma: no cover - status updates are best-effort only
                pass

    relevance_agent, agent_message, model_used = _resolve_relevance_agent(
        args,
        interaction_logger,
    )
    model_label_holder["value"] = (
        model_used
        or args.llm_model
        or os.getenv("OPENROUTER_MODEL")
        or "LLM classifier"
    )
    orchestrator = OpenAlexResearchOrchestrator(service=service, relevance_agent=relevance_agent)

    _emit(console, agent_message, style="bold green" if model_used else "bold yellow")

    status_ctx = nullcontext()
    if model_used:
        if console:
            status_ctx = console.status(
                f"[cyan]Classifying works with LLM model '{model_used}'[/]"
            )
        else:
            print(f"Classifying works with LLM model '{model_used}'...")

    with status_ctx as status_obj:
        status_ref["obj"] = status_obj
        result = orchestrator.run(seed_id=args.seed, theme=args.theme)
    status_ref["obj"] = None

    _render_summary(console, result)
    _render_interactions(console, interaction_logs)
    _render_decisions(console, "Accepted Works", result.accepted)
    _render_decisions(console, "Rejected Works", result.rejected)
    _render_graph(console, result.graph)


def _resolve_relevance_agent(
    args: argparse.Namespace,
    interaction_logger: Callable[[Work, List[Dict[str, str]], Dict[str, object]], None] | None,
) -> Tuple[SimpleThemeRelevanceAgent, str, str | None]:
    if args.no_llm:
        return (
            SimpleThemeRelevanceAgent(),
            "Using heuristic relevance agent (LLM disabled)",
            None,
        )

    model = args.llm_model or os.getenv("OPENROUTER_MODEL")
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key or not model:
        sys.stderr.write(
            "[warn] LLM classification requested but OPENROUTER_API_KEY/OPENROUTER_MODEL are not set. "
            "Falling back to heuristic relevance agent.\n"
        )
        return (
            SimpleThemeRelevanceAgent(),
            "Using heuristic relevance agent (missing OpenRouter configuration)",
            None,
        )

    try:
        agent = LLMThemeRelevanceAgent(
            model=model,
            api_key=api_key,
            temperature=args.llm_temperature,
            max_retries=args.llm_max_retries,
            app_url=args.llm_app_url,
            app_title=args.llm_app_title,
            interaction_logger=interaction_logger,
        )
        message = f"Using LLM relevance agent with model '{model}' (temperature={args.llm_temperature})"
        return agent, message, model
    except ValueError as exc:
        sys.stderr.write(f"[warn] {exc}. Falling back to heuristic relevance agent.\n")
        return (
            SimpleThemeRelevanceAgent(),
            "Using heuristic relevance agent (invalid LLM configuration)",
            None,
        )


def _emit(console: Console | None, message: str, *, style: str | None = None) -> None:
    if console:
        console.print(message, style=style)
    else:
        print(message)


def _render_summary(console: Console | None, result) -> None:
    summary_text = (
        f"Seed: {result.seed.title} ({result.seed.openalex_id})\n"
        f"Theme: {result.theme}\n"
        f"Accepted: {len(result.accepted)} | Rejected: {len(result.rejected)}"
    )
    if console and Panel:
        panel = Panel(
            summary_text,
            title="OpenAlex Research Summary",
            border_style="bright_blue",
            expand=False,
        )
        console.print(panel)
        console.print()
    else:
        print(summary_text)
        print()


def _render_interactions(
    console: Console | None,
    interactions: Iterable[Tuple[Work, List[Dict[str, str]], str]],
) -> None:
    interactions = list(interactions)
    if not interactions:
        return

    if console and Panel and Table and box:
        console.print(Panel("LLM request/response log", border_style="cyan", expand=False))
        for work, messages, response_content in interactions:
            request_table = Table(
                title=f"Request · {work.openalex_id}",
                box=box.MINIMAL_HEAVY_HEAD,
                show_lines=False,
            )
            request_table.add_column("Role", style="cyan", no_wrap=True)
            request_table.add_column("Content", style="white")
            for message in messages:
                role = message.get("role", "?")
                content = message.get("content", "")
                request_table.add_row(role, content)

            response_panel = Panel(
                response_content,
                title=f"Response · {work.openalex_id}",
                border_style="magenta",
            )

            console.print(request_table)
            console.print(response_panel)
            console.print()
    else:
        print("LLM interactions:")
        for work, messages, response_content in interactions:
            print(f"Work: {work.title} ({work.openalex_id})")
            print("  Request messages:")
            for message in messages:
                role = message.get("role", "?")
                content = message.get("content", "")
                print(f"    - {role}: {content}")
            print("  Response:")
            print(f"    {response_content}")
            print()


def _render_decisions(console: Console | None, title: str, decisions: Iterable[WorkDecision]) -> None:
    if console and Table and box:
        table = Table(title=title, box=box.SIMPLE_HEAVY)
        table.add_column("#", justify="right", style="cyan", no_wrap=True)
        table.add_column("Key", style="green", no_wrap=True)
        table.add_column("Verdict", style="magenta", no_wrap=True)
        table.add_column("Title", style="white")
        table.add_column("Justification", style="yellow", overflow="fold")
        for idx, decision in enumerate(decisions, start=1):
            table.add_row(
                str(idx),
                decision.graph_key,
                decision.verdict.upper(),
                decision.work.title,
                decision.justification,
            )
        if not table.rows:
            table.add_row("-", "-", "-", "-", "(none)")
        console.print(table)
        console.print()
    else:
        print(_format_decisions(title, decisions))
        print()


def _render_graph(console: Console | None, graph) -> None:
    if console and Table and box and Panel:
        table = Table(box=box.MINIMAL_HEAVY_HEAD)
        table.add_column("From", style="cyan", no_wrap=True)
        table.add_column("To", style="magenta", no_wrap=True)
        for src, dst in graph.edges:
            table.add_row(src, dst)
        panel = Panel.fit(table, title=f"Citation Graph (seed: {graph.seed_key})", border_style="bright_magenta")
        console.print(panel)
    else:
        print("Citation graph:")
        print(f"  Seed key: {graph.seed_key}")
        print(f"  Nodes: {len(graph.nodes)}")
        for edge in graph.edges:
            print(f"    {edge[0]} -> {edge[1]}")


def _format_decisions(title: str, decisions: Iterable[WorkDecision]) -> str:
    lines = [title]
    for idx, decision in enumerate(decisions, start=1):
        lines.append(
            f"  {idx:>2}. {decision.graph_key} | {decision.verdict.upper()} | "
            f"{decision.work.title}"
        )
        lines.append(f"       Justification: {decision.justification}")
    if len(lines) == 1:
        lines.append("  (none)")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
