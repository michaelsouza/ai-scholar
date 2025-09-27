# Agents Overview

This project currently ships a single LangGraph-powered agent focused on Semantic Scholar retrieval. The sections below describe how it is put together and how to extend it safely.

## Execution Flow
- `agents/semantic_scholar_agent.py` loads configuration from `.env`, validates the OpenRouter key, and warns if the Semantic Scholar key is absent.
- A LangGraph prebuilt ReAct agent (`create_react_agent`) is created around a custom tool named `Semantic Scholar Search`.
- Each user query is prefixed with a system message that forces at least one tool call and requests citation-rich answers.
- The agent conversation is streamed, and the final message is rendered with Rich panels while tool inputs/outputs are logged for debugging.

## OpenRouter Integration
- The orchestrating LLM is `ChatOpenAI` configured to hit the OpenRouter base URL (`OPENROUTER_BASE_URL`), defaulting to `x-ai/grok-4-fast:free`.
- Any OpenRouter-compatible model name can be supplied via `--model` or the `OPENROUTER_MODEL` environment variable.
- If the client library expects `openai_api_base`, a compatibility shim falls back automatically.

## Semantic Scholar Tool
- The tool function wraps two code paths:
  - **Authenticated** (`SEMANTIC_SCHOLAR_API_KEY` present): uses `/graph/v1/paper/search` with the `x-api-key` header and obeys the `limit` parameter directly.
  - **Unauthenticated** (no key): uses `/graph/v1/paper/search/bulk`, iterating with pagination tokens until the requested number of papers is gathered. Handles 429 responses with an explanatory message.
- Returned papers are formatted (`title`, `authors`, `venue`, `year`, `url`, `abstract` preview) and joined before being handed back to the LLM.
- Tool invocations and their raw responses (truncated to 1,500 characters) are printed through Rich so operators can verify grounding data.

## System Prompt & Output
- The system prompt instructs the agent to cite Semantic Scholar results, reference venues and years, and mention when unauthenticated limits may affect coverage.
- Rich panels delineate: the query banner, tool call panels, tool result panels, and the final answer.
- If the agent returns structured message content (e.g., chunk lists), the runner flattens it to human-readable text before display.

## Extending the Agent
- Add new tools by defining helper functions inside `build_agent` and appending them to the `tools` list, then updating the system prompt to reference expected usage.
- Consider introducing caching or local persistence if rate limits become a bottleneck; LangGraph supports stateful storage through checkpoints.
- Keep new dependencies minimal and ASCII-only to match repository guidelines.
