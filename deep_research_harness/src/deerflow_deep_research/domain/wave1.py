"""Frozen Wave1 result-contract models — worker output and claim structures.

@impl WON-002
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Sequence
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, field_validator, model_validator

from deerflow_deep_research.domain.critics import ClaimVerifierResult, SourceDiagnosticResult
from deerflow_deep_research.domain.lifecycle import LogicalPhase
from deerflow_deep_research.domain.work_units import (
    BUNDLE_ID_RE,
    CONTENT_HASH_RE,
    MAX_REQUIRED_OUTPUTS,
    MAX_SOURCE_REFS,
    SOURCE_ID_RE,
    WORKER_ROLE_RE,
    SourceRef,
    WorkUnitGateView,
    _FrozenModel,
    canonicalize_source_url,
)

CLAIM_ID_RE = re.compile(r"^claim:w1_[a-zA-Z0-9_-]{1,64}$")
MAX_CLAIMS_PER_WORK = 32
MAX_OPEN_QUESTIONS = 16
MAX_STATEMENT_CHARS = 2000
MAX_QUESTION_CHARS = 500
WAVE1_MINIMUM_NEW_SOURCE_URLS = 2
WAVE1_GATE_REVIEW_KEY = "__wave1_gate_review__"
WAVE1_REVIEW_SCHEMA_VERSION = 1
MAX_WAVE1_OPEN_QUESTION_PROJECTION = 64


class Wave1SemanticViolation(ValueError):
    """A deterministic Wave1 admission invariant did not hold."""


def canonicalize_wave0_urls(urls: Iterable[str]) -> frozenset[str]:
    """Return the canonical immutable Wave0 baseline or reject an invalid entry."""

    return frozenset(canonicalize_source_url(url) for url in urls)


def _validate_source_semantics(
    sources: Sequence[Wave1WorkerSource | Wave1SourceRef],
    claims: Sequence[ClaimDraft],
    *,
    wave0_urls: Iterable[str],
    expected_source_refs: Sequence[SourceRef] = (),
    require_newness_marker: bool,
) -> frozenset[str]:
    baseline = canonicalize_wave0_urls(wave0_urls)
    source_ids: set[str] = set()
    canonical_urls: set[str] = set()
    new_urls: set[str] = set()

    for source in sources:
        if source.source_id in source_ids:
            raise Wave1SemanticViolation("wave1_source_id_duplicate")
        source_ids.add(source.source_id)
        try:
            canonical_url = canonicalize_source_url(source.canonical_url)
        except ValueError as exc:
            raise Wave1SemanticViolation("wave1_source_url_invalid") from exc
        if canonical_url != source.canonical_url:
            raise Wave1SemanticViolation("wave1_source_url_not_canonical")
        if canonical_url in canonical_urls:
            raise Wave1SemanticViolation("wave1_source_url_duplicate")
        canonical_urls.add(canonical_url)
        is_new = canonical_url not in baseline
        if require_newness_marker and isinstance(source, Wave1SourceRef) and source.is_new_vs_wave0 != is_new:
            raise Wave1SemanticViolation("wave1_source_newness_mismatch")
        if is_new:
            new_urls.add(canonical_url)

    for claim in claims:
        if any(ref not in source_ids for ref in (*claim.support_refs, *claim.counter_refs)):
            raise Wave1SemanticViolation("wave1_claim_source_ref_foreign")

    if len(new_urls) < WAVE1_MINIMUM_NEW_SOURCE_URLS:
        raise Wave1SemanticViolation("wave1_new_source_floor_not_met")

    if expected_source_refs:
        by_source_id = {source.source_id: source.canonical_url for source in sources}
        observed = tuple((source.source_id, source.canonical_url) for source in expected_source_refs)
        expected = tuple((source_id, by_source_id.get(source_id)) for source_id, _url in observed)
        if tuple(source_id for source_id, _url in observed) != tuple(by_source_id):
            raise Wave1SemanticViolation("wave1_candidate_source_ids_mismatch")
        if any(
            expected_url != observed_url
            for (_source_id, expected_url), (_source_id2, observed_url) in zip(expected, observed, strict=True)
        ):
            raise Wave1SemanticViolation("wave1_candidate_source_url_mismatch")

    return frozenset(new_urls)


def validate_wave1_worker_output(
    output: Wave1WorkerOutput,
    *,
    wave0_urls: Iterable[str],
) -> frozenset[str]:
    """Validate pre-persistence Wave1 provenance, uniqueness, and source floor."""

    return _validate_source_semantics(
        output.sources,
        output.claims,
        wave0_urls=wave0_urls,
        require_newness_marker=False,
    )


def validate_wave1_source_intake_result(
    result: Wave1SourceIntakeResult,
    *,
    wave0_urls: Iterable[str],
    candidate_source_refs: Sequence[SourceRef] = (),
) -> frozenset[str]:
    """Recompute persisted Wave1 semantic facts before submission or gate use."""

    return _validate_source_semantics(
        result.sources,
        result.claims,
        wave0_urls=wave0_urls,
        expected_source_refs=candidate_source_refs,
        require_newness_marker=True,
    )


def _normalize_scoped_id(value: str, *, prefix: str) -> str:
    if not isinstance(value, str):
        raise ValueError("scoped_id_invalid")
    raw = value.strip()
    for known_prefix in ("claim:w1_", "q:w1_", "claim:", "question:", "q:"):
        if raw.lower().startswith(known_prefix):
            raw = raw[len(known_prefix) :]
            break
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", raw).strip("_-")[:64]
    if not slug:
        raise ValueError("scoped_id_invalid")
    return prefix + slug


def _normalize_source_id(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("source_id_invalid")
    raw = value.strip()
    if SOURCE_ID_RE.fullmatch(raw):
        return raw
    slug = re.sub(r"[^a-zA-Z0-9_.:-]+", "_", raw).strip("_.:-")[:64]
    if not slug:
        raise ValueError("source_id_invalid")
    return f"source:w1_{slug}"


class OpenQuestionState(StrEnum):
    RESOLVED = "resolved"
    TARGETED_SEARCH = "targeted_search"
    DEFERRED = "deferred"
    REQUIRES_INTERNAL_DATA = "requires_internal_data"


class ClaimDraft(_FrozenModel):
    """One claim extracted by a Wave1 evidence worker."""

    claim_id: str = Field(pattern=CLAIM_ID_RE.pattern)
    statement: str = Field(min_length=1, max_length=MAX_STATEMENT_CHARS)
    support_refs: Annotated[tuple[str, ...], Field(max_length=MAX_SOURCE_REFS)] = ()
    counter_refs: Annotated[tuple[str, ...], Field(max_length=MAX_SOURCE_REFS)] = ()

    @field_validator("claim_id", mode="before")
    @classmethod
    def normalize_claim_id(cls, value: str) -> str:
        return _normalize_scoped_id(value, prefix="claim:w1_")

    @model_validator(mode="after")
    def validate_refs_disjoint(self) -> ClaimDraft:
        overlap = set(self.support_refs) & set(self.counter_refs)
        if overlap:
            raise ValueError("support_and_counter_refs_overlap")
        return self


class OpenQuestion(_FrozenModel):
    """One open question recorded by a Wave1 worker."""

    question_id: str = Field(pattern=re.compile(r"^q:w1_[a-zA-Z0-9_-]{1,64}$"))
    question: str = Field(min_length=1, max_length=MAX_QUESTION_CHARS)
    state: OpenQuestionState

    @field_validator("question_id", mode="before")
    @classmethod
    def normalize_question_id(cls, value: str) -> str:
        return _normalize_scoped_id(value, prefix="q:w1_")

    @field_validator("state", mode="before")
    @classmethod
    def normalize_state(cls, value: str | OpenQuestionState) -> str | OpenQuestionState:
        if isinstance(value, OpenQuestionState):
            return value
        if not isinstance(value, str):
            raise ValueError("open_question_state_invalid")
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "resolved": OpenQuestionState.RESOLVED,
            "answered": OpenQuestionState.RESOLVED,
            "closed": OpenQuestionState.RESOLVED,
            "targeted_search": OpenQuestionState.TARGETED_SEARCH,
            "needs_more_research": OpenQuestionState.TARGETED_SEARCH,
            "needs_research": OpenQuestionState.TARGETED_SEARCH,
            "needs_evidence": OpenQuestionState.TARGETED_SEARCH,
            "open": OpenQuestionState.TARGETED_SEARCH,
            "unresolved": OpenQuestionState.TARGETED_SEARCH,
            "deferred": OpenQuestionState.DEFERRED,
            "later": OpenQuestionState.DEFERRED,
            "requires_internal_data": OpenQuestionState.REQUIRES_INTERNAL_DATA,
            "internal_data_required": OpenQuestionState.REQUIRES_INTERNAL_DATA,
        }
        try:
            return aliases[normalized]
        except KeyError as exc:
            raise ValueError("open_question_state_invalid") from exc


class Wave1SourceRef(_FrozenModel):
    """One source fetched by a Wave1 worker with new-vs-wave0 marking."""

    source_id: str = Field(pattern=SOURCE_ID_RE.pattern)
    canonical_url: str = Field(min_length=1, max_length=2048)
    title: str = Field(min_length=1, max_length=512)
    content_ref: str
    content_hash: str
    byte_count: int = Field(ge=1)
    is_new_vs_wave0: bool


class Wave1WorkerSource(_FrozenModel):
    """Model-proposed Wave1 source metadata before runtime authority fields."""

    source_id: str = Field(pattern=SOURCE_ID_RE.pattern)
    canonical_url: str = Field(min_length=1, max_length=2048)
    title: str = Field(min_length=1, max_length=512)

    @field_validator("source_id", mode="before")
    @classmethod
    def normalize_source_id(cls, value: str) -> str:
        return _normalize_source_id(value)

    @field_validator("canonical_url")
    @classmethod
    def normalize_url(cls, value: str) -> str:
        return canonicalize_source_url(value)


WAVE1_WORKER_OUTPUT_SCHEMA_VERSION = 1


class Wave1WorkerOutput(_FrozenModel):
    """The Wave1 evidence worker's structured output document (WON-002)."""

    schema_version: Literal[1]
    sources: Annotated[tuple[Wave1WorkerSource, ...], Field(max_length=MAX_SOURCE_REFS)] = ()
    source_ids: Annotated[tuple[str, ...], Field(max_length=MAX_SOURCE_REFS)] = ()
    claims: Annotated[tuple[ClaimDraft, ...], Field(max_length=MAX_CLAIMS_PER_WORK)] = ()
    open_questions: Annotated[tuple[OpenQuestion, ...], Field(max_length=MAX_OPEN_QUESTIONS)] = ()

    @model_validator(mode="before")
    @classmethod
    def normalize_provider_source_refs(cls, value: object) -> object:
        if not isinstance(value, dict):
            return value
        payload = dict(value)
        raw_sources = payload.get("sources")
        source_mapping: dict[str, str] = {}
        used_ids: set[str] = set()
        if isinstance(raw_sources, (tuple, list)):
            normalized_sources: list[object] = []
            for raw_source in raw_sources:
                if not isinstance(raw_source, dict):
                    normalized_sources.append(raw_source)
                    continue
                source = dict(raw_source)
                raw_id = source.get("source_id")
                if not isinstance(raw_id, str):
                    normalized_sources.append(source)
                    continue
                normalized_id = _normalize_source_id(raw_id)
                base_id = normalized_id
                suffix = 2
                while normalized_id in used_ids and source_mapping.get(str(raw_id)) != normalized_id:
                    normalized_id = f"{base_id}_{suffix}"
                    suffix += 1
                used_ids.add(normalized_id)
                source_mapping[raw_id] = normalized_id
                source["source_id"] = normalized_id
                normalized_sources.append(source)
            payload["sources"] = normalized_sources
        if isinstance(payload.get("source_ids"), (tuple, list)):
            payload["source_ids"] = [source_mapping.get(item, item) for item in payload["source_ids"]]
        raw_claims = payload.get("claims")
        if isinstance(raw_claims, (tuple, list)):
            normalized_claims: list[object] = []
            for raw_claim in raw_claims:
                if not isinstance(raw_claim, dict):
                    normalized_claims.append(raw_claim)
                    continue
                claim = dict(raw_claim)
                for field_name in ("support_refs", "counter_refs"):
                    refs = claim.get(field_name)
                    if isinstance(refs, (tuple, list)):
                        claim[field_name] = [source_mapping.get(ref, ref) for ref in refs]
                normalized_claims.append(claim)
            payload["claims"] = normalized_claims
        return payload

    @model_validator(mode="after")
    def validate_source_ids_match(self) -> Wave1WorkerOutput:
        declared = tuple(source.source_id for source in self.sources)
        if self.source_ids and declared != self.source_ids:
            raise ValueError("source_ids_mismatch")
        if len(set(declared)) != len(declared):
            raise ValueError("source_ids_duplicate")
        object.__setattr__(self, "source_ids", declared)
        return self


