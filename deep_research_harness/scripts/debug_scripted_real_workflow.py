"""Operator-only scripted-real workflow debug command.

Runs the complete production Deep Research control path — real node adapters,
prompts, parsers, work-unit ledger, gates, routes, and persistence — against a
fixed narrow scripted external world: a template scripted chat model and two
scripted web tools. Zero `.env` reads, zero network, zero credentials.

Composition: ``ResearchGraphRecipe.all_real(work_unit_store_factory=…,
node_agent_bridge_factory=<scripted>)`` + ``BundleGraphExecutor`` driven through
the public control entry ``run_deep_research(start → HITL1 confirm → resume)``.

Authenticity: scripted_real_workflow. This command proves production
control-path integration for fixed legal inputs only; it proves nothing about
live model comprehension, web availability, latency, cost, coverage breadth,
or the targeted/rerun/provider-recovery branches.

@impl SCR-001
@impl SCR-002
@impl SCR-003
@impl SCR-004
@impl SCR-005
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import secrets
import shutil
import sys
import tempfile
import time
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from deerflow.config.app_config import AppConfig
from deerflow.config.model_config import ModelConfig
from deerflow.config.sandbox_config import SandboxConfig
from deerflow.sandbox.local.local_sandbox import LocalSandbox, PathMapping
from deerflow.sandbox.sandbox_provider import reset_sandbox_provider, set_sandbox_provider
from deerflow_deep_research_fixtures.scripted_real import baseline
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langgraph.types import Command

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, bundle_host_relative_root
from deerflow_deep_research.domain.run_observation import RecordBearingLifecycleFact
from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.node_agent_bridge import RuntimeNodeAgentBridge
from deerflow_deep_research.runtime.research import ResearchGraphRecipe
from deerflow_deep_research.runtime.run_observation import BundleRunObservationPublisher
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore
from deerflow_deep_research.tool import run_deep_research


@dataclass
class ScriptedRealRun:
    """Bounded observation of one scripted-real baseline run."""

    bundle_id: str
    terminal_status: str
    execution_trace: tuple[str, ...]
    model_calls: int
    web_search_calls: int
    web_fetch_calls: int
    consumed: tuple[str, ...] = ()
    wall_seconds: float = 0.0
    user_id: str = ""
    thread_id: str = ""
    workspace_host_path: Path = field(default_factory=Path)
    journal_path: str = ""
    envelope: Any = None
    record_count: int = 0
    wave1_review_artifacts: tuple[str, ...] = ()
    final_artifacts_published: bool = False
    backed_claim_count: int = 0
    accepted_refs: tuple[str, ...] = ()


class TemplateScriptedModel(BaseChatModel):
    """Queue of scripted responses; placeholders filled from the incoming prompt.

    Extra calls raise ``AssertionError`` (strict exhaustion); rendered values
    come only from the trusted assignment embedded in the incoming prompt, never
    from fabricated constants.
    """

    templates: list[str]
    calls: int = 0
    consumed: list[str] = field(default_factory=list)
    trip_readiness_output_cap: bool = False

    def _render(self, template: str, incoming: str) -> str:
        def first_submission_ref(_m: re.Match) -> str:
            match = re.search(r'"submission_ref":"([^"]+)"', incoming)
            if match is None:
                raise AssertionError(f"submission ref placeholder unresolved; incoming: {incoming[:800]}")
            return match.group(1)

        def first_wave0_ref(_m: re.Match) -> str:
            match = re.search(r'"wave0":\["([^"]+)"', incoming)
            if match is None:
                raise AssertionError(f"wave0 ref placeholder unresolved; incoming: {incoming[:800]}")
            return match.group(1)

        def ids_of(kind: str) -> str:
            ids: list[str] = []
            for candidate in re.findall(rf"{kind}:\d+", incoming):
                if candidate not in ids:
                    ids.append(candidate)
            return json.dumps(ids)

        rendered = re.sub(r"\{\{first_submission_ref\}\}", first_submission_ref, template)
        rendered = re.sub(r"\{\{wave0_first_ref\}\}", first_wave0_ref, rendered)
        rendered = re.sub(r"\{\{conclusion_ids\}\}", lambda _m: ids_of("conclusion"), rendered)
        rendered = re.sub(r"\{\{uncertainty_ids\}\}", lambda _m: ids_of("uncertainty"), rendered)
        return rendered

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:  # noqa: ARG002
        if not self.templates:
            raise AssertionError("scripted model exhausted its scripted responses")
        template = self.templates.pop(0)
        incoming = " ".join(str(getattr(m, "content", "")) for m in messages)
        self.calls += 1
        usage = {
            "input_tokens": baseline.MODEL_INPUT_TOKENS,
            "output_tokens": (
                4_097
                if self.trip_readiness_output_cap
                and "Assess answerability for exactly the assigned questions" in incoming
                else baseline.MODEL_OUTPUT_TOKENS
            ),
            "total_tokens": baseline.MODEL_TOTAL_TOKENS,
        }
        usage["total_tokens"] = usage["input_tokens"] + usage["output_tokens"]
        if template.startswith("TOOL_CALL:"):
            name = template.split(":", 1)[1]
            message = AIMessage(
                content="",
                tool_calls=[
                    {"name": name, "args": {"query": "scripted bounded query"}, "id": f"scripted-call-{self.calls}"}
                ],
                usage_metadata=usage,
            )
            self.consumed.append(f"tool:{name}")
        else:
            content = self._render(template, incoming)
            message = AIMessage(content=content, usage_metadata=usage)
            self.consumed.append(f"text:{content[:60]!r}")
        return ChatResult(generations=[ChatGeneration(message=message)])

    def bind_tools(self, tools: Any, **kwargs: Any) -> BaseChatModel:  # noqa: ARG002
        return self

    @property
    def _llm_type(self) -> str:
        return "template-scripted"


class _ScriptedWebTool:
    """Deterministic scripted web tool adapter with strict exhaustion."""

    def __init__(self, name: str, responses: tuple[str, ...]) -> None:
        self.name = name
        self._responses = list(responses)
        self.calls = 0

    def as_langchain_tool(self) -> Any:
        from langchain_core.tools import StructuredTool

        async def invoke(query: str = "", url: str = "") -> str:
            del query, url
            self.calls += 1
            if not self._responses:
                raise AssertionError(f"scripted tool exhausted: {self.name}")
            return self._responses.pop(0)

        return StructuredTool.from_function(
            coroutine=invoke,
            name=self.name,
            description=f"Deterministic scripted {self.name} adapter.",
        )


class _ScriptedBridgeFactory:
    """Bridge factory: real node policies, scripted model/tool resolvers."""

    def __init__(self, model: TemplateScriptedModel, search: _ScriptedWebTool, fetch: _ScriptedWebTool) -> None:
        self._model = model
        self._search = search
        self._fetch = fetch

    def __call__(self, *, envelope: Any, policy: Any, tools_resolver: Any = None) -> RuntimeNodeAgentBridge:
        from deerflow_deep_research.agents.policies import ExecutionBudget

        narrow_budget = ExecutionBudget(
            max_model_calls=3 if policy.allowed_tool_names else 1,
            max_total_tool_calls=3,
            max_tool_calls_per_response=3,
            max_parallel_tool_calls=3,
            total_token_budget=32_768,
            per_call_output_token_cap=4_096,
            per_tool_result_bytes=16_384,
            structured_result_bytes=8_192,
            wall_time_seconds=30.0,
        )
        bounded_policy = replace(policy, budget=narrow_budget)

        def model_resolver(_env: Any) -> TemplateScriptedModel:
            return self._model

        if policy.allowed_tool_names:

            def resolved_tools(_env: Any, _pol: Any) -> tuple[Any, ...]:
                return tuple(tool.as_langchain_tool() for tool in (self._search, self._fetch))

        else:
            resolved_tools = tools_resolver or (lambda _env, _pol: ())
        return RuntimeNodeAgentBridge(
            envelope=envelope,
            policy=bounded_policy,
            model_resolver=model_resolver,
            tools_resolver=resolved_tools,
        )


class _RegisteredLocalProvider:
    uses_thread_data_mounts = True
    needs_upload_permission_adjustment = False

    def __init__(self, sandbox: Any) -> None:
        self._sandbox = sandbox

    def acquire(self, thread_id: str | None = None, *, user_id: str | None = None) -> str:
        del thread_id, user_id
        return self._sandbox.id

    def get(self, sandbox_id: str) -> Any | None:
        return self._sandbox if sandbox_id == self._sandbox.id else None

    def release(self, sandbox_id: str) -> None:
        del sandbox_id

    def reset(self) -> None:
        return None


class _ScriptedAdapter:
    def __init__(self, envelope: Any) -> None:
        self.envelope = envelope

    async def adapt(self, _runtime: Any, *, initialize_parent_sandbox: bool = True) -> Any:
        if initialize_parent_sandbox:
            return self.envelope
        return replace(self.envelope, parent_sandbox=None)


class _ScriptedWorld:
    def __init__(
        self,
        *,
        envelope: Any,
        identity: tuple[str, str],
        adapter: _ScriptedAdapter,
        executor: BundleGraphExecutor,
        model: TemplateScriptedModel,
        search: _ScriptedWebTool,
        fetch: _ScriptedWebTool,
    ) -> None:
        self.envelope = envelope
        self.identity = identity
        self.adapter = adapter
        self.executor = executor
        self.model = model
        self.search = search
        self.fetch = fetch


def _tool_call(action: str, call_id: str, bundle_id: str | None = None) -> AIMessage:
    args = {"action": action}
    if bundle_id is not None:
        args["bundle_id"] = bundle_id
    return AIMessage(content="", tool_calls=[{"name": "deep_research", "args": args, "id": call_id}])


def _runtime(messages: list[Any], call_id: str) -> SimpleNamespace:
    return SimpleNamespace(state={"messages": messages}, context={}, tool_call_id=call_id)


def _response(request_id: str, message_id: str, *, kind: str, value: str) -> HumanMessage:
    payload: dict[str, Any] = {
        "version": 1,
        "kind": "human_input_response",
        "source": "deep_research",
        "request_id": request_id,
        "response_kind": kind,
        "value": value,
    }
    if kind == "option":
        payload["option_id"] = value
    return HumanMessage(content=value, id=message_id, additional_kwargs={"human_input_response": payload})


def _command_payload(command: Command) -> tuple[dict[str, Any], dict[str, Any]]:
    message = command.update["messages"][0]
    return json.loads(message.content), message.artifact["human_input"]


def _dummy_app_config() -> AppConfig:
    """AppConfig that classifies local storage but never resolves a live model."""
    return AppConfig(
        models=[
            ModelConfig(
                name="scripted-real-debug",
                use="deerflow.models.patched_deepseek:PatchedChatDeepSeek",
                model="deepseek-v4-pro",
                api_key="unused-scripted-only",
                max_retries=0,
                base_url="https://api.deepseek.com/v1",
            )
        ],
        sandbox=SandboxConfig(use="deerflow.sandbox.local:LocalSandboxProvider"),
    )


def _local_envelope(workspace: Path) -> tuple[TrustedRuntimeEnvelope, tuple[str, str]]:
    """Build a credential-free local envelope with a fixed trusted identity."""

    token = secrets.token_urlsafe(12).replace("-", "_")
    user_id, thread_id = "debug-operator", f"thread-{token}"
    for path in (workspace / "workspace", workspace / "uploads", workspace / "outputs"):
        path.mkdir(parents=True, exist_ok=True)
    sandbox = LocalSandbox(
        id=f"local:{user_id}:{thread_id}",
        path_mappings=[
            PathMapping(container_path="/mnt/user-data/workspace", local_path=str(workspace / "workspace")),
            PathMapping(container_path="/mnt/user-data/uploads", local_path=str(workspace / "uploads")),
            PathMapping(container_path="/mnt/user-data/outputs", local_path=str(workspace / "outputs")),
        ],
    )
    envelope = TrustedRuntimeEnvelope(
        effective_user_id=user_id,
        outer_thread_id=thread_id,
        outer_run_id=f"run-{token}",
        app_config=_dummy_app_config(),
        workspace_host_path=workspace / "workspace",
        uploads_host_path=workspace / "uploads",
        outputs_host_path=workspace / "outputs",
        workspace_virtual_root="/mnt/user-data/workspace",
        uploads_virtual_root="/mnt/user-data/uploads",
        outputs_virtual_root="/mnt/user-data/outputs",
        parent_sandbox=sandbox,
    )
    return envelope, (user_id, thread_id)


def build_world(workspace: Path, *, run_id: str, scenario: str = "baseline") -> _ScriptedWorld:
    """Compose the all-real recipe with scripted capabilities on a local sandbox."""

    del run_id
    if scenario == "repair-targeted":
        model_script = baseline.REPAIR_TARGETED_SCRIPT
        search_responses = baseline.REPAIR_TARGETED_SEARCH_RESPONSES
        fetch_responses = baseline.REPAIR_TARGETED_FETCH_RESPONSES
    elif scenario in {"baseline", "readiness-cap-trip"}:
        model_script = baseline.MODEL_SCRIPT
        search_responses = baseline.WEB_SEARCH_RESPONSES
        fetch_responses = baseline.WEB_FETCH_RESPONSES
    else:
        raise ValueError(f"unknown_scripted_real_scenario:{scenario}")
    envelope, identity = _local_envelope(workspace)
    set_sandbox_provider(_RegisteredLocalProvider(envelope.parent_sandbox))

    def store_clock() -> datetime:
        # AttemptRef lifecycle requires an advancing clock (created_at <= terminal_at);
        # the real wave0 node stamps attempts with datetime.now(UTC). Freeze IDs,
        # never time.
        return datetime.now(UTC)

    async def create_store(envelope: Any, *, bundle: RunBundleRef, **_kwargs: Any) -> WorkUnitStore:
        return WorkUnitStore(
            workspace_host_path=envelope.workspace_host_path,
            bundle=bundle,
            clock=store_clock,
            monotonic=time.monotonic,
            lock_sleep=time.sleep,
            token_factory=lambda: "a" * 32,
            fault_hook=None,
        )

    model = TemplateScriptedModel(
        templates=list(model_script),
        trip_readiness_output_cap=scenario == "readiness-cap-trip",
    )
    search = _ScriptedWebTool("web_search", search_responses)
    fetch = _ScriptedWebTool("web_fetch", fetch_responses)
    recipe = ResearchGraphRecipe.all_real(
        work_unit_store_factory=create_store,
        node_agent_bridge_factory=_ScriptedBridgeFactory(model, search, fetch),
    )
    return _ScriptedWorld(
        envelope=envelope,
        identity=identity,
        adapter=_ScriptedAdapter(envelope),
        executor=BundleGraphExecutor(recipe=recipe),
        model=model,
        search=search,
        fetch=fetch,
    )


async def _drive(world: _ScriptedWorld, *, expected_code: str) -> dict[str, Any]:
    question = HumanMessage(content=baseline.BASELINE_QUESTION, id="scripted-real-start")
    start_call = _tool_call("start", "scripted-real-start-call")
    started = await run_deep_research(
        action="start",
        probe_id=None,
        runtime=_runtime([question, start_call], "scripted-real-start-call"),
        adapter=world.adapter,
        bundle_graph_executor=world.executor,
    )
    if not isinstance(started, Command):
        raise AssertionError(f"start did not suspend at HITL1: {started}")
    start_control, hitl1 = _command_payload(started)
    request_id = str(hitl1.get("request_id", ""))
    if not request_id:
        raise AssertionError(f"HITL1 interaction missing: {start_control}")
    bundle_id = start_control["bundle_id"]

    confirmation = _response(request_id, "scripted-real-confirm", kind="text", value=baseline.BASELINE_CONFIRMATION)
    resume_call = _tool_call("resume", "scripted-real-resume-1", bundle_id)
    resumed = await run_deep_research(
        action="resume",
        probe_id=None,
        bundle_id=bundle_id,
        runtime=_runtime([question, confirmation, resume_call], "scripted-real-resume-1"),
        adapter=world.adapter,
        bundle_graph_executor=world.executor,
    )
    if isinstance(resumed, Command):
        # Current real HITL2 is autonomous; keep a proceed step for a future
        # human-decision HITL2 route.
        _, hitl2 = _command_payload(resumed)
        proceed = _response(str(hitl2.get("request_id", "")), "scripted-real-proceed", kind="option", value="proceed")
        final_call = _tool_call("resume", "scripted-real-resume-2", bundle_id)
        completed = await run_deep_research(
            action="resume",
            probe_id=None,
            bundle_id=bundle_id,
            runtime=_runtime([question, confirmation, proceed, final_call], "scripted-real-resume-2"),
            adapter=world.adapter,
            bundle_graph_executor=world.executor,
        )
    else:
        completed = resumed
    if not isinstance(completed, dict):
        raise AssertionError(f"resume did not produce a terminal result: {completed}")
    if completed.get("code") != expected_code:
        raise AssertionError(f"scripted run did not complete ({expected_code}): {completed}")
    return completed


async def _observe(
    world: _ScriptedWorld, completed: dict[str, Any], *, allow_targeted_evidence: bool
) -> ScriptedRealRun:
    lifecycle = BundleLifecycle(workspace_host_path=world.envelope.workspace_host_path)
    bundle = await lifecycle.resolve(
        scope=(world.envelope.effective_user_id, world.envelope.outer_thread_id),
        bundle_id=BundleId(str(completed["bundle_id"])),
    )
    if bundle is None:
        raise AssertionError(f"selected bundle unavailable: {completed.get('bundle_id')}")
    state = await lifecycle.read_state(bundle)
    trace = tuple(state.execution_trace or ())
    if not allow_targeted_evidence and ("targeted_evidence" in trace or "rerun" in trace):
        raise AssertionError(f"baseline entered an out-of-scope branch: {trace}")
    if "rerun" in trace:
        raise AssertionError(f"scripted run entered the out-of-scope rerun branch: {trace}")
    # The demo entry points publish lifecycle observations through their experience
    # wrapper; this operator workflow drives the public tool surface directly, so it
    # publishes the terminal observation itself. Without this, run-summary.json stays
    # at the initial establish fact and inspection cannot report the terminal state.
    if state.terminal_status is not None:
        await BundleRunObservationPublisher(lifecycle=lifecycle, scope=world.identity).publish(
            RecordBearingLifecycleFact(
                bundle_id=bundle.bundle_id.value,
                action="status",
                status=state.terminal_status.value,
                phase=state.phase.value,
                generation=state.generation,
                durability="restart_durable",
                terminal_outcome=state.terminal_status.value,
            )
        )
    journal_path = str(
        Path(world.envelope.workspace_host_path) / bundle_host_relative_root(bundle) / "diagnostics" / "events.jsonl"
    )
    store = await WorkUnitStore.create(world.envelope, bundle=bundle)
    records = await store.load_records()
    accepted_refs = tuple(record.record_hash for record in records)
    bundle_root = Path(world.envelope.workspace_host_path) / "deep-research" / "scopes"
    review_artifacts = sorted(
        path.name
        for path in bundle_root.glob("*/b_*/work/g0_wave1_*/*/cache/review/*.json")
        if path.name in {"source-diagnostic.json", "claim-verifier.json"}
    )
    final_artifacts = await store.observe_final_artifacts()
    backed_claim_count = 0
    if final_artifacts is not None:
        try:
            citation_payload = json.loads(final_artifacts[1])
            claims = citation_payload.get("claims") if isinstance(citation_payload, dict) else None
            if isinstance(claims, dict):
                backed_claim_count = sum(
                    1 for value in claims.values() if isinstance(value, dict) and value.get("backing_refs")
                )
        except (UnicodeDecodeError, json.JSONDecodeError):
            backed_claim_count = 0
    return ScriptedRealRun(
        bundle_id=bundle.bundle_id.value,
        terminal_status=(state.terminal_status.value if state.terminal_status is not None else ""),
        execution_trace=trace,
        model_calls=world.model.calls,
        web_search_calls=world.search.calls,
        web_fetch_calls=world.fetch.calls,
        consumed=tuple(world.model.consumed),
        user_id=world.envelope.effective_user_id,
        thread_id=world.envelope.outer_thread_id,
        workspace_host_path=Path(world.envelope.workspace_host_path),
        journal_path=journal_path,
        envelope=world.envelope,
        record_count=len(records),
        wave1_review_artifacts=tuple(review_artifacts),
        final_artifacts_published=final_artifacts is not None,
        backed_claim_count=backed_claim_count,
        accepted_refs=accepted_refs,
    )


async def run_scripted_real_workflow(
    *, workspace: Path, run_id: str = "baseline", scenario: str = "baseline"
) -> ScriptedRealRun:
    """Run one fixed narrow scenario through the all-real production control path."""

    started_at = time.monotonic()
    world = build_world(workspace, run_id=run_id, scenario=scenario)
    try:
        expected_code = "blocked" if scenario == "repair-targeted" else "completed"
        completed = await _drive(world, expected_code=expected_code)
        result = await _observe(world, completed, allow_targeted_evidence=scenario == "repair-targeted")
        result.wall_seconds = time.monotonic() - started_at
        # The readiness cap trip degrades instead of killing (tiered budget):
        # the bridge keeps the already-generated critic output, so the cap-trip
        # scenario consumes the same model calls as baseline (the readiness
        # critic output is admitted and the real composer runs).
        expected_model_calls = (
            baseline.EXPECTED_REPAIR_TARGETED_MODEL_CALLS
            if scenario == "repair-targeted"
            else baseline.EXPECTED_MODEL_CALLS
        )
        expected_search_calls = (
            baseline.EXPECTED_WEB_SEARCH_CALLS
            if scenario != "repair-targeted"
            else baseline.EXPECTED_REPAIR_TARGETED_SEARCH_CALLS
        )
        expected_fetch_calls = (
            baseline.EXPECTED_WEB_FETCH_CALLS
            if scenario != "repair-targeted"
            else baseline.EXPECTED_REPAIR_TARGETED_FETCH_CALLS
        )
        if result.model_calls != expected_model_calls:
            raise AssertionError(
                f"scripted model-call budget violated: {result.model_calls} != {expected_model_calls} "
                f"(consumed: {result.consumed})"
            )
        if result.web_search_calls != expected_search_calls:
            raise AssertionError(
                f"scripted web_search budget violated: {result.web_search_calls} != {expected_search_calls}"
            )
        if result.web_fetch_calls != expected_fetch_calls:
            raise AssertionError(
                f"scripted web_fetch budget violated: {result.web_fetch_calls} != {expected_fetch_calls}"
            )
        if result.record_count < 2:
            raise AssertionError(f"scripted run accepted fewer than 2 work-unit records: {result.record_count}")
        if {"source-diagnostic.json", "claim-verifier.json"} - set(result.wave1_review_artifacts):
            raise AssertionError(f"scripted run missing Wave1 critic review artifacts: {result.wave1_review_artifacts}")
        if scenario in {"baseline", "readiness-cap-trip"}:
            if not result.final_artifacts_published:
                raise AssertionError("baseline did not publish the final report and citation-map pair")
            if result.backed_claim_count < 1:
                raise AssertionError("baseline citation map has no claim with a backing reference")
        return result
    finally:
        reset_sandbox_provider()


def _render_output(result: ScriptedRealRun) -> str:
    return "\n".join(
        [
            "Deep Research · scripted-real workflow debug",
            "composition:      all_real_adapters",
            "authenticity:     scripted_real_workflow",
            "zero-network:     true (scripted tools only)",
            "zero-credentials: true (no .env or provider keys read)",
            f"question:         {baseline.BASELINE_QUESTION}",
            f"bundle_id:        {result.bundle_id}",
            f"terminal_status:  {result.terminal_status}",
            f"execution_trace:  {' -> '.join(result.execution_trace)}",
            "wave0 intake:     accepted (>=1 work-unit record)",
            "wave1 reviews:    2 critic artifacts (source-diagnostic, claim-verifier)",
            "wave2 finding:    1 finding with an accepted backing ref",
            f"model calls:      {result.model_calls}",
            f"web_search calls: {result.web_search_calls}",
            f"web_fetch calls:  {result.web_fetch_calls}",
            f"wall seconds:     {result.wall_seconds:.2f}",
            f"event journal:    {result.journal_path}",
            "",
            "This run proves only that the production control path (real node adapters,",
            "prompts, parsers, work-unit ledger, gates, routes, and persistence) integrates",
            "correctly for these fixed legal inputs. It does NOT prove real model",
            "comprehension or prompt obedience, Tavily/web availability, page quality,",
            "latency, cost, or rate limits, multi-topic concurrency, coverage breadth,",
            "research depth quality, or the targeted-evidence/rerun/provider-recovery",
            "branches.",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Operator-only scripted-real workflow debug command.")
    parser.add_argument("--workspace", type=Path, default=None, help="Workspace root (default: fresh temp dir).")
    parser.add_argument("--keep", action="store_true", help="Keep the run bundle after completion.")
    args = parser.parse_args(argv)

    workspace = args.workspace
    cleanup = workspace is None and not args.keep
    if workspace is None:
        workspace = Path(tempfile.mkdtemp(prefix="scripted-real-debug-"))
    try:
        result = asyncio.run(run_scripted_real_workflow(workspace=workspace))
        print(_render_output(result))
        return 0
    except Exception as exc:
        print(f"scripted-real debug FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    finally:
        if cleanup:
            shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
