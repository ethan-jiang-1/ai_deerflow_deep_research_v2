"""Strict reflected Deep Research control tool.

@impl RUI-001
@impl RUI-006
@impl REG-004
"""

from __future__ import annotations

import json
import secrets
from collections.abc import Callable, Mapping
from typing import Annotated, Any

from langchain.tools import ToolRuntime
from langchain_core.messages import AIMessage
from langchain_core.tools import InjectedToolArg, tool
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from pydantic.json_schema import SkipJsonSchema

from deerflow_deep_research.runtime.bundle_control import BundleControl
from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle, CurrentBundleHandle
from deerflow_deep_research.runtime.control import get_default_graph_host
from deerflow_deep_research.runtime.human_input import HumanInputError, select_start_message
from deerflow_deep_research.runtime.identity import TrustedIdentityError
from deerflow_deep_research.runtime.non_interactive import NonInteractivePolicy, StartActionInput
from deerflow_deep_research.runtime.runtime_adapter import RuntimeAdapter, RuntimeAdapterError

ADVERTISED_ACTION = "infra_probe"
ADVERTISED_ACTIONS = ("infra_probe", "start", "resume", "status", "cancel", "refine")
_PROBE_ID_PATTERN = r"^[A-Za-z0-9_-]{1,64}$"
_BUNDLE_ID_PATTERN = r"^b_[A-Za-z0-9_-]{43}$"


class DeepResearchArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    action: str = Field(min_length=1, max_length=32)
    probe_id: str | None = Field(default=None, pattern=_PROBE_ID_PATTERN)
    bundle_id: str | None = Field(default=None, pattern=_BUNDLE_ID_PATTERN)
    refinement: str | None = Field(default=None, min_length=1, max_length=4_096)
    # The runtime is accepted only after ToolNode replaces any model input with its
    # trusted value. SkipJsonSchema keeps it out of the public tool contract.
    runtime: Annotated[SkipJsonSchema[ToolRuntime | None], InjectedToolArg] = Field(default=None)

    @model_validator(mode="after")
    def validate_action_fields(self) -> DeepResearchArgs:
        if self.action == "infra_probe":
            if self.bundle_id is not None or self.refinement is not None:
                raise ValueError("infra_probe accepts only probe_id")
        elif self.action == "start":
            if self.probe_id is not None or self.bundle_id is not None or self.refinement is not None:
                raise ValueError("start accepts no caller-selected id")
        elif self.action in {"resume", "status", "cancel"}:
            if self.probe_id is not None or self.refinement is not None:
                raise ValueError("lifecycle action accepts only bundle_id")
        elif self.action == "refine":
            if self.probe_id is not None:
                raise ValueError("refine accepts no probe_id")
            if self.refinement is None and self.bundle_id is None:
                raise ValueError("textless refine requires explicit bundle_id")
            if self.refinement is not None and not self.refinement.strip():
                raise ValueError("refine requires bounded nonblank refinement text")
        elif self.probe_id is not None or self.bundle_id is not None or self.refinement is not None:
            raise ValueError("unknown action accepts no authority fields")
        return self


def generate_probe_id() -> str:
    return secrets.token_urlsafe(16)


def normalize_validation_error(exc: ValidationError) -> dict[str, Any]:
    fields = sorted({".".join(str(part) for part in error["loc"]) for error in exc.errors()})
    codes = sorted({error["type"] for error in exc.errors()})
    return {"code": "invalid_arguments", "fields": fields, "violations": codes}


def _exclusive_lifecycle_call(runtime: Any) -> bool:
    state = getattr(runtime, "state", None)
    messages = state.get("messages", ()) if isinstance(state, dict) else ()
    latest = next((message for message in reversed(messages) if isinstance(message, AIMessage)), None)
    if latest is None or len(latest.tool_calls) != 1:
        return False
    call = latest.tool_calls[0]
    return call.get("name") == "deep_research" and call.get("id") == getattr(runtime, "tool_call_id", None)


def _runtime_messages(runtime: Any) -> tuple[Any, ...]:
    state = getattr(runtime, "state", None)
    return tuple(state.get("messages", ())) if isinstance(state, dict) else ()


def _admitted_start_action_input(*, action: str, context: Mapping[str, Any]) -> StartActionInput | None:
    """Validate a marked trusted policy before the lifecycle can publish a Bundle."""

    if action not in {"start", "resume", "refine"}:
        return None
    marked_non_interactive = context.get("non_interactive") is True or context.get("disable_clarification") is True
    if not marked_non_interactive:
        return None
    candidate = context.get("non_interactive_policy")
    required_keys = {"auto_profile", "auto_proceed"}
    if not isinstance(candidate, Mapping) or set(candidate) != required_keys:
        raise ValueError("non_interactive_policy_invalid")
    if candidate["auto_profile"] is not True or candidate["auto_proceed"] is not True:
        raise ValueError("non_interactive_policy_invalid")
    if action != "start":
        return None
    return StartActionInput(
        non_interactive_policy=NonInteractivePolicy(
            auto_profile=candidate["auto_profile"],
            auto_proceed=candidate["auto_proceed"],
        )
    )


