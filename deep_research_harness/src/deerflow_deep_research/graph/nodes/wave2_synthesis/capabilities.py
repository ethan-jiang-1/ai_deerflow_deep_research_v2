"""Local capability declarations for Wave2 accepted-evidence synthesis.

@impl NAC-003
"""

from deerflow_deep_research.domain.context import NodeAgentCapabilityRef

WAVE2_EVIDENCE_SYNTHESIS = NodeAgentCapabilityRef(
    capability_id="wave2-evidence-synthesis",
    package="deerflow_deep_research.graph.nodes.wave2_synthesis",
    resource="capabilities/wave2-evidence-synthesis.md",
)
WAVE2_EVIDENCE_SYNTHESIS_REPAIR = NodeAgentCapabilityRef(
    capability_id="wave2-evidence-synthesis-repair",
    package="deerflow_deep_research.graph.nodes.wave2_synthesis",
    resource="capabilities/wave2-evidence-synthesis-repair.md",
)

__all__ = ["WAVE2_EVIDENCE_SYNTHESIS", "WAVE2_EVIDENCE_SYNTHESIS_REPAIR"]
