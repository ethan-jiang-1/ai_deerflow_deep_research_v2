"""Cross-instance refinement-admission evidence.

@impl DRH-005
@impl REG-021
"""

from __future__ import annotations

import asyncio
from dataclasses import replace
from pathlib import Path

import pytest

from deerflow_deep_research.domain.lifecycle import (
    AcceptedHumanResponse,
    LifecycleStatus,
    RefinementAdmissionDisposition,
    ResponseKind,
)
from deerflow_deep_research.domain.profile import ResearchProfile, profile_state_fields
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.request_bundle import RequestBundleStore

_SCOPE = ("alice", "thread-1")


def _profile() -> ResearchProfile:
    return ResearchProfile(
        depth="standard",
        audience="practitioner",
        format="detailed_report",
        cost_tolerance="moderate",
        time_budget="standard",
        must_answer=("Which constraints matter?",),
        scope_boundaries="Grid scale only.",
        custom_notes="Prefer primary sources.",
    )


def _response(request_id: str) -> AcceptedHumanResponse:
    return AcceptedHumanResponse(
        request_id=request_id,
        message_id="human-response-1",
        value="accepted",
        response_kind=ResponseKind.TEXT,
    )


@pytest.mark.asyncio
async def test_independent_lifecycles_admit_only_one_pending_direction(tmp_path: Path) -> None:
    """REG-021: the Bundle root, not one Python instance, serializes admission."""

    first = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await first.start(scope=_SCOPE, request_text="Research question")
    second = BundleLifecycle(workspace_host_path=tmp_path)

    admissions = await asyncio.gather(
        first.admit_refinement(
            scope=_SCOPE,
            bundle_id=bundle.bundle_id,
            text="Prioritize regulations.",
            operation_key="direction-one",
        ),
        second.admit_refinement(
            scope=_SCOPE,
            bundle_id=bundle.bundle_id,
            text="Prioritize cost.",
            operation_key="direction-two",
        ),
    )
    state = await first.read_state(bundle)

    assert {admission.disposition for admission in admissions} == {
        RefinementAdmissionDisposition.PENDING,
        RefinementAdmissionDisposition.CONFLICT,
    }
    assert state.admitted_refinement is not None
    assert state.admitted_refinement.operation_key in {"direction-one", "direction-two"}
    assert state.revision == 1


@pytest.mark.asyncio
async def test_response_and_direction_race_preserves_each_independent_fact(tmp_path: Path) -> None:
    """DRH-005: response consumption cannot discard an admitted direction."""

    first = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await first.start(scope=_SCOPE, request_text="Research question")
    await first.set_pending_request(bundle=bundle, request_id="request-1", suspension_cursor="start-message")
    second = BundleLifecycle(workspace_host_path=tmp_path)

    resumed, admission = await asyncio.gather(
        first.resume(scope=_SCOPE, bundle_id=bundle.bundle_id, response=_response("request-1")),
        second.admit_refinement(
            scope=_SCOPE,
            bundle_id=bundle.bundle_id,
            text="Add regulatory scope.",
            operation_key="direction-response-race",
        ),
    )
    state = await first.read_state(bundle)

    assert resumed.pending_request_id is None
    assert admission.disposition is RefinementAdmissionDisposition.PENDING
    assert state.pending_request_id is None
    assert state.admitted_refinement is not None
    assert state.admitted_refinement.operation_key == "direction-response-race"


@pytest.mark.asyncio
async def test_profile_projection_reduces_from_latest_state_after_direction_admission(tmp_path: Path) -> None:
    """REG-021: HITL1's permitted profile fields rebase without lifecycle authority."""

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=_SCOPE, request_text="Research question")
    request_store = RequestBundleStore(workspace_host_path=tmp_path, bundle=bundle)
    stale = await request_store.read_bundle_state()

    admission = await BundleLifecycle(workspace_host_path=tmp_path).admit_refinement(
        scope=_SCOPE,
        bundle_id=bundle.bundle_id,
        text="Prioritize regulations.",
        operation_key="direction-profile-race",
    )
    profile = _profile()
    profile_ref = await request_store.write_profile(profile)
    projected = await request_store.write_bundle_state(
        replace(stale, **profile_state_fields(profile, profile_ref)),
        expected_revision=stale.revision,
    )
    state = await lifecycle.read_state(bundle)

    assert admission.disposition is RefinementAdmissionDisposition.PENDING
    assert projected.profile_ref == profile_ref
    assert state.profile_ref == profile_ref
    assert state.admitted_refinement is not None
    assert state.admitted_refinement.operation_key == "direction-profile-race"


@pytest.mark.asyncio
async def test_cancel_and_direction_race_preserves_terminal_and_pending_facts(tmp_path: Path) -> None:
    """DRH-005: a stale terminal reducer cannot remove a queued direction."""

    first = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await first.start(scope=_SCOPE, request_text="Research question")
    second = BundleLifecycle(workspace_host_path=tmp_path)

    cancelled, admission = await asyncio.gather(
        first.cancel(scope=_SCOPE, bundle_id=bundle.bundle_id),
        second.admit_refinement(
            scope=_SCOPE,
            bundle_id=bundle.bundle_id,
            text="Prioritize regulations.",
            operation_key="direction-cancel-race",
        ),
    )
    state = await first.read_state(bundle)

    assert cancelled.terminal_status is LifecycleStatus.CANCELLED
    assert admission.disposition is RefinementAdmissionDisposition.PENDING
    assert state.terminal_status is LifecycleStatus.CANCELLED
    assert state.admitted_refinement is not None
    assert state.admitted_refinement.operation_key == "direction-cancel-race"
