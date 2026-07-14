"""MongoDBSaveNode — persist workflow run + intermediates to Atlas."""

from __future__ import annotations

from datetime import datetime, timezone

from app.config import settings
from app.database.mongodb import ensure_indexes, get_content_collection
from app.graph.nodes._utils import run_node
from app.graph.registry import FORMAT_REGISTRY, PROMPT_VERSION
from app.graph.state import GraphState


def _api_outputs(outputs: dict[str, str]) -> dict[str, str]:
    """Map internal format ids → API field names for compatibility."""
    result: dict[str, str] = {}
    for fmt_id, content in (outputs or {}).items():
        spec = FORMAT_REGISTRY.get(fmt_id)
        key = spec.api_id if spec else fmt_id
        result[key] = content
    return result


async def save_to_mongodb(state: GraphState) -> dict:
    async def _run() -> dict:
        timings = state.get("node_timings") or {}
        processing = float(state.get("processing_time") or sum(timings.values()))
        outputs = state.get("outputs") or {}

        if not settings.mongodb_enabled:
            return {
                "document_id": "",
                "processing_time": processing,
                "workflow_status": state.get("workflow_status") or "completed",
            }

        ensure_indexes()
        col = get_content_collection()
        now = datetime.now(timezone.utc)
        api_outputs = _api_outputs(outputs)

        doc = {
            "workflow_id": state.get("workflow_id") or "",
            "workflow_status": state.get("workflow_status") or "completed",
            "original_article": state.get("cleaned_article") or state.get("article") or "",
            "summary": state.get("summary") or "",
            "key_insights": state.get("insights") or {},
            "tone": state.get("tone") or "",
            "outputs": outputs,
            "generated": api_outputs,
            # Denormalized for querying / backwards compatible readers
            "youtube_script": outputs.get("youtube", ""),
            "reel_script": outputs.get("reel", ""),
            "linkedin_post": outputs.get("linkedin", ""),
            "instagram_carousel": outputs.get("carousel", ""),
            "voiceover_script": outputs.get("voiceover", ""),
            "quality_score": state.get("quality_score") or 0,
            "quality_notes": state.get("quality_notes") or "",
            "failed_formats": state.get("failed_formats") or [],
            "selected_formats": state.get("selected_formats") or [],
            "retry_count": int(state.get("retry_count") or 0),
            "model_used": state.get("model_used") or "",
            "model_version": state.get("model_used") or "",
            "provider_id": state.get("provider_id") or "",
            "prompt_version": state.get("prompt_version") or PROMPT_VERSION,
            "processing_time": processing,
            "node_timings": timings,
            "usage": state.get("usage") or {},
            "errors": state.get("errors") or [],
            "intermediates": {
                "summary": state.get("summary") or "",
                "insights": state.get("insights") or {},
                "tone": state.get("tone") or "",
            },
            "created_at": now,
            "updated_at": now,
            # Reserved for future: vector embeddings / semantic search
            "embedding": None,
            "tenant_id": None,
        }

        result = col.insert_one(doc)
        return {
            "document_id": str(result.inserted_id),
            "processing_time": processing,
            "workflow_status": state.get("workflow_status") or "completed",
        }

    return await run_node("mongodb_save", _run, soft_fail=True)
