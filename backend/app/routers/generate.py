"""LangGraph-powered content generation API."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.graph.graph import graph_mermaid, run_repurpose_graph
from app.models.content import GenerateContentRequest, GenerateContentResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["langgraph"])


@router.post("/api/generate-content", response_model=GenerateContentResponse)
@router.post("/generate-content", response_model=GenerateContentResponse, include_in_schema=False)
async def generate_content(request: GenerateContentRequest):
    """
    Production LangGraph workflow:
    validate → summarize → insights → tone → parallel formats →
    quality (conditional retry) → MongoDB → response.
    """
    try:
        result = await run_repurpose_graph(
            article=request.article,
            formats=request.formats,
            tone=request.tone,
            thread_id=request.thread_id,
            provider_id=request.provider_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("LangGraph generate-content failed")
        raise HTTPException(status_code=500, detail=f"Generation failed: {e}") from e

    outputs = result.get("outputs") or {}
    return GenerateContentResponse(
        workflow_id=result.get("workflow_id") or "",
        workflow_status=result.get("workflow_status") or "",
        summary=result.get("summary") or "",
        tone=result.get("tone") or "",
        insights=result.get("insights") or {},
        youtube_script=outputs.get("youtube", ""),
        reel_script=outputs.get("reel", ""),
        linkedin_post=outputs.get("linkedin", ""),
        instagram_carousel=outputs.get("carousel", ""),
        voiceover_script=outputs.get("voiceover", ""),
        outputs=outputs,
        quality_score=float(result.get("quality_score") or 0),
        quality_notes=result.get("quality_notes") or "",
        model_used=result.get("model_used") or "",
        provider_id=result.get("provider_id") or "",
        prompt_version=result.get("prompt_version") or "",
        document_id=result.get("document_id") or "",
        processing_time=float(result.get("processing_time") or 0),
        node_timings=result.get("node_timings") or {},
        usage=result.get("usage") or {},
        errors=list(result.get("errors") or []),
        failed_formats=list(result.get("failed_formats") or []),
        retry_count=int(result.get("retry_count") or 0),
    )


@router.get("/api/generate-content/graph")
async def generate_content_graph_diagram():
    """Mermaid visualization of the compiled LangGraph (for debugging/docs)."""
    try:
        return {"mermaid": graph_mermaid()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
