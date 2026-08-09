#!/usr/bin/env python3
"""Run deterministic fixture-graph composition verification.

This command is intentionally separate from the credential-free full-fake demos.
It creates the fixture recipe and its BundleGraphExecutor, then checks the returned
graph-owned terminal projection.

@impl DPL-003
@impl DPL-005
"""

from __future__ import annotations

import argparse
import asyncio

from _demo_core import PHASE_META, DemoAdapter, DemoLifecycleTransport, build_demo_runtime, demo_readiness_report

from deerflow_deep_research.domain.run_experience import AnswerRun, AwaitingInput, Fault, StartRun, Terminal, Working
from deerflow_deep_research.runtime.run_experience import ResearchRunExperience

DEFAULT_QUESTION = "Compare lithium-ion batteries and pumped-hydro storage for grid balancing."
_FIXTURE_PROFILE_ANSWER = "Use broad public sources."


def _render(update: object) -> None:
    if isinstance(update, Working):
        print(f"  {update.message}")
        return
    if isinstance(update, AwaitingInput):
        for phase in update.trace_delta:
            label, description = PHASE_META[phase]
            print(f"  -> {label}: {description}")
        print(f"  Fixture graph is awaiting {update.prompt.phase} input.")
        return
    if isinstance(update, Terminal):
        for phase in update.trace_delta:
            label, description = PHASE_META[phase]
            print(f"  -> {label}: {description}")
        print(f"  terminal: {update.outcome}")
        return
    if isinstance(update, Fault):
        print(f"  {update.failure.message}")
        print(f"  Next: {update.failure.next_action}")


async def run_demo(*, question: str) -> int:
    """Exercise the fixed fixture graph without exposing a route selector."""

    print("\n  DeerFlow Deep Research · fixture-graph verification")
    print("  This deterministic command verifies graph composition; it is not a full-fake demo.")
    transport = DemoLifecycleTransport()
    experience = ResearchRunExperience(
        transport=transport,
        mode="fake",
        readiness_provider=lambda: demo_readiness_report(mode="fake"),
    )
    report = await experience.preflight()
    if not report.ready:
        print(f"  {report.summary}")
        return 2

    adapter = DemoAdapter()
    try:
        runtime = build_demo_runtime(mode="fixture_graph", adapter=adapter)
        transport.bind(runtime=runtime)
        if hasattr(experience, "set_observation_publisher"):
            experience.set_observation_publisher(adapter.observation_publisher)
        update = await experience.handle(StartRun(question=question, scripted=True), observer=_render)
        while isinstance(update, AwaitingInput):
            _render(update)
            if update.prompt.phase != "hitl1":
                print("  Fixture graph requested an unsupported verification input.")
                return 1
            print("  automatic hitl1: fixture profile")
            update = await experience.handle(AnswerRun(value=_FIXTURE_PROFILE_ANSWER), observer=_render)
        _render(update)
        if not isinstance(update, Terminal) or update.outcome != "completed":
            return 1
        if "final_delivery" not in update.snapshot.completed_trace:
            print("  Fixture graph returned no final-delivery evidence.")
            return 1
        print("  Fixture graph composition verified.")
        return 0
    except asyncio.CancelledError:
        raise
    except Exception:
        print("  Fixture graph verification could not start in this local environment.")
        return 1
    finally:
        await adapter.aclose()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run deterministic fixture-graph composition verification.",
        epilog=(
            "This fixed verification route constructs the fixture recipe and graph executor. "
            "It is not a replacement for make demo, make demo-scripted, or make demo-tui-fake."
        ),
    )
    parser.add_argument(
        "--question",
        default=DEFAULT_QUESTION,
        help="Comparison question used by the fixed fixture-graph verification route.",
    )
    args = parser.parse_args()
    code = asyncio.run(run_demo(question=args.question))
    if code:
        raise SystemExit(code)


if __name__ == "__main__":
    main()
