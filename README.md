# AI Scholar

CLI utilities and LangChain/LangGraph agents for exploring academic literature.

## Highlights
- Searches Semantic Scholar with or without an API key and automatically handles pagination limits.
- Uses OpenRouter (Grok 4 Fast by default) to orchestrate a ReAct-style workflow over the Semantic Scholar tool.
- Rich-powered console output surfaces prompts, tool calls, and final answers in a readable layout.
- Simple CLI interface with environment-driven configuration for quick experiments or scripting.

## Requirements
- Python 3.11+
- Dependencies: `langchain`, `langchain-openai`, `langgraph`, `python-dotenv`, `requests`, `rich`
- OpenRouter account + API key (required)
- Semantic Scholar API key (optional, but recommended to avoid low unauthenticated rate limits)

## Installation
1. Clone the repository and enter the project directory.
2. (Optional) Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install langchain langchain-openai langgraph python-dotenv requests rich
   ```

## Configuration
Set the necessary environment variables in `.env` or your shell. The agent automatically loads `.env` via `python-dotenv`.

| Variable | Required | Description |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | Yes | OpenRouter key used by `ChatOpenAI`.
| `OPENROUTER_MODEL` | No | Defaults to `x-ai/grok-4-fast:free`. Override to target other OpenRouter models.
| `OPENROUTER_BASE_URL` | No | Defaults to `https://openrouter.ai/api/v1`.
| `SEMANTIC_SCHOLAR_API_KEY` | No | Enables authenticated requests with higher limits. Leave unset to use unauthenticated mode (100 req / 5 min).
| `SEMANTIC_SCHOLAR_LIMIT` | No | Default result cap (5) when the `--limit` flag is omitted.

## Usage
Run the Semantic Scholar agent from the repository root:

```bash
python agents/semantic_scholar_agent.py "retrieval augmented generation"
```

Key flags:
- `--model`: override the OpenRouter model name.
- `--temperature`: adjust sampling (defaults to 0.0).
- `--base-url`: switch to another OpenRouter-compatible endpoint.
- `--limit`: set the maximum number of papers to retrieve.

The CLI prints each tool invocation, the raw Semantic Scholar response (truncated for readability), and the final agent answer inside Rich panels.

## Troubleshooting
- **`ModuleNotFoundError`**: verify the dependency list above is installed in the active environment.
- **OpenRouter connectivity errors**: check VPN/firewall settings and confirm the API key is valid.
- **Semantic Scholar 429 responses**: unauthenticated mode is limited to 100 requests per 5 minutes. Add `SEMANTIC_SCHOLAR_API_KEY` or wait before retrying.
- **No papers retrieved**: try a different query or increase the `--limit` (up to Semantic Scholar caps).

## Next Steps
- Extend the agent with additional tools (e.g., PDF summarization) in `agents/`.
- Wrap the CLI in a web or notebook interface for richer exploration.
