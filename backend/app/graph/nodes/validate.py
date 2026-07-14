"""ValidateInputNode — clean/validate article; seed workflow metadata."""

from __future__ import annotations

import re
import uuid

from app.graph.nodes._utils import MIN_ARTICLE_CHARS, run_node
from app.graph.registry import PROMPT_VERSION, normalize_format_ids
from app.graph.state import GraphState


def _clean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


async def validate_input(state: GraphState) -> dict:
    async def _run() -> dict:
        raw = (state.get("article") or "").strip()
        if len(raw) < MIN_ARTICLE_CHARS:
            raise ValueError(f"Article must be at least {MIN_ARTICLE_CHARS} characters.")
        cleaned = _clean(raw)
        if len(cleaned) < MIN_ARTICLE_CHARS:
            raise ValueError("Article is too short after cleaning.")

        selected = normalize_format_ids(state.get("selected_formats"))
        return {
            "cleaned_article": cleaned,
            "selected_formats": selected,
            "workflow_id": state.get("workflow_id") or str(uuid.uuid4()),
            "workflow_status": "running",
            "retry_count": int(state.get("retry_count") or 0),
            "failed_formats": [],
            "regenerate_formats": [],
            "quality_score": 0.0,
            "quality_notes": "",
            "outputs": dict(state.get("outputs") or {}),
            "prompt_version": PROMPT_VERSION,
            "errors": [],
            "usage": {},
        }

    return await run_node("validate", _run, soft_fail=False)
