"""Explicit test-only composition roots for fixture and mixed graph recipes."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from deerflow_deep_research_fixtures.catalog import build_fixture_catalog
from deerflow_deep_research_fixtures.scenario import FixtureScenario

from deerflow_deep_research.domain.gate import GateDefinition
from deerflow_deep_research.graph.builder import all_real_gate_definitions
from deerflow_deep_research.graph.implementation_map import AdapterKind, NodeAdapter, all_real_adapters
from deerflow_deep_research.graph.registry import load_research_node_specs
from deerflow_deep_research.graph.topology import LOGICAL_NODES
from deerflow_deep_research.runtime.research import ResearchGraphRecipe


def fixture_selection(
    scenario: FixtureScenario | None = None,
) -> tuple[dict[str, NodeAdapter], dict[str, GateDefinition]]:
    """Return the complete deterministic selections without touching production assembly."""

    active_scenario = scenario or FixtureScenario()
    adapters, gate_defs = build_fixture_catalog(active_scenario)
    return dict(adapters), dict(gate_defs)


def fixture_recipe(
    *,
    scenario: FixtureScenario | None = None,
    recipe_revision: str = "fixture-test-v1",
    work_unit_store_factory: Any = None,
    request_bundle_store_factory: Any = None,
    node_agent_bridge_factory: Any = None,
) -> ResearchGraphRecipe:
    """Compose a deterministic full-fixture recipe for a test process."""

    adapters, gate_defs = fixture_selection(scenario)
    return ResearchGraphRecipe.from_adapters(
        adapters=adapters,
        gate_defs=gate_defs,
        recipe_revision=recipe_revision,
        composition_name="fixture-test",
        work_unit_store_factory=work_unit_store_factory,
        request_bundle_store_factory=request_bundle_store_factory,
        node_agent_bridge_factory=node_agent_bridge_factory,
    )


def mixed_recipe(
    *,
    real_nodes: Iterable[str],
    scenario: FixtureScenario | None = None,
    recipe_revision: str | None = None,
    work_unit_store_factory: Any = None,
    request_bundle_store_factory: Any = None,
    node_agent_bridge_factory: Any = None,
) -> ResearchGraphRecipe:
    """Overlay named real adapters and rebuild gates from the final selections."""

    requested_nodes = tuple(real_nodes)
    if len(set(requested_nodes)) != len(requested_nodes):
        raise ValueError("mixed_recipe_real_nodes_duplicate")
    unknown = set(requested_nodes) - set(LOGICAL_NODES)
    if unknown:
        raise ValueError(f"mixed_recipe_real_nodes_unknown:{','.join(sorted(unknown))}")

    adapters, fixture_gates = fixture_selection(scenario)
    real_adapters = all_real_adapters(load_research_node_specs())
    for logical_name in requested_nodes:
        adapters[logical_name] = real_adapters[logical_name]

    real_gates = all_real_gate_definitions()
    gate_defs: dict[str, GateDefinition] = {}
    for logical_name, adapter in adapters.items():
        if not adapter.requires_gate:
            continue
        gate_defs[logical_name] = (
            real_gates[logical_name] if adapter.kind is AdapterKind.REAL else fixture_gates[logical_name]
        )

    revision = recipe_revision or "fixture-mixed-" + ("-".join(sorted(requested_nodes)) or "none")
    return ResearchGraphRecipe.from_adapters(
        adapters=adapters,
        gate_defs=gate_defs,
        recipe_revision=revision,
        composition_name="mixed-test",
        work_unit_store_factory=work_unit_store_factory,
        request_bundle_store_factory=request_bundle_store_factory,
        node_agent_bridge_factory=node_agent_bridge_factory,
    )


__all__ = ["fixture_recipe", "fixture_selection", "mixed_recipe"]
