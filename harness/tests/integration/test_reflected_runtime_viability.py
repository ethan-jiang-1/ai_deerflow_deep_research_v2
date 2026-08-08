"""Hard viability gate for reflected async ToolRuntime injection.

@impl RUI-001
@impl RUI-006
"""

from __future__ import annotations

import json
import secrets
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from deerflow.config.app_config import AppConfig
from deerflow.config.tool_config import ToolConfig
from deerflow.tools.tools import get_available_tools
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime
from langgraph.types import Command

from deerflow_deep_research.domain.lifecycle import LifecycleStatus
from deerflow_deep_research.domain.state import PhaseStatus
from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore
from tests.fixtures.recipes import fixture_recipe

TOOL_NAME = "deep_research_runtime_viability_probe"
TOOL_PATH = "tests.fixtures.reflected_runtime_tool:runtime_viability_probe"
COMMAND_TOOL_NAME = "deep_research_command_viability_probe"
COMMAND_TOOL_PATH = "tests.fixtures.reflected_runtime_tool:command_viability_probe"
CONTROL_TOOL_NAME = "deep_research"
CONTROL_TOOL_PATH = "deerflow_deep_research.tool:deep_research_tool"


def _config_with_reflected_probe() -> AppConfig:
    return AppConfig(
        sandbox={"use": "deerflow.sandbox.local:LocalSandboxProvider"},
        tools=[ToolConfig(name=TOOL_NAME, group="deep-research-viability", use=TOOL_PATH)],
    )


def _config_with_reflected_command_probe() -> AppConfig:
    return AppConfig(
        sandbox={"use": "deerflow.sandbox.local:LocalSandboxProvider"},
        tools=[ToolConfig(name=COMMAND_TOOL_NAME, group="deep-research-viability", use=COMMAND_TOOL_PATH)],
    )


def _config_with_reflected_control_tool() -> AppConfig:
    return AppConfig(
        sandbox={"use": "deerflow.sandbox.local:LocalSandboxProvider"},
        tools=[ToolConfig(name=CONTROL_TOOL_NAME, group="deep-research-control", use=CONTROL_TOOL_PATH)],
    )


def _fixture_envelope(tmp_path: Path) -> TrustedRuntimeEnvelope:
    workspace = tmp_path / "workspace"
    uploads = tmp_path / "uploads"
    outputs = tmp_path / "outputs"
    workspace.mkdir()
    uploads.mkdir()
    outputs.mkdir()
    return TrustedRuntimeEnvelope(
        effective_user_id="viability-user",
        outer_thread_id="viability-thread",
        outer_run_id="viability-run",
        app_config=SimpleNamespace(models=(), tools=(), checkpointer=None, database=None),
        workspace_host_path=workspace,
        uploads_host_path=uploads,
        outputs_host_path=outputs,
        workspace_virtual_root="/mnt/user-data/workspace",
        uploads_virtual_root="/mnt/user-data/uploads",
        outputs_virtual_root="/mnt/user-data/outputs",
        parent_sandbox=object(),
        progress=None,
    )


def _fixture_executor(tmp_path: Path) -> BundleGraphExecutor:
    async def create(_envelope, *, bundle, **_kwargs):  # noqa: ANN001
        return WorkUnitStore(
            workspace_host_path=tmp_path / "workspace",
            bundle=bundle,
            clock=lambda: datetime(2026, 8, 7, tzinfo=UTC),
            monotonic=time.monotonic,
            lock_sleep=time.sleep,
            token_factory=lambda: secrets.token_hex(16),
            fault_hook=None,
        )

    return BundleGraphExecutor(recipe=fixture_recipe(work_unit_store_factory=create))


async def _stage_terminal_bundle(
    *,
    lifecycle: BundleLifecycle,
    bundle,
    executor: BundleGraphExecutor,
) -> None:
    config = executor._config(bundle)
    async with lifecycle.open_graph_checkpoint(bundle) as saver:
        graph = executor._recipe.builder.compile(checkpointer=saver)
        await graph.aupdate_state(
            config,
            {
                "schema_version": 2,
                "bundle_id": bundle.bundle_id.value,
                "start_message_id": "fixture-start",
                "request_digest": "d_" + "R" * 43,
                "request_text": "Fixture terminal snapshot.",
                "phase": "final_delivery",
                "route": "pass",
                "phase_status": PhaseStatus.TERMINAL.value,
                "terminal_status": LifecycleStatus.COMPLETED.value,
                "generation": 0,
                "repair_counts": {},
                "wave0_results": (),
                "wave1_results": (),
                "consumed_request_ids": (),
                "consumed_message_ids": (),
                "execution_trace": ("final_delivery",),
            },
            as_node="final_delivery",
        )
        terminal = await graph.aget_state(config)
    await lifecycle.sync_graph_progress(bundle=bundle, values=dict(terminal.values), pending=None)


