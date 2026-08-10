"""Read-only contained Event Journal coverage for the demo inspection command.

@impl RUS-008
@impl REJ-004
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from deerflow_deep_research.domain.run_observation import (
    JournalAvailability,
    JournalIncompleteReason,
    RecordBearingLifecycleFact,
    RunEvent,
    RunEventCategory,
    RunSummary,
)
from deerflow_deep_research.domain.session_workbench import (
    WorkbenchAvailability,
    WorkbenchDiagnosisView,
)
from deerflow_deep_research.runtime.run_observation import RunObservationStore

AGENT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = AGENT_ROOT / "scripts" / "demo_sessions.py"
BUNDLE_ID = "b_" + "A" * 43


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


def _diagnosis() -> WorkbenchDiagnosisView:
    now = datetime.now(UTC)
    summary = RunSummary(
        schema_version=2,
        bundle_id=BUNDLE_ID,
        status="blocked",
        phase="wave1",
        generation=1,
        updated_at=now,
        durability="restart_durable",
        terminal_outcome="blocked",
        failure_category="output.structured_invalid",
        diagnostic_ref="diag_" + "P" * 24,
        journal_availability=JournalAvailability.INCOMPLETE,
        latest_event_sequence=4,
        dropped_event_count=1,
        first_dropped_sequence=2,
        last_dropped_sequence=2,
    )
    event = RunEvent(
        schema_version=2,
        sequence=4,
        timestamp=now,
        category=RunEventCategory.VALIDATION,
        generation=1,
        phase="wave1",
        outcome="failed",
        work_id="work-1",
        attempt_id="work-1_a01",
        validation_stage="repair",
        validation_codes=("wave1_new_source_floor_not_met",),
    )
    return WorkbenchDiagnosisView(
        availability=WorkbenchAvailability.AVAILABLE,
        summary=summary,
        events=(event,),
        incomplete_reasons=(JournalIncompleteReason.CAPACITY,),
    )


@pytest.mark.asyncio
async def test_inspect_renders_safe_contained_journal_facts(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _module()

    async def diagnosis(_bundle_id: str) -> WorkbenchDiagnosisView:
        return _diagnosis()

    monkeypatch.setattr(module, "_diagnosis", diagnosis)
    code = await module.run(argparse.Namespace(command="inspect", bundle_id=BUNDLE_ID))

    output = capsys.readouterr().out
    assert code == 0
    assert f"Run Bundle: {BUNDLE_ID}" in output
    assert "Journal health: incomplete" in output
    assert "Journal incomplete because: capacity" in output
    assert "Dropped event interval: 2-2 (1 events)" in output
    assert "generation 1 wave1 work work-1 attempt work-1_a01" in output
    assert "validation repair codes wave1_new_source_floor_not_met" in output
    assert "diag_" + "P" * 24 in output
    assert "Event Journal is read-only; lifecycle controls remain independent." in output
    assert "resume" not in output.lower()
    assert "provider-body" not in output
    assert "/Users/" not in output


@pytest.mark.asyncio
async def test_inspect_renders_only_explicit_safe_incomplete_reasons(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _module()

    async def diagnosis(_bundle_id: str) -> WorkbenchDiagnosisView:
        return _diagnosis().model_copy(
            update={
                "incomplete_reasons": (
                    JournalIncompleteReason.LEGACY,
                    JournalIncompleteReason.CAPACITY,
                    JournalIncompleteReason.PERSISTENCE,
                )
            }
        )

    monkeypatch.setattr(module, "_diagnosis", diagnosis)
    code = await module.run(argparse.Namespace(command="inspect", bundle_id=BUNDLE_ID))

    output = capsys.readouterr().out
    assert code == 0
    assert "Journal incomplete because: legacy, capacity, persistence" in output
    assert "manifest" not in output.lower()
    assert "journal-manifest.json" not in output


@pytest.mark.asyncio
async def test_invalid_or_unavailable_bundle_never_falls_back_to_external_history(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """@impl REC-004"""
    module = _module()
    calls: list[str] = []

    async def unavailable(bundle_id: str) -> WorkbenchDiagnosisView:
        calls.append(bundle_id)
        return WorkbenchDiagnosisView(availability=WorkbenchAvailability.UNAVAILABLE)

    monkeypatch.setattr(module, "_diagnosis", unavailable)
    invalid = await module.run(argparse.Namespace(command="inspect", bundle_id="not-a-bundle"))
    assert invalid == 2
    assert calls == []
    assert "Run Bundle id is invalid." in capsys.readouterr().out

    unavailable_result = await module.run(argparse.Namespace(command="inspect", bundle_id=BUNDLE_ID))
    assert unavailable_result == 2
    assert calls == [BUNDLE_ID]
    assert "contained Event Journal is unavailable" in capsys.readouterr().out


def test_demo_sessions_parser_exposes_only_a_bundle_target() -> None:
    module = _module()

    args = module._build_parser().parse_args(["inspect", BUNDLE_ID])

    assert args.command == "inspect"
    assert args.bundle_id == BUNDLE_ID
    assert not hasattr(args, "research_id")
    assert not hasattr(args, "session_ref")


@pytest.mark.asyncio
async def test_inspect_command_reads_only_an_existing_selected_bundle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """@impl RUS-003"""
    module = _module()
    from _demo_core import DemoAdapter

    bundle_root = tmp_path / "local-profile"
    adapter = DemoAdapter(bundle_root=bundle_root)
    await adapter.open()
    try:
        lifecycle = adapter._bundle_lifecycle
        scope = (adapter._envelope.effective_user_id, adapter._envelope.outer_thread_id)
        bundle = await lifecycle.start(scope=scope, request_text="Inspect this contained journal.")
        await RunObservationStore(
            bundle_root=lifecycle.private_root(bundle),
            bundle_id=bundle.bundle_id.value,
        ).publish(
            RecordBearingLifecycleFact(
                bundle_id=bundle.bundle_id.value,
                action="status",
                status="suspended",
                phase="bootstrap",
                generation=0,
                durability="restart_durable",
            )
        )
    finally:
        await adapter.aclose()

    monkeypatch.setattr(module, "_bundle_root", lambda: bundle_root)
    code = await module.run(argparse.Namespace(command="inspect", bundle_id=bundle.bundle_id.value))

    output = capsys.readouterr().out
    assert code == 0
    assert f"Run Bundle: {bundle.bundle_id.value}" in output
    assert "Journal health: complete" in output
    assert "Event Journal is read-only; lifecycle controls remain independent." in output
    assert "resume" not in output.lower()


@pytest.mark.asyncio
async def test_fixed_local_profile_reads_only_an_existing_selected_bundle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl DPL-007
    @impl RUS-006
    """
    module = _module()
    from _demo_core import DemoAdapter

    adapter = DemoAdapter(bundle_root=tmp_path / "local-profile")
    await adapter.open()
    try:
        lifecycle = adapter._bundle_lifecycle
        scope = (adapter._envelope.effective_user_id, adapter._envelope.outer_thread_id)
        bundle = await lifecycle.start(scope=scope, request_text="Inspect this contained journal.")
        store = RunObservationStore(
            bundle_root=lifecycle.private_root(bundle),
            bundle_id=bundle.bundle_id.value,
        )
        await store.publish(
            RecordBearingLifecycleFact(
                bundle_id=bundle.bundle_id.value,
                action="status",
                status="suspended",
                phase="bootstrap",
                generation=0,
                durability="restart_durable",
            )
        )
    finally:
        await adapter.aclose()

    monkeypatch.setattr(module, "_bundle_root", lambda: tmp_path / "local-profile")
    available = await module._diagnosis(bundle.bundle_id.value)
    assert available.availability is WorkbenchAvailability.AVAILABLE
    assert available.summary is not None
    assert available.summary.bundle_id == bundle.bundle_id.value

    shutil.rmtree(lifecycle.private_root(bundle))
    lost = await module._diagnosis(bundle.bundle_id.value)
    assert lost.availability is WorkbenchAvailability.UNAVAILABLE
    assert not await asyncio.to_thread(lambda: any(path.name == "observations" for path in tmp_path.rglob("*")))


def test_journal_reader_has_no_lifecycle_control_operations() -> None:
    public_methods = set(RunObservationStore.__dict__)

    assert {"publish", "inspect", "record_event", "cleanup"} <= public_methods
    assert not {"start", "status", "resume", "cancel", "refine", "resolve"} & public_methods
