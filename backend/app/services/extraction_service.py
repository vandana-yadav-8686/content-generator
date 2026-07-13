"""Structured content extraction — runs before any format generation."""

from __future__ import annotations

import json
import logging
import re

from app.models.schemas import ContentBrief
from app.services.prompts import get_extraction_prompt, get_system_prompt

logger = logging.getLogger(__name__)


class ExtractionService:
    def parse_brief_json(self, raw: str) -> ContentBrief:
        text = raw.strip()
        fence = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if fence:
            text = fence.group(1).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start : end + 1]
        data = json.loads(text)
        return ContentBrief.model_validate(data)

    def brief_to_text(self, brief: ContentBrief) -> str:
        return brief.model_dump_json(indent=2)

    async def extract(self, provider, article: str) -> ContentBrief:
        prompt = get_extraction_prompt().format(article=article)
        result = await provider.generate(
            prompt,
            system_prompt=get_system_prompt(),
            max_tokens=900,
        )
        try:
            return self.parse_brief_json(result.content)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning("Extraction JSON parse failed, using fallback: %s", e)
            return ContentBrief(
                topic=result.content[:200].strip(),
                audience="General audience",
                tone="informative",
            )


extraction_service = ExtractionService()
