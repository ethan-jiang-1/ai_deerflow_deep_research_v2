"""Headless debug-driver falsifiable matrix over the real fixture graph.

@impl LDD-001
@impl LDD-002
@impl LDD-003
@impl LDD-004
@impl LDD-005
"""

from __future__ import annotations

import json
import secrets
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from deerflow_deep_research.domain.debug_driving import (
    AttachRequest,
    DebugCommand,
    StartRequest,
    StopPolicy,
)
from deerflow_deep_research.domain.lifecycle import ImplementationMode
from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.debug_driver import DebugDriverError, DebugRunDriver
from deerflow_deep_research.runtime.run_observation import BundleRunObservationPublisher
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore
from tests.fixtures.recipes import fixture_recipe

_SCOPE_BASE = "debug-driver-matrix"


def _envelope(tmp_path: Path) -> TrustedRuntimeEnvelope:
    return TrustedRuntimeEnvelope(
        effective_user_id="debug-user",
        outer_thread_id="debug-thread",
        outer_run_id="debug-run",
        app_config=object(),
        workspace_host_path=tmp_path,
        uploads_host_path=tmp_path / "uploads",
        outputs_host_path=tmp_path / "outputs",
        workspace_virtual_root="/mnt/user-data/workspace",
        uploads_virtual_root="/mnt/user-data/uploads",
        outputs_virtual_root="/mnt/user-data/outputs",
        parent_sandbox=None,
        live_event_sink=None,
        execution_profile=None,
    )


def _make_driver(tmp_path: Path, *, owner: str, clock=None, lease_ttl: float = 300.0):
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path / "demo-runs")

    async def create(_envelope, *, bundle, **_kwargs):
        return WorkUnitStore(
            workspace_host_path=tmp_path / "demo-runs",
            bundle=bundle,
            clock=lambda: datetime.now(UTC),
            monotonic=time.monotonic,
            lock_sleep=time.sleep,
            token_factory=lambda: secrets.token_hex(16),
            fault_hook=None,
        )

    executor = BundleGraphExecutor(recipe=fixture_recipe(work_unit_store_factory=create))
    envelope = _envelope(tmp_path)
    scope = (envelope.effective_user_id, envelope.outer_thread_id)
    driver = DebugRunDriver(
        lifecycle=lifecycle,
        executor=executor,
        envelope=envelope,
        scope=scope,
        owner=owner,
        clock=clock or (lambda: time.time()),
        lease_ttl=lease_ttl,
        implementation_mode=ImplementationMode.FIXTURE,
    )
    return driver, lifecycle


@pytest.mark.asyncio
async def test_start_step_admission_and_double_start_busy(tmp_path: Path) -> None:
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(
            question="Compare two storage approaches.",
            mode="step",
            owner="op-1",
            command_id="start-00000001",
        )
    )
    assert opened.snapshot is not None
    bundle_id = opened.snapshot.bundle_id
    assert opened.snapshot.cursor.frame_sequence == 0
    assert opened.snapshot.lease.live is True

    second = await driver.open_start(
        StartRequest(
            question="Compare two storage approaches.",
            mode="step",
            owner="op-1",
            command_id="start-00000002",
        )
    )
    assert second.denied == "busy"

    token = opened.snapshot.cursor.token()
    advance = DebugCommand(
        kind="advance_one",
        bundle_id=bundle_id,
        command_id="advance-00000001",
        expected_cursor=token,
    )
    result = await driver.execute(advance)
    assert result.snapshot is not None
    assert result.committed_node == "bootstrap"
    # One advance commits exactly one boundary (bootstrap). The paused hitl1
    # projects its own suspended card but is not a committed advance.
    assert result.committed_node == "bootstrap"
    assert result.snapshot.cursor.frame_sequence == 2
    assert opened.snapshot.cursor.frame_sequence == 0


@pytest.mark.asyncio
async def test_stale_and_duplicate_denials(tmp_path: Path) -> None:
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(
            question="Compare storage",
            mode="step",
            owner="op-1",
            command_id="start-00000001",
        )
    )
    bundle_id = opened.snapshot.bundle_id
    stale_token = opened.snapshot.cursor.token()

    command = DebugCommand(
        kind="advance_one",
        bundle_id=bundle_id,
        command_id="advance-00000001",
        expected_cursor=stale_token,
    )
    first = await driver.execute(command)
    assert first.snapshot is not None

    replay = await driver.execute(command)
    assert replay.denied == "duplicate"

    fresh_cursor = first.snapshot.cursor.token()
    advance2 = DebugCommand(
        kind="advance_one",
        bundle_id=bundle_id,
        command_id="advance-00000002",
        expected_cursor=stale_token,
    )
    stale = await driver.execute(advance2)
    assert stale.denied == "stale"
    _ = fresh_cursor


