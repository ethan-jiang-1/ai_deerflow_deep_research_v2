"""Red tests for HITL2 deterministic brief builder.

@impl HIT-001
"""

from __future__ import annotations

import pytest

from deerflow_deep_research.domain.lifecycle import Hitl2Decision
from deerflow_deep_research.graph.nodes.hitl2.prompts import build_hitl2_brief, recommend_hitl2_route


class TestBuildHitl2Brief:
    def test_returns_dict_with_expected_keys(self) -> None:
        state = {
            "accepted_submission_refs": ("ref:1", "ref:2"),
            "synthesis_gaps": (
                {"gap_id": "gap:1", "description": "Missing X", "priority": 3, "search_required": True},
            ),
        }
        brief = build_hitl2_brief(state)
        assert isinstance(brief, dict)
        assert "confirmed_count" in brief
        assert "pending_gaps" in brief
        assert "available_actions" in brief

    def test_empty_state_produces_honest_brief(self) -> None:
        state = {}
        brief = build_hitl2_brief(state)
        assert brief["confirmed_count"] == 0
        assert brief["pending_gaps"] == 0

    def test_brief_includes_available_actions(self) -> None:
        state = {"accepted_submission_refs": ("ref:1",)}
        brief = build_hitl2_brief(state)
        actions = brief["available_actions"]
        assert "proceed" in actions
        assert "stop" in actions

    def test_brief_counts_gaps_correctly(self) -> None:
        state = {
            "accepted_submission_refs": ("a", "b", "c"),
            "synthesis_gaps": (
                {"gap_id": "g1", "description": "x", "priority": 1, "search_required": True},
                {"gap_id": "g2", "description": "y", "priority": 5, "search_required": False},
                {"gap_id": "g3", "description": "z", "priority": 3, "search_required": True},
            ),
        }
        brief = build_hitl2_brief(state)
        assert brief["confirmed_count"] == 3
        assert brief["pending_gaps"] == 3


class TestHitl2Policy:
    """@impl ALR-001"""

    def test_validated_state_recommends_graph_owned_continuation(self) -> None:
        recommendation = recommend_hitl2_route(
            {"bundle_id": "r_test", "generation": 0, "execution_trace": ("wave2_synthesis",)}
        )

        assert recommendation.route is Hitl2Decision.PROCEED
        assert recommendation.reason == "validated_quality_path_complete"

    @pytest.mark.parametrize("predecessor", [(), ("wave1",), ("readiness",)])
    def test_non_wave2_predecessor_cannot_select_a_route(self, predecessor: tuple[str, ...]) -> None:
        with pytest.raises(ValueError, match="hitl2_state_invalid"):
            recommend_hitl2_route({"bundle_id": "r_test", "generation": 0, "execution_trace": predecessor})

    @pytest.mark.parametrize(
        "state",
        [
            {},
            {"bundle_id": "r_test", "generation": "0", "execution_trace": ("wave2_synthesis",)},
            {"bundle_id": "r_test", "generation": 0, "execution_trace": []},
        ],
    )
    def test_malformed_state_cannot_select_a_route(self, state: dict[object, object]) -> None:
        with pytest.raises(ValueError, match="hitl2_state_invalid"):
            recommend_hitl2_route(state)  # type: ignore[arg-type]
