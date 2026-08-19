"""@impl GAK-005, REG-004 — Fixture gate integration tests (unit-level).

Full E2E paths through the compiled graph are covered by the existing
472-test suite (test_research_graph.py, test_research_lifecycle_tool.py,
etc.). These tests focus on gate-specific behaviors at the unit level.
"""

from __future__ import annotations

import pytest
from deerflow_deep_research_fixtures.gates import build_fixture_gate_definitions
from deerflow_deep_research_fixtures.scenario import FixtureScenario

from deerflow_deep_research.domain.gate import PhaseVerdict
from deerflow_deep_research.domain.synthesis import WAVE2_GATE_PREVIEW_KEY, Wave2GatePreview
from deerflow_deep_research.domain.work_units import WORK_UNIT_GATE_VIEW_KEY, WorkUnitGateView
from deerflow_deep_research.engine.gate_kernel import evaluate_gate
from deerflow_deep_research.engine.real_gates import build_wave2_real_gate_def
from deerflow_deep_research.graph.nodes.gate_adapter import evaluate_gate_for_node


def _fixture_gate(phase: str, scenario: FixtureScenario | None = None):
    return build_fixture_gate_definitions(scenario or FixtureScenario())[phase]


def _state(**overrides):
    base = {
        "generation": 0,
        "execution_trace": (),
        "gate_attempts_by_phase": {},
        "repair_budget_by_phase": {},
        "latest_gate_feedback": None,
        WORK_UNIT_GATE_VIEW_KEY: WorkUnitGateView(
            drained=True,
            planned_work_ids=(),
            terminal_attempt_by_work_id={},
            accepted_record_by_work_id={},
            failure_summaries=(),
        ),
    }
    return {**base, **overrides}


# ---------------------------------------------------------------------------
# 11.1 — Fixture gate rules produce identical outcomes
# ---------------------------------------------------------------------------


class TestFixtureGateOutcomes:
    def test_wave0_pass(self) -> None:
        gd = _fixture_gate("wave0")
        result = evaluate_gate(_state(), "wave0", gd)
        assert result.verdict.value == "pass"
        assert result.route == "pass"

    def test_wave0_repair_then_pass(self) -> None:
        scenario = FixtureScenario(wave0=("repair", "pass"))
        gd = _fixture_gate("wave0", scenario)
        s = _state()
        r1 = evaluate_gate(s, "wave0", gd)
        assert r1.verdict.value == "repair"
        assert r1.route == "repair"

        # Second evaluation (after repair)
        s2 = _state(
            gate_attempts_by_phase={"wave0": 1},
            repair_budget_by_phase={"wave0": 2},
            latest_gate_feedback=r1.model_dump(),
            execution_trace=("bootstrap", "topic_planning", "wave0"),
        )
        r2 = evaluate_gate(s2, "wave0", gd)
        assert r2.verdict.value == "pass"
        assert r2.route == "pass"
        assert r2.attempt == 2

    def test_wave2_synthesis_evidence_needed(self) -> None:
        scenario = FixtureScenario(wave2_synthesis=("evidence_needed", "pass"))
        gd = _fixture_gate("wave2_synthesis", scenario)
        s = _state()
        r = evaluate_gate(s, "wave2_synthesis", gd)
        assert r.verdict.value == "repair"
        assert r.route == "evidence_needed"


