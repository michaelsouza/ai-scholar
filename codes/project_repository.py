from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from codes.agent_openalex import (
    CitationGraph,
    GraphNode,
    OpenAlexResearchResult,
)


@dataclass
class ProjectData:
    name: str
    slug: str
    theme: str
    manifest_path: Path
    runs: Dict[str, Path]
    results: List[OpenAlexResearchResult]

    @property
    def merged_graph(self) -> CitationGraph:
        return _merge_graphs((result.graph for result in self.results), seed_key=self.slug)


class ProjectRepository:
    def __init__(self, *, root: Path | str = Path("data/projects")) -> None:
        self._root = Path(root)

    def save_run(self, project: str, result: OpenAlexResearchResult) -> Path:
        slug = self.slugify(project)
        project_dir = self._root / slug
        runs_dir = project_dir / "runs"
        runs_dir.mkdir(parents=True, exist_ok=True)

        manifest_path = project_dir / "project.json"
        manifest = self._load_manifest(manifest_path)

        if manifest is None:
            manifest = {
                "name": project,
                "slug": slug,
                "theme": result.theme,
                "runs": {},
            }
        else:
            stored_theme = manifest.get("theme")
            if stored_theme and stored_theme != result.theme:
                raise ValueError(
                    "Project theme mismatch: existing theme is '%s' but run was executed with '%s'"
                    % (stored_theme, result.theme)
                )
            manifest.setdefault("name", project)
            manifest.setdefault("slug", slug)
            manifest.setdefault("runs", {})

        run_filename = _sanitize_filename(result.seed.openalex_id) + ".json"
        run_path = runs_dir / run_filename

        run_payload = result.to_dict()
        run_payload["project"] = {"name": project, "slug": slug}
        run_payload["generated_at"] = _utc_now_iso()

        run_path.write_text(json.dumps(run_payload, indent=2, ensure_ascii=False), encoding="utf-8")

        manifest["runs"][result.seed.openalex_id] = {
            "seed_id": result.seed.openalex_id,
            "run_file": f"runs/{run_filename}",
            "updated_at": _utc_now_iso(),
        }

        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        return run_path

    def load_project(self, project: str) -> ProjectData:
        slug = self.slugify(project)
        project_dir = self._root / slug
        manifest_path = project_dir / "project.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Project '{project}' not found at {manifest_path}")

        manifest = json.loads(manifest_path.read_text("utf-8"))
        runs_meta = manifest.get("runs", {})
        results: List[OpenAlexResearchResult] = []
        run_paths: Dict[str, Path] = {}
        for seed_id, meta in runs_meta.items():
            if not isinstance(meta, dict):
                continue
            rel_path = meta.get("run_file")
            if not isinstance(rel_path, str):
                continue
            path = project_dir / rel_path
            run_paths[str(seed_id)] = path
            if not path.exists():
                continue
            payload = json.loads(path.read_text("utf-8"))
            results.append(OpenAlexResearchResult.from_dict(payload))

        return ProjectData(
            name=str(manifest.get("name", project)),
            slug=str(manifest.get("slug", slug)),
            theme=str(manifest.get("theme", "")),
            manifest_path=manifest_path,
            runs=run_paths,
            results=results,
        )

    def _load_manifest(self, path: Path) -> Dict[str, object] | None:
        if not path.exists():
            return None
        return json.loads(path.read_text("utf-8"))

    @staticmethod
    def slugify(name: str) -> str:
        normalized = unicodedata.normalize("NFKD", name)
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text).strip("-")
        slug = slug.lower() or "project"
        return slug


def _sanitize_filename(identifier: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", identifier)
    return safe.strip("_.") or "openalex_run"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _merge_graphs(graphs: Iterable[CitationGraph], *, seed_key: str) -> CitationGraph:
    combined_nodes: Dict[str, GraphNode] = {}
    combined_edges: List[Tuple[str, str]] = []
    seen_edges = set()
    for graph in graphs:
        for node_id, node in graph.nodes.items():
            combined_nodes.setdefault(node_id, node)
        for edge in graph.edges:
            key = (edge[0], edge[1])
            if key in seen_edges:
                continue
            seen_edges.add(key)
            combined_edges.append(key)
    return CitationGraph(seed_key=seed_key, nodes=combined_nodes, edges=combined_edges)
