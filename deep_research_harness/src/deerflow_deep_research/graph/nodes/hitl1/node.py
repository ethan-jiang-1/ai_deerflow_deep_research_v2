"""Real HITL1 structured-profile node.

@impl HIN-001
@impl HIN-002
@impl HIN-003
@impl HIN-004
@impl HIN-005
@impl WFO-001
"""

from __future__ import annotations

import asyncio
import secrets
from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from langgraph.types import interrupt

from deerflow_deep_research.domain.context import NodeExecutionResult
from deerflow_deep_research.domain.human_interaction import (
    InteractionFeedback,
    InteractionFeedbackKind,
    InteractionProjection,
    InteractionSubject,
    ProposalValues,
    SemanticCandidate,
    build_interaction_projection,
)
from deerflow_deep_research.domain.lifecycle import (
    AcceptedHumanResponse,
    HumanInputMode,
    HumanInputOption,
    HumanInputRequest,
    InternalCancelDecision,
    LifecycleStatus,
    LogicalPhase,
    PendingResearchInterrupt,
    ResponseKind,
    SupportedLanguageOption,
    TerminalReason,
    make_hitl_request_id,
)
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.profile import (
    PartialResearchProfile,
    RequestBundleStoreProtocol,
    StructuredBrief,
    SupportedLanguage,
    derive_comparison_intake_seed,
    finalize_profile,
    merge_profile_progress,
    missing_dimensions,
    normalize_clear_confirmation,
    parse_profile_input,
    profile_state_fields,
)
from deerflow_deep_research.domain.research_confirmation import (
    AcceptedResearchFacts,
    DirectConfirmation,
    OutstandingResearchDecision,
    SemanticInterpretation,
    admit_research_confirmation,
)
from deerflow_deep_research.domain.run_experience import (
    FailureCertainty,
    NodeProblem,
    ProviderRecoveryProjection,
    RunFailureCode,
    TerminalIncidentProjection,
)
from deerflow_deep_research.domain.run_observation import RunEventCategory
from deerflow_deep_research.domain.state import BundleLocalState, PhaseStatus, node_state_update
from deerflow_deep_research.domain.workflow_outcomes import (
    InvocationFailure,
    derive_provider_diagnostic_reference,
    invoke_and_normalize,
)
from deerflow_deep_research.graph.nodes.hitl1.prompts import (
    build_brief_prompt,
    build_followup_context,
    build_language_choice_context,
    build_proposal_context,
    build_semantic_intake_prompt,
    parse_brief_output,
    parse_semantic_candidate_output,
)

MAX_HITL1_ANSWER_ROUNDS = 3
MAX_SEMANTIC_INTAKE_CALLS = 3
MAX_SEMANTIC_TRANSIENT_RETRIES = 2
RETRY_BACKOFF_MILLISECONDS = 1_000
RETRY_BACKOFF_SECONDS = RETRY_BACKOFF_MILLISECONDS / 1_000

_SEMANTIC_UNAVAILABLE_MESSAGE = (
    "I could not interpret that reply right now. You can try again or start with the current proposal."
)
_SEMANTIC_INVALID_MESSAGE = (
    "I could not interpret that reply clearly. Please confirm, revise the proposal, or ask a focused question."
)


def _profile_progress_payload(profile: PartialResearchProfile) -> dict[str, Any]:
    payload = profile.model_dump(mode="json", exclude_none=True)
    if profile.schema_version == 1:
        payload.pop("schema_version", None)
        for field in ("comparison_required", "comparison_subjects", "request_language", "output_language"):
            payload.pop(field, None)
    return payload


_BUNDLE_HITL_FIELDS = (
    "generation",
    "start_message_id",
    "pending_request_id",
    "pending_cursor",
    "pending_request_mode",
    "consumed_request_ids",
    "consumed_message_ids",
    "hitl1_visit_count",
    "profile_ref",
    "research_depth",
    "target_audience",
    "output_format",
    "cost_tolerance",
    "time_budget",
    "must_answer_questions",
    "comparison_required",
    "comparison_subjects",
    "request_language",
    "output_language",
    "degraded_profile",
    "pending_profile",
    "profile_followup_round",
    "proposed_profile",
    "profile_rejection_round",
    "profile_feedback_cursor_message_id",
    "proposal_version",
    "interaction_feedback",
)


