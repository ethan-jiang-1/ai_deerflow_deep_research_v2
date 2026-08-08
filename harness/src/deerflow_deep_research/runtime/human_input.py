"""Trusted outer-message selection and HITL projection.

@impl REG-003
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.graph import END
from langgraph.types import Command

from deerflow_deep_research.domain.lifecycle import (
    AcceptedHumanResponse,
    BundleControlResult,
    HumanInputMode,
    PendingResearchInterrupt,
    ResponseKind,
    serialize_control_result,
    text_only_content,
)


class HumanInputError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"[{code}] {detail}")
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class SelectedStartMessage:
    message_id: str
    text: str


@dataclass(frozen=True)
class ConsumedResponseRetry:
    request_id: str
    message_id: str


@dataclass(frozen=True)
class BrokeredResumeResponse:
    """Ephemeral broker response that is revalidated inside the handler lock."""

    expected_request_id: str
    response: AcceptedHumanResponse


def _response_payload(message: HumanMessage) -> dict[str, Any] | None:
    payload = message.additional_kwargs.get("human_input_response")
    return payload if isinstance(payload, dict) else None


def _is_synthetic(message: HumanMessage) -> bool:
    if _response_payload(message) is not None:
        return False
    if message.additional_kwargs.get("hide_from_ui"):
        return True
    return message.name in {"summary", "dynamic_context", "system_reminder"}


def select_start_message(messages: list[Any] | tuple[Any, ...]) -> SelectedStartMessage:
    candidate: HumanMessage | None = None
    for message in reversed(messages):
        if not isinstance(message, HumanMessage) or _is_synthetic(message):
            continue
        candidate = message
        break
    if candidate is None or _response_payload(candidate) is not None or not candidate.id:
        raise HumanInputError("start_message_invalid", "newest visible user message is not a research request")
    try:
        text = text_only_content(candidate.content)
    except ValueError as exc:
        raise HumanInputError("start_message_invalid", "research request content is invalid") from exc
    return SelectedStartMessage(message_id=str(candidate.id), text=text)


def _latest_actual_human(messages: list[Any] | tuple[Any, ...]) -> HumanMessage | None:
    for message in reversed(messages):
        if isinstance(message, HumanMessage) and not _is_synthetic(message):
            return message
    return None


def _consumed_retry(
    message: HumanMessage | None,
    consumed_request_ids: tuple[str, ...],
    consumed_message_ids: tuple[str, ...],
) -> ConsumedResponseRetry | None:
    if message is None or not message.id:
        return None
    pairs = dict(zip(consumed_message_ids, consumed_request_ids, strict=True))
    request_id = pairs.get(str(message.id))
    if request_id is None:
        return None
    payload = _response_payload(message)
    if payload is not None and payload.get("request_id") != request_id:
        return None
    return ConsumedResponseRetry(request_id=request_id, message_id=str(message.id))


def find_consumed_retry(
    messages: list[Any] | tuple[Any, ...],
    *,
    consumed_request_ids: tuple[str, ...],
    consumed_message_ids: tuple[str, ...],
) -> ConsumedResponseRetry | None:
    if len(consumed_request_ids) != len(consumed_message_ids):
        raise HumanInputError("checkpoint_inconsistent", "consumed response ids are not paired")
    return _consumed_retry(_latest_actual_human(messages), consumed_request_ids, consumed_message_ids)


def extract_resume_response(
    messages: list[Any] | tuple[Any, ...],
    pending: PendingResearchInterrupt,
    *,
    consumed_request_ids: tuple[str, ...],
    consumed_message_ids: tuple[str, ...],
) -> AcceptedHumanResponse | ConsumedResponseRetry:
    replay = find_consumed_retry(
        messages,
        consumed_request_ids=consumed_request_ids,
        consumed_message_ids=consumed_message_ids,
    )
    if replay is not None:
        return replay

    cursor_index = next(
        (
            index
            for index, message in enumerate(messages)
            if isinstance(message, HumanMessage) and message.id == pending.suspension_cursor
        ),
        None,
    )
    if cursor_index is None:
        raise HumanInputError("response_mismatch", "suspension cursor is absent")
    candidate: HumanMessage | None = None
    for message in reversed(messages[cursor_index + 1 :]):
        if not isinstance(message, HumanMessage) or _is_synthetic(message):
            continue
        candidate = message
        break
    if candidate is None or not candidate.id:
        raise HumanInputError("response_mismatch", "no eligible response after suspension")

    payload = _response_payload(candidate)
    if payload is not None:
        if (
            payload.get("version") != 1
            or payload.get("kind") != "human_input_response"
            or payload.get("source") != "deep_research"
            or payload.get("request_id") != pending.request.request_id
        ):
            raise HumanInputError("response_mismatch", "structured response correlation does not match")
        try:
            response = AcceptedHumanResponse(
                request_id=pending.request.request_id,
                message_id=str(candidate.id),
                value=payload.get("value"),
                response_kind=payload.get("response_kind"),
                option_id=payload.get("option_id"),
                action_id=payload.get("action_id"),
            )
        except (TypeError, ValueError) as exc:
            raise HumanInputError("response_invalid", "structured response value is invalid") from exc
        return _validate_response_mode(response, pending)

    try:
        value = text_only_content(candidate.content)
    except ValueError as exc:
        raise HumanInputError("response_invalid", "plain response content is invalid") from exc
    response = AcceptedHumanResponse(
        request_id=pending.request.request_id,
        message_id=str(candidate.id),
        value=value,
        response_kind=ResponseKind.TEXT,
    )
    return _validate_response_mode(response, pending)


def make_brokered_resume_response(
    *,
    pending: PendingResearchInterrupt | None,
    expected_request_id: str,
    value: str,
    message_id: str,
    action_id: str | None = None,
    option_id: str | None = None,
) -> BrokeredResumeResponse:
    """Create an ephemeral response from a pending request or an idempotent retry."""
    if action_id is not None:
        if option_id is not None:
            raise HumanInputError("response_invalid", "brokered response cannot combine action and option")
        if value != action_id:
            raise HumanInputError("response_invalid", "brokered action value does not match action id")
        text = action_id
    elif option_id is not None:
        if value != option_id:
            raise HumanInputError("response_invalid", "brokered option value does not match option id")
        text = option_id
    else:
        try:
            text = text_only_content(value)
        except ValueError as exc:
            raise HumanInputError("response_invalid", "brokered response content is invalid") from exc
    response = AcceptedHumanResponse(
        request_id=expected_request_id,
        message_id=message_id,
        value=text,
        response_kind=(
            ResponseKind.ACTION
            if action_id is not None
            else ResponseKind.OPTION
            if option_id is not None
            else ResponseKind.TEXT
        ),
        action_id=action_id,
        option_id=option_id,
    )
    if pending is not None:
        if expected_request_id != pending.request.request_id:
            raise HumanInputError("response_mismatch", "expected request does not match pending interrupt")
        response = _validate_response_mode(response, pending)
    return BrokeredResumeResponse(expected_request_id=expected_request_id, response=response)


def extract_brokered_resume_response(
    brokered: BrokeredResumeResponse,
    pending: PendingResearchInterrupt | None,
    *,
    consumed_request_ids: tuple[str, ...],
    consumed_message_ids: tuple[str, ...],
) -> AcceptedHumanResponse | ConsumedResponseRetry:
    """Recheck an external operation's response under the handler namespace lock."""
    if len(consumed_request_ids) != len(consumed_message_ids):
        raise HumanInputError("checkpoint_inconsistent", "consumed response ids are not paired")
    response = brokered.response
    if brokered.expected_request_id != response.request_id:
        raise HumanInputError("response_mismatch", "brokered response correlation is invalid")
    pairs = dict(zip(consumed_message_ids, consumed_request_ids, strict=True))
    consumed_request_id = pairs.get(response.message_id)
    if consumed_request_id is not None:
        if consumed_request_id != response.request_id:
            raise HumanInputError("response_mismatch", "brokered retry has a different request")
        return ConsumedResponseRetry(request_id=response.request_id, message_id=response.message_id)
    if response.request_id in consumed_request_ids:
        raise HumanInputError("response_mismatch", "pending request was already answered")
    if pending is None or pending.request.request_id != brokered.expected_request_id:
        raise HumanInputError("response_mismatch", "pending interrupt changed before broker dispatch")
    return _validate_response_mode(response, pending)


