"""Deterministic report plan materializer.

@impl REA-003
"""

from __future__ import annotations

from deerflow_deep_research.domain.synthesis import GapRecord

from .contracts import (
    ReadinessCriticOutput,
    ReadinessReportPlan,
    ReportPlanConclusion,
    ReportPlanUncertainty,
)
from .hard_rules import HardRuleFailure


def _gap_uncertainty(gap_id: str, gap: GapRecord | None) -> ReportPlanUncertainty:
    """Project one gate-recorded unresolved gap as a mandatory uncertainty."""

    question = f"Unresolved research gap {gap_id}"
    if gap is None:
        return ReportPlanUncertainty(
            question=question,
            limitation="Gap description unavailable in the synthesis artifact.",
        )
    return ReportPlanUncertainty(question=question, limitation=gap.description)


def materialize_report_plan(
    critic_output: ReadinessCriticOutput,
    hard_failures: tuple[HardRuleFailure, ...],
    *,
    unresolved_gap_ids: tuple[str, ...] = (),
    gap_records: tuple[GapRecord, ...] = (),
) -> ReadinessReportPlan:
    """Produce an immutable report plan from critic verdicts and hard-rule results.

    - ready_substantive → writable conclusions
    - ready_insufficient_judgment → mandatory uncertainties
    - blocked_repair_required → absent from both (counted by caller)
    - gate-recorded unresolved searchable gaps → mandatory uncertainties
      (gap bodies come only from the canonical synthesis artifact; a recorded
      id without a body still discloses the id honestly)
    """
    conclusions: list[ReportPlanConclusion] = []
    uncertainties: list[ReportPlanUncertainty] = []

    for pq in critic_output.per_question:
        if pq.verdict == "ready_substantive":
            conclusions.append(
                ReportPlanConclusion(
                    question=pq.question,
                    conclusion_text=f"Evidence supports a substantive answer for: {pq.question}",
                    backing_claim_ids=pq.backing_claim_ids,
                )
            )
        elif pq.verdict == "ready_insufficient_judgment":
            uncertainties.append(
                ReportPlanUncertainty(
                    question=pq.question,
                    limitation=pq.limitation_note or "Evidence insufficient for definitive judgment.",
                )
            )

    gaps_by_id = {gap.gap_id: gap for gap in gap_records}
    for gap_id in unresolved_gap_ids:
        uncertainties.append(_gap_uncertainty(gap_id, gaps_by_id.get(gap_id)))

    # Provenance failures become blanket uncertainties
    for f in hard_failures:
        if f.code.startswith("provenance"):
            uncertainties.append(ReportPlanUncertainty(question="(provenance)", limitation=f.detail))

    return ReadinessReportPlan(
        schema_version=1,
        writable_conclusions=tuple(conclusions),
        mandatory_uncertainties=tuple(uncertainties),
    )


__all__ = ["materialize_report_plan"]
