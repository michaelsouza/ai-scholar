"""Optional live service checks for Semantic Scholar and SerpAPI."""

from __future__ import annotations

import os
from typing import Dict

import pytest
import requests


LIVE_TEST_ENV = "RUN_LIVE_API_TESTS"


def _should_run_live_tests() -> bool:
    return os.getenv(LIVE_TEST_ENV) == "1"


live_test = pytest.mark.skipif(
    not _should_run_live_tests(),
    reason=f"Set {LIVE_TEST_ENV}=1 to run live API checks.",
)


@live_test
def test_semantic_scholar_service_online() -> None:
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params: Dict[str, str] = {
        "query": "machine learning",
        "limit": "1",
        "fields": "paperId,title",
    }
    headers: Dict[str, str] = {}

    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key

    response = requests.get(url, params=params, headers=headers, timeout=30)
    if response.status_code == 429:
        pytest.skip("Semantic Scholar rate limit hit (429). Try with an API key or later.")

    response.raise_for_status()
    data = response.json()
    assert isinstance(data.get("data"), list), "Semantic Scholar response missing data list"
    assert data.get("data"), "Semantic Scholar returned no results"


@live_test
def test_serpapi_google_scholar_online() -> None:
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        pytest.skip("SERPAPI_API_KEY not configured")

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_scholar",
        "q": "machine learning",
        "num": "1",
        "api_key": api_key,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    if payload.get("error"):
        pytest.fail(f"SerpAPI reported error: {payload['error']}")

    organic = payload.get("organic_results")
    assert isinstance(organic, list), "SerpAPI response missing organic_results list"
    assert organic, "SerpAPI returned no results"
