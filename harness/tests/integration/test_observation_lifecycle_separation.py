"""Integration proof that retained observations cannot recover a lost Bundle.

@impl RUS-007
@impl RES-001
@impl RES-002
@impl RES-003
@impl RES-006
"""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pytest

from deerflow_deep_research.domain.lifecycle import BundleAvailability, LifecycleAction
from deerflow_deep_research.domain.run_observation import ObservationInspectability, RecordBearingLifecycleFact
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.run_observation import RunObservationStore


@pytest.mark.asyncio
async def test_retained_observation_cannot_recover_a_deleted_bundle_or_block_a_fresh_start(tmp_path: Path) -> None:
    scope = ("alice", "conversation-1")
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=scope, request_text="Research the lifecycle model.")
    store = RunObservationStore(retained_root=tmp_path / ".reports" / "deep-research-diagnostics")
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
    observation = await store.inspect(bundle_id=bundle.bundle_id.value)
    replacement = await lifecycle.start(scope=scope, request_text="Start an independent run.")

    assert status.availability is BundleAvailability.UNAVAILABLE
    assert observation.inspectability is ObservationInspectability.AVAILABLE
    assert replacement.bundle_id != bundle.bundle_id
    assert importlib.util.find_spec("deerflow_deep_research.runtime.session_lifecycle_binding") is None
    assert importlib.util.find_spec("deerflow_deep_research.domain.session_lifecycle_binding") is None
    assert LifecycleAction.STATUS.value == "status"
