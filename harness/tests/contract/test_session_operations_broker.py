"""Regression coverage that retired brokers cannot become Bundle authority.

@impl RES-001
@impl RES-002
@impl RES-003
@impl RES-006
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from deerflow_deep_research.domain.lifecycle import BundleAvailability, LifecycleAction
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.session_workbench import BundleWorkbench


def test_no_runtime_broker_or_historical_resolver_remains() -> None:
    assert importlib.util.find_spec("deerflow_deep_research.runtime.session_operations") is None
    assert importlib.util.find_spec("deerflow_deep_research.runtime.session_lifecycle_binding") is None


@pytest.mark.asyncio
async def test_only_scoped_bundle_state_can_authorize_a_local_operation(tmp_path: Path) -> None:
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=("alice", "thread-1"), request_text="research question")
    owner = BundleWorkbench(lifecycle=lifecycle, scope=("alice", "thread-1"))
    foreign = BundleWorkbench(lifecycle=lifecycle, scope=("mallory", "thread-2"))

    owner_view = await owner.status(bundle_id=bundle.bundle_id.value)
    foreign_view = await foreign.status(bundle_id=bundle.bundle_id.value)

    assert owner_view.action is LifecycleAction.STATUS
    assert owner_view.availability is BundleAvailability.AVAILABLE
    assert foreign_view.availability is BundleAvailability.UNAVAILABLE
    assert foreign_view.bundle_id is None
