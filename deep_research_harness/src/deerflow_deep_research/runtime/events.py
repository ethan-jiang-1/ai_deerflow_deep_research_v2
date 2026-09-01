"""Safe standard-log and live projections for runtime facts.

@impl RTO-001
@impl RTO-003
@impl REJ-005
"""

from __future__ import annotations

import asyncio
import logging
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol

EVENT_NAME = "deep_research.runtime_observation"
LIVE_EVENT_TYPE = "deep_research.progress.v1"
_FIELD_NAMES = frozenset(
    {
        "event_type",
        "bundle_id",
        "phase",
        "operation",
        "outcome",
        "work_id",
        "attempt_id",
        "code",
        "count",
        "outer_thread_id",
        "outer_run_id",
    }
)
_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,127}")


class ObservationValidationError(ValueError):
    """Raised when a candidate is outside the safe log-projection contract."""


class LiveEventValidationError(ValueError):
    """Raised when a payload is outside the closed live-event contract."""


class ObservationOutcome(StrEnum):
    STARTED = "started"
    COMPLETED = "completed"
    RETRYING = "retrying"
    REJECTED = "rejected"
    DEGRADED = "degraded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
    STOPPED = "stopped"
    SUSPENDED = "suspended"


_LIVE_OUTCOMES = {
    "node": frozenset(
        {
            ObservationOutcome.STARTED,
            ObservationOutcome.COMPLETED,
            ObservationOutcome.FAILED,
            ObservationOutcome.SUSPENDED,
        }
    ),
    "gate": frozenset(
        {
            ObservationOutcome.COMPLETED,
            ObservationOutcome.REJECTED,
            ObservationOutcome.CANCELLED,
            ObservationOutcome.STOPPED,
            ObservationOutcome.BLOCKED,
            ObservationOutcome.FAILED,
        }
    ),
    "attempt": frozenset({ObservationOutcome.STARTED, ObservationOutcome.FAILED}),
    "submit": frozenset({ObservationOutcome.COMPLETED}),
    "retry": frozenset({ObservationOutcome.RETRYING}),
    "exhaustion": frozenset({ObservationOutcome.FAILED}),
    "validation": frozenset({ObservationOutcome.REJECTED}),
}


class ObservationCode(StrEnum):
    VALIDATION_REJECTED = "validation_rejected"
    RETRYING = "retrying"
    OBSERVATION_DEGRADED = "observation_degraded"
    PROVIDER_FAILED = "provider_failed"
    TOOL_FAILED = "tool_failed"
    ATTEMPT_EXHAUSTED = "attempt_exhausted"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
    STOPPED = "stopped"


class LiveEventSink(Protocol):
    """Opaque current-runtime live projection with no control capability."""

    def emit(self, payload: Mapping[str, object]) -> None: ...


@dataclass(frozen=True)
class _StreamEventSink:
    writer: Callable[[object], None]

    def emit(self, payload: Mapping[str, object]) -> None:
        self.writer(validate_live_payload(payload))


def make_stream_event_sink(writer: object) -> LiveEventSink | None:
    """Reduce the current public runtime writer to the project-owned sink."""

    if not callable(writer):
        return None
    return _StreamEventSink(writer=writer)


@dataclass(frozen=True)
class SafeObservation:
    """One bounded fact that may be logged without affecting its owner."""

    phase: str
    operation: str
    outcome: ObservationOutcome
    bundle_id: str | None = None
    work_id: str | None = None
    attempt_id: str | None = None
    code: ObservationCode | None = None
    count: int | None = None
    outer_thread_id: str | None = None
    outer_run_id: str | None = None

    def __post_init__(self) -> None:
        for value in (self.phase, self.operation):
            if not isinstance(value, str) or not _TOKEN_RE.fullmatch(value):
                raise ObservationValidationError("observation_token_invalid")
        for value in (
            self.bundle_id,
            self.work_id,
            self.attempt_id,
            self.outer_thread_id,
            self.outer_run_id,
        ):
            if value is not None and (not isinstance(value, str) or not _TOKEN_RE.fullmatch(value)):
                raise ObservationValidationError("observation_correlation_invalid")
        if not isinstance(self.outcome, ObservationOutcome):
            raise ObservationValidationError("observation_outcome_invalid")
        if self.code is not None and not isinstance(self.code, ObservationCode):
            raise ObservationValidationError("observation_code_invalid")
        if self.count is not None and (
            not isinstance(self.count, int) or isinstance(self.count, bool) or not 1 <= self.count <= 1_000_000
        ):
            raise ObservationValidationError("observation_count_invalid")


