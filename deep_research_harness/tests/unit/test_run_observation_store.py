"""Tests for bounded, non-authoritative retained Run observations.

@impl DRH-001
@impl REJ-001
@impl DRH-006
@impl REJ-002
@impl REJ-004
@impl REJ-006
@impl REJ-007
"""

from __future__ import annotations

import asyncio
import os
from datetime import UTC, datetime
from pathlib import Path

import pytest

from deerflow_deep_research.domain.run_observation import (
    BudgetStopReason,
    ExecutionProfileEvidence,
    FinalResponseShape,
    JournalAvailability,
    JournalIncompleteReason,
    ObservationInspectability,
    RecordBearingLifecycleFact,
    RetentionState,
    RunEvent,
    RunEventCategory,
    RunObservationManifest,
    RunSummary,
    classify_final_response_shape,
)
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.run_observation import (
    BundleRunObservationPublisher,
    RunObservationRecorder,
    RunObservationStore,
)

BUNDLE_ID = "b_" + "A" * 43


def _execution_profile(*, profile_id: str = "deepseek-v4-flash") -> ExecutionProfileEvidence:
    return ExecutionProfileEvidence(profile_id=profile_id, registry_revision="v1")


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


@pytest.mark.parametrize(
    ("response", "expected"),
    (
        pytest.param("   ", FinalResponseShape.EMPTY, id="empty"),
        pytest.param("```json\n{}\n```", FinalResponseShape.FENCED, id="fenced"),
        pytest.param('{"sources":[]}', FinalResponseShape.JSON_OBJECT, id="standalone-object"),
        pytest.param('prose {"outer":{"nested":true}} after', FinalResponseShape.EMBEDDED_JSON, id="nested-object"),
        pytest.param('{"first":1} {"second":2}', FinalResponseShape.EMBEDDED_JSON, id="multiple-objects"),
        pytest.param('[{"nested":true}]', FinalResponseShape.EMBEDDED_JSON, id="object-inside-array"),
        pytest.param("final prose only", FinalResponseShape.PROSE, id="prose"),
    ),
)
def test_final_response_shape_classifier_retains_only_the_closed_enum(
    response: str,
    expected: FinalResponseShape,
) -> None:
    original = response

    assert classify_final_response_shape(response) is expected
    assert response == original


def test_v3_validation_contract_rejects_impossible_shape_and_stage_pairs() -> None:
    base = {
        "schema_version": 3,
        "sequence": 2,
        "timestamp": datetime.now(UTC),
        "category": RunEventCategory.VALIDATION,
        "generation": 0,
        "phase": "wave1",
        "work_id": "work-1",
        "attempt_id": "work-1_a00",
    }

    accepted = RunEvent(
        **{
            **base,
            "validation_stage": "initial",
            "validation_codes": ("wave1_worker_output_json_invalid",),
            "response_shape": FinalResponseShape.PROSE,
        }
    )
    assert accepted.response_shape is FinalResponseShape.PROSE

    with pytest.raises(ValueError, match="journal_validation_response_shape_required"):
        RunEvent(**{**base, "validation_stage": "repair"})
    with pytest.raises(ValueError, match="journal_post_candidate_response_shape_unexpected"):
        RunEvent(
            **{
                **base,
                "validation_stage": "post_candidate",
                "validation_codes": ("submission_source_missing",),
                "response_shape": FinalResponseShape.JSON_OBJECT,
            }
        )
    with pytest.raises(ValueError, match="journal_post_candidate_codes_required"):
        RunEvent(**{**base, "validation_stage": "post_candidate"})
    with pytest.raises(ValueError, match="journal_validation_response_shape_unexpected"):
        RunEvent(
            **{
                **base,
                "category": RunEventCategory.NODE,
                "validation_stage": None,
                "response_shape": FinalResponseShape.JSON_OBJECT,
            }
        )


