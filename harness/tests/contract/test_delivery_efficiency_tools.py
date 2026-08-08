"""Delivery-efficiency tool contracts.

@impl DER-004
@impl DER-005
@impl DER-006
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from scripts.benchmark_fast import validate_report
from scripts.check_test_durations import DurationWaiver, slow_selectors


def test_duration_policy_rejects_unwaived_and_expired_slow_test(tmp_path: Path) -> None:
    report = tmp_path / "fast.xml"
    report.write_text(
        '<testsuite><testcase classname="tests.fast" name="test_slow" time="5.1"/></testsuite>',
        encoding="utf-8",
    )
    assert slow_selectors(report, now=date(2026, 7, 23)) == ["tests.fast::test_slow=5.100s"]
    expired = DurationWaiver("tests.fast::test_slow", "known", "owner", date(2026, 7, 22))
    assert slow_selectors(report, now=date(2026, 7, 23), waivers=(expired,)) == ["tests.fast::test_slow=5.100s"]
    valid = DurationWaiver("tests.fast::test_slow", "known", "owner", date(2026, 7, 24))
    assert slow_selectors(report, now=date(2026, 7, 23), waivers=(valid,)) == []
    missing_owner = DurationWaiver("tests.fast::test_slow", "known", "", date(2026, 7, 24))
    assert slow_selectors(report, now=date(2026, 7, 23), waivers=(missing_owner,)) == ["tests.fast::test_slow=5.100s"]


def test_reference_benchmark_report_rejects_missing_or_invalid_phase_data() -> None:
    report = {
        "command": "make test-fast",
        "timestamp": "2026-07-23T00:00:00+00:00",
        "python": "3.13.5",
        "platform": "test",
        "selected_test_count": 1,
        "collection_seconds": 1.0,
        "setup_seconds": 1.0,
        "call_seconds": 1.0,
        "total_seconds": 3.0,
    }
    validate_report(report)
    report.pop("call_seconds")
    with pytest.raises(ValueError, match="benchmark_report_fields_invalid"):
        validate_report(report)
