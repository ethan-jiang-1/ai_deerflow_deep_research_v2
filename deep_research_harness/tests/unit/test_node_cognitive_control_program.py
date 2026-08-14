"""Pure final node-agent prompt rendering.

@impl NPC-001
@impl NAC-002
"""

from __future__ import annotations

import pytest

from deerflow_deep_research.agents import capabilities as capability_loader
from deerflow_deep_research.agents.capabilities import CapabilityResourceError, load_node_agent_capability
from deerflow_deep_research.agents.node_cognitive_control_program import render_node_cognitive_control_program
from deerflow_deep_research.domain.context import ArtifactRef, NodeAgentCapabilityRef, NodeExecutionRequest
from deerflow_deep_research.graph.nodes.hitl1.capabilities import HITL1_SEMANTIC_INTAKE


def _declared_request() -> NodeExecutionRequest:
    return NodeExecutionRequest(
        objective="classify one reply",
        expected_output="one candidate",
        tools_enabled=False,
        capability_ref=HITL1_SEMANTIC_INTAKE,
    )


def test_renderer_projects_the_exact_policy_and_final_human_message() -> None:
    rendered = render_node_cognitive_control_program(
        NodeExecutionRequest(
            objective="Summarize the assigned evidence.",
            expected_output="One JSON object.",
            source_artifact_refs=(ArtifactRef(artifact_id="source-1", virtual_path="/mnt/work/source-1.json"),),
            tools_enabled=False,
            capability_ref=HITL1_SEMANTIC_INTAKE,
        ),
        attempt_workspace="/mnt/work/attempts/a1",
    )

    assert "Deep Research Node Cognitive Control Program" in rendered.system_policy
    assert rendered.user_message == (
        "Objective: Summarize the assigned evidence.\n"
        "Expected output: One JSON object.\n"
        "Attempt workspace (virtual): /mnt/work/attempts/a1\n"
        "\n"
        "<untrusted-source-data>\n"
        "- source-1: /mnt/work/source-1.json\n"
        "</untrusted-source-data>\n"
    )


def test_renderer_loads_the_package_policy_without_runtime_configuration() -> None:
    rendered = render_node_cognitive_control_program(
        NodeExecutionRequest(
            objective="Produce a bounded answer.",
            expected_output="One result.",
            tools_enabled=False,
            capability_ref=HITL1_SEMANTIC_INTAKE,
        ),
        attempt_workspace="/mnt/work/attempts/a1",
    )

    assert "Deep Research Node Cognitive Control Program" in rendered.system_policy
    assert rendered.user_message.endswith("Attempt workspace (virtual): /mnt/work/attempts/a1\n")


def test_renderer_composes_a_declared_local_capability_after_base_policy() -> None:
    rendered = render_node_cognitive_control_program(
        _declared_request(),
        attempt_workspace="/mnt/work/attempts/a1",
    )

    assert rendered.capability is not None
    assert rendered.capability.ref == HITL1_SEMANTIC_INTAKE
    capability = load_node_agent_capability(HITL1_SEMANTIC_INTAKE)
    assert rendered.capability == capability
    assert rendered.system_policy.index("Deep Research Node Cognitive Control Program") < rendered.system_policy.index(
        capability.policy.strip()
    )


@pytest.mark.parametrize(
    ("capability_ref", "error"),
    [
        pytest.param(None, "capability_ref_invalid", id="missing"),
        pytest.param(object(), "capability_ref_invalid", id="malformed"),
        pytest.param(
            NodeAgentCapabilityRef(
                capability_id="unknown-node-capability",
                package="deerflow_deep_research.graph.nodes.unknown_node",
                resource="capabilities/unknown.md",
            ),
            "capability_resource_missing",
            id="unknown-package",
        ),
        pytest.param(
            NodeAgentCapabilityRef(
                capability_id="hitl1-semantic-intake",
                package="deerflow_deep_research.graph.nodes.hitl1",
                resource="capabilities/not-present.md",
            ),
            "capability_resource_missing",
            id="missing-resource",
        ),
    ],
)
def test_renderer_rejects_bypassed_invalid_capability_refs_before_projection(
    capability_ref: object,
    error: str,
) -> None:
    request = _declared_request().model_copy(update={"capability_ref": capability_ref})

    with pytest.raises(CapabilityResourceError, match=error):
        render_node_cognitive_control_program(request, attempt_workspace="/mnt/work/attempts/a1")


def test_renderer_rejects_metadata_id_mismatch_before_projection(monkeypatch: pytest.MonkeyPatch) -> None:
    class Resource:
        def joinpath(self, _resource: str) -> Resource:
            return self

        def read_text(self, *, encoding: str) -> str:
            assert encoding == "utf-8"
            return (
                '<!-- node-agent-capability: {"schema_version":1,"capability_id":"different-id",'
                '"role":"intake","method":"classify","authority_limit":"advisory",'
                '"completion_condition":"json","uncertainty_boundary":"preserve uncertainty",'
                '"tool_posture":{"kind":"forbidden"}} -->\npolicy'
            )

    monkeypatch.setattr(capability_loader.importlib.resources, "files", lambda _package: Resource())

    with pytest.raises(CapabilityResourceError, match="capability_id_mismatch"):
        render_node_cognitive_control_program(_declared_request(), attempt_workspace="/mnt/work/attempts/a1")
