#!/usr/bin/env python3
"""LangGraph ReAct agent that searches Semantic Scholar via OpenRouter."""

from __future__ import annotations

import argparse
import os
from typing import Any, Sequence

from dotenv import load_dotenv
import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from langchain.agents import Tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

console = Console()


try:
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - fallback for older LangChain installations
    from langchain.chat_models import ChatOpenAI  # type: ignore


SEMANTIC_SCHOLAR_AUTH_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper/search"
SEMANTIC_SCHOLAR_BULK_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
SEMANTIC_SCHOLAR_FIELDS = "title,authors.name,year,url,venue,abstract"


def ensure_env(var_name: str) -> str:
    """Return the value of a required environment variable or raise."""
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(
            f"Environment variable {var_name} is required."
        )
    return value


def _build_openrouter_llm(*, model: str, temperature: float, api_key: str, base_url: str) -> ChatOpenAI:
    """Instantiate a ChatOpenAI client configured for OpenRouter."""  # noqa: D401
    kwargs = {
        "model": model,
        "temperature": temperature,
        "openai_api_key": api_key,
    }
    try:
        return ChatOpenAI(base_url=base_url, **kwargs)
    except TypeError:
        kwargs["openai_api_base"] = base_url
        return ChatOpenAI(**kwargs)


def _format_paper(paper: dict, rank: int) -> str:
    title = paper.get("title") or "Untitled"
    url = paper.get("url") or ""
    year = paper.get("year")
    venue = paper.get("venue")
    authors = paper.get("authors") or []
    author_names = [a.get("name", "?") for a in authors]
    if len(author_names) > 5:
        author_display = ", ".join(author_names[:5]) + ", et al."
    else:
        author_display = ", ".join(author_names)

    header_parts = [f"{rank}. {title}"]
    if year:
        header_parts.append(f"({year})")
    if venue:
        header_parts.append(f"- {venue}")
    header = " ".join(header_parts)

    body = []
    if author_display:
        body.append(f"Authors: {author_display}")
    if url:
        body.append(f"Link: {url}")
    abstract = paper.get("abstract")
    if abstract:
        body.append(f"Abstract: {abstract[:500]}" + ("…" if len(abstract) > 500 else ""))

    return "\n".join([header] + body)


