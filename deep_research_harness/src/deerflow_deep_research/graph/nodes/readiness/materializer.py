"""Deterministic report plan materializer.

@impl REA-003
"""

from __future__ import annotations

from deerflow_deep_research.domain.synthesis import Confidence, GapRecord, SynthesisFinding

from .contracts import (
    ReadinessCriticOutput,
    ReadinessReportPlan,
    ReportPlanConclusion,
    ReportPlanUncertainty,
)
from .hard_rules import HardRuleFailure

# The plan contract bounds backing_claim_ids at 16; a finding may carry up to 32.
# The deterministic projection keeps the first 16 in the finding's own order.
_MAX_PLAN_BACKING_REFS = 16


def _substantive_conclusion_text(
    question: str,
    backing_claim_ids: tuple[str, ...],
    findings: tuple[SynthesisFinding, ...],
) -> str:
    """Real conclusion when a backing finding exists; else the honest template.

    The previous hard-coded "Evidence supports a substantive answer for: …"
    silently dropped the actual answer even when the critic judged the run
    ready_substantive and a backing finding carried the statement. Prefer the
    highest-confidence backing finding's statement; only fall back to the
    template when no backing finding is available.
    """
    backing = set(backing_claim_ids)
    best: SynthesisFinding | None = None
    for finding in findings:
        if finding.backing_refs and backing.intersection(finding.backing_refs):
            if best is None or finding.confidence.value <= best.confidence.value:
                best = finding
    if best is not None and best.statement.strip():
        return best.statement.strip()
    return f"Evidence supports a substantive answer for: {question}"


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
    findings: tuple[SynthesisFinding, ...] = (),
    accepted_refs: tuple[str, ...] = (),
    blocked_as_uncertainties: bool = False,
) -> ReadinessReportPlan:
    """Produce an immutable report plan from critic verdicts and hard-rule results.

    - ready_substantive → writable conclusions
    - ready_insufficient_judgment → mandatory uncertainties
    - blocked_repair_required → mandatory uncertainty only in a delivering posture
    - gate-recorded unresolved searchable gaps → mandatory uncertainties
      (gap bodies come only from the canonical synthesis artifact; a recorded
      id without a body still discloses the id honestly)
    - high-confidence findings with complete accepted backing refs → writable
      conclusions (BUG-054): the rule-derived source survives a non-substantive
      critic verdict, which still discloses as a mandatory uncertainty —
      partial conclusions plus disclosed limitations instead of zero delivery.
    """
    conclusions: list[ReportPlanConclusion] = []
    uncertainties: list[ReportPlanUncertainty] = []

    for pq in critic_output.per_question:
        if pq.verdict == "ready_substantive":
            conclusions.append(
                ReportPlanConclusion(
                    question=pq.question,
                    conclusion_text=_substantive_conclusion_text(pq.question, pq.backing_claim_ids, findings),
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
        elif blocked_as_uncertainties:
            uncertainties.append(
                ReportPlanUncertainty(
                    question=pq.question,
                    limitation=pq.limitation_note or "Evidence requires targeted repair before definitive judgment.",
                )
            )

    gaps_by_id = {gap.gap_id: gap for gap in gap_records}
    for gap_id in unresolved_gap_ids:
        uncertainties.append(_gap_uncertainty(gap_id, gaps_by_id.get(gap_id)))

    # Rule-derived writable conclusions (BUG-054): every high-confidence,
    # completely-backed, non-searching finding delivers its statement verbatim.
    # The critic cannot veto this source; its non-substantive verdicts already
    # landed above as disclosed uncertainties.
    accepted = set(accepted_refs)
    for finding in findings:
        if (
            finding.confidence is Confidence.HIGH
            and finding.backing_refs
            and set(finding.backing_refs) <= accepted
            and not finding.search_required
        ):
            conclusions.append(
                ReportPlanConclusion(
                    question=f"Finding {finding.finding_id}",
                    conclusion_text=finding.statement,
                    backing_claim_ids=tuple(finding.backing_refs[:_MAX_PLAN_BACKING_REFS]),
                )
            )

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
