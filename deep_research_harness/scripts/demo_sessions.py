#!/usr/bin/env python3
"""Inspect the safe Event Journal contained in one local Run Bundle.

This command is deliberately inspection-only. It first resolves the supplied opaque
Bundle id through the fixed local lifecycle profile, then reads only that selected
Bundle's diagnostics subtree. It has no external retained-observation fallback.

@impl RUS-003
@impl RUS-008
@impl REJ-004
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from _demo_core import DemoAdapter

from deerflow_deep_research.domain.bundle import BundleId
from deerflow_deep_research.domain.run_observation import JournalAvailability
from deerflow_deep_research.domain.session_workbench import WorkbenchAvailability, WorkbenchDiagnosisView


def _bundle_root() -> Path:
    return Path(__file__).resolve().parents[1] / ".deep-research-demo-runs"


async def _diagnosis(bundle_id: str) -> WorkbenchDiagnosisView:
    adapter = DemoAdapter(bundle_root=_bundle_root())
    try:
        await adapter.open()
        return await adapter.local_bundle_workbench().diagnosis(bundle_id=bundle_id)
    finally:
        await adapter.aclose()


def _render(*, bundle_id: str, diagnosis: WorkbenchDiagnosisView) -> tuple[str, ...]:
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


async def run(args: argparse.Namespace) -> int:
    try:
        BundleId(args.bundle_id)
    except (TypeError, ValueError):
        print("Run Bundle id is invalid.")
        return 2
    diagnosis = await _diagnosis(args.bundle_id)
    for line in _render(bundle_id=args.bundle_id, diagnosis=diagnosis):
        print(line)
    return 0 if diagnosis.availability is WorkbenchAvailability.AVAILABLE else 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect one contained Deep Research Event Journal.")
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect", help="Read one selected Bundle's Event Journal.")
    inspect.add_argument("bundle_id", help="Opaque Run Bundle id from a lifecycle result.")
    return parser


def main() -> None:
    raise SystemExit(asyncio.run(run(_build_parser().parse_args())))


if __name__ == "__main__":
    main()