def _state_from_bundle(state: Mapping[str, Any], bundle_state: BundleLocalState) -> dict[str, Any]:
    """Overlay durable HITL facts from the selected Bundle onto one graph invocation."""

    projected = dict(state)
    for field in _BUNDLE_HITL_FIELDS:
        value = getattr(bundle_state, field)
        if field != "start_message_id" or value is not None:
            projected[field] = value
    projected["bundle_id"] = bundle_state.bundle_id.value
    return projected


def _cursor(state: Mapping[str, Any]) -> str:
    return (
        state.get("profile_feedback_cursor_message_id")
        or (state.get("consumed_message_ids") or (state["start_message_id"],))[-1]
    )


def _request_id(bundle_state: BundleLocalState) -> tuple[str, int]:
    """Reuse the one pending id or allocate the next Bundle-local HITL1 visit."""

    if bundle_state.pending_request_id is not None:
        return bundle_state.pending_request_id, bundle_state.hitl1_visit_count
    ordinal = bundle_state.hitl1_visit_count + 1
    request_id = make_hitl_request_id(
        bundle_id=bundle_state.bundle_id.value,
        phase="hitl1",
        generation=bundle_state.generation,
        ordinal=ordinal,
    )
    return request_id, ordinal


async def _write_bundle_state(
    request_store: RequestBundleStoreProtocol,
    bundle_state: BundleLocalState,
    **changes: Any,
) -> BundleLocalState:
    """Commit one HITL1 transition through the preselected Bundle writer."""

    return await request_store.write_bundle_state(
        replace(bundle_state, **changes),
        expected_revision=bundle_state.revision,
    )


def _consume_response_changes(bundle_state: BundleLocalState, response: AcceptedHumanResponse) -> dict[str, Any]:
    """Return the sole correlated-response transition for one pending Bundle request."""

    if bundle_state.pending_request_id != response.request_id:
        raise ValueError("response_mismatch")
    return {
        "pending_request_id": None,
        "pending_cursor": None,
        "pending_request_mode": None,
        "waiting_for": None,
        "phase_status": PhaseStatus.IN_PROGRESS,
        "consumed_request_ids": (*bundle_state.consumed_request_ids, response.request_id)[-32:],
        "consumed_message_ids": (*bundle_state.consumed_message_ids, response.message_id)[-32:],
    }


def _graph_consumed_fields(bundle_state: BundleLocalState) -> dict[str, tuple[str, ...]]:
    return {
        "consumed_request_ids": bundle_state.consumed_request_ids,
        "consumed_message_ids": bundle_state.consumed_message_ids,
    }


async def _persist_terminal(
    request_store: RequestBundleStoreProtocol,
    bundle_state: BundleLocalState,
    *,
    status: LifecycleStatus,
) -> BundleLocalState:
    return await _write_bundle_state(
        request_store,
        bundle_state,
        phase=LogicalPhase.HITL1,
        phase_status=PhaseStatus.TERMINAL,
        terminal_status=status,
        waiting_for=None,
        pending_request_id=None,
        pending_cursor=None,
        pending_request_mode=None,
        pending_profile=None,
        profile_followup_round=0,
        proposed_profile=None,
        profile_rejection_round=0,
        profile_feedback_cursor_message_id="",
        proposal_version=0,
        interaction_feedback=None,
    )


