"""Workflow orchestrator for the dual-agent scholarly search system."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .classifier import ClassificationAgent, ClassificationResult
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
    ) -> None:
        self._console = console or Console()
        self._query_agent = query_agent
        self._classifier = classifier
        self._database = database
        self._config = config or OrchestratorConfig()

    # ------------------------------------------------------------------
    def run(self, initial_query: str) -> None:
        """Run the iterative retrieval-classification workflow."""

        query = initial_query.strip()
        feedback: Optional[str] = None

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

            classifications = self._classify_papers(query, agent_run.papers)
            run_id = self._database.log_run(
                query=query,
                iteration=iteration,
                agent_summary=agent_run.final_message,
                feedback=feedback,
            )
            for result in classifications:
                self._database.store_classification(run_id, result)

            if any(result.is_strong for result in classifications):
                self._console.print(
                    Panel.fit(
                        "Strongly relevant paper(s) found. Stopping iterations.",
                        border_style="bright_green",
                    )
                )
                break

            feedback = self._build_feedback(classifications)
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
    def _classify_papers(self, query: str, papers: Iterable[PaperRecord]) -> List[ClassificationResult]:
        papers = list(papers)
        if not papers:
            self._console.print(
                Panel.fit("No papers returned for classification.", border_style="yellow")
            )
            return []

        table = Table(title="Classification Results", show_lines=False)
        table.add_column("Title", style="bold", overflow="fold")
        table.add_column("Source", style="blue")
        table.add_column("Label", style="cyan")
        table.add_column("Confidence", style="magenta")
        table.add_column("Explanation", style="white", overflow="fold")

        results: List[ClassificationResult] = []
        for paper in papers:
            result = self._classifier.classify(query=query, paper=paper)
            results.append(result)
            table.add_row(
                paper.title,
                paper.source,
                result.label,
                f"{result.confidence:.2f}",
                result.explanation,
            )

        self._console.print(table)
        return results

    def _build_feedback(self, results: Iterable[ClassificationResult]) -> str:
        lines = []
        for result in results:
            if result.is_strong:
                continue
            lines.append(
                f"Paper '{result.paper.title}' from {result.paper.source} classified as {result.label} "
                f"(confidence {result.confidence:.2f}). "
                f"Rationale: {result.explanation}"
            )
        if not lines:
            return ""
        return "\n".join(lines)
