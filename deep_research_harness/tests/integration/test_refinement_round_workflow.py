"""Workflow evidence for one same-Bundle refinement round.

@impl DRH-005
@impl DRH-007
@impl REG-021
@impl RUI-006
"""

from __future__ import annotations

import asyncio
import secrets
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from deerflow_deep_research.domain.bundle import RunBundleRef
from deerflow_deep_research.domain.lifecycle import (
    AcceptedHumanResponse,
    Hitl2Decision,
    HumanInputMode,
    HumanInputOption,
    HumanInputRequest,
    LifecycleAction,
    LifecycleStatus,
    PendingResearchInterrupt,
    RefinementOperation,
    ResponseKind,
)
from deerflow_deep_research.domain.state import PhaseStatus
from deerflow_deep_research.runtime.bundle_control import BundleControl
from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
from deerflow_deep_research.runtime.bundle_lifecycle import BundleAlreadyActive, BundleLifecycle
from deerflow_deep_research.runtime.human_input import SelectedStartMessage
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore
from tests.fixtures.recipes import fixture_recipe

_SCOPE = ("alice", "refinement-workflow")


def _fixture_executor(tmp_path: Path) -> BundleGraphExecutor:
    async def create(_envelope, *, bundle, **_kwargs):  # noqa: ANN001
        return WorkUnitStore(
            workspace_host_path=tmp_path,
            bundle=bundle,
            clock=lambda: datetime(2026, 8, 7, tzinfo=UTC),
            monotonic=time.monotonic,
            lock_sleep=time.sleep,
            token_factory=lambda: secrets.token_hex(16),
            fault_hook=None,
        )

    return BundleGraphExecutor(recipe=fixture_recipe(work_unit_store_factory=create))


def _envelope(tmp_path: Path) -> TrustedRuntimeEnvelope:
    uploads = tmp_path / "uploads"
    outputs = tmp_path / "outputs"
    uploads.mkdir(exist_ok=True)
    outputs.mkdir(exist_ok=True)
    return TrustedRuntimeEnvelope(
        effective_user_id=_SCOPE[0],
        outer_thread_id=_SCOPE[1],
        outer_run_id="refinement-workflow-run",
        app_config=SimpleNamespace(models=(), tools=(), checkpointer=None, database=None),
        workspace_host_path=tmp_path,
        uploads_host_path=uploads,
        outputs_host_path=outputs,
        workspace_virtual_root="/mnt/user-data/workspace",
        uploads_virtual_root="/mnt/user-data/uploads",
        outputs_virtual_root="/mnt/user-data/outputs",
        parent_sandbox=object(),
        progress=None,
    )


def _terminal_snapshot(
    bundle: RunBundleRef,
    *,
    terminal_status: LifecycleStatus = LifecycleStatus.COMPLETED,
) -> dict[str, object]:
    return {
        "schema_version": 2,
        "bundle_id": bundle.bundle_id.value,
        "start_message_id": "fixture-start",
        "request_digest": "d_" + "R" * 43,
        "request_text": "Fixture terminal snapshot.",
        "phase": "final_delivery",
        "route": "pass",
        "phase_status": PhaseStatus.TERMINAL.value,
        "terminal_status": terminal_status.value,
        "generation": 0,
        "repair_counts": {},
        "wave0_results": (),
        "wave1_results": (),
        "consumed_request_ids": (),
        "consumed_message_ids": (),
        "execution_trace": ("final_delivery",),
    }


async def _stage_terminal(
    *,
    lifecycle: BundleLifecycle,
    bundle: RunBundleRef,
    executor: BundleGraphExecutor,
    terminal_status: LifecycleStatus = LifecycleStatus.COMPLETED,
) -> None:
    config = executor._config(bundle)
    async with lifecycle.open_graph_checkpoint(bundle) as saver:
        graph = executor._recipe.builder.compile(checkpointer=saver)
        await graph.aupdate_state(
            config,
            _terminal_snapshot(bundle, terminal_status=terminal_status),
            as_node="final_delivery",
        )
        terminal = await graph.aget_state(config)
    await lifecycle.sync_graph_progress(bundle=bundle, values=dict(terminal.values), pending=None)


async def _graph_values(
    *,
    lifecycle: BundleLifecycle,
    bundle: RunBundleRef,
    executor: BundleGraphExecutor,
) -> dict[str, object]:
    async with lifecycle.open_graph_checkpoint(bundle) as saver:
        graph = executor._recipe.builder.compile(checkpointer=saver)
        snapshot = await graph.aget_state(executor._config(bundle))
    return dict(snapshot.values)


