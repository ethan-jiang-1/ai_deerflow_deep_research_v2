"""Real topic planning node.

@impl TOP-001
@impl TOP-002
@impl TOP-003
@impl TOP-004
@impl TOP-005
@impl WFO-001
@impl TOP-009
"""

from __future__ import annotations

import asyncio
import secrets
from collections.abc import Mapping
from typing import Any

from deerflow_deep_research.domain.context import NodeExecutionResult
from deerflow_deep_research.domain.lifecycle import LifecycleStatus, TerminalReason
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.run_experience import (
    FailureCertainty,
    NodeProblem,
    ProviderRecoveryProjection,
    RunFailureCode,
    TerminalIncidentProjection,
)
from deerflow_deep_research.domain.run_observation import RunEventCategory
from deerflow_deep_research.domain.state import PhaseStatus, node_state_update
from deerflow_deep_research.domain.topics import (
    MaterializedTopics,
    TopicPlan,
    materialize_topic_plan,
    materialized_topics_state,
    parse_plan_output,
)
from deerflow_deep_research.domain.workflow_outcomes import (
    InvocationFailure,
    derive_provider_diagnostic_reference,
    invoke_and_normalize,
)
from deerflow_deep_research.graph.nodes.topic_planning.prompts import (
    PlannerInputs,
    build_planner_prompt,
    planner_assignment_from_state,
)

RETRY_BACKOFF_MILLISECONDS = 1_000
RETRY_BACKOFF_SECONDS = RETRY_BACKOFF_MILLISECONDS / 1_000
_TOPIC_PLAN_PARSER_CODES = frozenset(
    {
        "topic_plan_empty",
        "topic_plan_json_invalid",
        "topic_plan_extra_fields",
        "topic_plan_invalid",
    }
)
_TOPIC_MATERIALIZATION_CODES = frozenset(
    {
        "topic_count_profile_mismatch",
        "topic_coverage_empty",
        "topic_duplicate_slug",
        "topic_overlap",
        "topic_coverage_uncovered",
        "topic_materialization_invalid",
    }
)


def _exhausted_update(
    problem: NodeProblem | None,
    *,
    state: Mapping[str, Any],
    dependencies: NodeBuildDependencies,
    recovery: ProviderRecoveryProjection | None,
) -> dict[str, object]:
    incident: dict[str, Any] = {}
    if problem is not None:
        diagnostic_ref = problem.diagnostic_ref
        if diagnostic_ref is None and (recovery is not None or problem.provider_observation is not None):
            diagnostic_ref = derive_provider_diagnostic_reference(
                bundle_id=str(state["bundle_id"]),
                generation=int(state.get("generation", 0)),
                node_attempt=dependencies.agent_context.attempt_id,
                problem=problem,
                recovery=recovery,
            )
        incident["latest_incident"] = TerminalIncidentProjection(
            code=problem.code,
            phase=problem.phase,
            certainty=problem.certainty,
            diagnostic_ref=diagnostic_ref,
            provider_recovery=recovery,
            provider_observation=problem.provider_observation,
        ).model_dump(mode="json", exclude_none=True)
    return node_state_update(
        "topic_planning",
        route="exhausted",
        terminal_status=LifecycleStatus.BLOCKED.value,
        phase_status=PhaseStatus.TERMINAL.value,
        terminal_reason=TerminalReason.GATE_BLOCKED.value,
        **incident,
    )


def _retry_eligible(problem: NodeProblem | None) -> bool:
    return (
        problem is not None
        and problem.code in {RunFailureCode.PROVIDER_TIMEOUT, RunFailureCode.PROVIDER_UNAVAILABLE}
        and problem.provider_observation is not None
    )


def _provider_category(problem: NodeProblem | None) -> str | None:
    if problem is None or problem.code not in {
        RunFailureCode.PROVIDER_TIMEOUT,
        RunFailureCode.PROVIDER_UNAVAILABLE,
        RunFailureCode.PROVIDER_AUTHENTICATION_FAILED,
    }:
        return None
    return problem.code.value


def _canonical_parser_validation_code(error: TypeError | ValueError) -> str:
    """Collapse parser detail to the closed Journal vocabulary."""

    code = str(error)
    return code if code in _TOPIC_PLAN_PARSER_CODES else "topic_plan_invalid"


def _canonical_materialization_validation_code(error: TypeError | ValueError) -> str:
    """Retain only a materializer's closed code, never dynamic validation detail."""

    code = str(error)
    if code.startswith("topic_coverage_uncovered:"):
        return "topic_coverage_uncovered"
    return code if code in _TOPIC_MATERIALIZATION_CODES else "topic_materialization_invalid"