def _validate_response_mode(
    response: AcceptedHumanResponse,
    pending: PendingResearchInterrupt,
) -> AcceptedHumanResponse:
    if pending.request.mode is HumanInputMode.TEXT:
        if response.response_kind is ResponseKind.ACTION:
            if response.action_id not in pending.request.action_ids:
                raise HumanInputError("response_invalid", "action is not advertised")
            return response
        if response.response_kind is not ResponseKind.TEXT:
            raise HumanInputError("response_invalid", "text request requires a text response")
        if response.value in pending.request.action_ids:
            raise HumanInputError("response_invalid", "action id cannot be sent as plain text")
        return response
    advertised = {option.id.value for option in pending.request.options}
    if response.response_kind is ResponseKind.OPTION:
        if response.option_id != response.value or response.value not in advertised:
            raise HumanInputError("response_invalid", "choice option id/value is invalid")
        return response
    if pending.phase == "hitl1":
        raise HumanInputError("response_invalid", "hitl1 language choice requires an option response")
    normalized = response.value.strip().lower()
    if normalized not in advertised:
        raise HumanInputError("response_invalid", "plain choice does not match an advertised value")
    return response.model_copy(update={"value": normalized})


def pending_from_snapshot(snapshot: Any) -> PendingResearchInterrupt | None:
    interrupts = [interrupt for task in snapshot.tasks for interrupt in task.interrupts]
    if not interrupts:
        return None
    if len(interrupts) != 1:
        raise HumanInputError("checkpoint_inconsistent", "research lifecycle must have one pending interrupt")
    try:
        return PendingResearchInterrupt.model_validate(interrupts[0].value)
    except (TypeError, ValueError) as exc:
        raise HumanInputError("checkpoint_inconsistent", "pending interrupt descriptor is invalid") from exc


