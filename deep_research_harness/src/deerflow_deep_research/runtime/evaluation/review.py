"""Read-only Review Record admission for immutable Evaluation Bundles.

@impl CES-004
@impl CES-005
@impl CES-006
"""

from __future__ import annotations

import asyncio
import json
import os
import secrets
from datetime import UTC, datetime
from pathlib import Path

from deerflow_deep_research.domain.evaluation import ExecutionStatus, ReviewRecord, ReviewSubmission

from .runner import BundleIntegrityError, CaseRegistry, bundle_digest, verify_bundle


class EvaluationReviewService:
    """Validate and store a review without access to Runner execution operations."""

    def __init__(self, *, registry: CaseRegistry, runs_root: Path) -> None:
        self._registry = registry
        self._runs_root = runs_root

    async def submit(self, submission: ReviewSubmission) -> ReviewRecord:
        manifest = await asyncio.to_thread(
            verify_bundle,
            bundle_path=submission.bundle_path,
            runs_root=self._runs_root,
        )
        if manifest.status is not ExecutionStatus.COMPLETED:
            raise BundleIntegrityError("bundle_execution_not_reviewable")
        case = self._registry.resolve(case_id=manifest.case_id, version=manifest.case_version)
        if submission.controls != case.controls or submission.controls != manifest.controls:
            raise BundleIntegrityError("bundle_control_identity_mismatch")
        review_id = "r_" + secrets.token_hex(16)
        path = submission.bundle_path.parent / "reviews" / review_id / "record.json"
        digest = await asyncio.to_thread(bundle_digest, submission.bundle_path)
        reviewed_at = datetime.now(UTC)
        payload = {
            "schema_version": 1,
            "review_id": review_id,
            "bundle_digest": digest,
            "case_id": manifest.case_id,
            "case_version": manifest.case_version,
            "evidence_layer": manifest.evidence_layer.value,
            "controls": [control.model_dump(mode="json") for control in submission.controls],
            "evaluator": submission.evaluator,
            "reviewed_at": reviewed_at.isoformat(),
            "result": submission.result.value,
            "evidence": list(submission.evidence),
            "confidence": submission.confidence,
            "unknowns": list(submission.unknowns),
            "variance": list(submission.variance),
            "owning_seam": submission.owning_seam,
            "follow_up": submission.follow_up,
        }
        await asyncio.to_thread(_write_record, path, payload)
        return ReviewRecord(
            review_id=review_id,
            path=path,
            bundle_digest=digest,
            evaluator=submission.evaluator,
            result=submission.result,
            reviewed_at=reviewed_at,
            case_id=manifest.case_id,
            case_version=manifest.case_version,
            evidence_layer=manifest.evidence_layer,
            controls=submission.controls,
            evidence=submission.evidence,
            confidence=submission.confidence,
            unknowns=submission.unknowns,
            variance=submission.variance,
            owning_seam=submission.owning_seam,
            follow_up=submission.follow_up,
        )


def _write_record(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, mode=0o700)
    temporary = path.with_name(".record.json.tmp")
    encoded = (json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")
    with temporary.open("xb") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)
