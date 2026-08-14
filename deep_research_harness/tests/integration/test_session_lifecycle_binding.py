"""Integration evidence for contained Journal diagnostics.

@impl DRH-006
@impl REJ-004
@impl RUI-003
@impl REG-014
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from deerflow_deep_research.domain.lifecycle import BundleAvailability
from deerflow_deep_research.domain.run_observation import RecordBearingLifecycleFact
from deerflow_deep_research.domain.session_workbench import WorkbenchAvailability
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.run_observation import RunObservationStore
from deerflow_deep_research.runtime.session_workbench import BundleWorkbench


@pytest.mark.asyncio
async def test_contained_journal_does_not_reauthorize_a_lost_bundle(tmp_path: Path) -> None:
    scope = ("alice", "thread-1")
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=scope, request_text="Investigate observation authority.")
    observations = RunObservationStore(
        bundle_root=lifecycle.private_root(bundle),
        bundle_id=bundle.bundle_id.value,
    )
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
    diagnosis = await BundleWorkbench(lifecycle=lifecycle, scope=scope).diagnosis(bundle_id=bundle.bundle_id.value)
    assert diagnosis.availability is WorkbenchAvailability.UNAVAILABLE
    assert not (tmp_path / ".reports").exists()
