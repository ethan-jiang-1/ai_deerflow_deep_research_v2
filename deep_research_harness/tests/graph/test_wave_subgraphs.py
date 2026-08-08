"""Fixture wave adapters reuse the fixture-only deterministic work-unit component."""

from __future__ import annotations

from deerflow_deep_research_fixtures.graph.nodes.wave0 import adapter as wave0_adapter
from deerflow_deep_research_fixtures.graph.nodes.wave1 import adapter as wave1_adapter
from deerflow_deep_research_fixtures.work_units import run_fixture_work_unit_component


def test_wave_recipes_use_distinct_three_item_fixture_intents() -> None:
    assert tuple(intent.scope for intent in wave0_adapter._INTENTS) == (
        ("wave0:fixture:0",),
        ("wave0:fixture:1",),
        ("wave0:fixture:2",),
    )
    assert tuple(intent.scope for intent in wave1_adapter._INTENTS) == (
        ("wave1:fixture:0",),
        ("wave1:fixture:1",),
        ("wave1:fixture:2",),
    )
    assert all(
        intent.required_outputs == ("fixture.json",) for intent in (*wave0_adapter._INTENTS, *wave1_adapter._INTENTS)
    )


def test_both_wave_recipes_delegate_to_the_same_component_submit_path() -> None:
    assert wave0_adapter.run_fixture_work_unit_component is run_fixture_work_unit_component
    assert wave1_adapter.run_fixture_work_unit_component is run_fixture_work_unit_component
    forbidden_local_authorities = {
        "StateGraph",
        "WorkUnitStore",
        "validate_submission_candidate",
        "commit_candidate",
    }
    assert not forbidden_local_authorities & set(vars(wave0_adapter))
    assert not forbidden_local_authorities & set(vars(wave1_adapter))
