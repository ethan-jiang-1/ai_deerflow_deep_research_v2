"""One-shot local execution and immutable Bundle publication.

@impl CES-001
@impl CES-002
@impl CES-003
@impl CES-006
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from deerflow_deep_research.domain.evaluation import (
    EvaluationBundleManifest,
    EvaluationCase,
    EvidenceLayer,
    ExecutionResult,
    ExecutionStatus,
    FailureDetail,
    SubjectExecution,
)

Subject = Callable[["ExecutionContext"], Awaitable[SubjectExecution]]


class CaseAdmissionError(ValueError):
    pass


class BundleIntegrityError(ValueError):
    pass


class CaseRegistry:
    """The closed Case admission surface; it does not accept caller overrides."""

    def __init__(self, cases: tuple[EvaluationCase, ...]) -> None:
        index = {(case.case_id, case.version): case for case in cases}
        if not cases or len(index) != len(cases):
            raise ValueError("evaluation_case_registry_invalid")
        self._index = index

    def resolve(self, *, case_id: str, version: str) -> EvaluationCase:
        if not isinstance(case_id, str) or not case_id:
            raise CaseAdmissionError("evaluation_case_unknown")
        if not isinstance(version, str) or not version:
            raise CaseAdmissionError("evaluation_case_version_unknown")
        case = self._index.get((case_id, version))
        if case is not None:
            return case
        if any(registered_id == case_id for registered_id, _registered_version in self._index):
            raise CaseAdmissionError("evaluation_case_version_unknown")
        raise CaseAdmissionError("evaluation_case_unknown")


class ExecutionContext:
    """The only observation surface supplied to a declared production subject."""

    def __init__(self, *, workspace: Path, fixture: Mapping[str, Any]) -> None:
        self.workspace = workspace
        self.fixture = dict(fixture)
        self._observations: list[dict[str, Any]] = []

    def observe(self, kind: str, details: Mapping[str, Any]) -> None:
        if not isinstance(kind, str) or not kind or not isinstance(details, Mapping):
            raise ValueError("evaluation_observation_invalid")
        self._observations.append({"sequence": len(self._observations) + 1, "kind": kind, "details": dict(details)})

    @property
    def observations(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._observations)


class CognitiveEvaluationRunner:
    """Execute exactly one registered subject and publish its observed evidence."""

    def __init__(
        self,
        *,
        registry: CaseRegistry,
        runs_root: Path,
        subjects: Mapping[str, Subject],
        available_services: frozenset[str] = frozenset({"model", "web"}),
    ) -> None:
        self.registry = registry
        self.runs_root = runs_root
        self._subjects = dict(subjects)
        self._available_services = available_services

    async def run(self, *, case_id: str, version: str) -> ExecutionResult:
        return await self._run(case_id=case_id, version=version, evidence_layer=EvidenceLayer.DETERMINISTIC_HANDOFF)

    async def _run_selected_live(self, *, case_id: str, version: str) -> ExecutionResult:
        """Run only after the selected-live entrypoint has completed credential preflight."""

        return await self._run(
            case_id=case_id,
            version=version,
            evidence_layer=EvidenceLayer.CREDENTIALED_LIVE_QUALITY,
        )

    async def _run(
        self,
        *,
        case_id: str,
        version: str,
        evidence_layer: EvidenceLayer,
    ) -> ExecutionResult:
        case = self.registry.resolve(case_id=case_id, version=version)
        subject = self._subjects.get(case.subject)
        if subject is None:
            raise CaseAdmissionError("evaluation_subject_unavailable")

        execution_id = "e_" + secrets.token_hex(16)
        code_revision = await asyncio.to_thread(_code_revision)
        execution_root = self.runs_root / execution_id
        workspace = execution_root / "workspace"
        bundle_path = execution_root / "bundle"
        await asyncio.to_thread(_create_workspace, execution_root, workspace)
        context = ExecutionContext(workspace=workspace, fixture=case.fixture)
        context.observe("execution.started", {"case_id": case.case_id, "case_version": case.version})
        status = ExecutionStatus.COMPLETED
        execution: SubjectExecution | None = None
        failure: FailureDetail | None = None
        missing_services = set(case.required_services) - self._available_services
        if missing_services:
            status = ExecutionStatus.FAILED
            failure = FailureDetail(code="preflight_service_unavailable", phase="preflight")
            context.observe("preflight.failed", {"missing_services": sorted(missing_services)})
        else:
            try:
                context.observe("subject.started", {"subject": case.subject})
                started_at = time.monotonic()
                execution = await asyncio.wait_for(subject(context), timeout=case.bounds.timeout_seconds)
                if not isinstance(execution, SubjectExecution):
                    raise _MalformedSubjectResult
                execution = execution.model_copy(
                    update={
                        "resource_use": {
                            **execution.resource_use,
                            "latency_ms": max(0, round((time.monotonic() - started_at) * 1_000)),
                        }
                    }
                )
                _validate_resource_use(execution, case)
                context.observe("subject.completed", {"subject": case.subject})
            except asyncio.CancelledError:
                status = ExecutionStatus.FAILED
                failure = FailureDetail(code="execution_cancelled", phase="subject")
                context.observe("subject.cancelled", {})
            except TimeoutError:
                status = ExecutionStatus.FAILED
                failure = FailureDetail(code="execution_timeout", phase="subject")
                context.observe("subject.timeout", {})
            except _MalformedSubjectResult:
                status = ExecutionStatus.FAILED
                execution = None
                failure = FailureDetail(code="execution_malformed_output", phase="subject")
                context.observe("subject.malformed_output", {})
            except _ResourceBoundExceeded:
                status = ExecutionStatus.FAILED
                execution = None
                failure = FailureDetail(code="execution_resource_bound_exceeded", phase="subject")
                context.observe("subject.resource_bound_exceeded", {})
            except _ExecutionEvidenceInvalid:
                status = ExecutionStatus.FAILED
                execution = None
                failure = FailureDetail(code="execution_evidence_invalid", phase="subject")
                context.observe("subject.evidence_invalid", {})
            except Exception:
                status = ExecutionStatus.FAILED
                failure = FailureDetail(code="execution_failed", phase="subject")
                context.observe("subject.failed", {})

        await asyncio.to_thread(
            _publish_bundle,
            bundle_path,
            execution_id,
            case,
            status,
            context.observations,
            execution,
            failure,
            evidence_layer,
            code_revision,
        )
        return ExecutionResult(execution_id=execution_id, status=status, bundle_path=bundle_path)


def verify_bundle(*, bundle_path: Path, runs_root: Path) -> EvaluationBundleManifest:
    """Verify a published Bundle without granting write or execution authority."""

    try:
        resolved_root = runs_root.resolve(strict=False)
        resolved_bundle = bundle_path.resolve(strict=True)
        resolved_bundle.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise BundleIntegrityError("bundle_path_invalid") from exc
    if bundle_path.is_symlink() or not bundle_path.is_dir():
        raise BundleIntegrityError("bundle_path_invalid")
    try:
        raw_manifest = (bundle_path / "manifest.json").read_bytes()
        manifest = EvaluationBundleManifest.model_validate_json(raw_manifest)
    except Exception as exc:
        raise BundleIntegrityError("bundle_manifest_invalid") from exc
    for name, expected_digest in manifest.content_digests.items():
        path = bundle_path / name
        if not path.is_file() or path.is_symlink():
            raise BundleIntegrityError("bundle_record_missing")
        actual_digest = _digest(path.read_bytes())
        if actual_digest != expected_digest:
            raise BundleIntegrityError("bundle_digest_mismatch")
    return manifest


def bundle_digest(bundle_path: Path) -> str:
    return _digest((bundle_path / "manifest.json").read_bytes())


def _create_workspace(execution_root: Path, workspace: Path) -> None:
    execution_root.mkdir(parents=True, mode=0o700)
    os.chmod(execution_root, 0o700)
    workspace.mkdir(mode=0o700)
    os.chmod(workspace, 0o700)


class _MalformedSubjectResult(Exception):
    pass


class _ResourceBoundExceeded(Exception):
    pass


class _ExecutionEvidenceInvalid(Exception):
    pass


def _validate_resource_use(execution: SubjectExecution, case: EvaluationCase) -> None:
    model_calls = execution.resource_use.get("model_calls", 0)
    tool_calls = execution.resource_use.get("tool_calls", 0)
    if (
        not isinstance(model_calls, int)
        or isinstance(model_calls, bool)
        or not isinstance(tool_calls, int)
        or isinstance(tool_calls, bool)
        or model_calls < 0
        or tool_calls < 0
        or model_calls > case.bounds.max_model_calls
        or tool_calls > case.bounds.max_tool_calls
    ):
        raise _ResourceBoundExceeded
    plan = case.execution_plan
    if plan is None:
        return
    missing = set(plan.required_resource_fields) - set(execution.resource_use)
    if missing:
        raise _ExecutionEvidenceInvalid
    for control in plan.runtime_controls:
        if execution.resource_use.get(control.name) != control.digest:
            raise _ExecutionEvidenceInvalid
    for field in ("provider", "model", "composed_prompt_digest"):
        value = execution.resource_use.get(field)
        if not isinstance(value, str) or not value.strip() or len(value) > 256:
            raise _ExecutionEvidenceInvalid
    integer_fields = ("input_tokens", "output_tokens", "latency_ms")
    if not all(_nonnegative_int(execution.resource_use.get(field)) for field in integer_fields):
        raise _ExecutionEvidenceInvalid
    cost = execution.resource_use.get("cost_usd")
    if not isinstance(cost, (int, float)) or isinstance(cost, bool) or cost < 0:
        raise _ExecutionEvidenceInvalid


def _nonnegative_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _code_revision() -> str | None:
    """Best-effort provenance: the git worktree revision of this executing code.

    Returns None outside a git worktree (or without a git binary) so the manifest
    stays valid without claiming a revision it cannot honestly name (CES-003).
    """

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parent,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    revision = result.stdout.strip()
    return revision or None


def _publish_bundle(
    bundle_path: Path,
    execution_id: str,
    case: EvaluationCase,
    status: ExecutionStatus,
    observations: tuple[dict[str, Any], ...],
    execution: SubjectExecution | None,
    failure: FailureDetail | None,
    evidence_layer: EvidenceLayer,
    code_revision: str | None,
) -> None:
    staging = bundle_path.parent / ".bundle-staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(mode=0o700)
    records: dict[str, bytes] = {
        "inputs.json": _json_bytes(
            {
                "fixture": case.fixture,
                "required_services": case.required_services,
                "execution_plan": case.execution_plan.model_dump(mode="json") if case.execution_plan else None,
            }
        ),
        "observations.json": _json_bytes(observations),
        "output.json": _json_bytes(execution.output if execution is not None else {}),
        "artifacts.json": _json_bytes(execution.artifacts if execution is not None else {}),
        "resources.json": _json_bytes(execution.resource_use if execution is not None else {}),
        "diagnostics.json": _json_bytes({"failure": failure.model_dump(mode="json") if failure else None}),
    }
    for name, content in records.items():
        _atomic_write(staging / name, content)
    manifest = EvaluationBundleManifest(
        execution_id=execution_id,
        case_id=case.case_id,
        case_version=case.version,
        status=status,
        evidence_layer=evidence_layer,
        controls=case.controls,
        content_digests={name: _digest(content) for name, content in records.items()},
        failure=failure,
        code_revision=code_revision,
    )
    _atomic_write(staging / "manifest.json", manifest.model_dump_json(indent=2).encode("utf-8") + b"\n")
    os.replace(staging, bundle_path)
    os.chmod(bundle_path, 0o500)


def _atomic_write(path: Path, content: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("xb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=_json_default) + "\n"
    ).encode("utf-8")


def _json_default(value: Any) -> Any:
    """Materialize only established structured runtime values into Bundle evidence."""

    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return model_dump(mode="json")
    raise TypeError(f"evaluation_evidence_not_serializable:{type(value).__name__}")


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
