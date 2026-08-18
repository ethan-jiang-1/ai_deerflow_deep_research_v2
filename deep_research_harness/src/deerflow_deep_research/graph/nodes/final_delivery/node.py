"""Real bounded final-delivery composition and publication handoff.

@impl FID-001
@impl FID-002
@impl FID-003
@impl FID-004
@impl FID-005
"""

from __future__ import annotations

import json
from typing import Any

from deerflow_deep_research.domain.failure_codes import FailureCode
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.publication import (
    FINAL_DELIVERY_GATE_VIEW_KEY,
    FinalDeliveryGateView,
    FinalDeliveryLayoutCandidate,
)
from deerflow_deep_research.domain.readiness import ReadinessReportPlan
from deerflow_deep_research.domain.run_observation import RunEventCategory
from deerflow_deep_research.domain.state import node_state_update
from deerflow_deep_research.domain.synthesis import SynthesisEvidence
from deerflow_deep_research.domain.workflow_outcomes import InvocationFailure, invoke_and_normalize

from .composer import (
    admit_layout_candidate,
    build_final_delivery_request,
    parse_layout_candidate,
    plan_order_layout,
    render_final_artifacts,
)

_LAYOUT_LITERAL_CODES = frozenset(
    {
        "final_layout_empty",
        "final_layout_json_invalid",
        "final_layout_not_object",
        "final_layout_schema_unsupported",
        "final_layout_conclusions_invalid",
        "final_layout_uncertainties_invalid",
    }
)
_LAYOUT_SHAPE_INVALID = "final_layout_shape_invalid"


def _canonical_layout_code(error: ValueError) -> str:
    """Collapse parser/admission detail to the closed Journal vocabulary."""

    code = str(error)
    return code if code in _LAYOUT_LITERAL_CODES else _LAYOUT_SHAPE_INVALID


def _failure_view(*, evidence_present: bool, code: FailureCode) -> FinalDeliveryGateView:
    return FinalDeliveryGateView(accepted_evidence_present=evidence_present, failure_code=code)


def _validate_final_artifacts(report: bytes, citation_map: bytes) -> None:
    if not report.startswith(b"# Deep Research Report\n"):
        raise ValueError("final_report_shape_invalid")
    payload = json.loads(citation_map)
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != 1
        or not isinstance(payload.get("claims"), dict)
    ):
        raise ValueError("final_citation_map_shape_invalid")


async def _record_layout_validation_fact(dependencies: NodeBuildDependencies, *, code: str) -> None:
    """Retain the closed canonical code of a rejected composer delivery.

    Observation only (BUG-055): persistence failure must not perturb the visit,
    mirroring the topic-planning validation-fact owner.
    """

    if dependencies.event_recorder is None:
        return
    try:
        await dependencies.event_recorder.record(
            category=RunEventCategory.VALIDATION,
            phase="final_delivery",
            validation_stage="initial",
            validation_codes=(code,),
        )
    except Exception:
        return


def _is_degenerate(plan: ReadinessReportPlan) -> bool:
    return len(plan.writable_conclusions) <= 1 and len(plan.mandatory_uncertainties) <= 1


async def _admitted_or_degraded_layout(
    dependencies: NodeBuildDependencies,
    *,
    plan: ReadinessReportPlan,
    evidence: tuple[SynthesisEvidence, ...],
) -> FinalDeliveryLayoutCandidate:
    """Acquire the visit's layout candidate.

    Degenerate plans construct the unique order deterministically (BUG-053).
    Non-degenerate visits ask the composer once; an invocation failure or an
    inadmissible delivery degrades to the deterministic plan-order layout rather
    than failing the visit (BUG-055) — ordering is advisory and must not cost
    the run its delivery. Only a candidate that reached the parser/admission
    boundary leaves a validation fact; an invocation failure keeps only the
    existing invocation fact.
    """

    if _is_degenerate(plan):
        return plan_order_layout(plan)
    request = build_final_delivery_request(plan, evidence)
    outcome = await invoke_and_normalize(
        lambda: dependencies.capabilities.run_agent(context=dependencies.agent_context, request=request),
        phase="final_delivery",
    )
    if isinstance(outcome, InvocationFailure):
        return plan_order_layout(plan)
    try:
        return admit_layout_candidate(parse_layout_candidate(outcome.result.summary), plan)
    except ValueError as exc:
        await _record_layout_validation_fact(dependencies, code=_canonical_layout_code(exc))
        return plan_order_layout(plan)


def build_real(dependencies: NodeBuildDependencies):
    if dependencies.final_delivery_bundle is None:
        raise ValueError("final_delivery_bundle_capability_missing")
    if dependencies.publication_bundle is None:
        raise ValueError("publication_bundle_capability_missing")

    async def run(state: dict[str, Any]) -> dict[str, Any]:
        accepted_refs = tuple(state.get("accepted_submission_refs") or ())
        evidence_present = bool(accepted_refs)
        base = node_state_update("final_delivery")
        plan_ref = state.get("readiness_report_plan")
        if plan_ref is None:
            return {
                **base,
                FINAL_DELIVERY_GATE_VIEW_KEY: _failure_view(
                    evidence_present=evidence_present, code=FailureCode.WORK_FAILED
                ),
            }
        try:
            plan_bytes = await dependencies.final_delivery_bundle.read_readiness_report_plan(plan_ref)
            plan = ReadinessReportPlan.model_validate_json(plan_bytes)
        except Exception:
            return {
                **base,
                FINAL_DELIVERY_GATE_VIEW_KEY: _failure_view(
                    evidence_present=evidence_present, code=FailureCode.WORK_FAILED
                ),
            }
        if not evidence_present:
            return {
                **base,
                FINAL_DELIVERY_GATE_VIEW_KEY: _failure_view(
                    evidence_present=False, code=FailureCode.EVIDENCE_INSUFFICIENT
                ),
            }
        try:
            evidence = await dependencies.final_delivery_bundle.read_synthesis_evidence(accepted_refs)
            layout = await _admitted_or_degraded_layout(dependencies, plan=plan, evidence=evidence)
            report, citation_map = render_final_artifacts(plan, layout)
            refs = await dependencies.publication_bundle.publish_final(report, citation_map)
            if not isinstance(refs, tuple) or len(refs) != 2:
                raise ValueError("final_publication_refs_invalid")
            typed_refs = (refs[0], refs[1])
            read_report, read_citation_map = await dependencies.final_delivery_bundle.read_final_artifacts(typed_refs)
            _validate_final_artifacts(read_report, read_citation_map)
        except Exception:
            return {
                **base,
                FINAL_DELIVERY_GATE_VIEW_KEY: _failure_view(evidence_present=True, code=FailureCode.WORK_FAILED),
            }
        return {
            **base,
            "report_refs": typed_refs,
            FINAL_DELIVERY_GATE_VIEW_KEY: FinalDeliveryGateView(
                published_refs=typed_refs,
                accepted_evidence_present=True,
            ),
        }

    return run
