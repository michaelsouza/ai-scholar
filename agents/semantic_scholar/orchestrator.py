"""Workflow orchestrator for the dual-agent scholarly search system."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .classifier import ClassificationAgent, ClassificationResult
from .harvest import RelatedPaperHarvester
from .query_agent import QueryAgent
from .search import PaperRecord
from .storage import PaperDatabase


@dataclass
class OrchestratorConfig:
    max_iterations: int = 3
    database_path: str = "data/search_results.json"


class SemanticScholarOrchestrator:
    """Coordinates query and classification agents, persisting their outputs."""

    def __init__(
        self,
        *,
        query_agent: QueryAgent,
        classifier: ClassificationAgent,
        database: PaperDatabase,
        console: Optional[Console] = None,
        config: Optional[OrchestratorConfig] = None,
        harvester: Optional[RelatedPaperHarvester] = None,
    ) -> None:
        self._console = console or Console()
        self._query_agent = query_agent
        self._classifier = classifier
        self._database = database
        self._config = config or OrchestratorConfig()
        self._harvester = harvester

    # ------------------------------------------------------------------
    def run(self, initial_query: str) -> None:
        """Run the iterative retrieval-classification workflow."""

        query = initial_query.strip()
        feedback: Optional[str] = None
        seen_paper_ids: set[str] = set()

        for iteration in range(1, self._config.max_iterations + 1):
            self._console.rule(Text(f"Iteration {iteration}", style="bold magenta"))
            agent_run = self._query_agent.run(search_query=query, feedback=feedback)
            self._console.print(
                Panel.fit(
                    agent_run.final_message or "(no final response)",
                    title="Query Agent Summary",
                    border_style="green",
                )
            )

            new_papers = self._filter_new_papers(agent_run.papers, seen_paper_ids)
            classifications = self._classify_papers(query, new_papers)
            run_id = self._database.log_run(
                query=query,
                iteration=iteration,
                agent_summary=agent_run.final_message,
                feedback=feedback,
            )
            for result in classifications:
                self._database.store_classification(run_id, result)

            all_results = list(classifications)

            if self._harvester and classifications:
                label_map = {
                    result.paper.paper_id: result.label
                    for result in classifications
                    if result.paper.paper_id
                }
                related_candidates = self._harvester.harvest(
                    papers=[result.paper for result in classifications],
                    labels=label_map,
                    seen_ids=seen_paper_ids,
                )
                related_candidates = self._filter_new_papers(related_candidates, seen_paper_ids)

                if related_candidates:
                    self._console.print(
                        Panel.fit(
                            "Exploring references/citations for promising papers.",
                            title="Relationship Expansion",
                            border_style="blue",
                        )
                    )
                    derived_results = self._classify_papers(
                        query,
                        related_candidates,
                        heading="Derived Classification Results",
                    )
                    for result in derived_results:
                        self._database.store_classification(run_id, result)
                    all_results.extend(derived_results)

            if any(result.is_strong for result in all_results):
                self._console.print(
                    Panel.fit(
                        "Strongly relevant paper(s) found. Stopping iterations.",
                        border_style="bright_green",
                    )
                )
                break

            feedback = self._build_feedback(all_results)
            if not feedback:
                self._console.print(
                    Panel.fit(
                        "No useful feedback available; stopping iterations.",
                        border_style="yellow",
                    )
                )
                break

            refined_query = self._query_agent.suggest_refined_query(
                previous_query=query,
                feedback=feedback,
            )
            refined_query = refined_query.strip()
            if not refined_query or refined_query.lower() == query.lower():
                self._console.print(
                    Panel.fit(
                        "Query agent did not produce a new query; stopping iterations.",
                        border_style="yellow",
                    )
                )
                break

            self._console.print(
                Panel.fit(
                    Text(refined_query, style="bold"),
                    title="Refined Query",
                    border_style="cyan",
                )
            )
            query = refined_query

    # ------------------------------------------------------------------
    def _classify_papers(
        self,
        query: str,
        papers: Iterable[PaperRecord],
        *,
        heading: str = "Classification Results",
    ) -> List[ClassificationResult]:
        papers = list(papers)
        if not papers:
            self._console.print(
                Panel.fit("No papers returned for classification.", border_style="yellow")
            )
            return []

        table = Table(title=heading, show_lines=False)
        table.add_column("Title", style="bold", overflow="fold")
        table.add_column("Source", style="blue")
        table.add_column("Label", style="cyan")
        table.add_column("Confidence", style="magenta")
        table.add_column("Explanation", style="white", overflow="fold")

        results: List[ClassificationResult] = []
        for paper in papers:
            result = self._classifier.classify(query=query, paper=paper)
            results.append(result)
            title = paper.title
            if paper.relation_type:
                title = f"{title} [{paper.relation_type}]"
            table.add_row(
                title,
                paper.source,
                result.label,
                f"{result.confidence:.2f}",
                result.explanation,
            )

        self._console.print(table)
        return results

    def _filter_new_papers(
        self, papers: Iterable[PaperRecord], seen_ids: set[str]
    ) -> List[PaperRecord]:
        fresh: List[PaperRecord] = []
        for paper in papers:
            identifier = paper.paper_id
            if identifier and identifier in seen_ids:
                continue
            if identifier:
                seen_ids.add(identifier)
            fresh.append(paper)
        return fresh

    def _build_feedback(self, results: Iterable[ClassificationResult]) -> str:
        lines = []
        for result in results:
            if result.is_strong:
                continue
            relation_hint = ""
            if result.paper.relation_type:
                relation_hint = f" via {result.paper.relation_type}"
            lines.append(
                f"Paper '{result.paper.title}' from {result.paper.source}{relation_hint} classified as {result.label} "
                f"(confidence {result.confidence:.2f}). "
                f"Rationale: {result.explanation}"
            )
        if not lines:
            return ""
        return "\n".join(lines)
