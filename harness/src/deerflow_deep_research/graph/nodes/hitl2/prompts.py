"""HITL2 deterministic decision view and autonomous policy.

@impl HIT-001
@impl ALR-001
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from deerflow_deep_research.domain.lifecycle import Hitl2Decision


@dataclass(frozen=True)
class Hitl2Recommendation:
    """A bounded policy result; graph nodes retain route authority."""

    route: Hitl2Decision
    reason: str


def build_hitl2_brief(state: dict[str, Any]) -> dict[str, Any]:
    """Build a structured decision brief from accepted findings and gaps.

    Reads accepted submission refs and synthesis gaps from checkpoint state.
    Returns a dict with confirmed count, pending gap count, and available
    actions for bounded diagnostics and legacy inspection. Current HITL2 routing is
    autonomous, so this helper does not supply a user prompt or route authority.
    """
    accepted = state.get("accepted_submission_refs") or ()
    gaps = state.get("synthesis_gaps") or ()
    return {
        "confirmed_count": len(accepted),
        "pending_gaps": len(gaps),
        "available_actions": ["proceed", "revise_view", "repair", "rerun", "stop"],
    }


def recommend_hitl2_route(state: dict[str, Any]) -> Hitl2Recommendation:
    """Select the normal graph continuation from an already validated state.

    The node is called only after graph routing has accepted Wave2's pass verdict.
    It therefore does not reinterpret gaps or quality gates. It merely records the
    bounded, explainable normal continuation rather than asking a user to choose an
    internal route.
    """

    if not isinstance(state, dict):
        raise ValueError("hitl2_state_invalid")
    if not isinstance(state.get("bundle_id"), str) or not state["bundle_id"]:
        raise ValueError("hitl2_state_invalid")
    if not isinstance(state.get("generation", 0), int) or state.get("generation", 0) < 0:
        raise ValueError("hitl2_state_invalid")
    trace = state.get("execution_trace", ())
    if not isinstance(trace, tuple) or not trace or trace[-1] != "wave2_synthesis":
        raise ValueError("hitl2_state_invalid")
    return Hitl2Recommendation(
        route=Hitl2Decision.PROCEED,
        reason="validated_quality_path_complete",
    )
