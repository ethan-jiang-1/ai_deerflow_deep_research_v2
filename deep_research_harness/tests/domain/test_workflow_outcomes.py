"""@impl WFO-001 — workflow invocation outcome contract tests."""

from __future__ import annotations

import asyncio

import pytest

from deerflow_deep_research.domain.context import NodeExecutionResult
from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.domain.run_experience import (
    FailureCertainty,
    NodeProblem,
    ProviderObservation,
    ProviderRecoveryProjection,
    RunFailureCode,
)
from deerflow_deep_research.domain.work_units import WorkerFailureCategory
from deerflow_deep_research.domain.workflow_outcomes import (
    InvocationFailure,
    InvocationSuccess,
    derive_controller_worker_incident,
    derive_provider_diagnostic_reference,
    invoke_and_normalize,
    normalize_invocation_outcome,
    worker_failure_for_invocation,
)

_SENTINEL = "raw provider body and exception text must not survive"
_RESEARCH_ID = "r_" + "A" * 43


def test_known_node_problem_is_preserved_without_exposing_result_payload() -> None:
    problem = NodeProblem(
        code=RunFailureCode.PROVIDER_TIMEOUT,
        phase="topic_planning",
        certainty=FailureCertainty.DIRECT,
        diagnostic_ref="diag_abcdefgh",
        provider_observation=ProviderObservation(
            configured_service_label="primary-model",
            configured_endpoint_authority="https://api.example.test",
            response_kind="no_response",
        ),
    )
    source = NodeExecutionResult(
        finish_reason=NodeFinishReason.FAILED,
        summary=_SENTINEL,
        error_code="provider_timeout",
        problem=problem,
    )

    outcome = normalize_invocation_outcome(source, phase="topic_planning")

    assert isinstance(outcome, InvocationFailure)
    assert outcome.finish_reason is NodeFinishReason.FAILED
    assert outcome.problem == problem
    assert outcome.problem.code is RunFailureCode.PROVIDER_TIMEOUT
    assert outcome.problem.phase == "topic_planning"
    assert outcome.problem.certainty is FailureCertainty.DIRECT
    assert outcome.problem.provider_observation == problem.provider_observation
    assert _SENTINEL not in str(outcome.model_dump(mode="json"))


def test_non_success_without_safe_problem_becomes_redacted_unknown() -> None:
    source = NodeExecutionResult(
        finish_reason=NodeFinishReason.FAILED,
        summary=_SENTINEL,
        error_code="agent_invocation_failed",
    )

    outcome = normalize_invocation_outcome(source, phase="wave1")

    assert isinstance(outcome, InvocationFailure)
    assert outcome.finish_reason is NodeFinishReason.FAILED
    assert outcome.problem == NodeProblem(
        code=RunFailureCode.INTERNAL_UNEXPECTED,
        phase="wave1",
        certainty=FailureCertainty.UNKNOWN,
    )
    assert _SENTINEL not in str(outcome.model_dump(mode="json"))


def test_success_remains_available_only_to_the_success_variant() -> None:
    source = NodeExecutionResult(finish_reason=NodeFinishReason.SUCCESS, summary="validated output")

    outcome = normalize_invocation_outcome(source, phase="wave0")

    assert isinstance(outcome, InvocationSuccess)
    assert outcome.result == source


def test_cancellation_is_propagated_without_becoming_a_failure() -> None:
    cancellation = asyncio.CancelledError("caller cancellation")

    with pytest.raises(asyncio.CancelledError) as raised:
        normalize_invocation_outcome(cancellation, phase="topic_planning")

    assert raised.value is cancellation


def test_cancelled_result_is_propagated_without_a_durable_outcome() -> None:
    source = NodeExecutionResult(finish_reason=NodeFinishReason.CANCELLED)

    with pytest.raises(asyncio.CancelledError):
        normalize_invocation_outcome(source, phase="topic_planning")


async def test_invoker_normalizes_local_exception_without_retaining_its_text() -> None:
    async def invoke() -> object:
        raise RuntimeError(_SENTINEL)

    outcome = await invoke_and_normalize(invoke, phase="wave2_synthesis")

    assert isinstance(outcome, InvocationFailure)
    assert outcome.problem == NodeProblem(
        code=RunFailureCode.INTERNAL_UNEXPECTED,
        phase="wave2_synthesis",
        certainty=FailureCertainty.UNKNOWN,
    )
    assert _SENTINEL not in str(outcome.model_dump(mode="json"))


async def test_invoker_propagates_cancellation_without_a_durable_outcome() -> None:
    cancellation = asyncio.CancelledError("caller cancellation")

    async def invoke() -> object:
        raise cancellation

    with pytest.raises(asyncio.CancelledError) as raised:
        await invoke_and_normalize(invoke, phase="wave0")

    assert raised.value is cancellation


