"""Utilities for retrieving Google Scholar results via SerpAPI."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import requests

from .search import PaperRecord

GOOGLE_SCHOLAR_ENDPOINT = "https://serpapi.com/search.json"


class GoogleScholarError(RuntimeError):
    """Raised when Google Scholar retrieval fails."""


class GoogleScholarClient:
    """Thin wrapper around SerpAPI's Google Scholar endpoint."""

    def __init__(
        self,
        *,
        api_key: Optional[str],
        timeout: int = 20,
        default_limit: int = 5,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.default_limit = default_limit
        self.session = session or requests.Session()
        self.name = "Google Scholar"

    def search(self, query: str, *, limit: Optional[int] = None) -> List[PaperRecord]:
        query = query.strip()
        if not query:
            raise ValueError("Google Scholar search requires a non-empty query.")
        if not self.api_key:
            raise GoogleScholarError(
                "Google Scholar search requires a SERPAPI key (set SERPAPI_API_KEY or pass --google-scholar-api-key)."
            )

        limit = max(1, limit or self.default_limit)

        params = {
            "engine": "google_scholar",
            "q": query,
            "api_key": self.api_key,
            "hl": "en",
        }

        try:
            response = self.session.get(
                GOOGLE_SCHOLAR_ENDPOINT,
                params=params,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:  # pragma: no cover - passthrough network errors
            raise GoogleScholarError(f"Google Scholar request failed: {exc}") from exc

        if response.status_code != 200:
            raise GoogleScholarError(
                f"Google Scholar error {response.status_code}: {response.text}"
            )

        payload = response.json()
        organic_results: List[Dict[str, Any]] = payload.get("organic_results", [])
        if not organic_results and payload.get("error"):
            raise GoogleScholarError(f"Google Scholar error: {payload['error']}")

        papers: List[PaperRecord] = []
        for item in organic_results:
            papers.append(self._convert_result(item, query))
            if len(papers) >= limit:
                break
        return papers

    def _convert_result(self, payload: Dict[str, Any], query: str) -> PaperRecord:
        publication = payload.get("publication_info") or {}
        authors = self._parse_authors(publication)
        venue = publication.get("summary") or publication.get("venue")
        year = self._parse_year(publication.get("summary"))

        return PaperRecord(
            source="google_scholar",
            paper_id=payload.get("result_id") or payload.get("link"),
            title=payload.get("title") or "Untitled",
            url=payload.get("link"),
            year=year,
            venue=venue,
            abstract=payload.get("snippet"),
            authors=authors,
            source_query=query,
        )

    @staticmethod
    def _parse_authors(publication: Dict[str, Any]) -> List[str]:
        authors: List[str] = []
        for author in publication.get("authors", []) or []:
            if isinstance(author, dict):
                name = author.get("name")
            else:
                name = str(author)
            if name:
                authors.append(name)
        return authors

    @staticmethod
    def _parse_year(summary: Optional[str]) -> Optional[int]:
        if not summary:
            return None
        match = re.search(r"(19|20)\d{2}", summary)
        if not match:
            return None
        try:
            return int(match.group(0))
        except ValueError:  # pragma: no cover - defensive
            return None
