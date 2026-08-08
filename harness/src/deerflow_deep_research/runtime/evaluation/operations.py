"""Explicit operator/Coding-Agent handoff for local evaluation operations.

The adapter only invokes already-configured Runner and Review services. It does not
construct production dependencies, judge quality, or schedule work.
"""

from __future__ import annotations

from .contracts import EvaluationOperationResult, ReviewSubmission
from .review import EvaluationReviewService
from .runner import BundleIntegrityError, CaseAdmissionError, CognitiveEvaluationRunner


class EvaluationOperations:
    """Return stable references and bounded failure diagnostics for explicit actions."""

    def __init__(self, *, runner: CognitiveEvaluationRunner, review: EvaluationReviewService) -> None:
        self._runner = runner
        self._review = review

    async def run(self, *, case_id: str, version: str) -> EvaluationOperationResult:
        try:
            execution = await self._runner.run(case_id=case_id, version=version)
        except CaseAdmissionError as exc:
            return EvaluationOperationResult(operation="run", diagnostic=str(exc))
        return EvaluationOperationResult(
            operation="run",
            reference=str(execution.bundle_path),
            status=execution.status.value,
        )

    async def review(self, submission: ReviewSubmission) -> EvaluationOperationResult:
        try:
            record = await self._review.submit(submission)
        except (BundleIntegrityError, CaseAdmissionError) as exc:
            return EvaluationOperationResult(operation="review", diagnostic=str(exc))
        return EvaluationOperationResult(operation="review", reference=str(record.path), status=record.result.value)
