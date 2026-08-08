"""Manual full-real release acceptance control plane.

@impl EVH-004
@impl EVH-005
@impl EVH-009
"""

from __future__ import annotations

import asyncio
import json
import re
import secrets
import shutil
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Command

from deerflow_deep_research.domain.bundle import BundleId
from deerflow_deep_research.domain.state import BundleLocalState
from deerflow_deep_research.domain.work_units import canonicalize_source_url
from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle, BundleLifecycleError
from deerflow_deep_research.runtime.research import ResearchGraphRecipe
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore
from deerflow_deep_research.tool import run_deep_research
from tests.assets.evidence import AuthenticityLevel
from tests.scenarios.canaries import (
    _app_config,
    _BridgeFactory,
    _LiveAdapter,
    _LiveWebSearch,
    _UsageTracker,
)
from tests.scenarios.live import LiveEnvironment, LivePreflightError, preflight_live_environment


class ReleasePreflightError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def preflight_release_environment(*, environ: Mapping[str, str]) -> LiveEnvironment:
    if environ.get("RELEASE_E2E_CONFIRM") != "1":
        raise ReleasePreflightError(
            "release_confirmation_missing",
            "set RELEASE_E2E_CONFIRM=1 before selecting full-real acceptance",
        )
    try:
        return preflight_live_environment(environ=environ, require_web=True)
    except LivePreflightError as exc:
        raise ReleasePreflightError(exc.code, str(exc).split(": ", 1)[-1]) from exc


@dataclass(frozen=True)
class ReleaseInvocation:
    user_id: str
    thread_id: str
    run_id: str


def new_release_invocation() -> ReleaseInvocation:
    token = secrets.token_urlsafe(18).replace("-", "_")
    user_id = "release-e2e"
    thread_id = f"release-thread-{token}"
    run_id = f"release-run-{token}"
    return ReleaseInvocation(user_id, thread_id, run_id)


def _release_attempt_root(workspace: str | Path, run_id: str) -> Path:
    workspace_root = Path(workspace).resolve()
    attempt_root = (workspace_root / run_id).resolve()
    if attempt_root.parent != workspace_root:
        raise ValueError("release_workspace_invalid")
    return attempt_root


@dataclass(frozen=True)
class ReleaseScenario:
    scenario_id: str
    authenticity: AuthenticityLevel
    request_text: str
    confirmation_text: str
    declared_source_urls: tuple[str, ...]
    declared_source_set_id: str
    expected_trace: tuple[str, ...]
    required_artifacts: tuple[str, ...]


RELEASE_SCENARIO = ReleaseScenario(
    scenario_id="release-full-real-acceptance",
    authenticity=AuthenticityLevel.FULL_REAL_PIPELINE,
    request_text=(
        "请只使用 Python 官方文档，用中文为一个现有 Python Web 服务写一份升级到 Python 3.12 前的检查清单："
        "列出三项最重要的兼容性或运行时变化，并为每项给出具体来源链接。"
    ),
    confirmation_text="确认",
    declared_source_urls=(
        "https://docs.python.org/3.12/whatsnew/3.12.html",
        "https://docs.python.org/3.12/library/venv.html",
        "https://docs.python.org/3.12/library/removed.html",
    ),
    declared_source_set_id="python-docs-3.12",
    expected_trace=(
        "bootstrap",
        "hitl1",
        "topic_planning",
        "wave0",
        "wave1",
        "wave2_synthesis",
        "hitl2",
        "readiness",
        "final_delivery",
    ),
    required_artifacts=("final/report.md", "final/claim-citation-map.json"),
)


def _release_source_urls_by_policy(scenario: ReleaseScenario) -> dict[str, frozenset[str]]:
    """Partition the fixed release corpus across the existing worker policies."""
    try:
        declared_urls = tuple(canonicalize_source_url(url) for url in scenario.declared_source_urls)
    except ValueError as exc:
        raise ValueError("release_source_partition_invalid") from exc
    if len(declared_urls) != 3 or len(set(declared_urls)) != 3:
        raise ValueError("release_source_partition_invalid")
    return {
        "wave0-source-intake": frozenset(declared_urls[:1]),
        "wave1-evidence-extraction": frozenset(declared_urls[1:]),
    }