def _semantic_scholar_auth_search(query: str, *, api_key: str, limit: int) -> str:
    params = {
        "query": query,
        "limit": limit,
        "fields": SEMANTIC_SCHOLAR_FIELDS,
    }
    headers = {"x-api-key": api_key}

    try:
        response = requests.get(SEMANTIC_SCHOLAR_AUTH_ENDPOINT, params=params, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.HTTPError as err:
        return f"Semantic Scholar HTTP error: {err.response.status_code} {err.response.text}"
    except requests.RequestException as err:
        return f"Semantic Scholar request failed: {err}"

    payload = response.json()
    papers = payload.get("data") or []
    if not papers:
        return "Semantic Scholar returned no results."

    return "\n\n".join(_format_paper(paper, idx) for idx, paper in enumerate(papers[:limit], start=1))


def _semantic_scholar_unauth_search(query: str, *, limit: int) -> str:
    accumulated: list[dict] = []
    next_token: str | None = None

    while len(accumulated) < limit:
        page_size = max(1, min(limit - len(accumulated), 100))
        params = {
            "query": query,
            "fields": SEMANTIC_SCHOLAR_FIELDS,
            "limit": page_size,
        }
        if next_token:
            params["token"] = next_token

        try:
            response = requests.get(SEMANTIC_SCHOLAR_BULK_ENDPOINT, params=params, timeout=20)
        except requests.RequestException as err:
            return f"Semantic Scholar request failed: {err}"

        if response.status_code == 429:
            return (
                "Semantic Scholar rate limit hit (100 unauthenticated requests per 5 minutes). "
                "Please wait before trying again or supply SEMANTIC_SCHOLAR_API_KEY."
            )
        if response.status_code != 200:
            return f"Semantic Scholar error {response.status_code}: {response.text}"

        payload = response.json()
        batch = payload.get("data") or []
        accumulated.extend(batch)

        next_token = payload.get("token")
        if not next_token or not batch:
            break

    if not accumulated:
        return "Semantic Scholar returned no results."

    trimmed = accumulated[:limit]
    return "\n\n".join(_format_paper(paper, idx) for idx, paper in enumerate(trimmed, start=1))


def semantic_scholar_search(query: str, *, api_key: str | None, limit: int) -> str:
    if not query.strip():
        return "Semantic Scholar search requires a query."

    if api_key:
        return _semantic_scholar_auth_search(query, api_key=api_key, limit=limit)
    return _semantic_scholar_unauth_search(query, limit=limit)


def build_agent(
    model: str,
    temperature: float,
    *,
    api_key: str,
    base_url: str,
    semantic_scholar_key: str | None,
    limit: int,
) -> Any:
    """Construct a LangGraph ReAct agent configured with Semantic Scholar search."""


    def _search(query: str) -> str:
        console.print(Panel.fit(Text(query, style="bold"), title="Tool Call: Semantic Scholar Search", border_style="blue"))
        result = semantic_scholar_search(query, api_key=semantic_scholar_key, limit=limit)
        display = result if len(result) <= 1500 else result[:1500] + "… [truncated]"
        console.print(Panel.fit(display, title="Tool Result: Semantic Scholar Search", border_style="bright_blue"))
        return result

    tool = Tool(
        name="Semantic Scholar Search",
        func=_search,
        description=(
            "Use this when you need academic papers or bibliographic details from Semantic Scholar. "
            "Works with or without an API key; unauthenticated mode is limited to 100 requests per 5 minutes."
        ),
    )

    llm = _build_openrouter_llm(model=model, temperature=temperature, api_key=api_key, base_url=base_url)
    return create_react_agent(llm, tools=[tool])


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ask the agent to search Semantic Scholar for relevant papers.",
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Research question or keywords to search for",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENROUTER_MODEL", "x-ai/grok-4-fast:free"),
        help="Chat model to drive the agent (defaults to x-ai/grok-4-fast:free).",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature for the chat model.",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        help="Override the OpenRouter base URL if needed.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=int(os.getenv("SEMANTIC_SCHOLAR_LIMIT", "5")),
        help="Maximum number of papers to return (defaults to 5).",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    load_dotenv()
    args = parse_args(argv)
    query_text = " ".join(args.query).strip()

    if not query_text:
        query_text = input("Enter your paper search query: ").strip()
        if not query_text:
            console.print("[bold red]No query provided. Exiting.[/]")
            raise SystemExit(1)

    openrouter_key = ensure_env("OPENROUTER_API_KEY")
    semantic_scholar_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

    console.rule("Semantic Scholar Agent")
    console.print(Text(f"Query: {query_text}", style="bold cyan"))
    if not semantic_scholar_key:
        console.print(
            Text(
                "No SEMANTIC_SCHOLAR_API_KEY found. Falling back to unauthenticated mode "
                "(100 requests per 5 minutes limit).",
                style="yellow",
            )
        )

    agent = build_agent(
        model=args.model,
        temperature=args.temperature,
        api_key=openrouter_key,
        base_url=args.base_url,
        semantic_scholar_key=semantic_scholar_key,
        limit=max(1, args.limit),
    )

    instruction_parts = [
        "You are an academic research assistant.",
        "Always call the 'Semantic Scholar Search' tool at least once before finalizing an answer.",
        "Use the tool output to cite titles, venues, and publication years in the final response.",
        "Do not rely solely on prior knowledge; ground answers in retrieved papers.",
    ]
    if not semantic_scholar_key:
        instruction_parts.append(
            "Mention if results are limited due to unauthenticated access when relevant."
        )

    system_msg = SystemMessage(content=" ".join(instruction_parts))
    result = agent.invoke({"messages": [system_msg, HumanMessage(content=query_text)]})
    if isinstance(result, dict) and "messages" in result:
        messages: Any = result["messages"]
    else:
        messages = result

    if isinstance(messages, list) and messages:
        final_message = messages[-1]
        content = getattr(final_message, "content", str(final_message))
        if isinstance(content, list):
            content = "\n".join(
                chunk.get("text", str(chunk)) if isinstance(chunk, dict) else str(chunk)
                for chunk in content
            )
        console.print(Panel.fit(content, title="Agent Answer", border_style="green"))
    else:
        console.print(Panel.fit(str(result), title="Agent Output", border_style="yellow"))


if __name__ == "__main__":  # pragma: no cover
    main()
