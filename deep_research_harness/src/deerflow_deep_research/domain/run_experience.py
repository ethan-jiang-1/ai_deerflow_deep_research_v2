"""Frozen contracts for the standalone research run experience.

The contracts intentionally contain only safe presentation values.  Lifecycle
wire payloads, graph messages, raw exceptions, and diagnostic record contents
remain runtime-owned.

@impl RER-001
@impl RER-003
@impl RER-004
@impl PRS-005
"""

from __future__ import annotations

import ipaddress
import re
from enum import StrEnum
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from deerflow_deep_research.domain.human_interaction import InteractionProjection, VisibleControl
from deerflow_deep_research.domain.run_observation import ProviderTimeoutOrigin, RunObservationView


class FrozenRunContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class RunFailureCode(StrEnum):
    CONFIGURATION_MODEL_MISSING = "configuration.model_missing"
    CONFIGURATION_WEB_TOOL_MISSING = "configuration.web_tool_missing"
    CONFIGURATION_ENVIRONMENT_INVALID = "configuration.environment_invalid"
    PROVIDER_AUTHENTICATION_FAILED = "provider.authentication_failed"
    PROVIDER_UNAVAILABLE = "provider.unavailable"
    PROVIDER_TIMEOUT = "provider.timeout"
    PROVIDER_USAGE_UNAVAILABLE = "provider.usage_unavailable"
    BUDGET_EXHAUSTED = "budget.exhausted"
    POLICY_DENIED = "policy.denied"
    TOOL_UNAVAILABLE = "tool.unavailable"
    TOOL_EXECUTION_FAILED = "tool.execution_failed"
    OUTPUT_STRUCTURED_INVALID = "output.structured_invalid"
    INPUT_INVALID_RESPONSE = "input.invalid_response"
    PERSISTENCE_UNAVAILABLE = "persistence.unavailable"
    BUNDLE_UNAVAILABLE = "bundle.unavailable"
    CHECKPOINT_INCONSISTENT = "checkpoint.inconsistent"
    RESEARCH_BLOCKED = "research.blocked"
    PROTOCOL_INVALID_RESULT = "protocol.invalid_result"
    LOCAL_INTERRUPTED = "local.interrupted"
    INTERNAL_UNEXPECTED = "internal.unexpected"


class FailureCertainty(StrEnum):
    DIRECT = "direct"
    UNKNOWN = "unknown"


RunMode = Literal["fake", "real"]
LogicalPhaseName = Literal[
    "bootstrap",
    "hitl1",
    "topic_planning",
    "wave0",
    "wave1",
    "wave2_synthesis",
    "targeted_evidence",
    "hitl2",
    "rerun",
    "readiness",
    "final_delivery",
]
RunTraceEntry = LogicalPhaseName | Literal["hitl1_auto_profile", "hitl2_auto_proceed"]


class PendingInputProjection(FrozenRunContract):
    """Bounded presentation view of the one graph-owned pending interrupt."""

    schema_version: Literal[1] = 1
    request_id: str = Field(min_length=1, max_length=128)
    pending_phase: Literal["hitl1", "hitl2"]
    generation: int = Field(ge=0, le=2)
    mode: Literal["text", "choice"]

    @model_validator(mode="after")
    def validate_phase_mode(self) -> PendingInputProjection:
        if self.pending_phase == "hitl2" and self.mode != "choice":
            raise ValueError("pending_input_phase_mode_mismatch")
        return self


_SERVICE_LABEL_RE = re.compile(r"^[A-Za-z0-9._-]{1,96}$")
_TRANSIENT_HTTP_STATUSES = frozenset({408, 429, 500, 502, 503, 504})
_AUTHENTICATION_HTTP_STATUSES = frozenset({401, 403})
FRESH_START_NEXT_ACTION = "可启动一个独立的新研究运行；这不会恢复当前运行。"


