"""Production gate definitions for real research phases.

Fixture sequencing belongs to the separate fixture package.  These definitions operate
only on production state, accepted work, and node-provided gate views.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from deerflow_deep_research.domain.failure_codes import FailureCode
from deerflow_deep_research.domain.gate import Failure, GateDefinition, GateRule, PhaseVerdict
from deerflow_deep_research.domain.publication import FINAL_DELIVERY_GATE_VIEW_KEY
from deerflow_deep_research.domain.synthesis import WAVE2_GATE_PREVIEW_KEY, Wave2GatePreview
from deerflow_deep_research.domain.wave1 import WAVE1_GATE_REVIEW_KEY, Wave1GateReview
from deerflow_deep_research.domain.work_units import WORK_UNIT_GATE_VIEW_KEY, WorkUnitGateView
from deerflow_deep_research.engine.work_units.kernel import WorkUnitCompletionRule


def _work_unit_completion_rule() -> GateRule:
    instance = WorkUnitCompletionRule()
    return GateRule(name=instance.name, evaluate=instance.evaluate, failure_code=instance.failure_code)


def _wave2_searchable_gap_rule() -> GateRule:
    def evaluate(state: Mapping[str, Any]) -> Failure | None:
        preview = state.get(WAVE2_GATE_PREVIEW_KEY)
        if not isinstance(preview, Wave2GatePreview):
            raise ValueError("wave2_gate_preview_missing")
        if not preview.searchable_gap_ids:
            return None
        return Failure(
            code=FailureCode.MISSING_EVIDENCE,
            rule_name="wave2_searchable_gaps",
            description=f"{len(preview.searchable_gap_ids)} searchable synthesis gap(s) remain",
            ref=preview.searchable_gap_ids[0],
        )

    return GateRule(
        name="wave2_searchable_gaps",
        evaluate=evaluate,
        failure_code=FailureCode.MISSING_EVIDENCE,
    )


def _wave1_structural_review(state: Mapping[str, Any]) -> Wave1GateReview | None:
    view = state.get(WORK_UNIT_GATE_VIEW_KEY)
    if not isinstance(view, WorkUnitGateView):
        return None
    complete = (
        view.drained
        and not view.failure_summaries
        and set(view.accepted_record_by_work_id) == set(view.planned_work_ids)
    )
    if not complete:
        return None
    review = state.get(WAVE1_GATE_REVIEW_KEY)
    if not isinstance(review, Wave1GateReview):
        raise ValueError("wave1_gate_review_missing")
    review.validate_gate_view(view)
    return review


def _wave1_new_source_floor_rule() -> GateRule:
    def evaluate(state: Mapping[str, Any]) -> Failure | None:
        review = _wave1_structural_review(state)
        if review is None:
            return None
        for row in review.rows:
            if row.distinct_new_url_count < 2:
                return Failure(
                    code=FailureCode.INCOMPLETE_TOPIC_COVERAGE,
                    rule_name="wave1_new_source_floor",
                    description="accepted work has fewer than two distinct new source URLs",
                    ref=row.work_id,
                )
        return None

    return GateRule(
        name="wave1_new_source_floor",
        evaluate=evaluate,
        failure_code=FailureCode.INCOMPLETE_TOPIC_COVERAGE,
    )


def _wave1_review_presence_rule() -> GateRule:
    def evaluate(state: Mapping[str, Any]) -> Failure | None:
        review = _wave1_structural_review(state)
        if review is None:
            return None
        for row in review.rows:
            if not row.source_diagnostic_present or not row.claim_verifier_present:
                return Failure(
                    code=FailureCode.MISSING_EVIDENCE,
                    rule_name="wave1_review_presence",
                    description="accepted work is missing a bound Wave1 critic review",
                    ref=row.work_id,
                )
        return None

    return GateRule(
        name="wave1_review_presence",
        evaluate=evaluate,
        failure_code=FailureCode.MISSING_EVIDENCE,
    )


def _wave_route_map() -> dict[PhaseVerdict, str]:
    return {
        PhaseVerdict.PASS: "pass",
        PhaseVerdict.REPAIR: "repair",
        PhaseVerdict.BLOCKED: "exhausted",
    }


def _synthesis_route_map() -> dict[PhaseVerdict, str]:
    return {
        PhaseVerdict.PASS: "pass",
        PhaseVerdict.REPAIR: "evidence_needed",
        PhaseVerdict.BLOCKED: "exhausted",
    }


def _final_delivery_route_resolver(verdict: PhaseVerdict, failures: tuple[Failure, ...]) -> str:
    if verdict is PhaseVerdict.PASS:
        return "pass"
    if verdict is PhaseVerdict.BLOCKED:
        return "exhausted"
    for failure in failures:
        if failure.code is FailureCode.EVIDENCE_INSUFFICIENT:
            return "evidence_blocked"
        if failure.code is FailureCode.WORK_FAILED:
            return "repair"
    return "repair"


def _final_delivery_real_rule() -> GateRule:
    def evaluate(state: Mapping[str, Any]) -> Failure | None:
        view = state.get(FINAL_DELIVERY_GATE_VIEW_KEY)
        if view is None:
            return Failure(
                code=FailureCode.WORK_FAILED,
                rule_name="final_delivery_fresh_view",
                description="final delivery did not provide a fresh gate view",
            )
        failure_code = getattr(view, "failure_code", None)
        if isinstance(failure_code, FailureCode):
            return Failure(
                code=failure_code,
                rule_name="final_delivery_fresh_view",
                description="final delivery attempt did not produce verified artifacts",
            )
        if not bool(getattr(view, "accepted_evidence_present", False)):
            return Failure(
                code=FailureCode.EVIDENCE_INSUFFICIENT,
                rule_name="final_delivery_accepted_evidence",
                description="no accepted evidence is available for final delivery",
            )
        published_refs = getattr(view, "published_refs", None)
        if not isinstance(published_refs, tuple) or len(published_refs) != 2:
            return Failure(
                code=FailureCode.WORK_FAILED,
                rule_name="final_delivery_verified_artifacts",
                description="final delivery has no verified report and citation-map pair",
            )
        return None

    return GateRule(
        name="final_delivery_fresh_view",
        evaluate=evaluate,
        failure_code=FailureCode.WORK_FAILED,
    )


def build_wave0_real_gate_def() -> GateDefinition:
    return GateDefinition(
        phase="wave0",
        rules=(_work_unit_completion_rule(),),
        default_budget=5,
        route_map=_wave_route_map(),
    )


def build_wave1_real_gate_def() -> GateDefinition:
    return GateDefinition(
        phase="wave1",
        rules=(
            _work_unit_completion_rule(),
            _wave1_new_source_floor_rule(),
            _wave1_review_presence_rule(),
        ),
        default_budget=5,
        route_map=_wave_route_map(),
    )


def _wave2_minimal_pair_budget_resolver(state: Mapping[str, Any]) -> int | None:
    """Two evidence rounds under the minimal profile-intent pair, else default.

    Reads the HITL-owned profile intent fields already written into graph state
    (``profile_state_fields``); the gate only READS state, so no writer-role
    change is involved.
    """
    if state.get("cost_tolerance") == "minimal" and state.get("time_budget") == "very_quick":
        return 2
    return None


def build_wave2_real_gate_def() -> GateDefinition:
    return GateDefinition(
        phase="wave2_synthesis",
        rules=(_wave2_searchable_gap_rule(),),
        default_budget=1,
        route_map=_synthesis_route_map(),
        budget_resolver=_wave2_minimal_pair_budget_resolver,
    )


def build_final_delivery_real_gate_def() -> GateDefinition:
    return GateDefinition(
        phase="final_delivery",
        rules=(_final_delivery_real_rule(),),
        default_budget=3,
        route_resolver=_final_delivery_route_resolver,
    )


__all__ = [
    "build_final_delivery_real_gate_def",
    "build_wave0_real_gate_def",
    "build_wave1_real_gate_def",
    "build_wave2_real_gate_def",
]
