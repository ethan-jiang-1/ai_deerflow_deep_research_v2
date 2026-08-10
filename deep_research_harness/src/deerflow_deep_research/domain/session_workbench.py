"""Frozen safe projections for the standalone local session workbench.

The workbench is a presentation boundary over an already-authorized operation view.
It deliberately carries no runtime authority, retained-root path, artifact body, or
checkpoint payload.

@impl RWB-001
@impl RWB-002
@impl RWB-003
@impl RWB-004
@impl RSV-001
@impl RSV-002
@impl RSV-003
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from deerflow_deep_research.domain.lifecycle import BundleControlResult
from deerflow_deep_research.domain.run_observation import (
    MAX_EVENT_RECORDS,
    MAX_TRACE_RECORDS,
    JournalAvailability,
    JournalIncompleteReason,
    RunEvent,
    RunSummary,
)

MAX_WORKBENCH_ARTIFACT_BYTES = 2 * 1024 * 1024
MAX_WORKBENCH_CATALOG_ENTRIES = 4


class FrozenSessionWorkbenchContract(BaseModel):
    """Closed serializable contract for the local workbench presentation seam."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class WorkbenchAvailability(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class BundleWorkbenchControl(FrozenSessionWorkbenchContract):
    """Inert projection of a shared Bundle lifecycle result."""

    bundle_id: str | None = Field(default=None, pattern=r"^b_[A-Za-z0-9_-]{43}$")
    availability: Literal["available", "unavailable"]
    legal_next_action: Literal["start", "resume", "status", "cancel", "refine", "none"]

    @model_validator(mode="after")
    def validate_redaction(self) -> BundleWorkbenchControl:
        if self.availability == "unavailable" and self.bundle_id is not None:
            raise ValueError("unavailable_control_cannot_expose_bundle")
        if self.availability == "available" and self.bundle_id is None:
            raise ValueError("available_control_requires_bundle")
        return self


class ArtifactCatalogKey(StrEnum):
    REQUEST_MARKER = "request-marker"
    REQUEST_PROFILE = "request-profile"
    LIFECYCLE_TRACE = "lifecycle-trace"
    DIAGNOSTICS = "diagnostics"


_ARTIFACT_CATALOG: dict[ArtifactCatalogKey, tuple[str, str]] = {
    ArtifactCatalogKey.REQUEST_MARKER: ("request/marker.json", "application/json"),
    ArtifactCatalogKey.REQUEST_PROFILE: ("request/profile.json", "application/json"),
    ArtifactCatalogKey.LIFECYCLE_TRACE: ("diagnostics/lifecycle.jsonl", "application/x-ndjson"),
    ArtifactCatalogKey.DIAGNOSTICS: ("diagnostics/records.jsonl", "application/x-ndjson"),
}


def artifact_catalog_path(key: ArtifactCatalogKey) -> str:
    """Return the one fixed relative path for a workbench catalog key."""
    return _ARTIFACT_CATALOG[key][0]


def artifact_catalog_media_type(key: ArtifactCatalogKey) -> str:
    """Return the inert metadata classification for a workbench catalog key."""
    return _ARTIFACT_CATALOG[key][1]


class WorkbenchArtifactMetadata(FrozenSessionWorkbenchContract):
    """Inert metadata for exactly one fixed contained artifact, never its body."""

    key: ArtifactCatalogKey
    relative_path: Literal[
        "request/marker.json",
        "request/profile.json",
        "diagnostics/lifecycle.jsonl",
        "diagnostics/records.jsonl",
    ]
    media_type: Literal["application/json", "application/x-ndjson"]
    byte_size: int = Field(ge=0, le=MAX_WORKBENCH_ARTIFACT_BYTES)
    presentation: Literal["metadata_only"] = "metadata_only"

    @model_validator(mode="after")
    def validate_fixed_catalog_mapping(self) -> WorkbenchArtifactMetadata:
        expected_path, expected_media_type = _ARTIFACT_CATALOG[self.key]
        if self.relative_path != expected_path or self.media_type != expected_media_type:
            raise ValueError("artifact_catalog_mapping_invalid")
        return self


class WorkbenchTimelineEntry(FrozenSessionWorkbenchContract):
    """Safe retained lifecycle fact; not a phase cursor or resume authority."""

    sequence: int = Field(ge=1, le=2**31 - 1)
    timestamp: datetime
    action: Literal["start", "resume", "status", "cancel"]
    status: Literal["suspended", "completed", "stopped", "cancelled", "blocked"]
    phase: str = Field(min_length=1, max_length=32, pattern=r"^[a-z][a-z0-9_]*$")
    generation: int = Field(ge=0, le=2)
    pending_phase: Literal["hitl1", "hitl2"] | None = None
    pending_mode: Literal["text", "choice"] | None = None
    pending_request_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{1,128}$")
    terminal_outcome: Literal["completed", "stopped", "cancelled", "blocked"] | None = None
    failure_category: str | None = Field(default=None, pattern=r"^[a-z]+(?:[._][a-z]+)*$")
    diagnostic_ref: str | None = Field(default=None, pattern=r"^diag_[A-Za-z0-9_-]{8,64}$")


