"""SummarizeNode — ChatPromptTemplate → StrOutputParser path."""

from __future__ import annotations

from app.graph.nodes._utils import run_node
from app.graph.prompts.analysis.summarize import prompt as summarize_prompt
from app.graph.state import GraphState
from app.services.graph_llm import get_llm_service


async def summarize(state: GraphState) -> dict:
    async def _run() -> dict:
        llm = get_llm_service()
        article = state.get("cleaned_article") or state.get("article") or ""
        summary = await llm.arun_prompt(
            summarize_prompt,
            {"article": article},
            node="summarize",
            max_tokens=500,
        )
        return {
            "summary": summary,
            "provider_id": llm.session.provider_id,
            "model_used": llm.session.model,
            "usage": llm.session.usage_summary(),
        }

    return await run_node("summarize", _run, soft_fail=False)
