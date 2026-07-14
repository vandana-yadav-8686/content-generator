"""
Format generation nodes — built from FORMAT_REGISTRY.

Factory pattern: one implementation, N registered formats.
Adding a future format = register FormatSpec + prompt module.
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any

from app.graph.nodes._utils import excerpt, insights_json, run_node
from app.graph.registry import FORMAT_REGISTRY, FormatSpec
from app.graph.state import GraphState
from app.services.graph_llm import get_llm_service


def make_format_node(spec: FormatSpec) -> Callable[[GraphState], Coroutine[Any, Any, dict]]:
    """Create a LangGraph node function for a FormatSpec."""

    async def format_node(state: GraphState) -> dict:
        async def _run() -> dict:
            selected = set(state.get("selected_formats") or [])
            regen = set(state.get("regenerate_formats") or [])
            outputs = dict(state.get("outputs") or {})

            # Skip when not selected / not targeted for regenerate
            if regen:
                if spec.id not in regen:
                    return {"outputs": {spec.id: outputs.get(spec.id, "")}}
            elif spec.id not in selected:
                return {"outputs": {spec.id: outputs.get(spec.id, "")}}

            llm = get_llm_service()
            prompt = spec.prompt_factory()
            content = await llm.arun_prompt(
                prompt,
                {
                    "tone": state.get("tone") or "professional",
                    "summary": state.get("summary") or "",
                    "insights": insights_json(state),
                    "excerpt": excerpt(state),
                },
                node=spec.id,
                max_tokens=spec.max_tokens,
            )
            # Only write merge-safe keys — parallel nodes share one graph step.
            return {
                "outputs": {spec.id: content},
                "usage": llm.session.usage_summary(),
            }

        return await run_node(spec.id, _run, soft_fail=True)

    format_node.__name__ = f"generate_{spec.id}"
    format_node.__doc__ = f"Generate {spec.label}."
    return format_node


# Concrete node callables registered on the graph
FORMAT_NODES: dict[str, Callable[[GraphState], Coroutine[Any, Any, dict]]] = {
    fmt_id: make_format_node(spec) for fmt_id, spec in FORMAT_REGISTRY.items()
}
