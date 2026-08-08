from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.state import node_state_update


def build_fixture(_dependencies: NodeBuildDependencies):
    async def run(_state):
        return node_state_update("readiness")

    return run
