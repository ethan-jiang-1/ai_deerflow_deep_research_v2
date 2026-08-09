"""Shared Bundle lifecycle-to-presentation contract.

@impl RER-001
@impl RER-002
@impl RER-006
@impl RER-007
@impl RER-013
@impl RUI-007
@impl REG-012
@impl RER-004
"""

from __future__ import annotations

from collections import deque
from typing import Any

import pytest
from langgraph.types import Command

from deerflow_deep_research.domain.lifecycle import (
    BundleAvailability,
    BundleControlResult,
    BundleRefinementProjection,
    Durability,
    HumanInputMode,
    HumanInputRequest,
    LegalNextAction,
    LifecycleAction,
    LifecycleStatus,
    LogicalPhase,
    PendingResearchInterrupt,
    ResultCode,
)
from deerflow_deep_research.domain.run_experience import (
    AnswerRun,
    AwaitingInput,
    Fault,
    PendingInputProjection,
    RefineRun,
    StartRun,
    StatusRun,
    Terminal,
)
from deerflow_deep_research.domain.run_observation import (
    ObservationInspectability,
    RecordBearingLifecycleFact,
    RetentionState,
    RunObservationView,
)
from deerflow_deep_research.runtime.human_input import project_suspension
from deerflow_deep_research.runtime.run_experience import ResearchRunExperience

BUNDLE_ID = "b_" + "A" * 43


class ReplayTransport:
    def __init__(self, results: list[object]) -> None:
        self._results = deque(results)
        self.calls: list[tuple[str, str | None, dict[str, Any] | None]] = []

    async def dispatch(
        self,
        *,
        action: str,
        bundle_id: str | None,
        context: dict[str, Any] | None = None,
        **_kwargs: Any,
    ) -> object:
        self.calls.append((action, bundle_id, context))
        return self._results.popleft()


class RecordingObservationPublisher:
    def __init__(self) -> None:
        self.facts: list[RecordBearingLifecycleFact] = []

    async def publish(self, fact: RecordBearingLifecycleFact) -> RunObservationView:
        self.facts.append(fact)
        return RunObservationView(
            bundle_id=fact.bundle_id,
            inspectability=ObservationInspectability.AVAILABLE,
            retention_state=RetentionState.RETAINED,
            durability=fact.durability,
        )


def _pending() -> PendingResearchInterrupt:
    return PendingResearchInterrupt(
        request=HumanInputRequest(
            request_id="drh_pending",
            mode=HumanInputMode.TEXT,
            title="Research scope",
            context="Provide the remaining research preferences.",
        ),
        suspension_cursor="start-message",
        phase="hitl1",
        generation=0,
    )


def _suspended(*, action: LifecycleAction = LifecycleAction.START) -> BundleControlResult:
    return BundleControlResult(
        action=action,
        code=ResultCode.SUSPENDED,
        availability=BundleAvailability.AVAILABLE,
        durability=Durability.RESTART_DURABLE,
        bundle_id=BUNDLE_ID,
        status=LifecycleStatus.SUSPENDED,
        phase=LogicalPhase.HITL1,
        generation=0,
        request_id="drh_pending",
        pending_input=PendingInputProjection(
            request_id="drh_pending",
            pending_phase="hitl1",
            generation=0,
            mode="text",
        ),
        refinement=BundleRefinementProjection(disposition="none"),
        legal_next_action=LegalNextAction.RESUME,
        execution_trace=("bootstrap", "hitl1"),
    )


def _suspension(*, action: LifecycleAction = LifecycleAction.START) -> Command:
    return project_suspension(pending=_pending(), result=_suspended(action=action), tool_call_id="call-1")


def _completed() -> dict[str, object]:
    return BundleControlResult(
        action=LifecycleAction.RESUME,
        code=ResultCode.COMPLETED,
        availability=BundleAvailability.AVAILABLE,
        durability=Durability.RESTART_DURABLE,
        bundle_id=BUNDLE_ID,
        status=LifecycleStatus.COMPLETED,
        phase=LogicalPhase.FINAL_DELIVERY,
        generation=0,
        refinement=BundleRefinementProjection(disposition="none"),
        legal_next_action=LegalNextAction.REFINE,
        execution_trace=("bootstrap", "hitl1", "final_delivery"),
    ).model_dump(mode="json", exclude_none=True)


@pytest.mark.asyncio
async def test_start_projects_one_bundle_local_pending_request() -> None:
    transport = ReplayTransport([_suspension()])

    update = await ResearchRunExperience(transport=transport, mode="fake").handle(
        StartRun(question="Compare storage options")
    )

    assert isinstance(update, AwaitingInput)
    assert update.snapshot.bundle_id == BUNDLE_ID
    assert update.snapshot.pending_input is not None
    assert update.snapshot.pending_input.request_id == "drh_pending"
    assert transport.calls == [("start", None, None)]
    assert BUNDLE_ID in update.model_dump_json()
    assert "checkpoint" not in update.model_dump_json()


