"""Helpers for constructing LLM clients."""

from __future__ import annotations

from typing import Any

try:
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - fallback for older LangChain installs
    from langchain.chat_models import ChatOpenAI  # type: ignore


def build_openrouter_chat(
    *,
    model: str,
    temperature: float,
    api_key: str,
    base_url: str,
    **extra: Any,
) -> ChatOpenAI:
    """Instantiate a ChatOpenAI client configured for OpenRouter."""

    kwargs: dict[str, Any] = {
        "model": model,
        "temperature": temperature,
        "openai_api_key": api_key,
        **extra,
    }
    try:
        return ChatOpenAI(base_url=base_url, **kwargs)
    except TypeError:
        kwargs.setdefault("openai_api_base", base_url)
        return ChatOpenAI(**kwargs)
