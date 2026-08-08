"""Pure admission of a current research proposal into user-authorized facts.

This port receives only typed, already-correlated decision evidence. It neither
interprets free text nor owns lifecycle effects.

@impl RCF-001
"""

from __future__ import annotations

from typing import Literal

from pydantic import model_validator

from deerflow_deep_research.domain.human_interaction import (
    FrozenInteractionContract,
    InteractionFeedback,
    InteractionFeedbackKind,
    InteractionResolutionKind,
    InteractionSubject,
    ProposalValues,
    SemanticCandidate,
    resolve_semantic_candidate,
)


class DirectConfirmation(FrozenInteractionContract):
    """Trusted adapter evidence for an explicit current-user confirmation."""

    basis: Literal["visible_control", "clear_text"]


class SemanticInterpretation(FrozenInteractionContract):
    """A bounded model candidate or bounded semantic-path feedback."""

    candidate: SemanticCandidate | None = None
    feedback: InteractionFeedback | None = None

    @model_validator(mode="after")
    def has_one_semantic_result(self) -> SemanticInterpretation:
        if (self.candidate is None) == (self.feedback is None):
            raise ValueError("semantic_interpretation_result_required")
        return self


class AcceptedResearchFacts(FrozenInteractionContract):
    """The only proposal facts that HITL1 may materialize into a profile."""

    proposal: ProposalValues
    decision_basis: Literal["visible_control", "clear_text", "semantic_confirmation"]

    @model_validator(mode="after")
    def proposal_is_complete(self) -> AcceptedResearchFacts:
        if self.proposal.missing_material():
            raise ValueError("accepted_proposal_incomplete")
        return self


class OutstandingResearchDecision(FrozenInteractionContract):
    """One current or revised advisory proposal that still needs a user decision."""

    proposal: ProposalValues
    proposal_version: int
    feedback: InteractionFeedback | None = None


type ResearchConfirmationEvidence = DirectConfirmation | SemanticInterpretation
type ResearchConfirmationOutcome = AcceptedResearchFacts | OutstandingResearchDecision


def _outstanding(
    subject: InteractionSubject,
    *,
    feedback: InteractionFeedback | None = None,
) -> OutstandingResearchDecision:
    return OutstandingResearchDecision(
        proposal=subject.proposal,
        proposal_version=subject.proposal_version,
        feedback=feedback,
    )


def _incomplete_revision_feedback(subject: InteractionSubject) -> InteractionFeedback:
    return InteractionFeedback(
        kind=InteractionFeedbackKind.CLARIFICATION,
        message=(
            "请在完整修订中保留比较对象和输出语言。"
            if subject.proposal.output_language == "zh"
            else "Please retain the comparison subjects and output language in a complete revision."
        ),
    )


def _revised_outstanding(
    subject: InteractionSubject,
    revision: ProposalValues,
) -> OutstandingResearchDecision:
    """Keep request-derived comparison and language facts across a semantic revision."""

    if subject.proposal.schema_version == 2 and (
        revision.schema_version != 2
        or revision.output_language is None
        or (subject.proposal.comparison_required and revision.comparison_subjects is None)
    ):
        return _outstanding(subject, feedback=_incomplete_revision_feedback(subject))

    revised = revision.model_copy(
        update={
            "comparison_required": subject.proposal.comparison_required,
            "request_language": subject.proposal.request_language,
        }
    )
    if revised.missing_material():
        return _outstanding(subject, feedback=_incomplete_revision_feedback(subject))
    return OutstandingResearchDecision(
        proposal=revised,
        proposal_version=subject.proposal_version + 1,
    )


def admit_research_confirmation(
    subject: InteractionSubject,
    evidence: ResearchConfirmationEvidence | None,
) -> ResearchConfirmationOutcome:
    """Admit only a directly confirmed current complete proposal as research facts."""

    if evidence is None:
        return _outstanding(subject)

    if isinstance(evidence, DirectConfirmation):
        if subject.proposal.missing_material():
            return _outstanding(subject)
        return AcceptedResearchFacts(proposal=subject.proposal, decision_basis=evidence.basis)

    if evidence.feedback is not None:
        return _outstanding(subject, feedback=evidence.feedback)

    assert evidence.candidate is not None
    resolution = resolve_semantic_candidate(subject, evidence.candidate)
    if resolution.kind is InteractionResolutionKind.CONFIRM_CURRENT:
        if subject.proposal.missing_material():
            return _outstanding(subject)
        return AcceptedResearchFacts(proposal=subject.proposal, decision_basis="semantic_confirmation")
    if resolution.kind is InteractionResolutionKind.REVISE_PROPOSAL:
        assert resolution.revision is not None
        return _revised_outstanding(subject, resolution.revision)

    assert resolution.feedback is not None
    return _outstanding(subject, feedback=resolution.feedback)


__all__ = [
    "AcceptedResearchFacts",
    "DirectConfirmation",
    "OutstandingResearchDecision",
    "ResearchConfirmationEvidence",
    "ResearchConfirmationOutcome",
    "SemanticInterpretation",
    "admit_research_confirmation",
]
