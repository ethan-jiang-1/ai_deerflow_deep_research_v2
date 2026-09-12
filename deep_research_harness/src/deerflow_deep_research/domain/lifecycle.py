"""Pure lifecycle and wire contracts for Deep Research.

@impl REG-003
@impl REG-004
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from deerflow_deep_research.domain.human_interaction import InteractionProjection
from deerflow_deep_research.domain.identifiers import BUNDLE_ID_PATTERN, LogicalPhase
from deerflow_deep_research.domain.run_experience import PendingInputProjection, TerminalIncidentProjection

MAX_START_REQUEST_CHARS = 16_384
MAX_REFINEMENT_CHARS = 4_096
MAX_CONTROL_RESULT_CHARS = 4_096
MAX_RERUN_GENERATIONS = 2


class LifecycleAction(StrEnum):
    START = "start"
    RESUME = "resume"
    STATUS = "status"
    CANCEL = "cancel"
    REFINE = "refine"


class LifecycleStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    STOPPED = "stopped"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class BundleAvailability(StrEnum):
    """Whether a Bundle remains available for lifecycle control."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class LegalNextAction(StrEnum):
    """Closed next-action projection owned by the lifecycle boundary."""

    START = "start"
    RESUME = "resume"
    STATUS = "status"
    CANCEL = "cancel"
    REFINE = "refine"
    NONE = "none"


class ImplementationMode(StrEnum):
    FIXTURE = "fixture"
    MIXED = "mixed"
    ALL_REAL = "all_real"


class TerminalReason(StrEnum):
    COMPLETED = "completed"
    USER_STOPPED = "user_stopped"
    USER_CANCELLED = "user_cancelled"
    RERUN_EXHAUSTED = "rerun_exhausted"
    GATE_BLOCKED = "gate_blocked"  # @impl REG-004 — gate fatigue/budget exhaustion
    INTERNAL_BLOCKED = "internal_blocked"  # @impl REG-008 — internal invariant breach


class ResultCode(StrEnum):
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    STOPPED = "stopped"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
    STATUS_OK = "status_ok"
    START_MESSAGE_INVALID = "start_message_invalid"
    THREAD_RESEARCH_EXISTS = "thread_research_exists"
    RESPONSE_MISMATCH = "response_mismatch"
    RESPONSE_INVALID = "response_invalid"
    INVALID_TRANSITION = "invalid_transition"
    RESEARCH_NOT_FOUND = "research_not_found"
    SCHEMA_UNSUPPORTED = "schema_unsupported"
    CHECKPOINT_INCONSISTENT = "checkpoint_inconsistent"
    INTERNAL_UNEXPECTED = "internal_unexpected"
    INTERACTIVE_REQUIRED = "interactive_required"
    HUMAN_INPUT_TRANSPORT_UNAVAILABLE = "human_input_transport_unavailable"
    EXCLUSIVE_CONTROL_CALL_REQUIRED = "exclusive_control_call_required"
    IMPLEMENTATION_UNAVAILABLE = "implementation_unavailable"
    UNAVAILABLE = "unavailable"
    AMBIGUOUS = "ambiguous"
    ACTIVE_BUNDLE_EXISTS = "active_bundle_exists"
    EXPLICIT_BUNDLE_ID_REQUIRED = "explicit_bundle_id_required"
    ACTIVE = "active"
    REFINEMENT_PENDING = "refinement_pending"
    REFINEMENT_APPLIED = "refinement_applied"
    REFINEMENT_CONFLICT = "refinement_conflict"


class InfrastructureResultCode(StrEnum):
    RESTART_REQUIRED = "restart_required"
    IDENTITY_MISSING = "identity_missing"
    RUNTIME_CONTEXT_REQUIRED = "runtime_context_required"
    SANDBOX_UNAVAILABLE = "sandbox_unavailable"
    THREAD_PATH_INVALID = "thread_path_invalid"
    THREAD_PATH_ESCAPE = "thread_path_escape"
    THREAD_DATA_MISMATCH = "thread_data_mismatch"
    THREAD_MISSING = "thread_missing"
    RUN_MISSING = "run_missing"
    APP_CONFIG_MISSING = "app_config_missing"
    WORK_UNIT_STORAGE_UNAVAILABLE = "work_unit_storage_unavailable"
    WORK_UNIT_STORE_BUSY = "work_unit_store_busy"


