from deerflow_deep_research.domain.enums import NodePhase
from deerflow_deep_research.domain.node_spec import NodeCapability, NodeContracts, NodeSpec, PolicyRef

from .contracts import CONTRACTS as _CONTRACTS
from .node import build_real as _build_real

NODE_SPEC = NodeSpec(
    logical_name="final_delivery",
    phase=NodePhase.PUBLICATION,
    policy=PolicyRef(name="final-delivery-composer", version="v1"),
    contracts=NodeContracts(request_type=_CONTRACTS[0], result_type=_CONTRACTS[1]),
    real_factory=_build_real,
    capabilities=frozenset({NodeCapability.PUBLICATION_BUNDLE, NodeCapability.FINAL_DELIVERY_BUNDLE}),
)
__all__ = ["NODE_SPEC"]
