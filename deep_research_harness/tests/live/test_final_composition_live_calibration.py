"""Explicitly selected live judgment calibration for final composition.

@impl EVH-022
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from tests.scenarios.final_composition_calibration import FINAL_COMPOSITION_CALIBRATION_CASES
from tests.scenarios.final_composition_live import run_final_composition_calibration
from tests.scenarios.live import LiveScenarioFailure, RubricDisposition, write_live_report

pytestmark = pytest.mark.requires_llm


@pytest.mark.parametrize("case", FINAL_COMPOSITION_CALIBRATION_CASES, ids=lambda case: case.case_id)
async def test_live_final_composition_calibration(tmp_path, case) -> None:
    report_dir = os.environ.get("LIVE_REPORT_DIR")
    try:
        report = await run_final_composition_calibration(case, environ=os.environ, workspace=tmp_path)
    except LiveScenarioFailure as exc:
        if report_dir:
            write_live_report(exc.report, Path(report_dir))
        raise

    assert report.scenario_id == case.case_id
    assert report.attempt_count == 1
    assert report.retry_count == 0
    assert all(report.hard_invariants.values())
    assert report.tool_calls == 0
    assert report.tool_ids == ()
    assert report.quality_metrics["accepted-authority-count"]["status"] == "unavailable"
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
