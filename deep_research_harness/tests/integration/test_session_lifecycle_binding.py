"""Integration evidence for observation-only retained diagnostics.

@impl RES-002
@impl RES-003
@impl RES-006
@impl RES-005
@impl REG-014
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from deerflow_deep_research.domain.lifecycle import BundleAvailability
from deerflow_deep_research.domain.run_observation import ObservationInspectability, RecordBearingLifecycleFact
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.run_observation import RunObservationStore


@pytest.mark.asyncio
async def test_retained_observation_does_not_reauthorize_a_lost_bundle(tmp_path: Path) -> None:
    scope = ("alice", "thread-1")
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=scope, request_text="Investigate observation authority.")
    observations = RunObservationStore(retained_root=tmp_path / ".reports" / "deep-research-diagnostics")
    await observations.publish(
        RecordBearingLifecycleFact(
            bundle_id=bundle.bundle_id.value,
            action="status",
            status="active",
            phase="bootstrap",
            generation=0,
            durability="restart_durable",
        )
    )

    shutil.rmtree(lifecycle.private_root(bundle))

    assert (
        await lifecycle.status(scope=scope, bundle_id=bundle.bundle_id)
    ).availability is BundleAvailability.UNAVAILABLE
    retained = await observations.inspect(bundle_id=bundle.bundle_id.value)
    assert retained.inspectability is ObservationInspectability.AVAILABLE
    assert retained.bundle_id == bundle.bundle_id.value