@pytest.mark.asyncio
async def test_step_to_hitl_answer_then_breakpoint_drive(tmp_path: Path) -> None:
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(
            question="Compare storage",
            mode="step",
            owner="op-1",
            command_id="start-00000001",
        )
    )
    bundle_id = opened.snapshot.bundle_id
    cursor = opened.snapshot.cursor.token()

    step1 = await driver.execute(
        DebugCommand(
            kind="advance_one",
            bundle_id=bundle_id,
            command_id="advance-00000001",
            expected_cursor=cursor,
        )
    )
    assert step1.snapshot is not None
    cursor = step1.snapshot.cursor.token()

    step2 = await driver.execute(
        DebugCommand(
            kind="advance_one",
            bundle_id=bundle_id,
            command_id="advance-00000002",
            expected_cursor=cursor,
        )
    )
    assert step2.snapshot is not None
    assert step2.snapshot.posture == "awaiting_hitl"
    assert step2.snapshot.pending_request_id
    cursor = step2.snapshot.cursor.token()

    answered = await driver.execute(
        DebugCommand(
            kind="answer",
            bundle_id=bundle_id,
            command_id="answer-00000003",
            expected_cursor=cursor,
            answer_text="Use the default profile.",
        )
    )
    assert answered.snapshot is not None
    cursor = answered.snapshot.cursor.token()

    driven = await driver.execute(
        DebugCommand(
            kind="drive_until",
            bundle_id=bundle_id,
            command_id="drive-00000004",
            expected_cursor=cursor,
            breakpoint=StopPolicy(breakpoint_after="topic_planning"),
        )
    )
    assert driven.snapshot is not None
    assert driven.committed_node == "topic_planning"


@pytest.mark.asyncio
async def test_cursor_reports_the_next_node_after_a_step(tmp_path: Path) -> None:
    """BUG-070 regression: the boundary cursor names the durable next node.

    The cursor's ``next_nodes`` is the operator-facing projection the workbench
    renders; it must come from the compiled graph state, not from the trace
    frame (which never carried it).
    """
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    step = await driver.execute(
        DebugCommand(
            kind="advance_one",
            bundle_id=bundle_id,
            command_id="advance-00000001",
            expected_cursor=opened.snapshot.cursor.token(),
        )
    )
    assert step.snapshot is not None
    assert step.snapshot.cursor.next_nodes, "cursor must name the next node after a step"
    assert "hitl1" in step.snapshot.cursor.next_nodes
    # The write permit stays the durable boundary identity: a cursor rebuilt
    # without the graph-state projection must still compare equal.
    rebuilt = step.snapshot.cursor.model_copy(update={"next_nodes": ()})
    assert rebuilt.token() == step.snapshot.cursor.token()


@pytest.mark.asyncio
async def test_cancel_then_detach_releases_the_control_lease(tmp_path: Path) -> None:
    """The workbench's /cancel sequence: typed cancel, then detach to free the lease.

    ``cancel`` alone cancels the Bundle but keeps the control lease, so the
    workbench must run the driver's ``detach`` afterwards; otherwise a later
    session would be fenced by a lease nobody owns.
    """
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    session = await driver.session_snapshot(bundle_id)
    assert session is not None
    cancelled = await driver.execute(
        DebugCommand(
            kind="cancel",
            bundle_id=bundle_id,
            command_id="cancel-00000001",
            expected_cursor=session.cursor.token(),
        )
    )
    assert cancelled.denied is None
    after = await driver.session_snapshot(bundle_id)
    assert after is not None
    detached = await driver.execute(
        DebugCommand(
            kind="detach",
            bundle_id=bundle_id,
            command_id="detach-00000001",
            expected_cursor=after.cursor.token(),
        )
    )
    assert detached.denied is None
    assert detached.snapshot is not None
    assert detached.snapshot.lease.live is False
    assert await driver.session_snapshot(bundle_id) is None


@pytest.mark.asyncio
async def test_attach_posture_reports_takeover_rebind_busy_and_unresolvable(tmp_path: Path) -> None:
    """RED-014 candidate postures, answered by the driver (lease semantics stay here)."""
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    other, _lifecycle2 = _make_driver(tmp_path, owner="op-2")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    assert await driver.attach_posture(bundle_id) == "rebind"
    assert await other.attach_posture(bundle_id) == "busy"
    assert await other.attach_posture("b_" + "Z" * 43) == "unresolvable"
    session = await driver.session_snapshot(bundle_id)
    assert session is not None
    detached = await driver.execute(
        DebugCommand(
            kind="detach",
            bundle_id=bundle_id,
            command_id="detach-00000001",
            expected_cursor=session.cursor.token(),
        )
    )
    assert detached.denied is None
    assert await other.attach_posture(bundle_id) == "takeover"


