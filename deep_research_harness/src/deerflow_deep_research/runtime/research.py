"""Research graph recipes and bounded node-capability policy helpers.

This module deliberately does not own a Deep Research lifecycle action, Run identity,
checkpoint namespace, provider reopen path, or State mutation.  The Harness lifecycle
module owns those facts through a selected Run Bundle.  Recipes remain useful to graph
composition, demos, and deterministic node-policy evidence only.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from deerflow_deep_research.agents.policies import (
    ExecutionBudget,
    ExecutionPolicy,
    ProviderObservationAdmission,
    ToolPolicySpec,
)
from deerflow_deep_research.domain.gate import GateDefinition
from deerflow_deep_research.domain.lifecycle import ImplementationMode
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies, PolicyRef
from deerflow_deep_research.domain.state import RESEARCH_STATE_SCHEMA_VERSION
from deerflow_deep_research.graph.builder import all_real_gate_definitions, build_research_graph
from deerflow_deep_research.graph.implementation_map import (
    AdapterKind,
    NodeAdapter,
    all_real_adapters,
    resolve_implementations,
)
from deerflow_deep_research.graph.registry import load_research_node_specs
from deerflow_deep_research.graph.topology import LOGICAL_NODES, NORMALIZED_EDGES
from deerflow_deep_research.runtime.node_agent_bridge import RuntimeNodeAgentBridge
from deerflow_deep_research.runtime.projection import build_node_dependencies, project_node_agent
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope

RECIPE_COMPATIBILITY_VERSION = 2
PUBLIC_RECIPE_REVISION = "public-real-v2"


def _recipe_compatibility_fingerprint(
    adapter_kinds: Mapping[str, AdapterKind],
    *,
    recipe_revision: str,
) -> str:
    """Hash fixed graph composition semantics without turning it into State authority."""

    payload = json.dumps(
        {
            "domain": "deep-research/graph-recipe/v2",
            "recipe_protocol": RECIPE_COMPATIBILITY_VERSION,
            "recipe_revision": recipe_revision,
            "state_schema": RESEARCH_STATE_SCHEMA_VERSION,
            "logical_nodes": LOGICAL_NODES,
            "topology": tuple((edge.source, edge.route, edge.target) for edge in NORMALIZED_EDGES),
            "implementations": tuple((name, adapter_kinds[name].value) for name in LOGICAL_NODES),
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class UnavailableNodeCapabilities:
    async def run_agent(self, *, context: Any, request: Any) -> Any:
        raise RuntimeError("node_agent_capability_unavailable")


class RuntimeNodeDependencyResolver:
    def __init__(
        self,
        graph_context: Any,
        capabilities: Any | None = None,
        *,
        capabilities_by_node: Mapping[str, Any] | None = None,
        selected_bundle: Any | None = None,
        full_rerun_policy: object | None = None,
    ) -> None:
        self._graph_context = graph_context
        self._capabilities = capabilities if capabilities is not None else UnavailableNodeCapabilities()
        self._capabilities_by_node = dict(capabilities_by_node or {})
        self._selected_bundle = selected_bundle
        self._full_rerun_policy = full_rerun_policy

    def resolve(self, *, logical_name: str, attempt_id: str, policy: PolicyRef) -> NodeBuildDependencies:
        agent_context = project_node_agent(
            self._graph_context,
            node_name=logical_name,
            attempt_id=attempt_id,
            policy_name=policy.name,
            selected_bundle=self._selected_bundle,
        )
        capabilities = self._capabilities_by_node.get(logical_name, self._capabilities)
        return build_node_dependencies(
            self._graph_context,
            agent_context,
            capabilities,
            selected_bundle=self._selected_bundle,
            full_rerun_policy=self._full_rerun_policy,
        )


@dataclass(frozen=True)
class ResearchGraphRecipe:
    builder: Any
    adapter_kinds: tuple[tuple[str, AdapterKind], ...]
    recipe_revision: str
    composition_name: str
    compatibility_fingerprint: str
    requires_work_units: bool = False
    requires_bootstrap_bundle: bool = False
    requires_request_bundle: bool = False
    requires_publication_bundle: bool = False
    requires_final_delivery_bundle: bool = False
    requires_node_agent_bridge: bool = False
    requires_wave0_worker_bridge: bool = False
    requires_wave1_worker_bridge: bool = False
    work_unit_store_factory: Any = None
    request_bundle_store_factory: Any = None
    node_agent_bridge_factory: Any = None

    @property
    def implementation_mode(self) -> ImplementationMode:
        kinds = tuple(kind for _, kind in self.adapter_kinds)
        if all(kind is AdapterKind.REAL for kind in kinds):
            return ImplementationMode.ALL_REAL
        if all(kind is AdapterKind.FIXTURE for kind in kinds):
            return ImplementationMode.FIXTURE
        return ImplementationMode.MIXED

    @classmethod
    def from_adapters(
        cls,
        *,
        adapters: Mapping[str, NodeAdapter],
        gate_defs: Mapping[str, GateDefinition],
        recipe_revision: str,
        composition_name: str,
        work_unit_store_factory: Any = None,
        request_bundle_store_factory: Any = None,
        node_agent_bridge_factory: Any = None,
    ) -> ResearchGraphRecipe:
        if not isinstance(recipe_revision, str) or not recipe_revision:
            raise ValueError("recipe_revision_required")
        if not isinstance(composition_name, str) or not composition_name:
            raise ValueError("composition_name_required")
        specs = load_research_node_specs()
        resolved_adapters = resolve_implementations(specs, adapters)
        kinds = {name: adapter.kind for name, adapter in resolved_adapters.items()}
        builder = build_research_graph(implementations=resolved_adapters, gate_defs=gate_defs)

        def is_real(logical_name: str) -> bool:
            return kinds[logical_name] is AdapterKind.REAL

        hitl1_real = is_real("hitl1")
        bootstrap_real = is_real("bootstrap")
        topic_planning_real = is_real("topic_planning")
        wave0_real = is_real("wave0")
        wave1_real = is_real("wave1")
        wave2_real = is_real("wave2_synthesis")
        targeted_evidence_real = is_real("targeted_evidence")
        if hitl1_real and not bootstrap_real:
            raise ValueError("hitl1_real_requires_bootstrap_real")
        if topic_planning_real and not hitl1_real:
            raise ValueError("topic_planning_real_requires_hitl1_real")
        if wave0_real and not topic_planning_real:
            raise ValueError("wave0_real_requires_topic_planning_real")
        if wave1_real and not (wave0_real and targeted_evidence_real):
            raise ValueError("wave1_real_requires_wave0_and_targeted_evidence_real")
        hitl2_real = is_real("hitl2")
        if wave2_real and not wave1_real:
            raise ValueError("wave2_real_requires_wave1_real")
        if hitl2_real and not wave2_real:
            raise ValueError("hitl2_real_requires_wave2_synthesis_real")
        rerun_real = is_real("rerun")
        if rerun_real and not hitl2_real:
            raise ValueError("rerun_real_requires_hitl2_real")
        readiness_real = is_real("readiness")
        if readiness_real and not hitl2_real:
            raise ValueError("readiness_real_requires_hitl2_real")
        final_real = is_real("final_delivery")
        if final_real and not readiness_real:
            raise ValueError("final_delivery_real_requires_readiness_real")
        return cls(
            builder=builder,
            adapter_kinds=tuple((name, kinds[name]) for name in LOGICAL_NODES),
            recipe_revision=recipe_revision,
            composition_name=composition_name,
            compatibility_fingerprint=_recipe_compatibility_fingerprint(kinds, recipe_revision=recipe_revision),
            requires_work_units=True,
            requires_bootstrap_bundle=bootstrap_real,
            requires_request_bundle=hitl1_real,
            requires_publication_bundle=final_real,
            requires_final_delivery_bundle=final_real,
            requires_node_agent_bridge=hitl1_real or topic_planning_real or readiness_real or final_real,
            requires_wave0_worker_bridge=wave0_real or targeted_evidence_real,
            requires_wave1_worker_bridge=wave1_real,
            work_unit_store_factory=work_unit_store_factory,
            request_bundle_store_factory=request_bundle_store_factory,
            node_agent_bridge_factory=node_agent_bridge_factory,
        )

    @classmethod
    def all_real(
        cls,
        *,
        work_unit_store_factory: Any = None,
        request_bundle_store_factory: Any = None,
        node_agent_bridge_factory: Any = None,
    ) -> ResearchGraphRecipe:
        """Build the one public, deployable Deep Research graph recipe explicitly."""

        specs = load_research_node_specs()
        return cls.from_adapters(
            adapters=all_real_adapters(specs),
            gate_defs=all_real_gate_definitions(),
            recipe_revision=PUBLIC_RECIPE_REVISION,
            composition_name="all_real",
            work_unit_store_factory=work_unit_store_factory,
            request_bundle_store_factory=request_bundle_store_factory,
            node_agent_bridge_factory=node_agent_bridge_factory,
        )


def _hitl1_node_agent_policy(graph_context: Any) -> ExecutionPolicy:
    """Zero-tool, one-model-call policy for HITL1 brief generation.

    @impl HIN-001
    @impl NOA-001
    @impl NOA-002
    """

    return ExecutionPolicy(
        policy_name="hitl1-structured-brief",
        allowed_tool_names=frozenset(),
        read_roots=(graph_context.workspace_root, graph_context.uploads_root),
        write_roots=(),
        attempt_root=graph_context.workspace_root,
        budget=ExecutionBudget(
            max_model_calls=1,
            max_total_tool_calls=1,
            max_tool_calls_per_response=1,
            max_parallel_tool_calls=1,
            total_token_budget=8_192,
            per_call_output_token_cap=2_048,
            per_tool_result_bytes=1,
            structured_result_bytes=4_096,
            wall_time_seconds=60.0,
        ),
        provider_observation_admission=ProviderObservationAdmission.CONFIGURED_MODEL_SERVICE,
    )


def _topic_planning_node_agent_policy(graph_context: Any) -> ExecutionPolicy:
    """Zero-tool, one-model-call policy for topic-plan generation."""

    return ExecutionPolicy(
        policy_name="topic-planning-structured-plan",
        allowed_tool_names=frozenset(),
        read_roots=(graph_context.workspace_root, graph_context.uploads_root),
        write_roots=(),
        attempt_root=graph_context.workspace_root,
        budget=ExecutionBudget(
            max_model_calls=1,
            max_total_tool_calls=1,
            max_tool_calls_per_response=1,
            max_parallel_tool_calls=1,
            total_token_budget=12_288,
            per_call_output_token_cap=4_096,
            per_tool_result_bytes=1,
            structured_result_bytes=16_384,
            wall_time_seconds=60.0,
        ),
        provider_observation_admission=ProviderObservationAdmission.CONFIGURED_MODEL_SERVICE,
    )


def _build_hitl1_capabilities(envelope: TrustedRuntimeEnvelope, graph_context: Any, factory: Any) -> Any:
    """Construct the zero-tool bridge for real HITL1 brief generation."""

    policy = _hitl1_node_agent_policy(graph_context)
    bridge_factory = factory or RuntimeNodeAgentBridge
    return bridge_factory(envelope=envelope, policy=policy, tools_resolver=lambda _envelope, _policy: ())


def _build_topic_planning_capabilities(envelope: TrustedRuntimeEnvelope, graph_context: Any, factory: Any) -> Any:
    """Construct the independently bounded zero-tool bridge for topic planning."""

    policy = _topic_planning_node_agent_policy(graph_context)
    bridge_factory = factory or RuntimeNodeAgentBridge
    return bridge_factory(envelope=envelope, policy=policy, tools_resolver=lambda _envelope, _policy: ())


def _readiness_node_agent_policy(graph_context: Any) -> ExecutionPolicy:
    """Dedicated zero-tool policy for per-question evidence answerability."""

    return ExecutionPolicy(
        policy_name="readiness-evidence-critic",
        allowed_tool_names=frozenset(),
        read_roots=(graph_context.workspace_root, graph_context.uploads_root),
        write_roots=(),
        attempt_root=graph_context.workspace_root,
        budget=ExecutionBudget(
            max_model_calls=1,
            max_total_tool_calls=1,
            max_tool_calls_per_response=1,
            max_parallel_tool_calls=1,
            total_token_budget=8_192,
            per_call_output_token_cap=2_048,
            per_tool_result_bytes=1,
            structured_result_bytes=4_096,
            wall_time_seconds=60.0,
        ),
    )


def _build_readiness_capabilities(envelope: TrustedRuntimeEnvelope, graph_context: Any, factory: Any) -> Any:
    bridge_factory = factory or RuntimeNodeAgentBridge
    return bridge_factory(
        envelope=envelope,
        policy=_readiness_node_agent_policy(graph_context),
        tools_resolver=lambda _envelope, _policy: (),
    )


def _final_delivery_node_agent_policy(graph_context: Any) -> ExecutionPolicy:
    """Dedicated zero-tool policy for one bounded report-layout invocation."""

    return ExecutionPolicy(
        policy_name="final-delivery-composer",
        allowed_tool_names=frozenset(),
        read_roots=(graph_context.workspace_root, graph_context.uploads_root),
        write_roots=(),
        attempt_root=graph_context.workspace_root,
        budget=ExecutionBudget(
            max_model_calls=1,
            max_total_tool_calls=1,
            max_tool_calls_per_response=1,
            max_parallel_tool_calls=1,
            total_token_budget=8_192,
            per_call_output_token_cap=2_048,
            per_tool_result_bytes=1,
            structured_result_bytes=4_096,
            wall_time_seconds=60.0,
        ),
    )


def _build_final_delivery_capabilities(envelope: TrustedRuntimeEnvelope, graph_context: Any, factory: Any) -> Any:
    bridge_factory = factory or RuntimeNodeAgentBridge
    return bridge_factory(
        envelope=envelope,
        policy=_final_delivery_node_agent_policy(graph_context),
        tools_resolver=lambda _envelope, _policy: (),
    )


def _wave2_synthesis_node_agent_policy(graph_context: Any) -> ExecutionPolicy:
    """Dedicated zero-tool policy for accepted-evidence synthesis.

    @impl NOA-011
    """

    return ExecutionPolicy(
        policy_name="wave2-evidence-synthesis",
        allowed_tool_names=frozenset(),
        read_roots=(graph_context.workspace_root, graph_context.uploads_root),
        write_roots=(),
        attempt_root=graph_context.workspace_root,
        budget=ExecutionBudget(
            max_model_calls=2,
            max_total_tool_calls=1,
            max_tool_calls_per_response=1,
            max_parallel_tool_calls=1,
            total_token_budget=16_384,
            per_call_output_token_cap=4_096,
            per_tool_result_bytes=1,
            structured_result_bytes=8_192,
            wall_time_seconds=60.0,
        ),
    )


def _build_wave2_synthesis_capabilities(envelope: TrustedRuntimeEnvelope, graph_context: Any, factory: Any) -> Any:
    bridge_factory = factory or RuntimeNodeAgentBridge
    return bridge_factory(
        envelope=envelope,
        policy=_wave2_synthesis_node_agent_policy(graph_context),
        tools_resolver=lambda _envelope, _policy: (),
    )


WORKER_TOOL_NAMES = frozenset(
    {"tavily_search", "tavily_extract", "duckduckgo_search", "jina_ai", "firecrawl_scrape", "web_search", "web_fetch"}
)


def _worker_policy(*, policy_name: str, graph_context: Any) -> ExecutionPolicy:
    """Bounded multi-tool policy shared by the Wave0/Wave1 workers.

    @impl WAN-002
    @impl NOA-001
    @impl NOA-002
    """

    return ExecutionPolicy(
        policy_name=policy_name,
        allowed_tool_names=WORKER_TOOL_NAMES,
        read_roots=(graph_context.workspace_root, graph_context.uploads_root),
        write_roots=(graph_context.workspace_root,),
        attempt_root=graph_context.workspace_root,
        tool_specs=tuple(
            ToolPolicySpec(tool_name=name, effect="read", native_cancellable=True) for name in WORKER_TOOL_NAMES
        ),
        budget=ExecutionBudget(
            max_model_calls=50,
            max_total_tool_calls=200,
            max_tool_calls_per_response=12,
            max_parallel_tool_calls=12,
            total_token_budget=2_000_000,
            per_call_output_token_cap=64_000,
            per_tool_result_bytes=512_000,
            structured_result_bytes=64_000,
            wall_time_seconds=900.0,
        ),
    )


def _wave0_worker_policy(graph_context: Any) -> ExecutionPolicy:
    """Bounded multi-tool policy for a Wave0 source-intake worker."""

    return _worker_policy(policy_name="wave0-source-intake", graph_context=graph_context)


def _build_wave0_capabilities(envelope: TrustedRuntimeEnvelope, graph_context: Any, factory: Any) -> Any:
    """Construct the Wave0 worker node-agent bridge with bounded configured tools."""

    policy = _wave0_worker_policy(graph_context)
    bridge_factory = factory or RuntimeNodeAgentBridge
    return bridge_factory(envelope=envelope, policy=policy)


def _wave1_worker_policy(graph_context: Any) -> ExecutionPolicy:
    """Bounded multi-tool policy for a Wave1 evidence extraction worker."""

    return _worker_policy(policy_name="wave1-evidence-extraction", graph_context=graph_context)


def _build_wave1_capabilities(envelope: TrustedRuntimeEnvelope, graph_context: Any, factory: Any) -> Any:
    policy = _wave1_worker_policy(graph_context)
    bridge_factory = factory or RuntimeNodeAgentBridge
    return bridge_factory(envelope=envelope, policy=policy)


__all__ = [
    "ResearchGraphRecipe",
    "RuntimeNodeDependencyResolver",
    "UnavailableNodeCapabilities",
]
