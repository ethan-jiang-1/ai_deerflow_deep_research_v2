"""Selected live runner for the isolated Wave0/Wave1 evidence-intake corpus.

This test-only runner invokes a single generated branch request through the real
node-agent bridge. It evaluates the returned candidate without submitting it to a
work-unit controller, review materializer, ledger, gate, or route owner.

@impl EVH-019
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from deerflow_deep_research.domain.context import SelectedBundleContext
from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.domain.run_observation import (
    ExecutionProfileEvidence,
    FinalResponseShape,
    ObservationInspectability,
    RunEventCategory,
    classify_final_response_shape,
)
from deerflow_deep_research.graph.nodes.wave0 import NODE_SPEC as WAVE0_NODE_SPEC
from deerflow_deep_research.graph.nodes.wave1 import NODE_SPEC as WAVE1_NODE_SPEC
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.projection import project_research_scope
from deerflow_deep_research.runtime.research import (
    RuntimeNodeDependencyResolver,
    _build_wave0_capabilities,
    _build_wave1_capabilities,
)
from deerflow_deep_research.runtime.run_observation import RunObservationRecorder, RunObservationStore
from scripts._demo_core import DemoAppConfig, resolve_real_demo_model_profile
from tests.scenarios import canaries
from tests.scenarios.evidence_intake_calibration import (
    build_evidence_intake_request,
    evidence_intake_case_requires_web,
    parse_evidence_intake_candidate,
)
from tests.scenarios.intake_planning_calibration import CalibrationCase
from tests.scenarios.live import (
    LiveAttempt,
    LiveOutcome,
    LivePreflightError,
    LiveRubricResult,
    LiveScenario,
    LiveScenarioReport,
    LiveScenarioRunner,
    RubricDisposition,
)


@dataclass(frozen=True)
class _CalibrationBundleContext:
    bundle_id: str
    selected_bundle: SelectedBundleContext
    recorder: RunObservationRecorder
    journal_store: RunObservationStore


def _explicit_profile(environ: Mapping[str, str], *, requires_web: bool):
    """Resolve one trusted profile before creating a Bundle or bridge dependency."""

    profile = resolve_real_demo_model_profile(environ)
    if profile is None:
        raise LivePreflightError(
            "live_explicit_profile_missing",
            "set DEERFLOW_DEMO_MODEL and its matching supported credential before selecting the live lane",
        )
    if requires_web and not environ.get("TAVILY_API_KEY", "").strip():
        raise LivePreflightError(
            "live_web_credentials_missing",
            "set TAVILY_API_KEY before selecting a live web scenario",
        )
    return profile


async def _admit_calibration_bundle(
    *,
    adapter: object,
    profile: object,
    case: CalibrationCase,
    node_name: str,
) -> _CalibrationBundleContext:
    """Create the selected Bundle and its Journal before resolving a node dependency."""

    envelope = adapter.envelope  # type: ignore[union-attr]
    evidence = profile.evidence  # type: ignore[union-attr]
    if not isinstance(evidence, ExecutionProfileEvidence):
        raise TypeError("execution_profile_evidence_required")
    lifecycle = BundleLifecycle(workspace_host_path=envelope.workspace_host_path)
    bundle = await lifecycle.start(
        scope=(envelope.effective_user_id, envelope.outer_thread_id),
        request_text=f"Run selected evidence-intake calibration: {case.case_id}",
    )
    selected_bundle = SelectedBundleContext(bundle=bundle)
    journal_store = RunObservationStore(
        bundle_root=lifecycle.private_root(bundle),
        bundle_id=bundle.bundle_id.value,
    )
    recorder = RunObservationRecorder(
        store=journal_store,
        bundle_id=bundle.bundle_id.value,
        execution_profile=evidence,
    )
    view = await recorder.establish(generation=0, phase=node_name, durability="restart_durable")
    if view.inspectability is not ObservationInspectability.AVAILABLE:
        raise ValueError("evidence_intake_bundle_journal_unavailable")
    return _CalibrationBundleContext(
        bundle_id=bundle.bundle_id.value,
        selected_bundle=selected_bundle,
        recorder=recorder,
        journal_store=journal_store,
    )


def _validation_stage(case: CalibrationCase) -> str | None:
    if case.branch_id.endswith("/worker"):
        return "initial"
    if case.branch_id.endswith("/repair"):
        return "repair"
    return None


def _canonical_validation_code(case: CalibrationCase, error: ValueError) -> str:
    code = str(error)
    if case.branch_id.startswith("wave0/"):
        return (
            code
            if code in {"wave0_worker_output_empty", "wave0_worker_output_json_invalid"}
            else "wave0_worker_output_invalid"
        )
    if case.branch_id.startswith("wave1/") and code.startswith("wave1_") and code.replace("_", "").isalnum():
        return code
    return "wave1_worker_output_invalid"


def evidence_intake_live_scenario(case: CalibrationCase) -> LiveScenario:
    """Project one evidence-intake case to its declared direct bridge seam."""

    requires_web = evidence_intake_case_requires_web(case)
    return LiveScenario(
        scenario_id=case.case_id,
        requirement_ids=("EVH-030", "WAN-012" if case.branch_id.startswith("wave0/") else "WON-012"),
        entrypoint="direct-model-and-web-node-agent-bridge" if requires_web else "direct-model-node-agent-bridge",
        preconditions={
            "identity": "unique-per-invocation",
            "branch_id": case.branch_id,
            "require_web": requires_web,
            "max_attempts": case.max_attempts,
            "max_model_calls": case.max_model_calls,
            "max_tool_calls": case.max_tool_calls,
            "max_total_tokens": case.max_total_tokens,
            "timeout_seconds": case.timeout_seconds,
        },
        live_requirements=("model", "web_search") if requires_web else ("model",),
        expected=LiveOutcome(route="candidate-evaluated"),
        hard_invariants=(
            "branch_bound",
            "explicit_profile_bound",
            "bundle_bound",
            "declared_tool_window",
            "production_candidate_parser",
        ),
        metrics=("accepted-authority-count",),
    )


def assess_evidence_intake_candidate(case: CalibrationCase, summary: str) -> LiveRubricResult:
    """Assess a parsed candidate only; parser/validator failure is not a rubric result."""

    candidate = parse_evidence_intake_candidate(case, summary)
    rendered = json.dumps(candidate.model_dump(mode="json"), ensure_ascii=True, sort_keys=True).lower()
    forbidden = ("ledger", "gate", "route", "accepted evidence", "artifact publication")
    has_authority_claim = any(marker in rendered for marker in forbidden)
    is_empty = rendered in {"{}", "[]", '""'}
    return LiveRubricResult(
        case_id=case.case_id,
        branch_id=case.branch_id,
        criterion_ids=case.criterion_ids,
        disposition=RubricDisposition.LIMITED if has_authority_claim or is_empty else RubricDisposition.PASS,
        rationale=(
            "The typed candidate was structurally valid but did not satisfy every declared judgment criterion."
            if has_authority_claim or is_empty
            else "The typed candidate was structurally valid and satisfied the bounded branch rubric."
        ),
    )


async def _execute_case(
    case: CalibrationCase,
    scenario: LiveScenario,
    *,
    environ: Mapping[str, str],
    workspace: Path,
) -> LiveAttempt:
    started_at = time.monotonic()
    requires_web = evidence_intake_case_requires_web(case)
    profile = _explicit_profile(environ, requires_web=requires_web)
    app_config = DemoAppConfig(models=(profile.model_config,))
    tracker = canaries._UsageTracker(model_id=profile.evidence.profile_id)
    web = canaries._LiveWebSearch(environ["TAVILY_API_KEY"]) if requires_web else None
    adapter = canaries._LiveAdapter(workspace / case.case_id, app_config)
    response_shape: FinalResponseShape | None = None
    validation_codes: tuple[str, ...] = ()
    try:
        is_wave0 = case.branch_id.startswith("wave0/")
        node_spec = WAVE0_NODE_SPEC if is_wave0 else WAVE1_NODE_SPEC
        calibration = await _admit_calibration_bundle(
            adapter=adapter,
            profile=profile,
            case=case,
            node_name=node_spec.logical_name,
        )
        graph_context = project_research_scope(adapter.envelope, bundle=calibration.selected_bundle.bundle)
        capabilities = (
            _build_wave0_capabilities(
                adapter.envelope,
                graph_context,
                canaries._BridgeFactory(focused_node="wave0", tracker=tracker, web=web, scenario=scenario),
            )
            if is_wave0
            else _build_wave1_capabilities(
                adapter.envelope,
                graph_context,
                canaries._BridgeFactory(focused_node="wave1", tracker=tracker, web=web, scenario=scenario),
            )
        )
        dependencies = RuntimeNodeDependencyResolver(
            graph_context,
            capabilities,
            selected_bundle=calibration.selected_bundle,
        ).resolve(
            logical_name=node_spec.logical_name,
            attempt_id="evidence-intake-calibration",
            policy=node_spec.policy,
        )
        if (
            dependencies.selected_bundle != calibration.selected_bundle
            or dependencies.agent_context.bundle_context is None
        ):
            raise ValueError("evidence_intake_selected_bundle_context_missing")
        request = build_evidence_intake_request(case)
        result = await capabilities.run_agent(context=dependencies.agent_context, request=request)
        tool_window_valid = (
            request.tools_enabled is requires_web
            and request.minimum_tool_calls <= (web.calls if web is not None else 0)
            and (request.tool_call_limit is None or (web.calls if web is not None else 0) <= request.tool_call_limit)
        )
        if result.finish_reason is not NodeFinishReason.SUCCESS or not tool_window_valid:
            raise ValueError("evidence_intake_live_hard_invariant_failed")
        stage = _validation_stage(case)
        if stage is not None:
            response_shape = classify_final_response_shape(result.summary)
            try:
                parse_evidence_intake_candidate(case, result.summary)
            except ValueError as error:
                validation_codes = (_canonical_validation_code(case, error),)
                await calibration.recorder.record(
                    category=RunEventCategory.VALIDATION,
                    phase=node_spec.logical_name,
                    work_id=case.case_id,
                    attempt_id="evidence-intake-calibration",
                    validation_stage=stage,
                    validation_codes=validation_codes,
                    response_shape=response_shape,
                )
                raise
            await calibration.recorder.record(
                category=RunEventCategory.VALIDATION,
                phase=node_spec.logical_name,
                work_id=case.case_id,
                attempt_id="evidence-intake-calibration",
                validation_stage=stage,
                validation_codes=(),
                response_shape=response_shape,
            )
            rubric = assess_evidence_intake_candidate(case, result.summary)
        else:
            rubric = assess_evidence_intake_candidate(case, result.summary)
        inspection = await calibration.journal_store.inspect(bundle_id=calibration.bundle_id)
        if (
            inspection.summary is None
            or inspection.summary.execution_profile != profile.evidence
            or inspection.events[0].execution_profile != profile.evidence
        ):
            raise ValueError("evidence_intake_profile_journal_mismatch")
        if stage is not None:
            validation_events = tuple(
                event
                for event in inspection.events
                if event.category is RunEventCategory.VALIDATION and event.work_id == case.case_id
            )
            if len(validation_events) != 1 or validation_events[0].response_shape != response_shape:
                raise ValueError("evidence_intake_validation_journal_mismatch")
        return LiveAttempt(
            outcome=LiveOutcome(
                route="candidate-evaluated",
                values={
                    "identity": {
                        "thread_id": adapter.identity.thread_id,
                        "run_id": adapter.identity.run_id,
                        "bundle_id": calibration.bundle_id,
                    }
                },
            ),
            error_code=None,
            model_id=tracker.model_id,
            tool_ids=("tavily/web_search",) if web is not None else (),
            input_tokens=tracker.input_tokens or None,
            output_tokens=tracker.output_tokens or None,
            cost_usd=None,
            tool_calls=web.calls if web is not None else 0,
            wall_time_seconds=time.monotonic() - started_at,
            diagnostics=(
                f"profile={profile.evidence.profile_id} revision={profile.evidence.registry_revision} "
                f"correlation={case.case_id} response_shape={response_shape or 'not_applicable'} "
                f"validation_codes={','.join(validation_codes) or 'none'}"
            ),
            rubric_result=rubric,
        )
    except Exception:
        return LiveAttempt(
            outcome=None,
            error_code="evidence_intake_branch_execution_failed",
            model_id=tracker.model_id,
            tool_ids=("tavily/web_search",) if web is not None else (),
            input_tokens=tracker.input_tokens or None,
            output_tokens=tracker.output_tokens or None,
            cost_usd=None,
            tool_calls=web.calls if web is not None else 0,
            wall_time_seconds=time.monotonic() - started_at,
            diagnostics=(
                f"profile={profile.evidence.profile_id} revision={profile.evidence.registry_revision} "
                f"correlation={case.case_id} response_shape={response_shape or 'not_applicable'} "
                f"validation_codes={','.join(validation_codes) or 'none'} branch execution failed"
            ),
            rubric_result=None,
        )
    finally:
        canaries.reset_sandbox_provider()


async def run_evidence_intake_calibration(
    case: CalibrationCase,
    *,
    environ: Mapping[str, str],
    workspace: Path,
) -> LiveScenarioReport:
    """Run exactly one selected case after strict branch-specific preflight."""

    scenario = evidence_intake_live_scenario(case)
    _explicit_profile(environ, requires_web=evidence_intake_case_requires_web(case))

    async def execute(_scenario: LiveScenario) -> LiveAttempt:
        return await _execute_case(case, scenario, environ=environ, workspace=workspace)

    return await asyncio.wait_for(
        LiveScenarioRunner(executor=execute, max_attempts=case.max_attempts).run(scenario),
        timeout=float(case.timeout_seconds),
    )


__all__ = [
    "assess_evidence_intake_candidate",
    "evidence_intake_live_scenario",
    "run_evidence_intake_calibration",
]
