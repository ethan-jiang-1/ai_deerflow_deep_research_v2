#!/usr/bin/env python3
"""Standalone Textual presentation adapter for Deep Research run updates.

@impl RED-001
@impl RED-002
@impl RED-003
@impl RED-004
@impl DPL-002
@impl WFO-001
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal, TextIO

from _demo_core import (
    PHASE_META,
    DemoAdapter,
    DemoLifecycleTransport,
    build_demo_runtime,
    demo_readiness_report,
)
from _terminal_failure_presentation import (
    ProviderTerminalDetails,
    SafeProviderObservation,
    inspection_command,
    is_provider_diagnostic,
    provider_terminal_details,
)
from local_profiles import ProfileError, validate_observer_profile
from rich.table import Table
from rich.text import Text
from textual import events, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Input, RichLog, Static

from deerflow_deep_research.domain.lifecycle import SupportedLanguageOption
from deerflow_deep_research.domain.run_experience import (
    AnswerRun,
    AwaitingInput,
    CancelRun,
    FailureCertainty,
    Fault,
    ReadinessCheck,
    ReadinessReport,
    Ready,
    RunFailure,
    RunFailureCode,
    RunUpdate,
    SelectControlRun,
    StartRun,
    Terminal,
    Working,
)
from deerflow_deep_research.runtime.gateway_observer import (
    GatewayObserver,
    GatewayTransportObservation,
    HttpGatewayPublicClient,
)
from deerflow_deep_research.runtime.run_experience import ResearchRunExperience


@dataclass(frozen=True)
class TuiRenderedUpdate:
    heading: str
    detail: str
    placeholder: str
    completed_trace: tuple[str, ...]
    pending_phase: str | None
    options: tuple[str, ...]
    accepts_input: bool
    show_cancel: bool
    terminal: bool


def _failure_detail(failure, *, snapshot: object | None = None) -> str:
    provider_details = provider_terminal_details(failure=failure, snapshot=snapshot)
    if provider_details is not None:
        return _provider_failure_detail(provider_details)
    lines = [failure.message, f"Next: {failure.next_action}"]
    if failure.phase:
        lines.append(f"Phase: {failure.phase}")
    lines.append("Retryable" if failure.retryable else "Not retryable")
    if failure.diagnostic_ref:
        lines.append(f"Diagnostic: {failure.diagnostic_ref}")
    if not failure.journal_record_created:
        lines.append("Contained Event Journal record is unavailable.")
    return "\n".join(lines)


def _provider_failure_detail(details: ProviderTerminalDetails) -> str:
    lines = [f"Category: {details.category}"]
    if details.phase:
        lines.append(f"Phase: {details.phase}")
    if details.worker_failure_category:
        lines.append(f"Worker failure category: {details.worker_failure_category}")
    if details.final_observation is not None:
        lines.extend(_provider_observation_lines("Final service observation", details.final_observation))
    if details.recovery is not None:
        lines.extend(_provider_observation_lines("Retry trigger observation", details.recovery.trigger_observation))
        lines.append(f"Model invocations: {details.recovery.model_attempts}")
        lines.append(f"Automatic retries: {details.recovery.automatic_retries}")
        lines.append(f"Recovery disposition: {details.recovery.disposition}")
    if details.diagnostic_ref:
        lines.append(f"Diagnostic: {details.diagnostic_ref}")
    if details.diagnostic_location == "bundle_journal":
        lines.append("Diagnostic location: bundle_journal")
    elif details.diagnostic_location == "unavailable":
        lines.append("Diagnostic location: unavailable")
    journal_message = (
        "Contained Event Journal record created"
        if details.journal_record_created
        else "Contained Event Journal record is unavailable."
    )
    lines.append(journal_message)
    if details.recovery_action == "fresh_start":
        lines.append("Fresh run from deep_research_harness/: make demo-real")
    else:
        lines.append(f"Next: {_provider_next_step(details.category)}")
    if details.inspection_bundle_id is not None:
        command = inspection_command(details.inspection_bundle_id)
        if command is not None:
            lines.append(f"Read-only diagnosis from deep_research_harness/: {command}")
    return "\n".join(lines)


def _provider_observation_lines(label: str, observation: SafeProviderObservation) -> tuple[str, ...]:
    lines: list[str] = []
    if observation.configured_service_label:
        lines.append(f"{label} service: {observation.configured_service_label}")
    if observation.configured_endpoint_authority:
        lines.append(f"{label} endpoint: {observation.configured_endpoint_authority}")
    response = "no_response" if observation.response_kind == "no_response" else f"HTTP {observation.http_status}"
    lines.append(f"{label} response: {response}")
    if observation.timeout_origin is not None:
        lines.append(f"{label} timeout origin: {observation.timeout_origin}")
    return tuple(lines)


def _provider_next_step(category: str) -> str:
    if category == "provider.authentication_failed":
        return "Check the model-service credential, then start a distinct run."
    if category in {"provider.timeout", "provider.unavailable"}:
        return "Check service availability, then start a distinct run."
    return "Review the diagnostic reference before deciding whether to start a distinct run."


def _bundle_detail(snapshot, *, suppress_inspection: bool = False) -> tuple[str, ...]:
    bundle_id = snapshot.bundle_id
    if bundle_id is None:
        return ()
    lines = [f"Run Bundle: {bundle_id}", f"Durability: {snapshot.durability}"]
    observation = snapshot.observation
    if observation is not None and observation.inspectability.value == "available" and not suppress_inspection:
        command = inspection_command(bundle_id)
        if command is not None:
            lines.append(f"Inspect from deep_research_harness/: {command}")
    else:
        lines.append("Retained observation is unavailable; inspection is read-only.")
    return tuple(lines)


def _presentation_fault() -> Fault:
    return Fault(
        failure=RunFailure(
            code=RunFailureCode.INTERNAL_UNEXPECTED,
            certainty=FailureCertainty.UNKNOWN,
            message="The local presentation adapter could not continue.",
            next_action="Restart the standalone demo and provide a diagnostic reference if the issue repeats.",
            retryable=False,
            journal_record_created=False,
            diagnostic_location="unavailable",
        )
    )


def _gateway_readiness_report(profile: str | None) -> ReadinessReport:
    if profile is None:
        return _gateway_readiness_failure(
            summary="A selected local Gateway profile is required.",
            detail="Select one ready local profile before starting the Gateway observer.",
            next_action="Restart with --profile <name> after profile checks pass.",
        )
    try:
        validate_observer_profile(Path(__file__).resolve().parents[1], profile)
    except ProfileError:
        return _gateway_readiness_failure(
            summary="The selected local Gateway profile is not ready.",
            detail="The selected profile needs its Gateway observer prerequisites corrected.",
            next_action="Correct the selected profile, restart its Gateway, then start a new observer turn.",
        )
    return ReadinessReport(
        mode="real",
        ready=True,
        summary="Selected local Gateway profile is ready.",
        checks=(ReadinessCheck(name="environment", ready=True, detail="selected local Gateway profile"),),
        durability_note="Gateway history remains owned by the configured Gateway; this TUI retains no local session.",
    )


def _gateway_readiness_failure(*, summary: str, detail: str, next_action: str) -> ReadinessReport:
    return ReadinessReport(
        mode="real",
        ready=False,
        summary=summary,
        checks=(ReadinessCheck(name="environment", ready=False, detail=detail, next_action=next_action),),
        failure=RunFailure(
            code=RunFailureCode.CONFIGURATION_ENVIRONMENT_INVALID,
            certainty=FailureCertainty.DIRECT,
            message=summary,
            next_action=next_action,
            retryable=False,
            journal_record_created=False,
            diagnostic_location="unavailable",
        ),
        durability_note="No Gateway thread or Deep Research Run was created.",
    )


def _format_timestamp(value: object) -> str:
    """Best-effort local HH:MM:SS from an ISO-8601 journal timestamp."""
    if not isinstance(value, str):
        return "?"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.astimezone().strftime("%H:%M:%S")
    except ValueError:
        return value[-8:]


def live_progress_lines(bundle_root: Path | None) -> tuple[str, ...]:
    """Read the most-recently updated *active* bundle's journal and return
    human-readable live-progress lines for the Working heartbeat.

    The TUI dispatch itself carries no phase/trace while the graph runs, so the
    presentation layer reads the ignored retained-run journal on disk. Returns
    () when there is no readable active bundle (preflight, fixture mode, no run
    yet, or an I/O failure) so the heartbeat degrades to the static message.
    """
    if bundle_root is None:
        return ()
    scopes_dir = bundle_root / "workspace" / "deep-research" / "scopes"
    if not scopes_dir.is_dir():
        return ()
    candidates: list[tuple[str, Path]] = []
    for scope in scopes_dir.iterdir():
        if not scope.is_dir():
            continue
        for bundle in scope.iterdir():
            summary = bundle / "diagnostics" / "run-summary.json"
            try:
                data = json.loads(summary.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if data.get("status") != "active":
                continue
            candidates.append((str(data.get("updated_at", "")), bundle))
    if not candidates:
        return ()
    _, bundle = max(candidates)
    events_path = bundle / "diagnostics" / "events.jsonl"
    try:
        raw = events_path.read_text(encoding="utf-8")
    except OSError:
        return ()

    done: list[str] = []
    seen: set[str] = set()
    last_node_phase: str | None = None
    last_node_outcome: str | None = None
    model_calls = 0
    total_tokens = 0
    event_count = 0
    last_event: dict[str, object] | None = None
    for line in raw.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        event_count += 1
        last_event = event
        phase = event.get("phase")
        category = event.get("category")
        outcome = event.get("outcome")
        if category == "node":
            last_node_phase = phase if isinstance(phase, str) else None
            last_node_outcome = outcome if isinstance(outcome, str) else None
            if outcome == "completed" and isinstance(phase, str) and phase not in seen:
                seen.add(phase)
                done.append(phase)
        if category == "model_tool" and outcome == "completed":
            model_calls += 1
            tokens = event.get("usage_tokens")
            if isinstance(tokens, dict):
                total = tokens.get("total_tokens")
                if isinstance(total, (int, float)):
                    total_tokens += int(total)

    lines: list[str] = []
    if done or last_node_phase:
        chain = " → ".join(done)
        if last_node_outcome == "started" and last_node_phase is not None:
            chain = f"{chain} → {last_node_phase}（进行中）" if chain else f"{last_node_phase}（进行中）"
        lines.append(f"进度: {chain}")
    if last_event is not None:
        stamp = _format_timestamp(last_event.get("timestamp"))
        phase = str(last_event.get("phase") or "")
        category = str(last_event.get("category") or "")
        outcome = str(last_event.get("outcome") or "")
        lines.append(f"最近: {stamp} · {phase} {category} {outcome}".rstrip())
    if model_calls or total_tokens:
        lines.append(f"模型调用: {model_calls} 次完成 · {total_tokens / 1000:.1f}k tokens")
    if event_count:
        lines.append(f"journal 事件: {event_count}")
    return tuple(lines)


def find_bundle_dir(bundle_root: Path | None, bundle_id: str | None) -> Path | None:
    """Locate the retained bundle directory for a bundle id (scopes/<scope>/<bundle>/)."""
    if bundle_root is None or not bundle_id:
        return None
    scopes_dir = bundle_root / "workspace" / "deep-research" / "scopes"
    if not scopes_dir.is_dir():
        return None
    for scope in scopes_dir.iterdir():
        if not scope.is_dir():
            continue
        bundle = scope / bundle_id
        if bundle.is_dir():
            return bundle
    return None


def report_path(bundle_root: Path | None, bundle_id: str | None) -> Path | None:
    """Return the final report path for a bundle id, or None when not yet produced."""
    bundle_dir = find_bundle_dir(bundle_root, bundle_id)
    if bundle_dir is None:
        return None
    report = bundle_dir / "final" / "report.md"
    return report if report.is_file() else None


def render_run_update(
    update: object,
    progress: Sequence[str] = (),
    report_path: Path | None = None,
) -> TuiRenderedUpdate:
    """Return a native view model using only safe shared ``RunUpdate`` values."""
    if isinstance(update, Ready):
        return TuiRenderedUpdate(
            heading="Enter a research question" if update.report.ready else "Readiness check failed",
            detail=update.report.summary if update.report.ready else _failure_detail(update.report.failure),
            placeholder="Research question",
            completed_trace=(),
            pending_phase=None,
            options=(),
            accepts_input=update.report.ready,
            show_cancel=False,
            terminal=not update.report.ready,
        )
    if isinstance(update, Working):
        details = [*progress, update.message]
        if update.snapshot.bundle_id:
            details.append(f"Run Bundle: {update.snapshot.bundle_id}")
        if update.snapshot.lifecycle_phase:
            details.append(f"Last confirmed phase: {update.snapshot.lifecycle_phase}")
        details.append(f"Local returned-only wait: {update.snapshot.elapsed_seconds:.1f}s")
        return TuiRenderedUpdate(
            heading="Waiting for lifecycle result",
            detail="\n".join(details),
            placeholder="",
            completed_trace=update.snapshot.completed_trace,
            pending_phase=update.snapshot.pending_input.pending_phase if update.snapshot.pending_input else None,
            options=(),
            accepts_input=False,
            show_cancel=False,
            terminal=False,
        )
    if isinstance(update, AwaitingInput):
        prompt = update.prompt
        details = [*_bundle_detail(update.snapshot), prompt.goal, *prompt.proposed_scope]
        if prompt.interaction is not None and prompt.interaction.feedback is not None:
            details.append(prompt.interaction.feedback.message)
        if prompt.recognized_fields:
            details.append("Recognized: " + ", ".join(prompt.recognized_fields))
        if prompt.missing_fields:
            details.append("Missing: " + ", ".join(prompt.missing_fields))
        if prompt.rejection_category == "choice_input_invalid":
            details.append("The last choice was invalid. Enter an advertised option ID, for example proceed.")
        elif prompt.rejection_category:
            details.append("The last response was not recognized. Use an advertised value or complete JSON.")
        if prompt.accepted_rounds_remaining:
            details.append(f"Accepted answers remaining: {prompt.accepted_rounds_remaining}")
        if prompt.rejection_retries_remaining:
            details.append(f"Unrecognized retries remaining: {prompt.rejection_retries_remaining}")
        details.extend(prompt.body_lines)
        details.extend(f"{control.label}: {control.consequence}" for control in prompt.visible_controls)
        if prompt.answer_example:
            details.append("Example: " + prompt.answer_example)
        details.extend(f"{option.id}: {option.consequence}" for option in prompt.options)
        return TuiRenderedUpdate(
            heading=prompt.heading,
            detail="\n".join(details),
            placeholder="Type your response" if prompt.mode == "text" else "Choose an advertised option ID",
            completed_trace=update.snapshot.completed_trace,
            pending_phase=prompt.phase,
            options=tuple(option.id for option in prompt.options),
            accepts_input=True,
            show_cancel=True,
            terminal=False,
        )
    if isinstance(update, Terminal):
        provider_diagnostic = update.failure is not None and is_provider_diagnostic(update.failure)
        detail_lines = list(_bundle_detail(update.snapshot, suppress_inspection=provider_diagnostic))
        detail_lines.append(
            _failure_detail(update.failure, snapshot=update.snapshot)
            if update.failure is not None
            else f"Research {update.outcome}."
        )
        if update.snapshot.durability == "same_process":
            detail_lines.append("Retained records are inspectable, but this run cannot continue after process exit.")
        elif update.snapshot.durability == "restart_durable":
            detail_lines.append("Authorized local session operations may inspect or continue this durable run.")
        if update.outcome == "completed" and report_path is not None:
            detail_lines.append(f"Report: {report_path}")
        detail = "\n".join(detail_lines)
        return TuiRenderedUpdate(
            heading="Research complete" if update.outcome == "completed" else "Research ended",
            detail=detail,
            placeholder="",
            completed_trace=update.snapshot.completed_trace,
            pending_phase=None,
            options=(),
            accepts_input=False,
            show_cancel=False,
            terminal=True,
        )
    if isinstance(update, Fault):
        snapshot = update.snapshot
        return TuiRenderedUpdate(
            heading="Research could not continue",
            detail=_failure_detail(update.failure, snapshot=snapshot),
            placeholder="",
            completed_trace=snapshot.completed_trace if snapshot is not None else (),
            pending_phase=None,
            options=(),
            accepts_input=False,
            show_cancel=False,
            terminal=True,
        )
    return TuiRenderedUpdate(
        heading="Research could not continue",
        detail="The application received an unsafe update.",
        placeholder="",
        completed_trace=(),
        pending_phase=None,
        options=(),
        accepts_input=False,
        show_cancel=False,
        terminal=True,
    )


def _pipeline_tracker(completed: tuple[str, ...], pending: str | None) -> Table:
    """Render only the verified returned trace and the shared pending prompt."""
    table = Table(show_header=False, expand=True, padding=(0, 1))
    table.add_column("marker", width=2)
    table.add_column("phase", width=18)
    table.add_column("description", width=28)
    for phase in completed:
        label, description = PHASE_META[phase]
        table.add_row("[green]✓[/]", f"[dim green]{label}[/]", f"[dim green]{description}[/]")
    if pending is not None:
        label, description = PHASE_META[pending]
        table.add_row("[bold yellow]⏸[/]", f"[bold yellow]{label}[/]", f"[bold yellow]{description}[/]")
    return table


class DeepResearchDemoTUI(App[None]):
    """Textual adapter over one owned ``ResearchRunExperience`` instance."""

    CSS = """
    Screen { layout: vertical; background: #111827; color: #e5e7eb; }
    #banner { height: 3; padding: 1 2; background: #164e63; color: #ecfeff; text-style: bold; }
    #pipeline { height: auto; margin: 1 2; min-height: 3; }
    #log { height: 1fr; border: round #475569; margin: 0 2; padding: 0 1; }
    #prompt { height: auto; margin: 0 2; color: #fde68a; text-style: bold; }
    #controls { height: 3; margin: 0 2 1 2; }
    #composer { width: 1fr; }
    #copy-details { width: 14; margin-left: 1; }
    #accept { width: 16; margin-left: 1; }
    #cancel { width: 14; margin-left: 1; }
    #hint { height: 1; margin: 0 2 1 2; color: #94a3b8; }
    """

    BINDINGS = [("ctrl+c", "quit", "Quit")]
    _WORKER_GROUP = "research-lifecycle"
    _EXAMPLE_QUESTION = "Compare renewable-energy storage approaches"
    AUTO_QUESTION = "What is one bounded fact about China's EV battery market in 2024?"

    def __init__(
        self,
        *,
        mode: Literal["fixture", "gateway", "embedded_smoke"] = "gateway",
        profile: str | None = None,
        auto: bool = False,
    ) -> None:
        super().__init__()
        self.mode = mode
        self.profile = profile
        self.auto = auto
        self._adapter: DemoAdapter | None = None
        self._gateway_transport: GatewayObserver | None = None
        if self.mode == "gateway":
            report = _gateway_readiness_report(profile)
            self._gateway_transport = (
                GatewayObserver(
                    client=HttpGatewayPublicClient(),
                    transport_observer=self._gateway_transport_observer,
                    withheld_candidate_observer=self._gateway_progress_observer,
                )
                if report.ready
                else None
            )
            transport = self._gateway_transport

            def readiness_provider() -> ReadinessReport:
                return report

            experience_mode = "real"
        else:
            transport = DemoLifecycleTransport()
            embedded_smoke = self.mode == "embedded_smoke"

            def readiness_provider() -> ReadinessReport:
                return demo_readiness_report(mode="real" if embedded_smoke else "fixture")

            experience_mode = "real" if self.mode == "embedded_smoke" else "fixture"
        self._transport = transport
        self._experience = ResearchRunExperience(
            transport=transport,
            mode=experience_mode,
            readiness_provider=readiness_provider,
        )
        self.last_update: RunUpdate | None = None
        self.last_view: TuiRenderedUpdate | None = None
        self._last_detail = ""
        self._last_logged = ""
        self._tui_log: TextIO | None = None
        self._tui_log_path: Path | None = None

    def compose(self) -> ComposeResult:
        yield Static(id="banner")
        yield Static(id="pipeline")
        yield RichLog(id="log", wrap=True, markup=False, max_lines=100)
        yield Static(id="prompt")
        with Horizontal(id="options"):
            for language in SupportedLanguageOption:
                yield Button(language.value, id=f"option-{language.value}", classes="advertised-option")
        with Horizontal(id="controls"):
            yield Input(value=self._EXAMPLE_QUESTION, placeholder="Research question", id="composer")
            yield Button("Copy details", id="copy-details")
            yield Button("Start proposal", id="accept")
            yield Button("Cancel", id="cancel", variant="error")
        yield Static(
            "中间对话区: 双击=复制全文 · Option+拖拽=选中一段 · Copy details=复制全部 · Ctrl-C 退出",
            id="hint",
        )

    def on_mount(self) -> None:
        mode_label = {
            "fixture": "fixture-graph",
            "gateway": "local Gateway observer",
            "embedded_smoke": "embedded smoke",
        }[self.mode]
        if self.auto:
            mode_label += " · auto"
        self.query_one("#banner", Static).update(Text(f"Deep Research · {mode_label} demo", style="bold cyan"))
        self._render_view(
            TuiRenderedUpdate(
                heading="Checking local readiness",
                detail="Waiting for the local preflight result.",
                placeholder="",
                completed_trace=(),
                pending_phase=None,
                options=(),
                accepts_input=False,
                show_cancel=False,
                terminal=False,
            )
        )
        self._initialize()

    async def on_unmount(self) -> None:
        if self._tui_log is not None:
            log, self._tui_log = self._tui_log, None
            log.close()
        self._close_adapter()
        if self._gateway_transport is not None:
            transport, self._gateway_transport = self._gateway_transport, None
            await transport.aclose()

    def _close_adapter(self) -> None:
        if self._adapter is None:
            return
        adapter, self._adapter = self._adapter, None
        adapter.close()

    @work(group=_WORKER_GROUP, exclusive=True, exit_on_error=False)
    async def _initialize(self) -> None:
        report = await self._experience.preflight()
        if not report.ready:
            self.apply_run_update(Fault(failure=report.failure or _presentation_fault().failure))
            return
        if self.mode == "gateway":
            self.apply_run_update(Ready(report=report))
            return
        adapter: DemoAdapter | None = None
        try:
            adapter = DemoAdapter.for_real() if self.mode == "embedded_smoke" else DemoAdapter()
            if self.mode == "embedded_smoke":
                self._transport.bind(runtime=build_demo_runtime(mode="real", adapter=adapter))
            else:
                self._transport.bind(runtime=build_demo_runtime(mode="fixture_graph", adapter=adapter))
            if hasattr(self._experience, "set_observation_publisher"):
                self._experience.set_observation_publisher(adapter.observation_publisher)
            self._adapter = adapter
            self.apply_run_update(Ready(report=report))
            if self.mode == "embedded_smoke" and self.auto:
                # 010 auto TUI: dispatch the fixed scripted question with the
                # default product path (no profile_intent). Graph-owned policy
                # answers HITL1/HITL2; the human never types.
                self._dispatch(
                    StartRun(question=self.AUTO_QUESTION, scripted=True, profile_intent=None)
                )
        except asyncio.CancelledError:
            raise
        except Exception:
            if adapter is not None:
                adapter.close()
            self.apply_run_update(_presentation_fault())

    def _live_progress(self) -> tuple[str, ...]:
        """Live journal progress for the Working heartbeat (best effort)."""
        adapter = self._adapter
        if adapter is None:
            return ()
        return live_progress_lines(getattr(adapter, "bundle_root", None))

    def _terminal_report_path(self, update: RunUpdate) -> Path | None:
        """Resolve the produced report path for a completed terminal update."""
        if not isinstance(update, Terminal) or update.outcome != "completed":
            return None
        adapter = self._adapter
        if adapter is None:
            return None
        return report_path(
            getattr(adapter, "bundle_root", None),
            update.snapshot.bundle_id,
        )

    def _append_tui_log(self, detail: str) -> None:
        """Persist each distinct rendered detail to logs/tui-<pid>.log (best effort).

        Gives the operator a plain file to open and copy from when terminal text
        selection is inconvenient; never affects run behavior.
        """
        if not detail or detail == self._last_logged:
            return
        self._last_logged = detail
        if self._tui_log is None:
            adapter = self._adapter
            root = getattr(adapter, "bundle_root", None) if adapter is not None else None
            if root is None:
                return
            log_dir = root / "logs"
            try:
                log_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
                path = log_dir / f"tui-{os.getpid()}.log"
                self._tui_log = open(path, "a", encoding="utf-8")
                self._tui_log_path = path
            except OSError:
                self._tui_log = None
                return
        try:
            self._tui_log.write(detail + "\n---\n")
            self._tui_log.flush()
        except OSError:
            pass

    def apply_run_update(self, update: RunUpdate) -> None:
        """Public adapter seam: consume a shared update without lifecycle parsing."""
        self.last_update = update
        view = render_run_update(
            update,
            progress=self._live_progress(),
            report_path=self._terminal_report_path(update),
        )
        self._render_view(view)
        self._last_detail = view.detail
        self._append_tui_log(view.detail)

    def _render_view(self, view: TuiRenderedUpdate) -> None:
        self.last_view = view
        composer = self.query_one("#composer", Input)
        cancel = self.query_one("#cancel", Button)
        accept = self.query_one("#accept", Button)
        self.query_one("#prompt", Static).update(Text(view.heading, style="bold yellow"))
        self.query_one("#log", RichLog).clear()
        if view.detail:
            self.query_one("#log", RichLog).write(Text(view.detail))
        pipeline = self.query_one("#pipeline", Static)
        pipeline.display = bool(view.completed_trace or view.pending_phase)
        if pipeline.display:
            pipeline.update(_pipeline_tracker(view.completed_trace, view.pending_phase))
        composer.disabled = not view.accepts_input
        composer.placeholder = view.placeholder
        cancel_allowed = view.show_cancel and self.mode != "gateway"
        cancel.display = cancel_allowed
        cancel.disabled = not cancel_allowed
        accept.display = bool(
            isinstance(self.last_update, AwaitingInput)
            and any(control.id == "accept_current_proposal" for control in self.last_update.prompt.visible_controls)
        )
        accept.disabled = not accept.display
        advertised_options = self._advertised_language_options()
        options_bar = self.query_one("#options", Horizontal)
        options_bar.display = bool(advertised_options)
        for button in options_bar.query(Button):
            option = advertised_options.get(str(button.id).removeprefix("option-"))
            button.display = option is not None
            button.disabled = option is None
            if option is not None:
                button.label = option.label
        if view.accepts_input:
            composer.value = self._EXAMPLE_QUESTION if isinstance(self.last_update, Ready) else ""
            composer.focus()

    @work(group=_WORKER_GROUP, exclusive=True, exit_on_error=False)
    async def _dispatch(self, intent) -> None:
        try:
            update = await self._experience.handle(intent, observer=self.apply_run_update)
            self.apply_run_update(update)
        except asyncio.CancelledError:
            raise
        except Exception:
            self.apply_run_update(_presentation_fault())

    def _select_current_proposal(self) -> None:
        if not isinstance(self.last_update, AwaitingInput) or not any(
            control.id == "accept_current_proposal" for control in self.last_update.prompt.visible_controls
        ):
            return
        self._dispatch(SelectControlRun(control_id="accept_current_proposal"))

    def _advertised_language_options(self) -> dict[str, object]:
        """Project only the current HITL1 language CHOICE advertisement."""

        if not isinstance(self.last_update, AwaitingInput):
            return {}
        prompt = self.last_update.prompt
        if prompt.mode != "choice" or prompt.phase != "hitl1":
            return {}
        return {option.id: option for option in prompt.options}

    def _select_advertised_option(self, option_id: str) -> None:
        """Submit one currently advertised language option as a typed OPTION answer."""

        if option_id not in self._advertised_language_options():
            return
        self._dispatch(AnswerRun(value=option_id, response_kind="option", option_id=option_id))

    def _gateway_transport_observer(self, observation: GatewayTransportObservation) -> None:
        if observation.kind == "assistant_text" and observation.detail:
            detail = observation.detail
        else:
            detail = {
                "heartbeat": "Gateway liveness observed.",
                "gap": "Gateway stream gap observed; no research outcome was inferred.",
                "error": "Gateway reported a transport error; no research outcome was inferred.",
                "end": "Gateway turn ended; awaiting a validated lifecycle result.",
                "custom_invalid": "Gateway custom record was ignored.",
            }.get(observation.kind)
        if detail:
            self.query_one("#log", RichLog).write(Text(detail))

    def _gateway_progress_observer(self, candidate: Mapping[str, object]) -> None:
        """Render only predecessor-approved progress fields as a bounded projection."""

        phase = candidate.get("phase")
        operation = candidate.get("operation")
        outcome = candidate.get("outcome")
        bundle_id = candidate.get("bundle_id")
        if not (phase or operation or outcome):
            return
        label = " ".join(part for part in (str(phase), str(operation), str(outcome)) if part)
        scope = str(bundle_id)[:24] if isinstance(bundle_id, str) else ""
        line = f"Deep Research progress: {label}" + (f" (bundle {scope})" if scope else "")
        self.query_one("#log", RichLog).write(Text(line))

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        raw_value = event.value
        value = raw_value.strip()
        if not value:
            return
        if self.last_update is None:
            return
        if isinstance(self.last_update, Ready) and self.last_update.report.ready:
            self._dispatch(StartRun(question=value))
        elif isinstance(self.last_update, AwaitingInput):
            prompt = self.last_update.prompt
            if prompt.mode == "choice" and prompt.phase == "hitl1":
                # The shared contract requires a typed OPTION here; an exact
                # match of one advertised option id is the only legal composer
                # entry, and any other text dispatches nothing.
                if value in self._advertised_language_options():
                    self._dispatch(AnswerRun(value=value, response_kind="option", option_id=value))
                return
            self._dispatch(AnswerRun(value=value))

    def _rich_log_text(self) -> str:
        """Extract the full plain text currently shown in the middle log area."""
        log = self.query_one("#log", RichLog)
        return "\n".join(strip.text for strip in log.lines)

    def _copy_details(self) -> None:
        """Copy the middle conversation log (falling back to the latest detail)."""
        log = self.query_one("#log", RichLog)
        text = self._rich_log_text()
        source = "中间对话全文"
        if not text.strip():
            text = self._last_detail or ""
            source = "当前详情"
        try:
            self.copy_to_clipboard(text)
            copied = bool(text.strip())
        except Exception:
            copied = False
        if copied:
            self.notify(f"已复制{source}到剪贴板。", title="Copy", severity="information")
        else:
            self.notify("没有可复制的内容。", title="Copy", severity="warning")
        if self._tui_log_path is not None:
            log.write(Text(f"TUI 日志文件: {self._tui_log_path}", style="dim"))

    def on_double_click(self, event: events.DoubleClick) -> None:
        """Double-clicking the middle log copies the full conversation text."""
        if event.widget is not None and event.widget.id == "log":
            self._copy_details()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "accept":
            self._select_current_proposal()
        elif event.button.id == "copy-details":
            self._copy_details()
        elif event.button.id is not None and event.button.id.startswith("option-"):
            self._select_advertised_option(event.button.id.removeprefix("option-"))
        elif event.button.id == "cancel" and self.mode != "gateway" and isinstance(self.last_update, AwaitingInput):
            self._dispatch(CancelRun())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the standalone Deep Research Textual demo.",
        epilog=(
            "Preflight runs before a question can be submitted. Prompts and failures render only "
            "safe shared run updates; diagnostic records live in the returned Run Bundle's Event Journal. "
            "A returned lifecycle record retains an "
            "inspectable local bundle; inspection is not cross-process resume."
        ),
    )
    parser.add_argument("--fixture", action="store_true", help="Run the zero-credential fixture graph.")
    parser.add_argument("--profile", default=None, help="Selected ready local Gateway profile for default real mode.")
    parser.add_argument(
        "--embedded-smoke",
        action="store_true",
        help="Use the direct local graph smoke route without Gateway history, trace, or SSE claims.",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help=(
            "Auto TUI: after preflight, dispatch one fixed scripted question (010 run; "
            "HITL1/HITL2 answered by graph-owned policy, no human typing). "
            "Applies only with --embedded-smoke."
        ),
    )
    args = parser.parse_args()
    if args.fixture and args.embedded_smoke:
        parser.error("--fixture and --embedded-smoke cannot be combined")
    if args.profile is not None and (args.fixture or args.embedded_smoke):
        parser.error("--profile applies only to the default Gateway observer mode")
    if args.auto and not args.embedded_smoke:
        parser.error("--auto applies only with --embedded-smoke")
    mode: Literal["fixture", "gateway", "embedded_smoke"]
    if args.fixture:
        mode = "fixture"
    elif args.embedded_smoke:
        mode = "embedded_smoke"
    else:
        mode = "gateway"
    app = DeepResearchDemoTUI(mode=mode, profile=args.profile, auto=args.auto)
    try:
        app.run()
    finally:
        app._close_adapter()


if __name__ == "__main__":
    main()