class WorkUnitStorageReason(StrEnum):
    AIO_PROVISIONER_UNMOUNTED = "aio_provisioner_unmounted"
    E2B_UNMOUNTED = "e2b_unmounted"
    BOXLITE_UNMOUNTED = "boxlite_unmounted"
    PROVIDER_UNRECOGNIZED = "provider_unrecognized"
    THREAD_MOUNT_UNAVAILABLE = "thread_mount_unavailable"
    WORKSPACE_ALIAS_MISMATCH = "workspace_alias_mismatch"
    POSIX_PRIMITIVES_UNAVAILABLE = "posix_primitives_unavailable"
    PROBE_CLEANUP_FAILED = "probe_cleanup_failed"
    LEDGER_CORRUPT = "ledger_corrupt"
    ACCEPTED_ARTIFACT_DIVERGED = "accepted_artifact_diverged"
    LOCK_TIMEOUT = "lock_timeout"


class Durability(StrEnum):
    SAME_PROCESS = "same_process"
    RESTART_DURABLE = "restart_durable"
    UNAVAILABLE = "unavailable"


class ResponseKind(StrEnum):
    TEXT = "text"
    OPTION = "option"
    ACTION = "action"


class HumanInputMode(StrEnum):
    TEXT = "text"
    CHOICE = "choice"


class BootstrapRoute(StrEnum):
    NEEDS_INPUT = "needs_input"
    PROFILE_COMPLETE = "profile_complete"


class GateVerdict(StrEnum):
    PASS = "pass"
    REPAIR = "repair"


class SynthesisVerdict(StrEnum):
    PASS = "pass"
    EVIDENCE_NEEDED = "evidence_needed"


class Hitl2Decision(StrEnum):
    PROCEED = "proceed"
    REVISE_VIEW = "revise_view"
    REPAIR = "repair"
    RERUN = "rerun"
    STOP = "stop"


class SupportedLanguageOption(StrEnum):
    ZH = "zh"
    EN = "en"


class ReadinessVerdict(StrEnum):
    PASS = "pass"
    REPAIR_TARGETED = "repair_targeted"
    REPAIR_SYNTHESIS = "repair_synthesis"
    REPAIR_HITL2 = "repair_hitl2"


class FinalVerdict(StrEnum):
    PASS = "pass"
    REPAIR = "repair"
    EVIDENCE_BLOCKED = "evidence_blocked"


class FrozenContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class BranchResult(FrozenContract):
    branch_id: str = Field(min_length=1, max_length=64, pattern=r"^[a-z][a-z0-9_-]*$")
    verdict: GateVerdict


class AcceptedHumanResponse(FrozenContract):
    request_id: str = Field(min_length=1, max_length=128)
    message_id: str = Field(min_length=1, max_length=256)
    value: str = Field(min_length=1, max_length=MAX_START_REQUEST_CHARS)
    response_kind: ResponseKind
    option_id: str | None = Field(default=None, min_length=1, max_length=64)
    action_id: str | None = Field(default=None, min_length=1, max_length=64)

    @model_validator(mode="after")
    def validate_option_shape(self) -> AcceptedHumanResponse:
        if self.response_kind is ResponseKind.OPTION and (self.option_id is None or self.action_id is not None):
            raise ValueError("option response requires option_id")
        if self.response_kind is ResponseKind.TEXT and (self.option_id is not None or self.action_id is not None):
            raise ValueError("text response cannot include option_id")
        if self.response_kind is ResponseKind.ACTION and (self.action_id is None or self.option_id is not None):
            raise ValueError("action response requires action_id")
        return self


class RefinementInput(FrozenContract):
    """Bounded run-level direction that is distinct from a HITL response."""

    text: str = Field(min_length=1, max_length=MAX_REFINEMENT_CHARS)

    @model_validator(mode="after")
    def validate_text(self) -> RefinementInput:
        if not self.text.strip():
            raise ValueError("refinement_text_invalid")
        return self


class CurrentRoundDirection(FrozenContract):
    """Controller-owned direction projection for one graph generation.

    The Bundle lifecycle retains trusted replay details separately. Graph consumers see
    only the bounded assignment data needed for one committed refinement round.
    """

    text: str = Field(min_length=1, max_length=MAX_REFINEMENT_CHARS)
    round: int = Field(ge=1)
    generation: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_text(self) -> CurrentRoundDirection:
        if not self.text.strip():
            raise ValueError("refinement_text_invalid")
        return self


