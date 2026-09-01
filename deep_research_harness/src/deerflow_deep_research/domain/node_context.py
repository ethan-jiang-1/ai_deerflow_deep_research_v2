"""Typed contracts for Bundle-private node-agent invocation context capture.

A snapshot is the exact initial execution envelope of one admitted
``RuntimeNodeAgentBridge.run_agent`` invocation, durable before the first
provider call. It is Bundle-private sensitive content, never a prompt
authority, log line, or Gateway surface. (`LDO-005`, `LDO-006`)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from deerflow_deep_research.domain.lifecycle import FrozenContract

NODE_CONTEXT_SCHEMA_VERSION: Literal[1] = 1

ProvenanceLabel = Literal["MODEL_VISIBLE", "RUNTIME_ENFORCED", "DEVELOPER_ONLY"]
CaptureQuality = Literal["CAPTURED", "DEGRADED"]
SourceStatus = Literal["MATCH", "DRIFT", "CURRENT_SOURCE_UNAVAILABLE"]


class CapturedResourceLayer(FrozenContract):
    """One captured runtime Markdown layer: exact bytes plus identity."""

    identity: str = Field(min_length=1, max_length=256)
    text: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class EnforcedToolPosture(FrozenContract):
    requested_tool_names: tuple[str, ...] = ()
    enforced_tool_names: tuple[str, ...] = ()
    posture_kind: str = Field(min_length=1, max_length=32)


class VirtualRootsView(FrozenContract):
    workspace_root: str | None = None
    uploads_root: str | None = None
    outputs_root: str | None = None
    attempt_root: str | None = None
    read_roots: tuple[str, ...] = ()
    write_roots: tuple[str, ...] = ()


class MountManifestEntryView(FrozenContract):
    alias: str = Field(min_length=1, max_length=64)
    virtual_path: str = Field(min_length=1, max_length=256)


class NodeContextActivityFacts(FrozenContract):
    """Bounded per-invocation activity; never raw message histories."""

    model_calls: int = Field(ge=0)
    tool_calls: int = Field(ge=0)
    budget_stop_reason: str | None = None
    outcome: Literal["completed", "failed"]


class NodeContextSnapshot(FrozenContract):
    schema_version: Literal[1] = NODE_CONTEXT_SCHEMA_VERSION
    context_id: str = Field(min_length=8, max_length=128)
    bundle_id: str = Field(min_length=1, max_length=64)
    node: str = Field(min_length=1, max_length=32)
    attempt_id: str = Field(min_length=1, max_length=128)
    node_agent_ordinal: int = Field(ge=1)
    created_at: datetime

    initial_system_policy: str = Field(min_length=1)
    initial_human_message: str = Field(min_length=1)
    base_policy_layer: CapturedResourceLayer
    capability_layer: CapturedResourceLayer

    request_objective: str = Field(min_length=1, max_length=16_384)
    request_expected_output: str = Field(max_length=2048)
    request_source_artifact_refs: tuple[str, ...] = ()

    safe_model_label: str = Field(min_length=1, max_length=128)
    tool_posture: EnforcedToolPosture
    budget: dict[str, Any] = Field(default_factory=dict)
    structured_output_schema_identity: str | None = Field(default=None, max_length=256)
    virtual_roots: VirtualRootsView
    mount_manifest: tuple[MountManifestEntryView, ...] = ()

    capture_quality: CaptureQuality = "CAPTURED"


class NodeContextSummary(FrozenContract):
    context_id: str = Field(min_length=8, max_length=128)
    node: str = Field(min_length=1, max_length=32)
    attempt_id: str = Field(min_length=1, max_length=128)
    node_agent_ordinal: int = Field(ge=1)
    created_at: datetime
    capture_quality: CaptureQuality = "CAPTURED"


class NodeContextView(FrozenContract):
    """Full per-invocation view with fixed coverage and provenance labels."""

    snapshot: NodeContextSnapshot
    provenance: dict[str, ProvenanceLabel] = Field(default_factory=dict)
    coverage_initial_context: Literal["CAPTURED", "DEGRADED"] = "CAPTURED"
    coverage_runtime_posture: Literal["ENFORCED"] = "ENFORCED"
    coverage_inner_activity: Literal["BOUNDED", "DEGRADED"] = "BOUNDED"
    coverage_outcome: Literal["OBSERVED", "UNAVAILABLE"] = "UNAVAILABLE"
    coverage_files: Literal["CURRENT"] = "CURRENT"
    raw_provider_history: Literal["NOT_RETAINED"] = "NOT_RETAINED"
    activity: NodeContextActivityFacts | None = None


class NodeSourceView(FrozenContract):
    node: str = Field(min_length=1, max_length=32)
    base_policy_status: SourceStatus
    capability_status: SourceStatus
    capability_identity: str = Field(min_length=1, max_length=256)
    current_capability_text: str = Field(min_length=1)
    note: Literal["NOT_MODEL_VISIBLE"] = "NOT_MODEL_VISIBLE"


class NodeContextCollectionPage(FrozenContract):
    bundle_id: str = Field(min_length=1, max_length=64)
    summaries: tuple[NodeContextSummary, ...] = ()
    total: int = Field(ge=0)
