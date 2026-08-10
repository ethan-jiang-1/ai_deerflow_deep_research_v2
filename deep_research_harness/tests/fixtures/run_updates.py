"""Safe run-experience fixtures shared by standalone presentation adapters."""

from __future__ import annotations

from deerflow_deep_research.domain.human_interaction import (
    InteractionFeedback,
    InteractionProjection,
    InteractionSubject,
    ProposalValues,
    current_proposal_control,
)
from deerflow_deep_research.domain.run_experience import (
    FRESH_START_NEXT_ACTION,
    AwaitingInput,
    FailureCertainty,
    Fault,
    PendingInputProjection,
    PromptOption,
    PromptView,
    ProviderObservation,
    ProviderRecoveryProjection,
    RunFailure,
    RunFailureCode,
    RunSnapshot,
    Terminal,
)
from deerflow_deep_research.domain.run_observation import (
    ObservationInspectability,
    RetentionState,
    RunObservationView,
)

BUNDLE_ID = "b_" + "A" * 43
DIAGNOSTIC_REF = "diag_" + "P" * 24


def _observation(*, available: bool = True, matches_diagnostic: bool = True) -> RunObservationView:
    return RunObservationView(
        bundle_id=BUNDLE_ID,
        inspectability=(ObservationInspectability.AVAILABLE if available else ObservationInspectability.UNAVAILABLE),
        retention_state=RetentionState.RETAINED if available else None,
        durability="same_process",
        terminal_diagnostic_ref=DIAGNOSTIC_REF if matches_diagnostic else "diag_" + "S" * 24,
    )


def awaiting_hitl1(*, feedback: InteractionFeedback | None = None) -> AwaitingInput:
    interaction = InteractionProjection(
        subject=InteractionSubject(
            proposal_version=1,
            goal="Compare public storage options.",
            proposal=ProposalValues(
                depth="standard",
                audience="practitioner",
                format="detailed_report",
                cost_tolerance="moderate",
                time_budget="standard",
                must_answer=("Compare current options.",),
            ),
        ),
        feedback=feedback,
        controls=(current_proposal_control(),),
    )
    pending = PendingInputProjection(
        request_id="drh-profile",
        pending_phase="hitl1",
        generation=0,
        mode="text",
    )
    return AwaitingInput(
        snapshot=RunSnapshot(
            bundle_id=BUNDLE_ID,
            durability="same_process",
            lifecycle_phase="bootstrap",
            completed_trace=("bootstrap",),
            pending_input=pending,
        ),
        prompt=PromptView(
            phase="hitl1",
            request_id=pending.request_id,
            mode="text",
            heading="Confirm research scope",
            goal="Compare public storage options.",
            proposed_scope=("depth: standard",),
            missing_fields=("format",),
            interaction=interaction,
            visible_controls=interaction.controls,
            answer_example="For practitioners, use a detailed report.",
        ),
        trace_delta=("bootstrap",),
    )


def awaiting_complete_typed_hitl1() -> AwaitingInput:
    """Return one complete shared proposal with every bounded display line."""
    interaction = InteractionProjection(
        subject=InteractionSubject(
            proposal_version=2,
            goal="Prepare a Python 3.12 upgrade checklist.",
            proposal=ProposalValues(
                schema_version=2,
                depth="deep_dive",
                audience="practitioner",
                format="detailed_report",
                cost_tolerance="moderate",
                time_budget="thorough",
                must_answer=tuple(f"Question {index}" for index in range(1, 9)),
                scope_boundaries="Use Python official documentation only.",
                custom_notes="Write the result in Chinese.",
                comparison_required=True,
                comparison_subjects=("Python 3.11", "Python 3.12"),
                request_language="zh",
                output_language="zh",
            ),
        ),
        controls=(current_proposal_control(),),
    )
    pending = PendingInputProjection(
        request_id="drh-complete-proposal",
        pending_phase="hitl1",
        generation=0,
        mode="text",
    )
    return AwaitingInput(
        snapshot=RunSnapshot(
            bundle_id=BUNDLE_ID,
            durability="same_process",
            lifecycle_phase="bootstrap",
            completed_trace=("bootstrap",),
            pending_input=pending,
        ),
        prompt=PromptView(
            phase="hitl1",
            request_id=pending.request_id,
            mode="text",
            heading="Confirm research scope",
            goal=interaction.subject.goal,
            proposed_scope=(
                "depth: deep_dive",
                "audience: practitioner",
                "format: detailed_report",
                "cost_tolerance: moderate",
                "time_budget: thorough",
                *(f"must_answer[{index}]: Question {index}" for index in range(1, 9)),
                "scope_boundaries: Use Python official documentation only.",
                "custom_notes: Write the result in Chinese.",
                "comparison_subjects: Python 3.11 | Python 3.12",
                "output_language: zh",
            ),
            interaction=interaction,
            visible_controls=interaction.controls,
        ),
        trace_delta=("bootstrap",),
    )


