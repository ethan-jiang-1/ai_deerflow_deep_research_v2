"""Bounded public Gateway transport for the local operator entrypoints.

@impl GOO-001
@impl GOO-002
@impl PRS-005
"""

from __future__ import annotations

import inspect
import json
import re
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

import httpx
from httpx_sse import aconnect_sse
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.types import Command

from deerflow_deep_research.domain.lifecycle import BundleControlResult, HumanInputRequest

PUBLIC_GATEWAY_ORIGIN = "http://127.0.0.1:8001"
PUBLIC_ASSISTANT_ID = "deep-research"
_SAFE_CORRELATION = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_BUNDLE_ID = re.compile(r"^b_[A-Za-z0-9_-]{43}$")
_PROGRESS_REQUIRED = frozenset({"type", "phase", "operation", "outcome", "bundle_id"})
_PROGRESS_OPTIONAL = frozenset({"work_id", "attempt_id", "code", "count", "outer_thread_id", "outer_run_id"})


class GatewayObserverError(RuntimeError):
    """A bounded public transport failure that never exposes stream contents."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class GatewaySseRecord:
    """One structured public SSE record with an optional response trace reference."""

    name: str
    data: str
    trace_id: str | None = None


@dataclass(frozen=True)
class GatewayCorrelation:
    """Process-local public correlation; never a run, Bundle, or recovery selector."""

    run_id: str | None = None
    trace_id: str | None = None


@dataclass(frozen=True)
class GatewayTransportObservation:
    """Bounded presentation-only transport fact."""

    kind: str
    detail: str = ""


class GatewayPublicClient(Protocol):
    """Only public thread-create and run-stream operations enter this adapter."""

    async def create_thread(self) -> str: ...

    def stream_turn(
        self,
        *,
        thread_id: str,
        assistant_id: str,
        user_text: str,
    ) -> AsyncIterator[GatewaySseRecord]: ...


ObserverCallback = Callable[[GatewayTransportObservation], None | Awaitable[None]]
WithheldCandidateCallback = Callable[[dict[str, object]], None | Awaitable[None]]


class HttpGatewayPublicClient:
    """HTTP/SSE implementation over the configured direct local Gateway origin."""

    def __init__(self, *, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._client = httpx.AsyncClient(
            base_url=PUBLIC_GATEWAY_ORIGIN,
            timeout=httpx.Timeout(30.0),
            transport=transport,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def create_thread(self) -> str:
        try:
            response = await self._client.post("/api/threads", json={})
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise GatewayObserverError("gateway_thread_create_failed") from exc
        thread_id = payload.get("thread_id") if isinstance(payload, Mapping) else None
        if not _safe_correlation(thread_id):
            raise GatewayObserverError("gateway_thread_response_invalid")
        return thread_id

    async def stream_turn(
        self,
        *,
        thread_id: str,
        assistant_id: str,
        user_text: str,
    ) -> AsyncIterator[GatewaySseRecord]:
        request = {
            "assistant_id": assistant_id,
            "input": {"messages": [{"type": "human", "content": user_text}]},
            "stream_mode": ["messages-tuple", "custom"],
        }
        try:
            async with aconnect_sse(
                self._client,
                "POST",
                f"/api/threads/{thread_id}/runs/stream",
                json=request,
            ) as event_source:
                event_source.response.raise_for_status()
                trace_id = _safe_correlation(event_source.response.headers.get("X-Trace-Id"))
                async for event in event_source.aiter_sse():
                    yield GatewaySseRecord(name=event.event, data=event.data, trace_id=trace_id)
        except GatewayObserverError:
            raise
        except httpx.HTTPError as exc:
            raise GatewayObserverError("gateway_stream_failed") from exc


class GatewayObserver:
    """LifecycleTransport-compatible public stream adapter without local control authority."""

    def __init__(
        self,
        *,
        client: GatewayPublicClient,
        transport_observer: ObserverCallback | None = None,
        withheld_candidate_observer: WithheldCandidateCallback | None = None,
    ) -> None:
        self._client = client
        self._transport_observer = transport_observer
        self._withheld_candidate_observer = withheld_candidate_observer
        self._thread_id: str | None = None
        self._correlation = GatewayCorrelation()

    @property
    def correlation(self) -> GatewayCorrelation:
        return self._correlation

    async def aclose(self) -> None:
        closer = getattr(self._client, "aclose", None)
        if closer is not None:
            result = closer()
            if inspect.isawaitable(result):
                await result

    async def dispatch(
        self,
        *,
        action: str,
        bundle_id: str | None,
        messages: tuple[Any, ...],
        context: Mapping[str, Any] | None = None,
    ) -> object:
        """Submit one explicit user turn and return only a validated lifecycle result."""
        del bundle_id  # Shared experience retains this locally; it never crosses Gateway.
        if context:
            raise GatewayObserverError("gateway_context_unsupported")
        if action not in {"start", "resume"}:
            raise GatewayObserverError("gateway_action_unsupported")
        user_text = _last_explicit_text(messages)
        if action == "start":
            self._thread_id = await self._client.create_thread()
            self._correlation = GatewayCorrelation()
        elif self._thread_id is None:
            raise GatewayObserverError("gateway_follow_up_without_thread")

        assert self._thread_id is not None
        typed_result: object | None = None
        async for record in self._client.stream_turn(
            thread_id=self._thread_id,
            assistant_id=PUBLIC_ASSISTANT_ID,
            user_text=user_text,
        ):
            result = await self._consume_record(record)
            if result is not None:
                typed_result = result
        if typed_result is None:
            raise GatewayObserverError("gateway_typed_result_missing")
        return typed_result

    async def _consume_record(self, record: GatewaySseRecord) -> object | None:
        if record.trace_id is not None:
            self._correlation = GatewayCorrelation(run_id=self._correlation.run_id, trace_id=record.trace_id)
        if record.name == "metadata":
            metadata = _json_mapping(record.data)
            run_id = _safe_correlation(metadata.get("run_id")) if metadata is not None else None
            if run_id is not None:
                self._correlation = GatewayCorrelation(run_id=run_id, trace_id=self._correlation.trace_id)
            return None
        if record.name in {"messages", "messages-tuple"}:
            message = _find_message(_json_value(record.data))
            if message is None:
                return None
            if _message_type(message) == "ai":
                await self._observe(
                    GatewayTransportObservation(kind="assistant_text", detail=_safe_text(message.get("content")))
                )
                return None
            if _message_type(message) != "tool" or _tool_name(message) != "deep_research":
                return None
            return _validated_tool_result(message)
        if record.name == "custom":
            candidate = _valid_progress_candidate(_json_mapping(record.data))
            if candidate is not None:
                await self._withhold(candidate)
            else:
                await self._observe(GatewayTransportObservation(kind="custom_invalid"))
            return None
        if record.name in {"heartbeat", "gap", "error", "end"}:
            await self._observe(GatewayTransportObservation(kind=record.name))
        return None

    async def _observe(self, observation: GatewayTransportObservation) -> None:
        if self._transport_observer is None:
            return
        result = self._transport_observer(observation)
        if inspect.isawaitable(result):
            await result

    async def _withhold(self, candidate: dict[str, object]) -> None:
        if self._withheld_candidate_observer is None:
            return
        result = self._withheld_candidate_observer(candidate)
        if inspect.isawaitable(result):
            await result


def _last_explicit_text(messages: tuple[Any, ...]) -> str:
    for message in reversed(messages):
        if isinstance(message, HumanMessage) and isinstance(message.content, str) and message.content.strip():
            return message.content
    raise GatewayObserverError("gateway_explicit_text_required")


def _json_value(raw: str) -> object | None:
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


def _json_mapping(raw: str) -> Mapping[str, object] | None:
    value = _json_value(raw)
    return value if isinstance(value, Mapping) else None


def _find_message(value: object) -> Mapping[str, object] | None:
    if isinstance(value, Mapping):
        if _message_type(value) in {"ai", "tool"}:
            return value
        for key in ("message", "messages", "data"):
            found = _find_message(value.get(key))
            if found is not None:
                return found
        return None
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            found = _find_message(item)
            if found is not None:
                return found
    return None


def _message_type(message: Mapping[str, object]) -> str:
    value = message.get("type") or message.get("message_type")
    if not isinstance(value, str):
        return ""
    normalized = value.lower()
    if normalized in {"aimessagechunk", "aimessage"}:
        return "ai"
    if normalized in {"toolmessage", "toolmessagechunk"}:
        return "tool"
    return normalized


def _tool_name(message: Mapping[str, object]) -> str | None:
    value = message.get("name") or message.get("tool_name")
    return value if isinstance(value, str) else None


def _validated_tool_result(message: Mapping[str, object]) -> object | None:
    content = message.get("content")
    if not isinstance(content, str) or len(content) > 32_768:
        return None
    try:
        control = BundleControlResult.model_validate_json(content)
    except ValueError:
        return None
    artifact = message.get("artifact")
    if not isinstance(artifact, Mapping) or not isinstance(artifact.get("human_input"), Mapping):
        return control.model_dump(mode="json", exclude_none=True)
    try:
        request = HumanInputRequest.model_validate(dict(artifact["human_input"]))
    except ValueError:
        return None
    tool_call_id = message.get("tool_call_id")
    if not isinstance(tool_call_id, str) or not _safe_correlation(tool_call_id):
        return None
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=content,
                    tool_call_id=tool_call_id,
                    id=request.request_id,
                    artifact={"human_input": request.model_dump(mode="json")},
                )
            ]
        }
    )


def _valid_progress_candidate(value: Mapping[str, object] | None) -> dict[str, object] | None:
    if value is None or set(value) - (_PROGRESS_REQUIRED | _PROGRESS_OPTIONAL) or not _PROGRESS_REQUIRED <= set(value):
        return None
    if value.get("type") != "deep_research.progress.v1" or not _BUNDLE_ID.fullmatch(str(value.get("bundle_id", ""))):
        return None
    for key in ("phase", "operation", "outcome"):
        if not _safe_correlation(value.get(key)):
            return None
    for key in _PROGRESS_OPTIONAL - {"count"}:
        if key in value and not _safe_correlation(value[key]):
            return None
    if "count" in value and (
        not isinstance(value["count"], int) or isinstance(value["count"], bool) or value["count"] < 0
    ):
        return None
    return dict(value)


def _safe_correlation(value: object) -> str | None:
    return value if isinstance(value, str) and _SAFE_CORRELATION.fullmatch(value) else None


def _safe_text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    compact = " ".join("".join(char if char.isprintable() else " " for char in value).split())
    return compact[:512]


__all__ = [
    "GatewayCorrelation",
    "GatewayObserver",
    "GatewayObserverError",
    "GatewayPublicClient",
    "GatewaySseRecord",
    "GatewayTransportObservation",
    "HttpGatewayPublicClient",
    "PUBLIC_ASSISTANT_ID",
    "PUBLIC_GATEWAY_ORIGIN",
]
