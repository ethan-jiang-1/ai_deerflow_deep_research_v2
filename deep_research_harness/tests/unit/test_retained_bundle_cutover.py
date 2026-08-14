"""Cutover guards for Bundle State records retaining ``REPAIR_EXHAUSTED``.

@impl DRH-002
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from deerflow_deep_research.domain.lifecycle import BundleAvailability, ResultCode
from deerflow_deep_research.domain.state import BundleLocalState
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from scripts.retained_run_data_migration import (
    InventoryRecord,
    MigrationSource,
    RetainedDataInventory,
    RetainedDataMigrationError,
    decode_bundle_state,
    run_inventory,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "retained_run_data" / "bundle_state_v4_repair_exhausted.json"
_SCOPE = ("bundle-cutover-user", "bundle-cutover-thread")


def _fixture_mapping() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _digest(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _source(*, identity: str, payload: bytes) -> MigrationSource:
    return MigrationSource(family="bundle_state", schema=4, identity=identity, payload=payload)


def _record(*, source: MigrationSource, output: bytes) -> InventoryRecord:
    return InventoryRecord(
        family=source.family,
        source_schema=source.schema,
        identity=source.identity,
        source_digest=_digest(source.payload),
        disposition="migrate",
        output_digest=_digest(output),
    )


@pytest.mark.asyncio
async def test_unregistered_repair_exhausted_bundle_is_unavailable_before_status_projection(tmp_path: Path) -> None:
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(
        scope=_SCOPE,
        request_text="Reject the retired Bundle terminal.",
        implementation_mode="fixture",
    )
    legacy = _fixture_mapping()
    legacy["bundle_id"] = bundle.bundle_id.value
    state_path = lifecycle.private_root(bundle) / "state.json"
    source = json.dumps(legacy, sort_keys=True, separators=(",", ":")).encode("utf-8")
    state_path.write_bytes(source)

    result = await lifecycle.status(scope=_SCOPE, bundle_id=bundle.bundle_id)

    assert result.code is ResultCode.UNAVAILABLE
    assert result.availability is BundleAvailability.UNAVAILABLE
    assert result.bundle_id is None
    assert state_path.read_bytes() == source


def test_registered_terminal_migration_preserves_only_identity_and_terminal_status(tmp_path: Path) -> None:
    source_payload = FIXTURE.read_bytes()
    source = _source(identity=_fixture_mapping()["bundle_id"], payload=source_payload)
    output = decode_bundle_state(source)
    record = _record(source=source, output=output)

    report = run_inventory(
        RetainedDataInventory(version=1, records=(record,)),
        sources=(source,),
        output_directory=tmp_path / "output",
        decode=decode_bundle_state,
    )
    migrated = json.loads((tmp_path / "output" / "bundle_state" / f"{source.identity}.json").read_text())
    state = BundleLocalState.from_mapping(migrated)
    reloaded_after_restart = BundleLocalState.from_mapping(json.loads(json.dumps(migrated)))

    assert report.migrated == 1
    assert source.payload == source_payload
    assert state.bundle_id.value == source.identity
    assert state.terminal_status.value == "blocked"
    assert state.terminal_reason is None
    assert reloaded_after_restart == state
    assert "repair_exhausted" not in json.dumps(migrated, sort_keys=True)


@pytest.mark.parametrize(
    "mutate",
    (
        lambda value: value.__setitem__("phase_status", "in_progress"),
        lambda value: value.__setitem__("revision", -1),
    ),
)
def test_malformed_or_stale_terminal_migration_cannot_create_current_state(tmp_path: Path, mutate) -> None:
    legacy = _fixture_mapping()
    mutate(legacy)
    source = _source(
        identity=legacy["bundle_id"],
        payload=json.dumps(legacy, sort_keys=True, separators=(",", ":")).encode("utf-8"),
    )
    placeholder_output = b"{}"
    record = _record(source=source, output=placeholder_output)

    with pytest.raises(RetainedDataMigrationError, match="migration decoder failed for bundle_state"):
        run_inventory(
            RetainedDataInventory(version=1, records=(record,)),
            sources=(source,),
            output_directory=tmp_path / "output",
            decode=decode_bundle_state,
        )

    assert not (tmp_path / "output").exists()
    assert source.payload == json.dumps(legacy, sort_keys=True, separators=(",", ":")).encode("utf-8")


def test_replayed_or_atomic_failed_terminal_migration_cannot_replace_current_state(tmp_path: Path) -> None:
    source = _source(identity=_fixture_mapping()["bundle_id"], payload=FIXTURE.read_bytes())
    output = decode_bundle_state(source)
    record = _record(source=source, output=output)
    output_path = tmp_path / "output" / "bundle_state" / f"{source.identity}.json"
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(b'{"existing":"current"}')

    with pytest.raises(RetainedDataMigrationError, match="already exists"):
        run_inventory(
            RetainedDataInventory(version=1, records=(record,)),
            sources=(source,),
            output_directory=tmp_path / "output",
            decode=decode_bundle_state,
        )

    assert output_path.read_bytes() == b'{"existing":"current"}'
    assert source.payload == FIXTURE.read_bytes()
