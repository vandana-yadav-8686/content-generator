from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.prompt_schemas import (
    FormatPromptResponse,
    FormatPromptUpdate,
    GlobalPromptResponse,
    GlobalPromptUpdate,
    PromptListResponse,
)
from app.services.prompt_store import prompt_store

router = APIRouter(prefix="/api/prompts", tags=["prompts"])

GLOBAL_IDS = frozenset({"system", "extraction", "batch", "expand"})


def _to_response(item: dict) -> GlobalPromptResponse | FormatPromptResponse:
    if item["category"] == "global":
        return GlobalPromptResponse(**item)
    return FormatPromptResponse(**item)


@router.get("", response_model=PromptListResponse)
async def list_prompts():
    items = [_to_response(p) for p in prompt_store.list_prompts()]
    return PromptListResponse(prompts=items)


class ResetBody(BaseModel):
    prompt_id: str | None = None


@router.post("/reset")
async def reset_prompts(body: ResetBody | None = None):
    prompt_id = body.prompt_id if body else None
    try:
        prompt_store.reset_prompt(prompt_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if prompt_id:
        item = prompt_store.get_prompt(prompt_id)
        return {"message": f"Reset {prompt_id}", "prompt": _to_response(item) if item else None}
    return {"message": "All prompts reset to defaults"}


@router.get("/{prompt_id}/defaults")
async def get_default_prompt(prompt_id: str):
    try:
        return prompt_store.get_defaults_for(prompt_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/{prompt_id}")
async def get_prompt(prompt_id: str):
    item = prompt_store.get_prompt(prompt_id)
    if not item:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return _to_response(item)


@router.put("/{prompt_id}")
async def update_prompt(prompt_id: str, body: dict):
    try:
        if prompt_id in GLOBAL_IDS:
            content = body.get("content", "").strip()
            if not content:
                raise ValueError("content is required")
            updated = prompt_store.update_prompt(prompt_id, {"content": content})
        else:
            payload = {
                k: body[k]
                for k in ("format_prompt", "example")
                if k in body and body[k] is not None
            }
            if not payload:
                raise ValueError("format_prompt and/or example is required")
            updated = prompt_store.update_prompt(prompt_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return _to_response(updated)
