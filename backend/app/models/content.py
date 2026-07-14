from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class GenerateContentRequest(BaseModel):
    article: str = Field(..., min_length=50)
    formats: list[str] = Field(
        default_factory=lambda: [
            "youtube_script",
            "reel_script",
            "linkedin_post",
            "instagram_carousel",
            "voiceover_script",
        ]
    )
    tone: str = Field(default="auto")
    provider_id: Optional[str] = None
    thread_id: Optional[str] = Field(
        default=None,
        description="Optional LangGraph thread id for checkpoint resume",
    )


class GenerateContentResponse(BaseModel):
    workflow_id: str = ""
    workflow_status: str = ""
    summary: str = ""
    tone: str = ""
    insights: dict[str, Any] = Field(default_factory=dict)
    # Flat fields for API compatibility
    youtube_script: str = ""
    reel_script: str = ""
    linkedin_post: str = ""
    instagram_carousel: str = ""
    voiceover_script: str = ""
    # Extensible map (preferred going forward)
    outputs: dict[str, str] = Field(default_factory=dict)
    quality_score: float = 0
    quality_notes: str = ""
    model_used: str = ""
    provider_id: str = ""
    prompt_version: str = ""
    document_id: str = ""
    processing_time: float = 0
    node_timings: dict[str, float] = Field(default_factory=dict)
    usage: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    failed_formats: list[str] = Field(default_factory=list)
    retry_count: int = 0


class RepurposedContentDocument(BaseModel):
    workflow_id: str
    workflow_status: str
    original_article: str
    summary: str
    key_insights: dict[str, Any]
    tone: str
    outputs: dict[str, str] = Field(default_factory=dict)
    quality_score: float = 0
    model_used: str = ""
    model_version: str = ""
    prompt_version: str = ""
    processing_time: float = 0
    retry_count: int = 0
    usage: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    embedding: Any | None = None
    tenant_id: str | None = None
