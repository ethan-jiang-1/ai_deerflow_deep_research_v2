"""Controller submit authority and atomic publication integration.

@impl WOU-004, WAN-006
"""

from __future__ import annotations

import base64
import hashlib
import time
from dataclasses import replace
from datetime import UTC, datetime

import pytest
from deerflow_deep_research_fixtures.graph.nodes.wave0 import adapter as fixture_wave0_adapter
from deerflow_deep_research_fixtures.work_units import FixtureResultDocument, run_fixture_work_unit_component

from deerflow_deep_research.domain.bundle import (
    BundleId,
    RunBundleRef,
    bundle_attempt_dir,
    bundle_result_path,
    bundle_source_content_path,
)
from deerflow_deep_research.domain.context import GraphContextView, NodeAgentContext
from deerflow_deep_research.domain.invocation import (
    WorkUnitControllerDependencies,
    WorkUnitWorkerDependencies,
)
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies, PolicyRef
from deerflow_deep_research.domain.wave1 import ClaimDraft, Wave1SourceIntakeResult, Wave1SourceRef
from deerflow_deep_research.domain.work_units import (
    CandidateResult,
    OutputRef,
    SourceRef,
    canonical_json_bytes,
    compute_candidate_hash,
)
from deerflow_deep_research.engine.work_units.kernel import allocate_attempt, materialize_work_spec
from deerflow_deep_research.graph.components.work_units import submit_candidate_if_active
from deerflow_deep_research.graph.nodes.wave1.subgraph import WAVE1_REAL_POLICY, materialize_wave1_intents
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.projection import RuntimeWorkUnitDependencyResolver
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore

BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "S" * 43), scope_bucket="s_" + "S" * 43)
BUNDLE_ID = BUNDLE.bundle_id.value
NOW = datetime(2026, 7, 14, tzinfo=UTC)


def _publish_bundle(workspace) -> None:
    BundleLifecycle(workspace_host_path=workspace)._publish_sync(BUNDLE)


async def _run_wave0_fixture_work_units(state, *, controller, clock):
    return await run_fixture_work_unit_component(
        state,
        logical_name="wave0",
        policy=PolicyRef(name="fixture-wave0", version="v1"),
        controller=controller,
        intents=fixture_wave0_adapter._INTENTS,
        clock=clock,
    )


def _hash(data: bytes) -> str:
    return "h_" + base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode("ascii").rstrip("=")


class ForbiddenCapabilities:
    async def run_agent(self, *, context, request):
        raise AssertionError("unused")


class BaseResolver:
    def __init__(self, graph_context: GraphContextView) -> None:
        self._graph_context = graph_context

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
            ),
            capabilities=ForbiddenCapabilities(),
        )


def _controller(tmp_path) -> tuple[WorkUnitControllerDependencies, WorkUnitStore]:
    _publish_bundle(tmp_path)
    graph = GraphContextView(
        research_scope_id=BUNDLE_ID,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{BUNDLE_ID}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{BUNDLE_ID}",
    )
    base = BaseResolver(graph)
    store = WorkUnitStore(
        workspace_host_path=tmp_path,
        bundle=BUNDLE,
        clock=lambda: NOW,
        monotonic=time.monotonic,
        lock_sleep=time.sleep,
        token_factory=lambda: "3" * 32,
        fault_hook=None,
    )
    return (
        WorkUnitControllerDependencies(
            store=store,
            resolver=RuntimeWorkUnitDependencyResolver(graph, base, store),
        ),
        store,
    )


class _OmitResultWriter:
    def __init__(self, delegate) -> None:
        self._delegate = delegate

    async def write_result(self, document) -> None:
        return None

    async def write_output(self, relative_path, content) -> None:
        await self._delegate.write_output(relative_path, content)


class _OmitResultResolver:
    def __init__(self, delegate) -> None:
        self._delegate = delegate

    async def resolve_worker(self, **kwargs) -> WorkUnitWorkerDependencies:
        resolved = await self._delegate.resolve_worker(**kwargs)
        assert resolved.artifact_writer is not None
        return replace(resolved, artifact_writer=_OmitResultWriter(resolved.artifact_writer))


async def test_worker_completion_without_result_fails_through_real_component_before_ledger(tmp_path) -> None:
    controller, store = _controller(tmp_path)
    controller = WorkUnitControllerDependencies(
        store=controller.store,
        resolver=_OmitResultResolver(controller.resolver),
    )
    state = {"bundle_id": BUNDLE_ID, "generation": 0}
    result = await _run_wave0_fixture_work_units(state, controller=controller, clock=lambda: NOW)
    attempt = next(iter(result.parent_update["attempts_by_id"].values()))
    assert attempt["terminal_code"] == "validation_failed"
    assert attempt["failure_category"] == "submission_validation"
    assert await store.load_records() == ()


