"""Orphan resume contracts: a process-death orphan continues from its checkpoint.

@impl REG-023
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from deerflow_deep_research.domain.lifecycle import LifecycleAction
from deerflow_deep_research.runtime.bundle_control import BundleControl
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle

BUNDLE_ID = "b_" + "A" * 43


class _StubExecutor:
    """Record which control path runs; never touches a real graph."""

    def __init__(self, policy: object) -> None:
        self.full_rerun_policy = policy
        self.calls: list[str] = []

    async def continue_run(self, **_kwargs: object) -> dict[str, object]:
        self.calls.append("continue")
        return {"stub": "continued"}

    async def resume(self, **_kwargs: object) -> dict[str, object]:
        self.calls.append("resume")
        return {"stub": "resumed"}


def _envelope() -> SimpleNamespace:
    return SimpleNamespace()


@pytest.mark.asyncio
async def test_orphan_resume_with_no_messages_continues_from_checkpoint(tmp_path) -> None:
    """@impl REG-023
    @bug BUG-064

    A resume action with no human messages on an orphaned bundle (active, no
    pending request) continues from the durable checkpoint: the executor's
    continue path runs and no human response is constructed.
    """

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    executor = _StubExecutor(policy=lifecycle.rerun_policy)
    control = BundleControl(lifecycle=lifecycle, graph_executor=executor)
    bundle = await lifecycle.start(
        scope=("alice", "thread-1"),
        request_text="Continue a stalled research run.",
        implementation_mode="all_real",
    )

    result = await control.dispatch(
        action=LifecycleAction.RESUME,
        effective_user_id="alice",
        outer_thread_id="thread-1",
        messages=[],
        tool_call_id="call-1",
        bundle_id=bundle.bundle_id.value,
        envelope=_envelope(),
    )

    assert executor.calls == ["continue"]
    assert result == {"stub": "continued"}


@pytest.mark.asyncio
async def test_waiting_bundle_with_no_messages_does_not_continue(tmp_path) -> None:
    """@impl REG-023 — a bundle awaiting human input keeps the answer contract.

    An empty resume on a pending-input bundle must not fabricate a continue:
    the continue path is exclusive to the orphan shape (no pending request),
    and the empty answer surfaces as the existing response-invalid result.
    """
    from dataclasses import replace as dc_replace

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    executor = _StubExecutor(policy=lifecycle.rerun_policy)
    bundle = await lifecycle.start(
        scope=("alice", "thread-1"),
        request_text="Await a bounded human answer.",
        implementation_mode="all_real",
    )
    await lifecycle._mutate_state(
        bundle,
        lambda state: dc_replace(state, pending_request_id="req-1", waiting_for="hitl1"),
    )
    control = BundleControl(lifecycle=lifecycle, graph_executor=executor)

    result = await control.dispatch(
        action=LifecycleAction.RESUME,
        effective_user_id="alice",
        outer_thread_id="thread-1",
        messages=[],
        tool_call_id="call-1",
        bundle_id=bundle.bundle_id.value,
        envelope=_envelope(),
    )

    assert executor.calls == []  # neither continue nor resume without an answer
    assert isinstance(result, dict)
    assert result.get("pending_input") is not None


async def test_executor_continue_run_reenters_checkpoint_without_a_response(tmp_path) -> None:
    """@impl REG-023 — the executor re-entry uses no resume command payload.

    The continue variant re-enters the persisted checkpoint graph with no
    input (never a fabricated human response), under the execution exclusion
    lease, and projects through the normal resume projection.
    """

    class _RecordingGraph:
        def __init__(self) -> None:
            self.inputs: list[object] = []

        async def aget_state(self, _config):
            return SimpleNamespace(values={"phase": "wave1"})

        async def ainvoke(self, raw_input, config=None, context=None):
            self.inputs.append(raw_input)
            return {}

    graph = _RecordingGraph()

    class _Builder:
        def compile(self, checkpointer=None):
            return graph

    class _Recipe:
        builder = _Builder()

    from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(
        scope=("alice", "thread-1"),
        request_text="Continue a stalled research run.",
        implementation_mode="all_real",
    )
    executor = BundleGraphExecutor(recipe=_Recipe())

    async def _fake_project(**_kwargs):
        return {"stub": "projected"}

    async def _fake_journal_envelope(**_kwargs):
        return SimpleNamespace()

    async def _fake_refinement_continue(**_kwargs):
        return {"stub": True}

    async def _fake_context(**_kwargs):
        return SimpleNamespace()

    executor._project = _fake_project  # type: ignore[method-assign]
    executor._context = _fake_context  # type: ignore[method-assign]
    executor._journal_envelope = _fake_journal_envelope  # type: ignore[method-assign]
    executor._continue_completed_refinement_if_eligible = _fake_refinement_continue  # type: ignore[method-assign]

    result = await executor.continue_run(
        lifecycle=lifecycle,
        bundle=bundle,
        envelope=SimpleNamespace(),
        tool_call_id="call-1",
    )

    assert graph.inputs == [None]  # continue input, never a fabricated response
    assert result == {"stub": True}  # refinement-continue tail owns the final result
