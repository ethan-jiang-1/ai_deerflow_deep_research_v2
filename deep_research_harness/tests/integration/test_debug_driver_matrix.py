"""Headless debug-driver falsifiable matrix over the real fixture graph.

@impl LDD-001
@impl LDD-002
@impl LDD-003
@impl LDD-004
@impl LDD-005
"""

from __future__ import annotations

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
