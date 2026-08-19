"""Real targeted_evidence node — critic dispatch + gap worker fan-out.

@impl EVC-001, EVC-002, EVC-003
@impl TEL-001, TEL-002
@impl TEL-008
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from deerflow_deep_research.domain.critics import ClaimVerifierResult, SourceDiagnosticResult
from deerflow_deep_research.domain.lifecycle import make_node_visit_id
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.run_observation import RunEventCategory
from deerflow_deep_research.domain.state import node_state_update
from deerflow_deep_research.domain.work_units import WORK_UNIT_GATE_VIEW_KEY, WorkUnitGateView

from .materializer import materialize_claim_verifier, materialize_source_diagnostic
from .subgraph import dispatch_critic, materialize_gap_intents, run_gap_workers


def _empty_drained_gate_view() -> WorkUnitGateView:
    """Canonical empty view for a gap-less visit; nothing is planned or reconciled."""

    return WorkUnitGateView(
        drained=True,
        planned_work_ids=(),
        terminal_attempt_by_work_id={},
        accepted_record_by_work_id={},
        failure_summaries=(),
    )


def build_real(dependencies: NodeBuildDependencies):
    async def run(state: dict[str, Any]) -> dict[str, Any]:
        work_items = state.get("critic_work_items") or ()
        gap_ids = state.get("unresolved_gaps") or ()
        gap_intents = materialize_gap_intents(gap_ids)
        workspace_root = dependencies.graph_context.workspace_root
        node_attempt_id = make_node_visit_id(state, "targeted_evidence")
        bundle_id = state["bundle_id"]

        if gap_intents:
            component_result = await run_gap_workers(state, gap_intents, dependencies)
            base = {
                **node_state_update("targeted_evidence"),
                **component_result.parent_update,
                WORK_UNIT_GATE_VIEW_KEY: component_result.gate_view,
            }
        else:
            # The shared component's plan bound requires 1..32 intents, so a gap-less
            # visit returns the canonical empty drained view directly.
            base = {
                **node_state_update("targeted_evidence"),
                WORK_UNIT_GATE_VIEW_KEY: _empty_drained_gate_view(),
            }
            try:
                if dependencies.event_recorder is not None:
                    await dependencies.event_recorder.record(
                        category=RunEventCategory.NODE,
                        phase="targeted_evidence",
                        attempt_id=dependencies.agent_context.attempt_id,
                        targeted_evidence_reason="drained_no_op",
                        targeted_gap_count=0,
                    )
            except Exception:
                pass

        if work_items:
            results = await dispatch_critic(
                work_items,
                dependencies.capabilities,
                dependencies.agent_context,
                node_attempt_id,
                bundle_id,
                workspace_root,
            )
            for entry in results:
                result = entry["result"]
                if isinstance(result, SourceDiagnosticResult):
                    allowed = set()
                    for item in work_items:
                        if item.get("type") == "source_diagnostic":
                            allowed.update(item.get("source_refs", ()))
                    materialize_source_diagnostic(
                        result, node_attempt_id, Path(workspace_root), allowed_source_ids=allowed
                    )
                elif isinstance(result, ClaimVerifierResult):
                    allowed = set()
                    for item in work_items:
                        if item.get("type") == "claim_verifier":
                            allowed.update(item.get("evidence_refs", ()))
                    materialize_claim_verifier(
                        result, node_attempt_id, Path(workspace_root), allowed_source_ids=allowed
                    )

        return {**base, "route": "next"}

    return run
