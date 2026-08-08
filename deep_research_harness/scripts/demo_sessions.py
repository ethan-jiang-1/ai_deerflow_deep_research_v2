#!/usr/bin/env python3
"""Read bounded retained Deep Research observations.

This command is deliberately inspection-only. A retained observation can describe a
previous Bundle outcome but can never locate, resume, cancel, refine, or recreate a
Run Bundle.

@impl RUS-003
@impl REC-004
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from deerflow_deep_research.domain.run_observation import (
    JournalAvailability,
    ObservationInspectability,
    RunObservationInspection,
)
from deerflow_deep_research.runtime.run_observation import RunObservationStore


def _observation_store() -> RunObservationStore:
    project_root = Path(__file__).resolve().parents[1]
    return RunObservationStore(retained_root=RunObservationStore.project_default_root(project_root))


def _render(inspection: RunObservationInspection) -> tuple[str, ...]:
    if inspection.inspectability is ObservationInspectability.INVALID_REFERENCE:
        return ("Run Bundle id is invalid.",)
    if inspection.inspectability is ObservationInspectability.NOT_FOUND:
        return ("No retained observation was found for this Run Bundle.",)
    if inspection.inspectability is ObservationInspectability.UNAVAILABLE:
        return ("Retained observation is unavailable for safe inspection.",)

    lines = [f"Run Bundle: {inspection.bundle_id}"]
    if inspection.retention_state is not None:
        lines.append(f"Retention: {inspection.retention_state.value}")
    if inspection.durability is not None:
        lines.append(f"Durability: {inspection.durability}")
    if inspection.summary is not None:
        lines.append(f"Observed summary: {inspection.summary.status}@{inspection.summary.phase}")
    if inspection.terminal_diagnostic is not None:
        diagnostic = inspection.terminal_diagnostic
        lines.extend(
            (
                f"Diagnostic reference: {diagnostic.reference}",
                f"Diagnostic category: {diagnostic.category}",
                f"Diagnostic phase: {diagnostic.phase}",
            )
        )
    if inspection.journal_availability is JournalAvailability.COMPLETE:
        lines.extend(
            f"Observed event #{event.sequence}: {event.category.value}@{event.phase}"
            for event in inspection.events[-8:]
        )
    else:
        lines.append("Observation journal: unavailable")
    lines.append("Observation does not resume or control this Run Bundle.")
    return tuple(lines)


async def run(args: argparse.Namespace) -> int:
    inspection = await _observation_store().inspect(bundle_id=args.bundle_id)
    for line in _render(inspection):
        print(line)
    return 0 if inspection.inspectability is ObservationInspectability.AVAILABLE else 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read one retained Deep Research observation.")
    parser.add_argument("bundle_id", help="Opaque Run Bundle id from a prior lifecycle result.")
    return parser


def main() -> None:
    raise SystemExit(asyncio.run(run(_build_parser().parse_args())))


if __name__ == "__main__":
    main()
