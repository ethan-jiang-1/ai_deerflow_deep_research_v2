"""Test-owned compact authority seeds for focused late-node live cases.

@impl EVH-005
@impl EVH-007
"""

from __future__ import annotations

import base64
import hashlib
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from deerflow_deep_research.domain.bundle import (
    BundleId,
    RunBundleRef,
    bundle_result_path,
    bundle_source_content_path,
)
from deerflow_deep_research.domain.context import (
    GraphContextView,
    NodeAgentBundleContext,
    NodeAgentContext,
    SelectedBundleContext,
)
from deerflow_deep_research.domain.invocation import WorkUnitControllerDependencies
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.state import RESEARCH_STATE_SCHEMA_VERSION, validate_research_state
from deerflow_deep_research.domain.synthesis import GapRecord, SynthesisResult
from deerflow_deep_research.domain.wave1 import ClaimDraft, Wave1SourceIntakeResult, Wave1SourceRef
from deerflow_deep_research.domain.work_units import (
    CandidateResult,
    SourceRef,
    Wave0SourceMeta,
    canonical_json_bytes,
    compute_candidate_hash,
)
from deerflow_deep_research.engine.work_units.kernel import allocate_attempt, materialize_work_spec
from deerflow_deep_research.graph.components.work_units import submit_candidate_if_active
from deerflow_deep_research.graph.nodes.wave0.prompts import build_wave0_result_document
from deerflow_deep_research.graph.nodes.wave0.subgraph import (
    WAVE0_REAL_POLICY,
    materialize_wave0_intents,
)
from deerflow_deep_research.graph.nodes.wave1.subgraph import (
    WAVE1_REAL_POLICY,
    materialize_wave1_intents,
)
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.projection import RuntimeWorkUnitDependencyResolver
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore

NOW = datetime(2026, 7, 18, tzinfo=UTC)
DEFAULT_BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "L" * 43), scope_bucket="s_" + "L" * 43)
TOPIC_REGISTRY = (
    {
        "topic_id": "storage",
        "title": "Synthetic storage",
        "scope": "Synthetic storage evidence",
        "must_answer_bindings": ("What supports the synthetic finding?",),
    },
)


class _ForbiddenCapabilities:
    async def run_agent(self, *, context, request):
        raise AssertionError("seed_builder_does_not_call_agent")


class _BaseResolver:
    def __init__(self, graph_context: GraphContextView, *, bundle: RunBundleRef) -> None:
        self._graph_context = graph_context
        self._selected_bundle = SelectedBundleContext(bundle=bundle)

    def resolve(self, *, logical_name, attempt_id, policy):
        return NodeBuildDependencies(
            graph_context=self._graph_context,
            agent_context=NodeAgentContext(
                research_scope_id=self._graph_context.research_scope_id,
                node_name=logical_name,
                attempt_id=attempt_id,
                workspace_root=self._graph_context.workspace_root,
                attempt_root=f"{self._graph_context.workspace_root}/attempts/{attempt_id}",
                policy_name=policy.name,
                bundle_context=NodeAgentBundleContext.from_selected_bundle(self._selected_bundle),
            ),
            capabilities=_ForbiddenCapabilities(),
            selected_bundle=self._selected_bundle,
        )


@dataclass(frozen=True)
class LiveSeedBundle:
    bundle_id: str
    bundle: RunBundleRef
    checkpoint: dict[str, object]
    store: WorkUnitStore
    synthesis_gaps: tuple[dict[str, object], ...] = ()
    synthesis_result: SynthesisResult | None = None


