"""Scripted-real lead-agent handoff evidence for the public controller.

The external model's selected response is scripted. DeerFlow's ordinary skill loader,
tool middleware, trusted runtime injection, Bundle lifecycle, and typed results are
real. These cases therefore prove the handoff after selection, not model judgment.

@impl DEC-003
@impl DEC-004
@impl RUI-006
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import secrets
import time
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef
from deerflow_deep_research.domain.lifecycle import ImplementationMode, LifecycleStatus, RefinementOperation
from deerflow_deep_research.domain.state import PhaseStatus
from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore
from tests.fixtures.recipes import fixture_recipe
from tests.integration.test_public_skill_activation import (
    SKILL_CONTAINER_PATH,
    SKILL_SOURCE,
    _ordinary_loader_indexes,
    _run_ordinary_turn,
    _tool_call,
    _tool_message,
    configured_deerflow_home,  # noqa: F401
)

pytestmark = pytest.mark.workflow


class _PreparationInterrupted(RuntimeError):
    pass


def _await(coro: Any) -> Any:
    return asyncio.run(coro)


def _control_call(messages: list[BaseMessage]) -> AIMessage:
    return next(
        message
        for message in messages
        if isinstance(message, AIMessage)
        and len(message.tool_calls or []) == 1
        and message.tool_calls[0].get("name") == "deep_research"
    )


def _fixture_graph_executor() -> BundleGraphExecutor:
    """Supply graph dependencies only through the test's trusted composition seam."""

    async def create(envelope, *, bundle, **_kwargs):  # noqa: ANN001
        return WorkUnitStore(
            workspace_host_path=envelope.workspace_host_path,
            bundle=bundle,
            clock=lambda: datetime(2026, 8, 7, tzinfo=UTC),
            monotonic=time.monotonic,
            lock_sleep=time.sleep,
            token_factory=lambda: secrets.token_hex(16),
            fault_hook=None,
        )

    return BundleGraphExecutor(recipe=fixture_recipe(work_unit_store_factory=create))


def _workspace_for(thread_id: str) -> Path:
    from deerflow.config.paths import get_paths

    workspace = Path(get_paths().sandbox_work_dir(thread_id, user_id="default")).resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


def _lifecycle_for(thread_id: str, *, fault_hook: Any = None) -> BundleLifecycle:
    return BundleLifecycle(workspace_host_path=_workspace_for(thread_id), fault_hook=fault_hook)


async def _stage_terminal_bundle(
    *,
    lifecycle: BundleLifecycle,
    bundle: RunBundleRef,
    executor: BundleGraphExecutor,
) -> None:
    """Create a terminal checkpoint through the fixture's production-shaped graph."""

    config = executor._config(bundle)
    async with lifecycle.open_graph_checkpoint(bundle) as saver:
        graph = executor._recipe.builder.compile(checkpointer=saver)
        await graph.aupdate_state(
            config,
            {
                "schema_version": 3,
                "bundle_id": bundle.bundle_id.value,
                "start_message_id": "controller-fixture-start",
                "request_digest": "d_" + "R" * 43,
                "request_text": "Fixture terminal research request.",
                "phase": "final_delivery",
                "route": "pass",
                "phase_status": PhaseStatus.TERMINAL.value,
                "terminal_status": LifecycleStatus.COMPLETED.value,
                "generation": 0,
                "wave0_results": (),
                "wave1_results": (),
                "consumed_request_ids": (),
                "consumed_message_ids": (),
                "execution_trace": ("final_delivery",),
            },
            as_node="final_delivery",
        )
        terminal = await graph.aget_state(config)
    await lifecycle.sync_graph_progress(bundle=bundle, values=dict(terminal.values), pending=None)


async def _replace_state(*, lifecycle: BundleLifecycle, bundle: RunBundleRef, state: Any) -> None:
    store = lifecycle._state_store(bundle)
    async with store.transition() as lease:
        await store.write(state, expected_revision=state.revision, lease=lease)


