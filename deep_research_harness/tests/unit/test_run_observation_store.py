"""Tests for bounded, non-authoritative retained Run observations.

@impl RUS-001
@impl RUS-002
@impl RUS-004
@impl RUS-007
"""

from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime
from pathlib import Path

import pytest

from deerflow_deep_research.domain.run_observation import (
    JournalAvailability,
    ObservationInspectability,
    RecordBearingLifecycleFact,
    RetentionState,
    RunEvent,
    RunEventCategory,
    RunObservationManifest,
    RunSummary,
)
from deerflow_deep_research.runtime.run_observation import RunObservationRecorder, RunObservationStore
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.run_observation import BundleRunObservationPublisher

BUNDLE_ID = "b_" + "A" * 43


def _fact(**overrides: object) -> RecordBearingLifecycleFact:
    return RecordBearingLifecycleFact(
        **{
            "bundle_id": BUNDLE_ID,
            "action": "start",
            "status": "suspended",
            "phase": "bootstrap",
            "generation": 0,
            "durability": "restart_durable",
            **overrides,
        }
    )


@pytest.mark.asyncio
async def test_observations_use_an_opaque_storage_key_and_contain_no_lifecycle_authority(tmp_path: Path) -> None:
    root = tmp_path / ".reports" / "deep-research-diagnostics"
    store = RunObservationStore(retained_root=root)

    view = await store.publish(_fact())
    inspection = await store.inspect(bundle_id=BUNDLE_ID)

    assert view.inspectability is ObservationInspectability.AVAILABLE
    assert inspection.inspectability is ObservationInspectability.AVAILABLE
    assert inspection.summary is not None
    assert inspection.summary.bundle_id == BUNDLE_ID
    assert inspection.summary.updated_at <= datetime.now(UTC)
    assert all(BUNDLE_ID not in str(path.relative_to(root)) for path in root.rglob("*"))
    serialized = inspection.model_dump_json(exclude_none=True)
    assert BUNDLE_ID in serialized
    for retired_authority in (
        "bundle_directory",
        "checkpoint",
        "binding",
        "provider_dsn",
        "provider_endpoint",
        "scope_bucket",
        "owner_index",
    ):
        assert retired_authority not in serialized
    for forbidden_operation in ("resolve", "discover", "control", "resume", "cancel", "refine", "bind", "reopen"):
        assert not hasattr(store, forbidden_operation)


@pytest.mark.asyncio
async def test_corrupt_observation_is_bounded_and_never_repaired_from_a_bundle(tmp_path: Path) -> None:
    root = tmp_path / ".reports" / "deep-research-diagnostics"
    store = RunObservationStore(retained_root=root)
    await store.publish(_fact())
    record = next(path for path in root.rglob("manifest.json"))
    record.write_text("{not-json", encoding="utf-8")
    record.chmod(0o600)

    inspection = await store.inspect(bundle_id=BUNDLE_ID)

    assert inspection.inspectability is ObservationInspectability.UNAVAILABLE
    assert inspection.summary is None
    assert inspection.events == ()


@pytest.mark.asyncio
async def test_admitted_bundle_journal_retains_correlated_validation_evidence_inside_its_diagnostics_subtree(
    tmp_path: Path,
) -> None:
    bundle_root = tmp_path / "workspace" / "deep-research" / "scopes" / ("s_" + "B" * 43) / BUNDLE_ID
    (bundle_root / "diagnostics").mkdir(mode=0o700, parents=True)
    os.chmod(bundle_root / "diagnostics", 0o700)
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID)
    recorder = RunObservationRecorder(store=store, bundle_id=BUNDLE_ID)

    await recorder.establish(generation=0, phase="wave1", durability="restart_durable")
    await recorder.record(
        category=RunEventCategory.VALIDATION,
        phase="wave1",
        work_id="work-1",
        attempt_id="work-1_a00",
        validation_stage="initial",
        validation_codes=("wave1_new_source_floor_not_met",),
    )
    inspection = await store.inspect(bundle_id=BUNDLE_ID)

    assert inspection.inspectability is ObservationInspectability.AVAILABLE
    assert (bundle_root / "diagnostics" / "journal-manifest.json").is_file()
    assert not (tmp_path / ".reports").exists()
    assert [(event.generation, event.validation_stage, event.validation_codes) for event in inspection.events] == [
        (0, None, ()),
        (0, "initial", ("wave1_new_source_floor_not_met",)),
    ]


