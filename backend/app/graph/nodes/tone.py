"""DetectToneNode — structured tone classification."""

from __future__ import annotations

from app.graph.nodes._utils import run_node
from app.graph.prompts.analysis.tone import prompt as tone_prompt
from app.graph.schemas import ToneResult
from app.graph.state import GraphState
from app.services.graph_llm import get_llm_service

ALLOWED = {
    "professional",
    "educational",
    "conversational",
    "inspirational",
    "news",
}

_UI_MAP = {
    "casual": "conversational",
    "witty": "conversational",
    "bold": "inspirational",
    "professional": "professional",
    "educational": "educational",
    "conversational": "conversational",
    "inspirational": "inspirational",
    "news": "news",
}


async def detect_tone(state: GraphState) -> dict:
    async def _run() -> dict:
        requested = (state.get("requested_tone") or "").strip().lower()
        if requested and requested not in {"auto", ""}:
            mapped = _UI_MAP.get(requested, requested)
            if mapped in ALLOWED:
                return {"tone": mapped}

        llm = get_llm_service()
        parsed = await llm.arun_structured(
            tone_prompt,
            {"article": (state.get("cleaned_article") or "")[:4000]},
            schema=ToneResult,
            node="tone",
            max_tokens=60,
        )
        tone = parsed.tone if parsed.tone in ALLOWED else "professional"
        return {"tone": tone, "usage": llm.session.usage_summary()}

    return await run_node("tone", _run, soft_fail=False)