class ProviderObservation(FrozenRunContract):
    """Closed, redacted fact about the configured HITL1 model service response."""

    configured_service_label: str | None = Field(default=None, max_length=96)
    configured_endpoint_authority: str | None = Field(default=None, max_length=253)
    response_kind: Literal["no_response", "http_response"]
    http_status: int | None = Field(default=None, ge=100, le=599)
    timeout_origin: ProviderTimeoutOrigin | None = None

    @field_validator("configured_service_label")
    @classmethod
    def validate_service_label(cls, value: str | None) -> str | None:
        if value is not None and _SERVICE_LABEL_RE.fullmatch(value) is None:
            raise ValueError("configured_service_label_invalid")
        return value

    @field_validator("configured_endpoint_authority")
    @classmethod
    def validate_endpoint_authority(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value.isascii() or len(value) > 253 or value != value.lower():
            raise ValueError("configured_endpoint_authority_invalid")
        try:
            parsed = urlsplit(value)
            port = parsed.port
        except ValueError as exc:
            raise ValueError("configured_endpoint_authority_invalid") from exc
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path
            or parsed.query
            or parsed.fragment
            or parsed.hostname is None
            or "@" in parsed.netloc
        ):
            raise ValueError("configured_endpoint_authority_invalid")
        hostname = parsed.hostname
        try:
            ipaddress.ip_address(hostname)
        except ValueError:
            labels = hostname.split(".")
            if any(
                not label
                or len(label) > 63
                or label[0] == "-"
                or label[-1] == "-"
                or not all(character.isascii() and (character.isalnum() or character == "-") for character in label)
                for label in labels
            ):
                raise ValueError("configured_endpoint_authority_invalid") from None
        if (parsed.scheme == "http" and port == 80) or (parsed.scheme == "https" and port == 443):
            raise ValueError("configured_endpoint_authority_not_normalized")
        return value

    @model_validator(mode="after")
    def validate_response_shape(self) -> ProviderObservation:
        if (self.response_kind == "no_response") != (self.http_status is None):
            raise ValueError("provider_observation_response_pairing_invalid")
        if self.timeout_origin is not None and self.response_kind != "no_response":
            raise ValueError("provider_timeout_origin_requires_no_response")
        return self


class ProviderRecoveryProjection(FrozenRunContract):
    """Checkpoint-owned bounded account of one HITL1 transient recovery visit."""

    trigger_category: Literal["provider.timeout", "provider.unavailable"]
    trigger_observation: ProviderObservation
    trigger_invocation_ordinal: int = Field(ge=1, le=2)
    model_attempts: int = Field(ge=1, le=2)
    automatic_retries: int = Field(ge=0, le=1)
    disposition: Literal[
        "exhausted",
        "retry_followed_by_terminal_failure",
        "retry_not_started_budget_consumed",
    ]

    @model_validator(mode="after")
    def validate_recovery_tuple(self) -> ProviderRecoveryProjection:
        if self.trigger_category == "provider.timeout":
            if self.trigger_observation.response_kind != "no_response":
                raise ValueError("provider_timeout_trigger_observation_invalid")
        elif not (
            self.trigger_observation.response_kind == "no_response"
            or self.trigger_observation.http_status in _TRANSIENT_HTTP_STATUSES
        ):
            raise ValueError("provider_unavailable_trigger_observation_invalid")
        expected = {
            "exhausted": (1, 2, 1),
            "retry_followed_by_terminal_failure": (1, 2, 1),
            "retry_not_started_budget_consumed": (2, 2, 0),
        }[self.disposition]
        if (self.trigger_invocation_ordinal, self.model_attempts, self.automatic_retries) != expected:
            raise ValueError("provider_recovery_tuple_invalid")
        return self


def _validate_final_provider_observation(
    *,
    code: RunFailureCode,
    observation: ProviderObservation | None,
) -> None:
    if observation is None:
        return
    if code is RunFailureCode.PROVIDER_TIMEOUT:
        if observation.response_kind != "no_response":
            raise ValueError("provider_timeout_observation_invalid")
        return
    if code is RunFailureCode.PROVIDER_UNAVAILABLE:
        if not (observation.response_kind == "no_response" or observation.http_status in _TRANSIENT_HTTP_STATUSES):
            raise ValueError("provider_unavailable_observation_invalid")
        return
    if code is RunFailureCode.PROVIDER_AUTHENTICATION_FAILED:
        if observation.response_kind != "http_response" or observation.http_status not in _AUTHENTICATION_HTTP_STATUSES:
            raise ValueError("provider_authentication_observation_invalid")
        return
    if observation.response_kind != "http_response" or observation.http_status in (
        _TRANSIENT_HTTP_STATUSES | _AUTHENTICATION_HTTP_STATUSES
    ):
        raise ValueError("non_retryable_provider_observation_invalid")


