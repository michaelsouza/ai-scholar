#!/usr/bin/env python3
"""Command-line interface for the dual-agent Semantic Scholar workflow."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Sequence

from dotenv import load_dotenv
from rich.console import Console
from rich.text import Text

from semantic_scholar import (
    ClassificationAgent,
    OrchestratorConfig,
    PaperDatabase,
    QueryAgent,
    QueryAgentConfig,
    SemanticScholarClient,
    SemanticScholarOrchestrator,
)


console = Console()


def ensure_env(var_name: str) -> str:
    """Return an environment variable or exit with a helpful error."""

    value = os.getenv(var_name)
    if not value:
        console.print(f"[bold red]Environment variable {var_name} is required.[/]")
        raise SystemExit(1)
    return value


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Iteratively search Semantic Scholar and classify relevance of papers.",
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Initial research question or keywords to seed the search.",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENROUTER_MODEL", "x-ai/grok-4-fast:free"),
        help="OpenRouter model for the query agent (default: x-ai/grok-4-fast:free).",
    )
    parser.add_argument(
        "--classifier-model",
        default=os.getenv("OPENROUTER_CLASSIFIER_MODEL"),
        help="Optional override model for the classification agent (defaults to --model).",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=float(os.getenv("OPENROUTER_TEMPERATURE", "0.0")),
        help="Sampling temperature for the query agent (default: 0.0).",
    )
    parser.add_argument(
        "--classifier-temperature",
        type=float,
        default=float(os.getenv("CLASSIFIER_TEMPERATURE", "0.0")),
        help="Sampling temperature for the classifier agent (default: 0.0).",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        help="Base URL for the OpenRouter API.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=int(os.getenv("SEMANTIC_SCHOLAR_LIMIT", "5")),
        help="Maximum number of papers to fetch per query (default: 5).",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=int(os.getenv("SEMANTIC_SCHOLAR_MAX_ITERATIONS", "3")),
        help="Maximum number of query refinement iterations (default: 3).",
    )
    parser.add_argument(
        "--db-path",
        default=os.getenv("SEMANTIC_SCHOLAR_DB_PATH", "data/search_results.json"),
        help="Path to the JSON file for storing results.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    load_dotenv()
    args = parse_args(argv)

    initial_query = " ".join(args.query).strip()
    if not initial_query:
        initial_query = input("Enter your paper search query: ").strip()
    if not initial_query:
        console.print("[bold red]No query provided. Exiting.[/]")
        raise SystemExit(1)

    openrouter_key = ensure_env("OPENROUTER_API_KEY")
    semantic_scholar_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

    console.rule("Semantic Scholar Agent")
    console.print(Text(f"Initial query: {initial_query}", style="bold cyan"))
    if not semantic_scholar_key:
        console.print(
            Text(
                "No SEMANTIC_SCHOLAR_API_KEY found. Using unauthenticated mode (100 requests per 5 minutes).",
                style="yellow",
            )
        )

    client = SemanticScholarClient(api_key=semantic_scholar_key, default_limit=max(1, args.limit))

    query_config = QueryAgentConfig(
        model=args.model,
        temperature=args.temperature,
        api_key=openrouter_key,
        base_url=args.base_url,
        result_limit=max(1, args.limit),
    )
    query_agent = QueryAgent(config=query_config, client=client, console=console)

    classifier_model = args.classifier_model or args.model
    classifier = ClassificationAgent(
        model=classifier_model,
        api_key=openrouter_key,
        base_url=args.base_url,
        temperature=args.classifier_temperature,
        console=console,
    )

    db_path = Path(args.db_path)
    database = PaperDatabase(db_path)

    orchestrator = SemanticScholarOrchestrator(
        query_agent=query_agent,
        classifier=classifier,
        database=database,
        console=console,
        config=OrchestratorConfig(max_iterations=max(1, args.iterations)),
    )
    orchestrator.run(initial_query)


if __name__ == "__main__":  # pragma: no cover
    main()
