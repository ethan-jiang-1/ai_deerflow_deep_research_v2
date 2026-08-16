"""Safe standard-log projection contract.

@impl RTO-001
@impl RTO-003
@impl REJ-005
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import pytest

from deerflow_deep_research.runtime import events


class RecordingLogger:
    def __init__(self) -> None:
        self.records: list[tuple[int, str, dict[str, object]]] = []

    def log(self, level: int, message: str, *, extra: dict[str, object]) -> None:
        self.records.append((level, message, extra))


class FailingLogger:
    def __init__(self) -> None:
        self.calls = 0

    def log(self, level: int, message: str, *, extra: dict[str, object]) -> None:
        self.calls += 1
        raise OSError("configured log sink unavailable")


class CancelledLogger:
    def log(self, level: int, message: str, *, extra: dict[str, object]) -> None:
        raise asyncio.CancelledError


class RecordingWriter:
    def __init__(self) -> None:
        self.payloads: list[dict[str, object]] = []

    def __call__(self, payload: dict[str, object]) -> None:
        self.payloads.append(payload)


class FailingWriter:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, _payload: object) -> None:
        self.calls += 1
        raise RuntimeError("secret writer failure")


class CancelledWriter:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, _payload: object) -> None:
        self.calls += 1
        raise asyncio.CancelledError


def test_safe_observation_has_closed_log_extra_and_no_application_trace_field() -> None:
    observation = events.SafeObservation(
        phase="work_units",
        operation="attempt_started",
        outcome=events.ObservationOutcome.STARTED,
        bundle_id="bundle-1",
        work_id="work-1",
        attempt_id="attempt-1",
        count=2,
        outer_thread_id="thread-1",
        outer_run_id="run-1",
    )

    assert events.to_log_extra(observation) == {
        "event_type": "deep_research.runtime_observation",
        "bundle_id": "bundle-1",
        "phase": "work_units",
        "operation": "attempt_started",
        "outcome": "started",
        "work_id": "work-1",
        "attempt_id": "attempt-1",
        "count": 2,
        "outer_thread_id": "thread-1",
        "outer_run_id": "run-1",
    }
    assert "trace_id" not in events.to_log_extra(observation)


def test_safe_observation_schema_rejects_unsafe_fields() -> None:
    for fields in (
        {
            "event_type": "deep_research.runtime_observation",
            "phase": "validation",
            "operation": "candidate_rejected",
            "outcome": "rejected",
            "detail": "token=sk-not-safe",
        },
        {
            "event_type": "deep_research.runtime_observation.v2",
            "phase": "validation",
            "operation": "candidate_rejected",
            "outcome": "rejected",
        },
        {
            "event_type": "deep_research.runtime_observation",
            "phase": "validation",
            "operation": "candidate_rejected",
            "outcome": "rejected",
            "code": "arbitrary-model-output",
        },
        {
            "event_type": "deep_research.runtime_observation",
            "phase": "validation",
            "operation": "candidate_rejected",
            "outcome": "rejected",
            "trace_id": "caller-forged",
        },
    ):
        with pytest.raises(events.ObservationValidationError):
            events.observation_from_fields(fields)


def test_safe_observation_logs_once_with_required_level() -> None:
    logger = RecordingLogger()
    observation = events.SafeObservation(
        phase="validation",
        operation="candidate_rejected",
        outcome=events.ObservationOutcome.REJECTED,
        code=events.ObservationCode.VALIDATION_REJECTED,
    )

    events.project_observation(observation, logger=logger)

    assert logger.records == [
        (
            logging.WARNING,
            "deep_research.runtime_observation",
            {
                "event_type": "deep_research.runtime_observation",
                "phase": "validation",
                "operation": "candidate_rejected",
                "outcome": "rejected",
                "code": "validation_rejected",
            },
        )
    ]


def test_runtime_bound_projection_adds_only_trusted_correlation() -> None:
    logger = RecordingLogger()
    projection = events.RuntimeObservationProjection(
        bundle_id="bundle-1",
        outer_thread_id="thread-1",
        outer_run_id="run-1",
    )

    projection.emit(
        {
            "phase": "wave1",
            "operation": "validation",
            "outcome": "rejected",
            "work_id": "work-1",
            "attempt_id": "attempt-1",
            "code": "validation_rejected",
        },
        logger=logger,
    )
    projection.emit(
        {
            "phase": "wave1",
            "operation": "validation",
            "outcome": "rejected",
            "outer_thread_id": "caller-forged",
        },
        logger=logger,
    )
    projection.emit(
        {
            "phase": "wave1",
            "operation": "validation",
            "outcome": "rejected",
            "bundle_id": "other-bundle",
        },
        logger=logger,
    )

    assert logger.records == [
        (
            logging.WARNING,
            "deep_research.runtime_observation",
            {
                "event_type": "deep_research.runtime_observation",
                "phase": "wave1",
                "operation": "validation",
                "outcome": "rejected",
                "bundle_id": "bundle-1",
                "work_id": "work-1",
                "attempt_id": "attempt-1",
                "code": "validation_rejected",
                "outer_thread_id": "thread-1",
                "outer_run_id": "run-1",
            },
        )
    ]


def test_runtime_observation_projection_logs_and_emits_one_live_node_fact() -> None:
    logger = RecordingLogger()
    writer = RecordingWriter()
    projection = events.RuntimeObservationProjection(
        bundle_id="bundle-1",
        outer_thread_id="thread-1",
        outer_run_id="run-1",
        event_sink=events.make_stream_event_sink(writer),
    )

    projection.emit(
        {
            "phase": "wave0",
            "operation": "node",
            "outcome": "started",
            "attempt_id": "attempt-1",
        },
        logger=logger,
    )

    assert len(logger.records) == 1
    assert writer.payloads == [
        {
            "type": "deep_research.progress.v1",
            "phase": "wave0",
            "operation": "node",
            "outcome": "started",
            "bundle_id": "bundle-1",
            "attempt_id": "attempt-1",
            "outer_thread_id": "thread-1",
            "outer_run_id": "run-1",
        }
    ]


@pytest.mark.parametrize(
    ("operation", "outcome", "specific"),
    [("node", outcome, {"attempt_id": "attempt-1"}) for outcome in ("started", "completed", "failed")]
    + [
        ("gate", outcome, {"attempt_id": "attempt-1"})
        for outcome in ("completed", "rejected", "cancelled", "stopped", "blocked", "failed")
    ]
    + [("attempt", outcome, {"work_id": "work-1", "attempt_id": "attempt-1"}) for outcome in ("started", "failed")]
    + [
        ("submit", "completed", {"work_id": "work-1", "attempt_id": "attempt-1"}),
        (
            "retry",
            "retrying",
            {"work_id": "work-1", "attempt_id": "attempt-1", "count": 2},
        ),
        ("exhaustion", "failed", {"work_id": "work-1", "attempt_id": "attempt-1"}),
        ("validation", "rejected", {"code": "validation_rejected"}),
    ],
)
def test_runtime_observation_projection_uses_the_exact_live_visible_matrix(
    operation: str,
    outcome: str,
    specific: dict[str, object],
) -> None:
    writer = RecordingWriter()
    projection = events.RuntimeObservationProjection(
        bundle_id="bundle-1",
        event_sink=events.make_stream_event_sink(writer),
    )

    projection.emit(
        {"phase": "phase-1", "operation": operation, "outcome": outcome, **specific},
        logger=RecordingLogger(),
    )

    assert writer.payloads == [
        {
            "type": "deep_research.progress.v1",
            "phase": "phase-1",
            "operation": operation,
            "outcome": outcome,
            "bundle_id": "bundle-1",
            **specific,
        }
    ]


@pytest.mark.parametrize(
    "fields",
    [
        {"phase": "phase-1", "operation": "node", "outcome": "rejected", "attempt_id": "attempt-1"},
        {"phase": "phase-1", "operation": "gate", "outcome": "started", "attempt_id": "attempt-1"},
        {"phase": "phase-1", "operation": "attempt", "outcome": "started", "attempt_id": "attempt-1"},
        {
            "phase": "phase-1",
            "operation": "retry",
            "outcome": "retrying",
            "work_id": "work-1",
            "attempt_id": "attempt-1",
        },
        {"phase": "phase-1", "operation": "validation", "outcome": "rejected"},
        {"phase": "phase-1", "operation": "trusted_adaptation", "outcome": "completed"},
        {"phase": "runtime", "operation": "bundle_lifecycle", "outcome": "completed"},
        {"phase": "wave0", "operation": "node_agent_call", "outcome": "completed"},
        {"phase": "wave1", "operation": "validation", "outcome": "completed"},
        {"phase": "runtime", "operation": "terminal_category", "outcome": "completed"},
        {
            "phase": "journal",
            "operation": "retention",
            "outcome": "degraded",
            "code": "observation_degraded",
        },
        {
            "phase": "wave0",
            "operation": "live_event",
            "outcome": "degraded",
            "code": "observation_degraded",
        },
    ],
)
def test_runtime_observation_projection_keeps_other_or_incomplete_facts_log_only(
    fields: dict[str, object],
) -> None:
    logger = RecordingLogger()
    writer = RecordingWriter()
    projection = events.RuntimeObservationProjection(
        bundle_id="bundle-1",
        event_sink=events.make_stream_event_sink(writer),
    )

    projection.emit(fields, logger=logger)

    assert len(logger.records) == 1
    assert writer.payloads == []


def test_live_payload_validator_accepts_only_the_exact_schema() -> None:
    payload = {
        "type": "deep_research.progress.v1",
        "phase": "wave1",
        "operation": "retry",
        "outcome": "retrying",
        "bundle_id": "bundle-1",
        "work_id": "work-1",
        "attempt_id": "attempt-1",
        "code": "retrying",
        "count": 2,
        "outer_thread_id": "thread-1",
        "outer_run_id": "run-1",
    }

    assert events.validate_live_payload(payload) == payload

    for invalid in (
        {**payload, "event_type": "deep_research.runtime_observation"},
        {**payload, "detail": "raw model output"},
        {key: value for key, value in payload.items() if key != "type"},
        {**payload, "type": "deep_research.progress.v2"},
        {key: value for key, value in payload.items() if key != "bundle_id"},
        {key: value for key, value in payload.items() if key != "count"},
    ):
        with pytest.raises(events.LiveEventValidationError):
            events.validate_live_payload(invalid)


@pytest.mark.parametrize("forged", ["live_visible", "type", "sink", "writer", "detail", "trace_id"])
def test_runtime_observation_projection_rejects_producer_live_control_or_raw_content(forged: str) -> None:
    logger = RecordingLogger()
    writer = RecordingWriter()
    projection = events.RuntimeObservationProjection(
        bundle_id="bundle-1",
        event_sink=events.make_stream_event_sink(writer),
    )

    projection.emit(
        {
            "phase": "wave0",
            "operation": "node",
            "outcome": "started",
            "attempt_id": "attempt-1",
            forged: "caller-controlled",
        },
        logger=logger,
    )

    assert logger.records == []
    assert writer.payloads == []


def test_runtime_observation_projection_is_log_only_without_a_callable_writer() -> None:
    logger = RecordingLogger()
    projection = events.RuntimeObservationProjection(
        bundle_id="bundle-1",
        event_sink=events.make_stream_event_sink(None),
    )

    projection.emit(
        {
            "phase": "wave0",
            "operation": "node",
            "outcome": "started",
            "attempt_id": "attempt-1",
        },
        logger=logger,
    )

    assert len(logger.records) == 1


def test_logger_failure_does_not_suppress_the_independent_live_attempt() -> None:
    writer = RecordingWriter()
    projection = events.RuntimeObservationProjection(
        bundle_id="bundle-1",
        event_sink=events.make_stream_event_sink(writer),
    )

    projection.emit(
        {
            "phase": "wave0",
            "operation": "node",
            "outcome": "completed",
            "attempt_id": "attempt-1",
        },
        logger=FailingLogger(),
    )

    assert len(writer.payloads) == 1


def test_writer_failure_preserves_result_and_adds_one_bounded_log_only_degradation() -> None:
    logger = RecordingLogger()
    writer = FailingWriter()
    projection = events.RuntimeObservationProjection(
        bundle_id="bundle-1",
        outer_thread_id="thread-1",
        outer_run_id="run-1",
        event_sink=events.make_stream_event_sink(writer),
    )
    journal: list[str] = []
    expected_result = object()

    def producer() -> object:
        journal.append("node_completed")
        projection.emit(
            {
                "phase": "wave0",
                "operation": "node",
                "outcome": "completed",
                "attempt_id": "attempt-1",
            },
            logger=logger,
        )
        return expected_result

    assert producer() is expected_result
    assert journal == ["node_completed"]
    assert writer.calls == 1
    assert len(logger.records) == 2
    assert logger.records[1] == (
        logging.WARNING,
        "deep_research.runtime_observation",
        {
            "event_type": "deep_research.runtime_observation",
            "phase": "wave0",
            "operation": "live_event",
            "outcome": "degraded",
            "bundle_id": "bundle-1",
            "attempt_id": "attempt-1",
            "code": "observation_degraded",
            "outer_thread_id": "thread-1",
            "outer_run_id": "run-1",
        },
    )
    assert "secret writer failure" not in repr(logger.records)


async def test_async_projection_is_awaited_and_attempts_the_writer_once() -> None:
    writer = RecordingWriter()
    projection = events.RuntimeObservationProjection(
        bundle_id="bundle-1",
        event_sink=events.make_stream_event_sink(writer),
    )

    await projection.aemit(
        {
            "phase": "wave0",
            "operation": "node",
            "outcome": "started",
            "attempt_id": "attempt-1",
        },
        logger=RecordingLogger(),
    )

    assert len(writer.payloads) == 1


async def test_async_projection_propagates_cancellation_without_degradation() -> None:
    logger = RecordingLogger()
    writer = CancelledWriter()
    projection = events.RuntimeObservationProjection(
        bundle_id="bundle-1",
        event_sink=events.make_stream_event_sink(writer),
    )

    with pytest.raises(asyncio.CancelledError):
        await projection.aemit(
            {
                "phase": "wave0",
                "operation": "node",
                "outcome": "started",
                "attempt_id": "attempt-1",
            },
            logger=logger,
        )

    assert writer.calls == 1
    assert len(logger.records) == 1


def test_safe_observation_isolates_logger_failure_and_propagates_cancellation() -> None:
    """@impl RTO-001 REJ-005"""

    logger = FailingLogger()
    journal: list[str] = []
    expected_result = object()
    observation = events.SafeObservation(
        phase="work_units",
        operation="attempt_failed",
        outcome=events.ObservationOutcome.RETRYING,
        bundle_id="bundle-1",
        work_id="work-1",
        attempt_id="attempt-1",
        code=events.ObservationCode.RETRYING,
    )

    def existing_producer() -> tuple[object, str]:
        journal.append("attempt_failed")
        events.project_observation(observation, logger=logger)
        return expected_result, "retry"

    result, route = existing_producer()

    assert result is expected_result
    assert route == "retry"
    assert journal == ["attempt_failed"]
    assert logger.calls == 1

    with pytest.raises(asyncio.CancelledError):
        events.project_observation(observation, logger=CancelledLogger())


def _production_sources() -> dict[str, str]:
    source_root = Path(events.__file__).parents[1]
    return {
        path.relative_to(source_root).as_posix(): path.read_text(encoding="utf-8") for path in source_root.rglob("*.py")
    }


def _observation_source_violations(sources: dict[str, str]) -> set[str]:
    violations: set[str] = set()
    retired = ("get_stream_writer", "emit_custom_event", "aemit_custom_event", "ProgressEmitter")
    for path, source in sources.items():
        if any(token in source for token in retired):
            violations.add("retired_transport")
        if "stream_writer" in source and path != "runtime/runtime_adapter.py":
            violations.add("raw_writer_capture")
        if ".writer(" in source and path != "runtime/events.py":
            violations.add("raw_writer_invocation")
        if "deep_research.progress" in source and path not in {
            "runtime/events.py",
            "runtime/gateway_observer.py",
        }:
            violations.add("event_type_boundary")
        if path == "runtime/events.py" and (
            source.count("deep_research.progress") != 1 or 'LIVE_EVENT_TYPE = "deep_research.progress.v1"' not in source
        ):
            violations.add("event_type_boundary")
        if "live_visible" in source and path != "runtime/events.py":
            violations.add("producer_live_control")
        if "live_event_sink" in source and path.startswith(("domain/", "graph/")):
            violations.add("producer_sink_control")
        if "__run_journal" in source or "private_gateway" in source:
            violations.add("private_gateway_access")
        if "live_event_retry" in source or "retry_live_event" in source:
            violations.add("custom_live_retry")
        if "logging.basicConfig(" in source or "TraceContextFilter" in source:
            violations.add("root_logging_control")
    return violations


def test_production_sources_use_only_the_approved_current_writer_boundary() -> None:
    sources = _production_sources()

    assert _observation_source_violations(sources) == set()
    assert "stream_writer" in sources["runtime/runtime_adapter.py"]
    assert ".writer(" in sources["runtime/events.py"]
    assert 'LIVE_EVENT_TYPE = "deep_research.progress.v1"' in sources["runtime/events.py"]


@pytest.mark.parametrize(
    ("path", "planted", "expected"),
    [
        ("runtime/bundle_graph.py", "\nruntime.stream_writer({})\n", "raw_writer_capture"),
        ("runtime/bundle_graph.py", "\nself.writer({})\n", "raw_writer_invocation"),
        ("graph/builder.py", '\nEVENT = "deep_research.progress.v1"\n', "event_type_boundary"),
        ("runtime/events.py", '\nOLD_EVENT = "deep_research.progress.v0"\n', "event_type_boundary"),
        ("graph/builder.py", "\nlive_visible = True\n", "producer_live_control"),
        ("domain/invocation.py", "\nlive_event_sink = object()\n", "producer_sink_control"),
        ("runtime/bundle_graph.py", "\nget_stream_writer()\n", "retired_transport"),
        ("runtime/bundle_graph.py", "\nprivate_gateway.__run_journal\n", "private_gateway_access"),
        ("runtime/bundle_graph.py", "\nlive_event_retry = 1\n", "custom_live_retry"),
        ("runtime/bundle_graph.py", "\nlogging.basicConfig()\n", "root_logging_control"),
    ],
)
def test_observation_source_guard_detects_planted_violations(
    path: str,
    planted: str,
    expected: str,
) -> None:
    sources = _production_sources()
    sources[path] += planted

    assert expected in _observation_source_violations(sources)
    assert _observation_source_violations(_production_sources()) == set()
