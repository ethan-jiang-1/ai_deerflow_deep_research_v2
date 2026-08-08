"""Deterministic rerun planner — scope extraction, invalidation, generation, routing.

@impl REN-001
@impl REN-002
@impl REN-003
@impl REN-004
@impl REN-005
@impl REN-006
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from deerflow_deep_research.domain.lifecycle import MAX_FAKE_RERUN_GENERATIONS

from .contracts import CurrentRoundDirection, RerunPlan, RerunScope, RerunSource, RunRefinementSource

_VALID_SCOPES = frozenset({"full", "topic", "finding"})


@dataclass(frozen=True)
class FullRerunPolicy:
    """Trusted composition input for the full-rerun generation ceiling."""

    max_rerun_generations: int = MAX_FAKE_RERUN_GENERATIONS

    def __post_init__(self) -> None:
        if not isinstance(self.max_rerun_generations, int) or self.max_rerun_generations < 1:
            raise ValueError("max_rerun_generations_invalid")

    def allows_next_full_rerun(self, current_generation: int) -> bool:
        return has_full_rerun_capacity(current_generation=current_generation, policy=self)


def has_full_rerun_capacity(*, current_generation: int, policy: FullRerunPolicy) -> bool:
    """Return whether a current generation may start one more full rerun."""

    if not isinstance(current_generation, int) or current_generation < 0:
        raise ValueError("generation_invalid")
    if not isinstance(policy, FullRerunPolicy):
        raise TypeError("full_rerun_policy_required")
    return current_generation < policy.max_rerun_generations


@dataclass(frozen=True)
class FullRerunUpdate:
    """Pure typed rerun output shared by the node and checkpoint preparation.

    ``values`` is a read-only copy so a caller cannot mutate the compiler result
    before handing its exact update to LangGraph's rerun writer.
    """

    source: RerunSource
    plan: RerunPlan
    values: Mapping[str, Any] = field(default_factory=dict)
    is_replay: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "values", MappingProxyType(dict(self.values)))

    def to_state_update(self) -> dict[str, Any]:
        """Return a fresh mapping suitable for the production rerun writer."""

        return dict(self.values)


def run_refinement_source_from_state(state: Mapping[str, Any]) -> RunRefinementSource:
    """Read the controller-owned graph projection for a prepared direction round."""

    if not isinstance(state, Mapping):
        raise TypeError("rerun_state_required")
    raw_direction = state.get("current_refinement")
    raw_token = state.get("refinement_round_token")
    if raw_direction is None or raw_token is None:
        raise ValueError("run_refinement_projection_missing")
    try:
        direction = (
            raw_direction
            if isinstance(raw_direction, CurrentRoundDirection)
            else CurrentRoundDirection.model_validate(raw_direction)
        )
        return RunRefinementSource(direction=direction, round_token=raw_token)
    except (TypeError, ValueError) as exc:
        raise ValueError("run_refinement_projection_invalid") from exc


def compile_full_rerun_update(
    state: Mapping[str, Any],
    *,
    source: RerunSource | str,
    policy: FullRerunPolicy,
    run_refinement: RunRefinementSource | None = None,
) -> FullRerunUpdate:
    """Compile one full-rerun update without checkpoint or graph side effects.

    A Run refinement is assignment input, not a HITL2 decision. It therefore forces
    the existing full-scope plan and never constructs a synthetic HITL2 payload.
    """

    if not isinstance(state, Mapping):
        raise TypeError("rerun_state_required")
    if not isinstance(policy, FullRerunPolicy):
        raise TypeError("full_rerun_policy_required")
    try:
        parsed_source = RerunSource(source)
    except ValueError as exc:
        raise ValueError("rerun_source_invalid") from exc
    if parsed_source is RerunSource.NONE:
        raise ValueError("rerun_source_none")

    current_generation = _state_generation(state)
    if parsed_source is RerunSource.RUN_REFINEMENT:
        if not isinstance(run_refinement, RunRefinementSource):
            raise ValueError("run_refinement_source_required")
        target_generation = run_refinement.direction.generation
        if target_generation == current_generation:
            return FullRerunUpdate(
                source=parsed_source,
                plan=RerunPlan(
                    generation=current_generation,
                    parent_generation=max(current_generation - 1, 0),
                    scope=RerunScope(scope="full"),
                    route="topic_planning",
                ),
                is_replay=True,
            )
        if target_generation != current_generation + 1:
            raise ValueError("run_refinement_generation_mismatch")
        scope = RerunScope(scope="full")
    else:
        if run_refinement is not None:
            raise ValueError("hitl2_rerun_source_mismatch")
        scope = build_rerun_scope(dict(state))
        target_generation = current_generation + 1

    route = determine_rerun_route(
        scope,
        generation=current_generation,
        max_rerun_generations=policy.max_rerun_generations,
    )
    plan = RerunPlan(
        generation=target_generation,
        parent_generation=current_generation,
        scope=scope,
        route=route,
    )
    values = {
        **_rerun_node_state_update(route),
        **apply_invalidation(scope),
        "generation": target_generation,
        "parent_generation": current_generation,
        **materialize_rerun_workspecs(dict(state), scope),
        **reset_gate_state_for_scope(dict(state), scope),
        "rerun_scope": scope.scope,
        "rerun_reason": scope.reason,
        "rerun_source": RerunSource.NONE.value,
        "phase_status": "waiting",
        "terminal_status": None,
        "terminal_reason": None,
        "latest_incident": None,
    }
    if parsed_source is RerunSource.RUN_REFINEMENT and route != "exhausted":
        assert run_refinement is not None
        values["current_refinement"] = run_refinement.direction.model_dump(mode="json")
        values["refinement_round_token"] = run_refinement.round_token
    elif parsed_source is RerunSource.HITL2:
        values["current_refinement"] = None
        values["refinement_round_token"] = None
    if route == "exhausted":
        from deerflow_deep_research.domain.lifecycle import LifecycleStatus, TerminalReason

        values.update(
            terminal_status=LifecycleStatus.BLOCKED.value,
            terminal_reason=TerminalReason.RERUN_EXHAUSTED.value,
        )
    return FullRerunUpdate(source=parsed_source, plan=plan, values=values)


def _state_generation(state: Mapping[str, Any]) -> int:
    value = state.get("generation", 0)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError("generation_invalid")
    return value


def _rerun_node_state_update(route: str) -> dict[str, Any]:
    """Keep the pure compiler independent from the graph module's node wrapper."""

    return {
        "phase": "rerun",
        "execution_trace": ("rerun",),
        "route": route,
    }


