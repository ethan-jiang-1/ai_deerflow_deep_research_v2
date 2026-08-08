"""Topic-planning integration at the selected-Bundle boundary.

@impl TOP-008
"""

from __future__ import annotations

import json

import pytest

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, bundle_profile_path
from deerflow_deep_research.domain.context import (
    GraphContextView,
    NodeAgentBundleContext,
    NodeAgentContext,
    NodeExecutionResult,
    SelectedBundleContext,
)
from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.profile import ResearchProfile, compute_profile_content_hash, profile_state_fields
from deerflow_deep_research.domain.state import ContentRef
from deerflow_deep_research.graph.nodes.topic_planning import node as topic_planning_node

BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "T" * 43), scope_bucket="s_" + "T" * 43)
BUNDLE_ID = BUNDLE.bundle_id.value


PROFILE = ResearchProfile(
    schema_version=2,
    depth="standard",
    audience="practitioner",
    format="detailed_report",
    cost_tolerance="moderate",
    time_budget="standard",
    must_answer=("Q1",),
    scope_boundaries="Storage technologies only.",
    custom_notes="Do not claim deployment dates without evidence.",
    comparison_required=False,
    request_language="en",
    output_language="en",
)
PROFILE_REF = ContentRef(
    sandbox_path=bundle_profile_path(BUNDLE),
    content_hash=compute_profile_content_hash(PROFILE),
    schema_version=1,
    short_summary="canonical profile",
)


class _ProfileReader:
    def __init__(self) -> None:
        self.refs: list[ContentRef] = []

    async def read_profile(self, profile_ref: ContentRef) -> ResearchProfile:
        self.refs.append(profile_ref)
        if profile_ref != PROFILE_REF:
            raise ValueError("profile_ref_unexpected")
        return PROFILE


class _PlannerCapabilities:
    def __init__(self) -> None:
        self.contexts: list[NodeAgentContext] = []
        self.requests: list[object] = []

    async def run_agent(self, *, context: NodeAgentContext, request: object) -> NodeExecutionResult:
        self.contexts.append(context)
        self.requests.append(request)
        return NodeExecutionResult(
            finish_reason=NodeFinishReason.SUCCESS,
            summary=json.dumps(
                {
                    "schema_version": 1,
                    "topics": [
                        {
                            "title": "Storage",
                            "scope": "Storage evidence",
                            "must_answer_bindings": ["Q1"],
                            "search_dimensions": [],
                            "exclusions": [],
                        }
                    ],
                }
            ),
        )


def _state() -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": 2,
        "bundle_id": BUNDLE_ID,
        "outer_thread_id": "topic-planning-test",
        "request_text": "Research storage options",
        "research_depth": "standard",
        "target_audience": "practitioner",
        "output_format": "detailed_report",
        "cost_tolerance": "moderate",
        "time_budget": "standard",
        "must_answer_questions": ("Q1",),
        "degraded_profile": False,
        "phase": "topic_planning",
        "generation": 0,
        "execution_trace": (),
    }
    payload.update(profile_state_fields(PROFILE, PROFILE_REF))
    return payload


def _dependencies(
    capabilities: _PlannerCapabilities,
    *,
    selected: bool = True,
    request_bundle: _ProfileReader | None = None,
) -> NodeBuildDependencies:
    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root="/mnt/user-data/workspace/deep-research/topic-planning-test",
        uploads_root="/mnt/user-data/uploads",
        outputs_root="/mnt/user-data/outputs/deep-research/topic-planning-test",
    )
    selected_bundle = SelectedBundleContext(bundle=BUNDLE)
    return NodeBuildDependencies(
        graph_context=graph_context,
        agent_context=NodeAgentContext(
            research_scope_id=BUNDLE_ID,
            node_name="topic_planning",
            attempt_id="g0-topic-planning-a00",
            workspace_root=graph_context.workspace_root,
            attempt_root=f"{graph_context.workspace_root}/attempts/g0-topic-planning-a00",
            policy_name="topic-planning",
            bundle_context=NodeAgentBundleContext.from_selected_bundle(selected_bundle),
        ),
        capabilities=capabilities,
        request_bundle=request_bundle or _ProfileReader(),
        selected_bundle=selected_bundle if selected else None,
    )


async def test_topic_planning_projects_only_the_selected_bundle_identity_to_the_agent() -> None:
    capabilities = _PlannerCapabilities()

    result = await topic_planning_node.build_real(_dependencies(capabilities))(_state())

    assert result["route"] == "next"
    assert result["topic_refs"] == ("storage",)
    assert len(capabilities.contexts) == 1
    agent_bundle = capabilities.contexts[0].bundle_context
    assert agent_bundle == NodeAgentBundleContext(bundle_id=BUNDLE.bundle_id)
    assert not hasattr(agent_bundle, "scope_bucket")
    assert set(NodeAgentBundleContext.model_fields) == {"bundle_id"}


async def test_topic_planning_loads_only_the_selected_bundle_profile_into_its_assignment() -> None:
    capabilities = _PlannerCapabilities()
    profile_reader = _ProfileReader()

    result = await topic_planning_node.build_real(_dependencies(capabilities, request_bundle=profile_reader))(_state())

    assert result["route"] == "next"
    assert profile_reader.refs == [PROFILE_REF]
    request = capabilities.requests[0]
    assert "Storage technologies only." in request.objective
    assert "Do not claim deployment dates without evidence." in request.objective


def test_topic_planning_rejects_missing_selected_bundle_before_agent_invocation() -> None:
    capabilities = _PlannerCapabilities()

    with pytest.raises(ValueError, match="selected_bundle_context_missing"):
        topic_planning_node.build_real(_dependencies(capabilities, selected=False))

    assert capabilities.contexts == []
