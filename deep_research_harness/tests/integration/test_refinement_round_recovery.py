"""Crash-recovery evidence for one Bundle-bound refinement round.

@impl DRH-005
@impl REG-021
"""

from __future__ import annotations

import asyncio
import secrets
import shutil
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from deerflow_deep_research.domain.bundle import RunBundleRef
from deerflow_deep_research.domain.lifecycle import (
    ImplementationMode,
    LifecycleAction,
    LifecycleStatus,
    RefinementAdmissionDisposition,
    RefinementOperation,
)
from deerflow_deep_research.domain.state import PhaseStatus
from deerflow_deep_research.runtime.bundle_control import BundleControl
from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle, BundleLifecycleError
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore
from tests.fixtures.recipes import fixture_recipe

_SCOPE = ("alice", "refinement-recovery")


class _InjectedCrash(RuntimeError):
    pass


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
        outer_run_id="refinement-recovery-run",
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


def _terminal_snapshot(bundle: RunBundleRef, *, generation: int = 0) -> dict[str, object]:
    return {
        "schema_version": 3,
        "bundle_id": bundle.bundle_id.value,
        "start_message_id": "fixture-start",
        "request_digest": "d_" + "R" * 43,
        "request_text": "Fixture terminal snapshot.",
        "phase": "final_delivery",
        "route": "pass",
        "phase_status": PhaseStatus.TERMINAL.value,
        "terminal_status": LifecycleStatus.COMPLETED.value,
        "generation": generation,
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
) -> None:
    """Use the production topology/writers to create a Bundle-contained terminal graph."""

    config = executor._config(bundle)
    async with lifecycle.open_graph_checkpoint(bundle) as saver:
        graph = executor._recipe.builder.compile(checkpointer=saver)
        await graph.aupdate_state(config, _terminal_snapshot(bundle), as_node="final_delivery")
        terminal = await graph.aget_state(config)
    await lifecycle.sync_graph_progress(bundle=bundle, values=dict(terminal.values), pending=None)


async def _prepared_values(
    *,
    lifecycle: BundleLifecycle,
    bundle: RunBundleRef,
    executor: BundleGraphExecutor,
) -> dict[str, object]:
    config = executor._config(bundle)
    async with lifecycle.open_graph_checkpoint(bundle) as saver:
        graph = executor._recipe.builder.compile(checkpointer=saver)
        snapshot = await graph.aget_state(config)
    return dict(snapshot.values)


async def _admit(
    *,
    lifecycle: BundleLifecycle,
    bundle: RunBundleRef,
    operation_key: str = "operation-one",
    text: str = "Prioritize primary regulatory sources.",
) -> RefinementOperation:
    operation = RefinementOperation.from_text(operation_key=operation_key, text=text)
    admitted = await lifecycle.admit_refinement(
        scope=_SCOPE,
        bundle_id=bundle.bundle_id,
        text=operation.text,
        operation_key=operation.operation_key,
    )
    assert admitted.disposition is RefinementAdmissionDisposition.PENDING
    return operation


async def _start_fixture(lifecycle: BundleLifecycle) -> RunBundleRef:
    return await lifecycle.start(
        scope=_SCOPE,
        request_text="Question",
        implementation_mode=ImplementationMode.FIXTURE,
    )


@pytest.mark.asyncio
async def test_preparation_crash_leaves_terminal_pending_state_and_status_never_reconciles(tmp_path: Path) -> None:
    """DRH-005: a prepared rerun checkpoint is not public application before CAS."""

    def fault(point: str) -> None:
        if point == "after_refinement_checkpoint_prepared":
            raise _InjectedCrash(point)

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path, fault_hook=fault)
    bundle = await _start_fixture(lifecycle)
    executor = BundleGraphExecutor(recipe=fixture_recipe())
    await _stage_terminal(lifecycle=lifecycle, bundle=bundle, executor=executor)
    original = await _admit(lifecycle=lifecycle, bundle=bundle)

    with pytest.raises(_InjectedCrash, match="after_refinement_checkpoint_prepared"):
        await executor.prepare_refinement_round(
            lifecycle=lifecycle,
            scope=_SCOPE,
            bundle=bundle,
            submitted_operation=original,
        )

    before_status = await lifecycle.read_state(bundle)
    assert before_status.terminal_status is LifecycleStatus.COMPLETED
    assert before_status.admitted_refinement == original
    assert before_status.current_refinement is None
    prepared = await _prepared_values(lifecycle=lifecycle, bundle=bundle, executor=executor)
    assert prepared["generation"] == 1
    assert prepared["route"] == "topic_planning"
    assert prepared["current_refinement"]["text"] == original.text
    assert prepared["refinement_round_token"]

    status = await lifecycle.status(scope=_SCOPE, bundle_id=bundle.bundle_id)
    assert status.action is LifecycleAction.STATUS
    assert status.status is LifecycleStatus.COMPLETED
    assert status.refinement is not None
    assert status.refinement.disposition.value == "pending"
    assert status.legal_next_action.value == "refine"
    assert await lifecycle.read_state(bundle) == before_status


