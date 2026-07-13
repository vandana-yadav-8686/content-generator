import time
import cohere

from app.providers.base import LLMProvider, ProviderMetadata, GenerationResult, TestResult, text_models


class CohereProvider(LLMProvider):
    metadata = ProviderMetadata(
        id="cohere",
        name="Cohere",
        description="Command R+ and other Cohere language models",
        default_model="command-r-plus-08-2024",
        models=text_models(
            "command-r-plus-08-2024",
            "command-r-08-2024",
            "command-r7b-12-2024",
            "command-light",
        ),
        key_prefix_hint="",
    )

    def __init__(self, api_key: str, model: str | None = None, base_url: str | None = None):
        super().__init__(api_key, model, base_url)
        self._client = cohere.AsyncClientV2(api_key=api_key)

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

        response = await self._client.chat(**kwargs)
        content = response.message.content[0].text if response.message.content else ""
        return GenerationResult(content=content, model=self.model)

    async def test_connection(self) -> TestResult:
        start = time.perf_counter()
        try:
            await self._client.chat(
                model=self.model,
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=5,
            )
            latency = (time.perf_counter() - start) * 1000
            return TestResult(success=True, message="Connection successful", latency_ms=round(latency, 2))
        except Exception as e:
            return TestResult(success=False, message=str(e))
