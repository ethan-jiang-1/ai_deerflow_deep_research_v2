"""Public Gateway observer contracts.

@impl GOO-001
@impl GOO-002
"""

from __future__ import annotations

import inspect
import json
from collections.abc import AsyncIterator

import httpx
import pytest
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.types import Command

from deerflow_deep_research.domain.lifecycle import (
    BundleAvailability,
    BundleControlResult,
    BundleRefinementProjection,
    Durability,
    LegalNextAction,
    LifecycleAction,
    LifecycleStatus,
    LogicalPhase,
    ResultCode,
)
from deerflow_deep_research.runtime.gateway_observer import (
    PUBLIC_GATEWAY_ORIGIN,
    GatewayCorrelation,
    GatewayObserver,
    GatewayObserverError,
    GatewaySseRecord,
    HttpGatewayPublicClient,
)


def _control_payload() -> dict[str, object]:
    return BundleControlResult(
        action=LifecycleAction.RESUME,
        code=ResultCode.COMPLETED,
        availability=BundleAvailability.AVAILABLE,
        durability=Durability.RESTART_DURABLE,
        bundle_id="b_" + "A" * 43,
        status=LifecycleStatus.COMPLETED,
        phase=LogicalPhase.FINAL_DELIVERY,
        generation=0,
        refinement=BundleRefinementProjection(disposition="none"),
        legal_next_action=LegalNextAction.REFINE,
        execution_trace=("bootstrap", "hitl1", "final_delivery"),
    ).model_dump(mode="json", exclude_none=True)


def _tool_record(*, payload: dict[str, object] | None = None) -> GatewaySseRecord:
    return GatewaySseRecord(
        name="messages-tuple",
        data=json.dumps(
            [
                {
                    "type": "tool",
                    "name": "deep_research",
                    "tool_call_id": "call-public",
                    "content": json.dumps(payload if payload is not None else _control_payload()),
                },
                {"langgraph_node": "lead"},
            ]
        ),
    )


class _FakePublicGateway:
    def __init__(self, streams: list[list[GatewaySseRecord]]) -> None:
        self._streams = iter(streams)
        self.created_threads = 0
        self.turns: list[tuple[str, str, str]] = []

    async def create_thread(self) -> str:
        self.created_threads += 1
        return f"thread-{self.created_threads}"

    async def stream_turn(
        self,
        *,
        thread_id: str,
        assistant_id: str,
        user_text: str,
    ) -> AsyncIterator[GatewaySseRecord]:
        self.turns.append((thread_id, assistant_id, user_text))
        for record in next(self._streams):
            yield record


@pytest.mark.asyncio
async def test_observer_creates_one_fresh_thread_then_reuses_only_its_public_thread_for_follow_up() -> None:
    gateway = _FakePublicGateway(
        [
            [GatewaySseRecord(name="metadata", data='{"run_id":"run-1"}'), _tool_record()],
            [GatewaySseRecord(name="metadata", data='{"run_id":"run-2"}'), _tool_record()],
        ]
    )
    observer = GatewayObserver(client=gateway)

    first = await observer.dispatch(
        action="start",
        bundle_id=None,
        messages=(HumanMessage(content="Compare storage costs."),),
    )
    second = await observer.dispatch(
        action="resume",
        bundle_id="b_" + "forged" * 8,
        messages=(HumanMessage(content="Use a practitioner audience."),),
    )

    assert first == _control_payload()
    assert second == _control_payload()
    assert gateway.created_threads == 1
    assert gateway.turns == [
        ("thread-1", "deep-research", "Compare storage costs."),
        ("thread-1", "deep-research", "Use a practitioner audience."),
    ]
    assert observer.correlation.run_id == "run-2"


@pytest.mark.asyncio
async def test_observer_rejects_scripted_context_and_local_control_before_any_gateway_request() -> None:
    gateway = _FakePublicGateway([])
    observer = GatewayObserver(client=gateway)

    with pytest.raises(GatewayObserverError, match="gateway_context_unsupported"):
        await observer.dispatch(
            action="start",
            bundle_id=None,
            messages=(HumanMessage(content="Compare storage costs."),),
            context={"non_interactive": True},
        )
    with pytest.raises(GatewayObserverError, match="gateway_action_unsupported"):
        await observer.dispatch(
            action="cancel",
            bundle_id="b_" + "A" * 43,
            messages=(HumanMessage(content="Compare storage costs."),),
        )

    assert gateway.created_threads == 0
    assert gateway.turns == []


