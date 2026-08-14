"""Integration proof that a contained Journal cannot recover a lost Bundle.

@impl DRH-006
@impl REJ-004
@impl PRS-006
@impl RUI-003
"""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pytest

from deerflow_deep_research.domain.lifecycle import BundleAvailability, LifecycleAction
from deerflow_deep_research.domain.run_observation import RecordBearingLifecycleFact
from deerflow_deep_research.domain.session_workbench import WorkbenchAvailability
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.run_observation import RunObservationStore
from deerflow_deep_research.runtime.session_workbench import BundleWorkbench


@pytest.mark.asyncio
async def test_contained_journal_is_unavailable_after_bundle_loss_and_cannot_block_a_fresh_start(
    tmp_path: Path,
) -> None:
    scope = ("alice", "conversation-1")
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=scope, request_text="Research the lifecycle model.")
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

    shutil.rmtree(lifecycle.private_root(bundle))

    status = await lifecycle.status(scope=scope, bundle_id=bundle.bundle_id)
    observation = await BundleWorkbench(lifecycle=lifecycle, scope=scope).diagnosis(bundle_id=bundle.bundle_id.value)
    replacement = await lifecycle.start(scope=scope, request_text="Start an independent run.")

    assert status.availability is BundleAvailability.UNAVAILABLE
    assert observation.availability is WorkbenchAvailability.UNAVAILABLE
    assert replacement.bundle_id != bundle.bundle_id
    assert not (tmp_path / ".reports").exists()
    assert importlib.util.find_spec("deerflow_deep_research.runtime.session_lifecycle_binding") is None
    assert importlib.util.find_spec("deerflow_deep_research.domain.session_lifecycle_binding") is None
    assert LifecycleAction.STATUS.value == "status"