def _terminal_bundle(
    thread_id: str,
    *,
    pending_text: str | None = None,
    generation: int = 0,
    fault_hook: Any = None,
) -> tuple[BundleLifecycle, RunBundleRef, BundleGraphExecutor]:
    lifecycle = _lifecycle_for(thread_id, fault_hook=fault_hook)
    scope = ("default", thread_id)
    bundle = _await(
        lifecycle.start(
            scope=scope,
            request_text="Fixture terminal research request.",
            start_message_id=f"{thread_id}-fixture-start",
            implementation_mode=ImplementationMode.FIXTURE,
        )
    )
    executor = _fixture_graph_executor()
    _await(_stage_terminal_bundle(lifecycle=lifecycle, bundle=bundle, executor=executor))
    if pending_text is not None:
        _await(
            lifecycle.admit_refinement(
                scope=scope,
                bundle_id=bundle.bundle_id,
                text=pending_text,
                operation_key=f"{thread_id}-stored-direction",
            )
        )
    if generation:
        state = _await(lifecycle.read_state(bundle))
        _await(
            _replace_state(
                lifecycle=lifecycle,
                bundle=bundle,
                state=replace(state, generation=generation),
            )
        )
    return lifecycle, bundle, executor


def _run_controller_turn(
    *,
    app_config: Any,
    thread_id: str,
    messages: list[BaseMessage],
    action_args: dict[str, Any] | None,
    deferred_discovery: bool = False,
) -> dict[str, Any]:
    responses: list[AIMessage] = []
    if deferred_discovery:
        responses.append(
            _tool_call("describe_skill", {"name": "select:deep-research-controller"}, "describe-controller")
        )
    responses.append(
        _tool_call(
            "read_file",
            {"description": "Load the controller workflow", "path": SKILL_CONTAINER_PATH},
            "read-controller",
        )
    )
    if action_args is not None:
        responses.append(_tool_call("deep_research", action_args, "controller-lifecycle"))
        responses.append(AIMessage(content="The lifecycle outcome is available."))
    else:
        responses.append(AIMessage(content="I need one clarification before changing this research run."))

    from deerflow_deep_research import tool as public_tool

    with patch.object(public_tool, "BundleGraphExecutor", _fixture_graph_executor):
        # recursion_limit: the shared _run_ordinary_turn default (64) applies —
        # DeerFlow v2.1.0 consumes ~7 supersteps per scripted round-trip.
        return _run_ordinary_turn(
            app_config=app_config,
            responses=responses,
            messages=messages,
            thread_id=thread_id,
            run_id=f"{thread_id}-run",
        )


def _assert_canonical_read(result: dict[str, Any]) -> int:
    messages = list(result["messages"])
    read_index = next(
        index
        for index, message in enumerate(messages)
        if isinstance(message, AIMessage)
        and len(message.tool_calls or []) == 1
        and message.tool_calls[0].get("name") == "read_file"
        and message.tool_calls[0].get("args", {}).get("path") == SKILL_CONTAINER_PATH
    )
    read_call = messages[read_index].tool_calls[0]
    read_result = _tool_message(messages, str(read_call["id"]))
    actual_digest = hashlib.sha256(read_result.content.encode("utf-8")).hexdigest()
    expected_digest = hashlib.sha256(SKILL_SOURCE.read_bytes()).hexdigest()
    assert actual_digest == expected_digest
    assert [entry["path"] for entry in result["skill_context"]] == [SKILL_CONTAINER_PATH]
    return read_index


def _assert_selected_handoff(
    result: dict[str, Any],
    *,
    action_args: dict[str, Any],
    deferred_discovery: bool = False,
) -> dict[str, Any]:
    messages = list(result["messages"])
    read_index = _assert_canonical_read(result)
    positions = _ordinary_loader_indexes(messages)
    assert positions is not None
    assert positions[0] == read_index
    control = _control_call(messages)
    control_index = messages.index(control)
    assert control_index > read_index
    assert control.tool_calls[0]["args"] == action_args
    assert (
        sum(
            call.get("name") == "deep_research"
            for message in messages
            if isinstance(message, AIMessage)
            for call in message.tool_calls or []
        )
        == 1
    )
    payload: dict[str, Any] = json.loads(_tool_message(messages, "controller-lifecycle").content)

    describe_indexes = [
        index
        for index, message in enumerate(messages)
        if isinstance(message, AIMessage)
        and any(call.get("name") == "describe_skill" for call in message.tool_calls or [])
    ]
    if deferred_discovery:
        assert len(describe_indexes) == 1
        assert describe_indexes[0] < read_index
    else:
        assert describe_indexes == []
    return payload


def _assert_clarification_handoff(result: dict[str, Any]) -> None:
    messages = list(result["messages"])
    _assert_canonical_read(result)
    assert not any(
        call.get("name") == "deep_research"
        for message in messages
        if isinstance(message, AIMessage)
        for call in message.tool_calls or []
    )


