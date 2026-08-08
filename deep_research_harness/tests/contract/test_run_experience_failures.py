"""Safe Bundle-result failure projection at the shared run-experience seam.

@impl RER-003
@impl RER-009
@impl RER-013
@impl REG-013
@impl RER-008
"""

from __future__ import annotations

from collections import deque
from typing import Any

import pytest

from deerflow_deep_research.domain.lifecycle import (
    BundleAvailability,
    BundleControlResult,
    BundleRefinementProjection,
    Durability,
    InfrastructureResultCode,
    LegalNextAction,
    LifecycleAction,
    ResultCode,
    WorkUnitStorageReason,
)
from deerflow_deep_research.domain.run_experience import Fault, RunFailureCode, StartRun
from deerflow_deep_research.runtime.run_experience import ResearchRunExperience

BUNDLE_ID = "b_" + "B" * 43
SENTINEL = "secret=sentinel /Users/alice/private https://provider.invalid/body"


class ReplayTransport:
    def __init__(self, results: list[object]) -> None:
        self._results = deque(results)

    async def dispatch(self, **_kwargs: Any) -> object:
        result = self._results.popleft()
        if isinstance(result, BaseException):
            raise result
        return result


@pytest.mark.asyncio
async def test_unavailable_bundle_is_truthful_and_does_not_expose_legacy_observation_facts() -> None:
    result = BundleControlResult(
        action=LifecycleAction.STATUS,
        code=ResultCode.UNAVAILABLE,
        availability=BundleAvailability.UNAVAILABLE,
        durability=Durability.UNAVAILABLE,
        legal_next_action=LegalNextAction.START,
    ).model_dump(mode="json")

    update = await ResearchRunExperience(transport=ReplayTransport([result]), mode="real").handle(
        StartRun(question="Compare storage options")
    )

    assert isinstance(update, Fault)
    assert update.failure.code is RunFailureCode.BUNDLE_UNAVAILABLE
    assert BUNDLE_ID not in update.model_dump_json()
    assert '"bundle_id":null' in update.model_dump_json()
    assert "独立的新研究运行" in update.failure.next_action


@pytest.mark.asyncio
async def test_storage_failure_projects_a_closed_failure_category_without_a_second_lifecycle_source() -> None:
    result = BundleControlResult(
        action=LifecycleAction.START,
        code=InfrastructureResultCode.WORK_UNIT_STORAGE_UNAVAILABLE,
        availability=BundleAvailability.AVAILABLE,
        durability=Durability.SAME_PROCESS,
        bundle_id=BUNDLE_ID,
        infrastructure_reason=WorkUnitStorageReason.THREAD_MOUNT_UNAVAILABLE,
        refinement=BundleRefinementProjection(disposition="none"),
    ).model_dump(mode="json")

    update = await ResearchRunExperience(transport=ReplayTransport([result]), mode="real").handle(
        StartRun(question="Compare storage options")
    )

    assert isinstance(update, Fault)
    assert update.failure.code is RunFailureCode.PERSISTENCE_UNAVAILABLE
    assert SENTINEL not in update.model_dump_json()


@pytest.mark.asyncio
async def test_runtime_exception_is_redacted_as_a_safe_internal_failure() -> None:
    update = await ResearchRunExperience(
        transport=ReplayTransport([RuntimeError(SENTINEL)]),
        mode="real",
    ).handle(StartRun(question="Compare storage options"))

    assert isinstance(update, Fault)
    assert update.failure.code is RunFailureCode.INTERNAL_UNEXPECTED
    assert SENTINEL not in update.model_dump_json()
