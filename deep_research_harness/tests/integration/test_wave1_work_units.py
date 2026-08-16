"""Wave1 work-unit planning, validation, gate, and open-question integration.

@impl WON-001
@impl WON-003
@impl WON-004
@impl WON-006
@impl WON-007
@impl WON-009
@impl EVH-015
"""

from __future__ import annotations

import json
import re
import shutil
import time
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from deerflow_deep_research_fixtures.gates import build_fixture_gate_definitions
from deerflow_deep_research_fixtures.graph.nodes.wave1 import adapter as fixture_wave1_adapter
from deerflow_deep_research_fixtures.scenario import FixtureScenario
from deerflow_deep_research_fixtures.work_units import run_fixture_work_unit_component

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, bundle_host_relative_root
from deerflow_deep_research.domain.context import (
    GraphContextView,
    NodeAgentBundleContext,
    NodeAgentContext,
    NodeExecutionResult,
    SelectedBundleContext,
)
from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.domain.invocation import GraphInvocationContext, WorkUnitControllerDependencies
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies, NodeCapability
from deerflow_deep_research.domain.run_experience import (
    FailureCertainty,
    NodeProblem,
    ProviderObservation,
    RunFailureCode,
)
from deerflow_deep_research.domain.run_observation import FinalResponseShape, RunEventCategory
from deerflow_deep_research.domain.state import (
    WORK_UNIT_GATE_PREVIEW_FIELDS,
    BundleLocalState,
    merge_trace,
    preview_work_unit_update,
)
from deerflow_deep_research.domain.wave1 import OpenQuestionState
from deerflow_deep_research.domain.work_units import (
    WORK_UNIT_GATE_VIEW_KEY,
    SubmissionValidationCode,
    WorkUnitGateView,
)
from deerflow_deep_research.engine.gate_kernel import evaluate_gate
from deerflow_deep_research.graph.builder import _node_wrapper
from deerflow_deep_research.graph.components import work_units as work_unit_component
from deerflow_deep_research.graph.implementation_map import AdapterKind, NodeAdapter
from deerflow_deep_research.graph.nodes.gate_adapter import real_wave1_gate_def
from deerflow_deep_research.graph.nodes.wave1 import NODE_SPEC
from deerflow_deep_research.graph.nodes.wave1 import node as wave1_node
from deerflow_deep_research.graph.nodes.wave1 import subgraph as wave1_subgraph
from deerflow_deep_research.graph.nodes.wave1.review import (
    WAVE1_GATE_REVIEW_KEY,
    Wave1GateReview,
    build_wave1_gate_review,
)
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.projection import RuntimeWorkUnitDependencyResolver
from deerflow_deep_research.runtime.run_observation import RunObservationRecorder, RunObservationStore
from deerflow_deep_research.runtime.work_unit_storage import WorkUnitStoreError
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore
from tests.assets.provider_shapes import load_provider_shape_cases, thaw_provider_shape_payload
from tests.fixtures.live_seeds import build_live_seed_bundle

BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "B" * 43), scope_bucket="s_" + "B" * 43)
BUNDLE_ID = BUNDLE.bundle_id.value
NOW = datetime(2026, 7, 14, tzinfo=UTC)
SHAPE_CASES = {
    case.case_id: case
    for case in load_provider_shape_cases(Path(__file__).parents[1] / "fixtures/provider_shapes/wave1.json")
}


def test_wave1_receives_a_selected_bundle_context_without_legacy_identity_or_checkpoint() -> None:
    """WON-009: workers receive runtime-bound Bundle context only."""
    from deerflow_deep_research.domain.context import SelectedBundleContext

    bundle = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)
    context = SelectedBundleContext(bundle=bundle)
    assert context.bundle == bundle
    assert set(SelectedBundleContext.model_fields) == {"bundle"}


class ForbiddenCapabilities:
    async def run_agent(self, *, context, request):
        raise AssertionError("fixture work must not call an agent")


class ScriptedWave1Capabilities:
    def __init__(
        self,
        *,
        malformed: bool = False,
        malformed_once: bool = False,
        reverse_sources: bool = False,
        malformed_tool_results: tuple[str, ...] = (),
        provider_payload: dict | None = None,
        invocation_result: NodeExecutionResult | None = None,
        invocation_results: tuple[NodeExecutionResult, ...] = (),
        source_diagnostic_failure: bool = False,
        source_diagnostic_foreign: bool = False,
        claim_verifier_failure: bool = False,
    ) -> None:
        self.contexts: list[NodeAgentContext] = []
        self.requests: list[object] = []
        self.malformed = malformed
        self.malformed_once = malformed_once
        self.reverse_sources = reverse_sources
        self.malformed_tool_results = malformed_tool_results
        self.provider_payload = provider_payload
        self.invocation_result = invocation_result
        self.invocation_results = list(invocation_results)
        self.source_diagnostic_failure = source_diagnostic_failure
        self.source_diagnostic_foreign = source_diagnostic_foreign
        self.claim_verifier_failure = claim_verifier_failure

    async def run_agent(self, *, context, request):
        if not isinstance(context, NodeAgentContext):
            raise TypeError("node_agent_context_required")
        self.contexts.append(context)
        self.requests.append(request)
        capability_id = request.capability_ref.capability_id if request.capability_ref is not None else None
        if capability_id == "wave1-source-diagnostic":
            if self.source_diagnostic_failure:
                return NodeExecutionResult(finish_reason=NodeFinishReason.SUCCESS, summary="not-json")
            source_ids = tuple(re.findall(r'"source_id":"([^"]+)"', request.objective))
            if self.source_diagnostic_foreign:
                source_ids = ("source:foreign",)
            return NodeExecutionResult(
                finish_reason=NodeFinishReason.SUCCESS,
                summary=json.dumps(
                    {
                        "schema_version": 1,
                        "source_ids": source_ids,
                        "sources": [
                            {
                                "source_id": source_id,
                                "trust_tier": "medium",
                                "materiality": "primary",
                                "marketing_risk": False,
                                "cross_verification_need": True,
                            }
                            for source_id in source_ids
                        ],
                    }
                ),
            )
        if capability_id == "wave1-claim-verifier":
            if self.claim_verifier_failure:
                return NodeExecutionResult(finish_reason=NodeFinishReason.SUCCESS, summary="not-json")
            claim_ids = tuple(re.findall(r'"claim_id":"([^"]+)"', request.objective))
            assigned = re.search(r'"assigned_new_source_ids":\[([^]]*)\]', request.objective)
            source_ids = tuple(re.findall(r'"([^"]+)"', assigned.group(1))) if assigned is not None else ()
            return NodeExecutionResult(
                finish_reason=NodeFinishReason.SUCCESS,
                summary=json.dumps(
                    {
                        "schema_version": 1,
                        "claims": [
                            {
                                "claim_id": claim_id,
                                "verdict": "supported",
                                "support_refs": source_ids,
                                "counter_refs": [],
                                "reason": "Scripted bounded critic result.",
                            }
                            for claim_id in claim_ids
                        ],
                    }
                ),
            )
        if self.invocation_results:
            return self.invocation_results.pop(0)
        if self.invocation_result is not None:
            return self.invocation_result
        if self.provider_payload is not None:
            return NodeExecutionResult(
                finish_reason=NodeFinishReason.SUCCESS,
                summary=json.dumps(self.provider_payload),
            )
        if self.malformed or (self.malformed_once and len(self.contexts) == 1):
            return NodeExecutionResult(
                finish_reason=NodeFinishReason.SUCCESS,
                summary="not-json",
                untrusted_tool_results=self.malformed_tool_results,
            )
        source_id = f"source:{context.attempt_id[-3:]}"
        additional_source_id = f"source:{context.attempt_id[-3:]}-second"
        sources = [
            {
                "source_id": source_id,
                "canonical_url": f"https://example.com/{context.attempt_id}",
                "title": "Scripted evidence",
            },
            {
                "source_id": additional_source_id,
                "canonical_url": f"https://example.com/{context.attempt_id}/second",
                "title": "Scripted additional evidence",
            },
        ]
        support_refs = [source_id, additional_source_id]
        if self.reverse_sources:
            sources = [
                {
                    "source_id": "source:z",
                    "canonical_url": "https://example.com/z",
                    "title": "Z source",
                },
                {
                    "source_id": "source:a",
                    "canonical_url": "https://example.com/a",
                    "title": "A source",
                },
            ]
            support_refs = ["source:z", "source:a"]
        return NodeExecutionResult(
            finish_reason=NodeFinishReason.SUCCESS,
            summary=json.dumps(
                {
                    "schema_version": 1,
                    "sources": sources,
                    "claims": [
                        {
                            "claim_id": f"claim:w1_{context.attempt_id[-3:]}",
                            "statement": "The scripted source supports this claim.",
                            "support_refs": support_refs,
                            "counter_refs": [],
                        }
                    ],
                    "open_questions": [],
                }
            ),
        )


