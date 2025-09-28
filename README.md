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
The project includes a comprehensive test suite in the `tests/` directory, separating fast unit tests from network-dependent integration tests.

To run the fast unit tests, which validate local logic without network calls, simply use:
```bash
pytest
```

### Live Integration Tests
The suite also includes tests that interact with live external APIs. These are skipped by default.

To run them, create a `.env` file in the project root (if you haven't already) and add `RUN_LIVE_API_TESTS=1`. You must also provide the necessary API keys in this file. `pytest` will automatically load the file and run the full test suite.

### Test Suite Structure
- **`test_agents_logic.py`**: Unit tests for the internal logic of the classification and orchestration agents.
- **`test_search_client.py`**: Unit tests for the `SemanticScholarClient` and `GoogleScholarClient`, using mock network sessions.
- **`test_related_harvester.py`**: Unit tests for the logic of finding related papers (references and citations).
- **`test_storage_json.py`**: Tests the `PaperDatabase` class for logging results to a JSON file.
- **`test_usage_arxiv_library.py`**: Live integration tests for the arXiv API, verifying searches and metadata parsing, including abstracts.
- **`test_usage_google_scholar_api.py`**: Live integration tests for Google Scholar via SerpAPI. Checks search functionality and parsing of key metadata like abstracts and citation counts.
- **`test_usage_openalex_api.py`**: Live integration tests for the OpenAlex API. Validates metadata fetching, including abstracts, citation counts, and references.
- **`test_usage_semanticscholar_library.py`**: Live integration test for the `semanticscholar` library. Retrieves a known paper to validate all its core metadata (abstract, citation/reference counts) and relations (citations/references).
- **`test_live_services.py`**: Simple "smoke tests" that check the availability of the core external services.

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
