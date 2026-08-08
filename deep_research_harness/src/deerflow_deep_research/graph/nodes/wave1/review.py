"""Bound Wave1 critic artifacts and the non-checkpointed gate review.

The module owns only local review construction. It never admits a candidate,
updates the ledger, or chooses a route.

@impl WON-003
@impl WON-004
"""

from __future__ import annotations

import base64
import hashlib
from collections.abc import Sequence
from dataclasses import dataclass

from deerflow_deep_research.domain.bundle import (
    RunBundleRef,
    bundle_source_content_path,
    bundle_work_spec_path,
)
from deerflow_deep_research.domain.critics import ClaimVerifierResult, SourceDiagnosticResult
from deerflow_deep_research.domain.invocation import WorkUnitControllerDependencies
from deerflow_deep_research.domain.lifecycle import LogicalPhase
from deerflow_deep_research.domain.node_spec import PolicyRef
from deerflow_deep_research.domain.wave1 import (
    WAVE1_GATE_REVIEW_KEY,
    WAVE1_REVIEW_SCHEMA_VERSION,
    Wave1ClaimVerifierAssignment,
    Wave1CriticKind,
    Wave1GateReview,
    Wave1GateReviewRow,
    Wave1ReviewArtifact,
    Wave1SourceDiagnosticAssignment,
    Wave1SourceIntakeResult,
    Wave1SourceObservation,
    canonicalize_wave0_urls,
    validate_wave1_source_intake_result,
)
from deerflow_deep_research.domain.work_units import (
    Attempt,
    AttemptArtifactWriter,
    SubmissionRecord,
    WorkSpec,
    WorkUnitGateView,
    _FrozenModel,
    canonical_json_bytes,
)
from deerflow_deep_research.domain.workflow_outcomes import InvocationFailure, invoke_and_normalize

from .prompts import (
    build_wave1_claim_verifier_prompt,
    build_wave1_source_diagnostic_prompt,
    parse_wave1_claim_verifier,
    parse_wave1_source_diagnostic,
)

_ASSIGNMENT_HASH_DOMAIN = b"deerflow-deep-research:wave1-review-assignment:v1\0"
_MAX_REVIEW_ARTIFACT_BYTES = 256 * 1024


@dataclass(frozen=True)
class _AcceptedWave1Work:
    record: SubmissionRecord
    document: Wave1SourceIntakeResult
    source_assignment: Wave1SourceDiagnosticAssignment
    claim_assignment: Wave1ClaimVerifierAssignment


def _content_hash(data: bytes) -> str:
    return "h_" + base64.urlsafe_b64encode(hashlib.sha256(data).digest()).decode("ascii").rstrip("=")


def _assignment_hash(kind: Wave1CriticKind, assignment: _FrozenModel) -> str:
    digest = hashlib.sha256(
        _ASSIGNMENT_HASH_DOMAIN + kind.value.encode("ascii") + b"\0" + canonical_json_bytes(assignment)
    ).digest()
    return "h_" + base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _review_cache_name(kind: Wave1CriticKind) -> str:
    return f"review/{kind.value.replace('_', '-')}.json"


def _source_assignment(document: Wave1SourceIntakeResult) -> Wave1SourceDiagnosticAssignment:
    observations = tuple(
        Wave1SourceObservation(
            source_id=source.source_id,
            canonical_url=source.canonical_url,
            title=source.title,
            is_new_vs_wave0=True,
        )
        for source in sorted(
            (source for source in document.sources if source.is_new_vs_wave0),
            key=lambda source: source.source_id,
        )
    )
    return Wave1SourceDiagnosticAssignment(observations=observations)


def _claim_assignment(
    document: Wave1SourceIntakeResult,
    source_assignment: Wave1SourceDiagnosticAssignment,
) -> Wave1ClaimVerifierAssignment:
    return Wave1ClaimVerifierAssignment(
        claims=tuple(sorted(document.claims, key=lambda claim: claim.claim_id)),
        assigned_new_source_ids=tuple(observation.source_id for observation in source_assignment.observations),
    )


def _bound_source_diagnostic(
    result: SourceDiagnosticResult,
    assignment: Wave1SourceDiagnosticAssignment,
) -> SourceDiagnosticResult:
    expected_ids = tuple(observation.source_id for observation in assignment.observations)
    by_id = {source.source_id: source for source in result.sources}
    if tuple(sorted(by_id)) != expected_ids or len(by_id) != len(result.sources):
        raise ValueError("wave1_source_diagnostic_coverage_invalid")
    return SourceDiagnosticResult(
        schema_version=1,
        sources=tuple(by_id[source_id] for source_id in expected_ids),
        source_ids=expected_ids,
    )


