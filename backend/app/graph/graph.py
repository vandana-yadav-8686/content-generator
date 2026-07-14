"""
LangGraph StateGraph — production composition.

Extension model
---------------
Parallel format nodes are driven by FORMAT_REGISTRY. To add Twitter:
register a FormatSpec; this module wires it automatically.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from app.graph.nodes.formats import FORMAT_NODES
from app.graph.nodes.insights import extract_insights
from app.graph.nodes.mongodb import save_to_mongodb
from app.graph.nodes.review import quality_review
from app.graph.nodes.summarize import summarize
from app.graph.nodes.tone import detect_tone
from app.graph.nodes.validate import validate_input
from app.graph.registry import FORMAT_REGISTRY, PROMPT_VERSION, normalize_format_ids
from app.graph.state import GraphState
from app.services.graph_llm import reset_llm_service

logger = logging.getLogger(__name__)

FORMAT_NODE_NAMES = tuple(FORMAT_REGISTRY.keys())


def fan_out_formats(state: GraphState) -> list[Send]:
    """Spawn independent format nodes in parallel via Send()."""
    selected = state.get("selected_formats") or list(FORMAT_NODE_NAMES)
    return [Send(node, state) for node in selected if node in FORMAT_REGISTRY]


def after_quality(state: GraphState) -> str | list[Send]:
    """
    Conditional routing:
    - score < 90 & failures & retries left → regenerate ONLY failed formats
    - else → save
    """
    regen = state.get("regenerate_formats") or []
    if regen:
        logger.info(
            "conditional_retry formats=%s retry_count=%s",
            regen,
            state.get("retry_count"),
        )
        return [Send(node, state) for node in regen if node in FORMAT_REGISTRY]
    return "mongodb_save"


def build_graph(*, checkpointer: Any | None = None):
    g = StateGraph(GraphState)

    g.add_node("validate", validate_input)
    g.add_node("summarize", summarize)
    g.add_node("insights", extract_insights)
    g.add_node("tone", detect_tone)

    for fmt_id, node_fn in FORMAT_NODES.items():
        g.add_node(fmt_id, node_fn)

    g.add_node("quality_review", quality_review)
    g.add_node("mongodb_save", save_to_mongodb)

    g.add_edge(START, "validate")
    g.add_edge("validate", "summarize")
    g.add_edge("summarize", "insights")
    g.add_edge("insights", "tone")
    g.add_conditional_edges("tone", fan_out_formats, list(FORMAT_NODE_NAMES))

    for fmt_id in FORMAT_NODE_NAMES:
        g.add_edge(fmt_id, "quality_review")

    g.add_conditional_edges(
        "quality_review",
        after_quality,
        [*FORMAT_NODE_NAMES, "mongodb_save"],
    )
    g.add_edge("mongodb_save", END)

    return g.compile(checkpointer=checkpointer)


_memory = MemorySaver()
_compiled = None


def get_compiled_graph():
    """Compiled graph with in-memory checkpointing (swap for Postgres/SQLite later)."""
    global _compiled
    if _compiled is None:
        _compiled = build_graph(checkpointer=_memory)
    return _compiled


def graph_mermaid() -> str:
    """Return Mermaid diagram source for docs / debugging."""
    return get_compiled_graph().get_graph().draw_mermaid()


async def run_repurpose_graph(
    *,
    article: str,
    formats: list[str] | None = None,
    tone: str = "auto",
    thread_id: str | None = None,
    provider_id: str | None = None,
) -> dict[str, Any]:
    """Execute workflow; returns flat result including extensible `outputs`."""
    from app.models.schemas import ProviderId as Pid

    parsed: Pid | None = None
    if provider_id:
        try:
            parsed = Pid(provider_id)
        except ValueError:
            parsed = None
    reset_llm_service(parsed)

    graph = get_compiled_graph()
    selected = normalize_format_ids(formats)
    started = time.perf_counter()
    workflow_id = str(uuid.uuid4())
    thread = thread_id or workflow_id

    initial: GraphState = {
        "article": article,
        "selected_formats": selected,
        "requested_tone": tone,
        "workflow_id": workflow_id,
        "cleaned_article": "",
        "summary": "",
        "tone": "",
        "insights": {},
        "outputs": {},
        "quality_score": 0.0,
        "quality_notes": "",
        "failed_formats": [],
        "regenerate_formats": [],
        "retry_count": 0,
        "workflow_status": "pending",
        "model_used": "",
        "provider_id": "",
        "prompt_version": PROMPT_VERSION,
        "errors": [],
        "node_timings": {},
        "usage": {},
        "processing_time": 0.0,
    }

    config = {"configurable": {"thread_id": thread}}
    final = await graph.ainvoke(initial, config=config)
    final["processing_time"] = round(time.perf_counter() - started, 3)
    if not final.get("workflow_status") or final["workflow_status"] == "running":
        final["workflow_status"] = "partial" if final.get("failed_formats") else "completed"
    return dict(final)
