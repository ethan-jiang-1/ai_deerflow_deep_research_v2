"""Pure contracts for bounded HITL proposal interaction.

@impl HIC-001
@impl HIC-002
@impl HIC-003
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from deerflow_deep_research.domain.human_interaction import (
    HumanIntent,
    InteractionFeedback,
    InteractionFeedbackKind,
    InteractionResolutionKind,
    InteractionSubject,
    MissingProposalMaterial,
    ProposalValues,
    SemanticCandidate,
    build_interaction_projection,
    resolve_semantic_candidate,
)


def _proposal(**overrides: object) -> ProposalValues:
    values: dict[str, object] = {
        "schema_version": 2,
        "depth": "deep_dive",
        "audience": "domain_expert",
        "format": "detailed_report",
        "cost_tolerance": "moderate",
        "time_budget": "thorough",
        "must_answer": ("What is the adoption level?",),
        "scope_boundaries": "Use primary sources.",
        "custom_notes": "Include citations.",
        "comparison_required": False,
        "comparison_subjects": None,
        "request_language": "en",
        "output_language": "en",
    }
    values.update(overrides)
    return ProposalValues(**values)


def _subject(**overrides: object) -> InteractionSubject:
    values: dict[str, object] = {
        "proposal_version": 1,
        "goal": "Assess OpenSpec adoption and effects.",
        "proposal": _proposal(),
    }
    values.update(overrides)
    return InteractionSubject(**values)


def test_confirmation_candidate_is_not_an_action() -> None:
    resolution = resolve_semantic_candidate(
        _subject(),
        SemanticCandidate(intent=HumanIntent.ACCEPT_CURRENT_PROPOSAL),
    )

    assert resolution.kind is InteractionResolutionKind.CONFIRM_CURRENT
    assert resolution.revision is None
    assert resolution.feedback is None


def test_revision_requires_full_profile_and_fresh_confirmation() -> None:
    revised = _proposal(cost_tolerance="extensive", time_budget="overnight")
    resolution = resolve_semantic_candidate(
        _subject(),
        SemanticCandidate(intent=HumanIntent.REVISE_PROPOSAL, revision=revised),
    )

    assert resolution.kind is InteractionResolutionKind.REVISE_PROPOSAL
    assert resolution.revision == revised
    assert resolution.feedback is None

    with pytest.raises(ValidationError, match="revision_required"):
        SemanticCandidate(intent=HumanIntent.REVISE_PROPOSAL)


def test_question_becomes_bounded_feedback_without_changing_subject() -> None:
    subject = _subject()
    resolution = resolve_semantic_candidate(
        subject,
        SemanticCandidate(
            intent=HumanIntent.ASK_ABOUT_PROPOSAL,
            explanation="Moderate cost preserves breadth while keeping the scope practical.",
        ),
    )

    assert resolution.kind is InteractionResolutionKind.FEEDBACK
    assert resolution.feedback == InteractionFeedback(
        kind=InteractionFeedbackKind.PROPOSAL_EXPLANATION,
        message="Moderate cost preserves breadth while keeping the scope practical.",
    )
    assert subject.proposal.cost_tolerance == "moderate"


def test_projection_preserves_feedback_and_only_exposes_visible_control() -> None:
    projection = build_interaction_projection(
        _subject(),
        feedback=InteractionFeedback(
            kind=InteractionFeedbackKind.SEMANTIC_UNAVAILABLE,
            message="I could not interpret that reply right now. You can try again or start with this proposal.",
        ),
    )

    assert projection.subject.proposal_version == 1
    assert projection.feedback is not None
    assert tuple(control.id for control in projection.controls) == ("accept_current_proposal",)
    assert not hasattr(projection.controls[0], "action_id")


def test_v2_incomplete_comparison_has_focused_material_but_no_acceptance_control() -> None:
    incomplete = _subject(
        proposal=_proposal(
            schema_version=2,
            comparison_required=True,
            comparison_subjects=None,
            request_language="zh",
            output_language="zh",
        )
    )

    projection = build_interaction_projection(incomplete)

    assert projection.subject.proposal.comparison_required is True
    assert projection.missing_material == (MissingProposalMaterial.COMPARISON_SUBJECTS,)
    assert projection.controls == ()


def test_complete_v2_projection_displays_pair_and_language_before_acceptance() -> None:
    complete = _subject(
        proposal=_proposal(
            schema_version=2,
            comparison_required=True,
            comparison_subjects=("锂离子电池", "钒液流电池"),
            request_language="zh",
            output_language="zh",
        )
    )

    projection = build_interaction_projection(complete)

    assert projection.subject.proposal.comparison_subjects == ("锂离子电池", "钒液流电池")
    assert projection.subject.proposal.output_language == "zh"
    assert projection.missing_material == ()
    assert tuple(control.id for control in projection.controls) == ("accept_current_proposal",)


@pytest.mark.parametrize(
    "candidate",
    (
        {"intent": "unknown"},
        {"intent": "revise_proposal", "revision": {"depth": "deep_dive"}},
        {"intent": "accept_current_proposal", "action_id": "accept_suggestion"},
        {"intent": "ask_about_proposal", "explanation": "x" * 513},
    ),
)
def test_invalid_candidates_fail_closed(candidate: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        SemanticCandidate.model_validate(candidate)
