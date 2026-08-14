#!/usr/bin/env python3
"""Fail-closed offline admission for explicitly registered retained Run data.

Production readers must not consult the inventory: this is an operator-invoked
migration evidence tool. Family decoders import a domain contract only when the
offline tool invokes them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final

DEFAULT_INVENTORY_PATH: Final = Path(__file__).with_name("retained_run_data_inventory.json")
INVENTORY_VERSION: Final = 1
_IDENTITY_RE: Final = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}\Z")
_DIGEST_RE: Final = re.compile(r"sha256:[0-9a-f]{64}\Z")

# Each source schema is accepted only by the offline decoder for its family.  The
# current runtime readers intentionally have no entry in this table.
SUPPORTED_SOURCE_SCHEMAS: Final[Mapping[str, frozenset[int]]] = {
    "bundle_state": frozenset({4}),
    "graph_checkpoint": frozenset({2}),
    "journal": frozenset({2}),
    "terminal_result": frozenset({1}),
}
READER_WRITER_MATRIX: Final[Mapping[str, Mapping[str, str]]] = {
    "bundle_state": {
        "offline_reader": "registered v4 REPAIR_EXHAUSTED terminal only",
        "runtime_reader": "current Bundle State only",
        "current_writer": "current Bundle State without REPAIR_EXHAUSTED",
    },
    "graph_checkpoint": {
        "offline_reader": "registered v2 checkpoint with repair_counts only",
        "runtime_reader": "current checkpoint without repair_counts",
        "current_writer": "current checkpoint without repair_counts",
    },
    "journal": {
        "offline_reader": "registered complete v2 manifest and events only",
        "runtime_reader": "v3 manifest and events only",
        "current_writer": "v3 manifest and events; Summary v2 unchanged",
    },
    "terminal_result": {
        "offline_reader": "registered missing-location result for rejection only",
        "runtime_reader": "result with explicit diagnostic_location only",
        "current_writer": "explicit bundle_journal or unavailable location",
    },
}


class InventoryError(ValueError):
    """Raised when a source-controlled inventory fails structural admission."""


class RetainedDataMigrationError(RuntimeError):
    """Raised when an explicitly registered source cannot migrate safely."""


@dataclass(frozen=True, slots=True)
class InventoryRecord:
    family: str
    source_schema: int
    identity: str
    source_digest: str
    disposition: str
    output_digest: str | None

    @property
    def key(self) -> tuple[str, int, str]:
        return (self.family, self.source_schema, self.identity)


@dataclass(frozen=True, slots=True)
class RetainedDataInventory:
    version: int
    records: tuple[InventoryRecord, ...]


@dataclass(frozen=True, slots=True)
class MigrationSource:
    family: str
    schema: int
    identity: str
    payload: bytes

    @property
    def key(self) -> tuple[str, int, str]:
        return (self.family, self.schema, self.identity)


@dataclass(frozen=True, slots=True)
class MigrationReport:
    registered: int
    migrated: int
    rejected: int
    failed: int
    unaccounted_supported: int
    families: Mapping[str, Mapping[str, int]]
    matrix: Mapping[str, Mapping[str, str]]

    def as_dict(self) -> dict[str, object]:
        return {
            "families": {family: dict(counts) for family, counts in self.families.items()},
            "matrix": {family: dict(entry) for family, entry in self.matrix.items()},
            "totals": {
                "failed": self.failed,
                "migrated": self.migrated,
                "rejected": self.rejected,
                "registered": self.registered,
                "unaccounted_supported": self.unaccounted_supported,
            },
        }


def sha256_digest(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def load_inventory(path: Path) -> RetainedDataInventory:
    """Load the exact, versioned inventory shape without any source discovery."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InventoryError(f"unable to read inventory: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InventoryError(f"inventory is not valid JSON: {path}") from exc

    if not isinstance(raw, dict) or set(raw) != {"version", "records"}:
        raise InventoryError("inventory must contain exactly version and records")
    version = raw["version"]
    records = raw["records"]
    if isinstance(version, bool) or version != INVENTORY_VERSION:
        raise InventoryError(f"unsupported inventory version: {version!r}")
    if not isinstance(records, list):
        raise InventoryError("inventory records must be a list")

    parsed = tuple(_parse_record(record, index) for index, record in enumerate(records))
    keys = [record.key for record in parsed]
    if len(keys) != len(set(keys)):
        raise InventoryError("duplicate family/schema/opaque identity record")
    return RetainedDataInventory(version=version, records=tuple(sorted(parsed, key=lambda record: record.key)))


