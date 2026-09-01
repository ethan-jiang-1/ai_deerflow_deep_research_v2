"""Bridge capture-seam: snapshot is durable before the first provider call.

@impl LDO-005
@impl LDO-006
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

import deerflow_deep_research.runtime.node_agent_bridge as bridge_module
from deerflow_deep_research.domain.node_context import (
    NodeContextActivityFacts,
    NodeContextSnapshot,
)
from deerflow_deep_research.runtime.node_agent_bridge import RuntimeNodeAgentBridge
from tests.fixtures.fake_models import ScriptedChatModel


def _load_bridge_test_helpers():
    spec = importlib.util.spec_from_file_location(
        "bridge_test_helpers",
        Path(__file__).resolve().parent / "test_node_agent_bridge.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


helpers = _load_bridge_test_helpers()


class _StubRecorder:
    """Captures the call order and the snapshot candidate itself."""

    def __init__(self, *, fail: bool = False) -> None:
        self.events: list[tuple[str, object]] = []
        self.fail = fail

    async def record(self, snapshot: NodeContextSnapshot) -> str:
        if self.fail:
            raise RuntimeError("store unavailable")
        self.events.append(("snapshot", snapshot))
        return f"{snapshot.attempt_id}/0001"

    async def record_activity(self, context_key: str, facts: NodeContextActivityFacts) -> None:
        self.events.append(("activity", facts))


def _bridge_with_recorder(recorder: _StubRecorder, monkeypatch: pytest.MonkeyPatch):
    order: list[str] = []

    class _SpyAgent:
        async def ainvoke(self, _state, *, context=None):  # noqa: ANN001
            order.append("provider_call")
            from deerflow_deep_research.domain.enums import NodeFinishReason

            return SimpleNamespace(
                finish_reason=NodeFinishReason.SUCCESS,
                summary="done",
                structured_output=None,
                messages=[],
            )

    monkeypatch.setattr(bridge_module, "build_node_agent", lambda **_kwargs: _SpyAgent())

    def spy_wrapper(**kwargs):
        recorder_agent = kwargs.get("model")
        _ = recorder_agent

        class _Guard:
            def __getattr__(self, item):  # model used only inside ainvoke
                raise AttributeError(item)

        return _SpyAgent()

    bridge = RuntimeNodeAgentBridge(
        envelope=helpers._envelope(),
        policy=helpers._policy(),
        model_resolver=lambda _e: ScriptedChatModel(responses=[]),
        tools_resolver=lambda _e, _p: [],
        node_context_recorder=recorder,
    )

    original_record = recorder.record

    async def ordered_record(snapshot):
        order.append("snapshot")
        return await original_record(snapshot)

    recorder.record = ordered_record  # type: ignore[method-assign]
    return bridge, order


def test_node_context_capture_defaults_to_none(monkeypatch: pytest.MonkeyPatch) -> None:
    bridge = RuntimeNodeAgentBridge(
        envelope=helpers._envelope(),
        policy=helpers._policy(),
        model_resolver=lambda _e: ScriptedChatModel(responses=[]),
    )
    assert bridge.node_context_recorder is None


@pytest.mark.asyncio
async def test_snapshot_is_durable_before_the_first_provider_call(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    recorder = _StubRecorder()
    bridge, order = _bridge_with_recorder(recorder, monkeypatch)
    store = __import__(
        "deerflow_deep_research.runtime.node_context_store", fromlist=["NodeContextStore"]
    ).NodeContextStore(bundle_root=tmp_path, bundle_id="b_" + "A" * 43)
    recorder.store = store

    async def record_via_store(snapshot):
        order.append("snapshot")
        key = store.record_sync(snapshot)
        return key

    recorder.record = record_via_store  # type: ignore[method-assign]

    from deerflow_deep_research.domain.enums import NodeFinishReason

    result = await bridge.run_agent(context=helpers._context(), request=helpers._request())
    assert result.finish_reason is NodeFinishReason.SUCCESS
    assert order[:2] == ["snapshot", "provider_call"]

    view = store.read(order and f"{helpers._context().attempt_id}/0001")
    assert view is not None
    assert view.snapshot.initial_system_policy
    assert view.snapshot.initial_human_message.startswith("Objective:")
    assert view.provenance["tool_posture"] == "RUNTIME_ENFORCED"


@pytest.mark.asyncio
async def test_capture_failure_means_zero_provider_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = _StubRecorder(fail=True)
    bridge, order = _bridge_with_recorder(recorder, monkeypatch)

    from deerflow_deep_research.domain.enums import NodeFinishReason

    result = await bridge.run_agent(context=helpers._context(), request=helpers._request())

    assert result.finish_reason is NodeFinishReason.FAILED
    assert result.error_code == "node_context_capture_failed"
    assert "provider_call" not in order  # zero provider calls before capture succeeded
