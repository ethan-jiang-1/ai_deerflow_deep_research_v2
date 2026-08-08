"""Zero-API wiring replay for the public Deep Research lifecycle tool.

@impl DEC-003
@impl RUI-006
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from langchain.agents import create_agent
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import Runnable
from langchain_core.tools import tool
from pydantic import ValidationError

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_PATH = REPO_ROOT / "deep_research_harness/config/public-skill/deep-research-controller/SKILL.md"
BUNDLE_ID = "b_" + "A" * 43
RETIRED_BUNDLE_ID = "r_" + "A" * 43
REQUEST_ID = "drh_real_request"


def test_public_tool_schema_accepts_only_bundle_id_for_lifecycle_targets() -> None:
    """DRH-003/RUI-006: public controls do not accept the retired research identity."""
    from deerflow_deep_research.tool import DeepResearchArgs

    assert DeepResearchArgs(action="status", bundle_id=BUNDLE_ID).bundle_id == BUNDLE_ID
    with pytest.raises(ValidationError):
        DeepResearchArgs(action="status", bundle_id=RETIRED_BUNDLE_ID)


def test_public_tool_schema_exposes_only_text_bearing_and_explicit_textless_refine_forms() -> None:
    """DRH-005/RUI-006: refinement text and terminal continuation are disjoint."""
    from deerflow_deep_research.tool import DeepResearchArgs

    args = DeepResearchArgs(action="refine", bundle_id=BUNDLE_ID, refinement="Prioritize primary sources")
    assert args.refinement == "Prioritize primary sources"
    continuation = DeepResearchArgs(action="refine", bundle_id=BUNDLE_ID)
    assert continuation.refinement is None
    assert continuation.bundle_id == BUNDLE_ID
    assert DeepResearchArgs(action="refine", bundle_id=BUNDLE_ID, refinement=None).refinement is None
    with pytest.raises(ValidationError):
        DeepResearchArgs(action="refine")
    with pytest.raises(ValidationError):
        DeepResearchArgs(action="refine", bundle_id=BUNDLE_ID, refinement="   ")
    with pytest.raises(ValidationError):
        DeepResearchArgs(action="refine", bundle_id=BUNDLE_ID, refinement="Direction", operation_key="forged")
    with pytest.raises(ValidationError):
        DeepResearchArgs(action="refine", bundle_id=BUNDLE_ID, refinement=False)
    with pytest.raises(ValidationError):
        DeepResearchArgs(action="resume", bundle_id=BUNDLE_ID, refinement="not an answer")


class ReplayToolCallingModel(FakeMessagesListChatModel):
    """Replay committed assistant turns while accepting bound tools."""

    def bind_tools(  # type: ignore[override]
        self,
        tools: Any,
        *,
        tool_choice: Any = None,
        **kwargs: Any,
    ) -> Runnable:
        return self


def test_prewritten_lifecycle_calls_exercise_tool_wiring_only() -> None:
    """Prewritten calls prove tool/result wiring, never controller action selection."""

    calls: list[dict[str, str]] = []

    @tool
    def deep_research(action: str, bundle_id: str | None = None) -> str:
        """All-real global Deep Research lifecycle control tool."""
        call = {"action": action}
        if bundle_id is not None:
            call["bundle_id"] = bundle_id
        calls.append(call)
        if action == "start":
            return json.dumps(
                {
                    "action": "start",
                    "code": "suspended",
                    "implementation_mode": "all_real",
                    "bundle_id": BUNDLE_ID,
                    "request_id": REQUEST_ID,
                },
                sort_keys=True,
            )
        return json.dumps(
            {
                "action": "resume",
                "code": "completed",
                "implementation_mode": "all_real",
                "bundle_id": BUNDLE_ID,
            },
            sort_keys=True,
        )

    wiring_prompt = "This replay prewrites lifecycle calls to exercise tool/result wiring only."
    start_text = f"All-real lifecycle suspended. Keep {BUNDLE_ID} for the matching reply."
    start_model = ReplayToolCallingModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "deep_research",
                        "args": {"action": "start"},
                        "id": "start-call",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(content=start_text),
        ]
    )
    started = create_agent(model=start_model, tools=[deep_research], system_prompt=wiring_prompt).invoke(
        {"messages": [{"role": "user", "content": "Research the question using multiple sources."}]}
    )

    terminal_text = "The all-real lifecycle completed; use the returned lifecycle result for its current outcome."
    resume_model = ReplayToolCallingModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "deep_research",
                        "args": {"action": "resume", "bundle_id": BUNDLE_ID},
                        "id": "resume-call",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(content=terminal_text),
        ]
    )
    resumed = create_agent(model=resume_model, tools=[deep_research], system_prompt=wiring_prompt).invoke(
        {"messages": [{"role": "user", "content": "proceed"}]}
    )

    assert calls == [{"action": "start"}, {"action": "resume", "bundle_id": BUNDLE_ID}]
    start_tool = next(message for message in started["messages"] if isinstance(message, ToolMessage))
    resume_tool = next(message for message in resumed["messages"] if isinstance(message, ToolMessage))
    assert json.loads(start_tool.content)["implementation_mode"] == "all_real"
    assert json.loads(resume_tool.content)["implementation_mode"] == "all_real"
    assert BUNDLE_ID in started["messages"][-1].content
    assert resumed["messages"][-1].content == terminal_text
    assert "fixture" not in terminal_text.casefold()


def test_public_skill_keeps_controller_guidance_bounded() -> None:
    surface = SKILL_PATH.read_text(encoding="utf-8").casefold()
    for required in (
        "implementation_mode=all_real",
        'action="start"',
        'action="resume"',
        'action="refine"',
        "bundle_id",
        "ended",
        "unavailable",
        "exactly one `deep_research`",
        "no sibling tool call",
        "status",
        "cancel",
    ):
        assert required in surface
    for forbidden in (
        "stategraph",
        "fixture controls",
        "phase prompt",
        "security isolation",
        "authorization boundary",
        "research_id",
        "answer=",
        "fixture",
        "full_fake",
    ):
        assert forbidden not in surface
