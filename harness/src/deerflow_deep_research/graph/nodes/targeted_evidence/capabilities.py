"""Local capability declarations for the targeted evidence evaluation loop.

@impl NAC-007
"""

from deerflow_deep_research.domain.context import NodeAgentCapabilityRef

_PACKAGE = "deerflow_deep_research.graph.nodes.targeted_evidence"

TARGETED_GAP_EVIDENCE_RETRIEVAL = NodeAgentCapabilityRef(
    capability_id="targeted-gap-evidence-retrieval",
    package=_PACKAGE,
    resource="capabilities/targeted-gap-evidence-retrieval.md",
)
TARGETED_GAP_EVIDENCE_REPAIR = NodeAgentCapabilityRef(
    capability_id="targeted-gap-evidence-repair",
    package=_PACKAGE,
    resource="capabilities/targeted-gap-evidence-repair.md",
)
TARGETED_SOURCE_DIAGNOSTIC = NodeAgentCapabilityRef(
    capability_id="targeted-source-diagnostic",
    package=_PACKAGE,
    resource="capabilities/targeted-source-diagnostic.md",
)
TARGETED_CLAIM_VERIFIER = NodeAgentCapabilityRef(
    capability_id="targeted-claim-verifier",
    package=_PACKAGE,
    resource="capabilities/targeted-claim-verifier.md",
)

__all__ = [
    "TARGETED_CLAIM_VERIFIER",
    "TARGETED_GAP_EVIDENCE_REPAIR",
    "TARGETED_GAP_EVIDENCE_RETRIEVAL",
    "TARGETED_SOURCE_DIAGNOSTIC",
]
