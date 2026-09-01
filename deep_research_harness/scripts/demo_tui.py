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
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, TextIO

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
    ContinueRun,
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
from deerflow_deep_research.domain.session_workbench import WorkbenchAvailability
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


def _latest_active_bundle(bundle_root: Path | None) -> Path | None:
    """Locate the newest in-flight (active or suspended) bundle, if any."""
    if bundle_root is None:
        return None
    scopes_dir = bundle_root / "workspace" / "deep-research" / "scopes"
    if not scopes_dir.is_dir():
        return None
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
            if data.get("status") not in ("active", "suspended"):
                continue
            candidates.append((str(data.get("updated_at", "")), bundle))
    if not candidates:
        return None
    return max(candidates)[1]


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
    bundle = _latest_active_bundle(bundle_root)
    if bundle is None:
        return ()
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

    # User-visible pipeline (internal auto/script phases and reruns are hidden).
    pipeline = tuple(
        phase
        for phase in PHASE_META
        if not phase.endswith(("_auto_profile", "_auto_proceed")) and phase not in {"bootstrap", "rerun"}
    )
    lines: list[str] = []
    if done or last_node_phase:
        deduped = list(dict.fromkeys(done))  # dedupe repeated phases
        in_flight = last_node_outcome == "started" and last_node_phase is not None
        if in_flight and (not deduped or last_node_phase != deduped[-1]):
            chain = " → ".join(deduped)
            chain = f"{chain} → {last_node_phase}（进行中）" if chain else f"{last_node_phase}（进行中）"
        else:
            chain = " → ".join(deduped)
        lines.append(f"进度: {chain}")
        # "What comes next": show the remaining pipeline so the operator knows
        # the run is still alive and how far it still has to go, instead of
        # staring at a static "in progress" line and assuming it died.
        remaining = [
            phase for phase in pipeline if phase not in done and (phase != last_node_phase if in_flight else True)
        ]
        if remaining:
            lines.append(f"接下来: {' → '.join(remaining)}")
    if last_event is not None:
        stamp = _format_timestamp(last_event.get("timestamp"))
        phase = str(last_event.get("phase") or "")
        category = str(last_event.get("category") or "")
        outcome = str(last_event.get("outcome") or "")
        lines.append(f"最近: {stamp} · {phase} {category} {outcome}".rstrip())
    # Counters and elapsed seconds are deliberately omitted: what matters is
    # "what is it doing", not how many tokens/events/seconds have passed.
    return tuple(lines)


_RESEARCH_TRIGGER_PHRASES = frozenset(
    {
        "start deep research",
        "deep research",
        "go deep research",
        "开始 deep research",
        "开始深度研究",
        "deep research 开始",
        "我要让你 deep research",
        "开始 deep research 吧",
    }
)


_RECON_SYSTEM_PROMPT = (
    "你是 Deep Research 工作台的侦察助手（020 手动 TUI 的启动阶段）。"
    "用户还没有启动正式研究，正在看环境或和你闲聊。"
    "你有三个只读工具可以查看本地 workspace：list_workspace（列目录）、"
    "read_workspace_file（预览文件）、inspect_bundle（bundle 摘要）。"
    "用户问 workspace 里有什么、某个 run/bundle 在哪、文件内容等，就调用工具查"
    "真实文件系统来回答，不要猜。"
    "规则：用户说「开始 Deep Research」（或 start deep research）会触发正式研究，"
    "那由界面处理——你只在被问到时说明这个规则。"
    "回答保持简洁（3-6 句）；不要替用户做研究。"
)

_HITL1_QUICK_REVISIONS = {
    "depth-quick": {"label": "深度: 快速概览", "value": "depth: quick_overview"},
    "depth-deep": {"label": "深度: 深入", "value": "depth: deep_dive"},
    "audience-general": {"label": "受众: 普通读者", "value": "audience: layperson"},
    "audience-expert": {"label": "受众: 领域专家", "value": "audience: domain_expert"},
}


def is_research_trigger(text: str) -> bool:
    """True only when the whole line is an explicit research-start command.

    Exact whole-line matching protects the control environment: casual chat
    (questions containing "deep research") never starts a run.
    """
    normalized = " ".join(text.strip().lower().split()).strip("?？。.!！")
    return normalized in _RESEARCH_TRIGGER_PHRASES


def is_env_inspect(text: str) -> bool:
    """True when the line asks to inspect the local environment."""
    normalized = " ".join(text.strip().lower().split())
    if normalized in {
        "env",
        "ls",
        "list",
        "inspect",
        "环境",
        "看看环境",
        "看环境",
        "跑过什么",
        "workspace",
        "工作区",
    }:
        return True
    return any(
        token in normalized for token in ("环境", "bundle", "日志", "where", "在哪", "run 在哪", "workspace", "工作区")
    )


def _safe_workspace_path(workspace: Path, raw: str) -> Path | None:
    """Resolve a workspace-relative path with escape containment (read-only)."""
    candidate = (workspace / raw.strip("/")).resolve()
    try:
        candidate.relative_to(workspace.resolve())
    except ValueError:
        return None
    return candidate


