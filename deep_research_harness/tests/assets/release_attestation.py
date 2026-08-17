"""Versioned release-attestation contracts and sensitivity scanning.

@impl EVH-005
@impl EVH-010
@impl EVH-024
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

RELEASE_INVARIANTS = (
    "accepted_evidence_present",
    "checkpoint_isolated",
    "citation_bindings_valid",
    "cleanup_complete",
    "lifecycle_trace_complete",
    "paths_contained",
    "report_artifacts_present",
    "terminal_completed",
)
RELEASE_SMOKE_INVARIANTS = (
    "confirmation_traversed",
    "report_nonempty",
    "report_contains_chinese",
    "minimum_cited_claims",
    "declared_source_set_only",
    "minimum_distinct_sources",
)
RELEASE_V2_INVARIANTS = tuple(sorted((*RELEASE_INVARIANTS, *RELEASE_SMOKE_INVARIANTS)))
SOURCE_LOCATOR = "release-evidence/evaluate-harden-deep-research-graph/task-6.6"
SOURCE_TARGET_SCOPE = ("deerflow_research/.reports/live", "deerflow_research/.reports/release")
MAX_ATTESTATION_BYTES = 16 * 1024
_RELEASE_SCENARIO_ID = "release-full-real-acceptance"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_SOURCE_SET_ID_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{0,63}$")
_SENSITIVE_RE = re.compile(
    r"(?i)(?:https?://|/(?:Users|home|private|tmp)/|(?:api[_-]?key|token|secret|authorization)[\"']?\s*[:=]\s*[\"']?(?!<redacted>)[^\s,}\"]+)"
)
_V1_ATTESTATION_FIELDS = {
    "schema_version",
    "scenario_id",
    "source_observation_date",
    "source_report_sha256",
    "attestation_base_revision",
    "run_revision",
    "source_run",
    "source_archive_scan",
    "attestation_scan",
}
_V2_ATTESTATION_FIELDS = {
    "schema_version",
    "scenario_id",
    "source_report_sha256",
    "source_run",
    "attestation_scan",
}
_V1_SOURCE_RUN_FIELDS = {
    "attempt_count",
    "retry_count",
    "hard_invariants",
    "accepted_count",
    "citation_claim_count",
    "citation_ref_count",
    "input_tokens",
    "output_tokens",
    "tool_calls",
    "wall_time_seconds",
}
_V2_SOURCE_RUN_FIELDS = {
    *_V1_SOURCE_RUN_FIELDS,
    "source_set_id",
    "distinct_source_count",
}
_SOURCE_RUN_COUNT_FIELDS = (
    "attempt_count",
    "retry_count",
    "accepted_count",
    "citation_claim_count",
    "citation_ref_count",
    "input_tokens",
    "output_tokens",
    "tool_calls",
)


def load_release_attestation(path: Path) -> dict[str, Any]:
    if not isinstance(path, Path):
        raise TypeError("release_attestation_path_required")
    raw = path.read_bytes()
    if not raw or len(raw) > MAX_ATTESTATION_BYTES:
        raise ValueError("release_attestation_size_invalid")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("release_attestation_json_invalid") from exc
    validate_release_attestation(value)
    scan_release_attestation(path)
    return value


def validate_release_attestation(value: Any) -> None:
    if not isinstance(value, dict):
        raise ValueError("release_attestation_fields_invalid")
    fields = set(value)
    schema_version = value.get("schema_version")
    if schema_version == 1:
        if fields == _V2_ATTESTATION_FIELDS:
            raise ValueError("release_attestation_schema_mixed")
        _validate_v1_release_attestation(value)
        return
    if schema_version == 2:
        if fields == _V1_ATTESTATION_FIELDS:
            raise ValueError("release_attestation_schema_mixed")
        _validate_v2_release_attestation(value)
        return
    if fields in {_V1_ATTESTATION_FIELDS, _V2_ATTESTATION_FIELDS}:
        raise ValueError("release_attestation_identity_invalid")
    raise ValueError("release_attestation_fields_invalid")


def _validate_v1_release_attestation(value: dict[str, Any]) -> None:
    if set(value) != _V1_ATTESTATION_FIELDS:
        raise ValueError("release_attestation_fields_invalid")
    if value["schema_version"] != 1 or value["scenario_id"] != _RELEASE_SCENARIO_ID:
        raise ValueError("release_attestation_identity_invalid")
    if not isinstance(value["source_observation_date"], str) or not _DATE_RE.fullmatch(
        value["source_observation_date"]
    ):
        raise ValueError("source_observation_date_invalid")
    if not isinstance(value["source_report_sha256"], str) or not _SHA256_RE.fullmatch(value["source_report_sha256"]):
        raise ValueError("source_report_sha256_invalid")
    if not isinstance(value["attestation_base_revision"], str) or not _REVISION_RE.fullmatch(
        value["attestation_base_revision"]
    ):
        raise ValueError("attestation_base_revision_invalid")
    if value["run_revision"] != "unknown" or value["run_revision"] == value["attestation_base_revision"]:
        raise ValueError("run_revision_invalid")
    _validate_v1_source_run(value["source_run"])
    _validate_source_archive_scan(value["source_archive_scan"])
    _validate_attestation_scan(value["attestation_scan"])


def _validate_v2_release_attestation(value: dict[str, Any]) -> None:
    if set(value) != _V2_ATTESTATION_FIELDS:
        raise ValueError("release_attestation_fields_invalid")
    if value["schema_version"] != 2 or value["scenario_id"] != _RELEASE_SCENARIO_ID:
        raise ValueError("release_attestation_identity_invalid")
    if not isinstance(value["source_report_sha256"], str) or not _SHA256_RE.fullmatch(value["source_report_sha256"]):
        raise ValueError("source_report_sha256_invalid")
    _assert_redacted_attestation(value)
    _validate_v2_source_run(value["source_run"])
    _validate_attestation_scan(value["attestation_scan"])


def _validate_v1_source_run(value: Any) -> None:
    if not isinstance(value, dict) or set(value) != _V1_SOURCE_RUN_FIELDS:
        raise ValueError("source_run_fields_invalid")
    invariants = value["hard_invariants"]
    if not isinstance(invariants, dict) or tuple(sorted(invariants)) != RELEASE_INVARIANTS:
        raise ValueError("release_invariants_invalid")
    if any(result is not True for result in invariants.values()):
        raise ValueError("release_invariants_invalid")
    if any(not _is_nonnegative_int(value[field]) for field in _SOURCE_RUN_COUNT_FIELDS):
        raise ValueError("source_run_counts_invalid")
    if value["attempt_count"] != 1 or value["retry_count"] != 0:
        raise ValueError("source_run_attempts_invalid")
    if not _is_valid_duration(value["wall_time_seconds"]):
        raise ValueError("source_run_duration_invalid")


def _validate_v2_source_run(value: Any) -> None:
    if not isinstance(value, dict) or set(value) != _V2_SOURCE_RUN_FIELDS:
        raise ValueError("source_run_fields_invalid")
    invariants = value["hard_invariants"]
    if not isinstance(invariants, dict) or tuple(sorted(invariants)) != RELEASE_V2_INVARIANTS:
        raise ValueError("release_invariants_invalid")
    if any(result is not True for result in invariants.values()):
        raise ValueError("release_invariants_invalid")
    if any(not _is_nonnegative_int(value[field]) for field in _SOURCE_RUN_COUNT_FIELDS):
        raise ValueError("source_run_counts_invalid")
    if not 1 <= value["attempt_count"] <= 2 or value["retry_count"] != value["attempt_count"] - 1:
        raise ValueError("source_run_attempts_invalid")
    if not _is_valid_duration(value["wall_time_seconds"]):
        raise ValueError("source_run_duration_invalid")
    if not isinstance(value["source_set_id"], str) or not _SOURCE_SET_ID_RE.fullmatch(value["source_set_id"]):
        raise ValueError("source_set_id_invalid")
    if (
        value["accepted_count"] < 1
        or value["citation_claim_count"] < 3
        or value["citation_ref_count"] < 3
        or value["distinct_source_count"] < 2
    ):
        raise ValueError("source_run_smoke_evidence_invalid")


def _validate_source_archive_scan(value: Any) -> None:
    fields = {"source_locator", "target_scope", "credential_values_absent", "raw_host_paths_absent"}
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError("archive_scan_fields_invalid")
    if value["source_locator"] != SOURCE_LOCATOR or value["target_scope"] != list(SOURCE_TARGET_SCOPE):
        raise ValueError("archive_scan_provenance_invalid")
    if value["credential_values_absent"] is not True or value["raw_host_paths_absent"] is not True:
        raise ValueError("archive_scan_verdict_invalid")


def _validate_attestation_scan(value: Any) -> None:
    fields = {"credential_values_absent", "raw_host_paths_absent"}
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError("attestation_scan_fields_invalid")
    if value["credential_values_absent"] is not True or value["raw_host_paths_absent"] is not True:
        raise ValueError("attestation_scan_verdict_invalid")


def _is_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_valid_duration(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 < value <= 1200


def _assert_redacted_attestation(value: dict[str, Any]) -> None:
    try:
        text = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("release_attestation_fields_invalid") from exc
    if _SENSITIVE_RE.search(text):
        raise ValueError("release_attestation_sensitive")


def scan_release_attestation(path: Path) -> dict[str, bool]:
    if not isinstance(path, Path):
        raise TypeError("release_attestation_path_required")
    raw = path.read_bytes()
    if not raw or len(raw) > MAX_ATTESTATION_BYTES:
        raise ValueError("release_attestation_size_invalid")
    text = raw.decode("utf-8", "strict")
    if _SENSITIVE_RE.search(text):
        raise ValueError("release_attestation_sensitive")
    return {"credential_values_absent": True, "raw_host_paths_absent": True}


def build_v2_release_attestation(source: dict[str, Any]) -> dict[str, Any]:
    """Return the bounded v2 projection for one complete successful release report."""

    source_run = _derive_v2_source_run(source)
    attestation = {
        "schema_version": 2,
        "scenario_id": _RELEASE_SCENARIO_ID,
        "source_report_sha256": _source_report_sha256(source),
        "source_run": source_run,
        "attestation_scan": {
            "credential_values_absent": True,
            "raw_host_paths_absent": True,
        },
    }
    validate_release_attestation(attestation)
    return attestation


def validate_attestation_source_run(attestation: dict[str, Any], source: dict[str, Any]) -> None:
    if not isinstance(attestation, dict):
        raise ValueError("attestation_source_run_mismatch")
    if attestation.get("schema_version") == 1:
        _validate_v1_attestation_source_run(attestation, source)
        return
    if attestation.get("schema_version") != 2:
        raise ValueError("attestation_source_run_mismatch")
    validate_release_attestation(attestation)
    if attestation["source_report_sha256"] != _source_report_sha256(source):
        raise ValueError("attestation_source_report_hash_mismatch")
    expected = _derive_v2_source_run(source)
    if attestation["source_run"] != expected:
        raise ValueError("attestation_source_run_mismatch")


def _validate_v1_attestation_source_run(attestation: dict[str, Any], source: dict[str, Any]) -> None:
    attempts = source.get("attempts")
    outcome = source.get("outcome_summary")
    invariants = source.get("hard_invariants")
    if not isinstance(attempts, list) or len(attempts) != 1 or not isinstance(outcome, dict):
        raise ValueError("attestation_source_run_invalid")
    attempt = attempts[0]
    expected = {
        "attempt_count": source.get("attempt_count"),
        "retry_count": source.get("retry_count"),
        "hard_invariants": invariants,
        "accepted_count": outcome.get("accepted_count"),
        "citation_claim_count": outcome.get("citation_claim_count"),
        "citation_ref_count": outcome.get("citation_ref_count"),
        "input_tokens": attempt.get("input_tokens"),
        "output_tokens": attempt.get("output_tokens"),
        "tool_calls": attempt.get("tool_calls"),
        "wall_time_seconds": attempt.get("wall_time_seconds"),
    }
    attested = attestation.get("source_run")
    if not isinstance(attested, dict):
        raise ValueError("attestation_source_run_mismatch")
    attested_duration = attested.get("wall_time_seconds")
    source_duration = expected.pop("wall_time_seconds")
    attested_without_duration = {key: value for key, value in attested.items() if key != "wall_time_seconds"}
    if attested_without_duration != expected or not (
        isinstance(attested_duration, (int, float))
        and isinstance(source_duration, (int, float))
        and math.isclose(attested_duration, source_duration, rel_tol=0, abs_tol=1e-6)
    ):
        raise ValueError("attestation_source_run_mismatch")


def _source_report_sha256(source: dict[str, Any]) -> str:
    if not isinstance(source, dict):
        raise ValueError("attestation_source_run_invalid")
    try:
        canonical = json.dumps(source, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("attestation_source_run_invalid") from exc
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _derive_v2_source_run(source: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(source, dict) or source.get("scenario_id") != _RELEASE_SCENARIO_ID:
        raise ValueError("attestation_source_run_invalid")
    invariants = source.get("hard_invariants")
    outcome = source.get("outcome_summary")
    attempts = source.get("attempts")
    if (
        not isinstance(invariants, dict)
        or tuple(sorted(invariants)) != RELEASE_V2_INVARIANTS
        or any(result is not True for result in invariants.values())
        or not isinstance(outcome, dict)
        or not isinstance(attempts, (list, tuple))
        or not attempts
    ):
        raise ValueError("attestation_source_run_invalid")
    if outcome.get("terminal_status") != "completed" or any(
        outcome.get(field) is not True
        for field in (
            "confirmation_traversed",
            "report_nonempty",
            "report_contains_chinese",
            "declared_source_set_only",
        )
    ):
        raise ValueError("attestation_source_run_invalid")
    input_tokens = 0
    output_tokens = 0
    tool_calls = 0
    wall_time_seconds = 0.0
    for index, attempt in enumerate(attempts, start=1):
        if (
            not isinstance(attempt, dict)
            or any(
                not _is_nonnegative_int(attempt.get(field)) for field in ("input_tokens", "output_tokens", "tool_calls")
            )
            or not _is_valid_duration(attempt.get("wall_time_seconds"))
        ):
            raise ValueError("attestation_source_run_invalid")
        if index == len(attempts) and attempt.get("error_code") is not None:
            raise ValueError("attestation_source_run_invalid")
        input_tokens += attempt["input_tokens"]
        output_tokens += attempt["output_tokens"]
        tool_calls += attempt["tool_calls"]
        wall_time_seconds += float(attempt["wall_time_seconds"])
    source_run = {
        "attempt_count": source.get("attempt_count"),
        "retry_count": source.get("retry_count"),
        "hard_invariants": dict(invariants),
        "accepted_count": outcome.get("accepted_count"),
        "citation_claim_count": outcome.get("citation_claim_count"),
        "citation_ref_count": outcome.get("citation_ref_count"),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tool_calls": tool_calls,
        "wall_time_seconds": wall_time_seconds,
        "source_set_id": outcome.get("declared_source_set_id"),
        "distinct_source_count": outcome.get("distinct_source_count"),
    }
    if source_run["attempt_count"] != len(attempts):
        raise ValueError("attestation_source_run_invalid")
    try:
        _validate_v2_source_run(source_run)
    except ValueError as exc:
        raise ValueError("attestation_source_run_invalid") from exc
    return source_run


__all__ = [
    "RELEASE_INVARIANTS",
    "RELEASE_SMOKE_INVARIANTS",
    "RELEASE_V2_INVARIANTS",
    "build_v2_release_attestation",
    "load_release_attestation",
    "scan_release_attestation",
    "validate_attestation_source_run",
    "validate_release_attestation",
]
