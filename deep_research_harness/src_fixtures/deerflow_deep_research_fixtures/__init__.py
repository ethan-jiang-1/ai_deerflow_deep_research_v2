"""Deterministic Deep Research fixture implementations.

This package is intentionally outside the production distribution.  It is loaded only
by test and credential-free demo composition roots.
"""

from .catalog import build_fixture_adapters, build_fixture_catalog, build_fixture_recipe
from .gates import build_fixture_gate_definitions
from .scenario import FixtureScenario

__all__ = [
    "FixtureScenario",
    "build_fixture_adapters",
    "build_fixture_catalog",
    "build_fixture_gate_definitions",
    "build_fixture_recipe",
]
