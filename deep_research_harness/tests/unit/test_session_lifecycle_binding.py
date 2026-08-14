"""Observation stores cannot become lifecycle bindings.

@impl RES-001
@impl RES-004
@impl RES-006
"""

from __future__ import annotations

import pytest

from deerflow_deep_research.runtime.run_observation import RunObservationStore

_OBSERVATION_METHODS = {"cleanup", "inspect", "publish", "record_event"}
_CONTROL_METHODS = {
    "bind",
    "cancel",
    "control",
    "create",
    "discover",
    "reopen",
    "resolve",
    "resume",
    "start",
}


def _assert_observation_only(surface: type[object]) -> None:
    public_methods = {name for name in dir(surface) if not name.startswith("_") and callable(getattr(surface, name))}

    assert public_methods == _OBSERVATION_METHODS
    assert public_methods.isdisjoint(_CONTROL_METHODS)


def test_bundle_journal_store_has_no_bundle_control_or_discovery_interface() -> None:
    _assert_observation_only(RunObservationStore)


def test_bundle_journal_guard_rejects_a_planted_control_method() -> None:
    class PlantedObservationStore:
        def cleanup(self) -> None: ...

        def inspect(self) -> None: ...

        def publish(self) -> None: ...

        def record_event(self) -> None: ...

        def resume(self) -> None: ...

    with pytest.raises(AssertionError):
        _assert_observation_only(PlantedObservationStore)
