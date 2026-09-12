from datetime import UTC, datetime

from deerflow_deep_research.domain.node_spec import NodeBuildDependencies, PolicyRef
from deerflow_deep_research.domain.state import node_state_update
from deerflow_deep_research.domain.work_units import WORK_UNIT_GATE_VIEW_KEY
from deerflow_deep_research.engine.work_units.kernel import WorkIntent
from deerflow_deep_research_fixtures.work_units import run_fixture_work_unit_component

_INTENTS = tuple(
    WorkIntent(
        worker_role="fixture_worker",
        scope=(f"wave1:fixture:{index}",),
        result_contract="fixture.work-unit",
        result_schema_version=1,
        required_outputs=("fixture.json",),
    )
    for index in range(3)
)


def build_fixture(dependencies: NodeBuildDependencies):
    if dependencies.work_units is None:
        raise ValueError("work_unit_capability_missing")

    async def run(state):
        result = await run_fixture_work_unit_component(
            state,
            logical_name="wave1",
            policy=PolicyRef(name="fixture-wave1", version="v1"),
            controller=dependencies.work_units,
            intents=_INTENTS,
            clock=lambda: datetime(2026, 1, 2, tzinfo=UTC),
            event_recorder=dependencies.event_recorder,
        )
        return {
            **node_state_update("wave1"),
            **result.parent_update,
            WORK_UNIT_GATE_VIEW_KEY: result.gate_view,
        }

    return run
