"""Tests for the real readiness critic boundary.

@impl REA-001
@impl REA-002
@impl REA-004
@impl REA-006
@impl REA-007
@impl REA-008
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import time
from dataclasses import replace
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, bundle_readiness_report_plan_path
from deerflow_deep_research.domain.context import GraphContextView, NodeAgentContext, NodeExecutionResult
from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.domain.lifecycle import LifecycleStatus
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.state import BundleLocalState, ContentRef
from deerflow_deep_research.domain.synthesis import GapRecord, SynthesisEvidence, SynthesisFinding
from deerflow_deep_research.domain.work_units import canonical_json_bytes
from deerflow_deep_research.graph.nodes.readiness.contracts import ReadinessReportPlan
from deerflow_deep_research.graph.nodes.readiness.critic import (
    MAX_READINESS_EVIDENCE_BYTES,
    build_readiness_critic_request,
)
from deerflow_deep_research.graph.nodes.readiness.hard_rules import run_hard_rules
from deerflow_deep_research.graph.nodes.readiness.node import build_real
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore

LEDGER_HASH = "h_" + "A" * 43
BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "A" * 43)


class ScriptedStore:
    def __init__(
        self,
        *,
        fail: bool = False,
        plan_fail: bool = False,
        gaps: tuple[GapRecord, ...] = (),
    ) -> None:
        self.fail = fail
        self.plan_fail = plan_fail
        self.gaps = gaps
        self.calls: list[tuple[str, ...]] = []
        self.written_plans: list[ReadinessReportPlan] = []

    async def read_synthesis_gaps(self) -> tuple[GapRecord, ...]:
        if self.fail:
            raise ValueError("synthesis artifact unavailable")
        return self.gaps

    async def read_synthesis_findings(self) -> tuple[SynthesisFinding, ...]:
        if self.fail:
            raise ValueError("synthesis artifact unavailable")
        return ()

    async def read_synthesis_evidence(self, accepted_refs: tuple[str, ...]) -> tuple[SynthesisEvidence, ...]:
        self.calls.append(accepted_refs)
        if self.fail:
            raise ValueError("synthesis_evidence_integrity_mismatch: /private/raw-path")
        return tuple(
            SynthesisEvidence(
                submission_ref=ref,
                phase="wave1",
                result_contract="wave1.evidence-extraction",
                content=json.dumps({"claim": f"Evidence for {ref}"}),
            )
            for ref in accepted_refs
        )

    async def write_readiness_report_plan(self, plan: ReadinessReportPlan) -> ContentRef:
        self.written_plans.append(plan)
        if self.plan_fail:
            raise OSError("review subtree unavailable")
        raw = canonical_json_bytes(plan.model_dump(mode="json"))
        digest = base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).decode("ascii").rstrip("=")
        return ContentRef(
            sandbox_path=bundle_readiness_report_plan_path(BUNDLE),
            content_hash=f"h_{digest}",
            short_summary="readiness-report-plan.json",
        )


class ScriptedCapabilities:
    def __init__(self, response: str | None = None, *, raises: bool = False) -> None:
        self.response = response
        self.raises = raises
        self.requests = []

    async def run_agent(self, *, context, request) -> NodeExecutionResult:
        self.requests.append((context, request))
        if self.raises:
            raise RuntimeError("provider failure")
        return NodeExecutionResult(
            finish_reason=NodeFinishReason.SUCCESS,
            summary=self.response or _candidate(("Q1",), LEDGER_HASH),
        )


def _candidate(
    questions: tuple[str, ...],
    ref: str = LEDGER_HASH,
    *,
    verdict: str = "ready_substantive",
    extras: bool = False,
) -> str:
    payload: dict[str, object] = {
        "schema_version": 1,
        "per_question": [
            {
                "question": question,
                "verdict": verdict,
                "backing_claim_ids": [ref],
                "limitation_note": "Bounded fixture limitation.",
            }
            for question in questions
        ],
    }
    if extras:
        payload.update(
            overall_limitations=["unretained"],
            synthesis_flaws=["unretained"],
            contradiction_ids=["unretained"],
        )
    return json.dumps(payload)


def _deps(
    *,
    response: str | None = None,
    raises: bool = False,
    store_fail: bool = False,
    plan_fail: bool = False,
    gaps: tuple[GapRecord, ...] = (),
):
    graph = GraphContextView(
        research_scope_id=BUNDLE.bundle_id.value,
        workspace_root="/mnt/user-data/workspace/deep-research/r",
        uploads_root="/mnt/user-data/uploads",
        outputs_root="/mnt/user-data/outputs/deep-research/r",
    )
    capabilities = ScriptedCapabilities(response, raises=raises)
    store = ScriptedStore(fail=store_fail, plan_fail=plan_fail, gaps=gaps)
    dependencies = NodeBuildDependencies(
        graph_context=graph,
        agent_context=NodeAgentContext(
            research_scope_id=graph.research_scope_id,
            node_name="readiness",
            attempt_id="g0-readiness-a1",
            workspace_root=graph.workspace_root,
            attempt_root=f"{graph.workspace_root}/readiness",
            policy_name="readiness-evidence-critic",
        ),
        capabilities=capabilities,
        work_units=SimpleNamespace(store=store),
    )
    return dependencies, capabilities, store


def _state(*, questions: tuple[str, ...] = ("Q1",), refs: tuple[str, ...] = (LEDGER_HASH,)) -> dict[str, object]:
    return {
        "bundle_id": BUNDLE.bundle_id.value,
        "generation": 0,
        "accepted_submission_refs": refs,
        "must_answer_questions": questions,
        "consumed_request_ids": ("req_001",),
    }


class TestRealReadiness:
    @pytest.mark.asyncio
    async def test_admitted_plan_round_trips_at_its_canonical_hashed_ref(self, tmp_path) -> None:
        BundleLifecycle(workspace_host_path=tmp_path)._publish_sync(
            BUNDLE, BundleLocalState(bundle_id=BUNDLE.bundle_id, implementation_mode="all_real")
        )
        store = WorkUnitStore(
            workspace_host_path=tmp_path,
            bundle=BUNDLE,
            clock=lambda: datetime(2026, 7, 30, tzinfo=UTC),
            monotonic=time.monotonic,
            lock_sleep=time.sleep,
            token_factory=lambda: "a" * 32,
            fault_hook=None,
        )
        plan = ReadinessReportPlan.model_validate(
            {
                "writable_conclusions": [
                    {"question": "Q1", "conclusion_text": "Approved conclusion.", "backing_claim_ids": [LEDGER_HASH]}
                ],
                "mandatory_uncertainties": [{"question": "Q1", "limitation": "Bounded limitation."}],
            }
        )

        ref = await store.write_readiness_report_plan(plan)

        assert ref.sandbox_path == bundle_readiness_report_plan_path(BUNDLE)
        assert await store.read_readiness_report_plan(ref) == canonical_json_bytes(plan.model_dump(mode="json"))

    def test_canonical_ledger_hash_passes_provenance(self) -> None:
        assert run_hard_rules(_state()) == ()

    def test_all_clear_routes_pass_with_admitted_candidate(self) -> None:
        """@impl REA-003"""
        dependencies, capabilities, store = _deps(response=_candidate(("Q1", "Q2")))
        result = asyncio.run(build_real(dependencies)(_state(questions=("Q1", "Q2"))))
        assert result["route"] == "pass"
        assert result["readiness_blocked_count"] == 0
        assert len(result["readiness_critic_summary"]["per_question"]) == 2
        assert store.calls == [(LEDGER_HASH,)]
        assert len(capabilities.requests) == 1
        _context, request = capabilities.requests[0]
        assert request.tools_enabled is False
        assert "<untrusted-source-data>" in request.objective
        assert "</untrusted-source-data>" in request.objective
        assert len(store.written_plans) == 1
        assert result["readiness_report_plan"].content_hash == (
            "h_"
            + base64.urlsafe_b64encode(
                hashlib.sha256(canonical_json_bytes(store.written_plans[0].model_dump(mode="json"))).digest()
            )
            .decode("ascii")
            .rstrip("=")
        )

    def test_request_bounds_the_ledger_evidence_projection(self) -> None:
        request = build_readiness_critic_request(
            ("Q1",),
            (
                SynthesisEvidence(
                    submission_ref=LEDGER_HASH,
                    phase="wave1",
                    result_contract="wave1.evidence-extraction",
                    content="x" * 24_000,
                ),
                SynthesisEvidence(
                    submission_ref="h_" + "B" * 43,
                    phase="wave1",
                    result_contract="wave1.evidence-extraction",
                    content="y" * 24_000,
                ),
            ),
        )
        rendered_projection = request.objective.split("<untrusted-source-data>\n", 1)[1].split(
            "\n</untrusted-source-data>", 1
        )[0]
        projection = json.loads(rendered_projection)
        assert sum(len(item["content"].encode("utf-8")) for item in projection) <= MAX_READINESS_EVIDENCE_BYTES

    def test_autonomous_hitl2_requires_no_consumed_request(self) -> None:
        """@impl REA-005"""
        dependencies, _capabilities, _store = _deps(response=_candidate(()))
        state = _state(questions=())
        state["consumed_request_ids"] = ()
        result = asyncio.run(build_real(dependencies)(state))
        assert result["route"] == "pass"
        assert result["readiness_hard_failures"] == ()

    def test_candidate_unknown_or_duplicate_question_fails_closed(self) -> None:
        unknown = _candidate(("Q1", "unknown"))
        duplicate = _candidate(("Q1", "Q1"))
        for response in (unknown, duplicate, "not-json"):
            dependencies, _capabilities, store = _deps(response=response)
            result = asyncio.run(build_real(dependencies)(_state()))
            assert result["route"] == "pass"
            assert result["readiness_critic_summary"]["per_question"][0]["verdict"] == ("ready_insufficient_judgment")
            assert store.written_plans[0].mandatory_uncertainties[0].limitation == (
                "Readiness critic did not produce an admissible answerability verdict."
            )

    def test_candidate_rejects_unknown_backing_ref(self) -> None:
        dependencies, _capabilities, store = _deps(response=_candidate(("Q1",), "h_" + "B" * 43))
        result = asyncio.run(build_real(dependencies)(_state()))
        assert result["route"] == "pass"
        assert result["readiness_critic_summary"]["per_question"][0]["backing_claim_ids"] == []
        assert result["readiness_critic_summary"]["per_question"][0]["verdict"] == ("ready_insufficient_judgment")
        assert len(store.written_plans[0].mandatory_uncertainties) == 1

    def test_parseable_unused_fields_are_not_checkpointed(self) -> None:
        dependencies, _capabilities, _store = _deps(response=_candidate(("Q1",), extras=True))
        result = asyncio.run(build_real(dependencies)(_state()))
        summary = result["readiness_critic_summary"]
        assert set(summary) == {"schema_version", "per_question"}
        assert "unretained" not in json.dumps(summary)

    def test_bridge_failure_projects_disclosed_insufficiency_and_delivers(self) -> None:
        dependencies, capabilities, store = _deps(raises=True)
        result = asyncio.run(build_real(dependencies)(_state(questions=("Q1", "Q2"))))
        assert result["route"] == "pass"
        assert len(capabilities.requests) == 1
        assert {item["verdict"] for item in result["readiness_critic_summary"]["per_question"]} == {
            "ready_insufficient_judgment"
        }
        assert {item.question for item in store.written_plans[0].mandatory_uncertainties} == {"Q1", "Q2"}
        assert {item.limitation for item in store.written_plans[0].mandatory_uncertainties} == {
            "Readiness critic did not produce an admissible answerability verdict."
        }

    def test_gapless_admitted_blocked_verdict_delivers_with_disclosure(self) -> None:
        dependencies, _capabilities, store = _deps(response=_candidate(("Q1",), verdict="blocked_repair_required"))

        result = asyncio.run(build_real(dependencies)(_state()))

        assert result["route"] == "pass"
        assert result["readiness_blocked_count"] == 1
        assert len(store.written_plans[0].mandatory_uncertainties) == 1
        assert store.written_plans[0].mandatory_uncertainties[0].question == "Q1"
        assert store.written_plans[0].mandatory_uncertainties[0].limitation == "Bounded fixture limitation."

    def test_admitted_blocked_verdict_with_declared_gap_still_repairs(self) -> None:
        dependencies, _capabilities, store = _deps(
            response=_candidate(("Q1",), verdict="blocked_repair_required"),
            gaps=(GAP_CONFLICT,),
        )
        state = _state()
        state["unresolved_gaps"] = (GAP_CONFLICT.gap_id,)

        result = asyncio.run(build_real(dependencies)(state))

        assert result["route"] == "repair_targeted"
        assert result["readiness_blocked_count"] == 1
        assert all(item.question != "Q1" for item in store.written_plans[0].mandatory_uncertainties)

    def test_store_integrity_failure_is_structural_and_skips_model(self) -> None:
        dependencies, capabilities, _store = _deps(store_fail=True)
        result = asyncio.run(build_real(dependencies)(_state()))
        assert result["route"] == "exhausted"
        assert result["terminal_status"] == LifecycleStatus.BLOCKED.value
        assert result["readiness_hard_failures"] == (
            {"code": "synthesis_evidence_unavailable", "detail": "", "refs": ()},
            {"code": "synthesis_findings_unavailable", "detail": "", "refs": ()},
        )
        assert capabilities.requests == []

    def test_plan_persistence_failure_never_emits_a_fabricated_ref(self) -> None:
        dependencies, _capabilities, store = _deps(plan_fail=True)
        result = asyncio.run(build_real(dependencies)(_state()))

        assert result["route"] == "exhausted"
        assert "readiness_report_plan" not in result
        assert len(store.written_plans) == 1

    def test_missing_work_unit_controller_fails_before_node_invocation(self) -> None:
        dependencies, _capabilities, _store = _deps()
        with pytest.raises(ValueError, match="work_unit_capability_missing"):
            build_real(
                dependencies.__class__(
                    graph_context=dependencies.graph_context,
                    agent_context=dependencies.agent_context,
                    capabilities=dependencies.capabilities,
                )
            )


GAP_CONFLICT = GapRecord(
    gap_id="gap:share_conflict",
    description="Sources report differing 2024 market-share figures; the divergence is unexplained.",
    priority=2,
    search_required=True,
)


class TestWave2DegradedRoute:
    """BUG-044: after the wave2 gate degrades, readiness must deliver, not re-open the spent repair loop."""

    DEGRADED = ("wave2_synthesis:exhaustion_degraded",)

    def test_bridge_failure_in_degraded_run_routes_pass_with_disclosure(self) -> None:
        dependencies, _capabilities, store = _deps(raises=True, gaps=(GAP_CONFLICT,))
        state = _state(questions=("Q1",))
        state["degraded_decisions"] = self.DEGRADED
        state["unresolved_gaps"] = (GAP_CONFLICT.gap_id,)

        result = asyncio.run(build_real(dependencies)(state))

        assert result["route"] == "pass"
        assert result["readiness_blocked_count"] == 0
        assert {item["verdict"] for item in result["readiness_critic_summary"]["per_question"]} == {
            "ready_insufficient_judgment"
        }
        uncertainties = store.written_plans[0].mandatory_uncertainties
        assert any(
            u.question == f"Unresolved research gap {GAP_CONFLICT.gap_id}" and u.limitation == GAP_CONFLICT.description
            for u in uncertainties
        )

    def test_rejected_candidate_in_degraded_run_routes_pass(self) -> None:
        for response in (_candidate(("Q1", "unknown")), _candidate(("Q1", "Q1")), "not-json"):
            dependencies, _capabilities, store = _deps(response=response, gaps=(GAP_CONFLICT,))
            state = _state()
            state["degraded_decisions"] = self.DEGRADED
            state["unresolved_gaps"] = (GAP_CONFLICT.gap_id,)

            result = asyncio.run(build_real(dependencies)(state))

            assert result["route"] == "pass"
            assert result["readiness_critic_summary"]["per_question"][0]["verdict"] == ("ready_insufficient_judgment")
            assert any(
                u.question == f"Unresolved research gap {GAP_CONFLICT.gap_id}"
                for u in store.written_plans[0].mandatory_uncertainties
            )

    def test_structural_failure_still_routes_exhausted_in_degraded_run(self) -> None:
        dependencies, _capabilities, _store = _deps(store_fail=True)
        state = _state()
        state["degraded_decisions"] = self.DEGRADED

        result = asyncio.run(build_real(dependencies)(state))

        assert result["route"] == "exhausted"
        assert result["terminal_status"] == LifecycleStatus.BLOCKED.value
        assert result["readiness_hard_failures"] == (
            {"code": "synthesis_evidence_unavailable", "detail": "", "refs": ()},
            {"code": "synthesis_findings_unavailable", "detail": "", "refs": ()},
        )

    def test_ready_verdicts_in_degraded_run_still_route_pass(self) -> None:
        dependencies, _capabilities, store = _deps(response=_candidate(("Q1",)))
        state = _state()
        state["degraded_decisions"] = self.DEGRADED

        result = asyncio.run(build_real(dependencies)(state))

        assert result["route"] == "pass"
        assert result["readiness_blocked_count"] == 0
        assert len(store.written_plans) == 1


class TestHonestGapDisclosure:
    """@impl REA-003 — unresolved searchable gaps become disclosed uncertainties."""

    def test_matched_gap_becomes_a_disclosed_uncertainty(self) -> None:
        dependencies, _capabilities, store = _deps(gaps=(GAP_CONFLICT,))
        state = _state()
        state["unresolved_gaps"] = ("gap:share_conflict",)

        asyncio.run(build_real(dependencies)(state))

        uncertainties = store.written_plans[0].mandatory_uncertainties
        assert any(
            u.question == "Unresolved research gap gap:share_conflict" and u.limitation == GAP_CONFLICT.description
            for u in uncertainties
        )

    def test_recorded_gap_id_without_a_body_discloses_the_id_only(self) -> None:
        dependencies, _capabilities, store = _deps(gaps=())
        state = _state()
        state["unresolved_gaps"] = ("gap:missing_body",)

        asyncio.run(build_real(dependencies)(state))

        uncertainties = store.written_plans[0].mandatory_uncertainties
        assert any(
            u.question == "Unresolved research gap gap:missing_body"
            and u.limitation == "Gap description unavailable in the synthesis artifact."
            for u in uncertainties
        )

    def test_failed_gap_read_still_discloses_the_id(self) -> None:
        dependencies, _capabilities, store = _deps(store_fail=True)
        state = _state()
        state["unresolved_gaps"] = ("gap:any",)

        asyncio.run(build_real(dependencies)(state))

        uncertainties = store.written_plans[0].mandatory_uncertainties
        assert any(u.question == "Unresolved research gap gap:any" for u in uncertainties)

    def test_no_unresolved_gaps_keeps_the_plan_unchanged(self) -> None:
        dependencies, _capabilities, store = _deps(gaps=(GAP_CONFLICT,))

        asyncio.run(build_real(dependencies)(_state()))

        uncertainties = store.written_plans[0].mandatory_uncertainties
        assert uncertainties == ()


class _RecordingEventRecorder:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    async def record(self, **event: object) -> None:
        self.events.append(dict(event))


def test_critic_fallback_is_a_first_class_event_with_closed_reasons() -> None:
    """@bug BUG-048 item 3: execution and candidate failures each emit once."""

    from deerflow_deep_research.domain.run_observation import RunEventCategory

    # Execution failure -> execution_failed.
    deps, _caps, _store = _deps(raises=True)
    recorder = _RecordingEventRecorder()
    deps = replace(deps, event_recorder=recorder)
    result = asyncio.run(build_real(deps)(_state()))
    assert [e.get("failure_category") for e in recorder.events if e.get("failure_category")] == [
        "readiness_critic_fallback.execution_failed"
    ]
    assert recorder.events[-1]["readiness_route"] == "pass"
    assert recorder.events[-1]["readiness_blocked_count"] == 0
    assert recorder.events[-1]["readiness_pass_guard"] == "fallback_projection"
    assert recorder.events[-1]["readiness_failure_codes"] == ()
    assert all(e["category"] is RunEventCategory.NODE for e in recorder.events)
    assert result["route"] == "pass"

    # Inadmissible candidate -> candidate_invalid.
    deps2, _caps2, _store2 = _deps(response="not-json")
    recorder2 = _RecordingEventRecorder()
    deps2 = replace(deps2, event_recorder=recorder2)
    asyncio.run(build_real(deps2)(_state()))
    assert [e.get("failure_category") for e in recorder2.events if e.get("failure_category")] == [
        "readiness_critic_fallback.candidate_invalid"
    ]
    assert recorder2.events[-1]["readiness_pass_guard"] == "fallback_projection"

    # Admitted candidate -> only the minimal decision fact.
    deps3, _caps3, _store3 = _deps(response=_candidate(("Q1",), LEDGER_HASH))
    recorder3 = _RecordingEventRecorder()
    deps3 = replace(deps3, event_recorder=recorder3)
    asyncio.run(build_real(deps3)(_state()))
    assert len(recorder3.events) == 1
    assert recorder3.events[0]["readiness_route"] == "pass"
    assert recorder3.events[0]["readiness_blocked_count"] == 0
    assert recorder3.events[0]["readiness_pass_guard"] is None

    # A failing recorder cannot change the projection.
    class FailingRecorder:
        async def record(self, **_event: object) -> None:
            raise RuntimeError("journal unavailable")

    deps4, _caps4, _store4 = _deps(raises=True)
    deps4 = replace(deps4, event_recorder=FailingRecorder())
    result4 = asyncio.run(build_real(deps4)(_state()))
    assert result4.get("route") is not None


def test_ready_substantive_conclusion_uses_backing_finding_statement() -> None:
    from deerflow_deep_research.domain.synthesis import Confidence, SynthesisFinding
    from deerflow_deep_research.graph.nodes.readiness.contracts import (
        PerQuestionVerdict,
        ReadinessCriticOutput,
    )
    from deerflow_deep_research.graph.nodes.readiness.materializer import materialize_report_plan

    finding = SynthesisFinding(
        finding_id="finding:f_1",
        statement="In 2024, China's cumulative installed capacity of power batteries was 548.4 GWh, up 41.5%.",
        confidence=Confidence.MEDIUM,
        priority=1,
        backing_refs=("h_A",),
        affected_topics=("China EV battery market 2024",),
    )
    critic = ReadinessCriticOutput(
        per_question=(
            PerQuestionVerdict(
                question="What is one bounded fact about China's EV battery market in 2024?",
                verdict="ready_substantive",
                backing_claim_ids=("h_A",),
                limitation_note="",
            ),
        )
    )

    plan = materialize_report_plan(critic, (), findings=(finding,), accepted_refs=("h_A",))

    assert len(plan.writable_conclusions) == 1
    assert plan.writable_conclusions[0].conclusion_text == finding.statement
    assert "Evidence supports" not in plan.writable_conclusions[0].conclusion_text


def test_ready_substantive_without_backing_finding_keeps_honest_template() -> None:
    from deerflow_deep_research.graph.nodes.readiness.contracts import (
        PerQuestionVerdict,
        ReadinessCriticOutput,
    )
    from deerflow_deep_research.graph.nodes.readiness.materializer import materialize_report_plan

    critic = ReadinessCriticOutput(
        per_question=(
            PerQuestionVerdict(
                question="Q1",
                verdict="ready_substantive",
                backing_claim_ids=(),
                limitation_note="",
            ),
        )
    )
    plan = materialize_report_plan(critic, ())
    assert plan.writable_conclusions[0].conclusion_text == "Evidence supports a substantive answer for: Q1"
