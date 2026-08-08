"""Committed release attestation schema, provenance, and sensitivity.

@impl EVH-005
@impl EVH-010
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

import tests.assets.release_attestation as release_attestation
from tests.assets.release_attestation import (
    RELEASE_INVARIANTS,
    load_release_attestation,
    scan_release_attestation,
    validate_attestation_source_run,
    validate_release_attestation,
)

ATTESTATION = Path("docs/release-attestation-2026-07-17.json")
_V1_INVARIANTS = (
    "accepted_evidence_present",
    "checkpoint_isolated",
    "citation_bindings_valid",
    "cleanup_complete",
    "lifecycle_trace_complete",
    "paths_contained",
    "report_artifacts_present",
    "terminal_completed",
)
_V2_SMOKE_INVARIANTS = (
    "confirmation_traversed",
    "report_nonempty",
    "report_contains_chinese",
    "minimum_cited_claims",
    "declared_source_set_only",
    "minimum_distinct_sources",
)


def _synthetic_smoke_report() -> dict[str, object]:
    return {
        "scenario_id": "release-full-real-acceptance",
        "invocation": {
            "user_id": "release-e2e",
            "thread_id": "release-thread-redacted",
            "run_id": "release-run-redacted",
            "bundle_id": "r_redacted",
            "checkpoint_key": "h_redacted",
        },
        "attempt_count": 1,
        "retry_count": 0,
        "hard_invariants": {name: True for name in (*_V1_INVARIANTS, *_V2_SMOKE_INVARIANTS)},
        "outcome_summary": {
            "terminal_status": "completed",
            "lifecycle_trace": (
                "bootstrap",
                "hitl1",
                "topic_planning",
                "wave0",
                "wave1",
                "wave2_synthesis",
                "hitl2",
                "readiness",
                "final_delivery",
            ),
            "accepted_count": 3,
            "artifacts": ("final/report.md", "final/claim-citation-map.json"),
            "citation_claim_count": 3,
            "citation_ref_count": 3,
            "confirmation_traversed": True,
            "report_nonempty": True,
            "report_contains_chinese": True,
            "declared_source_set_id": "python-docs-3.12",
            "declared_source_set_only": True,
            "distinct_source_count": 2,
            "contained": True,
            "cleaned_up": True,
        },
        "attempts": [
            {
                "attempt": 1,
                "error_code": None,
                "wall_time_seconds": 1.0,
                "input_tokens": 100,
                "output_tokens": 200,
                "tool_calls": 3,
                "checkpoint_validation_error": None,
                "checkpoint_summary": None,
                "response_shapes": [],
            }
        ],
    }


def _source_report_sha256(source: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(source, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


def _synthetic_v2_attestation(source: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": 2,
        "scenario_id": "release-full-real-acceptance",
        "source_report_sha256": _source_report_sha256(source),
        "source_run": {
            "attempt_count": 1,
            "retry_count": 0,
            "hard_invariants": {name: True for name in (*_V1_INVARIANTS, *_V2_SMOKE_INVARIANTS)},
            "accepted_count": 3,
            "citation_claim_count": 3,
            "citation_ref_count": 3,
            "input_tokens": 100,
            "output_tokens": 200,
            "tool_calls": 3,
            "wall_time_seconds": 1.0,
            "source_set_id": "python-docs-3.12",
            "distinct_source_count": 2,
        },
        "attestation_scan": {
            "credential_values_absent": True,
            "raw_host_paths_absent": True,
        },
    }


def test_committed_release_attestation_preserves_frozen_accepted_evidence() -> None:
    attestation = load_release_attestation(ATTESTATION)

    assert RELEASE_INVARIANTS == _V1_INVARIANTS
    assert attestation["source_report_sha256"] == "36f41ca7c631320d05205f26afba9fbddcc0652e8f8323a7832e7816b7828146"
    assert attestation["attestation_base_revision"] == "665ca33575b0d7eb3a408d68956d0ac7b2669d47"
    assert attestation["run_revision"] == "unknown"
    assert attestation["attestation_base_revision"] != attestation["run_revision"]
    assert attestation["source_run"]["hard_invariants"] == {name: True for name in RELEASE_INVARIANTS}
    assert attestation["source_archive_scan"]["target_scope"] == [
        "deerflow_research/.reports/live",
        "deerflow_research/.reports/release",
    ]


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        (lambda value: value.pop("run_revision"), "release_attestation_fields_invalid"),
        (lambda value: value["source_run"]["hard_invariants"].pop("cleanup_complete"), "release_invariants_invalid"),
        (lambda value: value.update(run_revision=value["attestation_base_revision"]), "run_revision_invalid"),
        (
            lambda value: value["source_archive_scan"].update(source_locator="unknown"),
            "archive_scan_provenance_invalid",
        ),
        (lambda value: value["source_run"].update(executed_at="2026-07-17T00:00:00Z"), "source_run_fields_invalid"),
    ],
)
def test_release_attestation_rejects_minimal_schema_and_provenance_violations(mutation, error) -> None:
    value = deepcopy(json.loads(ATTESTATION.read_text(encoding="utf-8")))
    mutation(value)
    with pytest.raises(ValueError, match=error):
        validate_release_attestation(value)


def test_release_attestation_scan_catches_known_sensitive_fixture(tmp_path) -> None:
    invalid = tmp_path / "known-sensitive.json"
    invalid.write_text(json.dumps({"provider_url": "https://private.example/source"}), encoding="utf-8")

    with pytest.raises(ValueError, match="release_attestation_sensitive"):
        scan_release_attestation(invalid)


def test_release_attestation_scan_passes_committed_artifact() -> None:
    assert scan_release_attestation(ATTESTATION) == {
        "credential_values_absent": True,
        "raw_host_paths_absent": True,
    }


def test_release_attestation_source_run_mismatch_is_rejected() -> None:
    attestation = load_release_attestation(ATTESTATION)
    source = {
        "attempt_count": 1,
        "retry_count": 0,
        "hard_invariants": {name: True for name in RELEASE_INVARIANTS},
        "outcome_summary": {"accepted_count": 999, "citation_claim_count": 2, "citation_ref_count": 2},
        "attempts": [
            {
                "input_tokens": 37597,
                "output_tokens": 18591,
                "tool_calls": 12,
                "wall_time_seconds": 286.1884355,
            }
        ],
    }
    with pytest.raises(ValueError, match="attestation_source_run_mismatch"):
        validate_attestation_source_run(attestation, source)


def test_historical_v1_cannot_attest_the_current_model_led_smoke_shape() -> None:
    attestation = load_release_attestation(ATTESTATION)

    with pytest.raises(ValueError, match="attestation_source_run_mismatch"):
        validate_attestation_source_run(attestation, _synthetic_smoke_report())


def test_synthetic_v2_attestation_is_redacted_and_matches_a_complete_smoke_report() -> None:
    """@impl EVH-024"""
    source = _synthetic_smoke_report()
    attestation = _synthetic_v2_attestation(source)

    validate_release_attestation(attestation)
    validate_attestation_source_run(attestation, source)

    assert set(attestation) == {
        "schema_version",
        "scenario_id",
        "source_report_sha256",
        "source_run",
        "attestation_scan",
    }
    assert attestation["source_run"] == {
        "attempt_count": 1,
        "retry_count": 0,
        "hard_invariants": {name: True for name in (*_V1_INVARIANTS, *_V2_SMOKE_INVARIANTS)},
        "accepted_count": 3,
        "citation_claim_count": 3,
        "citation_ref_count": 3,
        "input_tokens": 100,
        "output_tokens": 200,
        "tool_calls": 3,
        "wall_time_seconds": 1.0,
        "source_set_id": "python-docs-3.12",
        "distinct_source_count": 2,
    }


def test_v2_builder_derives_the_closed_redacted_attestation_from_a_matching_report() -> None:
    """@impl EVH-024"""
    source = _synthetic_smoke_report()

    assert release_attestation.build_v2_release_attestation(source) == _synthetic_v2_attestation(source)


def test_v2_builder_rejects_an_incomplete_or_false_smoke_report() -> None:
    """@impl EVH-024"""
    incomplete = _synthetic_smoke_report()
    incomplete_invariants = incomplete["hard_invariants"]
    assert isinstance(incomplete_invariants, dict)
    incomplete_invariants.pop("minimum_distinct_sources")

    with pytest.raises(ValueError, match="attestation_source_run_invalid"):
        release_attestation.build_v2_release_attestation(incomplete)

    false_confirmation = _synthetic_smoke_report()
    false_outcome = false_confirmation["outcome_summary"]
    assert isinstance(false_outcome, dict)
    false_outcome["confirmation_traversed"] = False

    with pytest.raises(ValueError, match="attestation_source_run_invalid"):
        release_attestation.build_v2_release_attestation(false_confirmation)


def test_v2_attestation_rejects_a_mixed_schema_and_unmatched_report() -> None:
    """@impl EVH-024"""
    source = _synthetic_smoke_report()
    mixed = _synthetic_v2_attestation(source)
    mixed["schema_version"] = 1

    with pytest.raises(ValueError, match="release_attestation_schema_mixed"):
        validate_release_attestation(mixed)

    changed_source = deepcopy(source)
    changed_outcome = changed_source["outcome_summary"]
    assert isinstance(changed_outcome, dict)
    changed_outcome["distinct_source_count"] = 1
    with pytest.raises(ValueError, match="attestation_source_report_hash_mismatch"):
        validate_attestation_source_run(_synthetic_v2_attestation(source), changed_source)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda value: value["source_run"].update(source_set_id="https://private.example/forbidden"),
        lambda value: value["source_run"].update(report_body="a raw report body"),
        lambda value: value["source_run"].update(credential="api_key=not-redacted"),
    ],
)
def test_v2_attestation_rejects_url_body_and_credential_bearing_payloads(mutate) -> None:
    """@impl EVH-024"""
    attestation = _synthetic_v2_attestation(_synthetic_smoke_report())
    mutate(attestation)

    with pytest.raises(ValueError, match="release_attestation_sensitive|source_run_fields_invalid"):
        validate_release_attestation(attestation)