class _FixtureRuntimeAdapter:
    def __init__(self, envelope: TrustedRuntimeEnvelope) -> None:
        self.envelope = envelope
        self.initialize_parent_sandbox: list[bool] = []

    async def adapt(self, _runtime, *, initialize_parent_sandbox: bool = True):  # noqa: ANN001
        self.initialize_parent_sandbox.append(initialize_parent_sandbox)
        return self.envelope


async def _invoke_reflected_control(
    *,
    control: BaseTool,
    envelope: TrustedRuntimeEnvelope,
    call_id: str,
    args: dict[str, object],
    preceding_messages: tuple[object, ...] = (),
) -> object:
    state = {
        "messages": [
            *preceding_messages,
            AIMessage(
                content="",
                tool_calls=[{"name": CONTROL_TOOL_NAME, "args": args, "id": call_id}],
            ),
        ]
    }
    return await ToolNode([control]).ainvoke(
        state,
        config={
            "configurable": {
                "__pregel_runtime": Runtime(
                    context={
                        "user_id": envelope.effective_user_id,
                        "thread_id": envelope.outer_thread_id,
                        "run_id": envelope.outer_run_id,
                    }
                )
            }
        },
    )


def test_reflected_control_tool_exposes_expanded_lifecycle_schema_without_new_config() -> None:
    loaded = get_available_tools(
        groups=["deep-research-control"],
        include_mcp=False,
        app_config=_config_with_reflected_control_tool(),
    )
    control = next(tool for tool in loaded if tool.name == CONTROL_TOOL_NAME)
    schema = control.get_input_schema().model_json_schema()

    assert control.coroutine is not None
    assert set(schema["properties"]) == {"action", "probe_id", "bundle_id", "refinement"}
    assert "infra_probe|start|resume|status|cancel|refine" in control.description
    assert CONTROL_TOOL_PATH == "deerflow_deep_research.tool:deep_research_tool"


@pytest.mark.asyncio
async def test_reflected_control_tool_passes_the_exact_trusted_runtime_to_its_handler(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The custom public schema must retain ToolNode's trusted injection path."""

    loaded = get_available_tools(
        groups=["deep-research-control"],
        include_mcp=False,
        app_config=_config_with_reflected_control_tool(),
    )
    control = next(tool for tool in loaded if tool.name == CONTROL_TOOL_NAME)
    from deerflow_deep_research import tool as public_tool

    observed: dict[str, object] = {}

    async def observe_dispatch(*, runtime: object, **_kwargs: object) -> dict[str, str]:
        observed["runtime"] = runtime
        return {"code": "observed"}

    monkeypatch.setattr(public_tool, "run_deep_research", observe_dispatch)
    state = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[{"name": CONTROL_TOOL_NAME, "args": {"action": "status"}, "id": "control-call"}],
            )
        ],
        "state_sentinel": "control-state",
    }
    outer_runtime = Runtime(context={"user_id": "viability-user", "thread_id": "viability-thread"})

    result = await ToolNode([control]).ainvoke(
        state,
        config={"configurable": {"__pregel_runtime": outer_runtime}},
    )

    assert json.loads(result["messages"][0].content) == {"code": "observed"}
    runtime = observed["runtime"]
    assert runtime.tool_call_id == "control-call"
    assert runtime.state is state
    assert runtime.context == {"user_id": "viability-user", "thread_id": "viability-thread"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("tool_calls", "tool_call_id"),
    [
        ([], "control-call"),
        ([{"name": CONTROL_TOOL_NAME, "args": {"action": "status"}, "id": "different-call"}], "control-call"),
        (
            [
                {"name": CONTROL_TOOL_NAME, "args": {"action": "status"}, "id": "control-call"},
                {"name": "other", "args": {}, "id": "sibling-call"},
            ],
            "control-call",
        ),
        (
            [
                {"name": CONTROL_TOOL_NAME, "args": {"action": "status"}, "id": "control-call"},
                {"name": CONTROL_TOOL_NAME, "args": {"action": "status"}, "id": "second-call"},
            ],
            "control-call",
        ),
    ],
    ids=("missing", "mismatched", "sibling", "plural"),
)
async def test_public_control_refuses_nonexclusive_runtime_calls(
    tool_calls: list[dict[str, object]],
    tool_call_id: str,
) -> None:
    from deerflow_deep_research import tool as public_tool

    runtime = SimpleNamespace(
        state={"messages": [AIMessage(content="", tool_calls=tool_calls)]},
        context={},
        tool_call_id=tool_call_id,
    )
    assert public_tool.deep_research_tool.coroutine is not None

    result = await public_tool.deep_research_tool.coroutine(action="status", runtime=runtime)
    payload = json.loads(result)

    assert payload["action"] == "status"
    assert payload["code"] == "exclusive_control_call_required"


