import json
from pathlib import Path

import pytest

from codes.agent_openalex import (
    CitationGraph,
    GraphNode,
    OpenAlexResearchResult,
    Work,
    WorkDecision,
)

from codes.project_repository import ProjectRepository


def _make_result(seed_id: str, theme: str, *, verdict: str, relation: str = "reference") -> OpenAlexResearchResult:
    seed_work = Work(
        openalex_id=seed_id,
        title=f"Seed {seed_id}",
        publication_year=2024,
        authors=["Ada Lovelace"],
        referenced_works=[],
    )
    related_work = Work(
        openalex_id=f"{seed_id}-REF",
        title="Reference paper",
        publication_year=2020,
        authors=["Grace Hopper"],
        referenced_works=[],
        abstract="Example abstract",
    )

    decision = WorkDecision(
        work=related_work,
        verdict=verdict,
        justification="Mock justification",
        relation=relation,
        graph_key=f"{seed_id}_1",
    )

    graph = CitationGraph(
        seed_key=f"SeedKey-{seed_id}",
        nodes={
            f"SeedKey-{seed_id}": GraphNode(
                work_id=seed_id,
                title=f"Seed {seed_id}",
                role="seed",
                verdict="seed",
            ),
            f"{seed_id}_1": GraphNode(
                work_id=related_work.openalex_id,
                title=related_work.title,
                role=relation if relation in {"reference", "citation"} else "reference",
                verdict=verdict if verdict in {"accepted", "rejected"} else "accepted",
            ),
        },
        edges=[(f"SeedKey-{seed_id}", f"{seed_id}_1")],
    )

    accepted = [decision] if verdict == "accepted" else []
    rejected = [decision] if verdict == "rejected" else []

    return OpenAlexResearchResult(
        seed=seed_work,
        theme=theme,
        accepted=accepted,
        rejected=rejected,
        graph=graph,
    )


def test_repository_persists_runs_and_manifest(tmp_path: Path) -> None:
    repo = ProjectRepository(root=tmp_path)
    result = _make_result("W1", "data science", verdict="accepted")

    run_path = repo.save_run("My Project", result)

    assert run_path.exists()
    project_dir = tmp_path / ProjectRepository.slugify("My Project")
    manifest_path = project_dir / "project.json"
    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text("utf-8"))
    assert manifest["theme"] == "data science"
    assert set(manifest["runs"]) == {"W1"}
    assert manifest["runs"]["W1"]["run_file"] == f"runs/{run_path.name}"

    second = _make_result("W2", "data science", verdict="rejected", relation="citation")
    repo.save_run("My Project", second)

    manifest = json.loads(manifest_path.read_text("utf-8"))
    assert set(manifest["runs"].keys()) == {"W1", "W2"}


def test_repository_rejects_theme_mismatch(tmp_path: Path) -> None:
    repo = ProjectRepository(root=tmp_path)
    repo.save_run("Thesis", _make_result("W1", "graph theory", verdict="accepted"))

    with pytest.raises(ValueError):
        repo.save_run("Thesis", _make_result("W2", "machine learning", verdict="accepted"))


def test_repository_loads_project_with_merged_graph(tmp_path: Path) -> None:
    repo = ProjectRepository(root=tmp_path)
    repo.save_run("Consortium", _make_result("S1", "ai", verdict="accepted"))
    repo.save_run("Consortium", _make_result("S2", "ai", verdict="rejected"))

    project = repo.load_project("Consortium")

    assert project.name == "Consortium"
    assert {result.seed.openalex_id for result in project.results} == {"S1", "S2"}

    merged = project.merged_graph
    assert merged.seed_key == project.slug
    assert len(merged.edges) == 2
    assert len(merged.nodes) >= 3