def _bound_claim_verifier(
    result: ClaimVerifierResult,
    assignment: Wave1ClaimVerifierAssignment,
) -> ClaimVerifierResult:
    expected_ids = tuple(claim.claim_id for claim in assignment.claims)
    assigned_sources = set(assignment.assigned_new_source_ids)
    by_id = {claim.claim_id: claim for claim in result.claims}
    if tuple(sorted(by_id)) != expected_ids or len(by_id) != len(result.claims):
        raise ValueError("wave1_claim_verifier_coverage_invalid")
    normalized = []
    for claim_id in expected_ids:
        claim = by_id[claim_id]
        refs = (*claim.support_refs, *claim.counter_refs)
        if any(ref not in assigned_sources for ref in refs):
            raise ValueError("wave1_claim_verifier_ref_invalid")
        normalized.append(
            claim.model_copy(
                update={
                    "support_refs": tuple(sorted(set(claim.support_refs))),
                    "counter_refs": tuple(sorted(set(claim.counter_refs))),
                }
            )
        )
    return ClaimVerifierResult(schema_version=1, claims=tuple(normalized))


def _build_artifact(
    *,
    kind: Wave1CriticKind,
    record: SubmissionRecord,
    assignment: Wave1SourceDiagnosticAssignment | Wave1ClaimVerifierAssignment,
    result: SourceDiagnosticResult | ClaimVerifierResult,
) -> Wave1ReviewArtifact:
    if kind is Wave1CriticKind.SOURCE_DIAGNOSTIC:
        if not isinstance(assignment, Wave1SourceDiagnosticAssignment) or not isinstance(
            result, SourceDiagnosticResult
        ):
            raise ValueError("wave1_review_assignment_kind_invalid")
        bound_result: SourceDiagnosticResult | ClaimVerifierResult = _bound_source_diagnostic(result, assignment)
    else:
        if not isinstance(assignment, Wave1ClaimVerifierAssignment) or not isinstance(result, ClaimVerifierResult):
            raise ValueError("wave1_review_assignment_kind_invalid")
        bound_result = _bound_claim_verifier(result, assignment)
    return Wave1ReviewArtifact(
        schema_version=WAVE1_REVIEW_SCHEMA_VERSION,
        critic_kind=kind,
        bundle_id=record.bundle_id,
        generation=record.generation,
        phase=record.phase,
        work_id=record.work_id,
        attempt_id=record.attempt_id,
        accepted_record_hash=record.record_hash,
        input_hash=_assignment_hash(kind, assignment),
        result=bound_result,
    )


async def materialize_wave1_review_artifact(
    writer: AttemptArtifactWriter,
    *,
    kind: Wave1CriticKind,
    record: SubmissionRecord,
    assignment: Wave1SourceDiagnosticAssignment | Wave1ClaimVerifierAssignment,
    result: SourceDiagnosticResult | ClaimVerifierResult,
) -> Wave1ReviewArtifact:
    """Validate and idempotently persist one identity-bound Wave1 review artifact."""

    artifact = _build_artifact(kind=kind, record=record, assignment=assignment, result=result)
    await writer.write_source(_review_cache_name(kind), canonical_json_bytes(artifact))
    return artifact


def _validate_read_artifact(
    artifact: Wave1ReviewArtifact,
    *,
    kind: Wave1CriticKind,
    record: SubmissionRecord,
    assignment: Wave1SourceDiagnosticAssignment | Wave1ClaimVerifierAssignment,
) -> Wave1ReviewArtifact:
    expected_identity = (
        kind,
        record.bundle_id,
        record.generation,
        record.phase,
        record.work_id,
        record.attempt_id,
        record.record_hash,
        _assignment_hash(kind, assignment),
    )
    actual_identity = (
        artifact.critic_kind,
        artifact.bundle_id,
        artifact.generation,
        artifact.phase,
        artifact.work_id,
        artifact.attempt_id,
        artifact.accepted_record_hash,
        artifact.input_hash,
    )
    if actual_identity != expected_identity:
        raise ValueError("wave1_review_artifact_identity_mismatch")
    _build_artifact(kind=kind, record=record, assignment=assignment, result=artifact.result)
    return artifact


async def read_wave1_review_artifact(
    store: object,
    *,
    kind: Wave1CriticKind,
    record: SubmissionRecord,
    assignment: Wave1SourceDiagnosticAssignment | Wave1ClaimVerifierAssignment,
    bundle: RunBundleRef,
) -> Wave1ReviewArtifact | None:
    """Read a canonical matching review artifact, returning ``None`` only when absent."""

    path = bundle_source_content_path(bundle, record.work_id, record.attempt_id, _review_cache_name(kind))
    try:
        raw = await store.read_canonical_bytes(path, max_bytes=_MAX_REVIEW_ARTIFACT_BYTES)  # type: ignore[union-attr]
    except FileNotFoundError:
        return None
    try:
        artifact = Wave1ReviewArtifact.model_validate_json(raw)
        if canonical_json_bytes(artifact) != raw:
            raise ValueError("wave1_review_artifact_noncanonical")
        return _validate_read_artifact(artifact, kind=kind, record=record, assignment=assignment)
    except ValueError as exc:
        raise ValueError("wave1_review_artifact_invalid") from exc


