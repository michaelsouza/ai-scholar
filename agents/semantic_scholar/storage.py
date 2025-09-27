"""SQLite persistence for Semantic Scholar agent runs."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from .classifier import ClassificationResult

CREATE_RUNS = """
CREATE TABLE IF NOT EXISTS search_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    iteration INTEGER NOT NULL,
    agent_summary TEXT,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_PAPERS = """
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    paper_id TEXT,
    title TEXT,
    year INTEGER,
    venue TEXT,
    url TEXT,
    authors TEXT,
    abstract TEXT,
    classification TEXT,
    confidence REAL,
    explanation TEXT,
    raw_payload TEXT,
    FOREIGN KEY(run_id) REFERENCES search_runs(id) ON DELETE CASCADE
);
"""


class PaperDatabase:
    """Minimal SQLite helper to persist agent runs and paper judgements."""

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    # ------------------------------------------------------------------
    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._path)

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute(CREATE_RUNS)
            conn.execute(CREATE_PAPERS)

    # ------------------------------------------------------------------
    def log_run(
        self,
        *,
        query: str,
        iteration: int,
        agent_summary: Optional[str],
        feedback: Optional[str] = None,
    ) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO search_runs (query, iteration, agent_summary, feedback)
                VALUES (?, ?, ?, ?)
                """,
                (query, iteration, agent_summary, feedback),
            )
            return int(cursor.lastrowid)

    def store_classification(self, run_id: int, result: ClassificationResult) -> None:
        paper = result.paper
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO papers (
                    run_id, paper_id, title, year, venue, url,
                    authors, abstract, classification, confidence, explanation, raw_payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    paper.paper_id,
                    paper.title,
                    paper.year,
                    paper.venue,
                    paper.url,
                    json.dumps(paper.authors, ensure_ascii=False),
                    paper.abstract,
                    result.label,
                    result.confidence,
                    result.explanation,
                    json.dumps(asdict(result), ensure_ascii=False),
                ),
            )

    # Convenience helpers ------------------------------------------------
    def last_runs(self, limit: int = 5) -> list[tuple]:
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT id, query, iteration, agent_summary, created_at FROM search_runs ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            return list(cursor.fetchall())