async def build_live_seed_bundle(
    workspace_host_path: Path,
    *,
    include_wave1: bool,
    now: datetime = NOW,
    clock: Callable[[], datetime] | None = None,
    include_synthesis_gap: bool = False,
    bundle: RunBundleRef = DEFAULT_BUNDLE,
) -> LiveSeedBundle:
    if not isinstance(bundle, RunBundleRef):
        raise TypeError("bundle_required")
    bundle_id = bundle.bundle_id.value
    effective_clock = clock or (lambda: now)
    graph = GraphContextView(
        research_scope_id=bundle_id,
        workspace_root=f"/mnt/user-data/workspace/deep-research/{bundle_id}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/deep-research/{bundle_id}",
    )
    lifecycle = BundleLifecycle(workspace_host_path=workspace_host_path)
    if not lifecycle.private_root(bundle).exists():
        lifecycle._publish_sync(bundle)
    store = WorkUnitStore(
        workspace_host_path=workspace_host_path,
        bundle=bundle,
        clock=effective_clock,
        monotonic=time.monotonic,
        lock_sleep=time.sleep,
        token_factory=lambda: "6" * 32,
        fault_hook=None,
    )
    controller = WorkUnitControllerDependencies(
        store=store,
        resolver=RuntimeWorkUnitDependencyResolver(graph, _BaseResolver(graph, bundle=bundle), store),
    )
    await _publish_wave0(controller, bundle=bundle, now=now)
    if include_wave1:
        await _publish_wave1(controller, bundle=bundle, now=now)
    synthesis_gaps: tuple[dict[str, object], ...] = ()
    synthesis_result: SynthesisResult | None = None
    if include_synthesis_gap:
        gap = GapRecord(
            gap_id="gap:focused-targeted",
            description="Focused targeted evidence gap.",
            priority=1,
            affected_topics=("storage",),
            search_required=True,
        )
        synthesis_result = SynthesisResult(
            schema_version=1,
            findings=(),
            relations=(),
            gaps=(gap,),
            summary="One focused gap.",
        )
        await store.write_synthesis(synthesis_result)
        synthesis_gaps = tuple(item.model_dump(mode="python") for item in synthesis_result.gaps)
    records = await store.load_records()
    checkpoint: dict[str, object] = {
        "schema_version": RESEARCH_STATE_SCHEMA_VERSION,
        "bundle_id": bundle_id,
        "outer_thread_id": "thread-live-seed",
        "topic_registry": TOPIC_REGISTRY,
        "must_answer_questions": ("What supports the synthetic finding?",),
        "accepted_submission_refs": tuple(record.record_hash for record in records),
        "execution_trace": (),
    }
    validate_research_state(checkpoint)
    return LiveSeedBundle(
        bundle_id=bundle_id,
        bundle=bundle,
        checkpoint=checkpoint,
        store=store,
        synthesis_gaps=synthesis_gaps,
        synthesis_result=synthesis_result,
    )


async def _publish_wave0(
    controller: WorkUnitControllerDependencies,
    *,
    bundle: RunBundleRef,
    now: datetime,
) -> None:
    bundle_id = bundle.bundle_id.value
    intent = materialize_wave0_intents(TOPIC_REGISTRY)[0]
    spec = materialize_work_spec(
        bundle_id=bundle_id,
        generation=0,
        phase="wave0",
        work_ordinal=0,
        intent=intent,
    )
    attempt = allocate_attempt(spec, attempt_ordinal=0, created_at=now)
    resolved = await controller.resolver.resolve_worker(
        logical_name="wave0",
        work_spec=spec,
        attempt=attempt,
        policy=WAVE0_REAL_POLICY,
    )
    writer = resolved.artifact_writer
    if writer is None:
        raise ValueError("seed_artifact_writer_missing")
    source_content = b'{"body":"Synthetic Wave0 evidence body"}'
    await writer.write_source("source-0.json", source_content)
    content_ref = bundle_source_content_path(bundle, spec.work_id, attempt.attempt_id, "source-0.json")
    source_ref = SourceRef(
        source_id="source:wave0",
        canonical_url="https://example.invalid/wave0",
        content_ref=content_ref,
        content_hash=_content_hash(source_content),
        byte_count=len(source_content),
    )
    document = build_wave0_result_document(
        spec,
        attempt,
        (
            Wave0SourceMeta(
                source_id=source_ref.source_id,
                canonical_url=source_ref.canonical_url,
                title="Synthetic Wave0 source",
                content_ref=source_ref.content_ref,
                fetch_status="fetched",
            ),
        ),
        ("Synthetic Wave0 finding.",),
        "",
    )
    await writer.write_result(document)
    candidate = _candidate(bundle, spec, attempt.attempt_id, canonical_json_bytes(document), (source_ref,))
    await submit_candidate_if_active(
        controller,
        spec=spec,
        attempt=attempt,
        candidate=candidate,
        active_attempt_id=attempt.attempt_id,
        now=now,
    )


