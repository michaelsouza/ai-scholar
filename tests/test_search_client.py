import unittest
from typing import Any, Dict, List, Optional

import requests

from agents.semantic_scholar.search import (
    PaperRecord,
    SemanticScholarClient,
    SemanticScholarError,
)


class FakeResponse:
    def __init__(
        self,
        *,
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text: str = "",
    ) -> None:
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text or ""

    def json(self) -> Dict[str, Any]:
        return self._json

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            error = requests.HTTPError(f"{self.status_code} error")
            error.response = self
            raise error


class FakeSession:
    def __init__(self, responses: List[FakeResponse]) -> None:
        self._responses = responses
        self.calls: List[Dict[str, Any]] = []

    def get(
        self,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
    ) -> FakeResponse:
        self.calls.append({
            "url": url,
            "params": params or {},
            "headers": headers or {},
            "timeout": timeout,
        })
        if not self._responses:
            raise AssertionError("Unexpected extra GET call")
        return self._responses.pop(0)


class SemanticScholarClientTest(unittest.TestCase):
    def test_authenticated_search_returns_paper_records(self) -> None:
        payload = {
            "data": [
                {
                    "paperId": "p1",
                    "title": "First Paper",
                    "authors": [{"name": "Ada"}],
                    "year": 2024,
                    "venue": "NeurIPS",
                    "url": "http://example.com",
                },
            ]
        }
        session = FakeSession([FakeResponse(json_data=payload)])
        client = SemanticScholarClient(api_key="secret", session=session)

        results = client.search("graph neural networks", limit=1)

        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], PaperRecord)
        self.assertEqual(results[0].paper_id, "p1")
        self.assertEqual(session.calls[0]["headers"].get("x-api-key"), "secret")

    def test_unauthenticated_search_uses_pagination(self) -> None:
        first_page = {
            "data": [
                {
                    "paperId": "p1",
                    "title": "Chunk One",
                    "authors": [],
                }
            ],
            "token": "next-token",
        }
        second_page = {
            "data": [
                {
                    "paperId": "p2",
                    "title": "Chunk Two",
                    "authors": [],
                }
            ]
        }
        session = FakeSession([
            FakeResponse(json_data=first_page),
            FakeResponse(json_data=second_page),
        ])
        client = SemanticScholarClient(api_key=None, session=session, default_limit=3)

        results = client.search("graph neural networks", limit=2)

        self.assertEqual({paper.paper_id for paper in results}, {"p1", "p2"})
        self.assertEqual(session.calls[0]["params"].get("token"), None)
        self.assertEqual(session.calls[1]["params"].get("token"), "next-token")

    def test_rate_limit_surfaces_semantic_scholar_error(self) -> None:
        session = FakeSession([
            FakeResponse(status_code=429, text="Too Many Requests"),
        ])
        client = SemanticScholarClient(api_key=None, session=session)

        with self.assertRaises(SemanticScholarError) as ctx:
            client.search("graph neural networks", limit=1)

        self.assertIn("rate limit", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