def project_suspension(
    *,
    pending: PendingResearchInterrupt,
    result: BundleControlResult,
    tool_call_id: str,
) -> Command:
    if result.request_id != pending.request.request_id:
        raise HumanInputError("checkpoint_inconsistent", "result and interrupt request ids differ")
    projection = result.pending_input
    if (
        projection is None
        or projection.request_id != pending.request.request_id
        or projection.pending_phase != pending.phase
        or projection.generation != pending.generation
        or projection.mode != pending.request.mode.value
    ):
        raise HumanInputError("checkpoint_inconsistent", "result and interrupt pending input differ")
    artifact_request = pending.request.model_dump(mode="json")
    if pending.request.mode is HumanInputMode.TEXT:
        artifact_request.pop("options", None)
    message = ToolMessage(
        content=serialize_control_result(result),
        tool_call_id=tool_call_id,
        id=pending.request.request_id,
        name="deep_research",
        artifact={"human_input": artifact_request},
    )
    return Command(update={"messages": [message]}, goto=END)


__all__ = [
    "ConsumedResponseRetry",
    "BrokeredResumeResponse",
    "HumanInputError",
    "SelectedStartMessage",
    "extract_resume_response",
    "extract_brokered_resume_response",
    "find_consumed_retry",
    "make_brokered_resume_response",
    "pending_from_snapshot",
    "project_suspension",
    "select_start_message",
]
