# AI Scholar

CLI utilities and modular LangChain agents for exploring academic literature with iterative refinement.

## Highlights
- Dual-agent workflow: a query agent drives Semantic Scholar searches while a classifier judges each paper as strongly relevant, partially relevant, or irrelevant.
- Automatic query refinement that keeps searching until a strongly relevant article is located or the iteration budget is reached.
- Persistent SQLite database (`data/search_results.db`) records every run, query, and classification for later auditing.
- Semantic Scholar client supports authenticated and unauthenticated modes with pagination safeguards and Rich-powered console trace.

## Requirements
- Python 3.11+
- Dependencies: `langchain`, `langchain-openai`, `langgraph`, `python-dotenv`, `requests`, `rich`
- OpenRouter account + API key (required)
- Semantic Scholar API key (optional; unauthenticated mode is capped at 100 requests per 5 minutes)

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
| `SEMANTIC_SCHOLAR_LIMIT` | No | Default result cap per query (5).
| `SEMANTIC_SCHOLAR_MAX_ITERATIONS` | No | Default iteration budget (3).
| `SEMANTIC_SCHOLAR_DB_PATH` | No | SQLite path for persistence (`data/search_results.db`).

## Usage
Run the Semantic Scholar workflow from the repository root:

```bash
python agents/semantic_scholar_agent.py "retrieval augmented generation"
```

Useful flags:
- `--classifier-model`: pick a specialised classification model.
- `--iterations`: control how many refinement rounds are allowed.
- `--limit`: maximum papers fetched per query (default 5).
- `--db-path`: point to an alternate SQLite database.

The CLI prints query details, every Semantic Scholar tool invocation, the query agent’s synthesis, and a Rich table of classification decisions. Iterations continue until a “strong” hit appears or the iteration budget is exhausted.

## Results Database
Results are stored in SQLite. Each run logs:
- the executed query and iteration index,
- the query agent’s final summary,
- every paper judged, along with label, confidence, explanation, and the raw payload.

Inspect recent runs with any SQLite browser or by querying the `search_runs` and `papers` tables directly.

Example CLI inspection:

```bash
sqlite3 data/search_results.db 'SELECT id, query, iteration, created_at FROM search_runs ORDER BY id DESC LIMIT 10;'
```

To view just the strongly relevant papers from the latest run:

```bash
sqlite3 data/search_results.db \
  "SELECT title, classification, confidence FROM papers WHERE classification = 'strong' ORDER BY id DESC;"
```

## Troubleshooting
- **`ModuleNotFoundError`**: verify requirements are installed in the active interpreter.
- **OpenRouter failures**: confirm the API key and base URL; OpenRouter occasionally rate-limits free-tier requests.
- **Semantic Scholar 429**: unauthenticated mode is strict. Provide `SEMANTIC_SCHOLAR_API_KEY` or retry later.
- **No strong matches**: increase `--iterations`, broaden the seed query, or inspect stored results to craft a better follow-up.

## Next Steps
- Extend the classifier with domain-specific heuristics or use embeddings for pre-filtering.
- Add export utilities that convert stored runs into markdown briefs or CSV datasets.
