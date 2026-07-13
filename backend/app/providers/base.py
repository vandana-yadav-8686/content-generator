from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelInfo:
    id: str
    name: str
    modality: str = "text"


@dataclass
class ProviderMetadata:
    id: str
    name: str
    description: str
    default_model: str
    models: list[ModelInfo] = field(default_factory=list)
    key_prefix_hint: str = ""
    supports_custom_base_url: bool = False
    default_base_url: Optional[str] = None

    @property
    def model_ids(self) -> list[str]:
        return [model.id for model in self.models]


def text_models(*entries: tuple[str, str] | str) -> list[ModelInfo]:
    """Helper to build model lists from id/name pairs or plain ids."""
    result: list[ModelInfo] = []
    for entry in entries:
        if isinstance(entry, str):
            result.append(ModelInfo(id=entry, name=entry))
        else:
            result.append(ModelInfo(id=entry[0], name=entry[1]))
    return result


@dataclass
class GenerationResult:
    content: str
    model: str
    tokens_used: Optional[int] = None


@dataclass
class TestResult:
    success: bool
    message: str
    latency_ms: Optional[float] = None


class LLMProvider(ABC):
    """Base adapter for all LLM providers."""

    metadata: ProviderMetadata

    def __init__(self, api_key: str, model: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.model = model or self.metadata.default_model
        self.base_url = base_url or self.metadata.default_base_url

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> GenerationResult:
        pass

    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Yield text chunks. Default: single chunk from non-streaming generate."""
        result = await self.generate(prompt, system_prompt=system_prompt, max_tokens=max_tokens)
        if result.content:
            yield result.content

    @abstractmethod
    async def test_connection(self) -> TestResult:
        pass

    def validate_api_key(self, api_key: str) -> tuple[bool, str]:
        if not api_key or not api_key.strip():
            return False, "API key is required"
        if len(api_key.strip()) < 8:
            return False, "API key appears too short"
        return True, "Valid format"

    def get_available_models(self) -> list[ModelInfo]:
        return self.metadata.models
