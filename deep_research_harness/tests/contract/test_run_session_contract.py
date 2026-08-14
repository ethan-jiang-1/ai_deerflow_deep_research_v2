"""Contracts for retained, observation-only Run Bundle projections.

@impl DRH-001
@impl REJ-001
@impl REJ-002
@impl DRH-006
@impl REJ-004
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from deerflow_deep_research.domain.run_observation import (
    MAX_LIFECYCLE_SEQUENCE,
    JournalAvailability,
    LifecycleTraceRecord,
    ObservationInspectability,
    RecordBearingLifecycleFact,
    RetentionState,
    RunObservationManifest,
    RunObservationView,
)

BUNDLE_ID = "b_" + "A" * 43


def test_record_bearing_fact_requires_the_available_bundle_identity() -> None:
    payload = {
        "bundle_id": BUNDLE_ID,
        "action": "start",
        "status": "suspended",
        "phase": "bootstrap",
        "generation": 0,
        "durability": "same_process",
    }
    assert RecordBearingLifecycleFact.model_validate(payload).bundle_id == BUNDLE_ID
    for field in ("bundle_id", "status", "phase", "generation"):
        invalid = dict(payload)
        invalid.pop(field)
        with pytest.raises(ValidationError):
            RecordBearingLifecycleFact.model_validate(invalid)


def test_observation_manifest_is_closed_and_contains_only_safe_references() -> None:
    manifest = RunObservationManifest(
        bundle_id=BUNDLE_ID,
        created_at="2026-07-21T00:00:00Z",
        updated_at="2026-07-21T00:00:01Z",
        retention_state=RetentionState.RETAINED,
        durability="same_process",
    )
    assert manifest.lifecycle_path == "diagnostics/lifecycle.jsonl"
    with pytest.raises(ValidationError):
        RunObservationManifest.model_validate({**manifest.model_dump(), "host_path": "/private/secret"})


def test_trace_sequence_bounds_are_explicit() -> None:
    payload = {
        "sequence": 1,
        "timestamp": "2026-07-21T00:00:00Z",
        "action": "start",
        "phase": "bootstrap",
        "status": "suspended",
        "generation": 0,
    }
    assert LifecycleTraceRecord.model_validate(payload).sequence == 1
    with pytest.raises(ValidationError):
        LifecycleTraceRecord.model_validate({**payload, "sequence": 0})
    with pytest.raises(ValidationError):
        LifecycleTraceRecord.model_validate({**payload, "sequence": MAX_LIFECYCLE_SEQUENCE + 1})


def test_observation_view_is_a_closed_safe_presentation_contract() -> None:
    view = RunObservationView(
        bundle_id=BUNDLE_ID,
        inspectability=ObservationInspectability.AVAILABLE,
        retention_state=RetentionState.RETAINED,
        durability="same_process",
    )
    assert view.inspectability is ObservationInspectability.AVAILABLE
    assert JournalAvailability.UNAVAILABLE.value == "unavailable"
    with pytest.raises(ValidationError):
        RunObservationView.model_validate({**view.model_dump(), "bundle_host_path": "/private/secret"})


@pytest.mark.parametrize("unsafe_field", ["prompt", "answer", "provider_body", "exception", "url", "host_path"])
def test_lifecycle_fact_rejects_untrusted_payload_fields(unsafe_field: str) -> None:
    payload = {
        "bundle_id": BUNDLE_ID,
        "action": "start",
        "status": "suspended",
        "phase": "bootstrap",
        "generation": 0,
        "durability": "same_process",
        unsafe_field: "secret=sentinel /Users/private https://provider.invalid",
    }
    with pytest.raises(ValidationError):
        RecordBearingLifecycleFact.model_validate(payload)
