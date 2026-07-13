import logging
import re

from app.prompts.defaults import (
    ALL_FORMAT_IDS,
    BANNED_PHRASE_REPLACEMENTS,
    EXCERPT_CHARS,
    FORMAT_LABELS,
    FORMAT_MAX_TOKENS,
    FREE_TIER_PROVIDERS,
    GENERIC_PHRASES,
    MAX_ARTICLE_CHARS,
    MAX_WORD_COUNTS,
    MIN_WORD_COUNTS,
    OPEN_WEIGHT_MAX_TOKENS,
    OPEN_WEIGHT_PROVIDERS,
)
from app.prompts.compress import COMPRESS_PROMPT
from app.services.prompt_store import prompt_store

logger = logging.getLogger(__name__)

# Re-export format ids for callers that iterate FORMAT_PROMPTS keys
FORMAT_PROMPTS = {fmt: "" for fmt in ALL_FORMAT_IDS}
FORMAT_EXAMPLES = {fmt: "" for fmt in ALL_FORMAT_IDS}


def get_system_prompt() -> str:
    return prompt_store.get_system_prompt()


def get_extraction_prompt() -> str:
    return prompt_store.get_extraction_prompt()


def get_batch_prompt() -> str:
    return prompt_store.get_batch_prompt()


def get_expand_prompt() -> str:
    return prompt_store.get_expand_prompt()


def get_compress_prompt() -> str:
    return COMPRESS_PROMPT


def get_format_prompts() -> dict[str, str]:
    return prompt_store.get_format_prompts()


def get_format_examples() -> dict[str, str]:
    return prompt_store.get_format_examples()


def local_cleanup(text: str) -> str:
    result = text
    for pattern, replacement in BANNED_PHRASE_REPLACEMENTS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return re.sub(r"\n{3,}", "\n\n", result).strip()


def word_count(text: str) -> int:
    return len(text.split())


def is_too_generic(text: str) -> bool:
    lower = text.lower()
    if any(phrase in lower for phrase in GENERIC_PHRASES):
        return True
    # Flag uniformly long sentences — typical of AI essay output
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    if sentences:
        avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_len > 22:
            return True
    return False


def is_too_long(text: str, fmt: str) -> bool:
    return word_count(text) > MAX_WORD_COUNTS.get(fmt, 500)


def strip_draft_echo(text: str, draft: str) -> str:
    """Remove echoed copies of the pre-expand draft from model output."""
    text = text.strip()
    draft_norm = draft.strip()
    if not text or not draft_norm:
        return text

    if text == draft_norm:
        return text

    if text.count(draft_norm) >= 2:
        parts = [p.strip() for p in text.split(draft_norm) if p.strip()]
        candidates = [p for p in parts if p != draft_norm]
        if candidates:
            return max(candidates, key=len)

    while text.startswith(draft_norm):
        remainder = text[len(draft_norm) :].lstrip("\n")
        if not remainder or remainder == text:
            break
        text = remainder

    return text


def dedupe_repeated_blocks(text: str) -> str:
    """If the same paragraph block appears more than once, keep only the first."""
    blocks = re.split(r"\n\s*\n", text.strip())
    seen: list[str] = []
    deduped: list[str] = []
    removed = 0
    for block in blocks:
        normalized = re.sub(r"\s+", " ", block).strip().lower()
        if normalized and normalized in seen:
            removed += 1
            continue
        seen.append(normalized)
        deduped.append(block)
    if removed:
        logger.warning(
            "dedupe_repeated_blocks removed %d duplicate paragraph(s)", removed
        )
    return "\n\n".join(deduped)
