"""Typed observation contracts for the local workflow-debug trace surface.

Frames are projections: the checkpoint remains the commit authority and the
journal remains the bounded causal-detail authority. Nothing here mutates runs.
(`LDO-001`, `LDO-002`)
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from deerflow_deep_research.domain.lifecycle import FrozenContract

TRACE_SCHEMA_VERSION: Literal[1] = 1


class ActiveVisitProjection(FrozenContract):
    """The at-most-one in-flight visit; never a frame until commit or failure."""

    state: Literal["running", "committing", "uncertain"]
    node: str = Field(min_length=1, max_length=32)
    visit_id: str | None = Field(default=None, min_length=1, max_length=128)


class TraceFrame(FrozenContract):
    """One committed/suspended boundary or one non-committed failed segment."""

    schema_version: Literal[1] = TRACE_SCHEMA_VERSION
    bundle_id: str = Field(min_length=1, max_length=64)
    frame_sequence: int = Field(ge=1)
    checkpoint_id: str | None = Field(default=None, min_length=1, max_length=128)
    failure_event_sequence: int | None = Field(default=None, ge=1)
    visit_id: str | None = Field(default=None, min_length=1, max_length=128)
    generation: int | None = Field(default=None, ge=0)
    node: str = Field(min_length=1, max_length=32)
    outcome: Literal["completed", "suspended", "failed"]
    route: str | None = Field(default=None, min_length=1, max_length=64)
    next_nodes: tuple[str, ...] = ()
    changed_field_names: tuple[str, ...] = ()
    node_agent_context_count: int = Field(default=0, ge=0)
    node_context_collection_ref: str | None = Field(default=None, min_length=1, max_length=256)
    context_quality: Literal["complete", "degraded", "unavailable"] | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    failure_category: str | None = Field(default=None, min_length=1, max_length=128)
    terminal_disposition: str | None = Field(default=None, min_length=1, max_length=32)
    pending_input: str | None = Field(default=None, min_length=1, max_length=64)
    observation_quality: Literal["complete", "degraded", "unavailable"] = "complete"
    gap_reason: str | None = Field(default=None, min_length=1, max_length=256)


class TracePage(FrozenContract):
    """One bounded, redacted page of frames plus the honest active projection."""

    schema_version: Literal[1] = TRACE_SCHEMA_VERSION
    bundle_id: str = Field(min_length=1, max_length=64)
    frames: tuple[TraceFrame, ...] = ()
    active_visit: ActiveVisitProjection | None = None
    next_cursor: str | None = Field(default=None, min_length=1, max_length=1024)
    observation_quality: Literal["complete", "degraded", "unavailable"] = "complete"
    gap_reason: str | None = Field(default=None, min_length=1, max_length=256)