def _recovery_projection(
    *,
    trigger: NodeProblem,
    trigger_invocation_ordinal: int,
    automatic_retries: int,
    disposition: str,
) -> ProviderRecoveryProjection:
    if trigger.provider_observation is None:
        raise ValueError("retry_trigger_requires_provider_observation")
    return ProviderRecoveryProjection(
        trigger_category=trigger.code.value,
        trigger_observation=trigger.provider_observation,
        trigger_invocation_ordinal=trigger_invocation_ordinal,
        model_attempts=2,
        automatic_retries=automatic_retries,
        disposition=disposition,
    )


async def _record_recovery_observation(
    dependencies: NodeBuildDependencies,
    *,
    category: RunEventCategory,
    recovery_correlation_id: str,
    attempt_id: str | None = None,
    provider_category: str | None = None,
    retry_ordinal: int | None = None,
    backoff_milliseconds: int | None = None,
    recovery_event_disposition: str | None = None,
) -> None:
    recorder = dependencies.event_recorder
    if recorder is None:
        return
    try:
        await recorder.record(
            category=category,
            phase="topic_planning",
            attempt_id=attempt_id,
            recovery_correlation_id=recovery_correlation_id,
            provider_category=provider_category,
            retry_ordinal=retry_ordinal,
            backoff_milliseconds=backoff_milliseconds,
            recovery_event_disposition=recovery_event_disposition,
        )
    except Exception:
        return


async def _record_validation_observation(
    dependencies: NodeBuildDependencies,
    *,
    stage: str,
    codes: tuple[str, ...],
) -> None:
    """Publish parser/materializer evidence without affecting planner control flow."""

    recorder = dependencies.event_recorder
    if recorder is None:
        return
    try:
        await recorder.record(
            category=RunEventCategory.VALIDATION,
            phase="topic_planning",
            validation_stage=stage,
            validation_codes=codes,
        )
    except Exception:
        return


async def _invoke_plan(
    dependencies: NodeBuildDependencies,
    *,
    request: object,
) -> tuple[NodeExecutionResult | None, NodeProblem | None]:
    outcome = await invoke_and_normalize(
        lambda: dependencies.capabilities.run_agent(
            context=dependencies.agent_context,
            request=request,
        ),
        phase="topic_planning",
    )
    if isinstance(outcome, InvocationFailure):
        return None, outcome.problem
    return outcome.result, None


async def _materialize_with_observation(
    result: NodeExecutionResult,
    inputs: PlannerInputs,
    *,
    dependencies: NodeBuildDependencies,
    stage: str,
) -> MaterializedTopics:
    """Validate one candidate and retain only its closed observational outcome."""

    try:
        plan: TopicPlan = parse_plan_output(result.summary)
    except (TypeError, ValueError) as error:
        await _record_validation_observation(
            dependencies,
            stage=stage,
            codes=(_canonical_parser_validation_code(error),),
        )
        raise
    try:
        if inputs.single_topic and len(plan.topics) != 1:
            raise ValueError("topic_count_profile_mismatch")
        materialized = materialize_topic_plan(plan, inputs.coverage_questions)
    except (TypeError, ValueError) as error:
        await _record_validation_observation(
            dependencies,
            stage=stage,
            codes=(_canonical_materialization_validation_code(error),),
        )
        raise
    await _record_validation_observation(dependencies, stage=stage, codes=())
    return materialized