class Wave1SourceIntakeResult(_FrozenModel):
    """Controller-bound Wave1 result document written to the attempt root."""

    schema_version: Literal[1]
    bundle_id: str = Field(pattern=BUNDLE_ID_RE.pattern)
    generation: int = Field(ge=0, le=2)
    phase: Literal[LogicalPhase.WAVE1]
    work_id: str
    attempt_id: str
    worker_role: str = Field(pattern=WORKER_ROLE_RE.pattern)
    spec_hash: str = Field(pattern=CONTENT_HASH_RE.pattern)
    result_contract: Literal["wave1.source-intake"]
    output_paths: Annotated[tuple[str, ...], Field(max_length=MAX_REQUIRED_OUTPUTS)] = ()
    source_ids: Annotated[tuple[str, ...], Field(max_length=MAX_SOURCE_REFS)] = ()
    sources: Annotated[tuple[Wave1SourceRef, ...], Field(max_length=MAX_SOURCE_REFS)] = ()
    claims: Annotated[tuple[ClaimDraft, ...], Field(max_length=MAX_CLAIMS_PER_WORK)] = ()
    open_questions: Annotated[tuple[OpenQuestion, ...], Field(max_length=MAX_OPEN_QUESTIONS)] = ()

    @model_validator(mode="after")
    def validate_identity_and_sources(self) -> Wave1SourceIntakeResult:
        if not self.attempt_id.startswith(f"{self.work_id}_a"):
            raise ValueError("attempt_id_identity_mismatch")
        if tuple(source.source_id for source in self.sources) != self.source_ids:
            raise ValueError("source_ids_mismatch")
        return self


