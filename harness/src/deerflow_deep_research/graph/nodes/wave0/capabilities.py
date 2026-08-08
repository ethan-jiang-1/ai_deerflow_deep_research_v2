"""Local capability declarations for Wave0 source intake.

@impl NAC-003
"""

from deerflow_deep_research.domain.context import NodeAgentCapabilityRef

WAVE0_AUTHORITATIVE_SOURCE_INTAKE = NodeAgentCapabilityRef(
    capability_id="wave0-authoritative-source-intake",
    package="deerflow_deep_research.graph.nodes.wave0",
    resource="capabilities/wave0-authoritative-source-intake.md",
)
WAVE0_SOURCE_INTAKE_REPAIR = NodeAgentCapabilityRef(
    capability_id="wave0-source-intake-repair",
    package="deerflow_deep_research.graph.nodes.wave0",
    resource="capabilities/wave0-source-intake-repair.md",
)

__all__ = ["WAVE0_AUTHORITATIVE_SOURCE_INTAKE", "WAVE0_SOURCE_INTAKE_REPAIR"]
