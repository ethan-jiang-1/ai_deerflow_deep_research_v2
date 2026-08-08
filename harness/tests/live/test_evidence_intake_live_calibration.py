"""Explicitly selected live judgment calibration for Wave0/Wave1 evidence intake.

@impl EVH-019
"""

from __future__ import annotations

import os

import pytest

from tests.scenarios.evidence_intake_calibration import EVIDENCE_INTAKE_CALIBRATION_CASES
from tests.scenarios.evidence_intake_live import run_evidence_intake_calibration


@pytest.mark.requires_llm
@pytest.mark.parametrize("case", EVIDENCE_INTAKE_CALIBRATION_CASES, ids=lambda case: case.case_id)
async def test_live_evidence_intake_calibration(tmp_path, case) -> None:
    report = await run_evidence_intake_calibration(case, environ=os.environ, workspace=tmp_path)

    assert report.scenario_id == case.case_id
    assert report.rubric_result is not None