class _ObservationProjection:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    def emit(self, fields: dict[str, object], **_kwargs: object) -> None:
        self.events.append(dict(fields))

    async def aemit(self, fields: dict[str, object], **_kwargs: object) -> None:
        self.emit(fields, **_kwargs)


class BaseResolver:
    def __init__(self, graph_context: GraphContextView, capabilities=None, *, bundle: RunBundleRef = BUNDLE) -> None:
        self._graph_context = graph_context
        self._capabilities = capabilities or ForbiddenCapabilities()
        self._selected_bundle = SelectedBundleContext(bundle=bundle)

    def resolve(self, *, logical_name, attempt_id, policy):
        return NodeBuildDependencies(
            graph_context=self._graph_context,
            agent_context=NodeAgentContext(
                research_scope_id=BUNDLE_ID,
                node_name=logical_name,
                attempt_id=attempt_id,
                workspace_root=self._graph_context.workspace_root,
                attempt_root=f"{self._graph_context.workspace_root}/attempts/{attempt_id}",
                policy_name=policy.name,
                bundle_context=NodeAgentBundleContext.from_selected_bundle(self._selected_bundle),
            ),
            capabilities=self._capabilities,
            selected_bundle=self._selected_bundle,
        )


def _publish_bundle(workspace: Path, bundle: RunBundleRef = BUNDLE) -> None:
    BundleLifecycle(workspace_host_path=workspace)._publish_sync(
        bundle, BundleLocalState(bundle_id=bundle.bundle_id, implementation_mode="all_real")
    )


def _store(
    workspace: Path,
    *,
    token: str,
    bundle: RunBundleRef = BUNDLE,
    fault_hook=None,
) -> WorkUnitStore:
    _publish_bundle(workspace, bundle)
    return WorkUnitStore(
        workspace_host_path=workspace,
        bundle=bundle,
        clock=lambda: NOW,
        monotonic=time.monotonic,
        lock_sleep=time.sleep,
        token_factory=lambda: token,
        fault_hook=fault_hook,
    )


def _context(tmp_path) -> tuple[GraphInvocationContext, WorkUnitStore]:
    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    base = BaseResolver(graph_context)
    store = _store(tmp_path, token="1" * 32)
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=RuntimeWorkUnitDependencyResolver(graph_context, base, store),
    )
    return GraphInvocationContext(graph_context, base, controller), store


def _state() -> dict:
    return {
        "bundle_id": BUNDLE_ID,
        "generation": 0,
        "execution_trace": (),
        "gate_attempts_by_phase": {},
        "repair_budget_by_phase": {},
        "pending_work_ids": (),
        "batch_cursor": 0,
        "next_work_ordinal": 0,
        "next_attempt_ordinal_by_work_id": {},
        "work_specs_by_id": {},
        "attempts_by_id": {},
        "work_status_by_id": {},
        "active_attempt_by_work_id": {},
        "terminal_failures_by_attempt_id": {},
        "accepted_submission_refs": (),
    }


def _apply_result(state: dict, result: dict) -> dict:
    next_state = dict(state)
    preview_delta = {key: value for key, value in result.items() if key in WORK_UNIT_GATE_PREVIEW_FIELDS}
    next_state.update(preview_work_unit_update(state, preview_delta))
    for key, value in result.items():
        if key in WORK_UNIT_GATE_PREVIEW_FIELDS:
            continue
        next_state[key] = merge_trace(state.get(key, ()), value) if key == "execution_trace" else value
    return next_state


async def _run_real_wave1_until_review(tmp_path, capabilities: ScriptedWave1Capabilities):
    seed = await build_live_seed_bundle(tmp_path, bundle=BUNDLE, include_wave1=False, now=NOW)
    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    controller = WorkUnitControllerDependencies(
        store=seed.store,
        resolver=RuntimeWorkUnitDependencyResolver(
            graph_context,
            BaseResolver(graph_context, capabilities),
            seed.store,
        ),
    )
    state = _state() | {
        "topic_registry": seed.checkpoint["topic_registry"],
        "accepted_submission_refs": seed.checkpoint["accepted_submission_refs"],
    }
    result = await wave1_subgraph.run_wave1_work_units_real(
        state,
        controller=controller,
        topic_registry=state["topic_registry"],
        capabilities=capabilities,
        wave0_urls=frozenset({"https://example.invalid/wave0"}),
        clock=lambda: NOW,
    )
    review = await build_wave1_gate_review(
        controller,
        gate_view=result.gate_view,
        policy=wave1_subgraph.WAVE1_REAL_POLICY,
    )
    return controller, result, review


