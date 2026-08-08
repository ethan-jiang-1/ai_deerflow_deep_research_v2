"""Deterministic contracts for the separate evidence-intake calibration corpus.

@impl EVH-019
@impl WAN-008
@impl WON-008
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from deerflow_deep_research.agents.capabilities import load_node_agent_capability
from scripts.check_test_assets import collect_deterministic_selectors, collect_pytest_selectors
from tests.assets.selection import LIVE_EXPRESSION, LIVE_PATHS
from tests.scenarios.canaries import LIVE_CANARIES, validate_live_canary_deadlines
from tests.scenarios.contracts import ScenarioCase
from tests.scenarios.evidence_intake_calibration import (
    EVIDENCE_INTAKE_CALIBRATION_CASES,
    build_evidence_intake_request,
    evidence_intake_case_requires_web,
    validate_evidence_intake_calibration_cases,
)
from tests.scenarios.evidence_intake_live import evidence_intake_live_scenario, run_evidence_intake_calibration
from tests.scenarios.intake_planning_calibration import CALIBRATION_CASES, CalibrationRisk
from tests.scenarios.live import LiveAttempt, LiveOutcome, LivePreflightError, LiveRubricResult, RubricDisposition
from tests.scenarios.replays import FIRST_WAVE_CASES


def test_evidence_intake_corpus_has_two_labeled_cases_per_branch_with_declared_bounds() -> None:
    validate_evidence_intake_calibration_cases()

    assert len(EVIDENCE_INTAKE_CALIBRATION_CASES) == 12
    assert {case.branch_id for case in EVIDENCE_INTAKE_CALIBRATION_CASES} == {
        "wave0/worker",
        "wave0/repair",
        "wave1/worker",
        "wave1/repair",
        "wave1/source-diagnostic",
        "wave1/claim-verifier",
    }
    for branch_id in {case.branch_id for case in EVIDENCE_INTAKE_CALIBRATION_CASES}:
        assert {case.risk for case in EVIDENCE_INTAKE_CALIBRATION_CASES if case.branch_id == branch_id} == {
            CalibrationRisk.NORMAL,
            CalibrationRisk.HIGHEST_RISK,
        }
    assert all(case.permitted_degradation == ("limited", "inconclusive") for case in EVIDENCE_INTAKE_CALIBRATION_CASES)
    assert all(case.max_attempts == 1 and case.criterion_ids for case in EVIDENCE_INTAKE_CALIBRATION_CASES)


def test_evidence_intake_corpus_is_disjoint_from_other_calibration_and_scenario_collections() -> None:
    evidence_ids = {case.case_id for case in EVIDENCE_INTAKE_CALIBRATION_CASES}

    assert evidence_ids.isdisjoint({case.case_id for case in CALIBRATION_CASES})
    assert evidence_ids.isdisjoint({scenario.scenario_id for scenario in LIVE_CANARIES})
    assert evidence_ids.isdisjoint({case.case_id for case in FIRST_WAVE_CASES})
    assert all(not isinstance(case, ScenarioCase) for case in EVIDENCE_INTAKE_CALIBRATION_CASES)
    assert validate_live_canary_deadlines(LIVE_CANARIES, job_timeout_seconds=1200)["case_count"] == 6


def test_evidence_intake_request_composition_preserves_branch_tool_posture() -> None:
    for case in EVIDENCE_INTAKE_CALIBRATION_CASES:
        request = build_evidence_intake_request(case)
        requires_web = evidence_intake_case_requires_web(case)

        assert request.tools_enabled is requires_web
        assert request.minimum_tool_calls == (1 if requires_web else 0)
        expected_tool_limit = 3 if case.branch_id == "wave0/worker" else 1 if case.branch_id == "wave1/worker" else None
        assert request.tool_call_limit == expected_tool_limit
        if case.branch_id in {"wave0/worker", "wave0/repair", "wave1/worker", "wave1/repair"}:
            assert request.capability_ref is not None
            capability = load_node_agent_capability(request.capability_ref)
            assert "ledger" in capability.policy.lower()
            assert "ledger" not in request.objective.lower()
            if case.branch_id == "wave1/repair" and case.risk is CalibrationRisk.HIGHEST_RISK:
                assert "baseline URL cannot supply a repaired source" in capability.policy
                assert "baseline URL cannot supply a repaired source" not in request.objective
        else:
            assert "ledger" in request.objective.lower()


def test_evidence_intake_case_validator_fails_closed_on_denominator_or_bound_drift() -> None:
    with pytest.raises(ValueError, match="evidence_intake_calibration_case_identity_invalid"):
        validate_evidence_intake_calibration_cases(EVIDENCE_INTAKE_CALIBRATION_CASES[:-1])
    with pytest.raises(ValueError, match="evidence_intake_calibration_bounds_invalid"):
        validate_evidence_intake_calibration_cases(
            (replace(EVIDENCE_INTAKE_CALIBRATION_CASES[0], max_tool_calls=0), *EVIDENCE_INTAKE_CALIBRATION_CASES[1:])
        )


def test_evidence_intake_live_scenarios_select_the_declared_real_dependency_seam() -> None:
    for case in EVIDENCE_INTAKE_CALIBRATION_CASES:
        scenario = evidence_intake_live_scenario(case)
        requires_web = evidence_intake_case_requires_web(case)

        assert scenario.preconditions["require_web"] is requires_web
        assert scenario.live_requirements == (("model", "web_search") if requires_web else ("model",))
        assert scenario.entrypoint == (
            "direct-model-and-web-node-agent-bridge" if requires_web else "direct-model-node-agent-bridge"
        )


@pytest.mark.asyncio
async def test_selected_evidence_intake_runner_uses_strict_branch_preflight(monkeypatch, tmp_path) -> None:
    worker = next(case for case in EVIDENCE_INTAKE_CALIBRATION_CASES if case.branch_id == "wave0/worker")
    repair = next(case for case in EVIDENCE_INTAKE_CALIBRATION_CASES if case.branch_id == "wave0/repair")

    with pytest.raises(LivePreflightError, match="live_web_credentials_missing"):
        await run_evidence_intake_calibration(worker, environ={"OPENAI_API_KEY": "test"}, workspace=tmp_path)
    with pytest.raises(LivePreflightError, match="live_model_credentials_missing"):
        await run_evidence_intake_calibration(repair, environ={}, workspace=tmp_path)

    async def fake_execute(case, scenario, *, environ, workspace):
        del environ, workspace
        return LiveAttempt(
            outcome=LiveOutcome(
                route="candidate-evaluated",
                values={"identity": {"thread_id": "thread", "run_id": "run", "bundle_id": "research"}},
            ),
            error_code=None,
            model_id="openai/test",
            tool_ids=("tavily/web_search",) if scenario.preconditions["require_web"] else (),
            input_tokens=None,
            output_tokens=None,
            cost_usd=None,
            tool_calls=1 if scenario.preconditions["require_web"] else 0,
            wall_time_seconds=0.1,
            diagnostics="test selected branch",
            rubric_result=LiveRubricResult(
                case_id=case.case_id,
                branch_id=case.branch_id,
                criterion_ids=case.criterion_ids,
                disposition=RubricDisposition.PASS,
                rationale="The test fixture proves report selection only.",
            ),
        )

    monkeypatch.setattr("tests.scenarios.evidence_intake_live._execute_case", fake_execute)
    report = await run_evidence_intake_calibration(
        worker,
        environ={"OPENAI_API_KEY": "test", "TAVILY_API_KEY": "test"},
        workspace=tmp_path,
    )
    assert report.rubric_result is not None
    assert report.rubric_result.case_id == worker.case_id


def test_default_deterministic_selection_excludes_both_live_calibration_collections() -> None:
    evidence_selectors = {
        (f"tests/live/test_evidence_intake_live_calibration.py::test_live_evidence_intake_calibration[{case.case_id}]")
        for case in EVIDENCE_INTAKE_CALIBRATION_CASES
    }

    assert evidence_selectors.isdisjoint(collect_deterministic_selectors())
    live_selectors = collect_pytest_selectors(paths=LIVE_PATHS, expression=LIVE_EXPRESSION, label="live evidence")
    assert evidence_selectors <= live_selectors
