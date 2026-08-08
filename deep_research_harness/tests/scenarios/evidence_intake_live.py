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
from pathlib import Path

from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.graph.nodes.wave0 import NODE_SPEC as WAVE0_NODE_SPEC
from deerflow_deep_research.graph.nodes.wave1 import NODE_SPEC as WAVE1_NODE_SPEC
from deerflow_deep_research.runtime.projection import project_research_scope
from deerflow_deep_research.runtime.research import (
    RuntimeNodeDependencyResolver,
    _build_wave0_capabilities,
    _build_wave1_capabilities,
)
from tests.scenarios import canaries
from tests.scenarios.evidence_intake_calibration import (
    build_evidence_intake_request,
    evidence_intake_case_requires_web,
    parse_evidence_intake_candidate,
)
from tests.scenarios.intake_planning_calibration import CalibrationCase
from tests.scenarios.live import (
    MODEL_CREDENTIALS,
    LiveAttempt,
    LiveOutcome,
    LiveRubricResult,
    LiveScenario,
    LiveScenarioReport,
    LiveScenarioRunner,
    RubricDisposition,
    preflight_live_environment,
)


def evidence_intake_live_scenario(case: CalibrationCase) -> LiveScenario:
    """Project one evidence-intake case to its declared direct bridge seam."""

    requires_web = evidence_intake_case_requires_web(case)
    return LiveScenario(
        scenario_id=case.case_id,
        requirement_ids=("EVH-019", "WAN-008" if case.branch_id.startswith("wave0/") else "WON-008"),
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
        hard_invariants=("branch_bound", "declared_tool_window", "production_candidate_parser"),
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
    environment = preflight_live_environment(environ=environ, require_web=requires_web)
    credential_name = next(
        name for name, provider in MODEL_CREDENTIALS.items() if provider == environment.model_provider
    )
    app_config = canaries._app_config(environment.model_provider, environ[credential_name])
    model = app_config.models[0]
    tracker = canaries._UsageTracker(model_id=f"{environment.model_provider}/{model.model}")
    web = canaries._LiveWebSearch(environ["TAVILY_API_KEY"]) if requires_web else None
    adapter = canaries._LiveAdapter(workspace / case.case_id, app_config)
    try:
        graph_context = project_research_scope(adapter.envelope, bundle=adapter.identity.bundle_ref)
        is_wave0 = case.branch_id.startswith("wave0/")
        node_spec = WAVE0_NODE_SPEC if is_wave0 else WAVE1_NODE_SPEC
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
        dependencies = RuntimeNodeDependencyResolver(graph_context, capabilities).resolve(
            logical_name=node_spec.logical_name,
            attempt_id="evidence-intake-calibration",
            policy=node_spec.policy,
        )
        request = build_evidence_intake_request(case)
        result = await capabilities.run_agent(context=dependencies.agent_context, request=request)
        tool_window_valid = (
            request.tools_enabled is requires_web
            and request.minimum_tool_calls <= (web.calls if web is not None else 0)
            and (request.tool_call_limit is None or (web.calls if web is not None else 0) <= request.tool_call_limit)
        )
        if result.finish_reason is not NodeFinishReason.SUCCESS or not tool_window_valid:
            raise ValueError("evidence_intake_live_hard_invariant_failed")
        rubric = assess_evidence_intake_candidate(case, result.summary)
        return LiveAttempt(
            outcome=LiveOutcome(
                route="candidate-evaluated",
                values={
                    "identity": {
                        "thread_id": adapter.identity.thread_id,
                        "run_id": adapter.identity.run_id,
                        "bundle_id": adapter.identity.bundle_id,
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
            diagnostics="selected evidence-intake branch candidate evaluated",
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
            diagnostics="selected evidence-intake branch execution failed",
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
    preflight_live_environment(environ=environ, require_web=evidence_intake_case_requires_web(case))

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
