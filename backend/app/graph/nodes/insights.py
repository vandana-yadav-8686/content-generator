"""ExtractInsightsNode — structured output with JSON salvage + fallback."""

from __future__ import annotations

import logging

from pydantic import ValidationError

from app.graph.nodes._utils import (
    coerce_insights,
    insights_from_summary,
    parse_json_object,
    run_node,
)
from app.graph.prompts.analysis.insights import prompt as insights_prompt
from app.graph.prompts.analysis.insights import retry_prompt
from app.graph.schemas import ArticleInsights
from app.graph.state import GraphState
from app.services.graph_llm import get_llm_service

logger = logging.getLogger(__name__)


def _validate_insights(data: dict) -> ArticleInsights:
    coerced = coerce_insights(data)
    return ArticleInsights.model_validate(coerced)


async def _call_insights_llm(llm, prompt, article: str, summary: str) -> ArticleInsights:
    raw = await llm.arun_prompt(
        prompt,
        {"article": article, "summary": summary},
        node="insights",
        max_tokens=900,
    )
    data = parse_json_object(raw)
    return _validate_insights(data)


async def extract_insights(state: GraphState) -> dict:
    async def _run() -> dict:
        llm = get_llm_service()
        article = state.get("cleaned_article") or state.get("article") or ""
        summary = state.get("summary") or ""
        errors: list[str] = []

        for attempt, prompt in enumerate((insights_prompt, retry_prompt), start=1):
            try:
                parsed = await _call_insights_llm(llm, prompt, article, summary)
                return {
                    "insights": parsed.model_dump(),
                    "usage": llm.session.usage_summary(),
                }
            except (ValueError, ValidationError) as exc:
                msg = f"insights attempt {attempt}: {exc}"
                logger.warning(msg)
                errors.append(msg)

        # Never block generation — derive minimal insights from summary/article
        fallback = insights_from_summary(summary, article)
        logger.warning("insights using summary fallback after %d failed attempts", len(errors))
        return {
            "insights": ArticleInsights.model_validate(fallback).model_dump(),
            "errors": errors + ["insights: used summary fallback (model JSON was invalid)"],
            "usage": llm.session.usage_summary(),
        }

    return await run_node("insights", _run, soft_fail=True)
