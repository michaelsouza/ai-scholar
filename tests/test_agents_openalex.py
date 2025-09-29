import os

import pytest
import requests

import codes.agent_openalex as agent


SEED_ID = "W2002097905"
THEME = "machine learning"


@pytest.fixture(scope="module")
def openalex_live_enabled():
    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        pytest.skip("Live OpenAlex integration tests disabled")


def test_orchestrator_builds_live_graph(openalex_live_enabled, tmp_path):
    cache_path = tmp_path / "openalex_cache.json"
    client = agent.OpenAlexHttpClient(max_citations=40, citation_page_size=40)
    service = agent.CachedOpenAlexService(client=client, cache=agent.JsonFileCache(cache_path))
    orchestrator = agent.OpenAlexResearchOrchestrator(service=service)

    result = orchestrator.run(seed_id=SEED_ID, theme=THEME)

    assert result.seed.openalex_id == SEED_ID
    assert result.decisions, "Expected at least one decision from references or citations"
    assert all(decision.justification for decision in result.decisions)
    assert result.graph.nodes[result.graph.seed_key].verdict == "seed"
    assert result.graph.edges, "Citation graph should include edges for references/citations"
    assert cache_path.exists()


class _FailingSession(requests.Session):
    def __init__(self):
        super().__init__()

    def get(self, *args, **kwargs):  # noqa: D401 - simple override
        raise AssertionError("Unexpected network request while using cached data")


def test_cached_service_reuses_live_data(openalex_live_enabled, tmp_path):
    cache_path = tmp_path / "openalex_cache.json"

    warm_client = agent.OpenAlexHttpClient(max_citations=40, citation_page_size=40)
    warm_service = agent.CachedOpenAlexService(client=warm_client, cache=agent.JsonFileCache(cache_path))
    orchestrator = agent.OpenAlexResearchOrchestrator(service=warm_service)
    orchestrator.run(seed_id=SEED_ID, theme=THEME)

    offline_client = agent.OpenAlexHttpClient(session=_FailingSession())
    cached_service = agent.CachedOpenAlexService(client=offline_client, cache=agent.JsonFileCache(cache_path))

    seed = cached_service.get_seed(SEED_ID)
    refs = cached_service.get_references(SEED_ID)
    cits = cached_service.get_citations(SEED_ID)

    assert seed.openalex_id == SEED_ID
    assert refs, "References should be loaded from cache"
    assert cits, "Citations should be loaded from cache"


def test_graph_key_generator_handles_collisions_and_missing_metadata():
    works = [
        agent.Work(
            openalex_id="W1",
            title="Paper A",
            publication_year=2020,
            authors=["Jane Smith"],
            referenced_works=[],
        ),
        agent.Work(
            openalex_id="W2",
            title="Paper B",
            publication_year=2020,
            authors=["John Smith"],
            referenced_works=[],
        ),
        agent.Work(
            openalex_id="W3",
            title="Paper C",
            publication_year=2020,
            authors=["Jane Smith"],
            referenced_works=[],
        ),
        agent.Work(
            openalex_id="W4",
            title="Paper D",
            publication_year=None,
            authors=[],
            referenced_works=[],
        ),
    ]

    generator = agent.GraphKeyGenerator()
    mapping = generator.assign_keys(works)

    assert mapping["W1"] == "Smith2020"
    assert mapping["W2"] == "Smith2020a"
    assert mapping["W3"] == "Smith2020b"
    assert mapping["W4"].startswith("W4")
