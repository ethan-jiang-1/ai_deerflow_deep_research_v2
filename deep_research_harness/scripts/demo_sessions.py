#!/usr/bin/env python3
"""Inspect the safe Event Journal contained in one local Run Bundle.

This command is deliberately inspection-only. It first resolves the supplied opaque
Bundle id through the fixed local lifecycle profile, then reads only that selected
Bundle's diagnostics subtree. It has no external retained-observation fallback.

@impl RDO-001
@impl RDO-004
@impl REJ-004
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from _demo_core import DemoAdapter
from _inspect_view import render_diagnosis

from deerflow_deep_research.domain.bundle import BundleId
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


async def run(args: argparse.Namespace) -> int:
    try:
        BundleId(args.bundle_id)
    except (TypeError, ValueError):
        print("Run Bundle id is invalid.")
        return 2
    diagnosis = await _diagnosis(args.bundle_id)
    for line in render_diagnosis(bundle_id=args.bundle_id, diagnosis=diagnosis):
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