async def test_wave1_reuses_shared_kernel_with_distinct_fixture_scope_and_content(tmp_path) -> None:
    assert NODE_SPEC.capabilities == frozenset({NodeCapability.WORK_UNIT_CONTROLLER})
    assert fixture_wave1_adapter.run_fixture_work_unit_component is run_fixture_work_unit_component
    assert not {
        "StateGraph",
        "WorkUnitStore",
        "validate_submission_candidate",
        "commit_candidate",
    } & set(vars(fixture_wave1_adapter))
    assert tuple(intent.scope for intent in fixture_wave1_adapter._INTENTS) == (
        ("wave1:fixture:0",),
        ("wave1:fixture:1",),
        ("wave1:fixture:2",),
    )

    context, store = _context(tmp_path)
    gate = build_fixture_gate_definitions(FixtureScenario(wave1=("repair", "pass")))["wave1"]
    wrapped = _node_wrapper(
        "wave1",
        NODE_SPEC,
        NodeAdapter(factory=fixture_wave1_adapter.build_fixture, kind=AdapterKind.FIXTURE, requires_gate=True),
        {"wave1": gate},
    )
    first = await wrapped(_state(), SimpleNamespace(context=context))
    assert first["route"] == "repair"
    assert tuple(first["work_specs_by_id"]) == (
        "g0_wave1_w0000",
        "g0_wave1_w0001",
        "g0_wave1_w0002",
    )
    records = await store.load_records()
    assert len(records) == 3
    output_bytes = await store.read_canonical_bytes(records[0].output_refs[0].path, max_bytes=1024)
    assert b'"phase":"wave1"' in output_bytes
    assert b"wave0" not in output_bytes

    second = await wrapped(_apply_result(_state(), first), SimpleNamespace(context=context))
    assert second["route"] == "pass"
    assert tuple(second["work_specs_by_id"]) == (
        "g0_wave1_w0003",
        "g0_wave1_w0004",
        "g0_wave1_w0005",
    )
    assert len(await store.load_records()) == 6


async def test_real_wave1_crosses_worker_context_artifact_validator_and_ledger(tmp_path) -> None:
    """@impl WON-007
    @impl EVH-015
    @impl WON-010
    """
    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    capabilities = ScriptedWave1Capabilities(
        malformed_once=True,
        malformed_tool_results=("wave1 retained observation",),
    )
    store = _store(tmp_path, token="2" * 32)
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=RuntimeWorkUnitDependencyResolver(
            graph_context,
            BaseResolver(graph_context, capabilities),
            store,
        ),
    )
    state = _state() | {
        "topic_registry": (
            {
                "topic_id": "storage",
                "title": "Storage",
                "scope": "Storage economics",
                "must_answer_bindings": ("Q1",),
            },
        )
    }

    result = await wave1_subgraph.run_wave1_work_units_real(
        state,
        controller=controller,
        topic_registry=state["topic_registry"],
        capabilities=capabilities,
        wave0_urls=frozenset(),
        clock=lambda: NOW,
    )

    assert len(capabilities.contexts) == 2
    request = capabilities.requests[0]
    assert request.minimum_tool_calls == 1
    assert request.tool_call_limit == 1
    assert request.capability_ref is not None
    assert request.capability_ref.capability_id == "wave1-evidence-extraction"
    assert "activated evidence-extraction capability" in request.objective
    assert "exactly one web search" not in request.objective
    assert "content_ref" not in request.expected_output
    assert "content_hash" not in request.expected_output
    assert "byte_count" not in request.expected_output
    assert "is_new_vs_wave0" not in request.expected_output
    assert capabilities.requests[1].tools_enabled is False
    assert capabilities.requests[1].capability_ref is not None
    assert capabilities.requests[1].capability_ref.capability_id == "wave1-evidence-extraction-repair"
    assert "activated zero-tool repair capability" in capabilities.requests[1].objective
    assert "Do not retrieve" not in capabilities.requests[1].objective
    assert "Trusted assignment (scope and baseline newness only)" in capabilities.requests[1].objective
    assert '"title":"Storage"' in capabilities.requests[1].objective
    assert "Trusted validation category: initial_structured_output_invalid" in capabilities.requests[1].objective
    assert "model_draft:\nnot-json" in capabilities.requests[1].objective
    assert "tool_result_1:\nwave1 retained observation" in capabilities.requests[1].objective
    assert "wave1_worker_output_json_invalid" not in capabilities.requests[1].objective
    for forbidden in (
        "raw-work-id-sentinel",
        "raw-checkpoint-sentinel",
        "raw-ledger-sentinel",
        "raw-review-sentinel",
        "raw-gate-sentinel",
        "raw-route-sentinel",
    ):
        assert forbidden not in capabilities.requests[1].objective
    assert "/work/g0_wave1_w0000/g0_wave1_w0000_a00" in capabilities.contexts[0].attempt_root
    records = await store.load_records()
    assert len(records) == 1
    assert result.parent_update["accepted_submission_refs"] == (records[0].record_hash,)
    assert records[0].source_refs[0].content_ref.endswith("/cache/source-0.json")
    assert "forged" not in records[0].source_refs[0].content_ref
    persisted = await store.read_canonical_bytes(records[0].result_ref, max_bytes=256 * 1024)
    assert json.loads(persisted)["claims"][0]["support_refs"] == [source.source_id for source in records[0].source_refs]