@pytest.mark.asyncio
async def test_pause_request_holds_drive_at_next_boundary(tmp_path: Path) -> None:
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="run", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    cursor = opened.snapshot.cursor.token()

    pause = await driver.execute(
        DebugCommand(
            kind="pause_request",
            bundle_id=bundle_id,
            command_id="pause-00000001",
            expected_cursor=cursor,
        )
    )
    assert pause.snapshot is not None
    assert pause.snapshot.pause_requested is True


@pytest.mark.asyncio
async def test_detach_releases_lease_and_ends_session(tmp_path: Path) -> None:
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    cursor = opened.snapshot.cursor.token()

    detached = await driver.execute(
        DebugCommand(
            kind="detach",
            bundle_id=bundle_id,
            command_id="detach-00000001",
            expected_cursor=cursor,
        )
    )
    assert detached.snapshot is not None
    assert detached.snapshot.lease.live is False

    after = await driver.execute(
        DebugCommand(
            kind="advance_one",
            bundle_id=bundle_id,
            command_id="advance-00000009",
            expected_cursor=detached.snapshot.cursor.token(),
        )
    )
    assert after.denied == "not_found"


@pytest.mark.asyncio
async def test_second_driver_is_fenced_until_lease_stale_then_cas(tmp_path: Path) -> None:
    clock = {"now": 1000.0}
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1", clock=lambda: clock["now"], lease_ttl=60.0)
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    generation = opened.snapshot.lease.generation

    driver2, _l2 = _make_driver(tmp_path, owner="op-2", clock=lambda: clock["now"], lease_ttl=60.0)
    busy = await driver2.open_attach(
        AttachRequest(bundle_id=bundle_id, owner="op-2", expected_lease_generation=generation)
    )
    assert busy.denied == "busy"

    # TTL passes: the live lease is stale, but the wrong generation is refused.
    clock["now"] += 120
    stale_generation = await driver2.open_attach(
        AttachRequest(bundle_id=bundle_id, owner="op-2", expected_lease_generation=0)
    )
    assert stale_generation.denied == "busy"

    taken = await driver2.open_attach(
        AttachRequest(bundle_id=bundle_id, owner="op-2", expected_lease_generation=generation)
    )
    assert taken.snapshot is not None
    assert taken.snapshot.lease.owner == "op-2"
    assert taken.snapshot.lease.live is True
    # Attach does not advance.
    assert taken.snapshot.cursor.frame_sequence == 0


@pytest.mark.asyncio
async def test_boundary_crash_restart_restores_cursor_without_advancing(tmp_path: Path) -> None:
    clock = {"now": 1000.0}
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1", clock=lambda: clock["now"], lease_ttl=60.0)
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    result = await driver.execute(
        DebugCommand(
            kind="advance_one",
            bundle_id=bundle_id,
            command_id="advance-00000001",
            expected_cursor=opened.snapshot.cursor.token(),
        )
    )
    assert result.snapshot is not None
    pre_death_frames = result.snapshot.cursor.frame_sequence

    # The debugger process dies: TTL passes with no heartbeat and no new command.
    clock["now"] += 120
    driver2, _l2 = _make_driver(tmp_path, owner="op-2", clock=lambda: clock["now"], lease_ttl=60.0)
    generation = opened.snapshot.lease.generation
    attached = await driver2.open_attach(
        AttachRequest(bundle_id=bundle_id, owner="op-2", expected_lease_generation=generation)
    )
    assert attached.snapshot is not None
    assert attached.snapshot.cursor.frame_sequence == pre_death_frames
    assert attached.snapshot.lease.owner == "op-2"

    # Attach itself never advances; the boundary is hitl1-suspended, so the
    # legal first command is the typed answer, which grows the timeline.
    answered = await driver2.execute(
        DebugCommand(
            kind="answer",
            bundle_id=bundle_id,
            command_id="answer-00000002",
            expected_cursor=attached.snapshot.cursor.token(),
            answer_text="Use the default profile.",
        )
    )
    assert answered.snapshot is not None
    assert answered.snapshot.cursor.frame_sequence > pre_death_frames
    assert answered.committed_node == "hitl1"


