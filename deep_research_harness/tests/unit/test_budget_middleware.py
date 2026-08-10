"""BudgetMiddleware admission-control and tool-budget contract.

@impl NOA-002
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from deerflow_deep_research.agents.middleware import AgentBudgetError, BudgetMiddleware
from deerflow_deep_research.agents.phase_prompt import render_phase_agent_prompt
from deerflow_deep_research.agents.policies import ExecutionBudget
from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.domain.run_observation import BudgetStopReason
from deerflow_deep_research.graph.nodes.topic_planning.prompts import PlannerAssignment, build_planner_prompt


def _budget(**overrides) -> ExecutionBudget:
    base = {
        "max_model_calls": 2,
        "max_total_tool_calls": 2,
        "max_tool_calls_per_response": 2,
        "max_parallel_tool_calls": 1,
        "total_token_budget": 1_000,
        "per_call_output_token_cap": 200,
        "per_tool_result_bytes": 64,
        "structured_result_bytes": 512,
        "wall_time_seconds": 5.0,
    }
    base.update(overrides)
    return ExecutionBudget(**base)


class FakeRequest:
    def __init__(self, messages=None, tools=(), system=None) -> None:
        self.messages = messages or [HumanMessage("hello")]
        self.tools = list(tools)
        self.system_message = system


class FakeResponse:
    def __init__(self, message: AIMessage) -> None:
        self.result = [message]


def _ai(content="ok", *, tool_calls=None, input_tokens=10, output_tokens=5) -> AIMessage:
    usage = None
    if input_tokens is not None and output_tokens is not None:
        usage = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        }
    return AIMessage(content=content, tool_calls=tool_calls or [], usage_metadata=usage)


def _handler_for(message: AIMessage):
    async def handler(_request):
        return FakeResponse(message)

    return handler


def _topic_planning_policy():
    from deerflow_deep_research.runtime.research import _topic_planning_node_agent_policy

    return _topic_planning_node_agent_policy(
        SimpleNamespace(
            workspace_root="/mnt/user-data/workspace/deep-research/fixed",
            uploads_root="/mnt/user-data/uploads",
        )
    )


def _fixed_demo_request() -> FakeRequest:
    assignment = PlannerAssignment(
        request_text=(
            "Compare lithium-ion batteries and pumped-hydro storage on grid-balancing cost and deployment risk."
        ),
        research_depth="",
        target_audience="",
        output_format="",
        cost_tolerance="",
        time_budget="",
        must_answer_questions=(),
        degraded_profile=True,
        comparison_subjects=(
            "lithium-ion batteries",
            "pumped-hydro storage on grid-balancing cost and deployment risk.",
        ),
        request_language="en",
        output_language="en",
    )
    rendered = render_phase_agent_prompt(
        build_planner_prompt(assignment),
        attempt_workspace="/mnt/user-data/workspace/deep-research/fixed/topic_planning",
    )
    return FakeRequest(
        messages=[HumanMessage(rendered.user_message)],
        system=SystemMessage(rendered.system_policy),
    )


async def test_normal_call_updates_counters() -> None:
    mw = BudgetMiddleware(_budget())
    await mw.awrap_model_call(FakeRequest(), _handler_for(_ai(output_tokens=5)))
    assert mw.model_calls == 1
    assert mw.tokens_used == 15


async def test_max_model_calls_refused_before_handler() -> None:
    mw = BudgetMiddleware(_budget(max_model_calls=1))
    mw.model_calls = 1
    called = False

    async def handler(_request):
        nonlocal called
        called = True
        return FakeResponse(_ai())

    with pytest.raises(AgentBudgetError) as excinfo:
        await mw.awrap_model_call(FakeRequest(), handler)
    assert excinfo.value.finish_reason == NodeFinishReason.BUDGET_EXHAUSTED
    assert excinfo.value.budget_stop_reason is BudgetStopReason.MODEL_CALL_LIMIT
    assert called is False


async def test_non_text_content_fails_admission() -> None:
    mw = BudgetMiddleware(_budget())
    non_text = HumanMessage(content=[{"type": "image_url", "image_url": {"url": "x"}}])
    with pytest.raises(AgentBudgetError) as excinfo:
        await mw.awrap_model_call(FakeRequest(messages=[non_text]), _handler_for(_ai()))
    assert excinfo.value.budget_stop_reason is BudgetStopReason.REQUEST_CONTENT_UNESTIMABLE


async def test_token_admission_upper_bound_refused_before_handler() -> None:
    mw = BudgetMiddleware(_budget(total_token_budget=50, per_call_output_token_cap=40))
    called = False

    async def handler(_request):
        nonlocal called
        called = True
        return FakeResponse(_ai())

    big = HumanMessage("x" * 200)
    with pytest.raises(AgentBudgetError) as excinfo:
        await mw.awrap_model_call(FakeRequest(messages=[big]), handler)
    assert excinfo.value.budget_stop_reason is BudgetStopReason.TOKEN_ADMISSION
    assert called is False


async def test_topic_planning_fixed_demo_render_is_admitted_but_oversized_request_is_not() -> None:
    """@impl TOP-010

    Use the final renderer for both sides of the local admission boundary.
    """
    policy = _topic_planning_policy()
    middleware = BudgetMiddleware(policy.budget)
    fixed_request = _fixed_demo_request()
    fixed_upper_bound = middleware._request_upper_bound(fixed_request)
    called = False

    async def admitted_handler(_request):
        nonlocal called
        called = True
        return FakeResponse(_ai(input_tokens=100, output_tokens=100))

    assert fixed_upper_bound + policy.budget.per_call_output_token_cap <= policy.budget.total_token_budget
    await middleware.awrap_model_call(fixed_request, admitted_handler)
    assert called is True

    oversized = FakeRequest(messages=[HumanMessage("x" * (policy.budget.total_token_budget + 1))])
    rejected = BudgetMiddleware(policy.budget)
    provider_called = False

    async def rejected_handler(_request):
        nonlocal provider_called
        provider_called = True
        return FakeResponse(_ai())

    with pytest.raises(AgentBudgetError) as excinfo:
        await rejected.awrap_model_call(oversized, rejected_handler)
    assert excinfo.value.budget_stop_reason is BudgetStopReason.TOKEN_ADMISSION
    assert provider_called is False


async def test_missing_usage_is_terminal_usage_unavailable() -> None:
    mw = BudgetMiddleware(_budget())
    with pytest.raises(AgentBudgetError) as excinfo:
        await mw.awrap_model_call(FakeRequest(), _handler_for(_ai(input_tokens=None, output_tokens=None)))
    assert excinfo.value.finish_reason == NodeFinishReason.USAGE_UNAVAILABLE
    assert excinfo.value.budget_stop_reason is None


async def test_per_call_output_cap_exceeded() -> None:
    mw = BudgetMiddleware(_budget(per_call_output_token_cap=100, total_token_budget=1_000))
    with pytest.raises(AgentBudgetError) as excinfo:
        await mw.awrap_model_call(FakeRequest(), _handler_for(_ai(output_tokens=500)))
    assert excinfo.value.finish_reason == NodeFinishReason.BUDGET_EXHAUSTED
    assert excinfo.value.budget_stop_reason is BudgetStopReason.PER_CALL_OUTPUT_CAP


async def test_total_token_budget_exhausted_after_reconcile() -> None:
    mw = BudgetMiddleware(_budget(total_token_budget=300, per_call_output_token_cap=100))
    mw.tokens_used = 101
    with pytest.raises(AgentBudgetError) as excinfo:
        await mw.awrap_model_call(FakeRequest(), _handler_for(_ai(input_tokens=150, output_tokens=50)))
    assert excinfo.value.budget_stop_reason is BudgetStopReason.TOTAL_TOKEN_BUDGET


async def test_too_many_tool_calls_per_response() -> None:
    mw = BudgetMiddleware(_budget(max_tool_calls_per_response=2, max_parallel_tool_calls=2))
    three = [
        {"name": "t", "args": {}, "id": "1"},
        {"name": "t", "args": {}, "id": "2"},
        {"name": "t", "args": {}, "id": "3"},
    ]
    with pytest.raises(AgentBudgetError) as excinfo:
        await mw.awrap_model_call(FakeRequest(), _handler_for(_ai(tool_calls=three)))
    assert excinfo.value.budget_stop_reason is BudgetStopReason.TOOL_CALLS_PER_RESPONSE


async def test_parallel_tool_call_limit() -> None:
    mw = BudgetMiddleware(_budget(max_tool_calls_per_response=2, max_parallel_tool_calls=1))
    two = [{"name": "t", "args": {}, "id": "1"}, {"name": "t", "args": {}, "id": "2"}]
    with pytest.raises(AgentBudgetError) as excinfo:
        await mw.awrap_model_call(FakeRequest(), _handler_for(_ai(tool_calls=two)))
    assert excinfo.value.budget_stop_reason is BudgetStopReason.PARALLEL_TOOL_CALLS


async def test_max_total_tool_calls_refused() -> None:
    mw = BudgetMiddleware(_budget(max_total_tool_calls=1, max_tool_calls_per_response=1, max_parallel_tool_calls=1))
    mw.tool_calls = 1

    async def handler(_request):
        return ToolMessage(content="x", tool_call_id="c1")

    with pytest.raises(AgentBudgetError) as excinfo:
        await mw.awrap_tool_call(object(), handler)
    assert excinfo.value.budget_stop_reason is BudgetStopReason.TOTAL_TOOL_CALLS


async def test_tool_result_is_size_bounded() -> None:
    mw = BudgetMiddleware(_budget(per_tool_result_bytes=16))
    big = "A" * 200

    async def handler(_request):
        return ToolMessage(content=big, tool_call_id="c1")

    result = await mw.awrap_tool_call(object(), handler)
    assert len(result.content.encode("utf-8")) < len(big.encode("utf-8"))
    assert "[truncated" in result.content


async def test_large_tool_result_history_uses_bounded_admission() -> None:
    mw = BudgetMiddleware(_budget(total_token_budget=1_000, per_tool_result_bytes=32))

    async def tool_handler(_request):
        return ToolMessage(content="x" * 20_000, tool_call_id="c1")

    bounded = await mw.awrap_tool_call(object(), tool_handler)
    messages = [HumanMessage("question"), AIMessage(content="", tool_calls=[]), bounded]
    await mw.awrap_model_call(FakeRequest(messages=messages), _handler_for(_ai(input_tokens=20, output_tokens=10)))
    assert mw.model_calls == 1
    assert len(bounded.content.encode()) < 200
