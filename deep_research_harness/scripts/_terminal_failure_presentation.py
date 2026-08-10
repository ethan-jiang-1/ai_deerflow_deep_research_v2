"""Safe provider-terminal projections shared by standalone CLI and TUI.

The shared run result remains the authority. This module only validates the
small display subset again so a malformed test double or future adapter input
cannot turn a terminal screen into a raw diagnostic surface.

@impl REC-006
@impl WFO-001
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, cast

from deerflow_deep_research.domain.run_experience import ProviderObservation, RunFailure, RunFailureCode
from deerflow_deep_research.domain.run_observation import (
    ObservationInspectability,
    ProviderTimeoutOrigin,
    RunObservationView,
)

_DIAGNOSTIC_REFERENCE_RE = re.compile(r"^diag_[A-Za-z0-9_-]{8,64}$")
_BUNDLE_REFERENCE_RE = re.compile(r"^b_[A-Za-z0-9_-]{43}$")
_PHASE_RE = re.compile(r"^[a-z][a-z0-9_]{0,31}$")
_RECOVERY_DISPOSITIONS = frozenset(
    {
        "exhausted",
        "retry_followed_by_terminal_failure",
        "retry_not_started_budget_consumed",
    }
)
WorkerFailureCategory = Literal[
    "agent_invocation",
    "tool_execution",
    "structured_output",
    "submission_validation",
    "unknown",
    "mixed",
]
_WORKER_FAILURE_CATEGORIES = frozenset(
    {
        "agent_invocation",
        "tool_execution",
        "structured_output",
        "submission_validation",
        "unknown",
        "mixed",
    }
)


@dataclass(frozen=True)
class SafeProviderObservation:
    configured_service_label: str | None
    configured_endpoint_authority: str | None
    response_kind: Literal["no_response", "http_response"]
    http_status: int | None
    timeout_origin: ProviderTimeoutOrigin | None


@dataclass(frozen=True)
class SafeRecoveryProjection:
    trigger_category: Literal["provider.timeout", "provider.unavailable"]
    trigger_observation: SafeProviderObservation
    trigger_invocation_ordinal: int
    model_attempts: int
    automatic_retries: int
    disposition: Literal[
        "exhausted",
        "retry_followed_by_terminal_failure",
        "retry_not_started_budget_consumed",
    ]


@dataclass(frozen=True)
class ProviderTerminalDetails:
    category: str
    phase: str | None
    worker_failure_category: WorkerFailureCategory | None
    final_observation: SafeProviderObservation | None
    recovery: SafeRecoveryProjection | None
    diagnostic_ref: str | None
    diagnostic_location: Literal["bundle_journal", "unavailable"] | None
    journal_record_created: bool
    recovery_action: Literal["fresh_start"] | None
    inspection_bundle_id: str | None


def is_provider_diagnostic(failure: object) -> bool:
    """Recognize the closed shape without rendering untrusted detail."""
    return (
        getattr(failure, "provider_recovery", None) is not None
        or getattr(failure, "provider_observation", None) is not None
    )


def inspection_command(bundle_id: object) -> str | None:
    """Return the one module-local, read-only observation command."""
    if not isinstance(bundle_id, str) or _BUNDLE_REFERENCE_RE.fullmatch(bundle_id) is None:
        return None
    return f'make demo-sessions DEMO_ARGS="inspect {bundle_id}"'


def provider_terminal_details(*, failure: RunFailure, snapshot: object | None) -> ProviderTerminalDetails | None:
    """Return a redacted display projection from one shared terminal failure."""
    if not is_provider_diagnostic(failure):
        return None

    recovery = _safe_recovery(getattr(failure, "provider_recovery", None))
    category = _safe_failure_category(getattr(failure, "code", None))
    location = _safe_diagnostic_location(getattr(failure, "diagnostic_location", None))
    diagnostic_ref = _safe_diagnostic_reference(getattr(failure, "diagnostic_ref", None))
    fresh_start = _is_legal_fresh_start(
        category=category,
        recovery=recovery,
        requested=getattr(failure, "recovery_action", None),
    )
    return ProviderTerminalDetails(
        category=category,
        phase=_safe_phase(getattr(failure, "phase", None)),
        worker_failure_category=_safe_worker_failure_category(getattr(failure, "worker_failure_category", None)),
        final_observation=_safe_observation(getattr(failure, "provider_observation", None)),
        recovery=recovery,
        diagnostic_ref=diagnostic_ref,
        diagnostic_location=location,
        journal_record_created=getattr(failure, "journal_record_created", None) is True,
        recovery_action="fresh_start" if fresh_start else None,
        inspection_bundle_id=_matching_inspection_bundle_id(
            snapshot=snapshot,
            diagnostic_ref=diagnostic_ref,
            diagnostic_location=location,
        ),
    )


def _safe_observation(value: object) -> SafeProviderObservation | None:
    response_kind = getattr(value, "response_kind", None)
    http_status = getattr(value, "http_status", None)
    timeout_origin = getattr(value, "timeout_origin", None)
    if response_kind not in {"no_response", "http_response"}:
        return None
    try:
        normalized = ProviderObservation(
            response_kind=response_kind,
            http_status=http_status,
            timeout_origin=timeout_origin,
        )
    except (TypeError, ValueError):
        return None

    label = getattr(value, "configured_service_label", None)
    if not isinstance(label, str):
        label = None
    try:
        normalized = ProviderObservation(
            configured_service_label=label,
            response_kind=normalized.response_kind,
            http_status=normalized.http_status,
            timeout_origin=normalized.timeout_origin,
        )
    except (TypeError, ValueError):
        pass

    authority = getattr(value, "configured_endpoint_authority", None)
    if not isinstance(authority, str):
        authority = None
    try:
        normalized = ProviderObservation(
            configured_service_label=normalized.configured_service_label,
            configured_endpoint_authority=authority,
            response_kind=normalized.response_kind,
            http_status=normalized.http_status,
            timeout_origin=normalized.timeout_origin,
        )
    except (TypeError, ValueError):
        pass

    return SafeProviderObservation(
        configured_service_label=normalized.configured_service_label,
        configured_endpoint_authority=normalized.configured_endpoint_authority,
        response_kind=normalized.response_kind,
        http_status=normalized.http_status,
        timeout_origin=normalized.timeout_origin,
    )


def _safe_recovery(value: object) -> SafeRecoveryProjection | None:
    trigger_category = getattr(value, "trigger_category", None)
    disposition = getattr(value, "disposition", None)
    trigger_observation = _safe_observation(getattr(value, "trigger_observation", None))
    trigger_ordinal = getattr(value, "trigger_invocation_ordinal", None)
    model_attempts = getattr(value, "model_attempts", None)
    automatic_retries = getattr(value, "automatic_retries", None)
    if (
        trigger_category not in {"provider.timeout", "provider.unavailable"}
        or disposition not in _RECOVERY_DISPOSITIONS
        or trigger_observation is None
        or type(trigger_ordinal) is not int
        or type(model_attempts) is not int
        or type(automatic_retries) is not int
    ):
        return None
    expected = {
        "exhausted": (1, 2, 1),
        "retry_followed_by_terminal_failure": (1, 2, 1),
        "retry_not_started_budget_consumed": (2, 2, 0),
    }[disposition]
    if (trigger_ordinal, model_attempts, automatic_retries) != expected:
        return None
    if trigger_category == "provider.timeout" and trigger_observation.response_kind != "no_response":
        return None
    if trigger_category == "provider.unavailable" and not (
        trigger_observation.response_kind == "no_response"
        or trigger_observation.http_status in {408, 429, 500, 502, 503, 504}
    ):
        return None
    return SafeRecoveryProjection(
        trigger_category=trigger_category,
        trigger_observation=trigger_observation,
        trigger_invocation_ordinal=trigger_ordinal,
        model_attempts=model_attempts,
        automatic_retries=automatic_retries,
        disposition=disposition,
    )


def _safe_failure_category(value: object) -> str:
    return value.value if isinstance(value, RunFailureCode) else "unknown"


def _safe_phase(value: object) -> str | None:
    return value if isinstance(value, str) and _PHASE_RE.fullmatch(value) is not None else None


def _safe_worker_failure_category(value: object) -> WorkerFailureCategory | None:
    if isinstance(value, str) and value in _WORKER_FAILURE_CATEGORIES:
        return cast(WorkerFailureCategory, value)
    return None


def _safe_diagnostic_reference(value: object) -> str | None:
    return value if isinstance(value, str) and _DIAGNOSTIC_REFERENCE_RE.fullmatch(value) is not None else None


def _safe_diagnostic_location(
    value: object,
) -> Literal["bundle_journal", "unavailable"] | None:
    if value in {"bundle_journal", "unavailable"}:
        return value
    return None


def _is_legal_fresh_start(
    *,
    category: str,
    recovery: SafeRecoveryProjection | None,
    requested: object,
) -> bool:
    return (
        requested == "fresh_start"
        and recovery is not None
        and recovery.disposition in {"exhausted", "retry_not_started_budget_consumed"}
        and category in {"provider.timeout", "provider.unavailable"}
    )


def _matching_inspection_bundle_id(
    *,
    snapshot: object | None,
    diagnostic_ref: str | None,
    diagnostic_location: Literal["bundle_journal", "unavailable"] | None,
) -> str | None:
    if diagnostic_location != "bundle_journal" or diagnostic_ref is None:
        return None
    bundle_id = getattr(snapshot, "bundle_id", None)
    observation = getattr(snapshot, "observation", None)
    if (
        not isinstance(bundle_id, str)
        or _BUNDLE_REFERENCE_RE.fullmatch(bundle_id) is None
        or not isinstance(observation, RunObservationView)
        or observation.inspectability is not ObservationInspectability.AVAILABLE
        or observation.bundle_id != bundle_id
        or observation.terminal_diagnostic_ref != diagnostic_ref
    ):
        return None
    return bundle_id


__all__ = [
    "ProviderTerminalDetails",
    "SafeProviderObservation",
    "SafeRecoveryProjection",
    "inspection_command",
    "is_provider_diagnostic",
    "provider_terminal_details",
]
