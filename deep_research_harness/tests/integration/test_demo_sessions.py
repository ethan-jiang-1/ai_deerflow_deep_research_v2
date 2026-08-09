"""Read-only retained-observation coverage for the demo inspection command.

@impl RUS-003
@impl REC-004
@impl DPL-007
@impl RUS-005
@impl RUS-006
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import secrets
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from deerflow_deep_research.domain.run_observation import (
    ObservationInspectability,
    RecordBearingLifecycleFact,
    RunObservationInspection,
)
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


def _fact(*, bundle_id: str = BUNDLE_ID, **updates: object) -> RecordBearingLifecycleFact:
    values: dict[str, object] = {
        "bundle_id": bundle_id,
        "action": "start",
        "status": "suspended",
        "phase": "bootstrap",
        "generation": 0,
        "durability": "same_process",
    }
    values.update(updates)
    return RecordBearingLifecycleFact(**values)


def _bundle_id() -> str:
    return "b_" + secrets.token_urlsafe(32)


def _rendered_command(bundle_id: str) -> list[str]:
    _module()
    from _terminal_failure_presentation import inspection_command

    command = inspection_command(bundle_id)
    assert command is not None
    return shlex.split(command)


def _run_rendered_command(bundle_id: str) -> subprocess.CompletedProcess[str]:
    return _run_inspection_command(arguments=_rendered_command(bundle_id))


def _run_inspection_command(*, arguments: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=AGENT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


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

    args = module._build_parser().parse_args(["inspect", BUNDLE_ID])

    assert args.command == "inspect"
    assert args.bundle_id == BUNDLE_ID
    assert not hasattr(args, "research_id")
    assert not hasattr(args, "session_ref")
    with pytest.raises(SystemExit):
        module._build_parser().parse_args([BUNDLE_ID])


class _InspectOnlyStore:
    def __init__(self, inspection: RunObservationInspection) -> None:
        self.inspection = inspection
        self.bundle_ids: list[str] = []

    async def inspect(self, *, bundle_id: str) -> RunObservationInspection:
        self.bundle_ids.append(bundle_id)
        return self.inspection

    def __getattr__(self, name: str) -> object:
        raise AssertionError(f"unexpected_observation_store_access:{name}")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("inspectability", "expected_code", "expected_line"),
    (
        (ObservationInspectability.AVAILABLE, 0, f"Run Bundle: {BUNDLE_ID}"),
        (ObservationInspectability.UNAVAILABLE, 2, "Retained observation is unavailable for safe inspection."),
    ),
)
async def test_inspection_dispatches_only_to_store_inspect(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    inspectability: ObservationInspectability,
    expected_code: int,
    expected_line: str,
) -> None:
    module = _module()
    store = _InspectOnlyStore(RunObservationInspection(bundle_id=BUNDLE_ID, inspectability=inspectability))
    monkeypatch.setattr(module, "_observation_store", lambda: store)

    code = await module.run(argparse.Namespace(command="inspect", bundle_id=BUNDLE_ID))

    assert code == expected_code
    assert expected_line in capsys.readouterr().out
    assert store.bundle_ids == [BUNDLE_ID]


@pytest.mark.asyncio
async def test_rendered_inspection_command_is_executable_from_harness_root() -> None:
    bundle_id = _bundle_id()
    corrupt_bundle_id = _bundle_id()
    store = RunObservationStore(retained_root=RunObservationStore.project_default_root(AGENT_ROOT))
    record_roots: list[Path] = []

    try:
        available = await store.publish(_fact(bundle_id=bundle_id))
        assert available.inspectability is ObservationInspectability.AVAILABLE
        record_roots.append(store._record_root(bundle_id))

        completed = await asyncio.to_thread(_run_rendered_command, bundle_id)
        assert completed.returncode == 0
        assert f"Run Bundle: {bundle_id}" in completed.stdout
        assert "Observation does not resume or control this Run Bundle." in completed.stdout

        invalid = await asyncio.to_thread(
            _run_inspection_command,
            arguments=["make", "demo-sessions", "DEMO_ARGS=inspect not-a-bundle"],
        )
        assert invalid.returncode == 2
        assert "Run Bundle id is invalid." in invalid.stdout

        missing = await asyncio.to_thread(
            _run_inspection_command,
            arguments=["make", "demo-sessions", f"DEMO_ARGS=inspect {_bundle_id()}"],
        )
        assert missing.returncode == 2
        assert "No retained observation was found for this Run Bundle." in missing.stdout

        corrupt = await store.publish(_fact(bundle_id=corrupt_bundle_id))
        assert corrupt.inspectability is ObservationInspectability.AVAILABLE
        corrupt_root = store._record_root(corrupt_bundle_id)
        record_roots.append(corrupt_root)
        (corrupt_root / "manifest.json").write_text("{not-json", encoding="utf-8")

        unavailable = await asyncio.to_thread(
            _run_inspection_command,
            arguments=["make", "demo-sessions", f"DEMO_ARGS=inspect {corrupt_bundle_id}"],
        )
        assert unavailable.returncode == 2
        assert "Retained observation is unavailable for safe inspection." in unavailable.stdout

        retired = await asyncio.to_thread(
            _run_inspection_command,
            arguments=["make", "demo-sessions", f"DEMO_ARGS={bundle_id}"],
        )
        assert retired.returncode == 2
        assert "usage:" in retired.stderr
    finally:
        for record_root in reversed(record_roots):
            shutil.rmtree(record_root, ignore_errors=True)


def test_observation_store_has_no_lifecycle_control_operations() -> None:
    public_methods = set(RunObservationStore.__dict__)

    assert {"publish", "inspect", "record_event", "cleanup"} <= public_methods
    assert not {"start", "status", "resume", "cancel", "refine", "resolve"} & public_methods
