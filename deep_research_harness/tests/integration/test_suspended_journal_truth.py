"""Suspended-attempt journal truth through the real Bundle recorder and store.

@impl REJ-011
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from deerflow_deep_research.domain.bundle import BundleId
from deerflow_deep_research.domain.run_observation import (
    ObservationInspectability,
    RunEventCategory,
)
from deerflow_deep_research.runtime.run_observation import (
    RunObservationRecorder,
    RunObservationStore,
)

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _demo_core import DemoAdapter, DemoLifecycleTransport, build_demo_runtime  # noqa: E402, I001

_BUNDLE_ID = "b_" + "A" * 43


def _bundle_and_request(command: Command) -> tuple[str, dict[str, object]]:
    message = command.update["messages"][0]
    return json.loads(message.content)["bundle_id"], message.artifact["human_input"]


@pytest.mark.asyncio
async def test_human_interrupt_suspension_persists_as_suspended_not_failure(tmp_path: Path) -> None:
    """The durable journal distinguishes awaiting-recovery from crashed (REJ-011)."""

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
    bundle_id, _request = _bundle_and_request(started)

    scope = (adapter._envelope.effective_user_id, adapter._envelope.outer_thread_id)
    lifecycle = adapter._bundle_lifecycle
    bundle = await lifecycle.resolve(scope=scope, bundle_id=BundleId(bundle_id))
    assert bundle is not None
    bundle_root = lifecycle.private_root(bundle)
    journal = await RunObservationStore(bundle_root=bundle_root, bundle_id=bundle_id).inspect(
        bundle_id=bundle_id
    )
    assert journal.inspectability is ObservationInspectability.AVAILABLE

    hitl1_attempts = [
        event
        for event in journal.events
        if event.category is RunEventCategory.NODE and event.phase == "hitl1"
    ]
    assert hitl1_attempts, "the hitl1 attempt must be journaled"
    assert hitl1_attempts[0].outcome == "started"
    assert hitl1_attempts[-1].outcome == "suspended"
    assert not any(
        event.failure_category == "internal.unexpected" for event in hitl1_attempts
    )

    # The serialized round trip: events.jsonl itself carries the closed value and
    # a fresh reader returns it.
    events_file = bundle_root / "diagnostics" / "events.jsonl"
    raw_outcomes = [
        json.loads(line).get("outcome")
        for line in events_file.read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert "suspended" in raw_outcomes
    reloaded = await RunObservationStore(bundle_root=bundle_root, bundle_id=bundle_id).inspect(
        bundle_id=bundle_id
    )
    assert reloaded.events[-1].outcome == "suspended"


@pytest.mark.asyncio
async def test_unexpected_failure_round_trip_keeps_internal_unexpected(tmp_path: Path) -> None:
    """A real unexpected failure keeps its labels through the persisted round trip."""

    bundle_root = tmp_path / "bundle"
    (bundle_root / "diagnostics").mkdir(mode=0o700, parents=True)
    os.chmod(bundle_root / "diagnostics", 0o700)
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=_BUNDLE_ID)
    recorder = RunObservationRecorder(store=store, bundle_id=_BUNDLE_ID)
    await recorder.establish(generation=0, phase="wave0", durability="restart_durable")

    await recorder.record(
        category=RunEventCategory.NODE,
        phase="wave0",
        attempt_id="g0-wave0-a1",
        outcome="failed",
        failure_category="internal.unexpected",
        worker_failure_category="unknown",
    )

    journal = await store.inspect(bundle_id=_BUNDLE_ID)
    node_events = [event for event in journal.events if event.category is RunEventCategory.NODE]
    assert [event.outcome for event in node_events] == ["failed"]
    assert node_events[0].failure_category == "internal.unexpected"
    assert node_events[0].worker_failure_category == "unknown"
