"""Source-faithful final prompt rendering for bounded node-agents.

The runtime owns invocation context, while this module owns only the prompt text
shared by runtime execution and deterministic review projections.

@impl NPC-001
"""

from __future__ import annotations

from dataclasses import dataclass

from deerflow_deep_research.agents.capabilities import LoadedNodeAgentCapability, load_node_agent_capability
from deerflow_deep_research.agents.prompts import build_untrusted_data_block, load_policy_prompt
from deerflow_deep_research.domain.context import NodeExecutionRequest


@dataclass(frozen=True)
class RenderedNodeCognitiveControlProgram:
    """The exact trusted system text and human message for one LLM-Bearing Node request."""

    system_policy: str
    user_message: str
    capability: LoadedNodeAgentCapability
    base_policy: str = ""


def render_node_cognitive_control_program(
    request: NodeExecutionRequest,
    *,
    attempt_workspace: str,
) -> RenderedNodeCognitiveControlProgram:
    """Render one node-agent prompt without resolving runtime execution authority."""

    if not isinstance(request, NodeExecutionRequest):
        raise TypeError("node_cognitive_control_program_request_invalid")
    if not isinstance(attempt_workspace, str) or not attempt_workspace.strip():
        raise ValueError("node_cognitive_control_program_attempt_workspace_invalid")
    capability = load_node_agent_capability(request.capability_ref)
    resolved_policy = load_policy_prompt()
    resolved_policy = f"{resolved_policy.rstrip()}\n\n{capability.policy.strip()}\n"
    prompt = (
        f"Objective: {request.objective}\n"
        f"Expected output: {request.expected_output}\n"
        f"Attempt workspace (virtual): {attempt_workspace}\n"
    )
    if request.source_artifact_refs:
        listed = [f"- {ref.artifact_id}: {ref.virtual_path}" for ref in request.source_artifact_refs]
        prompt += f"\n{build_untrusted_data_block(listed)}\n"
    return RenderedNodeCognitiveControlProgram(
        system_policy=resolved_policy,
        user_message=prompt,
        capability=capability,
        base_policy=load_policy_prompt(),
    )


__all__ = ["RenderedNodeCognitiveControlProgram", "render_node_cognitive_control_program"]