def _start_suspended_run(
    *,
    app_config: Any,
    thread_id: str,
) -> tuple[HumanMessage, BundleLifecycle, RunBundleRef]:
    start_message = HumanMessage(
        content="Research the policy evidence through primary sources.",
        id=f"{thread_id}-start",
    )
    result = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[start_message],
        action_args={"action": "start"},
    )
    payload = _assert_selected_handoff(result, action_args={"action": "start"})
    assert payload["code"] == "suspended"
    lifecycle = _lifecycle_for(thread_id)
    bundle = _await(
        lifecycle.resolve(
            scope=("default", thread_id),
            bundle_id=BundleId(payload["bundle_id"]),
            handle=None,
        )
    )
    assert bundle is not None
    state = _await(lifecycle.read_state(bundle))
    assert state.pending_request_id is not None
    persisted_start = next(
        message
        for message in result["messages"]
        if isinstance(message, HumanMessage) and message.id == state.pending_cursor
    )
    return persisted_start, lifecycle, bundle


@pytest.mark.parametrize("deferred_discovery", (False, True), ids=("direct", "deferred"))
def test_ordinary_loaded_controller_hands_a_new_request_to_the_real_lifecycle(
    request: pytest.FixtureRequest,
    deferred_discovery: bool,
) -> None:
    """DEC-003: a selected new request crosses the real loader and lifecycle path."""

    configured_home = request.getfixturevalue("configured_deerflow_home")
    app_config = configured_home(deferred_discovery=deferred_discovery)
    thread_id = f"controller-new-{int(deferred_discovery)}"
    result = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[HumanMessage(content="Investigate the policy evidence.", id=f"{thread_id}-request")],
        action_args={"action": "start"},
        deferred_discovery=deferred_discovery,
    )

    payload = _assert_selected_handoff(
        result,
        action_args={"action": "start"},
        deferred_discovery=deferred_discovery,
    )
    assert payload["action"] == "start"
    assert payload["code"] == "suspended"
    assert payload["legal_next_action"] == "resume"


def test_ordinary_loaded_controller_hands_a_correlated_answer_to_resume(
    request: pytest.FixtureRequest,
) -> None:
    app_config = request.getfixturevalue("configured_deerflow_home")(deferred_discovery=False)
    thread_id = "controller-correlated-answer"
    start_message, lifecycle, bundle = _start_suspended_run(app_config=app_config, thread_id=thread_id)
    pending = _await(lifecycle.read_state(bundle))
    assert pending.pending_cursor == start_message.id
    assert pending.pending_request_id is not None
    answer = HumanMessage(
        content="Use an executive audience.",
        id=f"{thread_id}-answer",
        additional_kwargs={
            "human_input_response": {
                "version": 1,
                "kind": "human_input_response",
                "source": "deep_research",
                "request_id": pending.pending_request_id,
                "response_kind": "text",
                "value": "Use an executive audience.",
            }
        },
    )
    result = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[start_message, answer],
        action_args={"action": "resume", "bundle_id": bundle.bundle_id.value},
    )

    payload = _assert_selected_handoff(
        result,
        action_args={"action": "resume", "bundle_id": bundle.bundle_id.value},
    )
    assert payload["action"] == "resume"
    assert payload["code"] == "completed"
    assert payload["status"] == "completed"
    state = _await(lifecycle.read_state(bundle))
    assert state.pending_request_id is None


def test_ordinary_loaded_controller_admits_mid_suspension_direction_without_consuming_answer(
    request: pytest.FixtureRequest,
) -> None:
    app_config = request.getfixturevalue("configured_deerflow_home")(deferred_discovery=False)
    thread_id = "controller-mid-suspension-direction"
    start_message, lifecycle, bundle = _start_suspended_run(app_config=app_config, thread_id=thread_id)
    direction = HumanMessage(
        content="For this run, prioritize primary regulatory sources.",
        id=f"{thread_id}-direction",
    )
    args = {
        "action": "refine",
        "bundle_id": bundle.bundle_id.value,
        "refinement": "Prioritize primary regulatory sources.",
    }

    result = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[start_message, direction],
        action_args=args,
    )

    payload = _assert_selected_handoff(result, action_args=args)
    state = _await(lifecycle.read_state(bundle))
    assert payload["code"] == "refinement_pending"
    assert payload["legal_next_action"] == "resume"
    assert state.pending_request_id is not None
    assert state.admitted_refinement is not None


