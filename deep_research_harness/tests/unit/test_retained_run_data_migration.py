"""Fail-closed contract tests for the offline retained-data migration tool.

@impl REG-011
@impl DRH-002
@impl REJ-002
@impl RER-009
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from deerflow_deep_research.domain.run_experience import RunFailure
from deerflow_deep_research.domain.run_observation import RunEvent, RunObservationManifest
from scripts.retained_run_data_migration import (
    DEFAULT_INVENTORY_PATH,
    InventoryError,
    MigrationSource,
    RetainedDataMigrationError,
    load_inventory,
    render_report,
    run_inventory,
)

FIXTURE_ROOT = Path(__file__).parents[1] / "fixtures" / "retained_run_data"


def _digest(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _record(
    *,
    family: str = "graph_checkpoint",
    source_schema: int = 2,
    identity: str = "checkpoint-a",
    source: bytes = b'{"repair_counts":{}}',
    disposition: str = "migrate",
    output: bytes = b'{"schema_version":2}',
) -> dict[str, object]:
    record: dict[str, object] = {
        "family": family,
        "source_schema": source_schema,
        "identity": identity,
        "source_digest": _digest(source),
        "disposition": disposition,
    }
    if disposition == "migrate":
        record["output_digest"] = _digest(output)
    return record


def _write_manifest(tmp_path: Path, records: list[dict[str, object]]) -> Path:
    path = tmp_path / "inventory.json"
    path.write_text(
        json.dumps({"version": 1, "records": records}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def _source(record: dict[str, object], payload: bytes) -> MigrationSource:
    return MigrationSource(
        family=record["family"],
        schema=record["source_schema"],
        identity=record["identity"],
        payload=payload,
    )


def _fixture_payload(name: str) -> bytes:
    return (FIXTURE_ROOT / name).read_bytes()


def _fixture_mapping(name: str) -> dict[str, object]:
    return json.loads(_fixture_payload(name))


def test_checked_in_inventory_is_an_explicit_zero_record_dry_run(tmp_path: Path) -> None:
    inventory = load_inventory(DEFAULT_INVENTORY_PATH)

    report = run_inventory(inventory, sources=(), output_directory=tmp_path)

    assert inventory.version == 1
    assert inventory.records == ()
    assert report.registered == 0
    assert report.migrated == 0
    assert report.failed == 0
    assert report.unaccounted_supported == 0
    assert set(report.families) == {
        "bundle_state",
        "graph_checkpoint",
        "journal",
        "terminal_result",
    }
    expected_counts = {"registered": 0, "migrated": 0, "rejected": 0, "failed": 0}
    assert all(counts == expected_counts for counts in report.families.values())
    expected_report = _fixture_mapping("initial_zero_inventory_dry_run.json")
    assert json.loads(render_report(report)) == expected_report


def test_legacy_decoder_fixtures_are_accurate_pre_cutover_records() -> None:
    checkpoint = _fixture_mapping("graph_checkpoint_v2_repair_counts.json")
    bundle = _fixture_mapping("bundle_state_v4_repair_exhausted.json")
    journal_v2 = _fixture_mapping("journal_v2_complete.json")
    journal_v1 = _fixture_mapping("journal_v1_reject.json")
    terminal = _fixture_mapping("terminal_result_missing_diagnostic_location.json")

    assert checkpoint["schema_version"] == 2
    assert checkpoint["repair_counts"] == {"wave0": 2}
    assert bundle["terminal_reason"] == "repair_exhausted"
    assert RunObservationManifest.model_validate(journal_v2["manifest"]).schema_version == 2
    assert RunEvent.model_validate(journal_v2["events"][0]).schema_version == 2
    assert RunObservationManifest.model_validate(journal_v1["manifest"]).schema_version == 1
    assert RunEvent.model_validate(journal_v1["events"][0]).schema_version == 1
    assert "diagnostic_location" not in terminal


def test_runner_processes_only_registered_sources(tmp_path: Path) -> None:
    source = _fixture_payload("graph_checkpoint_v2_repair_counts.json")
    output = b'{"schema_version":3}'
    record = _record(source=source, output=output)
    inventory = load_inventory(_write_manifest(tmp_path, [record]))
    decoded: list[MigrationSource] = []

    report = run_inventory(
        inventory,
        sources=(_source(record, source),),
        output_directory=tmp_path / "output",
        decode=lambda current: decoded.append(current) or output,
    )

    assert decoded == [_source(record, source)]
    assert report.migrated == 1
    assert (tmp_path / "output" / "graph_checkpoint" / "checkpoint-a.json").read_bytes() == output


def test_unregistered_source_is_rejected_before_any_decoder_or_write(tmp_path: Path) -> None:
    source = _fixture_payload("graph_checkpoint_v2_repair_counts.json")
    output = b'{"schema_version":3}'
    record = _record(source=source, output=output)
    inventory = load_inventory(_write_manifest(tmp_path, [record]))
    decoded: list[MigrationSource] = []
    unregistered = MigrationSource(
        family="graph_checkpoint",
        schema=2,
        identity="checkpoint-unregistered",
        payload=source,
    )

    with pytest.raises(RetainedDataMigrationError, match="unregistered source"):
        run_inventory(
            inventory,
            sources=(_source(record, source), unregistered),
            output_directory=tmp_path / "output",
            decode=lambda current: decoded.append(current) or output,
        )

    assert decoded == []
    assert not (tmp_path / "output").exists()


def test_inventory_rejects_duplicate_record_identity(tmp_path: Path) -> None:
    record = _record()
    path = _write_manifest(tmp_path, [record, record.copy()])

    with pytest.raises(InventoryError, match="duplicate"):
        load_inventory(path)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("family", "unknown", "unknown family"),
        ("identity", "*", "opaque identity"),
        ("identity", "/host/private/run", "opaque identity"),
    ],
)
def test_inventory_rejects_unknown_or_selector_like_records(
    tmp_path: Path,
    field: str,
    value: object,
    message: str,
) -> None:
    record = _record()
    record[field] = value
    path = _write_manifest(tmp_path, [record])

    with pytest.raises(InventoryError, match=message):
        load_inventory(path)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda record: record.pop("source_digest"),
        lambda record: record.__setitem__("unexpected", "value"),
    ],
)
def test_inventory_requires_the_exact_record_shape(tmp_path: Path, mutate) -> None:
    record = _record()
    mutate(record)
    path = _write_manifest(tmp_path, [record])

    with pytest.raises(InventoryError, match="fields"):
        load_inventory(path)


def test_inventory_rejects_unsupported_source_schema(tmp_path: Path) -> None:
    path = _write_manifest(tmp_path, [_record(source_schema=9)])

    with pytest.raises(InventoryError, match="unsupported source schema"):
        load_inventory(path)


def test_runner_fails_closed_when_registered_source_digest_does_not_match(tmp_path: Path) -> None:
    expected_source = b'{"repair_counts":{}}'
    record = _record(source=expected_source)
    inventory = load_inventory(_write_manifest(tmp_path, [record]))

    with pytest.raises(RetainedDataMigrationError, match="digest mismatch"):
        run_inventory(
            inventory,
            sources=(_source(record, b'{"repair_counts":{"phase":1}}'),),
            output_directory=tmp_path / "output",
        )

    assert not (tmp_path / "output").exists()


def test_reject_disposition_never_creates_a_current_output(tmp_path: Path) -> None:
    source = b'{"diagnostic_location":null}'
    record = _record(
        family="terminal_result",
        source_schema=1,
        identity="terminal-a",
        source=source,
        disposition="reject",
    )
    inventory = load_inventory(_write_manifest(tmp_path, [record]))

    report = run_inventory(
        inventory,
        sources=(_source(record, source),),
        output_directory=tmp_path / "output",
    )

    assert report.rejected == 1
    assert report.migrated == 0
    assert not (tmp_path / "output").exists()


def test_failed_atomic_write_leaves_the_source_and_current_output_unchanged(tmp_path: Path) -> None:
    source = b'{"repair_counts":{}}'
    output = b'{"schema_version":2}'
    record = _record(source=source, output=output)
    inventory = load_inventory(_write_manifest(tmp_path, [record]))
    migration_source = _source(record, source)

    def fail_atomic_replace(staged: Path, destination: Path) -> None:
        raise OSError("simulated atomic write failure")

    with pytest.raises(RetainedDataMigrationError, match="atomic write"):
        run_inventory(
            inventory,
            sources=(migration_source,),
            output_directory=tmp_path / "output",
            decode=lambda current: output,
            atomic_replace=fail_atomic_replace,
        )

    assert migration_source.payload == source
    assert not (tmp_path / "output" / "graph_checkpoint" / "checkpoint-a.json").exists()