class Wave1OpenQuestionRef(_FrozenModel):
    """Ids-only ref of one targeted-search open question for the synthesis handoff.

    Deliberately carries no question text: the checkpointed projection stays bounded
    under ``MAX_CHECKPOINT_STATE_BYTES``, and the owning synthesis node resolves text
    from the accepted Wave1 result documents.
    """

    question_id: str = Field(pattern=re.compile(r"^q:w1_[a-zA-Z0-9_-]{1,64}$"))
    work_id: str = Field(pattern=r"^[A-Za-z0-9:_-]{1,128}$")


_QUESTION_ID_PREFIX = "q:w1_"
_MAX_QUESTION_ID_SUFFIX_CHARS = 64
_WORK_TAG_CHARS = 8


def work_scoped_question_id(work_id: str, question_id: str) -> str:
    """Namespace one worker-authored question id with its owning work.

    Independent Wave1 workers author ``q:w1_*`` ids without cross-work
    coordination, so two workers can mint the same id for different questions;
    the synthesis pre-model guard then fails the whole run typed
    (``wave1_open_question_id_collision``). Scoping every admitted id with a
    short digest of the owning work id makes cross-work collisions impossible
    by construction (any work-id shape, including rerun generations) while
    staying inside the id grammar and keeping the echoed id short enough for
    the model to reproduce. Within one work the suffix is kept verbatim, so
    repair-rerun idempotence (BUG-051) is unchanged.
    """

    if not isinstance(work_id, str) or not isinstance(question_id, str) or not work_id:
        raise ValueError("work_scoped_question_id_invalid")
    suffix = question_id[len(_QUESTION_ID_PREFIX) :] if question_id.startswith(_QUESTION_ID_PREFIX) else question_id
    tag = hashlib.sha256(work_id.encode("utf-8")).hexdigest()[:_WORK_TAG_CHARS]
    budget = _MAX_QUESTION_ID_SUFFIX_CHARS - len(tag) - 1
    return f"{_QUESTION_ID_PREFIX}{tag}_{suffix[:budget]}"


