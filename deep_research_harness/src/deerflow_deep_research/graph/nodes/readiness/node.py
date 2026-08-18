"""Real readiness node — hard checks, critic, report plan, route determination.

Non-gated pattern (like hitl2, rerun): the node writes its own route.

@impl REA-001
@impl REA-002
@impl REA-003
@impl REA-004
@impl REA-005
@impl REA-006
@impl REA-007
"""

from __future__ import annotations

from typing import Any

from deerflow_deep_research.domain.lifecycle import LifecycleStatus, TerminalReason
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.state import PhaseStatus, node_state_update
from deerflow_deep_research.domain.workflow_outcomes import InvocationFailure, invoke_and_normalize
from deerflow_deep_research.engine.gate_kernel import exhaustion_degradation_marker

from .contracts import HardRuleFailure, ReadinessCriticOutput
from .critic import (
    admit_readiness_candidate,
    build_readiness_critic_request,
    checkpointed_critic_summary,
    conservative_readiness_output,
    parse_readiness_critic_output,
)
from .hard_rules import has_structural_failure, run_hard_rules
from .materializer import materialize_report_plan


def build_real(dependencies: NodeBuildDependencies):
    if dependencies.work_units is None:
        raise ValueError("work_unit_capability_missing")

    async def run(state: dict[str, Any]) -> dict[str, Any]:
        # 1. Hard checks
        hard_failures = run_hard_rules(state)
        must_answer = tuple(state.get("must_answer_questions") or ())
        accepted_refs = tuple(state.get("accepted_submission_refs") or ())

        # 2. Ledger-derived projection and bounded critic. A corrupted accepted
        # record is structural, while an untrusted model result is repairable.
        if hard_failures:
            critic_output = ReadinessCriticOutput(schema_version=1)
        else:
            try:
                evidence = await dependencies.work_units.store.read_synthesis_evidence(accepted_refs)
            except Exception:
                hard_failures = (*hard_failures, HardRuleFailure(code="synthesis_evidence_unavailable"))
                critic_output = ReadinessCriticOutput(schema_version=1)
            else:
                try:
                    request = build_readiness_critic_request(must_answer, evidence)
                    outcome = await invoke_and_normalize(
                        lambda: dependencies.capabilities.run_agent(
                            context=dependencies.agent_context,
                            request=request,
                        ),
                        phase="readiness",
                    )
                    if isinstance(outcome, InvocationFailure):
                        raise ValueError("readiness_critic_execution_failed")
                    candidate = parse_readiness_critic_output(outcome.result.summary)
                    critic_output = admit_readiness_candidate(
                        candidate,
                        must_answer_questions=must_answer,
                        accepted_submission_refs=accepted_refs,
                    )
                except Exception:
                    critic_output = conservative_readiness_output(must_answer)

        # 2b. Honest-gap disclosure: gate-recorded unresolved searchable gap ids
        #     joined against the canonical synthesis artifact (ids from state,
        #     bodies from the store; a missing body still discloses the id).
        unresolved_gap_ids = tuple(gap_id for gap_id in (state.get("unresolved_gaps") or ()) if isinstance(gap_id, str))
        gap_records = ()
        if unresolved_gap_ids:
            try:
                gap_records = await dependencies.work_units.store.read_synthesis_gaps()
            except Exception:
                gap_records = ()

        # 3. Materialize report plan
        report_plan = materialize_report_plan(
            critic_output,
            hard_failures,
            unresolved_gap_ids=unresolved_gap_ids,
            gap_records=gap_records,
        )
        try:
            report_plan_ref = await dependencies.work_units.store.write_readiness_report_plan(report_plan)
        except Exception:
            report_plan_ref = None
            hard_failures = (*hard_failures, HardRuleFailure(code="readiness_plan_persistence_unavailable"))

        # 4. Route determination
        blocked_count = sum(1 for pq in critic_output.per_question if pq.verdict == "blocked_repair_required")

        # Once the wave2 gate has already exhausted its repair budget and
        # degraded (gate-owned marker in ``degraded_decisions``), any further
        # ``repair_targeted`` route would be re-evaluated by the wave2 gate at
        # exhausted budget with the marker present and terminate the run
        # ``blocked`` without a report (BUG-044). In that state the only
        # non-terminal route is ``pass``, delivering the degraded-pass contract:
        # the report plan keeps disclosing the gate-recorded unresolved gaps.
        wave2_degraded = exhaustion_degradation_marker("wave2_synthesis") in (state.get("degraded_decisions") or ())

        if has_structural_failure(hard_failures) or report_plan_ref is None:
            route = "exhausted"
            terminal_status = LifecycleStatus.BLOCKED.value
            terminal_reason = TerminalReason.GATE_BLOCKED.value
            phase_status = PhaseStatus.TERMINAL.value
        elif blocked_count > 0 and not wave2_degraded:
            route = "repair_targeted"
            terminal_status = None
            terminal_reason = None
            phase_status = PhaseStatus.WAITING.value
        else:
            route = "pass"
            terminal_status = None
            terminal_reason = None
            phase_status = PhaseStatus.WAITING.value

        return {
            **node_state_update("readiness", route=route, phase_status=phase_status),
            "readiness_hard_failures": tuple(
                {"code": f.code, "detail": f.detail, "refs": f.refs} for f in hard_failures
            ),
            "readiness_critic_summary": checkpointed_critic_summary(critic_output),
            "readiness_blocked_count": blocked_count,
            **({"readiness_report_plan": report_plan_ref} if report_plan_ref is not None else {}),
            **(dict(terminal_status=terminal_status) if terminal_status else {}),
            **(dict(terminal_reason=terminal_reason) if terminal_reason else {}),
        }

    return run
