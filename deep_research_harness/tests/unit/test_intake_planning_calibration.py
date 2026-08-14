"""Deterministic governance checks for the separate intake/planning calibration corpus.

@impl EVH-018
"""

from __future__ import annotations

import asyncio
from dataclasses import replace

import pytest

from scripts.check_test_assets import collect_deterministic_selectors, collect_pytest_selectors
from tests.assets.selection import LIVE_EXPRESSION, LIVE_PATHS
from tests.scenarios.canaries import LIVE_CANARIES, validate_live_canary_deadlines
from tests.scenarios.contracts import ScenarioCase
from tests.scenarios.intake_planning_calibration import (
    CALIBRATION_CASES,
    CalibrationRisk,
    build_calibration_request,
    validate_calibration_cases,
)
from tests.scenarios.intake_planning_live import calibration_live_scenario, run_intake_planning_calibration
from tests.scenarios.live import LiveAttempt, LiveOutcome, LivePreflightError, LiveRubricResult, RubricDisposition
from tests.scenarios.replays import FIRST_WAVE_CASES


def test_calibration_corpus_has_two_labeled_cases_per_intake_and_planning_branch() -> None:
    validate_calibration_cases()

    assert len(CALIBRATION_CASES) == 12
    assert {case.branch_id for case in CALIBRATION_CASES} == {
        "hitl1/brief",
        "hitl1/brief-repair",
        "hitl1/semantic-intake",
        "hitl1/semantic-intake-repair",
        "topic-planning/plan",
        "topic-planning/plan-repair",
    }
    for branch_id in {case.branch_id for case in CALIBRATION_CASES}:
        assert {case.risk for case in CALIBRATION_CASES if case.branch_id == branch_id} == {
            CalibrationRisk.NORMAL,
            CalibrationRisk.HIGHEST_RISK,
        }
    assert all(case.permitted_degradation == ("limited", "inconclusive") for case in CALIBRATION_CASES)
    assert all(case.max_attempts == case.max_model_calls == 1 for case in CALIBRATION_CASES)
    assert all(case.max_tool_calls == 0 for case in CALIBRATION_CASES)


def test_calibration_corpus_stays_outside_canaries_and_the_reusable_scenario_registry() -> None:
    calibration_ids = {case.case_id for case in CALIBRATION_CASES}

    assert [scenario.scenario_id for scenario in LIVE_CANARIES] == [
        "live-start-to-hitl1",
        "live-hitl1-to-topic-planning",
        "live-one-topic-wave0",
        "live-one-topic-wave1",
        "live-wave2-synthesis",
        "live-one-gap-targeted-evidence",
    ]
    assert validate_live_canary_deadlines(LIVE_CANARIES, job_timeout_seconds=1200) == {
        "case_count": 6,
        "declared_seconds": 900,
        "job_timeout_seconds": 1200,
        "margin_seconds": 300,
    }
    assert [case.case_id for case in FIRST_WAVE_CASES] == [
        "quick-factual",
        "claim-verification",
        "insufficient-evidence",
        "prompt-injection",
        "malformed-output",
        "tool-unavailable-timeout",
        "budget-exhaustion",
        "partial-worker-success",
        "bundle-lifecycle-control",
        "sandbox-filesystem-failure",
    ]
    assert calibration_ids.isdisjoint({scenario.scenario_id for scenario in LIVE_CANARIES})
    assert calibration_ids.isdisjoint({case.case_id for case in FIRST_WAVE_CASES})
    assert not any(isinstance(case, ScenarioCase) for case in CALIBRATION_CASES)


def test_calibration_cases_compose_real_zero_tool_branch_requests() -> None:
    requests = [build_calibration_request(case) for case in CALIBRATION_CASES]

    assert all(request.tools_enabled is False for request in requests)
    assert {request.capability_ref.capability_id for request in requests} == {
        "hitl1-profile-brief",
        "hitl1-profile-brief-repair",
        "hitl1-semantic-intake",
        "hitl1-semantic-intake-repair",
        "topic-planning-profile-decomposition",
        "topic-planning-plan-repair",
    }


