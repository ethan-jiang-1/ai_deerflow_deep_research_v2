from deerflow_deep_research.domain.enums import NodePhase
from deerflow_deep_research.domain.node_spec import NodeContracts, NodeSpec, PolicyRef

from .contracts import CONTRACTS as _CONTRACTS
from .node import build_real as _build_real

NODE_SPEC = NodeSpec(
    logical_name="rerun",
    phase=NodePhase.ORCHESTRATION,
    policy=PolicyRef(name="skeleton-rerun", version="v1"),
    contracts=NodeContracts(request_type=_CONTRACTS[0], result_type=_CONTRACTS[1]),
    real_factory=_build_real,
)
__all__ = ["NODE_SPEC"]
