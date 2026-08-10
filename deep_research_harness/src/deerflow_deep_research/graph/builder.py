"""Request-independent Deep Research StateGraph recipe.

@impl REG-001
@impl REG-002
@impl REG-006
@impl GAK-003
@impl GAK-005
@impl WFO-001
"""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime

from deerflow_deep_research.domain.gate import GateDefinition
from deerflow_deep_research.domain.invocation import GraphInvocationContext
from deerflow_deep_research.domain.lifecycle import LifecycleStatus, make_attempt_id
from deerflow_deep_research.domain.node_spec import NodeCapability, NodeSpec
from deerflow_deep_research.domain.publication import FINAL_DELIVERY_GATE_VIEW_KEY, FinalDeliveryGateView
from deerflow_deep_research.domain.run_observation import RunEventCategory
from deerflow_deep_research.domain.state import WORK_UNIT_GATE_PREVIEW_FIELDS, ResearchState, preview_work_unit_update
from deerflow_deep_research.domain.synthesis import WAVE2_GATE_PREVIEW_KEY, Wave2GatePreview
from deerflow_deep_research.domain.wave1 import WAVE1_GATE_REVIEW_KEY, Wave1GateReview
from deerflow_deep_research.domain.work_units import (
    WORK_UNIT_GATE_VIEW_KEY,
    WorkUnitGateView,
    validate_wrapper_gate_view,
)
from deerflow_deep_research.graph.implementation_map import (
    AdapterKind,
    NodeAdapter,
    resolve_implementations,
    validate_gate_definitions,
)
from deerflow_deep_research.graph.nodes.gate_adapter import (
    all_real_gate_defs,
    evaluate_gate_for_node,
)
from deerflow_deep_research.graph.registry import load_research_node_specs
from deerflow_deep_research.graph.topology import LOGICAL_NODES


async def _record_node_event(
    context: GraphInvocationContext,
    *,
    category: RunEventCategory,
    phase: str,
    attempt_id: str,
    outcome: str,
    failure_category: str | None = None,
    worker_failure_category: str | None = None,
) -> None:
    if context.event_recorder is None:
        return
    try:
        await context.event_recorder.record(
            category=category,
            phase=phase,
            attempt_id=attempt_id,
            outcome=outcome,
            failure_category=failure_category,
            worker_failure_category=worker_failure_category,
        )
    except Exception:
        # Observation must never change graph/checkpoint/route authority.
        return


