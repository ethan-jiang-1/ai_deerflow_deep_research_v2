"""Pure candidate-to-fact admission for interactive Research Confirmation.

@impl RCF-001
"""

from __future__ import annotations

import pytest

from deerflow_deep_research.domain.human_interaction import (
    HumanIntent,
    InteractionFeedback,
    InteractionFeedbackKind,
    InteractionSubject,
    ProposalValues,
    SemanticCandidate,
)
from deerflow_deep_research.domain.research_confirmation import (
    AcceptedResearchFacts,
    DirectConfirmation,
    OutstandingResearchDecision,
    SemanticInterpretation,
    admit_research_confirmation,
)


def _proposal(**overrides: object) -> ProposalValues:
    values: dict[str, object] = {
        "schema_version": 2,
        "depth": "deep_dive",
        "audience": "practitioner",
        "format": "detailed_report",
        "cost_tolerance": "moderate",
        "time_budget": "thorough",
        "must_answer": ("Which Python 3.12 changes affect this service?",),
        "scope_boundaries": "Use Python official documentation only.",
        "custom_notes": "Write the result in Chinese.",
        "comparison_required": False,
        "request_language": "zh",
        "output_language": "zh",
    }
    values.update(overrides)
    return ProposalValues(**values)


def _subject(*, proposal: ProposalValues | None = None, version: int = 1) -> InteractionSubject:
    return InteractionSubject(
        proposal_version=version,
        goal="Prepare a Python 3.12 upgrade checklist.",
        proposal=proposal or _proposal(),
    )


def test_unconfirmed_model_proposal_remains_one_outstanding_decision() -> None:
    """@impl RCF-001"""
    subject = _subject()

    outcome = admit_research_confirmation(subject, evidence=None)

    assert isinstance(outcome, OutstandingResearchDecision)
    assert outcome.proposal == subject.proposal
    assert outcome.proposal_version == subject.proposal_version
    assert outcome.feedback is None
    assert set(outcome.model_dump()) == {"proposal", "proposal_version", "feedback"}


@pytest.mark.parametrize("basis", ("visible_control", "clear_text"))
def test_direct_confirmation_accepts_only_the_current_complete_proposal(basis: str) -> None:
    subject = _subject()

    outcome = admit_research_confirmation(subject, evidence=DirectConfirmation(basis=basis))

    assert isinstance(outcome, AcceptedResearchFacts)
    assert outcome.proposal == subject.proposal
    assert outcome.decision_basis == basis
    assert set(outcome.model_dump()) == {"proposal", "decision_basis"}


def test_correlated_semantic_confirmation_is_a_candidate_path_to_current_facts() -> None:
    subject = _subject()

    outcome = admit_research_confirmation(
        subject,
        evidence=SemanticInterpretation(
            candidate=SemanticCandidate(intent=HumanIntent.ACCEPT_CURRENT_PROPOSAL),
        ),
    )

    assert isinstance(outcome, AcceptedResearchFacts)
    assert outcome.proposal == subject.proposal
    assert outcome.decision_basis == "semantic_confirmation"


def test_complete_semantic_revision_requires_a_later_direct_confirmation() -> None:
    subject = _subject()
    revised = _proposal(format="faq", custom_notes="Put compatibility changes first.")

    outcome = admit_research_confirmation(
        subject,
        evidence=SemanticInterpretation(
            candidate=SemanticCandidate(intent=HumanIntent.REVISE_PROPOSAL, revision=revised),
        ),
    )

    assert isinstance(outcome, OutstandingResearchDecision)
    assert outcome.proposal == revised
    assert outcome.proposal_version == subject.proposal_version + 1
    assert outcome.feedback is None

    accepted = admit_research_confirmation(
        _subject(proposal=outcome.proposal, version=outcome.proposal_version),
        evidence=DirectConfirmation(basis="clear_text"),
    )
    assert isinstance(accepted, AcceptedResearchFacts)
    assert accepted.proposal == revised


def test_semantic_fallback_preserves_current_decision_without_admission() -> None:
    subject = _subject()
    feedback = InteractionFeedback(
        kind=InteractionFeedbackKind.SEMANTIC_UNAVAILABLE,
        message="Please confirm the current proposal or try again.",
    )

    outcome = admit_research_confirmation(subject, evidence=SemanticInterpretation(feedback=feedback))

    assert isinstance(outcome, OutstandingResearchDecision)
    assert outcome.proposal == subject.proposal
    assert outcome.proposal_version == subject.proposal_version
    assert outcome.feedback == feedback


def test_incomplete_proposal_cannot_be_accepted_by_direct_confirmation() -> None:
    incomplete = _proposal(
        comparison_required=True,
        comparison_subjects=None,
    )

    outcome = admit_research_confirmation(
        _subject(proposal=incomplete),
        evidence=DirectConfirmation(basis="visible_control"),
    )

    assert isinstance(outcome, OutstandingResearchDecision)
    assert outcome.proposal == incomplete
    assert outcome.proposal_version == 1
