"""Deterministic contracts for the Wave2/targeted judgment corpus.

@impl EVH-020
@impl EVH-021
@impl WSN-006
@impl TEL-006
"""
# ruff: noqa: E501

from __future__ import annotations

from dataclasses import replace

import pytest

from tests.scenarios.canaries import LIVE_CANARIES, validate_live_canary_deadlines
from tests.scenarios.contracts import ScenarioCase
from tests.scenarios.evidence_intake_calibration import EVIDENCE_INTAKE_CALIBRATION_CASES
from tests.scenarios.evidence_judgment_calibration import (
    EVIDENCE_JUDGMENT_CALIBRATION_CASES,
    build_evidence_judgment_request,
    evidence_judgment_case_requires_web,
    validate_evidence_judgment_calibration_cases,
)
from tests.scenarios.evidence_judgment_live import (
    evidence_judgment_live_scenario,
    run_evidence_judgment_calibration,
)
from tests.scenarios.intake_planning_calibration import CALIBRATION_CASES, CalibrationRisk
from tests.scenarios.live import LivePreflightError


def test_evidence_judgment_corpus_has_two_labeled_cases_per_branch_with_declared_bounds() -> None:
    validate_evidence_judgment_calibration_cases()
    assert len(EVIDENCE_JUDGMENT_CALIBRATION_CASES) == 15
    assert {case.branch_id for case in EVIDENCE_JUDGMENT_CALIBRATION_CASES} == {
        "wave2-synthesis/synthesis",
        "wave2-synthesis/repair",
        "targeted-evidence/worker",
        "targeted-evidence/repair",
        "targeted-evidence/source-diagnostic",
        "targeted-evidence/claim-verifier",
        "readiness/critic",
    }
    for branch in {case.branch_id for case in EVIDENCE_JUDGMENT_CALIBRATION_CASES}:
        assert {case.risk for case in EVIDENCE_JUDGMENT_CALIBRATION_CASES if case.branch_id == branch} == {
            CalibrationRisk.NORMAL,
            CalibrationRisk.HIGHEST_RISK,
        }
    readiness = [case for case in EVIDENCE_JUDGMENT_CALIBRATION_CASES if case.branch_id == "readiness/critic"]
    assert {constraint for case in readiness for constraint in case.expected_candidate_constraints} >= {
        "ready_substantive",
        "ready_insufficient_judgment",
        "blocked_repair_required",
    }


def test_evidence_judgment_corpus_is_a_separate_live_only_collection() -> None:
    ids = {case.case_id for case in EVIDENCE_JUDGMENT_CALIBRATION_CASES}
    assert ids.isdisjoint({case.case_id for case in CALIBRATION_CASES})
    assert ids.isdisjoint({case.case_id for case in EVIDENCE_INTAKE_CALIBRATION_CASES})
    assert ids.isdisjoint({case.scenario_id for case in LIVE_CANARIES})
    assert all(not isinstance(case, ScenarioCase) for case in EVIDENCE_JUDGMENT_CALIBRATION_CASES)
    assert validate_live_canary_deadlines(LIVE_CANARIES, job_timeout_seconds=1200)["case_count"] == 6


def test_evidence_judgment_request_composition_preserves_tool_posture() -> None:
    for case in EVIDENCE_JUDGMENT_CALIBRATION_CASES:
        request = build_evidence_judgment_request(case)
        assert request.tools_enabled is evidence_judgment_case_requires_web(case)
        assert request.minimum_tool_calls == (1 if evidence_judgment_case_requires_web(case) else 0)
        assert request.tool_call_limit == (1 if evidence_judgment_case_requires_web(case) else None)
        assert request.capability_ref is not None


def test_evidence_judgment_live_scenarios_select_direct_branch_bridge() -> None:
    for case in EVIDENCE_JUDGMENT_CALIBRATION_CASES:
        scenario = evidence_judgment_live_scenario(case)
        requires_web = evidence_judgment_case_requires_web(case)
        assert scenario.preconditions["require_web"] is requires_web
        assert scenario.live_requirements == (("model", "web_search") if requires_web else ("model",))
        assert scenario.entrypoint == (
            "direct-model-and-web-node-agent-bridge" if requires_web else "direct-model-node-agent-bridge"
        )


@pytest.mark.asyncio
async def test_evidence_judgment_live_runner_preflights_before_invocation(tmp_path) -> None:
    worker = next(case for case in EVIDENCE_JUDGMENT_CALIBRATION_CASES if case.branch_id == "targeted-evidence/worker")
    repair = next(case for case in EVIDENCE_JUDGMENT_CALIBRATION_CASES if case.branch_id == "wave2-synthesis/repair")
    with pytest.raises(LivePreflightError, match="live_web_credentials_missing"):
        await run_evidence_judgment_calibration(worker, environ={"OPENAI_API_KEY": "test"}, workspace=tmp_path)
    with pytest.raises(LivePreflightError, match="live_model_credentials_missing"):
        await run_evidence_judgment_calibration(repair, environ={}, workspace=tmp_path)


def test_evidence_judgment_corpus_fails_closed_on_denominator_or_bound_drift() -> None:
    with pytest.raises(ValueError, match="evidence_judgment_calibration_case_identity_invalid"):
        validate_evidence_judgment_calibration_cases(EVIDENCE_JUDGMENT_CALIBRATION_CASES[:-1])
    with pytest.raises(ValueError, match="evidence_judgment_calibration_bounds_invalid"):
        validate_evidence_judgment_calibration_cases(
            (
                replace(EVIDENCE_JUDGMENT_CALIBRATION_CASES[0], max_tool_calls=1),
                *EVIDENCE_JUDGMENT_CALIBRATION_CASES[1:],
            )
        )