@pytest.mark.asyncio
async def test_v3_journal_retains_redacted_shape_and_post_candidate_facts(tmp_path: Path) -> None:
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
        validation_codes=("wave1_worker_output_json_invalid",),
        response_shape=FinalResponseShape.PROSE,
    )
    await recorder.record(
        category=RunEventCategory.VALIDATION,
        phase="wave1",
        work_id="work-1",
        attempt_id="work-1_a00",
        validation_stage="post_candidate",
        validation_codes=("submission_source_missing",),
    )

    inspection = await store.inspect(bundle_id=BUNDLE_ID)
    manifest = RunObservationManifest.model_validate_json(
        (bundle_root / "diagnostics" / "journal-manifest.json").read_bytes()
    )

    assert manifest.schema_version == 3
    assert inspection.summary is not None and inspection.summary.schema_version == 2
    assert [
        (event.validation_stage, event.response_shape, event.validation_codes) for event in inspection.events[1:]
    ] == [
        ("initial", FinalResponseShape.PROSE, ("wave1_worker_output_json_invalid",)),
        ("post_candidate", None, ("submission_source_missing",)),
    ]
    serialized = inspection.model_dump_json(exclude_none=True)
    assert "final prose body must never persist" not in serialized


@pytest.mark.asyncio
async def test_bundle_journal_is_contained_and_has_no_lifecycle_authority(tmp_path: Path) -> None:
    bundle_root = tmp_path / "workspace" / "deep-research" / BUNDLE_ID
    (bundle_root / "diagnostics").mkdir(mode=0o700, parents=True)
    os.chmod(bundle_root / "diagnostics", 0o700)
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID)

    view = await store.publish(_fact())
    inspection = await store.inspect(bundle_id=BUNDLE_ID)

    assert view.inspectability is ObservationInspectability.AVAILABLE
    assert inspection.inspectability is ObservationInspectability.AVAILABLE
    assert inspection.summary is not None
    assert inspection.summary.bundle_id == BUNDLE_ID
    assert inspection.summary.updated_at <= datetime.now(UTC)
    assert (bundle_root / "diagnostics" / "journal-manifest.json").is_file()
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
async def test_corrupt_bundle_journal_is_bounded_and_never_repaired_from_a_bundle(tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundle"
    (bundle_root / "diagnostics").mkdir(mode=0o700, parents=True)
    os.chmod(bundle_root / "diagnostics", 0o700)
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID)
    await store.publish(_fact())
    record = bundle_root / "diagnostics" / "journal-manifest.json"
    record.write_text("{not-json", encoding="utf-8")
    record.chmod(0o600)

    inspection = await store.inspect(bundle_id=BUNDLE_ID)

    assert inspection.inspectability is ObservationInspectability.UNAVAILABLE
    assert inspection.summary is None
    assert inspection.events == ()


@pytest.mark.asyncio
async def test_journal_cannot_recreate_a_lost_bundle(tmp_path: Path) -> None:
    bundle_root = tmp_path / "lost-bundle"
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID)
    recorder = RunObservationRecorder(store=store, bundle_id=BUNDLE_ID)

    view = await recorder.establish(generation=0, phase="bootstrap", durability="restart_durable")

    assert view.inspectability is ObservationInspectability.UNAVAILABLE
    assert not bundle_root.exists()


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
        response_shape=FinalResponseShape.JSON_OBJECT,
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
async def test_admitted_journal_retains_profile_only_on_matching_admission_and_summary(tmp_path: Path) -> None:
    """@impl REJ-006"""
    bundle_root = tmp_path / "bundle"
    (bundle_root / "diagnostics").mkdir(mode=0o700, parents=True)
    os.chmod(bundle_root / "diagnostics", 0o700)
    profile = _execution_profile()
    recorder = RunObservationRecorder(
        store=RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID),
        bundle_id=BUNDLE_ID,
        execution_profile=profile,
    )

    await recorder.establish(generation=0, phase="bootstrap", durability="restart_durable")
    await recorder.record(category=RunEventCategory.NODE, phase="bootstrap", attempt_id="bootstrap_a00")
    inspection = await RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID).inspect(bundle_id=BUNDLE_ID)

    assert inspection.summary is not None
    assert inspection.summary.execution_profile == profile
    assert inspection.events[0].category is RunEventCategory.ADMISSION
    assert inspection.events[0].execution_profile == profile
    assert all(event.execution_profile is None for event in inspection.events[1:])
    serialized = inspection.model_dump_json(exclude_none=True)
    assert "deepseek-v4-flash" in serialized
    for forbidden in ("api_key", "https://", "prompt", "provider_body", "demo-secret"):
        assert forbidden not in serialized


