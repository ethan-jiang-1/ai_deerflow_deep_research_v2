"""Deterministic contracts for the controller live subject.

The real-model judgment is NOT claimed here: these tests pin the declared
typed-results table against the case's own declarations and prove the capture
path end to end with a scripted model double through the real composition.

@impl CES-003
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, HumanMessage

from deerflow_deep_research.domain.lifecycle import BundleControlResult, ResultCode
from deerflow_deep_research.runtime.evaluation import load_case_registry
from deerflow_deep_research.runtime.evaluation.controller_live import (
    _DECLARED_RESULTS,
    _STATE_PREFIX,
    SKILL_CONTAINER_PATH,
    _capture,
    _control_factory,
    controller_live_subject,
)
from deerflow_deep_research.runtime.evaluation.runner import ExecutionContext
from tests.integration.test_public_skill_activation import SKILL_SOURCE, configured_deerflow_home  # noqa: F401

_EXPECTED_CODE = {
    "suspended": ResultCode.SUSPENDED,
    "completed": ResultCode.COMPLETED,
    "refinement_pending": ResultCode.REFINEMENT_PENDING,
    "refinement_applied": ResultCode.REFINEMENT_APPLIED,
    "refinement_conflict": ResultCode.REFINEMENT_CONFLICT,
    "cancelled": ResultCode.CANCELLED,
    "status": ResultCode.STATUS_OK,
    "unavailable": ResultCode.UNAVAILABLE,
}


def _case() -> Any:
    return load_case_registry().resolve(case_id="public-controller-direction-loop", version="v1")


def test_declared_results_cover_every_case_state_and_expected_result() -> None:
    case = _case()
    for scenario in case.fixture["scenarios"]:
        state = scenario["subject_state"]
        assert state in _DECLARED_RESULTS, f"state without declared results: {state}"
        assert state in _STATE_PREFIX, f"state without conversation prefix: {state}"
        expected_action = scenario["expected_action"]
        if expected_action is None:
            continue  # clarification scenarios: proposing no action is the point
        answer = _DECLARED_RESULTS[state][expected_action]
        assert answer["code"] == _EXPECTED_CODE[scenario["expected_result"]].value, (
            f"{scenario['scenario_id']}: declared {expected_action} answer is {answer['code']}, "
            f"case expects {scenario['expected_result']}"
        )


def test_declared_answers_are_closed_typed_results() -> None:
    for _state, answers in _DECLARED_RESULTS.items():
        for action, answer in answers.items():
            validated = BundleControlResult.model_validate(answer)
            assert validated.action.value == action
            assert validated.availability is not None


def test_undeclared_state_fails_closed() -> None:
    with pytest.raises(ValueError, match="controller_live_subject_state_undeclared"):
        _control_factory("no_such_state", [])


def test_capture_reads_skill_first_then_action_and_usage() -> None:
    usage = {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}
    messages = [
        HumanMessage(content="Check the research run."),
        AIMessage(
            content="",
            tool_calls=[{"name": "read_file", "args": {"path": SKILL_CONTAINER_PATH}, "id": "c1"}],
            usage_metadata=dict(usage),
        ),
        AIMessage(
            content="",
            tool_calls=[{"name": "deep_research", "args": {"action": "status"}, "id": "c2"}],
            usage_metadata=dict(usage),
        ),
        AIMessage(content="Here is the status.", usage_metadata=dict(usage)),
    ]

    captured = _capture(messages)

    assert captured["skill_read_first"] is True
    assert captured["proposal"] == {
        "kind": "action",
        "action": "status",
        "bundle_id": None,
        "refinement": None,
        "all_calls": [{"action": "status", "bundle_id": None, "refinement": None}],
    }
    assert captured["usage"] == {"input_tokens": 30, "output_tokens": 15, "model_calls": 3}


def test_capture_records_a_clarification_when_no_lifecycle_call_happens() -> None:
    messages = [
        HumanMessage(content="This direction is not useful."),
        AIMessage(
            content="Which run do you mean — the active one or the completed one?",
            usage_metadata={"input_tokens": 7, "output_tokens": 3, "total_tokens": 10},
        ),
    ]

    captured = _capture(messages)

    assert captured["skill_read_first"] is False
    assert captured["proposal"]["kind"] == "clarification"
    assert captured["proposal"]["text"].startswith("Which run")


def _make_uniform_model(counts: dict[str, int]):
    """A scripted double that reads the skill, proposes status, then closes."""

    class _UniformControllerModel(FakeMessagesListChatModel):
        def __init__(self) -> None:
            super().__init__(responses=[])

        def bind_tools(self, tools: Any = None, **_: Any) -> Any:  # type: ignore[override]
            return self

        def invoke(self, messages: Any, config: Any = None, **_: Any) -> AIMessage:  # type: ignore[override]
            counts["invocations"] += 1
            usage = {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}
            tool_results = [message for message in messages if getattr(message, "type", "") == "tool"]
            read_skill = any(getattr(message, "name", "") == "read_file" for message in tool_results)
            made_control = any(getattr(message, "name", "") == "deep_research" for message in tool_results)
            if not read_skill:
                return AIMessage(
                    content="",
                    tool_calls=[{"name": "read_file", "args": {"path": SKILL_CONTAINER_PATH}, "id": "read-skill"}],
                    usage_metadata=dict(usage),
                )
            if not made_control:
                return AIMessage(
                    content="",
                    tool_calls=[{"name": "deep_research", "args": {"action": "status"}, "id": "propose-status"}],
                    usage_metadata=dict(usage),
                )
            return AIMessage(content="Status delivered for this turn.", usage_metadata=dict(usage))

    return _UniformControllerModel()


@pytest.mark.asyncio
async def test_subject_end_to_end_with_scripted_model_through_real_composition(
    tmp_path: Path,
    configured_deerflow_home,  # noqa: F811  (imported fixture from the activation test)
) -> None:
    case = _case()
    app_config = configured_deerflow_home(deferred_discovery=False)

    subject = controller_live_subject(app_config=app_config, provider="fixture-provider", model="fixture-model")
    context = ExecutionContext(workspace=tmp_path / "workspace", fixture=case.fixture)

    counts: dict[str, int] = {"invocations": 0}
    model = _make_uniform_model(counts)
    with patch("deerflow.agents.lead_agent.agent.create_chat_model", return_value=model):
        execution = await subject(context)

    output = execution.output
    updates = output["scenario_updates"]
    assert [row["scenario_id"] for row in updates] == [s["scenario_id"] for s in case.fixture["scenarios"]]
    assert all(row["skill_read_first"] for row in updates)
    assert all(row["proposal"]["kind"] == "action" and row["proposal"]["action"] == "status" for row in updates)
    no_bundle = next(row for row in updates if row["subject_state"] == "no_active_bundle")
    assert no_bundle["lifecycle_calls"] == [{"action": "status", "bundle_id": None, "refinement": None}]

    expected_calls = len(case.fixture["scenarios"])
    # Structural aggregation: every model response counted exactly once, and the
    # subject's totals equal the per-scenario capture sums. Each scenario needs
    # at least the read-skill, propose-action and closing responses.
    assert counts["invocations"] == sum(row["usage"]["model_calls"] for row in updates)
    assert execution.resource_use["model_calls"] == counts["invocations"]
    assert execution.resource_use["model_calls"] >= expected_calls * 3
    assert execution.resource_use["input_tokens"] == counts["invocations"] * 10
    assert execution.resource_use["output_tokens"] == counts["invocations"] * 5
    assert execution.resource_use["tool_calls"] == expected_calls * 2
    committed_digest = hashlib.sha256(SKILL_SOURCE.read_bytes()).hexdigest()
    assert execution.resource_use["skill_digest"] == committed_digest
    assert execution.resource_use["cost_usd"] == 0.0
    assert output["cost_unpriced"] is True