def _wave0_urls(records: Sequence[SubmissionRecord], *, bundle_id: str, generation: int) -> frozenset[str]:
    return canonicalize_wave0_urls(
        source.canonical_url
        for record in records
        if record.bundle_id == bundle_id and record.generation == generation and record.phase is LogicalPhase.WAVE0
        for source in record.source_refs
    )


async def _accepted_wave1_work(
    controller: WorkUnitControllerDependencies,
    *,
    record: SubmissionRecord,
    records: Sequence[SubmissionRecord],
) -> _AcceptedWave1Work:
    if record.phase is not LogicalPhase.WAVE1:
        raise ValueError("wave1_review_record_phase_invalid")
    try:
        raw = await controller.store.read_canonical_bytes(record.result_ref, max_bytes=_MAX_REVIEW_ARTIFACT_BYTES)
        if len(raw) != record.result_byte_count or _content_hash(raw) != record.result_hash:
            raise ValueError("wave1_review_result_integrity_invalid")
        document = Wave1SourceIntakeResult.model_validate_json(raw)
        if canonical_json_bytes(document) != raw:
            raise ValueError("wave1_review_result_noncanonical")
    except (FileNotFoundError, ValueError) as exc:
        raise ValueError("wave1_review_result_invalid") from exc
    if (
        document.bundle_id,
        document.generation,
        document.phase,
        document.work_id,
        document.attempt_id,
        document.worker_role,
        document.spec_hash,
    ) != (
        record.bundle_id,
        record.generation,
        record.phase,
        record.work_id,
        record.attempt_id,
        record.worker_role,
        record.spec_hash,
    ):
        raise ValueError("wave1_review_result_identity_mismatch")
    try:
        validate_wave1_source_intake_result(
            document,
            wave0_urls=_wave0_urls(records, bundle_id=record.bundle_id, generation=record.generation),
            candidate_source_refs=record.source_refs,
        )
    except ValueError as exc:
        raise ValueError("wave1_review_result_semantics_invalid") from exc
    source_assignment = _source_assignment(document)
    return _AcceptedWave1Work(
        record=record,
        document=document,
        source_assignment=source_assignment,
        claim_assignment=_claim_assignment(document, source_assignment),
    )


async def _load_spec_for_record(
    controller: WorkUnitControllerDependencies,
    record: SubmissionRecord,
    *,
    bundle: RunBundleRef,
) -> WorkSpec:
    path = bundle_work_spec_path(bundle, record.work_id, record.attempt_id)
    try:
        raw = await controller.store.read_canonical_bytes(path, max_bytes=16 * 1024)
        spec = WorkSpec.model_validate_json(raw)
        if canonical_json_bytes(spec) != raw:
            raise ValueError("wave1_review_spec_noncanonical")
    except (FileNotFoundError, ValueError) as exc:
        raise ValueError("wave1_review_spec_invalid") from exc
    if (
        spec.bundle_id,
        spec.generation,
        spec.phase,
        spec.work_id,
        spec.worker_role,
        spec.spec_hash,
    ) != (
        record.bundle_id,
        record.generation,
        record.phase,
        record.work_id,
        record.worker_role,
        record.spec_hash,
    ):
        raise ValueError("wave1_review_spec_identity_mismatch")
    return spec