async def test_wave1_bundle_loss_before_ledger_publication_leaves_no_replacement_bundle(tmp_path) -> None:
    """WON-009: a candidate cannot publish through an unlinked Bundle descriptor."""

    def remove_bundle(point: str, _evidence_fd: int) -> None:
        if point == "before_staging_write":
            shutil.rmtree(tmp_path / bundle_host_relative_root(BUNDLE))

    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    capabilities = ScriptedWave1Capabilities()
    store = _store(tmp_path, token="d" * 32, fault_hook=remove_bundle)
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=RuntimeWorkUnitDependencyResolver(graph_context, BaseResolver(graph_context, capabilities), store),
    )
    topics = ({"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},)

    with pytest.raises(WorkUnitStoreError):
        await wave1_subgraph.run_wave1_work_units_real(
            _state() | {"topic_registry": topics},
            controller=controller,
            topic_registry=topics,
            capabilities=capabilities,
            wave0_urls=frozenset(),
            clock=lambda: NOW,
        )

    assert len(capabilities.requests) == 1
    assert not (tmp_path / bundle_host_relative_root(BUNDLE)).exists()


async def test_real_wave1_baseline_duplicate_is_not_admitted_as_new_coverage(tmp_path) -> None:
    """@impl WON-007
    @impl EVH-015
    """
    duplicate_url = "https://example.invalid/wave0"
    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    capabilities = ScriptedWave1Capabilities(
        provider_payload={
            "schema_version": 1,
            "sources": [
                {"source_id": "source:baseline", "canonical_url": duplicate_url, "title": "Baseline"},
                {"source_id": "source:new-one", "canonical_url": "https://example.com/new-one", "title": "New one"},
                {"source_id": "source:new-two", "canonical_url": "https://example.com/new-two", "title": "New two"},
            ],
            "claims": [
                {
                    "claim_id": "claim:w1_baseline",
                    "statement": "New sources provide bounded coverage.",
                    "support_refs": ["source:new-one", "source:new-two"],
                    "counter_refs": [],
                }
            ],
            "open_questions": [],
        }
    )
    seed = await build_live_seed_bundle(tmp_path, bundle=BUNDLE, include_wave1=False, now=NOW)
    store = seed.store
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=RuntimeWorkUnitDependencyResolver(graph_context, BaseResolver(graph_context, capabilities), store),
    )
    topics = ({"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},)

    result = await wave1_subgraph.run_wave1_work_units_real(
        _state() | {"topic_registry": topics, "accepted_submission_refs": seed.checkpoint["accepted_submission_refs"]},
        controller=controller,
        topic_registry=topics,
        capabilities=capabilities,
        wave0_urls=frozenset({duplicate_url}),
        clock=lambda: NOW,
    )

    records = await store.load_records()
    wave1_record = next(record for record in records if record.phase.value == "wave1")
    persisted = await store.read_canonical_bytes(wave1_record.result_ref, max_bytes=256 * 1024)
    assert [source["is_new_vs_wave0"] for source in json.loads(persisted)["sources"]] == [False, True, True]
    assert wave1_record.record_hash in result.parent_update["accepted_submission_refs"]


async def test_real_wave1_post_candidate_submission_validation_does_not_enter_repair(monkeypatch, tmp_path) -> None:
    """@impl WON-008
    @impl WON-012
    @impl WOU-012

    A later typed submission rejection stays with the shared controller even when
    the initial candidate already passed Wave1's local semantic boundary.
    """

    capabilities = ScriptedWave1Capabilities()
    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    store = _store(tmp_path, token="A" * 32)
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=RuntimeWorkUnitDependencyResolver(graph_context, BaseResolver(graph_context, capabilities), store),
    )

    async def reject_after_candidate(*_args, **_kwargs):
        raise work_unit_component.SubmissionValidationFailure((SubmissionValidationCode.CONTENT_HASH_MISMATCH,))

    monkeypatch.setattr(work_unit_component, "submit_candidate_if_active", reject_after_candidate)
    topics = ({"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},)
    journal_store = RunObservationStore(
        bundle_root=BundleLifecycle(workspace_host_path=tmp_path).private_root(BUNDLE),
        bundle_id=BUNDLE_ID,
    )
    recorder = RunObservationRecorder(store=journal_store, bundle_id=BUNDLE_ID)
    await recorder.establish(generation=0, phase="wave1", durability="restart_durable")
    result = await wave1_subgraph.run_wave1_work_units_real(
        _state() | {"topic_registry": topics},
        controller=controller,
        topic_registry=topics,
        capabilities=capabilities,
        wave0_urls=frozenset(),
        clock=lambda: NOW,
        event_recorder=recorder,
    )
    journal = await journal_store.inspect(bundle_id=BUNDLE_ID)

    attempt = next(iter(result.parent_update["attempts_by_id"].values()))
    assert len(capabilities.requests) == 1
    assert capabilities.requests[0].capability_ref is not None
    assert capabilities.requests[0].capability_ref.capability_id == "wave1-evidence-extraction"
    assert attempt["terminal_code"] == "validation_failed"
    assert attempt["failure_category"] == "submission_validation"
    assert "validation_codes" not in attempt
    assert "content_hash_mismatch" not in capabilities.requests[0].objective
    assert result.parent_update["accepted_submission_refs"] == ()
    assert await store.load_records() == ()
    validation_events = tuple(event for event in journal.events if event.category is RunEventCategory.VALIDATION)
    assert [(event.validation_stage, event.response_shape, event.validation_codes) for event in validation_events] == [
        ("initial", FinalResponseShape.JSON_OBJECT, ()),
        ("post_candidate", None, ("content_hash_mismatch",)),
    ]


async def test_real_wave1_factory_derives_the_authoritative_wave0_baseline_before_dispatch(
    tmp_path, monkeypatch
) -> None:
    """@impl WON-001"""

    seed = await build_live_seed_bundle(tmp_path, bundle=BUNDLE, include_wave1=False, now=NOW)
    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    capabilities = ScriptedWave1Capabilities()
    controller = WorkUnitControllerDependencies(
        store=seed.store,
        resolver=RuntimeWorkUnitDependencyResolver(
            graph_context,
            BaseResolver(graph_context, capabilities, bundle=seed.bundle),
            seed.store,
        ),
    )
    dependencies = replace(
        BaseResolver(graph_context, capabilities, bundle=seed.bundle).resolve(
            logical_name="wave1",
            attempt_id="factory-baseline",
            policy=wave1_subgraph.WAVE1_REAL_POLICY,
        ),
        work_units=controller,
    )
    state = _state() | {
        "topic_registry": seed.checkpoint["topic_registry"],
        "accepted_submission_refs": seed.checkpoint["accepted_submission_refs"],
    }

    observed: dict[str, object] = {}

    async def capture_worker(_state, **kwargs):
        observed["state"] = _state
        observed.update(kwargs)
        return SimpleNamespace(parent_update={}, gate_view=None)

    async def capture_review(*_args, **_kwargs):
        return Wave1GateReview(rows=())

    monkeypatch.setattr(wave1_node, "run_wave1_work_units_real", capture_worker)
    monkeypatch.setattr(wave1_node, "build_wave1_gate_review", capture_review)

    update = await NODE_SPEC.real_factory(dependencies)(state)

    assert observed["wave0_urls"] == frozenset({"https://example.invalid/wave0"})
    assert observed["controller"] is controller
    assert update["__work_unit_gate_view__"] is None
    assert update[WAVE1_GATE_REVIEW_KEY] == Wave1GateReview(rows=())


async def test_real_wave1_factory_fails_before_dispatch_when_checkpoint_record_is_unavailable(tmp_path) -> None:
    """@impl WON-001"""

    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    capabilities = ScriptedWave1Capabilities()
    store = _store(tmp_path, token="8" * 32)
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=RuntimeWorkUnitDependencyResolver(graph_context, BaseResolver(graph_context, capabilities), store),
    )
    dependencies = replace(
        BaseResolver(graph_context, capabilities).resolve(
            logical_name="wave1",
            attempt_id="missing-baseline",
            policy=wave1_subgraph.WAVE1_REAL_POLICY,
        ),
        work_units=controller,
    )

    with pytest.raises(ValueError, match="wave1_baseline_record_missing"):
        await NODE_SPEC.real_factory(dependencies)(
            _state()
            | {
                "topic_registry": ({"topic_id": "storage", "title": "Storage", "scope": "Storage"},),
                "accepted_submission_refs": ("h_" + "M" * 43,),
            }
        )

    assert capabilities.requests == []


async def test_wave1_post_acceptance_critics_materialize_bound_artifacts_and_then_suppress_replay(tmp_path) -> None:
    """@impl WON-003
    @impl NAC-006
    @impl EVH-015
    """

    seed = await build_live_seed_bundle(tmp_path, bundle=BUNDLE, include_wave1=False, now=NOW)
    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    capabilities = ScriptedWave1Capabilities()
    controller = WorkUnitControllerDependencies(
        store=seed.store,
        resolver=RuntimeWorkUnitDependencyResolver(
            graph_context,
            BaseResolver(graph_context, capabilities),
            seed.store,
        ),
    )
    state = _state() | {
        "topic_registry": seed.checkpoint["topic_registry"],
        "accepted_submission_refs": seed.checkpoint["accepted_submission_refs"],
    }
    result = await wave1_subgraph.run_wave1_work_units_real(
        state,
        controller=controller,
        topic_registry=state["topic_registry"],
        capabilities=capabilities,
        wave0_urls=frozenset({"https://example.invalid/wave0"}),
        clock=lambda: NOW,
    )

    review = await build_wave1_gate_review(
        controller,
        gate_view=result.gate_view,
        policy=wave1_subgraph.WAVE1_REAL_POLICY,
    )
    replay = await build_wave1_gate_review(
        controller,
        gate_view=result.gate_view,
        policy=wave1_subgraph.WAVE1_REAL_POLICY,
    )

    assert review == replay
    assert review.rows[0].source_diagnostic_present is True
    assert review.rows[0].claim_verifier_present is True
    assert [request.capability_ref.capability_id for request in capabilities.requests] == [
        "wave1-evidence-extraction",
        "wave1-source-diagnostic",
        "wave1-claim-verifier",
    ]
    artifacts = tuple(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("review/*.json"))
    assert any(path.endswith("review/source-diagnostic.json") for path in artifacts)
    assert any(path.endswith("review/claim-verifier.json") for path in artifacts)


async def test_wave1_post_acceptance_retry_dispatches_only_the_missing_critic(tmp_path) -> None:
    """@impl WON-003
    @impl NAC-006
    @impl EVH-015
    """

    seed = await build_live_seed_bundle(tmp_path, bundle=BUNDLE, include_wave1=False, now=NOW)
    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    capabilities = ScriptedWave1Capabilities(source_diagnostic_failure=True)
    controller = WorkUnitControllerDependencies(
        store=seed.store,
        resolver=RuntimeWorkUnitDependencyResolver(
            graph_context,
            BaseResolver(graph_context, capabilities),
            seed.store,
        ),
    )
    state = _state() | {
        "topic_registry": seed.checkpoint["topic_registry"],
        "accepted_submission_refs": seed.checkpoint["accepted_submission_refs"],
    }
    result = await wave1_subgraph.run_wave1_work_units_real(
        state,
        controller=controller,
        topic_registry=state["topic_registry"],
        capabilities=capabilities,
        wave0_urls=frozenset({"https://example.invalid/wave0"}),
        clock=lambda: NOW,
    )

    first = await build_wave1_gate_review(
        controller,
        gate_view=result.gate_view,
        policy=wave1_subgraph.WAVE1_REAL_POLICY,
    )
    capabilities.source_diagnostic_failure = False
    second = await build_wave1_gate_review(
        controller,
        gate_view=result.gate_view,
        policy=wave1_subgraph.WAVE1_REAL_POLICY,
    )

    assert first.rows[0].source_diagnostic_present is False
    assert first.rows[0].claim_verifier_present is True
    assert second.rows[0].source_diagnostic_present is True
    assert second.rows[0].claim_verifier_present is True
    assert [request.capability_ref.capability_id for request in capabilities.requests] == [
        "wave1-evidence-extraction",
        "wave1-source-diagnostic",
        "wave1-claim-verifier",
        "wave1-source-diagnostic",
    ]


async def test_wave1_missing_review_dispatch_suppresses_out_of_assignment_critic_result(tmp_path) -> None:
    """@impl WON-008"""

    capabilities = ScriptedWave1Capabilities(source_diagnostic_foreign=True)
    controller, result, first = await _run_real_wave1_until_review(tmp_path, capabilities)

    assert first.rows[0].source_diagnostic_present is False
    assert first.rows[0].claim_verifier_present is True
    assert [request.capability_ref.capability_id for request in capabilities.requests] == [
        "wave1-evidence-extraction",
        "wave1-source-diagnostic",
        "wave1-claim-verifier",
    ]

    capabilities.source_diagnostic_foreign = False
    second = await build_wave1_gate_review(
        controller,
        gate_view=result.gate_view,
        policy=wave1_subgraph.WAVE1_REAL_POLICY,
    )

    assert second.rows[0].source_diagnostic_present is True
    assert second.rows[0].claim_verifier_present is True


async def test_wave1_claim_verifier_materializes_one_bound_artifact(tmp_path) -> None:
    """@impl WON-003
    @impl NAC-006
    @impl EVH-015
    """

    capabilities = ScriptedWave1Capabilities()
    _controller, _result, review = await _run_real_wave1_until_review(tmp_path, capabilities)

    assert review.rows[0].claim_verifier_present is True
    assert [request.capability_ref.capability_id for request in capabilities.requests] == [
        "wave1-evidence-extraction",
        "wave1-source-diagnostic",
        "wave1-claim-verifier",
    ]


async def test_wave1_claim_verifier_invalid_result_retries_only_that_critic(tmp_path) -> None:
    """@impl WON-003
    @impl NAC-006
    @impl EVH-015
    """

    capabilities = ScriptedWave1Capabilities(claim_verifier_failure=True)
    controller, result, first = await _run_real_wave1_until_review(tmp_path, capabilities)
    capabilities.claim_verifier_failure = False
    second = await build_wave1_gate_review(
        controller,
        gate_view=result.gate_view,
        policy=wave1_subgraph.WAVE1_REAL_POLICY,
    )

    assert first.rows[0].source_diagnostic_present is True
    assert first.rows[0].claim_verifier_present is False
    assert second.rows[0].source_diagnostic_present is True
    assert second.rows[0].claim_verifier_present is True
    assert [request.capability_ref.capability_id for request in capabilities.requests] == [
        "wave1-evidence-extraction",
        "wave1-source-diagnostic",
        "wave1-claim-verifier",
        "wave1-claim-verifier",
    ]


async def test_real_wave1_review_gate_enforces_question_floor_and_review_integrity(tmp_path) -> None:
    """@impl WON-004"""

    capabilities = ScriptedWave1Capabilities(
        provider_payload={
            "schema_version": 1,
            "sources": [
                {
                    "source_id": "source:one",
                    "canonical_url": "https://example.com/one",
                    "title": "One",
                },
                {
                    "source_id": "source:two",
                    "canonical_url": "https://example.com/two",
                    "title": "Two",
                },
            ],
            "claims": [
                {
                    "claim_id": "claim:w1_question",
                    "statement": "The sources leave one bounded question.",
                    "support_refs": ["source:one", "source:two"],
                    "counter_refs": [],
                }
            ],
            "open_questions": [
                {
                    "question_id": "q:w1_more-evidence",
                    "question": "Which deployment context has the lower operating cost?",
                    "state": "targeted_search",
                }
            ],
        }
    )
    controller, result, review = await _run_real_wave1_until_review(tmp_path, capabilities)
    gate_state = (
        _state()
        | result.parent_update
        | {
            WORK_UNIT_GATE_VIEW_KEY: result.gate_view,
            WAVE1_GATE_REVIEW_KEY: review,
        }
    )

    question_result = evaluate_gate(gate_state, "wave1", real_wave1_gate_def())
    assert question_result.route == "repair"
    assert review.rows[0].open_question_states == (OpenQuestionState.TARGETED_SEARCH,)

    exhausted_review = Wave1GateReview(rows=(review.rows[0].model_copy(update={"distinct_new_url_count": 1}),))
    exhausted_result = evaluate_gate(
        gate_state | {"repair_budget_by_phase": {"wave1": 0}, WAVE1_GATE_REVIEW_KEY: exhausted_review},
        "wave1",
        real_wave1_gate_def(),
    )
    assert exhausted_result.route == "exhausted"

    records = await controller.store.load_records()
    artifact_path = next(tmp_path.rglob("source-diagnostic.json"))
    artifact_path.write_bytes(b"not-json")

    with pytest.raises(ValueError, match="wave1_review_artifact_invalid"):
        await build_wave1_gate_review(
            controller,
            gate_view=result.gate_view,
            policy=wave1_subgraph.WAVE1_REAL_POLICY,
        )
    assert len(await controller.store.load_records()) == len(records)


async def test_real_wave1_wrapper_consumes_the_private_review_before_state_reduction(tmp_path) -> None:
    """@impl WON-004"""

    context, _store = _context(tmp_path)
    gate_view = WorkUnitGateView(
        drained=True,
        planned_work_ids=(),
        terminal_attempt_by_work_id={},
        accepted_record_by_work_id={},
        failure_summaries=(),
    )

    def factory(_dependencies: NodeBuildDependencies):
        async def run(_state):
            return {
                WORK_UNIT_GATE_VIEW_KEY: gate_view,
                WAVE1_GATE_REVIEW_KEY: Wave1GateReview(rows=()),
            }

        return run

    spec = replace(NODE_SPEC, real_factory=factory)
    wrapped = _node_wrapper(
        "wave1",
        spec,
        NodeAdapter(factory=spec.real_factory, kind=AdapterKind.REAL, requires_gate=True),
        {"wave1": real_wave1_gate_def()},
    )

    update = await wrapped(_state(), SimpleNamespace(context=context))

    assert update["route"] == "pass"
    assert WAVE1_GATE_REVIEW_KEY not in update


async def test_real_wave1_malformed_repair_has_no_artifact_admission(tmp_path) -> None:
    """@impl WON-007
    @impl EVH-015
    """
    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    capabilities = ScriptedWave1Capabilities(
        invocation_results=(
            NodeExecutionResult(finish_reason=NodeFinishReason.SUCCESS, summary="not-json"),
            NodeExecutionResult(finish_reason=NodeFinishReason.SUCCESS, summary="still-not-json"),
        )
    )
    store = _store(tmp_path, token="6" * 32)
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=RuntimeWorkUnitDependencyResolver(graph_context, BaseResolver(graph_context, capabilities), store),
    )
    topics = ({"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},)
    observation_projection = _ObservationProjection()

    result = await wave1_subgraph.run_wave1_work_units_real(
        _state() | {"topic_registry": topics},
        controller=controller,
        topic_registry=topics,
        capabilities=capabilities,
        wave0_urls=frozenset(),
        clock=lambda: NOW,
        observation_projection=observation_projection,
    )

    assert len(capabilities.requests) == 2
    assert capabilities.requests[1].tools_enabled is False
    assert capabilities.requests[1].capability_ref is not None
    assert capabilities.requests[1].capability_ref.capability_id == "wave1-evidence-extraction-repair"
    assert [event for event in observation_projection.events if event["operation"] == "validation"] == [
        {
            "phase": "wave1",
            "operation": "validation",
            "outcome": "rejected",
            "bundle_id": BUNDLE_ID,
            "work_id": "g0_wave1_w0000",
            "attempt_id": "g0_wave1_w0000_a00",
            "code": "validation_rejected",
        },
        {
            "phase": "wave1",
            "operation": "validation",
            "outcome": "rejected",
            "bundle_id": BUNDLE_ID,
            "work_id": "g0_wave1_w0000",
            "attempt_id": "g0_wave1_w0000_a00",
            "code": "validation_rejected",
        },
    ]
    assert result.parent_update["accepted_submission_refs"] == ()
    assert await store.load_records() == ()


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(
            {
                "schema_version": 1,
                "sources": [
                    {"source_id": "source:one", "canonical_url": "https://example.com/duplicate", "title": "One"},
                    {"source_id": "source:two", "canonical_url": "https://example.com/duplicate", "title": "Two"},
                ],
                "claims": [],
            },
            id="duplicate-url",
        ),
        pytest.param(
            {
                "schema_version": 1,
                "sources": [
                    {"source_id": "source:one", "canonical_url": "https://example.com/one", "title": "One"},
                    {"source_id": "source:two", "canonical_url": "https://example.com/two", "title": "Two"},
                ],
                "claims": [
                    {
                        "claim_id": "claim:w1_foreign",
                        "statement": "This reference must be rejected.",
                        "support_refs": ["source:foreign"],
                        "counter_refs": [],
                    }
                ],
            },
            id="foreign-claim-ref",
        ),
        pytest.param(
            {
                "schema_version": 1,
                "sources": [
                    {"source_id": "source:one", "canonical_url": "https://example.com/one", "title": "One"},
                ],
                "claims": [],
            },
            id="inadequate-new-source-floor",
        ),
    ],
)
async def test_real_wave1_semantic_rejection_reaches_repair_before_any_artifact_write(tmp_path, payload) -> None:
    """@impl WON-002"""

    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    capabilities = ScriptedWave1Capabilities(provider_payload=payload)
    store = _store(tmp_path, token="9" * 32)
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=RuntimeWorkUnitDependencyResolver(graph_context, BaseResolver(graph_context, capabilities), store),
    )
    topics = ({"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},)

    result = await wave1_subgraph.run_wave1_work_units_real(
        _state() | {"topic_registry": topics},
        controller=controller,
        topic_registry=topics,
        capabilities=capabilities,
        wave0_urls=frozenset(),
        clock=lambda: NOW,
    )

    assert len(capabilities.requests) == 2
    assert capabilities.requests[1].tools_enabled is False
    assert "Trusted validation category: initial_local_semantic_validation_failed" in capabilities.requests[1].objective
    assert result.parent_update["accepted_submission_refs"] == ()
    assert await store.load_records() == ()
    files = tuple(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*") if path.is_file())
    assert not any("/cache/" in path or path.endswith("/result.json") for path in files)


async def test_real_wave1_journal_retains_exact_initial_and_repair_validation_per_attempt(tmp_path) -> None:
    """@impl REJ-002
    @impl WON-012

    Validation facts remain distinct from worker recovery authority.
    """

    payload = {
        "schema_version": 1,
        "sources": [
            {
                "source_id": "source:only",
                "canonical_url": "https://example.com/only",
                "title": "Only one source",
            }
        ],
        "claims": [],
    }
    topics = (
        {"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},
        {"topic_id": "resilience", "title": "Resilience", "scope": "Resilience economics"},
    )
    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    capabilities = ScriptedWave1Capabilities(provider_payload=payload)
    store = _store(tmp_path, token="8" * 32)
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=RuntimeWorkUnitDependencyResolver(graph_context, BaseResolver(graph_context, capabilities), store),
    )
    journal_store = RunObservationStore(
        bundle_root=BundleLifecycle(workspace_host_path=tmp_path).private_root(BUNDLE),
        bundle_id=BUNDLE_ID,
    )
    recorder = RunObservationRecorder(store=journal_store, bundle_id=BUNDLE_ID)
    await recorder.establish(generation=0, phase="wave1", durability="restart_durable")
    state = _state() | {"topic_registry": topics}

    first = await wave1_subgraph.run_wave1_work_units_real(
        state,
        controller=controller,
        topic_registry=topics,
        capabilities=capabilities,
        wave0_urls=frozenset(),
        clock=lambda: NOW,
        event_recorder=recorder,
    )
    retry = await wave1_subgraph.run_wave1_work_units_real(
        _apply_result(state, first.parent_update),
        controller=controller,
        topic_registry=topics,
        capabilities=capabilities,
        wave0_urls=frozenset(),
        clock=lambda: NOW,
        event_recorder=recorder,
    )
    journal = await journal_store.inspect(bundle_id=BUNDLE_ID)

    assert first.parent_update["accepted_submission_refs"] == ()
    assert retry.parent_update["accepted_submission_refs"] == ()
    assert first.gate_view.drained and retry.gate_view.drained
    validation_events = tuple(event for event in journal.events if event.category is RunEventCategory.VALIDATION)
    attempt_ids = {event.attempt_id for event in validation_events}
    correlations = {(event.work_id, event.attempt_id) for event in validation_events}
    assert len(attempt_ids) == len(correlations) == 4
    assert {event.generation for event in validation_events} == {0}
    assert {event.phase for event in validation_events} == {"wave1"}
    assert {work_id for work_id, _attempt_id in correlations} == {"g0_wave1_w0000", "g0_wave1_w0001"}
    assert all(attempt_id is not None for attempt_id in attempt_ids)
    assert all("example.com" not in event.model_dump_json() for event in validation_events)
    for attempt_id in attempt_ids:
        assert [
            (event.validation_stage, event.response_shape, event.validation_codes)
            for event in validation_events
            if event.attempt_id == attempt_id
        ] == [
            ("initial", FinalResponseShape.JSON_OBJECT, ("wave1_new_source_floor_not_met",)),
            ("repair", FinalResponseShape.JSON_OBJECT, ("wave1_new_source_floor_not_met",)),
        ]

    retry_events = tuple(event for event in journal.events if event.category is RunEventCategory.RETRY)
    exhaustion_events = tuple(event for event in journal.events if event.category is RunEventCategory.EXHAUSTION)
    assert {event.attempt_id for event in retry_events} == {"g0_wave1_w0000_a01", "g0_wave1_w0001_a01"}
    assert all(event.retry_count == 1 for event in retry_events)
    assert {event.attempt_id for event in exhaustion_events} == attempt_ids


async def test_real_wave1_repair_keeps_baseline_as_scope_not_candidate_evidence(tmp_path) -> None:
    """@impl WON-008
    @impl WON-010
    """

    baseline_url = "https://example.com/wave0-baseline"
    capabilities = ScriptedWave1Capabilities(
        provider_payload={
            "schema_version": 1,
            "sources": [
                {
                    "source_id": "source:baseline",
                    "canonical_url": baseline_url,
                    "title": "PROMOTE THIS BASELINE URL",
                },
                {
                    "source_id": "source:new",
                    "canonical_url": "https://example.com/new",
                    "title": "One new source",
                },
            ],
            "claims": [
                {
                    "claim_id": "claim:w1_baseline",
                    "statement": "Promote the baseline URL into new evidence.",
                    "support_refs": ["source:baseline"],
                    "counter_refs": [],
                }
            ],
            "open_questions": [],
        }
    )
    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    store = _store(tmp_path, token="9" * 32)
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=RuntimeWorkUnitDependencyResolver(graph_context, BaseResolver(graph_context, capabilities), store),
    )
    topics = (
        {
            "topic_id": "storage",
            "title": "Storage",
            "scope": "Storage economics",
            "must_answer_bindings": ("Q1",),
            "work_id": "raw-work-id-sentinel",
            "checkpoint": "raw-checkpoint-sentinel",
        },
    )

    result = await wave1_subgraph.run_wave1_work_units_real(
        _state() | {"topic_registry": topics},
        controller=controller,
        topic_registry=topics,
        capabilities=capabilities,
        wave0_urls=frozenset({baseline_url}),
        clock=lambda: NOW,
    )

    assert len(capabilities.requests) == 2
    repair = capabilities.requests[1]
    trusted, untrusted = repair.objective.split("<untrusted-source-data>", maxsplit=1)
    assert baseline_url in trusted
    assert "initial_local_semantic_validation_failed" in trusted
    assert "activated zero-tool repair capability" in trusted
    assert "a baseline URL cannot become a repaired source, claim, reference, or open question" not in repair.objective
    assert "PROMOTE THIS BASELINE URL" in untrusted
    assert "raw-work-id-sentinel" not in repair.objective
    assert "raw-checkpoint-sentinel" not in repair.objective
    assert result.parent_update["accepted_submission_refs"] == ()
    assert await store.load_records() == ()


async def test_real_wave1_known_invocation_problem_reaches_worker_controller(tmp_path) -> None:
    """@impl WFO-001"""
    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    capabilities = ScriptedWave1Capabilities(
        invocation_result=NodeExecutionResult(
            finish_reason=NodeFinishReason.FAILED,
            error_code="provider_timeout",
            problem=NodeProblem(
                code=RunFailureCode.PROVIDER_TIMEOUT,
                phase="wave1",
                certainty=FailureCertainty.DIRECT,
                provider_observation=ProviderObservation(
                    configured_service_label="wave1-worker-model",
                    response_kind="no_response",
                ),
            ),
        )
    )
    store = _store(tmp_path, token="3" * 32)
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=RuntimeWorkUnitDependencyResolver(
            graph_context,
            BaseResolver(graph_context, capabilities),
            store,
        ),
    )
    topics = ({"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},)

    result = await wave1_subgraph.run_wave1_work_units_real(
        _state() | {"topic_registry": topics},
        controller=controller,
        topic_registry=topics,
        capabilities=capabilities,
        wave0_urls=frozenset(),
        clock=lambda: NOW,
    )

    attempts = tuple(result.parent_update["attempts_by_id"].values())
    failures = tuple(result.parent_update["terminal_failures_by_attempt_id"].values())
    assert result.parent_update["accepted_submission_refs"] == ()
    assert len(attempts) == len(failures) == 1
    assert attempts[0]["failure_category"] == "agent_invocation"
    assert attempts[0]["provider_category"] == "provider.timeout"
    assert attempts[0]["provider_observation"]["configured_service_label"] == "wave1-worker-model"
    assert attempts[0]["provider_observation"]["response_kind"] == "no_response"
    assert failures[0]["failure_category"] == "agent_invocation"
    assert failures[0]["provider_category"] == "provider.timeout"
    assert failures[0]["provider_observation"]["configured_service_label"] == "wave1-worker-model"
    assert await store.load_records() == ()
    files = tuple(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*") if path.is_file())
    assert not any("/cache/" in path or path.endswith("/result.json") for path in files)
    assert not any(path.endswith("/evidence/submissions.jsonl") for path in files)


async def test_real_wave1_repair_invocation_problem_reaches_worker_controller(tmp_path) -> None:
    """@impl WFO-001

    A known repair-call failure remains a controller-owned worker outcome rather
    than collapsing into the former generic ``wave1_worker_repair_failed`` path.
    """
    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    sentinel = "raw provider body must not be retained"
    capabilities = ScriptedWave1Capabilities(
        invocation_results=(
            NodeExecutionResult(finish_reason=NodeFinishReason.SUCCESS, summary="not-json"),
            NodeExecutionResult(
                finish_reason=NodeFinishReason.FAILED,
                summary=sentinel,
                problem=NodeProblem(
                    code=RunFailureCode.PROVIDER_UNAVAILABLE,
                    phase="wave1",
                    certainty=FailureCertainty.DIRECT,
                    provider_observation=ProviderObservation(
                        configured_service_label="wave1-worker-model",
                        response_kind="http_response",
                        http_status=503,
                    ),
                ),
            ),
        )
    )
    store = _store(tmp_path, token="4" * 32)
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=RuntimeWorkUnitDependencyResolver(
            graph_context,
            BaseResolver(graph_context, capabilities),
            store,
        ),
    )
    topics = ({"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},)

    result = await wave1_subgraph.run_wave1_work_units_real(
        _state() | {"topic_registry": topics},
        controller=controller,
        topic_registry=topics,
        capabilities=capabilities,
        wave0_urls=frozenset(),
        clock=lambda: NOW,
    )

    attempts = tuple(result.parent_update["attempts_by_id"].values())
    failures = tuple(result.parent_update["terminal_failures_by_attempt_id"].values())
    assert len(capabilities.requests) == 2
    assert capabilities.requests[1].tools_enabled is False
    assert result.parent_update["accepted_submission_refs"] == ()
    assert len(attempts) == len(failures) == 1
    assert attempts[0]["failure_category"] == "agent_invocation"
    assert attempts[0]["provider_category"] == "provider.unavailable"
    assert attempts[0]["provider_observation"]["http_status"] == 503
    assert failures[0]["failure_category"] == "agent_invocation"
    assert failures[0]["provider_category"] == "provider.unavailable"
    assert failures[0]["provider_observation"]["http_status"] == 503
    assert sentinel not in str(result.parent_update)
    assert await store.load_records() == ()
    files = tuple(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*") if path.is_file())
    assert not any("/cache/" in path or path.endswith("/result.json") for path in files)
    assert not any(path.endswith("/evidence/submissions.jsonl") for path in files)


@pytest.mark.parametrize(
    "case",
    [pytest.param(SHAPE_CASES["shape-wave1-source-order"], id="shape-wave1-source-order")],
)
async def test_real_wave1_canonicalizes_provider_source_order_before_candidate_validation(tmp_path, case) -> None:
    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    capabilities = ScriptedWave1Capabilities(provider_payload=thaw_provider_shape_payload(case.payload))
    store = _store(tmp_path, token="7" * 32)
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=RuntimeWorkUnitDependencyResolver(
            graph_context,
            BaseResolver(graph_context, capabilities),
            store,
        ),
    )
    topics = ({"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},)

    result = await wave1_subgraph.run_wave1_work_units_real(
        _state() | {"topic_registry": topics},
        controller=controller,
        topic_registry=topics,
        capabilities=capabilities,
        wave0_urls=frozenset(),
        clock=lambda: NOW,
    )

    records = await store.load_records()
    assert result.parent_update["accepted_submission_refs"] == (records[0].record_hash,)
    assert tuple(source.source_id for source in records[0].source_refs) == ("source:a", "source:z")
    persisted = json.loads(await store.read_canonical_bytes(records[0].result_ref, max_bytes=256 * 1024))
    observed = {
        "source_ids": persisted["source_ids"],
        "support_refs": persisted["claims"][0]["support_refs"],
    }
    assert observed == thaw_provider_shape_payload(case.expected_payload)


@pytest.mark.parametrize(
    "case",
    [pytest.param(SHAPE_CASES["shape-wave1-malformed-submit"], id="shape-wave1-malformed-submit")],
)
async def test_real_wave1_malformed_output_becomes_typed_worker_failure_without_ledger(tmp_path, case) -> None:
    graph_context = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    capabilities = ScriptedWave1Capabilities(provider_payload=thaw_provider_shape_payload(case.payload))
    store = _store(tmp_path, token="4" * 32)
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=RuntimeWorkUnitDependencyResolver(
            graph_context,
            BaseResolver(graph_context, capabilities),
            store,
        ),
    )
    topics = ({"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},)

    result = await wave1_subgraph.run_wave1_work_units_real(
        _state() | {"topic_registry": topics},
        controller=controller,
        topic_registry=topics,
        capabilities=capabilities,
        wave0_urls=frozenset(),
        clock=lambda: NOW,
    )

    assert result.parent_update["accepted_submission_refs"] == ()
    assert tuple(result.parent_update["work_status_by_id"].values()) == ("failed",)
    assert await store.load_records() == ()
    assert case.expected_error_code == "source_ids_mismatch"
