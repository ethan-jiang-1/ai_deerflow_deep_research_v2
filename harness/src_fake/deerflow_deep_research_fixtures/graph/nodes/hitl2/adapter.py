from deerflow_deep_research.domain.lifecycle import Hitl2Decision, LifecycleStatus
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.state import PhaseStatus, node_state_update
from deerflow_deep_research_fixtures.routing import scenario_route
from deerflow_deep_research_fixtures.scenario import FixtureScenario


def build_fixture(scenario: FixtureScenario):
    def factory(_dependencies: NodeBuildDependencies):
        async def run(state):
            decision = Hitl2Decision(scenario_route(state, scenario=scenario, logical_name="hitl2"))
            updates = {}
            if decision is Hitl2Decision.STOP:
                updates = {
                    "terminal_status": LifecycleStatus.STOPPED.value,
                    "phase_status": PhaseStatus.TERMINAL.value,
                }
            return node_state_update("hitl2", route=decision.value, **updates)

        return run

    return factory
