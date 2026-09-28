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


def _launcher_forwarded_argv(*args: str, tmp_path: Path, extra_env: dict[str, str] | None = None) -> str:
    """Run the launcher with a stub interpreter and capture the forwarded argv."""
    import os

    stub = tmp_path / "stub-python"
    stub.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n', encoding="utf-8")
    stub.chmod(0o755)
    env = dict(os.environ)
    env["DEBUGGER_PYTHON"] = str(stub)
    env.pop("PYTHONPATH", None)
    env.pop("DEBUGGER_COMPOSITION", None)
    env.pop("DEBUGGER_PROFILE", None)
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        [str(LAUNCHER), *args],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=tmp_path,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_launcher_chooses_a_composition_when_started_bare(tmp_path: Path) -> None:
    """RED-013 chooser: a bare invocation must not fall into Gateway mode.

    Non-interactive callers (agents, CI) take the documented default — the
    fixture debugger — and DEBUGGER_COMPOSITION is the explicit selection seam.
    """
    import os

    default_argv = _launcher_forwarded_argv(tmp_path=tmp_path)
    assert "--fixture" in default_argv and "--debug" in default_argv

    embedded = _launcher_forwarded_argv(tmp_path=tmp_path, extra_env={"DEBUGGER_COMPOSITION": "embedded-smoke"})
    assert "--embedded-smoke" in embedded
    # This launcher IS the debugger, so the all-real composition is debugged too.
    assert "--debug" in embedded
    assert "--fixture" not in embedded

    stub = tmp_path / "stub-python"
    stub.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n', encoding="utf-8")
    stub.chmod(0o755)
    env = dict(os.environ)
    env["DEBUGGER_PYTHON"] = str(stub)
    env.pop("PYTHONPATH", None)
    env["DEBUGGER_COMPOSITION"] = "gateway"
    no_profile = subprocess.run([str(LAUNCHER)], capture_output=True, text=True, timeout=30, cwd=tmp_path, env=env)
    assert no_profile.returncode != 0
    assert "DEBUGGER_PROFILE" in (no_profile.stderr + no_profile.stdout)

    gateway = _launcher_forwarded_argv(
        tmp_path=tmp_path, extra_env={"DEBUGGER_COMPOSITION": "gateway", "DEBUGGER_PROFILE": "demo"}
    )
    assert "--profile" in gateway and "demo" in gateway
    assert "--debug" not in gateway


def test_launcher_injects_the_fixture_debugger_for_every_entry_spelling(tmp_path: Path) -> None:
    """RED-013 regression: the injection is behavioural, not a text grep.

    A bare ``--fixture``, an explicit ``--debug``, and argparse's
    ``--attach=<id>`` spelling must all reach the TUI as a fixture debugger
    session; a real composition must never gain the fixture extras.
    """

    fixture_argv = _launcher_forwarded_argv("--fixture", tmp_path=tmp_path)
    assert "--fixture" in fixture_argv
    assert "--debug" in fixture_argv

    explicit = _launcher_forwarded_argv("--fixture", "--debug", tmp_path=tmp_path)
    assert explicit.count("--debug") == 1, "an operator-supplied --debug must not be duplicated"

    attached = _launcher_forwarded_argv("--attach=b_aaaaaaaaaaaaaaaaaaaaaaaa", tmp_path=tmp_path)
    assert "--fixture" in attached and "--debug" in attached
    assert "--attach=b_aaaaaaaaaaaaaaaaaaaaaaaa" in attached

    embedded = _launcher_forwarded_argv("--embedded-smoke", tmp_path=tmp_path)
    assert "--debug" in embedded, "the debugger launcher debugs the composition it was given"
    assert "--fixture" not in embedded, "a real composition must not gain the fixture composition"


_EMBEDDED_PROBE_CHILD = """
import asyncio, sys
sys.path.insert(0, "scripts")
import demo_tui

async def main():
    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test(size=(100, 40)) as pilot:
        for _ in range(80):
            await pilot.pause()
            update = getattr(app, "last_update", None)
            name = type(update).__name__
            if name in ("Fault", "Ready"):
                print("RESULT:", name)
                failure = getattr(update, "failure", None)
                if failure is not None:
                    print("CODE:", getattr(failure, "code", None))
                    print("MESSAGE:", failure.message)
                return
            await asyncio.sleep(0.1)
    print("RESULT: TIMEOUT")

asyncio.run(main()
)
"""


def test_embedded_smoke_reaches_ready_from_env_file_alone(tmp_path: Path) -> None:
    """BUG-075 regression: the entry chain must see the documented .env file.

    runbook-031 promises the `.env` three-variable preflight, but the launcher
    chain (and bare python) bypasses make's ``--env-file``, so an operator
    with a correct `.env` hit ``configuration.model_missing`` before any
    bundle. The three variables arrive only through a temp env file named by
    the ``DEMO_ENV_FILE`` seam; the child environment has them stripped.

    The child runs in FILE mode (like the launcher's ``python demo_tui.py``),
    not ``-c``: the framework's implicit ``find_dotenv`` anchors differently
    across invocation modes, and only file mode reproduces the operator's
    entry chain. The child script lives one directory below the env file and
    the env file is not named ``.env``, so no ambient ``find_dotenv`` walk can
    find any env file — the loader under test is the only path to Ready.
    """
    import os
    import sys

    env_file = tmp_path / "harness-env"
    env_file.write_text(
        "DEEPSEEK_API_KEY=dummy-key-not-real\n"
        "DEERFLOW_DEMO_MODEL=deepseek-v4-pro\n"
        "TAVILY_API_KEY=dummy-tavily-not-real\n",
        encoding="utf-8",
    )
    child_dir = tmp_path / "wd"
    child_dir.mkdir()
    child_file = child_dir / "embedded_probe_child.py"
    child_file.write_text(_EMBEDDED_PROBE_CHILD, encoding="utf-8")
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in ("DEEPSEEK_API_KEY", "DEERFLOW_DEMO_MODEL", "TAVILY_API_KEY", "PYTHONPATH")
    }
    env["DEMO_ENV_FILE"] = str(env_file)
    result = subprocess.run(
        [sys.executable, str(child_file)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=Path(__file__).resolve().parents[2],
        env=env,
    )
    assert "RESULT: Ready" in result.stdout, (
        f"embedded-smoke entry ignored the .env file: {result.stdout.strip()[-400:] or result.stderr.strip()[-400:]}"
    )
