"""Explicit topology and adapter/gate-composition contracts.

@impl REG-001
@impl REG-005
@impl REG-019
@impl FSI-002
@impl HIT-003
@impl TOP-005
@impl WAN-005
@impl WON-005
@impl WSN-004
"""

from __future__ import annotations

import inspect
from dataclasses import replace
from types import MappingProxyType

import pytest
from deerflow_deep_research_fixtures import catalog as fixture_catalog
from deerflow_deep_research_fixtures.catalog import build_fixture_adapters, build_fixture_catalog
from deerflow_deep_research_fixtures.gates import build_fixture_gate_definitions
from deerflow_deep_research_fixtures.scenario import FixtureScenario

from deerflow_deep_research.domain.node_spec import UNAVAILABLE_REAL_FACTORY
from deerflow_deep_research.graph.builder import all_real_gate_definitions, build_research_graph
from deerflow_deep_research.graph.implementation_map import (
    AdapterKind,
    ImplementationMapError,
    NodeAdapter,
    all_real_adapters,
    resolve_implementations,
)
from deerflow_deep_research.graph.nodes.hitl1.contracts import Hitl1Result
from deerflow_deep_research.graph.registry import load_research_node_specs
from deerflow_deep_research.graph.topology import LOGICAL_NODES, NORMALIZED_EDGES, TopologyEdge, validate_topology
from deerflow_deep_research.runtime.research import ResearchGraphRecipe
from tests.fixtures.recipes import mixed_recipe


def _placeholder_fixture_factory(_dependencies):
    def run(_state):
        return {}

    return run


def _fixture_selection() -> tuple[dict[str, NodeAdapter], dict]:
    scenario = FixtureScenario()
    return dict(build_fixture_adapters(scenario)), build_fixture_gate_definitions(scenario)


def test_normalized_topology_has_eleven_reachable_nodes_and_no_internal_workers() -> None:
    assert LOGICAL_NODES == (
        "bootstrap",
        "hitl1",
        "topic_planning",
        "wave0",
        "wave1",
        "wave2_synthesis",
        "targeted_evidence",
        "hitl2",
        "rerun",
        "readiness",
        "final_delivery",
    )
    validate_topology(LOGICAL_NODES, NORMALIZED_EDGES)
    assert not any("dispatch" in edge.source or "join" in edge.source for edge in NORMALIZED_EDGES)
    assert not {"initialize", "allocate", "worker", "submit", "drain"} & set(LOGICAL_NODES)


def test_only_work_unit_controller_nodes_declare_that_capability() -> None:
    from deerflow_deep_research.domain.node_spec import NodeCapability

    specs = load_research_node_specs()
    declaring = {name for name, spec in specs.items() if NodeCapability.WORK_UNIT_CONTROLLER in spec.capabilities}
    assert declaring == {"wave0", "wave1", "targeted_evidence", "readiness"}


def test_real_hitl1_declares_only_request_bundle_capability() -> None:
    from deerflow_deep_research.domain.node_spec import NodeCapability

    hitl1 = load_research_node_specs()["hitl1"]
    assert hitl1.real_factory is not UNAVAILABLE_REAL_FACTORY
    assert hitl1.capabilities == frozenset({NodeCapability.REQUEST_BUNDLE})
    assert NodeCapability.BOOTSTRAP_BUNDLE not in hitl1.capabilities
    assert NodeCapability.WORK_UNIT_CONTROLLER not in hitl1.capabilities


def test_hitl1_route_contract_and_topology_include_followup_and_exhausted() -> None:
    assert set(Hitl1Result.model_fields["route"].annotation.__args__) == {
        "accepted",
        "cancel",
        "needs_followup",
        "exhausted",
    }
    assert TopologyEdge("hitl1", "needs_followup", "hitl1") in NORMALIZED_EDGES
    assert TopologyEdge("hitl1", "exhausted", "blocked") in NORMALIZED_EDGES


def test_explicit_fixture_and_all_real_compositions_preserve_topology_shape() -> None:
    fixture_adapters, fixture_gates = build_fixture_catalog()
    fixture = build_research_graph(implementations=fixture_adapters, gate_defs=fixture_gates).compile()
    real = ResearchGraphRecipe.all_real().builder.compile()

    assert {(edge.source, edge.target) for edge in fixture.get_graph().edges} == {
        (edge.source, edge.target) for edge in real.get_graph().edges
    }
    assert set(fixture_gates) == {"wave0", "wave1", "wave2_synthesis", "readiness", "final_delivery"}
    assert set(all_real_gate_definitions()) == {"wave0", "wave1", "wave2_synthesis", "final_delivery"}


