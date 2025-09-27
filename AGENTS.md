# Agents Overview

The Semantic Scholar workflow now uses two specialised LangChain-based agents plus a persistence layer. This document captures the moving parts so you can extend them safely.

## Module Layout
- `agents/semantic_scholar/search.py`: thin API client that supports authenticated and unauthenticated access, automatic pagination, and friendly formatting helpers.
- `agents/semantic_scholar/query_agent.py`: builds a LangGraph ReAct agent around the Semantic Scholar tool. It records every tool invocation so downstream components can access raw papers.
- `agents/semantic_scholar/classifier.py`: lightweight classification agent that labels each paper as `strong`, `partial`, or `irrelevant` and emits confidence plus rationale.
- `agents/semantic_scholar/storage.py`: JSON helper that persists runs and paper-level judgements.
- `agents/semantic_scholar/orchestrator.py`: coordinates the two agents, loops through refinement iterations, and stores outputs.
- `agents/semantic_scholar_agent.py`: CLI entry point that wires environment config, creates the agents, and boots the orchestrator.

## Execution Flow
1. CLI loads `.env`, validates `OPENROUTER_API_KEY`, warns if Semantic Scholar key is absent, and instantiates `SemanticScholarClient`.
2. `QueryAgent` (LangGraph `create_react_agent`) receives the user focus and optional feedback, calls the Semantic Scholar tool at least once, and returns both the final message and structured paper metadata captured by the tool wrapper.
3. `ClassificationAgent` runs on each paper, returning JSON with label, confidence, and a brief explanation. Rich renders these decisions in a table for quick scanning.
4. `SemanticScholarOrchestrator` persists the run via `PaperDatabase`, checks whether any `strong` labels were found, and, if not, asks the query agent to suggest a refined search string before the next iteration.
5. The loop stops once a strong hit appears, the iteration cap is reached, or the query agent fails to propose a new query.

## Classification Rubric
- **strong**: paper directly answers the research focus or is foundational evidence; iteration stops once at least one strong hit exists.
- **partial**: tangential relevance or missing critical detail; feedback summarises the gap so a refined query can course-correct.
- **irrelevant**: unrelated or noisy retrieval; logged for auditing but omitted from feedback unless all results are poor.

Confidence is expected to land in `[0.0, 1.0]`. Out-of-range values are clamped before persistence so downstream analytics remain stable.

## Feedback Loop
- `SemanticScholarOrchestrator._build_feedback` aggregates the classifier’s explanations (excluding strong hits) into a compact memo.
- The memo is appended to the next user message for `QueryAgent.run`, nudging the LLM to adjust search keywords, venues, or filters.
- If the refined query echoes the previous query verbatim or comes back empty, iterations halt to avoid infinite loops.

## OpenRouter Integration
- Both agents share OpenRouter credentials but can target different models (`--model` for queries, `--classifier-model` for judgements).
- `agents/semantic_scholar/llm.py` centralises client construction and automatically falls back to `openai_api_base` if needed.
- Temperatures are independently configurable to keep the query agent exploratory while the classifier remains deterministic.

## Semantic Scholar Tooling
- Authenticated path hits `/graph/v1/paper/search` with the `x-api-key` header; unauthenticated path leverages `/graph/v1/paper/search/bulk` with token-based pagination and 100-result safeguards.
- Each tool call logs the textual summary for the LLM and preserves structured `PaperRecord` objects for persistence and classification.
- Rich panels frame the tool call and response, truncating the display to keep the console readable without losing underlying data.

## Persistence Model
- A single JSON document groups two arrays: `runs` summarises each iteration with query text, index, agent summary, feedback, and timestamp; `papers` stores paper-level metadata, classification labels, confidence scores, explanations, and the raw dataclass snapshot.
- `PaperDatabase` initialises the file on first use and can be repointed via the `--db-path` flag or `SEMANTIC_SCHOLAR_DB_PATH`.

## Extensibility Notes
- When adding new tools, extend `QueryAgent` by composing additional `Tool` instances; the orchestrator already handles arbitrary paper lists.
- To plug in alternative classifiers (e.g., embeddings or rule-based filters), implement a drop-in replacement exposing `classify(query=..., paper=...)` that returns a `ClassificationResult`.
- Keep refinements iterative: feed summarised feedback into `QueryAgent.suggest_refined_query` so the language model understands why prior searches failed.
- If you need to capture extra metadata (citations, PDFs, etc.), extend `PaperRecord` and update `PaperDatabase.store_classification` to persist the new fields.

## Coding Style Expectations
- Prefer short, single-purpose modules and functions; decompose complex workflows into composable helpers inside `agents/semantic_scholar/*`.
- Follow DRY principles by centralising shared logic (e.g., response parsing, validation) in well-named utilities instead of re-implementing them in agents.
- Document public functions and classes with concise docstrings that state intent, inputs, and notable side effects; inline comments are reserved for non-obvious control flow.
- Choose pragmatic design patterns (factory functions for tools, strategy-like classifier swaps) when they reduce duplication; avoid over-engineering or speculative abstractions.
- Keep new interfaces specialised for the agents they serve and expose the minimum surface area needed for orchestration and persistence layers.
- Maintain readability by favouring straightforward control flow over clever constructs; prefer explicit data transformations to implicit magic.

## Testing and Validation
- Add or update unit tests under `tests/` whenever agent behaviour or storage contracts change; test new edge cases introduced by refinements or tooling additions.
- Use focused test fixtures that mirror `PaperRecord` and database schemas so regressions in metadata handling surface early.
- Run the existing test suite (`pytest`) before shipping substantial changes and ensure optional dependencies are guarded to keep tests deterministic.
- Validate LangChain integrations with lightweight mocks or recorded responses to avoid brittle network dependencies in CI.
- When modifying CLI wiring, include smoke tests that cover argument parsing, environment validation, and orchestrator bootstrapping paths.
