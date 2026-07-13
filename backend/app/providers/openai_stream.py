"""Shared OpenAI-compatible streaming helper."""

from collections.abc import AsyncIterator

from openai import AsyncOpenAI


async def stream_openai_chat(
    client: AsyncOpenAI,
    *,
    model: str,
    messages: list[dict],
    max_tokens: int | None = None,
    temperature: float = 0.5,
) -> AsyncIterator[str]:
    kwargs: dict = {"model": model, "messages": messages, "stream": True, "temperature": temperature}
    if max_tokens:
        kwargs["max_tokens"] = max_tokens

    stream = await client.chat.completions.create(**kwargs)
    async for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        if delta:
            yield delta
