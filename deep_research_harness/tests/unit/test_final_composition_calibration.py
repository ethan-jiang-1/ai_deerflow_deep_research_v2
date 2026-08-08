"""Deterministic contracts for the final-composition live-only corpus.

@impl EVH-022
@impl FID-001
@impl FID-003
@impl NAC-009
@impl NOA-013
"""

from __future__ import annotations

import ast
import json
from dataclasses import replace
from pathlib import Path

import pytest

from deerflow_deep_research.graph.nodes.final_delivery.composer import MAX_FINAL_DELIVERY_EVIDENCE_BYTES
from tests.scenarios.canaries import LIVE_CANARIES
from tests.scenarios.contracts import ScenarioCase
from tests.scenarios.evidence_intake_calibration import EVIDENCE_INTAKE_CALIBRATION_CASES
from tests.scenarios.evidence_judgment_calibration import EVIDENCE_JUDGMENT_CALIBRATION_CASES
from tests.scenarios.final_composition_calibration import (
    FINAL_COMPOSITION_CALIBRATION_CASES,
    FinalCompositionDisposition,
    assess_final_composition_candidate,
    build_final_composition_request,
    validate_final_composition_calibration_cases,
)
from tests.scenarios.final_composition_live import (
    final_composition_live_scenario,
    run_final_composition_calibration,
)
from tests.scenarios.intake_planning_calibration import CALIBRATION_CASES, CalibrationRisk
from tests.scenarios.live import (
    LiveAttempt,
    LiveOutcome,
    LivePreflightError,
    LiveRubricResult,
    LiveScenarioRunner,
    RubricDisposition,
)


def _summary(case, *, conclusion_order=None, uncertainty_order=None) -> str:
    return json.dumps(
        {
            "schema_version": 1,
            "conclusion_order": conclusion_order or case.preferred_conclusion_order,
            "uncertainty_order": uncertainty_order or case.preferred_uncertainty_order,
        }
    )


def test_final_composition_corpus_has_normal_and_highest_risk_cases_with_declared_bounds() -> None:
    validate_final_composition_calibration_cases()

    assert len(FINAL_COMPOSITION_CALIBRATION_CASES) == 2
    assert {case.risk for case in FINAL_COMPOSITION_CALIBRATION_CASES} == {
        CalibrationRisk.NORMAL,
        CalibrationRisk.HIGHEST_RISK,
    }
    for case in FINAL_COMPOSITION_CALIBRATION_CASES:
        assert case.branch_id == "final-delivery/composer"
        assert case.plan_projection == (
            "conclusions:id,question,conclusion_text,backing_submission_refs",
            "uncertainties:id,question,limitation",
        )
        assert case.evidence_projection == ("submission_ref", "phase", "result_contract", "content", "truncated")
        assert case.max_evidence_projection_bytes == MAX_FINAL_DELIVERY_EVIDENCE_BYTES
        assert case.preferred_layout_label
        assert case.preservation_requirements == (
            "exact-conclusion-text",
            "exact-uncertainty-text",
            "exact-citation-binding",
        )
        assert case.permitted_degradation == (
            FinalCompositionDisposition.LIMITED,
            FinalCompositionDisposition.INCONCLUSIVE,
        )
        assert case.assessable_candidate_dispositions == (
            FinalCompositionDisposition.PASS,
            FinalCompositionDisposition.LIMITED,
        )
        assert (case.max_attempts, case.max_model_calls, case.max_tool_calls) == (1, 1, 0)


def test_final_composition_corpus_is_a_separate_live_only_collection() -> None:
    ids = {case.case_id for case in FINAL_COMPOSITION_CALIBRATION_CASES}
    assert ids.isdisjoint({case.case_id for case in CALIBRATION_CASES})
    assert ids.isdisjoint({case.case_id for case in EVIDENCE_INTAKE_CALIBRATION_CASES})
    assert ids.isdisjoint({case.case_id for case in EVIDENCE_JUDGMENT_CALIBRATION_CASES})
    assert ids.isdisjoint({case.scenario_id for case in LIVE_CANARIES})
    assert all(not isinstance(case, ScenarioCase) for case in FINAL_COMPOSITION_CALIBRATION_CASES)


@pytest.mark.parametrize("case", FINAL_COMPOSITION_CALIBRATION_CASES, ids=lambda case: case.case_id)
def test_final_composition_request_and_assessment_use_production_bounded_surfaces(case) -> None:
    request = build_final_composition_request(case)

    assert request.tools_enabled is False
    assert request.minimum_tool_calls == 0
    assert request.tool_call_limit is None
    assert request.capability_ref is not None
    assert request.capability_ref.capability_id == "final-delivery-composer"
    assert "<untrusted-source-data>" in request.objective
    assert "</untrusted-source-data>" in request.objective
    assert sum(len(item.content.encode("utf-8")) for item in case.evidence) <= case.max_evidence_projection_bytes

    assessment = assess_final_composition_candidate(case, _summary(case))

    assert assessment.disposition is FinalCompositionDisposition.PASS
    report = assessment.report.decode("utf-8")
    for conclusion in case.plan.writable_conclusions:
        assert report.count(conclusion.conclusion_text) == 1
    for uncertainty in case.plan.mandatory_uncertainties:
        assert report.count(uncertainty.limitation) == 1
    expected_claims = {
        f"conclusion:{index}": {"backing_refs": list(conclusion.backing_claim_ids)}
        for index, conclusion in enumerate(case.plan.writable_conclusions)
    }
    assert json.loads(assessment.citation_map) == {"schema_version": 1, "claims": expected_claims}