@pytest.mark.asyncio
async def test_reflected_public_tool_uses_the_trusted_graph_factory_for_ended_refinement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RUI-006: the reflected production wrapper cannot fall back to fake lifecycle work."""

    envelope = _fixture_envelope(tmp_path)
    lifecycle = BundleLifecycle(workspace_host_path=envelope.workspace_host_path)
    bundle = await lifecycle.start(
        scope=(envelope.effective_user_id, envelope.outer_thread_id),
        request_text="Fixture terminal question.",
    )
    executor = _fixture_executor(tmp_path)
    await _stage_terminal_bundle(lifecycle=lifecycle, bundle=bundle, executor=executor)
    adapter = _FixtureRuntimeAdapter(envelope)

    from deerflow_deep_research import tool as public_tool

    factory_calls: list[None] = []

    def build_executor() -> BundleGraphExecutor:
        factory_calls.append(None)
        return executor

    monkeypatch.setattr(public_tool, "RuntimeAdapter", lambda: adapter)
    monkeypatch.setattr(public_tool, "BundleGraphExecutor", build_executor, raising=False)
    loaded = get_available_tools(
        groups=["deep-research-control"],
        include_mcp=False,
        app_config=_config_with_reflected_control_tool(),
    )
    control = next(tool for tool in loaded if tool.name == CONTROL_TOOL_NAME)
    state = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": CONTROL_TOOL_NAME,
                        "args": {
                            "action": "refine",
                            "bundle_id": bundle.bundle_id.value,
                            "refinement": "Prioritize primary regulatory sources.",
                        },
                        "id": "ended-refinement",
                    }
                ],
            )
        ]
    }

    result = await ToolNode([control]).ainvoke(
        state,
        config={
            "configurable": {
                "__pregel_runtime": Runtime(
                    context={
                        "user_id": envelope.effective_user_id,
                        "thread_id": envelope.outer_thread_id,
                        "run_id": envelope.outer_run_id,
                    }
                )
            }
        },
    )

    payload = json.loads(result["messages"][0].content)
    current = await lifecycle.read_state(bundle)
    async with lifecycle.open_graph_checkpoint(bundle) as saver:
        snapshot = await executor._recipe.builder.compile(checkpointer=saver).aget_state(executor._config(bundle))

    assert factory_calls == [None]
    assert adapter.initialize_parent_sandbox == [False]
    assert payload["code"] == "refinement_applied"
    assert current.current_refinement is not None
    assert current.generation == 1
    assert tuple(snapshot.values["execution_trace"]).count("topic_planning") == 1


@pytest.mark.asyncio
async def test_reflected_public_tool_continues_only_the_selected_terminal_pending_direction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RUI-006: textless public continuation consumes no caller-created direction."""

    envelope = _fixture_envelope(tmp_path)
    lifecycle = BundleLifecycle(workspace_host_path=envelope.workspace_host_path)
    bundle = await lifecycle.start(
        scope=(envelope.effective_user_id, envelope.outer_thread_id),
        request_text="Fixture terminal question.",
    )
    executor = _fixture_executor(tmp_path)
    await _stage_terminal_bundle(lifecycle=lifecycle, bundle=bundle, executor=executor)
    await lifecycle.admit_refinement(
        scope=(envelope.effective_user_id, envelope.outer_thread_id),
        bundle_id=bundle.bundle_id,
        text="Use the previously queued primary-source direction.",
        operation_key="stored-terminal-direction",
    )
    adapter = _FixtureRuntimeAdapter(envelope)

    from deerflow_deep_research import tool as public_tool

    factory_calls: list[None] = []

    def build_executor() -> BundleGraphExecutor:
        factory_calls.append(None)
        return executor

    monkeypatch.setattr(public_tool, "RuntimeAdapter", lambda: adapter)
    monkeypatch.setattr(public_tool, "BundleGraphExecutor", build_executor, raising=False)
    loaded = get_available_tools(
        groups=["deep-research-control"],
        include_mcp=False,
        app_config=_config_with_reflected_control_tool(),
    )
    control = next(tool for tool in loaded if tool.name == CONTROL_TOOL_NAME)

    result = await _invoke_reflected_control(
        control=control,
        envelope=envelope,
        call_id="terminal-continuation",
        args={"action": "refine", "bundle_id": bundle.bundle_id.value},
    )
    payload = json.loads(result["messages"][0].content)
    current = await lifecycle.read_state(bundle)

    assert factory_calls == [None]
    assert adapter.initialize_parent_sandbox == [False]
    assert payload["code"] == "refinement_applied"
    assert current.admitted_refinement is None
    assert current.current_refinement is not None
    assert current.current_refinement.operation_key == "stored-terminal-direction"