async def _dispatch_missing_reviews(
    controller: WorkUnitControllerDependencies,
    work: _AcceptedWave1Work,
    *,
    missing: tuple[Wave1CriticKind, ...],
    bundle: RunBundleRef,
    policy: PolicyRef,
) -> None:
    spec = await _load_spec_for_record(controller, work.record, bundle=bundle)
    attempt = Attempt(
        schema_version=1,
        bundle_id=work.record.bundle_id,
        generation=work.record.generation,
        phase=work.record.phase,
        work_id=work.record.work_id,
        attempt_id=work.record.attempt_id,
        attempt_ordinal=int(work.record.attempt_id.rsplit("_a", 1)[1]),
        spec_hash=work.record.spec_hash,
        status="pending",
        created_at=work.record.submitted_at,
        started_at=None,
        expires_at=None,
        terminal_at=None,
        terminal_code=None,
    )
    resolved = await controller.resolver.resolve_worker(
        logical_name="wave1",
        work_spec=spec,
        attempt=attempt,
        policy=policy,
    )
    writer = resolved.artifact_writer
    if writer is None:
        raise ValueError("wave1_review_artifact_writer_missing")
    for kind in missing:
        if kind is Wave1CriticKind.SOURCE_DIAGNOSTIC:
            request = build_wave1_source_diagnostic_prompt(
                tuple(observation.model_dump(mode="python") for observation in work.source_assignment.observations)
            )
            parser = parse_wave1_source_diagnostic
            assignment: Wave1SourceDiagnosticAssignment | Wave1ClaimVerifierAssignment = work.source_assignment
        else:
            request = build_wave1_claim_verifier_prompt(
                tuple(claim.model_dump(mode="python") for claim in work.claim_assignment.claims),
                work.claim_assignment.assigned_new_source_ids,
            )
            parser = parse_wave1_claim_verifier
            assignment = work.claim_assignment
        outcome = await invoke_and_normalize(
            lambda request=request: resolved.node_dependencies.capabilities.run_agent(  # type: ignore[union-attr]
                context=resolved.node_dependencies.agent_context,
                request=request,
            ),
            phase="wave1",
        )
        if isinstance(outcome, InvocationFailure):
            continue
        try:
            critic_result = parser(outcome.result.summary)
            artifact = _build_artifact(
                kind=kind,
                record=work.record,
                assignment=assignment,
                result=critic_result,
            )
        except ValueError:
            continue
        await writer.write_source(_review_cache_name(kind), canonical_json_bytes(artifact))


async def build_wave1_gate_review(
    controller: WorkUnitControllerDependencies,
    *,
    gate_view: WorkUnitGateView,
    policy: PolicyRef,
) -> Wave1GateReview:
    """Dispatch only missing local critics, then construct the frozen review projection."""

    records = await controller.store.load_records()
    by_hash = {record.record_hash: record for record in records}
    bundle = getattr(controller.store, "bundle", None)
    if not isinstance(bundle, RunBundleRef):
        raise ValueError("selected_bundle_context_missing")
    rows: list[Wave1GateReviewRow] = []
    for work_id, record_hash in sorted(gate_view.accepted_record_by_work_id.items()):
        try:
            record = by_hash[record_hash]
        except KeyError as exc:
            raise ValueError("wave1_review_accepted_record_missing") from exc
        if record.work_id != work_id:
            raise ValueError("wave1_review_work_record_mismatch")
        work = await _accepted_wave1_work(controller, record=record, records=records)
        source_artifact = await read_wave1_review_artifact(
            controller.store,
            kind=Wave1CriticKind.SOURCE_DIAGNOSTIC,
            record=record,
            assignment=work.source_assignment,
            bundle=bundle,
        )
        claim_artifact = await read_wave1_review_artifact(
            controller.store,
            kind=Wave1CriticKind.CLAIM_VERIFIER,
            record=record,
            assignment=work.claim_assignment,
            bundle=bundle,
        )
        missing = tuple(
            kind
            for kind, artifact in (
                (Wave1CriticKind.SOURCE_DIAGNOSTIC, source_artifact),
                (Wave1CriticKind.CLAIM_VERIFIER, claim_artifact),
            )
            if artifact is None
        )
        if missing:
            await _dispatch_missing_reviews(
                controller,
                work,
                missing=missing,
                bundle=bundle,
                policy=policy,
            )
            source_artifact = await read_wave1_review_artifact(
                controller.store,
                kind=Wave1CriticKind.SOURCE_DIAGNOSTIC,
                record=record,
                assignment=work.source_assignment,
                bundle=bundle,
            )
            claim_artifact = await read_wave1_review_artifact(
                controller.store,
                kind=Wave1CriticKind.CLAIM_VERIFIER,
                record=record,
                assignment=work.claim_assignment,
                bundle=bundle,
            )
        rows.append(
            Wave1GateReviewRow(
                work_id=record.work_id,
                accepted_record_hash=record.record_hash,
                distinct_new_url_count=len(work.source_assignment.observations),
                source_diagnostic_present=source_artifact is not None,
                claim_verifier_present=claim_artifact is not None,
                open_question_states=tuple(question.state for question in work.document.open_questions),
            )
        )
    review = Wave1GateReview(rows=tuple(rows))
    review.validate_gate_view(gate_view)
    return review


__all__ = [
    "WAVE1_GATE_REVIEW_KEY",
    "WAVE1_REVIEW_SCHEMA_VERSION",
    "Wave1ClaimVerifierAssignment",
    "Wave1CriticKind",
    "Wave1GateReview",
    "Wave1GateReviewRow",
    "Wave1ReviewArtifact",
    "Wave1SourceDiagnosticAssignment",
    "Wave1SourceObservation",
    "build_wave1_gate_review",
    "materialize_wave1_review_artifact",
    "read_wave1_review_artifact",
]
