"""Selected direct-bridge runner for final report composition judgment.

@impl EVH-022
@impl FID-001
@impl FID-003
@impl NAC-009
@impl NOA-013
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Mapping
from pathlib import Path

from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.graph.nodes.final_delivery import NODE_SPEC as FINAL_DELIVERY_NODE_SPEC
from deerflow_deep_research.runtime.projection import project_research_scope
from deerflow_deep_research.runtime.research import (
    RuntimeNodeDependencyResolver,
    _build_final_delivery_capabilities,
    _final_delivery_node_agent_policy,
)
from tests.scenarios import canaries
from tests.scenarios.final_composition_calibration import (
    FinalCompositionCalibrationCase,
    FinalCompositionDisposition,
    assess_final_composition_candidate,
    build_final_composition_request,
)
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


def final_composition_live_scenario(case: FinalCompositionCalibrationCase) -> LiveScenario:
    return LiveScenario(
        scenario_id=case.case_id,
        requirement_ids=("EVH-022", "FID-001", "FID-003", "NAC-009", "NOA-013"),
        entrypoint="direct-model-final-composer-bridge",
        preconditions={
            "identity": "unique-per-invocation",
            "branch_id": case.branch_id,
            "require_web": False,
            "max_attempts": case.max_attempts,
            "max_model_calls": case.max_model_calls,
            "max_tool_calls": case.max_tool_calls,
            "max_total_tokens": case.max_total_tokens,
            "timeout_seconds": case.timeout_seconds,
            "preferred_layout_label": case.preferred_layout_label,
            "authority_scope": "candidate-only",
        },
        live_requirements=("model",),
        expected=LiveOutcome(route="candidate-evaluated"),
        hard_invariants=(
            "production_request_builder",
            "final_delivery_zero_tool_policy",
            "production_candidate_parser_and_admission",
            "deterministic_exact_render_preservation",
            "no_publication_checkpoint_route_or_lifecycle",
        ),
        metrics=("accepted-authority-count",),
    )


def _rubric_result(
    case: FinalCompositionCalibrationCase,
    disposition: FinalCompositionDisposition,
) -> LiveRubricResult:
    rationale = (
        "The assessable candidate matched the labeled preferred layout and deterministic rendering preserved all "
        "declared content bindings."
        if disposition is FinalCompositionDisposition.PASS
        else "The assessable candidate preserved all declared content bindings but used a non-preferred valid layout."
        if disposition is FinalCompositionDisposition.LIMITED
        else "No admitted candidate was available for the declared composition judgment."
    )
    return LiveRubricResult(
        case_id=case.case_id,
        branch_id=case.branch_id,
        criterion_ids=case.criterion_ids,
        disposition=RubricDisposition(disposition.value),
        rationale=rationale,
    )


async def _execute_case(
    case: FinalCompositionCalibrationCase,
    scenario: LiveScenario,
    *,
    environ: Mapping[str, str],
    workspace: Path,
) -> LiveAttempt:
    started = time.monotonic()
    environment = preflight_live_environment(environ=environ, require_web=False)
    credential = next(name for name, provider in MODEL_CREDENTIALS.items() if provider == environment.model_provider)
    app_config = canaries._app_config(environment.model_provider, environ[credential])
    tracker = canaries._UsageTracker(model_id=f"{environment.model_provider}/{app_config.models[0].model}")
    adapter = canaries._LiveAdapter(workspace / case.case_id, app_config)
    try:
        graph_context = project_research_scope(adapter.envelope, bundle=adapter.identity.bundle_ref)
        policy = _final_delivery_node_agent_policy(graph_context)
        if (
            policy.policy_name != "final-delivery-composer"
            or policy.allowed_tool_names
            or policy.write_roots
            or policy.budget.max_model_calls != 1
        ):
            raise ValueError("final_composition_live_policy_invalid")
        capabilities = _build_final_delivery_capabilities(
            adapter.envelope,
            graph_context,
            canaries._BridgeFactory(focused_node="final_delivery", tracker=tracker, web=None, scenario=scenario),
        )
        dependencies = RuntimeNodeDependencyResolver(graph_context, capabilities).resolve(
            logical_name=FINAL_DELIVERY_NODE_SPEC.logical_name,
            attempt_id="final-composition-calibration",
            policy=FINAL_DELIVERY_NODE_SPEC.policy,
        )
        request = build_final_composition_request(case)
        if request.tools_enabled or request.minimum_tool_calls != 0 or request.tool_call_limit is not None:
            raise ValueError("final_composition_live_request_tool_window_invalid")
        result = await capabilities.run_agent(context=dependencies.agent_context, request=request)
        if result.finish_reason is not NodeFinishReason.SUCCESS:
            raise ValueError("final_composition_live_bridge_failed")
        assessment = assess_final_composition_candidate(case, result.summary)
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
            tool_ids=(),
            input_tokens=tracker.input_tokens or None,
            output_tokens=tracker.output_tokens or None,
            cost_usd=None,
            tool_calls=0,
            wall_time_seconds=time.monotonic() - started,
            diagnostics="selected final-composition candidate evaluated without authority invocation",
            rubric_result=_rubric_result(case, assessment.disposition),
        )
    except Exception:
        return LiveAttempt(
            outcome=None,
            error_code="final_composition_candidate_execution_failed",
            model_id=tracker.model_id,
            tool_ids=(),
            input_tokens=tracker.input_tokens or None,
            output_tokens=tracker.output_tokens or None,
            cost_usd=None,
            tool_calls=0,
            wall_time_seconds=time.monotonic() - started,
            diagnostics="selected final-composition candidate was not assessable",
            rubric_result=_rubric_result(case, FinalCompositionDisposition.INCONCLUSIVE),
        )
    finally:
        canaries.reset_sandbox_provider()


async def run_final_composition_calibration(
    case: FinalCompositionCalibrationCase,
    *,
    environ: Mapping[str, str],
    workspace: Path,
) -> LiveScenarioReport:
    scenario = final_composition_live_scenario(case)
    preflight_live_environment(environ=environ, require_web=False)

    async def execute(_scenario: LiveScenario) -> LiveAttempt:
        return await _execute_case(case, scenario, environ=environ, workspace=workspace)

    return await asyncio.wait_for(
        LiveScenarioRunner(executor=execute, max_attempts=case.max_attempts).run(scenario),
        timeout=float(case.timeout_seconds),
    )


__all__ = [
    "final_composition_live_scenario",
    "run_final_composition_calibration",
]
