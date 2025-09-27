"""Utility script for inspecting OpenRouter models by provider."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Iterable, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    import pandas as pd
except ImportError as exc:  # pragma: no cover - runtime dependency guard
    print("pandas is required. Install it with 'pip install pandas'.", file=sys.stderr)
    raise SystemExit(1) from exc

API_URL = "https://openrouter.ai/api/v1/models"
DEFAULT_PROVIDERS = [
    "openai",
    "x-ai",
    "anthropic",
    "google",
    "deepseek",
    # "z-ai",
    "qwen",
]


@dataclass
class ModelInfo:
    """Lightweight holder for the output we care about."""

    provider: str
    model_id: str
    prompt_price_per_million: Optional[Decimal]
    completion_price_per_million: Optional[Decimal]
    context_tokens: Optional[int]
    created_at: Optional[dt.datetime]
    supported_parameters: List[str] = field(default_factory=list)


def fetch_models(timeout: float = 10.0) -> List[dict]:
    """Retrieve the raw model listing from OpenRouter."""

    request = Request(API_URL, headers={"User-Agent": "ai-scholar-openrouter-script"})
    with urlopen(request, timeout=timeout) as response:  # noqa: S310
        payload = json.load(response)
    return payload.get("data", [])


def is_provider_match(model_id: str, provider_candidates: Iterable[str]) -> Optional[str]:
    """Return the matched provider slug if the model belongs to one of the targets."""

    if not model_id:
        return None

    provider = model_id.split("/", 1)[0].split(":", 1)[0].lower()
    return provider if provider in provider_candidates else None


def parse_price_per_million(value: Optional[str]) -> Optional[Decimal]:
    """Convert per-token pricing into a per-million-tokens figure."""

    if value in (None, ""):
        return None
    try:
        amount = Decimal(value)
    except InvalidOperation:
        return None

    per_million = amount * Decimal(1_000_000)
    return per_million.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def parse_created(timestamp: Optional[float]) -> Optional[dt.datetime]:
    """Convert a Unix timestamp to a UTC datetime."""

    if not timestamp:
        return None
    return dt.datetime.fromtimestamp(float(timestamp), tz=dt.timezone.utc)


def collect_models(
    raw_models: Iterable[dict],
    providers: Iterable[str],
    from_date: Optional[dt.datetime],
) -> List[ModelInfo]:
    """Filter and transform raw models into ModelInfo records."""

    print(f"from_date: {from_date}")
    provider_set = {provider.lower() for provider in providers}
    cut_off_timestamp = from_date.timestamp() if from_date else None
    collected: List[ModelInfo] = []

    for model in raw_models:
        model_id = model.get("id", "")
        provider = is_provider_match(model_id, provider_set)
        if not provider:
            continue

        created_at = parse_created(model.get("created"))
        if cut_off_timestamp is not None and created_at:
            if created_at.timestamp() < cut_off_timestamp:
                continue

        context_value = (
            model.get("top_provider", {}).get("context_length")
            or model.get("context_length")
        )
        try:
            context_tokens = int(context_value) if context_value is not None else None
        except (TypeError, ValueError):
            context_tokens = None

        pricing = model.get("pricing", {}) or {}
        supported_parameters = [
            parameter.lower()
            for parameter in model.get("supported_parameters") or []
        ]
        collect_entry = ModelInfo(
            provider=provider,
            model_id=model_id,
            prompt_price_per_million=parse_price_per_million(pricing.get("prompt")),
            completion_price_per_million=parse_price_per_million(
                pricing.get("completion")
            ),
            context_tokens=context_tokens,
            created_at=created_at,
            supported_parameters=supported_parameters,
        )
        collected.append(collect_entry)
    return collected


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    """Define and parse supported CLI arguments."""

    default_from_date = default_from_date_string()
    parser = argparse.ArgumentParser(
        description=(
            "Fetch OpenRouter model pricing and context metadata for specific providers."
        )
    )
    parser.add_argument(
        "--providers",
        nargs="+",
        default=DEFAULT_PROVIDERS,
        help=(
            "List of providers to include (defaults to openai, x-ai, anthropic, google, "
            "deepseek, z-ai, qwen)."
        ),
    )
    parser.add_argument(
        "--from-date",
        dest="from_date",
        default=default_from_date,
        help=(
            "Filter models released on or after this date (YYYY-MM-DD). "
            f"Default: {default_from_date}."
        ),
    )
    return parser.parse_args(argv)


def parse_from_date(value: Optional[str]) -> Optional[dt.datetime]:
    """Convert the user supplied date string into the start-of-day UTC timestamp."""

    if not value:
        return None
    try:
        date_value = dt.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:  # pragma: no cover - argparse already validates
        raise ValueError("Expected YYYY-MM-DD for --from-date") from exc
    return dt.datetime.combine(date_value, dt.time(0, 0), tzinfo=dt.timezone.utc)


def default_from_date_string() -> str:
    """Compute the default release date filter (approximately last six months)."""

    six_months_ago = dt.datetime.now(tz=dt.timezone.utc) - dt.timedelta(days=182)
    return six_months_ago.date().isoformat()


def render(models: Iterable[ModelInfo]) -> None:
    """Display the collected model data in a pandas table."""

    rows = list(models)
    if not rows:
        print("No models matched the provided filters.")
        return

    frame = pd.DataFrame(
        [
            {
                "provider": item.provider,
                "Model ID": item.model_id,
                "Prompt ($/1M)": item.prompt_price_per_million,
                "Completion ($/1M)": item.completion_price_per_million,
                "Context Tokens": item.context_tokens,
                "Released": item.created_at.date().isoformat()
                if item.created_at
                else "-",
                "Tools": has_parameter(item, "tools"),
                "Reasoning": has_parameter(item, "reasoning"),
                "_prompt_sort": float(item.prompt_price_per_million)
                if item.prompt_price_per_million is not None
                else float("inf"),
                "_completion_sort": float(item.completion_price_per_million)
                if item.completion_price_per_million is not None
                else float("inf"),
            }
            for item in rows
        ]
    )

    frame.sort_values(
        by=["provider", "_prompt_sort", "_completion_sort", "Model ID"],
        inplace=True,
        na_position="last",
        kind="mergesort",
    )

    frame.drop(columns=["provider", "_prompt_sort", "_completion_sort"], inplace=True)
    frame["Prompt ($/1M)"] = frame["Prompt ($/1M)"].apply(format_price)
    frame["Completion ($/1M)"] = frame["Completion ($/1M)"].apply(format_price)
    frame["Context Tokens"] = frame["Context Tokens"].apply(format_context)

    print(frame.to_string(index=False))
    output_file = export_to_excel(frame)
    if output_file:
        print(f"Saved snapshot to {output_file}")

def has_parameter(item: ModelInfo, parameter: str) -> bool:
    """Check whether a model supports a specific OpenAI-compatible parameter."""

    return parameter in item.supported_parameters


def format_price(value: Optional[Decimal]) -> str:
    """Format Decimal pricing values for display."""

    if value is None or pd.isna(value):
        return "-"
    return f"${value:.3f}"


def format_context(value: Optional[int]) -> str:
    """Render context sizes with thousands separators."""

    if value is None:
        return "-"
    return f"{value:,}"


def export_to_excel(frame: pd.DataFrame) -> Optional[str]:
    """Persist the rendered table to an Excel workbook with a dated filename."""

    today = dt.datetime.now(tz=dt.timezone.utc)
    filename = f"openrouter_models_{today.strftime('%Y%m%d')}.xlsx"
    try:
        frame.to_excel(filename, index=False)
        return filename
    except (ImportError, ValueError) as exc:
        print(
            "Failed to export Excel file. Install 'openpyxl' or 'xlsxwriter' to enable "
            f"Excel exports (error: {exc}).",
            file=sys.stderr,
        )
        return None


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)
    try:
        from_date = parse_from_date(args.from_date)
    except ValueError as err:
        print(err, file=sys.stderr)
        return 2

    try:
        raw_models = fetch_models()
    except (HTTPError, URLError, json.JSONDecodeError) as err:
        print(f"Failed to fetch models: {err}", file=sys.stderr)
        return 1

    models = collect_models(raw_models, args.providers, from_date)
    render(models)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
