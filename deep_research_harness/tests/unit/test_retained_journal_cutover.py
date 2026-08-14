"""Cutover guards for retained Journal v1/v2 records.

@impl REJ-002
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path

import pytest

from deerflow_deep_research.domain.run_observation import (
    JournalAvailability,
    ObservationInspectability,
    RunSummary,
)
from deerflow_deep_research.runtime.run_observation import RunObservationStore
from scripts.retained_run_data_migration import (
    InventoryRecord,
    MigrationSource,
    RetainedDataInventory,
    RetainedDataMigrationError,
    decode_journal,
    run_inventory,
)

FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "retained_run_data"
_BUNDLE_ID = "b_" + "A" * 43


def _fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def _digest(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _source(*, schema: int, payload: bytes) -> MigrationSource:
    return MigrationSource(family="journal", schema=schema, identity=_BUNDLE_ID, payload=payload)


def _record(*, source: MigrationSource, output: bytes, disposition: str = "migrate") -> InventoryRecord:
    return InventoryRecord(
        family=source.family,
        source_schema=source.schema,
        identity=source.identity,
        source_digest=_digest(source.payload),
        disposition=disposition,
        output_digest=_digest(output) if disposition == "migrate" else None,
    )


@pytest.mark.asyncio
async def test_registered_complete_v2_journal_migrates_without_inferred_v3_provenance(tmp_path: Path) -> None:
    source = _source(schema=2, payload=(FIXTURE_ROOT / "journal_v2_complete.json").read_bytes())
    output = decode_journal(source)
    record = _record(source=source, output=output)

    report = run_inventory(
        RetainedDataInventory(version=1, records=(record,)),
        sources=(source,),
        output_directory=tmp_path / "output",
        decode=decode_journal,
    )
    migrated = json.loads((tmp_path / "output" / "journal" / f"{_BUNDLE_ID}.json").read_text())

    assert report.migrated == 1
    assert migrated["manifest"]["schema_version"] == 3
    assert [event["schema_version"] for event in migrated["events"]] == [3]
    assert "response_shape" not in migrated["events"][0]
    assert "validation_stage" not in migrated["events"][0]
    assert source.payload == (FIXTURE_ROOT / "journal_v2_complete.json").read_bytes()

    current_root = tmp_path / "current-bundle" / "diagnostics"
    current_root.mkdir(mode=0o700, parents=True)
    manifest_path = current_root / "journal-manifest.json"
    events_path = current_root / "events.jsonl"
    manifest_path.write_text(json.dumps(migrated["manifest"]), encoding="utf-8")
    events_path.write_text("\n".join(json.dumps(event) for event in migrated["events"]) + "\n", encoding="utf-8")
    os.chmod(manifest_path, 0o600)
    os.chmod(events_path, 0o600)

    inspection = await RunObservationStore(
        bundle_root=current_root.parent,
        bundle_id=_BUNDLE_ID,
    ).inspect(bundle_id=_BUNDLE_ID)
    reloaded_after_restart = await RunObservationStore(
        bundle_root=current_root.parent,
        bundle_id=_BUNDLE_ID,
    ).inspect(bundle_id=_BUNDLE_ID)

    assert inspection.inspectability is ObservationInspectability.AVAILABLE
    assert inspection.journal_availability is JournalAvailability.COMPLETE
    assert [event.schema_version for event in inspection.events] == [3]
    assert reloaded_after_restart.events == inspection.events


def test_v1_journal_is_reject_only_and_creates_no_current_output(tmp_path: Path) -> None:
    source = _source(schema=1, payload=(FIXTURE_ROOT / "journal_v1_reject.json").read_bytes())
    record = _record(source=source, output=b"", disposition="reject")

    report = run_inventory(
        RetainedDataInventory(version=1, records=(record,)),
        sources=(source,),
        output_directory=tmp_path / "output",
    )

    assert report.rejected == 1
    assert not (tmp_path / "output").exists()


@pytest.mark.asyncio
async def test_partial_or_unregistered_old_journal_is_unavailable_before_append_or_projection(tmp_path: Path) -> None:
    payload = _fixture("journal_v2_complete.json")
    diagnostics = tmp_path / "diagnostics"
    diagnostics.mkdir(mode=0o700)
    manifest_path = diagnostics / "journal-manifest.json"
    events_path = diagnostics / "events.jsonl"
    manifest_path.write_text(json.dumps(payload["manifest"]), encoding="utf-8")
    events_path.write_text("", encoding="utf-8")
    os.chmod(manifest_path, 0o600)
    os.chmod(events_path, 0o600)
    before = (manifest_path.read_bytes(), events_path.read_bytes())
    store = RunObservationStore(bundle_root=tmp_path, bundle_id=_BUNDLE_ID)

    inspection = await store.inspect(bundle_id=_BUNDLE_ID)
    await store.record_event(
        bundle_id=_BUNDLE_ID,
        category="lifecycle",  # type: ignore[arg-type]
        phase="bootstrap",
        generation=0,
    )

    assert inspection.inspectability is ObservationInspectability.UNAVAILABLE
    assert (manifest_path.read_bytes(), events_path.read_bytes()) == before


def test_summary_v2_remains_current_and_unmodified_by_journal_cutover() -> None:
    summary = RunSummary(
        schema_version=2,
        bundle_id=_BUNDLE_ID,
        status="active",
        phase="bootstrap",
        generation=0,
        updated_at=datetime(2026, 8, 15, tzinfo=UTC),
        durability="restart_durable",
        journal_availability=JournalAvailability.COMPLETE,
    )

    assert summary.schema_version == 2


def test_mismatched_or_stale_v2_journal_cannot_migrate(tmp_path: Path) -> None:
    payload = _fixture("journal_v2_complete.json")
    payload["manifest"]["event_high_watermark"] = 2
    source = _source(schema=2, payload=json.dumps(payload, sort_keys=True).encode("utf-8"))
    record = _record(source=source, output=b"{}")

    with pytest.raises(RetainedDataMigrationError, match="migration decoder failed for journal"):
        run_inventory(
            RetainedDataInventory(version=1, records=(record,)),
            sources=(source,),
            output_directory=tmp_path / "output",
            decode=decode_journal,
        )

    assert not (tmp_path / "output").exists()