class RunRefinementSource(FrozenContract):
    """Trusted rerun input for an already-admitted direction round."""

    source: Literal["run_refinement"] = "run_refinement"
    direction: CurrentRoundDirection
    round_token: str = Field(min_length=1, max_length=256, pattern=r"^[A-Za-z0-9_-]+$")


class RefinementAdmissionDisposition(StrEnum):
    """Private reducer outcome for one trusted refinement operation."""

    PENDING = "pending"
    APPLIED = "applied"
    CONFLICT = "conflict"
    EXHAUSTED = "exhausted"


class BundleRefinementDisposition(StrEnum):
    """Public post-call refinement facts for one available Bundle."""

    NONE = "none"
    PENDING = "pending"
    APPLIED = "applied"
    APPLIED_WITH_PENDING = "applied_with_pending"


class BundleRefinementProjection(FrozenContract):
    """Redacted direction disposition derived only from Bundle-local State."""

    disposition: BundleRefinementDisposition
    current_round: int | None = Field(default=None, ge=1, le=MAX_RERUN_GENERATIONS)

    @model_validator(mode="after")
    def validate_current_round(self) -> BundleRefinementProjection:
        requires_round = {
            BundleRefinementDisposition.APPLIED,
            BundleRefinementDisposition.APPLIED_WITH_PENDING,
        }
        if self.disposition in requires_round and self.current_round is None:
            raise ValueError("applied_refinement_requires_current_round")
        if self.disposition not in requires_round and self.current_round is not None:
            raise ValueError("pending_refinement_cannot_expose_current_round")
        return self


def refinement_text_digest(text: str) -> str:
    """Return the private stable digest used to verify a trusted operation replay."""

    if not isinstance(text, str):
        raise TypeError("refinement_text_required")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def refinement_round_token(
    *,
    bundle_id: str,
    operation_key: str,
    text_digest: str,
    round: int,
    generation: int,
) -> str:
    """Derive the private, stable authorization token for one refinement round."""

    if not isinstance(bundle_id, str) or re.fullmatch(BUNDLE_ID_PATTERN, bundle_id) is None:
        raise ValueError("bundle_id_invalid")
    if not isinstance(operation_key, str) or not operation_key:
        raise ValueError("refinement_operation_key_invalid")
    if not isinstance(text_digest, str) or len(text_digest) != 64:
        raise ValueError("refinement_digest_invalid")
    if not isinstance(round, int) or not 1 <= round <= MAX_RERUN_GENERATIONS:
        raise ValueError("refinement_round_invalid")
    if not isinstance(generation, int) or not 1 <= generation <= MAX_RERUN_GENERATIONS:
        raise ValueError("generation_invalid")
    payload = json.dumps(
        ("deep-research/refinement-round/v1", bundle_id, operation_key, text_digest, round, generation),
        separators=(",", ":"),
    ).encode("utf-8")
    digest = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).decode("ascii").rstrip("=")
    return f"rt_{digest}"


class RefinementOperation(RefinementInput):
    """A trusted delivery operation plus its bounded direction text.

    ``operation_key`` is injected by a trusted runtime adapter. It is persisted only
    inside Bundle State and never belongs in a public tool argument or result.
    """

    operation_key: str = Field(min_length=1, max_length=256)
    text_digest: str = Field(pattern=r"^[a-f0-9]{64}$")

    @model_validator(mode="after")
    def validate_digest(self) -> RefinementOperation:
        if self.text_digest != refinement_text_digest(self.text):
            raise ValueError("refinement_digest_invalid")
        return self

    @classmethod
    def from_text(cls, *, operation_key: str, text: str) -> RefinementOperation:
        return cls(
            operation_key=operation_key,
            text=text,
            text_digest=refinement_text_digest(text),
        )


