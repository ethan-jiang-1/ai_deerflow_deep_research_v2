"""Integration evidence for direct BundleWorkbench lifecycle operations.

@impl RDO-001
@impl RDO-003
@impl RDO-004
@impl RDO-005
@impl RDO-006
@impl RDO-007
@impl DRH-006
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from deerflow_deep_research.domain.lifecycle import BundleAvailability, ImplementationMode, LifecycleStatus, ResultCode
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.session_workbench import BundleWorkbench


async def _workbench(tmp_path: Path) -> tuple[BundleWorkbench, BundleLifecycle, object]:
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(
        scope=("alice", "thread-1"),
        request_text="research question",
        implementation_mode=ImplementationMode.ALL_REAL,
    )
    await lifecycle.set_pending_request(bundle=bundle, request_id="drh_pending", suspension_cursor="start-message")
    return BundleWorkbench(lifecycle=lifecycle, scope=("alice", "thread-1")), lifecycle, bundle


@pytest.mark.asyncio
async def test_discovery_and_status_read_only_scoped_bundle_state(tmp_path: Path) -> None:
    workbench, _lifecycle, bundle = await _workbench(tmp_path)

    discovered = await workbench.discover()
    opened = await workbench.open(bundle_id=bundle.bundle_id.value)

    assert len(discovered) == 1
    assert discovered[0].bundle_id == bundle.bundle_id.value
    assert opened.availability is BundleAvailability.AVAILABLE
    assert opened.status is LifecycleStatus.SUSPENDED
    assert opened.request_id == "drh_pending"


@pytest.mark.asyncio
async def test_resume_revalidates_bundle_local_pending_request(tmp_path: Path) -> None:
    workbench, lifecycle, bundle = await _workbench(tmp_path)

    stale = await workbench.resume(
        bundle_id=bundle.bundle_id.value,
        expected_request_id="drh_stale",
        answer="ignored",
    )
    completed = await workbench.resume(
        bundle_id=bundle.bundle_id.value,
        expected_request_id="drh_pending",
        answer="accepted",
    )
    state = await lifecycle.read_state(bundle)

    assert stale.code is ResultCode.RESPONSE_MISMATCH
    assert completed.status is LifecycleStatus.COMPLETED
    assert state.terminal_status is LifecycleStatus.COMPLETED


@pytest.mark.asyncio
async def test_refine_preserves_pending_response_and_foreign_scope_fails_closed(tmp_path: Path) -> None:
    workbench, lifecycle, bundle = await _workbench(tmp_path)
    foreign = BundleWorkbench(lifecycle=lifecycle, scope=("mallory", "thread-2"))

    refined = await workbench.refine(
        bundle_id=bundle.bundle_id.value,
        text="add regulatory scope",
        operation_key="workbench-refine-1",
    )
    denied = await foreign.status(bundle_id=bundle.bundle_id.value)
    state = await lifecycle.read_state(bundle)

    assert refined.availability is BundleAvailability.AVAILABLE
    assert state.pending_request_id == "drh_pending"
    assert state.admitted_refinement is not None
    assert denied.availability is BundleAvailability.UNAVAILABLE
    assert denied.bundle_id is None


@pytest.mark.asyncio
async def test_workbench_refinement_uses_admission_not_the_state_wrapper(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workbench, lifecycle, bundle = await _workbench(tmp_path)

    async def legacy_state_wrapper(**_kwargs: object) -> object:
        raise AssertionError("workbench_called_removed_state_wrapper")

    monkeypatch.setattr(lifecycle, "refine", legacy_state_wrapper, raising=False)

    first = await workbench.refine(
        bundle_id=bundle.bundle_id.value,
        text="add regulatory scope",
        operation_key="workbench-refine-1",
    )
    replay = await workbench.refine(
        bundle_id=bundle.bundle_id.value,
        text="add regulatory scope",
        operation_key="workbench-refine-1",
    )
    conflict = await workbench.refine(
        bundle_id=bundle.bundle_id.value,
        text="different direction",
        operation_key="workbench-refine-2",
    )
    foreign = await BundleWorkbench(lifecycle=lifecycle, scope=("mallory", "thread-2")).refine(
        bundle_id=bundle.bundle_id.value,
        text="foreign direction",
        operation_key="foreign-refine-1",
    )
    state = await lifecycle.read_state(bundle)

    assert (first.code, replay.code, conflict.code) == (ResultCode.SUSPENDED,) * 3
    assert first.legal_next_action.value == "resume"
    assert replay == first
    assert conflict.refinement == first.refinement
    assert state.pending_request_id == "drh_pending"
    assert state.admitted_refinement is not None
    assert state.admitted_refinement.operation_key == "workbench-refine-1"
    assert foreign.availability is BundleAvailability.UNAVAILABLE
    assert foreign.bundle_id is None

    shutil.rmtree(lifecycle.private_root(bundle))
    unavailable = await workbench.refine(
        bundle_id=bundle.bundle_id.value,
        text="lost bundle direction",
        operation_key="lost-refine-1",
    )

    assert unavailable.availability is BundleAvailability.UNAVAILABLE
    assert unavailable.bundle_id is None


def test_lifecycle_has_no_state_only_refinement_wrapper() -> None:
    assert not hasattr(BundleLifecycle, "refine")


@pytest.mark.asyncio
async def test_deleted_bundle_is_unavailable_and_fresh_start_is_independent(tmp_path: Path) -> None:
    workbench, lifecycle, bundle = await _workbench(tmp_path)
    root = lifecycle.private_root(bundle)
    shutil.rmtree(root)

    unavailable = await workbench.status(bundle_id=bundle.bundle_id.value)
    fresh = await lifecycle.start(
        scope=("alice", "thread-1"),
        request_text="fresh question",
        implementation_mode=ImplementationMode.ALL_REAL,
    )

    assert unavailable.availability is BundleAvailability.UNAVAILABLE
    assert unavailable.bundle_id is None
    assert not root.exists()
    assert fresh.bundle_id != bundle.bundle_id
