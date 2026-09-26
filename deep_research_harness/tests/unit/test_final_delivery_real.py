"""Tests for bounded real final-delivery composition and publication handoff.

@impl FID-001
@impl FID-002
@impl FID-003
@impl FID-004
@impl FID-005
@impl EVH-022
@impl WFO-001
@impl WFO-002
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
from datetime import UTC, datetime

import pytest

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, run_bundle_root
from deerflow_deep_research.domain.context import GraphContextView, NodeAgentContext, NodeExecutionResult
from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.domain.failure_codes import FailureCode
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.state import BundleLocalState, ContentRef
from deerflow_deep_research.domain.synthesis import SynthesisEvidence
from deerflow_deep_research.domain.work_units import canonical_json_bytes
from deerflow_deep_research.engine.gate_kernel import evaluate_gate, gate_result_to_state_update
from deerflow_deep_research.engine.real_gates import build_final_delivery_real_gate_def
from deerflow_deep_research.graph.nodes.final_delivery.composer import (
    MAX_FINAL_DELIVERY_EVIDENCE_BYTES,
    admit_layout_candidate,
    build_final_delivery_request,
    parse_layout_candidate,
    plan_order_layout,
    render_final_artifacts,
)
from deerflow_deep_research.graph.nodes.final_delivery.contracts import (
    FINAL_DELIVERY_GATE_VIEW_KEY,
    FinalDeliveryGateView,
)
from deerflow_deep_research.graph.nodes.final_delivery.node import (
    _LAYOUT_LITERAL_CODES,
    _canonical_layout_code,
    _validate_final_artifacts,
    build_real,
)
from deerflow_deep_research.graph.nodes.readiness.contracts import ReadinessReportPlan
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore

BUNDLE = RunBundleRef(
    bundle_id=BundleId("b_" + "A" * 43),
    scope_bucket="s_" + "B" * 43,
)
_RID = BUNDLE.bundle_id.value
_BUNDLE_ROOT = run_bundle_root(BUNDLE)
_LEDGER_HASH = "h_" + "B" * 43


def _ref(path: str, content: bytes, summary: str = "") -> ContentRef:
    digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).decode("ascii").rstrip("=")
    return ContentRef(sandbox_path=path, content_hash=f"h_{digest}", short_summary=summary)


def _plan() -> ReadinessReportPlan:
    return ReadinessReportPlan.model_validate(
        {
            "writable_conclusions": [
                {
                    "question": "What is established?",
                    "conclusion_text": "The approved conclusion is retained verbatim.",
                    "backing_claim_ids": [_LEDGER_HASH],
                }
            ],
            "mandatory_uncertainties": [
                {"question": "What remains uncertain?", "limitation": "The approved limitation is retained verbatim."}
            ],
        }
    )


class ScriptedFinalBundle:
    def __init__(
        self,
        *,
        plan: ReadinessReportPlan | None = None,
        evidence: tuple[SynthesisEvidence, ...] | None = None,
    ) -> None:
        self.plan = plan
        self.plan_ref = (
            _ref(
                f"{_BUNDLE_ROOT}/review/readiness-report-plan.json",
                canonical_json_bytes(plan.model_dump(mode="json")),
            )
            if plan is not None
            else None
        )
        self.evidence = (
            evidence
            if evidence is not None
            else (
                SynthesisEvidence(
                    submission_ref=_LEDGER_HASH,
                    phase="wave1",
                    result_contract="wave1.evidence-extraction",
                    content='{"claim":"approved evidence"}',
                ),
            )
        )
        self.plan_reads = 0
        self.evidence_reads = 0
        self.final_reads = 0
        self.final_artifacts: tuple[bytes, bytes] | None = None
        self.fail_final_read = False
        self.fail_publication = False

    async def read_readiness_report_plan(self, ref: ContentRef) -> bytes:
        self.plan_reads += 1
        if self.plan_ref is None or ref != self.plan_ref:
            raise ValueError("readiness_plan_hash_mismatch")
        return canonical_json_bytes(self.plan.model_dump(mode="json"))

    async def read_synthesis_evidence(self, accepted_refs: tuple[str, ...]) -> tuple[SynthesisEvidence, ...]:
        self.evidence_reads += 1
        if tuple(item.submission_ref for item in self.evidence) != accepted_refs:
            raise ValueError("accepted_evidence_mismatch")
        return self.evidence

    async def read_final_artifacts(self, refs: tuple[ContentRef, ContentRef]) -> tuple[bytes, bytes]:
        self.final_reads += 1
        if self.final_artifacts is None or self.fail_final_read:
            raise ValueError("final_artifact_readback_failed")
        report, citation_map = self.final_artifacts
        if refs != (
            _ref(f"{_BUNDLE_ROOT}/final/report.md", report, "report.md"),
            _ref(
                f"{_BUNDLE_ROOT}/final/claim-citation-map.json",
                citation_map,
                "claim-citation-map.json",
            ),
        ):
            raise ValueError("final_artifact_hash_mismatch")
        return self.final_artifacts


class ScriptedPublicationBundle:
    def __init__(self, reader: ScriptedFinalBundle) -> None:
        self.reader = reader
        self.calls: list[tuple[bytes, bytes]] = []

    async def publish_final(self, report: bytes, citation_map: bytes) -> tuple[ContentRef, ContentRef]:
        self.calls.append((report, citation_map))
        if self.reader.fail_publication:
            raise ValueError("final_artifact_write_conflict")
        self.reader.final_artifacts = (report, citation_map)
        return (
            _ref(f"{_BUNDLE_ROOT}/final/report.md", report, "report.md"),
            _ref(
                f"{_BUNDLE_ROOT}/final/claim-citation-map.json",
                citation_map,
                "claim-citation-map.json",
            ),
        )


class ScriptedCapabilities:
    def __init__(self, response: str | None = None, *, fails: bool = False) -> None:
        self.response = response or json.dumps(
            {"schema_version": 1, "conclusion_order": ["conclusion:0"], "uncertainty_order": ["uncertainty:0"]}
        )
        self.fails = fails
        self.requests = []

    async def run_agent(self, *, context, request) -> NodeExecutionResult:
        self.requests.append((context, request))
        if self.fails:
            raise RuntimeError("provider failure")
        return NodeExecutionResult(finish_reason=NodeFinishReason.SUCCESS, summary=self.response)


class SpyEventRecorder:
    """Duck-typed journal recorder capturing validation facts for assertion."""

    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    async def record(self, **kwargs: object) -> None:
        self.events.append(kwargs)


def _deps(
    *,
    bundle: ScriptedFinalBundle,
    capabilities: ScriptedCapabilities | None = None,
    event_recorder: SpyEventRecorder | None = None,
) -> NodeBuildDependencies:
    graph = GraphContextView(
        research_scope_id=_RID,
        workspace_root=f"/mnt/user-data/{_BUNDLE_ROOT}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root="/mnt/user-data/outputs/deep-research",
    )
    return NodeBuildDependencies(
        graph_context=graph,
        agent_context=NodeAgentContext(
            research_scope_id=graph.research_scope_id,
            node_name="final_delivery",
            attempt_id="g0-final_delivery-a1",
            workspace_root=graph.workspace_root,
            attempt_root=f"{graph.workspace_root}/final",
            policy_name="final-delivery-composer",
        ),
        capabilities=capabilities or ScriptedCapabilities(),
        publication_bundle=ScriptedPublicationBundle(bundle),
        final_delivery_bundle=bundle,
        event_recorder=event_recorder,
    )


def _multi_conclusion_plan() -> ReadinessReportPlan:
    """Non-degenerate plan (2 conclusions + 1 uncertainty): the composer path applies."""

    return ReadinessReportPlan.model_validate(
        {
            "writable_conclusions": [
                {
                    "question": "What is established?",
                    "conclusion_text": "The approved conclusion is retained verbatim.",
                    "backing_claim_ids": [_LEDGER_HASH],
                },
                {
                    "question": "What else is established?",
                    "conclusion_text": "The second approved conclusion is retained verbatim.",
                    "backing_claim_ids": [_LEDGER_HASH],
                },
            ],
            "mandatory_uncertainties": [
                {"question": "What remains uncertain?", "limitation": "The approved limitation is retained verbatim."}
            ],
        }
    )


def _state(bundle: ScriptedFinalBundle, *, accepted_refs: tuple[str, ...] = (_LEDGER_HASH,)) -> dict[str, object]:
    return {
        "bundle_id": _RID,
        "generation": 0,
        "accepted_submission_refs": accepted_refs,
        "readiness_report_plan": bundle.plan_ref,
    }


class TestRealFinalDelivery:
    def test_composer_request_is_bounded_and_cannot_expose_tools_or_checkpoint_state(self) -> None:
        request = build_final_delivery_request(
            _plan(),
            (
                SynthesisEvidence(
                    submission_ref=_LEDGER_HASH,
                    phase="wave1",
                    result_contract="wave1.evidence-extraction",
                    content="x" * 20_000,
                ),
            ),
        )

        projection = request.objective.split("<untrusted-source-data>\n", 1)[1].split("\n</untrusted-source-data>", 1)[
            0
        ]
        parsed = json.loads(projection)
        assert parsed[0]["submission_ref"] == _LEDGER_HASH
        assert len(parsed[0]["content"].encode("utf-8")) <= MAX_FINAL_DELIVERY_EVIDENCE_BYTES
        assert request.tools_enabled is False
        assert request.capability_ref.capability_id == "final-delivery-composer"
        assert "readiness_report_plan" not in request.objective
        assert "/mnt/user-data" not in request.objective

    def test_layout_parse_normalizes_fenced_and_embedded_deliveries(self) -> None:
        """@bug BUG-055: delivery shape (fence/prose wrapping) must not cost the run."""

        plan = _multi_conclusion_plan()
        payload = {
            "schema_version": 1,
            "conclusion_order": ["conclusion:1", "conclusion:0"],
            "uncertainty_order": ["uncertainty:0"],
        }
        body = json.dumps(payload)
        fenced = f"```json\n{body}\n```"
        embedded = f"Here is the requested layout:\n{body}\nHope that helps."

        for delivery in (body, fenced, embedded):
            candidate = admit_layout_candidate(parse_layout_candidate(delivery), plan)
            assert candidate.conclusion_order == ("conclusion:1", "conclusion:0")
            assert candidate.uncertainty_order == ("uncertainty:0",)

    def test_layout_parse_still_rejects_inadmissible_content(self) -> None:
        """Normalization is delivery-shape only: content admission stays closed."""

        for delivery in ("", "   ", "not json at all", json.dumps([1, 2]), "null"):
            with pytest.raises(ValueError, match="final_layout_"):
                parse_layout_candidate(delivery)

    def test_real_gate_uses_only_the_current_attempt_view_and_owns_completion(self) -> None:
        report = b"# Deep Research Report\n"
        citation_map = b'{"schema_version":1,"claims":{}}'
        refs = (
            _ref(f"{_BUNDLE_ROOT}/final/report.md", report),
            _ref(f"{_BUNDLE_ROOT}/final/claim-citation-map.json", citation_map),
        )
        gate = build_final_delivery_real_gate_def()
        base_state = {"generation": 0, "gate_attempts_by_phase": {}, "repair_budget_by_phase": {}}

        passed = evaluate_gate(
            {
                **base_state,
                FINAL_DELIVERY_GATE_VIEW_KEY: FinalDeliveryGateView(
                    published_refs=refs,
                    accepted_evidence_present=True,
                ),
            },
            "final_delivery",
            gate,
        )
        assert passed.route == "pass"
        completion = gate_result_to_state_update(passed, "final_delivery", base_state)
        assert completion["terminal_status"] == "completed"

        stale = evaluate_gate({**base_state, "report_refs": refs}, "final_delivery", gate)
        assert stale.route == "repair"
        evidence_blocked = evaluate_gate(
            {
                **base_state,
                FINAL_DELIVERY_GATE_VIEW_KEY: FinalDeliveryGateView(
                    accepted_evidence_present=False,
                    failure_code=FailureCode.EVIDENCE_INSUFFICIENT,
                ),
            },
            "final_delivery",
            gate,
        )
        assert evidence_blocked.route == "evidence_blocked"
        exhausted = evaluate_gate(
            {
                **base_state,
                "repair_budget_by_phase": {"final_delivery": 0},
                FINAL_DELIVERY_GATE_VIEW_KEY: FinalDeliveryGateView(
                    accepted_evidence_present=True,
                    failure_code=FailureCode.WORK_FAILED,
                ),
            },
            "final_delivery",
            gate,
        )
        assert exhausted.route == "exhausted"

    @pytest.mark.asyncio
    async def test_renders_only_plan_text_and_keeps_completion_gate_owned(self) -> None:
        bundle = ScriptedFinalBundle(plan=_plan())
        dependencies = _deps(bundle=bundle)

        result = await build_real(dependencies)(_state(bundle))

        assert "terminal_status" not in result
        assert len(result["report_refs"]) == 2
        report, citation_map = dependencies.publication_bundle.calls[0]  # type: ignore[union-attr]
        assert b"The approved conclusion is retained verbatim." in report
        assert b"The approved limitation is retained verbatim." in report
        assert json.loads(citation_map) == {
            "schema_version": 1,
            "claims": {"conclusion:0": {"backing_refs": [_LEDGER_HASH]}},
        }
        view = result[FINAL_DELIVERY_GATE_VIEW_KEY]
        assert isinstance(view, FinalDeliveryGateView)
        assert view.published_refs == result["report_refs"]
        assert bundle.final_reads == 1

    @pytest.mark.asyncio
    async def test_degenerate_plan_renders_deterministically_without_the_composer(self) -> None:
        """@bug BUG-053: a 0+1 plan's unique layout needs no model echo."""

        plan = ReadinessReportPlan.model_validate(
            {
                "writable_conclusions": [],
                "mandatory_uncertainties": [
                    {
                        "question": "What remains uncertain?",
                        "limitation": "The approved limitation is retained verbatim.",
                    },
                ],
            }
        )
        bundle = ScriptedFinalBundle(plan=plan)
        capabilities = ScriptedCapabilities(fails=True)  # any model call would fail
        dependencies = _deps(bundle=bundle, capabilities=capabilities)

        result = await build_real(dependencies)(_state(bundle))

        assert "terminal_status" not in result
        assert capabilities.requests == []  # no composer invocation at all
        assert len(result["report_refs"]) == 2
        report, citation_map = dependencies.publication_bundle.calls[0]  # type: ignore[union-attr]
        assert b"The approved limitation is retained verbatim." in report
        assert json.loads(citation_map) == {"schema_version": 1, "claims": {}}
        assert result[FINAL_DELIVERY_GATE_VIEW_KEY].published_refs == result["report_refs"]

    @pytest.mark.asyncio
    async def test_missing_or_divergent_plan_calls_neither_composer_nor_publisher(self) -> None:
        bundle = ScriptedFinalBundle(plan=_plan())
        capabilities = ScriptedCapabilities()
        dependencies = _deps(bundle=bundle, capabilities=capabilities)
        state = _state(bundle)
        state["readiness_report_plan"] = None

        result = await build_real(dependencies)(state)

        assert capabilities.requests == []
        assert dependencies.publication_bundle.calls == []  # type: ignore[union-attr]
        assert result[FINAL_DELIVERY_GATE_VIEW_KEY].failure_code is FailureCode.WORK_FAILED

    @pytest.mark.asyncio
    async def test_empty_accepted_evidence_never_publishes(self) -> None:
        bundle = ScriptedFinalBundle(plan=_plan())
        capabilities = ScriptedCapabilities()
        dependencies = _deps(bundle=bundle, capabilities=capabilities)

        result = await build_real(dependencies)(_state(bundle, accepted_refs=()))

        assert capabilities.requests == []
        assert dependencies.publication_bundle.calls == []  # type: ignore[union-attr]
        assert result[FINAL_DELIVERY_GATE_VIEW_KEY].failure_code is FailureCode.EVIDENCE_INSUFFICIENT

    @pytest.mark.asyncio
    async def test_inadmissible_candidate_degrades_to_plan_order_and_publishes(self) -> None:
        """@bug BUG-055: an ordering miss must not cost the run its delivery."""

        recorder = SpyEventRecorder()
        bundle = ScriptedFinalBundle(plan=_multi_conclusion_plan())
        dependencies = _deps(
            bundle=bundle,
            capabilities=ScriptedCapabilities("not json at all"),
            event_recorder=recorder,
        )

        result = await build_real(dependencies)(_state(bundle))

        view = result[FINAL_DELIVERY_GATE_VIEW_KEY]
        assert isinstance(view, FinalDeliveryGateView)
        assert view.failure_code is None
        assert view.published_refs == result["report_refs"]
        report, _citation_map = dependencies.publication_bundle.calls[0]  # type: ignore[union-attr]
        first = report.find(b"The approved conclusion is retained verbatim.")
        second = report.find(b"The second approved conclusion is retained verbatim.")
        assert 0 < first < second  # plan order: conclusion:0 before conclusion:1
        validations = [event for event in recorder.events if event.get("category") is not None]
        assert len(validations) == 1
        assert validations[0]["validation_codes"] == ("final_layout_json_invalid",)
        assert validations[0]["validation_stage"] == "initial"
        assert "response_shape" not in validations[0] or validations[0]["response_shape"] is None

    @pytest.mark.asyncio
    async def test_duplicate_order_candidate_carries_the_closed_schema_code_and_degrades(self) -> None:
        """Typed-candidate validation failures carry the closed schema-invalid code."""

        recorder = SpyEventRecorder()
        duplicate = json.dumps(
            {
                "schema_version": 1,
                "conclusion_order": ["conclusion:0", "conclusion:0"],
                "uncertainty_order": ["uncertainty:0"],
            }
        )
        bundle = ScriptedFinalBundle(plan=_multi_conclusion_plan())
        dependencies = _deps(bundle=bundle, capabilities=ScriptedCapabilities(duplicate), event_recorder=recorder)

        result = await build_real(dependencies)(_state(bundle))

        assert result[FINAL_DELIVERY_GATE_VIEW_KEY].failure_code is None
        validations = [event for event in recorder.events if event.get("category") is not None]
        assert len(validations) == 1
        assert validations[0]["validation_codes"] == ("final_layout_schema_invalid",)
        assert len(dependencies.publication_bundle.calls) == 1  # type: ignore[union-attr]

    @pytest.mark.asyncio
    async def test_fenced_candidate_is_admitted_without_degradation(self) -> None:
        """A fenced delivery is normalized and the composer's order is kept."""

        recorder = SpyEventRecorder()
        fenced = (
            "```json\n"
            + json.dumps(
                {
                    "schema_version": 1,
                    "conclusion_order": ["conclusion:1", "conclusion:0"],
                    "uncertainty_order": ["uncertainty:0"],
                }
            )
            + "\n```"
        )
        bundle = ScriptedFinalBundle(plan=_multi_conclusion_plan())
        dependencies = _deps(bundle=bundle, capabilities=ScriptedCapabilities(fenced), event_recorder=recorder)

        result = await build_real(dependencies)(_state(bundle))

        assert result[FINAL_DELIVERY_GATE_VIEW_KEY].failure_code is None
        report, _citation_map = dependencies.publication_bundle.calls[0]  # type: ignore[union-attr]
        first = report.find(b"The approved conclusion is retained verbatim.")
        second = report.find(b"The second approved conclusion is retained verbatim.")
        assert 0 < second < first  # composer order: conclusion:1 before conclusion:0
        assert recorder.events == []

    @pytest.mark.asyncio
    async def test_composer_invocation_failure_degrades_without_a_validation_fact(self) -> None:
        """@bug BUG-055: invocation failure degrades too; only the invocation fact exists."""

        recorder = SpyEventRecorder()
        bundle = ScriptedFinalBundle(plan=_multi_conclusion_plan())
        failed_capabilities = ScriptedCapabilities(fails=True)
        dependencies = _deps(bundle=bundle, capabilities=failed_capabilities, event_recorder=recorder)

        result = await build_real(dependencies)(_state(bundle))

        assert len(failed_capabilities.requests) == 1
        view = result[FINAL_DELIVERY_GATE_VIEW_KEY]
        assert isinstance(view, FinalDeliveryGateView)
        assert view.failure_code is None
        assert len(dependencies.publication_bundle.calls) == 1  # type: ignore[union-attr]
        assert recorder.events == []  # no validation fact for a pre-boundary failure

    @pytest.mark.asyncio
    async def test_readback_failure_never_publishes_a_pass_view(self) -> None:
        complete_candidate = json.dumps(
            {
                "schema_version": 1,
                "conclusion_order": ["conclusion:0", "conclusion:1"],
                "uncertainty_order": ["uncertainty:0"],
            }
        )
        bundle = ScriptedFinalBundle(plan=_multi_conclusion_plan())
        bundle.fail_final_read = True
        dependencies = _deps(bundle=bundle, capabilities=ScriptedCapabilities(complete_candidate))

        result = await build_real(dependencies)(_state(bundle))

        assert result[FINAL_DELIVERY_GATE_VIEW_KEY].failure_code is FailureCode.WORK_FAILED
        assert len(dependencies.publication_bundle.calls) == 1  # type: ignore[union-attr]

    @pytest.mark.asyncio
    async def test_publisher_failure_takes_one_attempt_without_a_pass_view(self) -> None:
        publisher_bundle = ScriptedFinalBundle(plan=_plan())
        publisher_bundle.fail_publication = True
        publisher_dependencies = _deps(bundle=publisher_bundle)

        publisher_result = await build_real(publisher_dependencies)(_state(publisher_bundle))

        assert len(publisher_dependencies.publication_bundle.calls) == 1  # type: ignore[union-attr]
        assert publisher_result[FINAL_DELIVERY_GATE_VIEW_KEY].failure_code is FailureCode.WORK_FAILED

    def test_missing_declared_dependencies_fail_before_request_construction(self) -> None:
        bundle = ScriptedFinalBundle(plan=_plan())
        dependencies = _deps(bundle=bundle)
        with pytest.raises(ValueError, match="final_delivery_bundle_capability_missing"):
            build_real(
                dependencies.__class__(
                    graph_context=dependencies.graph_context,
                    agent_context=dependencies.agent_context,
                    capabilities=dependencies.capabilities,
                    publication_bundle=dependencies.publication_bundle,
                )
            )

    @pytest.mark.asyncio
    async def test_publication_replay_is_idempotent_and_conflicting_content_fails_closed(self, tmp_path) -> None:
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
        first = await store.publish_final(b"report\n", b'{"claims":{}}')
        assert await store.publish_final(b"report\n", b'{"claims":{}}') == first
        with pytest.raises(ValueError, match="final_artifact_write_conflict"):
            await store.publish_final(b"changed\n", b'{"claims":{}}')


