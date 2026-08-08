"""Bounded answerability contracts shared by the readiness node.

@impl REA-002
@impl REA-003
@impl REA-006
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from deerflow_deep_research.domain.lifecycle import FrozenContract


class HardRuleFailure(FrozenContract):
    """One deterministic hard-rule failure. Serialized to dict for checkpoint."""

    code: Annotated[str, Field(min_length=1, max_length=96)]
    detail: Annotated[str, Field(max_length=512)] = ""
    refs: Annotated[tuple[str, ...], Field(max_length=16)] = ()


class PerQuestionVerdict(FrozenContract):
    """Answerability verdict for a single must-answer question."""

    question: Annotated[str, Field(min_length=1, max_length=500)]
    verdict: Literal["ready_substantive", "ready_insufficient_judgment", "blocked_repair_required"]
    backing_claim_ids: Annotated[tuple[str, ...], Field(max_length=16)] = ()
    limitation_note: Annotated[str, Field(max_length=1_024)] = ""


class ReadinessCriticOutput(FrozenContract):
    """Structured output from the readiness critic."""

    schema_version: Literal[1] = 1
    per_question: Annotated[tuple[PerQuestionVerdict, ...], Field(max_length=16)] = ()
    overall_limitations: Annotated[tuple[Annotated[str, Field(max_length=512)], ...], Field(max_length=8)] = ()
    synthesis_flaws: Annotated[tuple[Annotated[str, Field(max_length=512)], ...], Field(max_length=8)] = ()
    contradiction_ids: Annotated[tuple[Annotated[str, Field(max_length=128)], ...], Field(max_length=16)] = ()


class ReportPlanConclusion(FrozenContract):
    question: str
    conclusion_text: str
    backing_claim_ids: tuple[str, ...]


class ReportPlanUncertainty(FrozenContract):
    question: str
    limitation: str


class ReportPlanProhibitedUpgrade(FrozenContract):
    claim_id: str
    stated_strength: str
    allowed_strength: str


class ReadinessReportPlan(FrozenContract):
    """Immutable projection of what final delivery may and must include."""

    schema_version: int = 1
    writable_conclusions: tuple[ReportPlanConclusion, ...] = ()
    mandatory_uncertainties: tuple[ReportPlanUncertainty, ...] = ()
    prohibited_upgrades: tuple[ReportPlanProhibitedUpgrade, ...] = ()


__all__ = [
    "HardRuleFailure",
    "PerQuestionVerdict",
    "ReadinessCriticOutput",
    "ReadinessReportPlan",
    "ReportPlanConclusion",
    "ReportPlanProhibitedUpgrade",
    "ReportPlanUncertainty",
]
