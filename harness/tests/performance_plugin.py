"""Opt-in phase timing for the reference fast-lane benchmark.

@impl DER-006
"""

from __future__ import annotations

import json
import os
from pathlib import Path

_PHASES = {"setup": 0.0, "call": 0.0}


def pytest_runtest_logreport(report: object) -> None:
    when = getattr(report, "when", None)
    if when in _PHASES:
        _PHASES[when] += float(getattr(report, "duration", 0.0))


def pytest_sessionfinish(session: object, exitstatus: int) -> None:
    output = os.environ.get("DEEP_RESEARCH_PHASE_TIMING_FILE")
    if output:
        Path(output).write_text(json.dumps(_PHASES, separators=(",", ":")), encoding="utf-8")
