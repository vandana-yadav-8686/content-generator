"""Fluent prompt builder: PromptBuilder().set_platform('youtube').set_tone('professional').build()"""

from __future__ import annotations

from app.services.prompts import get_format_examples, get_format_prompts, get_system_prompt

PLATFORM_ALIASES: dict[str, str] = {
    "youtube": "youtube_script",
    "youtube_script": "youtube_script",
    "reel": "reel_script",
    "reel_script": "reel_script",
    "linkedin": "linkedin_post",
    "linkedin_post": "linkedin_post",
    "carousel": "instagram_carousel",
    "instagram": "instagram_carousel",
    "instagram_carousel": "instagram_carousel",
    "voiceover": "voiceover_script",
    "voiceover_script": "voiceover_script",
}

TONE_MODIFIERS: dict[str, str] = {
    "professional": (
        "Voice: confident creator who knows their stuff — clear, direct, credible. "
        "Still conversational. Contractions OK. No corporate jargon."
    ),
    "casual": (
        "Voice: talking to a friend over coffee. Loose, warm, contractions everywhere. "
        "Start sentences with And/But/So. Fragments are great."
    ),
    "witty": (
        "Voice: sharp and a little playful — punchy one-liners, light humor, "
        "never cheesy. Sound like a creator with personality, not a comedian doing bits."
    ),
    "educational": (
        "Voice: smart friend explaining something cool they just learned. "
        "Simple words. No lecturer tone. No 'it's important to note'."
    ),
    "bold": (
        "Voice: direct, opinionated, scroll-stopping. Short sentences. "
        "Strong claims. No hedging ('might', 'perhaps', 'could potentially')."
    ),
}


class BuiltPrompt:
    def __init__(self, system_prompt: str, user_prompt: str, format_id: str, tone: str):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.format_id = format_id
        self.tone = tone


class PromptBuilder:
    """Chainable builder for per-platform generation prompts."""

    def __init__(self) -> None:
        self._platform: str | None = None
        self._tone: str = "professional"
        self._brief: str = ""
        self._excerpt: str = ""

    def set_platform(self, platform: str) -> PromptBuilder:
        key = platform.strip().lower().replace("-", "_")
        if key not in PLATFORM_ALIASES:
            raise ValueError(
                f"Unknown platform '{platform}'. "
                f"Use one of: {', '.join(sorted(set(PLATFORM_ALIASES.keys())))}"
            )
        self._platform = PLATFORM_ALIASES[key]
        return self

    def set_tone(self, tone: str) -> PromptBuilder:
        key = tone.strip().lower()
        if key not in TONE_MODIFIERS:
            raise ValueError(
                f"Unknown tone '{tone}'. "
                f"Use one of: {', '.join(TONE_MODIFIERS.keys())}"
            )
        self._tone = key
        return self

    def set_brief(self, brief: str) -> PromptBuilder:
        self._brief = brief
        return self

    def set_excerpt(self, excerpt: str) -> PromptBuilder:
        self._excerpt = excerpt
        return self

    def build(self) -> BuiltPrompt:
        if not self._platform:
            raise ValueError("Platform is required. Call set_platform() first.")

        format_prompts = get_format_prompts()
        format_examples = get_format_examples()
        template = format_prompts[self._platform]
        example = format_examples[self._platform]

        user_prompt = template.format(
            brief=self._brief,
            excerpt=self._excerpt,
            example=example,
        )

        tone_line = TONE_MODIFIERS[self._tone]
        system_prompt = f"{get_system_prompt()}\n\nTONE FOR THIS PIECE:\n{tone_line}"

        return BuiltPrompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            format_id=self._platform,
            tone=self._tone,
        )
