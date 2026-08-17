#!/usr/bin/env python3
"""Shared read-only diagnosis renderer for local Run Bundle inspection.

Both the `demo-sessions` inspection command and the operator `soft-bundle` CLI
render the same human-readable journal-health fact lines from a
`WorkbenchDiagnosisView`. The renderer is presentation-only and never a lifecycle
authority.

@impl REJ-004
"""

from __future__ import annotations

from deerflow_deep_research.domain.run_observation import JournalAvailability
from deerflow_deep_research.domain.session_workbench import WorkbenchAvailability, WorkbenchDiagnosisView


def render_diagnosis(*, bundle_id: str, diagnosis: WorkbenchDiagnosisView) -> tuple[str, ...]:
    if diagnosis.availability is WorkbenchAvailability.UNAVAILABLE:
        return ("Run Bundle or its contained Event Journal is unavailable for safe inspection.",)

    lines = [f"Run Bundle: {bundle_id}"]
    summary = diagnosis.summary
    if summary is not None:
        lines.append(f"Observed summary: {summary.status}@{summary.phase} generation {summary.generation}")
        lines.append(f"Journal health: {summary.journal_availability.value}")
        if summary.diagnostic_ref is not None:
            lines.append(f"Diagnostic reference: {summary.diagnostic_ref}")
        if summary.dropped_event_count:
            lines.append(
                "Dropped event interval: "
                f"{summary.first_dropped_sequence}-{summary.last_dropped_sequence} "
                f"({summary.dropped_event_count} events)"
            )
    elif diagnosis.events:
        lines.append(f"Journal health: {JournalAvailability.INCOMPLETE.value}")
    if diagnosis.incomplete_reasons:
        reasons = ", ".join(reason.value for reason in diagnosis.incomplete_reasons)
        lines.append(f"Journal incomplete because: {reasons}")

    for event in diagnosis.events:
        correlation = [f"generation {event.generation}", event.phase]
        if event.work_id is not None:
            correlation.append(f"work {event.work_id}")
        if event.attempt_id is not None:
            correlation.append(f"attempt {event.attempt_id}")
        fact = f"Observed event #{event.sequence}: {event.category.value} {' '.join(correlation)}"
        if event.outcome is not None:
            fact += f" {event.outcome}"
        if event.validation_stage is not None:
            fact += f" validation {event.validation_stage} codes {','.join(event.validation_codes) or 'none'}"
        if event.failure_category is not None:
            fact += f" failure {event.failure_category}"
        if event.provider_category is not None:
            fact += f" provider {event.provider_category}"
        if event.diagnostic_ref is not None:
            fact += f" diagnostic {event.diagnostic_ref}"
        lines.append(fact)
    lines.append("Event Journal is read-only; lifecycle controls remain independent.")
    return tuple(lines)


__all__ = ["render_diagnosis"]
