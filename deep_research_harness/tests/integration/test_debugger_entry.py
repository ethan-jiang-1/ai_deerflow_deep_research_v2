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


_JOURNEY_CHILD = r"""
import asyncio, sys, tempfile
from pathlib import Path

sys.argv = ["demo_tui.py", "--fixture", "--debug"]
sys.path.insert(0, "scripts")

import textual.app

STEPS = []


def fake_run(self, *a, **k):
    # Headless stand-in for App.run: drive the runbook-030 loop for real.
    main_mod = sys.modules["__main__"]
    real_adapter = main_mod.DemoAdapter
    isolated_root = Path(tempfile.mkdtemp(prefix="debugger-journey-")) / "demo-runs"
    main_mod.DemoAdapter = lambda: real_adapter(bundle_root=isolated_root)

    async def drive():
        async with self.run_test(size=(100, 40)) as pilot:
            for _ in range(120):
                await pilot.pause()
                if type(getattr(self, "last_update", None)).__name__ == "Ready":
                    STEPS.append("ready")
                    break
                await asyncio.sleep(0.05)
            else:
                STEPS.append("ready-timeout")
                return
            self.query_one("#composer").value = "Compare renewable-energy storage approaches"
            await pilot.press("enter")
            for _ in range(120):
                await pilot.pause()
                if self._debug_driver is not None:
                    STEPS.append("session")
                    break
                await asyncio.sleep(0.05)
            else:
                STEPS.append("session-timeout")
                return
            self.query_one("#composer").value = "advance"
            await pilot.press("enter")
            await pilot.pause()
            self.query_one("#composer").value = "/detach"
            await pilot.press("enter")
            for _ in range(120):
                await pilot.pause()
                if self._debug_driver is None:
                    STEPS.append("detach")
                    break
                await asyncio.sleep(0.05)
            else:
                STEPS.append("detach-timeout")

    asyncio.run(drive())


textual.app.App.run = fake_run

import runpy

runpy.run_path("scripts/demo_tui.py", run_name="__main__")
print("STEPS:", ",".join(STEPS))
"""


def test_debugger_script_as_main_runs_the_workbench_journey() -> None:
    """Executing the TUI script as __main__ must serve the runbook-030 loop.

    Regression: the C4b debug methods were defined and bound to the class
    AFTER the ``if __name__ == "__main__": main()`` guard, so a real launch
    blocked inside main() before the bindings executed and the composer
    submit crashed with AttributeError. Import-time tests cannot see this;
    only executing the script as __main__ can.
    """
    import os
    import sys

    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    result = subprocess.run(
        [sys.executable, "-c", _JOURNEY_CHILD],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=Path(__file__).resolve().parents[2],
        env=env,
    )
    output = result.stdout.strip()
    assert "STEPS: ready,session,detach" in output, (
        f"debug journey through the real script failed: {output[-400:] or result.stderr.strip()[-400:]}"
    )


def test_launcher_enables_fixture_source_and_injects_debug_for_fixture() -> None:
    """Launcher contract: enable src_fixtures for the child; --fixture means debugger."""
    text = LAUNCHER.read_text(encoding="utf-8")
    assert "src_fixtures" in text, "launcher must enable the fixture source for its child"
    assert "--debug" in text, "launcher must inject --debug for the fixture composition"