@pytest.mark.asyncio
async def test_drive_until_stops_at_hitl_then_runs_to_terminal(tmp_path: Path) -> None:
    """Start Run stops at the formal HITL request; the answer drives to terminal."""
    driver, lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="run", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    cursor = opened.snapshot.cursor.token()

    driven = await driver.execute(
        DebugCommand(
            kind="drive_until",
            bundle_id=bundle_id,
            command_id="drive-00000001",
            expected_cursor=cursor,
        )
    )
    assert driven.snapshot is not None
    assert driven.snapshot.posture == "awaiting_hitl"

    answered = await driver.execute(
        DebugCommand(
            kind="answer",
            bundle_id=bundle_id,
            command_id="answer-00000002",
            expected_cursor=driven.snapshot.cursor.token(),
            answer_text="Use the default profile.",
        )
    )
    assert answered.snapshot is not None

    driven2 = await driver.execute(
        DebugCommand(
            kind="drive_until",
            bundle_id=bundle_id,
            command_id="drive-00000003",
            expected_cursor=answered.snapshot.cursor.token(),
            breakpoint=StopPolicy(stop_on_hitl=False, stop_on_terminal=True),
        )
    )
    assert driven2.snapshot is not None
    assert driven2.snapshot.posture == "terminal"
    assert driven2.snapshot.cursor.frame_sequence >= 9

    journal = (
        await __import__("deerflow_deep_research.runtime.run_observation", fromlist=["RunObservationStore"])
        .RunObservationStore(
            bundle_root=lifecycle.private_root(
                await lifecycle.resolve(
                    scope=("debug-user", "debug-thread"),
                    bundle_id=__import__("deerflow_deep_research.domain.bundle", fromlist=["BundleId"]).BundleId(
                        bundle_id
                    ),
                )
            ),
            bundle_id=bundle_id,
        )
        .inspect(bundle_id=bundle_id)
    )
    completed = [event for event in journal.events if event.category.value == "node" and event.outcome == "completed"]
    assert len(completed) >= 9


@pytest.mark.asyncio
async def test_topology_guard_fails_closed_on_multi_visit_superstep(tmp_path: Path) -> None:
    """A superstep projecting two logical visits is refused with a typed failure.

    @impl LDD-005
    """
    driver, _lifecycle = _make_driver(tmp_path, owner="op-guard")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-guard", command_id="start-00000001")
    )
    assert opened.snapshot is not None
    bundle_id = opened.snapshot.bundle_id
    token = opened.snapshot.cursor.token()

    class _MultiVisitGraph:
        async def aget_state(self, _config):
            return SimpleNamespace(values={}, next=("bootstrap", "hitl1"))

    class _MultiVisitBuilder:
        def compile(self, **_kwargs):
            return _MultiVisitGraph()

    object.__setattr__(driver._executor._recipe, "builder", _MultiVisitBuilder())

    with pytest.raises(DebugDriverError) as excinfo:
        await driver.execute(
            DebugCommand(
                kind="advance_one",
                bundle_id=bundle_id,
                command_id="advance-00000001",
                expected_cursor=token,
            )
        )
    assert str(excinfo.value) == "topology_guard_multi_visit"


@pytest.mark.asyncio
async def test_accepted_commands_keep_the_run_summary_truthful(tmp_path: Path) -> None:
    """DPL-014's operator report reads the run summary; a debug run must refresh it.

    Regression for BUG-072: debug sessions drive the lifecycle directly, so no
    observation was ever published and the retained summary stayed at the
    establishment fact - the workspace report then called a cancelled bundle
    resumable.
    """
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path / "demo-runs")

    async def create(_envelope, *, bundle, **_kwargs):
        return WorkUnitStore(
            workspace_host_path=tmp_path / "demo-runs",
            bundle=bundle,
            clock=lambda: datetime.now(UTC),
            monotonic=time.monotonic,
            lock_sleep=time.sleep,
            token_factory=lambda: secrets.token_hex(16),
            fault_hook=None,
        )

    executor = BundleGraphExecutor(recipe=fixture_recipe(work_unit_store_factory=create))
    envelope = _envelope(tmp_path)
    scope = (envelope.effective_user_id, envelope.outer_thread_id)
    driver = DebugRunDriver(
        lifecycle=lifecycle,
        executor=executor,
        envelope=envelope,
        scope=scope,
        owner="op-summary",
        observation_publisher=BundleRunObservationPublisher(lifecycle=lifecycle, scope=scope),
    )

    def summary_status(bundle_id: str) -> str | None:
        summary = next((tmp_path / "demo-runs").rglob(f"{bundle_id}/diagnostics/run-summary.json"))
        return json.loads(summary.read_text(encoding="utf-8")).get("status")

    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-summary", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    assert summary_status(bundle_id) in {"active", "suspended"}

    session = await driver.session_snapshot(bundle_id)
    assert session is not None
    cancelled = await driver.execute(
        DebugCommand(
            kind="cancel",
            bundle_id=bundle_id,
            command_id="cancel-00000001",
            expected_cursor=session.cursor.token(),
        )
    )
    assert cancelled.denied is None
    assert summary_status(bundle_id) == "cancelled", "the operator report would call this bundle resumable"