def to_log_extra(observation: SafeObservation) -> dict[str, str | int]:
    """Serialize a validated fact into the exact safe logging extra fields."""

    if not isinstance(observation, SafeObservation):
        raise ObservationValidationError("safe_observation_required")
    extra: dict[str, str | int] = {
        "event_type": EVENT_NAME,
        "phase": observation.phase,
        "operation": observation.operation,
        "outcome": observation.outcome.value,
    }
    for name, value in (
        ("bundle_id", observation.bundle_id),
        ("work_id", observation.work_id),
        ("attempt_id", observation.attempt_id),
        ("code", None if observation.code is None else observation.code.value),
        ("count", observation.count),
        ("outer_thread_id", observation.outer_thread_id),
        ("outer_run_id", observation.outer_run_id),
    ):
        if value is not None:
            extra[name] = value
    return extra


def observation_from_fields(fields: Mapping[str, object]) -> SafeObservation:
    """Validate a generic boundary candidate before it reaches a logger."""

    if not isinstance(fields, Mapping) or set(fields) - _FIELD_NAMES:
        raise ObservationValidationError("observation_fields_invalid")
    if fields.get("event_type") != EVENT_NAME:
        raise ObservationValidationError("observation_event_type_invalid")
    required = ("phase", "operation", "outcome")
    if any(not isinstance(fields.get(name), str) for name in required):
        raise ObservationValidationError("observation_required_field_invalid")
    for name in ("bundle_id", "work_id", "attempt_id", "code", "outer_thread_id", "outer_run_id"):
        if name in fields and not isinstance(fields[name], str):
            raise ObservationValidationError("observation_optional_field_invalid")
    if "count" in fields and (not isinstance(fields["count"], int) or isinstance(fields["count"], bool)):
        raise ObservationValidationError("observation_optional_field_invalid")
    try:
        outcome = ObservationOutcome(str(fields["outcome"]))
        code = ObservationCode(str(fields["code"])) if "code" in fields else None
    except ValueError as exc:
        raise ObservationValidationError("observation_closed_value_invalid") from exc
    return SafeObservation(
        phase=str(fields["phase"]),
        operation=str(fields["operation"]),
        outcome=outcome,
        bundle_id=fields.get("bundle_id") if isinstance(fields.get("bundle_id"), str) else None,
        work_id=fields.get("work_id") if isinstance(fields.get("work_id"), str) else None,
        attempt_id=fields.get("attempt_id") if isinstance(fields.get("attempt_id"), str) else None,
        code=code,
        count=fields.get("count") if isinstance(fields.get("count"), int) else None,
        outer_thread_id=(fields.get("outer_thread_id") if isinstance(fields.get("outer_thread_id"), str) else None),
        outer_run_id=fields.get("outer_run_id") if isinstance(fields.get("outer_run_id"), str) else None,
    )


def level_for(observation: SafeObservation) -> int:
    """Map an accepted fact to its fixed operational severity."""

    if observation.outcome in {
        ObservationOutcome.RETRYING,
        ObservationOutcome.REJECTED,
        ObservationOutcome.DEGRADED,
    }:
        return logging.WARNING
    if observation.outcome in {
        ObservationOutcome.FAILED,
        ObservationOutcome.CANCELLED,
        ObservationOutcome.BLOCKED,
        ObservationOutcome.STOPPED,
    }:
        return logging.ERROR
    return logging.INFO


def project_observation(observation: SafeObservation, *, logger: logging.Logger | Any) -> None:
    """Write one safe record while keeping handler failures observational."""

    payload = to_log_extra(observation)
    try:
        logger.log(level_for(observation), EVENT_NAME, extra=payload)
    except asyncio.CancelledError:
        raise
    except Exception:
        return


def _to_live_payload(observation: SafeObservation) -> dict[str, object] | None:
    if observation.bundle_id is None:
        return None
    if observation.outcome not in _LIVE_OUTCOMES.get(observation.operation, frozenset()):
        return None
    if observation.operation in {"node", "gate"} and observation.attempt_id is None:
        return None
    if observation.operation in {"attempt", "submit", "retry", "exhaustion"} and (
        observation.work_id is None or observation.attempt_id is None
    ):
        return None
    if observation.operation == "retry" and observation.count is None:
        return None
    if observation.operation == "validation" and observation.code is None:
        return None
    payload: dict[str, object] = {
        "type": LIVE_EVENT_TYPE,
        "phase": observation.phase,
        "operation": observation.operation,
        "outcome": observation.outcome.value,
        "bundle_id": observation.bundle_id,
    }
    for name, value in (
        ("work_id", observation.work_id),
        ("attempt_id", observation.attempt_id),
        ("code", None if observation.code is None else observation.code.value),
        ("count", observation.count),
        ("outer_thread_id", observation.outer_thread_id),
        ("outer_run_id", observation.outer_run_id),
    ):
        if value is not None:
            payload[name] = value
    return payload


