"""Trace contract fixtures over the real checkpoint + journal authorities.

@impl LDO-001
@impl LDO-002
@impl LDO-003
@impl LDO-004
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from deerflow_deep_research.domain.bundle import BundleId
from deerflow_deep_research.domain.run_observation import (
    RunEventCategory,
)
from deerflow_deep_research.domain.trace import TraceFrame, TracePage
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.run_observation import RunObservationStore
from deerflow_deep_research.runtime.trace_projector import RunTraceProjector, _decode_cursor

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _demo_core import DemoAdapter, DemoLifecycleTransport, build_demo_runtime  # noqa: E402, I001


async def _suspended_fixture_bundle(tmp_path: Path) -> tuple[BundleLifecycle, object, str]:
    adapter = DemoAdapter(bundle_root=tmp_path / "fixture-graph-runs")
    transport = DemoLifecycleTransport()
    runtime = build_demo_runtime(mode="fixture_graph", adapter=adapter)
    transport.bind(runtime=runtime)
    start = HumanMessage(content="Compare two storage approaches.", id="fixture-start")
    try:
        started = await transport.dispatch(action="start", bundle_id=None, messages=(start,))
    finally:
        adapter.close()
    assert isinstance(started, Command)
    message = started.update["messages"][0]
    bundle_id = json.loads(message.content)["bundle_id"]
    lifecycle = adapter._bundle_lifecycle
    bundle = await lifecycle.resolve(
        scope=(adapter._envelope.effective_user_id, adapter._envelope.outer_thread_id),
        bundle_id=BundleId(bundle_id),
    )
    assert bundle is not None
    return lifecycle, bundle, bundle_id


@pytest.mark.asyncio
async def test_replay_and_incremental_live_reads_are_isomorphic(tmp_path: Path) -> None:
    lifecycle, bundle, bundle_id = await _suspended_fixture_bundle(tmp_path)
    projector = RunTraceProjector(lifecycle)

    replay = await projector.project_full(bundle)
    assert isinstance(replay, TracePage)
    assert replay.bundle_id == bundle_id
    assert replay.frames, "committed boundaries must project frames"
    assert all(isinstance(frame, TraceFrame) for frame in replay.frames)
    assert [frame.frame_sequence for frame in replay.frames] == list(range(1, len(replay.frames) + 1))
    assert all(frame.checkpoint_id for frame in replay.frames)
    assert replay.frames[0].node == "bootstrap"
    assert replay.observation_quality == "complete"

    live_first = await projector.project_full(bundle, live=True, page_size=1)
    assert live_first.frames == replay.frames[:1]
    assert live_first.next_cursor

    live_next, cursor = await projector.project_incremental(bundle, live_first.next_cursor or "")
    assert live_next.frames == replay.frames[1:]
    assert cursor

    replay_again = await projector.project_full(bundle)
    assert replay_again.frames == replay.frames


def test_trace_cursor_fails_closed_on_tamper(tmp_path: Path) -> None:
    bundle_id = "b_" + "B" * 43
    from deerflow_deep_research.runtime.trace_projector import _encode_cursor

    good = _encode_cursor({"bundle_id": bundle_id, "frame_sequence": 2, "journal": 5})
    payload = _decode_cursor(good, bundle_id=bundle_id)
    assert payload["frame_sequence"] == 2
    with pytest.raises(ValueError):
        _decode_cursor(good, bundle_id="b_" + "C" * 43)
    with pytest.raises(ValueError):
        _decode_cursor(good[:-2] + "xx", bundle_id=bundle_id)
    with pytest.raises(ValueError):
        _decode_cursor("LDT9." + good.split(".", 1)[1], bundle_id=bundle_id)


@pytest.mark.asyncio
async def test_frames_carry_wrapper_measured_duration_and_privacy_sentinels(tmp_path: Path) -> None:
    lifecycle, bundle, bundle_id = await _suspended_fixture_bundle(tmp_path)
    projector = RunTraceProjector(lifecycle)

    page = await projector.project_full(bundle)
    durations = [frame.duration_ms for frame in page.frames if frame.duration_ms is not None]
    assert durations, "finalized segments must carry wrapper-measured duration"
    assert all(0 <= value <= 3_600_000 for value in durations)

    rendered = str(page.model_dump())
    assert "SENTINEL" not in rendered
    assert str(tmp_path) not in rendered
    assert "request_text" not in rendered


@pytest.mark.asyncio
async def test_noncommitted_journal_failure_becomes_failed_frame(tmp_path: Path) -> None:
    lifecycle, bundle, bundle_id = await _suspended_fixture_bundle(tmp_path)
    store = RunObservationStore(bundle_root=lifecycle.private_root(bundle), bundle_id=bundle_id)
    recorder = __import__(
        "deerflow_deep_research.runtime.run_observation", fromlist=["RunObservationRecorder"]
    ).RunObservationRecorder(store=store, bundle_id=bundle_id)
    await recorder.establish(generation=0, phase="wave_extra", durability="restart_durable")
    await recorder.record(
        category=RunEventCategory.NODE,
        phase="wave_extra",
        attempt_id="g0-wave_extra-a9",
        outcome="failed",
        failure_category="internal.unexpected",
        worker_failure_category="unknown",
    )

    page = await RunTraceProjector(lifecycle).project_full(bundle)
    failed = [frame for frame in page.frames if frame.outcome == "failed"]
    assert len(failed) == 1
    assert failed[0].node == "wave_extra"
    assert failed[0].checkpoint_id is None
    assert failed[0].failure_event_sequence is not None
    assert failed[0].failure_category == "internal.unexpected"
    completed_for_extra = [
        frame for frame in page.frames if frame.node == "wave_extra" and frame.outcome == "completed"
    ]
    assert not completed_for_extra


@pytest.mark.xfail(
    reason="suspended 帧与 unmatched started 的 active 投影配对边界排查中（LDD-001 剩余行）",
    strict=False,
)
@pytest.mark.asyncio
async def test_unmatched_started_stays_uncertain_on_replay(tmp_path: Path) -> None:
    lifecycle, bundle, bundle_id = await _suspended_fixture_bundle(tmp_path)
    store = RunObservationStore(bundle_root=lifecycle.private_root(bundle), bundle_id=bundle_id)
    recorder = __import__(
        "deerflow_deep_research.runtime.run_observation", fromlist=["RunObservationRecorder"]
    ).RunObservationRecorder(store=store, bundle_id=bundle_id)
    await recorder.establish(generation=0, phase="wave0", durability="restart_durable")
    await recorder.record(
        category=RunEventCategory.NODE,
        phase="wave0",
        attempt_id="g0-wave0-a1",
        outcome="started",
    )

    replay = await RunTraceProjector(lifecycle).project_full(bundle)
    assert replay.active_visit is not None
    assert replay.active_visit.state == "uncertain"
    assert replay.active_visit.node == "wave0"

    live = await RunTraceProjector(lifecycle).project_full(bundle, live=True)
    assert live.active_visit is not None
    assert live.active_visit.state == "running"


@pytest.mark.asyncio
async def test_two_bundles_never_share_frames(tmp_path: Path) -> None:
    first_lifecycle, first_bundle, first_id = await _suspended_fixture_bundle(tmp_path / "one")
    second_root = tmp_path / "two"
    adapter = DemoAdapter(bundle_root=second_root / "fixture-graph-runs")
    transport = DemoLifecycleTransport()
    runtime = build_demo_runtime(mode="fixture_graph", adapter=adapter)
    transport.bind(runtime=runtime)
    try:
        started = await transport.dispatch(
            action="start",
            bundle_id=None,
            messages=(HumanMessage(content="Compare two storage approaches.", id="fixture-start-two"),),
        )
    finally:
        adapter.close()
    assert isinstance(started, Command)
    message = started.update["messages"][0]
    second_id = json.loads(message.content)["bundle_id"]
    second_lifecycle = adapter._bundle_lifecycle
    second_bundle = await second_lifecycle.resolve(
        scope=(adapter._envelope.effective_user_id, adapter._envelope.outer_thread_id),
        bundle_id=BundleId(second_id),
    )
    assert second_bundle is not None

    page_one = await RunTraceProjector(first_lifecycle).project_full(first_bundle)
    page_two = await RunTraceProjector(second_lifecycle).project_full(second_bundle)
    assert all(frame.bundle_id == first_id for frame in page_one.frames)
    assert all(frame.bundle_id == second_id for frame in page_two.frames)
    assert page_one.frames != page_two.frames


@pytest.mark.asyncio
async def test_journal_inspection_failure_keeps_checkpoint_skeletons(tmp_path: Path) -> None:
    lifecycle, bundle, bundle_id = await _suspended_fixture_bundle(tmp_path)
    events_file = lifecycle.private_root(bundle) / "diagnostics" / "events.jsonl"
    events_file.write_text("{corrupt json line\n", encoding="utf-8")

    page = await RunTraceProjector(lifecycle).project_full(bundle)
    assert page.frames, "checkpoint boundary skeletons must survive journal damage"
    assert page.observation_quality in {"degraded", "unavailable"}
    assert page.gap_reason
    assert all(frame.duration_ms is None for frame in page.frames)