@pytest.mark.asyncio
async def test_profile_provenance_is_strict_and_legacy_or_non_demo_journals_do_not_invent_it(tmp_path: Path) -> None:
    """@impl REJ-006"""
    bundle_root = tmp_path / "bundle"
    (bundle_root / "diagnostics").mkdir(mode=0o700, parents=True)
    os.chmod(bundle_root / "diagnostics", 0o700)
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID)
    profile = _execution_profile()
    await RunObservationRecorder(store=store, bundle_id=BUNDLE_ID, execution_profile=profile).establish(
        generation=0,
        phase="bootstrap",
        durability="restart_durable",
    )

    conflicting = await RunObservationRecorder(
        store=RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID),
        bundle_id=BUNDLE_ID,
        execution_profile=_execution_profile(profile_id="openai-demo"),
    ).establish(generation=0, phase="bootstrap", durability="restart_durable")
    assert conflicting.inspectability is ObservationInspectability.UNAVAILABLE

    with pytest.raises(ValueError, match="journal_execution_profile_unexpected"):
        RunEvent(
            schema_version=2,
            sequence=2,
            timestamp=datetime.now(UTC),
            category=RunEventCategory.NODE,
            generation=0,
            phase="bootstrap",
            execution_profile=profile,
        )

    non_demo_root = tmp_path / "non-demo"
    (non_demo_root / "diagnostics").mkdir(mode=0o700, parents=True)
    os.chmod(non_demo_root / "diagnostics", 0o700)
    non_demo_store = RunObservationStore(bundle_root=non_demo_root, bundle_id=BUNDLE_ID)
    await RunObservationRecorder(store=non_demo_store, bundle_id=BUNDLE_ID).establish(
        generation=0,
        phase="bootstrap",
        durability="restart_durable",
    )
    non_demo = await non_demo_store.inspect(bundle_id=BUNDLE_ID)
    assert non_demo.summary is not None
    assert non_demo.summary.execution_profile is None
    assert non_demo.events[0].execution_profile is None


@pytest.mark.asyncio
async def test_journal_retains_only_valid_closed_budget_stop_reasons(tmp_path: Path) -> None:
    """@impl REJ-007"""

    bundle_root = tmp_path / "bundle"
    (bundle_root / "diagnostics").mkdir(mode=0o700, parents=True)
    os.chmod(bundle_root / "diagnostics", 0o700)
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID)
    recorder = RunObservationRecorder(store=store, bundle_id=BUNDLE_ID)
    await recorder.establish(generation=0, phase="bootstrap", durability="restart_durable")

    await recorder.record(
        category=RunEventCategory.MODEL_TOOL,
        phase="topic_planning",
        attempt_id="topic_planning_a00",
        outcome="failed",
        failure_category="budget.exhausted",
        worker_failure_category="agent_invocation",
        budget_stop_reason=BudgetStopReason.TOKEN_ADMISSION,
    )
    await recorder.record(
        category=RunEventCategory.MODEL_TOOL,
        phase="hitl1",
        attempt_id="hitl1_a00",
        outcome="failed",
        failure_category="provider.timeout",
        worker_failure_category="agent_invocation",
        provider_category="provider.timeout",
        budget_stop_reason=BudgetStopReason.BRIDGE_WALL_TIME,
    )
    await recorder.record(
        category=RunEventCategory.MODEL_TOOL,
        phase="wave0",
        attempt_id="wave0_a00",
        outcome="failed",
        failure_category="provider.unavailable",
        worker_failure_category="agent_invocation",
        provider_category="provider.unavailable",
        budget_stop_reason=BudgetStopReason.UNKNOWN,
    )
    inspection = await store.inspect(bundle_id=BUNDLE_ID)

    assert [event.budget_stop_reason for event in inspection.events] == [
        None,
        BudgetStopReason.TOKEN_ADMISSION,
        BudgetStopReason.BRIDGE_WALL_TIME,
    ]
    serialized = inspection.model_dump_json(exclude_none=True)
    assert '"token_admission"' in serialized
    assert '"bridge_wall_time"' in serialized
    assert "provider.unavailable" not in serialized

    invalid_event = {
        "schema_version": 2,
        "sequence": 4,
        "timestamp": datetime.now(UTC),
        "category": RunEventCategory.NODE,
        "generation": 0,
        "phase": "wave0",
        "outcome": "failed",
        "failure_category": "budget.exhausted",
        "budget_stop_reason": BudgetStopReason.TOTAL_TOKEN_BUDGET,
    }
    with pytest.raises(ValueError, match="journal_budget_stop_reason_unexpected"):
        RunEvent(**invalid_event)
    with pytest.raises(ValueError, match="journal_budget_stop_reason_failure_mismatch"):
        RunEvent(
            **{
                **invalid_event,
                "category": RunEventCategory.MODEL_TOOL,
                "budget_stop_reason": BudgetStopReason.BRIDGE_WALL_TIME,
            }
        )
    with pytest.raises(ValueError, match="journal_budget_stop_reason_failure_mismatch"):
        RunEvent(
            **{
                **invalid_event,
                "category": RunEventCategory.MODEL_TOOL,
                "failure_category": "provider.timeout",
            }
        )