@dataclass(frozen=True)
class ReleaseOutcome:
    invocation: ReleaseInvocation
    bundle_id: str
    terminal_status: str
    lifecycle_trace: tuple[str, ...]
    accepted_submission_refs: tuple[str, ...]
    artifacts: tuple[str, ...]
    citation_bindings: dict[str, tuple[str, ...]]
    confirmation_traversed: bool
    report_nonempty: bool
    report_contains_chinese: bool
    declared_source_set_id: str
    declared_source_set_only: bool
    distinct_source_count: int
    contained: bool
    cleaned_up: bool


@dataclass(frozen=True)
class _CitationSourceEvidence:
    declared_source_set_only: bool
    distinct_source_count: int


@dataclass(frozen=True)
class ReleaseAttempt:
    outcome: ReleaseOutcome | None
    error_code: str | None
    wall_time_seconds: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    tool_calls: int = 0
    response_shapes: tuple[dict[str, object], ...] = ()


@dataclass(frozen=True)
class ReleaseAttemptReport:
    attempt: int
    error_code: str | None
    wall_time_seconds: float
    input_tokens: int | None
    output_tokens: int | None
    tool_calls: int
    response_shapes: tuple[dict[str, object], ...]


@dataclass(frozen=True)
class ReleaseReport:
    scenario_id: str
    invocation: ReleaseInvocation
    attempt_count: int
    retry_count: int
    hard_invariants: dict[str, bool]
    outcome_summary: dict[str, object] | None
    attempts: tuple[ReleaseAttemptReport, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class ReleaseAcceptanceFailure(AssertionError):
    def __init__(self, message: str, report: ReleaseReport) -> None:
        super().__init__(message)
        self.report = report


ReleaseExecutor = Callable[[ReleaseScenario, ReleaseInvocation], Awaitable[ReleaseAttempt]]


def _citation_source_evidence(
    *,
    accepted_submission_refs: tuple[str, ...],
    citation_bindings: Mapping[str, tuple[str, ...]],
    records: tuple[object, ...],
    declared_source_urls: tuple[str, ...],
) -> _CitationSourceEvidence:
    """Derive only bounded source-set facts from cited accepted records."""

    records_by_hash: dict[str, object] = {}
    for record in records:
        record_hash = getattr(record, "record_hash", None)
        if isinstance(record_hash, str):
            records_by_hash[record_hash] = record

    cited_record_refs = {reference for references in citation_bindings.values() for reference in references}
    cited_urls: set[str] = set()
    source_refs_complete = True
    for reference in cited_record_refs:
        record = records_by_hash.get(reference)
        source_refs = getattr(record, "source_refs", ())
        if record is None or not isinstance(source_refs, (tuple, list)) or not source_refs:
            source_refs_complete = False
            continue
        for source in source_refs:
            canonical_url = getattr(source, "canonical_url", None)
            if not isinstance(canonical_url, str) or not canonical_url:
                source_refs_complete = False
                continue
            cited_urls.add(canonical_url)

    return _CitationSourceEvidence(
        declared_source_set_only=(
            bool(cited_record_refs)
            and cited_record_refs <= set(accepted_submission_refs)
            and source_refs_complete
            and bool(cited_urls)
            and cited_urls <= set(declared_source_urls)
        ),
        distinct_source_count=len(cited_urls),
    )


def _hard_invariants(
    scenario: ReleaseScenario,
    invocation: ReleaseInvocation,
    outcome: ReleaseOutcome | None,
) -> dict[str, bool]:
    if outcome is None:
        return {
            "terminal_completed": False,
            "lifecycle_trace_complete": False,
            "accepted_evidence_present": False,
            "report_artifacts_present": False,
            "citation_bindings_valid": False,
            "paths_contained": False,
            "cleanup_complete": False,
            "bundle_result_bound": False,
            "confirmation_traversed": False,
            "report_nonempty": False,
            "report_contains_chinese": False,
            "minimum_cited_claims": False,
            "declared_source_set_only": False,
            "minimum_distinct_sources": False,
        }
    accepted = set(outcome.accepted_submission_refs)
    cited_claim_count = sum(bool(refs) for refs in outcome.citation_bindings.values())
    citation_bindings_valid = bool(outcome.citation_bindings) and all(
        bool(refs) and all(isinstance(reference, str) and reference in accepted for reference in refs)
        for refs in outcome.citation_bindings.values()
    )
    collapsed_trace: list[str] = []
    max_consecutive_visits = 0
    consecutive_visits = 0
    for phase in outcome.lifecycle_trace:
        if collapsed_trace and phase == collapsed_trace[-1]:
            consecutive_visits += 1
        else:
            collapsed_trace.append(phase)
            consecutive_visits = 1
        max_consecutive_visits = max(max_consecutive_visits, consecutive_visits)
    try:
        BundleId(outcome.bundle_id)
        bundle_result_bound = outcome.invocation == invocation
    except ValueError:
        bundle_result_bound = False
    return {
        "terminal_completed": outcome.terminal_status == "completed",
        "lifecycle_trace_complete": tuple(collapsed_trace) == scenario.expected_trace and max_consecutive_visits <= 3,
        "accepted_evidence_present": bool(accepted),
        "report_artifacts_present": set(scenario.required_artifacts) <= set(outcome.artifacts),
        "citation_bindings_valid": citation_bindings_valid,
        "paths_contained": outcome.contained,
        "cleanup_complete": outcome.cleaned_up,
        "bundle_result_bound": bundle_result_bound,
        "confirmation_traversed": outcome.confirmation_traversed and "hitl1" in outcome.lifecycle_trace,
        "report_nonempty": outcome.report_nonempty,
        "report_contains_chinese": outcome.report_contains_chinese,
        "minimum_cited_claims": cited_claim_count >= 3,
        "declared_source_set_only": (
            outcome.declared_source_set_only and outcome.declared_source_set_id == scenario.declared_source_set_id
        ),
        "minimum_distinct_sources": outcome.distinct_source_count >= 2,
    }


def _outcome_summary(outcome: ReleaseOutcome | None) -> dict[str, object] | None:
    if outcome is None:
        return None
    return {
        "terminal_status": outcome.terminal_status,
        "lifecycle_trace": outcome.lifecycle_trace,
        "accepted_count": len(outcome.accepted_submission_refs),
        "artifacts": outcome.artifacts,
        "citation_claim_count": len(outcome.citation_bindings),
        "citation_ref_count": sum(len(refs) for refs in outcome.citation_bindings.values()),
        "confirmation_traversed": outcome.confirmation_traversed,
        "report_nonempty": outcome.report_nonempty,
        "report_contains_chinese": outcome.report_contains_chinese,
        "declared_source_set_id": outcome.declared_source_set_id,
        "declared_source_set_only": outcome.declared_source_set_only,
        "distinct_source_count": outcome.distinct_source_count,
        "contained": outcome.contained,
        "cleaned_up": outcome.cleaned_up,
    }


class ReleaseRunner:
    def __init__(self, *, executor: ReleaseExecutor, max_attempts: int) -> None:
        if not 1 <= max_attempts <= 2:
            raise ValueError("release_attempt_bound_invalid")
        self._executor = executor
        self._max_attempts = max_attempts

    async def run(self, scenario: ReleaseScenario, invocation: ReleaseInvocation) -> ReleaseReport:
        attempts: list[ReleaseAttempt] = []
        outcome: ReleaseOutcome | None = None
        for _ in range(self._max_attempts):
            attempt = await self._executor(scenario, invocation)
            attempts.append(attempt)
            if attempt.outcome is not None:
                outcome = attempt.outcome
                break
        invariants = _hard_invariants(scenario, invocation, outcome)
        report = ReleaseReport(
            scenario_id=scenario.scenario_id,
            invocation=invocation,
            attempt_count=len(attempts),
            retry_count=len(attempts) - 1,
            hard_invariants=invariants,
            outcome_summary=_outcome_summary(outcome),
            attempts=tuple(
                ReleaseAttemptReport(
                    index,
                    attempt.error_code,
                    attempt.wall_time_seconds,
                    attempt.input_tokens,
                    attempt.output_tokens,
                    attempt.tool_calls,
                    attempt.response_shapes,
                )
                for index, attempt in enumerate(attempts, start=1)
            ),
        )
        if not all(invariants.values()):
            failed = ",".join(name for name, passed in invariants.items() if not passed)
            raise ReleaseAcceptanceFailure(
                f"scenario={scenario.scenario_id} lane=release authenticity=full_real_pipeline: "
                f"hard invariants failed: {failed}",
                report,
            )
        return report


def _tool_call(action: str, call_id: str, bundle_id: str | None = None) -> AIMessage:
    args = {"action": action}
    if bundle_id is not None:
        args["bundle_id"] = bundle_id
    return AIMessage(content="", tool_calls=[{"name": "deep_research", "args": args, "id": call_id}])


def _runtime(messages: list[object], call_id: str):
    from types import SimpleNamespace

    return SimpleNamespace(state={"messages": messages}, context={}, tool_call_id=call_id)


def _command_payload(command: Command) -> tuple[dict[str, object], dict[str, object]]:
    message = command.update["messages"][0]
    return json.loads(message.content), message.artifact["human_input"]


def _response(request_id: str, message_id: str, *, kind: str, value: str) -> HumanMessage:
    payload: dict[str, object] = {
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


def _is_complete_hitl1_interaction(request: Mapping[str, object]) -> bool:
    interaction = request.get("interaction")
    if request.get("mode") != "text" or not isinstance(interaction, Mapping):
        return False
    subject = interaction.get("subject")
    controls = interaction.get("controls")
    if not isinstance(subject, Mapping) or not isinstance(subject.get("proposal"), Mapping):
        return False
    if not isinstance(controls, list):
        return False
    return any(isinstance(control, Mapping) and control.get("id") == "accept_current_proposal" for control in controls)


def _is_hitl2_proceed_interaction(control: Mapping[str, object], request: Mapping[str, object]) -> bool:
    pending = control.get("pending_input")
    options = request.get("options")
    if (
        not isinstance(pending, Mapping)
        or pending.get("pending_phase") != "hitl2"
        or pending.get("request_id") != request.get("request_id")
        or request.get("mode") != "choice"
        or not isinstance(options, list)
    ):
        return False
    return any(
        isinstance(option, Mapping) and option.get("id") == "proceed" and option.get("value") == "proceed"
        for option in options
    )


def _selected_bundle_id(control: Mapping[str, object]) -> str | None:
    """Extract the one public Bundle identity from a trusted lifecycle result."""

    value = control.get("bundle_id")
    if not isinstance(value, str):
        return None
    try:
        return BundleId(value).value
    except ValueError:
        return None


_RELEASE_CONTROL_TOKEN = re.compile(r"^[a-z][a-z0-9_.-]{0,95}$")


def _release_control_failure_code(stage: str, control: Mapping[str, object]) -> str:
    """Report only the public bounded terminal classification for a failed control."""

    code = control.get("code")
    if not isinstance(code, str) or _RELEASE_CONTROL_TOKEN.fullmatch(code) is None:
        return f"{stage}:invalid"
    incident = control.get("terminal_incident")
    if code != "blocked" or not isinstance(incident, Mapping):
        return f"{stage}:{code}"
    phase = incident.get("phase")
    failure_code = incident.get("code")
    if not (
        isinstance(phase, str)
        and isinstance(failure_code, str)
        and _RELEASE_CONTROL_TOKEN.fullmatch(phase) is not None
        and _RELEASE_CONTROL_TOKEN.fullmatch(failure_code) is not None
    ):
        return f"{stage}:{code}"
    return f"{stage}:{code}:{phase}:{failure_code}"


@dataclass(frozen=True)
class _SelectedBundleObservation:
    """Bounded release facts read only through one selected Run Bundle."""

    state: BundleLocalState
    records: tuple[object, ...]
    final_artifacts: tuple[bytes, bytes] | None


class ReleaseBundleExecutionAdapter:
    """Drive public controls and observe their selected Bundle without a side channel.

    The release scenario owns only its trusted outer scope and the public opaque id
    returned by the entry point. It reauthorizes that id against Bundle-local State
    before reading fixed contained final artifacts.

    @impl EVH-024
    """

    def __init__(
        self,
        *,
        adapter: Any,
        graph_executor: BundleGraphExecutor,
        invocation: ReleaseInvocation,
    ) -> None:
        self._adapter = adapter
        self._graph_executor = graph_executor
        self._invocation = invocation

    async def control(
        self,
        *,
        action: str,
        messages: list[object],
        tool_call_id: str,
        bundle_id: str | None = None,
    ) -> Any:
        return await run_deep_research(
            action=action,
            probe_id=None,
            bundle_id=bundle_id,
            runtime=_runtime(messages, tool_call_id),
            adapter=self._adapter,
            bundle_graph_executor=self._graph_executor,
        )

    async def observe(self, *, bundle_id: str) -> _SelectedBundleObservation | None:
        """Reauthorize and read the selected Bundle without reopening another source."""

        try:
            selected_id = BundleId(bundle_id)
            envelope = self._adapter.envelope
            lifecycle = BundleLifecycle(workspace_host_path=envelope.workspace_host_path)
            bundle = await lifecycle.resolve(
                scope=(self._invocation.user_id, self._invocation.thread_id),
                bundle_id=selected_id,
            )
            if bundle is None:
                return None
            state = await lifecycle.read_state(bundle)
            if state.bundle_id != selected_id:
                return None
            store = await WorkUnitStore.create(envelope, bundle=bundle)
            if store.bundle != bundle:
                return None
            return _SelectedBundleObservation(
                state=state,
                records=await store.load_records(),
                final_artifacts=await store.observe_final_artifacts(),
            )
        except (BundleLifecycleError, OSError, RuntimeError, ValueError):
            return None


async def execute_full_real_release(
    scenario: ReleaseScenario,
    invocation: ReleaseInvocation,
    *,
    environ: Mapping[str, str],
    workspace,
) -> ReleaseAttempt:
    started_at = time.monotonic()
    environment = preflight_release_environment(environ=environ)
    credential_names = {
        "deepseek": "DEEPSEEK_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
    }
    app_config = _app_config(environment.model_provider, environ[credential_names[environment.model_provider]])
    model = app_config.models[0]
    tracker = _UsageTracker(model_id=f"{environment.model_provider}/{model.model}")
    web = _LiveWebSearch(environ["TAVILY_API_KEY"], allowed_source_urls=scenario.declared_source_urls)
    attempt_root = await asyncio.to_thread(_release_attempt_root, workspace, invocation.run_id)

    def failed(code: str) -> ReleaseAttempt:
        return ReleaseAttempt(
            outcome=None,
            error_code=code,
            wall_time_seconds=time.monotonic() - started_at,
            input_tokens=tracker.input_tokens or None,
            output_tokens=tracker.output_tokens or None,
            tool_calls=web.calls,
            response_shapes=tuple(tracker.response_shapes[-16:]),
        )

    try:
        with _LiveAdapter(attempt_root, app_config, identity=invocation) as adapter:
            recipe = ResearchGraphRecipe.all_real(
                node_agent_bridge_factory=_BridgeFactory(
                    focused_node=None,
                    tracker=tracker,
                    web=web,
                    web_source_urls_by_policy=_release_source_urls_by_policy(scenario),
                ),
            )
            graph_executor = BundleGraphExecutor(recipe=recipe)
            release = ReleaseBundleExecutionAdapter(
                adapter=adapter,
                graph_executor=graph_executor,
                invocation=invocation,
            )
            question = HumanMessage(content=scenario.request_text, id="release-start")
            start_call = _tool_call("start", "release-start-call")
            started = await release.control(
                action="start",
                messages=[question, start_call],
                tool_call_id="release-start-call",
            )
            if not isinstance(started, Command):
                return failed(f"start:{started.get('code', 'invalid')}")
            start_control, hitl1 = _command_payload(started)
            bundle_id = _selected_bundle_id(start_control)
            if bundle_id is None:
                return failed("start:bundle_id_missing")
            if not _is_complete_hitl1_interaction(hitl1):
                return failed("start:hitl1_interaction_missing")

            confirmation_response = _response(
                str(hitl1["request_id"]),
                "release-confirmation",
                kind="text",
                value=scenario.confirmation_text,
            )
            first_resume_call = _tool_call("resume", "release-resume-1", bundle_id)
            first_resume = await release.control(
                action="resume",
                bundle_id=bundle_id,
                messages=[question, confirmation_response, first_resume_call],
                tool_call_id="release-resume-1",
            )
            if not isinstance(first_resume, Command):
                return failed(_release_control_failure_code("first_resume", first_resume))
            first_resume_control, hitl2 = _command_payload(first_resume)
            if not _is_hitl2_proceed_interaction(first_resume_control, hitl2):
                return failed("first_resume:hitl2_interaction_missing")

            proceed = _response(str(hitl2["request_id"]), "release-proceed", kind="option", value="proceed")
            second_resume_call = _tool_call("resume", "release-resume-2", bundle_id)
            completed = await release.control(
                action="resume",
                bundle_id=bundle_id,
                messages=[question, confirmation_response, proceed, second_resume_call],
                tool_call_id="release-resume-2",
            )
            if not isinstance(completed, dict):
                return failed("second_resume:suspended")
            if completed.get("bundle_id") != bundle_id:
                return failed("second_resume:bundle_result_mismatch")

            observation = await release.observe(bundle_id=bundle_id)
            if observation is None:
                return failed("selected_bundle_unavailable")
            records = observation.records
            final_artifacts = observation.final_artifacts
            if final_artifacts is None:
                return failed("selected_bundle_final_artifacts_missing")
            report_bytes, citation_bytes = final_artifacts
            try:
                report_text = report_bytes.decode("utf-8")
                citation_payload = json.loads(citation_bytes)
            except (UnicodeDecodeError, json.JSONDecodeError):
                return failed("selected_bundle_final_artifacts_invalid")
            claims = citation_payload.get("claims") if isinstance(citation_payload, dict) else None
            bindings = (
                {
                    str(claim): tuple(str(ref) for ref in value.get("backing_refs", ()))
                    for claim, value in claims.items()
                    if isinstance(value, Mapping)
                }
                if isinstance(claims, Mapping)
                else {}
            )
            accepted = tuple(record.record_hash for record in records)
            citation_evidence = _citation_source_evidence(
                accepted_submission_refs=accepted,
                citation_bindings=bindings,
                records=records,
                declared_source_urls=scenario.declared_source_urls,
            )
            trace = observation.state.execution_trace

            shutil.rmtree(attempt_root, ignore_errors=True)
            outcome = ReleaseOutcome(
                invocation=invocation,
                bundle_id=bundle_id,
                terminal_status=(
                    observation.state.terminal_status.value if observation.state.terminal_status is not None else ""
                ),
                lifecycle_trace=trace,
                accepted_submission_refs=accepted,
                artifacts=scenario.required_artifacts,
                citation_bindings=bindings,
                confirmation_traversed=True,
                report_nonempty=bool(report_text.strip()),
                report_contains_chinese=bool(re.search(r"[\u3400-\u9fff]", report_text)),
                declared_source_set_id=scenario.declared_source_set_id,
                declared_source_set_only=citation_evidence.declared_source_set_only,
                distinct_source_count=citation_evidence.distinct_source_count,
                contained=True,
                cleaned_up=not attempt_root.exists(),
            )
            return ReleaseAttempt(
                outcome=outcome,
                error_code=None,
                wall_time_seconds=time.monotonic() - started_at,
                input_tokens=tracker.input_tokens or None,
                output_tokens=tracker.output_tokens or None,
                tool_calls=web.calls,
                response_shapes=tuple(tracker.response_shapes[-16:]),
            )
    finally:
        shutil.rmtree(attempt_root, ignore_errors=True)


__all__ = [
    "RELEASE_SCENARIO",
    "ReleaseAcceptanceFailure",
    "ReleaseAttempt",
    "ReleaseBundleExecutionAdapter",
    "ReleaseInvocation",
    "ReleaseOutcome",
    "ReleasePreflightError",
    "ReleaseReport",
    "ReleaseRunner",
    "_release_control_failure_code",
    "execute_full_real_release",
    "new_release_invocation",
    "preflight_release_environment",
]
