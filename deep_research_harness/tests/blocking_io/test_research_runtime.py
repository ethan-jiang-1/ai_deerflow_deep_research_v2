"""Event-loop blocking guard for an explicitly composed fixture lifecycle."""

from __future__ import annotations

import json
import secrets
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

from blockbuster import blockbuster_ctx
from deerflow_deep_research_fixtures import build_fixture_recipe
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Command

from deerflow_deep_research.domain.bundle import BundleId
from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore
from deerflow_deep_research.tool import run_deep_research


class Adapter:
    def __init__(self, envelope: TrustedRuntimeEnvelope) -> None:
        self.envelope = envelope

    async def adapt(self, _runtime, *, initialize_parent_sandbox: bool = True):
        return self.envelope


def _runtime(messages, call_id: str, *, context: dict[str, object] | None = None):
    return SimpleNamespace(state={"messages": list(messages)}, context=context or {}, tool_call_id=call_id)


def _call(action: str, call_id: str, bundle_id: str | None = None) -> AIMessage:
    args = {"action": action}
    if bundle_id is not None:
        args["bundle_id"] = bundle_id
    return AIMessage(content="", tool_calls=[{"name": "deep_research", "args": args, "id": call_id}])


def _payload(command: Command):
    message = command.update["messages"][0]
    return message, message.artifact["human_input"]


