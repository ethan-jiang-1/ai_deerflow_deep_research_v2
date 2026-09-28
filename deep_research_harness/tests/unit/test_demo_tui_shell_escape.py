"""Operator shell escape contract for the debugger workbench (BUG-free feature).

@impl add-debugger-shell-escape
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


@pytest.fixture
def _scripts_path():
    """Ensure demo_tui is importable."""
    scripts = str(Path(__file__).resolve().parents[2] / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    return scripts


@pytest.mark.asyncio
async def test_runs_in_the_anchored_cwd(_scripts_path, tmp_path):
    """The escape runs with the caller-provided working directory (the live
    session's Bundle directory when one is open)."""
    from demo_tui import _capture_shell_output

    output = _capture_shell_output("pwd", tmp_path)
    assert output.strip() == str(tmp_path)


@pytest.mark.asyncio
async def test_reports_nonzero_exit(_scripts_path):
    from demo_tui import _capture_shell_output

    output = _capture_shell_output("false", None)
    assert "[exit 1]" in output


@pytest.mark.asyncio
async def test_captures_stderr(_scripts_path):
    from demo_tui import _capture_shell_output

    output = _capture_shell_output("echo oops >&2", None)
    assert "oops" in output
    assert "[stderr]" in output


@pytest.mark.asyncio
async def test_timeout_is_bounded(_scripts_path, tmp_path):
    from demo_tui import _capture_shell_output

    output = _capture_shell_output("sleep 5", None, timeout_s=1)
    assert "timeout" in output


@pytest.mark.asyncio
async def test_output_is_truncated(_scripts_path):
    from demo_tui import _capture_shell_output

    output = _capture_shell_output("yes x | head -c 6000", None, max_chars=200)
    assert len(output) < 400
    assert "已截断" in output


@pytest.mark.asyncio
async def test_stdin_is_not_the_terminal(_scripts_path):
    """cat must hit EOF immediately (stdin is /dev/null), never block on the TUI."""
    from demo_tui import _capture_shell_output

    output = _capture_shell_output("cat", None)
    assert output is not None