def _node_wrapper(
    logical_name: str,
    spec: NodeSpec,
    adapter: NodeAdapter,
    gate_defs: Mapping[str, GateDefinition],
):
    async def run(state: ResearchState, runtime: Runtime[GraphInvocationContext]) -> dict[str, Any]:
        factory = adapter.factory
        is_real_adapter = adapter.kind is AdapterKind.REAL
        context = runtime.context
        current_attempt = make_attempt_id(state, logical_name)
        await _record_node_event(
            context,
            category=RunEventCategory.NODE,
            phase=logical_name,
            attempt_id=current_attempt,
            outcome="started",
        )
        dependencies = context.dependency_resolver.resolve(
            logical_name=logical_name,
            attempt_id=current_attempt,
            policy=spec.policy,
        )
        declares_work_units = NodeCapability.WORK_UNIT_CONTROLLER in spec.capabilities
        if declares_work_units and context.work_units is None:
            raise ValueError("work_unit_capability_missing")
        if not declares_work_units and dependencies.work_units is not None:
            raise ValueError("work_unit_capability_undeclared")
        if declares_work_units:
            dependencies = replace(dependencies, work_units=context.work_units)
        if context.event_recorder is not None:
            dependencies = replace(dependencies, event_recorder=context.event_recorder)
        declares_bootstrap = NodeCapability.BOOTSTRAP_BUNDLE in spec.capabilities
        if declares_bootstrap and is_real_adapter:
            # The bootstrap store is a real-adapter filesystem capability. Fixture
            # adapters are supplied outside the production package and do not receive it.
            if context.bootstrap_bundle is None:
                raise ValueError("bootstrap_bundle_capability_missing")
            dependencies = replace(dependencies, bootstrap_bundle=context.bootstrap_bundle)
        elif dependencies.bootstrap_bundle is not None:
            raise ValueError("bootstrap_bundle_capability_undeclared")
        declares_request_bundle = NodeCapability.REQUEST_BUNDLE in spec.capabilities
        if declares_request_bundle and is_real_adapter:
            if context.request_bundle is None:
                raise ValueError("request_bundle_capability_missing")
            dependencies = replace(dependencies, request_bundle=context.request_bundle)
        elif dependencies.request_bundle is not None:
            raise ValueError("request_bundle_capability_undeclared")
        declares_synthesis_bundle = NodeCapability.SYNTHESIS_BUNDLE in spec.capabilities
        if declares_synthesis_bundle and is_real_adapter:
            if context.synthesis_bundle is None:
                raise ValueError("synthesis_bundle_capability_missing")
            dependencies = replace(dependencies, synthesis_bundle=context.synthesis_bundle)
        elif dependencies.synthesis_bundle is not None:
            raise ValueError("synthesis_bundle_capability_undeclared")
        declares_publication_bundle = NodeCapability.PUBLICATION_BUNDLE in spec.capabilities
        if declares_publication_bundle and is_real_adapter:
            if context.publication_bundle is None:
                raise ValueError("publication_bundle_capability_missing")
            dependencies = replace(dependencies, publication_bundle=context.publication_bundle)
        elif dependencies.publication_bundle is not None:
            raise ValueError("publication_bundle_capability_undeclared")
        declares_final_delivery_bundle = NodeCapability.FINAL_DELIVERY_BUNDLE in spec.capabilities
        if declares_final_delivery_bundle and is_real_adapter:
            if context.final_delivery_bundle is None:
                raise ValueError("final_delivery_bundle_capability_missing")
            dependencies = replace(dependencies, final_delivery_bundle=context.final_delivery_bundle)
        elif dependencies.final_delivery_bundle is not None:
            raise ValueError("final_delivery_bundle_capability_undeclared")
        if dependencies.graph_context != context.graph_context:
            raise ValueError("dependency_context_mismatch")
        if dependencies.agent_context.node_name != logical_name:
            raise ValueError("dependency_node_mismatch")
        if dependencies.agent_context.attempt_id != current_attempt:
            raise ValueError("dependency_attempt_mismatch")
        node = factory(dependencies)
        result = node(state)
        result = await result if inspect.isawaitable(result) else result
        result = dict(result)
        has_non_completed_terminal = (
            result.get("terminal_status") is not None
            and result.get("terminal_status") != LifecycleStatus.COMPLETED.value
        )
        await _record_node_event(
            context,
            category=RunEventCategory.TERMINAL if result.get("terminal_status") else RunEventCategory.NODE,
            phase=logical_name,
            attempt_id=current_attempt,
            outcome="completed",
        )

        gate_view = result.pop(WORK_UNIT_GATE_VIEW_KEY, None)
        # Readiness uses the controller's store but owns its route directly; only
        # worker-controller nodes participate in the WorkUnitGateView protocol.
        declares_work_unit_gate_view = declares_work_units and logical_name != "readiness"
        if declares_work_unit_gate_view:
            if not isinstance(gate_view, WorkUnitGateView):
                raise ValueError("work_unit_gate_view_inconsistent")
        elif gate_view is not None:
            raise ValueError("work_unit_gate_view_undeclared")

        wave1_gate_review = result.pop(WAVE1_GATE_REVIEW_KEY, None)
        declares_wave1_review = logical_name == "wave1" and is_real_adapter
        if declares_wave1_review:
            if not has_non_completed_terminal and not isinstance(wave1_gate_review, Wave1GateReview):
                raise ValueError("wave1_gate_review_inconsistent")
            if has_non_completed_terminal and wave1_gate_review is not None:
                raise ValueError("wave1_terminal_gate_review_forbidden")
        elif wave1_gate_review is not None:
            raise ValueError("wave1_gate_review_undeclared")

        wave2_gate_preview = result.pop(WAVE2_GATE_PREVIEW_KEY, None)
        declares_wave2_preview = logical_name == "wave2_synthesis" and is_real_adapter
        if declares_wave2_preview:
            if not has_non_completed_terminal and not isinstance(wave2_gate_preview, Wave2GatePreview):
                raise ValueError("wave2_gate_preview_inconsistent")
            if has_non_completed_terminal and wave2_gate_preview is not None:
                raise ValueError("wave2_terminal_gate_preview_forbidden")
        elif wave2_gate_preview is not None:
            raise ValueError("wave2_gate_preview_undeclared")

        final_delivery_gate_view = result.pop(FINAL_DELIVERY_GATE_VIEW_KEY, None)
        declares_final_delivery_view = logical_name == "final_delivery" and is_real_adapter
        if declares_final_delivery_view:
            if not has_non_completed_terminal and not isinstance(final_delivery_gate_view, FinalDeliveryGateView):
                raise ValueError("final_delivery_gate_view_inconsistent")
            if has_non_completed_terminal and final_delivery_gate_view is not None:
                raise ValueError("final_delivery_terminal_gate_view_forbidden")
            if isinstance(final_delivery_gate_view, FinalDeliveryGateView):
                if final_delivery_gate_view.published_refs is None and "report_refs" in result:
                    raise ValueError("final_delivery_gate_view_publication_inconsistent")
                if final_delivery_gate_view.published_refs is not None and tuple(result.get("report_refs") or ()) != (
                    final_delivery_gate_view.published_refs
                ):
                    raise ValueError("final_delivery_gate_view_publication_inconsistent")
        elif final_delivery_gate_view is not None:
            raise ValueError("final_delivery_gate_view_undeclared")

        # Gate evaluation — delegated to nodes layer (architecture: graph → nodes → engine)
        gate_def = gate_defs.get(logical_name)
        # A real final-delivery gate consumes the current node visit's private view,
        # never checkpointed report refs from an earlier attempt.
        if gate_def is not None and not has_non_completed_terminal:
            gate_state: Mapping[str, Any] = state
            if declares_work_unit_gate_view:
                preview_delta = {key: value for key, value in result.items() if key in WORK_UNIT_GATE_PREVIEW_FIELDS}
                gate_state = preview_work_unit_update(state, preview_delta)
                assert gate_view is not None
                validate_wrapper_gate_view(gate_view, gate_state, phase=logical_name)
                gate_state = {**gate_state, WORK_UNIT_GATE_VIEW_KEY: gate_view}
                if declares_wave1_review:
                    assert isinstance(wave1_gate_review, Wave1GateReview)
                    wave1_gate_review.validate_gate_view(gate_view)
                    gate_state = {**gate_state, WAVE1_GATE_REVIEW_KEY: wave1_gate_review}
            if declares_wave2_preview:
                gate_state = {**gate_state, WAVE2_GATE_PREVIEW_KEY: wave2_gate_preview}
            if declares_final_delivery_view:
                assert isinstance(final_delivery_gate_view, FinalDeliveryGateView)
                gate_state = {**gate_state, FINAL_DELIVERY_GATE_VIEW_KEY: final_delivery_gate_view}
            gate_update = evaluate_gate_for_node(gate_state, logical_name, gate_def)
            overlap = set(result) & set(gate_update)
            if overlap:
                raise ValueError(f"node_gate_write_conflict:{','.join(sorted(overlap))}")
            result = {**result, **gate_update}
        return result

    async def observed_run(state: ResearchState, runtime: Runtime[GraphInvocationContext]) -> dict[str, Any]:
        try:
            return await run(state, runtime)
        except asyncio.CancelledError:
            raise
        except Exception:
            context = runtime.context
            await _record_node_event(
                context,
                category=RunEventCategory.NODE,
                phase=logical_name,
                attempt_id=make_attempt_id(state, logical_name),
                outcome="failed",
                failure_category="internal.unexpected",
                worker_failure_category="unknown",
            )
            raise

    observed_run.__name__ = f"run_{logical_name}"
    return observed_run


