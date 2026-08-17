#!/usr/bin/env python3
"""Write reference fast-lane performance evidence.

@impl DER-006
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

FAST_PATHS = ("tests/contract", "tests/domain", "tests/engine", "tests/unit", "tests/graph", "tests/eval")
FAST_EXPRESSION = "not (requires_llm or release_e2e or workflow)"
REQUIRED_REPORT_FIELDS = {
    "command",
    "timestamp",
    "python",
    "platform",
    "selected_test_count",
    "collection_seconds",
    "setup_seconds",
    "call_seconds",
    "total_seconds",
}


def validate_report(report: dict[str, object]) -> None:
    if set(report) != REQUIRED_REPORT_FIELDS:
        raise ValueError("benchmark_report_fields_invalid")
    if report["command"] != "make test-fast" or not isinstance(report["timestamp"], str):
        raise ValueError("benchmark_report_identity_invalid")
    if not isinstance(report["selected_test_count"], int) or report["selected_test_count"] <= 0:
        raise ValueError("benchmark_report_count_invalid")
    for field in ("collection_seconds", "setup_seconds", "call_seconds", "total_seconds"):
        if not isinstance(report[field], (int, float)) or report[field] < 0:
            raise ValueError("benchmark_report_duration_invalid")


def _run(arguments: list[str], *, env: dict[str, str] | None = None) -> tuple[subprocess.CompletedProcess[str], float]:
    started = time.monotonic()
    result = subprocess.run(arguments, text=True, capture_output=True, check=False, env=env)
    return result, time.monotonic() - started


def main() -> int:
    output = Path(".reports/deterministic-performance/fast.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-m", "pytest", *FAST_PATHS, "-m", FAST_EXPRESSION]
    collected, collection_seconds = _run([*command, "--collect-only", "-q"])
    if collected.returncode != 0:
        raise SystemExit(collected.stderr or collected.stdout)
    selected_test_count = sum("::" in line and not line.startswith("=") for line in collected.stdout.splitlines())
    with tempfile.TemporaryDirectory(prefix="deep-research-phase-") as directory:
        phase_path = Path(directory) / "phases.json"
        env = {**__import__("os").environ, "DEEP_RESEARCH_PHASE_TIMING_FILE": str(phase_path)}
        run, total_seconds = _run([*command, "-p", "tests.performance_plugin", "-q"], env=env)
        if run.returncode != 0:
            raise SystemExit(run.stderr or run.stdout)
        phases = json.loads(phase_path.read_text(encoding="utf-8"))
    report = {
        "command": "make test-fast",
        "timestamp": datetime.now(UTC).isoformat(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "selected_test_count": selected_test_count,
        "collection_seconds": collection_seconds,
        "setup_seconds": phases["setup"],
        "call_seconds": phases["call"],
        "total_seconds": total_seconds,
    }
    validate_report(report)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
