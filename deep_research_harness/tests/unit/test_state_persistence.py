"""Typed ResearchState persistence and structure contracts (REG-005, REG-006, REG-011)."""

from __future__ import annotations

import importlib
import shutil

import pytest

from deerflow_deep_research.domain.bundle import BundleId
from deerflow_deep_research.domain.lifecycle import ImplementationMode, LifecycleAction, LifecycleStatus
from deerflow_deep_research.domain.run_experience import FailureCertainty, RunFailureCode, TerminalIncidentProjection
from deerflow_deep_research.domain.state import (
    MAX_CHECKPOINT_STATE_BYTES,
    RESEARCH_STATE_SCHEMA_VERSION,
    BundleLocalState,
    PhaseStatus,
    ResearchGraphState,
    ResearchState,
    project_lifecycle_status,
    serialize_research_state,
    validate_research_state,
)
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle, BundleLifecycleError, BundleStateStore

BUNDLE_ID = "b_" + "A" * 43


async def test_blocked_graph_incident_survives_bundle_state_sync_reload_and_projection(tmp_path) -> None:
    """REG-013: the shared lifecycle result exposes the bounded terminal cause."""
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=("alice", "thread-1"), request_text="Diagnose a blocked wave.")
    incident = TerminalIncidentProjection(
        code=RunFailureCode.RESEARCH_BLOCKED,
        phase="wave1",
        certainty=FailureCertainty.DIRECT,
    )
    state = await lifecycle.sync_graph_progress(
        bundle=bundle,
        values={
            "phase": "wave1",
            "phase_status": "terminal",
            "terminal_status": "blocked",
            "terminal_reason": "gate_blocked",
            "latest_incident": incident.model_dump(mode="json", exclude_none=True),
            "generation": 0,
            "execution_trace": ("bootstrap", "wave0", "wave1"),
        },
        pending=None,
    )

    assert state.latest_incident == incident
    reloaded = await lifecycle.read_state(bundle)
    assert reloaded.latest_incident == incident
    result = lifecycle.result_for_state(
        action=LifecycleAction.STATUS,
        bundle=bundle,
        state=reloaded,
    )

    assert result.status is LifecycleStatus.BLOCKED
    assert result.terminal_incident == incident


async def test_selected_implementation_mode_survives_bundle_reload_and_projection(tmp_path) -> None:
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(
        scope=("alice", "thread-1"),
        request_text="Verify fixture graph composition.",
        implementation_mode=ImplementationMode.FIXTURE,
    )

    reloaded = await lifecycle.read_state(bundle)
    result = lifecycle.result_for_state(
        action=LifecycleAction.STATUS,
        bundle=bundle,
        state=reloaded,
    )

    assert reloaded.implementation_mode is ImplementationMode.FIXTURE
    assert result.implementation_mode is ImplementationMode.FIXTURE


def test_bundle_local_waiting_state_is_active_until_a_terminal_round_is_recorded() -> None:
    waiting = BundleLocalState(bundle_id=BundleId("b_" + "A" * 43), waiting_for="hitl1")
    assert waiting.is_active

    terminal = BundleLocalState(
        bundle_id=BundleId("b_" + "A" * 43),
        phase_status="terminal",
        terminal_status="completed",
    )
    assert not terminal.is_active


async def test_bundle_state_store_rejects_a_stale_writer_without_overwriting_newer_state(tmp_path) -> None:
    """DRH-008: State publication is versioned and atomic."""
    store = BundleStateStore(root=tmp_path, bundle_id=BundleId("b_" + "A" * 43))
    initial = BundleLocalState(bundle_id=BundleId("b_" + "A" * 43))
    await store.initialize(initial)
    with pytest.raises(TypeError, match="bundle_transition_lease_required"):
        await store.write(initial, expected_revision=0, lease=None)  # type: ignore[arg-type]
    async with store.transition() as lease:
        latest = await store.write(initial, expected_revision=0, lease=lease)
        with pytest.raises(ValueError, match="state_revision_conflict"):
            await store.write(initial, expected_revision=0, lease=lease)
    assert (await store.read()) == latest


async def test_bundle_graph_checkpoint_is_contained_and_cannot_reopen_after_bundle_loss(tmp_path) -> None:
    """REG-020: recoverable graph state has no external checkpoint fallback."""
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=("alice", "thread-1"), request_text="Question")
    root = lifecycle.private_root(bundle)
    config = {"configurable": {"thread_id": bundle.bundle_id.value, "checkpoint_ns": ""}}

    async with lifecycle.open_graph_checkpoint(bundle) as saver:
        assert await saver.aget_tuple(config) is None
    assert (root / "graph.sqlite").is_file()

    shutil.rmtree(root)
    with pytest.raises(BundleLifecycleError, match="bundle_unavailable"):
        async with lifecycle.open_graph_checkpoint(bundle):
            pass


def _values(**overrides):
    values: dict = {
        "bundle_id": BUNDLE_ID,
        "outer_thread_id": "thread-1",
        "generation": 0,
    }
    values.update(overrides)
    return values


def test_research_state_control_fields_round_trip_through_serialization() -> None:
    waiting = _values(phase_status=PhaseStatus.WAITING.value, waiting_for="hitl1")
    restored = validate_research_state(waiting)
    assert restored.schema_version == RESEARCH_STATE_SCHEMA_VERSION
    assert restored.phase_status is PhaseStatus.WAITING
    assert project_lifecycle_status(restored) is LifecycleStatus.SUSPENDED

    terminal = _values(
        phase_status=PhaseStatus.TERMINAL.value,
        terminal_status=LifecycleStatus.COMPLETED.value,
    )
    restored_terminal = validate_research_state(terminal)
    assert restored_terminal.terminal_status is LifecycleStatus.COMPLETED
    assert project_lifecycle_status(restored_terminal) is LifecycleStatus.COMPLETED


def test_research_state_serialization_is_bounded() -> None:
    payload = serialize_research_state(_values())
    assert len(payload) <= MAX_CHECKPOINT_STATE_BYTES


def test_research_checkpoint_rejects_unknown_extra_field() -> None:
    # Raw runtime authority fields (app_config, user_id, handles) cannot enter the
    # checkpoint: the frozen dataclass forbids unknown fields.
    with pytest.raises(TypeError):
        ResearchGraphState(**_values(app_config={"db": "secret"}))  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        ResearchGraphState(**_values(user_id="alice"))  # type: ignore[call-arg]


def test_skeleton_state_module_is_removed_and_graph_binds_research_state() -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("deerflow_deep_research.graph.skeleton_state")
    from deerflow_deep_research.graph import builder

    assert builder.ResearchState is ResearchState


def test_research_state_declares_no_legacy_status_field() -> None:
    assert "status" not in ResearchState.__annotations__