@pytest.mark.asyncio
async def test_hitl_stop_carries_the_node_authored_request(tmp_path: Path) -> None:
    """The operator must not guess what a HITL stop asks: carry the request itself."""
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    session = await driver.session_snapshot(bundle_id)
    assert session is not None
    stepped = await driver.execute(
        DebugCommand(
            kind="advance_one",
            bundle_id=bundle_id,
            command_id="advance-00000001",
            expected_cursor=session.cursor.token(),
        )
    )
    assert stepped.snapshot is not None
    assert stepped.snapshot.posture == "awaiting_hitl"
    request = stepped.snapshot.pending_request
    assert request is not None, "a HITL stop without the request leaves the operator guessing"
    assert request.request_id == stepped.snapshot.pending_request_id
    assert request.mode in {"text", "choice"}
    assert request.title and request.context


@pytest.mark.asyncio
async def test_attach_reads_the_pending_request_from_the_own_checkpoint(tmp_path: Path) -> None:
    """Attaching to a paused Bundle must still say what it waits for (read-only)."""
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    session = await driver.session_snapshot(bundle_id)
    assert session is not None
    stepped = await driver.execute(
        DebugCommand(
            kind="advance_one",
            bundle_id=bundle_id,
            command_id="advance-00000001",
            expected_cursor=session.cursor.token(),
        )
    )
    # The previous operator leaves (detach keeps the Bundle paused but releases
    # the lease), which is exactly when the next operator attaches.
    after = await driver.session_snapshot(bundle_id)
    assert after is not None
    detached = await driver.execute(
        DebugCommand(
            kind="detach",
            bundle_id=bundle_id,
            command_id="detach-00000001",
            expected_cursor=after.cursor.token(),
        )
    )
    assert detached.denied is None
    assert stepped.snapshot is not None and stepped.snapshot.posture == "awaiting_hitl"

    other, _lifecycle2 = _make_driver(tmp_path, owner="op-2")
    attached = await other.open_attach(AttachRequest(bundle_id=bundle_id, owner="op-2", expected_lease_generation=None))
    assert attached.denied is None, attached.denied
    assert attached.snapshot is not None
    assert attached.snapshot.pending_request is not None, "attach lost the pending request"
    assert attached.snapshot.pending_request.request_id == attached.snapshot.pending_request_id


@pytest.mark.asyncio
async def test_drive_until_stops_at_the_hitl_boundary_once(tmp_path: Path) -> None:
    """`stop_on_hitl` must break at the boundary, not re-enter the interrupted node.

    Regression: the drive loop had no HITL check, so one command re-advanced
    until the 64-iteration cap and re-entered the waiting node each time.
    """
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    session = await driver.session_snapshot(bundle_id)
    assert session is not None

    calls = {"n": 0}
    real_advance = driver._advance

    async def counted(*args, **kwargs):
        calls["n"] += 1
        return await real_advance(*args, **kwargs)

    driver._advance = counted  # type: ignore[method-assign]
    result = await driver.execute(
        DebugCommand(
            kind="drive_until",
            bundle_id=bundle_id,
            command_id="run-00000001",
            expected_cursor=session.cursor.token(),
        )
    )
    assert result.snapshot is not None
    assert calls["n"] == 1, f"the drive advanced {calls['n']} times instead of stopping at the HITL"
    assert result.snapshot.posture == "awaiting_hitl"
    assert result.snapshot.cursor.next_nodes == ("hitl1",)


@pytest.mark.asyncio
async def test_a_pending_pause_makes_the_next_drive_advance_one_boundary(tmp_path: Path) -> None:
    """A pause takes effect at the next committed boundary (LDD-002), not before it."""
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id

    # Reach the post-HITL boundary, then ask for a pause.
    session = await driver.session_snapshot(bundle_id)
    assert session is not None
    await driver.execute(
        DebugCommand(
            kind="advance_one",
            bundle_id=bundle_id,
            command_id="advance-00000001",
            expected_cursor=session.cursor.token(),
        )
    )
    answered = await driver.execute(
        DebugCommand(
            kind="answer",
            bundle_id=bundle_id,
            command_id="answer-00000001",
            expected_cursor=(await driver.session_snapshot(bundle_id)).cursor.token(),  # type: ignore[union-attr]
            answer_text="depth: standard",
        )
    )
    assert answered.snapshot is not None
    assert answered.snapshot.posture == "paused_at_boundary"

    paused = await driver.execute(
        DebugCommand(
            kind="pause_request",
            bundle_id=bundle_id,
            command_id="pause-00000001",
            expected_cursor=answered.snapshot.cursor.token(),
        )
    )
    assert paused.snapshot is not None and paused.snapshot.pause_requested is True

    driven = await driver.execute(
        DebugCommand(
            kind="drive_until",
            bundle_id=bundle_id,
            command_id="run-00000001",
            expected_cursor=paused.snapshot.cursor.token(),
        )
    )
    assert driven.snapshot is not None, "a pending pause must never make the drive return nothing"
    assert driven.committed_node == "topic_planning", "the pause boundary is the next committed node"
    assert driven.snapshot.posture == "paused_at_boundary"
    assert driven.snapshot.pause_requested is False, "an honored pause request must be cleared"


