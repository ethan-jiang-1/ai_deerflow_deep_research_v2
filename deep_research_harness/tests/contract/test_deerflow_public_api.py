"""Current DeerFlow public boundary used by Deep Research observability."""

from __future__ import annotations

import inspect
import subprocess
import tomllib
from pathlib import Path

from deerflow.trace_context import get_current_trace_id
from langchain.tools import ToolRuntime

CURRENT_DEERFLOW_PIN = "66b9e7f21212490cf92fafac137542b9deb06615"
REPO_ROOT = Path(__file__).resolve().parents[3]


def _git(*args: str, cwd: Path = REPO_ROOT) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.stdout.strip()


def test_current_deerflow_pin_is_synchronized_without_an_upgrade() -> None:
    nested_head = _git("rev-parse", "HEAD", cwd=REPO_ROOT / "deerflow")
    index_entry = _git("ls-files", "--stage", "deerflow")
    registry = tomllib.loads((REPO_ROOT / "openspec/governance/project-structure.toml").read_text(encoding="utf-8"))

    assert nested_head == CURRENT_DEERFLOW_PIN
    assert index_entry.split()[:2] == ["160000", CURRENT_DEERFLOW_PIN]
    assert registry["upstream_gitlink"]["commit"] == CURRENT_DEERFLOW_PIN


def test_current_tool_runtime_publicly_injects_an_explicit_callable_writer() -> None:
    signature = inspect.signature(ToolRuntime)
    parameter = signature.parameters["stream_writer"]
    attempts: list[object] = []

    def writer(payload: object) -> None:
        attempts.append(payload)

    bound = signature.bind(
        state={},
        context={},
        config={},
        stream_writer=writer,
        tool_call_id=None,
        store=None,
    )

    assert parameter.kind is not inspect.Parameter.VAR_POSITIONAL
    assert parameter.kind is not inspect.Parameter.VAR_KEYWORD
    assert bound.arguments["stream_writer"] is writer
    assert callable(bound.arguments["stream_writer"])
    assert attempts == []


def test_current_trace_id_surface_remains_zero_argument() -> None:
    signature = inspect.signature(get_current_trace_id)

    assert tuple(signature.parameters) == ()
    assert get_current_trace_id() is None