def test_ordinary_loaded_controller_hands_status_to_the_existing_bundle(
    request: pytest.FixtureRequest,
) -> None:
    app_config = request.getfixturevalue("configured_deerflow_home")(deferred_discovery=False)
    thread_id = "controller-status"
    start_message, _lifecycle, bundle = _start_suspended_run(app_config=app_config, thread_id=thread_id)
    args = {"action": "status", "bundle_id": bundle.bundle_id.value}

    result = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[start_message, HumanMessage(content="What is the current status?", id=f"{thread_id}-status")],
        action_args=args,
    )

    payload = _assert_selected_handoff(result, action_args=args)
    assert payload["action"] == "status"
    assert payload["status"] == "suspended"
    assert payload["legal_next_action"] == "resume"


def test_explicit_stop_preserves_queued_direction_without_implicit_restart(
    request: pytest.FixtureRequest,
) -> None:
    app_config = request.getfixturevalue("configured_deerflow_home")(deferred_discovery=False)
    thread_id = "controller-explicit-stop"
    start_message, lifecycle, bundle = _start_suspended_run(app_config=app_config, thread_id=thread_id)
    direction = HumanMessage(content="Also compare regional enforcement.", id=f"{thread_id}-direction")
    direction_args = {
        "action": "refine",
        "bundle_id": bundle.bundle_id.value,
        "refinement": "Compare regional enforcement.",
    }
    direction_result = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[start_message, direction],
        action_args=direction_args,
    )
    assert _assert_selected_handoff(direction_result, action_args=direction_args)["code"] == "refinement_pending"

    cancel_args = {"action": "cancel", "bundle_id": bundle.bundle_id.value}
    result = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[start_message, direction, HumanMessage(content="Stop this research run.", id=f"{thread_id}-stop")],
        action_args=cancel_args,
    )

    payload = _assert_selected_handoff(result, action_args=cancel_args)
    state = _await(lifecycle.read_state(bundle))
    assert payload["code"] == "cancelled"
    assert payload["legal_next_action"] == "refine"
    assert state.terminal_status is LifecycleStatus.CANCELLED
    assert state.admitted_refinement is not None
    assert state.current_refinement is None


def test_explicit_terminal_continuation_omits_the_stored_direction_text(
    request: pytest.FixtureRequest,
) -> None:
    app_config = request.getfixturevalue("configured_deerflow_home")(deferred_discovery=False)
    thread_id = "controller-terminal-continuation"
    lifecycle, bundle, _executor = _terminal_bundle(
        thread_id,
        pending_text="Use the queued primary-source direction.",
    )
    args = {"action": "refine", "bundle_id": bundle.bundle_id.value}

    result = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[HumanMessage(content="Continue that queued direction.", id=f"{thread_id}-continue")],
        action_args=args,
    )

    payload = _assert_selected_handoff(result, action_args=args)
    state = _await(lifecycle.read_state(bundle))
    assert payload["code"] == "refinement_applied"
    assert payload["refinement"]["disposition"] == "applied"
    assert state.admitted_refinement is None
    assert state.current_refinement is not None


@pytest.mark.parametrize("pending_text", (None, "Retained but exhausted direction."), ids=("none", "pending"))
def test_exhausted_terminal_handoff_starts_fresh_run_instead_of_refining(
    request: pytest.FixtureRequest,
    pending_text: str | None,
) -> None:
    app_config = request.getfixturevalue("configured_deerflow_home")(deferred_discovery=False)
    thread_id = f"controller-exhausted-{pending_text is not None}"
    lifecycle, exhausted, _executor = _terminal_bundle(thread_id, pending_text=pending_text, generation=2)
    before = _await(lifecycle.status(scope=("default", thread_id), bundle_id=exhausted.bundle_id))
    assert before.legal_next_action.value == "start"
    assert before.refinement is not None

    result = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[HumanMessage(content="Start a fresh independent research request.", id=f"{thread_id}-new")],
        action_args={"action": "start"},
    )

    payload = _assert_selected_handoff(result, action_args={"action": "start"})
    assert payload["action"] == "start"
    assert payload["bundle_id"] != exhausted.bundle_id.value


