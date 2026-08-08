"""Pure final phase-agent prompt rendering.

@impl NPC-001
@impl NAC-002
"""

from __future__ import annotations

from deerflow_deep_research.agents.capabilities import load_node_agent_capability
from deerflow_deep_research.agents.phase_prompt import render_phase_agent_prompt
from deerflow_deep_research.domain.context import ArtifactRef, NodeExecutionRequest
from deerflow_deep_research.graph.nodes.hitl1.capabilities import HITL1_SEMANTIC_INTAKE


def test_renderer_projects_the_exact_policy_and_final_human_message() -> None:
    rendered = render_phase_agent_prompt(
        NodeExecutionRequest(
            objective="Summarize the assigned evidence.",
            expected_output="One JSON object.",
            source_artifact_refs=(ArtifactRef(artifact_id="source-1", virtual_path="/mnt/work/source-1.json"),),
        ),
        attempt_workspace="/mnt/work/attempts/a1",
    )

    assert "Deep Research Phase Agent" in rendered.system_policy
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
    rendered = render_phase_agent_prompt(
        NodeExecutionRequest(objective="Produce a bounded answer.", expected_output="One result."),
        attempt_workspace="/mnt/work/attempts/a1",
    )

    assert "Deep Research Phase Agent" in rendered.system_policy
    assert rendered.user_message.endswith("Attempt workspace (virtual): /mnt/work/attempts/a1\n")


def test_renderer_composes_a_declared_local_capability_after_base_policy() -> None:
    rendered = render_phase_agent_prompt(
        NodeExecutionRequest(
            objective="classify one reply",
            expected_output="one candidate",
            tools_enabled=False,
            capability_binding="required",
            capability_ref=HITL1_SEMANTIC_INTAKE,
        ),
        attempt_workspace="/mnt/work/attempts/a1",
    )

    assert rendered.capability is not None
    assert rendered.capability.ref == HITL1_SEMANTIC_INTAKE
    capability = load_node_agent_capability(HITL1_SEMANTIC_INTAKE)
    assert rendered.capability == capability
    assert rendered.system_policy.index("Deep Research Phase Agent") < rendered.system_policy.index(
        capability.policy.strip()
    )