def validate_live_payload(payload: Mapping[str, object]) -> dict[str, object]:
    """Validate the exact current live payload immediately before writer use."""

    required = {"type", "phase", "operation", "outcome", "bundle_id"}
    optional = {"work_id", "attempt_id", "code", "count", "outer_thread_id", "outer_run_id"}
    if not isinstance(payload, Mapping) or set(payload) - required - optional or required - set(payload):
        raise LiveEventValidationError("live_event_fields_invalid")
    if payload.get("type") != LIVE_EVENT_TYPE:
        raise LiveEventValidationError("live_event_type_invalid")
    for name in ("phase", "operation", "outcome", "bundle_id"):
        if not isinstance(payload.get(name), str):
            raise LiveEventValidationError("live_event_required_field_invalid")
    for name in ("work_id", "attempt_id", "code", "outer_thread_id", "outer_run_id"):
        if name in payload and not isinstance(payload[name], str):
            raise LiveEventValidationError("live_event_optional_field_invalid")
    if "count" in payload and (not isinstance(payload["count"], int) or isinstance(payload["count"], bool)):
        raise LiveEventValidationError("live_event_optional_field_invalid")
    try:
        observation = SafeObservation(
            phase=str(payload["phase"]),
            operation=str(payload["operation"]),
            outcome=ObservationOutcome(str(payload["outcome"])),
            bundle_id=str(payload["bundle_id"]),
            work_id=payload.get("work_id") if isinstance(payload.get("work_id"), str) else None,
            attempt_id=payload.get("attempt_id") if isinstance(payload.get("attempt_id"), str) else None,
            code=ObservationCode(str(payload["code"])) if "code" in payload else None,
            count=payload.get("count") if isinstance(payload.get("count"), int) else None,
            outer_thread_id=(
                payload.get("outer_thread_id") if isinstance(payload.get("outer_thread_id"), str) else None
            ),
            outer_run_id=payload.get("outer_run_id") if isinstance(payload.get("outer_run_id"), str) else None,
        )
    except (ObservationValidationError, ValueError) as exc:
        raise LiveEventValidationError("live_event_value_invalid") from exc
    if _to_live_payload(observation) is None:
        raise LiveEventValidationError("live_event_operation_invalid")
    return dict(payload)


@dataclass(frozen=True)
class RuntimeObservationProjection:
    """Runtime-bound implementation of the non-checkpointed observation protocol."""

    bundle_id: str | None = None
    outer_thread_id: str | None = None
    outer_run_id: str | None = None
    event_sink: LiveEventSink | None = None

    def emit(self, fields: Mapping[str, object], *, logger: logging.Logger | Any) -> None:
        """Project a synchronous fact without admitting untrusted correlation."""

        if "event_type" in fields or "outer_thread_id" in fields or "outer_run_id" in fields:
            return
        if self.bundle_id is not None and fields.get("bundle_id") not in (None, self.bundle_id):
            return
        payload: dict[str, object] = {"event_type": EVENT_NAME, **fields}
        if self.bundle_id is not None:
            payload["bundle_id"] = self.bundle_id
        if isinstance(self.outer_thread_id, str) and _TOKEN_RE.fullmatch(self.outer_thread_id):
            payload["outer_thread_id"] = self.outer_thread_id
        if isinstance(self.outer_run_id, str) and _TOKEN_RE.fullmatch(self.outer_run_id):
            payload["outer_run_id"] = self.outer_run_id
        try:
            observation = observation_from_fields(payload)
        except ObservationValidationError:
            return
        project_observation(observation, logger=logger)
        live_payload = _to_live_payload(observation)
        if live_payload is not None and self.event_sink is not None:
            try:
                self.event_sink.emit(live_payload)
            except asyncio.CancelledError:
                raise
            except Exception:
                project_observation(
                    SafeObservation(
                        phase=observation.phase,
                        operation="live_event",
                        outcome=ObservationOutcome.DEGRADED,
                        bundle_id=observation.bundle_id,
                        work_id=observation.work_id,
                        attempt_id=observation.attempt_id,
                        code=ObservationCode.OBSERVATION_DEGRADED,
                        outer_thread_id=observation.outer_thread_id,
                        outer_run_id=observation.outer_run_id,
                    ),
                    logger=logger,
                )

    async def aemit(self, fields: Mapping[str, object], *, logger: logging.Logger | Any) -> None:
        """Project an asynchronous owner's fact through the same bounded seam."""

        self.emit(fields, logger=logger)


__all__ = [
    "EVENT_NAME",
    "LIVE_EVENT_TYPE",
    "LiveEventValidationError",
    "LiveEventSink",
    "ObservationCode",
    "ObservationOutcome",
    "ObservationValidationError",
    "RuntimeObservationProjection",
    "SafeObservation",
    "level_for",
    "make_stream_event_sink",
    "observation_from_fields",
    "project_observation",
    "to_log_extra",
    "validate_live_payload",
]