async def _valid_boundary_fixture(controller: WorkUnitControllerDependencies):
    spec = materialize_work_spec(
        bundle_id=BUNDLE_ID,
        generation=0,
        phase="wave0",
        work_ordinal=0,
        intent=fixture_wave0_adapter._INTENTS[0],
    )
    attempt = allocate_attempt(spec, attempt_ordinal=0, created_at=NOW)
    resolved = await controller.resolver.resolve_worker(
        logical_name="wave0",
        work_spec=spec,
        attempt=attempt,
        policy=PolicyRef("skeleton-wave0", "v1"),
    )
    assert resolved.artifact_writer is not None
    output = b'{"fixture":true}'
    await resolved.artifact_writer.write_output("fixture.json", output)
    document = FixtureResultDocument(
        schema_version=1,
        bundle_id=spec.bundle_id,
        generation=spec.generation,
        phase=spec.phase,
        work_id=spec.work_id,
        attempt_id=attempt.attempt_id,
        worker_role=spec.worker_role,
        spec_hash=spec.spec_hash,
        result_contract="fixture.work-unit",
        fixture_marker="non_research_fixture",
        output_paths=spec.required_outputs,
        source_ids=(),
    )
    result = canonical_json_bytes(document)
    await resolved.artifact_writer.write_result(document)
    root = bundle_attempt_dir(BUNDLE, spec.work_id, attempt.attempt_id)
    payload = {
        "schema_version": 1,
        "bundle_id": BUNDLE_ID,
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
                path=f"{root}/outputs/fixture.json",
                content_hash=_hash(output),
                schema_version=1,
                byte_count=len(output),
            ),
        ),
        "source_refs": (),
    }
    payload["candidate_hash"] = compute_candidate_hash(payload)
    candidate = CandidateResult.model_validate(payload)
    return spec, attempt, candidate


async def test_wrong_identity_out_of_root_and_hash_mismatch_fail_real_submit_boundary(tmp_path) -> None:
    controller, store = _controller(tmp_path)
    spec, attempt, candidate = await _valid_boundary_fixture(controller)
    payload = candidate.__dict__

    wrong_identity = CandidateResult.model_construct(**{**payload, "worker_role": "other_worker"})
    with pytest.raises(ValueError, match="submission_validation_failed:identity_mismatch"):
        await submit_candidate_if_active(
            controller,
            spec=spec,
            attempt=attempt,
            candidate=wrong_identity,
            active_attempt_id=attempt.attempt_id,
            now=NOW,
        )

    out_of_root = CandidateResult.model_construct(
        **{**payload, "result_ref": f"workspace/deep-research/{BUNDLE_ID}/evidence/result.json"}
    )
    with pytest.raises(ValueError, match="path_not_canonical"):
        await submit_candidate_if_active(
            controller,
            spec=spec,
            attempt=attempt,
            candidate=out_of_root,
            active_attempt_id=attempt.attempt_id,
            now=NOW,
        )

    bad_hash = CandidateResult.model_construct(**{**payload, "result_hash": "h_" + "Z" * 43})
    with pytest.raises(ValueError, match="content_hash_mismatch"):
        await submit_candidate_if_active(
            controller,
            spec=spec,
            attempt=attempt,
            candidate=bad_hash,
            active_attempt_id=attempt.attempt_id,
            now=NOW,
        )
    assert await store.load_records() == ()


async def test_same_hash_replays_and_different_hash_conflicts_at_real_store_boundary(tmp_path) -> None:
    controller, store = _controller(tmp_path)
    spec, attempt, candidate = await _valid_boundary_fixture(controller)
    first = await submit_candidate_if_active(
        controller,
        spec=spec,
        attempt=attempt,
        candidate=candidate,
        active_attempt_id=attempt.attempt_id,
        now=NOW,
    )
    replay = await submit_candidate_if_active(
        controller,
        spec=spec,
        attempt=attempt,
        candidate=candidate,
        active_attempt_id=attempt.attempt_id,
        now=NOW,
    )
    assert replay.record_hash == first.record_hash

    divergent_payload = candidate.model_dump(mode="python")
    divergent_payload["result_hash"] = "h_" + "Y" * 43
    divergent_payload["candidate_hash"] = compute_candidate_hash(divergent_payload)
    divergent = CandidateResult.model_validate(divergent_payload)
    with pytest.raises(ValueError, match="candidate_conflict"):
        await store.commit_candidate(divergent, scope=spec.scope)
    assert len(await store.load_records()) == 1