@pytest.mark.parametrize(
    ("problem", "category", "provider_category"),
    [
        pytest.param(
            NodeProblem(
                code=RunFailureCode.PROVIDER_TIMEOUT,
                phase="wave0",
                certainty=FailureCertainty.DIRECT,
                provider_observation=ProviderObservation(
                    configured_service_label="wave0-worker-model",
                    response_kind="no_response",
                ),
            ),
            WorkerFailureCategory.AGENT_INVOCATION,
            "provider.timeout",
            id="provider-timeout",
        ),
        pytest.param(
            NodeProblem(
                code=RunFailureCode.TOOL_EXECUTION_FAILED,
                phase="wave1",
                certainty=FailureCertainty.DIRECT,
            ),
            WorkerFailureCategory.TOOL_EXECUTION,
            None,
            id="tool",
        ),
        pytest.param(
            NodeProblem(
                code=RunFailureCode.OUTPUT_STRUCTURED_INVALID,
                phase="targeted_evidence",
                certainty=FailureCertainty.DIRECT,
            ),
            WorkerFailureCategory.STRUCTURED_OUTPUT,
            None,
            id="structured-output",
        ),
        pytest.param(
            NodeProblem(
                code=RunFailureCode.INTERNAL_UNEXPECTED,
                phase="wave0",
                certainty=FailureCertainty.UNKNOWN,
            ),
            WorkerFailureCategory.UNKNOWN,
            None,
            id="unknown",
        ),
    ],
)
def test_worker_failure_mapping_preserves_only_closed_invocation_facts(
    problem: NodeProblem,
    category: WorkerFailureCategory,
    provider_category: str | None,
) -> None:
    failure = worker_failure_for_invocation(problem)

    assert failure.category is category
    assert failure.provider_category == provider_category
    assert failure.provider_observation == problem.provider_observation
    assert _SENTINEL not in str(failure)


def _provider_problem(*, timeout_origin: str | None = None, service_label: str | None = None) -> NodeProblem:
    return NodeProblem(
        code=RunFailureCode.PROVIDER_TIMEOUT,
        phase="hitl1",
        certainty=FailureCertainty.DIRECT,
        provider_observation=ProviderObservation(
            configured_service_label=service_label,
            response_kind="no_response",
            timeout_origin=timeout_origin,  # type: ignore[arg-type]
        ),
    )


def _timeout_recovery(*, timeout_origin: str | None = None) -> ProviderRecoveryProjection:
    return ProviderRecoveryProjection(
        trigger_category="provider.timeout",
        trigger_observation=ProviderObservation(
            response_kind="no_response",
            timeout_origin=timeout_origin,  # type: ignore[arg-type]
        ),
        trigger_invocation_ordinal=1,
        model_attempts=2,
        automatic_retries=1,
        disposition="exhausted",
    )


def test_provider_diagnostic_reference_keeps_v1_identity_without_origins_and_separates_roles() -> None:
    base = derive_provider_diagnostic_reference(
        bundle_id=_RESEARCH_ID,
        generation=0,
        node_attempt="g0-hitl1-a1",
        problem=_provider_problem(service_label="configured-service-a"),
        recovery=_timeout_recovery(),
    )
    same_safe_identity = derive_provider_diagnostic_reference(
        bundle_id=_RESEARCH_ID,
        generation=0,
        node_attempt="g0-hitl1-a1",
        problem=_provider_problem(service_label="configured-service-b"),
        recovery=_timeout_recovery(),
    )
    final_origin = derive_provider_diagnostic_reference(
        bundle_id=_RESEARCH_ID,
        generation=0,
        node_attempt="g0-hitl1-a1",
        problem=_provider_problem(timeout_origin="provider_sdk_timeout"),
        recovery=_timeout_recovery(),
    )
    trigger_origin = derive_provider_diagnostic_reference(
        bundle_id=_RESEARCH_ID,
        generation=0,
        node_attempt="g0-hitl1-a1",
        problem=_provider_problem(),
        recovery=_timeout_recovery(timeout_origin="bridge_wall_time_budget"),
    )

    assert base == "diag_05439d724de57c7f710119bd"
    assert same_safe_identity == base
    assert final_origin != base
    assert trigger_origin != base
    assert final_origin != trigger_origin
    assert _SENTINEL not in "|".join((base, final_origin, trigger_origin))


def _controller_timeout_incident(*, timeout_origin: str | None = None):
    attempt_id = "g0_wave0_w0000_a00"
    observation = {
        "configured_service_label": "wave0-worker-model",
        "response_kind": "no_response",
        "http_status": None,
        **({"timeout_origin": timeout_origin} if timeout_origin is not None else {}),
    }
    return derive_controller_worker_incident(
        bundle_id=_RESEARCH_ID,
        generation=0,
        phase="wave0",
        attempts_by_id={
            attempt_id: {
                "created_at": "2026-07-14T00:00:00Z",
                "started_at": "2026-07-14T00:00:00Z",
                "terminal_at": "2026-07-14T00:00:01Z",
                "terminal_code": "worker_failed",
                "failure_category": "agent_invocation",
                "provider_category": "provider.timeout",
                "provider_observation": observation,
            }
        },
        terminal_failures_by_attempt_id={
            attempt_id: {
                "failure_code": "work_failed",
                "detail_hash": "h_" + "A" * 43,
                "failure_category": "agent_invocation",
                "provider_category": "provider.timeout",
                "provider_observation": observation,
            }
        },
    )


def test_controller_provider_diagnostic_reference_uses_the_shared_timeout_origin_identity() -> None:
    legacy = _controller_timeout_incident()
    observed = _controller_timeout_incident(timeout_origin="bridge_wall_time_budget")

    assert legacy is not None
    assert observed is not None
    assert legacy.diagnostic_ref != observed.diagnostic_ref
    assert observed.provider_observation is not None
    assert observed.provider_observation.timeout_origin == "bridge_wall_time_budget"
