import time
from openai import AsyncOpenAI

from app.providers.base import LLMProvider, ProviderMetadata, GenerationResult, TestResult, text_models
from app.providers.openai_retry import stream_openai_chat_with_retry, with_rate_limit_retry
from app.providers.openai_stream import stream_openai_chat


class GroqProvider(LLMProvider):
    metadata = ProviderMetadata(
        id="groq",
        name="Groq",
        description="Ultra-fast inference for Llama and open models — free tier available",
        default_model="llama-3.1-8b-instant",
        models=text_models(
            ("llama-3.1-8b-instant", "llama-3.1-8b-instant (Free — higher RPM)"),
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ),
        key_prefix_hint="gsk_",
        default_base_url="https://api.groq.com/openai/v1",
    )

    def __init__(self, api_key: str, model: str | None = None, base_url: str | None = None):
        super().__init__(api_key, model, base_url)
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url or self.metadata.default_base_url,
        )

    def _messages(self, prompt: str, system_prompt: str | None) -> list[dict]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> GenerationResult:
        messages = self._messages(prompt, system_prompt)
        kwargs: dict = {"model": self.model, "messages": messages, "temperature": 0.65}
        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        async def _call():
            return await self._client.chat.completions.create(**kwargs)

        response = await with_rate_limit_retry(_call, label="groq")
        content = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else None
        return GenerationResult(content=content, model=self.model, tokens_used=tokens)

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ):
        messages = self._messages(prompt, system_prompt)
        async for chunk in stream_openai_chat_with_retry(
            self._client,
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.65,
        ):
            yield chunk

    async def test_connection(self) -> TestResult:
        start = time.perf_counter()
        try:
            await with_rate_limit_retry(
                lambda: self._client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "Say OK"}],
                    max_tokens=5,
                ),
                label="groq-test",
            )
            latency = (time.perf_counter() - start) * 1000
            return TestResult(success=True, message="Connection successful", latency_ms=round(latency, 2))
        except Exception as e:
            return TestResult(success=False, message=str(e))

    def validate_api_key(self, api_key: str) -> tuple[bool, str]:
        valid, msg = super().validate_api_key(api_key)
        if not valid:
            return valid, msg
        if not api_key.startswith("gsk_"):
            return False, "Groq keys typically start with 'gsk_'"
        return True, "Valid format"
