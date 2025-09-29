from __future__ import annotations

import json
import os
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, List, Literal, Optional, Protocol, Tuple

import requests


Relation = Literal["reference", "citation"]
Verdict = Literal["accepted", "rejected"]


@dataclass
class Work:
    openalex_id: str
    title: str
    publication_year: Optional[int]
    authors: List[str] = field(default_factory=list)
    referenced_works: List[str] = field(default_factory=list)
    abstract: Optional[str] = None
    primary_topic: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "openalex_id": self.openalex_id,
            "title": self.title,
            "publication_year": self.publication_year,
            "authors": self.authors,
            "referenced_works": self.referenced_works,
            "abstract": self.abstract,
            "primary_topic": self.primary_topic,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "Work":
        return cls(
            openalex_id=str(payload["openalex_id"]),
            title=str(payload.get("title", "")),
            publication_year=payload.get("publication_year"),
            authors=list(payload.get("authors", [])),
            referenced_works=list(payload.get("referenced_works", [])),
            abstract=payload.get("abstract"),
            primary_topic=payload.get("primary_topic"),
        )


@dataclass
class WorkDecision:
    work: Work
    verdict: Verdict
    justification: str
    relation: Relation
    graph_key: str = ""


@dataclass
class GraphNode:
    work_id: str
    title: str
    role: Literal["seed", "reference", "citation"]
    verdict: Literal["accepted", "rejected", "seed"]


@dataclass
class CitationGraph:
    seed_key: str
    nodes: Dict[str, GraphNode]
    edges: List[Tuple[str, str]]


@dataclass
class OpenAlexResearchResult:
    seed: Work
    theme: str
    accepted: List[WorkDecision]
    rejected: List[WorkDecision]
    graph: CitationGraph

    @property
    def decisions(self) -> List[WorkDecision]:
        return self.accepted + self.rejected


class OpenAlexClient(Protocol):
    def fetch_work(self, work_id: str) -> Work: ...

    def fetch_references(self, work_id: str) -> List[Work]: ...

    def fetch_citations(self, work_id: str) -> List[Work]: ...