def _recon_tools(workspace: Path) -> list[Any]:
    """Read-only workspace tools bound to the recon chat model.

    The chat model may inspect the same retained-run workspace the operator
    sees: list directories, preview files, summarize bundles. All paths are
    workspace-relative and containment-checked; nothing is writable.
    """
    from langchain_core.tools import tool

    @tool
    def list_workspace(path: str = "") -> str:
        """List a directory inside the local Deep Research workspace.
        `path` is relative to the workspace root; empty string lists the root."""
        target = _safe_workspace_path(workspace, path) if path else workspace
        if target is None:
            return "路径越界：只允许 workspace 内的相对路径。"
        if not target.exists():
            return f"不存在: {path or '/'}"
        if not target.is_dir():
            return "目标是文件，请用 read_workspace_file 读取。"
        return "\n".join(_list_directory(target, workspace))

    @tool
    def read_workspace_file(path: str) -> str:
        """Preview a text file inside the workspace (bounded).
        Example: deep-research/scopes/<scope>/<bundle>/state.json"""
        target = _safe_workspace_path(workspace, path)
        if target is None:
            return "路径越界：只允许 workspace 内的相对路径。"
        if not target.is_file():
            return f"不是文件或不存在: {path}"
        return "\n".join(_cat_file(target, workspace))

    @tool
    def inspect_bundle(bundle_id: str) -> str:
        """Summarize one retained run bundle by its id (b_...)."""
        bundle_dir = find_bundle_dir(workspace.parent, bundle_id)
        if bundle_dir is None:
            return f"未找到 bundle: {bundle_id}。可用 list_workspace 查看 deep-research/scopes 下有哪些。"
        return "\n".join(_inspect_bundle(bundle_dir))

    return [list_workspace, read_workspace_file, inspect_bundle]


def _event_to_feed_line(event: dict[str, object]) -> str | None:
    """One journal event -> one rolling feed line (or None to skip)."""
    category = event.get("category")
    outcome = event.get("outcome", "")
    phase = str(event.get("phase") or "")
    stamp = _format_timestamp(event.get("timestamp"))
    if category == "model_tool" and outcome == "completed":
        usage = event.get("usage_tokens") or {}
        total = usage.get("total_tokens")
        token_note = f" · {total / 1000:.1f}k tokens" if isinstance(total, (int, float)) else ""
        return f"{stamp} {phase} 模型调用完成{token_note}"
    if category == "model_tool" and outcome == "started":
        ordinal = event.get("call_ordinal")
        return f"{stamp} {phase} 模型调用 #{ordinal} 开始" if ordinal else f"{stamp} {phase} 模型调用开始"
    if category == "submit":
        size = event.get("result_byte_count")
        checks = event.get("passed_checks")
        size_note = f" · {size / 1000:.1f}KB" if isinstance(size, (int, float)) else ""
        check_note = f" · {len(checks)} 项检查通过" if isinstance(checks, (list, tuple)) else ""
        return f"{stamp} {phase} 提交结果{size_note}{check_note}"
    if category == "validation":
        return f"{stamp} {phase} 验证通过"
    if category == "node" and outcome == "completed":
        return f"{stamp} ✓ {phase} 完成"
    if category == "node" and outcome == "failed":
        return f"{stamp} ⚠ {phase} 失败（重试中）"
    if category == "terminal" and outcome == "completed":
        return f"{stamp} 🏁 {phase} 结束"
    return None


def _event_feed_lines(bundle_root: Path | None, *, limit: int = 6) -> tuple[str, ...]:
    """Human-readable recent event feed from the in-flight bundle journal."""
    bundle = _latest_active_bundle(bundle_root)
    if bundle is None:
        return ()
    events_file = bundle / "diagnostics" / "events.jsonl"
    try:
        raw = events_file.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ()
    lines: list[str] = []
    for line in reversed(raw):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        feed_line = _event_to_feed_line(event)
        if feed_line is not None:
            lines.append(feed_line)
        if len(lines) >= limit:
            break
    return tuple(reversed(lines))


