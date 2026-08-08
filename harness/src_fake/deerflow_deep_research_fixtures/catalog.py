"""Explicit fixture catalog and test/demo recipe factory.

@impl FSI-001
@impl FSI-002
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from deerflow_deep_research.domain.gate import GateDefinition
from deerflow_deep_research.graph.implementation_map import (
    AdapterKind,
    ImplementationMapError,
    NodeAdapter,
    validate_gate_definitions,
)
from deerflow_deep_research.graph.topology import LOGICAL_NODES

from .gates import build_fixture_gate_definitions
from .graph.nodes.bootstrap.adapter import build_fixture as build_bootstrap
from .graph.nodes.final_delivery.adapter import build_fixture as build_final_delivery
from .graph.nodes.hitl1.adapter import build_fixture as build_hitl1
from .graph.nodes.hitl2.adapter import build_fixture as build_hitl2
from .graph.nodes.readiness.adapter import build_fixture as build_readiness
from .graph.nodes.rerun.adapter import build_fixture as build_rerun
from .graph.nodes.targeted_evidence.adapter import build_fixture as build_targeted_evidence
from .graph.nodes.topic_planning.adapter import build_fixture as build_topic_planning
from .graph.nodes.wave0.adapter import build_fixture as build_wave0
from .graph.nodes.wave1.adapter import build_fixture as build_wave1
from .graph.nodes.wave2_synthesis.adapter import build_fixture as build_wave2_synthesis
from .scenario import FixtureScenario


def build_fixture_adapters(scenario: FixtureScenario | None = None) -> Mapping[str, NodeAdapter]:
    """Return one deterministic fixture adapter for every fixed logical node."""

    active_scenario = scenario or FixtureScenario()
    adapters = {
        "bootstrap": NodeAdapter(
            factory=build_bootstrap(active_scenario), kind=AdapterKind.FIXTURE, requires_gate=False
        ),
        "hitl1": NodeAdapter(factory=build_hitl1, kind=AdapterKind.FIXTURE, requires_gate=False),
        "topic_planning": NodeAdapter(factory=build_topic_planning, kind=AdapterKind.FIXTURE, requires_gate=False),
        "wave0": NodeAdapter(factory=build_wave0, kind=AdapterKind.FIXTURE, requires_gate=True),
        "wave1": NodeAdapter(factory=build_wave1, kind=AdapterKind.FIXTURE, requires_gate=True),
        "wave2_synthesis": NodeAdapter(factory=build_wave2_synthesis, kind=AdapterKind.FIXTURE, requires_gate=True),
        "targeted_evidence": NodeAdapter(
            factory=build_targeted_evidence,
            kind=AdapterKind.FIXTURE,
            requires_gate=False,
        ),
        "hitl2": NodeAdapter(factory=build_hitl2(active_scenario), kind=AdapterKind.FIXTURE, requires_gate=False),
        "rerun": NodeAdapter(factory=build_rerun, kind=AdapterKind.FIXTURE, requires_gate=False),
        "readiness": NodeAdapter(factory=build_readiness, kind=AdapterKind.FIXTURE, requires_gate=True),
        "final_delivery": NodeAdapter(factory=build_final_delivery, kind=AdapterKind.FIXTURE, requires_gate=True),
    }
    if tuple(adapters) != LOGICAL_NODES:
        raise ValueError("fixture_catalog_topology_mismatch")
    return MappingProxyType(adapters)


def _validate_fixture_catalog(
    adapters: Mapping[str, NodeAdapter],
    gate_defs: Mapping[str, GateDefinition],
) -> None:
    """Reject a partial or mismatched fixture catalog before recipe composition."""

    if tuple(adapters) != LOGICAL_NODES:
        raise ValueError("fixture_catalog_topology_mismatch")
    if any(adapter.kind is not AdapterKind.FIXTURE for adapter in adapters.values()):
        raise ValueError("fixture_catalog_adapter_kind_mismatch")
    try:
        validate_gate_definitions(adapters, gate_defs)
    except ImplementationMapError as exc:
        raise ValueError(f"fixture_catalog_{exc.code}") from exc


def build_fixture_catalog(
    scenario: FixtureScenario | None = None,
) -> tuple[Mapping[str, NodeAdapter], Mapping[str, GateDefinition]]:
    """Build one complete deterministic adapter and gate-definition pair."""

    active_scenario = scenario or FixtureScenario()
    adapters = build_fixture_adapters(active_scenario)
    gate_defs = MappingProxyType(build_fixture_gate_definitions(active_scenario))
    _validate_fixture_catalog(adapters, gate_defs)
    return adapters, gate_defs


def build_fixture_recipe(
    *,
    scenario: FixtureScenario | None = None,
    work_unit_store_factory: Any = None,
    request_bundle_store_factory: Any = None,
    node_agent_bridge_factory: Any = None,
):
    """Build a deterministic recipe for a test or credential-free demo root."""

    from deerflow_deep_research.runtime.research import ResearchGraphRecipe

    active_scenario = scenario or FixtureScenario()
    adapters, gate_defs = build_fixture_catalog(active_scenario)
    return ResearchGraphRecipe.from_adapters(
        adapters=adapters,
        gate_defs=gate_defs,
        recipe_revision="fixture-v1",
        composition_name="fixture",
        work_unit_store_factory=work_unit_store_factory,
        request_bundle_store_factory=request_bundle_store_factory,
        node_agent_bridge_factory=node_agent_bridge_factory,
    )


__all__ = ["build_fixture_adapters", "build_fixture_catalog", "build_fixture_recipe"]
