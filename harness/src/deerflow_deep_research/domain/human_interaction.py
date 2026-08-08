"""Pure bounded contracts for a human reply to a current HITL proposal.

The graph owns whether a candidate becomes a transition. This module only validates
candidate meaning and produces safe presentation facts; it deliberately imports no
runtime, graph, lifecycle, or profile contract.

@impl HIC-001
@impl HIC-002
@impl HIC-003
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MAX_INTERACTION_GOAL_CHARS = 768
MAX_INTERACTION_FEEDBACK_CHARS = 512
MAX_SCOPE_BOUNDARIES_CHARS = 2_048
MAX_CUSTOM_NOTES_CHARS = 1_024
MAX_MUST_ANSWER = 8
MAX_QUESTION_CHARS = 256


class FrozenInteractionContract(BaseModel):
    """Serialized domain data with no graph or runtime authority."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class HumanIntent(StrEnum):
    ACCEPT_CURRENT_PROPOSAL = "accept_current_proposal"
    REVISE_PROPOSAL = "revise_proposal"
    ASK_ABOUT_PROPOSAL = "ask_about_proposal"
    CLARIFY = "clarify"


class InteractionFeedbackKind(StrEnum):
    PROPOSAL_EXPLANATION = "proposal_explanation"
    CLARIFICATION = "clarification"
    COMPARISON_SUBJECTS_REQUIRED = "comparison_subjects_required"
    OUTPUT_LANGUAGE_REQUIRED = "output_language_required"
    SEMANTIC_UNAVAILABLE = "semantic_unavailable"
    SEMANTIC_INVALID = "semantic_invalid"


class InteractionResolutionKind(StrEnum):
    CONFIRM_CURRENT = "confirm_current"
    REVISE_PROPOSAL = "revise_proposal"
    FEEDBACK = "feedback"


class MissingProposalMaterial(StrEnum):
    """Typed proposal facts that must exist before a current proposal is actionable."""

    COMPARISON_SUBJECTS = "comparison_subjects"
    OUTPUT_LANGUAGE = "output_language"


class ProposalValues(FrozenInteractionContract):
    """Every material proposal field, in stable human-safe machine values."""

    schema_version: Literal[1, 2] = 1
    depth: Literal["quick_overview", "standard", "deep_dive", "exhaustive"]
    audience: Literal["layperson", "practitioner", "domain_expert", "executive"]
    format: Literal["executive_brief", "detailed_report", "annotated_bibliography", "faq"]
    cost_tolerance: Literal["minimal", "moderate", "extensive"]
    time_budget: Literal["very_quick", "standard", "thorough", "overnight"]
    must_answer: tuple[str, ...] = Field(min_length=1, max_length=MAX_MUST_ANSWER)
    scope_boundaries: str = Field(default="", max_length=MAX_SCOPE_BOUNDARIES_CHARS)
    custom_notes: str = Field(default="", max_length=MAX_CUSTOM_NOTES_CHARS)
    comparison_required: bool = False
    comparison_subjects: tuple[str, str] | None = None
    request_language: Literal["zh", "en", "unspecified", "legacy_unspecified"] = "legacy_unspecified"
    output_language: Literal["zh", "en"] | None = None

    @field_validator("must_answer", mode="before")
    @classmethod
    def validate_must_answer(cls, value: object) -> tuple[str, ...]:
        if not isinstance(value, (tuple, list)):
            raise ValueError("must_answer_invalid")
        questions = tuple(value)
        if not questions or len(questions) > MAX_MUST_ANSWER:
            raise ValueError("must_answer_invalid")
        if any(
            not isinstance(question, str) or not question.strip() or len(question) > MAX_QUESTION_CHARS
            for question in questions
        ):
            raise ValueError("must_answer_invalid")
        return tuple(question.strip() for question in questions)

    @field_validator("comparison_subjects", mode="before")
    @classmethod
    def validate_comparison_subjects(cls, value: object) -> tuple[str, str] | None:
        if value is None:
            return None
        if isinstance(value, dict):
            value = value.get("subjects")
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            raise ValueError("comparison_subjects_invalid")
        subjects = tuple(value)
        if any(not isinstance(subject, str) or not subject.strip() or len(subject) > 256 for subject in subjects):
            raise ValueError("comparison_subjects_invalid")
        if subjects[0].strip().casefold() == subjects[1].strip().casefold():
            raise ValueError("comparison_subjects_invalid")
        return (subjects[0].strip(), subjects[1].strip())

    def missing_material(self) -> tuple[MissingProposalMaterial, ...]:
        """Return the bounded facts that prevent current-proposal acceptance."""

        if self.schema_version == 1:
            return ()
        missing: list[MissingProposalMaterial] = []
        if self.comparison_required and self.comparison_subjects is None:
            missing.append(MissingProposalMaterial.COMPARISON_SUBJECTS)
        if self.output_language is None:
            missing.append(MissingProposalMaterial.OUTPUT_LANGUAGE)
        return tuple(missing)


class InteractionSubject(FrozenInteractionContract):
    proposal_version: int = Field(ge=1, le=1_000_000)
    goal: str = Field(min_length=1, max_length=MAX_INTERACTION_GOAL_CHARS)
    proposal: ProposalValues


class InteractionFeedback(FrozenInteractionContract):
    kind: InteractionFeedbackKind
    message: str = Field(min_length=1, max_length=MAX_INTERACTION_FEEDBACK_CHARS)


