import unittest
from types import SimpleNamespace

from rich.console import Console

from agents.semantic_scholar.classifier import ClassificationAgent, ClassificationResult
from agents.semantic_scholar.orchestrator import SemanticScholarOrchestrator
from agents.semantic_scholar.search import PaperRecord


class StubChain:
    def __init__(self, payload: str) -> None:
        self.payload = payload

    def invoke(self, _: dict) -> str:
        return self.payload


class ClassificationAgentTest(unittest.TestCase):
    def _make_agent(self, payload: str) -> ClassificationAgent:
        agent = ClassificationAgent.__new__(ClassificationAgent)
        agent._console = Console(width=80)
        agent._chain = StubChain(payload)
        return agent

    def _make_paper(self) -> PaperRecord:
        return PaperRecord(
            source="semantic_scholar",
            paper_id="pid",
            title="Interesting Paper",
            url="http://example.com",
            year=2024,
            venue="ICML",
            abstract="This work studies something relevant.",
            authors=["Ada"],
            source_query="graph neural networks",
        )

    def test_classify_parses_json_payload(self) -> None:
        agent = self._make_agent(
            '{"label": "strong", "confidence": 0.9, "explanation": "Direct match."}'
        )
        result = agent.classify(query="focus", paper=self._make_paper())

        self.assertTrue(result.is_strong)
        self.assertAlmostEqual(result.confidence, 0.9)
        self.assertEqual(result.explanation, "Direct match.")

    def test_classify_handles_non_json_payload(self) -> None:
        agent = self._make_agent("Likely partial relevance; lacks evaluation.")
        result = agent.classify(query="focus", paper=self._make_paper())

        self.assertEqual(result.label, "partial")
        self.assertIn("partial", result.explanation.lower())


class OrchestratorFeedbackTest(unittest.TestCase):
    def test_feedback_summarises_non_strong_results(self) -> None:
        orchestrator = SemanticScholarOrchestrator.__new__(SemanticScholarOrchestrator)
        orchestrator._console = Console(width=80)
        paper = PaperRecord(
            source="semantic_scholar",
            paper_id="pid",
            title="Off-topic Paper",
            url=None,
            year=None,
            venue=None,
            abstract=None,
            authors=[],
            source_query="focus",
        )
        strong_result = ClassificationResult(
            paper=paper,
            label="strong",
            confidence=0.95,
            explanation="Exactly on point.",
        )
        weak_result = ClassificationResult(
            paper=paper,
            label="irrelevant",
            confidence=0.4,
            explanation="Discusses a different domain.",
        )

        feedback = SemanticScholarOrchestrator._build_feedback(orchestrator, [strong_result, weak_result])

        self.assertIn("irrelevant", feedback)
        self.assertIn("different domain", feedback)
        self.assertNotIn("Exactly on point", feedback)


if __name__ == "__main__":
    unittest.main()
