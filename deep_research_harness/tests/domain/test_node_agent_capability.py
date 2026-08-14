"""Node-local capability reference and resource-admission contracts.

@impl NAC-001
@impl NAC-003
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from deerflow_deep_research.agents import capabilities as capability_loader
from deerflow_deep_research.agents.capabilities import CapabilityResourceError, load_node_agent_capability
from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef
from deerflow_deep_research.domain.context import (
    NodeAgentBundleContext,
    NodeAgentCapabilityRef,
    NodeExecutionRequest,
    SelectedBundleContext,
)
from deerflow_deep_research.graph.nodes.hitl1.capabilities import (
    HITL1_PROFILE_BRIEF,
    HITL1_PROFILE_BRIEF_REPAIR,
    HITL1_SEMANTIC_INTAKE,
)
from deerflow_deep_research.graph.nodes.topic_planning.capabilities import (
    TOPIC_PLANNING_PLAN_REPAIR,
    TOPIC_PLANNING_PROFILE_DECOMPOSITION,
)
from deerflow_deep_research.graph.nodes.wave0.capabilities import WAVE0_AUTHORITATIVE_SOURCE_INTAKE
from deerflow_deep_research.graph.nodes.wave2_synthesis.capabilities import WAVE2_EVIDENCE_SYNTHESIS


def _request(**overrides: object) -> NodeExecutionRequest:
    values: dict[str, object] = {"capability_ref": HITL1_SEMANTIC_INTAKE}
    values.update(overrides)
    return NodeExecutionRequest(objective="bounded assignment", expected_output="one result", **values)


@pytest.mark.parametrize(
    ("package", "resource"),
    [
        ("other.package", "capabilities/policy.md"),
        ("deerflow_deep_research.graph.nodes.hitl1", "/capabilities/policy.md"),
        ("deerflow_deep_research.graph.nodes.hitl1", "capabilities/../policy.md"),
        ("deerflow_deep_research.graph.nodes.hitl1", "capabilities/policy.txt"),
    ],
)
def test_ref_rejects_escaping_or_non_node_local_resources(package: str, resource: str) -> None:
    with pytest.raises(ValidationError):
        NodeAgentCapabilityRef(capability_id="bounded-policy", package=package, resource=resource)


def test_request_requires_one_capability_ref_at_construction() -> None:
    with pytest.raises(ValidationError, match="capability_ref"):
        NodeExecutionRequest(objective="bounded assignment", expected_output="one result")

    assert _request().capability_ref == HITL1_SEMANTIC_INTAKE


def test_node_agent_bundle_context_drops_scope_and_locator_authority() -> None:
    selected = SelectedBundleContext(
        bundle=RunBundleRef(
            bundle_id=BundleId("b_" + "A" * 43),
            scope_bucket="s_" + "B" * 43,
        )
    )

    context = NodeAgentBundleContext.from_selected_bundle(selected)

    assert context.bundle_id == selected.bundle.bundle_id
    assert set(NodeAgentBundleContext.model_fields) == {"bundle_id"}
    assert "scope_bucket" not in context.model_dump_json()


@pytest.mark.parametrize("field", ["bundle_path", "checkpoint", "state_writer", "lifecycle_action"])
def test_node_agent_bundle_context_rejects_lifecycle_authority_fields(field: str) -> None:
    with pytest.raises(ValidationError):
        NodeAgentBundleContext(bundle_id=BundleId("b_" + "A" * 43), **{field: "forged"})


@pytest.mark.parametrize("field", ["bundle_id", "bundle_path", "checkpoint", "state_writer", "lifecycle_action"])
def test_node_agent_request_rejects_bundle_control_overrides(field: str) -> None:
    with pytest.raises(ValidationError):
        _request(**{field: "forged"})


def test_local_resources_load_matching_closed_postures() -> None:
    hitl = load_node_agent_capability(HITL1_SEMANTIC_INTAKE)
    wave0 = load_node_agent_capability(WAVE0_AUTHORITATIVE_SOURCE_INTAKE)
    wave2 = load_node_agent_capability(WAVE2_EVIDENCE_SYNTHESIS)

    assert hitl.posture.kind == "forbidden"
    assert wave0.posture.kind == "required"
    assert "web_search" in wave0.posture.allowed_tool_names
    assert wave2.posture.kind == "forbidden"
    assert "route" in hitl.policy and "accepted evidence" in wave2.policy


def test_profile_brief_resources_are_distinct_local_forbidden_capabilities() -> None:
    normal = load_node_agent_capability(HITL1_PROFILE_BRIEF)
    repair = load_node_agent_capability(HITL1_PROFILE_BRIEF_REPAIR)

    assert (normal.ref.capability_id, normal.ref.package, normal.ref.resource) == (
        "hitl1-profile-brief",
        "deerflow_deep_research.graph.nodes.hitl1",
        "capabilities/hitl1-profile-brief.md",
    )
    assert (repair.ref.capability_id, repair.ref.package, repair.ref.resource) == (
        "hitl1-profile-brief-repair",
        "deerflow_deep_research.graph.nodes.hitl1",
        "capabilities/hitl1-profile-brief-repair.md",
    )
    assert normal.posture.kind == repair.posture.kind == "forbidden"
    assert "advisory" in normal.policy.lower()
    assert "repair" in repair.policy.lower()


def test_topic_planning_resources_declare_their_distinct_cognitive_methods() -> None:
    """TOP-006: the local resources, not Python, name reusable planning method."""
    initial = load_node_agent_capability(TOPIC_PLANNING_PROFILE_DECOMPOSITION)
    repair = load_node_agent_capability(TOPIC_PLANNING_PLAN_REPAIR)

    assert initial.posture.kind == repair.posture.kind == "forbidden"
    assert "decomposition method" in initial.policy.lower()
    assert "scope_boundaries" in initial.policy
    assert "custom_notes" in initial.policy
    assert "current_round_direction" in initial.policy
    assert "self-check" in initial.policy.lower()
    assert "repair method" in repair.policy.lower()
    assert "same assignment" in repair.policy.lower()
    assert "validation feedback" in repair.policy.lower()
    assert "self-check" in repair.policy.lower()


def test_profile_brief_metadata_rejects_lifecycle_authority(monkeypatch: pytest.MonkeyPatch) -> None:
    class Resource:
        def joinpath(self, _resource: str) -> Resource:
            return self

        def read_text(self, *, encoding: str) -> str:
            assert encoding == "utf-8"
            return (
                '<!-- node-agent-capability: {"schema_version":1,"capability_id":"hitl1-profile-brief",'
                '"role":"brief","method":"draft","authority_limit":"advisory",'
                '"completion_condition":"json","uncertainty_boundary":"preserve uncertainty",'
                '"tool_posture":{"kind":"forbidden"},"route":"accepted"} -->\npolicy'
            )

    monkeypatch.setattr(capability_loader.importlib.resources, "files", lambda _package: Resource())

    with pytest.raises(CapabilityResourceError, match="capability_metadata_invalid"):
        load_node_agent_capability(HITL1_PROFILE_BRIEF)
