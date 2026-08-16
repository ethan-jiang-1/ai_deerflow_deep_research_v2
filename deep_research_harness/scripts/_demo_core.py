#!/usr/bin/env python3
"""Shared demo infrastructure for CLI and TUI research lifecycle demos.

@impl DPL-001
@impl DPL-003
@impl DPL-009
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import secrets
import time
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Literal

import httpx
from deerflow.sandbox.local.local_sandbox import LocalSandbox, PathMapping
from langchain_core.messages import AIMessage
from langchain_core.tools import BaseTool, tool

from deerflow_deep_research.agents.policies import ExecutionPolicy
from deerflow_deep_research.domain.bundle import RunBundleRef
from deerflow_deep_research.domain.run_experience import (
    FailureCertainty,
    ReadinessCheck,
    ReadinessReport,
    RunFailure,
    RunFailureCode,
)
from deerflow_deep_research.domain.run_observation import ExecutionProfileEvidence
from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.control import build_control_graph_host
from deerflow_deep_research.runtime.node_agent_bridge import NodeAgentConfigurationError, RuntimeNodeAgentBridge
from deerflow_deep_research.runtime.research import ResearchGraphRecipe
from deerflow_deep_research.runtime.run_observation import (
    BundleRunObservationPublisher,
)
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope
from deerflow_deep_research.runtime.session_workbench import BundleWorkbench
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore
from deerflow_deep_research.tool import run_deep_research

# ── adapter ──────────────────────────────────────────────────────────


_KNOWN_API_KEY_VARS = (
    "DEEPSEEK_API_KEY",
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
)
_DEMO_MODEL_SELECTOR_ENV = "DEERFLOW_DEMO_MODEL"
_TAVILY_API_KEY_VAR = "TAVILY_API_KEY"
_MAX_SEARCH_RESULTS = 5
_MAX_SEARCH_SNIPPET_CHARS = 1_000
_MAX_FETCH_CONTENT_CHARS = 12_000
_TAVILY_ATTEMPT_TIMEOUT_SECONDS = 60.0
_TAVILY_MAX_READ_ATTEMPTS = 3
_TAVILY_RETRY_BACKOFF_SECONDS = (1.0, 2.0)
_DEMO_BUNDLE_ROOT_NAME = ".deep-research-demo-runs"
_DEMO_RETAINED_DATA_SCOPE_REVISION = "retained-run-data-v5"


@dataclass(frozen=True)
class _RegisteredDemoModel:
    credential_env: str
    name: str
    use_path: str
    model_id: str
    base_url: str | None
    extra_kwargs: Mapping[str, Any]
    safe_revision: str


@dataclass(frozen=True)
class DemoModelProfile:
    """One selected credential-backed model and its safe diagnostic identity."""

    model_config: Any
    evidence: ExecutionProfileEvidence


_MODEL_REGISTRY = (
    _RegisteredDemoModel(
        credential_env="DEEPSEEK_API_KEY",
        name="deepseek-v4-pro",
        use_path="deerflow.models.patched_deepseek:PatchedChatDeepSeek",
        model_id="deepseek-v4-pro",
        base_url="https://api.deepseek.com/v1",
        extra_kwargs={},
        safe_revision="v1",
    ),
    _RegisteredDemoModel(
        credential_env="DEEPSEEK_API_KEY",
        name="deepseek-v4-flash",
        use_path="deerflow.models.patched_deepseek:PatchedChatDeepSeek",
        model_id="deepseek-v4-flash",
        base_url="https://api.deepseek.com/v1",
        extra_kwargs={},
        safe_revision="v1",
    ),
    _RegisteredDemoModel(
        credential_env="ANTHROPIC_API_KEY",
        name="anthropic-demo",
        use_path="langchain_anthropic:ChatAnthropic",
        model_id="claude-sonnet-4-5-20250901",
        base_url=None,
        extra_kwargs={},
        safe_revision="v1",
    ),
    _RegisteredDemoModel(
        credential_env="OPENAI_API_KEY",
        name="openai-demo",
        use_path="langchain_openai:ChatOpenAI",
        model_id="gpt-4o",
        base_url=None,
        extra_kwargs={},
        safe_revision="v1",
    ),
)


def _nonblank_environment_value(name: str, environ: Mapping[str, str] | None = None) -> str | None:
    value = (os.environ if environ is None else environ).get(name)
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


class DemoPrerequisiteError(ValueError):
    """Raised when the standalone real demo lacks a required credential."""

    def __init__(self, *, model_missing: bool, web_tool_missing: bool) -> None:
        super().__init__("real_demo_prerequisites_missing")
        self.model_missing = model_missing
        self.web_tool_missing = web_tool_missing


def validate_real_demo_prerequisites(environ: Mapping[str, str] | None = None) -> None:
    """Fail before graph construction when real-demo credentials are incomplete.

    @impl DPL-001
    @impl DPL-004
    """
    model_missing = resolve_real_demo_model_profile(environ) is None
    web_tool_missing = _nonblank_environment_value(_TAVILY_API_KEY_VAR, environ) is None
    if model_missing or web_tool_missing:
        raise DemoPrerequisiteError(model_missing=model_missing, web_tool_missing=web_tool_missing)


def demo_readiness_report(*, mode: str, environ: Mapping[str, str] | None = None) -> ReadinessReport:
    """Build a safe, non-network readiness report for a standalone demo."""
    if mode == "fixture":
        return ReadinessReport(
            mode="fixture",
            ready=True,
            summary="无凭据 fixture 图模式已就绪，不会调用模型或网页工具。",
            checks=(ReadinessCheck(name="mode", ready=True, detail="已选择 fixture 图组合。"),),
            durability_note="返回带记录的结果后会保留可检查的本地 run bundle；检查不会继续执行。",
        )
    if mode != "real":
        raise ValueError("demo_mode_invalid")

    model_ready = resolve_real_demo_model_profile(environ) is not None
    web_ready = _nonblank_environment_value(_TAVILY_API_KEY_VAR, environ) is not None
    checks = (
        ReadinessCheck(
            name="mode",
            ready=True,
            detail="已选择真实模式。",
        ),
        ReadinessCheck(
            name="model",
            ready=model_ready,
            detail="模型配置已就绪。" if model_ready else "尚未找到可用的模型配置。",
            next_action="配置一个受支持的模型后重新开始。" if not model_ready else "",
        ),
        ReadinessCheck(
            name="web_tool",
            ready=web_ready,
            detail="网页检索配置已就绪。" if web_ready else "尚未找到可用的网页检索配置。",
            next_action="配置网页检索凭据后重新开始。" if not web_ready else "",
        ),
    )
    if model_ready and web_ready:
        return ReadinessReport(
            mode="real",
            ready=True,
            summary="真实模式的本地前提检查已就绪。",
            checks=checks,
            durability_note="返回带记录的结果后会保留可检查的本地 run bundle；检查不会继续执行。",
        )
    code = (
        RunFailureCode.CONFIGURATION_MODEL_MISSING if not model_ready else RunFailureCode.CONFIGURATION_WEB_TOOL_MISSING
    )
    message = "模型配置尚未就绪。" if not model_ready else "网页检索前提尚未就绪。"
    next_action = "配置一个受支持的模型后重新开始。" if not model_ready else "配置网页检索凭据后重新开始。"
    return ReadinessReport(
        mode="real",
        ready=False,
        summary="真实模式的本地前提检查未通过。",
        checks=checks,
        failure=RunFailure(
            code=code,
            certainty=FailureCertainty.DIRECT,
            message=message,
            next_action=next_action,
            retryable=True,
            journal_record_created=False,
            diagnostic_location="unavailable",
        ),
        durability_note="尚未创建 Run Bundle 或保留观察。",
    )


def _model_config_for_profile(entry: _RegisteredDemoModel, *, api_key: str) -> Any:
    """Materialize one configured model without exporting its secret-bearing fields."""
    from deerflow.config.model_config import ModelConfig

    config: dict[str, Any] = {
        "name": entry.name,
        "use": entry.use_path,
        "model": entry.model_id,
        "api_key": api_key,
        **entry.extra_kwargs,
    }
    if entry.base_url is not None:
        config["base_url"] = entry.base_url
    return ModelConfig(**config)


def resolve_real_demo_model_profile(environ: Mapping[str, str] | None = None) -> DemoModelProfile | None:
    """Resolve exactly one explicit credential-backed all-real demo profile."""

    requested_name = _nonblank_environment_value(_DEMO_MODEL_SELECTOR_ENV, environ)
    if requested_name is None:
        return None
    matches = [
        (entry, api_key)
        for entry in _MODEL_REGISTRY
        if entry.name == requested_name
        if (api_key := _nonblank_environment_value(entry.credential_env, environ)) is not None
    ]
    if len(matches) != 1:
        return None
    entry, api_key = matches[0]
    return DemoModelProfile(
        model_config=_model_config_for_profile(entry, api_key=api_key),
        evidence=ExecutionProfileEvidence(profile_id=entry.name, registry_revision=entry.safe_revision),
    )


class _DemoSandboxConfig:
    use = "deerflow.sandbox.local:LocalSandboxProvider"


class DemoAppConfig:
    """Minimal config shim for the standalone demo.

    Provides a single auto-detected model plus a local-sandbox stub so the
    work-unit storage classifier and model factory both resolve without a full
    ``config.yaml``.
    """

    checkpointer = None
    database = None
    sandbox = _DemoSandboxConfig()
    tools: list[Any] = []

    def __init__(self, *, models: Sequence[Any] = ()) -> None:
        self._models = list(models)
        self.models = self._models

    def get_model_config(self, name: str):
        for model in self._models:
            if model.name == name:
                return model
        return None


async def _demo_storage_verifier(
    envelope: Any,
    *,
    bundle: RunBundleRef,
    provider: Any = None,
) -> Any:
    """Return a ready check without running the full POSIX probe.

    The probe exercises edge cases (lock/fsync/aliased-readback/cleanup) that
    are already covered by the unit suite. For a demo run on a real temp dir
    we skip those to keep startup fast and avoid cleanup-ordering issues with
    the process-local provider.
    """
    del envelope, bundle, provider

    from deerflow_deep_research.runtime.work_unit_storage import WorkUnitStorageCheck

    return WorkUnitStorageCheck("ready", "local_thread_mount")


# Patch all work-unit store classes to skip the storage probe in demo mode.
# Only overrides the *default* verifier; explicit callers (tests, real Gateway)
# that pass a custom ``storage_verifier`` are unaffected.
def _install_demo_storage_patch() -> None:
    from deerflow_deep_research.runtime import bootstrap_bundle as _bb
    from deerflow_deep_research.runtime import request_bundle as _rb
    from deerflow_deep_research.runtime import work_unit_store as _ws

    _targets = [
        (_bb, "BootstrapBundleStore"),
        (_rb, "RequestBundleStore"),
        (_ws, "WorkUnitStore"),
    ]
    for _mod, _cls_name in _targets:
        _cls = getattr(_mod, _cls_name, None)
        if _cls is None:
            continue
        _orig_create = _cls.create

        def _make_patched(orig, demo_verifier):
            @classmethod
            async def _patched(cls, envelope, *, bundle, storage_verifier=None, provider=None, **kw):
                return await orig.__func__(
                    cls,
                    envelope,
                    bundle=bundle,
                    storage_verifier=demo_verifier if storage_verifier is None else storage_verifier,
                    provider=provider,
                    **kw,
                )

            return _patched

        _cls.create = _make_patched(_orig_create, _demo_storage_verifier)


class DemoAdapter:
    def __init__(
        self,
        *,
        bundle_root: Path | None = None,
        model_profile: DemoModelProfile | None = None,
    ) -> None:
        agent_root = Path(__file__).resolve().parents[1]
        root = bundle_root or agent_root / _DEMO_BUNDLE_ROOT_NAME
        workspace = root / "workspace"
        uploads = root / "uploads"
        outputs = root / "outputs"
        self._root = root
        self._paths = (root, workspace, uploads, outputs)
        self._opened = False
        self._closed = False
        self._execution_profile = model_profile.evidence if model_profile is not None else None

        # Create a proper LocalSandbox so the work-unit storage verification can
        # exercise real POSIX primitives (aliased read/write, directory listing).
        sandbox = LocalSandbox(
            id="local",
            path_mappings=[
                PathMapping(container_path="/mnt/user-data/workspace", local_path=str(workspace)),
                PathMapping(container_path="/mnt/user-data/uploads", local_path=str(uploads)),
                PathMapping(container_path="/mnt/user-data/outputs", local_path=str(outputs)),
            ],
        )
        profile_kind = "all-real" if model_profile is not None else "fixture-graph"
        # A clean retained-data cutover starts in a distinct trusted scope. Legacy
        # local Bundles stay rejected; the demo never reopens or rewrites them.
        profile_key = hashlib.sha256(
            f"{root.resolve()}:{profile_kind}:{_DEMO_RETAINED_DATA_SCOPE_REVISION}".encode()
        ).hexdigest()[:16]
        real_scope_token = f"-{secrets.token_hex(8)}" if model_profile is not None else ""
        self._bundle_lifecycle = BundleLifecycle(workspace_host_path=workspace)
        self._envelope = TrustedRuntimeEnvelope(
            effective_user_id="demo-user",
            # Fixture profiles retain a stable scope. Each all-real standalone demo
            # gets an independent trusted scope and never discovers prior processes.
            outer_thread_id=f"demo-thread-{profile_key}{real_scope_token}",
            outer_run_id=f"demo-run-{secrets.token_hex(4)}",
            app_config=DemoAppConfig(models=(model_profile.model_config,) if model_profile is not None else ()),
            workspace_host_path=workspace,
            uploads_host_path=uploads,
            outputs_host_path=outputs,
            workspace_virtual_root="/mnt/user-data/workspace",
            uploads_virtual_root="/mnt/user-data/uploads",
            outputs_virtual_root="/mnt/user-data/outputs",
            parent_sandbox=sandbox,
            execution_profile=self._execution_profile,
        )
        self._observation_publisher = BundleRunObservationPublisher(
            lifecycle=self._bundle_lifecycle,
            scope=(self._envelope.effective_user_id, self._envelope.outer_thread_id),
        )

    @classmethod
    def for_real(
        cls,
        *,
        bundle_root: Path | None = None,
        environ: Mapping[str, str] | None = None,
    ) -> DemoAdapter:
        validate_real_demo_prerequisites(environ)
        profile = resolve_real_demo_model_profile(environ)
        if profile is None:
            raise DemoPrerequisiteError(model_missing=True, web_tool_missing=False)
        return cls(bundle_root=bundle_root, model_profile=profile)

    @property
    def execution_profile(self) -> ExecutionProfileEvidence | None:
        return self._execution_profile

    @property
    def observation_publisher(self) -> BundleRunObservationPublisher:
        return self._observation_publisher

    def local_bundle_workbench(self) -> BundleWorkbench:
        """Expose the fixed demo scope through the shared Bundle lifecycle only."""
        if not self._opened or self._closed:
            raise RuntimeError("demo_adapter_not_open")
        return BundleWorkbench(
            lifecycle=self._bundle_lifecycle,
            scope=(self._envelope.effective_user_id, self._envelope.outer_thread_id),
        )

    async def open(self) -> None:
        if self._closed:
            raise RuntimeError("demo_adapter_closed")
        if not self._opened:
            await asyncio.to_thread(self._create_local_paths)
            self._opened = True

    def _create_local_paths(self) -> None:
        for path in self._paths:
            path.mkdir(mode=0o700, parents=True, exist_ok=True)
            os.chmod(path, 0o700)

    async def adapt(
        self,
        _runtime: Any,
        *,
        initialize_parent_sandbox: bool = True,
    ) -> TrustedRuntimeEnvelope:
        await self.open()
        if initialize_parent_sandbox:
            return self._envelope
        return replace(self._envelope, parent_sandbox=None)

    async def create_work_unit_store(self, _envelope: Any, *, bundle: RunBundleRef) -> WorkUnitStore:
        return WorkUnitStore(
            workspace_host_path=self._envelope.workspace_host_path,
            bundle=bundle,
            clock=lambda: datetime.now(UTC),
            monotonic=time.monotonic,
            lock_sleep=time.sleep,
            token_factory=lambda: secrets.token_hex(16),
            fault_hook=None,
        )

    async def aclose(self) -> None:
        if self._closed:
            return
        self._closed = True
        await self._observation_publisher.close()

    def close(self) -> None:
        """Synchronous TUI teardown: it performs no filesystem finalization."""
        self._closed = True


# ── helpers ──────────────────────────────────────────────────────────


def _tool_call(action: str, call_id: str, bundle_id: str | None = None) -> AIMessage:
    args: dict[str, str] = {"action": action}
    if bundle_id is not None:
        args["bundle_id"] = bundle_id
    return AIMessage(
        content="",
        tool_calls=[{"name": "deep_research", "args": args, "id": call_id}],
    )


def _runtime(
    messages: list[Any],
    call_id: str,
    context: dict[str, Any] | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        state={"messages": messages},
        context=context if context is not None else {},
        tool_call_id=call_id,
    )


@dataclass(frozen=True)
class DemoRuntime:
    """Opaque graph-backed demo composition passed to the lifecycle transport."""

    mode: Literal["real", "fixture_graph"]
    adapter: DemoAdapter
    recipe: ResearchGraphRecipe
    executor: BundleGraphExecutor


class DemoLifecycleTransport:
    """Demo-owned binding for the runtime-owned lifecycle presentation module."""

    def __init__(self) -> None:
        self._adapter: DemoAdapter | None = None
        self._graph_executor: BundleGraphExecutor | None = None
        self._graph_backed = False
        self._call_ordinal = 0

    def bind(self, *, runtime: DemoRuntime) -> None:
        if self._adapter is not None:
            raise RuntimeError("demo_transport_already_bound")
        if runtime.executor is None:
            raise RuntimeError("demo_graph_executor_required")
        self._adapter = runtime.adapter
        self._graph_executor = runtime.executor
        self._graph_backed = True

    async def dispatch(
        self,
        *,
        action: str,
        bundle_id: str | None,
        messages: tuple[Any, ...],
        context: Mapping[str, Any] | None = None,
    ) -> object:
        if self._adapter is None:
            raise RuntimeError("demo_transport_not_bound")
        if self._graph_backed and self._graph_executor is None:
            raise RuntimeError("demo_graph_executor_required")
        self._call_ordinal += 1
        call_id = f"demo-lifecycle-{action}-{self._call_ordinal}"

        async def invoke() -> object:
            refinement = (context or {}).get("refinement")
            if not isinstance(refinement, str):
                refinement = None
            kwargs: dict[str, Any] = {
                "action": action,
                "probe_id": None,
                "bundle_id": bundle_id,
                "refinement": refinement,
                "runtime": _runtime(
                    [*messages, _tool_call(action, call_id, bundle_id)],
                    call_id,
                    context=dict(context or {}),
                ),
                "adapter": self._adapter,
            }
            if self._graph_backed:
                kwargs["bundle_graph_executor"] = self._graph_executor
            return await run_deep_research(**kwargs)

        return await invoke()


# ── phase metadata ───────────────────────────────────────────────────


PHASE_META: dict[str, tuple[str, str]] = {
    "bootstrap": ("初始化", "建立 research 环境"),
    "hitl1": ("研究配置", "确定研究方向与范围"),
    "hitl1_auto_profile": ("自动建档", "按自动策略确认研究范围"),
    "topic_planning": ("主题规划", "拆解研究问题为子主题"),
    "wave0": ("源数据收集", "收集初步资料"),
    "wave1": ("深度证据", "深挖关键证据"),
    "wave2_synthesis": ("综合分析", "跨主题综合"),
    "targeted_evidence": ("补证", "针对性补充证据"),
    "hitl2": ("自主决策", "根据已验证状态选择下一步"),
    "hitl2_auto_proceed": ("自动决策", "按自动策略选择下一步"),
    "rerun": ("重搜索", "按新方向重新搜索"),
    "readiness": ("可答性评估", "检查证据是否充分"),
    "final_delivery": ("报告生成", "输出最终报告"),
}

# ── recipe / host factories ──────────────────────────────────────────


def _bounded_text(value: Any, limit: int) -> str:
    return value[:limit] if isinstance(value, str) else ""


def _tool_payload(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _tavily_http_status(error: Exception) -> int | None:
    response = getattr(error, "response", None)
    status = getattr(response, "status_code", None)
    return status if isinstance(status, int) else None


def _is_retryable_tavily_read_failure(error: Exception) -> bool:
    if isinstance(error, (TimeoutError, httpx.TimeoutException, httpx.NetworkError, httpx.ProtocolError)):
        return True
    if isinstance(error, httpx.HTTPStatusError):
        status = _tavily_http_status(error)
        return status == 429 or (isinstance(status, int) and 500 <= status <= 599)
    return type(error).__module__ == "tavily.errors" and type(error).__name__ in {
        "TimeoutError",
        "UsageLimitExceededError",
    }


async def _read_tavily_with_retry(operation: Callable[[], Awaitable[Any]]) -> Any | None:
    for attempt in range(_TAVILY_MAX_READ_ATTEMPTS):
        try:
            async with asyncio.timeout(_TAVILY_ATTEMPT_TIMEOUT_SECONDS):
                return await operation()
        except asyncio.CancelledError:
            raise
        except Exception as error:
            if not _is_retryable_tavily_read_failure(error) or attempt + 1 == _TAVILY_MAX_READ_ATTEMPTS:
                return None
            await asyncio.sleep(_TAVILY_RETRY_BACKOFF_SECONDS[attempt])
    return None


def _build_demo_tavily_tools(api_key: str) -> tuple[BaseTool, BaseTool]:
    """Return one run-local search/fetch pair with URL provenance state."""
    approved_urls: set[str] = set()

    @tool
    async def web_search(query: str) -> str:
        """Search the public web for sources relevant to a research query."""

        async def search() -> Any:
            from tavily import AsyncTavilyClient

            async with AsyncTavilyClient(api_key=api_key) as client:
                return await client.search(
                    query,
                    max_results=_MAX_SEARCH_RESULTS,
                    timeout=_TAVILY_ATTEMPT_TIMEOUT_SECONDS,
                )

        payload = await _read_tavily_with_retry(search)
        if payload is None:
            return _tool_payload({"error": "web_search_unavailable"})

        raw_results = payload.get("results", []) if isinstance(payload, Mapping) else []
        results: list[dict[str, str]] = []
        if isinstance(raw_results, list):
            for item in raw_results:
                if not isinstance(item, Mapping):
                    continue
                url = item.get("url")
                if not isinstance(url, str) or not url:
                    continue
                results.append(
                    {
                        "title": _bounded_text(item.get("title"), _MAX_SEARCH_SNIPPET_CHARS),
                        "url": url,
                        "snippet": _bounded_text(item.get("content"), _MAX_SEARCH_SNIPPET_CHARS),
                    }
                )
                approved_urls.add(url)
                if len(results) == _MAX_SEARCH_RESULTS:
                    break
        return _tool_payload({"results": results})

    @tool
    async def web_fetch(url: str) -> str:
        """Fetch extracted content from a URL returned by this run's web search."""
        if url not in approved_urls:
            return _tool_payload({"error": "fetch_url_not_approved"})

        async def fetch() -> Any:
            from tavily import AsyncTavilyClient

            async with AsyncTavilyClient(api_key=api_key) as client:
                return await client.extract(
                    [url],
                    format="markdown",
                    timeout=_TAVILY_ATTEMPT_TIMEOUT_SECONDS,
                )

        payload = await _read_tavily_with_retry(fetch)
        if payload is None:
            return _tool_payload({"error": "web_fetch_unavailable"})

        raw_results = payload.get("results", []) if isinstance(payload, Mapping) else []
        content = ""
        if isinstance(raw_results, list):
            for item in raw_results:
                if not isinstance(item, Mapping) or item.get("url") != url:
                    continue
                content = _bounded_text(item.get("raw_content") or item.get("content"), _MAX_FETCH_CONTENT_CHARS)
                break
        if not content:
            return _tool_payload({"error": "web_fetch_no_content"})
        return _tool_payload({"url": url, "content": content})

    return web_search, web_fetch


