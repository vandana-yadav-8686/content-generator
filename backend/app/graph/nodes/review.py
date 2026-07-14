"""QualityReviewNode — structured review + conditional regenerate list."""

from __future__ import annotations

from app.graph.nodes._utils import insights_json, run_node
from app.graph.prompts.review.quality import prompt as quality_prompt
from app.graph.registry import FORMAT_REGISTRY
from app.graph.schemas import QualityReviewResult
from app.graph.state import GraphState
from app.services.graph_llm import get_llm_service

MAX_RETRIES = 2


def _heuristic_failures(state: GraphState) -> list[str]:
    failed: list[str] = []
    selected = set(state.get("selected_formats") or FORMAT_REGISTRY.keys())
    outputs = state.get("outputs") or {}
    for fmt_id in selected:
        content = (outputs.get(fmt_id) or "").strip()
        if len(content) < 80:
            failed.append(fmt_id)
    return failed


async def quality_review(state: GraphState) -> dict:
    async def _run() -> dict:
        retry_count = int(state.get("retry_count") or 0)
        selected = list(state.get("selected_formats") or FORMAT_REGISTRY.keys())
        outputs = state.get("outputs") or {}
        heuristic = _heuristic_failures(state)

        outputs_block = "\n\n".join(
            f"### {fmt_id}\n{(outputs.get(fmt_id) or '(empty)').strip()}"
            for fmt_id in selected
        )

        llm = get_llm_service()
        try:
            parsed = await llm.arun_structured(
                quality_prompt,
                {
                    "summary": state.get("summary") or "",
                    "tone": state.get("tone") or "",
                    "insights": insights_json(state),
                    "outputs_block": outputs_block,
                    "format_ids": ", ".join(selected),
                },
                schema=QualityReviewResult,
                node="quality_review",
                max_tokens=700,
            )
            score = float(parsed.quality_score)
            notes = parsed.notes
            failed = [f for f in parsed.failed_formats if f in selected]
        except Exception as exc:
            score = 70.0 if heuristic else 90.0
            notes = f"Review parse fallback: {exc}"
            failed = heuristic

        for fmt_id in heuristic:
            if fmt_id not in failed:
                failed.append(fmt_id)

        regenerate: list[str] = []
        status = "completed"
        if score < 90 and failed and retry_count < MAX_RETRIES:
            regenerate = failed
            retry_count += 1
            status = "running"
        elif failed:
            status = "partial"
            if score >= 90:
                score = min(score, 88.0)

        return {
            "quality_score": round(score, 1),
            "quality_notes": notes,
            "failed_formats": failed,
            "regenerate_formats": regenerate,
            "retry_count": retry_count,
            "workflow_status": status,
            "usage": llm.session.usage_summary(),
        }

    return await run_node("quality_review", _run, soft_fail=True)
