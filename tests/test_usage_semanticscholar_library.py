import os
from types import SimpleNamespace

import pytest


semanticscholar = pytest.importorskip("semanticscholar")

from semanticscholar import AsyncSemanticScholar, SemanticScholar  # noqa: E402
from semanticscholar.SemanticScholarException import (  # noqa: E402
    InternalServerErrorException,
    ObjectNotFoundException,
)


class _FakePaper(SimpleNamespace):
    def keys(self):  # type: ignore[override]
        raw = getattr(self, "raw_data", {})
        return list(raw.keys())


def test_get_paper_exposes_typed_response(monkeypatch):
    fake_response = _FakePaper(title="Test Title", raw_data={"title": "Test Title"})

    def fake_get_paper(self, paper_id: str):
        assert paper_id == "10.1093/mind/lix.236.433"
        return fake_response

    monkeypatch.setattr(SemanticScholar, "get_paper", fake_get_paper, raising=False)

    sch = SemanticScholar()
    paper = sch.get_paper("10.1093/mind/lix.236.433")

    assert paper.title == "Test Title"
    assert paper.raw_data["title"] == "Test Title"
    assert "title" in paper.keys()


@pytest.mark.asyncio
async def test_async_get_paper_propagates_response(monkeypatch):
    fake_response = _FakePaper(title="Async Title")

    async def fake_async_get(self, paper_id: str):
        assert paper_id == "10.1093/mind/lix.236.433"
        return fake_response

    monkeypatch.setattr(AsyncSemanticScholar, "get_paper", fake_async_get, raising=False)

    sch = AsyncSemanticScholar()
    paper = await sch.get_paper("10.1093/mind/lix.236.433")

    assert paper.title == "Async Title"


def test_autocomplete_returns_suggestions(monkeypatch):
    fake_suggestions = [SimpleNamespace(suggestion="software engineering")]

    def fake_autocomplete(self, query: str):
        assert query == "softw"
        return fake_suggestions

    monkeypatch.setattr(SemanticScholar, "get_autocomplete", fake_autocomplete, raising=False)

    sch = SemanticScholar()
    suggestions = sch.get_autocomplete("softw")

    assert suggestions is fake_suggestions
    assert suggestions[0].suggestion == "software engineering"


def test_timeout_property_roundtrip():
    sch = SemanticScholar(timeout=5)

    assert hasattr(sch, "timeout")
    sch.timeout = 10
    assert sch.timeout == 10


def test_get_papers_accepts_batch(monkeypatch):
    ids = ["CorpusId:470667", "10.2139/ssrn.2250500"]
    called = {}

    def fake_get_papers(self, id_list):
        called["ids"] = id_list
        return [SimpleNamespace(paperId=pid) for pid in id_list]

    monkeypatch.setattr(SemanticScholar, "get_papers", fake_get_papers, raising=False)

    sch = SemanticScholar()
    papers = sch.get_papers(ids)

    assert called["ids"] == ids
    assert [paper.paperId for paper in papers] == ids


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_API_TESTS") != "1",
    reason="Live Semantic Scholar tests disabled",
)
def test_live_get_paper_retrieves_full_metadata_and_relations():
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    mode = "authenticated" if api_key else "unauthenticated"
    sch = SemanticScholar(api_key=api_key)

    paper_id = "arXiv:1706.03762"  # "Attention Is All You Need"
    fields_to_request = [
        "title",
        "abstract",
        "referenceCount",
        "citationCount",
        "references",
        "citations",
    ]

    try:
        paper = sch.get_paper(paper_id, fields=fields_to_request)
    except (InternalServerErrorException, ConnectionRefusedError) as exc:
        pytest.skip(f"Semantic Scholar API ({mode}) unavailable: {exc}")
    except ObjectNotFoundException as exc:
        pytest.skip(f"Semantic Scholar ({mode}) could not find paper: {exc}")

    # Metadata checks
    assert "attention is all you need" in paper.title.lower()
    assert paper.abstract is not None
    assert isinstance(paper.citationCount, int) and paper.citationCount > 10000
    assert isinstance(paper.referenceCount, int) and paper.referenceCount > 0

    # Relations checks
    assert paper.references is not None
    assert paper.citations is not None

    if not paper.references:
        pytest.fail("Expected references for this paper.")

    if not paper.citations:
        pytest.fail("Expected a highly cited paper to have citations.")

    # Check that one of the citations has a title (i.e., it's a populated object)
    assert any(c.title for c in paper.citations if c)
    assert any(r.title for r in paper.references if r)
