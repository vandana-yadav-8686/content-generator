import time
from openai import AsyncOpenAI

from app.providers.base import LLMProvider, ProviderMetadata, GenerationResult, TestResult, text_models


class MistralProvider(LLMProvider):
    metadata = ProviderMetadata(
        id="mistral",
        name="Mistral AI",
        description="Mistral Large, Medium, and Small models",
        default_model="mistral-small-latest",
        models=text_models(
            "mistral-large-latest",
            "mistral-medium-latest",
            "mistral-small-latest",
            "open-mistral-7b",
            "codestral-latest",
        ),
        key_prefix_hint="",
        default_base_url="https://api.mistral.ai/v1",
    )

    def __init__(self, api_key: str, model: str | None = None, base_url: str | None = None):
        super().__init__(api_key, model, base_url)
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url or self.metadata.default_base_url,
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> GenerationResult:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        kwargs: dict = {"model": self.model, "messages": messages, "temperature": 0.8}
        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        response = await self._client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else None
        return GenerationResult(content=content, model=self.model, tokens_used=tokens)

    async def test_connection(self) -> TestResult:
        start = time.perf_counter()
        try:
            await self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=5,
            )
            latency = (time.perf_counter() - start) * 1000
            return TestResult(success=True, message="Connection successful", latency_ms=round(latency, 2))
        except Exception as e:
            return TestResult(success=False, message=str(e))