@pytest.mark.asyncio
async def test_valid_custom_progress_stays_withheld_while_only_typed_tool_result_returns() -> None:
    withheld: list[dict[str, object]] = []
    gateway = _FakePublicGateway(
        [
            [
                GatewaySseRecord(
                    name="custom",
                    data=json.dumps(
                        {
                            "type": "deep_research.progress.v1",
                            "phase": "wave0",
                            "operation": "node",
                            "outcome": "started",
                            "bundle_id": "b_" + "A" * 43,
                        }
                    ),
                ),
                _tool_record(),
            ]
        ]
    )
    observer = GatewayObserver(client=gateway, withheld_candidate_observer=withheld.append)

    result = await observer.dispatch(
        action="start",
        bundle_id=None,
        messages=(HumanMessage(content="Compare storage costs."),),
    )

    assert result == _control_payload()
    assert withheld == [
        {
            "type": "deep_research.progress.v1",
            "phase": "wave0",
            "operation": "node",
            "outcome": "started",
            "bundle_id": "b_" + "A" * 43,
        }
    ]


@pytest.mark.asyncio
async def test_end_or_assistant_prose_cannot_manufacture_a_lifecycle_result() -> None:
    gateway = _FakePublicGateway(
        [
            [
                GatewaySseRecord(name="messages-tuple", data='[{"type":"ai","content":"finished"},{}]'),
                GatewaySseRecord(name="end", data="{}"),
            ]
        ]
    )
    observer = GatewayObserver(client=gateway)

    with pytest.raises(GatewayObserverError, match="gateway_typed_result_missing"):
        await observer.dispatch(
            action="start",
            bundle_id=None,
            messages=(HumanMessage(content="Compare storage costs."),),
        )


@pytest.mark.asyncio
async def test_http_client_uses_only_fixed_public_thread_and_stream_shapes() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/api/threads":
            return httpx.Response(200, json={"thread_id": "thread-public"})
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream", "X-Trace-Id": "trace-public"},
            content=b"event: end\ndata: {}\n\n",
        )

    gateway = HttpGatewayPublicClient(transport=httpx.MockTransport(handler))

    assert await gateway.create_thread() == "thread-public"
    records = [
        record
        async for record in gateway.stream_turn(
            thread_id="thread-public",
            assistant_id="deep-research",
            user_text="Keep the exact entered value.  ",
        )
    ]
    await gateway.aclose()

    assert [request.url.path for request in requests] == ["/api/threads", "/api/threads/thread-public/runs/stream"]
    assert [str(request.url) for request in requests] == [
        f"{PUBLIC_GATEWAY_ORIGIN}/api/threads",
        f"{PUBLIC_GATEWAY_ORIGIN}/api/threads/thread-public/runs/stream",
    ]
    assert json.loads(requests[0].content) == {}
    assert json.loads(requests[1].content) == {
        "assistant_id": "deep-research",
        "input": {"messages": [{"type": "human", "content": "Keep the exact entered value.  "}]},
        "stream_mode": ["messages-tuple", "custom"],
    }
    assert records == [GatewaySseRecord(name="end", data="{}", trace_id="trace-public")]
    assert ":2026" not in inspect.getsource(HttpGatewayPublicClient)
    assert "deerflow." not in inspect.getsource(HttpGatewayPublicClient)


@pytest.mark.asyncio
async def test_suspended_tool_message_reconstructs_only_the_existing_typed_command_contract() -> None:
    control = BundleControlResult(
        action=LifecycleAction.START,
        code=ResultCode.SUSPENDED,
        availability=BundleAvailability.AVAILABLE,
        durability=Durability.RESTART_DURABLE,
        bundle_id="b_" + "A" * 43,
        status=LifecycleStatus.SUSPENDED,
        phase=LogicalPhase.HITL1,
        generation=0,
        request_id="drh-public",
        pending_input={"request_id": "drh-public", "pending_phase": "hitl1", "generation": 0, "mode": "text"},
        refinement=BundleRefinementProjection(disposition="none"),
        legal_next_action=LegalNextAction.RESUME,
        execution_trace=("bootstrap", "hitl1"),
    ).model_dump(mode="json", exclude_none=True)
    human_input = {
        "request_id": "drh-public",
        "mode": "text",
        "title": "Scope",
        "context": "Give scope.",
    }
    gateway = _FakePublicGateway(
        [
            [
                GatewaySseRecord(
                    name="messages-tuple",
                    data=json.dumps(
                        [
                            {
                                "type": "tool",
                                "name": "deep_research",
                                "tool_call_id": "call-public",
                                "content": json.dumps(control),
                                "artifact": {"human_input": human_input},
                            },
                            {},
                        ]
                    ),
                )
            ]
        ]
    )

    result = await GatewayObserver(client=gateway).dispatch(
        action="start",
        bundle_id=None,
        messages=(HumanMessage(content="Compare storage costs."),),
    )

    assert isinstance(result, Command)
    [message] = result.update["messages"]
    assert isinstance(message, ToolMessage)
    assert message.content == json.dumps(control)
    assert message.artifact["human_input"]["request_id"] == "drh-public"
    assert message.artifact["human_input"]["mode"] == "text"
    assert message.artifact["human_input"]["title"] == "Scope"
    assert message.artifact["human_input"]["context"] == "Give scope."