class TerminalIncidentProjection(FrozenRunContract):
    """Compact checkpoint-safe cause for a terminal blocked result."""

    schema_version: Literal[1] = 1
    code: RunFailureCode
    phase: LogicalPhaseName | None = None
    certainty: FailureCertainty
    diagnostic_ref: str | None = Field(default=None, pattern=r"^diag_[A-Za-z0-9_-]{8,64}$")
    worker_failure_category: (
        Literal["agent_invocation", "tool_execution", "structured_output", "submission_validation", "unknown", "mixed"]
        | None
    ) = None
    provider_recovery: ProviderRecoveryProjection | None = None
    provider_observation: ProviderObservation | None = None

    @model_validator(mode="after")
    def validate_provider_terminal(self) -> TerminalIncidentProjection:
        _validate_final_provider_observation(code=self.code, observation=self.provider_observation)
        if self.provider_recovery is not None:
            if self.provider_recovery.disposition == "exhausted" and self.code not in {
                RunFailureCode.PROVIDER_TIMEOUT,
                RunFailureCode.PROVIDER_UNAVAILABLE,
            }:
                raise ValueError("provider_recovery_exhausted_final_category_invalid")
            if self.provider_recovery.disposition == "retry_not_started_budget_consumed" and self.code not in {
                RunFailureCode.PROVIDER_TIMEOUT,
                RunFailureCode.PROVIDER_UNAVAILABLE,
            }:
                raise ValueError("provider_recovery_budget_final_category_invalid")
            if self.provider_recovery.disposition == "retry_followed_by_terminal_failure" and self.code in {
                RunFailureCode.PROVIDER_TIMEOUT,
                RunFailureCode.PROVIDER_UNAVAILABLE,
            }:
                raise ValueError("provider_recovery_followed_final_category_invalid")
        has_provider_diagnostic = self.provider_recovery is not None or self.provider_observation is not None
        if has_provider_diagnostic and self.diagnostic_ref is None:
            raise ValueError("provider_terminal_requires_diagnostic_ref")
        return self


class NodeProblem(FrozenRunContract):
    """Safe causal category returned from a runtime node-agent boundary."""

    code: RunFailureCode
    phase: LogicalPhaseName | None = None
    certainty: FailureCertainty = FailureCertainty.UNKNOWN
    diagnostic_ref: str | None = Field(default=None, pattern=r"^diag_[A-Za-z0-9_-]{8,64}$")
    provider_observation: ProviderObservation | None = None

    @model_validator(mode="after")
    def validate_provider_observation(self) -> NodeProblem:
        _validate_final_provider_observation(code=self.code, observation=self.provider_observation)
        return self


class StartRun(FrozenRunContract):
    kind: Literal["start"] = "start"
    question: str = Field(min_length=1, max_length=16_384)
    scripted: bool = False


class AnswerRun(FrozenRunContract):
    kind: Literal["answer"] = "answer"
    value: str = Field(min_length=1, max_length=16_384)
    response_kind: Literal["text", "action", "option"] = "text"
    action_id: Literal["accept_suggestion"] | None = None
    option_id: Literal["zh", "en"] | None = None

    @model_validator(mode="after")
    def validate_response_shape(self) -> AnswerRun:
        if self.response_kind == "action":
            if self.action_id is None or self.option_id is not None or self.value != self.action_id:
                raise ValueError("action_answer_requires_matching_action_id")
        elif self.response_kind == "option":
            if self.option_id is None or self.action_id is not None or self.value != self.option_id:
                raise ValueError("option_answer_requires_matching_option_id")
        elif self.action_id is not None or self.option_id is not None:
            raise ValueError("text_answer_cannot_include_action_id")
        return self


