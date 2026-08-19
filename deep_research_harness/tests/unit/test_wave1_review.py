"""Wave1-local immutable critic review artifacts.

@impl WON-003
"""

from __future__ import annotations

import pytest

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, bundle_source_content_path
from deerflow_deep_research.domain.critics import ClaimVerifierResult, SourceDiagnosticResult
from deerflow_deep_research.domain.lifecycle import LogicalPhase
from deerflow_deep_research.domain.wave1 import ClaimDraft
from deerflow_deep_research.domain.work_units import SubmissionRecord, canonical_json_bytes
from deerflow_deep_research.graph.nodes.wave1.review import (
    Wave1ClaimVerifierAssignment,
    Wave1CriticKind,
    Wave1SourceDiagnosticAssignment,
    Wave1SourceObservation,
    _canonical_critic_code,
    materialize_wave1_review_artifact,
    read_wave1_review_artifact,
)

BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "R" * 43), scope_bucket="s_" + "R" * 43)
BUNDLE_ID = BUNDLE.bundle_id.value
WORK_ID = "g0_wave1_w0000"
ATTEMPT_ID = f"{WORK_ID}_a00"
RECORD_HASH = "h_" + "R" * 43


class MemoryWriter:
    def __init__(self) -> None:
        self.files: dict[str, bytes] = {}

    async def write_source(self, relative_path: str, content: bytes) -> None:
        existing = self.files.get(relative_path)
        if existing is not None and existing != content:
            raise ValueError("artifact_write_conflict")
        self.files[relative_path] = content


class MemoryStore:
    def __init__(self, files: dict[str, bytes]) -> None:
        self.files = files

    async def read_canonical_bytes(self, relative_ref: str, *, max_bytes: int) -> bytes:
        try:
            return self.files[relative_ref]
        except KeyError as exc:
            raise FileNotFoundError(relative_ref) from exc


def _record(**updates) -> SubmissionRecord:
    return SubmissionRecord.model_construct(
        bundle_id=BUNDLE_ID,
        generation=0,
        phase=LogicalPhase.WAVE1,
        work_id=WORK_ID,
        attempt_id=ATTEMPT_ID,
        worker_role="wave1_extraction",
        spec_hash="h_" + "S" * 43,
        record_hash=RECORD_HASH,
        **updates,
    )


def _source_assignment() -> Wave1SourceDiagnosticAssignment:
    return Wave1SourceDiagnosticAssignment(
        observations=(
            Wave1SourceObservation(
                source_id="source:a",
                canonical_url="https://example.com/a",
                title="A",
                is_new_vs_wave0=True,
            ),
            Wave1SourceObservation(
                source_id="source:b",
                canonical_url="https://example.com/b",
                title="B",
                is_new_vs_wave0=True,
            ),
        )
    )


def _claim_assignment() -> Wave1ClaimVerifierAssignment:
    return Wave1ClaimVerifierAssignment(
        claims=(
            ClaimDraft(
                claim_id="claim:w1_a",
                statement="A claim.",
                support_refs=("source:a",),
            ),
        ),
        assigned_new_source_ids=("source:a", "source:b"),
    )


def _source_result(*, ids: tuple[str, ...] = ("source:a", "source:b")) -> SourceDiagnosticResult:
    return SourceDiagnosticResult.model_validate(
        {
            "schema_version": 1,
            "source_ids": list(ids),
            "sources": [
                {
                    "source_id": source_id,
                    "trust_tier": "medium",
                    "materiality": "primary",
                    "marketing_risk": False,
                    "cross_verification_need": True,
                }
                for source_id in ids
            ],
        }
    )


def _claim_result(*, claim_id: str = "claim:w1_a", refs: tuple[str, ...] = ("source:a",)) -> ClaimVerifierResult:
    return ClaimVerifierResult.model_validate(
        {
            "schema_version": 1,
            "claims": [
                {
                    "claim_id": claim_id,
                    "verdict": "supported",
                    "support_refs": list(refs),
                    "counter_refs": [],
                    "reason": "Bounded deterministic fixture.",
                }
            ],
        }
    )


async def test_source_diagnostic_artifact_binds_identity_orders_results_and_is_idempotent() -> None:
    writer = MemoryWriter()
    assignment = _source_assignment()
    reversed_result = _source_result(ids=("source:b", "source:a"))

    artifact = await materialize_wave1_review_artifact(
        writer,
        kind=Wave1CriticKind.SOURCE_DIAGNOSTIC,
        record=_record(),
        assignment=assignment,
        result=reversed_result,
    )
    repeated = await materialize_wave1_review_artifact(
        writer,
        kind=Wave1CriticKind.SOURCE_DIAGNOSTIC,
        record=_record(),
        assignment=assignment,
        result=reversed_result,
    )

    assert artifact == repeated
    assert tuple(source.source_id for source in artifact.result.sources) == ("source:a", "source:b")
    assert writer.files == {"review/source-diagnostic.json": canonical_json_bytes(artifact)}