class TestRealWave2GateOutcomes:
    def test_searchable_gap_routes_evidence_needed_and_projects_only_ids(self) -> None:
        state = _state() | {
            "unresolved_gaps": ("gap:forged-prior",),
            WAVE2_GATE_PREVIEW_KEY: Wave2GatePreview(searchable_gap_ids=("gap:needed", "gap:also-needed")),
        }

        update = evaluate_gate_for_node(state, "wave2_synthesis", build_wave2_real_gate_def())

        assert update["route"] == "evidence_needed"
        assert update["unresolved_gaps"] == ("gap:needed", "gap:also-needed")
        assert WAVE2_GATE_PREVIEW_KEY not in update

    def test_empty_current_preview_clears_fabricated_prior_gap_and_passes(self) -> None:
        state = _state() | {
            "unresolved_gaps": ("gap:forged-prior",),
            WAVE2_GATE_PREVIEW_KEY: Wave2GatePreview(searchable_gap_ids=()),
        }

        update = evaluate_gate_for_node(state, "wave2_synthesis", build_wave2_real_gate_def())

        assert update["route"] == "pass"
        assert update["unresolved_gaps"] == ()

    def test_first_exhausted_gap_degrades_to_honest_pass(self) -> None:
        """@impl WSN-004 — first exhaustion degrades once instead of blocking."""

        state = _state() | {
            "repair_budget_by_phase": {"wave2_synthesis": 0},
            WAVE2_GATE_PREVIEW_KEY: Wave2GatePreview(searchable_gap_ids=("gap:needed",)),
        }

        update = evaluate_gate_for_node(state, "wave2_synthesis", build_wave2_real_gate_def())

        assert update["route"] == "pass"
        assert "terminal_status" not in update
        assert "latest_incident" not in update
        assert update["unresolved_gaps"] == ("gap:needed",)  # kept for disclosure
        assert update["degraded_decisions"] == ("wave2_synthesis:exhaustion_degraded",)

    def test_repeated_searchable_gap_exhausts_to_blocked(self) -> None:
        """@impl WSN-004 — after the one degradation, exhaustion blocks as before."""

        state = _state() | {
            "repair_budget_by_phase": {"wave2_synthesis": 0},
            "degraded_decisions": ("wave2_synthesis:exhaustion_degraded",),
            WAVE2_GATE_PREVIEW_KEY: Wave2GatePreview(searchable_gap_ids=("gap:needed",)),
        }

        update = evaluate_gate_for_node(state, "wave2_synthesis", build_wave2_real_gate_def())

        assert update["route"] == "exhausted"
        assert update["terminal_status"] == "blocked"
        assert update["unresolved_gaps"] == ("gap:needed",)

    def test_missing_current_preview_fails_closed(self) -> None:
        with pytest.raises(ValueError, match="wave2_gate_preview_missing"):
            evaluate_gate_for_node(_state(), "wave2_synthesis", build_wave2_real_gate_def())

    def test_wave2_gate_budget_resolves_two_rounds_for_minimal_profile_intent(self) -> None:
        """@impl WSN-001

        The wave2 gate budget resolver reads the HITL-owned profile intent
        fields: the minimal pair yields two evidence rounds.

        @impl EXI-001
        @impl LSA-001  # deterministic two-round gate budget wiring; real-run
                       # evidence is separately carried by runbook-003
        """
        state = _state() | {
            "cost_tolerance": "minimal",
            "time_budget": "very_quick",
            WAVE2_GATE_PREVIEW_KEY: Wave2GatePreview(searchable_gap_ids=("gap:needed",)),
        }

        result = evaluate_gate(state, "wave2_synthesis", build_wave2_real_gate_def())

        assert result.verdict is PhaseVerdict.REPAIR
        assert result.remaining_budget == 1  # 2 rounds seeded, one decremented

    def test_wave2_gate_budget_keeps_one_round_without_the_minimal_pair(self) -> None:
        """@impl WSN-001

        Absent (or partial) profile intent keeps today's single-round budget.
        """
        for overrides in (
            {},
            {"cost_tolerance": "minimal"},
            {"time_budget": "very_quick"},
            {"cost_tolerance": "moderate", "time_budget": "very_quick"},
        ):
            state = _state() | {
                **overrides,
                WAVE2_GATE_PREVIEW_KEY: Wave2GatePreview(searchable_gap_ids=("gap:needed",)),
            }

            result = evaluate_gate(state, "wave2_synthesis", build_wave2_real_gate_def())

            assert result.verdict is PhaseVerdict.REPAIR
            assert result.remaining_budget == 0  # default one round, decremented

    def test_wave2_preview_cannot_write_other_phase_projection(self) -> None:
        state = _state() | {
            WAVE2_GATE_PREVIEW_KEY: Wave2GatePreview(searchable_gap_ids=("gap:forged",)),
        }

        update = evaluate_gate_for_node(state, "wave0", _fixture_gate("wave0"))

        assert "unresolved_gaps" not in update

    def test_readiness_repair_targeted(self) -> None:
        gd = _fixture_gate("readiness", FixtureScenario(readiness=("repair_targeted", "pass")))
        r = evaluate_gate(_state(), "readiness", gd)
        assert r.verdict.value == "repair"
        assert r.route == "repair_targeted"

    def test_readiness_repair_hitl2(self) -> None:
        gd = _fixture_gate("readiness", FixtureScenario(readiness=("repair_hitl2", "pass")))
        r = evaluate_gate(_state(), "readiness", gd)
        assert r.route == "repair_hitl2"

    def test_final_delivery_evidence_blocked(self) -> None:
        gd = _fixture_gate("final_delivery", FixtureScenario(final_delivery=("evidence_blocked", "pass")))
        r = evaluate_gate(_state(), "final_delivery", gd)
        assert r.verdict.value == "repair"
        assert r.route == "evidence_blocked"


# ---------------------------------------------------------------------------
# 11.3 — GATE_BLOCKED terminal reason
# ---------------------------------------------------------------------------


class TestGateBlockedTerminal:
    def test_fixture_exhaustion_produces_gate_blocked(self) -> None:
        gd = _fixture_gate("wave0", FixtureScenario(wave0=("repair", "pass")))
        # First visit gets "repair", budget is already 0 → BLOCKED
        s = _state(
            repair_budget_by_phase={"wave0": 0},
            execution_trace=("bootstrap", "topic_planning"),
        )
        r = evaluate_gate(s, "wave0", gd)
        assert r.verdict.value == "blocked"


# ---------------------------------------------------------------------------
# 11.4 — Topology snapshot
# ---------------------------------------------------------------------------


class TestTopologySnapshot:
    def test_topology_unchanged(self) -> None:
        from deerflow_deep_research.graph.topology import LOGICAL_NODES, NORMALIZED_EDGES, validate_topology

        validate_topology(LOGICAL_NODES, NORMALIZED_EDGES)
        edge_routes = {(e.source, e.route, e.target) for e in NORMALIZED_EDGES}
        assert ("wave0", "repair", "wave0") in edge_routes
        assert ("wave0", "pass", "wave1") in edge_routes
        assert ("wave0", "exhausted", "blocked") in edge_routes
        assert ("readiness", "repair_targeted", "targeted_evidence") in edge_routes
        assert ("final_delivery", "evidence_blocked", "readiness") in edge_routes
