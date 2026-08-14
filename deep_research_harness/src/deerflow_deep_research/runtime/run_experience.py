"""Runtime-owned lifecycle-to-presentation projection for standalone demos.

@impl RER-001
@impl RER-003
@impl RER-004
@impl RER-012
@impl PRS-005
"""

from __future__ import annotations

import asyncio
import inspect
import json
import secrets
import time
from collections.abc import Awaitable, Callable, Mapping, Sequence
from contextlib import suppress
from typing import Any, Literal, Protocol

from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.types import Command

from deerflow_deep_research.domain.human_interaction import InteractionProjection
from deerflow_deep_research.domain.lifecycle import (
    BundleAvailability,
    BundleControlResult,
    HumanInputMode,
    HumanInputRequest,
    LifecycleAction,
    LifecycleStatus,
    LogicalPhase,
    ResultCode,
)
from deerflow_deep_research.domain.run_experience import (
    FRESH_START_NEXT_ACTION,
    AnswerRun,
    AwaitingInput,
    CancelRun,
    FailureCertainty,
    Fault,
    PendingInputProjection,
    PromptOption,
    PromptView,
    ProviderObservation,
    ProviderRecoveryProjection,
    ReadinessCheck,
    ReadinessReport,
    RefineRun,
    RunFailure,
    RunFailureCode,
    RunIntent,
    RunMode,
    RunSnapshot,
    RunUpdate,
    SelectControlRun,
    StartRun,
    StatusRun,
    Terminal,
    Working,
)
from deerflow_deep_research.domain.run_observation import (
    ObservationInspectability,
    ProviderTimeoutOrigin,
    RecordBearingLifecycleFact,
    RetainedRecoverySummary,
    RunObservationView,
    derive_diagnostic_reference,
)


class LifecycleTransport(Protocol):
    """Narrow runtime seam supplied by a standalone demo adapter."""

    async def dispatch(
        self,
        *,
        action: str,
        bundle_id: str | None,
        messages: tuple[Any, ...],
        context: Mapping[str, Any] | None = None,
    ) -> object: ...


class RunObservationPublisher(Protocol):
    """Runtime-owned publication seam; presentation adapters never receive paths."""

    async def publish(self, fact: RecordBearingLifecycleFact) -> RunObservationView: ...


ReadinessProvider = Callable[[], ReadinessReport | Awaitable[ReadinessReport]]
RunObserver = Callable[[Working], None | Awaitable[None]]

_KNOWN_PHASES = frozenset((*[phase.value for phase in LogicalPhase], "hitl1_auto_profile", "hitl2_auto_proceed"))
_HITL1_DIMENSIONS = frozenset({"depth", "audience", "format", "cost_tolerance", "time_budget"})
_HITL2_COPY: dict[str, tuple[str, str]] = {
    "proceed": ("继续", "按当前研究计划继续。"),
    "rerun": ("重新检索", "开始新的研究轮次并按新方向检索。"),
    "repair": ("补充证据", "保留当前方向并补充缺失证据。"),
    "revise_view": ("修订综合", "回到综合分析并调整当前观点。"),
    "stop": ("结束", "停止当前研究流程。"),
}
_HITL1_JSON_EXAMPLE = (
    '{"depth":"standard","audience":"practitioner","format":"detailed_report",'
    '"cost_tolerance":"moderate","time_budget":"standard","must_answer":["..."]}'
)
_VISIBLE_CONTROL_ACTIONS = {"accept_current_proposal": "accept_suggestion"}
_FAILURE_COPY: dict[RunFailureCode, tuple[str, str, bool]] = {
    RunFailureCode.CONFIGURATION_MODEL_MISSING: ("模型配置尚未就绪。", "配置一个受支持的模型后重新开始。", True),
    RunFailureCode.CONFIGURATION_WEB_TOOL_MISSING: ("网页检索前提尚未就绪。", "配置网页检索凭据后重新开始。", True),
    RunFailureCode.CONFIGURATION_ENVIRONMENT_INVALID: ("本地运行环境不可用。", "按命令提示修复项目环境后重试。", True),
    RunFailureCode.PROVIDER_AUTHENTICATION_FAILED: ("模型服务认证未通过。", "检查模型服务凭据后重新开始。", True),
    RunFailureCode.PROVIDER_UNAVAILABLE: ("模型服务当前不可用。", "稍后重试，或检查服务状态。", True),
    RunFailureCode.PROVIDER_TIMEOUT: ("模型服务在限定时间内未响应。", "稍后重试，或缩小研究问题。", True),
    RunFailureCode.PROVIDER_USAGE_UNAVAILABLE: (
        "模型响应未提供可验证的用量信息。",
        "检查模型服务的用量返回配置后，启动新的研究运行。",
        False,
    ),
    RunFailureCode.BUDGET_EXHAUSTED: (
        "当前研究步骤超出已设置的资源预算。",
        "调整研究范围或预算设置后，启动新的研究运行。",
        False,
    ),
    RunFailureCode.POLICY_DENIED: (
        "当前研究步骤不符合已配置的执行策略。",
        "调整已批准的研究配置后，启动新的研究运行。",
        False,
    ),
    RunFailureCode.TOOL_UNAVAILABLE: ("所需研究工具当前不可用。", "检查网页工具配置后重新开始。", True),
    RunFailureCode.TOOL_EXECUTION_FAILED: ("研究工具未能完成请求。", "稍后重试，或检查工具服务状态。", True),
    RunFailureCode.OUTPUT_STRUCTURED_INVALID: (
        "研究步骤返回了无效的结构化结果。",
        "重新开始该研究；若持续出现，请提供诊断引用。",
        True,
    ),
    RunFailureCode.INPUT_INVALID_RESPONSE: ("输入不符合当前研究请求。", "按当前提示重新提供答案或选择。", True),
    RunFailureCode.PERSISTENCE_UNAVAILABLE: ("本地研究存储不可用。", "检查本地工作区后重新开始。", True),
    RunFailureCode.BUNDLE_UNAVAILABLE: ("当前 Run Bundle 已不可用。", FRESH_START_NEXT_ACTION, False),
    RunFailureCode.CHECKPOINT_INCONSISTENT: ("研究检查点状态不一致。", "不要继续当前运行；请提供诊断引用。", False),
    RunFailureCode.RESEARCH_BLOCKED: ("研究流程被安全地阻止。", "根据提示检查前提条件或提供诊断引用。", False),
    RunFailureCode.PROTOCOL_INVALID_RESULT: (
        "研究运行返回了无法安全解释的结果。",
        "不要继续当前运行；请提供诊断引用。",
        False,
    ),
    RunFailureCode.LOCAL_INTERRUPTED: ("本地等待已中断，尚未确认图已取消。", "可查询状态，或在需要时显式取消。", True),
    RunFailureCode.INTERNAL_UNEXPECTED: ("研究运行遇到未分类的本地问题。", "请提供诊断引用以便排查。", False),
}


