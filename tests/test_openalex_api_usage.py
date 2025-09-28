import os
from typing import Any, Dict

import pytest
import requests


BASE_URL = "https://api.openalex.org"
DEFAULT_MAILTO = os.getenv("OPENALEX_MAILTO", "michael@ufc.br")
_TIMEOUT_SECONDS = 30


def _skip_from_response(response: requests.Response, context: str) -> None:
    detail = response.text[:200].strip()
    pytest.skip(f"OpenAlex {context} unavailable: {response.status_code} {detail}")


def _get(path: str, *, params: Dict[str, Any] | None = None, context: str) -> Dict[str, Any]:
    query = {"mailto": DEFAULT_MAILTO}
    if params:
        query.update(params)

    try:
        response = requests.get(
            f"{BASE_URL}{path}",
            params=query,
            timeout=_TIMEOUT_SECONDS,
        )
    except requests.exceptions.RequestException as exc:  # pragma: no cover - network dependent
        pytest.skip(f"OpenAlex request failed: {exc}")

    if response.status_code >= 500:
        _skip_from_response(response, context)

    if response.status_code == 429:
        _skip_from_response(response, f"rate limit during {context}")

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:  # pragma: no cover - network dependent
        pytest.skip(f"OpenAlex HTTP error for {context}: {exc}")

    return response.json()


@pytest.fixture(scope="module")
def openalex_enabled():
    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        pytest.skip("Live OpenAlex tests disabled")


@pytest.mark.usefixtures("openalex_enabled")
def test_openalex_keyword_search_returns_results():
    payload = _get(
        "/works",
        params={
            "filter": "title.search:machine learning",
            "per-page": 5,
            "sort": "cited_by_count:desc",
        },
        context="keyword search",
    )

    results = payload.get("results", [])
    assert results, "OpenAlex keyword search returned no results"
    titles = [work.get("title", "").lower() for work in results]
    assert any("machine" in title for title in titles)


@pytest.mark.usefixtures("openalex_enabled")
def test_openalex_work_includes_references_and_citations():
    work_id = "W2002097905"  # Moderately cited work with stable metadata
    payload = _get(f"/works/{work_id}", context="work lookup")

    work_identifier = payload.get("id", "")
    assert work_identifier.endswith(work_id)
    references = payload.get("referenced_works", [])
    assert isinstance(references, list)
    assert references, "Expected at least one referenced work"

    citations_payload = _get(
        "/works",
        params={"filter": f"cited_by:{work_id}", "per-page": 5},
        context="citations lookup",
    )
    cited_by = citations_payload.get("results", [])
    if not cited_by:
        meta_count = citations_payload.get("meta", {}).get("count")
        pytest.skip(
            "OpenAlex cited_by filter returned no citing works; "
            f"meta.count={meta_count}."
        )
    citing_titles = [item.get("title") for item in cited_by]
    assert any(citing_titles), "Citing works missing titles"


@pytest.mark.usefixtures("openalex_enabled")
def test_openalex_lookup_by_doi_returns_expected_paper():
    doi = "10.1016/j.patcog.2009.06.018"  # Matches work W2002097905
    payload = _get(f"/works/doi:{doi}", context="doi lookup")

    title = payload.get("title", "")
    assert title, "OpenAlex DOI lookup returned empty title"
    authors = [entry["author"]["display_name"] for entry in payload.get("authorships", [])]
    assert authors, "Expected at least one author in authorships"
    assert doi in payload.get("doi", "").lower(), "Returned record does not match expected DOI"


@pytest.mark.usefixtures("openalex_enabled")
def test_openalex_author_lookup_and_top_work_listing():
    search_payload = _get(
        "/authors",
        params={
            "filter": "display_name.search:Yoshua Bengio",
            "per-page": 5,
        },
        context="author search",
    )

    authors = search_payload.get("results", [])
    assert authors, "Author search returned no results"

    target = next(
        (author for author in authors if "yoshua bengio" in author["display_name"].lower()),
        None,
    )
    if not target:
        pytest.skip("Unable to locate Yoshua Bengio in OpenAlex author results")

    author_id = target["id"].split("/")[-1]
    works_payload = _get(
        "/works",
        params={
            "filter": f"authorships.author.id:{author_id}",
            "per-page": 5,
            "sort": "cited_by_count:desc",
        },
        context="author works lookup",
    )

    works = works_payload.get("results", [])
    assert works, "Expected works authored by Yoshua Bengio"
    assert all("title" in work for work in works)


@pytest.mark.usefixtures("openalex_enabled")
def test_openalex_select_fields_limits_payload():
    payload = _get(
        "/works",
        params={
            "filter": "title.search:graph neural networks",
            "select": "id,title,publication_date,cited_by_count",
            "per-page": 3,
        },
        context="field selection",
    )

    works = payload.get("results", [])
    assert works, "Expected results when selecting fields"

    allowed_keys = {"id", "title", "publication_date", "cited_by_count"}
    for work in works:
        work_keys = set(work.keys())
        assert work_keys <= allowed_keys, (
            "OpenAlex returned unexpected fields when select parameter was applied. "
            f"Unexpected keys: {sorted(work_keys - allowed_keys)}"
        )
        assert work.get("title")
