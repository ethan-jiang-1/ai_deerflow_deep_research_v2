"""Deterministic contracts for the local cognitive evaluation suite.

@impl CES-001
@impl CES-002
@impl CES-003
@impl CES-004
@impl CES-005
@impl CES-006
@impl CES-007
@impl CES-009
@impl EVH-025
@impl EVH-026
@impl HIN-016
@impl EVH-027
@impl WAN-009
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib
import json
import time
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, bundle_host_relative_root, bundle_profile_path
from deerflow_deep_research.domain.context import (
    GraphContextView,
    NodeAgentBundleContext,
    NodeAgentContext,
    NodeExecutionResult,
    SelectedBundleContext,
)
from deerflow_deep_research.domain.enums import NodeFinishReason
from deerflow_deep_research.domain.invocation import WorkUnitControllerDependencies
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.profile import ResearchProfile, compute_profile_content_hash, profile_state_fields
from deerflow_deep_research.domain.state import ContentRef
from deerflow_deep_research.domain.synthesis import SynthesisEvidence, SynthesisResult
from deerflow_deep_research.graph.nodes.hitl1 import NODE_SPEC as HITL1_NODE_SPEC
from deerflow_deep_research.graph.nodes.topic_planning import NODE_SPEC as TOPIC_PLANNING_NODE_SPEC
from deerflow_deep_research.graph.nodes.wave0 import NODE_SPEC as WAVE0_NODE_SPEC
from deerflow_deep_research.graph.nodes.wave2_synthesis import NODE_SPEC as WAVE2_NODE_SPEC
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.evaluation import (
    BundleIntegrityError,
    CaseAdmissionError,
    CaseRegistry,
    CognitiveEvaluationRunner,
    ControlIdentity,
    EvaluationBundleManifest,
    EvaluationCase,
    EvaluationOperations,
    EvaluationReviewService,
    EvidenceLayer,
    ExecutionBounds,
    ExecutionStatus,
    ReviewRecord,
    ReviewResult,
    ReviewSubmission,
    SelectedLivePreflightError,
    SubjectExecution,
    load_case_registry,
    production_branch_subject,
    production_node_subject,
    production_scenario_node_subject,
    run_selected_live_case,
    run_selected_live_case_series,
)
from deerflow_deep_research.runtime.node_agent_bridge import RuntimeNodeAgentBridge
from deerflow_deep_research.runtime.projection import (
    RuntimeWorkUnitDependencyResolver,
    project_node_agent,
    project_research_scope,
)
from deerflow_deep_research.runtime.request_bundle import RequestBundleStore
from deerflow_deep_research.runtime.research import _wave2_synthesis_node_agent_policy
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore
from tests.fixtures.fake_models import ScriptedChatModel, ai_message
from tests.fixtures.runtime import local_runtime_envelope, unique_run_identity


def _case() -> EvaluationCase:
    return EvaluationCase(
        case_id="hitl1-brief",
        version="v1",
        subject="hitl1_brief",
        fixture={"question": "Compare two battery chemistries."},
        required_services=("model",),
        bounds=ExecutionBounds(timeout_seconds=60, max_model_calls=1, max_tool_calls=0),
        controls=(
            ControlIdentity(kind="case", version="v1", digest="a" * 64),
            ControlIdentity(kind="contract", version="v1", digest="b" * 64),
            ControlIdentity(kind="rubric", version="v1", digest="c" * 64),
            ControlIdentity(kind="protocol", version="v1", digest="d" * 64),
        ),
    )


async def _successful_subject(context: object) -> SubjectExecution:
    context.observe("bridge.started", {"model_id": "fake-model"})
    return SubjectExecution(
        output={"candidate": "bounded brief"},
        artifacts={"brief.json": {"candidate": "bounded brief"}},
        resource_use={"model_calls": 1, "tool_calls": 0},
    )


async def _failing_subject(context: object) -> SubjectExecution:
    context.observe("bridge.started", {"model_id": "fake-model"})
    raise TimeoutError("provider timed out")


@pytest.mark.asyncio
async def test_case_registry_and_runner_reject_unregistered_or_extra_execution_authority(tmp_path: Path) -> None:
    registry = CaseRegistry((_case(),))
    runner = CognitiveEvaluationRunner(
        registry=registry,
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": _successful_subject},
    )

    with pytest.raises(CaseAdmissionError, match="evaluation_case_unknown"):
        await runner.run(case_id="unknown", version="v1")
    with pytest.raises(CaseAdmissionError, match="evaluation_case_version_unknown"):
        await runner.run(case_id="hitl1-brief", version="v2")
    with pytest.raises(TypeError):
        await runner.run(case_id="hitl1-brief", version="v1", prompt="override")  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        await runner.run(case_id="hitl1-brief", version="v1", resume_from="prior-run")  # type: ignore[call-arg]


@pytest.mark.asyncio
async def test_each_runner_invocation_is_fresh_one_shot_and_never_starts_review(tmp_path: Path) -> None:
    registry = CaseRegistry((_case(),))
    seen_workspaces: list[Path] = []

    async def subject(context: object) -> SubjectExecution:
        seen_workspaces.append(context.workspace)
        return await _successful_subject(context)

    runner = CognitiveEvaluationRunner(
        registry=registry,
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": subject},
    )

    first = await runner.run(case_id="hitl1-brief", version="v1")
    second = await runner.run(case_id="hitl1-brief", version="v1")

    assert first.status is ExecutionStatus.COMPLETED
    assert second.status is ExecutionStatus.COMPLETED
    assert first.execution_id != second.execution_id
    assert first.bundle_path != second.bundle_path
    assert seen_workspaces[0] != seen_workspaces[1]
    assert not (first.bundle_path.parent / "reviews").exists()


@pytest.mark.asyncio
async def test_concurrent_invocations_and_preflight_failure_have_separate_failed_or_completed_bundles(
    tmp_path: Path,
) -> None:
    registry = CaseRegistry((_case(),))
    runner = CognitiveEvaluationRunner(
        registry=registry,
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": _successful_subject},
    )
    first, second = await asyncio.gather(
        runner.run(case_id="hitl1-brief", version="v1"),
        runner.run(case_id="hitl1-brief", version="v1"),
    )
    assert first.bundle_path.parent != second.bundle_path.parent

    unavailable = CognitiveEvaluationRunner(
        registry=registry,
        runs_root=tmp_path / "evals" / "unavailable-runs",
        subjects={"hitl1_brief": _successful_subject},
        available_services=frozenset(),
    )
    failed = await unavailable.run(case_id="hitl1-brief", version="v1")
    manifest = json.loads((failed.bundle_path / "manifest.json").read_text(encoding="utf-8"))
    assert failed.status is ExecutionStatus.FAILED
    assert manifest["failure"] == {"code": "preflight_service_unavailable", "phase": "preflight"}


@pytest.mark.asyncio
async def test_failed_execution_retains_partial_observations_without_a_hidden_retry(tmp_path: Path) -> None:
    calls = 0

    async def subject(context: object) -> SubjectExecution:
        nonlocal calls
        calls += 1
        return await _failing_subject(context)

    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((_case(),)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": subject},
    )

    result = await runner.run(case_id="hitl1-brief", version="v1")

    assert result.status is ExecutionStatus.FAILED
    assert calls == 1
    observations = json.loads((result.bundle_path / "observations.json").read_text(encoding="utf-8"))
    assert any(observation["kind"] == "bridge.started" for observation in observations)
    manifest = json.loads((result.bundle_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["failure"]["code"] == "execution_timeout"


@pytest.mark.asyncio
async def test_malformed_subject_result_is_failed_once_and_cannot_be_reviewed(tmp_path: Path) -> None:
    async def malformed_subject(context: object) -> SubjectExecution:
        context.observe("bridge.started", {"model_id": "fake-model"})
        return object()  # type: ignore[return-value]

    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((_case(),)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": malformed_subject},
    )
    execution = await runner.run(case_id="hitl1-brief", version="v1")
    review = EvaluationReviewService(registry=runner.registry, runs_root=runner.runs_root)
    submission = ReviewSubmission(
        bundle_path=execution.bundle_path,
        evaluator="codex",
        result=ReviewResult.INCONCLUSIVE,
        evidence=("the execution did not produce an assessable candidate",),
        confidence="high",
        unknowns=("candidate missing",),
        owning_seam="runtime.evaluation",
        follow_up="repair the execution seam",
        controls=_case().controls,
    )

    assert execution.status is ExecutionStatus.FAILED
    with pytest.raises(BundleIntegrityError, match="bundle_execution_not_reviewable"):
        await review.submit(submission)


@pytest.mark.asyncio
async def test_review_verifies_bundle_and_control_identity_without_rerunning_execution(tmp_path: Path) -> None:
    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((_case(),)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": _successful_subject},
    )
    execution = await runner.run(case_id="hitl1-brief", version="v1")
    review = EvaluationReviewService(registry=runner.registry, runs_root=runner.runs_root)
    submission = ReviewSubmission(
        bundle_path=execution.bundle_path,
        evaluator="codex",
        result=ReviewResult.PASS,
        evidence=("candidate satisfies the fixed rubric",),
        confidence="high",
        unknowns=(),
        owning_seam="graph.nodes.hitl1",
        follow_up="none",
        controls=_case().controls,
    )

    record = await review.submit(submission)

    assert record.result is ReviewResult.PASS
    assert record.path.parents[2] == execution.bundle_path.parent
    assert execution.status is ExecutionStatus.COMPLETED

    altered = list(_case().controls)
    altered[2] = ControlIdentity(kind="rubric", version="v2", digest="e" * 64)
    with pytest.raises(BundleIntegrityError, match="bundle_control_identity_mismatch"):
        await review.submit(submission.model_copy(update={"controls": tuple(altered)}))

    (execution.bundle_path / "output.json").write_text("{}", encoding="utf-8")
    with pytest.raises(BundleIntegrityError, match="bundle_digest_mismatch"):
        await review.submit(submission)


@pytest.mark.asyncio
async def test_cognitive_corpus_requires_declared_telemetry_and_retains_runtime_control_plan(tmp_path: Path) -> None:
    case = load_case_registry().resolve(case_id="public-controller-direction-loop", version="v1")
    assert case.execution_plan is not None

    async def missing_telemetry(_context: object) -> SubjectExecution:
        return SubjectExecution(output={"selection": "start"}, resource_use={"model_calls": 1, "tool_calls": 2})

    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((case,)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"public_controller": missing_telemetry},
    )
    failed = await runner.run(case_id=case.case_id, version=case.version)
    failed_manifest = json.loads((failed.bundle_path / "manifest.json").read_text(encoding="utf-8"))
    assert failed.status is ExecutionStatus.FAILED
    assert failed_manifest["failure"] == {"code": "execution_evidence_invalid", "phase": "subject"}

    async def measured(_context: object) -> SubjectExecution:
        return SubjectExecution(
            output={"selection": "start"},
            resource_use={
                "model_calls": 1,
                "tool_calls": 2,
                "provider": "fixture-provider",
                "model": "fixture-model",
                "composed_prompt_digest": "d" * 64,
                **{control.name: control.digest for control in case.execution_plan.runtime_controls},
                "input_tokens": 120,
                "output_tokens": 40,
                "cost_usd": 0.01,
            },
        )

    completed_runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((case,)),
        runs_root=tmp_path / "evals" / "completed-runs",
        subjects={"public_controller": measured},
    )
    completed = await completed_runner.run(case_id=case.case_id, version=case.version)
    assert completed.status is ExecutionStatus.COMPLETED
    inputs = json.loads((completed.bundle_path / "inputs.json").read_text(encoding="utf-8"))
    resources = json.loads((completed.bundle_path / "resources.json").read_text(encoding="utf-8"))
    assert inputs["execution_plan"]["repeat_count"] == 3
    assert inputs["execution_plan"]["runtime_controls"] == [
        control.model_dump(mode="json") for control in case.execution_plan.runtime_controls
    ]
    assert resources["latency_ms"] >= 0
    assert resources["skill_digest"] == case.execution_plan.runtime_controls[0].digest


@pytest.mark.asyncio
async def test_topic_planning_corpus_reuses_the_registered_production_node_subject(tmp_path: Path) -> None:
    case = load_case_registry().resolve(case_id="topic-planning-direction-loop", version="v1")
    canonical = next(
        scenario for scenario in case.topic_planning_fixture.scenarios if scenario.case_kind == "canonical_notes"
    )
    bundle = RunBundleRef(bundle_id=BundleId("b_" + "E" * 43), scope_bucket="s_" + "F" * 43)
    profile = ResearchProfile(
        schema_version=2,
        depth="deep_dive",
        audience="practitioner",
        format="detailed_report",
        cost_tolerance="moderate",
        time_budget="standard",
        must_answer=("Q1",),
        scope_boundaries=canonical.scope_boundaries,
        custom_notes=canonical.custom_notes,
        comparison_required=False,
        comparison_subjects=None,
        request_language="en",
        output_language="en",
    )
    profile_ref = ContentRef(
        sandbox_path=bundle_profile_path(bundle),
        content_hash=compute_profile_content_hash(profile),
        schema_version=1,
        short_summary="evaluation canonical profile",
    )

    class ProfileReader:
        async def read_profile(self, received_ref: ContentRef) -> ResearchProfile:
            assert received_ref == profile_ref
            return profile

    class Capabilities:
        def __init__(self) -> None:
            self.requests: list[object] = []

        async def run_agent(self, *, context: object, request: object) -> NodeExecutionResult:  # noqa: ARG002
            self.requests.append(request)
            return NodeExecutionResult(
                finish_reason=NodeFinishReason.SUCCESS,
                summary=json.dumps(
                    {
                        "schema_version": 1,
                        "topics": [
                            {
                                "title": "Storage procurement evidence",
                                "scope": "Grid-connected stationary storage procurement evidence.",
                                "must_answer_bindings": ["Q1"],
                                "search_dimensions": [],
                                "exclusions": [],
                            }
                        ],
                    }
                ),
            )

    graph = GraphContextView(
        research_scope_id=bundle.bundle_id.value,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{bundle.bundle_id.value}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{bundle.bundle_id.value}",
    )
    selected_bundle = SelectedBundleContext(bundle=bundle)
    capabilities = Capabilities()
    dependencies = NodeBuildDependencies(
        graph_context=graph,
        agent_context=NodeAgentContext(
            research_scope_id=graph.research_scope_id,
            node_name="topic_planning",
            attempt_id="evaluation-topic-planning-a1",
            workspace_root=graph.workspace_root,
            attempt_root=f"{graph.workspace_root}/topic_planning",
            policy_name="topic-planning",
            bundle_context=NodeAgentBundleContext.from_selected_bundle(selected_bundle),
        ),
        capabilities=capabilities,  # type: ignore[arg-type]
        request_bundle=ProfileReader(),
        selected_bundle=selected_bundle,
    )
    assert case.execution_plan is not None
    subject = production_node_subject(
        subject=case.subject,
        node_spec=TOPIC_PLANNING_NODE_SPEC,
        dependencies=dependencies,
        state_factory=lambda fixture, _context: {
            "schema_version": 2,
            "bundle_id": bundle.bundle_id.value,
            "outer_thread_id": "evaluation-topic-thread",
            "start_message_id": "evaluation-topic-start",
            "request_digest": "d_" + "A" * 43,
            "request_text": fixture["scenarios"][0]["request_text"],
            "phase": "topic_planning",
            "generation": 0,
            "execution_trace": (),
            **profile_state_fields(profile, profile_ref),
        },
        resource_use_factory=lambda _context, _update: {
            "model_calls": 1,
            "tool_calls": 0,
            "provider": "fixture-provider",
            "model": "fixture-model",
            "composed_prompt_digest": "f" * 64,
            **{control.name: control.digest for control in case.execution_plan.runtime_controls},
            "input_tokens": 140,
            "output_tokens": 45,
            "cost_usd": 0.01,
        },
    )
    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((case,)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={case.subject: subject},
    )

    execution = await runner.run(case_id=case.case_id, version=case.version)

    assert execution.status is ExecutionStatus.COMPLETED
    assert len(capabilities.requests) == 1
    request = capabilities.requests[0]
    assert request.tools_enabled is False
    assert request.capability_ref is not None
    assert request.capability_ref.capability_id == "topic-planning-profile-decomposition"
    assert canonical.scope_boundaries in request.objective
    assert canonical.custom_notes in request.objective
    output = json.loads((execution.bundle_path / "output.json").read_text(encoding="utf-8"))
    assert output["state_update"]["route"] == "next"


@pytest.mark.asyncio
async def test_cancellation_preserves_prior_observations_and_does_not_resume(tmp_path: Path) -> None:
    started = asyncio.Event()
    calls = 0

    async def cancellable_subject(context: object) -> SubjectExecution:
        nonlocal calls
        calls += 1
        context.observe("bridge.started", {"model_id": "fake-model"})
        started.set()
        await asyncio.Event().wait()
        raise AssertionError("cancelled subject continued")

    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((_case(),)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": cancellable_subject},
    )
    task = asyncio.create_task(runner.run(case_id="hitl1-brief", version="v1"))
    await started.wait()
    task.cancel()
    execution = await task

    assert execution.status is ExecutionStatus.FAILED
    assert calls == 1
    manifest = json.loads((execution.bundle_path / "manifest.json").read_text(encoding="utf-8"))
    observations = json.loads((execution.bundle_path / "observations.json").read_text(encoding="utf-8"))
    assert manifest["failure"] == {"code": "execution_cancelled", "phase": "subject"}
    assert [event["kind"] for event in observations][-1] == "subject.cancelled"


@pytest.mark.asyncio
async def test_resource_limits_and_artifact_paths_fail_closed_with_retained_trace(tmp_path: Path) -> None:
    async def excessive_subject(context: object) -> SubjectExecution:
        context.observe("tool.called", {"tool": "web_search"})
        return SubjectExecution(output={}, resource_use={"model_calls": 2, "tool_calls": 0})

    with pytest.raises(ValueError, match="evaluation_artifact_path_invalid"):
        SubjectExecution(output={}, artifacts={"../outside.json": {}})

    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((_case(),)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": excessive_subject},
    )
    execution = await runner.run(case_id="hitl1-brief", version="v1")
    manifest = json.loads((execution.bundle_path / "manifest.json").read_text(encoding="utf-8"))

    assert execution.status is ExecutionStatus.FAILED
    assert manifest["failure"]["code"] == "execution_resource_bound_exceeded"
    observations = json.loads((execution.bundle_path / "observations.json").read_text(encoding="utf-8"))
    assert observations[1]["kind"] == "subject.started"


@pytest.mark.asyncio
async def test_opaque_runtime_objects_are_not_silently_serialized_as_bundle_evidence(tmp_path: Path) -> None:
    async def opaque_subject(context: object) -> SubjectExecution:
        context.observe("bridge.returned", {})
        return SubjectExecution(output={"opaque": object()})

    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((_case(),)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": opaque_subject},
    )

    with pytest.raises(TypeError, match="evaluation_evidence_not_serializable"):
        await runner.run(case_id="hitl1-brief", version="v1")


@pytest.mark.asyncio
async def test_atomic_bundle_and_multiple_separate_review_records_are_immutable(tmp_path: Path) -> None:
    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((_case(),)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": _successful_subject},
    )
    execution = await runner.run(case_id="hitl1-brief", version="v1")
    assert not list(execution.bundle_path.parent.glob(".bundle-staging*"))
    assert (execution.bundle_path / "manifest.json").is_file()

    review = EvaluationReviewService(registry=runner.registry, runs_root=runner.runs_root)
    base = ReviewSubmission(
        bundle_path=execution.bundle_path,
        evaluator="reviewer-a",
        result=ReviewResult.LIMITED,
        evidence=("bounded evidence",),
        confidence="medium",
        unknowns=("provider distribution",),
        variance=("repeat action selection was stable",),
        owning_seam="graph.nodes.hitl1",
        follow_up="add a scenario",
        controls=_case().controls,
    )
    first = await review.submit(base)
    second = await review.submit(
        base.model_copy(update={"evaluator": "reviewer-b", "result": ReviewResult.INCONCLUSIVE})
    )

    assert first.path != second.path
    payload = json.loads(first.path.read_text(encoding="utf-8"))
    assert payload["case_id"] == "hitl1-brief"
    assert payload["reviewed_at"]
    assert payload["controls"] == [control.model_dump(mode="json") for control in _case().controls]
    assert payload["variance"] == ["repeat action selection was stable"]
    assert first.evidence == ("bounded evidence",)
    assert first.variance == ("repeat action selection was stable",)
    assert first.owning_seam == "graph.nodes.hitl1"
    assert not (execution.bundle_path / "reviews").exists()


@pytest.mark.asyncio
@pytest.mark.parametrize("result", list(ReviewResult))
async def test_review_accepts_only_explicit_four_state_results(tmp_path: Path, result: ReviewResult) -> None:
    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((_case(),)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": _successful_subject},
    )
    execution = await runner.run(case_id="hitl1-brief", version="v1")
    review = EvaluationReviewService(registry=runner.registry, runs_root=runner.runs_root)
    record = await review.submit(
        ReviewSubmission(
            bundle_path=execution.bundle_path,
            evaluator="human-controlled-interface",
            result=result,
            evidence=("retained observation",),
            confidence="low",
            unknowns=(),
            owning_seam="runtime.evaluation",
            follow_up="inspect manually",
            controls=_case().controls,
        )
    )
    assert record.result is result


@pytest.mark.asyncio
async def test_operator_handoff_is_explicit_and_returns_bounded_references(tmp_path: Path) -> None:
    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((_case(),)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": _successful_subject},
    )
    operations = EvaluationOperations(
        runner=runner,
        review=EvaluationReviewService(registry=runner.registry, runs_root=runner.runs_root),
    )

    rejected = await operations.run(case_id="not-registered", version="v1")
    completed = await operations.run(case_id="hitl1-brief", version="v1")

    assert rejected.reference is None
    assert rejected.diagnostic == "evaluation_case_unknown"
    assert completed.status == "completed"
    assert completed.reference is not None


@pytest.mark.asyncio
async def test_v1_subject_adapter_invokes_the_supplied_production_branch_once(tmp_path: Path) -> None:
    calls: list[dict[str, object]] = []

    async def production_branch(state: dict[str, object]) -> dict[str, object]:
        calls.append(state)
        return {"node_visits": {"hitl1": 1}, "route": "needs_followup"}

    subject = production_branch_subject(
        subject="hitl1_brief",
        branch=production_branch,
        state_factory=lambda fixture, _context: {"request_text": fixture["question"]},
    )
    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((_case(),)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": subject},
    )
    execution = await runner.run(case_id="hitl1-brief", version="v1")

    assert execution.status is ExecutionStatus.COMPLETED
    assert calls == [{"request_text": "Compare two battery chemistries."}]
    output = json.loads((execution.bundle_path / "output.json").read_text(encoding="utf-8"))
    assert output["state_update"]["route"] == "needs_followup"


@pytest.mark.asyncio
async def test_hitl1_case_uses_the_real_node_factory_bridge_and_parser_with_fake_capability(tmp_path: Path) -> None:
    class Capabilities:
        async def run_agent(self, *, context: object, request: object) -> NodeExecutionResult:  # noqa: ARG002
            return NodeExecutionResult(
                finish_reason=NodeFinishReason.SUCCESS,
                summary=json.dumps(
                    {
                        "schema_version": 1,
                        "brief_summary": "A bounded intake brief.",
                        "depth": "standard",
                        "audience": "practitioner",
                        "format": "detailed_report",
                        "cost_tolerance": "moderate",
                        "time_budget": "standard",
                        "must_answer": ["Q1"],
                        "scope_boundaries": "Only the requested comparison.",
                        "custom_notes": "",
                    }
                ),
            )

    identity = unique_run_identity()
    envelope = local_runtime_envelope(tmp_path, identity=identity)
    bundle = identity.bundle_ref
    BundleLifecycle(workspace_host_path=envelope.workspace_host_path)._publish_sync(bundle)
    graph = project_research_scope(envelope, bundle=bundle)
    selected_bundle = SelectedBundleContext(bundle=bundle)

    async def ready(*_args: object, **_kwargs: object):
        from deerflow_deep_research.runtime.work_unit_storage import WorkUnitStorageCheck

        return WorkUnitStorageCheck("ready", "local_thread_mount")

    request_bundle = await RequestBundleStore.create(envelope, bundle=bundle, storage_verifier=ready)
    dependencies = NodeBuildDependencies(
        graph_context=graph,
        agent_context=NodeAgentContext(
            research_scope_id=graph.research_scope_id,
            node_name="hitl1",
            attempt_id="evaluation-hitl1-a1",
            workspace_root=graph.workspace_root,
            attempt_root=graph.workspace_root,
            policy_name="hitl1-profile",
            bundle_context=NodeAgentBundleContext.from_selected_bundle(selected_bundle),
        ),
        capabilities=Capabilities(),  # type: ignore[arg-type]
        request_bundle=request_bundle,
        selected_bundle=selected_bundle,
    )
    subject = production_node_subject(
        subject="hitl1_brief",
        node_spec=HITL1_NODE_SPEC,
        dependencies=dependencies,
        state_factory=lambda fixture, _context: {
            "schema_version": 2,
            "bundle_id": graph.research_scope_id,
            "outer_thread_id": identity.thread_id,
            "start_message_id": "evaluation-start",
            "request_digest": "d_" + "B" * 43,
            "request_text": fixture["question"],
            "phase": "hitl1",
            "generation": 0,
            "consumed_request_ids": (),
            "consumed_message_ids": (),
            "execution_trace": (),
        },
    )
    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((_case(),)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": subject},
    )

    execution = await runner.run(case_id="hitl1-brief", version="v1")

    assert execution.status is ExecutionStatus.COMPLETED
    output = json.loads((execution.bundle_path / "output.json").read_text(encoding="utf-8"))
    assert output["state_update"]["route"] == "needs_followup"


@pytest.mark.asyncio
async def test_wave0_case_uses_the_real_worker_bridge_policy_and_controller_with_fake_capability(
    tmp_path: Path,
) -> None:
    identity = unique_run_identity()
    envelope = local_runtime_envelope(tmp_path, identity=identity)
    bundle = identity.bundle_ref
    BundleLifecycle(workspace_host_path=envelope.workspace_host_path)._publish_sync(bundle)
    graph = project_research_scope(envelope, bundle=bundle)
    selected_bundle = SelectedBundleContext(bundle=bundle)
    bundle_id = bundle.bundle_id.value

    class Capabilities:
        def __init__(self) -> None:
            self.requests: list[object] = []

        async def run_agent(self, *, context: object, request: object) -> NodeExecutionResult:  # noqa: ARG002
            self.requests.append(request)
            return NodeExecutionResult(
                finish_reason=NodeFinishReason.SUCCESS,
                summary=(
                    '{"schema_version":1,"sources":[{"source_id":"source:storage","canonical_url":'
                    '"https://example.com/storage","title":"Storage","fetch_status":"fetched"}],'
                    '"baseline_facts":["storage is bounded"],"limitations":""}'
                ),
            )

    capabilities = Capabilities()

    class BaseResolver:
        def resolve(self, *, logical_name: str, attempt_id: str, policy: object) -> NodeBuildDependencies:
            return NodeBuildDependencies(
                graph_context=graph,
                agent_context=NodeAgentContext(
                    research_scope_id=bundle_id,
                    node_name=logical_name,
                    attempt_id=attempt_id,
                    workspace_root=graph.workspace_root,
                    attempt_root=f"{graph.workspace_root}/attempts/{attempt_id}",
                    policy_name=policy.name,
                    bundle_context=NodeAgentBundleContext.from_selected_bundle(selected_bundle),
                ),
                capabilities=capabilities,  # type: ignore[arg-type]
                selected_bundle=selected_bundle,
            )

    store = WorkUnitStore(
        workspace_host_path=envelope.workspace_host_path,
        bundle=bundle,
        clock=lambda: datetime.now(UTC),
        monotonic=time.monotonic,
        lock_sleep=time.sleep,
        token_factory=lambda: "0" * 32,
        fault_hook=None,
    )
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=RuntimeWorkUnitDependencyResolver(graph, BaseResolver(), store),
    )
    subject = production_node_subject(
        subject="wave0_worker",
        node_spec=WAVE0_NODE_SPEC,
        dependencies=NodeBuildDependencies(
            graph_context=graph,
            agent_context=NodeAgentContext(
                research_scope_id=bundle_id,
                node_name="wave0",
                attempt_id="evaluation-wave0-a1",
                workspace_root=graph.workspace_root,
                attempt_root=graph.workspace_root,
                policy_name="real-wave0",
                bundle_context=NodeAgentBundleContext.from_selected_bundle(selected_bundle),
            ),
            capabilities=capabilities,  # type: ignore[arg-type]
            work_units=controller,
            selected_bundle=selected_bundle,
        ),
        state_factory=lambda fixture, _context: {
            "bundle_id": bundle_id,
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
            "topic_registry": ({"topic_id": fixture["topic_id"], "title": "Storage", "scope": "Storage"},),
        },
    )
    wave0_case = EvaluationCase(
        case_id="wave0-worker",
        version="v1",
        subject="wave0_worker",
        fixture={"topic_id": "topic:storage"},
        required_services=("model", "web"),
        bounds=ExecutionBounds(timeout_seconds=60, max_model_calls=1, max_tool_calls=3),
        controls=_case().controls,
    )
    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((wave0_case,)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"wave0_worker": subject},
    )

    execution = await runner.run(case_id="wave0-worker", version="v1")

    assert execution.status is ExecutionStatus.COMPLETED
    assert capabilities.requests[0].tools_enabled is True
    assert capabilities.requests[0].minimum_tool_calls == 1
    output = json.loads((execution.bundle_path / "output.json").read_text(encoding="utf-8"))
    assert output["state_update"]["accepted_submission_refs"]


def test_source_controlled_v1_registry_exposes_only_the_declared_cases() -> None:
    registry = load_case_registry()

    assert registry.resolve(case_id="hitl1-brief", version="v1").subject == "hitl1_brief"
    wave0 = registry.resolve(case_id="wave0-worker", version="v1")
    assert wave0.subject == "wave0_worker"
    assert wave0.required_services == ("model", "web")

    controller = registry.resolve(case_id="public-controller-direction-loop", version="v1")
    assert controller.subject == "public_controller"
    assert controller.execution_plan is not None
    assert controller.execution_plan.repeat_count == 3
    assert {scenario.scenario_id for scenario in controller.controller_fixture.scenarios} >= {
        "profile-note-non-mutation",
        "terminal-queued-direction-continuation",
        "exhausted-terminal-no-direction",
        "exhausted-terminal-queued-direction",
        "ambiguous-terminal-follow-up",
        "precommit-recovery-conflict",
    }
    assert {control.name for control in controller.execution_plan.runtime_controls} == {
        "skill_digest",
        "soul_digest",
        "tool_schema_digest",
    }

    topic_planning = registry.resolve(case_id="topic-planning-direction-loop", version="v1")
    assert topic_planning.subject == "topic_planning"
    assert topic_planning.execution_plan is not None
    assert topic_planning.execution_plan.repeat_count == 3
    assert {scenario.case_kind for scenario in topic_planning.topic_planning_fixture.scenarios} == {
        "canonical_notes",
        "baseline",
        "direction",
        "adversarial_control_text",
        "ambiguity_boundary",
        "invalid_draft_repair",
    }
    assert {control.name for control in topic_planning.execution_plan.runtime_controls} == {
        "initial_capability_digest",
        "repair_capability_digest",
        "topic_schema_digest",
    }


@pytest.mark.parametrize("fixture_name", ("missing-controller-execution", "topic-repeat-count"))
def test_invalid_direction_corpus_registry_fixtures_fail_closed(fixture_name: str) -> None:
    fixture_root = Path(__file__).parents[1] / "fixtures" / "evaluation-control-invalid" / fixture_name

    with pytest.raises(ValueError, match="evaluation_case_declaration_invalid"):
        load_case_registry(fixture_root)


@pytest.mark.asyncio
async def test_selected_live_entrypoint_requires_the_declared_provider_preflight(tmp_path: Path) -> None:
    runner = CognitiveEvaluationRunner(
        registry=load_case_registry(),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": _successful_subject, "wave0_worker": _successful_subject},
    )

    with pytest.raises(SelectedLivePreflightError, match="live_model_credentials_missing"):
        await run_selected_live_case(
            runner=runner,
            case_id="hitl1-brief",
            version="v1",
            environ={},
        )
    with pytest.raises(SelectedLivePreflightError, match="live_model_credentials_missing"):
        await run_selected_live_case(
            runner=runner,
            case_id="public-controller-direction-loop",
            version="v1",
            environ={},
        )
    with pytest.raises(SelectedLivePreflightError, match="live_model_credentials_missing"):
        await run_selected_live_case(
            runner=runner,
            case_id="hitl1-cognitive-program",
            version="v1",
            environ={},
        )
    with pytest.raises(SelectedLivePreflightError, match="live_web_credentials_missing"):
        await run_selected_live_case(
            runner=runner,
            case_id="wave0-worker",
            version="v1",
            environ={"OPENAI_API_KEY": "configured"},
        )
    with pytest.raises(CaseAdmissionError, match="evaluation_live_case_not_registered"):
        await run_selected_live_case(
            runner=runner,
            case_id="not-a-case",
            version="v1",
            environ={"OPENAI_API_KEY": "configured"},
        )
    completed = await run_selected_live_case(
        runner=runner,
        case_id="hitl1-brief",
        version="v1",
        environ={"OPENAI_API_KEY": "configured"},
    )
    assert completed.status is ExecutionStatus.COMPLETED


@pytest.mark.asyncio
async def test_selected_cognitive_case_series_uses_only_declared_fresh_repetitions(tmp_path: Path) -> None:
    case = load_case_registry().resolve(case_id="public-controller-direction-loop", version="v1")
    assert case.execution_plan is not None

    async def measured(_context: object) -> SubjectExecution:
        return SubjectExecution(
            output={"selection": "clarification"},
            resource_use={
                "model_calls": 1,
                "tool_calls": 1,
                "provider": "fixture-provider",
                "model": "fixture-model",
                "composed_prompt_digest": "e" * 64,
                **{control.name: control.digest for control in case.execution_plan.runtime_controls},
                "input_tokens": 80,
                "output_tokens": 20,
                "cost_usd": 0.005,
            },
        )

    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((case,)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"public_controller": measured},
    )
    executions = await run_selected_live_case_series(
        runner=runner,
        case_id=case.case_id,
        version=case.version,
        environ={"OPENAI_API_KEY": "configured"},
    )

    assert len(executions) == case.execution_plan.repeat_count
    assert {execution.execution_id for execution in executions}.__len__() == case.execution_plan.repeat_count
    assert all(execution.status is ExecutionStatus.COMPLETED for execution in executions)


def test_hitl1_cognitive_program_registry_binds_the_closed_scenarios_and_runtime_controls() -> None:
    case = load_case_registry().resolve(case_id="hitl1-cognitive-program", version="v1")

    assert case.subject == "hitl1_cognitive_program"
    fixture = case.hitl1_cognitive_program_fixture
    assert {scenario.scenario_id for scenario in fixture.scenarios} == {
        "normal-confirmation",
        "complete-revision",
        "proposal-question",
        "ambiguity",
        "adversarial-input",
        "malformed-candidate-repair",
    }
    assert case.execution_plan is not None
    assert {control.name for control in case.execution_plan.runtime_controls} == {
        "brief_capability_digest",
        "brief_repair_capability_digest",
        "semantic_intake_capability_digest",
        "semantic_repair_capability_digest",
        "profile_schema_digest",
        "semantic_candidate_schema_digest",
    }
    assert all(scenario.expected_capability_ids for scenario in fixture.scenarios)
    assert all(scenario.expected_assignment_fragments for scenario in fixture.scenarios)
    assert all(scenario.forbidden_effects for scenario in fixture.scenarios)
    assert all(scenario.review_criteria for scenario in fixture.scenarios)


def test_wave0_cognitive_program_registry_binds_the_closed_scenarios_and_runtime_controls() -> None:
    case = load_case_registry().resolve(case_id="wave0-cognitive-program", version="v1")

    assert case.subject == "wave0_cognitive_program"
    fixture = case.wave0_cognitive_program_fixture
    assert {scenario.scenario_id for scenario in fixture.scenarios} == {
        "normal-bounded-retrieval-handoff",
        "adversarial-retrieved-instruction",
        "retrieval-shortfall",
        "malformed-initial-candidate-one-repair",
        "post-candidate-validation-rejection",
    }
    assert case.execution_plan is not None
    assert {control.name for control in case.execution_plan.runtime_controls} == {
        "source_intake_capability_digest",
        "source_intake_repair_capability_digest",
        "worker_schema_digest",
    }
    assert all(scenario.expected_capability_ids for scenario in fixture.scenarios)
    assert all(scenario.expected_assignment_fragments for scenario in fixture.scenarios)
    assert all(scenario.forbidden_effects for scenario in fixture.scenarios)
    assert all(scenario.review_criteria for scenario in fixture.scenarios)


@pytest.mark.parametrize("mutation", ("missing-scenario", "duplicate-capability", "duplicate-control"))
def test_hitl1_cognitive_program_fixture_rejects_incomplete_or_duplicate_control_data(mutation: str) -> None:
    case = load_case_registry().resolve(case_id="hitl1-cognitive-program", version="v1")
    payload = deepcopy(case.model_dump(mode="json"))

    if mutation == "missing-scenario":
        payload["fixture"]["scenarios"] = payload["fixture"]["scenarios"][:-1]
    elif mutation == "duplicate-capability":
        payload["fixture"]["scenarios"][0]["expected_capability_ids"] *= 2
    else:
        control = payload["fixture"]["execution"]["runtime_controls"][0]
        payload["fixture"]["execution"]["runtime_controls"].append(control)

    with pytest.raises(ValidationError):
        EvaluationCase.model_validate(payload)


@pytest.mark.parametrize(
    "mutation",
    ("missing-scenario", "duplicate-capability", "duplicate-control", "duplicate-rubric"),
)
def test_wave0_cognitive_program_fixture_rejects_incomplete_or_duplicate_control_data(mutation: str) -> None:
    case = load_case_registry().resolve(case_id="wave0-cognitive-program", version="v1")
    payload = deepcopy(case.model_dump(mode="json"))

    if mutation == "missing-scenario":
        payload["fixture"]["scenarios"] = payload["fixture"]["scenarios"][:-1]
    elif mutation == "duplicate-capability":
        payload["fixture"]["scenarios"][0]["expected_capability_ids"] *= 2
    elif mutation == "duplicate-control":
        control = payload["fixture"]["execution"]["runtime_controls"][0]
        payload["fixture"]["execution"]["runtime_controls"].append(control)
    else:
        payload["fixture"]["scenarios"][0]["review_criteria"] *= 2

    with pytest.raises(ValidationError):
        EvaluationCase.model_validate(payload)


@pytest.mark.asyncio
async def test_wave0_cognitive_program_selected_live_admission_rejects_before_runs_root(tmp_path: Path) -> None:
    """EVH-027: deterministic Wave0 evidence cannot claim a selected-live layer."""

    case = load_case_registry().resolve(case_id="wave0-cognitive-program", version="v1")
    runs_root = tmp_path / "evals" / "runs"
    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((case,)),
        runs_root=runs_root,
        subjects={},
    )

    with pytest.raises(CaseAdmissionError, match="evaluation_live_case_not_registered"):
        await run_selected_live_case(runner=runner, case_id=case.case_id, version=case.version)

    assert not runs_root.exists()


@pytest.mark.asyncio
async def test_wave0_cognitive_program_runner_and_review_retain_deterministic_handoff_only(tmp_path: Path) -> None:
    """EVH-027: the closed corpus records handoff evidence without a quality claim."""

    case = load_case_registry().resolve(case_id="wave0-cognitive-program", version="v1")
    assert case.execution_plan is not None

    async def subject(context: object) -> SubjectExecution:
        fixture = context.fixture
        return SubjectExecution(
            output={"scenario_ids": [scenario["scenario_id"] for scenario in fixture["scenarios"]]},
            resource_use={
                "model_calls": 0,
                "tool_calls": 0,
                "provider": "scripted",
                "model": "scripted",
                "composed_prompt_digest": "w" * 64,
                **{control.name: control.digest for control in case.execution_plan.runtime_controls},
                "input_tokens": 0,
                "output_tokens": 0,
                "cost_usd": 0.0,
                "latency_ms": 0,
            },
        )

    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((case,)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={case.subject: subject},
    )
    execution = await runner.run(case_id=case.case_id, version=case.version)
    review = EvaluationReviewService(registry=runner.registry, runs_root=runner.runs_root)
    record = await review.submit(
        ReviewSubmission(
            bundle_path=execution.bundle_path,
            evaluator="deterministic-wave0-reviewer",
            result=ReviewResult.LIMITED,
            evidence=("Closed corpus retains deterministic handoff only.",),
            confidence="high",
            unknowns=("Live source-quality evidence not collected.",),
            owning_seam="graph.nodes.wave0",
            follow_up="none",
            controls=case.controls,
        )
    )

    assert execution.status is ExecutionStatus.COMPLETED
    assert record.evidence_layer is EvidenceLayer.DETERMINISTIC_HANDOFF


def test_wave1_cognitive_program_registry_binds_the_closed_scenarios_and_runtime_controls() -> None:
    """@impl EVH-028"""

    case = load_case_registry().resolve(case_id="wave1-cognitive-program", version="v1")

    assert case.subject == "wave1_cognitive_program"
    fixture = case.wave1_cognitive_program_fixture
    assert {scenario.scenario_id for scenario in fixture.scenarios} == {
        "normal-bounded-retrieval-handoff",
        "adversarial-retrieved-instruction",
        "baseline-duplicate-containment",
        "malformed-initial-candidate-one-repair",
        "local-semantic-candidate-one-repair",
        "post-candidate-validation-rejection",
    }
    assert case.execution_plan is not None
    assert {control.name for control in case.execution_plan.runtime_controls} == {
        "evidence_extraction_capability_digest",
        "evidence_extraction_repair_capability_digest",
        "worker_schema_digest",
    }


def test_wave2_cognitive_program_registry_binds_the_closed_scenarios_and_runtime_controls() -> None:
    """@impl EVH-029"""

    case = load_case_registry().resolve(case_id="wave2-cognitive-program", version="v1")

    assert case.subject == "wave2_cognitive_program"
    fixture = case.wave2_cognitive_program_fixture
    assert {scenario.scenario_id for scenario in fixture.scenarios} == {
        "normal-accepted-evidence-synthesis",
        "instruction-like-evidence-containment",
        "honest-uncertainty-with-backed-finding",
        "malformed-initial-candidate-one-repair",
        "invalid-repaired-candidate-non-publication",
    }
    assert case.execution_plan is not None
    assert {control.name for control in case.execution_plan.runtime_controls} == {
        "synthesis_capability_digest",
        "synthesis_repair_capability_digest",
        "synthesis_result_schema_digest",
    }


@pytest.mark.parametrize(
    "mutation",
    (
        "missing-scenario",
        "duplicate-capability",
        "duplicate-control",
        "duplicate-rubric",
        "provider-dependency",
        "tool-dependency",
        "over-broad-fixture",
    ),
)
def test_wave2_cognitive_program_fixture_rejects_incomplete_duplicate_or_over_broad_control_data(
    mutation: str,
) -> None:
    """@impl EVH-029"""

    case = load_case_registry().resolve(case_id="wave2-cognitive-program", version="v1")
    payload = deepcopy(case.model_dump(mode="json"))

    if mutation == "missing-scenario":
        payload["fixture"]["scenarios"] = payload["fixture"]["scenarios"][:-1]
    elif mutation == "duplicate-capability":
        payload["fixture"]["scenarios"][0]["expected_capability_ids"] *= 2
    elif mutation == "duplicate-control":
        payload["fixture"]["execution"]["runtime_controls"].append(
            payload["fixture"]["execution"]["runtime_controls"][0]
        )
    elif mutation == "duplicate-rubric":
        payload["fixture"]["scenarios"][0]["review_criteria"] *= 2
    elif mutation == "provider-dependency":
        payload["required_services"] = ["model"]
    elif mutation == "tool-dependency":
        payload["bounds"]["max_tool_calls"] = 1
    else:
        payload["fixture"]["scenarios"][0]["dependencies"] = ["targeted_evidence"]

    with pytest.raises(ValidationError):
        EvaluationCase.model_validate(payload)


@pytest.mark.asyncio
async def test_wave2_cognitive_program_selected_live_admission_rejects_before_runs_root_or_subject(
    tmp_path: Path,
) -> None:
    """@impl EVH-029"""

    case = load_case_registry().resolve(case_id="wave2-cognitive-program", version="v1")
    runs_root = tmp_path / "evals" / "runs"
    subject_called = False

    async def forbidden_subject(_context: object) -> SubjectExecution:
        nonlocal subject_called
        subject_called = True
        raise AssertionError("selected-live admission constructed the Wave2 subject")

    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((case,)),
        runs_root=runs_root,
        subjects={case.subject: forbidden_subject},
    )

    with pytest.raises(CaseAdmissionError, match="evaluation_live_case_not_registered"):
        await run_selected_live_case(
            runner=runner,
            case_id=case.case_id,
            version=case.version,
            environ={"OPENAI_API_KEY": "configured"},
        )

    assert subject_called is False
    assert not runs_root.exists()


@pytest.mark.asyncio
@pytest.mark.workflow
async def test_wave2_cognitive_program_production_scenarios_record_only_declared_handoffs(
    tmp_path: Path,
) -> None:
    """@impl EVH-029"""

    case = load_case_registry().resolve(case_id="wave2-cognitive-program", version="v1")
    fixture = case.wave2_cognitive_program_fixture
    assert case.execution_plan is not None
    supports: dict[str, dict[str, object]] = {}

    class ScenarioStore:
        def __init__(
            self,
            delegate: WorkUnitStore,
            *,
            accepted_submission_refs: tuple[str, ...],
            accepted_evidence: tuple[str, ...],
        ) -> None:
            self.bundle = delegate.bundle
            self._delegate = delegate
            self._accepted_submission_refs = accepted_submission_refs
            self._accepted_evidence = accepted_evidence
            self.write_count = 0

        async def read_synthesis_evidence(self, accepted_refs: tuple[str, ...]) -> tuple[SynthesisEvidence, ...]:
            assert accepted_refs == self._accepted_submission_refs
            return tuple(
                SynthesisEvidence(
                    submission_ref=ref,
                    phase="wave1",
                    result_contract="wave1.evidence-extraction",
                    content=evidence,
                )
                for ref, evidence in zip(self._accepted_submission_refs, self._accepted_evidence, strict=True)
            )

        async def write_synthesis(self, result: SynthesisResult) -> None:
            self.write_count += 1
            await self._delegate.write_synthesis(result)

    class ObservedBridge:
        def __init__(self, delegate: RuntimeNodeAgentBridge) -> None:
            self.delegate = delegate
            self.requests: list[object] = []

        async def run_agent(self, *, context: object, request: object) -> NodeExecutionResult:
            self.requests.append(request)
            return await self.delegate.run_agent(context=context, request=request)  # type: ignore[arg-type]

    def candidate_for(scenario: dict[str, object]) -> str:
        accepted_ref = scenario["accepted_submission_refs"][0]  # type: ignore[index]
        finding = {
            "finding_id": "finding:storage",
            "statement": "Storage duration changes project economics.",
            "priority": 1,
            "affected_topics": [scenario["assignment"]["topic_id"]],  # type: ignore[index]
            "backing_refs": [accepted_ref],
            "confidence": "high",
            "search_required": False,
        }
        gaps = []
        if scenario["case_kind"] == "honest-uncertainty-with-backed-finding":
            gaps.append(
                {
                    "gap_id": "gap:durability",
                    "description": "Geographic durability evidence is unavailable.",
                    "priority": 2,
                    "affected_topics": [scenario["assignment"]["topic_id"]],  # type: ignore[index]
                    "search_required": False,
                }
            )
        return json.dumps(
            {
                "schema_version": 1,
                "findings": [finding],
                "relations": [],
                "gaps": gaps,
                "summary": "One accepted-evidence finding with bounded uncertainty when applicable.",
            }
        )

    def scripted_responses(scenario: dict[str, object]) -> list[str]:
        if scenario["case_kind"] in {
            "malformed-initial-candidate-one-repair",
            "invalid-repaired-candidate-non-publication",
        }:
            return [scenario["initial_candidate"], scenario["repair_candidate"]]  # type: ignore[list-item]
        return [candidate_for(scenario)]

    def dependencies_factory(
        scenario: dict[str, object], _fixture: dict[str, object], context: object
    ) -> NodeBuildDependencies:
        scenario_id = scenario["scenario_id"]
        assert isinstance(scenario_id, str)
        identity = unique_run_identity()
        envelope = local_runtime_envelope(context.workspace / scenario_id, identity=identity)
        bundle = identity.bundle_ref
        BundleLifecycle(workspace_host_path=envelope.workspace_host_path)._publish_sync(bundle)
        selected_bundle = SelectedBundleContext(bundle=bundle)
        graph = project_research_scope(envelope, bundle=bundle)
        model = ScriptedChatModel(responses=[ai_message(response) for response in scripted_responses(scenario)])
        runtime_bridge = RuntimeNodeAgentBridge(
            envelope=envelope,
            policy=_wave2_synthesis_node_agent_policy(graph),
            model_resolver=lambda _envelope: model,
            tools_resolver=lambda _envelope, _policy: (),
        )
        bridge = ObservedBridge(runtime_bridge)
        store = ScenarioStore(
            WorkUnitStore(
                workspace_host_path=envelope.workspace_host_path,
                bundle=bundle,
                clock=lambda: datetime(2026, 7, 17, tzinfo=UTC),
                monotonic=time.monotonic,
                lock_sleep=time.sleep,
                token_factory=lambda: "e" * 32,
                fault_hook=None,
            ),
            accepted_submission_refs=tuple(scenario["accepted_submission_refs"]),  # type: ignore[arg-type]
            accepted_evidence=tuple(scenario["accepted_evidence"]),  # type: ignore[arg-type]
        )
        supports[scenario_id] = {
            "bridge": bridge,
            "model": model,
            "store": store,
            "runtime_bridge": runtime_bridge,
            "bundle_root": envelope.workspace_host_path / bundle_host_relative_root(bundle),
        }
        return NodeBuildDependencies(
            graph_context=graph,
            agent_context=project_node_agent(
                graph,
                node_name="wave2_synthesis",
                attempt_id=f"evaluation-{scenario_id}",
                policy_name=runtime_bridge.policy.policy_name,
                selected_bundle=selected_bundle,
            ),
            capabilities=bridge,  # type: ignore[arg-type]
            synthesis_bundle=store,
            selected_bundle=selected_bundle,
        )

    def state_factory(scenario: dict[str, object], _fixture: dict[str, object], _context: object) -> dict[str, object]:
        assignment = scenario["assignment"]
        scenario_id = scenario["scenario_id"]
        assert isinstance(assignment, dict)
        assert isinstance(scenario_id, str)
        store = supports[scenario_id]["store"]
        assert isinstance(store, ScenarioStore)
        return {
            "bundle_id": store.bundle.bundle_id.value,
            "topic_registry": ({"topic_id": assignment["topic_id"], "title": assignment["title"]},),
            "accepted_submission_refs": tuple(scenario["accepted_submission_refs"]),
            "execution_trace": (),
        }

    def expected_failure_factory(
        scenario: dict[str, object], error: Exception, _context: object
    ) -> dict[str, object] | None:
        if (
            scenario["case_kind"] != "invalid-repaired-candidate-non-publication"
            or not isinstance(error, ValueError)
            or str(error) != "synthesis_findings_required"
        ):
            return None
        store = supports[scenario["scenario_id"]]["store"]
        assert isinstance(store, ScenarioStore)
        assert store.write_count == 0
        return {"expected_invalid_candidate": True}

    production_subject = production_scenario_node_subject(
        subject=case.subject,
        node_spec=WAVE2_NODE_SPEC,
        dependencies_factory=dependencies_factory,
        state_factory=state_factory,
        expected_failure_factory=expected_failure_factory,
    )

    async def subject(context: object) -> SubjectExecution:
        await production_subject(context)
        facts: list[dict[str, object]] = []
        prompt_bytes = bytearray()
        for scenario in fixture.scenarios:
            support = supports[scenario.scenario_id]
            bridge = support["bridge"]
            store = support["store"]
            runtime_bridge = support["runtime_bridge"]
            assert isinstance(bridge, ObservedBridge)
            assert isinstance(store, ScenarioStore)
            assert isinstance(runtime_bridge, RuntimeNodeAgentBridge)
            requests = bridge.requests
            prompt = "\n".join(
                f"{request.objective}\n{request.expected_output}"
                for request in requests  # type: ignore[attr-defined]
            )
            prompt_bytes.extend(prompt.encode("utf-8"))
            facts.append(
                {
                    "scenario_id": scenario.scenario_id,
                    "capability_ids": [request.capability_ref.capability_id for request in requests],  # type: ignore[attr-defined]
                    "prompt_assignment_bound": all(
                        fragment in prompt for fragment in scenario.expected_assignment_fragments
                    ),
                    "accepted_evidence_bound": all(
                        ref in requests[0].objective
                        for ref in scenario.accepted_submission_refs  # type: ignore[attr-defined]
                    ),
                    "zero_tool_runtime_enforced": runtime_bridge.policy.allowed_tool_names == frozenset()
                    and all(request.tools_enabled is False for request in requests),  # type: ignore[attr-defined]
                    "repair_count": len(requests) - 1,
                    "deterministic_admission": scenario.case_kind != "invalid-repaired-candidate-non-publication",
                    "invalid_candidate_no_write": (
                        store.write_count == 0
                        if scenario.case_kind == "invalid-repaired-candidate-non-publication"
                        else None
                    ),
                }
            )
        model_calls = sum(support["model"].calls for support in supports.values())  # type: ignore[attr-defined]
        return SubjectExecution(
            output={"wave2_handoff_facts": facts},
            resource_use={
                "model_calls": model_calls,
                "tool_calls": 0,
                "provider": "scripted",
                "model": "scripted",
                "composed_prompt_digest": hashlib.sha256(prompt_bytes).hexdigest(),
                **{control.name: control.digest for control in case.execution_plan.runtime_controls},
                "input_tokens": model_calls * 10,
                "output_tokens": model_calls * 5,
                "cost_usd": 0.0,
            },
        )

    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((case,)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={case.subject: subject},
        available_services=frozenset(),
    )
    execution = await runner.run(case_id=case.case_id, version=case.version)

    assert execution.status is ExecutionStatus.COMPLETED
    output = json.loads((execution.bundle_path / "output.json").read_text(encoding="utf-8"))
    facts = output["wave2_handoff_facts"]
    assert [fact["scenario_id"] for fact in facts] == [scenario.scenario_id for scenario in fixture.scenarios]
    assert [fact["repair_count"] for fact in facts] == [0, 0, 0, 1, 1]
    assert all(fact["prompt_assignment_bound"] for fact in facts)
    assert all(fact["accepted_evidence_bound"] for fact in facts)
    assert all(fact["zero_tool_runtime_enforced"] for fact in facts)
    assert facts[-1]["invalid_candidate_no_write"] is True
    assert all("state_update" not in fact for fact in facts)
    assert all("gate" not in key and "route" not in key for fact in facts for key in fact)
    assert sum(support["model"].calls for support in supports.values()) == 7  # type: ignore[attr-defined]
    assert all(support["model"].responses == [] for support in supports.values())  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "mutation",
    ("missing-scenario", "duplicate-capability", "duplicate-control", "duplicate-rubric", "baseline-missing"),
)
def test_wave1_cognitive_program_fixture_rejects_incomplete_or_over_broad_control_data(mutation: str) -> None:
    """@impl EVH-028"""

    case = load_case_registry().resolve(case_id="wave1-cognitive-program", version="v1")
    payload = deepcopy(case.model_dump(mode="json"))
    if mutation == "missing-scenario":
        payload["fixture"]["scenarios"] = payload["fixture"]["scenarios"][:-1]
    elif mutation == "duplicate-capability":
        payload["fixture"]["scenarios"][0]["expected_capability_ids"] *= 2
    elif mutation == "duplicate-control":
        payload["fixture"]["execution"]["runtime_controls"].append(
            payload["fixture"]["execution"]["runtime_controls"][0]
        )
    elif mutation == "duplicate-rubric":
        payload["fixture"]["scenarios"][0]["review_criteria"] *= 2
    else:
        payload["fixture"]["scenarios"][2]["wave0_baseline_urls"] = []

    with pytest.raises(ValidationError):
        EvaluationCase.model_validate(payload)


@pytest.mark.asyncio
async def test_wave1_cognitive_program_selected_live_admission_rejects_before_runs_root(tmp_path: Path) -> None:
    """@impl EVH-028"""

    case = load_case_registry().resolve(case_id="wave1-cognitive-program", version="v1")
    runs_root = tmp_path / "evals" / "runs"
    runner = CognitiveEvaluationRunner(registry=CaseRegistry((case,)), runs_root=runs_root, subjects={})

    with pytest.raises(CaseAdmissionError, match="evaluation_live_case_not_registered"):
        await run_selected_live_case(runner=runner, case_id=case.case_id, version=case.version)

    assert not runs_root.exists()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("case_id", "fixture_name"),
    (
        ("hitl1-cognitive-program", "hitl1_cognitive_program_fixture"),
        ("wave1-cognitive-program", "wave1_cognitive_program_fixture"),
    ),
)
async def test_multi_scenario_adapter_uses_only_the_registered_factory_and_declared_scenarios(
    tmp_path: Path,
    case_id: str,
    fixture_name: str,
) -> None:
    """@impl EVH-028"""

    class NodeSpec:
        def real_factory(self, _dependencies: object):
            async def branch(state: dict[str, object]) -> dict[str, object]:
                return {"candidate": state["scenario_id"]}

            return branch

    case = load_case_registry().resolve(case_id=case_id, version="v1")
    assert case.execution_plan is not None
    subject = production_scenario_node_subject(
        subject=case.subject,
        node_spec=NodeSpec(),
        dependencies_factory=lambda _scenario, _fixture, _context: object(),
        state_factory=lambda scenario, _fixture, _context: {"scenario_id": scenario["scenario_id"]},
        resource_use_factory=lambda _context, _output: {
            "model_calls": 6,
            "tool_calls": 0,
            "provider": "fixture-provider",
            "model": "fixture-model",
            "composed_prompt_digest": "a" * 64,
            **{control.name: control.digest for control in case.execution_plan.runtime_controls},
            "input_tokens": 120,
            "output_tokens": 60,
            "cost_usd": 0.01,
        },
    )
    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((case,)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={case.subject: subject},
    )

    execution = await runner.run(case_id=case.case_id, version=case.version)

    assert execution.status is ExecutionStatus.COMPLETED
    output = json.loads((execution.bundle_path / "output.json").read_text(encoding="utf-8"))
    assert [row["scenario_id"] for row in output["scenario_updates"]] == [
        scenario.scenario_id for scenario in getattr(case, fixture_name).scenarios
    ]


@pytest.mark.asyncio
async def test_evidence_layer_is_manifest_derived_and_live_requires_selected_preflight(tmp_path: Path) -> None:
    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((_case(),)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": _successful_subject},
    )

    deterministic = await runner.run(case_id="hitl1-brief", version="v1")
    manifest = json.loads((deterministic.bundle_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["evidence_layer"] == EvidenceLayer.DETERMINISTIC_HANDOFF.value
    legacy_manifest = dict(manifest)
    legacy_manifest.pop("evidence_layer")
    with pytest.raises(ValidationError):
        EvaluationBundleManifest.model_validate(legacy_manifest)
    with pytest.raises(ValidationError):
        EvaluationBundleManifest.model_validate({**manifest, "evidence_layer": "unsupported_evidence_layer"})
    assert EvaluationBundleManifest.model_validate(manifest).evidence_layer is EvidenceLayer.DETERMINISTIC_HANDOFF

    review = EvaluationReviewService(registry=runner.registry, runs_root=runner.runs_root)
    submission = ReviewSubmission(
        bundle_path=deterministic.bundle_path,
        evaluator="deterministic-reviewer",
        result=ReviewResult.PASS,
        evidence=("bounded deterministic handoff",),
        confidence="high",
        unknowns=(),
        owning_seam="graph.nodes.hitl1",
        follow_up="none",
        controls=_case().controls,
    )
    record = await review.submit(submission)
    assert record.evidence_layer is EvidenceLayer.DETERMINISTIC_HANDOFF
    payload = json.loads(record.path.read_text(encoding="utf-8"))
    assert payload["evidence_layer"] == EvidenceLayer.DETERMINISTIC_HANDOFF.value
    record_payload = record.model_dump(mode="json")
    missing_record_layer = dict(record_payload)
    missing_record_layer.pop("evidence_layer")
    with pytest.raises(ValidationError):
        ReviewRecord.model_validate(missing_record_layer)
    with pytest.raises(ValidationError):
        ReviewRecord.model_validate({**record_payload, "evidence_layer": "unsupported_evidence_layer"})

    with pytest.raises(TypeError):
        await runner.run(  # type: ignore[call-arg]
            case_id="hitl1-brief",
            version="v1",
            evidence_layer=EvidenceLayer.CREDENTIALED_LIVE_QUALITY,
        )
    with pytest.raises(ValidationError):
        ReviewSubmission.model_validate(
            {
                **submission.model_dump(),
                "evidence_layer": EvidenceLayer.CREDENTIALED_LIVE_QUALITY.value,
            }
        )
    with pytest.raises(ValidationError):
        ReviewSubmission.model_validate({**submission.model_dump(), "release_pass": True})

    missing_root = tmp_path / "evals" / "missing-credentials"
    unavailable_runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((_case(),)),
        runs_root=missing_root,
        subjects={"hitl1_brief": _successful_subject},
    )
    with pytest.raises(SelectedLivePreflightError, match="live_model_credentials_missing"):
        await run_selected_live_case(
            runner=unavailable_runner,
            case_id="hitl1-brief",
            version="v1",
            environ={},
        )
    assert not missing_root.exists()

    live = await run_selected_live_case(
        runner=runner,
        case_id="hitl1-brief",
        version="v1",
        environ={"OPENAI_API_KEY": "configured"},
    )
    live_manifest = json.loads((live.bundle_path / "manifest.json").read_text(encoding="utf-8"))
    assert live_manifest["evidence_layer"] == EvidenceLayer.CREDENTIALED_LIVE_QUALITY.value
    assert (
        EvaluationBundleManifest.model_validate(live_manifest).evidence_layer is EvidenceLayer.CREDENTIALED_LIVE_QUALITY
    )
    assert (
        ReviewRecord.model_validate(
            {**record_payload, "evidence_layer": EvidenceLayer.CREDENTIALED_LIVE_QUALITY.value}
        ).evidence_layer
        is EvidenceLayer.CREDENTIALED_LIVE_QUALITY
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_layer",
    (None, "unsupported_evidence_layer"),
    ids=("missing", "unknown"),
)
async def test_invalid_manifest_evidence_layer_rejects_before_review_write(
    tmp_path: Path, invalid_layer: str | None
) -> None:
    runner = CognitiveEvaluationRunner(
        registry=CaseRegistry((_case(),)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"hitl1_brief": _successful_subject},
    )
    execution = await runner.run(case_id="hitl1-brief", version="v1")
    manifest_path = execution.bundle_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if invalid_layer is None:
        manifest.pop("evidence_layer")
    else:
        manifest["evidence_layer"] = invalid_layer
    rejected_manifest_bytes = (
        json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
    ).encode("utf-8")
    manifest_path.write_bytes(rejected_manifest_bytes)

    submission = ReviewSubmission(
        bundle_path=execution.bundle_path,
        evaluator="deterministic-reviewer",
        result=ReviewResult.PASS,
        evidence=("bounded deterministic handoff",),
        confidence="high",
        unknowns=(),
        owning_seam="graph.nodes.hitl1",
        follow_up="none",
        controls=_case().controls,
    )
    review = EvaluationReviewService(registry=runner.registry, runs_root=runner.runs_root)
    result = await EvaluationOperations(runner=runner, review=review).review(submission)

    assert result.operation == "review"
    assert result.diagnostic == "bundle_manifest_invalid"
    assert result.reference is None
    assert result.status is None
    assert manifest_path.read_bytes() == rejected_manifest_bytes
    assert not (execution.bundle_path.parent / "reviews").exists()


def test_evaluation_runtime_facade_is_the_only_contract_import_surface() -> None:
    from deerflow_deep_research.domain.evaluation import EvaluationBundleManifest as DomainManifest
    from deerflow_deep_research.runtime.evaluation import EvaluationBundleManifest as FacadeManifest

    assert FacadeManifest is DomainManifest
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("deerflow_deep_research.runtime.evaluation.contracts")
