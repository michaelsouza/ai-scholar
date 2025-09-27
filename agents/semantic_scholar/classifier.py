"""Classification agent that scores paper relevance."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rich.console import Console

from .llm import build_openrouter_chat
from .search import PaperRecord


@dataclass
class ClassificationResult:
    """Structured output from the classification agent."""

    paper: PaperRecord
    label: str
    confidence: float
    explanation: str

    @property
    def is_strong(self) -> bool:
        return self.label.lower() == "strong"


class ClassificationAgent:
    """Agent that labels Semantic Scholar papers as strongly relevant or not."""

    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        base_url: str,
        temperature: float = 0.0,
        console: Optional[Console] = None,
    ) -> None:
        self._console = console or Console()
        self._llm = build_openrouter_chat(
            model=model,
            temperature=temperature,
            api_key=api_key,
            base_url=base_url,
        )
        self._chain = (
            ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You judge whether an academic paper is strongly relevant to a research focus. "
                        "Respond in compact JSON with keys: label (strong|partial|irrelevant), "
                        "confidence (0.0-1.0), explanation (short factual rationale).",
                    ),
                    (
                        "human",
                        "Research focus: {query}\n"
                        "Title: {title}\n"
                        "Authors: {authors}\n"
                        "Venue: {venue}\n"
                        "Year: {year}\n"
                        "Abstract: {abstract}",
                    ),
                ]
            )
            | self._llm
            | StrOutputParser()
        )

    def classify(self, *, query: str, paper: PaperRecord) -> ClassificationResult:
        """Return a ClassificationResult for the supplied paper."""

        abstract = (paper.abstract or "").strip()
        if len(abstract) > 1200:
            abstract = abstract[:1200] + "…"

        raw = self._chain.invoke(
            {
                "query": query,
                "title": paper.title,
                "authors": ", ".join(paper.authors) or "Unknown",
                "venue": paper.venue or "Unknown venue",
                "year": paper.year or "Unknown year",
                "abstract": abstract or "No abstract provided.",
            }
        )

        label = "partial"
        confidence = 0.5
        explanation = raw.strip()
        try:
            parsed = json.loads(raw)
            label = str(parsed.get("label", label)).lower()
            confidence = float(parsed.get("confidence", confidence))
            explanation = str(parsed.get("explanation", explanation)).strip()
        except json.JSONDecodeError:
            # Fall back to simple heuristics when JSON fails.
            label = "strong" if "strong" in raw.lower() else label
            explanation = raw.strip() or explanation

        return ClassificationResult(
            paper=paper,
            label=label,
            confidence=max(0.0, min(1.0, confidence)),
            explanation=explanation,
        )
