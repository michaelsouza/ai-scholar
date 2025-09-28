# AI Scholar

CLI utilities and modular LangChain agents for exploring academic literature with iterative refinement.

## Highlights
- Dual-agent workflow: a query agent drives Semantic Scholar searches while a classifier judges each paper as strongly relevant, partially relevant, or irrelevant.
- Optional Google Scholar coverage via SerpAPI-backed provider to widen search results.
- Automatic query refinement that keeps searching until a strongly relevant article is located or the iteration budget is reached.
- Relationship expansion that follows Semantic Scholar references (and optional citations) to surface additional leads from promising papers.
- Persistent JSON log (`data/search_results.json`) records every run, query, and classification for later auditing.
- Semantic Scholar client supports authenticated and unauthenticated modes with pagination safeguards and Rich-powered console trace.

## Requirements
- Python 3.11+
- Dependencies: `langchain`, `langchain-openai`, `langgraph`, `python-dotenv`, `requests`, `rich`
- OpenRouter account + API key (required)
- Semantic Scholar API key (optional; unauthenticated mode is capped at 100 requests per 5 minutes)
- SerpAPI API key (optional; enables Google Scholar results)

## Installation
1. Clone the repository and enter the project directory.
2. Install dependencies for the system interpreter (no virtualenv required):

   ```bash
   pip install langchain langchain-openai langgraph python-dotenv requests rich
   ```

   > Tip: Run `python -m pip install --upgrade pip` first if you encounter install errors.
3. Copy your `.env` template (see *Configuration*) and fill in the required keys.

## Configuration
Populate a `.env` file (or export variables in your shell). The CLI loads it automatically via `python-dotenv`.

| Variable | Required | Description |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | Yes | OpenRouter key used by both agents.
| `OPENROUTER_MODEL` | No | Defaults to `x-ai/grok-4-fast:free` for the query agent.
| `OPENROUTER_CLASSIFIER_MODEL` | No | Override model for the classifier (defaults to the query model).
| `OPENROUTER_BASE_URL` | No | Defaults to `https://openrouter.ai/api/v1`.
| `OPENROUTER_TEMPERATURE` | No | Default temperature for the query agent (0.0).
| `CLASSIFIER_TEMPERATURE` | No | Temperature for the classifier agent (0.0).
| `SEMANTIC_SCHOLAR_API_KEY` | No | Enables authenticated requests with higher limits.
| `SERPAPI_API_KEY` / `GOOGLE_SCHOLAR_API_KEY` | No | Enables Google Scholar results through SerpAPI.
| `SEMANTIC_SCHOLAR_LIMIT` | No | Default result cap per query (5).
| `SEMANTIC_SCHOLAR_MAX_ITERATIONS` | No | Default iteration budget (3).
| `SEMANTIC_SCHOLAR_DB_PATH` | No | JSON path for persistence (`data/search_results.json`).
| `SEMANTIC_SCHOLAR_RELATED_LIMIT` | No | Default number of references/citations pulled per seed paper (3).

## Usage
Run the scholarly search workflow from the repository root:

```bash
python agents/scholarly_search_agent.py "retrieval augmented generation"
```

Useful flags:
- `--serpapi-api-key`: supply a SerpAPI key to include Google Scholar alongside Semantic Scholar (alias: --google-scholar-api-key).
- `--classifier-model`: pick a specialised classification model.
- `--iterations`: control how many refinement rounds are allowed.
- `--limit`: maximum papers fetched per query (default 5).
- `--db-path`: point to an alternate JSON log.
- `--related-limit`: cap how many references/citations are harvested per promising paper (default 3).
- `--include-citations`: expand discovery with citing papers in addition to references.
- `--no-related-expansion`: skip the relationship expansion step entirely.

The CLI prints query details, every Semantic Scholar or Google Scholar tool invocation, the query agent’s synthesis, and Rich tables of classification decisions. When enabled (default), the workflow also explores references—and optionally citations—for partially relevant papers before moving on. Iterations continue until a “strong” hit appears or the iteration budget is exhausted.

## Testing
The project includes a comprehensive test suite in the `tests/` directory.

To run the fast unit tests, which validate local logic and client wiring without network calls, use:
```bash
pytest
```

### Live Integration Tests
The suite also includes tests that interact with live external APIs (Semantic Scholar, Google Scholar/SerpAPI, arXiv, OpenAlex) to ensure integrations are working correctly. These are skipped by default to keep the standard test run fast and reliable.

To run them, set the `RUN_LIVE_API_TESTS=1` environment variable and ensure the necessary API keys (`SEMANTIC_SCHOLAR_API_KEY`, `SERPAPI_API_KEY`) are configured in your `.env` file.

```bash
RUN_LIVE_API_TESTS=1 pytest
```

### Test Suite Structure
- **`test_agents_logic.py`**: Unit tests for the internal logic of the classification and orchestration agents. It verifies that agents correctly process simulated model outputs and build feedback summaries.
- **`test_search_client.py`**: Unit tests for the `SemanticScholarClient` and `GoogleScholarClient`. These tests use mock network sessions to ensure that API requests are built correctly and that responses are parsed as expected, without making real network calls.
- **`test_related_harvester.py`**: Unit tests for the `RelatedPaperHarvester`, which is responsible for finding related papers (references and citations). It uses a stub client to test the harvesting logic in isolation.
- **`test_storage_json.py`**: Tests the `PaperDatabase` class, ensuring that search runs and classification results are correctly logged to the JSON database file.
- **`test_arxiv_library_usage.py`**: Live integration tests for the arXiv API. These tests verify that keyword searches, ID lookups, and author queries work correctly against the live service.
- **`test_google_scholar_api_usage.py`**: Live integration tests for the Google Scholar search via SerpAPI. It checks search functionality, result limiting, and data parsing.
- **`test_openalex_api_usage.py`**: Live integration tests for the OpenAlex API, covering keyword and author searches, DOI lookups, and validation of response data.
- **`test_semanticscholar_library_usage.py`**: Tests the direct usage of the `semanticscholar` library, including a live test to retrieve a known paper.
- **`test_live_services.py`**: Contains simple "smoke tests" that check the availability of the core external services (Semantic Scholar and SerpAPI).

## Results Log
Results are stored in a human-readable JSON document. Each run logs:
- the executed query and iteration index,
- the query agent’s final summary,
- every paper judged, along with label, confidence, explanation, and the raw payload.

Open `data/search_results.json` in any editor or use `jq` to inspect the latest runs:

```bash
jq '.runs | sort_by(-.id)[:5]' data/search_results.json
```

## Troubleshooting
- **`ModuleNotFoundError`**: verify requirements are installed in the active interpreter.
- **OpenRouter failures**: confirm the API key and base URL; OpenRouter occasionally rate-limits free-tier requests.
- **Semantic Scholar 429**: unauthenticated mode is strict. Provide `SEMANTIC_SCHOLAR_API_KEY` or retry later.
- **No strong matches**: increase `--iterations`, broaden the seed query, or inspect stored results to craft a better follow-up.

## Next Steps
- Extend the classifier with domain-specific heuristics or use embeddings for pre-filtering.
- Add export utilities that convert stored runs into markdown briefs or CSV datasets.
