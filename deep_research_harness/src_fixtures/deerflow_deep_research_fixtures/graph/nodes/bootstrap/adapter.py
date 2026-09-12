from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.state import node_state_update
from deerflow_deep_research_fixtures.routing import scenario_route
from deerflow_deep_research_fixtures.scenario import FixtureScenario


def build_fixture(scenario: FixtureScenario):
    def factory(_dependencies: NodeBuildDependencies):
        async def run(state):
            return node_state_update(
                "bootstrap",
                route=scenario_route(state, scenario=scenario, logical_name="bootstrap"),
            )

        return run

    return factory
