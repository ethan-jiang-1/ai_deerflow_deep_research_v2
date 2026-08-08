from __future__ import annotations

import time
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from deerflow_deep_research_fixtures.gates import build_fixture_gate_definitions
from deerflow_deep_research_fixtures.graph.nodes.wave0 import adapter as fixture_wave0_adapter
from deerflow_deep_research_fixtures.scenario import FixtureScenario
from deerflow_deep_research_fixtures.work_units import run_fixture_work_unit_component

from deerflow_deep_research.domain.bundle import (
    BundleId,
    RunBundleRef,
    bundle_host_relative_root,
    bundle_result_path,
    bundle_source_content_path,
    run_bundle_root,
)
from deerflow_deep_research.domain.context import (
    GraphContextView,
    NodeAgentBundleContext,
    NodeAgentContext,
    NodeExecutionResult,
    SelectedBundleContext,
)
from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.domain.invocation import GraphInvocationContext, WorkUnitControllerDependencies
from deerflow_deep_research.domain.lifecycle import WorkUnitStorageReason
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies, NodeCapability, PolicyRef
from deerflow_deep_research.domain.run_experience import (
    FailureCertainty,
    NodeProblem,
    ProviderObservation,
    RunFailureCode,
)
from deerflow_deep_research.domain.state import WORK_UNIT_GATE_PREVIEW_FIELDS, merge_trace, preview_work_unit_update
from deerflow_deep_research.domain.work_units import (
    WORK_UNIT_GATE_VIEW_KEY,
    SubmissionValidationCode,
    WorkerFailureAggregate,
    WorkSpecRef,
    aggregate_worker_failure_category,
    canonical_json_bytes,
)
from deerflow_deep_research.engine.gate_kernel import evaluate_gate, gate_result_to_state_update
from deerflow_deep_research.engine.work_units.kernel import allocate_attempt, materialize_work_spec, transition_attempt
from deerflow_deep_research.graph.builder import _node_wrapper
from deerflow_deep_research.graph.components import work_units as work_unit_component
from deerflow_deep_research.graph.components.work_units import reconcile_parent_ledger_authority
from deerflow_deep_research.graph.implementation_map import AdapterKind, NodeAdapter
from deerflow_deep_research.graph.nodes.gate_adapter import real_wave0_gate_def
from deerflow_deep_research.graph.nodes.wave0 import NODE_SPEC
from deerflow_deep_research.graph.nodes.wave0.subgraph import run_wave0_work_units_real
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.projection import RuntimeWorkUnitDependencyResolver
from deerflow_deep_research.runtime.work_unit_storage import WorkUnitStoreError
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore
from tests.scenarios.assertions import assert_scenario
from tests.scenarios.observation import (
    CheckpointFacts,
    LedgerFacts,
    SandboxFacts,
    ScenarioObservation,
    WorkGateOutcome,
    WorkStateFacts,
)
from tests.scenarios.replays import PARTIAL_WORKER_SUCCESS_CASE, PARTIAL_WORKER_SUCCESS_FAMILY

NOW = datetime(2026, 7, 14, tzinfo=UTC)
BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "A" * 43)
BUNDLE_ID = BUNDLE.bundle_id.value
WAVE0_FIXTURE_INTENTS = fixture_wave0_adapter._INTENTS


class ForbiddenCapabilities:
    async def run_agent(self, *, context, request):
        raise AssertionError("fixture work must not call an agent")


class _ResultCapabilities:
    def __init__(self, result: object) -> None:
        self.results = [result] if not isinstance(result, tuple) else list(result)
        self.requests: list[object] = []

    async def run_agent(self, *, context, request) -> NodeExecutionResult:  # noqa: ARG002
        self.requests.append(request)
        result = self.results.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result  # type: ignore[return-value]


def _graph_context() -> GraphContextView:
    return GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )


class BaseResolver:
    def __init__(
        self,
        graph_context: GraphContextView,
        capabilities: object | None = None,
        *,
        bundle: RunBundleRef = BUNDLE,
    ) -> None:
        self._graph_context = graph_context
        self._capabilities = capabilities if capabilities is not None else ForbiddenCapabilities()
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


class FailOneWorkerResolver:
    def __init__(self, delegate, *, work_ordinal: int) -> None:
        self._delegate = delegate
        self._work_ordinal = work_ordinal

    async def resolve_worker(self, **kwargs):
        resolved = await self._delegate.resolve_worker(**kwargs)
        if kwargs["work_spec"].work_ordinal == self._work_ordinal:
            raise RuntimeError("scripted worker failure")
        return resolved


def _publish_bundle(workspace, bundle: RunBundleRef = BUNDLE) -> None:
    BundleLifecycle(workspace_host_path=workspace)._publish_sync(bundle)