class TestFullCardinalityAndClosedFeedback:
    """@impl FID-001

    The 2026-09-26 Gateway incident: a real plan (7 conclusions + 9 uncertainties)
    killed both the composer path and the deterministic plan-order fallback on the
    layout contract's legacy max_length=8, and the terminal block left no journal
    fact. These tests lock the corrected contracts.
    """

    def test_full_cardinality_plan_constructs_renders_and_validates_end_to_end(self) -> None:
        plan = ReadinessReportPlan.model_validate(
            {
                "writable_conclusions": [
                    {
                        "question": f"Established fact {index}?",
                        "conclusion_text": f"Approved conclusion {index} is retained verbatim.",
                        "backing_claim_ids": [_LEDGER_HASH],
                    }
                    for index in range(7)
                ],
                "mandatory_uncertainties": [
                    {"question": f"Open question {index}?", "limitation": f"Bounded limitation {index}."}
                    for index in range(9)
                ],
            }
        )
        layout = plan_order_layout(plan)
        assert len(layout.conclusion_order) == 7
        assert len(layout.uncertainty_order) == 9
        report, citation_map = render_final_artifacts(plan, layout)
        _validate_final_artifacts(report, citation_map)
        text = report.decode("utf-8")
        assert text.startswith("# Deep Research Report\n")
        assert text.count("### Open question") == 9

    def test_schema_invalid_object_delivery_keeps_a_concrete_closed_category(self) -> None:
        delivery = json.dumps({"schema_version": 1, "conclusion_order": "not-a-tuple", "uncertainty_order": []})
        with pytest.raises(ValueError) as excinfo:
            parse_layout_candidate(delivery)
        assert str(excinfo.value) == "final_layout_schema_invalid"
        detail = getattr(excinfo.value, "detail", None)
        errors = detail.get("schema_errors") if isinstance(detail, dict) else None
        assert isinstance(errors, list) and 0 < len(errors) <= 3
        assert errors[0]["loc"] == "conclusion_order"
        assert _canonical_layout_code(excinfo.value) == "final_layout_schema_invalid"

    @pytest.mark.asyncio
    async def test_readback_failure_records_one_closed_code_fact_before_work_failure(self) -> None:
        bundle = ScriptedFinalBundle(plan=_multi_conclusion_plan())
        bundle.fail_final_read = True
        recorder = SpyEventRecorder()
        dependencies = _deps(bundle=bundle, event_recorder=recorder)
        result = await build_real(dependencies)(_state(bundle))
        view = result[FINAL_DELIVERY_GATE_VIEW_KEY]
        assert view.failure_code is FailureCode.WORK_FAILED
        codes = [event.get("validation_codes") for event in recorder.events if event.get("category") == "validation"]
        assert codes and all(all(code for code in entry) for entry in codes)
        flat = {code for entry in codes for code in entry}
        assert flat <= {"final_layout_schema_invalid", "final_delivery_readback_failed"} | set(_LAYOUT_LITERAL_CODES)
        assert "final_delivery_readback_failed" in flat, "read-back failure must leave its own closed-code fact"
