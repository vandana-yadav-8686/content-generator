"""Offline mock LLM — zero API calls, for UI/pipeline testing without rate limits."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from app.providers.base import (
    GenerationResult,
    LLMProvider,
    ProviderMetadata,
    TestResult,
    text_models,
)

MOCK_REEL = """**Hook (0–5 sec)**
"Most teams aren't failing at content — they're failing at repurposing it."

**Scene 1 (5–15 sec)**
You publish one solid article. Then you stare at a blank caption box for twenty minutes. Sound familiar?

**Scene 2 (15–30 sec)**
The ideas are already in the post — hooks, stats, examples, takeaways. The hard part is reshaping them for Reels, LinkedIn, and carousels without sounding robotic.

**Scene 3 (30–45 sec)**
A good repurposing flow extracts the brief first: topic, audience, key points, proof. Then each platform gets its own voice — not a copy-paste job.

**Scene 4 (45–55 sec)**
Test with one format, nail the tone, then scale. Quick iterations beat one giant batch that burns your API quota.

**Ending (55–60 sec)**
Write once. Ship everywhere. That's the whole game.

**On-screen CTA:**
"What's your hardest platform to repurpose for? Drop it below."
"""


class MockProvider(LLMProvider):
    metadata = ProviderMetadata(
        id="mock",
        name="Offline Mock",
        description="No API calls — for local UI testing",
        default_model="offline-mock",
        models=text_models("offline-mock"),
    )

    def __init__(self, api_key: str, model: str | None = None, base_url: str | None = None):
        super().__init__(api_key or "offline", model, base_url)
        self._article = ""

    def _capture_article(self, prompt: str) -> None:
        marker = "ARTICLE"
        idx = prompt.upper().rfind(marker)
        if idx != -1:
            self._article = prompt[idx + len(marker) :].strip()[:500]
        elif len(prompt) > 200:
            self._article = prompt[-500:].strip()

    def _is_extraction(self, prompt: str) -> bool:
        upper = prompt.upper()
        # Format prompts embed brief JSON (with key_points) — only match the extraction step.
        return "RETURN JSON ONLY" in upper or (
            "READ THE ARTICLE CAREFULLY" in upper and "CONTENT BRIEF" not in upper
        )

    def _response_text(self, prompt: str) -> str:
        self._capture_article(prompt)
        if self._is_extraction(prompt):
            return self._mock_brief_json()
        lower = prompt.lower()
        if "60-second reel" in lower or "reel script" in lower:
            return MOCK_REEL
        return (
            "[Offline mock output]\n\n"
            "This is placeholder content for pipeline testing. "
            "Enable a real provider in Settings for live generation."
        )

    def _mock_brief_json(self) -> str:
        topic = self._article[:120].strip() or "Article topic from your paste"
        return json.dumps(
            {
                "topic": topic,
                "audience": "Creators and marketers repurposing long-form content",
                "main_problem": "One article doesn't automatically become platform-native posts.",
                "main_solution": "Extract a structured brief, then generate per-platform scripts.",
                "key_points": [
                    "Start with extraction before generation",
                    "Match each platform's native format",
                    "Keep hooks short and spoken",
                ],
                "examples": ["Before/after repurposing workflow"],
                "facts": ["Testing in offline mode uses zero API quota"],
                "quotes": [],
                "steps": ["Paste article", "Extract brief", "Generate formats"],
                "tone": "conversational",
                "best_hook": "You already wrote the hard part.",
                "second_best_hook": "Stop rewriting from scratch.",
            }
        )

    async def _stream_text(self, text: str) -> AsyncIterator[str]:
        chunk_size = 24
        for i in range(0, len(text), chunk_size):
            yield text[i : i + chunk_size]
            await asyncio.sleep(0.03)

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> GenerationResult:
        await asyncio.sleep(0.15)
        content = self._response_text(prompt)
        return GenerationResult(content=content, model=self.model, tokens_used=0)

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        content = self._response_text(prompt)
        async for chunk in self._stream_text(content):
            yield chunk

    async def test_connection(self) -> TestResult:
        return TestResult(success=True, message="Offline mock — no network call", latency_ms=1.0)

    def validate_api_key(self, api_key: str) -> tuple[bool, str]:
        return True, "Offline mode — no key required"
