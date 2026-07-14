"""Shared node utilities — timing, excerpt, JSON salvage."""

from __future__ import annotations

import ast
import json
import logging
import re
import time
from collections.abc import Awaitable, Callable
from typing import Any

from app.graph.state import GraphState

logger = logging.getLogger(__name__)

EXCERPT_CHARS = 3500
MIN_ARTICLE_CHARS = 50


def excerpt(state: GraphState) -> str:
    text = state.get("cleaned_article") or state.get("article") or ""
    return text[:EXCERPT_CHARS]


def insights_json(state: GraphState) -> str:
    return json.dumps(state.get("insights") or {}, ensure_ascii=False, indent=2)


def _strip_wrappers(text: str) -> str:
    text = text.strip().lstrip("\ufeff")
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start : end + 1]
    return text.strip()


def _remove_trailing_commas(text: str) -> str:
    return re.sub(r",\s*([}\]])", r"\1", text)


def _quote_unquoted_keys(text: str) -> str:
    """Fix {topic: "x"} → {"topic": "x"} (common LLM mistake)."""
    return re.sub(r"([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)", r'\1"\2"\3', text)


def _python_literals_to_json(text: str) -> str:
    text = re.sub(r"\bNone\b", "null", text)
    text = re.sub(r"\bTrue\b", "true", text)
    text = re.sub(r"\bFalse\b", "false", text)
    return text


def _try_parse(candidate: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass
    try:
        obj = ast.literal_eval(candidate)
        if isinstance(obj, dict):
            return obj
    except (ValueError, SyntaxError):
        pass
    return None


def parse_json_object(raw: str) -> dict[str, Any]:
    """
    Parse LLM JSON output with salvage for markdown fences, single quotes,
    trailing commas, unquoted keys, and Python literals.
    """
    text = _strip_wrappers(raw)
    if not text:
        raise ValueError("Empty JSON payload from model")

    variants: list[str] = []
    for base in (text, _quote_unquoted_keys(text), _python_literals_to_json(text)):
        variants.append(base)
        variants.append(_remove_trailing_commas(base))
        variants.append(_python_literals_to_json(_remove_trailing_commas(_quote_unquoted_keys(base))))

    seen: set[str] = set()
    last_error: Exception | None = None
    for candidate in variants:
        if candidate in seen:
            continue
        seen.add(candidate)
        parsed = _try_parse(candidate)
        if parsed is not None:
            return parsed
        try:
            json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = exc

    logger.warning("parse_json_object failed preview=%r", text[:400])
    if last_error is not None:
        raise ValueError(f"Invalid JSON from model: {last_error}") from last_error
    raise ValueError("Invalid JSON from model: expected a JSON object")


def coerce_insights(data: dict[str, Any]) -> dict[str, Any]:
    """Map heterogeneous LLM keys into ArticleInsights field names."""

    def as_list(value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [line.strip() for line in value.split("\n") if line.strip()]
        return []

    def as_str(value: Any, default: str = "") -> str:
        if value is None:
            return default
        text = str(value).strip()
        return text or default

    return {
        "topic": as_str(
            data.get("topic")
            or data.get("main_topic")
            or data.get("subject")
            or data.get("title")
        ),
        "audience": as_str(data.get("audience") or data.get("target_audience")),
        "key_points": as_list(
            data.get("key_points") or data.get("points") or data.get("insights")
        ),
        "facts": as_list(data.get("facts")),
        "statistics": as_list(data.get("statistics") or data.get("stats")),
        "quotes": as_list(data.get("quotes")),
        "cta": as_str(data.get("cta")),
        "keywords": as_list(data.get("keywords") or data.get("tags")),
    }


def insights_from_summary(summary: str, article: str) -> dict[str, Any]:
    """Last-resort insights when the model will not return parseable JSON."""
    summary = (summary or "").strip()
    article = (article or "").strip()
    snippet = summary or article[:500]
    sentences = [s.strip() for s in re.split(r"[.!?]+", snippet) if s.strip()]
    key_points = sentences[:3] if sentences else ([snippet[:200]] if snippet else [])
    return {
        "topic": (sentences[0][:200] if sentences else snippet[:200]) or "Article topic",
        "audience": "General audience",
        "key_points": key_points,
        "facts": key_points[:2],
        "statistics": [],
        "quotes": [],
        "cta": "",
        "keywords": [],
    }


async def run_node(
    name: str,
    fn: Callable[[], Awaitable[dict]],
    *,
    soft_fail: bool = True,
) -> dict:
    """Execute a node with timing + optional soft failure (workflow continues)."""
    started = time.perf_counter()
    logger.info("node_start name=%s", name)
    try:
        result = await fn()
    except Exception as exc:
        elapsed = round(time.perf_counter() - started, 3)
        logger.exception("node_error name=%s seconds=%.3f", name, elapsed)
        if not soft_fail:
            raise
        return {
            "errors": [f"{name}: {exc}"],
            "node_timings": {name: elapsed},
        }
    elapsed = round(time.perf_counter() - started, 3)
    logger.info("node_end name=%s seconds=%.3f", name, elapsed)
    out = dict(result)
    timings = dict(out.get("node_timings") or {})
    timings[name] = elapsed
    out["node_timings"] = timings
    return out