def _exhausted_update(
    problem: NodeProblem | None = None,
    *,
    state: Mapping[str, Any] | None = None,
    dependencies: NodeBuildDependencies | None = None,
    recovery: ProviderRecoveryProjection | None = None,
) -> dict[str, Any]:
    incident: dict[str, Any] = {}
    if problem is not None:
        diagnostic_ref = problem.diagnostic_ref
        provider_diagnostic = recovery is not None or problem.provider_observation is not None
        if provider_diagnostic and diagnostic_ref is None and state is not None and dependencies is not None:
            run_identity = state.get("bundle_id") or state.get("bundle_id")
            if not isinstance(run_identity, str) or not run_identity:
                raise ValueError("run_identity_missing")
            diagnostic_ref = derive_provider_diagnostic_reference(
                bundle_id=run_identity,
                generation=int(state.get("generation", 0)),
                node_attempt=dependencies.agent_context.attempt_id,
                problem=problem,
                recovery=recovery,
            )
        incident = {
            "latest_incident": TerminalIncidentProjection(
                code=problem.code,
                phase=problem.phase,
                certainty=problem.certainty,
                diagnostic_ref=diagnostic_ref,
                provider_recovery=recovery,
                provider_observation=problem.provider_observation,
            ).model_dump(mode="json", exclude_none=True)
        }
    return node_state_update(
        "hitl1",
        route="exhausted",
        terminal_status=LifecycleStatus.BLOCKED.value,
        phase_status=PhaseStatus.TERMINAL.value,
        terminal_reason=TerminalReason.GATE_BLOCKED.value,
        pending_profile=None,
        profile_followup_round=0,
        proposed_profile=None,
        profile_rejection_round=0,
        profile_feedback_cursor_message_id="",
        proposal_version=0,
        interaction_feedback=None,
        **incident,
    )


def _cancel_update() -> dict[str, Any]:
    return node_state_update(
        "hitl1",
        route="cancel",
        terminal_status=LifecycleStatus.CANCELLED.value,
        phase_status=PhaseStatus.TERMINAL.value,
        terminal_reason=TerminalReason.USER_CANCELLED.value,
        pending_profile=None,
        profile_followup_round=0,
        proposed_profile=None,
        profile_rejection_round=0,
        profile_feedback_cursor_message_id="",
        proposal_version=0,
        interaction_feedback=None,
    )


def _descriptor(
    *,
    state: Mapping[str, Any],
    request_id: str,
    context: str,
    allow_acceptance: bool = False,
    interaction: InteractionProjection | None = None,
    language_choice: bool = False,
    output_language: SupportedLanguage | None = None,
) -> PendingResearchInterrupt:
    if language_choice:
        return PendingResearchInterrupt(
            request=HumanInputRequest(
                request_id=request_id,
                mode=HumanInputMode.CHOICE,
                title="选择研究语言 / Select research language",
                context=context,
                options=tuple(
                    HumanInputOption(
                        id=value,
                        value=value,
                        label="中文" if value is SupportedLanguageOption.ZH else "English",
                    )
                    for value in SupportedLanguageOption
                ),
            ),
            suspension_cursor=_cursor(state),
            phase="hitl1",
            generation=int(state.get("generation", 0)),
        )
    return PendingResearchInterrupt(
        request=HumanInputRequest(
            request_id=request_id,
            mode=HumanInputMode.TEXT,
            title="深度研究配置" if output_language is SupportedLanguage.ZH else "Deep Research profile",
            context=context,
            action_ids=("accept_suggestion",) if allow_acceptance else (),
            interaction=interaction,
        ),
        suspension_cursor=_cursor(state),
        phase="hitl1",
        generation=int(state.get("generation", 0)),
    )


def _proposal_payload(brief: StructuredBrief | PartialResearchProfile) -> dict[str, Any]:
    fields = (
        "schema_version",
        "depth",
        "audience",
        "format",
        "cost_tolerance",
        "time_budget",
        "must_answer",
        "scope_boundaries",
        "custom_notes",
        "comparison_required",
        "comparison_subjects",
        "request_language",
        "output_language",
    )
    payload = brief.model_dump(mode="json")
    return {field: payload[field] for field in fields}


def _seeded_profile(brief: StructuredBrief | PartialResearchProfile, request_text: str) -> PartialResearchProfile:
    seed = derive_comparison_intake_seed(request_text)
    payload = _proposal_payload(brief)
    payload.update(
        schema_version=2,
        comparison_required=seed.comparison_required,
        comparison_subjects=seed.comparison_subjects,
        request_language=seed.request_language,
        output_language=seed.output_language,
    )
    return PartialResearchProfile.model_validate(payload)


