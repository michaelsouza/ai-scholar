import unittest
from typing import Dict, List, Optional

from agents.semantic_scholar.harvest import (
    RelatedPaperHarvester,
    RelatedPaperHarvesterConfig,
)
from agents.semantic_scholar.search import PaperRecord


def _make_record(paper_id: str, title: str) -> PaperRecord:
    return PaperRecord(
        source="semantic_scholar",
        paper_id=paper_id,
        title=title,
        url=None,
        year=None,
        venue=None,
        abstract=None,
        authors=[],
        source_query="seed",
    )


class StubSemanticClient:
    def __init__(self, references: Dict[str, List[PaperRecord]], citations: Dict[str, List[PaperRecord]]) -> None:
        self._references = references
        self._citations = citations
        self.records: List[tuple[str, str]] = []

    def fetch_references(self, paper_id: str, *, limit: Optional[int] = None) -> List[PaperRecord]:
        self.records.append(("references", paper_id))
        items = self._references.get(paper_id, [])
        return list(items[: limit or len(items)])

    def fetch_citations(self, paper_id: str, *, limit: Optional[int] = None) -> List[PaperRecord]:
        self.records.append(("citations", paper_id))
        items = self._citations.get(paper_id, [])
        return list(items[: limit or len(items)])


class RelatedPaperHarvesterTest(unittest.TestCase):
    def test_harvest_collects_references_for_partial_labels(self) -> None:
        base = _make_record("base", "Seed Paper")
        references = {
            "base": [_make_record("ref-1", "Reference One"), _make_record("ref-2", "Reference Two")]
        }
        citations: Dict[str, List[PaperRecord]] = {}
        client = StubSemanticClient(references, citations)
        harvester = RelatedPaperHarvester(
            client=client,
            config=RelatedPaperHarvesterConfig(include_citations=False, max_per_relation=3),
        )

        results = harvester.harvest(papers=[base], labels={"base": "partial"})

        self.assertEqual({paper.paper_id for paper in results}, {"ref-1", "ref-2"})
        self.assertIn(("references", "base"), client.records)

    def test_harvest_skips_papers_with_ineligible_labels(self) -> None:
        base = _make_record("base", "Seed Paper")
        client = StubSemanticClient(references={}, citations={})
        harvester = RelatedPaperHarvester(
            client=client,
            config=RelatedPaperHarvesterConfig(include_citations=True),
        )

        results = harvester.harvest(papers=[base], labels={"base": "irrelevant"})

        self.assertEqual(results, [])
        self.assertEqual(client.records, [])

    def test_harvest_collects_citations_when_enabled(self) -> None:
        base = _make_record("base", "Seed Paper")
        citations = {"base": [_make_record("cit-1", "Citing Paper")]}
        client = StubSemanticClient(references={}, citations=citations)
        harvester = RelatedPaperHarvester(
            client=client,
            config=RelatedPaperHarvesterConfig(include_citations=True),
        )

        results = harvester.harvest(papers=[base], labels={"base": "partial"})

        self.assertEqual({paper.paper_id for paper in results}, {"cit-1"})
        self.assertIn(("citations", "base"), client.records)

    def test_harvest_deduplicates_seen_ids(self) -> None:
        base = _make_record("base", "Seed Paper")
        references = {"base": [_make_record("dup-id", "Reference One")]}
        client = StubSemanticClient(references, citations={})
        harvester = RelatedPaperHarvester(client=client)

        results = harvester.harvest(papers=[base], labels={"base": "partial"}, seen_ids={"dup-id"})

        self.assertEqual(results, [])

    def test_harvest_skips_non_semantic_scholar_sources(self) -> None:
        paper = _make_record("ext-1", "External Paper")
        paper.source = "google_scholar"
        client = StubSemanticClient(references={"ext-1": [_make_record("ref", "Ref")]}, citations={})
        harvester = RelatedPaperHarvester(client=client)

        results = harvester.harvest(papers=[paper], labels={"ext-1": "partial"})

        self.assertEqual(results, [])
        self.assertEqual(client.records, [])


if __name__ == "__main__":
    unittest.main()