def run_inventory(
    inventory: RetainedDataInventory,
    *,
    sources: Iterable[MigrationSource],
    output_directory: Path,
    decode: Callable[[MigrationSource], bytes] | None = None,
    atomic_replace: Callable[[Path, Path], None] = os.replace,
) -> MigrationReport:
    """Validate exact registered sources and write only verified current outputs.

    The caller supplies every source explicitly.  This function never walks a local
    directory, interprets an identity as a path, or mutates a supplied source.
    """
    source_by_key = _index_sources(sources)
    record_by_key = {record.key: record for record in inventory.records}
    source_keys = set(source_by_key)
    record_keys = set(record_by_key)
    unregistered = source_keys - record_keys
    missing = record_keys - source_keys
    if unregistered:
        raise RetainedDataMigrationError("unregistered source is not supported")
    if missing:
        raise RetainedDataMigrationError("registered source was not supplied")

    family_counts = {
        family: {"registered": 0, "migrated": 0, "rejected": 0, "failed": 0}
        for family in sorted(SUPPORTED_SOURCE_SCHEMAS)
    }
    migrated = 0
    rejected = 0
    for record in inventory.records:
        family_counts[record.family]["registered"] += 1
        source = source_by_key[record.key]
        _validate_source(record, source)
        if record.disposition == "reject":
            family_counts[record.family]["rejected"] += 1
            rejected += 1
            continue
        if decode is None:
            raise RetainedDataMigrationError("a migration decoder is required for migrate records")
        try:
            output = decode(source)
        except Exception as exc:  # Decoder implementations are family-specific.
            raise RetainedDataMigrationError(f"migration decoder failed for {record.family}/{record.identity}") from exc
        if not isinstance(output, bytes):
            raise RetainedDataMigrationError("migration decoder must return bytes")
        if sha256_digest(output) != record.output_digest:
            raise RetainedDataMigrationError("output digest mismatch")
        destination = output_directory / record.family / f"{record.identity}.json"
        _atomic_write(destination, output, atomic_replace=atomic_replace)
        family_counts[record.family]["migrated"] += 1
        migrated += 1

    return MigrationReport(
        registered=len(inventory.records),
        migrated=migrated,
        rejected=rejected,
        failed=0,
        unaccounted_supported=0,
        families=family_counts,
        matrix={family: READER_WRITER_MATRIX[family] for family in sorted(READER_WRITER_MATRIX)},
    )


def render_report(report: MigrationReport) -> str:
    """Render the stable report for checked-in and operator dry-run evidence."""
    return json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n"