async def _publish_wave1(
    controller: WorkUnitControllerDependencies,
    *,
    bundle: RunBundleRef,
    now: datetime,
) -> None:
    bundle_id = bundle.bundle_id.value
    intent = materialize_wave1_intents(TOPIC_REGISTRY)[0]
    spec = materialize_work_spec(
        bundle_id=bundle_id,
        generation=0,
        phase="wave1",
        work_ordinal=0,
        intent=intent,
    )
    attempt = allocate_attempt(spec, attempt_ordinal=0, created_at=now)
    resolved = await controller.resolver.resolve_worker(
        logical_name="wave1",
        work_spec=spec,
        attempt=attempt,
        policy=WAVE1_REAL_POLICY,
    )
    writer = resolved.artifact_writer
    if writer is None:
        raise ValueError("seed_artifact_writer_missing")
    source_content = b'{"body":"Synthetic Wave1 evidence body"}'
    additional_source_content = b'{"body":"Synthetic Wave1 additional evidence body"}'
    await writer.write_source("source-0.json", source_content)
    await writer.write_source("source-1.json", additional_source_content)
    content_ref = bundle_source_content_path(bundle, spec.work_id, attempt.attempt_id, "source-0.json")
    additional_content_ref = bundle_source_content_path(bundle, spec.work_id, attempt.attempt_id, "source-1.json")
    source_ref = SourceRef(
        source_id="source:wave1",
        canonical_url="https://example.invalid/wave1",
        content_ref=content_ref,
        content_hash=_content_hash(source_content),
        byte_count=len(source_content),
    )
    additional_source_ref = SourceRef(
        source_id="source:wave1-second",
        canonical_url="https://example.invalid/wave1-second",
        content_ref=additional_content_ref,
        content_hash=_content_hash(additional_source_content),
        byte_count=len(additional_source_content),
    )
    document = Wave1SourceIntakeResult(
        schema_version=1,
        bundle_id=bundle_id,
        generation=0,
        phase="wave1",
        work_id=spec.work_id,
        attempt_id=attempt.attempt_id,
        worker_role=spec.worker_role,
        spec_hash=spec.spec_hash,
        result_contract="wave1.source-intake",
        output_paths=(),
        source_ids=(source_ref.source_id, additional_source_ref.source_id),
        sources=(
            Wave1SourceRef(
                source_id=source_ref.source_id,
                canonical_url=source_ref.canonical_url,
                title="Synthetic Wave1 source",
                content_ref=source_ref.content_ref,
                content_hash=source_ref.content_hash,
                byte_count=source_ref.byte_count,
                is_new_vs_wave0=True,
            ),
            Wave1SourceRef(
                source_id=additional_source_ref.source_id,
                canonical_url=additional_source_ref.canonical_url,
                title="Synthetic Wave1 second source",
                content_ref=additional_source_ref.content_ref,
                content_hash=additional_source_ref.content_hash,
                byte_count=additional_source_ref.byte_count,
                is_new_vs_wave0=True,
            ),
        ),
        claims=(
            ClaimDraft(
                claim_id="claim:w1_storage",
                statement="Synthetic Wave1 claim.",
                support_refs=(source_ref.source_id, additional_source_ref.source_id),
            ),
        ),
        open_questions=(),
    )
    await writer.write_result(document)
    candidate = _candidate(
        bundle,
        spec,
        attempt.attempt_id,
        canonical_json_bytes(document),
        (source_ref, additional_source_ref),
    )
    await submit_candidate_if_active(
        controller,
        spec=spec,
        attempt=attempt,
        candidate=candidate,
        active_attempt_id=attempt.attempt_id,
        now=now,
    )


def _candidate(
    bundle: RunBundleRef,
    spec,
    attempt_id: str,
    result_bytes: bytes,
    source_refs: tuple[SourceRef, ...],
) -> CandidateResult:
    payload = {
        "schema_version": 1,
        "bundle_id": spec.bundle_id,
        "generation": spec.generation,
        "phase": spec.phase,
        "work_id": spec.work_id,
        "attempt_id": attempt_id,
        "worker_role": spec.worker_role,
        "spec_hash": spec.spec_hash,
        "result_contract": spec.result_contract,
        "result_ref": bundle_result_path(bundle, spec.work_id, attempt_id),
        "result_hash": _content_hash(result_bytes),
        "result_schema_version": spec.result_schema_version,
        "result_byte_count": len(result_bytes),
        "output_refs": (),
        "source_refs": source_refs,
    }
    payload["candidate_hash"] = compute_candidate_hash(payload)
    return CandidateResult.model_validate(payload)


def _content_hash(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    return "h_" + base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


__all__ = ["LiveSeedBundle", "build_live_seed_bundle"]
