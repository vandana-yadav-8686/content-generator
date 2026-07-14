"""
Format registry — single extension point for new content types.

To add X/Twitter threads later:
  1. Add prompts/generation/twitter.py
  2. Register FormatSpec below
  3. Graph auto-wires the node (no GraphState field changes)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from langchain_core.prompts import ChatPromptTemplate


@dataclass(frozen=True, slots=True)
class FormatSpec:
    """Declarative description of one parallel generation node."""

    id: str  # graph node name / outputs key: "youtube"
    api_id: str  # external/API id: "youtube_script"
    label: str
    max_tokens: int
    prompt_factory: Callable[[], ChatPromptTemplate]


def _load_prompt(factory: Callable[[], ChatPromptTemplate]) -> Callable[[], ChatPromptTemplate]:
    return factory


def get_youtube_prompt() -> ChatPromptTemplate:
    from app.graph.prompts.generation.youtube import prompt

    return prompt


def get_reel_prompt() -> ChatPromptTemplate:
    from app.graph.prompts.generation.reel import prompt

    return prompt


def get_linkedin_prompt() -> ChatPromptTemplate:
    from app.graph.prompts.generation.linkedin import prompt

    return prompt


def get_carousel_prompt() -> ChatPromptTemplate:
    from app.graph.prompts.generation.carousel import prompt

    return prompt


def get_voiceover_prompt() -> ChatPromptTemplate:
    from app.graph.prompts.generation.voiceover import prompt

    return prompt


FORMAT_REGISTRY: dict[str, FormatSpec] = {
    "youtube": FormatSpec(
        id="youtube",
        api_id="youtube_script",
        label="YouTube Script",
        max_tokens=900,
        prompt_factory=get_youtube_prompt,
    ),
    "reel": FormatSpec(
        id="reel",
        api_id="reel_script",
        label="60-Second Reel Script",
        max_tokens=700,
        prompt_factory=get_reel_prompt,
    ),
    "linkedin": FormatSpec(
        id="linkedin",
        api_id="linkedin_post",
        label="LinkedIn Post",
        max_tokens=800,
        prompt_factory=get_linkedin_prompt,
    ),
    "carousel": FormatSpec(
        id="carousel",
        api_id="instagram_carousel",
        label="Instagram Carousel",
        max_tokens=1000,
        prompt_factory=get_carousel_prompt,
    ),
    "voiceover": FormatSpec(
        id="voiceover",
        api_id="voiceover_script",
        label="Voice-over Script",
        max_tokens=600,
        prompt_factory=get_voiceover_prompt,
    ),
}

API_ID_TO_FORMAT = {spec.api_id: spec.id for spec in FORMAT_REGISTRY.values()}

PROMPT_VERSION = "graph-v2.1.0"


def normalize_format_ids(formats: list[str] | None) -> list[str]:
    if not formats:
        return list(FORMAT_REGISTRY.keys())
    out: list[str] = []
    for raw in formats:
        key = raw.strip().lower()
        node = API_ID_TO_FORMAT.get(key, key)
        if node in FORMAT_REGISTRY and node not in out:
            out.append(node)
    return out or list(FORMAT_REGISTRY.keys())
