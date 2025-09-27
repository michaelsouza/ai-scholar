import json
import tempfile
import unittest
from pathlib import Path

from agents.semantic_scholar.classifier import ClassificationResult
from agents.semantic_scholar.search import PaperRecord
from agents.semantic_scholar.storage import PaperDatabase


class PaperDatabaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.db_path = Path(self._tmpdir.name) / "runs.json"
        self.database = PaperDatabase(self.db_path)

    def _paper(self) -> PaperRecord:
        return PaperRecord(
            paper_id="p-1",
            title="Sample Paper",
            url="http://example.com",
            year=2024,
            venue="TestConf",
            abstract="A short abstract.",
            authors=["Ada"],
            source_query="graph neural networks",
        )

    def test_initialises_empty_document(self) -> None:
        payload = json.loads(self.db_path.read_text())
        self.assertEqual(payload["runs"], [])
        self.assertEqual(payload["papers"], [])

    def test_log_run_appends_entry(self) -> None:
        run_id = self.database.log_run(
            query="graph neural networks",
            iteration=1,
            agent_summary="Summary",
            feedback=None,
        )
        payload = json.loads(self.db_path.read_text())
        self.assertEqual(run_id, 1)
        self.assertEqual(len(payload["runs"]), 1)
        self.assertEqual(payload["runs"][0]["query"], "graph neural networks")

    def test_store_classification_records_paper(self) -> None:
        run_id = self.database.log_run(
            query="graph neural networks",
            iteration=1,
            agent_summary="Summary",
            feedback=None,
        )
        result = ClassificationResult(
            paper=self._paper(),
            label="partial",
            confidence=0.55,
            explanation="Promising but off-topic.",
        )
        self.database.store_classification(run_id, result)

        payload = json.loads(self.db_path.read_text())
        self.assertEqual(len(payload["papers"]), 1)
        paper_entry = payload["papers"][0]
        self.assertEqual(paper_entry["run_id"], run_id)
        self.assertEqual(paper_entry["classification"], "partial")
        self.assertEqual(paper_entry["raw_payload"]["label"], "partial")

    def test_last_runs_returns_recent_entries(self) -> None:
        for iteration in range(1, 4):
            self.database.log_run(
                query=f"query-{iteration}",
                iteration=iteration,
                agent_summary=f"summary-{iteration}",
                feedback=None,
            )

        last_two = self.database.last_runs(limit=2)
        self.assertEqual(len(last_two), 2)
        self.assertEqual(last_two[0][1], "query-3")
        self.assertEqual(last_two[1][1], "query-2")


if __name__ == "__main__":
    unittest.main()
