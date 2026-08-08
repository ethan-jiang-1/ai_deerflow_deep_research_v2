"""Explicitly selected live judgment calibration for intake and planning.

@impl EVH-018
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from tests.scenarios.intake_planning_calibration import CALIBRATION_CASES
from tests.scenarios.intake_planning_live import run_intake_planning_calibration
from tests.scenarios.live import LiveScenarioFailure, RubricDisposition, write_live_report

pytestmark = pytest.mark.requires_llm


@pytest.mark.parametrize("case", CALIBRATION_CASES, ids=lambda case: case.case_id)
async def test_live_intake_and_planning_calibration(tmp_path, case) -> None:
    report_dir = os.environ.get("LIVE_REPORT_DIR")
    try:
        report = await run_intake_planning_calibration(case, environ=os.environ, workspace=tmp_path)
    except LiveScenarioFailure as exc:
        if report_dir:
            write_live_report(exc.report, Path(report_dir))
        raise

    assert report.scenario_id == case.case_id
    assert report.attempt_count == 1
    assert report.retry_count == 0
    assert all(report.hard_invariants.values())
    assert report.tool_calls == 0
    assert report.wall_time_seconds >= 0
    assert report.rubric_result is not None
    assert report.rubric_result.case_id == case.case_id
    assert report.rubric_result.branch_id == case.branch_id
    assert report.rubric_result.criterion_ids == case.criterion_ids
    assert report.rubric_result.disposition in {
        RubricDisposition.PASS,
        RubricDisposition.LIMITED,
        RubricDisposition.INCONCLUSIVE,
    }
    if report_dir:
        write_live_report(report, Path(report_dir))