@pytest.mark.asyncio
async def test_capacity_preserves_diagnostic_anchors_without_renumbering_retained_sequences(tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundle"
    (bundle_root / "diagnostics").mkdir(mode=0o700, parents=True)
    os.chmod(bundle_root / "diagnostics", 0o700)
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID, max_event_records=3)
    recorder = RunObservationRecorder(store=store, bundle_id=BUNDLE_ID)

    await recorder.establish(generation=0, phase="bootstrap", durability="restart_durable")
    await recorder.record(category=RunEventCategory.NODE, phase="bootstrap", attempt_id="bootstrap_a00")
    await recorder.record(category=RunEventCategory.NODE, phase="topic_planning", attempt_id="topic_planning_a00")
    await recorder.record(
        category=RunEventCategory.VALIDATION,
        phase="wave1",
        work_id="work-1",
        attempt_id="work-1_a00",
        validation_stage="initial",
        validation_codes=("wave1_new_source_floor_not_met",),
    )
    await store.publish(
        _fact(
            status="blocked",
            phase="wave1",
            terminal_outcome="blocked",
            failure_category="structured_output",
            diagnostic_ref="diag_" + "C" * 24,
        )
    )

    inspection = await store.inspect(bundle_id=BUNDLE_ID)

    assert inspection.journal_availability is JournalAvailability.INCOMPLETE
    assert inspection.summary is not None
    assert inspection.summary.dropped_event_count == 2
    assert inspection.summary.first_dropped_sequence == 2
    assert inspection.summary.last_dropped_sequence == 3
    assert [event.sequence for event in inspection.events] == [1, 4, 5]
    assert [event.category for event in inspection.events] == [
        RunEventCategory.ADMISSION,
        RunEventCategory.VALIDATION,
        RunEventCategory.TERMINAL,
    ]


@pytest.mark.asyncio
async def test_bundle_journal_keeps_generation_scoped_canonical_events_and_rejects_unsafe_codes(tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundle"
    (bundle_root / "diagnostics").mkdir(mode=0o700, parents=True)
    os.chmod(bundle_root / "diagnostics", 0o700)
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID)
    recorder = RunObservationRecorder(store=store, bundle_id=BUNDLE_ID)

    await recorder.establish(generation=0, phase="wave1", durability="restart_durable")
    await recorder.record(
        category=RunEventCategory.VALIDATION,
        phase="wave1",
        work_id="work-1",
        attempt_id="work-1_a00",
        validation_stage="initial",
        validation_codes=("wave1_new_source_floor_not_met",),
    )
    await recorder.establish(generation=1, phase="rerun", durability="restart_durable")
    await recorder.record(
        category=RunEventCategory.NODE,
        phase="rerun",
        attempt_id="rerun_a00",
    )
    await recorder.record(
        category=RunEventCategory.VALIDATION,
        phase="rerun",
        work_id="work-1",
        attempt_id="work-1_a01",
        validation_stage="repair",
        validation_codes=("raw validation detail must not persist",),
    )

    inspection = await store.inspect(bundle_id=BUNDLE_ID)

    assert [(event.sequence, event.generation, event.validation_stage, event.validation_codes) for event in inspection.events] == [
        (1, 0, None, ()),
        (2, 0, "initial", ("wave1_new_source_floor_not_met",)),
        (3, 1, None, ()),
    ]
    assert "raw validation detail must not persist" not in inspection.model_dump_json()


@pytest.mark.asyncio
async def test_bundle_journal_marks_readable_legacy_correlation_incomplete(tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundle"
    journal_root = bundle_root / "diagnostics"
    journal_root.mkdir(mode=0o700, parents=True)
    os.chmod(journal_root, 0o700)
    now = datetime.now(UTC)
    manifest = RunObservationManifest(
        schema_version=1,
        bundle_id=BUNDLE_ID,
        created_at=now,
        updated_at=now,
        retention_state=RetentionState.RETAINED,
        durability="restart_durable",
        summary_path="run-summary.json",
        events_path="diagnostics/events.jsonl",
    )
    summary = RunSummary(
        schema_version=1,
        bundle_id=BUNDLE_ID,
        status="active",
        phase="bootstrap",
        generation=0,
        updated_at=now,
        durability="restart_durable",
        journal_availability=JournalAvailability.COMPLETE,
        latest_event_sequence=1,
    )
    event = RunEvent(
        schema_version=1,
        sequence=1,
        timestamp=now,
        category=RunEventCategory.ADMISSION,
        phase="bootstrap",
    )
    for path, content in (
        (journal_root / "journal-manifest.json", manifest.model_dump_json().encode("utf-8")),
        (journal_root / "run-summary.json", summary.model_dump_json().encode("utf-8")),
        (journal_root / "events.jsonl", (event.model_dump_json() + "\n").encode("utf-8")),
    ):
        path.write_bytes(content)
        os.chmod(path, 0o600)
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID)

    inspection = await store.inspect(bundle_id=BUNDLE_ID)

    assert inspection.inspectability is ObservationInspectability.AVAILABLE
    assert inspection.journal_availability is JournalAvailability.INCOMPLETE
    assert inspection.summary is not None
    assert inspection.summary.journal_availability is JournalAvailability.INCOMPLETE


