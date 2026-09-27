"""Deterministic contracts for the topic-planning live subject.

The real-model judgment is NOT claimed here: a scripted plan model drives the
real zero-tool bridge end to end, proving the scenario wiring (profile, state,
direction), the capture, and the telemetry aggregation.

@impl CES-003
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage

from deerflow_deep_research.runtime.evaluation import load_case_registry
from deerflow_deep_research.runtime.evaluation.runner import ExecutionContext
from deerflow_deep_research.runtime.evaluation.topic_planning_live import (
    _scenario_state,
    topic_planning_live_subject,
)
from tests.integration.test_public_skill_activation import configured_deerflow_home  # noqa: F401

PLAN = json.dumps(
    {
        "schema_version": 1,
        "topics": [
            {
                "title": "Batteries",
                "scope": "Grid battery economics",
                "must_answer_bindings": ["Q1"],
                "search_dimensions": [],
                "exclusions": [],
            },
            {
                "title": "Solar",
                "scope": "Utility-scale solar economics",
                "must_answer_bindings": ["Q2"],
                "search_dimensions": [],
                "exclusions": [],
            },
        ],
    }
)


def _case() -> Any:
    return load_case_registry().resolve(case_id="topic-planning-direction-loop", version="v1")


def _profile_ref_for(scenario: Any, position: int) -> Any:
    from deerflow_deep_research.domain.bundle import bundle_profile_path
    from deerflow_deep_research.domain.profile import compute_profile_content_hash
    from deerflow_deep_research.domain.state import ContentRef
    from deerflow_deep_research.runtime.evaluation.topic_planning_live import _scenario_bundle, _scenario_profile

    bundle = _scenario_bundle(position)
    profile = _scenario_profile(scenario)
    return (
        ContentRef(
            sandbox_path=bundle_profile_path(bundle),
            content_hash=compute_profile_content_hash(profile),
            schema_version=1,
            short_summary="case scenario profile",
        ),
        bundle,
        profile,
    )


def test_direction_scenarios_carry_generation_one_direction() -> None:
    case = _case()
    for position, scenario in enumerate(case.fixture["scenarios"]):
        profile_ref, bundle, profile = _profile_ref_for(scenario, position)
        state = _scenario_state(scenario, profile=profile, profile_ref=profile_ref, bundle=bundle)
        assert state["request_text"] == scenario["request_text"]
        assert profile.scope_boundaries == scenario["scope_boundaries"]
        assert profile.custom_notes == scenario["custom_notes"]
        if scenario.get("current_direction"):
            assert state["generation"] == 1
            assert state["current_refinement"].text == scenario["current_direction"]
        else:
            assert state["generation"] == 0
            assert "current_refinement" not in state


class _PlanModel(FakeMessagesListChatModel):
    def __init__(self) -> None:
        super().__init__(responses=[])

    def bind_tools(self, tools: Any = None, **_: Any) -> Any:  # type: ignore[override]
        return self

    def _response(self) -> AIMessage:
        return AIMessage(
            content=PLAN,
            usage_metadata={"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        )

    def invoke(self, messages: Any, config: Any = None, **_: Any) -> AIMessage:  # type: ignore[override]
        return self._response()

    async def ainvoke(self, messages: Any, config: Any = None, **_: Any) -> AIMessage:  # type: ignore[override]
        return self._response()


@pytest.mark.asyncio
async def test_subject_end_to_end_with_scripted_plan_model_through_real_bridge(
    tmp_path: Path,
    configured_deerflow_home,  # noqa: F811
) -> None:
    from deerflow_deep_research.graph.nodes.topic_planning import NODE_SPEC

    case = _case()
    app_config = configured_deerflow_home(deferred_discovery=False)
    subject = topic_planning_live_subject(
        node_spec=NODE_SPEC,
        app_config=app_config,
        provider="fixture-provider",
        model="fixture-model",
    )
    context = ExecutionContext(workspace=tmp_path / "workspace", fixture=case.fixture)

    with patch("deerflow.models.factory.create_chat_model", return_value=_PlanModel()):
        execution = await subject(context)

    updates = execution.output["scenario_updates"]
    assert [row["scenario_id"] for row in updates] == [s["scenario_id"] for s in case.fixture["scenarios"]]
    assert all(row["route"] == "next" for row in updates)
    assert all(len(row["topic_refs"]) == 2 for row in updates)
    assert all(any("Batteries" in str(entry.get("title", "")) for entry in row["topic_registry"]) for row in updates)

    scenarios = len(case.fixture["scenarios"])
    assert execution.resource_use["model_calls"] == scenarios
    assert execution.resource_use["input_tokens"] == scenarios * 100
    assert execution.resource_use["output_tokens"] == scenarios * 50
    assert execution.resource_use["tool_calls"] == 0
    assert execution.resource_use["cost_usd"] == 0.0
    assert execution.output["cost_unpriced"] is True
    for control in case.execution_plan.runtime_controls:
        assert execution.resource_use[control.name] == control.digest
