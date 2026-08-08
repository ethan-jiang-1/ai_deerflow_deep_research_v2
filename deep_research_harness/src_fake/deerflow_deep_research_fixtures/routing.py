"""Deterministic routing helpers bound to an immutable fixture scenario."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from deerflow_deep_research.domain.lifecycle import completed_visits

from .scenario import FixtureScenario


def scenario_route(
    state: Mapping[str, Any],
    *,
    scenario: FixtureScenario,
    logical_name: str,
    sequence_name: str | None = None,
) -> str:
    """Select the route for the current visit without storing scenario data in state."""

    return scenario.value_for_visit(sequence_name or logical_name, completed_visits(state, logical_name))


__all__ = ["scenario_route"]
