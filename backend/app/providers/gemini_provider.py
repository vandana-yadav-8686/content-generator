import time
import asyncio
import re
from google import genai
from google.genai import types

from app.providers.base import LLMProvider, ProviderMetadata, GenerationResult, TestResult, text_models


class GeminiProvider(LLMProvider):
    metadata = ProviderMetadata(
        id="gemini",
        name="Google Gemini",
        description="Gemini Flash and Pro models — generous free tier",
        default_model="gemini-2.0-flash-lite",
        models=text_models(
            ("gemini-2.0-flash-lite", "gemini-2.0-flash-lite (Free — best quota)"),
            ("gemini-2.0-flash", "gemini-2.0-flash (Free)"),
            ("gemini-2.5-flash", "gemini-2.5-flash (Free)"),
            ("gemini-2.5-pro", "gemini-2.5-pro (Limited free quota)"),
        ),
        key_prefix_hint="AIza or AQ.",
    )

    def __init__(self, api_key: str, model: str | None = None, base_url: str | None = None):
        super().__init__(api_key, model, base_url)
        self._client = genai.Client(api_key=api_key)

    def _config(
        self,
        system_prompt: str | None,
        max_tokens: int | None = None,
    ) -> types.GenerateContentConfig | None:
        if not system_prompt and not max_tokens:
            return None
        return types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.8,
            max_output_tokens=max_tokens,
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> GenerationResult:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = await self._client.aio.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=self._config(system_prompt, max_tokens),
                )
                content = response.text or ""
                return GenerationResult(content=content, model=self.model)
            except Exception as e:
                last_error = e
                err = str(e)
                if "429" in err and attempt < 2:
                    delay = 20 * (attempt + 1)
                    match = re.search(r"retry in (\d+(?:\.\d+)?)s", err, re.IGNORECASE)
                    if match:
                        delay = max(int(float(match.group(1))) + 1, delay)
                    await asyncio.sleep(delay)
                    continue
                raise
        raise last_error  # type: ignore[misc]

    async def test_connection(self) -> TestResult:
        start = time.perf_counter()
        try:
            response = await self._client.aio.models.generate_content(
                model=self.model,
                contents="Say OK",
            )
            _ = response.text
            latency = (time.perf_counter() - start) * 1000
            return TestResult(success=True, message="Connection successful", latency_ms=round(latency, 2))
        except Exception as e:
            return TestResult(success=False, message=str(e))

    def validate_api_key(self, api_key: str) -> tuple[bool, str]:
        valid, msg = super().validate_api_key(api_key)
        if not valid:
            return valid, msg
        key = api_key.strip()
        # Google AI Studio: legacy AIza... keys or newer AQ.... auth keys
        if key.startswith("AIza") or key.startswith("AQ."):
            return True, "Valid format"
        return False, "Gemini keys typically start with 'AIza' or 'AQ.'"
