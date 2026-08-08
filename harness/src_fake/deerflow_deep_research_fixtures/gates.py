"""Fixture-only deterministic gate definitions."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from deerflow_deep_research.domain.failure_codes import FailureCode
from deerflow_deep_research.domain.gate import Failure, GateDefinition, GateRule, PhaseVerdict
from deerflow_deep_research.domain.lifecycle import completed_visits
from deerflow_deep_research.engine.work_units.kernel import WorkUnitCompletionRule

from .scenario import FixtureScenario


class FixtureSequenceRule:
    def __init__(
        self,
        *,
        scenario: FixtureScenario,
        pass_values: frozenset[str],
        failure_code_map: Mapping[str, FailureCode],
        phase: str,
    ) -> None:
        self._scenario = scenario
        self._pass_values = pass_values
        self._failure_code_map = dict(failure_code_map)
        self._phase = phase

    def evaluate(self, state: Mapping[str, Any]) -> Failure | None:
        value = self._scenario.value_for_visit(self._phase, completed_visits(state, self._phase))
        if value in self._pass_values:
            return None
        code = self._failure_code_map.get(value)
        if code is None:
            return None
        return Failure(code=code, rule_name="fixture_sequence", description=f"fixture: {value}")


def _fixture_rule(
    scenario: FixtureScenario,
    phase: str,
    pass_values: frozenset[str],
    failure_code_map: Mapping[str, FailureCode],
) -> GateRule:
    instance = FixtureSequenceRule(
        scenario=scenario,
        phase=phase,
        pass_values=pass_values,
        failure_code_map=failure_code_map,
    )
    return GateRule(
        name=f"fixture_sequence_{phase}",
        evaluate=instance.evaluate,
        failure_code=next(iter(failure_code_map.values()), FailureCode.WORK_FAILED),
    )


def _work_unit_completion_rule() -> GateRule:
    instance = WorkUnitCompletionRule()
    return GateRule(name=instance.name, evaluate=instance.evaluate, failure_code=instance.failure_code)


def _wave_route_map() -> dict[PhaseVerdict, str]:
    return {
        PhaseVerdict.PASS: "pass",
        PhaseVerdict.REPAIR: "repair",
        PhaseVerdict.BLOCKED: "exhausted",
    }


def _synthesis_route_map() -> dict[PhaseVerdict, str]:
    return {
        PhaseVerdict.PASS: "pass",
        PhaseVerdict.REPAIR: "evidence_needed",
        PhaseVerdict.BLOCKED: "exhausted",
    }


def _readiness_route(verdict: PhaseVerdict, failures: tuple[Failure, ...]) -> str:
    if verdict is PhaseVerdict.PASS:
        return "pass"
    if verdict is PhaseVerdict.BLOCKED:
        return "exhausted"
    routes = {
        FailureCode.REPAIR_TARGETED: "repair_targeted",
        FailureCode.REPAIR_SYNTHESIS: "repair_synthesis",
        FailureCode.REPAIR_HITL2: "repair_hitl2",
    }
    for failure in failures:
        if failure.code in routes:
            return routes[failure.code]
    return "repair_targeted"


def _final_delivery_route(verdict: PhaseVerdict, failures: tuple[Failure, ...]) -> str:
    if verdict is PhaseVerdict.PASS:
        return "pass"
    if verdict is PhaseVerdict.BLOCKED:
        return "exhausted"
    for failure in failures:
        if failure.code is FailureCode.EVIDENCE_INSUFFICIENT:
            return "evidence_blocked"
    return "repair"


def build_fixture_gate_definitions(scenario: FixtureScenario) -> dict[str, GateDefinition]:
    """Build the complete gate map for one immutable fixture scenario."""

    return {
        "wave0": GateDefinition(
            phase="wave0",
            rules=(
                _work_unit_completion_rule(),
                _fixture_rule(scenario, "wave0", frozenset({"pass"}), {"repair": FailureCode.WORK_FAILED}),
            ),
            default_budget=3,
            route_map=_wave_route_map(),
        ),
        "wave1": GateDefinition(
            phase="wave1",
            rules=(
                _work_unit_completion_rule(),
                _fixture_rule(scenario, "wave1", frozenset({"pass"}), {"repair": FailureCode.WORK_FAILED}),
            ),
            default_budget=3,
            route_map=_wave_route_map(),
        ),
        "wave2_synthesis": GateDefinition(
            phase="wave2_synthesis",
            rules=(
                _fixture_rule(
                    scenario,
                    "wave2_synthesis",
                    frozenset({"pass"}),
                    {"evidence_needed": FailureCode.MISSING_EVIDENCE},
                ),
            ),
            default_budget=3,
            route_map=_synthesis_route_map(),
        ),
        "readiness": GateDefinition(
            phase="readiness",
            rules=(
                _fixture_rule(
                    scenario,
                    "readiness",
                    frozenset({"pass"}),
                    {
                        "repair_targeted": FailureCode.REPAIR_TARGETED,
                        "repair_synthesis": FailureCode.REPAIR_SYNTHESIS,
                        "repair_hitl2": FailureCode.REPAIR_HITL2,
                    },
                ),
            ),
            default_budget=3,
            route_resolver=_readiness_route,
        ),
        "final_delivery": GateDefinition(
            phase="final_delivery",
            rules=(
                _fixture_rule(
                    scenario,
                    "final_delivery",
                    frozenset({"pass"}),
                    {
                        "repair": FailureCode.WORK_FAILED,
                        "evidence_blocked": FailureCode.EVIDENCE_INSUFFICIENT,
                    },
                ),
            ),
            default_budget=3,
            route_resolver=_final_delivery_route,
        ),
    }


__all__ = ["FixtureSequenceRule", "build_fixture_gate_definitions"]