class SelectControlRun(FrozenRunContract):
    """Adapter-facing selection of a current runtime-projected visible control."""

    kind: Literal["select_control"] = "select_control"
    control_id: Literal["accept_current_proposal"]


class CancelRun(FrozenRunContract):
    kind: Literal["cancel"] = "cancel"


class StatusRun(FrozenRunContract):
    kind: Literal["status"] = "status"


class RefineRun(FrozenRunContract):
    kind: Literal["refine"] = "refine"
    text: str = Field(min_length=1, max_length=4_096)


type RunIntent = StartRun | AnswerRun | SelectControlRun | CancelRun | StatusRun | RefineRun


class RunSnapshot(FrozenRunContract):
    bundle_id: str | None = Field(default=None, pattern=r"^b_[A-Za-z0-9_-]{43}$")
    durability: Literal["same_process", "restart_durable", "unavailable"] = "unavailable"
    lifecycle_phase: LogicalPhaseName | None = None
    completed_trace: tuple[RunTraceEntry, ...] = ()
    pending_input: PendingInputProjection | None = None
    elapsed_seconds: float = Field(default=0.0, ge=0.0, le=86_400.0)
    delivery_mode: Literal["returned_only"] = "returned_only"
    observation: RunObservationView | None = None


class PromptOption(FrozenRunContract):
    id: Literal["zh", "en", "proceed", "rerun", "repair", "revise_view", "stop"]
    label: str = Field(min_length=1, max_length=128)
    consequence: str = Field(min_length=1, max_length=256)


class PromptView(FrozenRunContract):
    phase: Literal["hitl1", "hitl2"]
    request_id: str = Field(min_length=1, max_length=128)
    mode: Literal["text", "choice"]
    heading: str = Field(min_length=1, max_length=256)
    goal: str = Field(min_length=1, max_length=768)
    proposed_scope: tuple[str, ...] = Field(default=(), max_length=17)
    missing_fields: tuple[str, ...] = Field(default=(), max_length=8)
    supported_values: tuple[str, ...] = Field(default=(), max_length=12)
    interaction: InteractionProjection | None = None
    visible_controls: tuple[VisibleControl, ...] = Field(default=(), max_length=4)
    recognized_fields: tuple[str, ...] = Field(default=(), max_length=8)
    rejection_category: Literal["profile_input_unrecognized", "choice_input_invalid"] | None = None
    accepted_rounds_remaining: int = Field(default=0, ge=0, le=3)
    rejection_retries_remaining: int = Field(default=0, ge=0, le=3)
    body_lines: tuple[str, ...] = Field(default=(), max_length=8)
    answer_example: str = Field(default="", max_length=512)
    options: tuple[PromptOption, ...] = ()

    @model_validator(mode="after")
    def interaction_controls_match(self) -> PromptView:
        if self.interaction is None:
            if self.visible_controls:
                raise ValueError("visible_controls_require_interaction")
        elif self.visible_controls != self.interaction.controls:
            raise ValueError("visible_controls_interaction_mismatch")
        return self


