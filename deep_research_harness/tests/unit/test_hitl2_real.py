"""Real HITL2 autonomous decision contract.

@impl HIT-002
@impl ALR-002
"""

from __future__ import annotations

import asyncio

import pytest

from deerflow_deep_research.domain.context import GraphContextView, NodeAgentContext
from deerflow_deep_research.domain.lifecycle import Hitl2Decision
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.graph.nodes.hitl2 import node as hitl2_node
from deerflow_deep_research.graph.nodes.hitl2.node import build_real
from deerflow_deep_research.graph.nodes.hitl2.prompts import Hitl2Recommendation

_STATE = {
    "bundle_id": "b_" + "A" * 43,
    "generation": 0,
    "start_message_id": "msg-start",
    "accepted_submission_refs": ("ref:1", "ref:2", "ref:3"),
    "synthesis_gaps": (
        {"gap_id": "gap:1", "description": "Missing evidence X", "priority": 3, "search_required": True},
    ),
    "consumed_request_ids": (),
    "consumed_message_ids": (),
    "execution_trace": ("wave2_synthesis",),
    "phase": "wave2_synthesis",
}


def _deps():
    graph = GraphContextView(
        research_scope_id=_STATE["bundle_id"],
        workspace_root="/mnt/user-data/workspace/deep-research/r",
        uploads_root="/mnt/user-data/uploads",
        outputs_root="/mnt/user-data/outputs/deep-research/r",
    )
    return NodeBuildDependencies(
        graph_context=graph,
        agent_context=NodeAgentContext(
            research_scope_id=graph.research_scope_id,
            node_name="hitl2",
            attempt_id="g0-hitl2-a1",
            workspace_root=graph.workspace_root,
            attempt_root=f"{graph.workspace_root}/hitl2",
            policy_name="skeleton-hitl2",
        ),
        capabilities=object(),
    )


class TestRealHitl2Factory:
    def test_validated_state_routes_proceed_without_a_human_response(self) -> None:
        result = asyncio.run(build_real(_deps())(_STATE))

        assert result == {"phase": "hitl2", "execution_trace": ("hitl2",), "route": "proceed"}

    @pytest.mark.parametrize(
        "state",
        [
            _STATE | {"bundle_id": ""},
            _STATE | {"generation": -1},
            _STATE | {"execution_trace": []},
            _STATE | {"execution_trace": ("wave1",)},
        ],
    )
    def test_malformed_state_fails_closed_without_a_human_prompt(self, state: dict) -> None:
        with pytest.raises(ValueError, match="hitl2_state_invalid"):
            asyncio.run(build_real(_deps())(state))

    def test_rerun_route_marks_the_distinct_hitl2_trigger(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            hitl2_node,
            "recommend_hitl2_route",
            lambda _state: Hitl2Recommendation(route=Hitl2Decision.RERUN, reason="fixture rerun"),
        )

        result = asyncio.run(build_real(_deps())(_STATE | {"rerun_source": "none"}))

        assert result["route"] == "rerun"
        assert result["rerun_source"] == "hitl2"

    def test_checkpointed_auto_proceed_overrides_recommendation_with_an_observation_marker(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            hitl2_node,
            "recommend_hitl2_route",
            lambda _state: Hitl2Recommendation(route=Hitl2Decision.RERUN, reason="fixture rerun"),
        )

        result = asyncio.run(
            build_real(_deps())(
                _STATE
                | {
                    "non_interactive_policy": {"auto_profile": True, "auto_proceed": True},
                    "rerun_source": "none",
                }
            )
        )

        assert result == {
            "phase": "hitl2",
            "execution_trace": ("hitl2", "hitl2_auto_proceed"),
            "route": "proceed",
        }
