"""Utilities for querying the Semantic Scholar API."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Iterable, List, Optional

import requests

SEMANTIC_SCHOLAR_AUTH_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper/search"
SEMANTIC_SCHOLAR_BULK_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
SEMANTIC_SCHOLAR_FIELDS = "paperId,title,authors.name,year,url,venue,abstract"


class SemanticScholarError(RuntimeError):
    """Raised when the Semantic Scholar API returns an error."""


@dataclass
class PaperRecord:
    """Structured representation of a Semantic Scholar paper."""

    paper_id: Optional[str]
    title: str
    url: Optional[str]
    year: Optional[int]
    venue: Optional[str]
    abstract: Optional[str]
    authors: List[str]
    source_query: str

    @classmethod
    def from_payload(cls, payload: dict, query: str) -> "PaperRecord":
        authors = [author.get("name", "?") for author in payload.get("authors", [])]
        return cls(
            paper_id=payload.get("paperId"),
            title=payload.get("title") or "Untitled",
            url=payload.get("url"),
            year=payload.get("year"),
            venue=payload.get("venue"),
            abstract=payload.get("abstract"),
            authors=authors,
            source_query=query,
        )


def _format_authors(authors: Iterable[str]) -> str:
    names = [name for name in authors if name]
    if not names:
        return "Unknown"
    if len(names) > 5:
        return ", ".join(names[:5]) + ", et al."
    return ", ".join(names)


def format_papers(papers: Iterable[PaperRecord]) -> str:
    """Return a human-readable summary of papers for LLM consumption."""

    lines = []
    for idx, paper in enumerate(papers, start=1):
        header_parts = [f"{idx}. {paper.title}"]
        if paper.year:
            header_parts.append(f"({paper.year})")
        if paper.venue:
            header_parts.append(f"- {paper.venue}")
        header = " ".join(header_parts)

        body = [header, f"Authors: {_format_authors(paper.authors)}"]
        if paper.url:
            body.append(f"URL: {paper.url}")
        if paper.abstract:
            abstract = paper.abstract.strip().replace("\n", " ")
            body.append(f"Abstract: {abstract[:500]}" + ("…" if len(abstract) > 500 else ""))
        lines.append("\n".join(body))

    if not lines:
        return "No papers returned."

    return "\n\n".join(lines)


class SemanticScholarClient:
    """Small client helper that supports authenticated and unauthenticated search."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        timeout: int = 20,
        default_limit: int = 5,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.default_limit = default_limit
        self.session = session or requests.Session()

    def search(self, query: str, *, limit: Optional[int] = None) -> List[PaperRecord]:
        query = query.strip()
        if not query:
            raise ValueError("Semantic Scholar search requires a non-empty query.")

        limit = limit or self.default_limit
        limit = max(1, limit)

        if self.api_key:
            payload = self._search_auth(query, limit)
        else:
            payload = self._search_unauth(query, limit)

        papers = [PaperRecord.from_payload(item, query) for item in payload]
        return papers

    # ------------------------------------------------------------------
    # Authenticated search
    # ------------------------------------------------------------------
    def _search_auth(self, query: str, limit: int) -> List[dict]:
        params = {
            "query": query,
            "limit": limit,
            "fields": SEMANTIC_SCHOLAR_FIELDS,
        }
        headers = {"x-api-key": self.api_key} if self.api_key else None

        try:
            response = self.session.get(
                SEMANTIC_SCHOLAR_AUTH_ENDPOINT,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.HTTPError as err:  # pragma: no cover - passthrough network errors
            raise SemanticScholarError(
                f"Semantic Scholar HTTP error {err.response.status_code}: {err.response.text}"
            ) from err
        except requests.RequestException as err:  # pragma: no cover - passthrough network errors
            raise SemanticScholarError(f"Semantic Scholar request failed: {err}") from err

        payload = response.json()
        return payload.get("data", [])

    # ------------------------------------------------------------------
    # Unauthenticated search
    # ------------------------------------------------------------------
    def _search_unauth(self, query: str, limit: int) -> List[dict]:
        accumulated: List[dict] = []
        next_token: Optional[str] = None

        while len(accumulated) < limit:
            page_size = max(1, min(limit - len(accumulated), 100))
            params = {
                "query": query,
                "fields": SEMANTIC_SCHOLAR_FIELDS,
                "limit": page_size,
            }
            if next_token:
                params["token"] = next_token

            try:
                response = self.session.get(
                    SEMANTIC_SCHOLAR_BULK_ENDPOINT,
                    params=params,
                    timeout=self.timeout,
                )
            except requests.RequestException as err:  # pragma: no cover - passthrough network errors
                raise SemanticScholarError(f"Semantic Scholar request failed: {err}") from err

            if response.status_code == 429:
                raise SemanticScholarError(
                    "Semantic Scholar rate limit hit (100 unauthenticated requests per 5 minutes)."
                )
            if response.status_code != 200:
                raise SemanticScholarError(
                    f"Semantic Scholar error {response.status_code}: {response.text}"
                )

            payload = response.json()
            batch = payload.get("data", [])
            accumulated.extend(batch)

            next_token = payload.get("token")
            if not next_token or not batch:
                break

        return accumulated[:limit]

    # ------------------------------------------------------------------
    def as_json(self, papers: Iterable[PaperRecord]) -> str:
        """Return a JSON representation of papers for storage or debug output."""

        return json.dumps([paper.__dict__ for paper in papers], ensure_ascii=False, indent=2)
