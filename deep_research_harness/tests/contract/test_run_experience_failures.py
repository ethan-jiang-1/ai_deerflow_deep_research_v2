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
    LifecycleStatus,
    LifecycleAction,
    ResultCode,
    WorkUnitStorageReason,
)
from deerflow_deep_research.domain.run_experience import Fault, RunFailureCode, StartRun, Terminal
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.run_experience import ResearchRunExperience
from deerflow_deep_research.runtime.run_observation import BundleRunObservationPublisher, RunObservationStore

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


@pytest.mark.asyncio
async def test_admitted_terminal_diagnostic_has_no_external_support_fallback(tmp_path) -> None:
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path / "workspace")
    scope = ("experience-user", "experience-thread")
    bundle = await lifecycle.start(scope=scope, request_text="Research journal diagnostics.")
    state = await lifecycle.end(bundle=bundle, terminal_status=LifecycleStatus.BLOCKED)
    result = lifecycle.result_for_state(action=LifecycleAction.START, bundle=bundle, state=state).model_dump(mode="json")
    support_path = tmp_path / "support-records.jsonl"
    experience = ResearchRunExperience(
        transport=ReplayTransport([result]),
        mode="real",
        observation_publisher=BundleRunObservationPublisher(lifecycle=lifecycle, scope=scope),
    )

    update = await experience.handle(StartRun(question="Research journal diagnostics."))
    journal = await RunObservationStore(
        bundle_root=lifecycle.private_root(bundle),
        bundle_id=bundle.bundle_id.value,
    ).inspect(bundle_id=bundle.bundle_id.value)

    assert isinstance(update, Terminal)
    assert update.failure is not None
    assert update.failure.diagnostic_ref is not None
    assert not support_path.exists()
    assert journal.terminal_diagnostic_ref == update.failure.diagnostic_ref
    assert journal.terminal_diagnostic is not None