@pytest.mark.asyncio
async def test_resume_uses_the_selected_bundle_id_and_returns_the_same_result_contract() -> None:
    transport = ReplayTransport([_suspension(), _completed()])
    experience = ResearchRunExperience(transport=transport, mode="fake")

    first = await experience.handle(StartRun(question="Compare storage options"))
    update = await experience.handle(AnswerRun(value="Use public sources."))

    assert isinstance(first, AwaitingInput)
    assert isinstance(update, Terminal)
    assert update.outcome == "completed"
    assert update.snapshot.bundle_id == BUNDLE_ID
    assert transport.calls == [("start", None, None), ("resume", BUNDLE_ID, None)]


@pytest.mark.asyncio
async def test_scripted_start_projects_policy_once_and_later_actions_do_not_reinject_it() -> None:
    transport = ReplayTransport(
        [
            _suspension(),
            _suspension(action=LifecycleAction.REFINE),
            _completed(),
        ]
    )
    experience = ResearchRunExperience(transport=transport, mode="fake")

    await experience.handle(StartRun(question="Compare storage options", scripted=True))
    await experience.handle(RefineRun(text="Focus on lifecycle durability."))
    update = await experience.handle(AnswerRun(value="Use public sources."))

    assert isinstance(update, Terminal)
    assert transport.calls == [
        (
            "start",
            None,
            {
                "non_interactive": True,
                "non_interactive_policy": {"auto_profile": True, "auto_proceed": True},
            },
        ),
        ("refine", BUNDLE_ID, {"refinement": "Focus on lifecycle durability."}),
        ("resume", BUNDLE_ID, None),
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("marker", ("hitl1_auto_profile", "hitl2_auto_proceed"))
async def test_policy_trace_marker_is_accepted_as_a_safe_observation(marker: str) -> None:
    suspended = _suspended().model_copy(update={"execution_trace": ("bootstrap", "hitl1", marker)})
    transport = ReplayTransport([project_suspension(pending=_pending(), result=suspended, tool_call_id="call-1")])

    update = await ResearchRunExperience(transport=transport, mode="fake").handle(
        StartRun(question="Compare storage options")
    )

    assert isinstance(update, AwaitingInput)
    assert update.snapshot.completed_trace == ("bootstrap", "hitl1", marker)
    assert update.trace_delta == ("bootstrap", "hitl1", marker)


@pytest.mark.asyncio
async def test_refine_is_dispatched_separately_without_consuming_the_pending_response() -> None:
    transport = ReplayTransport([_suspension(), _suspended(action=LifecycleAction.REFINE).model_dump(mode="json")])
    experience = ResearchRunExperience(transport=transport, mode="fake")

    await experience.handle(StartRun(question="Compare storage options"))
    update = await experience.handle(RefineRun(text="Focus on lifecycle durability."))

    assert isinstance(update, AwaitingInput)
    assert update.prompt.request_id == "drh_pending"
    assert transport.calls == [
        ("start", None, None),
        ("refine", BUNDLE_ID, {"refinement": "Focus on lifecycle durability."}),
    ]


@pytest.mark.asyncio
async def test_unavailable_result_clears_the_local_handle_and_offers_only_a_fresh_start() -> None:
    unavailable = BundleControlResult(
        action=LifecycleAction.STATUS,
        code=ResultCode.UNAVAILABLE,
        availability=BundleAvailability.UNAVAILABLE,
        durability=Durability.UNAVAILABLE,
        legal_next_action=LegalNextAction.START,
    ).model_dump(mode="json")
    transport = ReplayTransport([_suspension(), unavailable])
    experience = ResearchRunExperience(transport=transport, mode="fake")

    await experience.handle(StartRun(question="Compare storage options"))
    update = await experience.handle(StatusRun())

    assert isinstance(update, Fault)
    assert update.snapshot is not None
    assert update.snapshot.bundle_id is None
    assert "独立的新研究运行" in update.failure.next_action
    assert transport.calls == [("start", None, None), ("status", BUNDLE_ID, None)]


@pytest.mark.asyncio
async def test_observation_is_published_only_from_a_shared_available_result() -> None:
    publisher = RecordingObservationPublisher()
    experience = ResearchRunExperience(
        transport=ReplayTransport([_suspension()]),
        mode="fake",
        observation_publisher=publisher,
    )

    update = await experience.handle(StartRun(question="Compare storage options"))

    assert isinstance(update, AwaitingInput)
    assert [fact.bundle_id for fact in publisher.facts] == [BUNDLE_ID]
    assert update.snapshot.observation is not None
    assert update.snapshot.observation.bundle_id == BUNDLE_ID


@pytest.mark.asyncio
async def test_malformed_result_fails_closed_without_creating_a_control_projection() -> None:
    update = await ResearchRunExperience(
        transport=ReplayTransport([{"bundle_id": "r_" + "A" * 43, "code": "completed"}]),
        mode="fake",
    ).handle(StartRun(question="Compare storage options"))

    assert isinstance(update, Fault)
    assert update.failure.code.value == "protocol.invalid_result"
