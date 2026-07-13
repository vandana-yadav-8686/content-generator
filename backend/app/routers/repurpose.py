import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import RepurposeRequest, RepurposeResponse
from app.services.repurpose_service import repurpose_service

router = APIRouter(prefix="/api/repurpose", tags=["repurpose"])


@router.post("/", response_model=RepurposeResponse)
async def repurpose_article(request: RepurposeRequest):
    try:
        return await repurpose_service.repurpose(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repurposing failed: {str(e)}")


@router.post("/stream")
async def repurpose_stream(request: RepurposeRequest):
    async def event_generator():
        try:
            async for event in repurpose_service.repurpose_stream(request):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
