import datetime
import os
from typing import List

import pytest

from agents.semantic_scholar.google_scholar import (
    GoogleScholarClient,
    GoogleScholarError,
)
from agents.semantic_scholar.search import PaperRecord


def _require_serpapi_key() -> str:
    key = os.getenv("SERPAPI_API_KEY")
    if not key:
        pytest.skip("SERPAPI_API_KEY not configured; skipping live Google Scholar tests")
    return key


def _run_search(client: GoogleScholarClient, query: str, *, limit: int, context: str) -> List[PaperRecord]:
    try:
        results = client.search(query, limit=limit)
    except GoogleScholarError as exc:
        message = str(exc)
        lower_message = message.lower()
        if "429" in message or "rate limit" in lower_message or "insufficient" in lower_message:
            pytest.skip(f"Google Scholar API rate limited during {context}: {message}")
        if "temporary" in lower_message or "timeout" in lower_message:
            pytest.skip(f"Google Scholar API unavailable during {context}: {message}")
        raise
    return results


@pytest.fixture(scope="module")
def google_scholar_client() -> GoogleScholarClient:
    key = _require_serpapi_key()
    return GoogleScholarClient(api_key=key, timeout=30, default_limit=5)


@pytest.mark.usefixtures("google_scholar_client")
def test_google_scholar_search_returns_results(google_scholar_client: GoogleScholarClient):
    query = "graph neural networks"
    papers = _run_search(
        google_scholar_client,
        query,
        limit=5,
        context="general search",
    )
    if not papers:
        pytest.skip("Google Scholar returned no results for the general search query")

    for paper in papers:
        assert paper.source == "google_scholar"
        assert paper.title
        assert paper.source_query == query


@pytest.mark.usefixtures("google_scholar_client")
def test_google_scholar_respects_limit(google_scholar_client: GoogleScholarClient):
    papers = _run_search(
        google_scholar_client,
        "reinforcement learning robotics",
        limit=2,
        context="limit enforcement",
    )
    assert 0 < len(papers) <= 2


@pytest.mark.usefixtures("google_scholar_client")
def test_google_scholar_provides_reasonable_years(google_scholar_client: GoogleScholarClient):
    current_year = datetime.date.today().year
    papers = _run_search(
        google_scholar_client,
        "federated learning privacy",
        limit=5,
        context="year parsing",
    )
    if not papers:
        pytest.skip("Google Scholar returned no results for the year parsing query")

    # Validate at least one paper has a plausible publication year.
    for paper in papers:
        if paper.year is None:
            continue
        assert 1900 <= paper.year <= current_year
        break
    else:
        pytest.skip("No Google Scholar results included a publication year to validate")


def test_google_scholar_requires_api_key():
    client = GoogleScholarClient(api_key=None)
    with pytest.raises(GoogleScholarError) as excinfo:
        client.search("graph neural networks")
    assert "requires a SERPAPI key" in str(excinfo.value)