class VisibleControl(FrozenInteractionContract):
    """An adapter-safe control. Its action binding lives in trusted runtime code."""

    id: Literal["accept_current_proposal"]
    label: str = Field(min_length=1, max_length=128)
    consequence: str = Field(min_length=1, max_length=256)


class InteractionProjection(FrozenInteractionContract):
    schema_version: Literal[1] = 1
    subject: InteractionSubject
    feedback: InteractionFeedback | None = None
    missing_material: tuple[MissingProposalMaterial, ...] = Field(default=(), max_length=2)
    controls: tuple[VisibleControl, ...] = Field(default=(), max_length=4)

    @model_validator(mode="after")
    def control_ids_are_unique(self) -> InteractionProjection:
        identifiers = tuple(control.id for control in self.controls)
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("visible_control_ids_duplicate")
        if self.missing_material and self.controls:
            raise ValueError("incomplete_proposal_controls_forbidden")
        if not self.missing_material and not self.controls:
            raise ValueError("complete_proposal_control_required")
        return self


class SemanticCandidate(FrozenInteractionContract):
    """Structured model result that cannot carry graph transport authority."""

    intent: HumanIntent
    revision: ProposalValues | None = None
    explanation: str = Field(default="", max_length=MAX_INTERACTION_FEEDBACK_CHARS)
    clarification: str = Field(default="", max_length=MAX_INTERACTION_FEEDBACK_CHARS)

    @model_validator(mode="after")
    def candidate_shape_matches_intent(self) -> SemanticCandidate:
        if self.intent is HumanIntent.ACCEPT_CURRENT_PROPOSAL:
            if self.revision is not None or self.explanation or self.clarification:
                raise ValueError("confirmation_candidate_invalid")
        elif self.intent is HumanIntent.REVISE_PROPOSAL:
            if self.revision is None or self.explanation or self.clarification:
                raise ValueError("revision_required")
        elif self.intent is HumanIntent.ASK_ABOUT_PROPOSAL:
            if self.revision is not None or not self.explanation or self.clarification:
                raise ValueError("proposal_explanation_required")
        elif self.revision is not None or self.explanation or not self.clarification:
            raise ValueError("clarification_required")
        return self


class InteractionResolution(FrozenInteractionContract):
    kind: InteractionResolutionKind
    revision: ProposalValues | None = None
    feedback: InteractionFeedback | None = None

    @model_validator(mode="after")
    def resolution_shape_matches_kind(self) -> InteractionResolution:
        if self.kind is InteractionResolutionKind.CONFIRM_CURRENT:
            if self.revision is not None or self.feedback is not None:
                raise ValueError("confirmation_resolution_invalid")
        elif self.kind is InteractionResolutionKind.REVISE_PROPOSAL:
            if self.revision is None or self.feedback is not None:
                raise ValueError("revision_resolution_invalid")
        elif self.revision is not None or self.feedback is None:
            raise ValueError("feedback_resolution_invalid")
        return self


def current_proposal_control() -> VisibleControl:
    """Return the stable adapter-facing affordance for a complete current proposal."""

    return VisibleControl(
        id="accept_current_proposal",
        label="Start with the current proposal",
        consequence="Start research using the proposal currently shown.",
    )


def build_interaction_projection(
    subject: InteractionSubject,
    *,
    feedback: InteractionFeedback | None = None,
) -> InteractionProjection:
    missing_material = subject.proposal.missing_material()
    return InteractionProjection(
        subject=subject,
        feedback=feedback,
        missing_material=missing_material,
        controls=() if missing_material else (current_proposal_control(),),
    )


def resolve_semantic_candidate(
    subject: InteractionSubject,
    candidate: SemanticCandidate,
) -> InteractionResolution:
    """Convert a validated candidate into a non-authoritative graph resolution."""

    del subject  # The subject is deliberately not mutable semantic state.
    if candidate.intent is HumanIntent.ACCEPT_CURRENT_PROPOSAL:
        return InteractionResolution(kind=InteractionResolutionKind.CONFIRM_CURRENT)
    if candidate.intent is HumanIntent.REVISE_PROPOSAL:
        return InteractionResolution(kind=InteractionResolutionKind.REVISE_PROPOSAL, revision=candidate.revision)
    if candidate.intent is HumanIntent.ASK_ABOUT_PROPOSAL:
        return InteractionResolution(
            kind=InteractionResolutionKind.FEEDBACK,
            feedback=InteractionFeedback(
                kind=InteractionFeedbackKind.PROPOSAL_EXPLANATION,
                message=candidate.explanation,
            ),
        )
    return InteractionResolution(
        kind=InteractionResolutionKind.FEEDBACK,
        feedback=InteractionFeedback(
            kind=InteractionFeedbackKind.CLARIFICATION,
            message=candidate.clarification,
        ),
    )


__all__ = [
    "HumanIntent",
    "InteractionFeedback",
    "InteractionFeedbackKind",
    "InteractionProjection",
    "InteractionResolution",
    "InteractionResolutionKind",
    "InteractionSubject",
    "MissingProposalMaterial",
    "ProposalValues",
    "SemanticCandidate",
    "VisibleControl",
    "build_interaction_projection",
    "current_proposal_control",
    "resolve_semantic_candidate",
]
