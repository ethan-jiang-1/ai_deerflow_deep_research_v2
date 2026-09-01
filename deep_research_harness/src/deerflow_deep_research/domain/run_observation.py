"""Bounded, Bundle-local execution observations.

Run Event Journal records live only in an admitted Run Bundle's diagnostics subtree.
They never establish Bundle existence, scope, lifecycle state, or a control target. The
Bundle lifecycle boundary remains the sole owner of those facts.

@impl DRH-001
@impl REJ-001
@impl REJ-002
@impl DRH-006
@impl REJ-004
@impl REJ-010
@impl REG-014
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from deerflow_deep_research.domain.identifiers import BUNDLE_ID_PATTERN as _BUNDLE_ID_PATTERN
from deerflow_deep_research.domain.identifiers import LOGICAL_PHASE_NAMES

MAX_TRACE_RECORD_BYTES = 8 * 1024
MAX_TRACE_SNAPSHOT_BYTES = 2 * 1024 * 1024
MAX_TRACE_RECORDS = 256
MAX_LIFECYCLE_SEQUENCE = 2**31 - 1
MAX_LIST_ENTRIES = 20
MAX_SKIPPED_ENTRIES = 20
MAX_EVENT_RECORDS = 256
_RECOVERY_IDENTIFIER_PATTERN = r"^[A-Za-z0-9_-]{8,64}$"
_VALIDATION_CODE_PATTERN = r"^[a-z][a-z0-9]*(?:[._][a-z][a-z0-9]*)*$"
_TRANSIENT_PROVIDER_CATEGORIES = frozenset({"provider.timeout", "provider.unavailable"})
ProviderTimeoutOrigin = Literal["bridge_wall_time_budget", "provider_sdk_timeout"]


class FrozenRunObservationContract(BaseModel):
    """Closed serializable observation contract with no runtime authority."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class ExecutionProfileEvidence(FrozenRunObservationContract):
    """Safe profile provenance carried only by trusted runtime composition."""

    profile_id: str = Field(min_length=1, max_length=64, pattern=r"^[a-z][a-z0-9-]*$")
    registry_revision: str = Field(min_length=2, max_length=16, pattern=r"^v[1-9][0-9]*$")


class UsageTokensEvidence(FrozenRunObservationContract):
    """Provider usage counts of one completed model invocation (BUG-048 item 4).

    Closed non-negative integers only; absence on an event means the provider
    reported no usage and is never itself a failure.
    """

    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_totals(self) -> UsageTokensEvidence:
        if self.total_tokens != self.input_tokens + self.output_tokens:
            raise ValueError("usage_tokens_total_inconsistent")
        return self


class PolicyEnvelopeEvidence(FrozenRunObservationContract):
    """One phase's assembled execution-policy envelope (BUG-048 item 2).

    Read-only run summary provenance: it answers "what budget did this run give
    this phase" without source reading. It carries no prompt text, capability
    bodies, or credentials, and is never admission or routing authority.
    """

    phase: str = Field(min_length=1, max_length=32, pattern=r"^[a-z][a-z0-9_]*$")
    policy_name: str = Field(min_length=1, max_length=64, pattern=r"^[a-z][a-z0-9-]*$")
    total_token_budget: int = Field(ge=1)
    per_call_output_token_cap: int = Field(ge=1)
    max_model_calls: int = Field(ge=1)