@pytest.mark.asyncio
async def test_reflected_public_tool_binds_the_trusted_graph_factory_for_start_and_resume(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RUI-006: ordinary public start/resume uses the graph owner, not fake lifecycle fallback."""

    envelope = _fixture_envelope(tmp_path)
    adapter = _FixtureRuntimeAdapter(envelope)
    from deerflow_deep_research import tool as public_tool

    factory_calls: list[None] = []

    def build_executor() -> BundleGraphExecutor:
        factory_calls.append(None)
        return _fixture_executor(tmp_path)

    monkeypatch.setattr(public_tool, "RuntimeAdapter", lambda: adapter)
    monkeypatch.setattr(public_tool, "BundleGraphExecutor", build_executor, raising=False)
    loaded = get_available_tools(
        groups=["deep-research-control"],
        include_mcp=False,
        app_config=_config_with_reflected_control_tool(),
    )
    control = next(tool for tool in loaded if tool.name == CONTROL_TOOL_NAME)
    start_message = HumanMessage(content="Research the fixture evidence.", id="start-message")

    started = await _invoke_reflected_control(
        control=control,
        envelope=envelope,
        call_id="start-lifecycle",
        args={"action": "start"},
        preceding_messages=(start_message,),
    )
    assert isinstance(started, list)
    assert len(started) == 1
    start_command = started[0]
    assert isinstance(start_command, Command)
    start_tool_message = start_command.update["messages"][0]
    start_payload = json.loads(start_tool_message.content)
    request_id = start_tool_message.artifact["human_input"]["request_id"]
    assert start_payload["code"] == "suspended"

    answer = HumanMessage(
        content="Use primary sources.",
        id="correlated-answer",
        additional_kwargs={
            "human_input_response": {
                "version": 1,
                "kind": "human_input_response",
                "source": "deep_research",
                "request_id": request_id,
                "response_kind": "text",
                "value": "Use primary sources.",
            }
        },
    )
    resumed = await _invoke_reflected_control(
        control=control,
        envelope=envelope,
        call_id="resume-lifecycle",
        args={"action": "resume", "bundle_id": start_payload["bundle_id"]},
        preceding_messages=(start_message, answer),
    )
    resume_payload = json.loads(resumed["messages"][0].content)

    assert factory_calls == [None, None]
    assert adapter.initialize_parent_sandbox == [True, True]
    assert resume_payload["action"] == "resume"
    assert resume_payload["status"] == "completed"


@pytest.mark.asyncio
async def test_reflected_active_pending_refinement_does_not_construct_graph_dependencies(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """RUI-006: public admission remains lifecycle-only until its terminal safe point."""

    envelope = _fixture_envelope(tmp_path)
    lifecycle = BundleLifecycle(workspace_host_path=envelope.workspace_host_path)
    bundle = await lifecycle.start(
        scope=(envelope.effective_user_id, envelope.outer_thread_id),
        request_text="Fixture active question.",
    )
    adapter = _FixtureRuntimeAdapter(envelope)

    from deerflow_deep_research import tool as public_tool

    def graph_must_not_construct() -> BundleGraphExecutor:
        raise AssertionError("active pending refinement must not construct a graph executor")

    monkeypatch.setattr(public_tool, "RuntimeAdapter", lambda: adapter)
    monkeypatch.setattr(public_tool, "BundleGraphExecutor", graph_must_not_construct, raising=False)
    loaded = get_available_tools(
        groups=["deep-research-control"],
        include_mcp=False,
        app_config=_config_with_reflected_control_tool(),
    )
    control = next(tool for tool in loaded if tool.name == CONTROL_TOOL_NAME)
    state = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": CONTROL_TOOL_NAME,
                        "args": {
                            "action": "refine",
                            "bundle_id": bundle.bundle_id.value,
                            "refinement": "Keep the current direction narrow.",
                        },
                        "id": "active-refinement",
                    }
                ],
            )
        ]
    }

    result = await ToolNode([control]).ainvoke(
        state,
        config={
            "configurable": {
                "__pregel_runtime": Runtime(
                    context={
                        "user_id": envelope.effective_user_id,
                        "thread_id": envelope.outer_thread_id,
                        "run_id": envelope.outer_run_id,
                    }
                )
            }
        },
    )

    payload = json.loads(result["messages"][0].content)
    pending = await lifecycle.read_state(bundle)
    status_result = await _invoke_reflected_control(
        control=control,
        envelope=envelope,
        call_id="active-status",
        args={"action": "status", "bundle_id": bundle.bundle_id.value},
    )
    cancel_result = await _invoke_reflected_control(
        control=control,
        envelope=envelope,
        call_id="active-cancel",
        args={"action": "cancel", "bundle_id": bundle.bundle_id.value},
    )
    status_payload = json.loads(status_result["messages"][0].content)
    cancel_payload = json.loads(cancel_result["messages"][0].content)
    current = await lifecycle.read_state(bundle)

    assert adapter.initialize_parent_sandbox == [False, False, False]
    assert payload["code"] == "refinement_pending"
    assert pending.admitted_refinement is not None
    assert pending.current_refinement is None
    assert status_payload["action"] == "status"
    assert cancel_payload["code"] == "cancelled"
    assert current.admitted_refinement is not None


@pytest.mark.asyncio
async def test_reflected_async_tool_receives_runtime_context_and_state() -> None:
    """DeerFlow reflection plus ToolNode must preserve both authority channels."""
    loaded = get_available_tools(
        groups=["deep-research-viability"],
        include_mcp=False,
        app_config=_config_with_reflected_probe(),
    )
    probe = next(tool for tool in loaded if tool.name == TOOL_NAME)
    assert isinstance(probe, BaseTool)
    assert probe.coroutine is not None

    outer_runtime = Runtime(
        context={
            "user_id": "viability-user",
            "thread_id": "viability-thread",
            "run_id": "viability-run",
        }
    )
    config = {"configurable": {"__pregel_runtime": outer_runtime}}
    state = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[{"name": TOOL_NAME, "args": {"payload": "ping"}, "id": "probe-call"}],
            )
        ],
        "state_sentinel": "state-reached-tool",
    }

    result = await ToolNode([probe]).ainvoke(state, config=config)
    payload = json.loads(result["messages"][0].content)

    assert payload == {
        "context_sentinel": "viability-user",
        "payload": "ping",
        "state_sentinel": "state-reached-tool",
        "tool_call_id": "probe-call",
    }


@pytest.mark.asyncio
async def test_reflected_async_tool_preserves_outer_command_and_human_input_artifact() -> None:
    loaded = get_available_tools(
        groups=["deep-research-viability"],
        include_mcp=False,
        app_config=_config_with_reflected_command_probe(),
    )
    probe = next(tool for tool in loaded if tool.name == COMMAND_TOOL_NAME)
    state = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[{"name": COMMAND_TOOL_NAME, "args": {"payload": "ping"}, "id": "command-call"}],
            )
        ]
    }
    runtime = Runtime(context={"user_id": "viability-user", "thread_id": "viability-thread"})
    result = await ToolNode([probe]).ainvoke(state, config={"configurable": {"__pregel_runtime": runtime}})

    assert isinstance(result, list)
    assert len(result) == 1
    command = result[0]
    assert isinstance(command, Command)
    assert command.goto == END
    message = command.update["messages"][0]
    assert message.tool_call_id == "command-call"
    assert message.name == COMMAND_TOOL_NAME
    assert message.id == "viability-human-input"
    assert message.artifact["human_input"] == {
        "version": 1,
        "kind": "human_input_request",
        "source": "deep_research",
        "request_id": "viability-human-input",
        "mode": "text",
        "title": "implementation_mode=fixture viability",
        "context": "implementation_mode=fixture viability test composition",
    }