@pytest.mark.asyncio
async def test_explicit_ended_direction_commits_and_starts_topic_planning_in_the_same_bundle(tmp_path: Path) -> None:
    """DRH-005/RUI-006: an ended target is not merely marked pending."""

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=_SCOPE, request_text="Question")
    executor = _fixture_executor(tmp_path)
    await _stage_terminal(lifecycle=lifecycle, bundle=bundle, executor=executor)

    result = await BundleControl(lifecycle=lifecycle, graph_executor=executor).dispatch(
        action=LifecycleAction.REFINE,
        effective_user_id=_SCOPE[0],
        outer_thread_id=_SCOPE[1],
        messages=(),
        tool_call_id="ended-direction",
        bundle_id=bundle.bundle_id.value,
        refinement="Prioritize primary regulatory sources.",
        envelope=_envelope(tmp_path),
    )

    state = await lifecycle.read_state(bundle)
    values = await _graph_values(lifecycle=lifecycle, bundle=bundle, executor=executor)
    assert result["code"] == "refinement_applied"
    assert result["bundle_id"] == bundle.bundle_id.value
    assert state.current_refinement is not None
    assert state.admitted_refinement is None
    assert state.generation == 1
    assert tuple(values["execution_trace"]).count("topic_planning") == 1


@pytest.mark.asyncio
async def test_fresh_start_waits_while_ended_reactivation_holds_the_scope_decision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DRH-007: scope -> transition keeps fresh start and reactivation linearizable."""

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=_SCOPE, request_text="Question")
    executor = _fixture_executor(tmp_path)
    await _stage_terminal(lifecycle=lifecycle, bundle=bundle, executor=executor)
    operation = RefinementOperation.from_text(
        operation_key="ended-recovery",
        text="Prioritize primary regulatory sources.",
    )
    await lifecycle.admit_refinement(
        scope=_SCOPE,
        bundle_id=bundle.bundle_id,
        text=operation.text,
        operation_key=operation.operation_key,
    )

    entered_cas = asyncio.Event()
    release_cas = asyncio.Event()
    original_commit = lifecycle.commit_prepared_refinement_round

    async def delayed_commit(**kwargs):  # noqa: ANN003
        entered_cas.set()
        await release_cas.wait()
        return await original_commit(**kwargs)

    monkeypatch.setattr(lifecycle, "commit_prepared_refinement_round", delayed_commit)
    reactivation = asyncio.create_task(
        executor.prepare_refinement_round(
            lifecycle=lifecycle,
            scope=_SCOPE,
            bundle=bundle,
            submitted_operation=operation,
        )
    )
    await entered_cas.wait()
    fresh_lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    fresh_start = asyncio.create_task(fresh_lifecycle.start(scope=_SCOPE, request_text="Fresh question"))
    await asyncio.sleep(0.05)
    assert not fresh_start.done()

    release_cas.set()
    await reactivation
    with pytest.raises(BundleAlreadyActive):
        await fresh_start

    active = await lifecycle.discover_active(scope=_SCOPE)
    assert active == bundle


@pytest.mark.asyncio
async def test_active_suspended_round_consumes_its_direction_only_after_completed_projection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DRH-005: the current HITL subject remains intact until the graph completes."""

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=_SCOPE, request_text="Question", start_message_id="start-message")
    executor = _fixture_executor(tmp_path)
    envelope = _envelope(tmp_path)
    await executor.start(
        lifecycle=lifecycle,
        bundle=bundle,
        envelope=envelope,
        start_message=SelectedStartMessage(message_id="start-message", text="Question"),
        tool_call_id="start-round",
    )
    suspended = await lifecycle.read_state(bundle)
    assert suspended.pending_request_id is not None

    operation = RefinementOperation.from_text(
        operation_key="active-direction",
        text="Prioritize primary regulatory sources.",
    )
    admitted = await lifecycle.admit_refinement(
        scope=_SCOPE,
        bundle_id=bundle.bundle_id,
        text=operation.text,
        operation_key=operation.operation_key,
    )
    assert admitted.newly_admitted
    assert admitted.state.pending_request_id == suspended.pending_request_id
    assert admitted.state.current_refinement is None

    execution_entries = 0
    original_exclusion = lifecycle.execution_exclusion

    @asynccontextmanager
    async def counted_exclusion(target: RunBundleRef):
        nonlocal execution_entries
        execution_entries += 1
        async with original_exclusion(target) as lease:
            yield lease

    monkeypatch.setattr(lifecycle, "execution_exclusion", counted_exclusion)

    await executor.resume(
        lifecycle=lifecycle,
        bundle=bundle,
        envelope=envelope,
        response=AcceptedHumanResponse(
            request_id=suspended.pending_request_id,
            message_id="answer-message",
            value="Use the default profile.",
            response_kind=ResponseKind.TEXT,
        ),
        tool_call_id="resume-round",
    )

    state = await lifecycle.read_state(bundle)
    values = await _graph_values(lifecycle=lifecycle, bundle=bundle, executor=executor)
    assert state.current_refinement is not None
    assert state.current_refinement.operation_key == operation.operation_key
    assert state.admitted_refinement is None
    assert state.refinement_round == 1
    assert state.generation == 1
    assert tuple(values["execution_trace"]).count("topic_planning") == 2
    assert execution_entries == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "admit_before_terminal_projection",
    (True, False),
    ids=("before-terminal-projection", "after-terminal-projection"),
)
async def test_terminal_projection_race_preserves_one_direction_token_and_continuation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    admit_before_terminal_projection: bool,
) -> None:
    """REG-021: either side of the terminal boundary owns one next round."""

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=_SCOPE, request_text="Question", start_message_id="start-message")
    executor = _fixture_executor(tmp_path)
    envelope = _envelope(tmp_path)
    await executor.start(
        lifecycle=lifecycle,
        bundle=bundle,
        envelope=envelope,
        start_message=SelectedStartMessage(message_id="start-message", text="Question"),
        tool_call_id="start-round",
    )
    suspended = await lifecycle.read_state(bundle)
    assert suspended.pending_request_id is not None

    execution_entries = 0
    original_exclusion = lifecycle.execution_exclusion

    @asynccontextmanager
    async def counted_exclusion(target: RunBundleRef):
        nonlocal execution_entries
        execution_entries += 1
        async with original_exclusion(target) as lease:
            yield lease

    monkeypatch.setattr(lifecycle, "execution_exclusion", counted_exclusion)
    operation = RefinementOperation.from_text(
        operation_key=f"terminal-race-{admit_before_terminal_projection}",
        text="Prioritize primary regulatory sources.",
    )
    controller = BundleControl(lifecycle=lifecycle, graph_executor=executor)

    async def submit_direction() -> dict[str, object]:
        return await controller.dispatch(
            action=LifecycleAction.REFINE,
            effective_user_id=_SCOPE[0],
            outer_thread_id=_SCOPE[1],
            messages=(),
            tool_call_id=operation.operation_key,
            bundle_id=bundle.bundle_id.value,
            refinement=operation.text,
            envelope=envelope,
        )

    if admit_before_terminal_projection:
        admitted = await submit_direction()
        assert admitted["code"] == "refinement_pending"
        await executor.resume(
            lifecycle=lifecycle,
            bundle=bundle,
            envelope=envelope,
            response=AcceptedHumanResponse(
                request_id=suspended.pending_request_id,
                message_id="answer-message",
                value="Use the default profile.",
                response_kind=ResponseKind.TEXT,
            ),
            tool_call_id="resume-round",
        )
    else:
        terminal_projected = asyncio.Event()
        release_terminal_owner = asyncio.Event()
        external_round_prepared = asyncio.Event()
        release_external_continuation = asyncio.Event()
        original_sync = lifecycle.sync_graph_progress
        original_execute = executor.execute_prepared_refinement_round

        async def gate_terminal_projection(**kwargs):  # noqa: ANN003
            state = await original_sync(**kwargs)
            if kwargs["values"].get("terminal_status") == LifecycleStatus.COMPLETED.value:
                terminal_projected.set()
                await release_terminal_owner.wait()
            return state

        async def gate_external_continuation(**kwargs):  # noqa: ANN003
            if kwargs.get("execution_lease") is None:
                external_round_prepared.set()
                await release_external_continuation.wait()
            return await original_execute(**kwargs)

        monkeypatch.setattr(lifecycle, "sync_graph_progress", gate_terminal_projection)
        monkeypatch.setattr(executor, "execute_prepared_refinement_round", gate_external_continuation)
        resume = asyncio.create_task(
            executor.resume(
                lifecycle=lifecycle,
                bundle=bundle,
                envelope=envelope,
                response=AcceptedHumanResponse(
                    request_id=suspended.pending_request_id,
                    message_id="answer-message",
                    value="Use the default profile.",
                    response_kind=ResponseKind.TEXT,
                ),
                tool_call_id="resume-round",
            )
        )
        await terminal_projected.wait()
        direction = asyncio.create_task(submit_direction())
        await external_round_prepared.wait()
        prepared_state = await lifecycle.read_state(bundle)
        assert prepared_state.current_refinement is not None
        assert prepared_state.current_refinement.operation_key == operation.operation_key
        assert prepared_state.admitted_refinement is None

        release_terminal_owner.set()
        await resume
        release_external_continuation.set()
        admitted = await direction
        assert admitted["code"] == "refinement_applied"

    state = await lifecycle.read_state(bundle)
    values = await _graph_values(lifecycle=lifecycle, bundle=bundle, executor=executor)
    assert state.current_refinement is not None
    assert state.current_refinement.operation_key == operation.operation_key
    assert state.admitted_refinement is None
    assert state.refinement_round == 1
    assert state.generation == 1
    assert values["refinement_round_token"] == state.current_refinement.round_token
    assert tuple(values["execution_trace"]).count("topic_planning") == 2
    assert execution_entries == (1 if admit_before_terminal_projection else 2)


