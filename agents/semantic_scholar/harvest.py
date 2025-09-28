"""Utilities for expanding papers via Semantic Scholar relationships."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Mapping, Optional, Sequence, Set

from rich.console import Console

from .search import PaperRecord, SemanticScholarClient


@dataclass
class RelatedPaperHarvesterConfig:
    """Configuration for harvesting related papers."""

    include_references: bool = True
    include_citations: bool = False
    max_per_relation: int = 5
    eligible_labels: Optional[Set[str]] = None

    def __post_init__(self) -> None:
        if self.eligible_labels is None:
            self.eligible_labels = {"partial"}
        if self.max_per_relation < 1:
            raise ValueError("max_per_relation must be >= 1")


class RelatedPaperHarvester:
    """Fetches references/citations for promising papers to widen discovery."""

    def __init__(
        self,
        *,
        client: SemanticScholarClient,
        console: Optional[Console] = None,
        config: Optional[RelatedPaperHarvesterConfig] = None,
    ) -> None:
        self._client = client
        self._console = console or Console()
        self._config = config or RelatedPaperHarvesterConfig()

    def harvest(
        self,
        *,
        papers: Sequence[PaperRecord],
        labels: Optional[Mapping[str, str]] = None,
        seen_ids: Optional[Iterable[str]] = None,
    ) -> List[PaperRecord]:
        """Return related papers drawn from references/citations.

        Parameters
        ----------
        papers:
            Papers from the latest search iteration.
        labels:
            Optional mapping of paper_id to classification label to filter candidates.
        seen_ids:
            Identifiers already present in the working set; prevents duplicates.
        """

        seen: Set[str] = {pid for pid in (seen_ids or []) if pid}
        derived: List[PaperRecord] = []

        for paper in papers:
            if paper.source != "semantic_scholar":
                continue
            if not paper.paper_id:
                continue
            if labels and not self._is_label_eligible(paper.paper_id, labels):
                continue

            if self._config.include_references:
                derived.extend(
                    self._collect_related(
                        fetcher=self._client.fetch_references,
                        paper_id=paper.paper_id,
                        seen=seen,
                    )
                )
            if self._config.include_citations:
                derived.extend(
                    self._collect_related(
                        fetcher=self._client.fetch_citations,
                        paper_id=paper.paper_id,
                        seen=seen,
                    )
                )

        return derived

    # ------------------------------------------------------------------
    def _is_label_eligible(self, paper_id: str, labels: Mapping[str, str]) -> bool:
        label = labels.get(paper_id)
        if label is None:
            return True
        return label.lower() in self._config.eligible_labels

    def _collect_related(
        self,
        *,
        fetcher,
        paper_id: str,
        seen: Set[str],
    ) -> List[PaperRecord]:
        try:
            results = fetcher(paper_id, limit=self._config.max_per_relation)
        except Exception as error:  # pragma: no cover - network errors exercised elsewhere
            self._console.print(f"[yellow]Failed to fetch related papers for {paper_id}: {error}[/]")
            return []

        collected: List[PaperRecord] = []
        for record in results:
            record_id = record.paper_id
            if record_id and record_id in seen:
                continue
            if record_id:
                seen.add(record_id)
            collected.append(record)
        return collected