class RunFailure(FrozenRunContract):
    code: RunFailureCode
    phase: LogicalPhaseName | None = None
    certainty: FailureCertainty
    message: str = Field(min_length=1, max_length=512)
    next_action: str = Field(min_length=1, max_length=512)
    retryable: bool
    diagnostic_ref: str | None = Field(default=None, pattern=r"^diag_[A-Za-z0-9_-]{8,64}$")
    observation_record_created: bool = False
    worker_failure_category: (
        Literal["agent_invocation", "tool_execution", "structured_output", "submission_validation", "unknown", "mixed"]
        | None
    ) = None
    provider_recovery: ProviderRecoveryProjection | None = None
    provider_observation: ProviderObservation | None = None
    recovery_action: Literal["fresh_start"] | None = None
    diagnostic_location: Literal["observation_store", "support_journal", "unavailable"] | None = None

    @model_validator(mode="after")
    def validate_provider_diagnostic_projection(self) -> RunFailure:
        _validate_final_provider_observation(code=self.code, observation=self.provider_observation)
        provider_diagnostic = self.provider_recovery is not None or self.provider_observation is not None
        if provider_diagnostic:
            if self.diagnostic_ref is None or self.diagnostic_location is None:
                raise ValueError("provider_diagnostic_location_required")
            if self.observation_record_created != (self.diagnostic_location == "observation_store"):
                raise ValueError("provider_diagnostic_record_truth_invalid")
        elif self.diagnostic_location is not None:
            raise ValueError("legacy_failure_diagnostic_location_invalid")
        if self.provider_recovery is not None:
            disposition = self.provider_recovery.disposition
            if disposition == "retry_followed_by_terminal_failure" and self.code in {
                RunFailureCode.PROVIDER_TIMEOUT,
                RunFailureCode.PROVIDER_UNAVAILABLE,
            }:
                raise ValueError("provider_recovery_followed_final_category_invalid")
            legal_fresh_start = disposition in {"exhausted", "retry_not_started_budget_consumed"} and self.code in {
                RunFailureCode.PROVIDER_TIMEOUT,
                RunFailureCode.PROVIDER_UNAVAILABLE,
            }
        else:
            legal_fresh_start = False
        if self.recovery_action == "fresh_start":
            if not legal_fresh_start or not self.retryable or self.next_action != FRESH_START_NEXT_ACTION:
                raise ValueError("fresh_start_recovery_action_invalid")
        elif legal_fresh_start:
            raise ValueError("fresh_start_recovery_action_required")
        return self


class ReadinessCheck(FrozenRunContract):
    name: Literal["mode", "model", "web_tool", "environment"]
    ready: bool
    detail: str = Field(min_length=1, max_length=256)
    next_action: str = Field(default="", max_length=256)


class ReadinessReport(FrozenRunContract):
    mode: RunMode
    ready: bool
    summary: str = Field(min_length=1, max_length=512)
    checks: tuple[ReadinessCheck, ...] = Field(default=(), max_length=4)
    failure: RunFailure | None = None
    durability_note: str = Field(min_length=1, max_length=256)


class Ready(FrozenRunContract):
    kind: Literal["ready"] = "ready"
    report: ReadinessReport


class Working(FrozenRunContract):
    kind: Literal["working"] = "working"
    snapshot: RunSnapshot
    action: Literal["start", "resume", "status", "cancel", "refine"]
    message: str = Field(min_length=1, max_length=256)


class AwaitingInput(FrozenRunContract):
    kind: Literal["awaiting_input"] = "awaiting_input"
    snapshot: RunSnapshot
    prompt: PromptView
    trace_delta: tuple[RunTraceEntry, ...] = ()


class Terminal(FrozenRunContract):
    kind: Literal["terminal"] = "terminal"
    snapshot: RunSnapshot
    outcome: Literal["completed", "stopped", "cancelled", "blocked"]
    trace_delta: tuple[RunTraceEntry, ...] = ()
    trace_verified: bool = True
    failure: RunFailure | None = None


class Fault(FrozenRunContract):
    kind: Literal["fault"] = "fault"
    snapshot: RunSnapshot | None = None
    failure: RunFailure


type RunUpdate = Ready | Working | AwaitingInput | Terminal | Fault


__all__ = [
    "AnswerRun",
    "AwaitingInput",
    "CancelRun",
    "FailureCertainty",
    "FRESH_START_NEXT_ACTION",
    "Fault",
    "LogicalPhaseName",
    "NodeProblem",
    "PendingInputProjection",
    "ProviderObservation",
    "ProviderRecoveryProjection",
    "PromptOption",
    "PromptView",
    "ReadinessCheck",
    "ReadinessReport",
    "Ready",
    "RefineRun",
    "RunFailure",
    "RunFailureCode",
    "RunIntent",
    "RunMode",
    "RunSnapshot",
    "RunTraceEntry",
    "SelectControlRun",
    "RunUpdate",
    "StartRun",
    "StatusRun",
    "Terminal",
    "TerminalIncidentProjection",
    "Working",
]