def test_ambiguous_terminal_follow_up_makes_no_lifecycle_call(
    request: pytest.FixtureRequest,
) -> None:
    app_config = request.getfixturevalue("configured_deerflow_home")(deferred_discovery=False)
    thread_id = "controller-ambiguous-terminal"
    lifecycle, bundle, _executor = _terminal_bundle(thread_id, pending_text="Retained terminal direction.")

    result = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[HumanMessage(content="Can we do something about that?", id=f"{thread_id}-ambiguous")],
        action_args=None,
    )

    _assert_clarification_handoff(result)
    state = _await(lifecycle.read_state(bundle))
    assert state.admitted_refinement is not None
    assert state.current_refinement is None


def test_ambiguous_criticism_makes_no_lifecycle_call(
    request: pytest.FixtureRequest,
) -> None:
    app_config = request.getfixturevalue("configured_deerflow_home")(deferred_discovery=False)
    thread_id = "controller-ambiguous-criticism"
    lifecycle = _lifecycle_for(thread_id)
    bundle = _await(
        lifecycle.start(
            scope=("default", thread_id),
            request_text="Research question",
            implementation_mode=ImplementationMode.ALL_REAL,
        )
    )

    result = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[HumanMessage(content="This direction is not useful.", id=f"{thread_id}-criticism")],
        action_args=None,
    )

    _assert_clarification_handoff(result)
    state = _await(lifecycle.read_state(bundle))
    assert state.terminal_status is None
    assert state.admitted_refinement is None


def test_profile_note_request_does_not_mutate_then_clarified_direction_is_admitted(
    request: pytest.FixtureRequest,
) -> None:
    app_config = request.getfixturevalue("configured_deerflow_home")(deferred_discovery=False)
    thread_id = "controller-profile-note"
    lifecycle = _lifecycle_for(thread_id)
    bundle = _await(
        lifecycle.start(
            scope=("default", thread_id),
            request_text="Research question",
            implementation_mode=ImplementationMode.ALL_REAL,
        )
    )
    profile_note = HumanMessage(content="Save this as a profile note.", id=f"{thread_id}-profile-note")

    no_call = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[profile_note],
        action_args=None,
    )
    _assert_clarification_handoff(no_call)
    after_note = _await(lifecycle.read_state(bundle))
    assert after_note.profile_ref is None
    assert after_note.admitted_refinement is None

    direction = HumanMessage(
        content="For this run, prioritize regulatory implementation evidence.",
        id=f"{thread_id}-direction",
    )
    args = {
        "action": "refine",
        "bundle_id": bundle.bundle_id.value,
        "refinement": "Prioritize regulatory implementation evidence.",
    }
    clarified = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[profile_note, direction],
        action_args=args,
    )

    payload = _assert_selected_handoff(clarified, action_args=args)
    assert payload["code"] == "refinement_pending"
    assert _await(lifecycle.read_state(bundle)).admitted_refinement is not None


def test_active_conflict_preserves_the_first_direction(
    request: pytest.FixtureRequest,
) -> None:
    app_config = request.getfixturevalue("configured_deerflow_home")(deferred_discovery=False)
    thread_id = "controller-active-conflict"
    lifecycle = _lifecycle_for(thread_id)
    bundle = _await(
        lifecycle.start(
            scope=("default", thread_id),
            request_text="Research question",
            implementation_mode=ImplementationMode.ALL_REAL,
        )
    )
    _await(
        lifecycle.admit_refinement(
            scope=("default", thread_id),
            bundle_id=bundle.bundle_id,
            text="Keep the first direction.",
            operation_key="first-direction",
        )
    )
    args = {
        "action": "refine",
        "bundle_id": bundle.bundle_id.value,
        "refinement": "Attempt to replace the first direction.",
    }

    result = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[HumanMessage(content="Change the direction now.", id=f"{thread_id}-second")],
        action_args=args,
    )

    payload = _assert_selected_handoff(result, action_args=args)
    state = _await(lifecycle.read_state(bundle))
    assert payload["code"] == "refinement_conflict"
    assert payload["refinement"]["disposition"] == "pending"
    assert state.admitted_refinement is not None
    assert state.admitted_refinement.operation_key == "first-direction"


