"""Bounded, Bundle-local execution observations.

Run Event Journal records live only in an admitted Run Bundle's diagnostics subtree.
They never establish Bundle existence, scope, lifecycle state, or a control target. The
Bundle lifecycle boundary remains the sole owner of those facts.

@impl RUS-001
@impl RUS-002
@impl RUS-004
@impl RUS-007
@impl REG-014
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

MAX_TRACE_RECORD_BYTES = 8 * 1024
MAX_TRACE_SNAPSHOT_BYTES = 2 * 1024 * 1024
MAX_TRACE_RECORDS = 256
MAX_LIFECYCLE_SEQUENCE = 2**31 - 1
MAX_LIST_ENTRIES = 20
MAX_SKIPPED_ENTRIES = 20
MAX_EVENT_RECORDS = 256
_BUNDLE_ID_PATTERN = r"^b_[A-Za-z0-9_-]{43}$"
_RECOVERY_IDENTIFIER_PATTERN = r"^[A-Za-z0-9_-]{8,64}$"
_VALIDATION_CODE_PATTERN = r"^[a-z][a-z0-9]*(?:[._][a-z][a-z0-9]*)*$"
_TRANSIENT_PROVIDER_CATEGORIES = frozenset({"provider.timeout", "provider.unavailable"})
ProviderTimeoutOrigin = Literal["bridge_wall_time_budget", "provider_sdk_timeout"]


class FrozenRunObservationContract(BaseModel):
    """Closed serializable observation contract with no runtime authority."""

    model_config = ConfigDict(frozen=True, extra="forbid")


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

    schema_version: Literal[1, 2] = 1
    sequence: int = Field(ge=1, le=MAX_LIFECYCLE_SEQUENCE)
    timestamp: datetime
    category: RunEventCategory
    generation: int | None = Field(default=None, ge=0, le=2)
    phase: str = Field(min_length=1, max_length=32, pattern=r"^[a-z][a-z0-9_]*$")
    work_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9:_-]{1,128}$")
    attempt_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9:_-]{1,128}$")
    validation_code: str | None = Field(default=None, pattern=_VALIDATION_CODE_PATTERN)
    validation_stage: Literal["initial", "repair"] | None = None
    validation_codes: tuple[str, ...] = Field(default=(), max_length=MAX_LIST_ENTRIES)
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

    @model_validator(mode="after")
    def validate_recovery_event(self) -> RunEvent:
        if self.schema_version == 2 and self.generation is None:
            raise ValueError("journal_event_generation_required")
        if any(re.fullmatch(_VALIDATION_CODE_PATTERN, code) is None for code in self.validation_codes):
            raise ValueError("journal_validation_code_invalid")
        if len(set(self.validation_codes)) != len(self.validation_codes):
            raise ValueError("journal_validation_codes_duplicate")
        if self.category is RunEventCategory.VALIDATION and self.schema_version == 2:
            if self.validation_stage is None:
                raise ValueError("journal_validation_stage_required")
            if self.validation_code is not None:
                raise ValueError("journal_validation_code_legacy_forbidden")
        elif self.validation_stage is not None or self.validation_codes:
            raise ValueError("journal_validation_fields_unexpected")
        recovery_fields_present = any(
            value is not None
            for value in (
                self.recovery_correlation_id,
                self.provider_category,
                self.retry_ordinal,
                self.backoff_milliseconds,
                self.recovery_event_disposition,
            )
        )
        if not recovery_fields_present:
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
    phase: Literal[
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

    schema_version: Literal[1, 2] = 1
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
        if self.schema_version == 2 and self.event_high_watermark is None:
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
    observation_category: ObservationCategory | None = None
    terminal_diagnostic_ref: str | None = Field(default=None, pattern=r"^diag_[A-Za-z0-9_-]{8,64}$")
    terminal_diagnostic: TerminalDiagnosticProjection | None = None


__all__ = [
    "JournalAvailability",
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
]
