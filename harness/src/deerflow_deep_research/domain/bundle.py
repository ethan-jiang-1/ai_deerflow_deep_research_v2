"""Canonical research-bundle paths and containment rules.

@impl WOU-003
@impl WOU-004
@impl WOU-006
@impl REG-009
@impl REG-010
"""

from __future__ import annotations

import re
import secrets
from dataclasses import dataclass
from enum import StrEnum

from deerflow_deep_research.domain.work_units import (
    ATTEMPT_ID_RE,
    WORK_ID_RE,
    canonicalize_source_url,
)

BUNDLE_ROOT = "workspace/deep-research"
BUNDLE_SCOPE_ROOT = f"{BUNDLE_ROOT}/scopes"
BUNDLE_HOST_SUBTREE = BUNDLE_SCOPE_ROOT.removeprefix("workspace/")
REQUEST_SUBTREE = "request"
WORK_SUBTREE = "work"
EVIDENCE_SUBTREE = "evidence"
SYNTHESIS_SUBTREE = "synthesis"
REVIEW_SUBTREE = "review"
FINAL_SUBTREE = "final"
DIAGNOSTICS_SUBTREE = "diagnostics"

BUNDLE_SUBTREES = (
    REQUEST_SUBTREE,
    WORK_SUBTREE,
    EVIDENCE_SUBTREE,
    SYNTHESIS_SUBTREE,
    REVIEW_SUBTREE,
    FINAL_SUBTREE,
    DIAGNOSTICS_SUBTREE,
)

DIAGNOSTICS_GATE_ATTEMPTS = "gate-attempts.jsonl"
EVIDENCE_LEDGER = "submissions.jsonl"
EVIDENCE_LOCK = ".submissions.lock"
MARKER_FILENAME = "marker.json"
PROFILE_FILENAME = "profile.json"
SYNTHESIS_FINDINGS_FILENAME = "findings.json"
FINAL_REPORT_FILENAME = "report.md"
FINAL_CITATION_MAP_FILENAME = "claim-citation-map.json"
READINESS_REPORT_PLAN_FILENAME = "report-plan.json"

_PROBE_TOKEN_RE = re.compile(r"^[0-9a-f]{32}$")
_BUNDLE_ID_RE = re.compile(r"^b_[A-Za-z0-9_-]{43}$")
_SCOPE_BUCKET_RE = re.compile(r"^s_[A-Za-z0-9_-]{43}$")
_STAGING_RE = re.compile(r"^\.submissions\.[0-9a-f]{32}\.tmp$")
_ALIAS_PROBE_RE = re.compile(r"^\.work-unit-probe-[0-9a-f]{32}$")
_FS_PROBE_RE = re.compile(r"^\.work-unit-fsprobe-[0-9a-f]{32}\.(?:lock|src|dst)$")
_DPT_CONTROL_NAMES = frozenset({"queue.json", "index.json", "status.json"})