def _proposed_profile(state: Mapping[str, Any]) -> PartialResearchProfile | None:
    proposal = state.get("proposed_profile")
    return PartialResearchProfile.model_validate(proposal) if proposal is not None else None


def _proposal_version(state: Mapping[str, Any]) -> int:
    """Return a compatible first version for checkpoints written before HITL interaction."""

    version = state.get("proposal_version", 0)
    return version if isinstance(version, int) and version >= 1 else 1


def _interaction_subject(state: Mapping[str, Any], proposal: PartialResearchProfile) -> InteractionSubject:
    question = state.get("request_text")
    if not isinstance(question, str) or not question.strip():
        question = "Research request"
    payload = _proposal_payload(proposal)
    return InteractionSubject(
        proposal_version=_proposal_version(state),
        goal=question.strip()[:768],
        proposal=ProposalValues.model_validate(payload),
    )


def _interaction_feedback(state: Mapping[str, Any]) -> InteractionFeedback | None:
    feedback = state.get("interaction_feedback")
    if feedback is None:
        return None
    return InteractionFeedback.model_validate(feedback)


def _profile_from_confirmation_proposal(proposal: ProposalValues) -> PartialResearchProfile:
    """Convert admitted or advisory typed proposal facts back to HITL1's stored profile shape."""

    return PartialResearchProfile.model_validate(proposal.model_dump(mode="python"))


async def _accepted_confirmation_update(
    request_store: RequestBundleStoreProtocol,
    bundle_state: BundleLocalState,
    facts: AcceptedResearchFacts,
    *,
    response: AcceptedHumanResponse,
) -> dict[str, Any]:
    """Publish accepted content before its Bundle-local State reference."""

    profile = finalize_profile(_profile_from_confirmation_proposal(facts.proposal))
    profile_ref = await request_store.write_profile(profile)
    updated_bundle = await _write_bundle_state(
        request_store,
        bundle_state,
        phase=LogicalPhase.HITL1,
        **profile_state_fields(profile, profile_ref),
        **_consume_response_changes(bundle_state, response),
    )
    return node_state_update(
        "hitl1",
        route="accepted",
        **profile_state_fields(profile, profile_ref),
        **_graph_consumed_fields(updated_bundle),
    )


async def _outstanding_confirmation_update(
    request_store: RequestBundleStoreProtocol,
    bundle_state: BundleLocalState,
    decision: OutstandingResearchDecision,
    *,
    response: AcceptedHumanResponse,
) -> dict[str, Any]:
    """Map one advisory decision back to HITL1's existing follow-up state."""

    fields = {
        "pending_profile": None,
        "proposed_profile": _profile_progress_payload(_profile_from_confirmation_proposal(decision.proposal)),
        "profile_followup_round": 0,
        "profile_rejection_round": 0,
        "profile_feedback_cursor_message_id": response.message_id,
        "proposal_version": decision.proposal_version,
        "interaction_feedback": decision.feedback.model_dump(mode="json") if decision.feedback is not None else None,
    }
    updated_bundle = await _write_bundle_state(
        request_store,
        bundle_state,
        phase=LogicalPhase.HITL1,
        **fields,
        **_consume_response_changes(bundle_state, response),
    )
    return node_state_update(
        "hitl1",
        route="needs_followup",
        **fields,
        **_graph_consumed_fields(updated_bundle),
    )


def _semantic_failure_feedback(kind: InteractionFeedbackKind) -> InteractionFeedback:
    message = (
        _SEMANTIC_UNAVAILABLE_MESSAGE
        if kind is InteractionFeedbackKind.SEMANTIC_UNAVAILABLE
        else _SEMANTIC_INVALID_MESSAGE
    )
    return InteractionFeedback(kind=kind, message=message)


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
            phase="hitl1",
            attempt_id=attempt_id,
            recovery_correlation_id=recovery_correlation_id,
            provider_category=provider_category,
            retry_ordinal=retry_ordinal,
            backoff_milliseconds=backoff_milliseconds,
            recovery_event_disposition=recovery_event_disposition,
        )
    except Exception:
        return