def test_calibration_live_scenarios_retain_branch_bounds_and_hard_invariants() -> None:
    for case in CALIBRATION_CASES:
        scenario = calibration_live_scenario(case)

        assert scenario.scenario_id == case.case_id
        assert scenario.preconditions["branch_id"] == case.branch_id
        assert scenario.preconditions["max_attempts"] == case.max_attempts
        assert scenario.preconditions["max_model_calls"] == case.max_model_calls
        assert scenario.preconditions["max_tool_calls"] == case.max_tool_calls
        assert scenario.preconditions["max_total_tokens"] == case.max_total_tokens
        assert scenario.preconditions["timeout_seconds"] == case.timeout_seconds
        assert scenario.live_requirements == ("model",)
        assert scenario.hard_invariants == ("zero_tools", "branch_bound", "candidate_boundary")
        assert scenario.metrics == ("accepted-authority-count",)


def test_default_deterministic_selection_excludes_the_live_calibration_collection() -> None:
    calibration_selectors = {
        "tests/live/test_intake_planning_live_calibration.py::test_live_intake_and_planning_calibration["
        f"{case.case_id}]"
        for case in CALIBRATION_CASES
    }

    assert calibration_selectors.isdisjoint(collect_deterministic_selectors())
    assert calibration_selectors <= collect_pytest_selectors(
        paths=LIVE_PATHS,
        expression=LIVE_EXPRESSION,
        label="intake-planning-live",
    )


async def test_selected_calibration_requires_strict_model_credential_preflight(tmp_path) -> None:
    with pytest.raises(LivePreflightError, match="live_model_credentials_missing"):
        await run_intake_planning_calibration(CALIBRATION_CASES[0], environ={}, workspace=tmp_path)


async def test_selected_calibration_enforces_its_declared_outer_timeout(monkeypatch, tmp_path) -> None:
    from tests.scenarios import intake_planning_live

    async def slow_execute(*_args, **_kwargs) -> LiveAttempt:
        await asyncio.sleep(0.02)
        return LiveAttempt(
            outcome=LiveOutcome(route="candidate-evaluated"),
            error_code=None,
            model_id="test/model",
            tool_ids=(),
            input_tokens=None,
            output_tokens=None,
            cost_usd=None,
            tool_calls=0,
            wall_time_seconds=0.02,
            diagnostics="bounded test execution",
        )

    monkeypatch.setattr(intake_planning_live, "_execute_case", slow_execute)
    bounded_case = replace(CALIBRATION_CASES[0], timeout_seconds=0.001)

    with pytest.raises(TimeoutError):
        await run_intake_planning_calibration(
            bounded_case,
            environ={"OPENAI_API_KEY": "test-key"},
            workspace=tmp_path,
        )


async def test_selected_calibration_reports_its_typed_rubric_with_unavailable_authority_metric(
    monkeypatch, tmp_path
) -> None:
    from tests.scenarios import intake_planning_live

    case = CALIBRATION_CASES[0]

    async def successful_execute(*_args, **_kwargs) -> LiveAttempt:
        return LiveAttempt(
            outcome=LiveOutcome(route="candidate-evaluated"),
            error_code=None,
            model_id="test/model",
            tool_ids=(),
            input_tokens=5,
            output_tokens=3,
            cost_usd=None,
            tool_calls=0,
            wall_time_seconds=0.01,
            diagnostics="bounded test execution",
            rubric_result=LiveRubricResult(
                case_id=case.case_id,
                branch_id=case.branch_id,
                criterion_ids=case.criterion_ids,
                disposition=RubricDisposition.PASS,
                rationale="Every declared criterion was assessable and satisfied.",
            ),
        )

    monkeypatch.setattr(intake_planning_live, "_execute_case", successful_execute)

    report = await run_intake_planning_calibration(
        case,
        environ={"OPENAI_API_KEY": "test-key"},
        workspace=tmp_path,
    )

    assert report.quality_metrics["accepted-authority-count"]["status"] == "insufficient_authority"
    assert report.rubric_result is not None
    assert report.rubric_result.case_id == case.case_id
    assert report.rubric_result.criterion_ids == case.criterion_ids
