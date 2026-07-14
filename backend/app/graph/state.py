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


def last_value(left: Any, right: Any) -> Any:
    """Last-write-wins — required when parallel format nodes write the same key."""
    return right if right is not None else left


def merge_lists(left: list | None, right: list | None) -> list:
    """Deduping append for parallel writers (e.g. failed_formats)."""
    out: list = list(left or [])
    for item in right or []:
        if item not in out:
            out.append(item)
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
    quality_score: Annotated[float, last_value]
    quality_notes: Annotated[str, last_value]
    failed_formats: Annotated[list[str], merge_lists]
    regenerate_formats: Annotated[list[str], last_value]
    retry_count: Annotated[int, last_value]
    workflow_status: Annotated[str, last_value]

    # --- Observability ---
    # Parallel format nodes all write these — must use reducers
    model_used: Annotated[str, last_value]
    provider_id: Annotated[str, last_value]
    prompt_version: str
    document_id: NotRequired[str]
    errors: Annotated[list[str], operator.add]
    node_timings: Annotated[dict[str, float], merge_dicts]
    usage: Annotated[dict[str, Any], merge_dicts]
    processing_time: Annotated[float, last_value]
