"""Authority-reduced values that may cross into graph and node code."""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef
from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.domain.run_experience import NodeProblem


class FrozenDomainModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ArtifactRef(FrozenDomainModel):
    artifact_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    virtual_path: str = Field(min_length=1, max_length=1024)
    media_type: str | None = Field(default=None, max_length=128)


class GraphContextView(FrozenDomainModel):
    research_scope_id: str = Field(min_length=1, max_length=128)
    workspace_root: str = Field(min_length=1, max_length=1024)
    uploads_root: str = Field(min_length=1, max_length=1024)
    outputs_root: str = Field(min_length=1, max_length=1024)


class SelectedBundleContext(FrozenDomainModel):
    """The only durable-run fact a node may receive from the runtime boundary."""

    bundle: RunBundleRef


class NodeAgentBundleContext(FrozenDomainModel):
    """Ephemeral attribution for one already-selected node-agent Run Bundle.

    This projection keeps only the opaque public identity. It does not give the
    bridge a scope bucket, physical location, State writer, checkpoint, or
    lifecycle capability.

    @impl NOA-014
    """

    bundle_id: BundleId

    @classmethod
    def from_selected_bundle(cls, selected: SelectedBundleContext) -> NodeAgentBundleContext:
        if not isinstance(selected, SelectedBundleContext):
            raise TypeError("selected_bundle_context_required")
        return cls(bundle_id=selected.bundle.bundle_id)


class NodeAgentContext(FrozenDomainModel):
    research_scope_id: str = Field(min_length=1, max_length=128)
    node_name: str = Field(min_length=1, max_length=64, pattern=r"^[a-z][a-z0-9_]*$")
    attempt_id: str = Field(min_length=1, max_length=128)
    workspace_root: str = Field(min_length=1, max_length=1024)
    attempt_root: str = Field(min_length=1, max_length=1024)
    policy_name: str = Field(min_length=1, max_length=64)
    bundle_context: NodeAgentBundleContext | None = None


_CAPABILITY_ID = re.compile(r"^[a-z][a-z0-9-]{2,95}$")
_CAPABILITY_PACKAGE_PREFIX = "deerflow_deep_research.graph.nodes."


class NodeAgentCapabilityRef(FrozenDomainModel):
    """A package-local Markdown policy reference, never prompt text or authority.

    @impl NAC-001
    """

    capability_id: str = Field(min_length=3, max_length=96)
    package: str = Field(min_length=len(_CAPABILITY_PACKAGE_PREFIX) + 1, max_length=160)
    resource: str = Field(min_length=17, max_length=160)

    @model_validator(mode="after")
    def validate_local_reference(self) -> NodeAgentCapabilityRef:
        if not _CAPABILITY_ID.fullmatch(self.capability_id):
            raise ValueError("capability_id_invalid")
        if not self.package.startswith(_CAPABILITY_PACKAGE_PREFIX) or not self.package.removeprefix(
            _CAPABILITY_PACKAGE_PREFIX
        ):
            raise ValueError("capability_package_invalid")
        parts = self.resource.split("/")
        if (
            not self.resource.startswith("capabilities/")
            or not self.resource.endswith(".md")
            or self.resource.startswith("/")
            or "\\" in self.resource
            or ".." in parts
            or len(parts) != 2
        ):
            raise ValueError("capability_resource_invalid")
        return self


class NodeExecutionRequest(FrozenDomainModel):
    objective: str = Field(min_length=1, max_length=16_384)
    expected_output: str = Field(min_length=1, max_length=2048)
    capability_ref: NodeAgentCapabilityRef
    source_artifact_refs: tuple[ArtifactRef, ...] = ()
    minimum_tool_calls: int = Field(default=0, ge=0, le=32)
    tool_call_limit: int | None = Field(default=None, ge=1, le=32)
    tools_enabled: bool = True

    @model_validator(mode="after")
    def validate_tool_window(self) -> NodeExecutionRequest:
        if self.tool_call_limit is not None and self.minimum_tool_calls > self.tool_call_limit:
            raise ValueError("minimum_tool_calls_exceed_limit")
        if not self.tools_enabled and (self.minimum_tool_calls or self.tool_call_limit is not None):
            raise ValueError("disabled_tools_cannot_have_call_requirements")
        return self


class NodeExecutionResult(FrozenDomainModel):
    finish_reason: NodeFinishReason
    summary: str = Field(default="", max_length=16_384)
    artifact_refs: tuple[ArtifactRef, ...] = ()
    untrusted_tool_results: tuple[str, ...] = Field(default=(), max_length=8)
    error_code: str | None = Field(default=None, max_length=128, pattern=r"^[a-z][a-z0-9_]*$")
    problem: NodeProblem | None = None

    @field_validator("untrusted_tool_results")
    @classmethod
    def validate_tool_results(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if any(not isinstance(value, str) or len(value.encode("utf-8")) > 16_384 for value in values):
            raise ValueError("untrusted_tool_result_invalid")
        return values

    @model_validator(mode="after")
    def validate_problem_shape(self) -> NodeExecutionResult:
        if self.finish_reason is NodeFinishReason.SUCCESS and self.problem is not None:
            raise ValueError("successful_result_cannot_have_problem")
        return self
