#!/usr/bin/env python3
"""Run the credential-free full-fake lifecycle through the shared experience.

Usage:
  make demo                    interactive
  make demo-scripted           deterministic non-interactive fixture route

@impl REC-003
@impl RED-004
@impl DPL-002
@impl DPL-006
"""

from __future__ import annotations

import argparse
import asyncio

from _demo_core import (
    PHASE_META,
    DemoAdapter,
    DemoLifecycleTransport,
    build_demo_host,
    demo_readiness_report,
)
from _terminal_failure_presentation import inspection_command

from deerflow_deep_research.domain.run_experience import AnswerRun, AwaitingInput, Fault, StartRun, Terminal, Working
from deerflow_deep_research.runtime.run_experience import ResearchRunExperience

_SCRIPTED_ANSWERS = {"hitl1": "Use broad public sources"}


def _bundle_lines(snapshot) -> tuple[str, ...]:
    bundle_id = snapshot.bundle_id
    if bundle_id is None:
        return ()
    lines = [f"  Run Bundle: {bundle_id}", f"  Durability: {snapshot.durability}"]
    observation = snapshot.observation
    if observation is not None and observation.inspectability.value == "available":
        command = inspection_command(bundle_id)
        if command is not None:
            lines.append(f"  Inspect: {command}")
    else:
        lines.append("  Retained observation is unavailable; inspection never resumes execution.")
    return tuple(lines)


def _render(update: object) -> None:
    if isinstance(update, Working):
        print(f"  {update.message}")
        return
    if isinstance(update, AwaitingInput):
        for line in _bundle_lines(update.snapshot):
            print(line)
        for phase in update.trace_delta:
            label, description = PHASE_META[phase]
            print(f"  -> {label}: {description}")
        print(f"  {update.prompt.heading}: {update.prompt.goal}")
        if update.prompt.rejection_category == "choice_input_invalid":
            print("  上一次选择无效；请只输入上方显示的选项 ID，例如 proceed。")
        for line in update.prompt.body_lines:
            print(f"  {line}")
        for option in update.prompt.options:
            print(f"  {option.id}: {option.consequence}")
        return
    if isinstance(update, Terminal):
        for line in _bundle_lines(update.snapshot):
            print(line)
        for phase in update.trace_delta:
            label, description = PHASE_META[phase]
            print(f"  -> {label}: {description}")
        print(f"  terminal: {update.outcome}")
        if update.failure is not None:
            print(f"  {update.failure.message}")
        return
    if isinstance(update, Fault):
        print(f"  {update.failure.message}")
        print(f"  Next: {update.failure.next_action}")
        return
    print("  The demo received an unsafe update.")


def _answer(update: AwaitingInput, *, scripted: bool) -> str | None:
    if scripted:
        value = _SCRIPTED_ANSWERS[update.prompt.phase]
        print(f"  automatic {update.prompt.phase}: {value}")
        return value
    try:
        prompt = "  输入选项 ID: " if update.prompt.mode == "choice" else "  response: "
        value = input(prompt)
    except (EOFError, KeyboardInterrupt):
        return None
    return value.strip() or None


async def run_demo(*, question: str, scripted: bool) -> int:
    print("\n  DeerFlow Deep Research · full-fake standalone demo")
    print("  No model, web request, Gateway, findings, or report is created.")
    print("  A returned lifecycle record retains an inspectable local bundle; inspection never resumes execution.")
    transport = DemoLifecycleTransport()
    experience = ResearchRunExperience(
        transport=transport,
        mode="fake",
        readiness_provider=lambda: demo_readiness_report(mode="fake"),
    )
    report = await experience.preflight()
    print(f"  {report.summary}")
    if not report.ready:
        return 2

    adapter = DemoAdapter()
    try:
        if hasattr(experience, "set_observation_publisher"):
            experience.set_observation_publisher(adapter.observation_publisher)
        transport.bind(adapter=adapter, host=build_demo_host())
        update = await experience.handle(StartRun(question=question), observer=_render)
        while isinstance(update, AwaitingInput):
            _render(update)
            value = _answer(update, scripted=scripted)
            if value is None:
                print("  Local demo ended without cancelling the graph.")
                return 130
            update = await experience.handle(AnswerRun(value=value), observer=_render)
        _render(update)
        if isinstance(update, Terminal) and update.outcome == "completed":
            print("  Demo complete. This terminal fixture is not completed research.")
            return 0
        return 1
    except asyncio.CancelledError:
        raise
    finally:
        closer = getattr(adapter, "aclose", None)
        if closer is not None:
            await closer()
        else:
            adapter.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the credential-free full-fake standalone Deep Research demo.",
        epilog=(
            "The fake route performs local preflight and renders shared prompts only. It does not "
            "create research findings or a cross-process resumable run. Returned lifecycle records retain "
            "an inspectable local bundle; inspection never resumes execution."
        ),
    )
    parser.add_argument(
        "--question",
        default="Compare the evidence for two approaches to renewable energy storage.",
        help="Visible research question for the standalone fake demo.",
    )
    parser.add_argument("--scripted", action="store_true", help="Use deterministic graph responses without stdin.")
    args = parser.parse_args()
    code = asyncio.run(run_demo(question=args.question, scripted=args.scripted))
    if code:
        raise SystemExit(code)


if __name__ == "__main__":
    main()
