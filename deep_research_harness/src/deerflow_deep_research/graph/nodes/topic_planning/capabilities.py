"""Local capability declarations for bounded topic planning.

@impl NAC-006
@impl TOP-006
"""

from deerflow_deep_research.domain.context import NodeAgentCapabilityRef

TOPIC_PLANNING_PROFILE_DECOMPOSITION = NodeAgentCapabilityRef(
    capability_id="topic-planning-profile-decomposition",
    package="deerflow_deep_research.graph.nodes.topic_planning",
    resource="capabilities/topic-planning-profile-decomposition.md",
)
TOPIC_PLANNING_PLAN_REPAIR = NodeAgentCapabilityRef(
    capability_id="topic-planning-plan-repair",
    package="deerflow_deep_research.graph.nodes.topic_planning",
    resource="capabilities/topic-planning-plan-repair.md",
)

__all__ = ["TOPIC_PLANNING_PLAN_REPAIR", "TOPIC_PLANNING_PROFILE_DECOMPOSITION"]