@pytest.mark.asyncio
async def test_matching_replay_reconciles_prepared_checkpoint_once_without_another_generation(tmp_path: Path) -> None:
    """REG-021: reopening reconciles the exact prepared token, not a second rerun."""

    armed = True

    def fault(point: str) -> None:
        nonlocal armed
        if armed and point == "after_refinement_checkpoint_prepared":
            armed = False
            raise _InjectedCrash(point)

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path, fault_hook=fault)
    bundle = await _start_fixture(lifecycle)
    executor = BundleGraphExecutor(recipe=fixture_recipe())
    await _stage_terminal(lifecycle=lifecycle, bundle=bundle, executor=executor)
    original = await _admit(lifecycle=lifecycle, bundle=bundle)

    with pytest.raises(_InjectedCrash):
        await executor.prepare_refinement_round(
            lifecycle=lifecycle,
            scope=_SCOPE,
            bundle=bundle,
            submitted_operation=original,
        )

    reopened = BundleLifecycle(workspace_host_path=tmp_path)
    recovered = await executor.prepare_refinement_round(
        lifecycle=reopened,
        scope=_SCOPE,
        bundle=bundle,
        submitted_operation=original,
    )
    state = await reopened.read_state(bundle)

    assert recovered.disposition is RefinementAdmissionDisposition.APPLIED
    assert state.admitted_refinement is None
    assert state.current_refinement is not None
    assert state.current_refinement.operation_key == original.operation_key
    assert state.generation == 1
    assert state.refinement_round == 1
    assert state.terminal_status is None

    replay = await executor.prepare_refinement_round(
        lifecycle=reopened,
        scope=_SCOPE,
        bundle=bundle,
        submitted_operation=original,
    )
    assert replay.disposition is RefinementAdmissionDisposition.APPLIED
    assert await reopened.read_state(bundle) == state
    assert (await _prepared_values(lifecycle=reopened, bundle=bundle, executor=executor))["generation"] == 1


@pytest.mark.asyncio
async def test_precommit_reconciliation_preserves_first_round_and_rejects_a_different_operation(tmp_path: Path) -> None:
    """DRH-005: reconciliation cannot fall through into a new ordinary admission."""

    def fault(point: str) -> None:
        if point == "after_refinement_checkpoint_prepared":
            raise _InjectedCrash(point)

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path, fault_hook=fault)
    bundle = await _start_fixture(lifecycle)
    executor = BundleGraphExecutor(recipe=fixture_recipe())
    await _stage_terminal(lifecycle=lifecycle, bundle=bundle, executor=executor)
    first = await _admit(lifecycle=lifecycle, bundle=bundle)
    with pytest.raises(_InjectedCrash):
        await executor.prepare_refinement_round(
            lifecycle=lifecycle,
            scope=_SCOPE,
            bundle=bundle,
            submitted_operation=first,
        )

    second = RefinementOperation.from_text(operation_key="operation-two", text="Add a regional comparison.")
    second_admission = await lifecycle.admit_refinement(
        scope=_SCOPE,
        bundle_id=bundle.bundle_id,
        text=second.text,
        operation_key=second.operation_key,
    )
    assert second_admission.disposition is RefinementAdmissionDisposition.CONFLICT

    reconciled = await BundleGraphExecutor(recipe=fixture_recipe()).prepare_refinement_round(
        lifecycle=BundleLifecycle(workspace_host_path=tmp_path),
        scope=_SCOPE,
        bundle=bundle,
        submitted_operation=second,
    )
    state = await lifecycle.read_state(bundle)

    assert reconciled.disposition is RefinementAdmissionDisposition.CONFLICT
    assert state.current_refinement is not None
    assert state.current_refinement.operation_key == first.operation_key
    assert state.admitted_refinement is None
    assert state.generation == 1


