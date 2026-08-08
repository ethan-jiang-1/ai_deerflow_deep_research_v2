"""Local capability declarations for Wave1 evidence extraction.

@impl NAC-006
@impl WON-007
"""

from deerflow_deep_research.domain.context import NodeAgentCapabilityRef

WAVE1_EVIDENCE_EXTRACTION = NodeAgentCapabilityRef(
    capability_id="wave1-evidence-extraction",
    package="deerflow_deep_research.graph.nodes.wave1",
    resource="capabilities/wave1-evidence-extraction.md",
)
WAVE1_EVIDENCE_EXTRACTION_REPAIR = NodeAgentCapabilityRef(
    capability_id="wave1-evidence-extraction-repair",
    package="deerflow_deep_research.graph.nodes.wave1",
    resource="capabilities/wave1-evidence-extraction-repair.md",
)
WAVE1_SOURCE_DIAGNOSTIC = NodeAgentCapabilityRef(
    capability_id="wave1-source-diagnostic",
    package="deerflow_deep_research.graph.nodes.wave1",
    resource="capabilities/wave1-source-diagnostic.md",
)
WAVE1_CLAIM_VERIFIER = NodeAgentCapabilityRef(
    capability_id="wave1-claim-verifier",
    package="deerflow_deep_research.graph.nodes.wave1",
    resource="capabilities/wave1-claim-verifier.md",
)

__all__ = [
    "WAVE1_CLAIM_VERIFIER",
    "WAVE1_EVIDENCE_EXTRACTION",
    "WAVE1_EVIDENCE_EXTRACTION_REPAIR",
    "WAVE1_SOURCE_DIAGNOSTIC",
]
