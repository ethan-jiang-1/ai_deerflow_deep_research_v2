"""Selected direct-bridge runner for the bounded evidence-judgment corpus.

@impl EVH-020
@impl EVH-021
"""
# ruff: noqa: E501

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Mapping
from pathlib import Path

from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.graph.nodes.readiness import NODE_SPEC as READINESS_NODE_SPEC
from deerflow_deep_research.graph.nodes.wave1 import NODE_SPEC as WAVE1_NODE_SPEC
from deerflow_deep_research.graph.nodes.wave2_synthesis import NODE_SPEC as WAVE2_NODE_SPEC
from deerflow_deep_research.runtime.projection import project_research_scope
from deerflow_deep_research.runtime.research import (
    RuntimeNodeDependencyResolver,
    _build_readiness_capabilities,
    _build_wave1_capabilities,
    _build_wave2_synthesis_capabilities,
)
from tests.scenarios import canaries
from tests.scenarios.evidence_judgment_calibration import (
    build_evidence_judgment_request,
    evidence_judgment_case_requires_web,
    parse_evidence_judgment_candidate,
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


def evidence_judgment_live_scenario(case: CalibrationCase) -> LiveScenario:
    requires_web = evidence_judgment_case_requires_web(case)
    return LiveScenario(
        scenario_id=case.case_id,
        requirement_ids=(
            ("EVH-021", "REA-002")
            if case.branch_id == "readiness/critic"
            else ("EVH-020", "WSN-006" if case.branch_id.startswith("wave2-") else "TEL-006")
        ),
        entrypoint="direct-model-and-web-node-agent-bridge" if requires_web else "direct-model-node-agent-bridge",
        preconditions={
            "identity": "unique-per-invocation",
            "branch_id": case.branch_id,
            "require_web": requires_web,
            "max_attempts": 1,
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


def assess_evidence_judgment_candidate(case: CalibrationCase, summary: str) -> LiveRubricResult:
    candidate = parse_evidence_judgment_candidate(case, summary)
    rendered = json.dumps(candidate.model_dump(mode="json"), ensure_ascii=True, sort_keys=True).lower()
    unsafe = any(token in rendered for token in ("ledger", "gate", "route", "artifact publication"))
    return LiveRubricResult(
        case_id=case.case_id,
        branch_id=case.branch_id,
        criterion_ids=case.criterion_ids,
        disposition=RubricDisposition.LIMITED if unsafe else RubricDisposition.PASS,
        rationale="The typed candidate is bounded by the selected branch rubric."
        if not unsafe
        else "The typed candidate makes an authority claim outside the selected branch rubric.",
    )


async def _execute_case(
    case: CalibrationCase, scenario: LiveScenario, *, environ: Mapping[str, str], workspace: Path
) -> LiveAttempt:
    started = time.monotonic()
    requires_web = evidence_judgment_case_requires_web(case)
    environment = preflight_live_environment(environ=environ, require_web=requires_web)
    credential = next(name for name, provider in MODEL_CREDENTIALS.items() if provider == environment.model_provider)
    app_config = canaries._app_config(environment.model_provider, environ[credential])
    tracker = canaries._UsageTracker(model_id=f"{environment.model_provider}/{app_config.models[0].model}")
    web = canaries._LiveWebSearch(environ["TAVILY_API_KEY"]) if requires_web else None
    adapter = canaries._LiveAdapter(workspace / case.case_id, app_config)
    try:
        context = project_research_scope(adapter.envelope, bundle=adapter.identity.bundle_ref)
        # The selected runner exercises the generated request only, never a node/graph lifecycle.
        capabilities = (
            _build_wave1_capabilities(
                adapter.envelope,
                context,
                canaries._BridgeFactory(focused_node="wave1", tracker=tracker, web=web, scenario=scenario),
            )
            if requires_web
            else _build_readiness_capabilities(
                adapter.envelope,
                context,
                canaries._BridgeFactory(focused_node="readiness", tracker=tracker, web=None, scenario=scenario),
            )
            if case.branch_id == "readiness/critic"
            else _build_wave2_synthesis_capabilities(
                adapter.envelope,
                context,
                canaries._BridgeFactory(focused_node="wave2_synthesis", tracker=tracker, web=None, scenario=scenario),
            )
        )
        node_spec = (
            WAVE1_NODE_SPEC
            if requires_web
            else READINESS_NODE_SPEC
            if case.branch_id == "readiness/critic"
            else WAVE2_NODE_SPEC
        )
        dependencies = RuntimeNodeDependencyResolver(context, capabilities).resolve(
            logical_name=node_spec.logical_name, attempt_id="evidence-judgment-calibration", policy=node_spec.policy
        )
        request = build_evidence_judgment_request(case)
        result = await capabilities.run_agent(context=dependencies.agent_context, request=request)
        tool_calls = web.calls if web is not None else 0
        if (
            result.finish_reason is not NodeFinishReason.SUCCESS
            or tool_calls < request.minimum_tool_calls
            or (request.tool_call_limit is not None and tool_calls > request.tool_call_limit)
        ):
            raise ValueError("evidence_judgment_live_hard_invariant_failed")
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
            tool_calls=tool_calls,
            wall_time_seconds=time.monotonic() - started,
            diagnostics="selected evidence-judgment branch candidate evaluated",
            rubric_result=assess_evidence_judgment_candidate(case, result.summary),
        )
    except Exception:
        return LiveAttempt(
            outcome=None,
            error_code="evidence_judgment_branch_execution_failed",
            model_id=tracker.model_id,
            tool_ids=("tavily/web_search",) if web is not None else (),
            input_tokens=tracker.input_tokens or None,
            output_tokens=tracker.output_tokens or None,
            cost_usd=None,
            tool_calls=web.calls if web is not None else 0,
            wall_time_seconds=time.monotonic() - started,
            diagnostics="selected evidence-judgment branch execution failed",
            rubric_result=None,
        )
    finally:
        canaries.reset_sandbox_provider()


async def run_evidence_judgment_calibration(
    case: CalibrationCase, *, environ: Mapping[str, str], workspace: Path
) -> LiveScenarioReport:
    scenario = evidence_judgment_live_scenario(case)
    preflight_live_environment(environ=environ, require_web=evidence_judgment_case_requires_web(case))

    async def execute(_scenario: LiveScenario) -> LiveAttempt:
        return await _execute_case(case, scenario, environ=environ, workspace=workspace)

    return await asyncio.wait_for(
        LiveScenarioRunner(executor=execute, max_attempts=1).run(scenario), timeout=float(case.timeout_seconds)
    )


__all__ = ["assess_evidence_judgment_candidate", "evidence_judgment_live_scenario", "run_evidence_judgment_calibration"]
