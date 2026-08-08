"""Real rerun node — scoped invalidation, generation increment, back-edge routing.

@impl REN-001
@impl REN-002
@impl REN-003
@impl REN-004
@impl REN-005
@impl REN-006
@impl REN-007
"""

from __future__ import annotations

from typing import Any

from deerflow_deep_research.domain.node_spec import NodeBuildDependencies

from .contracts import RerunSource
from .planner import (
    FullRerunPolicy,
    compile_full_rerun_update,
    run_refinement_source_from_state,
)


def build_real(dependencies: NodeBuildDependencies):
    configured_policy = dependencies.full_rerun_policy
    if configured_policy is None:
        policy = FullRerunPolicy(max_rerun_generations=dependencies.max_rerun_generations)
    elif isinstance(configured_policy, FullRerunPolicy):
        policy = configured_policy
        if policy.max_rerun_generations != dependencies.max_rerun_generations:
            raise ValueError("rerun_policy_generation_mismatch")
    else:
        raise TypeError("full_rerun_policy_required")

    async def run(state: dict[str, Any]) -> dict[str, Any]:
        raw_source = state.get("rerun_source")
        if raw_source == RerunSource.NONE.value:
            return {}
        source = RerunSource.HITL2 if raw_source is None else RerunSource(raw_source)
        run_refinement = run_refinement_source_from_state(state) if source is RerunSource.RUN_REFINEMENT else None
        return compile_full_rerun_update(
            state,
            source=source,
            run_refinement=run_refinement,
            policy=policy,
        ).to_state_update()

    return run