class Wave1GateReviewRow(_FrozenModel):
    """Bounded facts about one accepted Wave1 work item for gate evaluation."""

    work_id: str
    accepted_record_hash: str = Field(pattern=CONTENT_HASH_RE.pattern)
    distinct_new_url_count: int = Field(ge=0, le=64)
    source_diagnostic_present: bool
    claim_verifier_present: bool
    open_question_states: tuple[OpenQuestionState, ...] = ()
    open_questions: Annotated[tuple[Wave1OpenQuestionRef, ...], Field(max_length=MAX_OPEN_QUESTIONS)] = ()

    @model_validator(mode="after")
    def validate_open_question_refs(self) -> Wave1GateReviewRow:
        ids = tuple(ref.question_id for ref in self.open_questions)
        if ids != tuple(sorted(ids)) or len(ids) != len(set(ids)):
            raise ValueError("wave1_gate_review_open_questions_invalid")
        return self


class Wave1GateReview(_FrozenModel):
    """Frozen non-checkpointed Wave1 review projection."""

    rows: tuple[Wave1GateReviewRow, ...] = ()

    @model_validator(mode="after")
    def validate_order(self) -> Wave1GateReview:
        work_ids = tuple(row.work_id for row in self.rows)
        if work_ids != tuple(sorted(work_ids)) or len(work_ids) != len(set(work_ids)):
            raise ValueError("wave1_gate_review_rows_invalid")
        return self

    def validate_gate_view(self, view: WorkUnitGateView) -> None:
        expected = tuple(sorted(view.accepted_record_by_work_id.items()))
        actual = tuple((row.work_id, row.accepted_record_hash) for row in self.rows)
        if actual != expected:
            raise ValueError("wave1_gate_review_gate_view_mismatch")