class ResearchRunExperience:
    """Own lifecycle wire parsing, safe prompts, and response correlation."""

    def __init__(
        self,
        *,
        transport: LifecycleTransport,
        mode: RunMode,
        readiness_provider: ReadinessProvider | None = None,
        observation_publisher: RunObservationPublisher | None = None,
        liveness_interval: float = 1.0,
    ) -> None:
        if not 0.001 <= liveness_interval <= 60.0:
            raise ValueError("liveness_interval_invalid")
        self._transport = transport
        self._mode = mode
        self._readiness_provider = readiness_provider
        self._observation_publisher = observation_publisher
        self._messages: list[Any] = []
        self._bundle_id: str | None = None
        self._pending_request: HumanInputRequest | None = None
        self._last_awaiting_input: AwaitingInput | None = None
        self._trace: tuple[str, ...] = ()
        self._lifecycle_phase: str | None = None
        self._durability = "unavailable"
        self._observation_view: RunObservationView | None = None
        self._liveness_interval = liveness_interval

    def set_observation_publisher(self, publisher: RunObservationPublisher) -> None:
        """Attach the adapter-owned publisher after a successful local preflight."""
        if self._observation_publisher is not None:
            raise RuntimeError("observation_publisher_already_set")
        self._observation_publisher = publisher

    async def preflight(self) -> ReadinessReport:
        """Return a non-network readiness report before a question is collected."""
        if self._readiness_provider is None:
            mode_detail = "已选择真实模式。" if self._mode == "real" else "已选择无凭据 fixture 图模式。"
            return ReadinessReport(
                mode=self._mode,
                ready=True,
                summary="运行前检查已就绪。",
                checks=(ReadinessCheck(name="mode", ready=True, detail=mode_detail),),
                durability_note="这是临时独立演示，进程退出后不保证可以继续。",
            )
        try:
            report = self._readiness_provider()
            if inspect.isawaitable(report):
                report = await report
            if not isinstance(report, ReadinessReport):
                raise TypeError("readiness_provider_result_invalid")
            if not report.ready and report.failure is not None and report.failure.diagnostic_ref is None:
                report = report.model_copy(
                    update={
                        "failure": self._failure(
                            report.failure.code,
                            phase=report.failure.phase,
                            certainty=report.failure.certainty,
                            source=report.failure,
                        )
                    }
                )
            return report
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            failure = self._failure(
                RunFailureCode.CONFIGURATION_ENVIRONMENT_INVALID,
                certainty=FailureCertainty.UNKNOWN,
                source=exc,
            )
            return ReadinessReport(
                mode=self._mode,
                ready=False,
                summary="运行前检查无法确认本地环境。",
                checks=(
                    ReadinessCheck(
                        name="environment",
                        ready=False,
                        detail="本地环境检查未完成。",
                        next_action=failure.next_action,
                    ),
                ),
                failure=failure,
                durability_note="尚未创建研究记录。",
            )

    async def handle(self, intent: RunIntent, observer: RunObserver | None = None) -> RunUpdate:
        """Dispatch one graph-owned intent and return only a safe run update."""
        try:
            action, bundle_id, context = self._prepare_intent(intent)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            return self._fault(RunFailureCode.INPUT_INVALID_RESPONSE, source=exc)

        started_at = time.monotonic()
        working = Working(
            snapshot=self._snapshot(elapsed_seconds=0.0),
            action=action,
            message="正在等待生命周期返回结果（仅返回结果模式）。",
        )
        await self._notify(observer, working)
        try:
            raw = await self._dispatch_with_liveness(
                action=action,
                bundle_id=bundle_id,
                context=context,
                observer=observer,
                started_at=started_at,
            )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            return self._fault(RunFailureCode.INTERNAL_UNEXPECTED, source=exc)

        return await self._project_result(
            raw,
            dispatched_action=action,
            elapsed_seconds=time.monotonic() - started_at,
        )

    async def _dispatch_with_liveness(
        self,
        *,
        action: str,
        bundle_id: str | None,
        context: Mapping[str, Any] | None,
        observer: RunObserver | None,
        started_at: float,
    ) -> object:
        dispatch = self._transport.dispatch(
            action=action,
            bundle_id=bundle_id,
            messages=tuple(self._messages),
            context=context,
        )
        if observer is None:
            return await dispatch
        task = asyncio.create_task(dispatch)
        try:
            while not task.done():
                await asyncio.wait({task}, timeout=self._liveness_interval)
                if task.done():
                    break
                await self._notify(
                    observer,
                    Working(
                        snapshot=self._snapshot(elapsed_seconds=time.monotonic() - started_at),
                        action=action,
                        message="正在等待生命周期返回结果（仅返回结果模式）。",
                    ),
                )
            return task.result()
        except asyncio.CancelledError:
            task.cancel()
            with suppress(asyncio.CancelledError, Exception):
                await task
            raise
        except Exception:
            task.cancel()
            with suppress(asyncio.CancelledError, Exception):
                await task
            raise

    def _prepare_intent(self, intent: RunIntent) -> tuple[str, str | None, Mapping[str, Any] | None]:
        if isinstance(intent, StartRun):
            self._messages = [HumanMessage(content=intent.question, id=self._fresh_id("start"))]
            self._bundle_id = None
            self._pending_request = None
            self._last_awaiting_input = None
            self._trace = ()
            self._lifecycle_phase = None
            self._durability = "unavailable"
            self._observation_view = None
            context: Mapping[str, Any] | None = None
            if intent.scripted:
                context = {
                    "non_interactive": True,
                    "non_interactive_policy": {"auto_profile": True, "auto_proceed": True},
                }
            return "start", None, context
        if isinstance(intent, AnswerRun):
            if self._pending_request is None or self._bundle_id is None:
                raise ValueError("answer_without_pending_request")
            current_prompt = self._last_awaiting_input.prompt if self._last_awaiting_input is not None else None
            hitl1_language_choice = (
                self._pending_request.mode is HumanInputMode.CHOICE
                and current_prompt is not None
                and current_prompt.phase == "hitl1"
            )
            if hitl1_language_choice and current_prompt.request_id != self._pending_request.request_id:
                raise ValueError("answer_request_not_current")
            if intent.response_kind == "action" and intent.action_id not in self._pending_request.action_ids:
                raise ValueError("unadvertised_answer_action")
            if intent.response_kind == "option" and (
                self._pending_request.mode is not HumanInputMode.CHOICE
                or intent.option_id not in {option.id.value for option in self._pending_request.options}
            ):
                raise ValueError("unadvertised_answer_option")
            if hitl1_language_choice and intent.response_kind != "option":
                raise ValueError("hitl1_language_answer_requires_option")
            response = HumanMessage(
                content=intent.value,
                id=self._fresh_id("answer"),
                additional_kwargs={
                    "human_input_response": {
                        "version": 1,
                        "kind": "human_input_response",
                        "source": "deep_research",
                        "request_id": self._pending_request.request_id,
                        "response_kind": intent.response_kind,
                        "value": intent.value,
                        **({"action_id": intent.action_id} if intent.action_id is not None else {}),
                        **({"option_id": intent.option_id} if intent.option_id is not None else {}),
                    }
                },
            )
            self._messages.append(response)
            return "resume", self._bundle_id, None
        if isinstance(intent, SelectControlRun):
            if self._pending_request is None or self._bundle_id is None or self._last_awaiting_input is None:
                raise ValueError("control_without_pending_request")
            pending = self._pending_request
            cached = self._last_awaiting_input
            interaction = pending.interaction
            if (
                pending.mode is not HumanInputMode.TEXT
                or interaction is None
                or cached.prompt.request_id != pending.request_id
                or cached.prompt.interaction != interaction
                or cached.prompt.visible_controls != interaction.controls
                or intent.control_id not in {control.id for control in interaction.controls}
            ):
                raise ValueError("control_not_currently_visible")
            action_id = _VISIBLE_CONTROL_ACTIONS.get(intent.control_id)
            if action_id is None or action_id not in pending.action_ids:
                raise ValueError("control_action_not_advertised")
            response = HumanMessage(
                content=action_id,
                id=self._fresh_id("control"),
                additional_kwargs={
                    "human_input_response": {
                        "version": 1,
                        "kind": "human_input_response",
                        "source": "deep_research",
                        "request_id": pending.request_id,
                        "response_kind": "action",
                        "value": action_id,
                        "action_id": action_id,
                    }
                },
            )
            self._messages.append(response)
            return "resume", self._bundle_id, None
        if isinstance(intent, CancelRun):
            if self._bundle_id is None:
                raise ValueError("cancel_without_research")
            return "cancel", self._bundle_id, None
        if isinstance(intent, StatusRun):
            if self._bundle_id is None:
                raise ValueError("status_without_research")
            return "status", self._bundle_id, None
        if isinstance(intent, RefineRun):
            if self._bundle_id is None:
                raise ValueError("refine_without_research")
            return "refine", self._bundle_id, {"refinement": intent.text}
        raise TypeError("run_intent_invalid")

    async def _project_result(
        self,
        raw: object,
        *,
        dispatched_action: str,
        elapsed_seconds: float,
    ) -> RunUpdate:
        try:
            control, request = self._decode_result(raw)
            retry = self._recoverable_invalid_choice(
                control,
                request=request,
                dispatched_action=dispatched_action,
            )
            if retry is not None:
                return retry
            if self._is_untrusted_human_input_denial(control):
                return self._fault(RunFailureCode.PROTOCOL_INVALID_RESULT, source=control)
            if control.availability is BundleAvailability.UNAVAILABLE:
                self._bundle_id = None
                self._pending_request = None
                self._last_awaiting_input = None
                self._lifecycle_phase = None
                self._durability = control.durability.value
                self._observation_view = None
                return self._fault(
                    RunFailureCode.BUNDLE_UNAVAILABLE,
                    snapshot=self._snapshot(elapsed_seconds=elapsed_seconds),
                    source=control,
                )
            trace_delta = self._validated_trace_delta(control.execution_trace)
            if not self._is_record_bearing(control):
                return self._fault(self._failure_code_for_control(control), source=control)
            self._bundle_id = control.bundle_id
            self._lifecycle_phase = control.phase.value if control.phase is not None else None
            self._durability = control.durability.value
            terminal_diagnostic_ref = self._terminal_diagnostic_reference(control)
            self._observation_view = await self._publish_observation(
                control,
                trace_delta,
                terminal_diagnostic_ref=terminal_diagnostic_ref,
            )
            snapshot = self._snapshot(
                pending_input=control.pending_input,
                elapsed_seconds=elapsed_seconds,
            )
            if control.status is LifecycleStatus.SUSPENDED:
                prompt = self._suspended_prompt(control, request)
                if request is not None:
                    self._pending_request = request
                update = AwaitingInput(snapshot=snapshot, prompt=prompt, trace_delta=trace_delta)
                self._last_awaiting_input = update
                return update
            self._pending_request = None
            self._last_awaiting_input = None
            if control.status is None:
                return self._fault(self._failure_code_for_control(control), snapshot=snapshot, source=control)
            failure = self._failure_for_terminal(control, terminal_diagnostic_ref=terminal_diagnostic_ref)
            return Terminal(
                snapshot=snapshot,
                outcome=control.status.value,
                trace_delta=trace_delta,
                failure=failure,
            )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            return self._fault(RunFailureCode.PROTOCOL_INVALID_RESULT, source=exc)

    def _recoverable_invalid_choice(
        self,
        control: BundleControlResult,
        *,
        request: HumanInputRequest | None,
        dispatched_action: str,
    ) -> AwaitingInput | None:
        cached = self._last_awaiting_input
        pending = self._pending_request
        cached_pending = cached.snapshot.pending_input if cached is not None else None
        if (
            dispatched_action != LifecycleAction.RESUME.value
            or request is not None
            or control.action is not LifecycleAction.RESUME
            or control.code is not ResultCode.RESPONSE_INVALID
            or control.bundle_id is None
            or control.bundle_id != self._bundle_id
            or control.execution_trace
            or control.status is not None
            or control.phase is not None
            or control.generation is not None
            or control.request_id is not None
            or control.pending_input is not None
            or control.terminal_reason is not None
            or control.terminal_incident is not None
            or control.infrastructure_reason is not None
            or cached is None
            or pending is None
            or cached_pending is None
            or cached.snapshot.bundle_id != control.bundle_id
            or cached.snapshot.completed_trace != self._trace
            or cached.prompt.phase != "hitl2"
            or cached.prompt.mode != "choice"
            or cached_pending.pending_phase != "hitl2"
            or cached_pending.mode != "choice"
            or pending.mode is not HumanInputMode.CHOICE
            or cached.prompt.request_id != cached_pending.request_id
            or cached.prompt.request_id != pending.request_id
        ):
            return None
        return cached.model_copy(
            update={
                "prompt": cached.prompt.model_copy(update={"rejection_category": "choice_input_invalid"}),
                "trace_delta": (),
            }
        )

    @staticmethod
    def _is_untrusted_human_input_denial(control: BundleControlResult) -> bool:
        return control.code in {ResultCode.RESPONSE_INVALID, ResultCode.RESPONSE_MISMATCH}

    @staticmethod
    def _is_record_bearing(control: BundleControlResult) -> bool:
        return (
            control.bundle_id is not None
            and control.status is not None
            and control.phase is not None
            and control.generation is not None
        )

    @staticmethod
    def _is_provider_diagnostic(control: BundleControlResult) -> bool:
        incident = control.terminal_incident
        return (
            control.status is LifecycleStatus.BLOCKED
            and incident is not None
            and (incident.provider_recovery is not None or incident.provider_observation is not None)
        )

    @staticmethod
    def _retained_recovery_summary(control: BundleControlResult) -> RetainedRecoverySummary | None:
        incident = control.terminal_incident
        if incident is None or incident.provider_recovery is None:
            return None
        recovery = incident.provider_recovery
        return RetainedRecoverySummary(
            trigger_category=recovery.trigger_category,
            trigger_invocation_ordinal=recovery.trigger_invocation_ordinal,
            model_attempts=recovery.model_attempts,
            automatic_retries=recovery.automatic_retries,
            disposition=recovery.disposition,
        )

    @staticmethod
    def _provider_timeout_origins(
        control: BundleControlResult,
    ) -> tuple[ProviderTimeoutOrigin | None, ProviderTimeoutOrigin | None]:
        incident = control.terminal_incident
        if incident is None:
            return None, None
        trigger_origin = (
            incident.provider_recovery.trigger_observation.timeout_origin
            if incident.provider_recovery is not None
            else None
        )
        final_origin = (
            incident.provider_observation.timeout_origin if incident.provider_observation is not None else None
        )
        return trigger_origin, final_origin

    def _terminal_diagnostic_reference(self, control: BundleControlResult) -> str | None:
        """Derive one safe Bundle-local reference before terminal projection."""

        if control.status is not LifecycleStatus.BLOCKED:
            return None
        incident = control.terminal_incident
        if incident is not None and incident.diagnostic_ref is not None:
            return incident.diagnostic_ref
        if control.bundle_id is None or control.generation is None or control.phase is None:
            return None
        return derive_diagnostic_reference(
            bundle_id=control.bundle_id,
            generation=control.generation,
            phase=control.phase.value,
            category=(incident.code if incident is not None else RunFailureCode.RESEARCH_BLOCKED).value,
            correlation_id=control.action.value,
        )

    async def _publish_observation(
        self,
        control: BundleControlResult,
        trace_delta: tuple[str, ...],
        *,
        terminal_diagnostic_ref: str | None,
    ) -> RunObservationView | None:
        if self._observation_publisher is None:
            return None
        assert control.bundle_id is not None
        assert control.status is not None
        assert control.phase is not None
        assert control.generation is not None
        pending = control.pending_input
        failure_category = None
        if control.status is LifecycleStatus.BLOCKED:
            failure_category = (
                control.terminal_incident.code.value
                if control.terminal_incident is not None
                else RunFailureCode.RESEARCH_BLOCKED.value
            )
        worker_failure_category = (
            control.terminal_incident.worker_failure_category if control.terminal_incident is not None else None
        )
        recovery_trigger_timeout_origin, final_timeout_origin = self._provider_timeout_origins(control)
        fact = RecordBearingLifecycleFact(
            bundle_id=control.bundle_id,
            action=control.action.value,
            status=control.status.value,
            phase=control.phase.value,
            generation=control.generation,
            durability=control.durability.value,
            trace_delta=trace_delta,
            pending_phase=pending.pending_phase if pending is not None else None,
            pending_mode=pending.mode if pending is not None else None,
            pending_request_id=pending.request_id if pending is not None else None,
            terminal_outcome=(
                control.status.value
                if control.status
                in {
                    LifecycleStatus.COMPLETED,
                    LifecycleStatus.STOPPED,
                    LifecycleStatus.CANCELLED,
                    LifecycleStatus.BLOCKED,
                }
                else None
            ),
            failure_category=failure_category,
            worker_failure_category=worker_failure_category,
            diagnostic_ref=terminal_diagnostic_ref,
            retained_recovery_summary=self._retained_recovery_summary(control),
            recovery_trigger_timeout_origin=recovery_trigger_timeout_origin,
            final_timeout_origin=final_timeout_origin,
        )
        try:
            return await self._observation_publisher.publish(fact)
        except asyncio.CancelledError:
            raise
        except (OSError, RuntimeError, TypeError, ValueError):
            return None

    def _decode_result(self, raw: object) -> tuple[BundleControlResult, HumanInputRequest | None]:
        if isinstance(raw, Command):
            return self._decode_command(raw)
        if not isinstance(raw, Mapping):
            raise ValueError("lifecycle_result_not_mapping")
        try:
            return BundleControlResult.model_validate(dict(raw)), None
        except ValueError as exc:
            raise ValueError("lifecycle_control_invalid") from exc

    def _decode_command(self, command: Command) -> tuple[BundleControlResult, HumanInputRequest]:
        update = command.update
        if not isinstance(update, Mapping):
            raise ValueError("command_update_invalid")
        messages = update.get("messages")
        if not isinstance(messages, Sequence) or isinstance(messages, (str, bytes, bytearray)) or len(messages) != 1:
            raise ValueError("command_messages_invalid")
        message = messages[0]
        if not isinstance(message, ToolMessage) or not isinstance(message.content, str):
            raise ValueError("command_tool_message_invalid")
        try:
            control = BundleControlResult.model_validate_json(message.content)
        except ValueError as exc:
            raise ValueError("command_control_invalid") from exc
        artifact = message.artifact
        if not isinstance(artifact, Mapping) or not isinstance(artifact.get("human_input"), Mapping):
            raise ValueError("command_artifact_invalid")
        try:
            request = HumanInputRequest.model_validate(dict(artifact["human_input"]))
        except ValueError as exc:
            raise ValueError("command_request_invalid") from exc
        if str(message.id) != request.request_id:
            raise ValueError("command_message_request_mismatch")
        return control, request

    def _validated_trace_delta(self, candidate: Sequence[str]) -> tuple[str, ...]:
        trace = tuple(candidate)
        if any(not isinstance(phase, str) or phase not in _KNOWN_PHASES for phase in trace):
            raise ValueError("execution_trace_invalid")
        if trace[: len(self._trace)] != self._trace:
            raise ValueError("execution_trace_diverged")
        delta = trace[len(self._trace) :]
        self._trace = trace
        return delta

    def _suspended_prompt(
        self,
        control: BundleControlResult,
        request: HumanInputRequest | None,
    ) -> PromptView:
        pending = control.pending_input
        if pending is None or control.request_id != pending.request_id:
            raise ValueError("pending_input_missing")
        if request is not None:
            self._validate_request_projection(request, pending)
        elif self._pending_request is not None:
            self._validate_request_projection(self._pending_request, pending)
            request = self._pending_request
        if pending.pending_phase == "hitl1":
            return self._hitl1_prompt(request, pending)
        return self._hitl2_prompt(request, pending)

    @staticmethod
    def _validate_request_projection(request: HumanInputRequest, pending: PendingInputProjection) -> None:
        if request.request_id != pending.request_id or request.mode.value != pending.mode:
            raise ValueError("pending_artifact_mismatch")

    def _hitl1_prompt(self, request: HumanInputRequest | None, pending: PendingInputProjection) -> PromptView:
        if request is not None and request.mode is HumanInputMode.CHOICE:
            advertised = tuple(option.id.value for option in request.options)
            if advertised != ("zh", "en"):
                raise ValueError("hitl1_language_options_invalid")
            return PromptView(
                phase="hitl1",
                request_id=pending.request_id,
                mode="choice",
                heading="选择研究语言",
                goal="请选择研究交互语言。",
                options=tuple(
                    PromptOption(id=option.id.value, label=option.label, consequence="Use this language for research.")
                    for option in request.options
                ),
            )
        generic = PromptView(
            phase="hitl1",
            request_id=pending.request_id,
            mode="text",
            heading="确认研究范围",
            goal="请补充研究范围和输出偏好。",
            body_lines=("请说明目标读者、研究深度和希望得到的输出形式。",),
            answer_example=_HITL1_JSON_EXAMPLE,
        )
        if request is None:
            return generic
        if request.interaction is not None:
            interaction = request.interaction
            return PromptView(
                phase="hitl1",
                request_id=pending.request_id,
                mode="text",
                heading="确认研究范围",
                goal=interaction.subject.goal,
                proposed_scope=self._interaction_proposal_lines(interaction),
                interaction=interaction,
                visible_controls=interaction.controls,
                body_lines=("可以直接确认、说明想修改的内容，或提出关于当前建议的问题。",),
            )
        try:
            payload = json.loads(request.context)
            if not isinstance(payload, Mapping) or payload.get("context_schema_version") != 1:
                return generic
            goal = self._safe_text(payload.get("brief_summary"), limit=768)
            if not goal:
                return generic
            scope = self._proposal_lines(payload.get("proposed_dimensions"), payload.get("must_answer"))
            missing = self._named_values(payload.get("missing_dimensions"))
            supported = self._supported_lines(payload.get("valid_options"))
            recognized = self._named_values(payload.get("recognized_fields"))
            rejection_category = (
                "profile_input_unrecognized"
                if payload.get("rejection_category") == "profile_input_unrecognized"
                else None
            )
            return PromptView(
                phase="hitl1",
                request_id=pending.request_id,
                mode="text",
                heading="确认研究范围",
                goal=goal,
                proposed_scope=scope,
                missing_fields=missing,
                supported_values=supported,
                recognized_fields=recognized,
                rejection_category=rejection_category,
                accepted_rounds_remaining=self._bounded_count(payload.get("accepted_rounds_remaining")),
                rejection_retries_remaining=self._bounded_count(payload.get("rejection_retries_remaining")),
                body_lines=("请确认或修正建议范围，并补充缺失的研究偏好。",),
                answer_example=_HITL1_JSON_EXAMPLE,
            )
        except (TypeError, ValueError, json.JSONDecodeError):
            return generic

    def _hitl2_prompt(self, request: HumanInputRequest | None, pending: PendingInputProjection) -> PromptView:
        if request is not None and request.mode is not HumanInputMode.CHOICE:
            raise ValueError("hitl2_mode_invalid")
        advertised = tuple(option.id.value for option in request.options) if request is not None else tuple(_HITL2_COPY)
        if set(advertised) != set(_HITL2_COPY) or len(advertised) != len(_HITL2_COPY):
            raise ValueError("hitl2_options_invalid")
        return PromptView(
            phase="hitl2",
            request_id=pending.request_id,
            mode="choice",
            heading="选择下一步",
            goal="研究已到达需要人工决策的节点。",
            body_lines=("请输入一个已声明的选项 ID，例如 proceed。",),
            options=tuple(
                PromptOption(id=option, label=_HITL2_COPY[option][0], consequence=_HITL2_COPY[option][1])
                for option in advertised
            ),
        )

    @staticmethod
    def _safe_text(value: object, *, limit: int) -> str:
        if not isinstance(value, str):
            return ""
        compact = " ".join("".join(char if char.isprintable() else " " for char in value).split())
        return compact[:limit]

    @staticmethod
    def _bounded_count(value: object) -> int:
        return value if isinstance(value, int) and 0 <= value <= 3 else 0

    def _scope_lines(self, value: object) -> tuple[str, ...]:
        if not isinstance(value, Mapping):
            return ()
        lines: list[str] = []
        for name in ("depth", "audience", "format", "cost_tolerance", "time_budget"):
            item = self._safe_text(value.get(name), limit=96)
            if item:
                lines.append(f"{name}: {item}")
        return tuple(lines)

    def _proposal_lines(self, dimensions: object, must_answer: object) -> tuple[str, ...]:
        lines = list(self._scope_lines(dimensions))
        if isinstance(must_answer, Sequence) and not isinstance(must_answer, (str, bytes, bytearray)):
            questions = tuple(self._safe_text(question, limit=256) for question in must_answer)
            lines.extend(f"must_answer: {question}" for question in questions if question)
        return tuple(lines[:8])

    def _interaction_proposal_lines(self, interaction: InteractionProjection) -> tuple[str, ...]:
        """Render all material values from the typed current proposal before acceptance."""

        proposal = interaction.subject.proposal
        lines = [
            f"depth: {proposal.depth}",
            f"audience: {proposal.audience}",
            f"format: {proposal.format}",
            f"cost_tolerance: {proposal.cost_tolerance}",
            f"time_budget: {proposal.time_budget}",
        ]
        lines.extend(
            f"must_answer[{index}]: {self._typed_text(question)}"
            for index, question in enumerate(proposal.must_answer, start=1)
        )
        scope_boundaries = self._typed_text(proposal.scope_boundaries)
        if scope_boundaries:
            lines.append(f"scope_boundaries: {scope_boundaries}")
        custom_notes = self._typed_text(proposal.custom_notes)
        if custom_notes:
            lines.append(f"custom_notes: {custom_notes}")
        if proposal.comparison_required and proposal.comparison_subjects is not None:
            first, second = (self._typed_text(subject) for subject in proposal.comparison_subjects)
            lines.append(f"comparison_subjects: {first} | {second}")
        if proposal.output_language is not None:
            lines.append(f"output_language: {proposal.output_language}")
        return tuple(lines)

    @staticmethod
    def _typed_text(value: str) -> str:
        return " ".join("".join(character if character.isprintable() else " " for character in value).split())

    def _named_values(self, value: object) -> tuple[str, ...]:
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
            return ()
        values = tuple(item for item in value if isinstance(item, str) and item in _HITL1_DIMENSIONS)
        return values[:8]

    def _supported_lines(self, value: object) -> tuple[str, ...]:
        if not isinstance(value, Mapping):
            return ()
        lines: list[str] = []
        for name in sorted(_HITL1_DIMENSIONS):
            options = value.get(name)
            if not isinstance(options, Sequence) or isinstance(options, (str, bytes, bytearray)):
                continue
            safe_options = tuple(self._safe_text(item, limit=48) for item in options if self._safe_text(item, limit=48))
            if safe_options:
                lines.append(f"{name}: {', '.join(safe_options[:6])}")
        return tuple(lines[:12])

    def _snapshot(
        self,
        *,
        pending_input: PendingInputProjection | None = None,
        elapsed_seconds: float = 0.0,
    ) -> RunSnapshot:
        return RunSnapshot(
            bundle_id=self._bundle_id,
            durability=self._durability,
            lifecycle_phase=self._lifecycle_phase,
            completed_trace=tuple(self._trace),
            pending_input=pending_input,
            elapsed_seconds=max(0.0, elapsed_seconds),
            observation=self._observation_view,
        )

    def _failure_for_terminal(
        self,
        control: BundleControlResult,
        *,
        terminal_diagnostic_ref: str | None,
    ) -> RunFailure | None:
        if control.status is not LifecycleStatus.BLOCKED:
            return None
        if control.terminal_incident is not None:
            incident = control.terminal_incident
            provider_diagnostic = self._is_provider_diagnostic(control)
            diagnostic_location: Literal["bundle_journal", "unavailable"] = "unavailable"
            journal_record_created = False
            if provider_diagnostic:
                if incident.diagnostic_ref is None:
                    raise ValueError("provider_diagnostic_reference_missing")
                diagnostic_location = self._provider_diagnostic_location(control, incident.diagnostic_ref)
                journal_record_created = diagnostic_location == "bundle_journal"
            return self._failure(
                incident.code,
                phase=incident.phase,
                certainty=incident.certainty,
                diagnostic_ref=terminal_diagnostic_ref,
                worker_failure_category=incident.worker_failure_category,
                provider_recovery=incident.provider_recovery,
                provider_observation=incident.provider_observation,
                diagnostic_location=diagnostic_location,
                journal_record_created=journal_record_created,
            )
        return self._failure(
            RunFailureCode.RESEARCH_BLOCKED,
            phase=control.phase.value if control.phase is not None else None,
            certainty=FailureCertainty.UNKNOWN,
            diagnostic_ref=terminal_diagnostic_ref,
            source=control,
        )

    def _provider_diagnostic_location(self, control: BundleControlResult, diagnostic_ref: str) -> str:
        session = self._observation_view
        if (
            session is not None
            and control.bundle_id is not None
            and session.inspectability is ObservationInspectability.AVAILABLE
            and session.bundle_id == control.bundle_id
            and session.terminal_diagnostic_ref == diagnostic_ref
        ):
            return "bundle_journal"
        return "unavailable"

    @staticmethod
    def _failure_code_for_control(control: BundleControlResult) -> RunFailureCode:
        if control.availability is BundleAvailability.UNAVAILABLE:
            return RunFailureCode.BUNDLE_UNAVAILABLE
        code = control.code.value
        if code in {
            ResultCode.START_MESSAGE_INVALID.value,
            ResultCode.RESPONSE_INVALID.value,
            ResultCode.RESPONSE_MISMATCH.value,
        }:
            return RunFailureCode.INPUT_INVALID_RESPONSE
        if code == ResultCode.CHECKPOINT_INCONSISTENT.value:
            return RunFailureCode.CHECKPOINT_INCONSISTENT
        if code == ResultCode.INTERNAL_UNEXPECTED.value:
            return RunFailureCode.INTERNAL_UNEXPECTED
        if code in {"work_unit_storage_unavailable", "work_unit_store_busy"}:
            return RunFailureCode.PERSISTENCE_UNAVAILABLE
        return RunFailureCode.PROTOCOL_INVALID_RESULT

    def _fault(
        self,
        code: RunFailureCode,
        *,
        snapshot: RunSnapshot | None = None,
        source: Any = None,
    ) -> Fault:
        return Fault(snapshot=snapshot, failure=self._failure(code, source=source))

    def _failure(
        self,
        code: RunFailureCode,
        *,
        phase: str | None = None,
        certainty: FailureCertainty = FailureCertainty.DIRECT,
        diagnostic_ref: str | None = None,
        worker_failure_category: str | None = None,
        provider_recovery: ProviderRecoveryProjection | None = None,
        provider_observation: ProviderObservation | None = None,
        diagnostic_location: Literal["bundle_journal", "unavailable"] = "unavailable",
        journal_record_created: bool = False,
        source: Any = None,
    ) -> RunFailure:
        message, next_action, retryable = _FAILURE_COPY[code]
        recovery_action = None
        if (
            provider_recovery is not None
            and provider_recovery.disposition in {"exhausted", "retry_not_started_budget_consumed"}
            and code in {RunFailureCode.PROVIDER_TIMEOUT, RunFailureCode.PROVIDER_UNAVAILABLE}
        ):
            next_action = FRESH_START_NEXT_ACTION
            retryable = True
            recovery_action = "fresh_start"
        del source
        reference = diagnostic_ref
        return RunFailure(
            code=code,
            phase=phase or self._lifecycle_phase,
            certainty=certainty,
            message=message,
            next_action=next_action,
            retryable=retryable,
            diagnostic_ref=reference,
            journal_record_created=journal_record_created,
            worker_failure_category=worker_failure_category,
            provider_recovery=provider_recovery,
            provider_observation=provider_observation,
            recovery_action=recovery_action,
            diagnostic_location=diagnostic_location,
        )

    @staticmethod
    async def _notify(observer: RunObserver | None, update: Working) -> None:
        if observer is None:
            return
        observed = observer(update)
        if inspect.isawaitable(observed):
            await observed

    @staticmethod
    def _fresh_id(kind: str) -> str:
        return f"demo-{kind}-{secrets.token_urlsafe(12)}"


__all__ = ["LifecycleTransport", "ResearchRunExperience", "RunObservationPublisher"]