def _store(tmp_path, *, bundle: RunBundleRef = BUNDLE) -> WorkUnitStore:
    _publish_bundle(tmp_path, bundle)
    return WorkUnitStore(
        workspace_host_path=tmp_path,
        bundle=bundle,
        clock=lambda: NOW,
        monotonic=time.monotonic,
        lock_sleep=time.sleep,
        token_factory=lambda: "0" * 32,
        fault_hook=None,
    )


def _context(tmp_path, capabilities: object | None = None) -> tuple[GraphInvocationContext, WorkUnitStore]:
    graph_context = _graph_context()
    base = BaseResolver(graph_context, capabilities, bundle=BUNDLE)
    store = _store(tmp_path)
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


async def run_wave0_work_units(
    state: dict,
    *,
    controller: WorkUnitControllerDependencies,
    clock,
    fault_hook=None,
):
    """Test-only adapter over the fixture-owned deterministic worker path."""

    return await run_fixture_work_unit_component(
        state,
        logical_name="wave0",
        policy=PolicyRef(name="fixture-wave0", version="v1"),
        controller=controller,
        intents=WAVE0_FIXTURE_INTENTS,
        clock=clock,
        fault_hook=fault_hook,
    )


def _apply_result(state: dict, result: dict) -> dict:
    next_state = dict(state)
    preview_delta = {key: value for key, value in result.items() if key in WORK_UNIT_GATE_PREVIEW_FIELDS}
    next_state.update(preview_work_unit_update(state, preview_delta))
    for key, value in result.items():
        if key in WORK_UNIT_GATE_PREVIEW_FIELDS:
            continue
        if key == "execution_trace":
            next_state[key] = merge_trace(state.get(key, ()), value)
        else:
            next_state[key] = value
    return next_state


async def test_wave0_shared_component_replays_and_quality_repair_allocates_new_work(tmp_path) -> None:
    assert NODE_SPEC.capabilities == frozenset({NodeCapability.WORK_UNIT_CONTROLLER})
    gate = build_fixture_gate_definitions(FixtureScenario(wave0=("repair", "pass")))["wave0"]
    assert tuple(rule.name for rule in gate.rules[:2]) == (
        "work_unit_completion",
        "fixture_sequence_wave0",
    )

    context, store = _context(tmp_path)
    wrapped = _node_wrapper(
        "wave0",
        NODE_SPEC,
        NodeAdapter(factory=fixture_wave0_adapter.build_fixture, kind=AdapterKind.FIXTURE, requires_gate=True),
        {"wave0": gate},
    )
    first = await wrapped(_state(), SimpleNamespace(context=context))
    assert WORK_UNIT_GATE_VIEW_KEY not in first
    assert first["route"] == "repair"
    assert tuple(first["work_specs_by_id"]) == (
        "g0_wave0_w0000",
        "g0_wave0_w0001",
        "g0_wave0_w0002",
    )
    assert tuple(first["attempts_by_id"]) == tuple(f"{work_id}_a00" for work_id in first["work_specs_by_id"])
    assert len(first["accepted_submission_refs"]) == 3
    assert first["next_work_ordinal"] == 3
    assert first["pending_work_ids"] == ()
    assert len(await store.load_records()) == 3

    replay_state = _state()
    replay = await wrapped(replay_state, SimpleNamespace(context=context))
    assert replay["accepted_submission_refs"] == first["accepted_submission_refs"]
    assert len(await store.load_records()) == 3

    second_state = _apply_result(_state(), first)
    second = await wrapped(second_state, SimpleNamespace(context=context))
    assert second["route"] == "pass"
    assert tuple(second["work_specs_by_id"]) == (
        "g0_wave0_w0003",
        "g0_wave0_w0004",
        "g0_wave0_w0005",
    )
    assert second["next_work_ordinal"] == 6
    assert len(await store.load_records()) == 6