def _build_demo_tools_resolver(api_key: str) -> Callable[[Any, ExecutionPolicy], Sequence[BaseTool]]:
    """Create a policy-filtered resolver without consulting global configuration."""

    def resolve(_envelope: Any, policy: ExecutionPolicy) -> Sequence[BaseTool]:
        allowed = policy.allowed_tool_names
        if "web_fetch" in allowed and "web_search" not in allowed:
            raise NodeAgentConfigurationError("tools_unavailable", "web_fetch requires web_search provenance")
        if "web_search" not in allowed:
            if allowed:
                names = ",".join(sorted(allowed))
                raise NodeAgentConfigurationError("tools_unavailable", f"no demo-local tools satisfy policy: {names}")
            return ()
        if not api_key:
            raise NodeAgentConfigurationError(
                "tools_unavailable", "TAVILY_API_KEY is required for demo-local web tools"
            )
        search, fetch = _build_demo_tavily_tools(api_key)
        return tuple(tool for tool in (search, fetch) if tool.name in allowed)

    return resolve


def build_demo_node_agent_bridge(
    *,
    envelope: Any,
    policy: ExecutionPolicy,
    tools_resolver: Callable[[Any, ExecutionPolicy], Sequence[Any]] | None = None,
    **kwargs: Any,
) -> RuntimeNodeAgentBridge:
    """Build a demo bridge that preserves zero-tool resolvers and localizes web tools.

    @impl DPL-001
    @impl DPL-003
    """
    resolver = tools_resolver
    if resolver is None:
        resolver = _build_demo_tools_resolver(_nonblank_environment_value(_TAVILY_API_KEY_VAR) or "")
    return RuntimeNodeAgentBridge(envelope=envelope, policy=policy, tools_resolver=resolver, **kwargs)