class Wave1CriticKind(StrEnum):
    SOURCE_DIAGNOSTIC = "source_diagnostic"
    CLAIM_VERIFIER = "claim_verifier"


class Wave1SourceObservation(_FrozenModel):
    source_id: str
    canonical_url: str = Field(min_length=1, max_length=2048)
    title: str = Field(min_length=1, max_length=512)
    is_new_vs_wave0: Literal[True]

    @field_validator("canonical_url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        canonical = canonicalize_source_url(value)
        if canonical != value:
            raise ValueError("wave1_review_url_not_canonical")
        return value


class Wave1SourceDiagnosticAssignment(_FrozenModel):
    observations: tuple[Wave1SourceObservation, ...]

    @model_validator(mode="after")
    def validate_order(self) -> Wave1SourceDiagnosticAssignment:
        ids = tuple(observation.source_id for observation in self.observations)
        if not ids or ids != tuple(sorted(ids)) or len(ids) != len(set(ids)):
            raise ValueError("wave1_source_diagnostic_assignment_invalid")
        return self


class Wave1ClaimVerifierAssignment(_FrozenModel):
    claims: tuple[ClaimDraft, ...]
    assigned_new_source_ids: tuple[str, ...]

    @model_validator(mode="after")
    def validate_order(self) -> Wave1ClaimVerifierAssignment:
        claim_ids = tuple(claim.claim_id for claim in self.claims)
        source_ids = self.assigned_new_source_ids
        if (
            claim_ids != tuple(sorted(claim_ids))
            or len(claim_ids) != len(set(claim_ids))
            or not source_ids
            or source_ids != tuple(sorted(source_ids))
            or len(source_ids) != len(set(source_ids))
        ):
            raise ValueError("wave1_claim_verifier_assignment_invalid")
        return self


class Wave1ReviewArtifact(_FrozenModel):
    schema_version: Literal[WAVE1_REVIEW_SCHEMA_VERSION]
    critic_kind: Wave1CriticKind
    bundle_id: str
    generation: int = Field(ge=0, le=2)
    phase: Literal[LogicalPhase.WAVE1]
    work_id: str
    attempt_id: str
    accepted_record_hash: str = Field(pattern=CONTENT_HASH_RE.pattern)
    input_hash: str = Field(pattern=CONTENT_HASH_RE.pattern)
    result: SourceDiagnosticResult | ClaimVerifierResult

    @model_validator(mode="after")
    def validate_result_kind(self) -> Wave1ReviewArtifact:
        expected = (
            SourceDiagnosticResult if self.critic_kind is Wave1CriticKind.SOURCE_DIAGNOSTIC else ClaimVerifierResult
        )
        if not isinstance(self.result, expected):
            raise ValueError("wave1_review_result_kind_mismatch")
        if not self.attempt_id.startswith(f"{self.work_id}_a"):
            raise ValueError("wave1_review_attempt_identity_mismatch")
        return self


__all__ = [
    "ClaimDraft",
    "OpenQuestion",
    "OpenQuestionState",
    "WAVE1_GATE_REVIEW_KEY",
    "WAVE1_MINIMUM_NEW_SOURCE_URLS",
    "WAVE1_REVIEW_SCHEMA_VERSION",
    "MAX_WAVE1_OPEN_QUESTION_PROJECTION",
    "Wave1ClaimVerifierAssignment",
    "Wave1CriticKind",
    "Wave1ReviewArtifact",
    "Wave1SemanticViolation",
    "Wave1SourceDiagnosticAssignment",
    "Wave1SourceIntakeResult",
    "Wave1SourceObservation",
    "Wave1SourceRef",
    "Wave1GateReview",
    "Wave1GateReviewRow",
    "Wave1OpenQuestionRef",
    "Wave1WorkerOutput",
    "Wave1WorkerSource",
    "canonicalize_wave0_urls",
    "validate_wave1_source_intake_result",
    "validate_wave1_worker_output",
]