class CurrentRefinement(RefinementOperation):
    """One committed current-round direction retained as assignment data."""

    round: int = Field(ge=1, le=MAX_RERUN_GENERATIONS)
    generation: int = Field(ge=1, le=MAX_RERUN_GENERATIONS)
    round_token: str = Field(min_length=46, max_length=46, pattern=r"^rt_[A-Za-z0-9_-]{43}$")

    @classmethod
    def from_operation(
        cls,
        operation: RefinementOperation,
        *,
        bundle_id: str,
        round: int,
        generation: int,
    ) -> CurrentRefinement:
        return cls(
            operation_key=operation.operation_key,
            text=operation.text,
            text_digest=operation.text_digest,
            round=round,
            generation=generation,
            round_token=refinement_round_token(
                bundle_id=bundle_id,
                operation_key=operation.operation_key,
                text_digest=operation.text_digest,
                round=round,
                generation=generation,
            ),
        )


class RefinementReplayReceipt(FrozenContract):
    """No-text replay identity retained for a committed refinement round."""

    operation_key: str = Field(min_length=1, max_length=256)
    text_digest: str = Field(pattern=r"^[a-f0-9]{64}$")
    round: int = Field(ge=1, le=MAX_RERUN_GENERATIONS)
    generation: int = Field(ge=1, le=MAX_RERUN_GENERATIONS)

    @classmethod
    def from_current(cls, current: CurrentRefinement) -> RefinementReplayReceipt:
        return cls(
            operation_key=current.operation_key,
            text_digest=current.text_digest,
            round=current.round,
            generation=current.generation,
        )


class InternalCancelDecision(FrozenContract):
    kind: Literal["internal_cancel"] = "internal_cancel"


ResumeDecision = Annotated[AcceptedHumanResponse | InternalCancelDecision, Field(discriminator=None)]


class HumanInputOption(FrozenContract):
    id: Hitl2Decision | SupportedLanguageOption
    label: str = Field(min_length=1, max_length=128)
    value: Hitl2Decision | SupportedLanguageOption

    @model_validator(mode="after")
    def id_matches_value(self) -> HumanInputOption:
        if self.id is not self.value:
            raise ValueError("option id and value must match")
        return self


class HumanInputRequest(FrozenContract):
    version: Literal[1] = 1
    kind: Literal["human_input_request"] = "human_input_request"
    source: Literal["deep_research"] = "deep_research"
    request_id: str = Field(min_length=1, max_length=128)
    mode: HumanInputMode
    title: str = Field(min_length=1, max_length=256)
    context: str = Field(min_length=1, max_length=2_048)
    options: tuple[HumanInputOption, ...] = ()
    action_ids: tuple[Literal["accept_suggestion"], ...] = ()
    interaction: InteractionProjection | None = None

    @model_validator(mode="after")
    def validate_mode(self) -> HumanInputRequest:
        if self.mode is HumanInputMode.TEXT and self.options:
            raise ValueError("text input cannot define options")
        if self.mode is HumanInputMode.CHOICE and self.action_ids:
            raise ValueError("choice input cannot define actions")
        if self.interaction is not None and self.mode is not HumanInputMode.TEXT:
            raise ValueError("interaction_requires_text_input")
        if self.mode is HumanInputMode.CHOICE:
            if not self.options:
                raise ValueError("choice input requires options")
        return self


class PendingResearchInterrupt(FrozenContract):
    request: HumanInputRequest
    suspension_cursor: str = Field(min_length=1, max_length=256)
    phase: Literal["hitl1", "hitl2"]
    generation: int = Field(ge=0, le=MAX_RERUN_GENERATIONS)

    @model_validator(mode="after")
    def interaction_belongs_to_hitl1(self) -> PendingResearchInterrupt:
        if self.request.interaction is not None and self.phase != "hitl1":
            raise ValueError("interaction_requires_hitl1")
        if self.request.mode is HumanInputMode.CHOICE:
            expected = tuple(SupportedLanguageOption) if self.phase == "hitl1" else tuple(Hitl2Decision)
            if tuple(option.id for option in self.request.options) != expected:
                raise ValueError("choice input options invalid for phase")
        return self