def _route(state: ResearchState) -> str:
    route = state.get("route")
    if not isinstance(route, str):
        raise ValueError("typed_route_missing")
    return route


def all_real_gate_definitions() -> Mapping[str, GateDefinition]:
    """Expose the production gate selection through the graph composition layer."""

    return all_real_gate_defs()


def build_research_graph(
    *,
    implementations: Mapping[str, NodeAdapter] | None,
    spec_overrides: Mapping[str, NodeSpec] | None = None,
    gate_defs: Mapping[str, GateDefinition] | None,
) -> StateGraph:
    loaded = dict(load_research_node_specs())
    if spec_overrides:
        unknown = set(spec_overrides) - set(loaded)
        if unknown:
            raise ValueError(f"unknown spec override: {', '.join(sorted(unknown))}")
        loaded.update(spec_overrides)
    if tuple(loaded) != LOGICAL_NODES:
        raise ValueError("research registry order does not match topology")
    adapters = resolve_implementations(loaded, implementations)
    _gate_defs = validate_gate_definitions(adapters, gate_defs)

    builder = StateGraph(ResearchState, context_schema=GraphInvocationContext)
    for logical_name in LOGICAL_NODES:
        builder.add_node(
            logical_name,
            _node_wrapper(logical_name, loaded[logical_name], adapters[logical_name], _gate_defs),
        )

    builder.add_edge(START, "bootstrap")
    builder.add_conditional_edges(
        "bootstrap",
        _route,
        {"needs_input": "hitl1", "profile_complete": "topic_planning", "exhausted": END},
    )
    builder.add_conditional_edges(
        "hitl1",
        _route,
        {"accepted": "topic_planning", "cancel": END, "needs_followup": "hitl1", "exhausted": END},
    )
    builder.add_conditional_edges("topic_planning", _route, {"next": "wave0", "exhausted": END})
    builder.add_conditional_edges("wave0", _route, {"repair": "wave0", "pass": "wave1", "exhausted": END})
    builder.add_conditional_edges(
        "wave1",
        _route,
        {"repair": "wave1", "pass": "wave2_synthesis", "exhausted": END},
    )
    builder.add_conditional_edges(
        "wave2_synthesis",
        _route,
        {"evidence_needed": "targeted_evidence", "pass": "hitl2", "exhausted": END},
    )
    builder.add_edge("targeted_evidence", "wave2_synthesis")
    builder.add_conditional_edges(
        "hitl2",
        _route,
        {
            "revise_view": "wave2_synthesis",
            "repair": "targeted_evidence",
            "rerun": "rerun",
            "proceed": "readiness",
            "stop": END,
            "cancel": END,
        },
    )
    builder.add_conditional_edges(
        "rerun",
        _route,
        {
            "next": "topic_planning",  # fake backward compat (unchanged)
            "topic_planning": "topic_planning",  # real FULL
            "wave0": "wave0",  # real TOPIC / FINDING (stale sources)
            "wave1": "wave1",  # real FINDING (deep evidence only)
            "exhausted": END,  # both fake and real
        },
    )
    builder.add_conditional_edges(
        "readiness",
        _route,
        {
            "repair_targeted": "targeted_evidence",
            "repair_synthesis": "wave2_synthesis",
            "repair_hitl2": "hitl2",
            "pass": "final_delivery",
            "exhausted": END,
        },
    )
    builder.add_conditional_edges(
        "final_delivery",
        _route,
        {"repair": "final_delivery", "evidence_blocked": "readiness", "pass": END, "exhausted": END},
    )
    return builder


__all__ = ["all_real_gate_definitions", "build_research_graph"]
