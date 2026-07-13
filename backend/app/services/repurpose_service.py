import asyncio
import json
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass

from app.models.schemas import (
    ProviderId,
    RepurposeOutput,
    RepurposeRequest,
    RepurposeResponse,
)
from app.providers.factory import ProviderFactory
from app.providers.mock_provider import MockProvider
from app.prompts.defaults import ALL_FORMAT_IDS
from app.services.extraction_service import extraction_service
from app.services.prompt_builder import PromptBuilder
from app.services.prompts import (
    EXCERPT_CHARS,
    FORMAT_LABELS,
    FORMAT_MAX_TOKENS,
    FREE_TIER_PROVIDERS,
    MAX_ARTICLE_CHARS,
    MAX_WORD_COUNTS,
    MIN_WORD_COUNTS,
    OPEN_WEIGHT_MAX_TOKENS,
    OPEN_WEIGHT_PROVIDERS,
    dedupe_repeated_blocks,
    get_batch_prompt,
    get_compress_prompt,
    get_expand_prompt,
    get_format_examples,
    get_system_prompt,
    is_too_generic,
    is_too_long,
    local_cleanup,
    strip_draft_echo,
    word_count,
)
from app.services.settings_service import settings_repository

logger = logging.getLogger(__name__)

FREE_TIER_DELAY_SEC = 4
OPEN_WEIGHT_DELAY_SEC = 2
TEST_MODE_FORMATS = ["reel_script"]


@dataclass
class _Runtime:
    provider: object
    provider_id: ProviderId
    model: str
    open_weight: bool
    use_batch: bool
    offline: bool


