"""Local capability declaration for the readiness evidence critic.

@impl REA-002
@impl REA-006
"""

from deerflow_deep_research.domain.context import NodeAgentCapabilityRef

READINESS_EVIDENCE_CRITIC = NodeAgentCapabilityRef(
    capability_id="readiness-evidence-critic",
    package="deerflow_deep_research.graph.nodes.readiness",
    resource="capabilities/readiness-evidence-critic.md",
)

__all__ = ["READINESS_EVIDENCE_CRITIC"]
