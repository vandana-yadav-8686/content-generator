from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ProviderId(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    OPENROUTER = "openrouter"
    MISTRAL = "mistral"
    COHERE = "cohere"
    DEEPSEEK = "deepseek"


class ProviderConfig(BaseModel):
    provider_id: ProviderId
    enabled: bool = False
    api_key: Optional[str] = None
    model: str = ""
    base_url: Optional[str] = None


class ModelOption(BaseModel):
    id: str
    name: str
    modality: str = "text"


class ProviderConfigResponse(BaseModel):
    provider_id: ProviderId
    name: str
    description: str
    enabled: bool
    api_key_masked: Optional[str] = None
    has_api_key: bool = False
    model: str
    available_models: list[ModelOption]
    base_url: Optional[str] = None


class ProviderConfigUpdate(BaseModel):
    enabled: bool = False
    api_key: Optional[str] = None
    model: str = ""
    base_url: Optional[str] = None


class TestConnectionRequest(BaseModel):
    provider_id: ProviderId
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None


class TestConnectionResponse(BaseModel):
    success: bool
    message: str
    latency_ms: Optional[float] = None


class RepurposeRequest(BaseModel):
    article: str = Field(..., min_length=50)
    provider_id: Optional[ProviderId] = None
    tone: str = Field(default="professional")
    test_mode: bool = Field(
        default=False,
        description="Quick test: 1 format only, no expand/compress retries",
    )
    offline_mode: bool = Field(
        default=False,
        description="Use offline mock LLM — zero API calls, no rate limits",
    )
    skip_quality_passes: bool = Field(
        default=False,
        description="Skip expand/compress passes (fewer API calls)",
    )
    formats: list[str] = Field(
        default=[
            "youtube_script",
            "reel_script",
            "linkedin_post",
            "instagram_carousel",
            "voiceover_script",
        ]
    )


class ContentBrief(BaseModel):
    topic: str = ""
    audience: str = ""
    main_problem: str = ""
    main_solution: str = ""
    key_points: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)
    facts: list[str] = Field(default_factory=list)
    quotes: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    tone: str = ""
    best_hook: str = ""
    second_best_hook: str = ""


class RepurposeOutput(BaseModel):
    format: str
    content: str


class RepurposeResponse(BaseModel):
    provider_id: ProviderId
    model: str
    outputs: list[RepurposeOutput]
    brief: Optional[ContentBrief] = None
