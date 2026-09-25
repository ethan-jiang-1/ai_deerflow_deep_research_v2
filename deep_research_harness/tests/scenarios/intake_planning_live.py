"""Selected live runner for the intake and planning calibration corpus.

This is test-only evidence code. It calls one existing zero-tool branch at a
time and never hands a candidate to a profile, topic, checkpoint, or route
owner.

@impl EVH-018
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Mapping
from pathlib import Path

from deerflow_deep_research.domain.context import SelectedBundleContext
from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.graph.nodes.hitl1 import NODE_SPEC as HITL1_NODE_SPEC
from deerflow_deep_research.graph.nodes.topic_planning import NODE_SPEC as TOPIC_PLANNING_NODE_SPEC
from deerflow_deep_research.runtime.projection import project_research_scope
from deerflow_deep_research.runtime.research import (
    RuntimeNodeDependencyResolver,
    _build_hitl1_capabilities,
    _build_topic_planning_capabilities,
)
from tests.scenarios import canaries
from tests.scenarios.intake_planning_calibration import (
    CalibrationCase,
    build_calibration_request,
    calibration_planner_inputs,
    parse_calibration_candidate,
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

_EXTERNAL_FACT_MARKERS = ("http://", "https://", "citation", "according to")


def calibration_live_scenario(case: CalibrationCase) -> LiveScenario:
    """Project a typed corpus case into one selected live invocation boundary."""

    return LiveScenario(
        scenario_id=case.case_id,
        requirement_ids=("EVH-018", "HIN-012" if case.branch_id.startswith("hitl1/") else "TOP-007"),
        entrypoint="direct-zero-tool-node-agent-bridge",
        preconditions={
            "identity": "unique-per-invocation",
            "branch_id": case.branch_id,
            "require_web": False,
            "max_attempts": case.max_attempts,
            "max_model_calls": case.max_model_calls,
            "max_tool_calls": case.max_tool_calls,
            "max_total_tokens": case.max_total_tokens,
            "timeout_seconds": case.timeout_seconds,
        },
        live_requirements=("model",),
        expected=LiveOutcome(route="candidate-evaluated"),
        hard_invariants=("zero_tools", "branch_bound", "candidate_boundary"),
        metrics=("accepted-authority-count",),
    )


def _candidate_text(candidate: object) -> str:
    model_dump = getattr(candidate, "model_dump", None)
    if not callable(model_dump):
        return ""
    return json.dumps(model_dump(mode="json"), ensure_ascii=True, sort_keys=True).lower()


def _semantic_intent(candidate: object) -> str:
    intent = getattr(candidate, "intent", None)
    return str(getattr(intent, "value", intent))


def _plan_is_decision_ready(case: CalibrationCase, candidate: object) -> bool:
    topics = getattr(candidate, "topics", ())
    if not topics:
        return False
    inputs = calibration_planner_inputs(case)
    remaining = set(inputs.coverage_questions)
    scopes: set[str] = set()
    for topic in topics:
        bindings = tuple(getattr(topic, "must_answer_bindings", ()))
        remaining.difference_update(bindings)
        scope = str(getattr(topic, "scope", "")).strip().lower()
        if not scope or scope in scopes:
            return False
        scopes.add(scope)
    return not remaining


def assess_calibration_candidate(case: CalibrationCase, summary: str) -> LiveRubricResult:
    """Return a bounded judgment disposition without asserting production acceptance."""

    try:
        candidate = parse_calibration_candidate(case, summary)
    except (TypeError, ValueError):
        return LiveRubricResult(
            case_id=case.case_id,
            branch_id=case.branch_id,
            criterion_ids=case.criterion_ids,
            disposition=RubricDisposition.INCONCLUSIVE,
            rationale="The successful invocation did not yield an admissible typed candidate for the declared rubric.",
        )

    candidate_text = _candidate_text(candidate)
    no_external_fact = not any(marker in candidate_text for marker in _EXTERNAL_FACT_MARKERS)
    if case.branch_id.startswith("hitl1/brief"):
        decision_ready = bool(getattr(candidate, "brief_summary", "")) and bool(getattr(candidate, "must_answer", ()))
        case_terms = {"battery", "storage"}
        faithful = bool(case_terms & set(candidate_text.replace('"', " ").split()))
        satisfied = decision_ready and faithful and no_external_fact
    elif case.branch_id.startswith("hitl1/semantic-intake"):
        expected_intent = "clarify" if case.risk.value == "highest-risk" else "accept_current_proposal"
        satisfied = _semantic_intent(candidate) == expected_intent
    else:
        satisfied = _plan_is_decision_ready(case, candidate) and no_external_fact

    return LiveRubricResult(
        case_id=case.case_id,
        branch_id=case.branch_id,
        criterion_ids=case.criterion_ids,
        disposition=RubricDisposition.PASS if satisfied else RubricDisposition.LIMITED,
        rationale=(
            "Every declared criterion was assessable and satisfied."
            if satisfied
            else "The candidate was assessable but did not satisfy every declared criterion."
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
    environment = preflight_live_environment(environ=environ, require_web=False)
    credential_name = next(
        name for name, provider in MODEL_CREDENTIALS.items() if provider == environment.model_provider
    )
    app_config = canaries._app_config(environment.model_provider, environ[credential_name])
    model = app_config.models[0]
    tracker = canaries._UsageTracker(model_id=f"{environment.model_provider}/{model.model}")
    adapter = canaries._LiveAdapter(workspace / case.case_id, app_config)
    try:
        graph_context = project_research_scope(adapter.envelope, bundle=adapter.identity.bundle_ref)
        # The bridge refuses to run without bundle attribution (the same
        # selected_bundle contract the graph runtime supplies in production).
        selected_bundle = SelectedBundleContext(bundle=adapter.identity.bundle_ref)
        if case.branch_id.startswith("hitl1/"):
            capabilities = _build_hitl1_capabilities(
                adapter.envelope,
                graph_context,
                canaries._BridgeFactory(focused_node=None, tracker=tracker, web=None, scenario=scenario),
            )
            dependencies = RuntimeNodeDependencyResolver(
                graph_context, capabilities, selected_bundle=selected_bundle
            ).resolve(
                logical_name="hitl1",
                attempt_id="calibration-hitl1",
                policy=HITL1_NODE_SPEC.policy,
            )
        else:
            capabilities = _build_topic_planning_capabilities(
                adapter.envelope,
                graph_context,
                canaries._BridgeFactory(focused_node=None, tracker=tracker, web=None, scenario=scenario),
            )
            dependencies = RuntimeNodeDependencyResolver(
                graph_context, capabilities, selected_bundle=selected_bundle
            ).resolve(
                logical_name="topic_planning",
                attempt_id="calibration-topic-planning",
                policy=TOPIC_PLANNING_NODE_SPEC.policy,
            )
        result = await capabilities.run_agent(
            context=dependencies.agent_context,
            request=build_calibration_request(case),
        )
        if result.finish_reason is not NodeFinishReason.SUCCESS:
            return LiveAttempt(
                outcome=None,
                error_code="calibration_candidate_unavailable",
                model_id=tracker.model_id,
                tool_ids=(),
                input_tokens=tracker.input_tokens or None,
                output_tokens=tracker.output_tokens or None,
                cost_usd=None,
                tool_calls=0,
                wall_time_seconds=time.monotonic() - started_at,
                diagnostics="selected calibration branch did not return a candidate",
                rubric_result=None,
            )
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
            wall_time_seconds=time.monotonic() - started_at,
            diagnostics="selected zero-tool calibration candidate evaluated",
            rubric_result=assess_calibration_candidate(case, result.summary),
        )
    except Exception:
        return LiveAttempt(
            outcome=None,
            error_code="calibration_branch_execution_failed",
            model_id=tracker.model_id,
            tool_ids=(),
            input_tokens=tracker.input_tokens or None,
            output_tokens=tracker.output_tokens or None,
            cost_usd=None,
            tool_calls=0,
            wall_time_seconds=time.monotonic() - started_at,
            diagnostics="selected calibration branch execution failed",
            rubric_result=None,
        )
    finally:
        canaries.reset_sandbox_provider()


async def run_intake_planning_calibration(
    case: CalibrationCase,
    *,
    environ: Mapping[str, str],
    workspace: Path,
) -> LiveScenarioReport:
    """Run exactly one credentialed case after strict model preflight."""

    scenario = calibration_live_scenario(case)
    preflight_live_environment(environ=environ, require_web=False)

    async def execute(_scenario: LiveScenario) -> LiveAttempt:
        return await _execute_case(case, scenario, environ=environ, workspace=workspace)

    return await asyncio.wait_for(
        LiveScenarioRunner(executor=execute, max_attempts=case.max_attempts).run(scenario),
        timeout=float(case.timeout_seconds),
    )


__all__ = [
    "assess_calibration_candidate",
    "calibration_live_scenario",
    "run_intake_planning_calibration",
]
