"""Real HITL2 autonomous decision node.

@impl HIT-001
@impl HIT-002
@impl ALR-001
@impl ALR-002
"""

from __future__ import annotations

from typing import Any

from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.state import node_state_update

from .prompts import recommend_hitl2_route


def build_real(dependencies: NodeBuildDependencies):
    """Build the real HITL2 node with graph-owned autonomous continuation."""

    async def run(state: dict[str, Any]) -> dict[str, Any]:
        recommendation = recommend_hitl2_route(state)
        updates: dict[str, Any] = {"route": recommendation.route.value}
        if recommendation.route.value == "rerun":
            updates["rerun_source"] = "hitl2"
        return node_state_update("hitl2", **updates)

    return run
