"""Outer HumanMessage selection and suspension projection (REG-003/004)."""

from __future__ import annotations

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from deerflow_deep_research.domain.human_interaction import (
    InteractionSubject,
    ProposalValues,
    build_interaction_projection,
)
from deerflow_deep_research.domain.lifecycle import (
    BundleAvailability,
    BundleControlResult,
    BundleRefinementProjection,
    HumanInputMode,
    HumanInputOption,
    HumanInputRequest,
    PendingResearchInterrupt,
    ResponseKind,
    SupportedLanguageOption,
)
from deerflow_deep_research.domain.run_experience import PendingInputProjection
from deerflow_deep_research.runtime.human_input import (
    ConsumedResponseRetry,
    HumanInputError,
    extract_resume_response,
    make_brokered_resume_response,
    project_suspension,
    select_start_message,
)


def _pending(mode: HumanInputMode = HumanInputMode.TEXT) -> PendingResearchInterrupt:
    return PendingResearchInterrupt(
        request=HumanInputRequest(
            request_id="drh_test",
            mode=mode,
            title="Research scope",
            context="safe context",
        ),
        suspension_cursor="cursor",
        phase="hitl1",
        generation=0,
    )


def _action_pending() -> PendingResearchInterrupt:
    return PendingResearchInterrupt(
        request=HumanInputRequest(
            request_id="drh_action",
            mode=HumanInputMode.TEXT,
            title="profile",
            context="safe context",
            action_ids=("accept_suggestion",),
        ),
        suspension_cursor="cursor",
        phase="hitl1",
        generation=0,
    )


def _language_pending(*, request_id: str = "drh_language") -> PendingResearchInterrupt:
    return PendingResearchInterrupt(
        request=HumanInputRequest(
            request_id=request_id,
            mode=HumanInputMode.CHOICE,
            title="Language",
            context="Choose the research language.",
            options=tuple(
                HumanInputOption(id=value, value=value, label=value.value) for value in SupportedLanguageOption
            ),
        ),
        suspension_cursor="cursor",
        phase="hitl1",
        generation=0,
    )


def _interaction():
    return build_interaction_projection(
        InteractionSubject(
            proposal_version=1,
            goal="Compare storage options.",
            proposal=ProposalValues(
                depth="standard",
                audience="practitioner",
                format="detailed_report",
                cost_tolerance="moderate",
                time_budget="standard",
                must_answer=("Which option is safer?",),
            ),
        )
    )


def test_typed_interaction_belongs_only_to_text_hitl1_requests() -> None:
    interaction = _interaction()
    request = HumanInputRequest(
        request_id="drh_interaction",
        mode=HumanInputMode.TEXT,
        title="Research scope",
        context="safe context",
        action_ids=("accept_suggestion",),
        interaction=interaction,
    )
    assert request.interaction == interaction

    with pytest.raises(ValueError, match="interaction_requires_text_input"):
        HumanInputRequest(
            request_id="drh_choice",
            mode=HumanInputMode.CHOICE,
            title="Decision",
            context="safe context",
            interaction=interaction,
        )
    with pytest.raises(ValueError, match="interaction_requires_hitl1"):
        PendingResearchInterrupt(
            request=request,
            suspension_cursor="cursor",
            phase="hitl2",
            generation=0,
        )


def test_start_selects_newest_visible_genuine_message_and_exact_text_blocks() -> None:
    messages = [
        HumanMessage(content="older", id="old"),
        HumanMessage(content="hidden", id="hidden", additional_kwargs={"hide_from_ui": True}),
        HumanMessage(content=[{"type": "text", "text": "new"}, {"type": "text", "text": " request"}], id="new"),
        AIMessage(content="calling tool"),
    ]
    selected = select_start_message(messages)
    assert selected.message_id == "new"
    assert selected.text == "new request"


def test_start_does_not_fall_back_past_invalid_newest_candidate() -> None:
    messages = [HumanMessage(content="older", id="old"), HumanMessage(content="", id="new")]
    with pytest.raises(HumanInputError, match="start_message_invalid"):
        select_start_message(messages)


@pytest.mark.parametrize(
    "content",
    [
        [{"type": "image_url", "image_url": {"url": "x"}}],
        [{"type": "text", "text": "ok", "extra": "no"}],
    ],
)
def test_start_rejects_non_text_or_malformed_blocks(content) -> None:
    with pytest.raises(HumanInputError, match="start_message_invalid"):
        select_start_message([HumanMessage(content=content, id="new")])


def test_structured_hidden_response_is_genuine_and_correlated() -> None:
    payload = {
        "version": 1,
        "kind": "human_input_response",
        "source": "deep_research",
        "request_id": "drh_test",
        "response_kind": "text",
        "value": "answer",
    }
    messages = [
        HumanMessage(content="start", id="cursor"),
        HumanMessage(
            content="formatted",
            id="reply",
            additional_kwargs={"hide_from_ui": True, "human_input_response": payload},
        ),
    ]
    response = extract_resume_response(messages, _pending(), consumed_request_ids=(), consumed_message_ids=())
    assert response.message_id == "reply"
    assert response.value == "answer"