@pytest.mark.asyncio
async def test_bundle_journal_serializes_concurrent_producers_with_stable_sequences(tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundle"
    (bundle_root / "diagnostics").mkdir(mode=0o700, parents=True)
    os.chmod(bundle_root / "diagnostics", 0o700)
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID, max_event_records=32)
    recorder = RunObservationRecorder(store=store, bundle_id=BUNDLE_ID)
    await recorder.establish(generation=0, phase="wave1", durability="restart_durable")

    await asyncio.gather(
        *(
            recorder.record(
                category=RunEventCategory.ATTEMPT,
                phase="wave1",
                work_id=f"work-{index}",
                attempt_id=f"work-{index}_a00",
            )
            for index in range(12)
        )
    )

    inspection = await store.inspect(bundle_id=BUNDLE_ID)

    assert [event.sequence for event in inspection.events] == list(range(1, 14))
    assert {event.attempt_id for event in inspection.events[1:]} == {
        f"work-{index}_a00" for index in range(12)
    }


@pytest.mark.asyncio
async def test_bundle_journal_marks_a_recovered_write_failure_incomplete(tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundle"
    journal_root = bundle_root / "diagnostics"
    journal_root.mkdir(mode=0o700, parents=True)
    os.chmod(journal_root, 0o700)
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID)
    recorder = RunObservationRecorder(store=store, bundle_id=BUNDLE_ID)
    await recorder.establish(generation=0, phase="bootstrap", durability="restart_durable")

    os.chmod(journal_root, 0o500)
    try:
        await recorder.record(
            category=RunEventCategory.NODE,
            phase="bootstrap",
            attempt_id="bootstrap_a00",
        )
    finally:
        os.chmod(journal_root, 0o700)

    inspection = await store.inspect(bundle_id=BUNDLE_ID)

    assert inspection.inspectability is ObservationInspectability.AVAILABLE
    assert inspection.journal_availability is JournalAvailability.INCOMPLETE
    assert inspection.summary is not None
    assert inspection.summary.journal_availability is JournalAvailability.INCOMPLETE


@pytest.mark.asyncio
async def test_bundle_journal_persists_a_prior_write_failure_after_the_next_successful_event(tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundle"
    journal_root = bundle_root / "diagnostics"
    journal_root.mkdir(mode=0o700, parents=True)
    os.chmod(journal_root, 0o700)
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID)
    recorder = RunObservationRecorder(store=store, bundle_id=BUNDLE_ID)
    await recorder.establish(generation=0, phase="bootstrap", durability="restart_durable")

    os.chmod(journal_root, 0o500)
    try:
        await recorder.record(
            category=RunEventCategory.NODE,
            phase="bootstrap",
            attempt_id="bootstrap_a00",
        )
    finally:
        os.chmod(journal_root, 0o700)
    await recorder.record(
        category=RunEventCategory.NODE,
        phase="bootstrap",
        attempt_id="bootstrap_a01",
    )

    reopened_store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID)
    inspection = await reopened_store.inspect(bundle_id=BUNDLE_ID)

    assert inspection.journal_availability is JournalAvailability.INCOMPLETE
    assert inspection.summary is not None
    assert inspection.summary.journal_availability is JournalAvailability.INCOMPLETE


@pytest.mark.asyncio
async def test_bundle_journal_returns_unavailable_for_a_corrupted_event_snapshot(tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundle"
    journal_root = bundle_root / "diagnostics"
    journal_root.mkdir(mode=0o700, parents=True)
    os.chmod(journal_root, 0o700)
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID)
    recorder = RunObservationRecorder(store=store, bundle_id=BUNDLE_ID)
    await recorder.establish(generation=0, phase="bootstrap", durability="restart_durable")
    event_path = journal_root / "events.jsonl"
    event_path.write_text("{not-json", encoding="utf-8")
    os.chmod(event_path, 0o600)

    inspection = await store.inspect(bundle_id=BUNDLE_ID)

    assert inspection.inspectability is ObservationInspectability.UNAVAILABLE
    assert inspection.summary is None
    assert inspection.events == ()


@pytest.mark.asyncio
async def test_lifecycle_resolved_publisher_writes_only_the_selected_bundle_journal(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    lifecycle = BundleLifecycle(workspace_host_path=workspace)
    scope = ("journal-user", "journal-thread")
    bundle = await lifecycle.start(scope=scope, request_text="Research journal lifetime.")
    publisher = BundleRunObservationPublisher(lifecycle=lifecycle, scope=scope)
    fact = _fact(bundle_id=bundle.bundle_id.value)

    view = await publisher.publish(fact)
    inspection = await RunObservationStore(
        bundle_root=lifecycle.private_root(bundle),
        bundle_id=bundle.bundle_id.value,
    ).inspect(bundle_id=bundle.bundle_id.value)

    assert view.inspectability is ObservationInspectability.AVAILABLE
    assert inspection.inspectability is ObservationInspectability.AVAILABLE
    assert inspection.summary is not None
    assert inspection.summary.bundle_id == bundle.bundle_id.value
    assert not (tmp_path / ".reports").exists()
