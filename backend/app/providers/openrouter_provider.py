import time
from openai import AsyncOpenAI

from app.providers.base import LLMProvider, ProviderMetadata, GenerationResult, TestResult, text_models

# OpenRouter retires free endpoints often — remap old IDs still held in the UI/DB.
DEPRECATED_MODELS: dict[str, str] = {
    "google/gemini-2.0-flash-exp:free": "openrouter/free",
    "google/gemini-2.0-flash-thinking-exp:free": "openrouter/free",
    "google/gemini-flash-1.5:free": "openrouter/free",
    "meta-llama/llama-3.3-70b-instruct:free": "openrouter/free",
    "meta-llama/llama-3.1-70b-instruct:free": "openrouter/free",
    "mistralai/mistral-7b-instruct:free": "openrouter/free",
}

DEAD_MODEL_FRAGMENTS = (
    "gemini-2.0-flash-exp",
    "gemini-2.0-flash-thinking",
    "gemini-flash-1.5:free",
)

DEFAULT_OPENROUTER_MODEL = "openrouter/free"
KNOWN_OPENROUTER_MODELS = {
    "openrouter/free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "openai/gpt-oss-20b:free",
    "openai/gpt-4o-mini",
    "anthropic/claude-3.5-sonnet",
    "deepseek/deepseek-chat",
    "google/gemini-2.5-flash",
}


def normalize_openrouter_model(model: str | None) -> str:
    """Always return a currently usable OpenRouter model id."""
    if not model or not model.strip():
        return DEFAULT_OPENROUTER_MODEL
    cleaned = model.strip()
    cleaned = DEPRECATED_MODELS.get(cleaned, cleaned)
    lower = cleaned.lower()
    if any(frag in lower for frag in DEAD_MODEL_FRAGMENTS):
        return DEFAULT_OPENROUTER_MODEL
    if cleaned not in KNOWN_OPENROUTER_MODELS:
        if ":free" in lower or cleaned.startswith("google/gemini-2"):
            return DEFAULT_OPENROUTER_MODEL
    return cleaned


class OpenRouterProvider(LLMProvider):
    metadata = ProviderMetadata(
        id="openrouter",
        name="OpenRouter",
        description="Unified API for 100+ models from multiple providers",
        default_model=DEFAULT_OPENROUTER_MODEL,
        models=text_models(
            ("openrouter/free", "Free Models Router (auto)"),
            ("google/gemma-4-31b-it:free", "Gemma 4 31B (free)"),
            ("google/gemma-4-26b-a4b-it:free", "Gemma 4 26B A4B (free)"),
            ("openai/gpt-oss-20b:free", "GPT-OSS 20B (free)"),
            ("openai/gpt-4o-mini", "GPT-4o Mini"),
            ("anthropic/claude-3.5-sonnet", "Claude 3.5 Sonnet"),
            ("deepseek/deepseek-chat", "DeepSeek Chat"),
            ("google/gemini-2.5-flash", "Gemini 2.5 Flash"),
        ),
        key_prefix_hint="sk-or-",
        default_base_url="https://openrouter.ai/api/v1",
        supports_custom_base_url=True,
    )

    def __init__(self, api_key: str, model: str | None = None, base_url: str | None = None):
        super().__init__(api_key, model, base_url)
        self.model = normalize_openrouter_model(self.model)
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url or self.metadata.default_base_url,
            default_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "AI Content Repurposer",
            },
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
        model = normalize_openrouter_model(self.model)
        self.model = model
        messages = self._messages(prompt, system_prompt)
        kwargs: dict = {"model": model, "messages": messages, "temperature": 0.65}
        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        response = await self._client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else None
        return GenerationResult(content=content, model=model, tokens_used=tokens)

    async def test_connection(self) -> TestResult:
        start = time.perf_counter()
        model = normalize_openrouter_model(self.model)
        self.model = model
        try:
            await self._client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Say OK"}],
                max_tokens=5,
            )
            latency = (time.perf_counter() - start) * 1000
            return TestResult(
                success=True,
                message=f"Connection successful ({model})",
                latency_ms=round(latency, 2),
            )
        except Exception as e:
            msg = str(e)
            if "404" in msg or "No endpoints found" in msg:
                return TestResult(
                    success=False,
                    message=(
                        f"Model '{model}' is unavailable on OpenRouter. "
                        "Choose 'Free Models Router (auto)', click Save, then Test again."
                    ),
                )
            return TestResult(success=False, message=msg)

    def validate_api_key(self, api_key: str) -> tuple[bool, str]:
        valid, msg = super().validate_api_key(api_key)
        if not valid:
            return valid, msg
        if not api_key.startswith("sk-or-"):
            return False, "OpenRouter keys typically start with 'sk-or-'"
        return True, "Valid format"
