"""Trusted-scope resolver evidence for direct Bundle operations.

@impl RDO-001
@impl RDO-002
@impl RDO-004
"""

from __future__ import annotations

from pathlib import Path

import pytest

from deerflow_deep_research.domain.lifecycle import BundleAvailability
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle, CurrentBundleHandle
from deerflow_deep_research.runtime.session_workbench import BundleWorkbench


@pytest.mark.asyncio
async def test_workbench_uses_only_trusted_scope_and_bundle_local_state(tmp_path: Path) -> None:
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    scope = ("alice", "thread-1")
    bundle = await lifecycle.start(scope=scope, request_text="research the market", implementation_mode="all_real")
    workbench = BundleWorkbench(
        lifecycle=lifecycle,
        scope=scope,
        current_bundle_handle=CurrentBundleHandle(bundle_id=bundle.bundle_id),
    )

    discovered = await workbench.discover()
    status = await workbench.result(bundle_id=bundle.bundle_id.value)

    assert discovered[0].bundle_id == bundle.bundle_id.value
    assert status.availability is BundleAvailability.AVAILABLE
    assert status.bundle_id == bundle.bundle_id.value


@pytest.mark.asyncio
async def test_workbench_hides_foreign_bundle_without_provider_or_index_fallback(tmp_path: Path) -> None:
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    foreign = await lifecycle.start(
        scope=("bob", "thread-2"), request_text="foreign research", implementation_mode="all_real"
    )
    workbench = BundleWorkbench(lifecycle=lifecycle, scope=("alice", "thread-1"))

    status = await workbench.result(bundle_id=foreign.bundle_id.value)

    assert status.availability is BundleAvailability.UNAVAILABLE
    assert status.bundle_id is None
