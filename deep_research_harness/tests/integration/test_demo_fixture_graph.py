"""Deterministic lifecycle evidence for the named fixture-graph verification route.

@impl DPL-001
@impl DPL-003
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from deerflow_deep_research.domain.bundle import BundleId
from deerflow_deep_research.domain.lifecycle import ImplementationMode, LifecycleAction, LifecycleStatus
from deerflow_deep_research.domain.run_observation import ObservationInspectability, RunEventCategory
from deerflow_deep_research.runtime.run_observation import RunObservationStore

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _demo_core import DemoAdapter, DemoLifecycleTransport, build_demo_runtime  # noqa: E402, I001


def _bundle_and_request(command: Command) -> tuple[str, dict[str, object]]:
    message = command.update["messages"][0]
    return json.loads(message.content)["bundle_id"], message.artifact["human_input"]


@pytest.mark.asyncio
async def test_fixture_graph_transport_runs_to_final_delivery_and_projects_its_durable_mode(tmp_path: Path) -> None:
    """@impl REJ-001"""

    adapter = DemoAdapter(bundle_root=tmp_path / "fixture-graph-runs")
    transport = DemoLifecycleTransport()
    runtime = build_demo_runtime(mode="fixture_graph", adapter=adapter)
    transport.bind(runtime=runtime)
    start = HumanMessage(content="Compare two storage approaches.", id="fixture-start")

    try:
        started = await transport.dispatch(action="start", bundle_id=None, messages=(start,))
        assert isinstance(started, Command)
        bundle_id, request = _bundle_and_request(started)
        assert request["mode"] == "text"

        scope = (adapter._envelope.effective_user_id, adapter._envelope.outer_thread_id)
        lifecycle = adapter._bundle_lifecycle
        bundle = await lifecycle.resolve(scope=scope, bundle_id=BundleId(bundle_id))
        assert bundle is not None
        journal = await RunObservationStore(
            bundle_root=lifecycle.private_root(bundle),
            bundle_id=bundle_id,
        ).inspect(bundle_id=bundle_id)
        assert journal.inspectability is ObservationInspectability.AVAILABLE
        assert [event.category for event in journal.events[:1]] == [RunEventCategory.ADMISSION]
        first_node = next(
            index for index, event in enumerate(journal.events) if event.category is RunEventCategory.NODE
        )
        assert first_node > 0
        # The transport has returned only the graph's suspension at this point. Its
        # presentation publisher has not yet observed a lifecycle result.
        assert not any(event.category is RunEventCategory.LIFECYCLE for event in journal.events[: first_node + 1])

        response = HumanMessage(
            content="Use broad public sources.",
            id="fixture-profile",
            additional_kwargs={
                "human_input_response": {
                    "version": 1,
                    "kind": "human_input_response",
                    "source": "deep_research",
                    "request_id": request["request_id"],
                    "response_kind": "text",
                    "value": "Use broad public sources.",
                }
            },
        )
        completed = await transport.dispatch(action="resume", bundle_id=bundle_id, messages=(start, response))
        assert isinstance(completed, dict)
        assert completed["code"] == "completed"
        assert completed["implementation_mode"] == "fixture"
        assert "final_delivery" in completed["execution_trace"]

        refined = await transport.dispatch(
            action="refine",
            bundle_id=bundle_id,
            messages=(start, response),
            context={"refinement": "Prioritize primary public sources."},
        )
        assert isinstance(refined, dict)
        assert refined["code"] == "refinement_applied"
        assert refined["generation"] == 1

        reopened_journal = await RunObservationStore(
            bundle_root=lifecycle.private_root(bundle),
            bundle_id=bundle_id,
        ).inspect(bundle_id=bundle_id)
        first_refinement_node = next(
            index
            for index, event in enumerate(reopened_journal.events)
            if event.category is RunEventCategory.NODE and event.generation == 1
        )
        assert reopened_journal.events[first_refinement_node].phase == "topic_planning"
        assert not any(
            event.category in {RunEventCategory.LIFECYCLE, RunEventCategory.TERMINAL} and event.generation == 1
            for event in reopened_journal.events[: first_refinement_node + 1]
        )

        status = await adapter.local_bundle_workbench().status(bundle_id=bundle_id)
        assert status.status is LifecycleStatus.COMPLETED
        assert status.implementation_mode is ImplementationMode.FIXTURE

        state = await lifecycle.read_state(bundle)
        assert state.implementation_mode is ImplementationMode.FIXTURE
        assert state.generation == 1

        reprojected = await runtime.executor.reproject(
            lifecycle=lifecycle,
            bundle=bundle,
            action=LifecycleAction.STATUS,
            tool_call_id="fixture-status",
        )
        assert isinstance(reprojected, dict)
        assert reprojected["implementation_mode"] == "fixture"
        assert "final_delivery" in reprojected["execution_trace"]

        async with lifecycle.open_graph_checkpoint(bundle) as saver:
            graph = runtime.recipe.builder.compile(checkpointer=saver)
            checkpoint = await graph.aget_state(runtime.executor._config(bundle))
        assert checkpoint is not None
        assert "final_delivery" in checkpoint.values["execution_trace"]
        assert checkpoint.values["phase"] == "final_delivery"
        assert checkpoint.values["terminal_status"] == "completed"
        assert checkpoint.values["terminal_reason"] == "completed"
        assert checkpoint.values["generation"] == 1
        assert checkpoint.values["gate_attempts_by_phase"]["final_delivery"] == 1
        assert tuple(checkpoint.values["report_refs"]) == ()
    finally:
        await adapter.aclose()