def test_typed_action_requires_advertisement_and_plain_text_cannot_spoof_it() -> None:
    action_payload = {
        "version": 1,
        "kind": "human_input_response",
        "source": "deep_research",
        "request_id": "drh_action",
        "response_kind": "action",
        "action_id": "accept_suggestion",
        "value": "accept_suggestion",
    }
    action_message = HumanMessage(
        content="ignored",
        id="action",
        additional_kwargs={"human_input_response": action_payload},
    )
    accepted = extract_resume_response(
        [HumanMessage(content="start", id="cursor"), action_message],
        _action_pending(),
        consumed_request_ids=(),
        consumed_message_ids=(),
    )
    assert accepted.response_kind is ResponseKind.ACTION

    with pytest.raises(HumanInputError, match="response_invalid"):
        extract_resume_response(
            [
                HumanMessage(content="start", id="cursor"),
                action_message.model_copy(
                    update={"additional_kwargs": {"human_input_response": {**action_payload, "request_id": "drh_test"}}}
                ),
            ],
            _pending(),
            consumed_request_ids=(),
            consumed_message_ids=(),
        )


def test_brokered_action_preserves_type_and_requires_current_advertisement() -> None:
    response = make_brokered_resume_response(
        pending=_action_pending(),
        expected_request_id="drh_action",
        value="accept_suggestion",
        action_id="accept_suggestion",
        message_id="broker-action",
    )
    assert response.response.response_kind is ResponseKind.ACTION
    assert response.response.action_id == "accept_suggestion"

    with pytest.raises(HumanInputError, match="response_invalid"):
        make_brokered_resume_response(
            pending=_pending(),
            expected_request_id="drh_test",
            value="accept_suggestion",
            action_id="accept_suggestion",
            message_id="broker-action",
        )

    with pytest.raises(HumanInputError, match="response_invalid"):
        extract_resume_response(
            [
                HumanMessage(content="start", id="cursor"),
                HumanMessage(content="accept_suggestion", id="spoof"),
            ],
            _action_pending(),
            consumed_request_ids=(),
            consumed_message_ids=(),
        )


def test_hitl1_language_choice_requires_a_current_typed_advertised_option() -> None:
    pending = _language_pending()
    accepted = make_brokered_resume_response(
        pending=pending,
        expected_request_id="drh_language",
        value="zh",
        option_id="zh",
        message_id="broker-language",
    )
    assert accepted.response.response_kind is ResponseKind.OPTION
    assert accepted.response.option_id == "zh"

    with pytest.raises(HumanInputError, match="response_mismatch"):
        make_brokered_resume_response(
            pending=pending,
            expected_request_id="drh_stale",
            value="zh",
            option_id="zh",
            message_id="broker-language",
        )
    with pytest.raises(HumanInputError, match="response_invalid"):
        make_brokered_resume_response(
            pending=pending,
            expected_request_id="drh_language",
            value="zh",
            message_id="broker-language",
        )


def test_forged_non_human_and_stale_message_do_not_resume() -> None:
    messages = [
        HumanMessage(content="start", id="cursor"),
        ToolMessage(content="answer", tool_call_id="x"),
        AIMessage(content="answer"),
    ]
    with pytest.raises(HumanInputError, match="response_mismatch"):
        extract_resume_response(messages, _pending(), consumed_request_ids=(), consumed_message_ids=())


def test_consumed_exact_pair_is_classified_for_reprojection() -> None:
    payload = {
        "version": 1,
        "kind": "human_input_response",
        "source": "deep_research",
        "request_id": "drh_old",
        "response_kind": "text",
        "value": "answer",
    }
    messages = [HumanMessage(content="formatted", id="reply", additional_kwargs={"human_input_response": payload})]
    result = extract_resume_response(
        messages,
        _pending(),
        consumed_request_ids=("drh_old",),
        consumed_message_ids=("reply",),
    )
    assert isinstance(result, ConsumedResponseRetry)


def test_suspension_projection_uses_same_control_envelope_and_omits_internal_cursor() -> None:
    pending = _pending()
    result = BundleControlResult(
        action="start",
        code="suspended",
        availability=BundleAvailability.AVAILABLE,
        durability="same_process",
        bundle_id="b_" + "A" * 43,
        status="suspended",
        phase="hitl1",
        generation=0,
        request_id="drh_test",
        pending_input=PendingInputProjection(
            request_id="drh_test",
            pending_phase="hitl1",
            generation=0,
            mode="text",
        ),
        refinement=BundleRefinementProjection(disposition="none"),
    )
    command = project_suspension(pending=pending, result=result, tool_call_id="tool-call")
    message = command.update["messages"][0]
    assert message.tool_call_id == "tool-call"
    assert message.id == "drh_test"
    assert message.name == "deep_research"
    assert "all_real" in message.content
    assert message.artifact["human_input"]["request_id"] == "drh_test"
    assert "suspension_cursor" not in str(message.artifact)
