import time
from openai import AsyncOpenAI

from app.providers.base import LLMProvider, ProviderMetadata, GenerationResult, TestResult, text_models


class DeepSeekProvider(LLMProvider):
    metadata = ProviderMetadata(
        id="deepseek",
        name="DeepSeek",
        description="DeepSeek Chat and Reasoner models",
        default_model="deepseek-chat",
        models=text_models(
            "deepseek-chat",
            "deepseek-reasoner",
        ),
        key_prefix_hint="sk-",
        default_base_url="https://api.deepseek.com",
        supports_custom_base_url=True,
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

    def validate_api_key(self, api_key: str) -> tuple[bool, str]:
        valid, msg = super().validate_api_key(api_key)
        if not valid:
            return valid, msg
        if not api_key.startswith("sk-"):
            return False, "DeepSeek keys typically start with 'sk-'"
        return True, "Valid format"
