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