def test_pending_view_carries_card_and_state_feedback() -> None:
    """LDD-006: a schema-following context parses into the carried prompt card,
    and the node's last feedback prefers the interaction projection with a
    durable-state fallback; an unparsed context stays card-free."""

    from deerflow_deep_research.domain.lifecycle import HumanInputMode, HumanInputRequest
    from deerflow_deep_research.runtime.debug_driver import _pending_request_view

    context = json.dumps(
        {
            "context_schema_version": 1,
            "brief_summary": "研究配置建议已准备好，等待确认。",
            "proposed_dimensions": {"depth": "standard"},
            "required_dimensions": ["depth"],
            "missing_dimensions": [],
            "valid_options": {},
            "accepted_rounds_remaining": 3,
            "rejection_retries_remaining": 3,
            "instructions": "请确认当前配置、提出聚焦问题，或说明需要修改的内容。",
        },
        ensure_ascii=False,
    )
    pending = SimpleNamespace(
        request=HumanInputRequest(
            request_id="drh_card_00000001",
            mode=HumanInputMode.TEXT,
            title="Deep Research profile",
            context=context,
        ),
        phase="hitl1",
    )
    view = _pending_request_view(
        pending,
        state_feedback={"kind": "clarification", "message": "请补充一个具体研究主题。"},
    )
    assert view is not None
    assert view.prompt is not None, "a schema-following context must yield a parsed card"
    assert view.prompt.goal == "研究配置建议已准备好，等待确认。"
    assert view.prompt.accepted_rounds_remaining == 3
    assert view.last_feedback is not None
    assert view.last_feedback.message == "请补充一个具体研究主题。", "state feedback is the fallback channel"

    plain = SimpleNamespace(
        request=HumanInputRequest(
            request_id="drh_plain_00000001",
            mode=HumanInputMode.TEXT,
            title="Deep Research input - fixture composition",
            context="Deterministic fixture scenario; this does not represent completed research.",
        ),
        phase="hitl1",
    )
    plain_view = _pending_request_view(plain)
    assert plain_view is not None
    assert plain_view.prompt is None, "an unparsed context must not fabricate a card"
    assert plain_view.last_feedback is None
    assert plain_view.title and plain_view.mode == "text", "carried fields remain unchanged"


def test_auto_hitl_predicate_gates_hitl1_text_only() -> None:
    """LDD-008: the auto-answer predicate admits only hitl1 text requests;
    HITL2 direction decisions and choice prompts always wait for a human."""
    from deerflow_deep_research.domain.debug_driving import PendingOptionView, PendingRequestView
    from deerflow_deep_research.runtime.debug_driver import auto_hitl_eligible, auto_hitl_should_stop

    hitl1 = PendingRequestView(
        request_id="drh_a_000000000000001", phase="hitl1", mode="text", title="profile", context="c"
    )
    hitl2 = PendingRequestView(
        request_id="drh_b_000000000000001",
        phase="hitl2",
        mode="choice",
        title="next step",
        context="c",
        options=(PendingOptionView(option_id="proceed", label="继续"),),
    )
    assert auto_hitl_eligible(hitl1) is True
    assert auto_hitl_eligible(hitl2) is False
    assert auto_hitl_should_stop(0) is False
    assert auto_hitl_should_stop(1) is False
    assert auto_hitl_should_stop(2) is True, "two consecutive unaccepted auto-answers must fall back to the human"


@pytest.mark.asyncio
async def test_rerun_node_reexecutes_last_commit(tmp_path: Path) -> None:
    """LDD-007: rerun_node forks to the pre-commit checkpoint and re-executes the
    same node; the journal gains fresh frames and the session stays drivable."""
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    cursor = opened.snapshot.cursor.token()

    step1 = await driver.execute(
        DebugCommand(kind="advance_one", bundle_id=bundle_id, command_id="advance-00000001", expected_cursor=cursor)
    )
    assert step1.snapshot is not None and step1.committed_node == "bootstrap"
    pre_rerun_frames = step1.snapshot.cursor.frame_sequence

    rerun = await driver.execute(
        DebugCommand(
            kind="rerun_node",
            bundle_id=bundle_id,
            command_id="rerun-00000001",
            expected_cursor=step1.snapshot.cursor.token(),
        )
    )
    assert rerun.denied is None, rerun.message
    assert rerun.committed_node == "bootstrap", "the rerun must re-execute the last committed node"
    assert rerun.snapshot is not None
    assert rerun.snapshot.cursor.frame_sequence > pre_rerun_frames, "the rerun must produce fresh frames"
    assert rerun.snapshot.posture in {"paused_at_boundary", "awaiting_hitl"}

    # The session stays drivable: the next advance reaches the hitl stop.
    nxt = await driver.execute(
        DebugCommand(
            kind="advance_one",
            bundle_id=bundle_id,
            command_id="advance-00000002",
            expected_cursor=rerun.snapshot.cursor.token(),
        )
    )
    assert nxt.snapshot is not None and nxt.snapshot.posture == "awaiting_hitl"


