"""Graph-owned HITL interrupt contracts (REG-003/004)."""

from __future__ import annotations

import pytest
from deerflow_deep_research_fixtures.graph.nodes.hitl1.adapter import build_fixture as build_fixture_hitl1
from deerflow_deep_research_fixtures.graph.nodes.hitl2.adapter import build_fixture as build_fixture_hitl2
from deerflow_deep_research_fixtures.scenario import FixtureScenario
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from deerflow_deep_research.domain.context import GraphContextView, NodeAgentContext
from deerflow_deep_research.domain.lifecycle import (
    AcceptedHumanResponse,
    BundleAvailability,
    BundleControlResult,
    BundleRefinementProjection,
    PendingResearchInterrupt,
    ResponseKind,
)
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.run_experience import PendingInputProjection
from deerflow_deep_research.domain.state import ResearchState
from deerflow_deep_research.runtime.human_input import HumanInputError, project_suspension


class ForbiddenCapabilities:
    async def run_agent(self, *, context, request):
        raise AssertionError("fixture HITL must not invoke agent capability")


def _dependencies(name: str) -> NodeBuildDependencies:
    graph = GraphContextView(
        research_scope_id="r_" + "A" * 43,
        workspace_root="/mnt/user-data/workspace/deep-research/r",
        uploads_root="/mnt/user-data/uploads",
        outputs_root="/mnt/user-data/outputs/deep-research/r",
    )
    return NodeBuildDependencies(
        graph_context=graph,
        agent_context=NodeAgentContext(
            research_scope_id=graph.research_scope_id,
            node_name=name,
            attempt_id=f"g0-{name}-a1",
            workspace_root=graph.workspace_root,
            attempt_root=f"{graph.workspace_root}/{name}",
            policy_name="skeleton",
        ),
        capabilities=ForbiddenCapabilities(),
    )


def _initial() -> dict:
    return {
        "schema_version": 3,
        "bundle_id": "r_" + "A" * 43,
        "start_message_id": "human-start",
        "request_digest": "d_" + "B" * 43,
        "request_text": "question",
        "phase": "bootstrap",
        "generation": 0,
        "wave0_results": (),
        "wave1_results": (),
        "consumed_request_ids": (),
        "consumed_message_ids": (),
        "execution_trace": (),
    }


def _graph(logical_name: str, factory):
    builder = StateGraph(ResearchState)
    builder.add_node(logical_name, factory(_dependencies(logical_name)))
    builder.add_edge(START, logical_name)
    builder.add_edge(logical_name, END)
    return builder.compile(checkpointer=InMemorySaver())


@pytest.mark.asyncio
async def test_hitl1_interrupt_is_checkpointed_and_resume_records_consumption() -> None:
    graph = _graph("hitl1", build_fixture_hitl1)
    config = {"configurable": {"thread_id": "hitl1-test"}}
    await graph.ainvoke(_initial(), config=config)
    snapshot = await graph.aget_state(config)
    assert len(snapshot.tasks) == 1
    assert len(snapshot.tasks[0].interrupts) == 1
    descriptor = snapshot.tasks[0].interrupts[0].value
    request = descriptor["request"]
    assert request["source"] == "deep_research"
    assert request["mode"] == "text"
    assert "fixture composition" in request["title"]
    assert descriptor["suspension_cursor"] == "human-start"

    response = AcceptedHumanResponse(
        request_id=request["request_id"],
        message_id="human-response-1",
        value="scope answer",
        response_kind=ResponseKind.TEXT,
    )
    result = await graph.ainvoke(Command(resume=response.model_dump(mode="json")), config=config)
    assert result["consumed_request_ids"] == (request["request_id"],)
    assert result["consumed_message_ids"] == ("human-response-1",)
    assert result["execution_trace"] == ("hitl1",)


@pytest.mark.asyncio
async def test_fixture_hitl2_consumes_its_fixture_route_without_an_interrupt() -> None:
    graph = _graph("hitl2", build_fixture_hitl2(FixtureScenario()))
    config = {"configurable": {"thread_id": "hitl2-test"}}
    initial = _initial() | {"execution_trace": ("hitl2",), "consumed_message_ids": ("human-response-1",)}
    result = await graph.ainvoke(initial, config=config)
    snapshot = await graph.aget_state(config)
    assert result["route"] == "proceed"
    assert result["execution_trace"] == ("hitl2", "hitl2")
    assert not snapshot.tasks


@pytest.mark.asyncio
async def test_projector_failure_after_interrupt_commit_does_not_rerun_node() -> None:
    graph = _graph("hitl1", build_fixture_hitl1)
    config = {"configurable": {"thread_id": "projection-fault"}}
    await graph.ainvoke(_initial(), config=config)
    before = await graph.aget_state(config)
    pending = PendingResearchInterrupt.model_validate(_pending_value := before.tasks[0].interrupts[0].value)
    bad = BundleControlResult(
        action="start",
        code="suspended",
        availability=BundleAvailability.AVAILABLE,
        durability="same_process",
        bundle_id="b_" + "A" * 43,
        status="suspended",
        phase="hitl1",
        generation=0,
        request_id="drh_wrong",
        pending_input=PendingInputProjection(
            request_id="drh_wrong",
            pending_phase="hitl1",
            generation=0,
            mode="text",
        ),
        refinement=BundleRefinementProjection(disposition="none"),
    )
    with pytest.raises(HumanInputError, match="checkpoint_inconsistent"):
        project_suspension(pending=pending, result=bad, tool_call_id="failed-call")
    after = await graph.aget_state(config)
    assert not after.values["execution_trace"]
    assert after.tasks[0].interrupts[0].value == _pending_value

    good = bad.model_copy(
        update={
            "request_id": pending.request.request_id,
            "pending_input": bad.pending_input.model_copy(update={"request_id": pending.request.request_id}),
        }
    )
    command = project_suspension(pending=pending, result=good, tool_call_id="retry-call")
    assert command.update["messages"][0].tool_call_id == "retry-call"
    assert command.update["messages"][0].id == pending.request.request_id