def awaiting_hitl2() -> AwaitingInput:
    pending = PendingInputProjection(
        request_id="drh-decision",
        pending_phase="hitl2",
        generation=1,
        mode="choice",
    )
    return AwaitingInput(
        snapshot=RunSnapshot(
            bundle_id=BUNDLE_ID,
            durability="same_process",
            lifecycle_phase="wave2_synthesis",
            completed_trace=("bootstrap", "hitl1", "wave2_synthesis"),
            pending_input=pending,
        ),
        prompt=PromptView(
            phase="hitl2",
            request_id=pending.request_id,
            mode="choice",
            heading="Choose the next step",
            goal="Review the current research plan.",
            body_lines=("Choose one graph-owned option.",),
            options=(
                PromptOption(id="proceed", label="Continue", consequence="Continue with the current plan."),
                PromptOption(id="rerun", label="Rerun", consequence="Start a new research generation."),
                PromptOption(id="repair", label="Repair", consequence="Collect missing evidence."),
                PromptOption(id="revise_view", label="Revise", consequence="Revisit synthesis."),
                PromptOption(id="stop", label="Stop", consequence="End this research run."),
            ),
        ),
        trace_delta=("wave2_synthesis",),
    )


def awaiting_invalid_hitl2_choice() -> AwaitingInput:
    """Return the safe shared retry view without any lifecycle wire data."""
    update = awaiting_hitl2()
    return update.model_copy(
        update={
            "prompt": update.prompt.model_copy(update={"rejection_category": "choice_input_invalid"}),
            "trace_delta": (),
        }
    )


def completed() -> Terminal:
    return Terminal(
        snapshot=RunSnapshot(
            bundle_id=BUNDLE_ID,
            durability="same_process",
            lifecycle_phase="final_delivery",
            completed_trace=("bootstrap", "final_delivery"),
        ),
        outcome="completed",
        trace_delta=("final_delivery",),
    )


def auto_profile_terminal() -> Terminal:
    """Terminal whose returned trace includes presentation-only policy trace steps."""
    return Terminal(
        snapshot=RunSnapshot(
            bundle_id=BUNDLE_ID,
            durability="same_process",
            lifecycle_phase="final_delivery",
            completed_trace=("hitl1", "hitl1_auto_profile", "hitl2", "hitl2_auto_proceed", "final_delivery"),
        ),
        outcome="completed",
        trace_delta=("hitl1", "hitl1_auto_profile", "hitl2_auto_proceed", "final_delivery"),
    )


def provider_fault() -> Fault:
    return Fault(
        snapshot=RunSnapshot(bundle_id=BUNDLE_ID, durability="same_process", lifecycle_phase="hitl1"),
        failure=RunFailure(
            code=RunFailureCode.PROVIDER_TIMEOUT,
            phase="hitl1",
            certainty=FailureCertainty.DIRECT,
            message="Provider did not respond in time.",
            next_action="Try again later.",
            retryable=True,
            diagnostic_ref="diag_ABCDEFGHIJKL",
            journal_record_created=True,
        ),
    )


def typed_hitl1_terminal(*, code: RunFailureCode) -> Terminal:
    """Return a non-provider HITL1 terminal with deliberately unsafe source text."""
    next_action = (
        "重新开始该研究；若持续出现，请提供诊断引用。"
        if code is RunFailureCode.OUTPUT_STRUCTURED_INVALID
        else "根据提示检查前提条件或提供诊断引用。"
    )
    return Terminal(
        snapshot=RunSnapshot(
            bundle_id=BUNDLE_ID,
            durability="same_process",
            lifecycle_phase="hitl1",
            completed_trace=("bootstrap", "hitl1"),
            observation=_observation(),
        ),
        outcome="blocked",
        failure=RunFailure(
            code=code,
            phase="hitl1",
            certainty=FailureCertainty.DIRECT,
            message=(
                "question=private prompt=private provider-body=private "
                "https://secret.example.test/path?token=secret exception=private"
            ),
            next_action=next_action,
            retryable=code is RunFailureCode.OUTPUT_STRUCTURED_INVALID,
            diagnostic_ref=DIAGNOSTIC_REF,
            journal_record_created=True,
        ),
    )