def build_rerun_scope(state: dict[str, Any]) -> RerunScope:
    """Extract typed RerunScope from hitl2_rerun_payload in checkpoint state.

    Pure parsing; generation is not involved. Defaults to FULL when payload is
    absent, None, or contains invalid data.
    """
    payload = state.get("hitl2_rerun_payload")
    if not isinstance(payload, dict):
        return RerunScope(scope="full", reason="")

    scope_key = payload.get("scope")
    if not isinstance(scope_key, str) or scope_key not in _VALID_SCOPES:
        raise ValueError(f"invalid_rerun_scope: {scope_key!r}")

    reason = payload.get("reason", "")
    if not isinstance(reason, str):
        reason = ""

    target_topic_ids = _parse_str_tuple(payload.get("target_topic_ids"))
    target_finding_ids = _parse_str_tuple(payload.get("target_finding_ids"))

    if scope_key == "topic":
        # Validate target_topic_ids against topic_registry
        topic_registry = state.get("topic_registry") or ()
        registry_ids = _extract_topic_ids(topic_registry)
        for tid in target_topic_ids:
            if tid not in registry_ids:
                # Invalid ID → fall back to FULL
                return RerunScope(scope="full", reason=reason)
        retain_topic_ids = tuple(tid for tid in registry_ids if tid not in target_topic_ids)
        return RerunScope(
            scope="topic",
            reason=reason,
            target_topic_ids=target_topic_ids,
            target_finding_ids=(),
            retain_topic_ids=retain_topic_ids,
        )

    if scope_key == "finding":
        return RerunScope(
            scope="finding",
            reason=reason,
            target_topic_ids=(),
            target_finding_ids=target_finding_ids,
            retain_topic_ids=_parse_str_tuple(payload.get("retain_topic_ids")),
        )

    # scope_key == "full"
    return RerunScope(
        scope="full",
        reason=reason,
        target_topic_ids=(),
        target_finding_ids=(),
        retain_topic_ids=(),
    )