@pytest.mark.asyncio
async def test_non_lifecycle_sse_records_are_observations_and_unsafe_custom_data_is_dropped() -> None:
    observations: list[str] = []
    withheld: list[dict[str, object]] = []
    gateway = _FakePublicGateway(
        [
            [
                GatewaySseRecord(name="heartbeat", data="{}"),
                GatewaySseRecord(name="gap", data="{}"),
                GatewaySseRecord(name="error", data='{"detail":"unsafe provider text"}'),
                GatewaySseRecord(name="messages-tuple", data='[{"type":"ai","content":"safe\\ntext"},{}]'),
                GatewaySseRecord(
                    name="custom",
                    data=json.dumps(
                        {
                            "type": "deep_research.progress.v1",
                            "phase": "wave0",
                            "operation": "node",
                            "outcome": "started",
                            "bundle_id": "b_" + "A" * 43,
                            "provider_body": "must not cross the boundary",
                        }
                    ),
                ),
                GatewaySseRecord(name="unknown", data='{"secret":"ignored"}'),
                GatewaySseRecord(name="end", data="{}"),
            ]
        ]
    )
    observer = GatewayObserver(
        client=gateway,
        transport_observer=lambda observation: observations.append(f"{observation.kind}:{observation.detail}"),
        withheld_candidate_observer=withheld.append,
    )

    with pytest.raises(GatewayObserverError, match="gateway_typed_result_missing"):
        await observer.dispatch(
            action="start",
            bundle_id=None,
            messages=(HumanMessage(content="Compare storage costs."),),
        )

    assert withheld == []
    assert observations == [
        "heartbeat:",
        "gap:",
        "error:",
        "assistant_text:safe text",
        "custom_invalid:",
        "end:",
    ]


@pytest.mark.asyncio
async def test_missing_thread_blank_input_and_malformed_tool_result_cannot_start_or_resume_a_turn() -> None:
    gateway = _FakePublicGateway(
        [
            [
                GatewaySseRecord(
                    name="messages-tuple",
                    data='[{"type":"tool","name":"deep_research","tool_call_id":"call-public","content":"not-json"},{}]',
                ),
                GatewaySseRecord(name="end", data="{}"),
            ]
        ]
    )
    observer = GatewayObserver(client=gateway)

    with pytest.raises(GatewayObserverError, match="gateway_follow_up_without_thread"):
        await observer.dispatch(
            action="resume",
            bundle_id=None,
            messages=(HumanMessage(content="Continue."),),
        )
    with pytest.raises(GatewayObserverError, match="gateway_explicit_text_required"):
        await observer.dispatch(
            action="start",
            bundle_id=None,
            messages=(HumanMessage(content="   "),),
        )
    with pytest.raises(GatewayObserverError, match="gateway_typed_result_missing"):
        await observer.dispatch(
            action="start",
            bundle_id=None,
            messages=(HumanMessage(content="Compare storage costs."),),
        )

    assert gateway.created_threads == 1
    assert gateway.turns == [("thread-1", "deep-research", "Compare storage costs.")]