class RepurposeService:
    def _resolve_formats(self, request: RepurposeRequest) -> tuple[list[str], bool]:
        skip_quality = request.skip_quality_passes or request.test_mode
        if request.test_mode:
            return list(TEST_MODE_FORMATS), True
        formats = [f for f in request.formats if f in ALL_FORMAT_IDS]
        if not formats:
            formats = list(ALL_FORMAT_IDS)
        return formats, skip_quality

    async def repurpose(self, request: RepurposeRequest) -> RepurposeResponse:
        runtime = self._build_runtime(request)
        provider = runtime.provider
        formats, skip_quality = self._resolve_formats(request)

        article = self._trim_article(request.article)
        excerpt = article[:EXCERPT_CHARS]
        tone = request.tone or "professional"

        try:
            brief_model = await extraction_service.extract(provider, article)
            await self._rate_limit_pause(runtime.provider_id, runtime.offline)
            brief = extraction_service.brief_to_text(brief_model)
            if runtime.use_batch:
                results = await self._generate_batch(
                    provider, runtime.provider_id, brief, excerpt, formats, skip_quality, runtime.offline
                )
            else:
                results = await self._generate_sequential(
                    provider,
                    runtime.provider_id,
                    brief,
                    excerpt,
                    formats,
                    runtime.open_weight,
                    tone,
                    skip_quality,
                    runtime.offline,
                )
        except Exception as e:
            raise ValueError(self._friendly_error(e, runtime.provider_id)) from e

        return RepurposeResponse(
            provider_id=runtime.provider_id,
            model=runtime.model,
            outputs=[RepurposeOutput(format=fmt, content=content) for fmt, content in results],
            brief=brief_model,
        )

    async def repurpose_stream(self, request: RepurposeRequest) -> AsyncIterator[dict]:
        """SSE event generator: extraction → per-format streaming chunks → done."""
        runtime = self._build_runtime(request)
        provider = runtime.provider
        article = self._trim_article(request.article)
        excerpt = article[:EXCERPT_CHARS]
        formats, skip_quality = self._resolve_formats(request)
        tone = request.tone or "professional"

        yield {"type": "status", "message": "Extracting article insights..."}

        try:
            brief_model = await extraction_service.extract(provider, article)
            brief = extraction_service.brief_to_text(brief_model)
            await self._rate_limit_pause(runtime.provider_id, runtime.offline)

            yield {"type": "extraction", "data": brief_model.model_dump()}

            for fmt in formats:
                label = FORMAT_LABELS.get(fmt, fmt)
                yield {"type": "format_start", "format": fmt, "label": label}

                built = (
                    PromptBuilder()
                    .set_platform(fmt)
                    .set_tone(tone)
                    .set_brief(brief)
                    .set_excerpt(excerpt)
                    .build()
                )
                max_tokens = self._max_tokens(fmt, runtime.open_weight)
                raw_parts: list[str] = []

                async for chunk in provider.stream_generate(
                    built.user_prompt,
                    system_prompt=built.system_prompt,
                    max_tokens=max_tokens,
                ):
                    raw_parts.append(chunk)
                    yield {"type": "chunk", "format": fmt, "content": chunk}

                raw = "".join(raw_parts)
                finalized = await self._finalize(
                    provider,
                    runtime.provider_id,
                    fmt,
                    raw,
                    brief,
                    excerpt,
                    runtime.open_weight,
                    skip_quality,
                    runtime.offline,
                )
                yield {"type": "format_done", "format": fmt, "content": finalized}
                await self._rate_limit_pause(runtime.provider_id, runtime.offline)

            yield {
                "type": "done",
                "provider_id": runtime.provider_id.value,
                "model": runtime.model,
            }
        except Exception as e:
            yield {"type": "error", "message": self._friendly_error(e, runtime.provider_id)}

    def _use_batch_mode(self, provider_id: ProviderId) -> bool:
        return provider_id.value in FREE_TIER_PROVIDERS

    def _is_open_weight(self, provider_id: ProviderId) -> bool:
        return provider_id.value in OPEN_WEIGHT_PROVIDERS

    def _friendly_error(self, error: Exception, provider_id: ProviderId) -> str:
        msg = str(error)
        if "429" not in msg and "RESOURCE_EXHAUSTED" not in msg and "rate limit" not in msg.lower():
            return msg

        if provider_id == ProviderId.GROQ:
            return (
                "Groq API rate limit reached (Groq's free-tier cap — this app cannot remove it). "
                "Options: wait 60 seconds and retry, use llama-3.1-8b-instant in Settings, "
                "enable Quick Test Mode (fewer calls), or check Offline demo on the home page "
                "(zero API calls)."
            )
        if provider_id == ProviderId.GEMINI:
            return (
                "Gemini quota exhausted. Wait a few minutes or switch to gemini-2.0-flash-lite in Settings."
            )
        return (
            f"Rate limit hit on {provider_id.value}. Wait a minute and retry, or switch provider in Settings."
        )

    async def _rate_limit_pause(self, provider_id: ProviderId, offline: bool = False) -> None:
        if offline:
            return
        if provider_id.value in FREE_TIER_PROVIDERS:
            await asyncio.sleep(FREE_TIER_DELAY_SEC)
        elif provider_id.value in OPEN_WEIGHT_PROVIDERS:
            await asyncio.sleep(OPEN_WEIGHT_DELAY_SEC)

    def _build_runtime(self, request: RepurposeRequest) -> _Runtime:
        if request.offline_mode:
            return _Runtime(
                provider=MockProvider(api_key="offline"),
                provider_id=ProviderId.GROQ,
                model="offline-mock",
                open_weight=False,
                use_batch=False,
                offline=True,
            )

        config = self._resolve_provider(request.provider_id)
        provider = ProviderFactory.create(
            provider_id=config.provider_id,
            api_key=config.api_key,
            model=config.model,
            base_url=config.base_url,
        )
        formats, _ = self._resolve_formats(request)
        full_set = set(ALL_FORMAT_IDS)
        use_batch = (
            self._use_batch_mode(config.provider_id)
            and not request.test_mode
            and set(formats) == full_set
        )
        return _Runtime(
            provider=provider,
            provider_id=config.provider_id,
            model=config.model,
            open_weight=self._is_open_weight(config.provider_id),
            use_batch=use_batch,
            offline=False,
        )

    def _trim_article(self, article: str) -> str:
        text = article.strip()
        if len(text) <= MAX_ARTICLE_CHARS:
            return text
        return text[:MAX_ARTICLE_CHARS] + "\n\n[Article truncated for processing]"

    def _extract_json(self, raw: str) -> dict:
        import re
        text = raw.strip()
        fence = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if fence:
            text = fence.group(1).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start : end + 1]
        return json.loads(text)

    def _resolve_provider(self, provider_id: ProviderId | None):
        if provider_id:
            config = settings_repository.get(provider_id)
            if not config or not config.api_key:
                raise ValueError(f"Provider {provider_id.value} is not configured")
            if not config.enabled:
                raise ValueError(f"Provider {provider_id.value} is disabled")
            return config

        active = settings_repository.get_active_provider()
        if not active:
            raise ValueError("No active LLM provider configured. Go to Settings and enable a provider.")
        return active

    async def _finalize(
        self,
        provider,
        provider_id: ProviderId,
        fmt: str,
        content: str,
        brief: str,
        excerpt: str,
        open_weight: bool,
        skip_quality_passes: bool = False,
        offline: bool = False,
    ) -> str:
        content = local_cleanup(content)
        if skip_quality_passes:
            return dedupe_repeated_blocks(content)

        min_words = MIN_WORD_COUNTS.get(fmt, 100)
        max_words = MAX_WORD_COUNTS.get(fmt, 500)

        if is_too_long(content, fmt):
            logger.info("Compressing %s (words=%d, max=%d)", fmt, word_count(content), max_words)
            content = await self._compress_output(
                provider, provider_id, fmt, content, brief, open_weight, offline
            )
            content = local_cleanup(content)
        elif word_count(content) < min_words or is_too_generic(content):
            logger.info("Expanding %s (words=%d)", fmt, word_count(content))
            content = await self._expand_output(
                provider, provider_id, fmt, content, brief, excerpt, open_weight, offline
            )
            content = local_cleanup(content)

        return dedupe_repeated_blocks(content)

    async def _compress_output(
        self,
        provider,
        provider_id: ProviderId,
        fmt: str,
        draft: str,
        brief: str,
        open_weight: bool,
        offline: bool = False,
    ) -> str:
        prompt = get_compress_prompt().format(
            format_label=FORMAT_LABELS.get(fmt, fmt),
            max_words=MAX_WORD_COUNTS.get(fmt, 400),
            brief=brief,
            draft=draft,
        )
        max_tokens = min(self._max_tokens(fmt, open_weight), 600)
        result = await provider.generate(
            prompt,
            system_prompt=get_system_prompt(),
            max_tokens=max_tokens,
        )
        await self._rate_limit_pause(provider_id, offline)
        compressed = result.content.strip()
        return compressed if compressed else draft

    async def _expand_output(
        self,
        provider,
        provider_id: ProviderId,
        fmt: str,
        draft: str,
        brief: str,
        excerpt: str,
        open_weight: bool,
        offline: bool = False,
    ) -> str:
        prompt = get_expand_prompt().format(
            format_label=FORMAT_LABELS.get(fmt, fmt),
            min_words=MIN_WORD_COUNTS.get(fmt, 100),
            max_words=MAX_WORD_COUNTS.get(fmt, 400),
            brief=brief,
            excerpt=excerpt,
            draft=draft,
        )
        max_tokens = self._max_tokens(fmt, open_weight)
        result = await provider.generate(
            prompt,
            system_prompt=get_system_prompt(),
            max_tokens=max_tokens,
        )
        await self._rate_limit_pause(provider_id, offline)

        expanded = result.content.strip()
        if not expanded:
            return draft

        expanded = strip_draft_echo(expanded, draft)
        if expanded.strip() == draft.strip():
            return draft

        return expanded

    async def _generate_batch(
        self,
        provider,
        provider_id: ProviderId,
        brief: str,
        excerpt: str,
        formats: list[str],
        skip_quality_passes: bool = False,
        offline: bool = False,
    ) -> list[tuple[str, str]]:
        examples = get_format_examples()
        prompt = get_batch_prompt().format(
            brief=brief,
            excerpt=excerpt,
            example_youtube=examples["youtube_script"],
            example_reel=examples["reel_script"],
            example_linkedin=examples["linkedin_post"],
            example_carousel=examples["instagram_carousel"],
            example_voiceover=examples["voiceover_script"],
        )
        result = await provider.generate(
            prompt,
            system_prompt=get_system_prompt(),
            max_tokens=4000,
        )
        await self._rate_limit_pause(provider_id, offline)

        try:
            outputs = self._extract_json(result.content)
        except (json.JSONDecodeError, ValueError):
            return await self._generate_sequential(
                provider,
                provider_id,
                brief,
                excerpt,
                formats,
                False,
                "professional",
                skip_quality_passes,
                offline,
            )

        results: list[tuple[str, str]] = []
        for fmt in formats:
            raw = outputs.get(fmt, "")
            finalized = await self._finalize(
                provider,
                provider_id,
                fmt,
                raw,
                brief,
                excerpt,
                False,
                skip_quality_passes,
                offline,
            )
            results.append((fmt, finalized))
            await self._rate_limit_pause(provider_id, offline)
        return results

    async def _generate_sequential(
        self,
        provider,
        provider_id: ProviderId,
        brief: str,
        excerpt: str,
        formats: list[str],
        open_weight: bool,
        tone: str,
        skip_quality_passes: bool = False,
        offline: bool = False,
    ) -> list[tuple[str, str]]:
        results: list[tuple[str, str]] = []
        for fmt in formats:
            content = await self._generate_format(
                provider,
                provider_id,
                fmt,
                brief,
                excerpt,
                open_weight,
                tone,
                skip_quality_passes,
                offline,
            )
            results.append((fmt, content))
            await self._rate_limit_pause(provider_id, offline)
        return results

    def _max_tokens(self, fmt: str, open_weight: bool) -> int:
        if open_weight:
            return OPEN_WEIGHT_MAX_TOKENS.get(fmt, 500)
        return FORMAT_MAX_TOKENS.get(fmt, 800)

    async def _generate_format(
        self,
        provider,
        provider_id: ProviderId,
        fmt: str,
        brief: str,
        excerpt: str,
        open_weight: bool,
        tone: str,
        skip_quality_passes: bool = False,
        offline: bool = False,
    ) -> str:
        built = (
            PromptBuilder()
            .set_platform(fmt)
            .set_tone(tone)
            .set_brief(brief)
            .set_excerpt(excerpt)
            .build()
        )
        max_tokens = self._max_tokens(fmt, open_weight)

        result = await provider.generate(
            built.user_prompt,
            system_prompt=built.system_prompt,
            max_tokens=max_tokens,
        )
        return await self._finalize(
            provider,
            provider_id,
            fmt,
            result.content,
            brief,
            excerpt,
            open_weight,
            skip_quality_passes,
            offline,
        )


repurpose_service = RepurposeService()
