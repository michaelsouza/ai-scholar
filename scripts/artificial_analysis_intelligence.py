"""Fetch intelligence benchmarks for LLMs from Artificial Analysis."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from dataclasses import dataclass
from typing import Iterable, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    import pandas as pd
except ImportError as exc:  # pragma: no cover - runtime dependency guard
    print("pandas is required. Install it with 'pip install pandas'.", file=sys.stderr)
    raise SystemExit(1) from exc

try:  # pragma: no cover - optional convenience
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None

if load_dotenv:  # pragma: no cover - depends on environment
    load_dotenv()

API_URL = "https://artificialanalysis.ai/api/v2/data/llms/models"
API_KEY_ENV = "ARTIFICIAL_ANALYSIS_API_KEY"
DEFAULT_TOP = 25

EVALUATION_FIELDS = {
    "Intelligence Index": "artificial_analysis_intelligence_index",
    "Coding Index": "artificial_analysis_coding_index",
    "Math Index": "artificial_analysis_math_index",
    "MMLU Pro": "mmlu_pro",
    "GPQA": "gpqa",
    "HLE": "hle",
    "LiveCodeBench": "livecodebench",
    "SciCode": "scicode",
    "Math 500": "math_500",
    "AIME": "aime",
}

@dataclass
class ModelBenchmarks:
    """Structured benchmark view for a single model."""

    model_id: str
    name: str
    creator: Optional[str]
    evaluations: dict
    output_tokens_per_second: Optional[float]
    time_to_first_token: Optional[float]
    time_to_first_answer: Optional[float]


def fetch_model_data(api_key: str, timeout: float = 10.0) -> List[dict]:
    """Call the Artificial Analysis API and return raw model payloads."""

    headers = {
        "User-Agent": "ai-scholar-artificial-analysis-script",
        "x-api-key": api_key,
    }
    request = Request(API_URL, headers=headers)
    with urlopen(request, timeout=timeout) as response:  # noqa: S310
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise ValueError("Unexpected API response shape")
    data = payload.get("data")
    if not isinstance(data, list):
        raise ValueError("API response missing 'data' list")
    return data

def collect_benchmarks(raw_models: Iterable[dict]) -> List[ModelBenchmarks]:
    """Transform raw API records into structured benchmark objects."""

    collected: List[ModelBenchmarks] = []
    for model in raw_models:
        evaluations = model.get("evaluations") or {}
        creator = (model.get("model_creator") or {}).get("name")
        collected.append(
            ModelBenchmarks(
                model_id=model.get("id", ""),
                name=model.get("name") or model.get("slug") or model.get("id", ""),
                creator=creator,
                evaluations=evaluations,
                output_tokens_per_second=as_float(model.get("median_output_tokens_per_second")),
                time_to_first_token=as_float(model.get("median_time_to_first_token_seconds")),
                time_to_first_answer=as_float(model.get("median_time_to_first_answer_token")),
            )
        )
    return collected


def as_float(value: Optional[float]) -> Optional[float]:
    """Coerce a value to float, returning None when not possible."""

    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    """CLI argument parsing."""

    parser = argparse.ArgumentParser(
        description=(
            "Retrieve Artificial Analysis intelligence benchmarks for LLMs and export to Excel."
        )
    )
    parser.add_argument(
        "--top",
        type=positive_int,
        default=DEFAULT_TOP,
        help=f"Limit output to the top N models by intelligence index (default: {DEFAULT_TOP}).",
    )
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="Ignore the --top limit and include every model in the export.",
    )
    return parser.parse_args(argv)


def positive_int(value: str) -> int:
    """Validate that an argument can be parsed as a positive integer."""

    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Value must be an integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("Value must be greater than zero")
    return parsed


def build_frame(models: Iterable[ModelBenchmarks]) -> pd.DataFrame:
    """Convert structured benchmarks into a pandas DataFrame."""

    rows = []
    for item in models:
        evaluations = item.evaluations or {}
        row = {
            "_Model ID": item.model_id,
            "Name": item.name,
            "Creator": item.creator or "-",
            "Output TPS": item.output_tokens_per_second,
            "TTFT (s)": item.time_to_first_token,
            "TTFA (s)": item.time_to_first_answer,
        }
        for column, key in EVALUATION_FIELDS.items():
            row[column] = as_float(evaluations.get(key))
        rows.append(row)

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame

    if "Intelligence Index" in frame:
        frame.sort_values(
            by=["Intelligence Index", "_Model ID"],
            ascending=[False, True],
            na_position="last",
            inplace=True,
        )
    if "_Model ID" in frame:
        frame.drop(columns=["_Model ID"], inplace=True)
    return frame


def apply_formatting(frame: pd.DataFrame) -> pd.DataFrame:
    """Pretty-print selected columns while keeping numeric data for export."""

    formatted = frame.copy()
    score_order = ["Intelligence Index"] + [
        col for col in EVALUATION_FIELDS.keys() if col != "Intelligence Index"
    ]
    score_columns = [col for col in score_order if col in formatted.columns]
    for column in score_columns:
        if column in formatted:
            formatted[column] = formatted[column].apply(format_score)

    for column in ["Output TPS", "TTFT (s)", "TTFA (s)"]:
        if column in formatted:
            formatted[column] = formatted[column].apply(format_speed)

    return formatted


def format_score(value: Optional[float]) -> str:
    """Format benchmark scores with one decimal place when available."""

    if value is None or (isinstance(value, float) and pd.isna(value)) or value < 0:
        return "-"
    return f"{value:.1f}"


def format_speed(value: Optional[float]) -> str:
    """Format float metrics with two decimal places."""

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "-"
    return f"{value:.2f}"


def export_to_excel(frame: pd.DataFrame) -> Optional[str]:
    """Persist the numeric DataFrame to an Excel workbook with a dated filename."""

    today = dt.datetime.now(tz=dt.timezone.utc)
    filename = f"artificial_analysis_llm_benchmarks_{today.strftime('%Y%m%d')}.xlsx"
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


def ensure_api_key() -> str:
    """Retrieve the API key from environment variables."""

    api_key = os.getenv(API_KEY_ENV)
    if not api_key:
        print(
            "ARTIFICIAL_ANALYSIS_API_KEY is missing. Set it in your environment or .env.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return api_key


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = parse_args(argv)
    api_key = ensure_api_key()

    try:
        raw_models = fetch_model_data(api_key)
    except (HTTPError, URLError, json.JSONDecodeError, ValueError) as err:
        print(f"Failed to fetch Artificial Analysis data: {err}", file=sys.stderr)
        return 1

    models = collect_benchmarks(raw_models)
    frame = build_frame(models)

    if frame.empty:
        print("No benchmark data returned by Artificial Analysis.")
        return 0

    if args.include_all:
        printable_frame = frame.copy()
    else:
        printable_frame = frame.head(args.top).copy()

    formatted = apply_formatting(printable_frame)
    print(formatted.to_string(index=False))

    export_frame = frame.copy() if args.include_all else frame.head(args.top).copy()
    output_file = export_to_excel(export_frame)
    if output_file:
        print(f"Saved snapshot to {output_file}")
        print("Attribution: https://artificialanalysis.ai/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
