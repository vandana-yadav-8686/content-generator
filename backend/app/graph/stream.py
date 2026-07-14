"""SSE-compatible streaming wrapper around the LangGraph workflow."""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import AsyncIterator
from typing import Any

from app.graph.graph import get_compiled_graph
from app.graph.registry import FORMAT_REGISTRY, PROMPT_VERSION, normalize_format_ids
from app.graph.state import GraphState
from app.models.schemas import ProviderId
from app.services.graph_llm import reset_llm_service

logger = logging.getLogger(__name__)

_STATUS = {
    "validate": "Validating article…",
    "summarize": "Summarizing with LangGraph…",
    "insights": "Extracting key insights…",
    "tone": "Applying tone…",
    "quality_review": "Quality review…",
    "mongodb_save": "Saving to MongoDB…",
}


def _parse_provider(provider_id: str | ProviderId | None) -> ProviderId | None:
    if provider_id is None:
        return None
    if isinstance(provider_id, ProviderId):
        return provider_id
    try:
        return ProviderId(provider_id)
    except ValueError:
        return None


async def stream_repurpose_graph(
    *,
    article: str,
    formats: list[str] | None = None,
    tone: str = "professional",
    provider_id: str | ProviderId | None = None,
    thread_id: str | None = None,
) -> AsyncIterator[dict[str, Any]]:
    """
    Run LangGraph (graph/prompts) and yield UI StreamEvent-shaped dicts:
    status | format_start | chunk | format_done | done | error
    """
    reset_llm_service(_parse_provider(provider_id))
    graph = get_compiled_graph()
    selected = normalize_format_ids(formats)
    workflow_id = str(uuid.uuid4())
    thread = thread_id or workflow_id
    started = time.perf_counter()

    initial: GraphState = {
        "article": article,
        "selected_formats": selected,
        "requested_tone": tone,
        "workflow_id": workflow_id,
        "cleaned_article": "",
        "summary": "",
        "tone": "",
        "insights": {},
        "outputs": {},
        "quality_score": 0.0,
        "quality_notes": "",
        "failed_formats": [],
        "regenerate_formats": [],
        "retry_count": 0,
        "workflow_status": "pending",
        "model_used": "",
        "provider_id": "",
        "prompt_version": PROMPT_VERSION,
        "errors": [],
        "node_timings": {},
        "usage": {},
        "processing_time": 0.0,
    }

    config = {"configurable": {"thread_id": thread}}
    yield {"type": "status", "message": "Starting LangGraph workflow…"}

    provider = "unknown"
    model = "unknown"
    emitted: set[str] = set()

    try:
        async for update in graph.astream(initial, config=config, stream_mode="updates"):
            if not isinstance(update, dict):
                continue
            for node, delta in update.items():
                if not isinstance(delta, dict):
                    continue

                if node in _STATUS:
                    yield {"type": "status", "message": _STATUS[node]}

                if delta.get("provider_id"):
                    provider = str(delta["provider_id"])
                if delta.get("model_used"):
                    model = str(delta["model_used"])

                if node in FORMAT_REGISTRY:
                    spec = FORMAT_REGISTRY[node]
                    content = ((delta.get("outputs") or {}).get(node) or "").strip()
                    if not content:
                        continue
                    # Allow re-emit after quality retry
                    key = f"{node}:{hash(content)}"
                    if key in emitted:
                        continue
                    emitted.add(key)

                    yield {
                        "type": "format_start",
                        "format": spec.api_id,
                        "label": spec.label,
                    }
                    # Deliver full text (LangGraph nodes return complete strings)
                    yield {
                        "type": "chunk",
                        "format": spec.api_id,
                        "content": content,
                    }
                    yield {
                        "type": "format_done",
                        "format": spec.api_id,
                        "content": content,
                    }

                if node == "insights" and delta.get("insights"):
                    insights = delta["insights"]
                    if isinstance(insights, dict):
                        yield {
                            "type": "extraction",
                            "data": {
                                "topic": insights.get("topic")
                                or insights.get("main_idea")
                                or "",
                                "audience": insights.get("audience") or "",
                                "main_problem": insights.get("problem")
                                or insights.get("main_problem")
                                or "",
                                "main_solution": insights.get("solution")
                                or insights.get("main_solution")
                                or "",
                                "key_points": insights.get("key_points")
                                or insights.get("points")
                                or [],
                                "examples": insights.get("examples") or [],
                                "facts": insights.get("facts") or [],
                                "quotes": insights.get("quotes") or [],
                                "steps": insights.get("steps") or [],
                                "tone": "",
                                "best_hook": insights.get("hook") or "",
                                "second_best_hook": "",
                            },
                        }

        elapsed = round(time.perf_counter() - started, 3)
        logger.info(
            "langgraph_stream done workflow_id=%s formats=%s elapsed=%ss emitted=%s",
            workflow_id,
            selected,
            elapsed,
            len(emitted),
        )
        if not emitted:
            yield {
                "type": "error",
                "message": (
                    "No content was generated. Enable a provider with a valid API key "
                    "in Settings. On Render, set ENCRYPTION_KEY and DATABASE_PATH=/tmp/settings.db."
                ),
            }
        yield {
            "type": "done",
            "provider_id": provider,
            "model": model,
        }
    except ValueError as e:
        yield {"type": "error", "message": str(e)}
    except Exception as e:
        logger.exception("langgraph_stream failed")
        yield {"type": "error", "message": f"Generation failed: {e}"}