async def _invoke_brief(
    dependencies: NodeBuildDependencies,
    *,
    request,
) -> tuple[NodeExecutionResult | None, NodeProblem | None]:
    outcome = await invoke_and_normalize(
        lambda: dependencies.capabilities.run_agent(
            context=dependencies.agent_context,
            request=request,
        ),
        phase="hitl1",
    )
    if isinstance(outcome, InvocationFailure):
        return None, outcome.problem
    return outcome.result, None


async def _classify_proposal_reply(
    dependencies: NodeBuildDependencies,
    *,
    original_question: str,
    subject: InteractionSubject,
    reply: str,
) -> tuple[SemanticCandidate | None, InteractionFeedback | None]:
    """Return one bounded semantic candidate or closed, non-terminal feedback.

    Each invocation is deliberately independent and zero-tool.  HITL1, rather than
    the bridge or model, owns the shared budget and the decision to preserve the
    proposal after recovery is exhausted.
    """

    repair_error: str | None = None
    invalid_draft: str | None = None
    repair_used = False
    transient_retries = 0

    for invocation_ordinal in range(1, MAX_SEMANTIC_INTAKE_CALLS + 1):
        request = build_semantic_intake_prompt(
            original_question=original_question,
            subject=subject,
            reply=reply,
            repair_error=repair_error,
            invalid_draft=invalid_draft,
        )
        result, problem = await _invoke_brief(dependencies, request=request)
        if problem is not None:
            can_retry = (
                _retry_eligible(problem)
                and transient_retries < MAX_SEMANTIC_TRANSIENT_RETRIES
                and invocation_ordinal < MAX_SEMANTIC_INTAKE_CALLS
            )
            if not can_retry:
                return None, _semantic_failure_feedback(InteractionFeedbackKind.SEMANTIC_UNAVAILABLE)
            transient_retries += 1
            await asyncio.sleep(RETRY_BACKOFF_SECONDS)
            continue

        assert result is not None
        try:
            return parse_semantic_candidate_output(result.summary), None
        except (TypeError, ValueError):
            if repair_used or invocation_ordinal >= MAX_SEMANTIC_INTAKE_CALLS:
                return None, _semantic_failure_feedback(InteractionFeedbackKind.SEMANTIC_INVALID)
            repair_used = True
            repair_error = "semantic_candidate_invalid"
            invalid_draft = result.summary

    return None, _semantic_failure_feedback(InteractionFeedbackKind.SEMANTIC_UNAVAILABLE)


async def _generate_brief(
    dependencies: NodeBuildDependencies,
    question: str,
) -> tuple[Any | None, NodeProblem | None, ProviderRecoveryProjection | None]:
    expected_output_language = derive_comparison_intake_seed(question).output_language
    initial_request = build_brief_prompt(question, output_language=expected_output_language)
    initial_result, initial_problem = await _invoke_brief(dependencies, request=initial_request)
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
        retry_result, retry_problem = await _invoke_brief(dependencies, request=initial_request)
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
            if retry_problem.code not in {RunFailureCode.PROVIDER_TIMEOUT, RunFailureCode.PROVIDER_UNAVAILABLE}:
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
            return None, retry_problem, None
        assert retry_result is not None
        try:
            return (
                parse_brief_output(
                    retry_result.summary,
                    expected_output_language=expected_output_language,
                ),
                None,
                None,
            )
        except (TypeError, ValueError):
            return (
                None,
                NodeProblem(
                    code=RunFailureCode.OUTPUT_STRUCTURED_INVALID,
                    phase="hitl1",
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
            parse_brief_output(
                initial_result.summary,
                expected_output_language=expected_output_language,
            ),
            None,
            None,
        )
    except (TypeError, ValueError):
        repair_result, repair_problem = await _invoke_brief(
            dependencies,
            request=build_brief_prompt(
                question,
                output_language=expected_output_language,
                repair_error="structured_output_invalid",
                invalid_draft=initial_result.summary,
            ),
        )
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
                parse_brief_output(
                    repair_result.summary,
                    expected_output_language=expected_output_language,
                ),
                None,
                None,
            )
        except (TypeError, ValueError):
            return (
                None,
                NodeProblem(
                    code=RunFailureCode.OUTPUT_STRUCTURED_INVALID,
                    phase="hitl1",
                    certainty=FailureCertainty.DIRECT,
                ),
                None,
            )