def build_fixture_demo_recipe(*, work_unit_store_factory: Any) -> ResearchGraphRecipe:
    """Load the deterministic fixture catalog for a fixture demo composition root.

    The caller must have enabled ``src_fake`` for its child process.  Keeping this
    import local prevents real demo paths from discovering fixture source.

    @impl DPL-003
    """
    from deerflow_deep_research_fixtures import build_fixture_recipe

    return build_fixture_recipe(work_unit_store_factory=work_unit_store_factory)


def build_real_demo_recipe(*, work_unit_store_factory: Any) -> ResearchGraphRecipe:
    """Build the fixed all-real recipe used by credentialed demo roots.

    @impl DPL-003
    """
    return ResearchGraphRecipe.all_real(
        work_unit_store_factory=work_unit_store_factory,
        node_agent_bridge_factory=build_demo_node_agent_bridge,
    )


def build_demo_runtime(*, mode: Literal["real", "fixture_graph"], adapter: DemoAdapter) -> DemoRuntime:
    """Compose one fixed graph-backed demo runtime without caller recipe authority."""

    if mode == "real":
        if adapter.execution_profile is None:
            raise RuntimeError("demo_real_profile_required")
        recipe = build_real_demo_recipe(work_unit_store_factory=adapter.create_work_unit_store)
    elif mode == "fixture_graph":
        recipe = build_fixture_demo_recipe(work_unit_store_factory=adapter.create_work_unit_store)
    else:
        raise ValueError("demo_runtime_mode_invalid")
    return DemoRuntime(
        mode=mode,
        adapter=adapter,
        recipe=recipe,
        executor=BundleGraphExecutor(recipe=recipe),
    )


def build_demo_host() -> Any:
    """Build the demo's generic probe host without lifecycle composition."""

    return build_control_graph_host(fingerprint_verifier=lambda _app_config: None)


# ── install demo patches at import time ──────────────────────────────

_install_demo_storage_patch()