def apply_invalidation(_scope: RerunScope) -> dict[str, Any]:
    """Clear derived projections and consume the HITL2 payload.

    Returns a dict of checkpoint field updates. Does not touch sandbox files.
    """
    return {
        "synthesis_ref": None,
        "decision_brief_ref": None,
        "report_refs": (),
        "repair_counts": {},
        "hitl2_rerun_payload": None,
    }


def apply_generation_increment(state: dict[str, Any]) -> dict[str, Any]:
    """Increment generation monotonically and record parent."""
    current_gen = int(state.get("generation", 0))
    return {
        "generation": current_gen + 1,
        "parent_generation": current_gen,
    }


def determine_rerun_route(
    scope: RerunScope,
    *,
    generation: int,
    max_rerun_generations: int,
) -> str:
    """Determine the graph back edge from the current generation's capacity."""
    if generation >= max_rerun_generations:
        return "exhausted"

    if scope.scope == "full":
        return "topic_planning"
    if scope.scope == "topic":
        return "wave0"
    # finding: stale sources → wave0 (conservative default)
    return "wave0"


def reset_gate_state_for_scope(
    state: dict[str, Any],
    scope: RerunScope,
) -> dict[str, Any]:
    """Reset gate_attempts and repair_budget for phases affected by the rerun scope."""
    if scope.scope == "full":
        # Full rerun: reset all phases
        return {
            "gate_attempts_by_phase": {},
            "repair_budget_by_phase": {},
        }
    # For topic/finding scoped reruns, reset all phases too —
    # the downstream planners filter by active_topic_filter, and the
    # gates need to evaluate the new work from scratch.
    return {
        "gate_attempts_by_phase": {},
        "repair_budget_by_phase": {},
    }


def materialize_rerun_workspecs(
    state: dict[str, Any],
    scope: RerunScope,
) -> dict[str, Any]:
    """Create scoped WorkSpecs via work-unit controller for TOPIC/FINDING.

    FULL scope is a no-op — topic_planning handles WorkSpec creation.
    Returns a dict with pending_work_ids and active_topic_filter.
    """
    if scope.scope == "full":
        return {
            "pending_work_ids": (),
            "active_topic_filter": (),
        }

    if scope.scope == "topic":
        return {
            "pending_work_ids": (),  # wave0 planner creates WorkSpecs via topic_filter
            "active_topic_filter": scope.target_topic_ids,
        }

    # finding scope
    return {
        "pending_work_ids": (),
        "active_topic_filter": scope.retain_topic_ids,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_str_tuple(value: Any) -> tuple[str, ...]:
    """Coerce a list/tuple of strings to a tuple of strings."""
    if isinstance(value, (list, tuple)):
        return tuple(str(v) for v in value if isinstance(v, str))
    return ()


def _extract_topic_ids(
    topic_registry: tuple[dict[str, Any], ...] | list[dict[str, Any]],
) -> frozenset[str]:
    """Extract all topic_id values from the topic registry."""
    ids: set[str] = set()
    for entry in topic_registry or ():
        if isinstance(entry, dict):
            tid = entry.get("topic_id")
            if isinstance(tid, str):
                ids.add(tid)
    return frozenset(ids)