@pytest.mark.asyncio
async def test_capacity_preserves_diagnostic_anchors_without_renumbering_retained_sequences(tmp_path: Path) -> None:
    """@impl REJ-003"""

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
        response_shape=FinalResponseShape.JSON_OBJECT,
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
    assert inspection.incomplete_reasons == (JournalIncompleteReason.CAPACITY,)
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
        response_shape=FinalResponseShape.JSON_OBJECT,
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

    observed_correlation = [
        (event.sequence, event.generation, event.validation_stage, event.validation_codes)
        for event in inspection.events
    ]
    assert observed_correlation == [
        (1, 0, None, ()),
        (2, 0, "initial", ("wave1_new_source_floor_not_met",)),
        (3, 1, None, ()),
    ]
    assert "raw validation detail must not persist" not in inspection.model_dump_json()


@pytest.mark.asyncio
@pytest.mark.parametrize("schema_version", (1, 2))
async def test_bundle_journal_marks_readable_legacy_correlation_incomplete_without_writing_or_upgrading(
    tmp_path: Path,
    schema_version: int,
) -> None:
    bundle_root = tmp_path / "bundle"
    journal_root = bundle_root / "diagnostics"
    journal_root.mkdir(mode=0o700, parents=True)
    os.chmod(journal_root, 0o700)
    now = datetime.now(UTC)
    manifest = RunObservationManifest(
        schema_version=schema_version,
        bundle_id=BUNDLE_ID,
        created_at=now,
        updated_at=now,
        retention_state=RetentionState.RETAINED,
        durability="restart_durable",
        summary_path="run-summary.json",
        events_path="diagnostics/events.jsonl",
        event_high_watermark=1 if schema_version == 2 else None,
    )
    summary = RunSummary(
        schema_version=schema_version,
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
        schema_version=schema_version,
        sequence=1,
        timestamp=now,
        category=RunEventCategory.ADMISSION,
        phase="bootstrap",
        generation=0 if schema_version == 2 else None,
    )
    for path, content in (
        (journal_root / "journal-manifest.json", manifest.model_dump_json().encode("utf-8")),
        (journal_root / "run-summary.json", summary.model_dump_json().encode("utf-8")),
        (journal_root / "events.jsonl", (event.model_dump_json() + "\n").encode("utf-8")),
    ):
        path.write_bytes(content)
        os.chmod(path, 0o600)
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID)
    recorder = RunObservationRecorder(store=store, bundle_id=BUNDLE_ID)
    before = {
        path.name: path.read_bytes()
        for path in (
            journal_root / "journal-manifest.json",
            journal_root / "run-summary.json",
            journal_root / "events.jsonl",
        )
    }

    await recorder.establish(generation=0, phase="bootstrap", durability="restart_durable")
    await recorder.record(category=RunEventCategory.NODE, phase="bootstrap", attempt_id="bootstrap_a00")

    inspection = await store.inspect(bundle_id=BUNDLE_ID)

    assert inspection.inspectability is ObservationInspectability.AVAILABLE
    assert inspection.journal_availability is JournalAvailability.INCOMPLETE
    assert inspection.summary is not None
    assert inspection.summary.journal_availability is JournalAvailability.INCOMPLETE
    assert inspection.incomplete_reasons == (JournalIncompleteReason.LEGACY, JournalIncompleteReason.PERSISTENCE)
    assert {
        path.name: path.read_bytes()
        for path in (
            journal_root / "journal-manifest.json",
            journal_root / "run-summary.json",
            journal_root / "events.jsonl",
        )
    } == before