class BundlePathKind(StrEnum):
    CONTENT = "content"
    EVIDENCE = "evidence"
    AUDIT = "audit"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class BundleId:
    """One opaque, public identity for an available Deep Research Run Bundle.

    A Bundle id is intentionally generated independently of the outer conversation.
    The runtime maps trusted scope to a private bucket; callers never select either a
    filesystem path or a scope bucket through this value.
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or _BUNDLE_ID_RE.fullmatch(self.value) is None:
            raise ValueError("bundle_id_invalid")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class RunBundleRef:
    """Runtime-bound Bundle selector for contained storage capabilities.

    ``scope_bucket`` is an internal opaque containment component produced from
    trusted runtime context. It is not a public control identity and has no durable
    lifecycle meaning beyond locating this selected Bundle during one operation.
    """

    bundle_id: BundleId
    scope_bucket: str

    def __post_init__(self) -> None:
        if not isinstance(self.bundle_id, BundleId):
            raise TypeError("bundle_id_required")
        if not isinstance(self.scope_bucket, str) or _SCOPE_BUCKET_RE.fullmatch(self.scope_bucket) is None:
            raise ValueError("scope_bucket_invalid")


def new_bundle_id() -> BundleId:
    """Allocate a fresh opaque id without deriving it from request or scope data."""
    return BundleId(f"b_{secrets.token_urlsafe(32)}")


def run_bundle_root(bundle: RunBundleRef) -> str:
    """Return the canonical virtual root from the selected runtime Bundle reference."""
    if not isinstance(bundle, RunBundleRef):
        raise TypeError("bundle_required")
    return f"{BUNDLE_SCOPE_ROOT}/{bundle.scope_bucket}/{bundle.bundle_id.value}"


def bundle_marker_path(bundle: RunBundleRef) -> str:
    """Return the Bootstrap marker path for one runtime-selected Bundle."""
    return f"{run_bundle_root(bundle)}/{REQUEST_SUBTREE}/{MARKER_FILENAME}"


def bundle_host_relative_root(bundle: RunBundleRef) -> str:
    """Return the selected Bundle path relative to a trusted host workspace root."""
    return run_bundle_root(bundle).removeprefix("workspace/")


def bundle_profile_path(bundle: RunBundleRef) -> str:
    """Return the profile artifact path for one preselected Bundle."""
    return f"{run_bundle_root(bundle)}/{REQUEST_SUBTREE}/{PROFILE_FILENAME}"


def bundle_evidence_ledger_path(bundle: RunBundleRef) -> str:
    """Return the contained evidence ledger path for one selected Bundle."""
    return f"{run_bundle_root(bundle)}/{EVIDENCE_SUBTREE}/{EVIDENCE_LEDGER}"


def bundle_evidence_lock_path(bundle: RunBundleRef) -> str:
    """Return the contained evidence lock path for one selected Bundle."""
    return f"{run_bundle_root(bundle)}/{EVIDENCE_SUBTREE}/{EVIDENCE_LOCK}"


def bundle_evidence_staging_path(bundle: RunBundleRef, token: str) -> str:
    """Return one contained ledger staging path for one selected Bundle."""
    return f"{run_bundle_root(bundle)}/{EVIDENCE_SUBTREE}/.submissions.{_require_probe_token(token)}.tmp"


def bundle_synthesis_findings_path(bundle: RunBundleRef) -> str:
    """Return the contained synthesis findings path for one selected Bundle."""
    return f"{run_bundle_root(bundle)}/{SYNTHESIS_SUBTREE}/{SYNTHESIS_FINDINGS_FILENAME}"


def bundle_readiness_report_plan_path(bundle: RunBundleRef) -> str:
    """Return the contained readiness-plan path for one selected Bundle."""
    return f"{run_bundle_root(bundle)}/{REVIEW_SUBTREE}/{READINESS_REPORT_PLAN_FILENAME}"


def bundle_final_report_path(bundle: RunBundleRef) -> str:
    """Return the contained final report path for one selected Bundle."""
    return f"{run_bundle_root(bundle)}/{FINAL_SUBTREE}/{FINAL_REPORT_FILENAME}"


def bundle_final_citation_map_path(bundle: RunBundleRef) -> str:
    """Return the contained final citation map path for one selected Bundle."""
    return f"{run_bundle_root(bundle)}/{FINAL_SUBTREE}/{FINAL_CITATION_MAP_FILENAME}"


def bundle_attempt_dir(bundle: RunBundleRef, work_id: str, attempt_id: str) -> str:
    """Return one work attempt root from the sole selected Bundle reference."""
    _require_work_attempt(work_id, attempt_id)
    return f"{run_bundle_root(bundle)}/{WORK_SUBTREE}/{work_id}/{attempt_id}"


def bundle_work_spec_path(bundle: RunBundleRef, work_id: str, attempt_id: str) -> str:
    """Return the canonical WorkSpec path beneath one selected Bundle."""
    return f"{bundle_attempt_dir(bundle, work_id, attempt_id)}/work-spec.json"


def bundle_first_work_spec_path(bundle: RunBundleRef, work_id: str) -> str:
    """Return the initial-attempt WorkSpec path beneath one selected Bundle."""
    if not isinstance(work_id, str) or not WORK_ID_RE.fullmatch(work_id):
        raise ValueError("work_id_invalid")
    return bundle_work_spec_path(bundle, work_id, f"{work_id}_a00")


def bundle_result_path(bundle: RunBundleRef, work_id: str, attempt_id: str) -> str:
    """Return the canonical result path beneath one selected Bundle."""
    return f"{bundle_attempt_dir(bundle, work_id, attempt_id)}/result.json"


def bundle_output_path(bundle: RunBundleRef, work_id: str, attempt_id: str, relative_output: str) -> str:
    """Return a declared output path beneath one selected Bundle."""
    relative = _canonical_relative(relative_output, label="output", max_length=256)
    if relative == "outputs" or relative.startswith("outputs/"):
        raise ValueError("output_must_be_relative_to_outputs")
    return f"{bundle_attempt_dir(bundle, work_id, attempt_id)}/outputs/{relative}"


def bundle_source_content_path(bundle: RunBundleRef, work_id: str, attempt_id: str, name: str) -> str:
    """Return one cached source-content path beneath the selected Bundle."""
    relative = _canonical_relative(name, label="source", max_length=256)
    return f"{bundle_attempt_dir(bundle, work_id, attempt_id)}/cache/{relative}"


def bundle_runtime_alias_probe_path(bundle: RunBundleRef, token: str) -> str:
    """Return a temporary diagnostics probe path beneath the selected Bundle."""
    _require_probe_token(token)
    return f"{run_bundle_root(bundle)}/{DIAGNOSTICS_SUBTREE}/.work-unit-probe-{token}"


def bundle_runtime_fs_probe_paths(bundle: RunBundleRef, token: str) -> tuple[str, str, str]:
    """Return contained lock/source/destination names for one storage probe."""
    _require_probe_token(token)
    root = f"{run_bundle_root(bundle)}/{DIAGNOSTICS_SUBTREE}/.work-unit-fsprobe-{token}"
    return (f"{root}.lock", f"{root}.src", f"{root}.dst")


def _require_probe_token(token: str) -> str:
    if not isinstance(token, str) or not _PROBE_TOKEN_RE.fullmatch(token):
        raise ValueError("probe_token_invalid")
    return token


def _canonical_relative(path: str, *, label: str, max_length: int = 1024) -> str:
    if not isinstance(path, str) or not path or len(path) > max_length or not path.isascii():
        raise ValueError(f"{label}_invalid")
    if path.startswith("/") or path.endswith("/") or "\\" in path or "\x00" in path:
        raise ValueError(f"{label}_invalid")
    if any(part in {"", ".", ".."} for part in path.split("/")):
        raise ValueError(f"{label}_invalid")
    return path


def _require_work_attempt(work_id: str, attempt_id: str) -> tuple[str, str]:
    if not isinstance(work_id, str) or not WORK_ID_RE.fullmatch(work_id):
        raise ValueError("work_id_invalid")
    match = ATTEMPT_ID_RE.fullmatch(attempt_id) if isinstance(attempt_id, str) else None
    if match is None or match.group("work_id") != work_id:
        raise ValueError("attempt_id_invalid")
    return work_id, attempt_id


def is_evidence_staging_name(name: str) -> bool:
    return isinstance(name, str) and _STAGING_RE.fullmatch(name) is not None


def bundle_diagnostics_path(bundle: RunBundleRef, name: str = DIAGNOSTICS_GATE_ATTEMPTS) -> str:
    if name != DIAGNOSTICS_GATE_ATTEMPTS:
        raise ValueError("diagnostic_unknown")
    return f"{run_bundle_root(bundle)}/{DIAGNOSTICS_SUBTREE}/{name}"


def prelaunch_fs_probe_names(token: str) -> tuple[str, str, str]:
    prefix = f".deep-research-work-unit-fsprobe-{_require_probe_token(token)}"
    return (f"{prefix}.lock", f"{prefix}.src", f"{prefix}.dst")


def _normalize_bundle_ref(path: str) -> str:
    canonical = _canonical_relative(path, label="bundle_ref")
    if not canonical.startswith(f"{BUNDLE_ROOT}/"):
        raise ValueError("bundle_ref_invalid")
    parts = canonical.split("/")
    if len(parts) < 5 or parts[:2] != ["workspace", "deep-research"]:
        raise ValueError("bundle_ref_invalid")
    if (
        parts[2] != "scopes"
        or _SCOPE_BUCKET_RE.fullmatch(parts[3]) is None
        or _BUNDLE_ID_RE.fullmatch(parts[4]) is None
    ):
        raise ValueError("bundle_ref_invalid")
    return canonical


def _bundle_tail_start(parts: list[str]) -> int:
    return 5


def bundle_ref_to_virtual(path: str, *, virtual_user_data_root: str = "/mnt/user-data") -> str:
    ref = _normalize_bundle_ref(path)
    if virtual_user_data_root != "/mnt/user-data":
        raise ValueError("virtual_root_invalid")
    return f"{virtual_user_data_root}/{ref}"


def relative_to_workspace_path(path: str) -> str:
    ref = _normalize_bundle_ref(path)
    return ref.removeprefix("workspace/")


def resolve_bundle_contained_path(
    write_path: str,
    *,
    bundle: RunBundleRef,
    work_id: str | None = None,
    attempt_id: str | None = None,
) -> str:
    """Validate a path against the sole runtime-selected Bundle reference."""
    if not isinstance(bundle, RunBundleRef):
        raise TypeError("bundle_required")
    try:
        normalized = _normalize_bundle_ref(write_path)
    except ValueError as exc:
        raise ValueError("path_not_contained") from exc
    if (work_id is None) != (attempt_id is None):
        raise ValueError("path_not_contained")
    try:
        root = bundle_attempt_dir(bundle, work_id, attempt_id) if work_id is not None else run_bundle_root(bundle)
    except ValueError as exc:
        raise ValueError("path_not_contained") from exc
    if normalized == root or normalized.startswith(f"{root}/"):
        return normalized
    raise ValueError("path_not_contained")


def classify_bundle_path(path: str) -> BundlePathKind:
    try:
        ref = _normalize_bundle_ref(path)
    except ValueError:
        return BundlePathKind.UNKNOWN
    parts = ref.split("/")
    tail = parts[_bundle_tail_start(parts) :]
    if not tail:
        return BundlePathKind.UNKNOWN
    subtree = tail[0]
    if subtree == DIAGNOSTICS_SUBTREE and len(tail) == 2:
        name = tail[1]
        if name == DIAGNOSTICS_GATE_ATTEMPTS or _ALIAS_PROBE_RE.fullmatch(name) or _FS_PROBE_RE.fullmatch(name):
            return BundlePathKind.AUDIT
    if subtree == EVIDENCE_SUBTREE and len(tail) == 2:
        name = tail[1]
        if name == EVIDENCE_LEDGER:
            return BundlePathKind.EVIDENCE
        if name == EVIDENCE_LOCK or _STAGING_RE.fullmatch(name):
            return BundlePathKind.AUDIT
    if subtree == REQUEST_SUBTREE and len(tail) == 2:
        name = tail[1]
        if name in {MARKER_FILENAME, PROFILE_FILENAME}:
            return BundlePathKind.CONTENT
    if subtree == FINAL_SUBTREE and len(tail) == 2:
        name = tail[1]
        if name in {FINAL_REPORT_FILENAME, FINAL_CITATION_MAP_FILENAME}:
            return BundlePathKind.CONTENT
    if subtree == WORK_SUBTREE and len(tail) >= 4:
        work_id, attempt_id = tail[1], tail[2]
        try:
            _require_work_attempt(work_id, attempt_id)
        except ValueError:
            return BundlePathKind.UNKNOWN
        artifact = "/".join(tail[3:])
        if artifact in {"work-spec.json", "result.json"} or artifact.startswith("outputs/"):
            if not any(name in _DPT_CONTROL_NAMES or name.endswith(".queue") for name in tail[3:]):
                return BundlePathKind.CONTENT
    return BundlePathKind.UNKNOWN


def is_audit_only(path: str) -> bool:
    return classify_bundle_path(path) is BundlePathKind.AUDIT


def dedupe_source_urls(urls: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for url in urls:
        canonical = canonicalize_source_url(url)
        if canonical in seen:
            continue
        seen.add(canonical)
        ordered.append(canonical)
    return tuple(ordered)


__all__ = [
    "ATTEMPT_ID_RE",
    "BUNDLE_HOST_SUBTREE",
    "BUNDLE_ROOT",
    "BUNDLE_SCOPE_ROOT",
    "BUNDLE_SUBTREES",
    "BundleId",
    "BundlePathKind",
    "DIAGNOSTICS_GATE_ATTEMPTS",
    "DIAGNOSTICS_SUBTREE",
    "EVIDENCE_LEDGER",
    "EVIDENCE_LOCK",
    "EVIDENCE_SUBTREE",
    "FINAL_SUBTREE",
    "FINAL_REPORT_FILENAME",
    "FINAL_CITATION_MAP_FILENAME",
    "MARKER_FILENAME",
    "PROFILE_FILENAME",
    "REQUEST_SUBTREE",
    "REVIEW_SUBTREE",
    "RunBundleRef",
    "SYNTHESIS_SUBTREE",
    "WORK_ID_RE",
    "WORK_SUBTREE",
    "bundle_attempt_dir",
    "bundle_diagnostics_path",
    "bundle_first_work_spec_path",
    "bundle_evidence_ledger_path",
    "bundle_evidence_lock_path",
    "bundle_evidence_staging_path",
    "bundle_final_citation_map_path",
    "bundle_final_report_path",
    "bundle_host_relative_root",
    "bundle_output_path",
    "bundle_profile_path",
    "bundle_readiness_report_plan_path",
    "bundle_runtime_alias_probe_path",
    "bundle_runtime_fs_probe_paths",
    "bundle_ref_to_virtual",
    "bundle_synthesis_findings_path",
    "bundle_result_path",
    "bundle_source_content_path",
    "bundle_work_spec_path",
    "canonicalize_source_url",
    "classify_bundle_path",
    "dedupe_source_urls",
    "is_audit_only",
    "is_evidence_staging_name",
    "new_bundle_id",
    "prelaunch_fs_probe_names",
    "relative_to_workspace_path",
    "resolve_bundle_contained_path",
    "run_bundle_root",
]
