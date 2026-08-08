from deerflow_deep_research.domain.lifecycle import LifecycleStatus, TerminalReason
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.state import PhaseStatus, node_state_update

_MAX_RERUN_GENERATIONS = 2


def build_fixture(_dependencies: NodeBuildDependencies):
    async def run(state):
        generation = int(state.get("generation", 0))
        if generation >= _MAX_RERUN_GENERATIONS:
            return node_state_update(
                "rerun",
                route="exhausted",
                terminal_status=LifecycleStatus.BLOCKED.value,
                phase_status=PhaseStatus.TERMINAL.value,
                terminal_reason=TerminalReason.RERUN_EXHAUSTED.value,
            )
        return node_state_update("rerun", route="next", generation=generation + 1, repair_counts={})

    return run
