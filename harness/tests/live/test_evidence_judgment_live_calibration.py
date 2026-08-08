"""Explicitly selected live judgment calibration for Wave2 and targeted evidence."""

from __future__ import annotations

import os

import pytest

from tests.scenarios.evidence_judgment_calibration import EVIDENCE_JUDGMENT_CALIBRATION_CASES
from tests.scenarios.evidence_judgment_live import run_evidence_judgment_calibration


@pytest.mark.requires_llm
@pytest.mark.parametrize("case", EVIDENCE_JUDGMENT_CALIBRATION_CASES, ids=lambda case: case.case_id)
async def test_live_evidence_judgment_calibration(tmp_path, case) -> None:
    report = await run_evidence_judgment_calibration(case, environ=os.environ, workspace=tmp_path)
    assert report.scenario_id == case.case_id
    assert report.rubric_result is not None