class WorkbenchTimelineView(FrozenSessionWorkbenchContract):
    availability: WorkbenchAvailability
    entries: tuple[WorkbenchTimelineEntry, ...] = Field(default=(), max_length=MAX_TRACE_RECORDS)

    @model_validator(mode="after")
    def validate_unavailable_redaction(self) -> WorkbenchTimelineView:
        if self.availability is WorkbenchAvailability.UNAVAILABLE and self.entries:
            raise ValueError("unavailable_timeline_cannot_expose_entries")
        return self


class WorkbenchDiagnosisView(FrozenSessionWorkbenchContract):
    availability: WorkbenchAvailability
    summary: RunSummary | None = None
    events: tuple[RunEvent, ...] = Field(default=(), max_length=min(MAX_EVENT_RECORDS, 8))
    incomplete_reasons: tuple[JournalIncompleteReason, ...] = Field(default=(), max_length=4)

    @model_validator(mode="after")
    def validate_shape(self) -> WorkbenchDiagnosisView:
        if self.availability is WorkbenchAvailability.UNAVAILABLE and (
            self.summary is not None or self.events or self.incomplete_reasons
        ):
            raise ValueError("unavailable_diagnosis_cannot_expose_facts")
        if (
            self.summary is not None
            and self.summary.journal_availability is not JournalAvailability.INCOMPLETE
            and self.incomplete_reasons
        ):
            raise ValueError("complete_diagnosis_cannot_expose_incomplete_reasons")
        if len(set(self.incomplete_reasons)) != len(self.incomplete_reasons):
            raise ValueError("diagnosis_incomplete_reasons_duplicate")
        return self


class WorkbenchCatalogView(FrozenSessionWorkbenchContract):
    availability: WorkbenchAvailability
    entries: tuple[WorkbenchArtifactMetadata, ...] = Field(default=(), max_length=MAX_WORKBENCH_CATALOG_ENTRIES)

    @model_validator(mode="after")
    def validate_catalog_shape(self) -> WorkbenchCatalogView:
        if self.availability is WorkbenchAvailability.UNAVAILABLE and self.entries:
            raise ValueError("unavailable_catalog_cannot_expose_entries")
        keys = tuple(entry.key for entry in self.entries)
        if len(set(keys)) != len(keys):
            raise ValueError("artifact_catalog_duplicate_key")
        return self


class WorkbenchArtifactView(FrozenSessionWorkbenchContract):
    availability: WorkbenchAvailability
    metadata: WorkbenchArtifactMetadata | None = None

    @model_validator(mode="after")
    def validate_artifact_shape(self) -> WorkbenchArtifactView:
        if (self.availability is WorkbenchAvailability.AVAILABLE) != (self.metadata is not None):
            raise ValueError("artifact_view_availability_mismatch")
        return self


class WorkbenchSessionView(FrozenSessionWorkbenchContract):
    """One Bundle-authorized view plus independent retained observations."""

    operation: BundleControlResult | None = None
    timeline: WorkbenchTimelineView
    catalog: WorkbenchCatalogView
    diagnosis: WorkbenchDiagnosisView = Field(
        default_factory=lambda: WorkbenchDiagnosisView(availability=WorkbenchAvailability.UNAVAILABLE)
    )

    @model_validator(mode="after")
    def validate_authorization_ordering(self) -> WorkbenchSessionView:
        if self.operation is None and (
            self.timeline.availability is not WorkbenchAvailability.UNAVAILABLE
            or self.catalog.availability is not WorkbenchAvailability.UNAVAILABLE
            or self.diagnosis.availability is not WorkbenchAvailability.UNAVAILABLE
        ):
            raise ValueError("missing_operation_cannot_expose_retained_observations")
        if (
            self.operation is not None
            and self.operation.availability.value == "unavailable"
            and (
                self.timeline.availability is not WorkbenchAvailability.UNAVAILABLE
                or self.catalog.availability is not WorkbenchAvailability.UNAVAILABLE
                or self.diagnosis.availability is not WorkbenchAvailability.UNAVAILABLE
            )
        ):
            raise ValueError("unavailable_operation_cannot_expose_retained_observations")
        return self


class WorkbenchDiscoveryView(FrozenSessionWorkbenchContract):
    """Trusted-scope Bundle discovery projection for the terminal selector."""

    entries: tuple[BundleControlResult, ...] = Field(default=(), max_length=20)


__all__ = [
    "ArtifactCatalogKey",
    "BundleWorkbenchControl",
    "FrozenSessionWorkbenchContract",
    "MAX_WORKBENCH_ARTIFACT_BYTES",
    "MAX_WORKBENCH_CATALOG_ENTRIES",
    "WorkbenchArtifactMetadata",
    "WorkbenchArtifactView",
    "WorkbenchAvailability",
    "WorkbenchCatalogView",
    "WorkbenchDiagnosisView",
    "WorkbenchDiscoveryView",
    "WorkbenchSessionView",
    "WorkbenchTimelineEntry",
    "WorkbenchTimelineView",
    "artifact_catalog_media_type",
    "artifact_catalog_path",
]