def _production_bundle_graph_executor() -> BundleGraphExecutor:
    """Construct one public graph executor only through trusted runtime composition."""

    return BundleGraphExecutor()


async def run_deep_research(
    *,
    action: str,
    probe_id: str | None,
    runtime: Any,
    bundle_id: str | None = None,
    refinement: str | None = None,
    adapter: RuntimeAdapter | None = None,
    host_factory: Any = None,
    bundle_graph_executor: Any = None,
    bundle_graph_executor_factory: Callable[[], BundleGraphExecutor] | None = None,
) -> Any:
    """Dispatch a strict public action through its single owning runtime boundary."""
    if action not in ADVERTISED_ACTIONS:
        return {
            "code": "action_unavailable",
            "supported": list(ADVERTISED_ACTIONS),
        }

    lifecycle_action = BundleControl.action_from_wire(action)
    if lifecycle_action is not None and not _exclusive_lifecycle_call(runtime):
        return BundleControl.unavailable_wire_result(
            action=lifecycle_action,
            code="exclusive_control_call_required",
        )

    adapter = adapter or RuntimeAdapter()
    try:
        initialize_parent_sandbox = action in {"start", "resume"}
        envelope = await adapter.adapt(
            runtime,
            initialize_parent_sandbox=initialize_parent_sandbox,
        )
    except (TrustedIdentityError, RuntimeAdapterError) as exc:
        if lifecycle_action is None:
            return {"code": exc.code}
        return BundleControl.unavailable_wire_result(action=lifecycle_action, code=exc.code)

    if lifecycle_action is None:
        host = host_factory() if host_factory is not None else get_default_graph_host()
        if not host.is_registered(action):
            return {"code": "action_unavailable", "supported": ["infra_probe"]}
        return await host.run_action(
            action=action,
            envelope=envelope,
            action_input=probe_id or generate_probe_id(),
        )

    context = getattr(runtime, "context", None)
    context = context if isinstance(context, dict) else {}
    try:
        start_input = _admitted_start_action_input(action=action, context=context)
    except ValueError:
        return BundleControl.unavailable_wire_result(action=lifecycle_action, code="interactive_required")
    if action in {"start", "resume", "refine"} and (context.get("channel_user_id") or context.get("channel_name")):
        return BundleControl.unavailable_wire_result(
            action=lifecycle_action,
            code="human_input_transport_unavailable",
        )

    messages = _runtime_messages(runtime)
    start_message = None
    if action == "start":
        try:
            start_message = select_start_message(messages)
        except HumanInputError:
            return BundleControl.unavailable_wire_result(action=lifecycle_action, code="start_message_invalid")

    handle = _trusted_handle(runtime)
    lifecycle = BundleLifecycle(workspace_host_path=envelope.workspace_host_path)
    controller = BundleControl(
        lifecycle=lifecycle,
        graph_executor=bundle_graph_executor,
        graph_executor_factory=None if bundle_graph_executor is not None else bundle_graph_executor_factory,
    )
    return await controller.dispatch(
        action=lifecycle_action,
        effective_user_id=envelope.effective_user_id,
        outer_thread_id=envelope.outer_thread_id,
        messages=messages,
        tool_call_id=str(getattr(runtime, "tool_call_id", "")),
        bundle_id=bundle_id,
        refinement=refinement,
        handle=handle,
        start_message=start_message,
        envelope=envelope,
        start_input=start_input,
    )


def _trusted_handle(runtime: Any) -> CurrentBundleHandle | None:
    """Accept a Handle only when the trusted runtime inserted the typed object."""

    context = getattr(runtime, "context", None)
    if not isinstance(context, dict):
        return None
    handle = context.get("deep_research_current_bundle_handle")
    return handle if isinstance(handle, CurrentBundleHandle) else None


@tool("deep_research", args_schema=DeepResearchArgs)
async def deep_research_tool(
    action: str,
    probe_id: str | None = None,
    bundle_id: str | None = None,
    refinement: str | None = None,
    runtime: Annotated[ToolRuntime | None, InjectedToolArg] = None,
) -> Any:
    """Route the infra probe or an all-real research lifecycle action.

    Args:
        action: One of ``infra_probe|start|resume|status|cancel|refine``.
        probe_id: Optional opaque id accepted only by ``infra_probe``.
        bundle_id: Opaque Run Bundle id for an existing lifecycle target.
        refinement: Bounded run-level direction required only by ``refine``.
        runtime: Trusted runtime injected by LangGraph ToolNode.
    """
    try:
        args = DeepResearchArgs(action=action, probe_id=probe_id, bundle_id=bundle_id, refinement=refinement)
    except ValidationError as exc:
        return json.dumps(normalize_validation_error(exc), sort_keys=True)
    result = await run_deep_research(
        action=args.action,
        probe_id=args.probe_id,
        bundle_id=args.bundle_id,
        refinement=args.refinement,
        runtime=runtime,
        bundle_graph_executor_factory=_production_bundle_graph_executor,
    )
    if not isinstance(result, dict):
        return result
    return json.dumps(result, sort_keys=True)


__all__ = ["DeepResearchArgs", "deep_research_tool", "generate_probe_id", "run_deep_research"]
