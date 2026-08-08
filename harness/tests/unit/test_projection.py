"""Runtime projection purity and non-leakage contract (RUI-002)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, bundle_ref_to_virtual, run_bundle_root
from deerflow_deep_research.domain.context import (
    GraphContextView,
    NodeAgentContext,
    NodeExecutionRequest,
    NodeExecutionResult,
)
from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.runtime.projection import (
    ProjectionError,
    build_node_dependencies,
    project_node_agent,
    project_research_scope,
)
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope

HOST_MARKER = "/srv/users/alice/threads/thread-1"
_BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)


class FakeCapabilities:
    async def run_agent(
        self,
        *,
        context: NodeAgentContext,
        request: NodeExecutionRequest,
    ) -> NodeExecutionResult:
        return NodeExecutionResult(finish_reason=NodeFinishReason.SUCCESS)


def _envelope() -> TrustedRuntimeEnvelope:
    from pathlib import Path

    return TrustedRuntimeEnvelope(
        effective_user_id="alice",
        outer_thread_id="thread-1",
        outer_run_id="run-1",
        app_config=object(),
        workspace_host_path=Path(HOST_MARKER) / "workspace",
        uploads_host_path=Path(HOST_MARKER) / "uploads",
        outputs_host_path=Path(HOST_MARKER) / "outputs",
        workspace_virtual_root="/mnt/user-data/workspace",
        uploads_virtual_root="/mnt/user-data/uploads",
        outputs_virtual_root="/mnt/user-data/outputs",
        parent_sandbox=object(),
        progress=None,
    )


def test_project_research_scope_emits_canonical_virtual_roots() -> None:
    view = project_research_scope(_envelope(), bundle=_BUNDLE)
    assert isinstance(view, GraphContextView)
    assert view.research_scope_id == _BUNDLE.bundle_id.value
    assert view.workspace_root == bundle_ref_to_virtual(run_bundle_root(_BUNDLE))
    assert view.uploads_root == "/mnt/user-data/uploads"
    assert view.outputs_root == f"/mnt/user-data/outputs/{run_bundle_root(_BUNDLE)}"


def test_project_research_scope_rejects_caller_supplied_locator() -> None:
    with pytest.raises(TypeError):
        project_research_scope(_envelope(), bundle=_BUNDLE, bundle_directory="caller-selected")  # type: ignore[call-arg]


def test_projection_requires_trusted_envelope() -> None:
    with pytest.raises(ProjectionError) as excinfo:
        project_research_scope(object(), bundle=_BUNDLE)  # type: ignore[arg-type]
    assert excinfo.value.code == "envelope_required"


def test_projection_requires_a_runtime_bound_bundle() -> None:
    with pytest.raises(ProjectionError) as excinfo:
        project_research_scope(_envelope(), bundle=object())  # type: ignore[arg-type]
    assert excinfo.value.code == "bundle_required"


def test_project_node_agent_derives_attempt_root_under_scope() -> None:
    view = project_research_scope(_envelope(), bundle=_BUNDLE)
    node = project_node_agent(view, node_name="collect_sources", attempt_id="att-1", policy_name="node-default")
    assert isinstance(node, NodeAgentContext)
    assert node.research_scope_id == _BUNDLE.bundle_id.value
    assert node.workspace_root == bundle_ref_to_virtual(run_bundle_root(_BUNDLE))
    assert node.attempt_root == f"{bundle_ref_to_virtual(run_bundle_root(_BUNDLE))}/attempts/att-1"


@pytest.mark.parametrize(
    ("node_name", "attempt_id", "policy_name"),
    [
        ("BadName", "att-1", "node-default"),
        ("collect_sources", "../x", "node-default"),
        ("collect_sources", "att-1", "Bad_Policy"),
    ],
)
def test_project_node_agent_rejects_unsafe_inputs(node_name: str, attempt_id: str, policy_name: str) -> None:
    view = project_research_scope(_envelope(), bundle=_BUNDLE)
    with pytest.raises(ProjectionError):
        project_node_agent(view, node_name=node_name, attempt_id=attempt_id, policy_name=policy_name)


def test_build_node_dependencies_requires_capabilities() -> None:
    view = project_research_scope(_envelope(), bundle=_BUNDLE)
    node = project_node_agent(view, node_name="collect_sources", attempt_id="att-1", policy_name="node-default")
    with pytest.raises(ProjectionError) as excinfo:
        build_node_dependencies(view, node, object())  # type: ignore[arg-type]
    assert excinfo.value.code == "capabilities_required"

    deps = build_node_dependencies(view, node, FakeCapabilities())
    assert isinstance(deps, NodeBuildDependencies)


def test_model_facing_contracts_leak_no_host_identity_or_appconfig() -> None:
    view = project_research_scope(_envelope(), bundle=_BUNDLE)
    node = project_node_agent(view, node_name="collect_sources", attempt_id="att-1", policy_name="node-default")
    serialized = f"{view.model_dump()}{node.model_dump()}"
    assert HOST_MARKER not in serialized
    assert "app_config" not in serialized
    assert "/users/" not in serialized
    assert "sandbox" not in serialized
    # Model-facing contracts have no field able to carry host paths or AppConfig.
    for model in (GraphContextView, NodeAgentContext):
        assert not {"host_path", "app_config", "sandbox", "user_id"} & set(model.model_fields)


def test_graph_context_is_frozen() -> None:
    view = project_research_scope(_envelope(), bundle=_BUNDLE)
    with pytest.raises(ValidationError):
        view.workspace_root = "/mnt/user-data/workspace/deep-research/evil"  # type: ignore[misc]