def test_explicit_full_fixture_and_paired_mixed_compositions_preserve_topology_shape() -> None:
    fixture = fixture_catalog.build_fixture_recipe()
    adapters, gate_defs = _fixture_selection()
    real_adapters = all_real_adapters(load_research_node_specs())
    real_gates = all_real_gate_definitions()
    for logical_name in ("bootstrap", "hitl1", "topic_planning", "wave0"):
        adapters[logical_name] = real_adapters[logical_name]
    gate_defs["wave0"] = real_gates["wave0"]
    mixed = ResearchGraphRecipe.from_adapters(
        adapters=adapters,
        gate_defs=gate_defs,
        recipe_revision="mixed-topology-v1",
        composition_name="mixed-topology",
    )

    fixture_graph = fixture.builder.compile()
    mixed_graph = mixed.builder.compile()
    real_graph = ResearchGraphRecipe.all_real().builder.compile()

    assert fixture.implementation_mode.value == "fixture"
    assert mixed.implementation_mode.value == "mixed"
    expected_edges = {(edge.source, edge.target) for edge in real_graph.get_graph().edges}
    assert {(edge.source, edge.target) for edge in fixture_graph.get_graph().edges} == expected_edges
    assert {(edge.source, edge.target) for edge in mixed_graph.get_graph().edges} == expected_edges


def test_normalized_topology_retains_repair_rerun_and_fan_in_paths() -> None:
    assert {
        TopologyEdge("wave0", "repair", "wave0"),
        TopologyEdge("wave1", "repair", "wave1"),
        TopologyEdge("rerun", "next", "topic_planning"),
        TopologyEdge("rerun", "wave0", "wave0"),
        TopologyEdge("rerun", "wave1", "wave1"),
    } <= set(NORMALIZED_EDGES)
    assert {
        "wave1",
        "targeted_evidence",
        "hitl2",
        "readiness",
    } <= {edge.source for edge in NORMALIZED_EDGES if edge.target == "wave2_synthesis"}


def test_fixture_catalog_rejects_incomplete_pair_before_recipe_composition(monkeypatch: pytest.MonkeyPatch) -> None:
    adapters, _ = _fixture_selection()
    adapters.pop("final_delivery")
    monkeypatch.setattr(fixture_catalog, "build_fixture_adapters", lambda _scenario: MappingProxyType(adapters))

    with pytest.raises(ValueError, match="fixture_catalog_topology_mismatch"):
        fixture_catalog.build_fixture_recipe()


def test_fixture_catalog_rejects_gate_membership_mismatch_before_recipe_composition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, gates = _fixture_selection()
    gates.pop("final_delivery")
    monkeypatch.setattr(fixture_catalog, "build_fixture_gate_definitions", lambda _scenario: gates)

    with pytest.raises(ValueError, match="fixture_catalog_gate_definitions_incomplete"):
        fixture_catalog.build_fixture_recipe()


def test_route_remains_a_typed_direct_read_of_state_route() -> None:
    from deerflow_deep_research.graph.builder import _route

    assert _route({"route": "pass"}) == "pass"
    assert _route({"route": "repair"}) == "repair"
    with pytest.raises(ValueError, match="typed_route_missing"):
        _route({})
    with pytest.raises(ValueError, match="typed_route_missing"):
        _route({"route": None})


@pytest.mark.parametrize(
    ("selection", "code"),
    [
        (None, "implementation_selection_required"),
        ({}, "implementation_map_incomplete"),
        (
            {
                "bootstrap": NodeAdapter(
                    _placeholder_fixture_factory,
                    AdapterKind.FIXTURE,
                    requires_gate=False,
                )
            },
            "implementation_map_incomplete",
        ),
    ],
)
def test_omitted_empty_and_incomplete_adapter_selections_fail_before_graph_construction(selection, code: str) -> None:
    specs = load_research_node_specs()

    with pytest.raises(ImplementationMapError, match=code):
        resolve_implementations(specs, selection)