async def test_real_wave0_known_invocation_problem_reaches_worker_controller(tmp_path) -> None:
    """@impl WFO-001"""
    problem = NodeProblem(
        code=RunFailureCode.PROVIDER_TIMEOUT,
        phase="wave0",
        certainty=FailureCertainty.DIRECT,
        provider_observation=ProviderObservation(
            configured_service_label="wave0-worker-model",
            response_kind="no_response",
        ),
    )
    capabilities = _ResultCapabilities(
        NodeExecutionResult(
            finish_reason=NodeFinishReason.FAILED,
            error_code="provider_timeout",
            problem=problem,
        )
    )
    context, store = _context(tmp_path, capabilities)
    assert context.work_units is not None

    component = await run_wave0_work_units_real(
        _state(),
        controller=context.work_units,
        topic_registry=({"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},),
        clock=lambda: NOW,
    )

    attempts = tuple(component.parent_update["attempts_by_id"].values())
    failures = tuple(component.parent_update["terminal_failures_by_attempt_id"].values())
    assert component.parent_update["accepted_submission_refs"] == ()
    assert len(attempts) == len(failures) == 1
    assert attempts[0]["failure_category"] == "agent_invocation"
    assert attempts[0]["provider_category"] == "provider.timeout"
    assert failures[0]["failure_category"] == "agent_invocation"
    assert failures[0]["provider_category"] == "provider.timeout"
    work_id = next(iter(component.parent_update["attempts_by_id"])).rsplit("_a", 1)[0]
    assert (
        aggregate_worker_failure_category(component.parent_update["attempts_by_id"], work_id=work_id)
        is WorkerFailureAggregate.AGENT_INVOCATION
    )
    assert await store.load_records() == ()
    files = tuple(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*") if path.is_file())
    assert not any("/cache/" in path or path.endswith("/result.json") for path in files)
    assert not any(path.endswith("/evidence/submissions.jsonl") for path in files)


async def test_real_wave0_worker_binds_the_required_capability_before_artifact_admission(tmp_path) -> None:
    """@impl NAC-003
    @impl NAC-004
    @impl EVH-012
    @impl WAN-007
    @impl EVH-015
    """
    capabilities = _ResultCapabilities(
        NodeExecutionResult(
            finish_reason=NodeFinishReason.SUCCESS,
            summary=(
                '{"schema_version":1,"sources":[{"source_id":"source:storage","canonical_url":'
                '"https://example.com/storage","title":"Storage","fetch_status":"fetched"}],'
                '"baseline_facts":["storage is bounded"],"limitations":""}'
            ),
        )
    )
    context, store = _context(tmp_path, capabilities)
    assert context.work_units is not None

    component = await run_wave0_work_units_real(
        _state(),
        controller=context.work_units,
        topic_registry=({"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},),
        clock=lambda: NOW,
    )

    request = capabilities.requests[0]
    assert request.capability_ref is not None
    assert request.capability_ref.capability_id == "wave0-authoritative-source-intake"
    assert request.tools_enabled is True
    assert request.minimum_tool_calls == 1
    assert request.tool_call_limit == 3
    assert len(component.parent_update["accepted_submission_refs"]) == 1
    assert len(await store.load_records()) == 1


async def test_real_wave0_artifacts_remain_bound_to_the_selected_run_bundle(tmp_path) -> None:
    """The worker cannot recreate legacy paths from its WorkSpec identity."""
    capabilities = _ResultCapabilities(
        NodeExecutionResult(
            finish_reason=NodeFinishReason.SUCCESS,
            summary=(
                '{"schema_version":1,"sources":[{"source_id":"source:storage","canonical_url":'
                '"https://example.com/storage","title":"Storage","fetch_status":"fetched"}],'
                '"baseline_facts":["storage is bounded"],"limitations":""}'
            ),
        )
    )
    context, store = _context(tmp_path, capabilities)
    assert context.work_units is not None

    component = await run_wave0_work_units_real(
        _state(),
        controller=context.work_units,
        topic_registry=({"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},),
        clock=lambda: NOW,
    )

    (record,) = await store.load_records()
    assert len(component.parent_update["accepted_submission_refs"]) == 1
    assert record.result_ref == bundle_result_path(BUNDLE, record.work_id, record.attempt_id)
    assert tuple(source.content_ref for source in record.source_refs) == (
        bundle_source_content_path(BUNDLE, record.work_id, record.attempt_id, "source-0.json"),
    )


async def test_real_wave0_all_workers_fail_without_evidence_publication(tmp_path) -> None:
    """The real component cannot create evidence when every assigned worker fails."""
    failure = NodeExecutionResult(
        finish_reason=NodeFinishReason.FAILED,
        error_code="provider_timeout",
        problem=NodeProblem(
            code=RunFailureCode.PROVIDER_TIMEOUT,
            phase="wave0",
            certainty=FailureCertainty.DIRECT,
        ),
    )
    capabilities = _ResultCapabilities((failure, failure))
    context, store = _context(tmp_path, capabilities)
    assert context.work_units is not None

    component = await run_wave0_work_units_real(
        _state(),
        controller=context.work_units,
        topic_registry=(
            {"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},
            {"topic_id": "solar", "title": "Solar", "scope": "Solar economics"},
        ),
        clock=lambda: NOW,
    )

    attempts = tuple(component.parent_update["attempts_by_id"].values())
    assert len(attempts) == 2
    assert component.parent_update["accepted_submission_refs"] == ()
    assert all(attempt["failure_category"] == "agent_invocation" for attempt in attempts)
    assert await store.load_records() == ()


async def test_real_wave0_repair_keeps_tools_disabled_and_preserves_worker_admission(tmp_path) -> None:
    """@impl NAC-003
    @impl NAC-004
    @impl EVH-012
    @impl WAN-007
    """
    capabilities = _ResultCapabilities(
        (
            NodeExecutionResult(
                finish_reason=NodeFinishReason.SUCCESS,
                summary="not-json",
                untrusted_tool_results=("wave0 retained observation",),
            ),
            NodeExecutionResult(
                finish_reason=NodeFinishReason.SUCCESS,
                summary=(
                    '{"schema_version":1,"sources":[{"source_id":"source:storage","canonical_url":'
                    '"https://example.com/storage","title":"Storage","fetch_status":"fetched"}],'
                    '"baseline_facts":[],"limitations":""}'
                ),
            ),
        )
    )
    context, _store = _context(tmp_path, capabilities)
    assert context.work_units is not None

    component = await run_wave0_work_units_real(
        _state(),
        controller=context.work_units,
        topic_registry=({"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},),
        clock=lambda: NOW,
    )

    assert len(capabilities.requests) == 2
    normal, repair = capabilities.requests
    assert normal.capability_ref is not None
    assert normal.capability_ref.capability_id == "wave0-authoritative-source-intake"
    assert repair.capability_ref is not None
    assert repair.capability_ref.capability_id == "wave0-source-intake-repair"
    assert repair.tools_enabled is False
    assert "Trusted assignment (scope only)" in repair.objective
    assert '"title":"Storage"' in repair.objective
    assert "Trusted validation category: initial_structured_output_invalid" in repair.objective
    assert "model_draft:\nnot-json" in repair.objective
    assert "tool_result_1:\nwave0 retained observation" in repair.objective
    assert "wave0_worker_output_json_invalid" not in repair.objective
    for forbidden in (
        "raw-checkpoint-field-sentinel",
        "raw-ledger-record-sentinel",
        "raw-review-sentinel",
        "raw-gate-sentinel",
        "raw-route-sentinel",
        "g0_wave0_w0000",
    ):
        assert forbidden not in repair.objective
    assert len(component.parent_update["accepted_submission_refs"]) == 1


async def test_real_wave0_malformed_repair_fails_without_artifact_admission(tmp_path) -> None:
    """@impl NAC-003
    @impl NAC-004
    @impl EVH-012
    """
    capabilities = _ResultCapabilities(
        (
            NodeExecutionResult(finish_reason=NodeFinishReason.SUCCESS, summary="not-json"),
            NodeExecutionResult(finish_reason=NodeFinishReason.SUCCESS, summary="still-not-json"),
        )
    )
    context, store = _context(tmp_path, capabilities)
    assert context.work_units is not None

    component = await run_wave0_work_units_real(
        _state(),
        controller=context.work_units,
        topic_registry=({"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},),
        clock=lambda: NOW,
    )

    assert len(capabilities.requests) == 2
    assert capabilities.requests[0].capability_ref is not None
    assert capabilities.requests[0].capability_ref.capability_id == "wave0-authoritative-source-intake"
    assert capabilities.requests[1].capability_ref is not None
    assert capabilities.requests[1].capability_ref.capability_id == "wave0-source-intake-repair"
    assert capabilities.requests[1].tools_enabled is False
    assert component.parent_update["accepted_submission_refs"] == ()
    assert await store.load_records() == ()


async def test_real_wave0_post_candidate_submission_validation_does_not_enter_repair(monkeypatch, tmp_path) -> None:
    """@impl WAN-008

    The shared controller, not the Wave0 subgraph, owns a later validation failure.
    """

    capabilities = _ResultCapabilities(
        NodeExecutionResult(
            finish_reason=NodeFinishReason.SUCCESS,
            summary=(
                '{"schema_version":1,"sources":[{"source_id":"source:storage","canonical_url":'
                '"https://example.com/storage","title":"Storage","fetch_status":"fetched"}],'
                '"baseline_facts":[],"limitations":""}'
            ),
        )
    )
    context, store = _context(tmp_path, capabilities)
    assert context.work_units is not None

    async def reject_after_candidate(*_args, **_kwargs):
        raise work_unit_component.SubmissionValidationFailure((SubmissionValidationCode.CONTENT_HASH_MISMATCH,))

    monkeypatch.setattr(work_unit_component, "submit_candidate_if_active", reject_after_candidate)
    component = await run_wave0_work_units_real(
        _state(),
        controller=context.work_units,
        topic_registry=({"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},),
        clock=lambda: NOW,
    )

    attempt = next(iter(component.parent_update["attempts_by_id"].values()))
    assert len(capabilities.requests) == 1
    assert capabilities.requests[0].capability_ref is not None
    assert capabilities.requests[0].capability_ref.capability_id == "wave0-authoritative-source-intake"
    assert attempt["terminal_code"] == "validation_failed"
    assert attempt["failure_category"] == "submission_validation"
    assert "validation_codes" not in attempt
    assert "content_hash_mismatch" not in capabilities.requests[0].objective
    assert component.parent_update["accepted_submission_refs"] == ()
    assert await store.load_records() == ()


@pytest.mark.parametrize(
    ("result", "expected_category"),
    [
        pytest.param(
            NodeExecutionResult(
                finish_reason=NodeFinishReason.FAILED,
                problem=NodeProblem(
                    code=RunFailureCode.TOOL_EXECUTION_FAILED,
                    phase="wave0",
                    certainty=FailureCertainty.DIRECT,
                ),
            ),
            "tool_execution",
            id="tool",
        ),
        pytest.param(
            NodeExecutionResult(
                finish_reason=NodeFinishReason.FAILED,
                problem=NodeProblem(
                    code=RunFailureCode.OUTPUT_STRUCTURED_INVALID,
                    phase="wave0",
                    certainty=FailureCertainty.DIRECT,
                ),
            ),
            "structured_output",
            id="structured-output",
        ),
        pytest.param(RuntimeError("raw unknown worker failure"), "unknown", id="unknown"),
    ],
)
async def test_real_wave0_invocation_outcomes_use_closed_controller_categories(
    tmp_path,
    result: object,
    expected_category: str,
) -> None:
    """@impl WFO-001"""
    context, store = _context(tmp_path, _ResultCapabilities(result))
    assert context.work_units is not None

    component = await run_wave0_work_units_real(
        _state(),
        controller=context.work_units,
        topic_registry=({"topic_id": "storage", "title": "Storage", "scope": "Storage economics"},),
        clock=lambda: NOW,
    )

    attempt_id, attempt = next(iter(component.parent_update["attempts_by_id"].items()))
    failure = component.parent_update["terminal_failures_by_attempt_id"][attempt_id]
    assert component.parent_update["accepted_submission_refs"] == ()
    assert attempt["failure_category"] == expected_category
    assert attempt["provider_category"] is None
    assert failure["failure_category"] == expected_category
    assert failure["provider_category"] is None
    assert aggregate_worker_failure_category(
        component.parent_update["attempts_by_id"],
        work_id=attempt_id.rsplit("_a", 1)[0],
    ) is WorkerFailureAggregate(expected_category)
    assert "raw unknown worker failure" not in str(component.parent_update)
    assert await store.load_records() == ()


@pytest.mark.workflow
@pytest.mark.parametrize(
    "case",
    [pytest.param(PARTIAL_WORKER_SUCCESS_CASE, id=PARTIAL_WORKER_SUCCESS_CASE.case_id)],
)
async def test_partial_worker_success_projects_distinct_gate_outcomes_from_authoritative_state(tmp_path, case) -> None:
    context, store = _context(tmp_path)
    assert context.work_units is not None
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=FailOneWorkerResolver(context.work_units.resolver, work_ordinal=1),
    )

    component = await run_wave0_work_units(
        _state(),
        controller=controller,
        clock=lambda: NOW,
    )
    projected = _apply_result(_state(), component.parent_update)
    gate_state = {**projected, WORK_UNIT_GATE_VIEW_KEY: component.gate_view}
    gate_def = real_wave0_gate_def()

    repair = evaluate_gate(gate_state, "wave0", gate_def)
    after_repair = {**gate_state, **gate_result_to_state_update(repair, "wave0", gate_state)}
    second_repair = evaluate_gate(after_repair, "wave0", gate_def)
    after_second = {**after_repair, **gate_result_to_state_update(second_repair, "wave0", after_repair)}
    fatigue = evaluate_gate(after_second, "wave0", gate_def)
    exhausted = evaluate_gate(
        {**gate_state, "repair_budget_by_phase": {"wave0": 0}},
        "wave0",
        gate_def,
    )

    records = await store.load_records()
    accepted_work_ids = tuple(sorted(component.gate_view.accepted_record_by_work_id))
    failed_attempt_ids = tuple(failure.attempt_id for failure in component.gate_view.failure_summaries)
    artifact_hashes = tuple((output.path, output.content_hash) for record in records for output in record.output_refs)
    outcomes = tuple(
        WorkGateOutcome(
            route=result.route,
            failure_codes=tuple(failure.code.value for failure in result.failures),
        )
        for result in (repair, fatigue, exhausted)
    )
    observation = ScenarioObservation(
        checkpoint=CheckpointFacts(route=fatigue.route, terminal="blocked", identity_isolated=True, attempt_count=3),
        ledger=LedgerFacts(
            accepted_refs=tuple(record.record_hash for record in records),
            conflict_detected=False,
            replay_idempotent=True,
        ),
        sandbox=SandboxFacts(
            paths_contained=all(path.startswith(f"{run_bundle_root(BUNDLE)}/") for path, _ in artifact_hashes),
            artifact_hashes=artifact_hashes,
            citation_bindings=(),
        ),
        work_state=WorkStateFacts(
            accepted_work_ids=accepted_work_ids,
            failed_attempt_ids=failed_attempt_ids,
            gate_outcomes=outcomes,
        ),
    )

    assert len(component.gate_view.planned_work_ids) == 3
    assert len(accepted_work_ids) == len(records) == 2
    assert len(failed_attempt_ids) == 1
    assert repair.route == second_repair.route == "repair"
    assert fatigue.route == exhausted.route == "exhausted"
    assert_scenario(PARTIAL_WORKER_SUCCESS_FAMILY, case, observation)


async def test_fault_before_submit_node_return_replays_ledger_ahead_of_parent_checkpoint(tmp_path) -> None:
    context, store = _context(tmp_path)
    assert context.work_units is not None

    def fault(point: str) -> None:
        if point == "before_submit_node_return":
            raise RuntimeError(point)

    with pytest.raises(RuntimeError, match="before_submit_node_return"):
        await run_wave0_work_units(
            _state(),
            controller=context.work_units,
            clock=lambda: NOW,
            fault_hook=fault,
        )
    assert len(await store.load_records()) == 3

    replay = await run_wave0_work_units(
        _state(),
        controller=context.work_units,
        clock=lambda: NOW,
    )
    assert len(replay.parent_update["accepted_submission_refs"]) == 3
    assert len(await store.load_records()) == 3


async def test_fault_after_returned_state_update_leaves_matching_checkpoint_and_ledger(tmp_path) -> None:
    context, store = _context(tmp_path)
    gate = build_fixture_gate_definitions(FixtureScenario())["wave0"]
    wrapped = _node_wrapper(
        "wave0",
        NODE_SPEC,
        NodeAdapter(factory=fixture_wave0_adapter.build_fixture, kind=AdapterKind.FIXTURE, requires_gate=True),
        {"wave0": gate},
    )
    returned = await wrapped(_state(), SimpleNamespace(context=context))

    class SimulatedCrash(RuntimeError):
        pass

    checkpoint = None
    with pytest.raises(SimulatedCrash):
        checkpoint = _apply_result(_state(), returned)
        raise SimulatedCrash("after_returned_state_update")
    assert checkpoint is not None
    records = await store.load_records()
    assert set(checkpoint["accepted_submission_refs"]) == {record.record_hash for record in records}


async def test_reconcile_matrix_catches_up_ledger_ahead_and_accepts_matching_checkpoint(tmp_path) -> None:
    context, store = _context(tmp_path)
    assert context.work_units is not None
    first = await run_wave0_work_units(
        _state(),
        controller=context.work_units,
        clock=lambda: NOW,
    )
    records = await reconcile_parent_ledger_authority(_state(), context.work_units)
    assert len(records) == 3

    checkpoint = _apply_result(_state(), first.parent_update)
    matching = await reconcile_parent_ledger_authority(checkpoint, context.work_units)
    assert tuple(record.record_hash for record in matching) == first.parent_update["accepted_submission_refs"]
    assert len(await store.load_records()) == 3


@pytest.mark.parametrize("checkpoint_ahead", ["accepted_ref", "submitted_status"])
async def test_reconcile_matrix_rejects_checkpoint_ahead_without_ledger_and_does_not_repair(
    tmp_path,
    checkpoint_ahead: str,
) -> None:
    context, store = _context(tmp_path)
    assert context.work_units is not None
    state = _state()
    if checkpoint_ahead == "accepted_ref":
        state["accepted_submission_refs"] = ("h_" + "Z" * 43,)
    else:
        state["work_status_by_id"] = {"g0_wave0_w0000_a00": "submitted"}
    before = dict(state)

    with pytest.raises(WorkUnitStoreError) as excinfo:
        await run_wave0_work_units(
            state,
            controller=context.work_units,
            clock=lambda: NOW,
        )
    assert excinfo.value.reason is WorkUnitStorageReason.LEDGER_CORRUPT
    assert state == before
    assert await store.load_records() == ()


@pytest.mark.parametrize("artifact_defect", ["missing", "mutated"])
async def test_reconcile_matrix_rejects_diverged_accepted_artifact_without_checkpoint_repair(
    tmp_path,
    artifact_defect: str,
) -> None:
    context, store = _context(tmp_path)
    assert context.work_units is not None
    first = await run_wave0_work_units(
        _state(),
        controller=context.work_units,
        clock=lambda: NOW,
    )
    checkpoint = _apply_result(_state(), first.parent_update)
    before = dict(checkpoint)
    record = (await store.load_records())[0]
    host_output = tmp_path / record.output_refs[0].path.removeprefix("workspace/")
    if artifact_defect == "missing":
        host_output.unlink()
    else:
        host_output.write_bytes(b"mutated")

    with pytest.raises(WorkUnitStoreError) as excinfo:
        await reconcile_parent_ledger_authority(checkpoint, context.work_units)
    assert excinfo.value.reason is WorkUnitStorageReason.ACCEPTED_ARTIFACT_DIVERGED
    assert checkpoint == before
    assert len(await store.load_records()) == 3


async def test_reconcile_matrix_maps_broken_ledger_to_typed_corruption_without_dispatch(tmp_path) -> None:
    context, store = _context(tmp_path)
    assert context.work_units is not None
    evidence = tmp_path / bundle_host_relative_root(BUNDLE) / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    ledger = evidence / "submissions.jsonl"
    ledger.write_bytes(b'{"broken":true}\n')
    ledger.chmod(0o600)

    with pytest.raises(WorkUnitStoreError) as excinfo:
        await run_wave0_work_units(
            _state(),
            controller=context.work_units,
            clock=lambda: NOW,
        )
    assert excinfo.value.reason is WorkUnitStorageReason.LEDGER_CORRUPT


async def test_reconcile_matrix_supersedes_active_retry_when_sibling_record_already_won(tmp_path) -> None:
    context, store = _context(tmp_path)
    assert context.work_units is not None
    first = await run_wave0_work_units(
        _state(),
        controller=context.work_units,
        clock=lambda: NOW,
    )
    state = _apply_result(_state(), first.parent_update)
    work_id = "g0_wave0_w0000"
    accepted_attempt = f"{work_id}_a00"
    retry_attempt = f"{work_id}_a01"
    state["accepted_submission_refs"] = ()
    state["attempts_by_id"] = {
        **state["attempts_by_id"],
        retry_attempt: {
            "created_at": NOW,
            "started_at": None,
            "expires_at": None,
            "terminal_at": None,
            "terminal_code": None,
        },
    }
    state["work_status_by_id"] = {
        **state["work_status_by_id"],
        retry_attempt: "pending",
    }
    state["active_attempt_by_work_id"] = {work_id: retry_attempt}
    state["pending_work_ids"] = (work_id,)
    state["next_attempt_ordinal_by_work_id"] = {
        **state["next_attempt_ordinal_by_work_id"],
        work_id: 2,
    }

    reconciled = await run_wave0_work_units(
        state,
        controller=context.work_units,
        clock=lambda: NOW,
    )
    record = next(record for record in await store.load_records() if record.work_id == work_id)
    assert reconciled.gate_view.planned_work_ids == (work_id,)
    assert reconciled.gate_view.terminal_attempt_by_work_id == {work_id: accepted_attempt}
    assert reconciled.parent_update["work_status_by_id"] == {retry_attempt: "cancelled"}
    assert reconciled.parent_update["attempts_by_id"][retry_attempt]["terminal_code"] == "superseded"
    assert reconciled.parent_update["active_attempt_by_work_id"] == {}
    assert reconciled.parent_update["accepted_submission_refs"] == (record.record_hash,)
    assert len(await store.load_records()) == 3


async def test_reconcile_matrix_executes_active_retry_and_copies_canonical_first_spec(tmp_path) -> None:
    context, store = _context(tmp_path)
    assert context.work_units is not None
    spec = materialize_work_spec(
        bundle_id=BUNDLE_ID,
        generation=0,
        phase="wave0",
        work_ordinal=0,
        intent=WAVE0_FIXTURE_INTENTS[0],
    )
    first_attempt = allocate_attempt(spec, attempt_ordinal=0, created_at=NOW)
    retry = allocate_attempt(spec, attempt_ordinal=1, created_at=NOW)
    await store.write_work_spec(spec, first_attempt)
    state = _state()
    state.update(
        pending_work_ids=(spec.work_id,),
        next_work_ordinal=1,
        next_attempt_ordinal_by_work_id={spec.work_id: 2},
        work_specs_by_id={
            spec.work_id: WorkSpecRef(worker_role=spec.worker_role, spec_hash=spec.spec_hash).model_dump(mode="json")
        },
        attempts_by_id={
            first_attempt.attempt_id: {
                "created_at": NOW,
                "started_at": NOW,
                "expires_at": None,
                "terminal_at": NOW,
                "terminal_code": "worker_failed",
            },
            retry.attempt_id: {
                "created_at": NOW,
                "started_at": None,
                "expires_at": None,
                "terminal_at": None,
                "terminal_code": None,
            },
        },
        work_status_by_id={first_attempt.attempt_id: "failed", retry.attempt_id: "pending"},
        active_attempt_by_work_id={spec.work_id: retry.attempt_id},
    )

    completed = await run_wave0_work_units(
        state,
        controller=context.work_units,
        clock=lambda: NOW,
    )
    assert completed.parent_update["work_status_by_id"] == {retry.attempt_id: "submitted"}
    first_ref = tmp_path / bundle_host_relative_root(BUNDLE) / "work" / spec.work_id
    first_ref = first_ref / first_attempt.attempt_id / "work-spec.json"
    retry_ref = first_ref.parent.parent / retry.attempt_id / "work-spec.json"
    assert first_ref.read_bytes() == retry_ref.read_bytes() == canonical_json_bytes(spec)
    assert len(await store.load_records()) == 1


async def test_recovery_fails_running_attempt_from_prior_generation_with_orphan_reason(tmp_path) -> None:
    """@impl RUO-003"""
    context, store = _context(tmp_path)
    assert context.work_units is not None
    stale_spec = materialize_work_spec(
        bundle_id=BUNDLE_ID,
        generation=0,
        phase="wave0",
        work_ordinal=0,
        intent=WAVE0_FIXTURE_INTENTS[0],
    )
    stale_attempt = transition_attempt(
        allocate_attempt(stale_spec, attempt_ordinal=0, created_at=NOW),
        status="running",
        at=NOW,
    )
    await store.write_work_spec(stale_spec, stale_attempt)
    state = _state()
    state.update(
        generation=1,
        work_specs_by_id={
            stale_spec.work_id: WorkSpecRef(
                worker_role=stale_spec.worker_role,
                spec_hash=stale_spec.spec_hash,
            ).model_dump(mode="json")
        },
        attempts_by_id={
            stale_attempt.attempt_id: {
                "created_at": NOW,
                "started_at": NOW,
                "expires_at": None,
                "terminal_at": None,
                "terminal_code": None,
            }
        },
        work_status_by_id={stale_attempt.attempt_id: "running"},
        active_attempt_by_work_id={stale_spec.work_id: stale_attempt.attempt_id},
    )

    recovered = await run_wave0_work_units(
        state,
        controller=context.work_units,
        clock=lambda: NOW,
    )

    assert recovered.parent_update["work_status_by_id"][stale_attempt.attempt_id] == "failed"
    assert recovered.parent_update["attempts_by_id"][stale_attempt.attempt_id]["terminal_code"] == "orphaned"
    assert recovered.parent_update["terminal_failures_by_attempt_id"][stale_attempt.attempt_id]["failure_code"] == (
        "work_failed"
    )
    assert recovered.parent_update["active_attempt_by_work_id"] == {}
    assert recovered.gate_view.planned_work_ids == tuple(f"g1_wave0_w{ordinal:04d}" for ordinal in range(3))
    assert len(await store.load_records()) == 3


@pytest.mark.parametrize(
    ("terminal_status", "terminal_code"),
    [("failed", "worker_failed"), ("timed_out", "deadline_exceeded")],
)
async def test_failed_or_timed_out_work_allocates_one_fresh_retry_through_shared_component(
    tmp_path,
    terminal_status: str,
    terminal_code: str,
) -> None:
    context, store = _context(tmp_path)
    assert context.work_units is not None
    spec = materialize_work_spec(
        bundle_id=BUNDLE_ID,
        generation=0,
        phase="wave0",
        work_ordinal=0,
        intent=WAVE0_FIXTURE_INTENTS[0],
    )
    failed = allocate_attempt(spec, attempt_ordinal=0, created_at=NOW)
    await store.write_work_spec(spec, failed)
    state = _state()
    state.update(
        next_work_ordinal=1,
        next_attempt_ordinal_by_work_id={spec.work_id: 1},
        work_specs_by_id={
            spec.work_id: WorkSpecRef(worker_role=spec.worker_role, spec_hash=spec.spec_hash).model_dump(mode="json")
        },
        attempts_by_id={
            failed.attempt_id: {
                "created_at": NOW,
                "started_at": NOW,
                "expires_at": None,
                "terminal_at": NOW,
                "terminal_code": terminal_code,
            }
        },
        work_status_by_id={failed.attempt_id: terminal_status},
    )

    completed = await run_wave0_work_units(
        state,
        controller=context.work_units,
        clock=lambda: NOW,
    )

    retry_id = f"{spec.work_id}_a01"
    assert completed.gate_view.planned_work_ids == (spec.work_id,)
    assert completed.parent_update["work_status_by_id"] == {retry_id: "submitted"}
    assert completed.parent_update["next_attempt_ordinal_by_work_id"] == {spec.work_id: 2}
    record = (await store.load_records())[0]
    assert record.attempt_id == retry_id
    first_ref = tmp_path / bundle_host_relative_root(BUNDLE) / "work" / spec.work_id
    first_ref = first_ref / failed.attempt_id / "work-spec.json"
    retry_ref = first_ref.parent.parent / retry_id / "work-spec.json"
    assert first_ref.read_bytes() == retry_ref.read_bytes() == canonical_json_bytes(spec)
