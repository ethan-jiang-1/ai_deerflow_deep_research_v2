"""Read-only retained-observation coverage for the demo inspection command.

@impl RUS-003
@impl REC-004
@impl DPL-007
@impl RUS-005
@impl RUS-006
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import pytest

from deerflow_deep_research.domain.run_observation import RecordBearingLifecycleFact
from deerflow_deep_research.runtime.run_observation import RunObservationStore

AGENT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = AGENT_ROOT / "scripts" / "demo_sessions.py"
BUNDLE_ID = "b_" + "A" * 43
DIAGNOSTIC_REF = "diag_" + "P" * 24


def _module():
    scripts = str(SCRIPT_PATH.parent)
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    spec = importlib.util.spec_from_file_location("deep_research_demo_sessions", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _fact(**updates: object) -> RecordBearingLifecycleFact:
    values: dict[str, object] = {
        "bundle_id": BUNDLE_ID,
        "action": "start",
        "status": "suspended",
        "phase": "bootstrap",
        "generation": 0,
        "durability": "same_process",
    }
    values.update(updates)
    return RecordBearingLifecycleFact(**values)


@pytest.mark.asyncio
async def test_inspect_prints_only_safe_observation_facts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _module()
    store = RunObservationStore(retained_root=tmp_path / "observations")
    await store.publish(_fact())
    monkeypatch.setattr(module, "_observation_store", lambda: store)

    code = await module.run(argparse.Namespace(bundle_id=BUNDLE_ID))

    output = capsys.readouterr().out
    assert code == 0
    assert f"Run Bundle: {BUNDLE_ID}" in output
    assert "Retention: retained" in output
    assert "Durability: same_process" in output
    assert "Observed summary: suspended@bootstrap" in output
    assert "Observed event #1: lifecycle@bootstrap" in output
    assert "Observation does not resume or control this Run Bundle." in output
    assert str(tmp_path) not in output
    assert "workspace/" not in output


@pytest.mark.asyncio
async def test_inspect_renders_only_the_verified_terminal_diagnostic(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _module()
    store = RunObservationStore(retained_root=tmp_path / "observations")
    await store.publish(
        _fact(
            status="blocked",
            phase="hitl1",
            terminal_outcome="blocked",
            failure_category="provider.timeout",
            diagnostic_ref=DIAGNOSTIC_REF,
            recovery_trigger_timeout_origin="bridge_wall_time_budget",
            final_timeout_origin="provider_sdk_timeout",
        )
    )
    monkeypatch.setattr(module, "_observation_store", lambda: store)

    code = await module.run(argparse.Namespace(bundle_id=BUNDLE_ID))

    output = capsys.readouterr().out
    assert code == 0
    assert f"Diagnostic reference: {DIAGNOSTIC_REF}" in output
    assert "Diagnostic category: provider.timeout" in output
    assert "Diagnostic phase: hitl1" in output
    assert "recovery_trigger_timeout_origin" not in output
    assert "provider_sdk_timeout" not in output


@pytest.mark.asyncio
async def test_invalid_or_missing_observation_never_creates_or_controls_a_bundle(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _module()
    root = tmp_path / "observations"
    store = RunObservationStore(retained_root=root)
    monkeypatch.setattr(module, "_observation_store", lambda: store)

    invalid = await module.run(argparse.Namespace(bundle_id="not-a-bundle"))
    assert invalid == 2
    assert "Run Bundle id is invalid." in capsys.readouterr().out
    assert not root.exists()

    missing = await module.run(argparse.Namespace(bundle_id=BUNDLE_ID))
    assert missing == 2
    assert "No retained observation was found" in capsys.readouterr().out
    assert not root.exists()


def test_demo_sessions_parser_exposes_only_a_bundle_observation_target() -> None:
    module = _module()

    args = module._build_parser().parse_args([BUNDLE_ID])

    assert args.bundle_id == BUNDLE_ID
    assert not hasattr(args, "research_id")
    assert not hasattr(args, "session_ref")


def test_observation_store_has_no_lifecycle_control_operations() -> None:
    public_methods = set(RunObservationStore.__dict__)

    assert {"publish", "inspect", "record_event", "cleanup"} <= public_methods
    assert not {"start", "status", "resume", "cancel", "refine", "resolve"} & public_methods
