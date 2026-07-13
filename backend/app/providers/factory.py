from typing import Type

from app.models.schemas import ProviderId
from app.providers.base import LLMProvider, ProviderMetadata
from app.providers.openai_provider import OpenAIProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.groq_provider import GroqProvider
from app.providers.openrouter_provider import OpenRouterProvider
from app.providers.mistral_provider import MistralProvider
from app.providers.cohere_provider import CohereProvider
from app.providers.deepseek_provider import DeepSeekProvider


PROVIDER_REGISTRY: dict[ProviderId, Type[LLMProvider]] = {
    ProviderId.OPENAI: OpenAIProvider,
    ProviderId.GEMINI: GeminiProvider,
    ProviderId.ANTHROPIC: AnthropicProvider,
    ProviderId.GROQ: GroqProvider,
    ProviderId.OPENROUTER: OpenRouterProvider,
    ProviderId.MISTRAL: MistralProvider,
    ProviderId.COHERE: CohereProvider,
    ProviderId.DEEPSEEK: DeepSeekProvider,
}


class ProviderFactory:
    """Factory for creating LLM provider instances."""

    @staticmethod
    def get_provider_class(provider_id: ProviderId) -> Type[LLMProvider]:
        if provider_id not in PROVIDER_REGISTRY:
            raise ValueError(f"Unknown provider: {provider_id}")
        return PROVIDER_REGISTRY[provider_id]

    @staticmethod
    def create(
        provider_id: ProviderId,
        api_key: str,
        model: str | None = None,
        base_url: str | None = None,
    ) -> LLMProvider:
        provider_class = ProviderFactory.get_provider_class(provider_id)
        return provider_class(api_key=api_key, model=model, base_url=base_url)

    @staticmethod
    def get_all_metadata() -> list[ProviderMetadata]:
        return [cls.metadata for cls in PROVIDER_REGISTRY.values()]

    @staticmethod
    def register_provider(provider_id: ProviderId, provider_class: Type[LLMProvider]) -> None:
        """Register a new provider at runtime for extensibility."""
        PROVIDER_REGISTRY[provider_id] = provider_class
