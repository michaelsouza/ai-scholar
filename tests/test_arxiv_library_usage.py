import itertools
import os

import pytest


arxiv = pytest.importorskip("arxiv")


def _collect_results(search: arxiv.Search, client: arxiv.Client, *, context: str, limit: int) -> list[arxiv.Result]:
    try:
        iterator = client.results(search)
        return list(itertools.islice(iterator, limit))
    except (arxiv.ArxivAPIError, ConnectionError, TimeoutError) as exc:  # pragma: no cover - network dependent
        pytest.skip(f"arXiv API unavailable during {context}: {exc}")
    except Exception as exc:  # pragma: no cover - network dependent
        if "503" in str(exc) or "timed out" in str(exc).lower():
            pytest.skip(f"arXiv API transient error during {context}: {exc}")
        raise


@pytest.fixture(scope="module")
def arxiv_client():
    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        pytest.skip("Live arXiv tests disabled")

    # The library does not expose a user-agent hook; rely on defaults and
    # respect rate limits via conservative pagination and retry settings.
    return arxiv.Client(
        page_size=100,
        delay_seconds=0.5,
        num_retries=1,
    )


def test_arxiv_keyword_search_returns_results(arxiv_client: arxiv.Client):
    search = arxiv.Search(
        query="ti:\"graph neural networks\"",
        max_results=3,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    results = _collect_results(search, arxiv_client, context="keyword search", limit=3)
    if not results:
        pytest.skip("arXiv keyword search returned no results")

    titles = [result.title.lower() for result in results]
    assert any("graph" in title for title in titles)


def test_arxiv_fetch_specific_work_by_id(arxiv_client: arxiv.Client):
    # Seminal CNN paper with stable metadata
    target_id = "1706.03762"
    search = arxiv.Search(id_list=[target_id])
    results = _collect_results(search, arxiv_client, context="id lookup", limit=1)
    if not results:
        pytest.skip(f"arXiv did not return result for id {target_id}")

    paper = results[0]
    assert target_id in paper.get_short_id()
    assert "attention" in paper.title.lower()
    assert paper.summary  # Abstract

    # Note: The arxiv API itself does not provide citation/reference counts.


def test_arxiv_returns_authors_for_author_query(arxiv_client: arxiv.Client):
    search = arxiv.Search(
        query='au:"Michael I Jordan"',
        max_results=5,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )
    results = _collect_results(search, arxiv_client, context="author query", limit=5)
    if not results:
        pytest.skip("arXiv author query returned no results")

    assert any(
        any("michael" in author.name.lower() and "jordan" in author.name.lower() for author in result.authors)
        for result in results
    ), "Expected at least one result authored by Michael I. Jordan"


def test_arxiv_result_contains_pdf_url(arxiv_client: arxiv.Client):
    search = arxiv.Search(
        query="cat:cs.LG",
        max_results=1,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )
    results = _collect_results(search, arxiv_client, context="pdf url lookup", limit=1)
    if not results:
        pytest.skip("arXiv category query returned no results")

    paper = results[0]
    pdf_url = paper.pdf_url
    assert pdf_url and pdf_url.startswith("http")
