"""JSON persistence for Semantic Scholar agent runs."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .classifier import ClassificationResult


class PaperDatabase:
    """Minimal JSON helper to persist agent runs and paper judgements."""

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._write({"runs": [], "papers": []})

    # ------------------------------------------------------------------
    def _read(self) -> Dict[str, Any]:
        if not self._path.exists():  # pragma: no cover - defensive guard
            return {"runs": [], "papers": []}
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"PaperDatabase file {self._path} is not valid JSON. Delete or fix the file."
            ) from exc
        data.setdefault("runs", [])
        data.setdefault("papers", [])
        return data

    def _write(self, payload: Dict[str, Any]) -> None:
        self._path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _next_id(items: List[Dict[str, Any]]) -> int:
        if not items:
            return 1
        return max(item.get("id", 0) for item in items) + 1

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        )

    # ------------------------------------------------------------------
    def log_run(
        self,
        *,
        query: str,
        iteration: int,
        agent_summary: Optional[str],
        feedback: Optional[str] = None,
    ) -> int:
        data = self._read()
        runs: List[Dict[str, Any]] = data["runs"]
        run_id = self._next_id(runs)
        runs.append(
            {
                "id": run_id,
                "query": query,
                "iteration": iteration,
                "agent_summary": agent_summary,
                "feedback": feedback,
                "created_at": self._utc_now(),
            }
        )
        self._write(data)
        return run_id

    def store_classification(self, run_id: int, result: ClassificationResult) -> None:
        paper = result.paper
        data = self._read()
        papers: List[Dict[str, Any]] = data["papers"]
        paper_id = self._next_id(papers)
        papers.append(
            {
                "id": paper_id,
                "run_id": run_id,
                "paper_id": paper.paper_id,
                "title": paper.title,
                "year": paper.year,
                "venue": paper.venue,
                "url": paper.url,
                "authors": list(paper.authors),
                "abstract": paper.abstract,
                "classification": result.label,
                "confidence": result.confidence,
                "explanation": result.explanation,
                "raw_payload": asdict(result),
            }
        )
        self._write(data)

    # Convenience helpers ------------------------------------------------
    def last_runs(self, limit: int = 5) -> list[tuple]:
        data = self._read()
        runs = sorted(data["runs"], key=lambda item: item.get("id", 0), reverse=True)
        trimmed = runs[:limit]
        return [
            (
                entry.get("id"),
                entry.get("query"),
                entry.get("iteration"),
                entry.get("agent_summary"),
                entry.get("created_at"),
            )
            for entry in trimmed
        ]
