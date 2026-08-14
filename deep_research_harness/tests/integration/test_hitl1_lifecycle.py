"""Bundle-local HITL lifecycle integration tests.

@impl DRH-005
@impl HIN-015
@impl REG-003
@impl REG-020
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from deerflow_deep_research.domain.lifecycle import (
    AcceptedHumanResponse,
    LifecycleAction,
    ResponseKind,
)
from deerflow_deep_research.domain.state import BUNDLE_STATE_SCHEMA_VERSION
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle, BundleLifecycleError, CurrentBundleHandle


@pytest.mark.asyncio
async def test_bundle_local_pending_hitl_survives_a_fresh_lifecycle_instance(tmp_path: Path) -> None:
    """A restart reads one pending request from the Bundle, not an external saver."""
    scope = ("alice", "thread-1")
    started = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await started.start(scope=scope, request_text="Research storage options", start_message_id="human-start")
    await started.set_pending_request(bundle=bundle, request_id="hitl-1", suspension_cursor="human-start")

    restarted = BundleLifecycle(workspace_host_path=tmp_path)
    resolved = await restarted.resolve_active(scope=scope, handle=CurrentBundleHandle(bundle.bundle_id))

    assert resolved == bundle
    state = await restarted.read_state(bundle)
    assert state.pending_request_id == "hitl-1"
    assert state.pending_cursor == "human-start"
    projected = restarted.result_for_state(action=LifecycleAction.STATUS, bundle=bundle, state=state)
    assert projected.status == "suspended"
    assert projected.request_id == "hitl-1"


@pytest.mark.asyncio
@pytest.mark.parametrize("scenario_case_id", ("bundle-lifecycle-control",))
async def test_bundle_lifecycle_state_survives_restart_without_external_checkpoint_control(
    scenario_case_id: str,
    tmp_path: Path,
) -> None:
    """The reusable scenario reads only the selected Bundle's durable State."""
    assert scenario_case_id == "bundle-lifecycle-control"
    scope = ("alice", "bundle-lifecycle-control")
    started = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await started.start(scope=scope, request_text="Research storage options", start_message_id="human-start")
    await started.set_pending_request(bundle=bundle, request_id="hitl-1", suspension_cursor="human-start")

    restarted = BundleLifecycle(workspace_host_path=tmp_path)
    state = await restarted.read_state(bundle)
    result = restarted.result_for_state(action=LifecycleAction.STATUS, bundle=bundle, state=state)

    assert result.bundle_id == bundle.bundle_id.value
    assert result.status == "suspended"
    assert state.pending_request_id == "hitl-1"
    assert state.schema_version == BUNDLE_STATE_SCHEMA_VERSION


@pytest.mark.asyncio
async def test_refinement_preserves_pending_response_and_correlated_resume_is_idempotent(tmp_path: Path) -> None:
    scope = ("alice", "thread-1")
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=scope, request_text="Research storage options")
    waiting = await lifecycle.set_pending_request(bundle=bundle, request_id="hitl-1")

    refined = (
        await lifecycle.admit_refinement(
            scope=scope,
            text="Prioritize primary sources",
            operation_key="operation-refine",
            bundle_id=bundle.bundle_id,
        )
    ).state
    assert refined.pending_request_id == "hitl-1"
    assert refined.admitted_refinement is not None
    assert refined.admitted_refinement.text == "Prioritize primary sources"
    assert refined.admitted_refinement.operation_key == "operation-refine"

    response = AcceptedHumanResponse(
        request_id="hitl-1",
        message_id="human-answer",
        value="Focus on costs",
        response_kind=ResponseKind.TEXT,
    )
    resumed = await lifecycle.resume(scope=scope, response=response, bundle_id=bundle.bundle_id)
    assert resumed.pending_request_id is None
    assert resumed.admitted_refinement == refined.admitted_refinement
    replay = await lifecycle.resume(scope=scope, response=response, bundle_id=bundle.bundle_id)
    assert replay == resumed
    assert replay.revision > waiting.revision


@pytest.mark.asyncio
async def test_refinement_of_an_ended_bundle_requires_explicit_target_and_reopens_only_that_bundle(
    tmp_path: Path,
) -> None:
    scope = ("alice", "thread-1")
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    ended = await lifecycle.start(scope=scope, request_text="Original question")
    await lifecycle.end(bundle=ended)

    with pytest.raises(BundleLifecycleError, match="explicit_bundle_id_required"):
        await lifecycle.admit_refinement(
            scope=scope,
            text="Add a comparison",
            operation_key="operation-ended-handle",
            handle=CurrentBundleHandle(ended.bundle_id),
        )

    admitted = (
        await lifecycle.admit_refinement(
            scope=scope,
            text="Add a comparison",
            operation_key="operation-ended",
            bundle_id=ended.bundle_id,
        )
    ).state
    assert not admitted.is_active
    assert admitted.refinement_round == 0
    assert admitted.admitted_refinement is not None
    assert await lifecycle.resolve_active(scope=scope, handle=None) is None


@pytest.mark.asyncio
async def test_lost_bundle_cannot_supply_pending_input_or_be_reactivated(tmp_path: Path) -> None:
    scope = ("alice", "thread-1")
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=scope, request_text="Question")
    await lifecycle.set_pending_request(bundle=bundle, request_id="hitl-1")
    root = lifecycle.private_root(bundle)

    shutil.rmtree(root)
    status = await lifecycle.status(scope=scope, bundle_id=bundle.bundle_id)
    assert status.code == "unavailable"
    assert status.availability == "unavailable"
    with pytest.raises(BundleLifecycleError, match="bundle_unavailable"):
        await lifecycle.admit_refinement(
            scope=scope,
            text="Recover it",
            operation_key="operation-lost",
            bundle_id=bundle.bundle_id,
        )
