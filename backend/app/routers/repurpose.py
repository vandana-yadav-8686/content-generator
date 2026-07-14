import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.graph.graph import run_repurpose_graph
from app.graph.registry import FORMAT_REGISTRY
from app.graph.stream import stream_repurpose_graph
from app.models.schemas import (
    ProviderId,
    RepurposeOutput,
    RepurposeRequest,
    RepurposeResponse,
)

router = APIRouter(prefix="/api/repurpose", tags=["repurpose"])


def _outputs_from_graph(result: dict) -> list[RepurposeOutput]:
    outputs = result.get("outputs") or {}
    items: list[RepurposeOutput] = []
    for node_id, content in outputs.items():
        spec = FORMAT_REGISTRY.get(node_id)
        if not spec or not (content or "").strip():
            continue
        items.append(RepurposeOutput(format=spec.api_id, content=content))
    return items


@router.post("/", response_model=RepurposeResponse)
async def repurpose_article(request: RepurposeRequest):
    """Generate via LangGraph using app/graph/prompts (not classic app/prompts)."""
    try:
        result = await run_repurpose_graph(
            article=request.article,
            formats=request.formats,
            tone=request.tone,
            provider_id=request.provider_id.value if request.provider_id else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repurposing failed: {e}") from e

    provider_raw = result.get("provider_id") or "openai"
    try:
        provider = ProviderId(provider_raw)
    except ValueError:
        provider = ProviderId.OPENAI

    return RepurposeResponse(
        provider_id=provider,
        model=result.get("model_used") or "",
        outputs=_outputs_from_graph(result),
    )


@router.post("/stream")
async def repurpose_stream(request: RepurposeRequest):
    """SSE stream powered by LangGraph + graph/prompts."""

    async def event_generator():
        async for event in stream_repurpose_graph(
            article=request.article,
            formats=request.formats,
            tone=request.tone,
            provider_id=request.provider_id.value if request.provider_id else None,
        ):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