class ObservationInspectability(StrEnum):
    """Availability of an external observation, never of its Run Bundle."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    NOT_FOUND = "not_found"
    INVALID_REFERENCE = "invalid_reference"


class RetentionState(StrEnum):
    RETAINED = "retained"
    ELIGIBLE_FOR_CLEANUP = "eligible_for_cleanup"


class ObservationCategory(StrEnum):
    PERSISTENCE_UNAVAILABLE = "persistence.unavailable"
    RECORD_INVALID = "record.invalid"


class JournalAvailability(StrEnum):
    UNAVAILABLE = "unavailable"
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


class JournalIncompleteReason(StrEnum):
    """Closed safe reasons a readable Journal cannot claim completeness."""

    LEGACY = "legacy"
    CAPACITY = "capacity"
    PERSISTENCE = "persistence"
    SEQUENCE_GAP = "sequence_gap"


class RunEventCategory(StrEnum):
    ADMISSION = "admission"
    LIFECYCLE = "lifecycle"
    NODE = "node"
    ATTEMPT = "attempt"
    MODEL_TOOL = "model_tool"
    VALIDATION = "validation"
    SUBMIT = "submit"
    RETRY = "retry"
    EXHAUSTION = "exhaustion"
    TERMINAL = "terminal"


class BudgetStopReason(StrEnum):
    """Closed diagnostic attribution for a stopped model/tool invocation."""

    REQUEST_CONTENT_UNESTIMABLE = "request_content_unestimable"
    MODEL_CALL_LIMIT = "model_call_limit"
    TOKEN_ADMISSION = "token_admission"
    PER_CALL_OUTPUT_CAP = "per_call_output_cap"
    TOTAL_TOKEN_BUDGET = "total_token_budget"
    TOOL_CALLS_PER_RESPONSE = "tool_calls_per_response"
    PARALLEL_TOOL_CALLS = "parallel_tool_calls"
    TOTAL_TOOL_CALLS = "total_tool_calls"
    BRIDGE_WALL_TIME = "bridge_wall_time"
    UNKNOWN = "unknown"


class FinalResponseShape(StrEnum):
    """Closed structural classification for unretained worker response text."""

    EMPTY = "empty"
    PROSE = "prose"
    FENCED = "fenced"
    EMBEDDED_JSON = "embedded_json"
    JSON_OBJECT = "json_object"


def classify_final_response_shape(response: str) -> FinalResponseShape:
    """Classify a response without extracting or retaining any of its content."""

    stripped = response.strip()
    if not stripped:
        return FinalResponseShape.EMPTY
    if "```" in response:
        return FinalResponseShape.FENCED
    try:
        if isinstance(json.loads(stripped), dict):
            return FinalResponseShape.JSON_OBJECT
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for index, character in enumerate(stripped):
        if character != "{":
            continue
        try:
            value, _ = decoder.raw_decode(stripped[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return FinalResponseShape.EMBEDDED_JSON
    return FinalResponseShape.PROSE


class RetainedRecoverySummary(FrozenRunObservationContract):
    """Read-only terminal recovery observation with no control effect."""

    trigger_category: Literal["provider.timeout", "provider.unavailable"]
    trigger_invocation_ordinal: int = Field(ge=1, le=2)
    model_attempts: int = Field(ge=1, le=2)
    automatic_retries: int = Field(ge=0, le=1)
    disposition: Literal[
        "exhausted",
        "retry_followed_by_terminal_failure",
        "retry_not_started_budget_consumed",
    ]

    @model_validator(mode="after")
    def validate_recovery_tuple(self) -> RetainedRecoverySummary:
        expected = {
            "exhausted": (1, 2, 1),
            "retry_followed_by_terminal_failure": (1, 2, 1),
            "retry_not_started_budget_consumed": (2, 2, 0),
        }[self.disposition]
        if (self.trigger_invocation_ordinal, self.model_attempts, self.automatic_retries) != expected:
            raise ValueError("retained_recovery_tuple_invalid")
        return self


class RunEvent(FrozenRunObservationContract):
    """One redacted historical event, never a raw log or lifecycle cursor."""

    schema_version: Literal[1, 2, 3] = 1
    sequence: int = Field(ge=1, le=MAX_LIFECYCLE_SEQUENCE)
    timestamp: datetime
    category: RunEventCategory
    generation: int | None = Field(default=None, ge=0, le=2)
    phase: str = Field(min_length=1, max_length=32, pattern=r"^[a-z][a-z0-9_]*$")
    outcome: Literal["started", "completed", "failed", "suspended"] | None = None
    work_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9:_-]{1,128}$")
    attempt_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9:_-]{1,128}$")
    validation_code: str | None = Field(default=None, pattern=_VALIDATION_CODE_PATTERN)
    validation_stage: Literal["initial", "repair", "post_candidate"] | None = None
    validation_codes: tuple[str, ...] = Field(default=(), max_length=MAX_LIST_ENTRIES)
    critic_kind: Literal["source_diagnostic", "claim_verifier"] | None = None
    response_shape: FinalResponseShape | None = None
    failure_category: str | None = Field(default=None, pattern=_VALIDATION_CODE_PATTERN)
    worker_failure_category: (
        Literal["agent_invocation", "tool_execution", "structured_output", "submission_validation", "unknown", "mixed"]
        | None
    ) = None
    retry_count: int | None = Field(default=None, ge=0, le=16)
    diagnostic_ref: str | None = Field(default=None, pattern=r"^diag_[A-Za-z0-9_-]{8,64}$")
    recovery_correlation_id: str | None = Field(default=None, pattern=_RECOVERY_IDENTIFIER_PATTERN)
    provider_category: Literal["provider.timeout", "provider.unavailable", "provider.authentication_failed"] | None = (
        None
    )
    retry_ordinal: int | None = Field(default=None, ge=1, le=1)
    backoff_milliseconds: int | None = Field(default=None, ge=1, le=60_000)
    recovery_event_disposition: Literal["scheduled", "exhausted"] | None = None
    execution_profile: ExecutionProfileEvidence | None = None
    budget_stop_reason: BudgetStopReason | None = None
    call_ordinal: int | None = Field(default=None, ge=1, le=64)
    usage_tokens: UsageTokensEvidence | None = None
    budget_operands: dict[str, int] | None = Field(default=None)
    readiness_route: Literal["pass", "repair_targeted", "exhausted"] | None = None
    readiness_blocked_count: int | None = Field(default=None, ge=0, le=16)
    readiness_pass_guard: Literal["wave2_degraded", "no_declared_gap_work", "fallback_projection"] | None = None
    readiness_failure_codes: tuple[
        Literal[
            "citation_no_accepted_evidence",
            "provenance_invalid_ref",
            "synthesis_evidence_unavailable",
            "synthesis_findings_unavailable",
            "readiness_plan_persistence_unavailable",
        ],
        ...,
    ] = Field(default=(), max_length=8)
    targeted_evidence_reason: Literal["drained_no_op"] | None = None
    targeted_gap_count: Literal[0] | None = None

    @field_validator("budget_operands")
    @classmethod
    def validate_budget_operands(cls, operands: dict[str, int] | None) -> dict[str, int] | None:
        if operands is None:
            return None
        if not operands or len(operands) > 4:
            raise ValueError("journal_budget_operands_invalid")
        for key, value in operands.items():
            if not re.fullmatch(r"[a-z][a-z0-9_]{0,31}", key) or value < 0:
                raise ValueError("journal_budget_operands_invalid")
        return dict(operands)

    @model_validator(mode="after")
    def validate_recovery_event(self) -> RunEvent:
        if self.schema_version in (2, 3) and self.generation is None:
            raise ValueError("journal_event_generation_required")
        if any(re.fullmatch(_VALIDATION_CODE_PATTERN, code) is None for code in self.validation_codes):
            raise ValueError("journal_validation_code_invalid")
        if len(set(self.validation_codes)) != len(self.validation_codes):
            raise ValueError("journal_validation_codes_duplicate")
        if self.schema_version in (2, 3) and self.validation_code is not None:
            raise ValueError("journal_validation_code_legacy_forbidden")
        if self.category is RunEventCategory.VALIDATION:
            if self.schema_version in (2, 3) and self.validation_stage is None:
                raise ValueError("journal_validation_stage_required")
            if self.schema_version == 3 and self.validation_stage == "post_candidate":
                if self.response_shape is not None:
                    raise ValueError("journal_post_candidate_response_shape_unexpected")
                if not self.validation_codes:
                    raise ValueError("journal_post_candidate_codes_required")
            elif self.schema_version == 3 and self.validation_stage in {"initial", "repair"}:
                if self.phase in {"wave0", "wave1"} and self.response_shape is None:
                    raise ValueError("journal_validation_response_shape_required")
                if self.phase not in {"wave0", "wave1"} and self.response_shape is not None:
                    raise ValueError("journal_validation_response_shape_unexpected")
            elif self.response_shape is not None:
                raise ValueError("journal_validation_response_shape_unexpected")
        elif self.response_shape is not None:
            raise ValueError("journal_validation_response_shape_unexpected")
        elif self.validation_stage is not None or self.validation_codes:
            raise ValueError("journal_validation_fields_unexpected")
        if self.critic_kind is not None:
            if (
                self.category is not RunEventCategory.VALIDATION
                or self.schema_version != 3
                or self.phase != "wave1"
                or self.validation_stage != "post_candidate"
            ):
                raise ValueError("journal_critic_kind_unexpected")
        if self.execution_profile is not None and self.category is not RunEventCategory.ADMISSION:
            raise ValueError("journal_execution_profile_unexpected")
        if self.budget_stop_reason is not None:
            if self.category is not RunEventCategory.MODEL_TOOL or self.outcome != "failed":
                raise ValueError("journal_budget_stop_reason_unexpected")
            if self.budget_stop_reason is BudgetStopReason.BRIDGE_WALL_TIME:
                if self.failure_category != "provider.timeout":
                    raise ValueError("journal_budget_stop_reason_failure_mismatch")
            elif self.failure_category != "budget.exhausted":
                raise ValueError("journal_budget_stop_reason_failure_mismatch")
        if self.usage_tokens is not None and (
            self.category is not RunEventCategory.MODEL_TOOL or self.outcome != "completed"
        ):
            raise ValueError("journal_usage_tokens_unexpected")
        if self.budget_operands is not None and self.budget_stop_reason is None:
            raise ValueError("journal_budget_operands_unexpected")
        readiness_attribution_present = any(
            value is not None
            for value in (self.readiness_route, self.readiness_blocked_count, self.readiness_pass_guard)
        ) or bool(self.readiness_failure_codes)
        if self.readiness_route is None:
            if readiness_attribution_present:
                raise ValueError("journal_readiness_attribution_incomplete")
        else:
            if self.category is not RunEventCategory.NODE or self.phase != "readiness":
                raise ValueError("journal_readiness_attribution_unexpected")
            if self.readiness_blocked_count is None:
                raise ValueError("journal_readiness_blocked_count_required")
            if self.readiness_pass_guard is not None and self.readiness_route != "pass":
                raise ValueError("journal_readiness_pass_guard_unexpected")
            if self.readiness_route == "exhausted":
                if not self.readiness_failure_codes:
                    raise ValueError("journal_readiness_failure_codes_required")
            elif self.readiness_failure_codes:
                raise ValueError("journal_readiness_failure_codes_unexpected")
        targeted_attribution_present = self.targeted_evidence_reason is not None or self.targeted_gap_count is not None
        if targeted_attribution_present:
            if (
                self.category is not RunEventCategory.NODE
                or self.phase != "targeted_evidence"
                or self.targeted_evidence_reason != "drained_no_op"
                or self.targeted_gap_count != 0
            ):
                raise ValueError("journal_targeted_no_op_attribution_invalid")
        recovery_control_fields_present = any(
            value is not None
            for value in (
                self.recovery_correlation_id,
                self.retry_ordinal,
                self.backoff_milliseconds,
                self.recovery_event_disposition,
            )
        )
        if self.category is RunEventCategory.MODEL_TOOL:
            if recovery_control_fields_present:
                raise ValueError("model_tool_recovery_fields_unexpected")
            return self
        if not recovery_control_fields_present:
            if self.provider_category is not None:
                raise ValueError("provider_category_unexpected")
            return self
        if self.recovery_correlation_id is None:
            raise ValueError("recovery_event_correlation_required")
        if self.diagnostic_ref is not None:
            raise ValueError("preterminal_recovery_event_cannot_carry_diagnostic_ref")
        if self.category is RunEventCategory.ATTEMPT:
            if self.attempt_id is None or re.fullmatch(_RECOVERY_IDENTIFIER_PATTERN, self.attempt_id) is None:
                raise ValueError("recovery_attempt_id_invalid")
            if any(
                value is not None
                for value in (self.retry_ordinal, self.backoff_milliseconds, self.recovery_event_disposition)
            ):
                raise ValueError("recovery_attempt_pairing_invalid")
            return self
        if self.category is RunEventCategory.RETRY:
            if (
                self.retry_ordinal != 1
                or self.backoff_milliseconds != 1_000
                or self.recovery_event_disposition != "scheduled"
                or self.provider_category is not None
                or self.attempt_id is not None
            ):
                raise ValueError("scheduled_recovery_event_invalid")
            return self
        if self.category is RunEventCategory.EXHAUSTION:
            if (
                self.retry_ordinal != 1
                or self.recovery_event_disposition != "exhausted"
                or self.provider_category not in _TRANSIENT_PROVIDER_CATEGORIES
                or self.backoff_milliseconds is not None
                or self.attempt_id is not None
            ):
                raise ValueError("exhausted_recovery_event_invalid")
            return self
        raise ValueError("recovery_event_category_invalid")


def derive_diagnostic_reference(
    *,
    bundle_id: str,
    generation: int,
    phase: str,
    category: str,
    correlation_id: str,
) -> str:
    """Derive one opaque diagnostic reference from bounded observation facts."""

    safe_fields = "|".join((bundle_id, str(generation), phase, category, correlation_id))
    return "diag_" + hashlib.sha256(safe_fields.encode("utf-8")).hexdigest()[:24]


class RunSummary(FrozenRunObservationContract):
    schema_version: Literal[1, 2] = 1
    bundle_id: str = Field(pattern=_BUNDLE_ID_PATTERN)
    status: Literal["active", "suspended", "completed", "stopped", "cancelled", "blocked"]
    phase: str = Field(min_length=1, max_length=32, pattern=r"^[a-z][a-z0-9_]*$")
    generation: int = Field(ge=0, le=2)
    updated_at: datetime
    durability: Literal["same_process", "restart_durable", "unavailable"]
    terminal_outcome: Literal["completed", "stopped", "cancelled", "blocked"] | None = None
    failure_category: str | None = Field(default=None, pattern=r"^[a-z]+(?:[._][a-z]+)*$")
    worker_failure_category: (
        Literal["agent_invocation", "tool_execution", "structured_output", "submission_validation", "unknown", "mixed"]
        | None
    ) = None
    diagnostic_ref: str | None = Field(default=None, pattern=r"^diag_[A-Za-z0-9_-]{8,64}$")
    journal_availability: JournalAvailability
    latest_event_sequence: int | None = Field(default=None, ge=1, le=MAX_LIFECYCLE_SEQUENCE)
    dropped_event_count: int = Field(default=0, ge=0, le=MAX_LIFECYCLE_SEQUENCE)
    first_dropped_sequence: int | None = Field(default=None, ge=1, le=MAX_LIFECYCLE_SEQUENCE)
    last_dropped_sequence: int | None = Field(default=None, ge=1, le=MAX_LIFECYCLE_SEQUENCE)
    retained_recovery_summary: RetainedRecoverySummary | None = None
    execution_profile: ExecutionProfileEvidence | None = None
    policy_envelopes: tuple[PolicyEnvelopeEvidence, ...] = Field(default=(), max_length=32)

    @model_validator(mode="after")
    def validate_policy_envelopes(self) -> RunSummary:
        phases = [envelope.phase for envelope in self.policy_envelopes]
        if len(set(phases)) != len(phases):
            raise ValueError("run_summary_policy_envelope_phases_duplicate")
        return self

    @model_validator(mode="after")
    def validate_journal_loss(self) -> RunSummary:
        has_interval = self.first_dropped_sequence is not None or self.last_dropped_sequence is not None
        if self.dropped_event_count == 0:
            if has_interval:
                raise ValueError("journal_drop_interval_without_drop")
            return self
        if self.journal_availability is JournalAvailability.COMPLETE:
            raise ValueError("complete_journal_cannot_have_dropped_events")
        if self.first_dropped_sequence is None or self.last_dropped_sequence is None:
            raise ValueError("journal_drop_interval_required")
        if self.first_dropped_sequence > self.last_dropped_sequence:
            raise ValueError("journal_drop_interval_invalid")
        return self


class RecordBearingLifecycleFact(FrozenRunObservationContract):
    """Validated values sufficient to publish a bounded historical observation."""

    bundle_id: str = Field(pattern=_BUNDLE_ID_PATTERN)
    action: Literal["start", "resume", "status", "cancel", "refine"]
    status: Literal["active", "suspended", "completed", "stopped", "cancelled", "blocked"]
    phase: Literal[*LOGICAL_PHASE_NAMES]
    generation: int = Field(ge=0, le=2)
    durability: Literal["same_process", "restart_durable", "unavailable"]
    trace_delta: tuple[str, ...] = Field(default=(), max_length=32)
    pending_phase: Literal["hitl1", "hitl2"] | None = None
    pending_mode: Literal["text", "choice"] | None = None
    pending_request_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{1,128}$")
    terminal_outcome: Literal["completed", "stopped", "cancelled", "blocked"] | None = None
    failure_category: str | None = Field(default=None, pattern=r"^[a-z]+(?:[._][a-z]+)*$")
    worker_failure_category: (
        Literal["agent_invocation", "tool_execution", "structured_output", "submission_validation", "unknown", "mixed"]
        | None
    ) = None
    diagnostic_ref: str | None = Field(default=None, pattern=r"^diag_[A-Za-z0-9_-]{8,64}$")
    retained_recovery_summary: RetainedRecoverySummary | None = None
    recovery_trigger_timeout_origin: ProviderTimeoutOrigin | None = None
    final_timeout_origin: ProviderTimeoutOrigin | None = None

    @model_validator(mode="after")
    def validate_terminal_correlation(self) -> RecordBearingLifecycleFact:
        if self.retained_recovery_summary is not None:
            if self.terminal_outcome != "blocked" or self.diagnostic_ref is None:
                raise ValueError("retained_recovery_summary_requires_terminal_reference")
        if self.diagnostic_ref is not None:
            if self.terminal_outcome is None:
                raise ValueError("terminal_diagnostic_ref_requires_terminal")
            if self.failure_category is None:
                raise ValueError("terminal_diagnostic_ref_requires_failure_category")
        return self


class RetainedDiagnosticRecord(FrozenRunObservationContract):
    """One frozen, bounded terminal diagnosis record."""

    schema_version: Literal[1] = 1
    reference: str = Field(pattern=r"^diag_[A-Za-z0-9_-]{8,64}$")
    time: datetime
    action: Literal["start", "resume", "status", "cancel", "refine"]
    phase: str = Field(min_length=1, max_length=32, pattern=r"^[a-z][a-z0-9_]*$")
    category: str = Field(pattern=r"^[a-z]+(?:[._][a-z]+)*$")
    recovery_trigger_timeout_origin: ProviderTimeoutOrigin | None = None
    final_timeout_origin: ProviderTimeoutOrigin | None = None


class RunObservationManifest(FrozenRunObservationContract):
    """Metadata for one Bundle-local Journal, never a Run locator."""

    schema_version: Literal[1, 2, 3] = 1
    bundle_id: str = Field(pattern=_BUNDLE_ID_PATTERN)
    created_at: datetime
    updated_at: datetime
    retention_state: RetentionState
    durability: Literal["same_process", "restart_durable", "unavailable"]
    lifecycle_path: Literal["diagnostics/lifecycle.jsonl"] = "diagnostics/lifecycle.jsonl"
    diagnostic_path: Literal["diagnostics/records.jsonl"] | None = None
    summary_path: Literal["run-summary.json"] | None = None
    events_path: Literal["diagnostics/events.jsonl"] | None = None
    event_high_watermark: int | None = Field(default=None, ge=0, le=MAX_LIFECYCLE_SEQUENCE)
    dropped_event_count: int = Field(default=0, ge=0, le=MAX_LIFECYCLE_SEQUENCE)
    first_dropped_sequence: int | None = Field(default=None, ge=1, le=MAX_LIFECYCLE_SEQUENCE)
    last_dropped_sequence: int | None = Field(default=None, ge=1, le=MAX_LIFECYCLE_SEQUENCE)
    persistence_failure_count: int = Field(default=0, ge=0, le=MAX_LIFECYCLE_SEQUENCE)

    @model_validator(mode="after")
    def validate_journal_metadata(self) -> RunObservationManifest:
        has_interval = self.first_dropped_sequence is not None or self.last_dropped_sequence is not None
        if self.dropped_event_count == 0:
            if has_interval:
                raise ValueError("journal_manifest_drop_interval_without_drop")
        elif self.first_dropped_sequence is None or self.last_dropped_sequence is None:
            raise ValueError("journal_manifest_drop_interval_required")
        elif self.first_dropped_sequence > self.last_dropped_sequence:
            raise ValueError("journal_manifest_drop_interval_invalid")
        if self.schema_version in (2, 3) and self.event_high_watermark is None:
            raise ValueError("journal_high_watermark_required")
        return self


class LifecycleTraceRecord(FrozenRunObservationContract):
    schema_version: Literal[1] = 1
    sequence: int = Field(ge=1, le=MAX_LIFECYCLE_SEQUENCE)
    timestamp: datetime
    action: Literal["start", "resume", "status", "cancel", "refine"]
    phase: str = Field(min_length=1, max_length=32)
    status: Literal["active", "suspended", "completed", "stopped", "cancelled", "blocked"]
    generation: int = Field(ge=0, le=2)
    trace_delta: tuple[str, ...] = Field(default=(), max_length=32)
    pending_phase: Literal["hitl1", "hitl2"] | None = None
    pending_mode: Literal["text", "choice"] | None = None
    pending_request_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{1,128}$")
    terminal_outcome: Literal["completed", "stopped", "cancelled", "blocked"] | None = None
    failure_category: str | None = Field(default=None, pattern=r"^[a-z]+(?:[._][a-z]+)*$")
    worker_failure_category: (
        Literal["agent_invocation", "tool_execution", "structured_output", "submission_validation", "unknown", "mixed"]
        | None
    ) = None
    diagnostic_ref: str | None = Field(default=None, pattern=r"^diag_[A-Za-z0-9_-]{8,64}$")
    retained_recovery_summary: RetainedRecoverySummary | None = None

    @model_validator(mode="after")
    def validate_terminal_correlation(self) -> LifecycleTraceRecord:
        if self.retained_recovery_summary is not None and self.terminal_outcome is None:
            raise ValueError("retained_recovery_summary_requires_terminal")
        return self


class RunObservationView(FrozenRunObservationContract):
    bundle_id: str = Field(pattern=_BUNDLE_ID_PATTERN)
    inspectability: ObservationInspectability
    retention_state: RetentionState | None = None
    durability: Literal["same_process", "restart_durable", "unavailable"]
    observation_category: ObservationCategory | None = None
    terminal_diagnostic_ref: str | None = Field(default=None, pattern=r"^diag_[A-Za-z0-9_-]{8,64}$")


class TerminalDiagnosticProjection(FrozenRunObservationContract):
    """Strictly verified safe subset of one retained terminal diagnosis."""

    reference: str = Field(pattern=r"^diag_[A-Za-z0-9_-]{8,64}$")
    category: str = Field(pattern=r"^[a-z]+(?:[._][a-z]+)*$")
    phase: str = Field(min_length=1, max_length=32, pattern=r"^[a-z][a-z0-9_]*$")
    recovery_trigger_timeout_origin: ProviderTimeoutOrigin | None = None
    final_timeout_origin: ProviderTimeoutOrigin | None = None


class RunObservationInspection(FrozenRunObservationContract):
    bundle_id: str | None = Field(default=None, pattern=_BUNDLE_ID_PATTERN)
    inspectability: ObservationInspectability
    retention_state: RetentionState | None = None
    durability: Literal["same_process", "restart_durable", "unavailable"] | None = None
    summary: RunSummary | None = None
    events: tuple[RunEvent, ...] = Field(default=(), max_length=MAX_EVENT_RECORDS)
    journal_availability: JournalAvailability = JournalAvailability.UNAVAILABLE
    incomplete_reasons: tuple[JournalIncompleteReason, ...] = Field(default=(), max_length=4)
    observation_category: ObservationCategory | None = None
    terminal_diagnostic_ref: str | None = Field(default=None, pattern=r"^diag_[A-Za-z0-9_-]{8,64}$")
    terminal_diagnostic: TerminalDiagnosticProjection | None = None

    @model_validator(mode="after")
    def validate_incomplete_reasons(self) -> RunObservationInspection:
        if self.inspectability is not ObservationInspectability.AVAILABLE and self.incomplete_reasons:
            raise ValueError("unavailable_journal_cannot_expose_incomplete_reasons")
        if self.journal_availability is not JournalAvailability.INCOMPLETE and self.incomplete_reasons:
            raise ValueError("journal_incomplete_reasons_require_incomplete_health")
        if len(set(self.incomplete_reasons)) != len(self.incomplete_reasons):
            raise ValueError("journal_incomplete_reasons_duplicate")
        return self


__all__ = [
    "JournalAvailability",
    "JournalIncompleteReason",
    "BudgetStopReason",
    "FinalResponseShape",
    "ExecutionProfileEvidence",
    "LifecycleTraceRecord",
    "MAX_EVENT_RECORDS",
    "MAX_LIFECYCLE_SEQUENCE",
    "MAX_LIST_ENTRIES",
    "MAX_SKIPPED_ENTRIES",
    "MAX_TRACE_RECORD_BYTES",
    "MAX_TRACE_RECORDS",
    "MAX_TRACE_SNAPSHOT_BYTES",
    "ObservationCategory",
    "ObservationInspectability",
    "ProviderTimeoutOrigin",
    "RecordBearingLifecycleFact",
    "RetainedDiagnosticRecord",
    "RetainedRecoverySummary",
    "RetentionState",
    "RunEvent",
    "RunEventCategory",
    "RunObservationInspection",
    "RunObservationManifest",
    "RunObservationView",
    "RunSummary",
    "TerminalDiagnosticProjection",
    "derive_diagnostic_reference",
    "classify_final_response_shape",
]