async def test_fixture_lifecycle_does_not_block_event_loop(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    uploads = tmp_path / "uploads"
    outputs = tmp_path / "outputs"
    for path in (workspace, uploads, outputs):
        path.mkdir()
    app_config = SimpleNamespace(
        models=[],
        tools=[],
        checkpointer=None,
        database=None,
    )
    envelope = TrustedRuntimeEnvelope(
        effective_user_id="alice",
        outer_thread_id="thread-blocking-io",
        outer_run_id="run-1",
        app_config=app_config,
        workspace_host_path=workspace,
        uploads_host_path=uploads,
        outputs_host_path=outputs,
        workspace_virtual_root="/mnt/user-data/workspace",
        uploads_virtual_root="/mnt/user-data/uploads",
        outputs_virtual_root="/mnt/user-data/outputs",
        parent_sandbox=object(),
    )
    adapter = Adapter(envelope)

    async def create(_envelope, *, bundle, **_kwargs):
        return WorkUnitStore(
            workspace_host_path=workspace,
            bundle=bundle,
            clock=lambda: datetime(2026, 7, 14, tzinfo=UTC),
            monotonic=time.monotonic,
            lock_sleep=time.sleep,
            token_factory=lambda: secrets.token_hex(16),
            fault_hook=None,
        )

    executor = BundleGraphExecutor(recipe=build_fixture_recipe(work_unit_store_factory=create))
    start_user = HumanMessage(content="research question", id="human-start")

    with blockbuster_ctx(["deerflow_deep_research"]):
        started = await run_deep_research(
            action="start",
            probe_id=None,
            runtime=_runtime([start_user, _call("start", "call-start")], "call-start"),
            adapter=adapter,
            bundle_graph_executor=executor,
        )
        assert isinstance(started, Command)
        start_message, hitl1 = _payload(started)
        bundle_id = json.loads(start_message.content)["bundle_id"]

        response1 = HumanMessage(
            content="profile answer",
            id="human-1",
            additional_kwargs={
                "human_input_response": {
                    "version": 1,
                    "kind": "human_input_response",
                    "source": "deep_research",
                    "request_id": hitl1["request_id"],
                    "response_kind": "text",
                    "value": "profile answer",
                }
            },
        )
        resumed = await run_deep_research(
            action="resume",
            probe_id=None,
            bundle_id=bundle_id,
            runtime=_runtime([start_user, response1, _call("resume", "call-resume-1", bundle_id)], "call-resume-1"),
            adapter=adapter,
            bundle_graph_executor=executor,
        )
        assert not isinstance(resumed, Command)
        completed = resumed

    assert completed["code"] == "completed"
    assert completed["implementation_mode"] == "fixture"


async def test_composed_start_persists_policy_once_in_the_selected_bundle_checkpoint(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    uploads = tmp_path / "uploads"
    outputs = tmp_path / "outputs"
    for path in (workspace, uploads, outputs):
        path.mkdir()
    envelope = TrustedRuntimeEnvelope(
        effective_user_id="alice",
        outer_thread_id="thread-policy",
        outer_run_id="run-policy",
        app_config=SimpleNamespace(models=(), tools=(), checkpointer=None, database=None),
        workspace_host_path=workspace,
        uploads_host_path=uploads,
        outputs_host_path=outputs,
        workspace_virtual_root="/mnt/user-data/workspace",
        uploads_virtual_root="/mnt/user-data/uploads",
        outputs_virtual_root="/mnt/user-data/outputs",
        parent_sandbox=object(),
    )
    adapter = Adapter(envelope)

    async def create(_envelope, *, bundle, **_kwargs):
        return WorkUnitStore(
            workspace_host_path=workspace,
            bundle=bundle,
            clock=lambda: datetime(2026, 7, 14, tzinfo=UTC),
            monotonic=time.monotonic,
            lock_sleep=time.sleep,
            token_factory=lambda: secrets.token_hex(16),
            fault_hook=None,
        )

    executor = BundleGraphExecutor(recipe=build_fixture_recipe(work_unit_store_factory=create))
    start_user = HumanMessage(content="Research storage options", id="human-policy-start")
    admitted_policy = {"auto_profile": True, "auto_proceed": True}

    with blockbuster_ctx(["deerflow_deep_research"]):
        started = await run_deep_research(
            action="start",
            probe_id=None,
            runtime=_runtime(
                [start_user, _call("start", "call-policy-start")],
                "call-policy-start",
                context={"non_interactive": True, "non_interactive_policy": admitted_policy},
            ),
            adapter=adapter,
            bundle_graph_executor=executor,
        )
        assert isinstance(started, Command)
        start_message, hitl1 = _payload(started)
        bundle_id = json.loads(start_message.content)["bundle_id"]
        lifecycle = BundleLifecycle(workspace_host_path=workspace)
        bundle = await lifecycle.resolve(
            scope=(envelope.effective_user_id, envelope.outer_thread_id),
            bundle_id=BundleId(bundle_id),
        )
        assert bundle is not None

        async with lifecycle.open_graph_checkpoint(bundle) as saver:
            graph = executor._recipe.builder.compile(checkpointer=saver)
            initial_snapshot = await graph.aget_state(executor._config(bundle))
        assert initial_snapshot is not None
        assert initial_snapshot.values["non_interactive_policy"] == admitted_policy

        response = HumanMessage(
            content="profile answer",
            id="human-policy-answer",
            additional_kwargs={
                "human_input_response": {
                    "version": 1,
                    "kind": "human_input_response",
                    "source": "deep_research",
                    "request_id": hitl1["request_id"],
                    "response_kind": "text",
                    "value": "profile answer",
                }
            },
        )
        await run_deep_research(
            action="resume",
            probe_id=None,
            bundle_id=bundle_id,
            runtime=_runtime(
                [start_user, response, _call("resume", "call-policy-resume", bundle_id)],
                "call-policy-resume",
                context={"non_interactive_policy": {"auto_profile": False, "auto_proceed": False}},
            ),
            adapter=adapter,
            bundle_graph_executor=executor,
        )

        async with lifecycle.open_graph_checkpoint(bundle) as saver:
            graph = executor._recipe.builder.compile(checkpointer=saver)
            resumed_snapshot = await graph.aget_state(executor._config(bundle))
        assert resumed_snapshot is not None
        assert resumed_snapshot.values["non_interactive_policy"] == admitted_policy


async def test_noninteractive_policy_does_not_compose_graph_work_without_an_executor(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    uploads = tmp_path / "uploads"
    outputs = tmp_path / "outputs"
    for path in (workspace, uploads, outputs):
        path.mkdir()
    envelope = TrustedRuntimeEnvelope(
        effective_user_id="alice",
        outer_thread_id="thread-fallback",
        outer_run_id="run-fallback",
        app_config=SimpleNamespace(models=(), tools=(), checkpointer=None, database=None),
        workspace_host_path=workspace,
        uploads_host_path=uploads,
        outputs_host_path=outputs,
        workspace_virtual_root="/mnt/user-data/workspace",
        uploads_virtual_root="/mnt/user-data/uploads",
        outputs_virtual_root="/mnt/user-data/outputs",
        parent_sandbox=object(),
    )

    started = await run_deep_research(
        action="start",
        probe_id=None,
        runtime=_runtime(
            [HumanMessage(content="Research storage options", id="human-fallback"), _call("start", "call-fallback")],
            "call-fallback",
            context={
                "non_interactive": True,
                "non_interactive_policy": {"auto_profile": True, "auto_proceed": True},
            },
        ),
        adapter=Adapter(envelope),
    )

    assert isinstance(started, dict)
    assert started["availability"] == "unavailable"
    assert started["code"] == "unavailable"
    assert not list(workspace.rglob("graph.sqlite"))
    assert not list(workspace.rglob("state.json"))