@pytest.mark.asyncio
async def test_textless_continuation_reconciles_only_the_selected_prepared_pending_record(tmp_path: Path) -> None:
    """DRH-005: textless recovery has no route into ordinary direction admission."""

    def fault(point: str) -> None:
        if point == "after_refinement_checkpoint_prepared":
            raise _InjectedCrash(point)

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path, fault_hook=fault)
    bundle = await _start_fixture(lifecycle)
    executor = BundleGraphExecutor(recipe=fixture_recipe())
    await _stage_terminal(lifecycle=lifecycle, bundle=bundle, executor=executor)
    original = await _admit(lifecycle=lifecycle, bundle=bundle)

    with pytest.raises(_InjectedCrash):
        await executor.prepare_refinement_round(
            lifecycle=lifecycle,
            scope=_SCOPE,
            bundle=bundle,
            submitted_operation=original,
        )

    selected = await BundleGraphExecutor(recipe=fixture_recipe()).prepare_refinement_round(
        lifecycle=BundleLifecycle(workspace_host_path=tmp_path),
        scope=_SCOPE,
        bundle=bundle,
        submitted_operation=None,
    )
    state = await lifecycle.read_state(bundle)

    assert selected.disposition is RefinementAdmissionDisposition.APPLIED
    assert state.current_refinement is not None
    assert state.current_refinement.operation_key == original.operation_key
    assert state.admitted_refinement is None


@pytest.mark.asyncio
async def test_public_matching_retry_reconciles_prepared_token_and_runs_one_queued_task(tmp_path: Path) -> None:
    """RUI-012: a matching public retry owns only its prepared round."""

    armed = True

    def fault(point: str) -> None:
        nonlocal armed
        if armed and point == "after_refinement_checkpoint_prepared":
            armed = False
            raise _InjectedCrash(point)

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path, fault_hook=fault)
    bundle = await _start_fixture(lifecycle)
    executor = _fixture_executor(tmp_path)
    await _stage_terminal(lifecycle=lifecycle, bundle=bundle, executor=executor)
    original = await _admit(lifecycle=lifecycle, bundle=bundle)
    with pytest.raises(_InjectedCrash):
        await executor.prepare_refinement_round(
            lifecycle=lifecycle,
            scope=_SCOPE,
            bundle=bundle,
            submitted_operation=original,
        )

    result = await BundleControl(lifecycle=lifecycle, graph_executor=executor).dispatch(
        action=LifecycleAction.REFINE,
        effective_user_id=_SCOPE[0],
        outer_thread_id=_SCOPE[1],
        messages=(),
        tool_call_id=original.operation_key,
        bundle_id=bundle.bundle_id.value,
        refinement=original.text,
        envelope=_envelope(tmp_path),
    )
    state = await lifecycle.read_state(bundle)
    values = await _prepared_values(lifecycle=lifecycle, bundle=bundle, executor=executor)

    assert result["code"] == "refinement_applied"
    assert result["refinement"]["disposition"] == "applied"
    assert state.current_refinement is not None
    assert state.current_refinement.operation_key == original.operation_key
    assert state.admitted_refinement is None
    assert tuple(values["execution_trace"]).count("topic_planning") == 1


@pytest.mark.asyncio
async def test_public_precommit_competitor_reconciles_first_round_then_returns_conflict(tmp_path: Path) -> None:
    """RUI-012: a competing call cannot fall through after first-token recovery."""

    def fault(point: str) -> None:
        if point == "after_refinement_checkpoint_prepared":
            raise _InjectedCrash(point)

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path, fault_hook=fault)
    bundle = await _start_fixture(lifecycle)
    executor = _fixture_executor(tmp_path)
    await _stage_terminal(lifecycle=lifecycle, bundle=bundle, executor=executor)
    original = await _admit(lifecycle=lifecycle, bundle=bundle)
    with pytest.raises(_InjectedCrash):
        await executor.prepare_refinement_round(
            lifecycle=lifecycle,
            scope=_SCOPE,
            bundle=bundle,
            submitted_operation=original,
        )

    result = await BundleControl(lifecycle=lifecycle, graph_executor=executor).dispatch(
        action=LifecycleAction.REFINE,
        effective_user_id=_SCOPE[0],
        outer_thread_id=_SCOPE[1],
        messages=(),
        tool_call_id="competing-operation",
        bundle_id=bundle.bundle_id.value,
        refinement="Add a regional comparison.",
        envelope=_envelope(tmp_path),
    )
    state = await lifecycle.read_state(bundle)
    values = await _prepared_values(lifecycle=lifecycle, bundle=bundle, executor=executor)

    assert result["code"] == "refinement_conflict"
    assert result["refinement"]["disposition"] == "applied"
    assert state.current_refinement is not None
    assert state.current_refinement.operation_key == original.operation_key
    assert state.admitted_refinement is None
    assert tuple(values["execution_trace"]).count("topic_planning") == 0