def make_hitl_request_id(*, bundle_id: str, phase: str, generation: int, ordinal: int) -> str:
    encoded = json.dumps(
        ["deep-research/hitl/v1", bundle_id, phase, generation, ordinal],
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()
    digest = base64.urlsafe_b64encode(hashlib.sha256(encoded).digest()).decode().rstrip("=")
    return f"drh_{digest}"


def completed_visits(state: Mapping[str, Any], logical_name: str) -> int:
    return sum(1 for item in state.get("execution_trace", ()) if item == logical_name)


def make_node_visit_id(state: Mapping[str, Any], logical_name: str) -> str:
    """Node-visit attempt id: ``g{gen}-{phase}-a{n}`` (dash form).

    This is the node-visit counter carried by ``RunEvent.attempt_id`` /
    ``agent_context.attempt_id``. It is deliberately distinct from the
    work-unit attempt id produced by ``engine.work_units.ids.allocate_attempt_id``
    (``g{gen}_{phase}_w{ordinal}_a{ordinal}``, underscore form), which is the only
    form validated by ``ATTEMPT_ID_RE``. The two schemes never cross.
    """
    generation = int(state.get("generation", 0))
    return f"g{generation}-{logical_name}-a{completed_visits(state, logical_name) + 1}"


def text_only_content(content: Any, *, max_chars: int = MAX_START_REQUEST_CHARS) -> str:
    if isinstance(content, str):
        text = content
    elif isinstance(content, Sequence) and not isinstance(content, (bytes, bytearray, str)):
        pieces: list[str] = []
        for block in content:
            if not isinstance(block, Mapping) or set(block) != {"type", "text"} or block.get("type") != "text":
                raise ValueError("content_blocks_invalid")
            value = block.get("text")
            if not isinstance(value, str):
                raise ValueError("content_blocks_invalid")
            pieces.append(value)
        text = "".join(pieces)
    else:
        raise ValueError("content_invalid")
    if not text or len(text) > max_chars:
        raise ValueError("content_invalid")
    return text


class BundleControlResult(FrozenContract):
    """The sole public lifecycle projection for a selected Run Bundle.

    A result carries only the opaque public identity and facts which the runtime has
    already derived from an available Bundle-local State.  In particular it has no
    session reference, checkpoint key, trusted scope, or physical location.
    """

    schema_version: Literal[1] = 1
    implementation_mode: ImplementationMode = ImplementationMode.ALL_REAL
    action: LifecycleAction
    code: ResultCode | InfrastructureResultCode
    availability: BundleAvailability
    durability: Durability
    bundle_id: str | None = Field(default=None, pattern=BUNDLE_ID_PATTERN)
    status: LifecycleStatus | None = None
    phase: LogicalPhase | None = None
    generation: int | None = Field(default=None, ge=0, le=2)
    request_id: str | None = Field(default=None, min_length=1, max_length=128)
    pending_input: PendingInputProjection | None = None
    terminal_reason: TerminalReason | None = None
    terminal_incident: TerminalIncidentProjection | None = None
    infrastructure_reason: WorkUnitStorageReason | None = None
    refinement: BundleRefinementProjection | None = None
    legal_next_action: LegalNextAction = LegalNextAction.NONE
    execution_trace: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_bundle_lifecycle_shape(self) -> BundleControlResult:
        storage_codes = {
            InfrastructureResultCode.WORK_UNIT_STORAGE_UNAVAILABLE,
            InfrastructureResultCode.WORK_UNIT_STORE_BUSY,
        }
        if self.code in storage_codes and self.infrastructure_reason is None:
            raise ValueError("work-unit infrastructure code requires infrastructure_reason")
        if self.code not in storage_codes and self.infrastructure_reason is not None:
            raise ValueError("infrastructure_reason is forbidden for this code")
        if self.code is InfrastructureResultCode.WORK_UNIT_STORE_BUSY:
            if self.infrastructure_reason is not WorkUnitStorageReason.LOCK_TIMEOUT:
                raise ValueError("work_unit_store_busy requires lock_timeout")
        elif self.infrastructure_reason is WorkUnitStorageReason.LOCK_TIMEOUT:
            raise ValueError("lock_timeout requires work_unit_store_busy")
        if self.availability is BundleAvailability.UNAVAILABLE:
            forbidden = (
                self.bundle_id,
                self.status,
                self.phase,
                self.generation,
                self.request_id,
                self.pending_input,
                self.terminal_reason,
                self.terminal_incident,
                self.refinement,
            )
            if any(value is not None for value in forbidden) or self.execution_trace:
                raise ValueError("unavailable_result_cannot_expose_bundle_facts")
            if self.legal_next_action is not LegalNextAction.START:
                raise ValueError("unavailable_result_requires_fresh_start")
            return self
        if self.bundle_id is None:
            raise ValueError("available_result_requires_bundle_id")
        if self.refinement is None:
            raise ValueError("available_result_requires_refinement_projection")
        lifecycle_fields = (self.status, self.phase, self.generation)
        if any(value is not None for value in lifecycle_fields) and not all(
            value is not None for value in lifecycle_fields
        ):
            raise ValueError("status, phase, and generation must appear together")
        if self.status is LifecycleStatus.SUSPENDED:
            if self.request_id is None or self.pending_input is None:
                raise ValueError("suspended_result_requires_pending_input")
            if self.request_id != self.pending_input.request_id:
                raise ValueError("suspended_request_id_must_match_pending_input")
            if self.generation != self.pending_input.generation:
                raise ValueError("suspended_generation_must_match_pending_input")
        elif self.request_id is not None or self.pending_input is not None:
            raise ValueError("pending_input_requires_suspended_status")
        if self.terminal_reason is not None and self.status not in {
            LifecycleStatus.COMPLETED,
            LifecycleStatus.STOPPED,
            LifecycleStatus.CANCELLED,
            LifecycleStatus.BLOCKED,
        }:
            raise ValueError("terminal_reason_requires_terminal_status")
        if self.terminal_incident is not None and self.status is not LifecycleStatus.BLOCKED:
            raise ValueError("terminal_incident_requires_blocked_status")
        if self.refinement.current_round is not None:
            if self.generation is None or self.refinement.current_round > self.generation:
                raise ValueError("refinement_current_round_generation_mismatch")
        if self.code is ResultCode.REFINEMENT_PENDING and self.refinement.disposition not in {
            BundleRefinementDisposition.PENDING,
            BundleRefinementDisposition.APPLIED_WITH_PENDING,
        }:
            raise ValueError("refinement_pending_requires_pending_direction")
        if self.code is ResultCode.REFINEMENT_APPLIED and self.refinement.disposition not in {
            BundleRefinementDisposition.APPLIED,
            BundleRefinementDisposition.APPLIED_WITH_PENDING,
        }:
            raise ValueError("refinement_applied_requires_current_round")
        if (
            self.code is ResultCode.REFINEMENT_CONFLICT
            and self.refinement.disposition is BundleRefinementDisposition.NONE
        ):
            raise ValueError("refinement_conflict_requires_existing_direction")
        return self


def serialize_control_result(result: BundleControlResult) -> str:
    payload = json.dumps(result.model_dump(mode="json", exclude_none=True), sort_keys=True, separators=(",", ":"))
    if len(payload) > MAX_CONTROL_RESULT_CHARS:
        raise ValueError("control_result_too_large")
    return payload


__all__ = [
    "AcceptedHumanResponse",
    "BranchResult",
    "BootstrapRoute",
    "BUNDLE_ID_PATTERN",
    "BundleAvailability",
    "BundleControlResult",
    "BundleRefinementDisposition",
    "BundleRefinementProjection",
    "CurrentRoundDirection",
    "Durability",
    "FinalVerdict",
    "GateVerdict",
    "Hitl2Decision",
    "HumanInputMode",
    "HumanInputOption",
    "HumanInputRequest",
    "InfrastructureResultCode",
    "InternalCancelDecision",
    "LifecycleAction",
    "LifecycleStatus",
    "LegalNextAction",
    "LogicalPhase",
    "MAX_CONTROL_RESULT_CHARS",
    "MAX_RERUN_GENERATIONS",
    "MAX_REFINEMENT_CHARS",
    "MAX_START_REQUEST_CHARS",
    "ReadinessVerdict",
    "RefinementAdmissionDisposition",
    "CurrentRefinement",
    "RefinementOperation",
    "RefinementReplayReceipt",
    "RunRefinementSource",
    "ResponseKind",
    "RefinementInput",
    "ResultCode",
    "ResumeDecision",
    "SynthesisVerdict",
    "SupportedLanguageOption",
    "TerminalReason",
    "WorkUnitStorageReason",
    "PendingResearchInterrupt",
    "PendingInputProjection",
    "TerminalIncidentProjection",
    "make_hitl_request_id",
    "completed_visits",
    "make_node_visit_id",
    "refinement_text_digest",
    "refinement_round_token",
    "text_only_content",
    "serialize_control_result",
]
