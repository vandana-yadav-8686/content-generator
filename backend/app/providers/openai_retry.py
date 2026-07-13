"""429 retry helper for OpenAI-compatible APIs (Groq, OpenRouter, etc.)."""

import asyncio
import re
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")

MAX_RETRIES = 5
BASE_DELAY_SEC = 3


def _retry_delay(attempt: int, error_msg: str) -> float:
    match = re.search(r"try again in (\d+(?:\.\d+)?)\s*s", error_msg, re.IGNORECASE)
    if match:
        return float(match.group(1)) + 1.0
    return BASE_DELAY_SEC * (2**attempt)


def _is_rate_limit_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "429" in msg or "rate limit" in msg or "too many requests" in msg


async def with_rate_limit_retry(
    fn: Callable[[], Awaitable[T]],
    *,
    label: str = "request",
) -> T:
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            return await fn()
        except Exception as e:
            last_error = e
            if _is_rate_limit_error(e) and attempt < MAX_RETRIES - 1:
                delay = _retry_delay(attempt, str(e))
                await asyncio.sleep(delay)
                continue
            raise
    raise last_error  # type: ignore[misc]


async def stream_openai_chat_with_retry(
    client,
    *,
    model: str,
    messages: list[dict],
    max_tokens: int | None = None,
    temperature: float = 0.5,
) -> AsyncIterator[str]:
    """Stream with one retry on 429 (restart full stream)."""
    from app.providers.openai_stream import stream_openai_chat

    for attempt in range(MAX_RETRIES):
        try:
            async for chunk in stream_openai_chat(
                client,
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            ):
                yield chunk
            return
        except Exception as e:
            if _is_rate_limit_error(e) and attempt < MAX_RETRIES - 1:
                await asyncio.sleep(_retry_delay(attempt, str(e)))
                continue
            raise
