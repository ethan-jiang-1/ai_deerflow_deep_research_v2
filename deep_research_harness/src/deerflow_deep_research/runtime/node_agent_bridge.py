"""Runtime-owned bridge from graph nodes to bounded node-agents.

@impl NOA-001
@impl NOA-014

This is the only raw-binding owner. Nodes call it exclusively through the pure
``NodeExecutionCapabilities`` protocol; they never import ``agents`` or
``runtime`` and never see the ``TrustedRuntimeEnvelope``. Each ``run_agent``
request resolves the model and eligible tools from trusted config, seeds an
ephemeral child state/context (parent sandbox + thread data + raw identity),
builds a *fresh* bounded agent as a separate runnable with ``checkpointer=None``,
invokes it under a wall-time budget, and discards it. Nothing is cached across
requests, users, threads, or attempts, and no second sandbox/thread lifecycle is
created. Raw identity/AppConfig/host paths live only in the ephemeral child
binding required by tools -- never in the node contract, model-facing result, or
graph checkpoint.
"""

from __future__ import annotations

import asyncio
import errno
import ipaddress
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit

import httpx
import openai
from langchain_core.messages import HumanMessage

from deerflow_deep_research.agents.factory import build_node_agent
from deerflow_deep_research.agents.middleware import (
    AgentBudgetError,
    BudgetMiddleware,
    NodeAgentStop,
    ToolExecutionFailure,
    ToolPolicyMiddleware,
)
from deerflow_deep_research.agents.node_cognitive_control_program import render_node_cognitive_control_program
from deerflow_deep_research.agents.policies import ExecutionPolicy, ProviderObservationAdmission
from deerflow_deep_research.agents.structured_output import project_failure, project_success
from deerflow_deep_research.domain.context import (
    NodeAgentContext,
    NodeExecutionRequest,
    NodeExecutionResult,
)
from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.domain.run_experience import (
    FailureCertainty,
    NodeProblem,
    ProviderObservation,
    RunFailureCode,
)
from deerflow_deep_research.domain.run_observation import BudgetStopReason, ProviderTimeoutOrigin, RunEventCategory
from deerflow_deep_research.runtime.events import build_progress_event
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope

ModelResolver = Callable[[TrustedRuntimeEnvelope], Any]
ToolsResolver = Callable[[TrustedRuntimeEnvelope, ExecutionPolicy], Sequence[Any]]
_SERVICE_LABEL_RE = re.compile(r"^[A-Za-z0-9._-]{1,96}$")
_CONNECTION_ERRNOS = frozenset(
    value
    for value in (
        errno.ECONNABORTED,
        errno.ECONNREFUSED,
        errno.ECONNRESET,
        errno.ENETDOWN,
        errno.ENETUNREACH,
        getattr(errno, "EHOSTDOWN", None),
        errno.EHOSTUNREACH,
        getattr(errno, "ETIMEDOUT", None),
    )
    if value is not None
)
_TRANSIENT_HTTP_STATUSES = frozenset({408, 429, 500, 502, 503, 504})
_AUTHENTICATION_HTTP_STATUSES = frozenset({401, 403})
_LOGICAL_PHASES = frozenset(
    {
        "bootstrap",
        "hitl1",
        "topic_planning",
        "wave0",
        "wave1",
        "wave2_synthesis",
        "targeted_evidence",
        "hitl2",
        "rerun",
        "readiness",
        "final_delivery",
    }
)
_NODE_AGENT_STOP_CODES = {
    NodeFinishReason.USAGE_UNAVAILABLE: RunFailureCode.PROVIDER_USAGE_UNAVAILABLE,
    NodeFinishReason.BUDGET_EXHAUSTED: RunFailureCode.BUDGET_EXHAUSTED,
    NodeFinishReason.POLICY_DENIED: RunFailureCode.POLICY_DENIED,
}
_MIDDLEWARE_BUDGET_STOP_REASONS = frozenset(
    {
        BudgetStopReason.REQUEST_CONTENT_UNESTIMABLE,
        BudgetStopReason.MODEL_CALL_LIMIT,
        BudgetStopReason.TOKEN_ADMISSION,
        BudgetStopReason.PER_CALL_OUTPUT_CAP,
        BudgetStopReason.TOTAL_TOKEN_BUDGET,
        BudgetStopReason.TOOL_CALLS_PER_RESPONSE,
        BudgetStopReason.PARALLEL_TOOL_CALLS,
        BudgetStopReason.TOTAL_TOOL_CALLS,
    }
)


