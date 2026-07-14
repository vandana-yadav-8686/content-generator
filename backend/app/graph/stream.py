"""SSE-compatible streaming wrapper around the LangGraph workflow."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from collections.abc import AsyncIterator
from typing import Any

from app.graph.graph import get_compiled_graph, reset_compiled_graph
from app.graph.registry import FORMAT_REGISTRY, PROMPT_VERSION, normalize_format_ids
from app.graph.state import GraphState
from app.models.schemas import ProviderId
from app.services.graph_llm import get_llm_service, reset_llm_service
from app.services.settings_service import settings_repository

logger = logging.getLogger(__name__)

_STATUS = {
    "validate": "Validating article…",
    "summarize": "Summarizing with LangGraph…",
    "extract_insights": "Extracting key insights…",
    "detect_tone": "Applying tone…",
    "quality_review": "Quality review…",
    "mongodb_save": "Saving to MongoDB…",
}

KEEPALIVE_SEC = 12


def _user_visible_error(err: str) -> bool:
    """Hide recovered/internal pipeline errors from the UI."""
    lower = err.lower()
    if lower.startswith("insights"):
        return False
    if "summary fallback" in lower:
        return False
    return True


def _is_graph_schema_error(msg: str) -> bool:
    lower = msg.lower()
    return (
        "already being used as a state key" in lower
        or "can receive only one value per step" in lower
        or "invalid_concurrent_graph_update" in lower
    )


def _parse_provider(provider_id: str | ProviderId | None) -> ProviderId | None:
    if provider_id is None:
        return None
    if isinstance(provider_id, ProviderId):
        return provider_id
    try:
        return ProviderId(provider_id)
    except ValueError:
        return None


def _provider_preflight() -> str | None:
    """Return an error message if no usable provider is configured."""
    active = settings_repository.get_active_provider()
    if not active:
        return (
            "No active LLM provider. Open Settings, enable a provider, paste your API key, "
            "click Save, then Test Connection before generating."
        )
    if not active.api_key:
        return (
            f"{active.provider_id.value} is enabled but the API key could not be loaded. "
            "Re-save your key in Settings (ensure ENCRYPTION_KEY is set on the server)."
        )
    try:
        get_llm_service()
    except ValueError as exc:
        return str(exc)
    return None


async def _run_graph_updates(
    queue: asyncio.Queue,
    initial: GraphState,
    config: dict,
) -> None:
    graph = get_compiled_graph()
    try:
        async for update in graph.astream(initial, config=config, stream_mode="updates"):
            await queue.put(("update", update))
        await queue.put(("finished", None))
    except Exception as exc:
        await queue.put(("failed", exc))


async def stream_repurpose_graph(
    *,
    article: str,
    formats: list[str] | None = None,
    tone: str = "professional",
    provider_id: str | ProviderId | None = None,
    thread_id: str | None = None,
) -> AsyncIterator[dict[str, Any]]:
    """
    Run LangGraph and yield UI StreamEvent-shaped dicts:
    status | format_start | chunk | format_done | done | error
    """
    preflight = _provider_preflight()
    if preflight:
        yield {"type": "error", "message": preflight}
        return

    reset_llm_service(_parse_provider(provider_id))
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
    collected_errors: list[str] = []

    queue: asyncio.Queue = asyncio.Queue()
    runner = asyncio.create_task(_run_graph_updates(queue, initial, config))

    try:
        while True:
            try:
                kind, payload = await asyncio.wait_for(queue.get(), timeout=KEEPALIVE_SEC)
            except asyncio.TimeoutError:
                if runner.done():
                    break
                yield {"type": "status", "message": "Still generating… (this can take 1–3 min)"}
                continue

            if kind == "failed":
                raise payload  # type: ignore[misc]

            if kind == "finished":
                break

            update = payload
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

                for err in delta.get("errors") or []:
                    if (
                        isinstance(err, str)
                        and err not in collected_errors
                        and _user_visible_error(err)
                    ):
                        collected_errors.append(err)
                        yield {"type": "error", "message": err}

                if node in FORMAT_REGISTRY:
                    spec = FORMAT_REGISTRY[node]
                    content = ((delta.get("outputs") or {}).get(node) or "").strip()
                    if not content:
                        continue
                    key = f"{node}:{hash(content)}"
                    if key in emitted:
                        continue
                    emitted.add(key)

                    yield {
                        "type": "format_start",
                        "format": spec.api_id,
                        "label": spec.label,
                    }
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

                if node == "extract_insights" and delta.get("insights"):
                    insights = delta["insights"]
                    if isinstance(insights, dict):
                        yield {
                            "type": "extraction",
                            "data": {
                                "topic": insights.get("topic") or "",
                                "audience": insights.get("audience") or "",
                                "main_problem": insights.get("problem") or "",
                                "main_solution": insights.get("solution") or "",
                                "key_points": insights.get("key_points") or [],
                                "examples": insights.get("examples") or [],
                                "facts": insights.get("facts") or [],
                                "quotes": insights.get("quotes") or [],
                                "steps": insights.get("steps") or [],
                                "tone": "",
                                "best_hook": insights.get("hook") or "",
                                "second_best_hook": "",
                            },
                        }

        await runner

        elapsed = round(time.perf_counter() - started, 3)
        logger.info(
            "langgraph_stream done workflow_id=%s formats=%s elapsed=%ss emitted=%s errors=%s",
            workflow_id,
            selected,
            elapsed,
            len(emitted),
            len(collected_errors),
        )

        if not emitted:
            if collected_errors:
                detail = collected_errors[-1]
                msg = f"Generation failed: {detail}"
            else:
                msg = (
                    "No content was generated. Your API key is saved in MongoDB, but the LLM call "
                    "likely failed or timed out. Try: (1) Test Connection in Settings, (2) use "
                    "openrouter/free, (3) generate fewer formats."
                )
            yield {"type": "error", "message": msg}

        yield {
            "type": "done",
            "provider_id": provider,
            "model": model,
        }
    except ValueError as e:
        msg = str(e)
        if _is_graph_schema_error(msg):
            reset_compiled_graph()
            logger.warning("graph_schema_stale recovered: %s", msg)
            yield {
                "type": "error",
                "message": "Workflow refreshed. Click Generate again.",
            }
        else:
            yield {"type": "error", "message": msg}
    except Exception as e:
        msg = str(e)
        if _is_graph_schema_error(msg):
            reset_compiled_graph()
            logger.warning("graph_schema_stale recovered: %s", msg)
            yield {
                "type": "error",
                "message": "Workflow refreshed. Click Generate again.",
            }
        else:
            logger.exception("langgraph_stream failed")
            yield {"type": "error", "message": f"Generation failed: {e}"}
    finally:
        if not runner.done():
            runner.cancel()