def test_final_composition_nonpreferred_admitted_layout_is_limited() -> None:
    case = FINAL_COMPOSITION_CALIBRATION_CASES[0]
    conclusion_order = tuple(reversed(case.preferred_conclusion_order))
    uncertainty_order = tuple(reversed(case.preferred_uncertainty_order))

    assessment = assess_final_composition_candidate(
        case,
        _summary(case, conclusion_order=conclusion_order, uncertainty_order=uncertainty_order),
    )

    assert assessment.disposition is FinalCompositionDisposition.LIMITED


def test_final_composition_candidate_rejects_plan_violation() -> None:
    case = FINAL_COMPOSITION_CALIBRATION_CASES[1]
    with pytest.raises(ValueError, match="final_layout_conclusions_invalid"):
        assess_final_composition_candidate(
            case,
            _summary(case, conclusion_order=case.preferred_conclusion_order[:-1]),
        )


def test_final_composition_live_scenario_is_direct_bridge_without_authority_calls() -> None:
    for case in FINAL_COMPOSITION_CALIBRATION_CASES:
        scenario = final_composition_live_scenario(case)
        assert scenario.entrypoint == "direct-model-final-composer-bridge"
        assert scenario.live_requirements == ("model",)
        assert scenario.preconditions["authority_scope"] == "candidate-only"
        assert scenario.preconditions["preferred_layout_label"] == case.preferred_layout_label
        assert scenario.metrics == ("accepted-authority-count",)

    from tests.scenarios import final_composition_live

    tree = ast.parse(Path(final_composition_live.__file__).read_text(encoding="utf-8"))
    calls = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))
    }
    assert calls.isdisjoint(
        {
            "publish_final",
            "write_readiness_report_plan",
            "read_final_artifacts",
            "build_real",
            "ainvoke",
            "compile",
        }
    )


async def test_final_composition_live_report_accepts_typed_disposition() -> None:
    case = FINAL_COMPOSITION_CALIBRATION_CASES[0]
    scenario = final_composition_live_scenario(case)

    async def execute(_scenario):
        return LiveAttempt(
            outcome=LiveOutcome(route="candidate-evaluated"),
            error_code=None,
            model_id="model/final-composition",
            tool_ids=(),
            input_tokens=None,
            output_tokens=None,
            cost_usd=None,
            tool_calls=0,
            wall_time_seconds=0.1,
            diagnostics="bounded final-composition candidate evaluated",
            rubric_result=LiveRubricResult(
                case_id=case.case_id,
                branch_id=case.branch_id,
                criterion_ids=case.criterion_ids,
                disposition=RubricDisposition.PASS,
                rationale="The candidate matched the declared preferred layout.",
            ),
        )

    report = await LiveScenarioRunner(executor=execute, max_attempts=1).run(scenario)

    assert report.rubric_result is not None
    assert report.rubric_result.case_id == case.case_id
    assert report.rubric_result.disposition is RubricDisposition.PASS


async def test_final_composition_live_runner_preflights_before_invocation(tmp_path) -> None:
    with pytest.raises(LivePreflightError, match="live_model_credentials_missing"):
        await run_final_composition_calibration(
            FINAL_COMPOSITION_CALIBRATION_CASES[0],
            environ={},
            workspace=tmp_path,
        )


def test_final_composition_corpus_fails_closed_on_denominator_bound_and_layout_drift() -> None:
    with pytest.raises(ValueError, match="final_composition_calibration_case_identity_invalid"):
        validate_final_composition_calibration_cases(FINAL_COMPOSITION_CALIBRATION_CASES[:-1])
    with pytest.raises(ValueError, match="final_composition_calibration_bounds_invalid"):
        validate_final_composition_calibration_cases(
            (replace(FINAL_COMPOSITION_CALIBRATION_CASES[0], max_model_calls=2), FINAL_COMPOSITION_CALIBRATION_CASES[1])
        )
    with pytest.raises(ValueError, match="final_composition_calibration_preferred_layout_invalid"):
        validate_final_composition_calibration_cases(
            (
                replace(
                    FINAL_COMPOSITION_CALIBRATION_CASES[0],
                    preferred_conclusion_order=("conclusion:0", "conclusion:0", "conclusion:2"),
                ),
                FINAL_COMPOSITION_CALIBRATION_CASES[1],
            )
        )
