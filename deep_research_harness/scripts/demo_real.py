#!/usr/bin/env python3
"""Standalone Deep Research CLI over the configured public Gateway.

The command is a presentation adapter over ``ResearchRunExperience``.  It does
not parse lifecycle control wire values or construct graph response envelopes.

@impl REC-001
@impl REC-002
@impl REC-003
@impl DPL-004
@impl DPL-002
@impl WFO-001
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Literal

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

from deerflow_deep_research.domain.run_experience import (
    AnswerRun,
    AwaitingInput,
    FailureCertainty,
    Fault,
    ReadinessCheck,
    ReadinessReport,
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

SCRIPTED_DEFAULT_QUESTION = (
    "Compare lithium-ion batteries and pumped-hydro storage on grid-balancing cost and deployment risk."
)


class CliInputError(ValueError):
    """Raised for an explicit CLI input that cannot start a research run."""


def _safe_display(value: object, *, limit: int = 160) -> str:
    if not isinstance(value, str):
        return ""
    compact = " ".join("".join(char if char.isprintable() else " " for char in value).split())
    return compact if len(compact) <= limit else f"{compact[: limit - 3]}..."


def _print_banner(*, embedded_smoke: bool) -> None:
    print(f"\n{'-' * 50}")
    if embedded_smoke:
        print("  DeerFlow Deep Research · embedded smoke")
        print("  直接本地图组合仅用于 smoke；不声明 Gateway history、trace 或 SSE forwarding。")
    else:
        print("  DeerFlow Deep Research · local Gateway observer")
        print("  生命周期仅来自 Gateway 返回的类型化 Deep Research 结果。")
    print(f"{'-' * 50}")


def _print_readiness(report: ReadinessReport) -> None:
    if report.ready:
        print(f"  {report.summary}")
    else:
        print("  开始前还需要完成一项设置：")
        for check in report.checks:
            if check.ready:
                continue
            print(f"  {check.detail}")
            if check.next_action:
                print(f"  下一步: {check.next_action}")
    if report.failure is not None and report.failure.diagnostic_ref:
        print(f"  诊断引用: {report.failure.diagnostic_ref}")
    if report.failure is not None and not report.failure.journal_record_created:
        print("  尚未创建保留观察。")
    print(f"  {report.durability_note}")


def select_question(*, question: str | None, scripted: bool) -> str | None:
    """Collect a non-blank question before any graph construction or dispatch."""
    if question is not None:
        if not isinstance(question, str) or not question.strip():
            raise CliInputError("研究问题不能为空。")
        print(f"  研究问题: {_safe_display(question)}{'  [自动]' if scripted else ''}")
        return question
    if scripted:
        print(f"  研究问题: {SCRIPTED_DEFAULT_QUESTION}  [自动]")
        print("  自动策略: 使用默认研究范围，并在决策点选择 proceed。")
        return SCRIPTED_DEFAULT_QUESTION
    print("  示例: 比较两种储能路线的成本、风险与适用场景")
    while True:
        try:
            value = input("  研究问题: ")
        except (EOFError, KeyboardInterrupt):
            return None
        if value.strip():
            selected = value.strip()
            print(f"  研究问题: {_safe_display(selected)}")
            return selected
        print("  研究问题不能为空，请重新输入。")


def _ask_answer(update: AwaitingInput) -> AnswerRun | SelectControlRun | None:
    try:
        if update.prompt.mode == "text":
            while True:
                value = input("  输入: ")
                if value.strip():
                    value = value.strip()
                    if value.isdecimal():
                        control_index = int(value) - 1
                        if 0 <= control_index < len(update.prompt.visible_controls):
                            return SelectControlRun(control_id=update.prompt.visible_controls[control_index].id)
                    return AnswerRun(value=value)
                print("  输入不能为空，请重新输入。")
        value = input("  输入选项 ID: ")
        return AnswerRun(value=value.strip()) if value.strip() else None
    except (EOFError, KeyboardInterrupt):
        return None


def _trace_lines(update: AwaitingInput | Terminal) -> tuple[str, ...]:
    lines: list[str] = []
    for phase in update.trace_delta:
        label, description = PHASE_META[phase]
        lines.append(f"  -> {label}: {description}")
    return tuple(lines)


def _failure_lines(failure, *, snapshot: object | None = None) -> tuple[str, ...]:
    provider_details = provider_terminal_details(failure=failure, snapshot=snapshot)
    if provider_details is not None:
        return _provider_failure_lines(provider_details)
    lines = [f"  结果类别: {failure.code}"]
    if failure.phase:
        lines.append(f"  已知阶段: {failure.phase}")
    if getattr(failure, "validation_category", None):
        lines.append(f"  验证类别: {failure.validation_category}")
    if failure.worker_failure_category:
        lines.append(f"  工作单元失败类别: {failure.worker_failure_category}")
    lines.append(f"  下一步: {failure.next_action}")
    lines.append(f"  可重试: {'是' if failure.retryable else '否'}")
    if failure.diagnostic_ref:
        lines.append(f"  诊断引用: {failure.diagnostic_ref}")
    if not failure.journal_record_created:
        lines.append("  Bundle 内 Event Journal 记录不可用。")
    return tuple(lines)


def _provider_failure_lines(details: ProviderTerminalDetails) -> tuple[str, ...]:
    lines = [f"  结果类别: {details.category}"]
    if details.phase:
        lines.append(f"  已知阶段: {details.phase}")
    if details.worker_failure_category:
        lines.append(f"  工作单元失败类别: {details.worker_failure_category}")
    if details.final_observation is not None:
        lines.extend(_provider_observation_lines("最终服务观察", details.final_observation))
    if details.recovery is not None:
        lines.extend(_provider_observation_lines("自动重试触发观察", details.recovery.trigger_observation))
        lines.append(f"  模型调用: {details.recovery.model_attempts} 次")
        lines.append(f"  自动重试: {details.recovery.automatic_retries} 次")
        lines.append(f"  恢复处置: {details.recovery.disposition}")
    if details.diagnostic_ref:
        lines.append(f"  诊断引用: {details.diagnostic_ref}")
    if details.diagnostic_location == "bundle_journal":
        lines.append("  诊断位置: Bundle 内 Event Journal")
    elif details.diagnostic_location == "unavailable":
        lines.append("  诊断位置: 本地诊断记录不可用")
    lines.append(f"  Event Journal: {'已创建' if details.journal_record_created else '不可用'}")
    if details.recovery_action == "fresh_start":
        lines.append("  新启动: make demo-real")
    else:
        lines.append(f"  下一步: {_provider_next_step(details.category)}")
    if details.inspection_bundle_id is not None:
        command = inspection_command(details.inspection_bundle_id)
        if command is not None:
            lines.append(f"  只读诊断: {command}")
    return tuple(lines)


def _provider_observation_lines(
    label: str,
    observation: SafeProviderObservation,
) -> tuple[str, ...]:
    lines: list[str] = []
    if observation.configured_service_label:
        lines.append(f"  {label}服务: {observation.configured_service_label}")
    if observation.configured_endpoint_authority:
        lines.append(f"  {label}端点: {observation.configured_endpoint_authority}")
    response = "无响应" if observation.response_kind == "no_response" else f"HTTP {observation.http_status}"
    lines.append(f"  {label}响应: {response}")
    if observation.timeout_origin is not None:
        lines.append(f"  {label}超时来源: {observation.timeout_origin}")
    return tuple(lines)


def _provider_next_step(category: str) -> str:
    if category == "provider.authentication_failed":
        return "检查模型服务凭据后启动新的研究运行。"
    if category in {"provider.timeout", "provider.unavailable"}:
        return "检查服务状态后启动新的研究运行。"
    return "根据诊断引用检查问题后，再决定是否启动新的研究运行。"


def _bundle_lines(snapshot, *, suppress_inspection: bool = False) -> tuple[str, ...]:
    bundle_id = snapshot.bundle_id
    if bundle_id is None:
        return ()
    lines = [f"  Run Bundle: {bundle_id}"]
    observation = snapshot.observation
    if observation is not None and observation.inspectability.value == "available" and not suppress_inspection:
        command = inspection_command(bundle_id)
        if command is not None:
            lines.append(f"  查看: {command}")
    else:
        lines.append("  保留观察当前不可检查；查看不会继续执行。")
    lines.append(f"  持久性: {snapshot.durability}")
    if observation is not None and observation.retention_state is not None:
        lines.append(f"  保留状态: {observation.retention_state}")
    return tuple(lines)


def render_run_update(update: object) -> tuple[str, ...]:
    """Render only safe ``RunUpdate`` contracts for the CLI presentation seam."""
    if isinstance(update, Working):
        lines = [f"  {update.message}"]
        if update.snapshot.bundle_id:
            lines.append(f"  Run Bundle: {update.snapshot.bundle_id}")
        if update.snapshot.lifecycle_phase:
            lines.append(f"  最后确认阶段: {update.snapshot.lifecycle_phase}")
        lines.append(f"  本地等待: {update.snapshot.elapsed_seconds:.1f}s（非执行流）")
        return tuple(lines)
    if isinstance(update, AwaitingInput):
        prompt = update.prompt
        lines = [
            *_bundle_lines(update.snapshot),
            *_trace_lines(update),
            f"  {prompt.heading}",
            f"  目标: {prompt.goal}",
        ]
        lines.extend(f"  建议: {item}" for item in prompt.proposed_scope)
        if prompt.interaction is not None and prompt.interaction.feedback is not None:
            lines.append(f"  说明: {prompt.interaction.feedback.message}")
        if prompt.recognized_fields:
            lines.append(f"  已识别: {', '.join(prompt.recognized_fields)}")
        if prompt.missing_fields:
            lines.append(f"  仍需补充: {', '.join(prompt.missing_fields)}")
        if prompt.rejection_category == "choice_input_invalid":
            lines.append("  上一次选择无效；请只输入上方显示的选项 ID，例如 proceed。")
        elif prompt.rejection_category:
            lines.append("  上一次输入未识别；请使用可用值或完整 JSON。")
        if prompt.accepted_rounds_remaining:
            lines.append(f"  有效回答余量: {prompt.accepted_rounds_remaining}")
        if prompt.rejection_retries_remaining:
            lines.append(f"  未识别重试余量: {prompt.rejection_retries_remaining}")
        lines.extend(f"  可用值: {item}" for item in prompt.supported_values)
        lines.extend(
            f"  {number}. {control.label}: {control.consequence}"
            for number, control in enumerate(prompt.visible_controls, start=1)
        )
        lines.extend(f"  {item}" for item in prompt.body_lines)
        if prompt.answer_example:
            lines.append(f"  示例: {prompt.answer_example}")
        for option in prompt.options:
            lines.append(f"  {option.id}: {option.consequence}")
        return tuple(lines)
    if isinstance(update, Terminal):
        provider_diagnostic = update.failure is not None and is_provider_diagnostic(update.failure)
        lines = [
            *_bundle_lines(update.snapshot, suppress_inspection=provider_diagnostic),
            *_trace_lines(update),
        ]
        if update.outcome == "completed":
            lines.append("  研究流程已完成。")
        elif update.failure is not None:
            lines.extend(_failure_lines(update.failure, snapshot=update.snapshot))
        else:
            lines.append(f"  研究流程已结束: {update.outcome}")
        if update.snapshot.durability == "same_process":
            lines.append("  说明: 保留观察可检查；进程退出后不能据此继续运行。")
        elif update.snapshot.durability == "restart_durable":
            lines.append("  说明: 仅 Harness 生命周期边界可继续控制可用 Bundle。")
        return tuple(lines)
    if isinstance(update, Fault):
        bundle_lines = _bundle_lines(update.snapshot) if update.snapshot is not None else ()
        return (*bundle_lines, *_failure_lines(update.failure, snapshot=update.snapshot))
    return ("  研究运行返回了无法安全显示的更新。",)


def _print_update(update: RunUpdate) -> None:
    for line in render_run_update(update):
        print(line)


def _dispatch_observer():
    """Render one copy of each truthful working update during one dispatch."""
    rendered: set[tuple[str, str]] = set()

    def observe(update: Working) -> None:
        key = (update.action, update.message)
        if key in rendered:
            return
        rendered.add(key)
        _print_update(update)

    return observe


def _gateway_readiness_report(profile: str | None) -> ReadinessReport:
    if profile is None:
        return _gateway_readiness_failure(
            summary="A selected local Gateway profile is required.",
            detail="Select one ready local profile before starting the Gateway observer.",
            next_action="Start the command again with --profile <name> after profile checks pass.",
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
        durability_note="Gateway history remains owned by the configured Gateway; this CLI retains no local session.",
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


def _gateway_transport_observer(observation: GatewayTransportObservation) -> None:
    if observation.kind == "assistant_text" and observation.detail:
        print(f"  Gateway: {_safe_display(observation.detail)}")
        return
    detail = {
        "heartbeat": "Gateway liveness observed.",
        "gap": "Gateway stream gap observed; no research outcome was inferred.",
        "error": "Gateway reported a transport error; no research outcome was inferred.",
        "end": "Gateway turn ended; waiting for a validated lifecycle result.",
        "custom_invalid": "Gateway custom record was ignored.",
    }.get(observation.kind)
    if detail is not None:
        print(f"  {detail}")


def _gateway_progress_observer(candidate: Mapping[str, object]) -> None:
    """Render only predecessor-approved progress fields as a bounded projection."""

    phase = candidate.get("phase")
    operation = candidate.get("operation")
    outcome = candidate.get("outcome")
    bundle_id = candidate.get("bundle_id")
    if not (phase or operation or outcome):
        return
    label = " ".join(part for part in (str(phase), str(operation), str(outcome)) if part)
    scope = _safe_display(str(bundle_id), limit=24) if bundle_id is not None else ""
    print(f"  Deep Research progress: {_safe_display(label)}" + (f" (bundle {scope})" if scope else ""))


async def _run_gateway_demo(*, question: str | None, profile: str | None, scripted: bool) -> int:
    _print_banner(embedded_smoke=False)
    if scripted:
        print("  输入错误: Gateway 默认路径不支持 --scripted；自动策略仅属于 embedded smoke。")
        return 2
    report = _gateway_readiness_report(profile)
    _print_readiness(report)
    if not report.ready:
        return 2
    try:
        selected_question = select_question(question=question, scripted=False)
    except CliInputError as exc:
        print(f"  输入错误: {_safe_display(str(exc))}")
        return 2
    if selected_question is None:
        print("  已退出，未启动研究。")
        return 130

    client = HttpGatewayPublicClient()
    transport = GatewayObserver(
        client=client,
        transport_observer=_gateway_transport_observer,
        withheld_candidate_observer=_gateway_progress_observer,
    )
    experience = ResearchRunExperience(transport=transport, mode="real", readiness_provider=lambda: report)
    try:
        await experience.preflight()
        update = await experience.handle(
            StartRun(question=selected_question, scripted=False),
            observer=_dispatch_observer(),
        )
        while isinstance(update, AwaitingInput):
            _print_update(update)
            answer = _ask_answer(update)
            if answer is None:
                print("  已退出，未继续研究。")
                return 130
            update = await experience.handle(answer, observer=_dispatch_observer())
        _print_update(update)
        return 0 if isinstance(update, Terminal) and update.outcome == "completed" else 1
    except asyncio.CancelledError:
        raise
    except Exception:
        print("  Gateway observer could not continue; no research completion was inferred.")
        return 1
    finally:
        await transport.aclose()


async def _run_embedded_smoke(
    *,
    question: str | None,
    scripted: bool,
    profile_intent: str | None = None,
) -> int:
    """Retain the pre-existing all-real graph only behind explicit smoke selection."""

    _print_banner(embedded_smoke=True)
    transport = DemoLifecycleTransport()
    experience = ResearchRunExperience(
        transport=transport,
        mode="real",
        readiness_provider=lambda: demo_readiness_report(mode="real"),
    )
    report = await experience.preflight()
    _print_readiness(report)
    if not report.ready:
        return 2
    try:
        selected_question = select_question(question=question, scripted=scripted)
    except CliInputError as exc:
        print(f"  输入错误: {_safe_display(str(exc))}")
        return 2
    if selected_question is None:
        print("  已退出，未启动研究。")
        return 130

    # Explicit "none" declines the intent declaration (default product path);
    # an absent selection keeps the credentialed automatic demo's minimal
    # declaration (modes 003 and prior behavior) exactly as before.
    declared_intent: Literal["minimal"] | None
    if scripted:
        declared_intent = None if profile_intent == "none" else "minimal"
    else:
        declared_intent = None

    adapter: DemoAdapter | None = None
    try:
        adapter = DemoAdapter.for_real()
        if hasattr(experience, "set_observation_publisher"):
            experience.set_observation_publisher(adapter.observation_publisher)
        transport.bind(runtime=build_demo_runtime(mode="real", adapter=adapter))
        update = await experience.handle(
            StartRun(
                question=selected_question,
                scripted=scripted,
                profile_intent=declared_intent,
            ),
            observer=_dispatch_observer(),
        )
        while isinstance(update, AwaitingInput):
            _print_update(update)
            if scripted:
                print("  自动策略未能完成图拥有的输入请求。")
                return 1
            answer = _ask_answer(update)
            if answer is None:
                print("  已退出，未继续研究。")
                return 130
            update = await experience.handle(answer, observer=_dispatch_observer())
        _print_update(update)
        return 0 if isinstance(update, Terminal) and update.outcome == "completed" else 1
    except asyncio.CancelledError:
        raise
    except Exception:
        print("  本地演示无法启动；请检查本地项目环境。")
        return 1
    finally:
        if adapter is not None:
            closer = getattr(adapter, "aclose", None)
            if closer is not None:
                await closer()
            else:
                adapter.close()


async def run_demo(
    *,
    question: str | None,
    scripted: bool,
    profile: str | None = None,
    embedded_smoke: bool = False,
    profile_intent: str | None = None,
) -> int:
    """Run the default public Gateway observer or the explicit embedded smoke route."""

    if embedded_smoke:
        return await _run_embedded_smoke(question=question, scripted=scripted, profile_intent=profile_intent)
    return await _run_gateway_demo(question=question, profile=profile, scripted=scripted)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the standalone Deep Research Gateway observer.",
        epilog=(
            "Default real mode requires a selected ready local Gateway profile. It submits only explicit "
            "user turns and accepts only returned typed Deep Research results. --embedded-smoke is the "
            "separate direct local graph path and makes no Gateway observation claim."
        ),
    )
    parser.add_argument(
        "--question",
        default=None,
        help="Research question. Interactive mode prompts after preflight when omitted.",
    )
    parser.add_argument(
        "--scripted",
        action="store_true",
        help="Use graph-owned automatic policy only with --embedded-smoke.",
    )
    parser.add_argument("--profile", default=None, help="Selected ready local Gateway profile for default real mode.")
    parser.add_argument(
        "--embedded-smoke",
        action="store_true",
        help="Use the direct local graph smoke path without Gateway history, trace, or SSE claims.",
    )
    parser.add_argument(
        "--profile-intent",
        choices=["minimal", "none"],
        default=None,
        help="Research intent declaration for the embedded-smoke --scripted route only "
        "(absent = minimal; 'none' runs the default product path without a declaration).",
    )
    args = parser.parse_args()
    if args.embedded_smoke and args.profile is not None:
        parser.error("--profile applies only to the default Gateway observer mode")
    if args.profile_intent is not None and not (args.embedded_smoke and args.scripted):
        parser.error("--profile-intent applies only to the embedded-smoke --scripted route")
    try:
        code = asyncio.run(
            run_demo(
                question=args.question,
                scripted=args.scripted,
                profile=args.profile,
                embedded_smoke=args.embedded_smoke,
                profile_intent=args.profile_intent,
            )
        )
    except KeyboardInterrupt:
        code = 130
    if code:
        sys.exit(code)


if __name__ == "__main__":
    main()