def exhausted_provider_terminal(
    *,
    matching_observation: bool = True,
    observation_available: bool = True,
    phase: str = "hitl1",
) -> Terminal:
    """Build one shared, bounded provider-recovery terminal projection.

    The presentation tests deliberately consume this shared ``Terminal`` rather
    than reaching into a retained bundle or a graph/control fixture.
    """
    final_observation = ProviderObservation(
        configured_service_label="deepseek-v4-pro",
        configured_endpoint_authority="https://api.example.test",
        response_kind="no_response",
        timeout_origin="provider_sdk_timeout",
    )
    trigger_observation = ProviderObservation(
        configured_service_label="deepseek-v4-pro",
        configured_endpoint_authority="https://api.example.test",
        response_kind="no_response",
        timeout_origin="bridge_wall_time_budget",
    )
    recovery = ProviderRecoveryProjection(
        trigger_category="provider.timeout",
        trigger_observation=trigger_observation,
        trigger_invocation_ordinal=1,
        model_attempts=2,
        automatic_retries=1,
        disposition="exhausted",
    )
    return Terminal(
        snapshot=RunSnapshot(
            bundle_id=BUNDLE_ID,
            durability="same_process",
            lifecycle_phase=phase,
            completed_trace=("bootstrap", phase),
            observation=_observation(
                available=observation_available,
                matches_diagnostic=matching_observation,
            ),
        ),
        outcome="blocked",
        failure=RunFailure(
            code=RunFailureCode.PROVIDER_TIMEOUT,
            phase=phase,
            certainty=FailureCertainty.DIRECT,
            message="Provider recovery failed after a bounded retry.",
            next_action=FRESH_START_NEXT_ACTION,
            retryable=True,
            diagnostic_ref=DIAGNOSTIC_REF,
            journal_record_created=observation_available,
            provider_recovery=recovery,
            provider_observation=final_observation,
            recovery_action="fresh_start",
            diagnostic_location="bundle_journal" if observation_available else "unavailable",
        ),
    )


def controller_provider_terminal() -> Terminal:
    """Build a provider incident derived from an exhausted worker controller."""
    observation = ProviderObservation(
        configured_service_label="wave0-worker-model",
        response_kind="no_response",
    )
    return Terminal(
        snapshot=RunSnapshot(
            bundle_id=BUNDLE_ID,
            durability="same_process",
            lifecycle_phase="wave0",
            completed_trace=("bootstrap", "wave0"),
            observation=_observation(),
        ),
        outcome="blocked",
        failure=RunFailure(
            code=RunFailureCode.PROVIDER_TIMEOUT,
            phase="wave0",
            certainty=FailureCertainty.DIRECT,
            message="The Wave0 worker controller exhausted a provider failure.",
            next_action="Check service availability, then start a distinct run.",
            retryable=True,
            diagnostic_ref=DIAGNOSTIC_REF,
            journal_record_created=True,
            worker_failure_category="agent_invocation",
            provider_observation=observation,
            diagnostic_location="bundle_journal",
        ),
    )


def repair_slot_provider_terminal() -> Terminal:
    """Build the second legal fresh-start disposition without a third call."""
    observation = ProviderObservation(
        configured_service_label="deepseek-v4-pro",
        configured_endpoint_authority="https://api.example.test",
        response_kind="no_response",
    )
    recovery = ProviderRecoveryProjection(
        trigger_category="provider.unavailable",
        trigger_observation=observation,
        trigger_invocation_ordinal=2,
        model_attempts=2,
        automatic_retries=0,
        disposition="retry_not_started_budget_consumed",
    )
    return Terminal(
        snapshot=RunSnapshot(
            bundle_id=BUNDLE_ID,
            durability="same_process",
            lifecycle_phase="hitl1",
            completed_trace=("bootstrap", "hitl1"),
        ),
        outcome="blocked",
        failure=RunFailure(
            code=RunFailureCode.PROVIDER_UNAVAILABLE,
            phase="hitl1",
            certainty=FailureCertainty.DIRECT,
            message="The repair invocation reached a transient provider failure.",
            next_action=FRESH_START_NEXT_ACTION,
            retryable=True,
            diagnostic_ref=DIAGNOSTIC_REF,
            journal_record_created=False,
            provider_recovery=recovery,
            provider_observation=observation,
            recovery_action="fresh_start",
            diagnostic_location="unavailable",
        ),
    )


def nonretryable_http_provider_terminal(*, journal_available: bool = False) -> Terminal:
    """Build a final safe HTTP observation without fabricated retry history."""
    location = "bundle_journal" if journal_available else "unavailable"
    return Terminal(
        snapshot=RunSnapshot(
            bundle_id=BUNDLE_ID,
            durability="same_process",
            lifecycle_phase="hitl1",
            completed_trace=("bootstrap", "hitl1"),
            observation=_observation() if journal_available else None,
        ),
        outcome="blocked",
        failure=RunFailure(
            code=RunFailureCode.INTERNAL_UNEXPECTED,
            phase="hitl1",
            certainty=FailureCertainty.DIRECT,
            message="The provider returned a non-retryable response.",
            next_action="Review the diagnostic reference before starting a distinct run.",
            retryable=False,
            diagnostic_ref=DIAGNOSTIC_REF,
            journal_record_created=journal_available,
            provider_observation=ProviderObservation(
                configured_service_label="deepseek-v4-pro",
                configured_endpoint_authority="https://api.example.test",
                response_kind="http_response",
                http_status=400,
            ),
            diagnostic_location=location,
        ),
    )