@pytest.mark.asyncio
async def test_active_hitl2_subject_survives_independent_direction_admission(tmp_path: Path) -> None:
    """DRH-005: an independent direction cannot consume a current HITL2 choice."""

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=_SCOPE, request_text="Question")
    pending = PendingResearchInterrupt(
        request=HumanInputRequest(
            request_id="hitl2-choice",
            mode=HumanInputMode.CHOICE,
            title="Choose a research decision",
            context="Choose the next graph decision.",
            options=tuple(
                HumanInputOption(id=decision, label=decision.value, value=decision) for decision in Hitl2Decision
            ),
        ),
        suspension_cursor="hitl2-suspension",
        phase="hitl2",
        generation=0,
    )
    suspended = await lifecycle.sync_graph_progress(
        bundle=bundle,
        values={
            "phase": "hitl2",
            "phase_status": PhaseStatus.WAITING.value,
            "terminal_status": None,
            "generation": 0,
            "execution_trace": ("wave2_synthesis",),
        },
        pending=pending,
    )

    operation = RefinementOperation.from_text(
        operation_key="hitl2-direction",
        text="Prioritize primary regulatory sources.",
    )
    admitted = await lifecycle.admit_refinement(
        scope=_SCOPE,
        bundle_id=bundle.bundle_id,
        text=operation.text,
        operation_key=operation.operation_key,
    )

    assert suspended.pending_request_id == pending.request.request_id
    assert admitted.newly_admitted
    assert admitted.state.pending_request_id == pending.request.request_id
    assert admitted.state.pending_cursor == pending.suspension_cursor
    assert admitted.state.pending_request_mode is HumanInputMode.CHOICE
    assert admitted.state.waiting_for == "hitl2"
    assert admitted.state.generation == pending.generation
    assert admitted.state.admitted_refinement == operation
    assert admitted.state.current_refinement is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "terminal_status",
    (LifecycleStatus.STOPPED, LifecycleStatus.CANCELLED, LifecycleStatus.BLOCKED),
)
async def test_non_completed_terminal_keeps_direction_pending_until_explicit_textless_continuation(
    tmp_path: Path,
    terminal_status: LifecycleStatus,
) -> None:
    """DRH-005: stop/cancel/block never turn a queued direction into auto-restart."""

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=_SCOPE, request_text="Question", start_message_id="start-message")
    executor = _fixture_executor(tmp_path)
    await _stage_terminal(
        lifecycle=lifecycle,
        bundle=bundle,
        executor=executor,
        terminal_status=terminal_status,
    )
    operation = RefinementOperation.from_text(
        operation_key=f"{terminal_status.value}-direction",
        text="Prioritize primary regulatory sources.",
    )
    await lifecycle.admit_refinement(
        scope=_SCOPE,
        bundle_id=bundle.bundle_id,
        text=operation.text,
        operation_key=operation.operation_key,
    )

    # This graph-owning re-projection observes the terminal snapshot but may not
    # interpret the pending record as restart authorization.
    await executor.start(
        lifecycle=lifecycle,
        bundle=bundle,
        envelope=_envelope(tmp_path),
        start_message=SelectedStartMessage(message_id="start-message", text="Question"),
        tool_call_id=f"{terminal_status.value}-projection",
    )
    retained = await lifecycle.read_state(bundle)
    assert retained.terminal_status is terminal_status
    assert retained.admitted_refinement == operation
    assert retained.current_refinement is None

    replay = await BundleControl(lifecycle=lifecycle, graph_executor=executor).dispatch(
        action=LifecycleAction.REFINE,
        effective_user_id=_SCOPE[0],
        outer_thread_id=_SCOPE[1],
        messages=(),
        tool_call_id=operation.operation_key,
        bundle_id=bundle.bundle_id.value,
        refinement=operation.text,
        envelope=_envelope(tmp_path),
    )
    assert replay["code"] == "refinement_pending"
    assert (await lifecycle.read_state(bundle)).current_refinement is None

    continued = await BundleControl(lifecycle=lifecycle, graph_executor=executor).dispatch(
        action=LifecycleAction.REFINE,
        effective_user_id=_SCOPE[0],
        outer_thread_id=_SCOPE[1],
        messages=(),
        tool_call_id=f"{terminal_status.value}-continue",
        bundle_id=bundle.bundle_id.value,
        envelope=_envelope(tmp_path),
    )
    state = await lifecycle.read_state(bundle)
    assert continued["code"] == "refinement_applied"
    assert state.current_refinement is not None
    assert state.current_refinement.operation_key == operation.operation_key
    assert state.admitted_refinement is None