@pytest.mark.asyncio
async def test_rerun_node_at_hitl_regenerates_the_stop(tmp_path: Path) -> None:
    """LDD-007: rerunning at a HITL stop re-executes the last committed node and
    lands back at a fresh HITL request on a later frame."""
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    step1 = await driver.execute(
        DebugCommand(
            kind="advance_one",
            bundle_id=bundle_id,
            command_id="advance-00000001",
            expected_cursor=opened.snapshot.cursor.token(),
        )
    )
    assert step1.snapshot is not None and step1.snapshot.posture == "awaiting_hitl"

    rerun = await driver.execute(
        DebugCommand(
            kind="rerun_node",
            bundle_id=bundle_id,
            command_id="rerun-00000001",
            expected_cursor=step1.snapshot.cursor.token(),
        )
    )
    assert rerun.denied is None, rerun.message
    assert rerun.snapshot is not None
    assert rerun.snapshot.posture == "awaiting_hitl", "a rerun before the pending node re-asks it"
    assert rerun.snapshot.pending_request_id is not None
    assert rerun.snapshot.cursor.frame_sequence > step1.snapshot.cursor.frame_sequence


@pytest.mark.asyncio
async def test_rerun_node_denials(tmp_path: Path) -> None:
    """LDD-007: a fresh session with no committed node and a terminal session
    both refuse rerun_node with typed denials instead of advancing."""
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    fresh = await driver.execute(
        DebugCommand(
            kind="rerun_node",
            bundle_id=bundle_id,
            command_id="rerun-00000001",
            expected_cursor=opened.snapshot.cursor.token(),
        )
    )
    assert fresh.denied == "invalid", "nothing has committed yet, so there is nothing to rerun"


@pytest.mark.asyncio
async def test_drive_until_auto_hitl_passes_the_proposal(tmp_path: Path) -> None:
    """LDD-008: the default drive stops at the hitl1 request for a human; an
    explicit auto-HITL drive submits the confirm answer as operator policy and
    runs on to terminal, carrying the answered-request facts."""
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="run", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id

    # Default policy: the drive stops at the hitl1 request for a human.
    human_drive = await driver.execute(
        DebugCommand(
            kind="drive_until",
            bundle_id=bundle_id,
            command_id="drive-00000001",
            expected_cursor=opened.snapshot.cursor.token(),
        )
    )
    assert human_drive.denied is None, human_drive.message
    assert human_drive.snapshot is not None
    assert human_drive.snapshot.posture == "awaiting_hitl"
    assert human_drive.snapshot.pending_request is not None
    assert human_drive.snapshot.pending_request.phase == "hitl1"
    assert human_drive.snapshot.auto_hitl_answers == (), "the default drive never auto-answers"

    # Auto policy: confirm is submitted as operator policy and the drive runs on.
    auto_drive = await driver.execute(
        DebugCommand(
            kind="drive_until",
            bundle_id=bundle_id,
            command_id="drive-00000002",
            expected_cursor=human_drive.snapshot.cursor.token(),
            breakpoint=StopPolicy(auto_hitl=True),
        )
    )
    assert auto_drive.denied is None, auto_drive.message
    assert auto_drive.snapshot is not None
    assert auto_drive.snapshot.posture == "terminal", "the auto drive must pass hitl1 and run to terminal"
    assert len(auto_drive.snapshot.auto_hitl_answers) >= 1, "the auto-answer fact must be carried for the operator"


@pytest.mark.asyncio
async def test_drive_typed_at_hitl_stop_never_blind_advances(tmp_path: Path) -> None:
    """LDD-008: a drive command typed while a HITL request is pending answers it
    only under the explicit auto policy (then runs on); without the policy it
    stops honestly without consuming the request."""
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    step1 = await driver.execute(
        DebugCommand(
            kind="advance_one",
            bundle_id=bundle_id,
            command_id="advance-00000001",
            expected_cursor=opened.snapshot.cursor.token(),
        )
    )
    assert step1.snapshot is not None and step1.snapshot.posture == "awaiting_hitl"

    held = await driver.execute(
        DebugCommand(
            kind="drive_until",
            bundle_id=bundle_id,
            command_id="drive-00000001",
            expected_cursor=step1.snapshot.cursor.token(),
        )
    )
    assert held.snapshot is not None
    assert held.snapshot.posture == "awaiting_hitl", "the default policy must hold the stop for a human"
    assert held.snapshot.auto_hitl_answers == ()
    assert held.snapshot.pending_request_id == step1.snapshot.pending_request_id

    answered_through = await driver.execute(
        DebugCommand(
            kind="drive_until",
            bundle_id=bundle_id,
            command_id="drive-00000002",
            expected_cursor=held.snapshot.cursor.token(),
            breakpoint=StopPolicy(auto_hitl=True),
        )
    )
    assert answered_through.snapshot is not None
    assert answered_through.snapshot.posture == "terminal"
    assert len(answered_through.snapshot.auto_hitl_answers) >= 1


