import unittest
from typing import Any, Dict, List, Optional

import requests

from agents.semantic_scholar.google_scholar import GoogleScholarClient, GoogleScholarError
from agents.semantic_scholar.search import PaperRecord, SemanticScholarClient, SemanticScholarError


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
        self.assertEqual(results[0].source, "semantic_scholar")
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

    def test_fetch_references_returns_related_records(self) -> None:
        payload = {
            "data": [
                {
                    "citedPaper": {
                        "paperId": "ref-1",
                        "title": "Reference Paper",
                        "authors": [{"name": "Alan"}],
                        "year": 2020,
                        "venue": "Journal",
                        "url": "http://example.com/ref",
                    }
                }
            ]
        }
        session = FakeSession([FakeResponse(json_data=payload)])
        client = SemanticScholarClient(api_key="secret", session=session)

        results = client.fetch_references("root-id", limit=5)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].relation_type, "reference")
        self.assertEqual(results[0].related_paper_id, "root-id")
        self.assertEqual(results[0].source_query, "references:root-id")
        self.assertIn("/paper/root-id/references", session.calls[0]["url"])

    def test_fetch_citations_returns_related_records(self) -> None:
        payload = {
            "data": [
                {
                    "citingPaper": {
                        "paperId": "cit-1",
                        "title": "Citing Paper",
                        "authors": [{"name": "Alan"}],
                    }
                }
            ]
        }
        session = FakeSession([FakeResponse(json_data=payload)])
        client = SemanticScholarClient(api_key=None, session=session)

        results = client.fetch_citations("root-id", limit=3)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].relation_type, "citation")
        self.assertEqual(results[0].related_paper_id, "root-id")
        self.assertEqual(results[0].paper_id, "cit-1")

    def test_fetch_related_requires_paper_id(self) -> None:
        client = SemanticScholarClient(api_key=None)

        with self.assertRaises(ValueError):
            client.fetch_references("  ")


class GoogleScholarClientTest(unittest.TestCase):
    def test_google_scholar_converts_results(self) -> None:
        payload = {
            "organic_results": [
                {
                    "result_id": "gs1",
                    "title": "Google Paper",
                    "link": "http://example.com/gs1",
                    "snippet": "Findings about AI.",
                    "publication_info": {
                        "summary": "Journal of AI, 2023",
                        "authors": [{"name": "Grace"}],
                    },
                }
            ]
        }
        session = FakeSession([FakeResponse(json_data=payload)])
        client = GoogleScholarClient(api_key="serp", session=session, default_limit=2)

        results = client.search("graph neural networks")

        self.assertEqual(len(results), 1)
        paper = results[0]
        self.assertEqual(paper.source, "google_scholar")
        self.assertEqual(paper.year, 2023)
        self.assertIn("Grace", paper.authors)

    def test_google_scholar_requires_api_key(self) -> None:
        client = GoogleScholarClient(api_key=None)

        with self.assertRaises(GoogleScholarError):
            client.search("graph neural networks")

    def test_google_scholar_surface_error_payload(self) -> None:
        payload = {"error": "Invalid API key", "organic_results": []}
        session = FakeSession([FakeResponse(json_data=payload)])
        client = GoogleScholarClient(api_key="serp", session=session)

        with self.assertRaises(GoogleScholarError) as ctx:
            client.search("graph neural networks")

        self.assertIn("invalid api key", str(ctx.exception).lower())

    def test_google_scholar_invalid_api_key_status_code(self) -> None:
        session = FakeSession([
            FakeResponse(status_code=401, text='{"error": "Invalid API key"}')
        ])
        client = GoogleScholarClient(api_key="serp", session=session)

        with self.assertRaises(GoogleScholarError) as ctx:
            client.search("graph neural networks")

        message = str(ctx.exception)
        self.assertIn("401", message)
        self.assertIn("Invalid API key", message)


if __name__ == "__main__":
    unittest.main()