def decode_graph_checkpoint(source: MigrationSource) -> bytes:
    """Migrate one registered schema-2 checkpoint without recreating repair facts."""
    if source.family != "graph_checkpoint" or source.schema != 2:
        raise RetainedDataMigrationError("graph checkpoint source schema is unsupported")
    try:
        legacy = json.loads(source.payload)
    except (TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RetainedDataMigrationError("graph checkpoint source is not valid JSON") from exc
    if not isinstance(legacy, dict) or legacy.get("schema_version") != 2:
        raise RetainedDataMigrationError("graph checkpoint source schema is unsupported")
    repair_counts = legacy.get("repair_counts")
    if not isinstance(repair_counts, dict) or any(
        not isinstance(phase, str) or not phase or isinstance(count, bool) or not isinstance(count, int) or count < 0
        for phase, count in repair_counts.items()
    ):
        raise RetainedDataMigrationError("graph checkpoint repair_counts is invalid")

    migrated = dict(legacy)
    migrated.pop("repair_counts")
    migrated["schema_version"] = 3
    for field_name in ("gate_attempts_by_phase", "repair_budget_by_phase"):
        if migrated.get(field_name, {}) != legacy.get(field_name, {}):
            raise RetainedDataMigrationError("graph checkpoint repair authority changed")
    try:
        from deerflow_deep_research.domain.state import serialize_research_state, validate_research_state

        validate_research_state(migrated)
        return serialize_research_state(migrated).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise RetainedDataMigrationError("graph checkpoint migration validation failed") from exc


def decode_bundle_state(source: MigrationSource) -> bytes:
    """Migrate one registered retired Bundle terminal without a replacement reason."""
    if source.family != "bundle_state" or source.schema != 4:
        raise RetainedDataMigrationError("bundle state source schema is unsupported")
    try:
        legacy = json.loads(source.payload)
    except (TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RetainedDataMigrationError("bundle state source is not valid JSON") from exc
    if not isinstance(legacy, dict) or legacy.get("schema_version") != 4:
        raise RetainedDataMigrationError("bundle state source schema is unsupported")
    if legacy.get("bundle_id") != source.identity:
        raise RetainedDataMigrationError("bundle state identity is incompatible")
    if (
        legacy.get("phase_status") != "terminal"
        or legacy.get("terminal_status") != "blocked"
        or legacy.get("terminal_reason") != "repair_exhausted"
    ):
        raise RetainedDataMigrationError("bundle state retired terminal is invalid")

    migrated = dict(legacy)
    migrated["terminal_reason"] = None
    try:
        from deerflow_deep_research.domain.state import BUNDLE_STATE_SCHEMA_VERSION, BundleLocalState

        migrated["schema_version"] = BUNDLE_STATE_SCHEMA_VERSION
        current = BundleLocalState.from_mapping(migrated)
    except (TypeError, ValueError) as exc:
        raise RetainedDataMigrationError("bundle state migration validation failed") from exc
    if current.bundle_id.value != source.identity or current.terminal_status.value != "blocked":
        raise RetainedDataMigrationError("bundle state migration changed terminal truth")
    if current.terminal_reason is not None:
        raise RetainedDataMigrationError("bundle state migration retained retired reason")
    return json.dumps(current.to_mapping(), sort_keys=True, separators=(",", ":")).encode("utf-8")


def decode_journal(source: MigrationSource) -> bytes:
    """Migrate one complete registered v2 Journal without adding v3-only facts."""
    if source.family != "journal" or source.schema != 2:
        raise RetainedDataMigrationError("journal source schema is unsupported")
    try:
        legacy = json.loads(source.payload)
    except (TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RetainedDataMigrationError("journal source is not valid JSON") from exc
    if not isinstance(legacy, dict) or set(legacy) != {"manifest", "events"}:
        raise RetainedDataMigrationError("journal source shape is invalid")
    manifest = legacy["manifest"]
    events = legacy["events"]
    if not isinstance(manifest, dict) or not isinstance(events, list):
        raise RetainedDataMigrationError("journal source shape is invalid")
    if manifest.get("schema_version") != 2 or manifest.get("bundle_id") != source.identity:
        raise RetainedDataMigrationError("journal source schema or identity is unsupported")
    watermark = manifest.get("event_high_watermark")
    if isinstance(watermark, bool) or not isinstance(watermark, int) or watermark < 1:
        raise RetainedDataMigrationError("journal source watermark is invalid")
    if manifest.get("dropped_event_count", 0) != 0 or manifest.get("persistence_failure_count", 0) != 0:
        raise RetainedDataMigrationError("journal source is incomplete")
    if any(not isinstance(event, dict) or event.get("schema_version") != 2 for event in events):
        raise RetainedDataMigrationError("journal event schema is unsupported")
    sequences = tuple(event.get("sequence") for event in events)
    if sequences != tuple(range(1, watermark + 1)):
        raise RetainedDataMigrationError("journal event sequence is incomplete")

    migrated_manifest = {**manifest, "schema_version": 3}
    migrated_events = [{**event, "schema_version": 3} for event in events]
    try:
        from deerflow_deep_research.domain.run_observation import RunEvent, RunObservationManifest

        RunObservationManifest.model_validate(migrated_manifest)
        for event in migrated_events:
            RunEvent.model_validate(event)
    except (TypeError, ValueError) as exc:
        raise RetainedDataMigrationError("journal migration validation failed") from exc
    return json.dumps(
        {"events": migrated_events, "manifest": migrated_manifest},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _parse_record(raw: object, index: int) -> InventoryRecord:
    if not isinstance(raw, dict):
        raise InventoryError(f"record {index} must be an object")
    disposition = raw.get("disposition")
    if disposition == "migrate":
        expected_fields = {"family", "source_schema", "identity", "source_digest", "disposition", "output_digest"}
    elif disposition == "reject":
        expected_fields = {"family", "source_schema", "identity", "source_digest", "disposition"}
    else:
        raise InventoryError(f"record {index} has unsupported disposition")
    if set(raw) != expected_fields:
        raise InventoryError(f"record {index} has invalid fields")

    family = raw["family"]
    schema = raw["source_schema"]
    identity = raw["identity"]
    source_digest = raw["source_digest"]
    output_digest = raw.get("output_digest")
    if not isinstance(family, str) or family not in SUPPORTED_SOURCE_SCHEMAS:
        raise InventoryError("unknown family")
    if isinstance(schema, bool) or not isinstance(schema, int) or schema not in SUPPORTED_SOURCE_SCHEMAS[family]:
        raise InventoryError("unsupported source schema")
    if not isinstance(identity, str) or not _IDENTITY_RE.fullmatch(identity):
        raise InventoryError("identity must be an opaque identity, not a selector or host path")
    if not isinstance(source_digest, str) or not _DIGEST_RE.fullmatch(source_digest):
        raise InventoryError("source digest must be sha256")
    if disposition == "migrate" and (not isinstance(output_digest, str) or not _DIGEST_RE.fullmatch(output_digest)):
        raise InventoryError("output digest must be sha256")
    return InventoryRecord(
        family=family,
        source_schema=schema,
        identity=identity,
        source_digest=source_digest,
        disposition=disposition,
        output_digest=output_digest if isinstance(output_digest, str) else None,
    )


def _index_sources(sources: Iterable[MigrationSource]) -> dict[tuple[str, int, str], MigrationSource]:
    indexed: dict[tuple[str, int, str], MigrationSource] = {}
    for source in sources:
        if not isinstance(source, MigrationSource):
            raise RetainedDataMigrationError("sources must be explicit MigrationSource records")
        if source.key in indexed:
            raise RetainedDataMigrationError("duplicate supplied source")
        indexed[source.key] = source
    return indexed


def _validate_source(record: InventoryRecord, source: MigrationSource) -> None:
    if not isinstance(source.payload, bytes):
        raise RetainedDataMigrationError("source payload must be bytes")
    if sha256_digest(source.payload) != record.source_digest:
        raise RetainedDataMigrationError("source digest mismatch")


def _atomic_write(
    destination: Path,
    output: bytes,
    *,
    atomic_replace: Callable[[Path, Path], None],
) -> None:
    if destination.exists():
        raise RetainedDataMigrationError("current output already exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staged_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as staged:
            staged.write(output)
            staged.flush()
            os.fsync(staged.fileno())
            staged_path = Path(staged.name)
        atomic_replace(staged_path, destination)
    except OSError as exc:
        raise RetainedDataMigrationError("atomic write failed") from exc
    finally:
        if staged_path is not None and staged_path.exists():
            staged_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY_PATH)
    parser.add_argument("--report", type=Path)
    arguments = parser.parse_args()
    try:
        report = run_inventory(
            load_inventory(arguments.inventory),
            sources=(),
            output_directory=Path(".retained-run-data-output"),
        )
    except (InventoryError, RetainedDataMigrationError) as exc:
        parser.error(str(exc))
    rendered = render_report(report)
    if arguments.report is not None:
        arguments.report.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
