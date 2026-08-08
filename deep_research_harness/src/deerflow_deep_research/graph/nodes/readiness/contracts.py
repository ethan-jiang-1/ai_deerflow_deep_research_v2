"""Readiness node contracts.

@impl REA-001
@impl REA-002
@impl REA-003
"""

from __future__ import annotations

from deerflow_deep_research.domain.lifecycle import FrozenContract, ReadinessVerdict
from deerflow_deep_research.domain.readiness import (
    HardRuleFailure,
    PerQuestionVerdict,
    ReadinessCriticOutput,
    ReadinessReportPlan,
    ReportPlanConclusion,
    ReportPlanProhibitedUpgrade,
    ReportPlanUncertainty,
)


class ReadinessRequest(FrozenContract):
    generation: int


class ReadinessResult(FrozenContract):
    route: ReadinessVerdict


CONTRACTS = (ReadinessRequest, ReadinessResult)

__all__ = [
    "CONTRACTS",
    "HardRuleFailure",
    "PerQuestionVerdict",
    "ReadinessCriticOutput",
    "ReadinessReportPlan",
    "ReportPlanConclusion",
    "ReportPlanProhibitedUpgrade",
    "ReportPlanUncertainty",
    "ReadinessRequest",
    "ReadinessResult",
]
