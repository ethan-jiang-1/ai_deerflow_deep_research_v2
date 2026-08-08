"""Safe normalized outcomes at a model-invocation boundary.

The phase that invokes a model owns recovery, routing, and terminal behavior.
This module only preserves safe invocation facts before those choices are made.

@impl WFO-001
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Awaitable, Callable, Mapping
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from deerflow_deep_research.domain.context import NodeExecutionResult
from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.domain.run_experience import (
    FailureCertainty,
    LogicalPhaseName,
    NodeProblem,
    ProviderRecoveryProjection,
    RunFailureCode,
    TerminalIncidentProjection,
)
from deerflow_deep_research.domain.work_units import (
    ATTEMPT_ID_RE,
    AttemptRef,
    AttemptTerminalCode,
    TerminalFailureSummary,
    WorkerAttemptFailure,
    WorkerFailureAggregate,
    WorkerFailureCategory,
    aggregate_worker_failure_category,
)


class _FrozenWorkflowOutcome(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class InvocationSuccess(_FrozenWorkflowOutcome):
    """A successful invocation whose result remains available to its phase."""

    kind: Literal["success"] = "success"
    result: NodeExecutionResult


class InvocationFailure(_FrozenWorkflowOutcome):
    """A safe classified invocation failure with no raw result payload."""

    kind: Literal["failure"] = "failure"
    finish_reason: NodeFinishReason
    problem: NodeProblem


type InvocationOutcome = InvocationSuccess | InvocationFailure
type InvocationSource = object


def normalize_invocation_outcome(
    source: InvocationSource,
    *,
    phase: LogicalPhaseName,
) -> InvocationOutcome:
    """Return a bounded result for a phase to handle, preserving cancellation."""
    if isinstance(source, NodeExecutionResult):
        if source.finish_reason is NodeFinishReason.SUCCESS:
            return InvocationSuccess(result=source)
        if source.finish_reason is NodeFinishReason.CANCELLED:
            raise asyncio.CancelledError
        if source.problem is not None:
            return InvocationFailure(finish_reason=source.finish_reason, problem=source.problem)
        return _unknown_failure(finish_reason=source.finish_reason, phase=phase)

    if isinstance(source, asyncio.CancelledError):
        raise source
    if isinstance(source, Exception):
        return _unknown_failure(finish_reason=NodeFinishReason.FAILED, phase=phase)
    if isinstance(source, BaseException):
        raise source
    return _unknown_failure(finish_reason=NodeFinishReason.FAILED, phase=phase)


async def invoke_and_normalize(
    invoke: Callable[[], Awaitable[object]],
    *,
    phase: LogicalPhaseName,
) -> InvocationOutcome:
    """Invoke one phase-owned operation and return its safe bounded outcome."""
    try:
        source = await invoke()
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        source = exc
    return normalize_invocation_outcome(source, phase=phase)


def worker_failure_for_invocation(problem: NodeProblem) -> WorkerAttemptFailure:
    """Map a normalized invocation failure to the controller's closed category.

    Worker phases retain their own retry, aggregate, gate, and terminal decisions.
    This only prevents an already-safe invocation fact from becoming a generic
    exception before it reaches that existing controller.
    """
    if problem.certainty is FailureCertainty.UNKNOWN:
        return WorkerAttemptFailure(WorkerFailureCategory.UNKNOWN)
    if problem.code in {RunFailureCode.TOOL_EXECUTION_FAILED, RunFailureCode.TOOL_UNAVAILABLE}:
        return WorkerAttemptFailure(WorkerFailureCategory.TOOL_EXECUTION)
    if problem.code is RunFailureCode.OUTPUT_STRUCTURED_INVALID:
        return WorkerAttemptFailure(WorkerFailureCategory.STRUCTURED_OUTPUT)
    if problem.code is RunFailureCode.PROVIDER_TIMEOUT:
        return WorkerAttemptFailure(
            WorkerFailureCategory.AGENT_INVOCATION,
            provider_category="provider.timeout",
            provider_observation=problem.provider_observation,
        )
    if problem.code is RunFailureCode.PROVIDER_UNAVAILABLE:
        return WorkerAttemptFailure(
            WorkerFailureCategory.AGENT_INVOCATION,
            provider_category="provider.unavailable",
            provider_observation=problem.provider_observation,
        )
    if problem.code is RunFailureCode.PROVIDER_AUTHENTICATION_FAILED:
        return WorkerAttemptFailure(
            WorkerFailureCategory.AGENT_INVOCATION,
            provider_category="provider.authentication_failed",
            provider_observation=problem.provider_observation,
        )
    return WorkerAttemptFailure(WorkerFailureCategory.AGENT_INVOCATION)


def derive_controller_worker_incident(
    *,
    bundle_id: str | None,
    generation: int,
    phase: LogicalPhaseName,
    attempts_by_id: Mapping[str, Any],
    terminal_failures_by_attempt_id: Mapping[str, Any],
) -> TerminalIncidentProjection | None:
    """Derive a compact terminal projection from controller-owned worker facts.

    The caller still owns the decision to terminally block and the checkpoint
    write. This helper only preserves a provider diagnosis when all relevant
    exhausted attempts agree on its closed category; otherwise it retains the
    existing honest worker aggregate without inferring a provider cause.
    """
    phase_work_ids = {
        match.group("work_id")
        for attempt_id in attempts_by_id
        if isinstance(attempt_id, str)
        and (match := ATTEMPT_ID_RE.fullmatch(attempt_id)) is not None
        and match.group("phase") == phase
    }
    if not phase_work_ids:
        return None

    aggregates = {aggregate_worker_failure_category(attempts_by_id, work_id=work_id) for work_id in phase_work_ids}
    if None in aggregates:
        return None
    aggregate = next(iter(aggregates)) if len(aggregates) == 1 else WorkerFailureAggregate.MIXED
    generic = TerminalIncidentProjection(
        code=RunFailureCode.RESEARCH_BLOCKED,
        phase=phase,
        certainty=FailureCertainty.DIRECT,
        worker_failure_category=aggregate.value,
    )
    if aggregate is not WorkerFailureAggregate.AGENT_INVOCATION:
        return generic

    failure_attempt_ids: set[str] = set()
    for attempt_id, raw_attempt in attempts_by_id.items():
        if not isinstance(attempt_id, str):
            continue
        match = ATTEMPT_ID_RE.fullmatch(attempt_id)
        if match is None or match.group("phase") != phase:
            continue
        attempt = AttemptRef.model_validate(raw_attempt)
        if (
            attempt.terminal_code is AttemptTerminalCode.WORKER_FAILED
            and attempt.failure_category is WorkerFailureCategory.AGENT_INVOCATION
        ):
            failure_attempt_ids.add(attempt_id)

    summaries: dict[str, TerminalFailureSummary] = {}
    for attempt_id, raw_summary in terminal_failures_by_attempt_id.items():
        if not isinstance(attempt_id, str):
            continue
        match = ATTEMPT_ID_RE.fullmatch(attempt_id)
        if match is None or match.group("phase") != phase:
            continue
        summaries[attempt_id] = TerminalFailureSummary.model_validate(raw_summary)
    if not failure_attempt_ids or set(summaries) != failure_attempt_ids:
        return generic
    if any(
        summary.failure_category is not WorkerFailureCategory.AGENT_INVOCATION or summary.provider_category is None
        for summary in summaries.values()
    ):
        return generic

    provider_categories = {summary.provider_category for summary in summaries.values()}
    if len(provider_categories) != 1:
        return generic
    provider_category = next(iter(provider_categories))
    code_by_category = {
        "provider.timeout": RunFailureCode.PROVIDER_TIMEOUT,
        "provider.unavailable": RunFailureCode.PROVIDER_UNAVAILABLE,
        "provider.authentication_failed": RunFailureCode.PROVIDER_AUTHENTICATION_FAILED,
    }
    code = code_by_category[provider_category]
    latest_attempt_id = max(summaries)
    observation = summaries[latest_attempt_id].provider_observation
    if observation is not None and bundle_id is None:
        return generic
    problem = NodeProblem(
        code=code,
        phase=phase,
        certainty=FailureCertainty.DIRECT,
        provider_observation=observation,
    )
    diagnostic_ref = (
        derive_provider_diagnostic_reference(
            bundle_id=bundle_id,
            generation=generation,
            node_attempt=latest_attempt_id,
            problem=problem,
        )
        if observation is not None
        else None
    )
    return TerminalIncidentProjection(
        code=code,
        phase=phase,
        certainty=FailureCertainty.DIRECT,
        diagnostic_ref=diagnostic_ref,
        worker_failure_category=aggregate.value,
        provider_observation=observation,
    )


def derive_provider_diagnostic_reference(
    *,
    bundle_id: str,
    generation: int,
    node_attempt: str,
    problem: NodeProblem,
    recovery: ProviderRecoveryProjection | None = None,
) -> str:
    """Derive a terminal-only diagnostic reference from closed safe facts.

    This intentionally accepts no result body, exception text, prompt, provider URL,
    or service label. Phase code decides whether recovery happened; this function
    merely gives that recorded fact a stable safe reference for terminal projection.
    """
    if problem.provider_observation is None and recovery is None:
        raise ValueError("provider_diagnostic_reference_requires_safe_observation")
    payload = {
        "version": 1,
        "bundle_id": bundle_id,
        "generation": generation,
        "node_attempt": node_attempt,
        "final_category": problem.code.value,
        "final_response": _observation_identity(problem.provider_observation),
        "recovery": (
            {
                "trigger_category": recovery.trigger_category,
                "trigger_ordinal": recovery.trigger_invocation_ordinal,
                "model_attempts": recovery.model_attempts,
                "automatic_retries": recovery.automatic_retries,
                "disposition": recovery.disposition,
                "trigger_response": _observation_identity(recovery.trigger_observation),
            }
            if recovery is not None
            else None
        ),
    }
    final_timeout_origin = _timeout_origin(problem.provider_observation)
    if final_timeout_origin is not None:
        payload["final_timeout_origin"] = final_timeout_origin
    if recovery is not None:
        trigger_timeout_origin = _timeout_origin(recovery.trigger_observation)
        if trigger_timeout_origin is not None:
            payload["recovery"]["trigger_timeout_origin"] = trigger_timeout_origin
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "diag_" + hashlib.sha256(encoded).hexdigest()[:24]


def _unknown_failure(*, finish_reason: NodeFinishReason, phase: LogicalPhaseName) -> InvocationFailure:
    return InvocationFailure(
        finish_reason=finish_reason,
        problem=NodeProblem(
            code=RunFailureCode.INTERNAL_UNEXPECTED,
            phase=phase,
            certainty=FailureCertainty.UNKNOWN,
        ),
    )


def _observation_identity(observation: object) -> tuple[str | None, int | None]:
    response_kind = getattr(observation, "response_kind", None)
    http_status = getattr(observation, "http_status", None)
    return (
        response_kind if isinstance(response_kind, str) else None,
        http_status if isinstance(http_status, int) else None,
    )


def _timeout_origin(observation: object) -> str | None:
    origin = getattr(observation, "timeout_origin", None)
    return origin if origin in {"bridge_wall_time_budget", "provider_sdk_timeout"} else None


__all__ = [
    "InvocationFailure",
    "InvocationOutcome",
    "InvocationSource",
    "InvocationSuccess",
    "derive_provider_diagnostic_reference",
    "derive_controller_worker_incident",
    "invoke_and_normalize",
    "normalize_invocation_outcome",
    "worker_failure_for_invocation",
]
