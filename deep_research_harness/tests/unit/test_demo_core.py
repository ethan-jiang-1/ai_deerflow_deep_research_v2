"""Unit tests for shared demo core module.

@impl DPL-001
@impl DPL-002
@impl DPL-003
@impl DPL-004
@impl DPL-005
@impl DPL-009
@impl DPL-010
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import types
from dataclasses import replace
from unittest.mock import patch

import httpx
import pytest

from deerflow_deep_research.agents.policies import ExecutionBudget, ExecutionPolicy
from deerflow_deep_research.graph.topology import LOGICAL_NODES
from deerflow_deep_research.runtime.node_agent_bridge import NodeAgentConfigurationError


@pytest.fixture
def _scripts_path():
    """Ensure _demo_core is importable."""
    import sys

    scripts = str(__import__("pathlib").Path(__file__).resolve().parents[2] / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    return scripts


def test_phase_meta_covers_all_logical_nodes(_scripts_path):
    from _demo_core import PHASE_META

    for name in LOGICAL_NODES:
        assert name in PHASE_META, f"Missing PHASE_META entry for {name}"
        label, desc = PHASE_META[name]
        assert isinstance(label, str) and label, f"Empty label for {name}"
        assert isinstance(desc, str) and desc, f"Empty description for {name}"


def test_phase_meta_covers_all_run_trace_entries(_scripts_path):
    from typing import get_args

    from _demo_core import PHASE_META

    from deerflow_deep_research.domain.run_experience import RunTraceEntry

    trace_entries: list[str] = []
    for member in get_args(RunTraceEntry):
        trace_entries.extend(get_args(member))
    assert trace_entries, "RunTraceEntry union unexpectedly empty"
    for entry in trace_entries:
        assert entry in PHASE_META, f"Missing PHASE_META entry for trace step {entry}"
        label, desc = PHASE_META[entry]
        assert isinstance(label, str) and label, f"Empty label for {entry}"
        assert isinstance(desc, str) and desc, f"Empty description for {entry}"


def test_build_fixture_demo_recipe(_scripts_path):
    from _demo_core import build_fixture_demo_recipe

    async def _fake_store_factory(_env, *, bundle):
        pass

    recipe = build_fixture_demo_recipe(work_unit_store_factory=_fake_store_factory)
    assert recipe.implementation_mode.value == "fixture"
    assert recipe.requires_node_agent_bridge is False
    assert recipe.requires_bootstrap_bundle is False
    assert recipe.requires_work_units is True


def test_build_real_demo_recipe(_scripts_path):
    from _demo_core import build_demo_node_agent_bridge, build_real_demo_recipe

    async def _fake_store_factory(_env, *, bundle):
        pass

    recipe = build_real_demo_recipe(work_unit_store_factory=_fake_store_factory)
    assert recipe.requires_node_agent_bridge is True
    assert recipe.requires_bootstrap_bundle is True
    assert recipe.requires_work_units is True
    assert recipe.node_agent_bridge_factory is build_demo_node_agent_bridge


def test_demo_recipe_factories_do_not_expose_a_mode_selector(_scripts_path):
    import _demo_core

    assert not hasattr(_demo_core, "build_demo_recipe")


def test_check_credentials_available_true(_scripts_path):
    from _demo_core import check_credentials_available

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
        assert check_credentials_available() is True


def test_check_credentials_available_false(_scripts_path):
    from _demo_core import check_credentials_available

    with patch.dict(os.environ, {}, clear=True):
        # Temporarily remove ANTHROPIC_API_KEY if set
        original = os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            assert check_credentials_available() is False
        finally:
            if original is not None:
                os.environ["ANTHROPIC_API_KEY"] = original


def test_real_demo_prerequisites_reject_missing_and_blank_values(_scripts_path):
    """@impl DPL-001
    @impl DPL-004
    """
    from _demo_core import DemoPrerequisiteError, validate_real_demo_prerequisites

    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(DemoPrerequisiteError) as missing:
            validate_real_demo_prerequisites()
        assert missing.value.model_missing is True
        assert missing.value.web_tool_missing is True
        assert "API_KEY" not in str(missing.value)

    with patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "   ", "TAVILY_API_KEY": "\t"},
        clear=True,
    ):
        with pytest.raises(DemoPrerequisiteError) as blank:
            validate_real_demo_prerequisites()
        assert blank.value.model_missing is True
        assert blank.value.web_tool_missing is True


def test_demo_readiness_report_is_safe_and_non_network(_scripts_path):
    from _demo_core import demo_readiness_report

    fake = demo_readiness_report(mode="fake", environ={})
    assert fake.ready is True
    assert fake.mode == "fake"

    real = demo_readiness_report(mode="real", environ={})
    assert real.ready is False
    assert real.failure is not None
    assert "API_KEY" not in str(real.model_dump(mode="json"))
    assert real.failure.observation_record_created is False


def test_demo_model_selector_restricts_to_configured_models(_scripts_path):
    from _demo_core import _resolve_demo_models

    environ = {
        "DEEPSEEK_API_KEY": "test-key",
        "DEERFLOW_DEMO_MODEL": "deepseek-v4-flash",
    }
    selected = _resolve_demo_models(environ)
    assert [model.name for model in selected] == ["deepseek-v4-flash"]

    unavailable = _resolve_demo_models({**environ, "DEERFLOW_DEMO_MODEL": "unavailable-model"})
    assert unavailable == []


@pytest.mark.asyncio
async def test_demo_adapter_close_is_idempotent(_scripts_path, tmp_path):
    """@impl DPL-001"""
    from _demo_core import DemoAdapter

    adapter = DemoAdapter(retained_root=tmp_path / ".deep-research-demo-runs")
    await adapter.aclose()
    await adapter.aclose()
    assert adapter._closed is True


def test_runtime_with_default_context(_scripts_path):
    from _demo_core import _runtime

    rt = _runtime([], "call-1")
    assert rt.tool_call_id == "call-1"
    assert rt.context == {}
    assert rt.state["messages"] == []


def test_runtime_with_custom_context(_scripts_path):
    from _demo_core import _runtime

    ctx = {"non_interactive_policy": {"auto_profile": True, "auto_proceed": True}}
    rt = _runtime([], "call-2", context=ctx)
    assert rt.context == ctx
    assert rt.tool_call_id == "call-2"


def test_tool_call_basic(_scripts_path):
    from _demo_core import _tool_call
    from langchain_core.messages import AIMessage

    msg = _tool_call("start", "call-start")
    assert isinstance(msg, AIMessage)
    assert len(msg.tool_calls) == 1
    assert msg.tool_calls[0]["name"] == "deep_research"
    assert msg.tool_calls[0]["args"]["action"] == "start"


def test_tool_call_with_bundle_id(_scripts_path):
    from _demo_core import _tool_call

    bundle_id = "b_" + "A" * 43
    msg = _tool_call("resume", "call-resume", bundle_id=bundle_id)
    assert msg.tool_calls[0]["args"]["bundle_id"] == bundle_id
    assert msg.tool_calls[0]["args"]["action"] == "resume"


class _DemoRuntimeAdapter:
    async def create_work_unit_store(self, _envelope, *, bundle):
        return None


def test_build_demo_runtime_selects_fixed_recipe_and_executor(_scripts_path):
    from _demo_core import build_demo_runtime

    adapter = _DemoRuntimeAdapter()
    real = build_demo_runtime(mode="real", adapter=adapter)
    fixture = build_demo_runtime(mode="fixture_graph", adapter=adapter)

    assert real.adapter is adapter
    assert real.recipe.implementation_mode.value == "all_real"
    assert real.executor._recipe is real.recipe
    assert fixture.adapter is adapter
    assert fixture.recipe.implementation_mode.value == "fixture"
    assert fixture.executor._recipe is fixture.recipe


@pytest.mark.asyncio
async def test_demo_lifecycle_transport_forwards_only_the_runtime_owned_executor(_scripts_path, monkeypatch):
    import _demo_core

    captured: dict[str, object] = {}
    raw_result = object()

    async def dispatch(**kwargs):
        captured.update(kwargs)
        return raw_result

    monkeypatch.setattr(_demo_core, "run_deep_research", dispatch)
    runtime = _demo_core.build_demo_runtime(mode="real", adapter=_DemoRuntimeAdapter())
    transport = _demo_core.DemoLifecycleTransport()
    transport.bind(runtime=runtime)
    result = await transport.dispatch(
        action="start",
        bundle_id=None,
        messages=(),
        context={"non_interactive_policy": {"auto_profile": True, "auto_proceed": True}},
    )

    assert result is raw_result
    assert captured["action"] == "start"
    assert captured["adapter"] is runtime.adapter
    assert captured["bundle_graph_executor"] is runtime.executor
    assert "host_factory" not in captured
    assert captured["runtime"].tool_call_id.startswith("demo-lifecycle-start-")


@pytest.mark.asyncio
async def test_demo_lifecycle_transport_rejects_missing_executor_before_dispatch(_scripts_path, monkeypatch):
    import _demo_core

    dispatched = False

    async def dispatch(**_kwargs):
        nonlocal dispatched
        dispatched = True
        return object()

    monkeypatch.setattr(_demo_core, "run_deep_research", dispatch)
    runtime = _demo_core.build_demo_runtime(mode="real", adapter=_DemoRuntimeAdapter())
    transport = _demo_core.DemoLifecycleTransport()

    with pytest.raises(RuntimeError, match="demo_graph_executor_required"):
        transport.bind(runtime=replace(runtime, executor=None))

    assert dispatched is False


def test_real_recipe_selects_all_real_adapters(_scripts_path):
    from _demo_core import build_real_demo_recipe

    async def store_factory(_envelope, *, bundle, **_kwargs):
        return None

    recipe = build_real_demo_recipe(work_unit_store_factory=store_factory)
    assert recipe.implementation_mode.value == "all_real"
    assert tuple(name for name, _kind in recipe.adapter_kinds) == LOGICAL_NODES
    assert all(kind.value == "real" for _name, kind in recipe.adapter_kinds)


async def test_demo_adapter_provides_legal_unique_sandbox(_scripts_path, tmp_path):
    from _demo_core import DemoAdapter

    first = DemoAdapter(retained_root=tmp_path / "first")
    second = DemoAdapter(retained_root=tmp_path / "second")
    try:
        first_envelope = await first.adapt(object())
        second_envelope = await second.adapt(object())
        assert first_envelope.parent_sandbox is not None
        assert getattr(first_envelope.parent_sandbox, "id", None)
        assert len(first_envelope.parent_sandbox.path_mappings) == 3
        assert first_envelope.workspace_host_path.is_dir()
        assert first_envelope.outer_thread_id != second_envelope.outer_thread_id
        assert first_envelope.outer_run_id != second_envelope.outer_run_id
    finally:
        await first.aclose()
        await second.aclose()


@pytest.mark.asyncio
async def test_demo_adapter_accepts_only_a_runtime_bound_bundle_for_work_unit_storage(_scripts_path, tmp_path):
    from _demo_core import DemoAdapter

    from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef

    adapter = DemoAdapter(retained_root=tmp_path / ".deep-research-demo-runs")
    bundle = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)
    try:
        store = await adapter.create_work_unit_store(object(), bundle=bundle)
        assert store.bundle == bundle
    finally:
        await adapter.aclose()


def _policy(*tool_names: str) -> ExecutionPolicy:
    return ExecutionPolicy(
        policy_name="demo-test",
        allowed_tool_names=frozenset(tool_names),
        read_roots=("/workspace",),
        write_roots=(),
        attempt_root="/workspace",
        budget=ExecutionBudget(
            max_model_calls=1,
            max_total_tool_calls=1,
            max_tool_calls_per_response=1,
            max_parallel_tool_calls=1,
            total_token_budget=128,
            per_call_output_token_cap=128,
            per_tool_result_bytes=4_096,
            structured_result_bytes=4_096,
            wall_time_seconds=1.0,
        ),
    )


class _FakeAsyncTavilyClient:
    instances: list[_FakeAsyncTavilyClient] = []
    search_outcomes: list[object] = []
    extract_outcomes: list[object] = []

    def __init__(self, *, api_key: str) -> None:
        self.api_key = api_key
        self.closed = False
        self.search_calls: list[tuple[str, dict[str, object]]] = []
        self.extract_calls: list[list[str]] = []
        self.extract_kwargs: list[dict[str, object]] = []
        type(self).instances.append(self)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args) -> None:
        self.closed = True

    async def search(self, query: str, **kwargs):
        self.search_calls.append((query, kwargs))
        outcome = type(self).search_outcomes.pop(0) if type(self).search_outcomes else None
        if isinstance(outcome, BaseException):
            raise outcome
        if outcome is not None:
            return outcome
        return {
            "results": [
                {"title": f"result-{index}", "url": f"https://example.test/{index}", "content": "snippet"}
                for index in range(6)
            ]
        }

    async def extract(self, urls: list[str], **kwargs):
        self.extract_calls.append(urls)
        self.extract_kwargs.append(kwargs)
        outcome = type(self).extract_outcomes.pop(0) if type(self).extract_outcomes else None
        if isinstance(outcome, BaseException):
            raise outcome
        if outcome is not None:
            return outcome
        return {"results": [{"url": urls[0], "raw_content": "extracted source"}]}


@pytest.fixture
def _stub_tavily(monkeypatch):
    _FakeAsyncTavilyClient.instances.clear()
    _FakeAsyncTavilyClient.search_outcomes.clear()
    _FakeAsyncTavilyClient.extract_outcomes.clear()
    module = types.ModuleType("tavily")
    module.AsyncTavilyClient = _FakeAsyncTavilyClient
    monkeypatch.setitem(sys.modules, "tavily", module)
    return _FakeAsyncTavilyClient


def _demo_tools(_scripts_path, monkeypatch, policy: ExecutionPolicy):
    from _demo_core import build_demo_node_agent_bridge

    monkeypatch.setenv("TAVILY_API_KEY", "sentinel-tavily-key")
    bridge = build_demo_node_agent_bridge(envelope=object(), policy=policy)
    return {tool.name: tool for tool in bridge.tools_resolver(object(), policy)}


def _http_status_error(status: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://tavily.test/read")
    return httpx.HTTPStatusError(
        f"status {status}",
        request=request,
        response=httpx.Response(status, request=request),
    )


def _tavily_error(name: str) -> Exception:
    return type(name, (Exception,), {"__module__": "tavily.errors"})(name)


def test_demo_tavily_retry_classification_is_limited_to_transient_read_failures(_scripts_path):
    """@impl DPL-009"""
    from _demo_core import _is_retryable_tavily_read_failure

    server_failure = _http_status_error(503)
    client_failure = _http_status_error(400)
    out_of_range_failure = _http_status_error(600)
    tavily_timeout = _tavily_error("TimeoutError")
    tavily_rate_limit = _tavily_error("UsageLimitExceededError")

    assert _is_retryable_tavily_read_failure(server_failure)
    assert not _is_retryable_tavily_read_failure(client_failure)
    assert not _is_retryable_tavily_read_failure(out_of_range_failure)
    assert _is_retryable_tavily_read_failure(tavily_timeout)
    assert _is_retryable_tavily_read_failure(tavily_rate_limit)
    assert not _is_retryable_tavily_read_failure(ValueError("invalid input"))


@pytest.mark.asyncio
async def test_demo_tavily_tools_are_local_bounded_and_closed(_scripts_path, monkeypatch, _stub_tavily):
    """@impl DPL-001"""
    tools = _demo_tools(_scripts_path, monkeypatch, _policy("web_search", "web_fetch"))

    assert set(tools) == {"web_search", "web_fetch"}
    search_payload = json.loads(await tools["web_search"].ainvoke({"query": "demo query"}))

    assert len(search_payload["results"]) == 5
    assert search_payload["results"][0] == {
        "title": "result-0",
        "url": "https://example.test/0",
        "snippet": "snippet",
    }
    assert all(client.closed for client in _stub_tavily.instances)
    assert all(client.api_key == "sentinel-tavily-key" for client in _stub_tavily.instances)


@pytest.mark.asyncio
async def test_demo_tavily_fetch_requires_same_run_search(_scripts_path, monkeypatch, _stub_tavily):
    """@impl DPL-001
    @impl DPL-009
    """
    first_tools = _demo_tools(_scripts_path, monkeypatch, _policy("web_search", "web_fetch"))
    await first_tools["web_search"].ainvoke({"query": "demo query"})

    second_tools = _demo_tools(_scripts_path, monkeypatch, _policy("web_search", "web_fetch"))
    denied = json.loads(await second_tools["web_fetch"].ainvoke({"url": "https://example.test/0"}))
    assert denied == {"error": "fetch_url_not_approved"}
    assert not any(client.extract_calls for client in _stub_tavily.instances)

    fetched = json.loads(await first_tools["web_fetch"].ainvoke({"url": "https://example.test/0"}))
    assert fetched == {"content": "extracted source", "url": "https://example.test/0"}
    assert any(client.extract_calls for client in _stub_tavily.instances)
    assert all(client.closed for client in _stub_tavily.instances)


@pytest.mark.parametrize(
    "transient_factory",
    (
        lambda: httpx.ReadTimeout("transient", request=httpx.Request("GET", "https://tavily.test/search")),
        lambda: httpx.ConnectError("transient", request=httpx.Request("GET", "https://tavily.test/search")),
        lambda: httpx.RemoteProtocolError("transient"),
        lambda: _tavily_error("TimeoutError"),
        lambda: _tavily_error("UsageLimitExceededError"),
        lambda: _http_status_error(429),
        lambda: _http_status_error(500),
        lambda: _http_status_error(599),
    ),
    ids=("timeout", "network", "protocol", "tavily-timeout", "usage-limit", "http-429", "http-500", "http-599"),
)
@pytest.mark.asyncio
async def test_demo_tavily_search_retries_each_allowed_direct_failure_before_succeeding(
    _scripts_path,
    monkeypatch,
    _stub_tavily,
    transient_factory,
):
    """@impl DPL-009"""
    from _demo_core import _TAVILY_ATTEMPT_TIMEOUT_SECONDS

    delays: list[float] = []

    async def no_wait(delay: float) -> None:
        delays.append(delay)

    _stub_tavily.search_outcomes.extend(
        (
            transient_factory(),
            {"results": [{"title": "recovered", "url": "https://example.test/recovered", "content": "ok"}]},
        )
    )
    monkeypatch.setattr("_demo_core.asyncio.sleep", no_wait)
    tools = _demo_tools(_scripts_path, monkeypatch, _policy("web_search"))

    payload = json.loads(await tools["web_search"].ainvoke({"query": "demo query"}))

    assert payload == {"results": [{"snippet": "ok", "title": "recovered", "url": "https://example.test/recovered"}]}
    assert len(_stub_tavily.instances) == 2
    assert all(client.closed for client in _stub_tavily.instances)
    assert all(
        client.search_calls[0][1]["timeout"] == _TAVILY_ATTEMPT_TIMEOUT_SECONDS for client in _stub_tavily.instances
    )
    assert delays == [1.0]


@pytest.mark.asyncio
async def test_demo_tavily_fetch_exhausts_three_transient_read_attempts(
    _scripts_path,
    monkeypatch,
    _stub_tavily,
):
    """@impl DPL-009"""
    from _demo_core import _TAVILY_ATTEMPT_TIMEOUT_SECONDS

    delays: list[float] = []

    async def no_wait(delay: float) -> None:
        delays.append(delay)

    _stub_tavily.extract_outcomes.extend(
        httpx.ConnectError("transient", request=httpx.Request("GET", "https://tavily.test/extract")) for _ in range(3)
    )
    monkeypatch.setattr("_demo_core.asyncio.sleep", no_wait)
    tools = _demo_tools(_scripts_path, monkeypatch, _policy("web_search", "web_fetch"))
    await tools["web_search"].ainvoke({"query": "demo query"})

    payload = json.loads(await tools["web_fetch"].ainvoke({"url": "https://example.test/0"}))

    assert payload == {"error": "web_fetch_unavailable"}
    assert len(_stub_tavily.instances) == 4
    assert sum(len(client.extract_calls) for client in _stub_tavily.instances) == 3
    assert all(
        client.extract_kwargs[0]["timeout"] == _TAVILY_ATTEMPT_TIMEOUT_SECONDS for client in _stub_tavily.instances[1:]
    )
    assert delays == [1.0, 2.0]


@pytest.mark.asyncio
async def test_demo_tavily_search_exhausts_three_transient_read_attempts(
    _scripts_path,
    monkeypatch,
    _stub_tavily,
):
    """@impl DPL-009"""
    delays: list[float] = []

    async def no_wait(delay: float) -> None:
        delays.append(delay)

    _stub_tavily.search_outcomes.extend(
        httpx.ReadTimeout("transient", request=httpx.Request("GET", "https://tavily.test/search")) for _ in range(3)
    )
    monkeypatch.setattr("_demo_core.asyncio.sleep", no_wait)
    tools = _demo_tools(_scripts_path, monkeypatch, _policy("web_search"))

    payload = json.loads(await tools["web_search"].ainvoke({"query": "demo query"}))

    assert payload == {"error": "web_search_unavailable"}
    assert len(_stub_tavily.instances) == 3
    assert all(client.closed for client in _stub_tavily.instances)
    assert delays == [1.0, 2.0]


@pytest.mark.parametrize(
    "outcome_factory",
    (
        lambda: _http_status_error(401),
        lambda: ValueError("malformed query"),
        lambda: _http_status_error(400),
        lambda: _http_status_error(600),
        lambda: RuntimeError("unknown failure"),
    ),
    ids=("authentication", "malformed-input", "http-400", "http-600", "unknown"),
)
@pytest.mark.asyncio
async def test_demo_tavily_does_not_retry_non_transient_errors(
    _scripts_path,
    monkeypatch,
    _stub_tavily,
    outcome_factory,
):
    """@impl DPL-009"""

    async def no_wait(_delay: float) -> None:
        raise AssertionError("non-transient Tavily error must not back off")

    _stub_tavily.search_outcomes.append(outcome_factory())
    monkeypatch.setattr("_demo_core.asyncio.sleep", no_wait)
    tools = _demo_tools(_scripts_path, monkeypatch, _policy("web_search"))

    payload = json.loads(await tools["web_search"].ainvoke({"query": "demo query"}))

    assert payload == {"error": "web_search_unavailable"}
    assert len(_stub_tavily.instances) == 1


@pytest.mark.asyncio
async def test_demo_tavily_cancellation_is_not_converted_or_retried(_scripts_path, monkeypatch, _stub_tavily):
    """@impl DPL-009"""
    _stub_tavily.search_outcomes.append(asyncio.CancelledError())
    tools = _demo_tools(_scripts_path, monkeypatch, _policy("web_search"))

    with pytest.raises(asyncio.CancelledError):
        await tools["web_search"].ainvoke({"query": "demo query"})

    assert len(_stub_tavily.instances) == 1


@pytest.mark.asyncio
async def test_demo_tavily_cancellation_during_backoff_does_not_start_another_attempt(
    _scripts_path,
    monkeypatch,
    _stub_tavily,
):
    """@impl DPL-009"""
    delays: list[float] = []

    async def cancel_backoff(delay: float) -> None:
        delays.append(delay)
        raise asyncio.CancelledError()

    _stub_tavily.search_outcomes.extend(
        (
            httpx.ReadTimeout("transient", request=httpx.Request("GET", "https://tavily.test/search")),
            {"results": [{"title": "must not run", "url": "https://example.test/never", "content": "no"}]},
        )
    )
    monkeypatch.setattr("_demo_core.asyncio.sleep", cancel_backoff)
    tools = _demo_tools(_scripts_path, monkeypatch, _policy("web_search"))

    with pytest.raises(asyncio.CancelledError):
        await tools["web_search"].ainvoke({"query": "demo query"})

    assert delays == [1.0]
    assert len(_stub_tavily.instances) == 1


def test_demo_tavily_fetch_only_policy_fails_closed(_scripts_path, monkeypatch):
    """@impl DPL-001"""
    from _demo_core import build_demo_node_agent_bridge

    monkeypatch.setenv("TAVILY_API_KEY", "sentinel-tavily-key")
    policy = _policy("web_fetch")
    bridge = build_demo_node_agent_bridge(envelope=object(), policy=policy)

    with pytest.raises(NodeAgentConfigurationError, match="tools_unavailable"):
        bridge.tools_resolver(object(), policy)