def test_precommit_recovery_conflict_projects_the_first_applied_round(
    request: pytest.FixtureRequest,
) -> None:
    app_config = request.getfixturevalue("configured_deerflow_home")(deferred_discovery=False)
    thread_id = "controller-precommit-conflict"

    def fault(point: str) -> None:
        if point == "after_refinement_checkpoint_prepared":
            raise _PreparationInterrupted(point)

    lifecycle, bundle, executor = _terminal_bundle(thread_id, fault_hook=fault)
    operation = RefinementOperation.from_text(
        operation_key="first-prepared-direction",
        text="Keep the prepared primary-source direction.",
    )
    _await(
        lifecycle.admit_refinement(
            scope=("default", thread_id),
            bundle_id=bundle.bundle_id,
            text=operation.text,
            operation_key=operation.operation_key,
        )
    )
    with pytest.raises(_PreparationInterrupted):
        _await(
            executor.prepare_refinement_round(
                lifecycle=lifecycle,
                scope=("default", thread_id),
                bundle=bundle,
                submitted_operation=operation,
            )
        )
    args = {
        "action": "refine",
        "bundle_id": bundle.bundle_id.value,
        "refinement": "Try a competing regional comparison.",
    }

    result = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[HumanMessage(content="Add a regional comparison.", id=f"{thread_id}-competing")],
        action_args=args,
    )

    payload = _assert_selected_handoff(result, action_args=args)
    state = _await(lifecycle.read_state(bundle))
    assert payload["code"] == "refinement_conflict"
    assert payload["refinement"]["disposition"] == "applied"
    assert state.current_refinement is not None
    assert state.current_refinement.operation_key == operation.operation_key


def test_ended_explicit_target_starts_its_same_bundle_refinement_round(
    request: pytest.FixtureRequest,
) -> None:
    app_config = request.getfixturevalue("configured_deerflow_home")(deferred_discovery=False)
    thread_id = "controller-ended-explicit"
    lifecycle, bundle, _executor = _terminal_bundle(thread_id)
    args = {
        "action": "refine",
        "bundle_id": bundle.bundle_id.value,
        "refinement": "Prioritize comparative primary sources.",
    }

    result = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[HumanMessage(content="Refine the ended run.", id=f"{thread_id}-refine")],
        action_args=args,
    )

    payload = _assert_selected_handoff(result, action_args=args)
    state = _await(lifecycle.read_state(bundle))
    assert payload["code"] == "refinement_applied"
    assert payload["bundle_id"] == bundle.bundle_id.value
    assert state.current_refinement is not None


def test_unavailable_target_returns_the_real_fresh_start_only_projection(
    request: pytest.FixtureRequest,
) -> None:
    app_config = request.getfixturevalue("configured_deerflow_home")(deferred_discovery=False)
    thread_id = "controller-unavailable"
    missing_bundle_id = "b_" + "U" * 43
    args = {"action": "status", "bundle_id": missing_bundle_id}

    result = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[HumanMessage(content="Check the unavailable research run.", id=f"{thread_id}-status")],
        action_args=args,
    )

    payload = _assert_selected_handoff(result, action_args=args)
    assert payload["action"] == "status"
    assert payload["availability"] == "unavailable"
    assert payload["code"] == "unavailable"
    assert payload["durability"] == "unavailable"
    assert payload["legal_next_action"] == "start"
    assert "bundle_id" not in payload
    assert "refinement" not in payload


def test_mixed_answer_and_direction_keeps_the_pending_subject_on_resume(
    request: pytest.FixtureRequest,
) -> None:
    """A scripted correlated answer stays on resume even when it carries context."""

    app_config = request.getfixturevalue("configured_deerflow_home")(deferred_discovery=False)
    thread_id = "controller-mixed-answer-direction"
    start_message, lifecycle, bundle = _start_suspended_run(app_config=app_config, thread_id=thread_id)
    pending = _await(lifecycle.read_state(bundle))
    answer = HumanMessage(
        content="Use an executive audience, and focus the analysis on regulator guidance.",
        id=f"{thread_id}-answer",
        additional_kwargs={
            "human_input_response": {
                "version": 1,
                "kind": "human_input_response",
                "source": "deep_research",
                "request_id": pending.pending_request_id,
                "response_kind": "text",
                "value": "Use an executive audience, and focus the analysis on regulator guidance.",
            }
        },
    )
    args = {"action": "resume", "bundle_id": bundle.bundle_id.value}

    result = _run_controller_turn(
        app_config=app_config,
        thread_id=thread_id,
        messages=[start_message, answer],
        action_args=args,
    )

    payload = _assert_selected_handoff(result, action_args=args)
    state = _await(lifecycle.read_state(bundle))
    assert payload["action"] == "resume"
    assert payload["code"] == "completed"
    assert state.admitted_refinement is None