def _pending_progress(state: Mapping[str, Any]) -> PartialResearchProfile | None:
    pending = state.get("pending_profile")
    if pending is None:
        return None
    return PartialResearchProfile.model_validate(pending)


def build_real(dependencies: NodeBuildDependencies):
    async def run(state):
        request_store = dependencies.request_bundle
        if request_store is None:
            raise ValueError("request_bundle_capability_missing")

        bundle_state = await request_store.read_bundle_state()
        durable_state = _state_from_bundle(state, bundle_state)
        request_text = str(state.get("request_text") or "")
        seed = derive_comparison_intake_seed(request_text)
        # Non-interactive auto-profile: skip interrupt only when no human fact is required.
        non_interactive = state.get("non_interactive_policy")
        if isinstance(non_interactive, dict) and non_interactive.get("auto_profile") is True:
            if (seed.comparison_required and seed.comparison_subjects is None) or seed.output_language is None:
                await _persist_terminal(request_store, bundle_state, status=LifecycleStatus.BLOCKED)
                return _exhausted_update()
            profile = finalize_profile(
                PartialResearchProfile(
                    schema_version=2,
                    comparison_required=seed.comparison_required,
                    comparison_subjects=seed.comparison_subjects,
                    request_language=seed.request_language,
                    output_language=seed.output_language,
                ),
                degraded=True,
            )
            profile_ref = await request_store.write_profile(profile)
            await _write_bundle_state(
                request_store,
                bundle_state,
                phase=LogicalPhase.HITL1,
                **profile_state_fields(profile, profile_ref),
            )
            return node_state_update(
                "hitl1",
                route="accepted",
                execution_trace=("hitl1", "hitl1_auto_profile"),
                **profile_state_fields(profile, profile_ref),
            )

        pending = _pending_progress(durable_state)
        proposal = _proposed_profile(durable_state)
        request_id, ordinal = _request_id(bundle_state)
        if pending is None and proposal is None:
            brief, problem, recovery = await _generate_brief(dependencies, request_text)
            if brief is None:
                await _persist_terminal(request_store, bundle_state, status=LifecycleStatus.BLOCKED)
                return _exhausted_update(
                    problem,
                    state=durable_state,
                    dependencies=dependencies,
                    recovery=recovery,
                )
            # Persist before the next interrupted visit. The graph update below is a
            # projection only; the selected Bundle retains the restart authority.
            fields = {
                "pending_profile": None,
                "proposed_profile": _proposal_payload(_seeded_profile(brief, request_text)),
                "profile_rejection_round": 0,
                "profile_feedback_cursor_message_id": "",
                "proposal_version": 1,
                "interaction_feedback": None,
            }
            await _write_bundle_state(
                request_store,
                bundle_state,
                phase=LogicalPhase.HITL1,
                phase_status=PhaseStatus.IN_PROGRESS,
                terminal_status=None,
                waiting_for=None,
                pending_request_id=None,
                pending_cursor=None,
                pending_request_mode=None,
                **fields,
            )
            return node_state_update(
                "hitl1",
                route="needs_followup",
                **fields,
            )
        else:
            progress = pending or proposal or _seeded_profile(PartialResearchProfile(), request_text)
            subject: InteractionSubject | None = None
            interaction: InteractionProjection | None = None
            language_choice = (
                proposal is not None
                and proposal.request_language.value == "unspecified"
                and proposal.output_language is None
            )
            if proposal is not None and pending is None and not language_choice:
                subject = _interaction_subject(durable_state, proposal)
                interaction = build_interaction_projection(
                    subject,
                    feedback=_interaction_feedback(durable_state),
                )
            if language_choice:
                assert proposal is not None
                context = build_language_choice_context(proposal)
            elif proposal is not None and pending is None and not missing_dimensions(proposal):
                context = build_proposal_context(proposal)
            else:
                context = build_followup_context(
                    progress,
                    missing_dimensions(progress),
                    rejection_round=int(durable_state.get("profile_rejection_round", 0)),
                )

        descriptor = _descriptor(
            state=durable_state,
            request_id=request_id,
            context=context,
            allow_acceptance=interaction is not None and bool(interaction.controls),
            interaction=interaction,
            language_choice=language_choice if proposal is not None else False,
            output_language=progress.output_language,
        )
        if bundle_state.pending_request_id is None:
            # This write must finish before ``interrupt``. A replay reads the same
            # Bundle-local descriptor and therefore never allocates a second id.
            bundle_state = await _write_bundle_state(
                request_store,
                bundle_state,
                phase=LogicalPhase.HITL1,
                phase_status=PhaseStatus.WAITING,
                terminal_status=None,
                waiting_for="hitl1",
                pending_request_id=request_id,
                pending_cursor=descriptor.suspension_cursor,
                pending_request_mode=descriptor.request.mode,
                hitl1_visit_count=ordinal,
            )
        elif bundle_state.pending_request_mode not in {None, descriptor.request.mode}:
            raise ValueError("pending_request_mode_mismatch")
        elif bundle_state.pending_request_mode is None or bundle_state.pending_cursor is None:
            bundle_state = await _write_bundle_state(
                request_store,
                bundle_state,
                phase=LogicalPhase.HITL1,
                phase_status=PhaseStatus.WAITING,
                waiting_for="hitl1",
                pending_cursor=bundle_state.pending_cursor or descriptor.suspension_cursor,
                pending_request_mode=descriptor.request.mode,
            )
        raw = interrupt(
            descriptor.model_dump(
                mode="json",
                exclude_none=descriptor.request.mode is HumanInputMode.CHOICE,
            )
        )
        if isinstance(raw, dict) and raw.get("kind") == "internal_cancel":
            InternalCancelDecision.model_validate(raw)
            await _persist_terminal(request_store, bundle_state, status=LifecycleStatus.CANCELLED)
            return _cancel_update()

        response = AcceptedHumanResponse.model_validate(raw)
        if response.request_id != request_id:
            raise ValueError("response_mismatch")

        if descriptor.request.mode is HumanInputMode.CHOICE:
            if (
                response.response_kind is not ResponseKind.OPTION
                or proposal is None
                or response.option_id not in {option.id.value for option in descriptor.request.options}
            ):
                raise ValueError("response_invalid")
            selected = proposal.model_copy(update={"output_language": response.option_id})
            fields = {
                "pending_profile": None,
                "proposed_profile": _profile_progress_payload(selected),
                "profile_followup_round": int(durable_state.get("profile_followup_round", 0)) + 1,
                "profile_rejection_round": 0,
                "profile_feedback_cursor_message_id": "",
                "proposal_version": _proposal_version(durable_state),
                "interaction_feedback": None,
            }
            updated_bundle = await _write_bundle_state(
                request_store,
                bundle_state,
                phase=LogicalPhase.HITL1,
                **fields,
                **_consume_response_changes(bundle_state, response),
            )
            return node_state_update(
                "hitl1",
                route="needs_followup",
                **fields,
                **_graph_consumed_fields(updated_bundle),
            )

        if response.response_kind is ResponseKind.ACTION:
            if (
                response.action_id != "accept_suggestion"
                or proposal is None
                or subject is None
                or missing_dimensions(proposal)
            ):
                raise ValueError("response_invalid")
            outcome = admit_research_confirmation(
                subject,
                evidence=DirectConfirmation(basis="visible_control"),
            )
            if isinstance(outcome, AcceptedResearchFacts):
                return await _accepted_confirmation_update(request_store, bundle_state, outcome, response=response)
            return await _outstanding_confirmation_update(request_store, bundle_state, outcome, response=response)

        if response.response_kind is not ResponseKind.TEXT:
            raise ValueError("response_invalid")

        if proposal is not None and pending is None and not missing_dimensions(proposal):
            assert subject is not None
            if normalize_clear_confirmation(response.value):
                evidence = DirectConfirmation(basis="clear_text")
            else:
                candidate, feedback = await _classify_proposal_reply(
                    dependencies,
                    original_question=str(durable_state.get("request_text") or "Research request"),
                    subject=subject,
                    reply=response.value,
                )
                if candidate is not None:
                    evidence = SemanticInterpretation(candidate=candidate)
                else:
                    assert feedback is not None
                    evidence = SemanticInterpretation(feedback=feedback)
            outcome = admit_research_confirmation(subject, evidence=evidence)
            if isinstance(outcome, AcceptedResearchFacts):
                return await _accepted_confirmation_update(request_store, bundle_state, outcome, response=response)
            return await _outstanding_confirmation_update(request_store, bundle_state, outcome, response=response)

        try:
            parsed = parse_profile_input(
                response.value,
                allow_comparison_pair=progress.comparison_required and progress.comparison_subjects is None,
            )
        except (TypeError, ValueError):
            parsed = None
        if parsed is None:
            incoming = PartialResearchProfile()
            recognized_fields: tuple[str, ...] = ()
        else:
            incoming = parsed.partial
            recognized_fields = parsed.recognized_fields
        if not recognized_fields:
            rejection_round = int(durable_state.get("profile_rejection_round", 0)) + 1
            if rejection_round >= MAX_HITL1_ANSWER_ROUNDS:
                await _persist_terminal(request_store, bundle_state, status=LifecycleStatus.BLOCKED)
                return _exhausted_update(
                    NodeProblem(
                        code=RunFailureCode.INPUT_INVALID_RESPONSE,
                        phase="hitl1",
                        certainty=FailureCertainty.DIRECT,
                        diagnostic_ref=f"diag_{request_id.removeprefix('drh_')[:24]}",
                    )
                )
            fields = {
                "pending_profile": _profile_progress_payload(progress),
                "profile_followup_round": int(durable_state.get("profile_followup_round", 0)),
                "profile_rejection_round": rejection_round,
                "profile_feedback_cursor_message_id": response.message_id,
                "proposal_version": 0,
                "interaction_feedback": None,
            }
            updated_bundle = await _write_bundle_state(
                request_store,
                bundle_state,
                phase=LogicalPhase.HITL1,
                **fields,
                **_consume_response_changes(bundle_state, response),
            )
            return node_state_update(
                "hitl1",
                route="needs_followup",
                **fields,
                **_graph_consumed_fields(updated_bundle),
            )
        merged = merge_profile_progress(progress, incoming)
        missing = missing_dimensions(merged)
        accepted_round = int(durable_state.get("profile_followup_round", 0)) + 1
        if missing and accepted_round < MAX_HITL1_ANSWER_ROUNDS:
            fields = {
                "pending_profile": _profile_progress_payload(merged),
                "profile_followup_round": accepted_round,
                "proposed_profile": None,
                "profile_rejection_round": 0,
                "profile_feedback_cursor_message_id": "",
                "proposal_version": 0,
                "interaction_feedback": None,
            }
            updated_bundle = await _write_bundle_state(
                request_store,
                bundle_state,
                phase=LogicalPhase.HITL1,
                **fields,
                **_consume_response_changes(bundle_state, response),
            )
            return node_state_update(
                "hitl1",
                route="needs_followup",
                **fields,
                **_graph_consumed_fields(updated_bundle),
            )

        if {"comparison_subjects", "output_language"} & set(missing):
            await _persist_terminal(request_store, bundle_state, status=LifecycleStatus.BLOCKED)
            return _exhausted_update()

        profile = finalize_profile(merged, degraded=bool(missing))
        profile_ref = await request_store.write_profile(profile)
        updated_bundle = await _write_bundle_state(
            request_store,
            bundle_state,
            phase=LogicalPhase.HITL1,
            **profile_state_fields(profile, profile_ref),
            **_consume_response_changes(bundle_state, response),
        )
        return node_state_update(
            "hitl1",
            route="accepted",
            **profile_state_fields(profile, profile_ref),
            **_graph_consumed_fields(updated_bundle),
        )

    return run


__all__ = ["build_real"]
