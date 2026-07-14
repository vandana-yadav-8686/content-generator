"""
Production GraphState for the repurposing workflow.

Design notes
------------
* Content outputs live in a single `outputs` dict keyed by format id
  (youtube, reel, …). Adding Twitter/Newsletter requires a registry entry,
  not a TypedDict field change.
* Reducers allow parallel Send() writers without clobbering sibling keys.
* Nodes must only read/write this state — no prompt strings in state.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, NotRequired, TypedDict


def merge_dicts(left: dict | None, right: dict | None) -> dict:
    out = dict(left or {})
    out.update(right or {})
    return out


def merge_outputs(left: dict | None, right: dict | None) -> dict:
    """Merge format outputs; non-empty right values win per key."""
    out = dict(left or {})
    for key, value in (right or {}).items():
        if value is None:
            continue
        text = value if isinstance(value, str) else str(value)
        if text.strip():
            out[key] = text
        elif key not in out:
            out[key] = text
    return out


class GraphState(TypedDict):
    # --- Input ---
    article: str
    selected_formats: list[str]
    requested_tone: NotRequired[str]
    workflow_id: NotRequired[str]

    # --- Analysis (shared context, not prompts) ---
    cleaned_article: str
    summary: str
    tone: str
    insights: dict[str, Any]

    # --- Generated content (extensible) ---
    outputs: Annotated[dict[str, str], merge_outputs]

    # --- Review / control ---
    quality_score: float
    quality_notes: str
    failed_formats: list[str]
    regenerate_formats: list[str]
    retry_count: int
    workflow_status: str  # pending | running | completed | partial | failed

    # --- Observability ---
    model_used: str
    provider_id: str
    prompt_version: str
    document_id: NotRequired[str]
    errors: Annotated[list[str], operator.add]
    node_timings: Annotated[dict[str, float], merge_dicts]
    usage: Annotated[dict[str, Any], merge_dicts]
    processing_time: float
