"""CLI contract for the operator-only scripted-real workflow debug command.

The baseline must complete in under 10 seconds with zero env reads and zero
network, and every script shortage or surplus must fail loudly instead of
reporting a completed run.

@impl SCR-003
@impl SCR-004
@impl SCR-005
"""

from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

import pytest


@pytest.fixture
def _scripts_path() -> str:
    scripts = str(Path(__file__).resolve().parents[2] / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    return scripts


def _await(coro: object) -> object:
    return asyncio.run(coro)  # type: ignore[arg-type]


def _makefile() -> str:
    return (Path(__file__).resolve().parents[2] / "Makefile").read_text(encoding="utf-8")


def test_debug_target_is_independent_of_the_demo_surface(_scripts_path: str) -> None:
    makefile = _makefile()
    assert "\ndebug-scripted-real-workflow: entry-preflight\n" in makefile
    assert "python scripts/debug_scripted_real_workflow.py" in makefile
    # The debug target is not a demo-real mode flag: demo-real keeps its own
    # entry and gains no scripted-real switch.
    demo_real_body = makefile.split("demo-real: entry-preflight", 1)[1].split("\n\n", 1)[0]
    assert "debug_scripted_real_workflow" not in demo_real_body
    assert "--scripted-real" not in demo_real_body


def test_baseline_command_reports_authenticity_and_boundaries(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch, _scripts_path: str
) -> None:
    """SCR-004/SCR-005: truthful labels, zero env, zero network, under 10 seconds."""

    import os

    import dotenv

    # deerflow.config performs one framework-owned import-time dotenv load;
    # the command's own path must never load dotenv again.
    import_calls: list[int] = []

    def recording_load(*_args: object, **_kwargs: object) -> bool:
        import_calls.append(len(import_calls))
        return False

    monkeypatch.setattr(dotenv, "load_dotenv", recording_load)
    monkeypatch.setattr(dotenv, "dotenv_values", lambda *_a, **_k: {})

    import debug_scripted_real_workflow as m

    def forbidden_load(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("the debug command must not read .env")

    monkeypatch.setattr(dotenv, "load_dotenv", forbidden_load)

    # No provider variable may be present for the run itself.
    stripped = {
        key: value
        for key, value in os.environ.items()
        if key
        not in {
            "TAVILY_API_KEY",
            "DEEPSEEK_API_KEY",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "DEERFLOW_DEMO_MODEL",
            "DEER_FLOW_CONFIG_PATH",
        }
    }
    monkeypatch.setattr(os, "environ", stripped)

    started_at = time.monotonic()
    exit_code = m.main(["--workspace", str(tmp_path / "run")])
    elapsed = time.monotonic() - started_at
    assert exit_code == 0
    assert elapsed < 10.0

    out = capsys.readouterr().out
    assert "composition:      all_real_adapters" in out
    assert "authenticity:     scripted_real_workflow" in out
    assert "zero-network:     true" in out
    assert "zero-credentials: true" in out
    assert "model calls:      11" in out
    assert "web_search calls: 2" in out
    assert "web_fetch calls:  0" in out
    assert "event journal:" in out
    assert "does NOT prove real model" in out
    assert "targeted-evidence/rerun/provider-recovery" in out


def test_missing_model_response_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _scripts_path: str) -> None:
    """SCR-003: a scripted response shortage is a failure, not a completed run."""

    import debug_scripted_real_workflow as m

    monkeypatch.setattr(m.baseline, "MODEL_SCRIPT", m.baseline.MODEL_SCRIPT[:-1])
    with pytest.raises(AssertionError, match="exhausted|budget violated|did not complete"):
        _await(m.run_scripted_real_workflow(workspace=tmp_path, run_id="missing-response"))


def test_surplus_tool_call_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _scripts_path: str) -> None:
    """SCR-003: an extra scripted tool call exhausts the queue and fails."""

    import debug_scripted_real_workflow as m

    script = list(m.baseline.MODEL_SCRIPT)
    script.insert(script.index(m.baseline.MODEL_SCRIPT[-4]) + 1, "TOOL_CALL:web_search")
    monkeypatch.setattr(m.baseline, "MODEL_SCRIPT", tuple(script))
    with pytest.raises(AssertionError, match="exhausted|budget violated|did not complete"):
        _await(m.run_scripted_real_workflow(workspace=tmp_path, run_id="surplus-tool"))


def test_invalid_script_output_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _scripts_path: str) -> None:
    """SCR-003: an invalid scripted candidate cannot produce a completed run."""

    import debug_scripted_real_workflow as m

    intake_index = next(index for index, template in enumerate(m.baseline.MODEL_SCRIPT) if "fetch_status" in template)
    script = list(m.baseline.MODEL_SCRIPT)
    script[intake_index] = script[intake_index].replace('"fetched"', '"broken-status"')
    monkeypatch.setattr(m.baseline, "MODEL_SCRIPT", tuple(script))
    with pytest.raises(AssertionError, match="did not complete|budget violated"):
        _await(m.run_scripted_real_workflow(workspace=tmp_path, run_id="invalid-output"))


def test_targeted_entry_fails_the_baseline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _scripts_path: str) -> None:
    """SCR-003: entering the targeted-evidence branch is a baseline failure."""

    import debug_scripted_real_workflow as m

    synthesis_index = next(
        index for index, template in enumerate(m.baseline.MODEL_SCRIPT) if "finding:storage-economics" in template
    )
    script = list(m.baseline.MODEL_SCRIPT)
    script[synthesis_index] = script[synthesis_index].replace(
        '"gaps": []',
        '"gaps": [{"gap_id": "gap:forced", '
        '"description": "forced searchable gap", "priority": 2, "affected_topics": ["primary-evidence"], '
        '"search_required": true}]',
    )
    monkeypatch.setattr(m.baseline, "MODEL_SCRIPT", tuple(script))
    with pytest.raises(Exception, match="targeted|inconsistent|did not complete"):
        _await(m.run_scripted_real_workflow(workspace=tmp_path, run_id="targeted-entry"))