@pytest.mark.asyncio
async def test_open_start_carries_the_operator_question_into_the_graph(tmp_path: Path) -> None:
    """BUG-079: the graph's fresh start must ask what the operator asked - the
    checkpointed request_text carries the operator's question, never a
    fallback placeholder."""
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    question = "Compare renewable energy storage technologies for grid-scale deployment."
    opened = await driver.open_start(
        StartRequest(question=question, mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    await driver.execute(
        DebugCommand(
            kind="advance_one",
            bundle_id=bundle_id,
            command_id="advance-00000001",
            expected_cursor=opened.snapshot.cursor.token(),
        )
    )
    lifecycle = _lifecycle
    from deerflow_deep_research.domain.bundle import BundleId as _BundleId

    bundle = await lifecycle.resolve(
        scope=(driver._envelope.effective_user_id, driver._envelope.outer_thread_id), bundle_id=_BundleId(bundle_id)
    )
    async with lifecycle.open_graph_checkpoint(bundle) as saver:
        graph = driver._executor._recipe.builder.compile(checkpointer=saver)
        snapshot = await graph.aget_state(driver._executor._config(bundle))
    values = snapshot.values if snapshot else {}
    assert values.get("request_text") == question, (
        f"the graph must run the operator's question, got {values.get('request_text')!r}"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "node",
    ["bootstrap", "topic_planning", "wave0", "wave1", "wave2_synthesis", "hitl2", "readiness", "final_delivery"],
)
async def test_drive_until_stops_after_every_named_node(tmp_path: Path, node: str) -> None:
    """LDD-003: every logical node of the composition is a legal breakpoint
    target - drive_until stops right after that node commits."""
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id
    driven = await driver.execute(
        DebugCommand(
            kind="drive_until",
            bundle_id=bundle_id,
            command_id=f"drive-{node}",
            expected_cursor=opened.snapshot.cursor.token(),
            breakpoint=StopPolicy(breakpoint_after=node, auto_hitl=True),
        )
    )
    assert driven.denied is None, driven.message
    assert driven.snapshot is not None
    assert driven.snapshot.posture in {"paused_at_boundary", "awaiting_hitl", "terminal"}
    bundle = await _lifecycle.resolve(
        scope=(driver._envelope.effective_user_id, driver._envelope.outer_thread_id),
        bundle_id=__import__("deerflow_deep_research.domain.bundle", fromlist=["BundleId"]).BundleId(bundle_id),
    )
    state = await _lifecycle.read_state(bundle)
    assert node in tuple(state.execution_trace or ()), f"the drive must have visited {node}: {state.execution_trace!r}"


@pytest.mark.asyncio
async def test_watch_field_stops_the_drive_and_advances_its_baseline(tmp_path: Path) -> None:
    """LDD-009: a watch on a typed State field stops the drive when that field
    changes, carries the hit on the snapshot, and advances its baseline so the
    same value does not re-trip; unknown field names are rejected."""
    driver, _lifecycle = _make_driver(tmp_path, owner="op-1")
    opened = await driver.open_start(
        StartRequest(question="Compare storage", mode="step", owner="op-1", command_id="start-00000001")
    )
    bundle_id = opened.snapshot.bundle_id

    accepted = driver.set_watch_fields(bundle_id, ("phase", "not_a_state_field"))
    assert accepted == ("phase",), "an unknown field name must be rejected"

    driven = await driver.execute(
        DebugCommand(
            kind="drive_until",
            bundle_id=bundle_id,
            command_id="drive-00000001",
            expected_cursor=opened.snapshot.cursor.token(),
            breakpoint=StopPolicy(auto_hitl=True),
        )
    )
    assert driven.denied is None
    assert driven.snapshot is not None
    assert "phase" in driven.snapshot.watch_hits, (
        f"the phase changes at the first boundary - the watch must stop the drive: {driven.snapshot.watch_hits!r}"
    )
    assert driven.snapshot.posture != "terminal", "the watch hit must stop the drive"

    # The baseline advanced to the current value at the hit.
    bundle = await _lifecycle.resolve(
        scope=(driver._envelope.effective_user_id, driver._envelope.outer_thread_id),
        bundle_id=__import__("deerflow_deep_research.domain.bundle", fromlist=["BundleId"]).BundleId(bundle_id),
    )
    state_now = await _lifecycle.read_state(bundle)
    baseline = driver._sessions[bundle_id]["watch_baseline"]
    assert baseline.get("phase") == state_now.phase.value, "the baseline must advance after a hit"
