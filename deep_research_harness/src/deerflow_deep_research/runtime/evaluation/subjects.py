"""Narrow adapters from declared Cases to already-built production node branches.

These adapters deliberately receive a callable constructed by the owning production
runtime. They do not copy prompts, parser logic, admission, recovery, or graph routes.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import Any

from .contracts import SubjectExecution
from .runner import ExecutionContext, Subject

ProductionBranch = Callable[[Mapping[str, Any]], Awaitable[Mapping[str, Any]]]
StateFactory = Callable[[Mapping[str, Any], ExecutionContext], Mapping[str, Any]]
ScenarioStateFactory = Callable[[Mapping[str, Any], Mapping[str, Any], ExecutionContext], Mapping[str, Any]]
ScenarioDependenciesFactory = Callable[[Mapping[str, Any], Mapping[str, Any], ExecutionContext], Any]
ScenarioExpectedFailureFactory = Callable[[Mapping[str, Any], Exception, ExecutionContext], Mapping[str, Any] | None]
ResourceUseFactory = Callable[[ExecutionContext, Mapping[str, Any]], Mapping[str, int | float | str | bool]]


def production_branch_subject(
    *,
    subject: str,
    branch: ProductionBranch,
    state_factory: StateFactory,
    resource_use_factory: ResourceUseFactory | None = None,
) -> Subject:
    """Adapt one existing, already-built production branch to the Runner protocol."""

    async def invoke(context: ExecutionContext) -> SubjectExecution:
        context.observe("branch.invoked", {"subject": subject})
        try:
            update = await branch(state_factory(context.fixture, context))
        except Exception as exc:
            context.observe("branch.failed", {"exception_type": type(exc).__name__})
            raise
        if not isinstance(update, Mapping):
            raise ValueError("production_branch_result_invalid")
        context.observe("branch.returned", {"subject": subject, "update_keys": sorted(map(str, update.keys()))})
        return SubjectExecution(
            output={"state_update": dict(update)},
            artifacts={},
            resource_use=dict(resource_use_factory(context, update)) if resource_use_factory is not None else {},
        )

    return invoke


def production_node_subject(
    *,
    subject: str,
    node_spec: Any,
    dependencies: Any,
    state_factory: StateFactory,
    resource_use_factory: ResourceUseFactory | None = None,
) -> Subject:
    """Use the registered production factory without reproducing its node implementation."""

    branch = node_spec.real_factory(dependencies)
    return production_branch_subject(
        subject=subject,
        branch=branch,
        state_factory=state_factory,
        resource_use_factory=resource_use_factory,
    )


def production_scenario_node_subject(
    *,
    subject: str,
    node_spec: Any,
    dependencies_factory: ScenarioDependenciesFactory,
    state_factory: ScenarioStateFactory,
    expected_failure_factory: ScenarioExpectedFailureFactory | None = None,
    resource_use_factory: ResourceUseFactory | None = None,
) -> Subject:
    """Run each declared bounded scenario through one registered production node factory.

    A fixture may declare one expected deterministic rejection. The adapter records
    only the supplied bounded replacement update; all other production exceptions
    still fail the execution.
    """

    async def invoke(context: ExecutionContext) -> SubjectExecution:
        scenarios = context.fixture.get("scenarios")
        if not isinstance(scenarios, list) or not scenarios:
            raise ValueError("evaluation_scenarios_missing")
        updates: list[dict[str, Any]] = []
        for scenario in scenarios:
            if not isinstance(scenario, Mapping):
                raise ValueError("evaluation_scenario_invalid")
            scenario_id = scenario.get("scenario_id")
            if not isinstance(scenario_id, str) or not scenario_id:
                raise ValueError("evaluation_scenario_id_invalid")
            context.observe("scenario.invoked", {"subject": subject, "scenario_id": scenario_id})
            branch = node_spec.real_factory(dependencies_factory(scenario, context.fixture, context))
            try:
                update = await branch(state_factory(scenario, context.fixture, context))
            except Exception as exc:
                if expected_failure_factory is None:
                    raise
                update = expected_failure_factory(scenario, exc, context)
                if update is None:
                    raise
                context.observe(
                    "scenario.expected_failure",
                    {
                        "subject": subject,
                        "scenario_id": scenario_id,
                        "exception_type": type(exc).__name__,
                    },
                )
            if not isinstance(update, Mapping):
                raise ValueError("production_branch_result_invalid")
            updates.append({"scenario_id": scenario_id, "state_update": dict(update)})
            context.observe("scenario.returned", {"subject": subject, "scenario_id": scenario_id})
        aggregate = {"scenario_updates": updates}
        return SubjectExecution(
            output=aggregate,
            artifacts={},
            resource_use=dict(resource_use_factory(context, aggregate)) if resource_use_factory is not None else {},
        )

    return invoke
