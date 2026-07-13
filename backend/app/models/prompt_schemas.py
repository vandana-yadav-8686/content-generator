from pydantic import BaseModel, Field


class GlobalPromptUpdate(BaseModel):
    content: str = Field(..., min_length=10)


class FormatPromptUpdate(BaseModel):
    format_prompt: str | None = None
    example: str | None = None


class PromptMeta(BaseModel):
    id: str
    label: str
    category: str
    is_customized: bool
    placeholders: list[str] = []


class GlobalPromptResponse(PromptMeta):
    content: str


class FormatPromptResponse(PromptMeta):
    format_prompt: str
    example: str


class PromptListResponse(BaseModel):
    prompts: list[GlobalPromptResponse | FormatPromptResponse]
