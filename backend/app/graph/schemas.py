"""Pydantic schemas for structured LLM outputs (LangChain parsers)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ArticleInsights(BaseModel):
    topic: str = Field(description="One-sentence topic")
    audience: str = Field(description="Primary audience")
    key_points: list[str] = Field(default_factory=list)
    facts: list[str] = Field(default_factory=list)
    statistics: list[str] = Field(default_factory=list)
    quotes: list[str] = Field(default_factory=list)
    cta: str = Field(default="", description="Suggested call to action")
    keywords: list[str] = Field(default_factory=list)


class ToneResult(BaseModel):
    tone: Literal[
        "professional",
        "educational",
        "conversational",
        "inspirational",
        "news",
    ]


class QualityReviewResult(BaseModel):
    quality_score: float = Field(ge=0, le=100)
    notes: str = ""
    failed_formats: list[str] = Field(
        default_factory=list,
        description="Format node ids that must be regenerated (e.g. youtube, reel)",
    )
