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

from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore
from deerflow_deep_research.tool import run_deep_research


class Adapter:
    def __init__(self, envelope: TrustedRuntimeEnvelope) -> None:
        self.envelope = envelope

    async def adapt(self, _runtime, *, initialize_parent_sandbox: bool = True):
        return self.envelope


def _runtime(messages, call_id: str):
    return SimpleNamespace(state={"messages": list(messages)}, context={}, tool_call_id=call_id)


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
        progress=None,
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
    assert completed["implementation_mode"] == "all_real"
