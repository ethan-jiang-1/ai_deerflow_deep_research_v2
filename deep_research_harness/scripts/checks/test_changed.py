#!/usr/bin/env python3
"""Run only tests affected by the working tree diff (local iteration speed-up).

L8 of the regression-speedup program: a local edit usually touches a handful of
test files, and the full gate (`make verify`) is now ~1 minute with `-n 4`. This
script narrows a local iteration to the changed test files (plus `--lf` for the
previously failing set) so the feedback loop is seconds, not minutes.

It is intentionally NOT part of `make verify` / CI: the deterministic gate stays
the full lane selection. This is a local convenience that never weakens evidence.

Usage (from deep_research_harness/):
    uv run python scripts/test_changed.py                 # changed tests only
    uv run python scripts/test_changed.py --last-failed   # + previously failed
    uv run python scripts/test_changed.py --base HEAD~1   # diff since another ref
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[2]
TEST_PREFIX = "tests/"


def changed_test_files(base: str) -> list[str]:
    """Return test files (relative paths) changed between base and the working tree."""
    result = subprocess.run(
        ["git", "-C", str(AGENT_ROOT), "diff", "--relative", "--name-only", base, "--", "tests/"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"git diff failed: {result.stderr or result.stdout}")
    return [
        line
        for line in result.stdout.splitlines()
        if line.startswith(TEST_PREFIX) and line.endswith(".py") and "/" in line
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="HEAD", help="git ref to diff against (default: HEAD)")
    parser.add_argument(
        "--last-failed",
        action="store_true",
        help="also re-run previously failed tests (pytest --lf)",
    )
    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="run serially (default: -n 4 like the gate)",
    )
    args = parser.parse_args()

    changed = changed_test_files(args.base)
    if not changed:
        print(f"no changed test files vs {args.base}; nothing to run.")
        return 0

    command = [sys.executable, "-m", "pytest"]
    if not args.no_parallel:
        command.append("-n 4")
    if args.last_failed:
        command.append("--lf")
    command.extend(changed)

    print("running: " + " ".join(command))
    result = subprocess.run(command, cwd=AGENT_ROOT, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
