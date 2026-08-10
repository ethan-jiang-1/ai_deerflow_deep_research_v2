"""Observation stores cannot become lifecycle bindings.

@impl RES-001
@impl RES-004
@impl RES-006
"""

from __future__ import annotations

from deerflow_deep_research.runtime.run_observation import RunObservationStore


def test_bundle_journal_store_has_no_bundle_control_or_discovery_interface() -> None:
    public_methods = {
        name
        for name in dir(RunObservationStore)
        if not name.startswith("_") and callable(getattr(RunObservationStore, name))
    }

    assert public_methods == {"cleanup", "inspect", "publish", "record_event"}
    assert public_methods.isdisjoint(
        {
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
    )
