"""Closed public contracts for the local retained-session workbench.

@impl RWB-001
@impl RWB-003
@impl RSV-001
@impl RSV-003
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from deerflow_deep_research.domain.session_workbench import (
    ArtifactCatalogKey,
    BundleWorkbenchControl,
    WorkbenchArtifactMetadata,
    WorkbenchArtifactView,
    WorkbenchAvailability,
    WorkbenchCatalogView,
    WorkbenchTimelineEntry,
    WorkbenchTimelineView,
)


def test_workbench_control_projects_a_shared_bundle_result_without_a_session_recovery_key() -> None:
    """RWB-008: workbench controls are presentation-only Bundle projections."""
    control = BundleWorkbenchControl(
        bundle_id="b_" + "A" * 43,
        availability="available",
        legal_next_action="refine",
    )

    assert control.bundle_id == "b_" + "A" * 43
    assert "session_ref" not in BundleWorkbenchControl.model_fields
    assert "checkpoint" not in BundleWorkbenchControl.model_fields


def test_timeline_projection_is_frozen_bounded_and_excludes_trace_payloads() -> None:
    entry = WorkbenchTimelineEntry(
        sequence=1,
        timestamp=datetime(2026, 7, 22, tzinfo=UTC),
        action="start",
        status="suspended",
        phase="bootstrap",
        generation=0,
        pending_phase="hitl1",
        pending_mode="text",
        pending_request_id="drh_pending",
    )
    view = WorkbenchTimelineView(availability=WorkbenchAvailability.AVAILABLE, entries=(entry,))

    assert view.entries == (entry,)
    assert view.model_dump() == {
        "availability": "available",
        "entries": (
            {
                "sequence": 1,
                "timestamp": datetime(2026, 7, 22, tzinfo=UTC),
                "action": "start",
                "status": "suspended",
                "phase": "bootstrap",
                "generation": 0,
                "pending_phase": "hitl1",
                "pending_mode": "text",
                "pending_request_id": "drh_pending",
                "terminal_outcome": None,
                "failure_category": None,
                "diagnostic_ref": None,
            },
        ),
    }

    for unsafe_field in ("trace_delta", "answer", "provider_payload", "host_path", "exception_body"):
        with pytest.raises(ValidationError):
            WorkbenchTimelineEntry.model_validate({**entry.model_dump(), unsafe_field: "secret=sentinel"})


def test_catalog_and_metadata_are_fixed_and_body_free() -> None:
    metadata = WorkbenchArtifactMetadata(
        key=ArtifactCatalogKey.REQUEST_PROFILE,
        relative_path="request/profile.json",
        media_type="application/json",
        byte_size=42,
    )
    catalog = WorkbenchCatalogView(availability=WorkbenchAvailability.AVAILABLE, entries=(metadata,))
    view = WorkbenchArtifactView(availability=WorkbenchAvailability.AVAILABLE, metadata=metadata)

    assert catalog.entries == (metadata,)
    assert view.metadata == metadata
    assert metadata.presentation == "metadata_only"

    for unsafe_field in ("body", "content", "host_path", "binding", "provider", "diagnostic_body"):
        with pytest.raises(ValidationError):
            WorkbenchArtifactMetadata.model_validate({**metadata.model_dump(), unsafe_field: "secret=sentinel"})
    with pytest.raises(ValidationError):
        WorkbenchArtifactMetadata(
            key=ArtifactCatalogKey.REQUEST_PROFILE,
            relative_path="diagnostics/records.jsonl",
            media_type="application/json",
            byte_size=42,
        )


def test_unavailable_workbench_projections_reveal_no_session_or_artifact_facts() -> None:
    assert WorkbenchTimelineView(availability=WorkbenchAvailability.UNAVAILABLE).entries == ()
    assert WorkbenchCatalogView(availability=WorkbenchAvailability.UNAVAILABLE).entries == ()
    assert WorkbenchArtifactView(availability=WorkbenchAvailability.UNAVAILABLE).metadata is None

    metadata = WorkbenchArtifactMetadata(
        key=ArtifactCatalogKey.REQUEST_MARKER,
        relative_path="request/marker.json",
        media_type="application/json",
        byte_size=1,
    )
    with pytest.raises(ValidationError):
        WorkbenchCatalogView(availability=WorkbenchAvailability.UNAVAILABLE, entries=(metadata,))
    with pytest.raises(ValidationError):
        WorkbenchArtifactView(availability=WorkbenchAvailability.UNAVAILABLE, metadata=metadata)


@pytest.mark.parametrize("value", ["../../etc/passwd", "work-result", "report", "diagnostics/records.jsonl"])
def test_catalog_key_rejects_arbitrary_paths_and_unknown_keys(value: str) -> None:
    with pytest.raises(ValueError):
        ArtifactCatalogKey(value)
