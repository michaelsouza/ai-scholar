"""Query agent responsible for interacting with scholarly search providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Sequence

from langchain.agents import Tool
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .llm import build_openrouter_chat
from .search import (
    PaperRecord,
    ProviderResult,
    SearchProvider,
    format_provider_results,
)


@dataclass
class QueryAgentConfig:
    """Configuration options for the query agent."""

    model: str
    temperature: float
    api_key: str
    base_url: str
    result_limit: int
    max_tool_chars: int = 1600
    system_prompt: str = (
        "You are an academic research assistant focused on finding highly relevant "
        "papers across scholarly databases. Always call the Scholarly Search tool at "
        "least once before responding; it combines Semantic Scholar and Google Scholar "
        "results. Cite titles, venues, and publication years in your answer and "
        "explicitly note if any provider limits the returned results."
    )


@dataclass
class QueryAgentRun:
    """Structured output from a query-agent invocation."""

    final_message: str
    papers: List[PaperRecord]
    tool_calls: List[dict]
    messages: List[BaseMessage]


class MultiSourceSearchTool:
    """LangChain tool wrapper that aggregates multiple scholarly providers."""

    def __init__(
        self,
        providers: Sequence[SearchProvider],
        console: Console,
        *,
        result_limit: int,
        max_chars: int,
    ) -> None:
        if not providers:
            raise ValueError("At least one search provider is required.")
        self._providers = list(providers)
        self._console = console
        self._limit = result_limit
        self._max_chars = max_chars
        self.history: List[dict[str, Any]] = []

    def reset(self) -> None:
        self.history.clear()

    def __call__(self, query: str) -> str:
        self._console.print(
            Panel.fit(
                Text(query, style="bold"),
                title="Tool Call • Scholarly Search",
                border_style="blue",
            )
        )

        provider_results: List[ProviderResult] = []
        aggregated: List[PaperRecord] = []

        for provider in self._providers:
            try:
                papers = provider.search(query, limit=self._limit)
                provider_results.append(ProviderResult(provider=provider.name, papers=papers))
                aggregated.extend(papers)
            except Exception as error:  # pragma: no cover - provider errors depend on network
                message = str(error) or error.__class__.__name__
                provider_results.append(ProviderResult(provider=provider.name, papers=[], error=message))

        formatted = format_provider_results(provider_results)
        display = (
            formatted if len(formatted) <= self._max_chars else formatted[: self._max_chars] + "… [truncated]"
        )

        self._console.print(
            Panel.fit(
                display,
                title="Tool Result • Scholarly Search",
                border_style="bright_blue",
            )
        )
        self.history.append(
            {
                "query": query,
                "papers": aggregated,
                "providers": [
                    {
                        "provider": result.provider,
                        "papers": list(result.papers),
                        "error": result.error,
                    }
                    for result in provider_results
                ],
            }
        )
        return formatted


class QueryAgent:
    """Agent responsible for conducting searches and summarising findings."""

    def __init__(
        self,
        *,
        config: QueryAgentConfig,
        providers: Sequence[SearchProvider],
        console: Optional[Console] = None,
    ) -> None:
        self._console = console or Console()
        self._llm = build_openrouter_chat(
            model=config.model,
            temperature=config.temperature,
            api_key=config.api_key,
            base_url=config.base_url,
        )
        self._search_tool = MultiSourceSearchTool(
            providers,
            self._console,
            result_limit=config.result_limit,
            max_chars=config.max_tool_chars,
        )
        tool = Tool(
            name="Scholarly Search",
            func=self._search_tool,
            description=(
                "Use this tool to retrieve academic papers from multiple scholarly databases, including "
                "Semantic Scholar and Google Scholar, with structured metadata."
            ),
        )
        self._agent = create_react_agent(self._llm, tools=[tool])
        self._system_prompt = config.system_prompt

    def run(
        self,
        *,
        search_query: str,
        feedback: Optional[str] = None,
    ) -> QueryAgentRun:
        """Execute the query agent with optional feedback from prior iterations."""

        self._search_tool.reset()
        prompt_lines = [
            f"Search focus: {search_query.strip()}",
            "Construct queries that maximise the chance of finding strongly relevant scholarly work.",
        ]
        if feedback:
            prompt_lines.append(
                "Feedback about previous attempts (address these issues):\n" + feedback.strip()
            )
        prompt_lines.append(
            "Provide a concise synthesis that references each promising paper you retrieve."
        )

        system_message = SystemMessage(content=self._system_prompt)
        human_message = HumanMessage(content="\n\n".join(prompt_lines))

        result = self._agent.invoke({"messages": [system_message, human_message]})
        messages: List[BaseMessage]
        if isinstance(result, dict) and "messages" in result:
            messages = result["messages"]
        elif isinstance(result, list):
            messages = result
        else:
            messages = [result]  # type: ignore[list-item]

        final_content = ""
        if messages:
            last_message = messages[-1]
            content = getattr(last_message, "content", "")
            if isinstance(content, list):
                final_content = "\n".join(
                    item.get("text", str(item)) if isinstance(item, dict) else str(item)
                    for item in content
                )
            else:
                final_content = str(content)

        papers: List[PaperRecord] = []
        for entry in self._search_tool.history:
            papers.extend(entry.get("papers", []))

        return QueryAgentRun(
            final_message=final_content or "",
            papers=papers,
            tool_calls=self._search_tool.history.copy(),
            messages=messages,
        )

    def suggest_refined_query(
        self,
        *,
        previous_query: str,
        feedback: str,
    ) -> str:
        """Ask the underlying LLM for a revised search query."""

        prompt = (
            "You are optimising scholarly search queries for Semantic Scholar and Google Scholar.\n"
            f"The last query was: {previous_query}\n"
            f"Feedback about the results: {feedback}\n"
            "Suggest a single improved search query string that will likely surface more relevant papers."
        )
        response = self._llm.invoke(prompt)
        content = getattr(response, "content", str(response))
        if isinstance(content, list):
            # ChatOpenAI sometimes returns list of dicts; flatten
            content = "\n".join(
                item.get("text", str(item)) if isinstance(item, dict) else str(item)
                for item in content
            )
        return str(content).strip()