@pytest.mark.asyncio
async def test_concurrent_textless_continuations_reconcile_the_selected_pending_record_after_cas(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RUI-012: a selected terminal continuation survives its pre-CAS wait gap."""

    armed = True

    def fault(point: str) -> None:
        nonlocal armed
        if armed and point == "after_refinement_checkpoint_prepared":
            armed = False
            raise _InjectedCrash(point)

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path, fault_hook=fault)
    bundle = await _start_fixture(lifecycle)
    executor = _fixture_executor(tmp_path)
    await _stage_terminal(lifecycle=lifecycle, bundle=bundle, executor=executor)
    original = await _admit(lifecycle=lifecycle, bundle=bundle)
    with pytest.raises(_InjectedCrash):
        await executor.prepare_refinement_round(
            lifecycle=lifecycle,
            scope=_SCOPE,
            bundle=bundle,
            submitted_operation=original,
        )

    first_selected = asyncio.Event()
    second_selected = asyncio.Event()
    release_first = asyncio.Event()
    release_second = asyncio.Event()
    original_admit = lifecycle.admit_refinement
    selected_count = 0

    async def gate_selected_continuation(**kwargs):  # noqa: ANN003
        nonlocal selected_count
        admission = await original_admit(**kwargs)
        if kwargs["text"] is None:
            selected_count += 1
            if selected_count == 1:
                first_selected.set()
                await release_first.wait()
            elif selected_count == 2:
                second_selected.set()
                await release_second.wait()
        return admission

    monkeypatch.setattr(lifecycle, "admit_refinement", gate_selected_continuation)
    controller = BundleControl(lifecycle=lifecycle, graph_executor=executor)

    async def continue_selected(operation_key: str) -> dict[str, object]:
        return await controller.dispatch(
            action=LifecycleAction.REFINE,
            effective_user_id=_SCOPE[0],
            outer_thread_id=_SCOPE[1],
            messages=(),
            tool_call_id=operation_key,
            bundle_id=bundle.bundle_id.value,
            envelope=_envelope(tmp_path),
        )

    first = asyncio.create_task(continue_selected("continue-one"))
    await first_selected.wait()
    second = asyncio.create_task(continue_selected("continue-two"))
    await second_selected.wait()

    release_first.set()
    first_result = await first
    release_second.set()
    second_result = await second
    state = await lifecycle.read_state(bundle)
    values = await _prepared_values(lifecycle=lifecycle, bundle=bundle, executor=executor)

    assert first_result["code"] == "refinement_applied"
    assert second_result["code"] == "refinement_applied"
    assert state.current_refinement is not None
    assert state.current_refinement.operation_key == original.operation_key
    assert state.admitted_refinement is None
    assert tuple(values["execution_trace"]).count("topic_planning") == 1


@pytest.mark.asyncio
async def test_stale_or_terminal_losing_graph_projection_cannot_overwrite_committed_round(tmp_path: Path) -> None:
    """REG-021: generation/token/terminal fences leave the current Bundle fact intact."""

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await _start_fixture(lifecycle)
    executor = BundleGraphExecutor(recipe=fixture_recipe())
    await _stage_terminal(lifecycle=lifecycle, bundle=bundle, executor=executor)
    original = await _admit(lifecycle=lifecycle, bundle=bundle)
    committed = await executor.prepare_refinement_round(
        lifecycle=lifecycle,
        scope=_SCOPE,
        bundle=bundle,
        submitted_operation=original,
    )
    before = await lifecycle.read_state(bundle)
    assert committed.disposition is RefinementAdmissionDisposition.APPLIED

    stale = {
        **_terminal_snapshot(bundle, generation=0),
        "refinement_round_token": "wrong-token",
    }
    observed = await lifecycle.sync_graph_progress(bundle=bundle, values=stale, pending=None)
    assert observed == before
    assert await lifecycle.read_state(bundle) == before

    cancelled = await lifecycle.cancel(scope=_SCOPE, bundle_id=bundle.bundle_id)
    assert cancelled.terminal_status is LifecycleStatus.CANCELLED
    late_active = {
        **_terminal_snapshot(bundle, generation=1),
        "phase": "topic_planning",
        "phase_status": PhaseStatus.IN_PROGRESS.value,
        "terminal_status": None,
        "refinement_round_token": before.current_refinement.round_token,
    }
    terminal_winner = await lifecycle.sync_graph_progress(bundle=bundle, values=late_active, pending=None)
    assert terminal_winner == cancelled
    assert await lifecycle.read_state(bundle) == cancelled


@pytest.mark.asyncio
async def test_crash_before_preparation_leaves_no_graph_transition_and_after_cas_leaves_only_queued_work(
    tmp_path: Path,
) -> None:
    """DRH-005: the two crash gaps preserve the authoritative side of the boundary."""

    def before_preparation(point: str) -> None:
        if point == "before_refinement_checkpoint_preparation":
            raise _InjectedCrash(point)

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path, fault_hook=before_preparation)
    bundle = await _start_fixture(lifecycle)
    executor = _fixture_executor(tmp_path)
    await _stage_terminal(lifecycle=lifecycle, bundle=bundle, executor=executor)
    original = await _admit(lifecycle=lifecycle, bundle=bundle)

    with pytest.raises(_InjectedCrash, match="before_refinement_checkpoint_preparation"):
        await executor.prepare_refinement_round(
            lifecycle=lifecycle,
            scope=_SCOPE,
            bundle=bundle,
            submitted_operation=original,
        )
    assert (await lifecycle.read_state(bundle)).admitted_refinement == original
    assert (await _prepared_values(lifecycle=lifecycle, bundle=bundle, executor=executor))["generation"] == 0

    def after_cas(point: str) -> None:
        if point == "after_refinement_bundle_cas":
            raise _InjectedCrash(point)

    lifecycle._fault_hook = after_cas
    with pytest.raises(_InjectedCrash, match="after_refinement_bundle_cas"):
        await executor.prepare_refinement_round(
            lifecycle=lifecycle,
            scope=_SCOPE,
            bundle=bundle,
            submitted_operation=original,
        )
    committed = await lifecycle.read_state(bundle)
    assert committed.current_refinement is not None
    assert committed.admitted_refinement is None
    prepared = await _prepared_values(lifecycle=lifecycle, bundle=bundle, executor=executor)
    assert prepared["generation"] == 1
    assert prepared["phase"] == "rerun"
    assert tuple(prepared["execution_trace"]) == ("final_delivery", "rerun")


@pytest.mark.asyncio
async def test_explicit_textless_retry_recovers_only_the_current_queued_task_after_cas(tmp_path: Path) -> None:
    """RUI-012: a post-CAS retry may recover its exact already-authorized task."""

    armed = True

    def after_cas(point: str) -> None:
        nonlocal armed
        if armed and point == "after_refinement_bundle_cas":
            armed = False
            raise _InjectedCrash(point)

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path, fault_hook=after_cas)
    bundle = await _start_fixture(lifecycle)
    executor = _fixture_executor(tmp_path)
    await _stage_terminal(lifecycle=lifecycle, bundle=bundle, executor=executor)
    original = await _admit(lifecycle=lifecycle, bundle=bundle)
    with pytest.raises(_InjectedCrash, match="after_refinement_bundle_cas"):
        await executor.prepare_refinement_round(
            lifecycle=lifecycle,
            scope=_SCOPE,
            bundle=bundle,
            submitted_operation=original,
        )

    recovered = await BundleControl(lifecycle=lifecycle, graph_executor=executor).dispatch(
        action=LifecycleAction.REFINE,
        effective_user_id=_SCOPE[0],
        outer_thread_id=_SCOPE[1],
        messages=(),
        tool_call_id="continue-after-cas",
        bundle_id=bundle.bundle_id.value,
        envelope=_envelope(tmp_path),
    )
    state = await lifecycle.read_state(bundle)
    values = await _prepared_values(lifecycle=lifecycle, bundle=bundle, executor=executor)

    assert recovered["code"] == "refinement_applied"
    assert recovered["refinement"]["disposition"] == "applied"
    assert state.current_refinement is not None
    assert state.current_refinement.operation_key == original.operation_key
    assert tuple(values["execution_trace"]).count("topic_planning") == 1

    rejected = await BundleControl(lifecycle=lifecycle, graph_executor=executor).dispatch(
        action=LifecycleAction.REFINE,
        effective_user_id=_SCOPE[0],
        outer_thread_id=_SCOPE[1],
        messages=(),
        tool_call_id="continue-after-completion",
        bundle_id=bundle.bundle_id.value,
        envelope=_envelope(tmp_path),
    )
    values_after_rejection = await _prepared_values(lifecycle=lifecycle, bundle=bundle, executor=executor)

    assert rejected["code"] == "invalid_transition"
    assert tuple(values_after_rejection["execution_trace"]).count("topic_planning") == 1


@pytest.mark.asyncio
async def test_independent_instances_prepare_one_round_and_cancelled_execution_waiter_writes_nothing(
    tmp_path: Path,
) -> None:
    """REG-021: transition and execution exclusions serialize different critical regions."""

    first = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await _start_fixture(first)
    first_executor = _fixture_executor(tmp_path)
    await _stage_terminal(lifecycle=first, bundle=bundle, executor=first_executor)
    original = await _admit(lifecycle=first, bundle=bundle)
    second = BundleLifecycle(workspace_host_path=tmp_path)
    second_executor = _fixture_executor(tmp_path)

    outcomes = await asyncio.gather(
        first_executor.prepare_refinement_round(
            lifecycle=first,
            scope=_SCOPE,
            bundle=bundle,
            submitted_operation=original,
        ),
        second_executor.prepare_refinement_round(
            lifecycle=second,
            scope=_SCOPE,
            bundle=bundle,
            submitted_operation=original,
        ),
    )
    state = await first.read_state(bundle)
    assert {outcome.disposition for outcome in outcomes} == {RefinementAdmissionDisposition.APPLIED}
    assert state.generation == 1
    assert state.refinement_round == 1

    async with first.execution_exclusion(bundle):
        waiting = asyncio.create_task(
            second_executor.execute_prepared_refinement_round(
                lifecycle=second,
                bundle=bundle,
                envelope=_envelope(tmp_path),
            )
        )
        await asyncio.sleep(0.05)
        assert not waiting.done()
        waiting.cancel()
        with pytest.raises(asyncio.CancelledError):
            await waiting
    assert await first.read_state(bundle) == state


@pytest.mark.asyncio
async def test_two_execution_owners_run_the_one_prepared_graph_task_once(tmp_path: Path) -> None:
    """REG-021: the execution contender rereads instead of invoking a second task."""

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await _start_fixture(lifecycle)
    executor = _fixture_executor(tmp_path)
    await _stage_terminal(lifecycle=lifecycle, bundle=bundle, executor=executor)
    original = await _admit(lifecycle=lifecycle, bundle=bundle)
    await executor.prepare_refinement_round(
        lifecycle=lifecycle,
        scope=_SCOPE,
        bundle=bundle,
        submitted_operation=original,
    )

    first, second = await asyncio.gather(
        executor.execute_prepared_refinement_round(
            lifecycle=lifecycle,
            bundle=bundle,
            envelope=_envelope(tmp_path),
        ),
        _fixture_executor(tmp_path).execute_prepared_refinement_round(
            lifecycle=BundleLifecycle(workspace_host_path=tmp_path),
            bundle=bundle,
            envelope=_envelope(tmp_path),
        ),
    )
    values = await _prepared_values(lifecycle=lifecycle, bundle=bundle, executor=executor)

    assert sorted((first, second)) == [False, True]
    assert tuple(values["execution_trace"]).count("topic_planning") == 1
    assert (await lifecycle.read_state(bundle)).generation == 1


@pytest.mark.asyncio
async def test_root_loss_before_checkpoint_preparation_is_unavailable_and_never_recreates_the_bundle(
    tmp_path: Path,
) -> None:
    """REG-021: a held transition lease never writes through a detached Bundle root."""

    lifecycle: BundleLifecycle
    bundle: RunBundleRef

    def remove_root(point: str) -> None:
        if point == "before_refinement_checkpoint_preparation":
            shutil.rmtree(lifecycle.private_root(bundle))

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path, fault_hook=remove_root)
    bundle = await _start_fixture(lifecycle)
    executor = _fixture_executor(tmp_path)
    await _stage_terminal(lifecycle=lifecycle, bundle=bundle, executor=executor)
    original = await _admit(lifecycle=lifecycle, bundle=bundle)

    with pytest.raises(BundleLifecycleError, match="bundle_unavailable"):
        await executor.prepare_refinement_round(
            lifecycle=lifecycle,
            scope=_SCOPE,
            bundle=bundle,
            submitted_operation=original,
        )
    assert not lifecycle.private_root(bundle).exists()
