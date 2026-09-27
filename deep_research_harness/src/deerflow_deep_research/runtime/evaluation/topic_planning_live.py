"""Real-model live subject for the topic-planning direction-loop case.

The ``topic_planning`` node's own cognitive program (not the lead agent):
each declared scenario builds the node's real dependencies — the production
zero-tool bridge carrying the real model — and drives one planner invocation,
capturing the materialized topic registry and the case's required telemetry.
The scenario's profile (scope boundaries, custom notes) lives in an in-memory
request bundle store; the state carries the matching profile projection, the
request text, and where the case declares one, the current round direction.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from deerflow.sandbox.local.local_sandbox import LocalSandbox, PathMapping

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, bundle_profile_path
from deerflow_deep_research.domain.context import (
    GraphContextView,
    NodeAgentBundleContext,
    NodeAgentContext,
    SelectedBundleContext,
)
from deerflow_deep_research.domain.evaluation import SubjectExecution
from deerflow_deep_research.domain.lifecycle import CurrentRoundDirection
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.profile import ResearchProfile, compute_profile_content_hash, profile_state_fields
from deerflow_deep_research.domain.state import ContentRef
from deerflow_deep_research.runtime.node_agent_bridge import ResolvedNodeModel, RuntimeNodeAgentBridge
from deerflow_deep_research.runtime.research import _build_topic_planning_capabilities
from deerflow_deep_research.runtime.runtime_adapter import (
    OUTPUTS_VIRTUAL_ROOT,
    UPLOADS_VIRTUAL_ROOT,
    WORKSPACE_VIRTUAL_ROOT,
    TrustedRuntimeEnvelope,
)

from .runner import ExecutionContext, Subject

_BASE_PROFILE: dict[str, Any] = {
    "schema_version": 2,
    "depth": "deep_dive",
    "audience": "domain_expert",
    "format": "annotated_bibliography",
    "cost_tolerance": "extensive",
    "time_budget": "overnight",
    "must_answer": ("Q1", "Q2"),
    "comparison_required": True,
    "comparison_subjects": ("lithium-ion batteries", "vanadium redox flow batteries"),
    "request_language": "en",
    "output_language": "zh",
}


def _rid(stem: str) -> str:
    return "b_" + (stem * 43)[:43]


class _ProfileReader:
    """In-memory request bundle store answering only the declared profile."""

    def __init__(self, profile: ResearchProfile, profile_ref: ContentRef) -> None:
        self.profile = profile
        self.profile_ref = profile_ref

    async def read_profile(self, profile_ref: ContentRef) -> ResearchProfile:
        if profile_ref != self.profile_ref:
            raise ValueError("profile_ref_unexpected")
        return self.profile


class _CountingRunnable:
    def __init__(self, inner: Any, counts: dict[str, int]) -> None:
        self._inner = inner
        self._counts = counts

    def _record(self, response: Any) -> None:
        self._counts["model_calls"] += 1
        usage = getattr(response, "usage_metadata", None)
        if isinstance(usage, Mapping):
            self._counts["input_tokens"] += int(usage.get("input_tokens", 0) or 0)
            self._counts["output_tokens"] += int(usage.get("output_tokens", 0) or 0)

    def invoke(self, messages: Any, config: Any = None, **kwargs: Any) -> Any:
        response = self._inner.invoke(messages, config, **kwargs)
        self._record(response)
        return response

    async def ainvoke(self, messages: Any, config: Any = None, **kwargs: Any) -> Any:
        response = await self._inner.ainvoke(messages, config, **kwargs)
        self._record(response)
        return response

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


class _CountingModel:
    """Transparent model proxy recording per-response usage for the subject."""

    def __init__(self, inner: Any, counts: dict[str, int]) -> None:
        self._inner = inner
        self._counts = counts

    def bind_tools(self, tools: Any = None, **kwargs: Any) -> _CountingRunnable:
        return _CountingRunnable(self._inner.bind_tools(tools, **kwargs), self._counts)

    def bind(self, **kwargs: Any) -> _CountingRunnable:
        return _CountingRunnable(self._inner.bind(**kwargs), self._counts)

    def invoke(self, messages: Any, config: Any = None, **kwargs: Any) -> Any:
        return _CountingRunnable(self._inner, self._counts).invoke(messages, config, **kwargs)

    async def ainvoke(self, messages: Any, config: Any = None, **kwargs: Any) -> Any:
        return await _CountingRunnable(self._inner, self._counts).ainvoke(messages, config, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


def _counting_model_resolver(app_config: Any, counts: dict[str, int]) -> Any:
    def resolver(envelope: Any) -> ResolvedNodeModel:
        from deerflow.models.factory import create_chat_model

        selected = envelope.app_config.models[0]
        resolved = ResolvedNodeModel(
            model=create_chat_model(name=selected.name, app_config=envelope.app_config, attach_tracing=False),
            configured_service_label=str(selected.name),
        )
        return ResolvedNodeModel(
            model=_CountingModel(resolved.model, counts),
            configured_service_label=resolved.configured_service_label,
            configured_endpoint_authority=resolved.configured_endpoint_authority,
        )

    return resolver


def _scenario_profile(scenario: Mapping[str, Any]) -> ResearchProfile:
    fields = dict(_BASE_PROFILE)
    fields["scope_boundaries"] = str(scenario.get("scope_boundaries") or "")
    fields["custom_notes"] = str(scenario.get("custom_notes") or "")
    return ResearchProfile(**fields)


def _scenario_bundle(position: int) -> RunBundleRef:
    stem = chr(ord("a") + (position % 26))
    return RunBundleRef(bundle_id=BundleId(_rid(stem)), scope_bucket="s_" + "B" * 43)


def _scenario_state(
    scenario: Mapping[str, Any],
    *,
    profile: ResearchProfile,
    profile_ref: ContentRef,
    bundle: RunBundleRef,
) -> dict[str, Any]:
    direction = scenario.get("current_direction")
    generation = 1 if isinstance(direction, str) and direction else 0
    payload: dict[str, Any] = {
        "schema_version": 3,
        "bundle_id": bundle.bundle_id.value,
        "outer_thread_id": f"topic-live-{scenario.get('scenario_id')}",
        "request_text": str(scenario.get("request_text") or ""),
        "phase": "topic_planning",
        "generation": generation,
        "execution_trace": (),
    }
    payload.update(profile_state_fields(profile, profile_ref))
    if generation:
        payload["current_refinement"] = CurrentRoundDirection.model_validate(
            {"text": direction, "round": 1, "generation": 1}
        )
    return payload


def _capture_update(update: Mapping[str, Any]) -> dict[str, Any]:
    route = update.get("route")
    captured: dict[str, Any] = {"route": route}
    if route == "next":
        captured["topic_refs"] = list(update.get("topic_refs") or ())
        captured["topic_registry"] = [dict(entry) for entry in (update.get("topic_registry") or ())]
    else:
        captured["terminal_status"] = update.get("terminal_status")
        incident = update.get("latest_incident")
        if incident is not None:
            captured["latest_incident"] = incident
    return captured


def topic_planning_live_subject(
    *,
    node_spec: Any,
    app_config: Any,
    provider: str,
    model: str,
    price_input_per_mtok: float | None = None,
    price_output_per_mtok: float | None = None,
) -> Subject:
    """Build the real-model topic-planning node subject for its direction-loop case."""

    async def invoke(context: ExecutionContext) -> SubjectExecution:
        scenarios = context.fixture.get("scenarios")
        if not isinstance(scenarios, list) or not scenarios:
            raise ValueError("evaluation_scenarios_missing")
        execution_plan = context.fixture.get("execution")
        runtime_controls = execution_plan.get("runtime_controls", []) if isinstance(execution_plan, Mapping) else []
        counts: dict[str, int] = {"model_calls": 0, "input_tokens": 0, "output_tokens": 0}
        updates: list[dict[str, Any]] = []
        prompt_digests: list[str] = []
        bridge_factory_used: list[Any] = []
        workspace = context.workspace
        for position, scenario in enumerate(scenarios):
            if not isinstance(scenario, Mapping):
                raise ValueError("evaluation_scenario_invalid")
            scenario_id = scenario.get("scenario_id")
            if not isinstance(scenario_id, str) or not scenario_id:
                raise ValueError("evaluation_scenario_id_invalid")
            context.observe("scenario.invoked", {"subject": "topic_planning", "scenario_id": scenario_id})
            bundle = _scenario_bundle(position)
            profile = _scenario_profile(scenario)
            profile_ref = ContentRef(
                sandbox_path=bundle_profile_path(bundle),
                content_hash=compute_profile_content_hash(profile),
                schema_version=1,
                short_summary="case scenario profile",
            )
            state = _scenario_state(scenario, profile=profile, profile_ref=profile_ref, bundle=bundle)
            prompt_digests.append(
                hashlib.sha256(
                    json.dumps(
                        {
                            "request_text": state["request_text"],
                            "current_refinement": (
                                state["current_refinement"].model_dump(mode="json")
                                if "current_refinement" in state
                                else None
                            ),
                            "profile": profile.model_dump(mode="json"),
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ).encode("utf-8")
                ).hexdigest()
            )
            host_root = workspace / f"scenario-{position:02d}-{scenario_id}"
            workspace_dir = host_root / "workspace"
            uploads_dir = host_root / "uploads"
            outputs_dir = host_root / "outputs"
            for path in (workspace_dir, uploads_dir, outputs_dir):
                path.mkdir(parents=True, exist_ok=True)
            sandbox = LocalSandbox(
                id=f"local:default:topic-live-{scenario_id}",
                path_mappings=[
                    PathMapping(container_path=WORKSPACE_VIRTUAL_ROOT, local_path=str(workspace_dir)),
                    PathMapping(container_path=UPLOADS_VIRTUAL_ROOT, local_path=str(uploads_dir)),
                    PathMapping(container_path=OUTPUTS_VIRTUAL_ROOT, local_path=str(outputs_dir)),
                ],
            )
            envelope = TrustedRuntimeEnvelope(
                effective_user_id="default",
                outer_thread_id=f"topic-live-{scenario_id}",
                outer_run_id=f"topic-live-run-{scenario_id}",
                app_config=app_config,
                workspace_host_path=workspace_dir,
                uploads_host_path=uploads_dir,
                outputs_host_path=outputs_dir,
                workspace_virtual_root=WORKSPACE_VIRTUAL_ROOT,
                uploads_virtual_root=UPLOADS_VIRTUAL_ROOT,
                outputs_virtual_root=OUTPUTS_VIRTUAL_ROOT,
                parent_sandbox=sandbox,
            )
            graph = GraphContextView(
                research_scope_id=bundle.bundle_id.value,
                workspace_root=f"{WORKSPACE_VIRTUAL_ROOT}/deep-research/{bundle.bundle_id.value}",
                uploads_root=UPLOADS_VIRTUAL_ROOT,
                outputs_root=f"{OUTPUTS_VIRTUAL_ROOT}/deep-research/{bundle.bundle_id.value}",
            )
            selected_bundle = SelectedBundleContext(bundle=bundle)

            def bridge_factory(*, envelope: Any, policy: Any, tools_resolver: Any) -> RuntimeNodeAgentBridge:
                bridge = RuntimeNodeAgentBridge(
                    envelope=envelope,
                    policy=policy,
                    tools_resolver=tools_resolver,
                    model_resolver=_counting_model_resolver(app_config, counts),
                )
                bridge_factory_used.append(bridge)
                return bridge

            capabilities = _build_topic_planning_capabilities(envelope, graph, bridge_factory)
            dependencies = NodeBuildDependencies(
                graph_context=graph,
                agent_context=NodeAgentContext(
                    research_scope_id=bundle.bundle_id.value,
                    node_name="topic_planning",
                    attempt_id=f"g0-tp-{position:02d}",
                    workspace_root=graph.workspace_root,
                    attempt_root=f"{graph.workspace_root}/topic_planning",
                    policy_name=str(getattr(node_spec.policy, "name", "topic-planning")),
                    bundle_context=NodeAgentBundleContext.from_selected_bundle(selected_bundle),
                ),
                capabilities=capabilities,
                request_bundle=_ProfileReader(profile, profile_ref),
                selected_bundle=selected_bundle,
            )
            branch = node_spec.real_factory(dependencies)
            update = await branch(state)
            if not isinstance(update, Mapping):
                raise ValueError("topic_planning_update_invalid")
            captured = _capture_update(update)
            captured["scenario_id"] = scenario_id
            captured["case_kind"] = scenario.get("case_kind")
            captured["expected_assignment_fragments"] = list(scenario.get("expected_assignment_fragments") or ())
            updates.append(captured)
            context.observe(
                "scenario.completed",
                {
                    "subject": "topic_planning",
                    "scenario_id": scenario_id,
                    "route": captured["route"],
                },
            )
        cost = 0.0
        cost_unpriced = price_input_per_mtok is None or price_output_per_mtok is None
        if not cost_unpriced:
            cost = round(
                counts["input_tokens"] / 1_000_000 * float(price_input_per_mtok or 0.0)
                + counts["output_tokens"] / 1_000_000 * float(price_output_per_mtok or 0.0),
                6,
            )
        resource_use: dict[str, int | float | str | bool] = {
            "model_calls": counts["model_calls"],
            "tool_calls": 0,
            "provider": provider,
            "model": model,
            "composed_prompt_digest": hashlib.sha256(json.dumps(prompt_digests).encode("utf-8")).hexdigest(),
            "input_tokens": counts["input_tokens"],
            "output_tokens": counts["output_tokens"],
            "cost_usd": cost,
        }
        for control in runtime_controls:
            if isinstance(control, Mapping):
                resource_use[str(control["name"])] = str(control["digest"])
        return SubjectExecution(
            output={"scenario_updates": updates, "cost_unpriced": cost_unpriced},
            resource_use=resource_use,
        )

    return invoke


__all__ = ["topic_planning_live_subject"]
