from __future__ import annotations

from enum import StrEnum
from typing import Literal

from deerflow_deep_research.domain.lifecycle import CurrentRoundDirection, FrozenContract, RunRefinementSource


class RerunSource(StrEnum):
    """Trusted source of a single rerun invocation."""

    HITL2 = "hitl2"
    RUN_REFINEMENT = "run_refinement"
    NONE = "none"


class RerunScope(FrozenContract):
    """Parsed rerun scope from HITL2 decision payload.

    @impl REN-001
    """

    scope: Literal["full", "topic", "finding"]
    reason: str = ""
    target_topic_ids: tuple[str, ...] = ()
    target_finding_ids: tuple[str, ...] = ()
    retain_topic_ids: tuple[str, ...] = ()


class RerunPlan(FrozenContract):
    """Final assembled output of the rerun node: scope + computed outputs.

    Generation validation (>= 0) is enforced by ResearchGraphState; RerunPlan
    is an internal assembly artifact created inside the rerun node where
    generation is always the result of a monotonic increment.

    @impl REN-001
    """

    generation: int
    parent_generation: int
    scope: RerunScope
    route: Literal["topic_planning", "wave0", "wave1", "exhausted"]


CONTRACTS = (RerunScope, RerunPlan)

__all__ = [
    "CONTRACTS",
    "CurrentRoundDirection",
    "RerunPlan",
    "RerunScope",
    "RerunSource",
    "RunRefinementSource",
]