class OpenAlexHttpClient:
    """HTTP client that retrieves OpenAlex works using the public API."""

    def __init__(
        self,
        *,
        base_url: str = "https://api.openalex.org",
        mailto: Optional[str] = None,
        session: Optional[requests.Session] = None,
        timeout: int = 30,
        bulk_page_size: int = 25,
        citation_page_size: int = 25,
        max_citations: Optional[int] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._mailto = mailto or os.getenv("OPENALEX_MAILTO", "michael@ufc.br")
        self._session = session or requests.Session()
        self._timeout = timeout
        self._bulk_page_size = max(1, bulk_page_size)
        self._citation_page_size = max(1, citation_page_size)
        self._max_citations = max_citations

    def fetch_work(self, work_id: str) -> Work:
        payload = self._get_json(f"/works/{work_id}")
        return self._parse_work(payload)

    def fetch_references(self, work_id: str) -> List[Work]:
        payload = self._get_json(
            f"/works/{work_id}",
            params={"select": "id,referenced_works"},
        )
        raw_refs = payload.get("referenced_works", []) or []
        ref_ids = [self._normalize_work_id(value) for value in raw_refs if value]
        if not ref_ids:
            return []
        return self._fetch_many(ref_ids)

    def fetch_citations(self, work_id: str) -> List[Work]:
        params: Dict[str, Any] = {
            "filter": f"referenced_works:{work_id}",
            "per-page": self._citation_page_size,
            "cursor": "*",
        }
        works: List[Work] = []
        for item in self._iterate_paginated("/works", params=params, limit=self._max_citations):
            works.append(self._parse_work(item))
        return works

    def _fetch_many(self, work_ids: List[str]) -> List[Work]:
        if not work_ids:
            return []

        collected: Dict[str, Work] = {}
        for chunk in self._chunk(work_ids, self._bulk_page_size):
            filter_value = "|".join(chunk)
            payload = self._get_json(
                "/works",
                params={
                    "filter": f"openalex_id:{filter_value}",
                    "per-page": len(chunk),
                },
            )
            results = payload.get("results", [])
            if not isinstance(results, list):
                continue
            for item in results:
                work = self._parse_work(item)
                collected[work.openalex_id] = work

        ordered = [collected[work_id] for work_id in work_ids if work_id in collected]
        return ordered

    def _iterate_paginated(
        self,
        path: str,
        *,
        params: Dict[str, Any],
        limit: Optional[int],
    ) -> Iterator[Dict[str, Any]]:
        query = dict(params)
        remaining = limit
        cursor = query.get("cursor", "*")

        while True:
            query["cursor"] = cursor
            payload = self._get_json(path, params=query)
            results = payload.get("results", [])
            if not isinstance(results, list) or not results:
                break

            for item in results:
                yield item
                if remaining is not None:
                    remaining -= 1
                    if remaining <= 0:
                        return

            meta = payload.get("meta") or {}
            cursor = meta.get("next_cursor")
            if not cursor:
                break

    def _get_json(self, path: str, *, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        query = dict(params or {})
        query.setdefault("mailto", self._mailto)
        response = self._session.get(
            f"{self._base_url}{path}",
            params=query,
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()

    def _parse_work(self, payload: Dict[str, Any]) -> Work:
        openalex_id = self._normalize_work_id(payload.get("id", ""))
        if not openalex_id:
            raise ValueError("OpenAlex record is missing an identifier")

        referenced_raw = payload.get("referenced_works", []) or []
        referenced = [self._normalize_work_id(item) for item in referenced_raw if item]

        year = payload.get("publication_year")
        if isinstance(year, str):
            try:
                year = int(year)
            except ValueError:
                year = None
        elif not isinstance(year, int):
            year = None

        return Work(
            openalex_id=openalex_id,
            title=str(payload.get("title", "")),
            publication_year=year,
            authors=self._extract_authors(payload),
            referenced_works=referenced,
            abstract=self._extract_abstract(payload),
            primary_topic=self._extract_primary_topic(payload),
        )

    def _extract_authors(self, payload: Dict[str, Any]) -> List[str]:
        authors: List[str] = []
        for entry in payload.get("authorships", []) or []:
            if not isinstance(entry, dict):
                continue
            author = entry.get("author")
            if isinstance(author, dict):
                name = author.get("display_name")
                if name:
                    authors.append(str(name))
        return authors

    def _extract_primary_topic(self, payload: Dict[str, Any]) -> Optional[str]:
        primary = payload.get("primary_topic")
        if isinstance(primary, dict):
            name = primary.get("display_name")
            if name:
                return str(name)
        return None

    def _extract_abstract(self, payload: Dict[str, Any]) -> Optional[str]:
        inverted = payload.get("abstract_inverted_index")
        if not isinstance(inverted, dict):
            return None

        positions: Dict[int, str] = {}
        for word, indexes in inverted.items():
            if not isinstance(indexes, list):
                continue
            for position in indexes:
                try:
                    positions[int(position)] = str(word)
                except (TypeError, ValueError):
                    continue

        if not positions:
            return None

        ordered_words = [positions[index] for index in sorted(positions)]
        return " ".join(ordered_words)

    def _normalize_work_id(self, value: Any) -> str:
        if not value:
            return ""
        text = str(value)
        if "/" in text:
            return text.rsplit("/", 1)[-1]
        return text

    def _chunk(self, items: List[str], size: int) -> Iterator[List[str]]:
        step = max(1, size)
        for index in range(0, len(items), step):
            yield items[index : index + step]


class JsonFileCache:
    _DEFAULT_DATA = {"works": {}, "references": {}, "citations": {}}

    def __init__(self, path: Path | str):
        self._path = Path(path)
        self._data: Optional[Dict[str, Dict[str, object]]] = None
        self._dirty = False

    def _load(self) -> Dict[str, Dict[str, object]]:
        if self._data is None:
            if self._path.exists():
                with self._path.open("r", encoding="utf-8") as handle:
                    self._data = json.load(handle)
            else:
                self._data = {
                    "works": {},
                    "references": {},
                    "citations": {},
                }
        return self._data

    def _mark_dirty(self) -> None:
        self._dirty = True

    def commit(self) -> None:
        if not self._dirty:
            return

        data = self._load()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
        self._dirty = False

    def get_work(self, work_id: str) -> Optional[Work]:
        data = self._load()["works"].get(work_id)
        if data is None:
            return None
        return Work.from_dict(data)

    def store_work(self, work: Work) -> None:
        bucket = self._load()["works"]
        bucket[work.openalex_id] = work.to_dict()
        self._mark_dirty()

    def get_reference_ids(self, seed_id: str) -> List[str]:
        value = self._load()["references"].get(seed_id, [])
        return list(value)

    def set_reference_ids(self, seed_id: str, work_ids: List[str]) -> None:
        self._load()["references"][seed_id] = list(work_ids)
        self._mark_dirty()

    def get_citation_ids(self, seed_id: str) -> List[str]:
        value = self._load()["citations"].get(seed_id, [])
        return list(value)

    def set_citation_ids(self, seed_id: str, work_ids: List[str]) -> None:
        self._load()["citations"][seed_id] = list(work_ids)
        self._mark_dirty()


class CachedOpenAlexService:
    def __init__(self, client: OpenAlexClient, cache: JsonFileCache):
        self._client = client
        self._cache = cache

    def get_seed(self, work_id: str) -> Work:
        cached = self._cache.get_work(work_id)
        if cached is not None:
            return cached

        work = self._client.fetch_work(work_id)
        self._cache.store_work(work)
        self._cache.commit()
        return work

    def get_references(self, work_id: str) -> List[Work]:
        cached_ids = self._cache.get_reference_ids(work_id)
        if cached_ids:
            works = self._collect_from_cache(cached_ids)
            if len(works) == len(cached_ids):
                return works

        works = self._client.fetch_references(work_id)
        self._persist_relation(work_id, works, relation="references")
        return works

    def get_citations(self, work_id: str) -> List[Work]:
        cached_ids = self._cache.get_citation_ids(work_id)
        if cached_ids:
            works = self._collect_from_cache(cached_ids)
            if len(works) == len(cached_ids):
                return works

        works = self._client.fetch_citations(work_id)
        self._persist_relation(work_id, works, relation="citations")
        return works

    def _collect_from_cache(self, work_ids: Iterable[str]) -> List[Work]:
        result: List[Work] = []
        for work_id in work_ids:
            cached = self._cache.get_work(work_id)
            if cached is not None:
                result.append(cached)
        return result

    def _persist_relation(self, work_id: str, works: List[Work], *, relation: str) -> None:
        ids: List[str] = []
        for work in works:
            ids.append(work.openalex_id)
            self._cache.store_work(work)

        if relation == "references":
            self._cache.set_reference_ids(work_id, ids)
        elif relation == "citations":
            self._cache.set_citation_ids(work_id, ids)
        else:  # pragma: no cover - defensive
            raise ValueError(f"Unknown relation: {relation}")

        self._cache.commit()


class SimpleThemeRelevanceAgent:
    def set_run_context(self, *, seed: Optional[Work] = None, theme: Optional[str] = None) -> None:
        """Hook for subclasses; heuristic agent does not use additional context."""

    def evaluate(self, works: Iterable[Work], *, theme: str, relation: Relation) -> List[WorkDecision]:
        tokens = self._prepare_theme(theme)
        decisions: List[WorkDecision] = []
        for work in works:
            verdict, justification = self._score_work(work, tokens)
            decisions.append(
                WorkDecision(
                    work=work,
                    verdict=verdict,
                    justification=justification,
                    relation=relation,
                )
            )
        return decisions

    def _prepare_theme(self, theme: str) -> List[str]:
        tokens = sorted({token for token in self._extract_tokens(theme) if token})
        return tokens

    def _score_work(self, work: Work, tokens: List[str]) -> Tuple[Verdict, str]:
        if not tokens:
            return "accepted", "No theme keywords provided; defaulting to acceptance"

        search_fields = [
            ("title", work.title or ""),
            ("abstract", work.abstract or ""),
            ("primary_topic", work.primary_topic or ""),
        ]

        for field_name, content in search_fields:
            content_token_set = set(self._extract_tokens(content))
            matches = [token for token in tokens if token in content_token_set]
            if matches:
                keyword = matches[0]
                return "accepted", f"Matches theme keyword '{keyword}' in {field_name}"

        keywords = ", ".join(tokens)
        return "rejected", f"No theme keyword match found (expected one of: {keywords})"

    def _extract_tokens(self, text: str) -> List[str]:
        normalized = unicodedata.normalize("NFKD", text.lower())
        ascii_text = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        return re.findall(r"[a-z0-9]+", ascii_text)


class LLMThemeRelevanceAgent(SimpleThemeRelevanceAgent):
    """Classify works using an OpenRouter-hosted LLM with optional heuristics fallback."""

    def __init__(
        self,
        *,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1/chat/completions",
        temperature: float = 0.0,
        max_retries: int = 2,
        request_timeout: int = 60,
        app_url: Optional[str] = None,
        app_title: Optional[str] = None,
        session: Optional[requests.Session] = None,
        interaction_logger: Optional[Callable[[Work, List[Dict[str, str]], Dict[str, Any]], None]] = None,
    ) -> None:
        self._model = model or os.getenv("OPENROUTER_MODEL")
        self._api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self._model:
            raise ValueError("LLMThemeRelevanceAgent requires an OpenRouter model identifier")
        if not self._api_key:
            raise ValueError("LLMThemeRelevanceAgent requires OPENROUTER_API_KEY")

        self._base_url = base_url
        self._temperature = max(0.0, float(temperature))
        self._max_retries = max(1, int(max_retries))
        self._timeout = max(1, int(request_timeout))
        self._session = session or requests.Session()
        self._interaction_logger = interaction_logger
        self._headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        if app_url:
            self._headers["HTTP-Referer"] = app_url
        if app_title:
            self._headers["X-Title"] = app_title
        self._seed: Optional[Work] = None
        self._seed_theme: Optional[str] = None

    def evaluate(self, works: Iterable[Work], *, theme: str, relation: Relation) -> List[WorkDecision]:
        work_list = list(works)
        fallback_decisions = super().evaluate(work_list, theme=theme, relation=relation)
        fallback_map = {decision.work.openalex_id: decision for decision in fallback_decisions}

        decisions: List[WorkDecision] = []
        for work in work_list:
            fallback = fallback_map.get(work.openalex_id)
            try:
                verdict, justification = self._classify_with_llm(work, theme=theme, relation=relation)
            except Exception as exc:  # pragma: no cover - network dependent
                if fallback is not None:
                    justification = f"Fallback to heuristic: {fallback.justification} (LLM error: {exc})"
                    verdict = fallback.verdict
                else:
                    justification = f"Unable to classify via LLM: {exc}"
                    verdict = "rejected"

            decisions.append(
                WorkDecision(
                    work=work,
                    verdict=verdict,
                    justification=justification,
                    relation=relation,
                )
            )
        return decisions

    def _classify_with_llm(self, work: Work, *, theme: str, relation: Relation) -> Tuple[Verdict, str]:
        payload = {
            "model": self._model,
            "temperature": self._temperature,
            "messages": self._build_messages(work, theme=theme, relation=relation),
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "relevance_response",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "verdict": {
                                "type": "string",
                                "enum": ["accepted", "rejected"],
                            },
                            "justification": {
                                "type": "string",
                                "minLength": 1,
                            },
                        },
                        "required": ["verdict", "justification"],
                        "additionalProperties": False,
                    },
                },
            },
        }

        last_error: Optional[Exception] = None
        for _ in range(self._max_retries):
            try:
                response = self._session.post(
                    self._base_url,
                    headers=self._headers,
                    data=json.dumps(payload),
                    timeout=self._timeout,
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                self._log_interaction(work, payload["messages"], data)
                return self._parse_llm_content(content)
            except Exception as exc:
                last_error = exc
        raise RuntimeError(f"LLM classification failed: {last_error}")

    def set_run_context(self, *, seed: Optional[Work] = None, theme: Optional[str] = None) -> None:
        self._seed = seed
        self._seed_theme = theme

    def _log_interaction(
        self,
        work: Work,
        messages: List[Dict[str, str]],
        response: Dict[str, Any],
    ) -> None:
        if not self._interaction_logger:
            return
        try:
            # Create shallow copies to avoid accidental mutation downstream
            safe_messages = [dict(message) for message in messages]
            safe_response = dict(response)
            self._interaction_logger(work, safe_messages, safe_response)
        except Exception:  # pragma: no cover - logging must never break the flow
            pass

    def _build_messages(self, work: Work, *, theme: str, relation: Relation) -> List[Dict[str, str]]:
        abstract_text = (work.abstract or "").strip()

        author_line = ", ".join(work.authors) if work.authors else "Unknown"
        referenced_summary = ", ".join(work.referenced_works[:5])
        if len(work.referenced_works) > 5:
            referenced_summary += ", …"

        user_lines = [
            f"Theme: {theme}",
            f"Relation: {relation}",
            f"Title: {work.title}",
            f"Publication year: {work.publication_year or 'Unknown'}",
            f"Authors: {author_line}",
        ]
        if work.primary_topic:
            user_lines.append(f"Primary topic: {work.primary_topic}")
        if abstract_text:
            user_lines.append(f"Abstract: {abstract_text}")
        if referenced_summary:
            user_lines.append(f"Referenced works: {referenced_summary}")

        if self._seed is not None:
            if getattr(self._seed, "title", None):
                user_lines.append(f"Seed title: {self._seed.title}")
            seed_abstract = getattr(self._seed, "abstract", None)
            if seed_abstract:
                seed_text = seed_abstract.strip()
                if seed_text:
                    user_lines.append(f"Seed abstract: {seed_text}")
        if self._seed_theme and self._seed_theme != theme:
            user_lines.append(f"Seed theme context: {self._seed_theme}")

        system_prompt = (
            "You are a research assistant evaluating whether scholarly works align with a given theme. "
            "Respond with JSON containing a verdict ('accepted' or 'rejected') and a concise justification that "
            "links the work back to the theme. Prefer conceptual alignment over surface keyword matches."
        )
        user_prompt = "\n".join(user_lines)

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _parse_llm_content(self, content: str) -> Tuple[Verdict, str]:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            if "```" in cleaned:
                cleaned = cleaned.rsplit("```", 1)[0]

        data = json.loads(cleaned)
        verdict = str(data["verdict"]).strip().lower()
        if verdict not in ("accepted", "rejected"):
            raise ValueError(f"Unexpected verdict from LLM: {verdict}")

        justification = str(data["justification"]).strip()
        if not justification:
            raise ValueError("LLM justification is empty")

        return verdict, justification


class GraphKeyGenerator:
    def assign_keys(self, works: Iterable[Work]) -> Dict[str, str]:
        keys: Dict[str, str] = {}
        counts: Dict[str, int] = {}
        for work in works:
            base = self._base_key(work)
            count = counts.get(base, 0)
            if count == 0:
                key = base
            else:
                key = f"{base}{self._suffix(count)}"
            counts[base] = count + 1
            keys[work.openalex_id] = key
        return keys

    def _base_key(self, work: Work) -> str:
        last_name = self._last_name_from_authors(work.authors)
        if last_name:
            year = work.publication_year if work.publication_year is not None else "0000"
            return f"{last_name}{year}"
        sanitized = re.sub(r"[^A-Za-z0-9]", "", work.openalex_id)
        return sanitized or "Work"

    def _last_name_from_authors(self, authors: List[str]) -> str:
        if not authors:
            return ""
        first_author = authors[0].strip()
        if not first_author:
            return ""
        last_segment = first_author.split()[-1]
        normalized = unicodedata.normalize("NFKD", last_segment)
        ascii_name = "".join(ch for ch in normalized if ch.isalpha())
        if not ascii_name:
            return ""
        return ascii_name[:1].upper() + ascii_name[1:]

    def _suffix(self, value: int) -> str:
        # value >= 1
        letters: List[str] = []
        number = value
        while number > 0:
            number -= 1
            letters.append(chr(ord("a") + number % 26))
            number //= 26
        return "".join(reversed(letters))


class CitationGraphBuilder:
    def build(
        self,
        *,
        seed: Work,
        decisions: Iterable[WorkDecision],
        keys: Dict[str, str],
    ) -> CitationGraph:
        nodes: Dict[str, GraphNode] = {}
        edges: List[Tuple[str, str]] = []

        seed_key = keys[seed.openalex_id]
        nodes[seed_key] = GraphNode(
            work_id=seed.openalex_id,
            title=seed.title,
            role="seed",
            verdict="seed",
        )

        for decision in decisions:
            key = decision.graph_key
            nodes[key] = GraphNode(
                work_id=decision.work.openalex_id,
                title=decision.work.title,
                role=decision.relation,
                verdict=decision.verdict,
            )
            if decision.relation == "reference":
                edges.append((seed_key, key))
            else:
                edges.append((key, seed_key))

        unique_edges = list(dict.fromkeys(edges))
        return CitationGraph(seed_key=seed_key, nodes=nodes, edges=unique_edges)


class OpenAlexResearchOrchestrator:
    def __init__(
        self,
        *,
        service: CachedOpenAlexService,
        relevance_agent: Optional[SimpleThemeRelevanceAgent] = None,
        key_generator: Optional[GraphKeyGenerator] = None,
        graph_builder: Optional[CitationGraphBuilder] = None,
    ):
        self._service = service
        self._relevance_agent = relevance_agent or SimpleThemeRelevanceAgent()
        self._key_generator = key_generator or GraphKeyGenerator()
        self._graph_builder = graph_builder or CitationGraphBuilder()

    def run(self, *, seed_id: str, theme: str) -> OpenAlexResearchResult:
        seed = self._service.get_seed(seed_id)
        references = self._service.get_references(seed_id)
        citations = self._service.get_citations(seed_id)

        all_works: List[Work] = [seed] + references + citations
        keys = self._key_generator.assign_keys(all_works)

        if hasattr(self._relevance_agent, "set_run_context"):
            try:
                self._relevance_agent.set_run_context(seed=seed, theme=theme)
            except TypeError:
                # Backward compat in case agent signature differs
                self._relevance_agent.set_run_context(seed=seed)  # type: ignore[arg-type]

        reference_decisions = self._relevance_agent.evaluate(references, theme=theme, relation="reference")
        citation_decisions = self._relevance_agent.evaluate(citations, theme=theme, relation="citation")

        decisions = reference_decisions + citation_decisions
        for decision in decisions:
            decision.graph_key = keys.get(decision.work.openalex_id, decision.work.openalex_id)

        graph = self._graph_builder.build(seed=seed, decisions=decisions, keys=keys)

        accepted = [decision for decision in decisions if decision.verdict == "accepted"]
        rejected = [decision for decision in decisions if decision.verdict == "rejected"]

        return OpenAlexResearchResult(
            seed=seed,
            theme=theme,
            accepted=accepted,
            rejected=rejected,
            graph=graph,
        )
