"""Local capability declarations for HITL1 profile and semantic interpretation.

@impl NAC-003
@impl NAC-005
"""

from deerflow_deep_research.domain.context import NodeAgentCapabilityRef

HITL1_PROFILE_BRIEF = NodeAgentCapabilityRef(
    capability_id="hitl1-profile-brief",
    package="deerflow_deep_research.graph.nodes.hitl1",
    resource="capabilities/hitl1-profile-brief.md",
)
HITL1_PROFILE_BRIEF_REPAIR = NodeAgentCapabilityRef(
    capability_id="hitl1-profile-brief-repair",
    package="deerflow_deep_research.graph.nodes.hitl1",
    resource="capabilities/hitl1-profile-brief-repair.md",
)
HITL1_SEMANTIC_INTAKE = NodeAgentCapabilityRef(
    capability_id="hitl1-semantic-intake",
    package="deerflow_deep_research.graph.nodes.hitl1",
    resource="capabilities/hitl1-semantic-intake.md",
)
HITL1_SEMANTIC_INTAKE_REPAIR = NodeAgentCapabilityRef(
    capability_id="hitl1-semantic-intake-repair",
    package="deerflow_deep_research.graph.nodes.hitl1",
    resource="capabilities/hitl1-semantic-intake-repair.md",
)

__all__ = [
    "HITL1_PROFILE_BRIEF",
    "HITL1_PROFILE_BRIEF_REPAIR",
    "HITL1_SEMANTIC_INTAKE",
    "HITL1_SEMANTIC_INTAKE_REPAIR",
]