class NodeAgentConfigurationError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"[{code}] {detail}")
        self.code = code


@dataclass(frozen=True)
class ResolvedNodeModel:
    """Runtime-only model binding for an explicitly selected configuration entry."""

    model: Any
    configured_service_label: str | None = None
    configured_endpoint_authority: str | None = None


@dataclass
class _InvocationRecording:
    """Private per-invocation Journal-only attribution; never a node result."""

    budget_stop_reason: BudgetStopReason | None = None


def _default_model_resolver(envelope: TrustedRuntimeEnvelope) -> ResolvedNodeModel:
    if not getattr(envelope.app_config, "models", None):
        raise NodeAgentConfigurationError("model_not_configured", "node-agent execution requires a configured model")
    from deerflow.models.factory import create_chat_model

    selected = envelope.app_config.models[0]
    name = getattr(selected, "name", None)
    if not isinstance(name, str) or not name:
        raise NodeAgentConfigurationError("model_not_configured", "selected model has no valid name")
    return ResolvedNodeModel(
        model=create_chat_model(name=name, app_config=envelope.app_config, attach_tracing=False),
        configured_service_label=_safe_model_label(name),
        configured_endpoint_authority=_configured_endpoint_authority(selected),
    )


def _safe_model_label(value: object) -> str | None:
    return value if isinstance(value, str) and _SERVICE_LABEL_RE.fullmatch(value) is not None else None


def _configured_endpoint_authority(selected_config: object) -> str | None:
    """Normalize only the exact selected config aliases; never inspect a model object."""

    candidates: list[str] = []
    for attribute in ("base_url", "openai_api_base", "api_base"):
        value = getattr(selected_config, attribute, None)
        if value is None:
            continue
        normalized = _normalize_endpoint_authority(value)
        if normalized is None:
            return None
        candidates.append(normalized)
    if not candidates or len(set(candidates)) != 1:
        return None
    return candidates[0]


def _normalize_endpoint_authority(value: object) -> str | None:
    if not isinstance(value, str) or not value.isascii() or not value:
        return None
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        return None
    if (
        parsed.scheme.lower() not in {"http", "https"}
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.hostname is None
        or "@" in parsed.netloc
    ):
        return None
    hostname = parsed.hostname.lower()
    try:
        is_ipv6 = ipaddress.ip_address(hostname).version == 6
    except ValueError:
        is_ipv6 = False
        labels = hostname.split(".")
        if any(
            not label
            or len(label) > 63
            or label[0] == "-"
            or label[-1] == "-"
            or not all(character.isascii() and (character.isalnum() or character == "-") for character in label)
            for label in labels
        ):
            return None
    scheme = parsed.scheme.lower()
    authority_host = f"[{hostname}]" if is_ipv6 else hostname
    if port is not None and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        authority_host = f"{authority_host}:{port}"
    normalized = f"{scheme}://{authority_host}"
    try:
        ProviderObservation(response_kind="no_response", configured_endpoint_authority=normalized)
    except ValueError:
        return None
    return normalized


def _default_tools_resolver(envelope: TrustedRuntimeEnvelope, policy: ExecutionPolicy) -> Sequence[Any]:
    from deerflow.tools.tools import get_available_tools

    # When the envelope carries a minimal demo config with no tools, fall
    # back to the global config.yaml so operators can configure web search
    # tools without threading them through the demo shim.
    app_config = envelope.app_config
    if not getattr(app_config, "tools", None):
        from deerflow.config import get_app_config

        app_config = get_app_config()
    loaded = get_available_tools(include_mcp=False, app_config=app_config)
    eligible = [tool for tool in loaded if tool.name in policy.allowed_tool_names]
    if policy.allowed_tool_names and not eligible:
        names = ",".join(sorted(policy.allowed_tool_names))
        raise NodeAgentConfigurationError("tools_unavailable", f"no configured tools satisfy policy: {names}")
    return eligible