@pytest.mark.asyncio
async def test_duplicate_reordered_malformed_and_unknown_records_remain_non_controlling() -> None:
    withheld: list[dict[str, object]] = []
    observations: list[str] = []
    candidate = {
        "type": "deep_research.progress.v1",
        "phase": "wave0",
        "operation": "node",
        "outcome": "started",
        "bundle_id": "b_" + "A" * 43,
    }
    gateway = _FakePublicGateway(
        [
            [
                GatewaySseRecord(name="custom", data=json.dumps(candidate)),
                GatewaySseRecord(name="metadata", data='{"run_id":"run-later"}'),
                GatewaySseRecord(name="custom", data="not-json"),
                GatewaySseRecord(name="custom", data=json.dumps(candidate)),
                GatewaySseRecord(name="unknown", data='{"untrusted":"ignored"}'),
                GatewaySseRecord(name="gap", data="{}"),
                GatewaySseRecord(name="end", data="{}"),
            ]
        ]
    )
    observer = GatewayObserver(
        client=gateway,
        transport_observer=lambda observation: observations.append(observation.kind),
        withheld_candidate_observer=withheld.append,
    )

    with pytest.raises(GatewayObserverError, match="gateway_typed_result_missing"):
        await observer.dispatch(
            action="start",
            bundle_id="b_" + "forged" * 8,
            messages=(HumanMessage(content="Compare storage costs."),),
        )

    assert withheld == [candidate, candidate]
    assert observations == ["custom_invalid", "gap", "end"]
    assert observer.correlation.run_id == "run-later"


@pytest.mark.asyncio
async def test_missing_custom_event_leaves_typed_lifecycle_result_unchanged() -> None:
    """A stream without any custom event still returns the validated typed result."""

    gateway = _FakePublicGateway(
        [
            [
                GatewaySseRecord(name="heartbeat", data="{}"),
                GatewaySseRecord(name="messages-tuple", data=json.dumps([{"type": "ai", "content": "working"}, {}])),
                _tool_record(),
                GatewaySseRecord(name="gap", data="{}"),
                GatewaySseRecord(name="end", data="{}"),
            ]
        ]
    )
    observer = GatewayObserver(client=gateway)

    result = await observer.dispatch(
        action="start",
        bundle_id=None,
        messages=(HumanMessage(content="Compare storage costs."),),
    )

    assert result == _control_payload()


@pytest.mark.asyncio
async def test_duplicate_reordered_custom_and_gap_leave_typed_result_unchanged() -> None:
    """Duplicate/reordered custom events and a gap never change the lifecycle result."""

    candidate = {
        "type": "deep_research.progress.v1",
        "phase": "wave0",
        "operation": "node",
        "outcome": "started",
        "bundle_id": "b_" + "A" * 43,
    }
    gateway = _FakePublicGateway(
        [
            [
                GatewaySseRecord(name="custom", data=json.dumps(candidate)),
                GatewaySseRecord(name="custom", data=json.dumps(candidate)),
                _tool_record(),
                GatewaySseRecord(name="custom", data=json.dumps(candidate)),
                GatewaySseRecord(name="gap", data="{}"),
                GatewaySseRecord(name="custom", data=json.dumps(candidate)),
                GatewaySseRecord(name="end", data="{}"),
            ]
        ]
    )
    observer = GatewayObserver(client=gateway)

    result = await observer.dispatch(
        action="start",
        bundle_id=None,
        messages=(HumanMessage(content="Compare storage costs."),),
    )

    assert result == _control_payload()


@pytest.mark.asyncio
async def test_custom_events_create_no_acknowledgement_dedupe_or_retry() -> None:
    """Custom events only project; they never create ack, dedupe authority, or retry."""

    candidate = {
        "type": "deep_research.progress.v1",
        "phase": "wave0",
        "operation": "node",
        "outcome": "started",
        "bundle_id": "b_" + "A" * 43,
    }
    gateway = _FakePublicGateway(
        [
            [
                GatewaySseRecord(name="custom", data=json.dumps(candidate)),
                GatewaySseRecord(name="custom", data=json.dumps(candidate)),
                _tool_record(),
                GatewaySseRecord(name="end", data="{}"),
            ]
        ]
    )
    observer = GatewayObserver(client=gateway)

    result = await observer.dispatch(
        action="start",
        bundle_id=None,
        messages=(HumanMessage(content="Compare storage costs."),),
    )
    assert result == _control_payload()
    # One fresh thread and one turn: duplicates never trigger a second request,
    # an acknowledgement, dedupe authority, or an execution retry.
    assert gateway.created_threads == 1
    assert gateway.turns == [("thread-1", "deep-research", "Compare storage costs.")]
    assert observer.correlation == GatewayCorrelation()