def _last_model_call_state(bundle_root: Path) -> tuple[str | None, float]:
    """(started|completed|None, epoch seconds of that event) from the journal tail."""
    if bundle_root is None:
        return None, 0.0
    events_path = bundle_root / "workspace" / "deep-research" / "scopes"
    # find the most recently updated active bundle journal, like live_progress_lines
    latest: tuple[str, Path] | None = None
    if events_path.is_dir():
        for scope in events_path.iterdir():
            if not scope.is_dir():
                continue
            for bundle in scope.iterdir():
                summary = bundle / "diagnostics" / "run-summary.json"
                try:
                    data = json.loads(summary.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                if data.get("status") not in ("active", "suspended"):
                    continue
                stamp = str(data.get("updated_at", ""))
                if latest is None or stamp > latest[0]:
                    latest = (stamp, bundle)
    if latest is None:
        return None, 0.0
    events_file = latest[1] / "diagnostics" / "events.jsonl"
    try:
        raw = events_file.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None, 0.0
    outcome: str | None = None
    stamp = 0.0
    for line in reversed(raw[-40:]):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("category") == "model_tool":
            outcome = event.get("outcome")
            ts = event.get("timestamp")
            if isinstance(ts, str):
                try:
                    stamp = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
                except ValueError:
                    stamp = 0.0
            break
    return outcome, stamp


def _list_directory(path: Path, workspace: Path) -> tuple[str, ...]:
    """One human-readable directory listing (entries + size + mtime)."""
    lines: list[str] = [f"📁 {path.relative_to(workspace) if path != workspace else '/'}"]
    try:
        entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except OSError as exc:
        return (f"读取失败: {exc}",)
    if not entries:
        lines.append("  （空）")
    for entry in entries:
        try:
            if entry.is_dir():
                count = sum(1 for _ in entry.iterdir())
                lines.append(f"  📁 {entry.name}/  ({count} 项)")
            else:
                size = entry.stat().st_size
                lines.append(f"  📄 {entry.name}  ({size}B)")
        except OSError:
            lines.append(f"  ? {entry.name}")
    return tuple(lines)


def _cat_file(path: Path, workspace: Path) -> tuple[str, ...]:
    """Preview a file's content (bounded; JSON pretty-printed, journal tailed)."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        return (f"读取失败: {exc}",)
    relative = path.relative_to(workspace) if path != workspace else path.name
    name = path.name
    if name in {"state.json", "run-summary.json", "journal-manifest.json", "manifest.json"}:
        try:
            pretty = json.dumps(json.loads(raw), ensure_ascii=False, indent=1)
        except ValueError:
            pretty = raw
        return (f"── {relative} ──", *pretty.splitlines()[:60])
    if name.endswith(".jsonl"):
        tail = raw.splitlines()[-15:]
        return (f"── {relative}（尾部 {len(tail)} 行）──", *tail)
    lines = raw.splitlines()
    return (f"── {relative}（{len(lines)} 行）──", *lines[:40])


def _inspect_bundle(bundle_dir: Path) -> tuple[str, ...]:
    """One bundle summary: terminal state, journal health, work units, report."""
    lines: list[str] = [f"bundle: {bundle_dir.name}"]
    state_path = bundle_dir / "state.json"
    if state_path.is_file():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            lines.append(
                f"  状态: {state.get('terminal_status') or 'active'} · phase {state.get('phase')} "
                f"{state.get('phase_status')} · hitl1 访问 {state.get('hitl1_visit_count', 0)}"
            )
            question = state.get("must_answer_questions") or ()
            if question:
                lines.append(f"  问题: {str(question[0])[:90]}")
        except (OSError, ValueError):
            lines.append("  state.json 不可读")
    summary = bundle_dir / "diagnostics" / "run-summary.json"
    if summary.is_file():
        try:
            data = json.loads(summary.read_text(encoding="utf-8"))
            lines.append(
                f"  journal: {data.get('journal_availability')} · 事件 {data.get('latest_event_sequence')} · "
                f"dropped {data.get('dropped_event_count')}"
            )
        except (OSError, ValueError):
            pass
    work = bundle_dir / "work"
    if work.is_dir():
        units = sorted(p.name for p in work.iterdir() if p.is_dir())
        if units:
            lines.append(f"  work: {', '.join(units[:6])}")
    report = bundle_dir / "final" / "report.md"
    lines.append(f"  报告: {report if report.is_file() else '(未产出)'}")
    lines.append(f'  详情: `make demo-sessions DEMO_ARGS="inspect {bundle_dir.name}"`')
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
    last_typed: str | None = None,
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
        # The journal-backed progress lines carry the real activity. The
        # bridge's static "waiting for lifecycle result" message and the stale
        # "last confirmed phase" (frozen during dispatch) are misleading, so
        # they are not rendered.
        details = [*progress]
        if update.snapshot.bundle_id:
            details.append(f"Run Bundle: {update.snapshot.bundle_id}")
        if update.snapshot.lifecycle_phase:
            details.append(f"上次确认阶段: {update.snapshot.lifecycle_phase}")
        return TuiRenderedUpdate(
            heading="研究进行中",
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
            example = prompt.options[0].id if prompt.options else "advertised"
            details.append(f"The last choice was invalid. Enter an advertised option ID, for example {example}.")
        elif prompt.rejection_category:
            details.append("未识别上次输入。")
            if last_typed:
                details.append(f"你输入的是: {last_typed}")
            details.append(
                "可用格式: `字段: 值`（如 depth: quick overview）、`confirm`、或完整 JSON（见 Example）；"
                "也可以点下方快捷按钮。"
            )
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
    #inspect { height: auto; max-height: 12; margin: 0 2; padding: 0 1; border: round #334155; color: #a5f3fc; }
    #prompt { height: auto; margin: 0 2; color: #fde68a; text-style: bold; }
    #controls { height: 3; margin: 0 2 1 2; }
    #composer { width: 1fr; }
    #start-research { width: 24; margin-left: 1; }
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
        self._onboarding = False
        self._chat_model: Any | None = None
        self._chat_history: list[tuple[str, str]] = []
        self._last_terminal_bundle: str | None = None
        self._recoverable_bundle_id: str | None = None
        self._recoverable_phase = "unknown"
        self._last_typed = ""
        self._pending_timer: Any | None = None
        self._pending_started = 0.0
        self._feed_watermark = 0

    def compose(self) -> ComposeResult:
        yield Static(id="banner")
        yield Static(id="pipeline")
        yield RichLog(id="log", wrap=True, markup=False, max_lines=100)
        yield Static(id="inspect")
        yield Static(id="prompt")
        with Horizontal(id="options"):
            for language in SupportedLanguageOption:
                yield Button(language.value, id=f"option-{language.value}", classes="advertised-option")
            for revision_id in _HITL1_QUICK_REVISIONS:
                yield Button("", id=f"revision-{revision_id}", classes="advertised-option")
        with Horizontal(id="controls"):
            yield Input(value=self._EXAMPLE_QUESTION, placeholder="Research question", id="composer")
            yield Button("Start Deep Research", id="start-research")
            yield Button("Copy details", id="copy-details")
            yield Button("Start proposal", id="accept")
            yield Button("Cancel", id="cancel", variant="error")
        yield Static(
            "「Start Deep Research」按钮启动研究 · 中间对话区: 双击=复制全文 · "
            "Option+拖拽=选中一段 · Copy details=复制全部 · Ctrl-C 退出",
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
                self._dispatch(StartRun(question=self.AUTO_QUESTION, scripted=True, profile_intent=None))
            elif self.mode == "embedded_smoke":
                # 020 manual TUI: start in recon mode. The operator may inspect
                # the environment and chat freely; only an explicit
                # research-start phrase dispatches the fixed question.
                self._onboarding = True
                await self._scan_recoverable_run()
                self._render_recon()
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
            last_typed=self._last_typed,
        )
        self._render_view(view)
        self._last_detail = view.detail
        self._append_tui_log(view.detail)
        self._render_interaction_status(update)
        if isinstance(update, Working) and self.mode == "embedded_smoke" and not self.auto:
            self._render_live_activity()
        if isinstance(update, Terminal) and self.mode == "embedded_smoke" and not self.auto:
            # Research ended (completed/blocked/cancelled/stopped): return to
            # recon mode and say clearly what happened — never dress a blocked
            # run up as "completed".
            self._onboarding = True
            self._last_terminal_bundle = update.snapshot.bundle_id
            self._render_recon(terminal=update)

    def _render_view(self, view: TuiRenderedUpdate) -> None:
        self.last_view = view
        composer = self.query_one("#composer", Input)
        cancel = self.query_one("#cancel", Button)
        accept = self.query_one("#accept", Button)
        self.query_one("#prompt", Static).update(Text(view.heading, style="bold yellow"))
        if isinstance(self.last_update, Working):
            # #log is the rolling event feed during research: never clear it.
            pass
        else:
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
        start_button = self.query_one("#start-research", Button)
        start_button.display = self._onboarding
        start_button.disabled = not self._onboarding
        accept.display = bool(
            isinstance(self.last_update, AwaitingInput)
            and any(control.id == "accept_current_proposal" for control in self.last_update.prompt.visible_controls)
        )
        accept.disabled = not accept.display
        advertised_options = self._advertised_options()
        options_bar = self.query_one("#options", Horizontal)
        options_bar.display = bool(advertised_options)
        for button in options_bar.query(Button):
            key = str(button.id).removeprefix("option-").removeprefix("revision-")
            option = advertised_options.get(key)
            button.display = option is not None
            button.disabled = option is None
            if option is not None:
                button.label = option.label if hasattr(option, "label") else option["label"]
        if view.accepts_input:
            if self._onboarding:
                composer.value = ""
            elif isinstance(self.last_update, Ready):
                composer.value = self.AUTO_QUESTION if self.mode == "embedded_smoke" else self._EXAMPLE_QUESTION
            else:
                composer.value = ""
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

    def _hitl1_quick_revisions(self) -> dict[str, dict[str, str]]:
        """Advertise bounded one-field revision buttons for a hitl1 text prompt."""

        if not isinstance(self.last_update, AwaitingInput):
            return {}
        prompt = self.last_update.prompt
        if prompt.mode != "text" or prompt.phase != "hitl1":
            return {}
        return dict(_HITL1_QUICK_REVISIONS)

    def _advertised_options(self) -> dict[str, object]:
        """Merge language CHOICE options with hitl1 quick-revision buttons."""

        options: dict[str, object] = dict(self._advertised_language_options())
        options.update(self._hitl1_quick_revisions())
        return options

    def _select_advertised_option(self, option_id: str) -> None:
        """Submit one currently advertised option: a typed OPTION or a text revision."""

        options = self._advertised_options()
        if option_id not in options:
            return
        option = options[option_id]
        if isinstance(option, dict):
            self._dispatch(AnswerRun(value=option["value"], response_kind="text"))
        else:
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

    def _echo_input(self, value: str) -> None:
        """Persistently echo the operator's latest input into the #inspect panel.

        The #log area is cleared by every Working heartbeat render, so an echo
        written there vanishes within a second — the exact "I typed it but
        nothing happened" failure. The #inspect panel is never cleared by
        renders, so the operator always sees their latest input and its status.
        """
        self._last_typed = value
        if self._onboarding:
            self._render_inspect((f"你: {value}",))
            return
        self._start_pending_timer()
        self._render_inspect((f"你: {value}", "（已收到，正在处理…）"))

    def _start_pending_timer(self) -> None:
        """Tick the "processing… Ns" line so a slow intake is visibly alive."""
        self._pending_started = time.monotonic()
        if self._pending_timer is not None:
            self._pending_timer.stop()
        self._pending_timer = self.set_interval(1.0, self._tick_pending)

    def _stop_pending_timer(self) -> None:
        if self._pending_timer is not None:
            self._pending_timer.stop()
            self._pending_timer = None

    def _tick_pending(self) -> None:
        if self._onboarding or not self._last_typed:
            return
        self._render_inspect(
            (
                f"你: {self._last_typed}",
                f"（已收到，正在处理… {int(time.monotonic() - self._pending_started)}s）",
            )
        )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        raw_value = event.value
        value = raw_value.strip()
        if not value:
            return
        if value.startswith("/"):
            # Global inspect commands work at any time (recon or mid-research)
            # and are never routed as chat or research answers.
            self._handle_slash_command(value)
            return
        self._echo_input(value)
        if self._onboarding:
            await self._handle_onboarding_input(value)
            return
        if self.last_update is None:
            return
        if isinstance(self.last_update, Ready) and self.last_update.report.ready:
            self._dispatch(StartRun(question=value))
        elif isinstance(self.last_update, AwaitingInput):
            prompt = self.last_update.prompt
            if prompt.mode == "choice":
                # The shared contract requires a typed OPTION for every CHOICE
                # prompt; an exact match of one advertised option id is the only
                # legal composer entry, and any other text dispatches nothing.
                if prompt.phase == "hitl1" and value in self._advertised_language_options():
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

    async def _scan_recoverable_run(self) -> None:
        """Project one recoverable orphan (legal next action = resume) for attach.

        Presentation only (RED-011): the lifecycle owns recovery semantics; this
        scan renders what the lifecycle already judged legal, best effort.
        """
        adapter = self._adapter
        if adapter is None:
            return
        try:
            workbench = adapter.local_bundle_workbench()
            found = await workbench.discover()
        except Exception:
            return
        for item in found:
            action = item.legal_next_action
            if item.bundle_id is not None and action is not None and action.value == "resume":
                self._recoverable_bundle_id = item.bundle_id.value
                self._recoverable_phase = item.phase.value if item.phase is not None else "unknown"
                return

    def _attach_card_lines(self) -> tuple[str, ...]:
        if self._recoverable_bundle_id is None:
            return ()
        short = self._recoverable_bundle_id[:16]
        return (
            f"· 📎 检测到未完成的研究: {short}…（阶段: {self._recoverable_phase}，证据已保存）",
            "  输入「继续」从断点恢复 · 「查看」检查诊断 · 「新跑」放弃并重新开始",
        )

    async def _show_recoverable_summary(self) -> None:
        """Render the read-only diagnosis of the recoverable bundle, best effort."""
        adapter = self._adapter
        bid = self._recoverable_bundle_id
        if adapter is None or bid is None:
            return
        log = self.query_one("#log", RichLog)
        log.write(Text("── 未完成研究诊断 ──", style="bold"))
        try:
            workbench = adapter.local_bundle_workbench()
            diagnosis = await workbench.diagnosis(bundle_id=bid)
        except Exception:
            log.write(Text("· 诊断暂不可用。", style="dim"))
            return
        summary = diagnosis.summary
        if diagnosis.availability is not WorkbenchAvailability.AVAILABLE or summary is None:
            log.write(Text("· journal 暂不可读（可能正被另一进程使用）。", style="dim"))
            return
        log.write(Text(f"· 状态: {summary.status}@{summary.phase} generation {summary.generation}", style="dim"))
        journal = summary.journal_availability.value
        log.write(Text(f"· journal: {journal} · 事件 {len(diagnosis.events)} 条", style="dim"))

    def _render_recon(self, *, terminal: Terminal | None = None) -> None:
        """Render the 020 recon-mode screen (before and after each research run).

        When a terminal result is provided, its outcome is stated honestly:
        completed shows the report, blocked shows the failure reason and next
        step — a blocked run is never dressed up as "completed".
        """
        adapter = self._adapter
        root = getattr(adapter, "bundle_root", None) if adapter is not None else None
        lines: list[str] = []
        if terminal is not None:
            if terminal.outcome == "completed":
                lines.append("上一轮研究已完成，你现在回到侦察模式。")
                if self._last_terminal_bundle and root is not None:
                    report = report_path(root, self._last_terminal_bundle)
                    if report is not None:
                        lines.append(f"· 报告: {report}")
            elif terminal.outcome == "blocked":
                lines.append("⚠ 上一轮研究失败（blocked），你现在回到侦察模式。")
                reason = (
                    terminal.failure.message
                    if terminal.failure is not None and terminal.failure.message
                    else "未知原因（见诊断记录）"
                )
                lines.append(f"  原因: {reason}")
                lines.append("  下一步: 调整研究范围/预算后重新触发；或 /inspect 查看失败现场。")
            elif terminal.outcome == "cancelled":
                lines.append("上一轮研究已取消，你现在回到侦察模式。")
            else:
                lines.append("上一轮研究已停止，你现在回到侦察模式。")
            lines.append("")
        lines.extend(
            [
                "这是 Deep Research 手动 TUI（020）的侦察模式——看环境、闲聊，都不会启动正式研究。",
                "",
                "· 看环境 / workspace / 之前跑过什么: 输入 `环境` 或 `env`（显示 workspace 路径与结构）",
                "· 随时查文件系统（研究中也能用）: `/ls [路径]` · `/cat <文件>` · `/inspect <bundle_id>` · `/clear`",
                "· 随便聊: 直接输入任何内容（真模型低成本回应）",
                "· 启动正式 Deep Research: 点「Start Deep Research」按钮，或输入「开始 Deep Research」",
                "  — 触发后运行固定问题: What is one bounded fact about China's EV battery market in 2024?",
            ]
        )
        lines.extend(self._attach_card_lines())
        if self._last_terminal_bundle:
            lines.append(f"· 上一轮研究 bundle: {self._last_terminal_bundle}")
        if root is not None:
            lines.append(f"· bundle 根: {root}")
        if self._tui_log_path is not None:
            lines.append(f"· TUI 日志: {self._tui_log_path}")
        view = TuiRenderedUpdate(
            heading="侦察模式 · 看环境 / 闲聊 / 点「Start Deep Research」或说触发语启动研究",
            detail="\n".join(lines),
            placeholder="随便聊，或说「开始 Deep Research」",
            completed_trace=(),
            pending_phase=None,
            options=(),
            accepts_input=True,
            show_cancel=False,
            terminal=False,
        )
        self._render_view(view)
        self._last_detail = view.detail
        self._append_tui_log(view.detail)

    def _start_research(self) -> None:
        """Explicit operator command: leave recon mode and start the fixed research."""
        if not self._onboarding:
            return
        self._onboarding = False
        self._dispatch(StartRun(question=self.AUTO_QUESTION, scripted=False))

    def _write_env_summary(self) -> None:
        """Print a bounded local-environment / workspace summary into the log."""
        adapter = self._adapter
        root = getattr(adapter, "bundle_root", None) if adapter is not None else None
        log = self.query_one("#log", RichLog)
        log.write(Text("── 本地环境 / workspace ──", style="bold"))
        if root is None:
            log.write(Text("（无本地 bundle 根：非 embedded 模式）", style="dim"))
            return
        log.write(Text(f"bundle 根: {root}", style="dim"))
        workspace = root / "workspace"
        log.write(Text(f"workspace: {workspace}", style="dim"))
        for name in ("deep-research", "scripted-real", "soft-bundles", "archive"):
            sub = workspace / name
            if not sub.is_dir():
                continue
            if name == "deep-research":
                scopes = [p for p in sub.iterdir() if p.is_dir()]
                bundles = [b for scope in scopes for b in scope.iterdir() if b.is_dir()]
                log.write(Text(f"  {name}/: {len(scopes)} scopes · {len(bundles)} bundles", style="dim"))
            elif name == "soft-bundles":
                entries = [p for p in sub.iterdir() if p.is_dir()]
                log.write(Text(f"  {name}/: {len(entries)} soft-bundle 会话", style="dim"))
            else:
                entries = [p for p in sub.iterdir()]
                log.write(Text(f"  {name}/: {len(entries)} 项", style="dim"))
        scopes_dir = workspace / "deep-research" / "scopes"
        if scopes_dir.is_dir():
            bundles = sorted(
                (b for scope in scopes_dir.iterdir() if scope.is_dir() for b in scope.iterdir() if b.is_dir()),
                key=lambda b: b.stat().st_mtime_ns,
                reverse=True,
            )
            if bundles:
                log.write(Text(f"保留的 run bundle: {len(bundles)} 个 · 最近 3 个：", style="dim"))
                for bundle in bundles[:3]:
                    terminal = "?"
                    try:
                        terminal = (
                            json.loads((bundle / "state.json").read_text(encoding="utf-8")).get("terminal_status")
                            or "active"
                        )
                    except (OSError, ValueError):
                        pass
                    report_note = " · 有报告" if (bundle / "final" / "report.md").is_file() else ""
                    log.write(Text(f"  {bundle.name}  [{terminal}]{report_note}", style="dim"))
        logs_dir = root / "logs"
        if logs_dir.is_dir():
            tui_logs = sorted(logs_dir.glob("tui-*.log"), key=lambda p: p.stat().st_mtime_ns, reverse=True)
            if tui_logs:
                log.write(Text(f"TUI 日志: {tui_logs[0]}", style="dim"))
        log.write(Text('用 `make demo-sessions DEMO_ARGS="inspect <bundle_id>"` 检查某个 bundle。', style="dim"))

    def _build_chat_model(self) -> None:
        if self._chat_model is not None:
            return
        try:
            from _demo_core import resolve_real_demo_model_profile
            from deerflow.models.patched_deepseek import PatchedChatDeepSeek

            profile = resolve_real_demo_model_profile()
            if profile is None:
                return
            config = profile.model_config
            self._chat_model = PatchedChatDeepSeek(
                api_key=config.api_key,
                model=config.model,
                base_url=getattr(config, "base_url", None),
            )
        except Exception:
            self._chat_model = None

    async def _chat_reply(self, value: str) -> None:
        """One bounded recon-mode chat turn with the low-cost demo model.

        The model is bound to read-only workspace tools, so natural-language
        questions about the workspace ("what is in it", "where is my last run")
        are answered from the real file system, not guessed.
        """
        log = self.query_one("#log", RichLog)
        log.write(Text(f"你: {value}", style="bold"))
        self._build_chat_model()
        if self._chat_model is None:
            log.write(Text("（没有可用的侦察模型——只说「开始 Deep Research」也能进入研究）", style="dim"))
            return
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

        self._chat_history.append(("user", value))
        messages = [SystemMessage(content=_RECON_SYSTEM_PROMPT)]
        for role, content in self._chat_history[-10:]:
            messages.append(HumanMessage(content=content) if role == "user" else AIMessage(content=content))
        try:
            workspace = self._inspect_workspace_root()
            tools = _recon_tools(workspace) if workspace is not None else []
            model = self._chat_model.bind_tools(tools) if tools else self._chat_model
            text = await self._stream_turn(model, messages, tools, echo=f"你: {value}")
            self._chat_history.append(("assistant", text))
            log.write(Text(f"AI: {text}", style="cyan"))
        except Exception as exc:
            log.write(Text(f"（侦察对话调用失败: {type(exc).__name__}）", style="red"))

    async def _stream_turn(
        self,
        model: Any,
        messages: list[Any],
        tools: list[Any],
        *,
        echo: str,
    ) -> str:
        """Stream one chat turn; tool calls are executed inline as they arrive.

        Every content chunk is rendered into the persistent #inspect panel
        immediately (no waiting for the full answer), while tool-call chunks
        are accumulated, executed, fed back as ToolMessages, and the stream
        continues.
        """
        from langchain_core.messages import AIMessage, ToolMessage

        tools_map = {tool.name: tool for tool in tools}
        text_parts: list[str] = []
        tool_calls: dict[int, dict[str, Any]] = {}
        for _round in range(3):
            async for chunk in model.astream(messages):
                content = getattr(chunk, "content", chunk)
                if isinstance(content, str) and content:
                    text_parts.append(content)
                    self._render_inspect((echo, f"AI: {''.join(text_parts)}"))
                for call in getattr(chunk, "tool_calls", None) or ():
                    index = call.get("index", 0)
                    tool_calls[index] = call
            if not tool_calls:
                return "".join(text_parts)
            messages.append(
                AIMessage(
                    content="".join(text_parts),
                    tool_calls=[
                        {k: v for k, v in call.items() if k not in {"index", "type", "extras"}}
                        for call in tool_calls.values()
                    ],
                )
            )
            for call in tool_calls.values():
                result = "（未知工具）"
                tool = tools_map.get(call.get("name", ""))
                if tool is not None:
                    try:
                        result = tool.invoke(call.get("args") or {})
                    except Exception as exc:
                        result = f"工具调用失败: {type(exc).__name__}: {exc}"
                messages.append(ToolMessage(content=str(result), tool_call_id=call.get("id", "")))
            text_parts = []
            tool_calls = {}
        return "".join(text_parts)

    def _render_live_activity(self) -> None:
        """Roll research activity like a coding-agent terminal.

        Every new journal event is appended to #log (a true scrolling feed,
        never cleared during research); #inspect shows the semantic status:
        progress chain, what comes next, and what is happening right now.
        """
        adapter = self._adapter
        root = getattr(adapter, "bundle_root", None) if adapter is not None else None
        bundle = _latest_active_bundle(root)
        if bundle is None:
            return
        events_file = bundle / "diagnostics" / "events.jsonl"
        try:
            raw = events_file.read_text(encoding="utf-8").splitlines()
        except OSError:
            return
        log = self.query_one("#log", RichLog)
        for line in raw[self._feed_watermark :]:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            feed_line = _event_to_feed_line(event)
            if feed_line is not None:
                log.write(Text(feed_line, style="dim"))
        self._feed_watermark = len(raw)

        progress = list(live_progress_lines(root))
        if not progress:
            return
        outcome, _stamp = _last_model_call_state(root)
        lines = list(progress)
        if outcome == "started":
            lines.append("⚙ 正在: 模型调用中")
        elif outcome == "completed":
            lines.append("⚙ 正在: 处理模型结果")
        self._render_inspect(tuple(lines))

    def _render_interaction_status(self, update: RunUpdate) -> None:
        """Keep the operator's latest input and the system's understanding visible.

        Written into the persistent #inspect panel so it survives Working
        heartbeats; the operator always sees "you said X -> system heard Y".
        """
        if not self._last_typed:
            return
        self._stop_pending_timer()
        if isinstance(update, AwaitingInput):
            prompt = update.prompt
            lines = [f"你: {self._last_typed}"]
            if prompt.rejection_category:
                lines.append("系统: 未识别你的输入——见下方格式指引与按钮。")
            elif prompt.interaction is not None and prompt.interaction.feedback is not None:
                lines.append(f"系统: {prompt.interaction.feedback.message}")
            else:
                lines.append("系统: 已收到，请按提示继续。")
            self._render_inspect(tuple(lines))
        elif isinstance(update, Fault) or isinstance(update, Terminal):
            self._render_inspect(())

    def _render_inspect(self, lines: Sequence[str]) -> None:
        """Render inspect output into the persistent #inspect panel (never cleared by heartbeats)."""
        if not lines:
            self.query_one("#inspect", Static).update("")
            return
        self.query_one("#inspect", Static).update(Text("\n".join(lines)))

    def _inspect_workspace_root(self) -> Path | None:
        adapter = self._adapter
        root = getattr(adapter, "bundle_root", None) if adapter is not None else None
        return root / "workspace" if root is not None else None

    def _resolve_inspect_path(self, raw: str) -> Path | None:
        """Resolve a workspace-relative path with escape containment."""
        workspace = self._inspect_workspace_root()
        if workspace is None:
            return None
        candidate = (workspace / raw.strip("/")).resolve()
        try:
            candidate.relative_to(workspace.resolve())
        except ValueError:
            return None
        return candidate

    def _handle_slash_command(self, value: str) -> None:
        """Global inspect commands: /ls, /cat, /inspect, /clear.

        Available at any time (recon or mid-research); never routed as a chat or
        research answer. All paths are workspace-relative and containment-checked.
        """
        parts = value.split(maxsplit=1)
        command = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""
        workspace = self._inspect_workspace_root()
        if command == "/clear":
            self._render_inspect(())
            return
        if workspace is None:
            self._render_inspect(("（无本地 workspace：非 embedded 模式）",))
            return
        if command in {"/ls", "/env", "/workspace"}:
            target = self._resolve_inspect_path(arg) if arg else workspace
            if target is None:
                self._render_inspect((f"路径越界或不存在: {arg or '/'}",))
                return
            if not target.exists():
                self._render_inspect((f"不存在: {target.relative_to(workspace)}",))
                return
            self._render_inspect(_list_directory(target, workspace))
            return
        if command == "/cat":
            target = self._resolve_inspect_path(arg) if arg else None
            if target is None or not target.is_file():
                self._render_inspect(("用法: /cat <workspace 相对路径，指向文件>",))
                return
            self._render_inspect(_cat_file(target, workspace))
            return
        if command == "/inspect":
            if not arg:
                self._render_inspect(("用法: /inspect <bundle_id>",))
                return
            bundle_dir = find_bundle_dir(self._adapter.bundle_root if self._adapter is not None else None, arg)
            if bundle_dir is None:
                self._render_inspect((f"未找到 bundle: {arg}",))
                return
            self._render_inspect(_inspect_bundle(bundle_dir))
            return
        self._render_inspect(("支持: /ls [路径] · /cat <文件> · /inspect <bundle_id> · /clear",))

    async def _handle_onboarding_input(self, value: str) -> None:
        if self._recoverable_bundle_id is not None and value == "继续":
            bundle_id = self._recoverable_bundle_id
            self._recoverable_bundle_id = None
            self._dispatch(ContinueRun(bundle_id=bundle_id))
            return
        if self._recoverable_bundle_id is not None and value == "查看":
            await self._show_recoverable_summary()
            return
        if self._recoverable_bundle_id is not None and value == "新跑":
            self._recoverable_bundle_id = None
            self._render_recon()
            return
        if is_research_trigger(value):
            self._start_research()
            return
        if is_env_inspect(value):
            self._write_env_summary()
            return
        await self._chat_reply(value)

    def on_double_click(self, event: events.DoubleClick) -> None:
        """Double-clicking the middle log copies the full conversation text."""
        if event.widget is not None and event.widget.id == "log":
            self._copy_details()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "accept":
            self._select_current_proposal()
        elif event.button.id == "start-research":
            self._start_research()
        elif event.button.id == "copy-details":
            self._copy_details()
        elif event.button.id is not None and (
            event.button.id.startswith("option-") or event.button.id.startswith("revision-")
        ):
            key = event.button.id.removeprefix("option-").removeprefix("revision-")
            self._select_advertised_option(key)
        elif event.button.id == "cancel" and self.mode != "gateway" and isinstance(self.last_update, AwaitingInput):
            self._dispatch(CancelRun())


def _build_parser() -> argparse.ArgumentParser:
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
    return parser


def _validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.fixture and args.embedded_smoke:
        parser.error("--fixture and --embedded-smoke cannot be combined")
    if args.profile is not None and (args.fixture or args.embedded_smoke):
        parser.error("--profile applies only to the default Gateway observer mode")
    if args.auto and not args.embedded_smoke:
        parser.error("--auto applies only with --embedded-smoke")


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    _validate_args(parser, args)
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
