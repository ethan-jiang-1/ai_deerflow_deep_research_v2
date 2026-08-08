"""Local capability reference for bounded final layout composition."""

from deerflow_deep_research.domain.context import NodeAgentCapabilityRef

FINAL_DELIVERY_COMPOSER = NodeAgentCapabilityRef(
    capability_id="final-delivery-composer",
    package="deerflow_deep_research.graph.nodes.final_delivery",
    resource="capabilities/composer.md",
)

__all__ = ["FINAL_DELIVERY_COMPOSER"]
