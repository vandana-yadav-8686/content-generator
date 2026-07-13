import time
from anthropic import AsyncAnthropic

from app.providers.base import LLMProvider, ProviderMetadata, GenerationResult, TestResult, text_models


class AnthropicProvider(LLMProvider):
    metadata = ProviderMetadata(
        id="anthropic",
        name="Anthropic Claude",
        description="Claude Sonnet, Haiku, and Opus models",
        default_model="claude-sonnet-4-20250514",
        models=text_models(
            "claude-sonnet-4-20250514",
            "claude-3-5-haiku-20241022",
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
        ),
        key_prefix_hint="sk-ant-",
    )

    def __init__(self, api_key: str, model: str | None = None, base_url: str | None = None):
        super().__init__(api_key, model, base_url)
        self._client = AsyncAnthropic(api_key=api_key, base_url=base_url)

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> GenerationResult:
        response = await self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens or 4096,
            system=system_prompt or "You are a helpful content repurposing assistant.",
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.content[0].text if response.content else ""
        tokens = (response.usage.input_tokens + response.usage.output_tokens) if response.usage else None
        return GenerationResult(content=content, model=self.model, tokens_used=tokens)

    async def test_connection(self) -> TestResult:
        start = time.perf_counter()
        try:
            await self._client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Say OK"}],
            )
            latency = (time.perf_counter() - start) * 1000
            return TestResult(success=True, message="Connection successful", latency_ms=round(latency, 2))
        except Exception as e:
            return TestResult(success=False, message=str(e))

    def validate_api_key(self, api_key: str) -> tuple[bool, str]:
        valid, msg = super().validate_api_key(api_key)
        if not valid:
            return valid, msg
        if not api_key.startswith("sk-ant-"):
            return False, "Anthropic keys typically start with 'sk-ant-'"
        return True, "Valid format"
