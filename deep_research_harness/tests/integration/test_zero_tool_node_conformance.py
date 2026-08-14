"""Zero-tool model-node and deterministic-node conformance.

@impl EVH-008
@impl FID-001..FID-005
@impl NAC-009
@impl NOA-013
@impl EVH-022
@impl RER-005
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from deerflow_deep_research_fixtures.graph.nodes.wave0 import adapter as fixture_wave0_adapter
from deerflow_deep_research_fixtures.work_units import FixtureResultDocument
from langgraph.graph import END, START, StateGraph

from deerflow_deep_research.agents.node_cognitive_control_program import render_node_cognitive_control_program
from deerflow_deep_research.agents.policies import ExecutionBudget, ExecutionPolicy
from deerflow_deep_research.domain.bundle import (
    BundleId,
    RunBundleRef,
    bundle_host_relative_root,
    bundle_readiness_report_plan_path,
    bundle_ref_to_virtual,
    run_bundle_root,
)
from deerflow_deep_research.domain.context import GraphContextView, SelectedBundleContext
from deerflow_deep_research.domain.invocation import GraphInvocationContext
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.profile import ResearchProfile, profile_state_fields
from deerflow_deep_research.domain.state import ContentRef, ResearchState
from deerflow_deep_research.domain.synthesis import SynthesisEvidence
from deerflow_deep_research.domain.work_units import (
    CandidateResult,
    OutputRef,
    canonical_json_bytes,
    compute_candidate_hash,
)
from deerflow_deep_research.engine.real_gates import build_final_delivery_real_gate_def
from deerflow_deep_research.engine.work_units.kernel import allocate_attempt, materialize_work_spec
from deerflow_deep_research.graph import builder as graph_builder
from deerflow_deep_research.graph.builder import _node_wrapper, _route
from deerflow_deep_research.graph.implementation_map import AdapterKind, NodeAdapter
from deerflow_deep_research.graph.nodes.final_delivery import NODE_SPEC as FINAL_SPEC
from deerflow_deep_research.graph.nodes.final_delivery import node as final_delivery_node
from deerflow_deep_research.graph.nodes.final_delivery.composer import build_final_delivery_request
from deerflow_deep_research.graph.nodes.hitl1 import node as hitl1_node
from deerflow_deep_research.graph.nodes.hitl2 import node as hitl2_node
from deerflow_deep_research.graph.nodes.readiness import NODE_SPEC as READINESS_SPEC
from deerflow_deep_research.graph.nodes.readiness.contracts import ReadinessReportPlan
from deerflow_deep_research.graph.nodes.rerun import NODE_SPEC as RERUN_SPEC
from deerflow_deep_research.graph.nodes.targeted_evidence import NODE_SPEC as TARGETED_SPEC
from deerflow_deep_research.graph.nodes.targeted_evidence import node as targeted_evidence_node
from deerflow_deep_research.graph.nodes.topic_planning import NODE_SPEC as TOPIC_SPEC
from deerflow_deep_research.graph.nodes.wave2_synthesis import NODE_SPEC as WAVE2_SPEC
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.node_agent_bridge import RuntimeNodeAgentBridge
from deerflow_deep_research.runtime.projection import project_node_agent, project_research_scope
from deerflow_deep_research.runtime.request_bundle import RequestBundleStore
from deerflow_deep_research.runtime.research import _final_delivery_node_agent_policy
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore
from tests.fixtures.fake_models import CapturingChatModel, ScriptedChatModel, ai_message
from tests.fixtures.runtime import local_runtime_envelope, unique_run_identity
from tests.scenarios.assertions import assert_scenario
from tests.scenarios.inputs import ScriptExecutionObservation, validate_script_observation
from tests.scenarios.observation import CheckpointFacts, LedgerFacts, SandboxFacts, ScenarioObservation
from tests.scenarios.replays import MALFORMED_OUTPUT_CASE, MALFORMED_OUTPUT_FAMILY


class _ForbiddenModelCapability:
    async def run_agent(self, *, context, request):
        raise AssertionError(f"deterministic node called model: {context.node_name}")


def _brief() -> str:
    return json.dumps(
        {
            "schema_version": 1,
            "brief_summary": "A bounded research brief.",
            "depth": "standard",
            "audience": "practitioner",
            "format": "detailed_report",
            "cost_tolerance": "moderate",
            "time_budget": "standard",
            "must_answer": ["Q1"],
            "scope_boundaries": "",
            "custom_notes": "",
        }
    )


def _topic_plan() -> str:
    return json.dumps(
        {
            "schema_version": 1,
            "topics": [
                {
                    "title": "Storage",
                    "scope": "Storage economics",
                    "must_answer_bindings": ["Q1"],
                    "search_dimensions": [],
                    "exclusions": [],
                }
            ],
        }
    )


def _synthesis() -> str:
    return json.dumps(
        {
            "schema_version": 1,
            "findings": [],
            "relations": [],
            "gaps": [],
            "summary": "No unsupported findings.",
        }
    )


def _bridge(tmp_path: Path, node_name: str, response: str):
    identity = unique_run_identity()
    envelope = local_runtime_envelope(tmp_path, identity=identity)
    bundle = identity.bundle_ref
    BundleLifecycle(workspace_host_path=envelope.workspace_host_path)._publish_sync(bundle)
    selected = SelectedBundleContext(bundle=bundle)
    graph = project_research_scope(envelope, bundle=bundle)
    workspace = graph.workspace_root
    policy = ExecutionPolicy(
        policy_name=f"{node_name.replace('_', '-')}-zero-tool",
        allowed_tool_names=frozenset(),
        read_roots=(workspace,),
        write_roots=(),
        attempt_root=workspace,
        budget=ExecutionBudget(2, 1, 1, 1, 8_192, 2_048, 1, 4_096, 5),
    )
    bridge = RuntimeNodeAgentBridge(
        envelope=envelope,
        policy=policy,
        model_resolver=lambda _envelope: ScriptedChatModel(responses=[ai_message(response)]),
        tools_resolver=lambda _envelope, _policy: (),
    )
    context = project_node_agent(
        graph,
        node_name=node_name,
        attempt_id=f"g0-{node_name}-a1".replace("_", "-"),
        policy_name=policy.policy_name,
        selected_bundle=selected,
    )
    return identity, selected, envelope, bridge, graph, context


@pytest.mark.workflow
async def test_hitl1_brief_generation_crosses_real_zero_tool_bridge(monkeypatch, tmp_path: Path) -> None:
    identity, selected, envelope, bridge, graph, context = _bridge(tmp_path, "hitl1", _brief())
    store = RequestBundleStore(workspace_host_path=envelope.workspace_host_path, bundle=selected.bundle)
    monkeypatch.setattr(hitl1_node, "interrupt", lambda _value: (_ for _ in ()).throw(RuntimeError("interrupt")))
    dependencies = NodeBuildDependencies(graph, context, bridge, request_bundle=store, selected_bundle=selected)
    state = {
        "bundle_id": identity.bundle_id,
        "start_message_id": "human-start",
        "request_text": "Compare storage options",
        "generation": 0,
        "execution_trace": (),
        "consumed_message_ids": (),
    }
    run = hitl1_node.build_real(dependencies)
    proposal = await run(state)
    assert proposal["route"] == "needs_followup"
    with pytest.raises(RuntimeError, match="interrupt"):
        await run(
            {
                **state,
                "proposed_profile": proposal["proposed_profile"],
                "execution_trace": ("hitl1",),
            }
        )
    assert bridge.agents_built == 1


@pytest.mark.workflow
async def test_topic_planning_crosses_real_zero_tool_bridge(tmp_path: Path) -> None:
    identity, selected, envelope, bridge, graph, context = _bridge(tmp_path, "topic_planning", _topic_plan())
    profile = ResearchProfile(
        schema_version=2,
        depth="standard",
        audience="practitioner",
        format="detailed_report",
        cost_tolerance="moderate",
        time_budget="standard",
        must_answer=("Q1",),
        request_language="en",
        output_language="en",
    )
    request_bundle = RequestBundleStore(workspace_host_path=envelope.workspace_host_path, bundle=selected.bundle)
    profile_ref = await request_bundle.write_profile(profile)
    baseline = await request_bundle.read_bundle_state()
    profile_fields = profile_state_fields(profile, profile_ref)
    await request_bundle.write_bundle_state(
        replace(baseline, **profile_fields),
        expected_revision=baseline.revision,
    )
    update = await TOPIC_SPEC.real_factory(
        NodeBuildDependencies(graph, context, bridge, request_bundle=request_bundle, selected_bundle=selected)
    )(
        {
            "bundle_id": identity.bundle_id,
            "request_text": "Compare storage options",
            "execution_trace": (),
            **profile_fields,
        }
    )
    assert update["route"] == "next"
    assert bridge.agents_built == 1


@pytest.mark.workflow
async def test_wave2_crosses_real_zero_tool_bridge(tmp_path: Path) -> None:
    identity, selected, envelope, bridge, graph, context = _bridge(tmp_path, "wave2_synthesis", _synthesis())
    store = WorkUnitStore(
        workspace_host_path=envelope.workspace_host_path,
        bundle=selected.bundle,
        clock=lambda: datetime(2026, 7, 17, tzinfo=UTC),
        monotonic=time.monotonic,
        lock_sleep=time.sleep,
        token_factory=lambda: "6" * 32,
        fault_hook=None,
    )
    update = await WAVE2_SPEC.real_factory(
        NodeBuildDependencies(graph, context, bridge, synthesis_bundle=store, selected_bundle=selected)
    )({"bundle_id": identity.bundle_id, "accepted_submission_refs": (), "execution_trace": ()})
    assert update["execution_trace"] == ("wave2_synthesis",)
    assert bridge.agents_built == 1
    assert (
        envelope.workspace_host_path / bundle_host_relative_root(selected.bundle) / "synthesis" / "findings.json"
    ).is_file()


@pytest.mark.workflow
async def test_targeted_critic_crosses_real_zero_tool_bridge_without_new_recovery(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    response = json.dumps(
        {
            "schema_version": 1,
            "sources": [
                {
                    "source_id": "source:assigned",
                    "trust_tier": "high",
                    "materiality": "primary",
                    "marketing_risk": False,
                    "cross_verification_need": False,
                }
            ],
            "source_ids": ["source:assigned"],
        }
    )
    identity, selected, _envelope, bridge, graph, context = _bridge(tmp_path, "targeted_evidence", response)
    materialized: list[tuple[str, tuple[str, ...]]] = []

    def capture_materialization(result, _attempt_id, _workspace, *, allowed_source_ids):
        materialized.append((result.source_ids[0], tuple(sorted(allowed_source_ids))))

    monkeypatch.setattr(targeted_evidence_node, "materialize_source_diagnostic", capture_materialization)
    update = await TARGETED_SPEC.real_factory(NodeBuildDependencies(graph, context, bridge, selected_bundle=selected))(
        {
            "bundle_id": identity.bundle_id,
            "execution_trace": (),
            "unresolved_gaps": (),
            "critic_work_items": (
                {
                    "type": "source_diagnostic",
                    "source_refs": ("source:assigned",),
                    "source_contents": ("untrusted source body",),
                },
            ),
        }
    )

    assert update["route"] == "next"
    assert bridge.agents_built == 1
    assert materialized == [("source:assigned", ("source:assigned",))]


@pytest.mark.workflow
async def test_readiness_critic_crosses_real_zero_tool_bridge_and_uses_ledger_projection(tmp_path: Path) -> None:
    evidence_ref = "h_" + "R" * 43
    response = json.dumps(
        {
            "schema_version": 1,
            "per_question": [
                {
                    "question": "Q1",
                    "verdict": "ready_substantive",
                    "backing_claim_ids": [evidence_ref],
                    "limitation_note": "",
                }
            ],
        }
    )
    identity, selected, _envelope, bridge, graph, context = _bridge(tmp_path, "readiness", response)

    class LedgerStore:
        bundle = selected.bundle

        async def read_synthesis_evidence(self, accepted_refs):
            assert accepted_refs == (evidence_ref,)
            return (
                SynthesisEvidence(
                    submission_ref=evidence_ref,
                    phase="wave1",
                    result_contract="wave1.evidence-extraction",
                    content="untrusted accepted evidence",
                ),
            )

        async def write_readiness_report_plan(self, plan):
            raw = canonical_json_bytes(plan.model_dump(mode="json"))
            digest = base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).decode("ascii").rstrip("=")
            return ContentRef(
                sandbox_path=bundle_readiness_report_plan_path(selected.bundle),
                content_hash=f"h_{digest}",
                short_summary="readiness-report-plan.json",
            )

    update = await READINESS_SPEC.real_factory(
        NodeBuildDependencies(
            graph,
            context,
            bridge,
            work_units=SimpleNamespace(store=LedgerStore()),
            selected_bundle=selected,
        )
    )(
        {
            "bundle_id": identity.bundle_id,
            "accepted_submission_refs": (evidence_ref,),
            "must_answer_questions": ("Q1",),
            "execution_trace": (),
        }
    )

    assert update["route"] == "pass"
    assert update["readiness_critic_summary"]["per_question"][0]["verdict"] == "ready_substantive"
    assert bridge.agents_built == 1
    assert bridge.policy.allowed_tool_names == frozenset()
    assert tuple(bridge.tools_resolver(_envelope, bridge.policy)) == ()


@pytest.mark.workflow
@pytest.mark.parametrize("case_id", [pytest.param("malformed-output", id="malformed-output")])
async def test_wave2_malformed_output_consumes_repair_and_leaves_no_partial_authority(
    tmp_path: Path,
    case_id: str,
) -> None:
    """@impl WSN-008"""

    identity, selected, envelope, bridge, graph, context = _bridge(tmp_path, "wave2_synthesis", "not-json")
    store = WorkUnitStore(
        workspace_host_path=envelope.workspace_host_path,
        bundle=selected.bundle,
        clock=lambda: datetime(2026, 7, 17, tzinfo=UTC),
        monotonic=time.monotonic,
        lock_sleep=time.sleep,
        token_factory=lambda: "7" * 32,
        fault_hook=None,
    )

    with pytest.raises(ValueError, match="synthesis_output_json_invalid"):
        await WAVE2_SPEC.real_factory(
            NodeBuildDependencies(graph, context, bridge, synthesis_bundle=store, selected_bundle=selected)
        )({"bundle_id": identity.bundle_id, "accepted_submission_refs": (), "execution_trace": ()})

    assert case_id == MALFORMED_OUTPUT_CASE.case_id
    assert bridge.agents_built == 2
    assert not (
        envelope.workspace_host_path / bundle_host_relative_root(selected.bundle) / "synthesis" / "findings.json"
    ).exists()
    validate_script_observation(
        MALFORMED_OUTPUT_CASE.inputs,
        MALFORMED_OUTPUT_CASE.bounds,
        ScriptExecutionObservation(model_calls=2, tool_calls=(), bound_tool_names=()),
    )
    assertion = assert_scenario(
        MALFORMED_OUTPUT_FAMILY,
        MALFORMED_OUTPUT_CASE,
        ScenarioObservation(
            checkpoint=CheckpointFacts(route=None, terminal=None, identity_isolated=True, attempt_count=1),
            ledger=LedgerFacts((), False, True),
            sandbox=SandboxFacts(True, (), ()),
            diagnostic_codes=("synthesis-output-json-invalid",),
            degradation="malformed-output",
        ),
    )
    assert assertion.case_id == "malformed-output"


def _deterministic_dependencies(node_name: str, *, publication_bundle=None) -> NodeBuildDependencies:
    bundle = RunBundleRef(bundle_id=BundleId("b_" + "D" * 43), scope_bucket="s_" + "D" * 43)
    selected = SelectedBundleContext(bundle=bundle)
    root = run_bundle_root(bundle)
    workspace = bundle_ref_to_virtual(root)
    graph = GraphContextView(
        research_scope_id=bundle.bundle_id.value,
        workspace_root=workspace,
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/{root}",
    )
    return NodeBuildDependencies(
        graph_context=graph,
        agent_context=project_node_agent(
            graph,
            node_name=node_name,
            attempt_id=f"g0-{node_name.replace('_', '-')}-a1",
            policy_name=f"{node_name.replace('_', '-')}-deterministic",
            selected_bundle=selected,
        ),
        capabilities=_ForbiddenModelCapability(),
        publication_bundle=publication_bundle,
        selected_bundle=selected,
    )


async def test_hitl2_is_deterministic_zero_tool_node() -> None:
    """@impl ALR-002"""
    dependencies = _deterministic_dependencies("hitl2")
    update = await hitl2_node.build_real(dependencies)(
        {
            "bundle_id": dependencies.graph_context.research_scope_id,
            "generation": 0,
            "start_message_id": "human-start",
            "accepted_submission_refs": ("h_" + "R" * 43,),
            "synthesis_gaps": (),
            "consumed_request_ids": (),
            "consumed_message_ids": (),
            "execution_trace": ("wave2_synthesis",),
        }
    )
    assert update["route"] == "proceed"


async def test_rerun_is_a_deterministic_zero_tool_node() -> None:
    dependencies = _deterministic_dependencies("rerun")
    rerun = await RERUN_SPEC.real_factory(dependencies)(
        {
            "bundle_id": dependencies.graph_context.research_scope_id,
            "generation": 0,
            "hitl2_rerun_payload": {"scope": "full", "reason": "re-evaluate"},
            "execution_trace": (),
        }
    )
    assert rerun["route"] == "topic_planning"


def _hash(content: bytes) -> str:
    digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).decode("ascii").rstrip("=")
    return f"h_{digest}"


class _ObservedChatModel(CapturingChatModel):
    events: list[str]

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.events.append("model")
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)


class _ObservedFinalStore:
    def __init__(self, delegate: WorkUnitStore, events: list[str]) -> None:
        self.delegate = delegate
        self.events = events
        self.published: tuple[bytes, bytes] | None = None

    async def read_readiness_report_plan(self, ref: ContentRef) -> bytes:
        self.events.append("plan-read")
        return await self.delegate.read_readiness_report_plan(ref)

    async def read_synthesis_evidence(self, accepted_refs: tuple[str, ...]) -> tuple[SynthesisEvidence, ...]:
        self.events.append("evidence-read")
        return await self.delegate.read_synthesis_evidence(accepted_refs)

    async def publish_final(self, report: bytes, citation_map: bytes) -> tuple[ContentRef, ContentRef]:
        self.events.append("publish")
        self.published = (report, citation_map)
        return await self.delegate.publish_final(report, citation_map)

    async def read_final_artifacts(self, refs: tuple[ContentRef, ContentRef]) -> tuple[bytes, bytes]:
        self.events.append("final-read")
        return await self.delegate.read_final_artifacts(refs)


class _FinalResolver:
    def __init__(
        self,
        graph: GraphContextView,
        bridge: RuntimeNodeAgentBridge,
        selected_bundle: SelectedBundleContext,
    ) -> None:
        self.graph = graph
        self.bridge = bridge
        self.selected_bundle = selected_bundle
        self.attempt_root: str | None = None

    def resolve(self, *, logical_name, attempt_id, policy) -> NodeBuildDependencies:
        assert logical_name == "final_delivery"
        assert policy == FINAL_SPEC.policy
        self.attempt_root = f"{self.graph.workspace_root}/attempts/{attempt_id}"
        return NodeBuildDependencies(
            graph_context=self.graph,
            agent_context=project_node_agent(
                self.graph,
                node_name=logical_name,
                attempt_id=attempt_id,
                policy_name=policy.name,
                selected_bundle=self.selected_bundle,
            ),
            capabilities=self.bridge,
            selected_bundle=self.selected_bundle,
        )


def _final_plan(accepted_ref: str) -> ReadinessReportPlan:
    return ReadinessReportPlan.model_validate(
        {
            "writable_conclusions": [
                {
                    "question": "What context should come first?",
                    "conclusion_text": "Approved context is retained verbatim.",
                    "backing_claim_ids": [accepted_ref],
                },
                {
                    "question": "What decision follows?",
                    "conclusion_text": "Approved decision is retained verbatim.",
                    "backing_claim_ids": [accepted_ref],
                },
            ],
            "mandatory_uncertainties": [
                {"question": "Which bound applies?", "limitation": "Approved bound is retained verbatim."},
                {"question": "What remains unknown?", "limitation": "Approved unknown is retained verbatim."},
            ],
        }
    )


async def _seed_final_evidence(store: WorkUnitStore) -> str:
    now = datetime(2026, 7, 30, tzinfo=UTC)
    spec = materialize_work_spec(
        bundle_id=store.bundle.bundle_id.value,
        generation=0,
        phase="wave0",
        work_ordinal=0,
        intent=fixture_wave0_adapter._INTENTS[0],
    )
    attempt = allocate_attempt(spec, attempt_ordinal=0, created_at=now)
    writer = store.attempt_artifact_writer(spec, attempt)
    assert len(spec.required_outputs) == 1
    output = b'{"accepted":"bounded final-composition evidence"}'
    await writer.write_output(spec.required_outputs[0], output)
    document = FixtureResultDocument(
        schema_version=1,
        bundle_id=spec.bundle_id,
        generation=spec.generation,
        phase=spec.phase,
        work_id=spec.work_id,
        attempt_id=attempt.attempt_id,
        worker_role=spec.worker_role,
        spec_hash=spec.spec_hash,
        result_contract=spec.result_contract,
        fixture_marker="non_research_fixture",
        output_paths=spec.required_outputs,
        source_ids=(),
    )
    result = canonical_json_bytes(document)
    await writer.write_result(document)
    root = f"{run_bundle_root(store.bundle)}/work/{spec.work_id}/{attempt.attempt_id}"
    payload = {
        "schema_version": 1,
        "bundle_id": store.bundle.bundle_id.value,
        "generation": 0,
        "phase": "wave0",
        "work_id": spec.work_id,
        "attempt_id": attempt.attempt_id,
        "worker_role": spec.worker_role,
        "spec_hash": spec.spec_hash,
        "result_contract": spec.result_contract,
        "result_ref": f"{root}/result.json",
        "result_hash": _hash(result),
        "result_schema_version": 1,
        "result_byte_count": len(result),
        "output_refs": (
            OutputRef(
                path=f"{root}/outputs/{spec.required_outputs[0]}",
                content_hash=_hash(output),
                schema_version=1,
                byte_count=len(output),
            ),
        ),
        "source_refs": (),
    }
    payload["candidate_hash"] = compute_candidate_hash(payload)
    committed = await store.commit_candidate(CandidateResult.model_validate(payload), scope=("final-composition",))
    return committed.record.record_hash


def _compile_final_delivery_graph():
    builder = StateGraph(ResearchState, context_schema=GraphInvocationContext)
    builder.add_node(
        "final_delivery",
        _node_wrapper(
            "final_delivery",
            FINAL_SPEC,
            NodeAdapter(factory=FINAL_SPEC.real_factory, kind=AdapterKind.REAL, requires_gate=True),
            {"final_delivery": build_final_delivery_real_gate_def()},
        ),
    )
    builder.add_edge(START, "final_delivery")
    builder.add_conditional_edges(
        "final_delivery",
        _route,
        {"pass": END, "repair": END, "evidence_blocked": END, "exhausted": END},
    )
    return builder.compile()


def _trace_final_delivery(monkeypatch: pytest.MonkeyPatch, events: list[str]) -> None:
    for name, event in (
        ("parse_layout_candidate", "parse"),
        ("admit_layout_candidate", "admit"),
        ("render_final_artifacts", "render"),
    ):
        original = getattr(final_delivery_node, name)

        def traced(*args, _event=event, _original=original, **kwargs):
            events.append(_event)
            return _original(*args, **kwargs)

        monkeypatch.setattr(final_delivery_node, name, traced)
    original_gate = graph_builder.evaluate_gate_for_node

    def traced_gate(*args, **kwargs):
        events.append("gate")
        return original_gate(*args, **kwargs)

    monkeypatch.setattr(graph_builder, "evaluate_gate_for_node", traced_gate)


async def _run_scripted_final_delivery(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    response: str,
):
    identity = unique_run_identity()
    envelope = local_runtime_envelope(tmp_path, identity=identity)
    bundle = identity.bundle_ref
    BundleLifecycle(workspace_host_path=envelope.workspace_host_path)._publish_sync(bundle)
    selected = SelectedBundleContext(bundle=bundle)
    graph = project_research_scope(envelope, bundle=bundle)
    store = WorkUnitStore(
        workspace_host_path=envelope.workspace_host_path,
        bundle=bundle,
        clock=lambda: datetime(2026, 7, 30, tzinfo=UTC),
        monotonic=time.monotonic,
        lock_sleep=time.sleep,
        token_factory=lambda: "c" * 32,
        fault_hook=None,
    )
    accepted_ref = await _seed_final_evidence(store)
    plan = _final_plan(accepted_ref)
    plan_ref = await store.write_readiness_report_plan(plan)
    evidence = await store.read_synthesis_evidence((accepted_ref,))
    events: list[str] = []
    model = _ObservedChatModel(reply=ai_message(response), seen=[], events=events)
    policy = _final_delivery_node_agent_policy(graph)

    def tools_must_remain_unresolved(_envelope, _policy):
        raise AssertionError("zero-tool final composition resolved tools")

    def resolve_model(_envelope):
        events.append("model")
        return model

    bridge = RuntimeNodeAgentBridge(
        envelope=envelope,
        policy=policy,
        model_resolver=resolve_model,
        tools_resolver=tools_must_remain_unresolved,
    )
    resolver = _FinalResolver(graph, bridge, selected)
    observed_store = _ObservedFinalStore(store, events)
    context = GraphInvocationContext(
        graph_context=graph,
        dependency_resolver=resolver,
        publication_bundle=observed_store,
        final_delivery_bundle=observed_store,
    )
    _trace_final_delivery(monkeypatch, events)
    result = await _compile_final_delivery_graph().ainvoke(
        {
            "schema_version": 2,
            "bundle_id": identity.bundle_id,
            "generation": 0,
            "accepted_submission_refs": (accepted_ref,),
            "readiness_report_plan": plan_ref,
            "execution_trace": (),
            "gate_attempts_by_phase": {},
            "repair_budget_by_phase": {},
        },
        context=context,
    )
    assert resolver.attempt_root is not None
    expected_prompt = render_node_cognitive_control_program(
        build_final_delivery_request(plan, evidence),
        attempt_workspace=resolver.attempt_root,
    )
    return result, events, model, expected_prompt, observed_store, policy, identity


@pytest.mark.workflow
async def test_final_delivery_scripted_real_bridge_composes_publishes_and_completes_through_gate(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    response = json.dumps(
        {
            "schema_version": 1,
            "conclusion_order": ["conclusion:1", "conclusion:0"],
            "uncertainty_order": ["uncertainty:1", "uncertainty:0"],
        }
    )

    result, events, model, expected_prompt, observed_store, policy, _identity = await _run_scripted_final_delivery(
        monkeypatch,
        tmp_path,
        response=response,
    )

    assert events == [
        "plan-read",
        "evidence-read",
        "model",
        "parse",
        "admit",
        "render",
        "publish",
        "final-read",
        "gate",
    ]
    assert model.seen == [[expected_prompt.system_policy, expected_prompt.user_message]]
    assert policy.policy_name == "final-delivery-composer"
    assert policy.allowed_tool_names == frozenset()
    assert policy.write_roots == ()
    assert policy.budget.max_model_calls == 1
    assert observed_store.published is not None
    report, citation_map = observed_store.published
    assert report.index(b"Approved decision is retained verbatim.") < report.index(
        b"Approved context is retained verbatim."
    )
    assert report.index(b"Approved unknown is retained verbatim.") < report.index(
        b"Approved bound is retained verbatim."
    )
    assert set(json.loads(citation_map)["claims"]) == {"conclusion:0", "conclusion:1"}
    assert result["route"] == "pass"
    assert result["terminal_status"] == "completed"
    assert result["phase_status"] == "terminal"
    assert result["gate_attempts_by_phase"]["final_delivery"] == 1


@pytest.mark.workflow
async def test_final_delivery_scripted_real_bridge_rejects_plan_violation_before_publication(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    response = json.dumps(
        {
            "schema_version": 1,
            "conclusion_order": ["conclusion:0"],
            "uncertainty_order": ["uncertainty:0", "uncertainty:1"],
        }
    )

    result, events, _model, _expected_prompt, observed_store, _policy, identity = await _run_scripted_final_delivery(
        monkeypatch,
        tmp_path,
        response=response,
    )

    assert events == ["plan-read", "evidence-read", "model", "parse", "admit", "gate"]
    assert observed_store.published is None
    assert result["route"] == "repair"
    assert "terminal_status" not in result
    assert not result.get("report_refs")
    assert not (tmp_path / bundle_host_relative_root(identity.bundle_ref) / "final").exists()