@dataclass
class RuntimeNodeAgentBridge:
    """Implements the domain ``NodeExecutionCapabilities`` protocol."""

    envelope: TrustedRuntimeEnvelope
    policy: ExecutionPolicy
    system_prompt: str | None = None
    model_resolver: ModelResolver = _default_model_resolver
    tools_resolver: ToolsResolver = _default_tools_resolver
    agents_built: int = field(default=0)

    def _validate_capability_window(
        self,
        request: NodeExecutionRequest,
        posture_kind: str,
        allowed_tool_names: frozenset[str],
    ) -> None:
        """Reject posture/request/policy disagreement before resolving a model."""

        if posture_kind == "forbidden":
            if request.tools_enabled or request.minimum_tool_calls or request.tool_call_limit is not None:
                raise ValueError("forbidden_capability_tool_window_invalid")
            return
        if posture_kind != "required":
            raise ValueError("capability_tool_posture_invalid")
        if (
            not request.tools_enabled
            or request.minimum_tool_calls < 1
            or request.tool_call_limit is None
            or not allowed_tool_names
            or not allowed_tool_names <= self.policy.allowed_tool_names
        ):
            raise ValueError("required_capability_tool_window_invalid")

    async def run_agent(
        self,
        *,
        context: NodeAgentContext,
        request: NodeExecutionRequest,
    ) -> NodeExecutionResult:
        """Run the bounded agent and publish one safe terminal invocation fact."""

        recording = _InvocationRecording()
        result = await self._run_agent(context=context, request=request, recording=recording)
        await self._record_result(context, result, budget_stop_reason=recording.budget_stop_reason)
        return result

    async def _run_agent(
        self,
        *,
        context: NodeAgentContext,
        request: NodeExecutionRequest,
        recording: _InvocationRecording,
    ) -> NodeExecutionResult:
        if context.bundle_context is None:
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="selected_bundle_context_missing",
                code=RunFailureCode.PERSISTENCE_UNAVAILABLE,
            )
        await self._record(context, outcome="started")
        if self.envelope.parent_sandbox is None:
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="parent_isolation_missing",
                code=RunFailureCode.PERSISTENCE_UNAVAILABLE,
            )

        self._emit(context, operation="run_agent", status="started")
        if self.system_prompt is not None:
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="system_prompt_override_forbidden",
                code=RunFailureCode.INTERNAL_UNEXPECTED,
            )
        try:
            rendered_prompt = render_node_cognitive_control_program(request, attempt_workspace=context.attempt_root)
            capability = rendered_prompt.capability
            self._validate_capability_window(
                request,
                capability.posture.kind,
                capability.posture.allowed_tool_names,
            )
        except asyncio.CancelledError:
            raise
        except (TypeError, ValueError):
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="capability_admission_failed",
                code=RunFailureCode.INTERNAL_UNEXPECTED,
            )
        try:
            resolved_tools = list(self.tools_resolver(self.envelope, self.policy)) if request.tools_enabled else []
            if capability.posture.kind == "required":
                resolved_tools = [
                    tool
                    for tool in resolved_tools
                    if getattr(tool, "name", None) in capability.posture.allowed_tool_names
                ]
                if not resolved_tools:
                    raise NodeAgentConfigurationError("tools_unavailable", "no configured capability tool is available")
        except asyncio.CancelledError:
            raise
        except NodeAgentConfigurationError:
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="tools_unavailable",
                code=RunFailureCode.TOOL_UNAVAILABLE,
            )
        except Exception:
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="tools_resolver_failed",
                code=RunFailureCode.INTERNAL_UNEXPECTED,
                certainty=FailureCertainty.UNKNOWN,
            )
        try:
            resolved_model = self.model_resolver(self.envelope)
        except asyncio.CancelledError:
            raise
        except NodeAgentConfigurationError:
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="model_not_configured",
                code=RunFailureCode.CONFIGURATION_MODEL_MISSING,
            )
        except Exception:
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="model_resolver_failed",
                code=RunFailureCode.INTERNAL_UNEXPECTED,
                certainty=FailureCertainty.UNKNOWN,
            )
        binding = self._model_binding(resolved_model)
        budget_middleware = BudgetMiddleware(self.policy.budget)
        tool_policy_middleware = ToolPolicyMiddleware(self.policy, tool_call_limit=request.tool_call_limit)
        try:
            agent = build_node_agent(
                model=binding.model,
                tools=resolved_tools,
                middleware=[budget_middleware, tool_policy_middleware],
                system_prompt=rendered_prompt.system_policy,
            )
        except asyncio.CancelledError:
            raise
        except Exception:
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="agent_construction_failed",
                code=RunFailureCode.INTERNAL_UNEXPECTED,
                certainty=FailureCertainty.UNKNOWN,
            )
        self.agents_built += 1

        child_state = self._ephemeral_child_state(context, rendered_prompt.user_message)
        child_context = self._ephemeral_child_context()
        admitted_provider_request = self._is_admitted_provider_request(request)
        deadline = asyncio.timeout(self.policy.budget.wall_time_seconds)
        try:
            async with deadline:
                result = await agent.ainvoke(child_state, context=child_context)
        except TimeoutError:
            if deadline.expired():
                recording.budget_stop_reason = BudgetStopReason.BRIDGE_WALL_TIME
                self._emit(context, operation="run_agent", status="budget_exhausted")
                if admitted_provider_request:
                    return self._provider_failure(
                        context,
                        NodeFinishReason.BUDGET_EXHAUSTED,
                        error_code="wall_time",
                        code=RunFailureCode.PROVIDER_TIMEOUT,
                        binding=binding,
                        timeout_origin="bridge_wall_time_budget",
                    )
                return self._safe_failure(
                    context,
                    NodeFinishReason.BUDGET_EXHAUSTED,
                    error_code="wall_time",
                    code=RunFailureCode.PROVIDER_TIMEOUT,
                )
            # A bare inner TimeoutError is not proof that the bridge deadline expired.
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="agent_invocation_failed",
                code=(
                    RunFailureCode.INTERNAL_UNEXPECTED if admitted_provider_request else RunFailureCode.PROVIDER_TIMEOUT
                ),
                certainty=FailureCertainty.UNKNOWN if admitted_provider_request else FailureCertainty.DIRECT,
            )
        except ToolExecutionFailure:
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="tool_execution_failed",
                code=RunFailureCode.TOOL_EXECUTION_FAILED,
            )
        except NodeAgentStop as exc:
            if exc.finish_reason is NodeFinishReason.BUDGET_EXHAUSTED:
                candidate = exc.budget_stop_reason if isinstance(exc, AgentBudgetError) else None
                recording.budget_stop_reason = (
                    candidate if candidate in _MIDDLEWARE_BUDGET_STOP_REASONS else BudgetStopReason.UNKNOWN
                )
            self._emit(context, operation="run_agent", status=str(exc.finish_reason))
            return self._safe_failure(
                context,
                exc.finish_reason,
                error_code="policy",
                code=_NODE_AGENT_STOP_CODES.get(exc.finish_reason, RunFailureCode.INTERNAL_UNEXPECTED),
            )
        except asyncio.CancelledError:
            # Never convert cancellation into success; the child runnable and its
            # tasks are torn down as the exception propagates.
            raise
        except httpx.TimeoutException:
            if admitted_provider_request:
                return self._provider_failure(
                    context,
                    NodeFinishReason.FAILED,
                    error_code="provider_timeout",
                    code=RunFailureCode.PROVIDER_TIMEOUT,
                    binding=binding,
                )
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="agent_invocation_failed",
                code=RunFailureCode.INTERNAL_UNEXPECTED,
                certainty=FailureCertainty.UNKNOWN,
            )
        except openai.APITimeoutError:
            if admitted_provider_request:
                return self._provider_failure(
                    context,
                    NodeFinishReason.FAILED,
                    error_code="provider_timeout",
                    code=RunFailureCode.PROVIDER_TIMEOUT,
                    binding=binding,
                    timeout_origin="provider_sdk_timeout",
                )
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="agent_invocation_failed",
                code=RunFailureCode.INTERNAL_UNEXPECTED,
                certainty=FailureCertainty.UNKNOWN,
            )
        except httpx.HTTPStatusError as exc:
            status = self._httpx_status(exc)
            if admitted_provider_request and status is not None:
                return self._http_status_failure(context, status=status, binding=binding)
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="agent_invocation_failed",
                code=RunFailureCode.INTERNAL_UNEXPECTED,
                certainty=FailureCertainty.UNKNOWN,
            )
        except openai.APIStatusError as exc:
            status = self._openai_status(exc)
            if admitted_provider_request and status is not None:
                return self._http_status_failure(context, status=status, binding=binding)
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="agent_invocation_failed",
                code=RunFailureCode.INTERNAL_UNEXPECTED,
                certainty=FailureCertainty.UNKNOWN,
            )
        except PermissionError:
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="provider_authentication_failed",
                code=RunFailureCode.PROVIDER_AUTHENTICATION_FAILED,
            )
        except ConnectionError:
            if admitted_provider_request:
                return self._provider_failure(
                    context,
                    NodeFinishReason.FAILED,
                    error_code="provider_unavailable",
                    code=RunFailureCode.PROVIDER_UNAVAILABLE,
                    binding=binding,
                )
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="provider_unavailable",
                code=RunFailureCode.PROVIDER_UNAVAILABLE,
            )
        except httpx.NetworkError:
            if admitted_provider_request:
                return self._provider_failure(
                    context,
                    NodeFinishReason.FAILED,
                    error_code="provider_unavailable",
                    code=RunFailureCode.PROVIDER_UNAVAILABLE,
                    binding=binding,
                )
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="agent_invocation_failed",
                code=RunFailureCode.INTERNAL_UNEXPECTED,
                certainty=FailureCertainty.UNKNOWN,
            )
        except openai.APIConnectionError:
            if admitted_provider_request:
                return self._provider_failure(
                    context,
                    NodeFinishReason.FAILED,
                    error_code="provider_unavailable",
                    code=RunFailureCode.PROVIDER_UNAVAILABLE,
                    binding=binding,
                )
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="agent_invocation_failed",
                code=RunFailureCode.INTERNAL_UNEXPECTED,
                certainty=FailureCertainty.UNKNOWN,
            )
        except OSError as exc:
            if admitted_provider_request and exc.errno in _CONNECTION_ERRNOS:
                return self._provider_failure(
                    context,
                    NodeFinishReason.FAILED,
                    error_code="provider_unavailable",
                    code=RunFailureCode.PROVIDER_UNAVAILABLE,
                    binding=binding,
                )
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code=("agent_invocation_failed" if admitted_provider_request else "provider_unavailable"),
                code=(
                    RunFailureCode.INTERNAL_UNEXPECTED
                    if admitted_provider_request
                    else RunFailureCode.PROVIDER_UNAVAILABLE
                ),
                certainty=FailureCertainty.UNKNOWN if admitted_provider_request else FailureCertainty.DIRECT,
            )
        except Exception:
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="agent_invocation_failed",
                code=RunFailureCode.INTERNAL_UNEXPECTED,
                certainty=FailureCertainty.UNKNOWN,
            )
        if tool_policy_middleware.tool_calls < request.minimum_tool_calls:
            self._emit(context, operation="run_agent", status="required_tool_not_called")
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="required_tool_not_called",
                code=RunFailureCode.TOOL_EXECUTION_FAILED,
            )
        try:
            node_result = self._project_result(
                result,
                untrusted_tool_results=tuple(tool_policy_middleware.tool_results),
            )
        except asyncio.CancelledError:
            raise
        except Exception:
            return self._safe_failure(
                context,
                NodeFinishReason.FAILED,
                error_code="structured_output_invalid",
                code=RunFailureCode.OUTPUT_STRUCTURED_INVALID,
            )
        self._emit(context, operation="run_agent", status="completed")
        return node_result

    async def _record_result(
        self,
        context: NodeAgentContext,
        result: NodeExecutionResult,
        *,
        budget_stop_reason: BudgetStopReason | None,
    ) -> None:
        problem = result.problem
        if problem is None:
            await self._record(context, outcome="completed")
            return
        code = problem.code.value
        provider_category = (
            code
            if code
            in {
                RunFailureCode.PROVIDER_TIMEOUT.value,
                RunFailureCode.PROVIDER_UNAVAILABLE.value,
                RunFailureCode.PROVIDER_AUTHENTICATION_FAILED.value,
            }
            else None
        )
        worker_failure_category = (
            "tool_execution"
            if problem.code in {RunFailureCode.TOOL_UNAVAILABLE, RunFailureCode.TOOL_EXECUTION_FAILED}
            else "structured_output"
            if problem.code is RunFailureCode.OUTPUT_STRUCTURED_INVALID
            else "agent_invocation"
            if problem.certainty is FailureCertainty.DIRECT
            else "unknown"
        )
        await self._record(
            context,
            outcome="failed",
            failure_category=code,
            worker_failure_category=worker_failure_category,
            provider_category=provider_category,
            budget_stop_reason=(
                budget_stop_reason
                if (
                    (
                        budget_stop_reason is BudgetStopReason.BRIDGE_WALL_TIME
                        and problem.code is RunFailureCode.PROVIDER_TIMEOUT
                    )
                    or (
                        budget_stop_reason is not BudgetStopReason.BRIDGE_WALL_TIME
                        and problem.code is RunFailureCode.BUDGET_EXHAUSTED
                    )
                )
                else None
            ),
        )

    async def _record(
        self,
        context: NodeAgentContext,
        *,
        outcome: str,
        failure_category: str | None = None,
        worker_failure_category: str | None = None,
        provider_category: str | None = None,
        budget_stop_reason: BudgetStopReason | None = None,
    ) -> None:
        factory = self.envelope.event_recorder_factory
        if factory is None:
            return
        try:
            event: dict[str, Any] = {
                "category": RunEventCategory.MODEL_TOOL,
                "phase": context.node_name,
                "attempt_id": context.attempt_id,
                "outcome": outcome,
                "failure_category": failure_category,
                "worker_failure_category": worker_failure_category,
                "provider_category": provider_category,
            }
            if budget_stop_reason is not None:
                event["budget_stop_reason"] = budget_stop_reason
            await factory(context.research_scope_id).record(
                **event,
            )
        except Exception:
            return
        self._emit(context, operation="journal", status=outcome)

    @staticmethod
    def _problem(
        context: NodeAgentContext,
        *,
        code: RunFailureCode,
        certainty: FailureCertainty,
        provider_observation: ProviderObservation | None = None,
    ) -> NodeProblem:
        phase = context.node_name if context.node_name in _LOGICAL_PHASES else None
        return NodeProblem(
            code=code,
            phase=phase,
            certainty=certainty,
            provider_observation=provider_observation,
        )

    def _safe_failure(
        self,
        context: NodeAgentContext,
        finish_reason: NodeFinishReason,
        *,
        error_code: str,
        code: RunFailureCode,
        certainty: FailureCertainty = FailureCertainty.DIRECT,
        provider_observation: ProviderObservation | None = None,
    ) -> NodeExecutionResult:
        return project_failure(
            finish_reason,
            error_code=error_code,
            problem=self._problem(
                context,
                code=code,
                certainty=certainty,
                provider_observation=provider_observation,
            ),
        )

    @staticmethod
    def _model_binding(value: Any) -> ResolvedNodeModel:
        return value if isinstance(value, ResolvedNodeModel) else ResolvedNodeModel(model=value)

    def _is_admitted_provider_request(self, request: NodeExecutionRequest) -> bool:
        return (
            self.policy.provider_observation_admission is ProviderObservationAdmission.CONFIGURED_MODEL_SERVICE
            and request.tools_enabled is False
        )

    @staticmethod
    def _safe_binding_observation(
        binding: ResolvedNodeModel,
        *,
        response_kind: str,
        http_status: int | None = None,
        timeout_origin: ProviderTimeoutOrigin | None = None,
    ) -> ProviderObservation:
        label = _safe_model_label(binding.configured_service_label)
        authority: str | None = None
        if isinstance(binding.configured_endpoint_authority, str):
            try:
                ProviderObservation(
                    response_kind="no_response",
                    configured_endpoint_authority=binding.configured_endpoint_authority,
                )
            except ValueError:
                authority = None
            else:
                authority = binding.configured_endpoint_authority
        return ProviderObservation(
            configured_service_label=label,
            configured_endpoint_authority=authority,
            response_kind=response_kind,  # type: ignore[arg-type]
            http_status=http_status,
            timeout_origin=timeout_origin,
        )

    def _provider_failure(
        self,
        context: NodeAgentContext,
        finish_reason: NodeFinishReason,
        *,
        error_code: str,
        code: RunFailureCode,
        binding: ResolvedNodeModel,
        http_status: int | None = None,
        timeout_origin: ProviderTimeoutOrigin | None = None,
    ) -> NodeExecutionResult:
        observation = self._safe_binding_observation(
            binding,
            response_kind="http_response" if http_status is not None else "no_response",
            http_status=http_status,
            timeout_origin=timeout_origin,
        )
        return self._safe_failure(
            context,
            finish_reason,
            error_code=error_code,
            code=code,
            provider_observation=observation,
        )

    def _http_status_failure(
        self,
        context: NodeAgentContext,
        *,
        status: int,
        binding: ResolvedNodeModel,
    ) -> NodeExecutionResult:
        if status in _TRANSIENT_HTTP_STATUSES:
            code = RunFailureCode.PROVIDER_UNAVAILABLE
        elif status in _AUTHENTICATION_HTTP_STATUSES:
            code = RunFailureCode.PROVIDER_AUTHENTICATION_FAILED
        else:
            code = RunFailureCode.INTERNAL_UNEXPECTED
        return self._provider_failure(
            context,
            NodeFinishReason.FAILED,
            error_code="provider_http_status",
            code=code,
            binding=binding,
            http_status=status,
        )

    @staticmethod
    def _httpx_status(exc: httpx.HTTPStatusError) -> int | None:
        status = exc.response.status_code
        return status if isinstance(status, int) and 100 <= status <= 599 else None

    @staticmethod
    def _openai_status(exc: openai.APIStatusError) -> int | None:
        status = exc.status_code
        return status if isinstance(status, int) and 100 <= status <= 599 else None

    def _emit(self, context: NodeAgentContext, *, operation: str, status: str) -> None:
        emitter = self.envelope.progress
        if emitter is None:
            return
        try:
            emitter.emit(
                build_progress_event(
                    kind="node_agent",
                    ref=context.research_scope_id,
                    operation=f"{context.node_name}.{operation}",
                    status=status,
                )
            )
        except Exception:
            # A DeerFlow custom-stream subscriber is only a live projection.
            return

    def _ephemeral_child_state(self, context: NodeAgentContext, user_message: str) -> dict[str, Any]:
        sandbox = self.envelope.parent_sandbox
        sandbox_id = getattr(sandbox, "id", None) or getattr(sandbox, "sandbox_id", None)
        return {
            "messages": [HumanMessage(user_message)],
            "sandbox": {"sandbox_id": sandbox_id},
            "thread_data": {"thread_id": self.envelope.outer_thread_id},
        }

    def _ephemeral_child_context(self) -> dict[str, Any]:
        return {
            "user_id": self.envelope.effective_user_id,
            "thread_id": self.envelope.outer_thread_id,
            "run_id": self.envelope.outer_run_id,
            "app_config": self.envelope.app_config,
        }

    def _project_result(
        self,
        result: Any,
        *,
        untrusted_tool_results: tuple[str, ...] = (),
    ) -> NodeExecutionResult:
        messages = result.get("messages") if isinstance(result, dict) else None
        summary = ""
        if messages:
            content = getattr(messages[-1], "content", "")
            summary = content if isinstance(content, str) else ""
        return project_success(
            summary,
            (),
            policy=self.policy,
            untrusted_tool_results=untrusted_tool_results,
        )


__all__ = ["NodeAgentConfigurationError", "RuntimeNodeAgentBridge"]
