"""Canonical launcher entry contract.

@impl RED-013
"""

from __future__ import annotations

import subprocess
from pathlib import Path

LAUNCHER = Path(__file__).resolve().parents[2] / "run" / "tui-workflow-debugger.sh"


def test_launcher_is_executable_and_help_lists_make_equivalents() -> None:
    import os

    assert os.access(LAUNCHER, os.X_OK)
    result = subprocess.run([str(LAUNCHER), "--help"], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0
    assert "demo-tui" in result.stdout
    assert "--attach" in result.stdout
    assert "--replay" in result.stdout


def test_launcher_runs_from_any_cwd(tmp_path: Path) -> None:
    result = subprocess.run(
        [str(LAUNCHER), "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=tmp_path,
    )
    assert result.returncode == 0


def test_launcher_unknown_flag_fails_without_starting(tmp_path: Path) -> None:
    result = subprocess.run(
        [str(LAUNCHER), "--not-a-flag"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=tmp_path,
    )
    assert result.returncode != 0
    assert "unrecognized" in (result.stderr + result.stdout).lower()


def test_launcher_forwards_fixture_intent(tmp_path: Path) -> None:
    """--fixture forwards to the TUI entry; short timeout kills the TUI itself."""
    result = subprocess.run(
        [str(LAUNCHER), "--fixture", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0


def test_launcher_contains_no_workspace_scan_or_lifecycle_logic() -> None:
    text = LAUNCHER.read_text(encoding="utf-8")
    for forbidden in ("scopes", "run-summary", "events.jsonl", "graph.sqlite", "discover()"):
        assert forbidden not in text


_PROBE_CHILD = """
import asyncio, sys
sys.path.insert(0, "scripts")
import demo_tui

async def main():
    app = demo_tui.DeepResearchDemoTUI(mode="fixture")
    async with app.run_test(size=(100, 40)) as pilot:
        for _ in range(60):
            await pilot.pause()
            update = getattr(app, "last_update", None)
            name = type(update).__name__
            if name in ("Fault", "Ready"):
                print("RESULT:", name)
                failure = getattr(update, "failure", None)
                if failure is not None:
                    print("MESSAGE:", failure.message)
                return
            await asyncio.sleep(0.1)
    print("RESULT: TIMEOUT")

asyncio.run(main())
"""


def test_fixture_workbench_reaches_ready_without_caller_pythonpath() -> None:
    """The fixture entry is self-sufficient: no caller-side path contract.

    Regression for the operator-reported startup fault: the launcher's child
    process used to die on a hidden `src_fixtures` import contract and render
    the generic presentation fault instead of the workbench.
    """
    import os
    import sys

    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    result = subprocess.run(
        [sys.executable, "-c", _PROBE_CHILD],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=Path(__file__).resolve().parents[2],
        env=env,
    )
    assert "RESULT: Ready" in result.stdout, (
        f"fixture entry did not reach Ready without caller PYTHONPATH: "
        f"{result.stdout.strip()[-400:] or result.stderr.strip()[-400:]}"
    )


def test_debugger_journey_harness_passes_through_the_real_entry() -> None:
    """The runbook-030 ladder must pass through the real script entry chain.

    Regression for three operator-reported failures that import-time tests
    could not see: the launcher's missing fixture path, the C4b methods bound
    after the ``__main__`` guard, and the session router re-opening a live
    session as ``busy``. The harness executes the actual script as
    ``__main__`` with PYTHONPATH stripped and asserts every ladder step.
    """
    import os
    import sys

    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    result = subprocess.run(
        [sys.executable, "scripts/tui_journey_probe.py"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=Path(__file__).resolve().parents[2],
        env=env,
    )
    output = result.stdout.strip()
    assert result.returncode == 0 and "JOURNEY OK" in output, (
        f"TUI journey harness failed (exit {result.returncode}):\n{output[-1200:] or result.stderr.strip()[-800:]}"
    )


def test_launcher_enables_fixture_source_and_injects_debug_for_fixture() -> None:
    """Launcher contract: enable src_fixtures for the child; --fixture means debugger."""
    text = LAUNCHER.read_text(encoding="utf-8")
    assert "src_fixtures" in text, "launcher must enable the fixture source for its child"
    assert "--debug" in text, "launcher must inject --debug for the fixture composition"
