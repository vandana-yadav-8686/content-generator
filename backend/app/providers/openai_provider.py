import time
from openai import AsyncOpenAI

from app.providers.base import (
    LLMProvider,
    ModelInfo,
    ProviderMetadata,
    GenerationResult,
    TestResult,
)
from app.providers.openai_stream import stream_openai_chat

OPENAI_MODELS: list[ModelInfo] = [
    ModelInfo(id="gpt-5", name="GPT-5"),
    ModelInfo(id="gpt-5-mini", name="GPT-5 Mini"),
    ModelInfo(id="gpt-5-nano", name="GPT-5 Nano"),
    ModelInfo(id="gpt-4.1", name="GPT-4.1"),
    ModelInfo(id="gpt-4.1-mini", name="GPT-4.1 Mini"),
    ModelInfo(id="gpt-4.1-nano", name="GPT-4.1 Nano"),
    ModelInfo(id="o3", name="o3"),
    ModelInfo(id="o3-pro", name="o3 Pro"),
    ModelInfo(id="o4-mini", name="o4 Mini"),
    ModelInfo(id="o4-mini-high", name="o4 Mini High"),
    ModelInfo(id="gpt-image-1", name="GPT Image 1", modality="image"),
]

REASONING_MODEL_PREFIXES = ("o1", "o3", "o4", "gpt-5")


class OpenAIProvider(LLMProvider):
    metadata = ProviderMetadata(
        id="openai",
        name="OpenAI",
        description="GPT-5, GPT-4.1, o3, o4, and image models",
        default_model="gpt-5-mini",
        models=OPENAI_MODELS,
        key_prefix_hint="sk-",
    )

    def __init__(self, api_key: str, model: str | None = None, base_url: str | None = None):
        super().__init__(api_key, model, base_url)
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    def _is_reasoning_model(self) -> bool:
        return self.model.startswith(REASONING_MODEL_PREFIXES)

    def _is_image_model(self) -> bool:
        model_info = next((m for m in OPENAI_MODELS if m.id == self.model), None)
        return model_info is not None and model_info.modality == "image"

    def _chat_kwargs(self, messages: list[dict], max_tokens: int) -> dict:
        kwargs: dict = {"model": self.model, "messages": messages}
        if self._is_reasoning_model():
            kwargs["max_completion_tokens"] = max_tokens
        else:
            kwargs["max_tokens"] = max_tokens
            kwargs["temperature"] = 0.8
        return kwargs

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> GenerationResult:
        if self._is_image_model():
            raise ValueError(
                f"{self.model} is an image model and cannot be used for text repurposing. "
                "Select a text model such as gpt-5-mini or gpt-4.1."
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self._client.chat.completions.create(
            **self._chat_kwargs(messages, max_tokens=max_tokens or 4096)
        )
        content = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else None
        return GenerationResult(content=content, model=self.model, tokens_used=tokens)

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ):
        if self._is_image_model():
            raise ValueError(f"{self.model} is an image model and cannot stream text.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        if self._is_reasoning_model():
            result = await self.generate(prompt, system_prompt=system_prompt, max_tokens=max_tokens)
            if result.content:
                yield result.content
            return

        async for chunk in stream_openai_chat(
            self._client,
            model=self.model,
            messages=messages,
            max_tokens=max_tokens or 4096,
            temperature=0.8,
        ):
            yield chunk

    async def test_connection(self) -> TestResult:
        if self._is_image_model():
            return TestResult(
                success=True,
                message="Image model configured (text connection test skipped)",
            )

        start = time.perf_counter()
        try:
            await self._client.chat.completions.create(
                **self._chat_kwargs(
                    [{"role": "user", "content": "Say OK"}],
                    max_tokens=5,
                )
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
            return False, "OpenAI keys typically start with 'sk-'"
        return True, "Valid format"