def test_unknown_duplicate_invalid_and_unavailable_adapter_selections_fail_closed() -> None:
    specs = load_research_node_specs()
    adapters, _ = _fixture_selection()

    unknown = {**adapters, "unknown": adapters["bootstrap"]}
    with pytest.raises(ImplementationMapError, match="implementation_map_unknown"):
        resolve_implementations(specs, unknown)

    duplicate = [*adapters.items(), ("bootstrap", adapters["bootstrap"])]
    with pytest.raises(ImplementationMapError, match="implementation_map_duplicate"):
        resolve_implementations(specs, duplicate)

    invalid = {**adapters, "bootstrap": object()}
    with pytest.raises(ImplementationMapError, match="implementation_adapter_invalid"):
        resolve_implementations(specs, invalid)

    unavailable_specs = {**specs, "bootstrap": replace(specs["bootstrap"], real_factory=UNAVAILABLE_REAL_FACTORY)}
    unavailable = {
        **adapters,
        "bootstrap": NodeAdapter(
            factory=UNAVAILABLE_REAL_FACTORY,
            kind=AdapterKind.REAL,
            requires_gate=False,
        ),
    }
    with pytest.raises(ImplementationMapError, match="implementation_unavailable"):
        resolve_implementations(unavailable_specs, unavailable)


def test_gate_selection_requires_exact_membership_and_matching_phase() -> None:
    adapters, gates = _fixture_selection()

    missing = {name: gate for name, gate in gates.items() if name != "wave0"}
    with pytest.raises(ImplementationMapError, match="gate_definitions_incomplete"):
        build_research_graph(implementations=adapters, gate_defs=missing)

    unknown = {**gates, "unknown": gates["wave0"]}
    with pytest.raises(ImplementationMapError, match="gate_definitions_unknown"):
        build_research_graph(implementations=adapters, gate_defs=unknown)

    extraneous = {**gates, "bootstrap": gates["wave0"]}
    with pytest.raises(ImplementationMapError, match="gate_definitions_extraneous"):
        build_research_graph(implementations=adapters, gate_defs=extraneous)

    mismatched = {**gates, "wave0": gates["wave1"]}
    with pytest.raises(ImplementationMapError, match="gate_definition_mismatch"):
        build_research_graph(implementations=adapters, gate_defs=mismatched)


def test_selected_ungated_real_adapter_cannot_retain_its_fixture_gate() -> None:
    specs = load_research_node_specs()
    adapters, gates = _fixture_selection()
    adapters["readiness"] = all_real_adapters(specs)["readiness"]

    with pytest.raises(ImplementationMapError, match="gate_definitions_extraneous"):
        build_research_graph(implementations=adapters, gate_defs=gates)


def test_test_composition_helper_removes_fixture_gate_for_ungated_real_readiness() -> None:
    recipe = mixed_recipe(
        real_nodes=(
            "bootstrap",
            "hitl1",
            "topic_planning",
            "wave0",
            "targeted_evidence",
            "wave1",
            "wave2_synthesis",
            "hitl2",
            "readiness",
        )
    )

    assert recipe.implementation_mode.value == "mixed"
    assert recipe.builder.compile() is not None


def test_generic_recipe_composition_validates_gate_selection_before_dependency_checks() -> None:
    adapters, _ = _fixture_selection()

    with pytest.raises(ImplementationMapError, match="gate_definitions_incomplete"):
        ResearchGraphRecipe.from_adapters(
            adapters=adapters,
            gate_defs={},
            recipe_revision="fixture-test-v1",
            composition_name="fixture-test",
        )


def test_fixed_all_real_factories_accept_no_mode_or_selection_authority() -> None:
    assert not hasattr(ResearchGraphRecipe, "create")
    parameters = inspect.signature(ResearchGraphRecipe.all_real).parameters
    assert "adapters" not in parameters
    assert "implementations" not in parameters
    assert "implementation_modes" not in parameters
    with pytest.raises(TypeError):
        ResearchGraphRecipe.all_real(implementation_modes={})


def test_real_adapter_selection_is_registered_and_gate_annotated() -> None:
    adapters = all_real_adapters(load_research_node_specs())

    assert tuple(adapters) == LOGICAL_NODES
    assert all(adapter.kind is AdapterKind.REAL for adapter in adapters.values())
    assert {name for name, adapter in adapters.items() if adapter.requires_gate} == {
        "wave0",
        "wave1",
        "wave2_synthesis",
        "final_delivery",
    }