async def _generate_plan(
    inputs: PlannerInputs,
    *,
    dependencies: NodeBuildDependencies,
) -> tuple[MaterializedTopics | None, NodeProblem | None, ProviderRecoveryProjection | None]:
    """Apply topic planning's bounded provider-recovery and output-repair table."""
    initial_request = build_planner_prompt(inputs)
    initial_result, initial_problem = await _invoke_plan(dependencies, request=initial_request)
    if initial_problem is not None:
        if not _retry_eligible(initial_problem):
            return None, initial_problem, None
        recovery_correlation_id = "rec_" + secrets.token_urlsafe(12)
        await _record_recovery_observation(
            dependencies,
            category=RunEventCategory.ATTEMPT,
            recovery_correlation_id=recovery_correlation_id,
            attempt_id="inv_" + secrets.token_urlsafe(12),
            provider_category=_provider_category(initial_problem),
        )
        await _record_recovery_observation(
            dependencies,
            category=RunEventCategory.RETRY,
            recovery_correlation_id=recovery_correlation_id,
            retry_ordinal=1,
            backoff_milliseconds=RETRY_BACKOFF_MILLISECONDS,
            recovery_event_disposition="scheduled",
        )
        await asyncio.sleep(RETRY_BACKOFF_SECONDS)
        retry_result, retry_problem = await _invoke_plan(dependencies, request=initial_request)
        await _record_recovery_observation(
            dependencies,
            category=RunEventCategory.ATTEMPT,
            recovery_correlation_id=recovery_correlation_id,
            attempt_id="inv_" + secrets.token_urlsafe(12),
            provider_category=_provider_category(retry_problem),
        )
        if retry_problem is not None:
            if _retry_eligible(retry_problem):
                await _record_recovery_observation(
                    dependencies,
                    category=RunEventCategory.EXHAUSTION,
                    recovery_correlation_id=recovery_correlation_id,
                    provider_category=_provider_category(retry_problem),
                    retry_ordinal=1,
                    recovery_event_disposition="exhausted",
                )
                return (
                    None,
                    retry_problem,
                    _recovery_projection(
                        trigger=initial_problem,
                        trigger_invocation_ordinal=1,
                        automatic_retries=1,
                        disposition="exhausted",
                    ),
                )
            return (
                None,
                retry_problem,
                _recovery_projection(
                    trigger=initial_problem,
                    trigger_invocation_ordinal=1,
                    automatic_retries=1,
                    disposition="retry_followed_by_terminal_failure",
                ),
            )
        assert retry_result is not None
        try:
            return (
                await _materialize_with_observation(
                    retry_result,
                    inputs,
                    dependencies=dependencies,
                    stage="initial",
                ),
                None,
                None,
            )
        except (TypeError, ValueError):
            return (
                None,
                NodeProblem(
                    code=RunFailureCode.OUTPUT_STRUCTURED_INVALID,
                    phase="topic_planning",
                    certainty=FailureCertainty.DIRECT,
                ),
                _recovery_projection(
                    trigger=initial_problem,
                    trigger_invocation_ordinal=1,
                    automatic_retries=1,
                    disposition="retry_followed_by_terminal_failure",
                ),
            )

    assert initial_result is not None
    try:
        return (
            await _materialize_with_observation(
                initial_result,
                inputs,
                dependencies=dependencies,
                stage="initial",
            ),
            None,
            None,
        )
    except (TypeError, ValueError) as exc:
        repair_request = build_planner_prompt(
            inputs,
            repair_error=str(exc) or type(exc).__name__,
            invalid_draft=initial_result.summary,
        )
        repair_result, repair_problem = await _invoke_plan(dependencies, request=repair_request)
        if repair_problem is not None:
            if _retry_eligible(repair_problem):
                recovery_correlation_id = "rec_" + secrets.token_urlsafe(12)
                await _record_recovery_observation(
                    dependencies,
                    category=RunEventCategory.ATTEMPT,
                    recovery_correlation_id=recovery_correlation_id,
                    attempt_id="inv_" + secrets.token_urlsafe(12),
                    provider_category=_provider_category(repair_problem),
                )
                return (
                    None,
                    repair_problem,
                    _recovery_projection(
                        trigger=repair_problem,
                        trigger_invocation_ordinal=2,
                        automatic_retries=0,
                        disposition="retry_not_started_budget_consumed",
                    ),
                )
            return None, repair_problem, None
        assert repair_result is not None
        try:
            return (
                await _materialize_with_observation(
                    repair_result,
                    inputs,
                    dependencies=dependencies,
                    stage="repair",
                ),
                None,
                None,
            )
        except (TypeError, ValueError):
            return (
                None,
                NodeProblem(
                    code=RunFailureCode.OUTPUT_STRUCTURED_INVALID,
                    phase="topic_planning",
                    certainty=FailureCertainty.DIRECT,
                ),
                None,
            )


def build_real(dependencies: NodeBuildDependencies):
    if dependencies.selected_bundle is None:
        raise ValueError("selected_bundle_context_missing")

    async def run(state):
        try:
            inputs = await planner_assignment_from_state(
                state,
                request_bundle=dependencies.request_bundle,
            )
        except (FileNotFoundError, OSError, RuntimeError, TypeError, ValueError):
            return _exhausted_update(
                None,
                state=state,
                dependencies=dependencies,
                recovery=None,
            )
        materialized, problem, recovery = await _generate_plan(
            inputs,
            dependencies=dependencies,
        )
        if materialized is None:
            return _exhausted_update(
                problem,
                state=state,
                dependencies=dependencies,
                recovery=recovery,
            )
        return node_state_update("topic_planning", route="next", **materialized_topics_state(materialized))

    return run


__all__ = ["build_real"]
