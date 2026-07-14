"""
LangChain-facing LLM layer.

* Builds ChatPromptTemplate messages
* Invokes the configured multi-provider backend (Settings) or OpenAI env key
* Tracks approximate token usage for observability
* Soft retries for transient failures
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, TypeVar

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.config import settings
from app.graph.nodes._utils import parse_json_object
from app.models.schemas import ProviderId
from app.providers.factory import ProviderFactory
from app.services.settings_service import settings_repository

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Rough USD estimates for logging only (not billing)
_COST_PER_1K = {
    "default": (0.00015, 0.0006),
}


@dataclass
class UsageEvent:
    node: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    model: str
    provider_id: str


@dataclass
class LLMSession:
    provider_id: str
    model: str
    events: list[UsageEvent] = field(default_factory=list)

    def usage_summary(self) -> dict[str, Any]:
        return {
            "prompt_tokens": sum(e.prompt_tokens for e in self.events),
            "completion_tokens": sum(e.completion_tokens for e in self.events),
            "total_tokens": sum(e.total_tokens for e in self.events),
            "estimated_cost_usd": round(sum(e.estimated_cost_usd for e in self.events), 6),
            "calls": len(self.events),
            "by_node": {
                e.node: {
                    "prompt_tokens": e.prompt_tokens,
                    "completion_tokens": e.completion_tokens,
                    "total_tokens": e.total_tokens,
                    "estimated_cost_usd": e.estimated_cost_usd,
                }
                for e in self.events
            },
        }


def _estimate_tokens(text: str) -> int:
    # Cheap approximation (~4 chars/token) for providers that don't return usage
    return max(1, len(text) // 4)


def _estimate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    inp, out = _COST_PER_1K["default"]
    return (prompt_tokens / 1000) * inp + (completion_tokens / 1000) * out


def _messages_to_strings(messages: list[BaseMessage]) -> tuple[str | None, str]:
    system_parts: list[str] = []
    human_parts: list[str] = []
    for msg in messages:
        content = msg.content if isinstance(msg.content, str) else str(msg.content)
        if isinstance(msg, SystemMessage):
            system_parts.append(content)
        elif isinstance(msg, HumanMessage):
            human_parts.append(content)
        elif isinstance(msg, AIMessage):
            human_parts.append(content)
        else:
            human_parts.append(content)
    system = "\n\n".join(system_parts) if system_parts else None
    user = "\n\n".join(human_parts)
    return system, user


class GraphLLMService:
    """Injectable LLM service used by all nodes."""

    def __init__(self, provider_id: ProviderId | None = None):
        self._provider = None
        self.session = LLMSession(provider_id="unset", model="unset")
        self._resolve(provider_id)

    def _resolve(self, provider_id: ProviderId | None) -> None:
        config = None
        if provider_id:
            config = settings_repository.get(provider_id)
        if not config or not config.api_key or not config.enabled:
            config = settings_repository.get_active_provider()

        if (not config or not config.api_key) and settings.openai_api_key:
            from app.providers.openai_provider import OpenAIProvider

            self._provider = OpenAIProvider(api_key=settings.openai_api_key)
            self.session = LLMSession(provider_id="openai", model=self._provider.model)
            return

        if not config or not config.api_key:
            raise ValueError(
                "No LLM provider configured. Enable a provider in Settings or set OPENAI_API_KEY."
            )

        self._provider = ProviderFactory.create(
            provider_id=config.provider_id,
            api_key=config.api_key,
            model=config.model,
            base_url=config.base_url,
        )
        self.session = LLMSession(
            provider_id=config.provider_id.value,
            model=config.model,
        )

    async def ainvoke_messages(
        self,
        messages: list[BaseMessage],
        *,
        node: str,
        max_tokens: int = 1200,
        retries: int = 2,
    ) -> str:
        assert self._provider is not None
        system, user = _messages_to_strings(messages)
        last_error: Exception | None = None
        for attempt in range(retries + 1):
            try:
                result = await self._provider.generate(
                    user,
                    system_prompt=system,
                    max_tokens=max_tokens,
                )
                text = (result.content or "").strip()
                prompt_tokens = _estimate_tokens((system or "") + user)
                completion_tokens = (
                    result.tokens_used - prompt_tokens
                    if result.tokens_used and result.tokens_used > prompt_tokens
                    else _estimate_tokens(text)
                )
                total = result.tokens_used or (prompt_tokens + completion_tokens)
                event = UsageEvent(
                    node=node,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=max(0, completion_tokens),
                    total_tokens=total,
                    estimated_cost_usd=_estimate_cost(prompt_tokens, max(0, completion_tokens)),
                    model=self.session.model,
                    provider_id=self.session.provider_id,
                )
                self.session.events.append(event)
                logger.info(
                    "llm_call node=%s model=%s tokens=%s cost≈$%.6f attempt=%s",
                    node,
                    self.session.model,
                    total,
                    event.estimated_cost_usd,
                    attempt + 1,
                )
                return text
            except Exception as e:
                last_error = e
                logger.warning("llm_retry node=%s attempt=%s error=%s", node, attempt + 1, e)
                if attempt < retries:
                    await asyncio.sleep(1.5 * (attempt + 1))
        assert last_error is not None
        raise last_error

    async def arun_prompt(
        self,
        prompt: ChatPromptTemplate,
        variables: dict[str, Any],
        *,
        node: str,
        max_tokens: int = 1200,
    ) -> str:
        messages = prompt.format_messages(**variables)
        return await self.ainvoke_messages(messages, node=node, max_tokens=max_tokens)

    async def arun_structured(
        self,
        prompt: ChatPromptTemplate,
        variables: dict[str, Any],
        *,
        schema: type[T],
        node: str,
        max_tokens: int = 900,
        retries: int = 1,
    ) -> T:
        parser: PydanticOutputParser[T] = PydanticOutputParser(pydantic_object=schema)
        vars_with_fmt = {
            **variables,
            "format_instructions": parser.get_format_instructions(),
        }

        last_exc: Exception | None = None
        for attempt in range(retries + 1):
            raw = await self.arun_prompt(
                prompt,
                vars_with_fmt,
                node=node,
                max_tokens=max_tokens,
            )
            try:
                data = parse_json_object(raw)
                return schema.model_validate(data)
            except Exception as first_exc:
                last_exc = first_exc
                try:
                    return parser.parse(raw)
                except Exception as second_exc:
                    last_exc = second_exc
                    logger.warning(
                        "structured_parse_failed node=%s attempt=%s preview=%r",
                        node,
                        attempt + 1,
                        raw[:300],
                    )
                    if attempt < retries:
                        await asyncio.sleep(0.5)

        assert last_exc is not None
        raise ValueError(
            f"Could not parse structured output for {node}. "
            "The model returned invalid JSON."
        ) from last_exc


# Process-local default; nodes can still accept injection later.
_default_llm: GraphLLMService | None = None


def get_llm_service(provider_id: ProviderId | None = None) -> GraphLLMService:
    global _default_llm
    if provider_id is not None:
        return GraphLLMService(provider_id)
    if _default_llm is None:
        _default_llm = GraphLLMService()
    return _default_llm


def reset_llm_service(provider_id: ProviderId | None = None) -> None:
    """Create a fresh LLM session for the next graph run."""
    global _default_llm
    _default_llm = GraphLLMService(provider_id)