@pytest.mark.asyncio
async def test_bundle_journal_marks_an_unexplained_sequence_gap_incomplete(tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundle"
    journal_root = bundle_root / "diagnostics"
    journal_root.mkdir(mode=0o700, parents=True)
    os.chmod(journal_root, 0o700)
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID)
    recorder = RunObservationRecorder(store=store, bundle_id=BUNDLE_ID)
    await recorder.establish(generation=0, phase="bootstrap", durability="restart_durable")
    await recorder.record(category=RunEventCategory.NODE, phase="bootstrap", attempt_id="bootstrap_a00")
    await recorder.record(category=RunEventCategory.NODE, phase="bootstrap", attempt_id="bootstrap_a01")

    event_path = journal_root / "events.jsonl"
    retained = event_path.read_text(encoding="utf-8").splitlines()
    event_path.write_text("\n".join((retained[0], retained[2])) + "\n", encoding="utf-8")
    os.chmod(event_path, 0o600)

    inspection = await store.inspect(bundle_id=BUNDLE_ID)

    assert inspection.inspectability is ObservationInspectability.AVAILABLE
    assert inspection.journal_availability is JournalAvailability.INCOMPLETE
    assert inspection.incomplete_reasons == (JournalIncompleteReason.SEQUENCE_GAP,)


@pytest.mark.asyncio
async def test_bundle_journal_serializes_concurrent_producers_with_stable_sequences(tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundle"
    (bundle_root / "diagnostics").mkdir(mode=0o700, parents=True)
    os.chmod(bundle_root / "diagnostics", 0o700)
    first_store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID, max_event_records=32)
    second_store = RunObservationStore(bundle_root=bundle_root, bundle_id=BUNDLE_ID, max_event_records=32)
    first_recorder = RunObservationRecorder(store=first_store, bundle_id=BUNDLE_ID)
    second_recorder = RunObservationRecorder(store=second_store, bundle_id=BUNDLE_ID)
    await first_recorder.establish(generation=0, phase="wave1", durability="restart_durable")
    await second_recorder.establish(generation=0, phase="wave1", durability="restart_durable")

    await asyncio.gather(
        *(
            (first_recorder if index % 2 else second_recorder).record(
                category=RunEventCategory.ATTEMPT,
                phase="wave1",
                work_id=f"work-{index}",
                attempt_id=f"work-{index}_a00",
            )
            for index in range(12)
        )
    )

    inspection = await first_store.inspect(bundle_id=BUNDLE_ID)

    assert [event.sequence for event in inspection.events] == list(range(1, 14))
    assert {event.attempt_id for event in inspection.events[1:]} == {f"work-{index}_a00" for index in range(12)}


@pytest.mark.asyncio
async def test_bundle_journal_marks_a_recovered_write_failure_incomplete(tmp_path: Path) -> None:
    """@impl REJ-003"""

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
    assert inspection.incomplete_reasons == (JournalIncompleteReason.PERSISTENCE,)
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
    assert inspection.incomplete_reasons == (JournalIncompleteReason.PERSISTENCE,)
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
    bundle = await lifecycle.start(
        scope=scope,
        request_text="Research journal lifetime.",
        implementation_mode="all_real",
    )
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
