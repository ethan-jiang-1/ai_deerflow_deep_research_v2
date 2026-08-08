"""Tests for bounded, non-authoritative retained Run observations.

@impl RUS-001
@impl RUS-002
@impl RUS-004
@impl RUS-007
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from deerflow_deep_research.domain.run_observation import (
    ObservationInspectability,
    RecordBearingLifecycleFact,
)
from deerflow_deep_research.runtime.run_observation import RunObservationStore

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