async def test_source_diagnostic_rejects_partial_or_foreign_coverage_before_write() -> None:
    writer = MemoryWriter()
    with pytest.raises(ValueError, match="coverage_invalid"):
        await materialize_wave1_review_artifact(
            writer,
            kind=Wave1CriticKind.SOURCE_DIAGNOSTIC,
            record=_record(),
            assignment=_source_assignment(),
            result=_source_result(ids=("source:a",)),
        )
    assert writer.files == {}


async def test_claim_verifier_rejects_foreign_refs_and_conflicting_existing_bytes() -> None:
    writer = MemoryWriter()
    assignment = _claim_assignment()
    with pytest.raises(ValueError, match="ref_invalid"):
        await materialize_wave1_review_artifact(
            writer,
            kind=Wave1CriticKind.CLAIM_VERIFIER,
            record=_record(),
            assignment=assignment,
            result=_claim_result(refs=("source:foreign",)),
        )
    assert writer.files == {}

    await materialize_wave1_review_artifact(
        writer,
        kind=Wave1CriticKind.CLAIM_VERIFIER,
        record=_record(),
        assignment=assignment,
        result=_claim_result(),
    )
    with pytest.raises(ValueError, match="artifact_write_conflict"):
        await materialize_wave1_review_artifact(
            writer,
            kind=Wave1CriticKind.CLAIM_VERIFIER,
            record=_record(),
            assignment=assignment,
            result=ClaimVerifierResult.model_validate(
                {
                    "schema_version": 1,
                    "claims": [
                        {
                            "claim_id": "claim:w1_a",
                            "verdict": "uncertain",
                            "support_refs": [],
                            "counter_refs": [],
                            "reason": "Different immutable result.",
                        }
                    ],
                }
            ),
        )


async def test_read_artifact_requires_canonical_exact_identity_and_assignment_binding() -> None:
    writer = MemoryWriter()
    record = _record()
    assignment = _source_assignment()
    artifact = await materialize_wave1_review_artifact(
        writer,
        kind=Wave1CriticKind.SOURCE_DIAGNOSTIC,
        record=record,
        assignment=assignment,
        result=_source_result(),
    )
    path = bundle_source_content_path(BUNDLE, WORK_ID, ATTEMPT_ID, "review/source-diagnostic.json")
    store = MemoryStore({path: writer.files["review/source-diagnostic.json"]})

    assert (
        await read_wave1_review_artifact(
            store,
            kind=Wave1CriticKind.SOURCE_DIAGNOSTIC,
            record=record,
            assignment=assignment,
            bundle=BUNDLE,
        )
        == artifact
    )

    forged = artifact.model_copy(update={"accepted_record_hash": "h_" + "F" * 43})
    store.files[path] = canonical_json_bytes(forged)
    with pytest.raises(ValueError, match="wave1_review_artifact_invalid"):
        await read_wave1_review_artifact(
            store,
            kind=Wave1CriticKind.SOURCE_DIAGNOSTIC,
            record=record,
            assignment=assignment,
            bundle=BUNDLE,
        )


def _pydantic_shape_error() -> ValueError:
    """Build a real pydantic ValidationError (the masked BUG-058 failure class)."""

    try:
        SourceDiagnosticResult.model_validate(
            {"schema_version": 1, "sources": [{"source_id": "source:1"}], "source_ids": ["source:1"]}
        )
    except ValueError as exc:
        return exc
    raise AssertionError("expected a ValidationError")


def test_canonical_critic_code_keeps_closed_codes_and_falls_back() -> None:
    """The critic-boundary Journal fact retains only closed canonical codes."""

    assert _canonical_critic_code(ValueError("wave1_claim_verifier_output_json_invalid")) == (
        "wave1_claim_verifier_output_json_invalid"
    )
    assert _canonical_critic_code(ValueError("wave1_claim_verifier_coverage_invalid")) == (
        "wave1_claim_verifier_coverage_invalid"
    )
    assert _canonical_critic_code(ValueError("wave1_review_assignment_kind_invalid")) == (
        "wave1_review_assignment_kind_invalid"
    )
    assert _canonical_critic_code(_pydantic_shape_error()) == "wave1_review_output_shape_invalid"
    assert _canonical_critic_code(ValueError("unexpected detail")) == "wave1_review_output_invalid"


def test_source_diagnostic_prompt_declares_boolean_flag_bounds() -> None:
    """@impl EVC-001 — wave1 matches the targeted-critic boolean declaration.

    Observed as bug 058: the missing declaration let the model emit severity labels.
    """

    import json

    from deerflow_deep_research.graph.nodes.wave1.prompts import build_wave1_source_diagnostic_prompt

    request = build_wave1_source_diagnostic_prompt(
        [
            {
                "source_id": "carnegie_endowment",
                "canonical_url": "https://example.org/a",
                "title": "A",
                "is_new_vs_wave0": True,
            }
        ]
    )
    expected = json.loads(request.expected_output)
    assert expected["bounds"]["marketing_risk"] == "boolean"
    assert expected["bounds"]["cross_verification_need"] == "boolean"
    assert expected["bounds"]["trust_tier"] == "high | medium | low | untrusted"
    assert expected["bounds"]["materiality"] == "primary | secondary | peripheral"
    assert "true/false" in request.objective or "boolean" in request.objective
