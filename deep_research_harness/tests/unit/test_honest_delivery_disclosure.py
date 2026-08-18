"""Honest-delivery disclosure chain (BUG-035).

Composed deterministic seam: a non-converging honest searchable gap degrades
the real wave2 gate to a pass, the gate-recorded unresolved gap ids survive in
state, readiness discloses them as mandatory uncertainties, and the final
report text carries the disclosure — plus the canonical-artifact round trip
that keeps gap bodies out of the checkpoint.

@impl WSN-004
@impl REA-003
"""

from __future__ import annotations

import asyncio
import time
from datetime import UTC, datetime

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef
from deerflow_deep_research.domain.publication import FinalDeliveryLayoutCandidate
from deerflow_deep_research.domain.state import BundleLocalState
from deerflow_deep_research.domain.synthesis import (
    WAVE2_GATE_PREVIEW_KEY,
    GapRecord,
    SynthesisResult,
    Wave2GatePreview,
)
from deerflow_deep_research.engine.real_gates import build_wave2_real_gate_def
from deerflow_deep_research.graph.nodes.final_delivery.composer import render_final_artifacts
from deerflow_deep_research.graph.nodes.gate_adapter import evaluate_gate_for_node
from deerflow_deep_research.graph.nodes.readiness.contracts import ReadinessCriticOutput, ReadinessReportPlan
from deerflow_deep_research.graph.nodes.readiness.materializer import materialize_report_plan
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore

BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "H" * 43), scope_bucket="s_" + "H" * 43)
GAP = GapRecord(
    gap_id="gap:share_conflict",
    description="Sources report differing 2024 market-share figures; the divergence is unexplained.",
    priority=2,
    search_required=True,
)


def _gate_state(**overrides):
    base = {
        "generation": 0,
        "execution_trace": ("bootstrap", "hitl1", "topic_planning", "wave0", "wave1"),
        "gate_attempts_by_phase": {"wave2_synthesis": 3},
        "repair_budget_by_phase": {"wave2_synthesis": 0},
        "latest_gate_feedback": None,
        WAVE2_GATE_PREVIEW_KEY: Wave2GatePreview(searchable_gap_ids=(GAP.gap_id,)),
    }
    return {**base, **overrides}


def test_first_exhausted_gap_degrades_and_the_report_discloses_it() -> None:
    # 1. The real wave2 gate hits its exhausted budget on an honest gap that
    #    did not converge: first exhaustion degrades to a pass (BUG-035).
    update = evaluate_gate_for_node(_gate_state(), "wave2_synthesis", build_wave2_real_gate_def())

    assert update["route"] == "pass"
    assert "terminal_status" not in update
    assert update["unresolved_gaps"] == (GAP.gap_id,)
    assert update["degraded_decisions"] == ("wave2_synthesis:exhaustion_degraded",)

    # 2. Readiness discloses the gate-recorded gap as a mandatory uncertainty
    #    (gap body projected from the canonical synthesis artifact).
    critic_output = ReadinessCriticOutput(schema_version=1)
    plan = materialize_report_plan(
        critic_output,
        (),
        unresolved_gap_ids=update["unresolved_gaps"],
        gap_records=(GAP,),
    )

    assert [u.question for u in plan.mandatory_uncertainties] == [f"Unresolved research gap {GAP.gap_id}"]

    # 3. The final report carries the disclosure in its uncertainties section.
    layout = FinalDeliveryLayoutCandidate(
        schema_version=1,
        conclusion_order=(),
        uncertainty_order=("uncertainty:0",),
    )
    report, _citations = render_final_artifacts(plan, layout)

    text = report.decode("utf-8")
    assert "## Uncertainties" in text
    assert GAP.description in text


def test_synthesis_gaps_round_trip_through_the_canonical_artifact(tmp_path) -> None:
    """Gap bodies live only in the canonical artifact; ids live in state."""

    BundleLifecycle(workspace_host_path=tmp_path)._publish_sync(
        BUNDLE, BundleLocalState(bundle_id=BUNDLE.bundle_id, implementation_mode="all_real")
    )
    store = WorkUnitStore(
        workspace_host_path=tmp_path,
        bundle=BUNDLE,
        clock=lambda: datetime(2026, 8, 18, tzinfo=UTC),
        monotonic=time.monotonic,
        lock_sleep=time.sleep,
        token_factory=lambda: "b" * 32,
        fault_hook=None,
    )
    result = SynthesisResult(
        schema_version=1,
        findings=(),
        gaps=(
            GAP,
            GapRecord(gap_id="gap:closed", description="Already resolved.", priority=3),
        ),
    )

    asyncio.run(store.write_synthesis(result))

    assert asyncio.run(store.read_synthesis_gaps()) == result.gaps


def test_readiness_plan_without_gaps_leaves_the_uncertainties_section_empty() -> None:
    plan = materialize_report_plan(ReadinessCriticOutput(schema_version=1), ())

    assert isinstance(plan, ReadinessReportPlan)
    assert plan.mandatory_uncertainties == ()