async def _wave1_boundary_fixture(
    controller: WorkUnitControllerDependencies,
    *,
    urls: tuple[str, ...],
    newness: tuple[bool, ...],
) -> tuple[object, object, CandidateResult]:
    intent = materialize_wave1_intents(({"topic_id": "topic", "title": "Topic", "scope": "Scope"},))[0]
    spec = materialize_work_spec(
        bundle_id=BUNDLE_ID,
        generation=0,
        phase="wave1",
        work_ordinal=0,
        intent=intent,
    )
    attempt = allocate_attempt(spec, attempt_ordinal=0, created_at=NOW)
    resolved = await controller.resolver.resolve_worker(
        logical_name="wave1",
        work_spec=spec,
        attempt=attempt,
        policy=WAVE1_REAL_POLICY,
    )
    assert resolved.artifact_writer is not None
    source_refs: list[SourceRef] = []
    document_sources: list[Wave1SourceRef] = []
    for index, (url, is_new) in enumerate(zip(urls, newness, strict=True)):
        source_id = f"source:wave1-{index}"
        content = f'{{"source":"{index}"}}'.encode("ascii")
        cache_name = f"source-{index}.json"
        await resolved.artifact_writer.write_source(cache_name, content)
        content_ref = bundle_source_content_path(BUNDLE, spec.work_id, attempt.attempt_id, cache_name)
        source_ref = SourceRef(
            source_id=source_id,
            canonical_url=url,
            content_ref=content_ref,
            content_hash=_hash(content),
            byte_count=len(content),
        )
        source_refs.append(source_ref)
        document_sources.append(
            Wave1SourceRef(
                source_id=source_id,
                canonical_url=url,
                title=f"Source {index}",
                content_ref=content_ref,
                content_hash=source_ref.content_hash,
                byte_count=source_ref.byte_count,
                is_new_vs_wave0=is_new,
            )
        )
    document = Wave1SourceIntakeResult(
        schema_version=1,
        bundle_id=BUNDLE_ID,
        generation=0,
        phase="wave1",
        work_id=spec.work_id,
        attempt_id=attempt.attempt_id,
        worker_role=spec.worker_role,
        spec_hash=spec.spec_hash,
        result_contract="wave1.source-intake",
        output_paths=(),
        source_ids=tuple(source.source_id for source in document_sources),
        sources=tuple(document_sources),
        claims=(
            ClaimDraft(
                claim_id="claim:w1_boundary",
                statement="A bounded source-floor test claim.",
                support_refs=tuple(source.source_id for source in document_sources),
            ),
        ),
        open_questions=(),
    )
    result = canonical_json_bytes(document)
    await resolved.artifact_writer.write_result(document)
    payload = {
        "schema_version": 1,
        "bundle_id": BUNDLE_ID,
        "generation": 0,
        "phase": "wave1",
        "work_id": spec.work_id,
        "attempt_id": attempt.attempt_id,
        "worker_role": spec.worker_role,
        "spec_hash": spec.spec_hash,
        "result_contract": spec.result_contract,
        "result_ref": bundle_result_path(BUNDLE, spec.work_id, attempt.attempt_id),
        "result_hash": _hash(result),
        "result_schema_version": 1,
        "result_byte_count": len(result),
        "output_refs": (),
        "source_refs": tuple(source_refs),
    }
    payload["candidate_hash"] = compute_candidate_hash(payload)
    return spec, attempt, CandidateResult.model_validate(payload)


@pytest.mark.parametrize(
    ("urls", "newness"),
    [
        pytest.param(("https://example.com/only",), (True,), id="fewer-than-two-new-urls"),
        pytest.param(
            ("https://example.com/one", "https://example.com/two"),
            (False, True),
            id="persisted-newness-marker-mismatch",
        ),
    ],
)
async def test_wave1_submit_recomputes_source_floor_and_newness_before_ledger_append(tmp_path, urls, newness) -> None:
    """@impl WON-002
    @impl WON-003
    """

    controller, store = _controller(tmp_path)
    spec, attempt, candidate = await _wave1_boundary_fixture(controller, urls=urls, newness=newness)

    with pytest.raises(ValueError, match="submission_validation_failed:invalid_output_schema"):
        await submit_candidate_if_active(
            controller,
            spec=spec,
            attempt=attempt,
            candidate=candidate,
            active_attempt_id=attempt.attempt_id,
            now=NOW,
        )

    assert await store.load_records() == ()
