"""Public lifecycle dispatch and namespace semantics (RUI-006/REG-004/005).

@impl REG-015
@impl REG-019
@impl RUI-004
@impl RUI-006
@impl RUI-010
@impl RUI-011
@impl DRH-001
@impl DRH-002
@impl DRH-003
@impl DRH-004
@impl DRH-006
@impl DRH-008
@impl DRH-007
@impl CES-008
"""

from __future__ import annotations

import json
import os
import secrets
import shutil
import time
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.types import Command
from pydantic import ValidationError

from deerflow_deep_research.domain.bundle import RunBundleRef, new_bundle_id
from deerflow_deep_research.domain.lifecycle import (
    AcceptedHumanResponse,
    LifecycleAction,
    RefinementInput,
    ResponseKind,
)
from deerflow_deep_research.domain.state import BundleLocalState
from deerflow_deep_research.runtime.bundle_control import BundleControl
from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
from deerflow_deep_research.runtime.bundle_lifecycle import (
    BundleAlreadyActive,
    BundleLifecycle,
    BundleLifecycleError,
    CurrentBundleHandle,
    scope_bucket,
)
from deerflow_deep_research.runtime.control import build_control_graph_host
from deerflow_deep_research.runtime.evaluation import (
    CaseRegistry,
    CognitiveEvaluationRunner,
    ControlIdentity,
    EvaluationCase,
    ExecutionBounds,
    SubjectExecution,
)
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore
from deerflow_deep_research.tool import DeepResearchArgs, run_deep_research
from tests.fixtures.recipes import fixture_recipe


class FakeAppConfig:
    checkpointer = None
    database = None


async def _start(lifecycle: BundleLifecycle, *, scope: tuple[str, str], request_text: str) -> RunBundleRef:
    return await lifecycle.start(
        scope=scope,
        request_text=request_text,
        implementation_mode="all_real",
    )


def _fixture_executor() -> BundleGraphExecutor:
    async def create(envelope: Any, *, bundle: RunBundleRef, **_kwargs: Any) -> WorkUnitStore:
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


async def _fixture_run(**kwargs: Any) -> Any:
    return await run_deep_research(bundle_graph_executor_factory=_fixture_executor, **kwargs)


@pytest.mark.asyncio
async def test_bundle_handle_and_absent_handle_resolve_only_one_active_bundle(tmp_path: Path) -> None:
    """DRH-003/004: Handle continuation and scoped fallback have no session authority."""
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    scope = ("alice", "thread-1")
    bundle = await _start(lifecycle, scope=scope, request_text="Research batteries")

    assert await lifecycle.resolve_active(scope=scope, handle=CurrentBundleHandle(bundle.bundle_id)) == bundle
    assert await lifecycle.resolve_active(scope=scope, handle=None) == bundle
    assert (
        await lifecycle.resolve_active(
            scope=("bob", "thread-1"),
            handle=CurrentBundleHandle(bundle.bundle_id),
        )
    ) is None


@pytest.mark.asyncio
async def test_start_admission_blocks_only_an_active_bundle_and_ended_bundle_allows_a_fresh_run(tmp_path: Path) -> None:
    """DRH-004: no durable active pointer is needed for one-active admission."""
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    scope = ("alice", "thread-1")
    first = await _start(lifecycle, scope=scope, request_text="First question")

    with pytest.raises(BundleAlreadyActive) as error:
        await _start(lifecycle, scope=scope, request_text="Second question")
    assert error.value.bundle == first

    await lifecycle.end(bundle=first)
    second = await _start(lifecycle, scope=scope, request_text="Second question")
    assert second.bundle_id != first.bundle_id


@pytest.mark.asyncio
async def test_malformed_foreign_and_ambiguous_candidates_fail_closed(tmp_path: Path) -> None:
    """DRH-003: discovery never guesses through malformed or competing candidates."""
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    scope = ("alice", "thread-1")
    first = await _start(lifecycle, scope=scope, request_text="First question")

    with pytest.raises(ValueError, match="bundle_id_invalid"):
        CurrentBundleHandle.from_value("r_" + "A" * 43)
    foreign = CurrentBundleHandle(first.bundle_id)
    assert await lifecycle.resolve_active(scope=("bob", "thread-1"), handle=foreign) is None

    bucket = scope_bucket(effective_user_id="alice", outer_thread_id="thread-1")
    second = RunBundleRef(bundle_id=new_bundle_id(), scope_bucket=bucket)
    lifecycle._publish_sync(second, BundleLocalState(bundle_id=second.bundle_id, implementation_mode="all_real"))
    with pytest.raises(BundleLifecycleError, match="bundle_discovery_ambiguous"):
        await lifecycle.resolve_active(scope=scope, handle=None)


@pytest.mark.asyncio
async def test_refine_preserves_the_pending_response_and_resume_requires_its_correlation(tmp_path: Path) -> None:
    """DRH-005: Run refinement is not an answer to a pending interaction."""
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    scope = ("alice", "thread-1")
    bundle = await _start(lifecycle, scope=scope, request_text="Question")
    await lifecycle.set_pending_request(bundle=bundle, request_id="hitl-1")

    refined = (
        await lifecycle.admit_refinement(
            scope=scope,
            text="Focus on cost",
            operation_key="operation-refine",
            bundle_id=bundle.bundle_id,
        )
    ).state
    assert refined.admitted_refinement is not None
    assert refined.pending_request_id == "hitl-1"

    with pytest.raises(BundleLifecycleError, match="response_mismatch"):
        await lifecycle.resume(
            scope=scope,
            response=AcceptedHumanResponse(
                request_id="stale",
                message_id="message-1",
                value="answer",
                response_kind=ResponseKind.TEXT,
            ),
            bundle_id=bundle.bundle_id,
        )
    resumed = await lifecycle.resume(
        scope=scope,
        response=AcceptedHumanResponse(
            request_id="hitl-1",
            message_id="message-1",
            value="answer",
            response_kind=ResponseKind.TEXT,
        ),
        bundle_id=bundle.bundle_id,
    )
    assert resumed.pending_request_id is None
    assert resumed.admitted_refinement is not None


@pytest.mark.asyncio
async def test_refine_without_explicit_id_never_reactivates_an_ended_handle(tmp_path: Path) -> None:
    """DRH-005: an ended Handle cannot guess a later refinement round."""
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    scope = ("alice", "thread-1")
    bundle = await _start(lifecycle, scope=scope, request_text="Question")
    await lifecycle.end(bundle=bundle)

    with pytest.raises(BundleLifecycleError, match="explicit_bundle_id_required"):
        await lifecycle.admit_refinement(
            scope=scope,
            text=RefinementInput(text="Reopen with new evidence").text,
            operation_key="operation-ended-handle",
            handle=CurrentBundleHandle(bundle.bundle_id),
        )


@pytest.mark.asyncio
async def test_explicit_refinement_queues_an_ended_bundle_only_without_another_active_bundle(
    tmp_path: Path,
) -> None:
    """DRH-005: Phase 1 admits an ended-Bundle direction without graph activation."""
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    scope = ("alice", "thread-1")
    ended = await _start(lifecycle, scope=scope, request_text="Original question")
    await lifecycle.end(bundle=ended)

    admitted = (
        await lifecycle.admit_refinement(
            scope=scope,
            text="Add a comparison",
            operation_key="operation-ended",
            bundle_id=ended.bundle_id,
        )
    ).state
    assert not admitted.is_active
    assert admitted.refinement_round == 0
    assert admitted.admitted_refinement is not None

    active = await _start(lifecycle, scope=scope, request_text="Different question")
    with pytest.raises(BundleLifecycleError, match="active_bundle_exists"):
        await lifecycle.admit_refinement(
            scope=scope,
            text="Try again",
            operation_key="operation-competing",
            bundle_id=ended.bundle_id,
        )
    assert (await lifecycle.read_state(active)).is_active


@pytest.mark.asyncio
async def test_deleted_bundle_is_unavailable_without_checkpoint_or_replacement_recovery(tmp_path: Path) -> None:
    """DRH-006: a missing Bundle is permanent even if observations remain elsewhere."""
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    scope = ("alice", "thread-1")
    bundle = await _start(lifecycle, scope=scope, request_text="Question")
    root = lifecycle.private_root(bundle)
    legacy_observation = {"checkpoint": "still-present", "binding": "still-present", "session": "still-present"}

    shutil.rmtree(root)
    result = await lifecycle.status(scope=scope, bundle_id=bundle.bundle_id)
    assert result.code == "unavailable"
    assert not root.exists()
    assert legacy_observation == {"checkpoint": "still-present", "binding": "still-present", "session": "still-present"}

    fresh = await _start(lifecycle, scope=scope, request_text="Independent question")
    assert fresh.bundle_id != bundle.bundle_id


@pytest.mark.asyncio
async def test_evaluation_bundle_cannot_restore_or_join_deep_research_discovery(tmp_path: Path) -> None:
    """DRH-007/CES-008: Evaluation Bundles are a separate non-recovery domain."""
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    scope = ("alice", "thread-1")
    lost = await _start(lifecycle, scope=scope, request_text="Question")
    shutil.rmtree(lifecycle.private_root(lost))

    async def evaluation_subject(context: Any) -> SubjectExecution:
        context.observe("evaluation.observed", {"former_bundle_id": lost.bundle_id.value})
        return SubjectExecution(output={"former_bundle_id": lost.bundle_id.value})

    evaluation_case = EvaluationCase(
        case_id="bundle-domain-separation",
        version="v1",
        subject="bounded_flow",
        fixture={"former_bundle_id": lost.bundle_id.value},
        required_services=(),
        bounds=ExecutionBounds(timeout_seconds=60, max_model_calls=0, max_tool_calls=0),
        controls=(
            ControlIdentity(kind="case", version="v1", digest="a" * 64),
            ControlIdentity(kind="contract", version="v1", digest="b" * 64),
            ControlIdentity(kind="rubric", version="v1", digest="c" * 64),
            ControlIdentity(kind="protocol", version="v1", digest="d" * 64),
        ),
    )
    evaluation = await CognitiveEvaluationRunner(
        registry=CaseRegistry((evaluation_case,)),
        runs_root=tmp_path / "evals" / "runs",
        subjects={"bounded_flow": evaluation_subject},
    ).run(case_id=evaluation_case.case_id, version=evaluation_case.version)

    assert evaluation.bundle_path.is_relative_to(tmp_path / "evals" / "runs")
    assert (await lifecycle.status(scope=scope, bundle_id=lost.bundle_id)).code == "unavailable"
    assert await lifecycle.discover_active(scope=scope) is None

    fresh = await _start(lifecycle, scope=scope, request_text="Independent question")
    assert fresh.bundle_id != lost.bundle_id


@pytest.mark.asyncio
async def test_control_returns_unavailable_when_bundle_is_deleted_during_state_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DRH-006: a deletion race never leaks a filesystem exception through control."""
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await _start(lifecycle, scope=("alice", "thread-1"), request_text="Question")
    root = lifecycle.private_root(bundle)
    original_replace = os.replace

    def delete_before_state_publish(source, destination, *args, **kwargs):
        if Path(destination).name == "state.json":
            shutil.rmtree(root)
        return original_replace(source, destination, *args, **kwargs)

    monkeypatch.setattr(os, "replace", delete_before_state_publish)
    result = await BundleControl(lifecycle=lifecycle).dispatch(
        action=LifecycleAction.CANCEL,
        effective_user_id="alice",
        outer_thread_id="thread-1",
        messages=(),
        tool_call_id="cancel-after-loss",
        bundle_id=bundle.bundle_id.value,
    )

    assert result["code"] == "unavailable"
    assert result["availability"] == "unavailable"
    assert "bundle_id" not in result
    assert not root.exists()


def _envelope(tmp_path: Path, user: str = "alice", thread: str = "thread-1") -> TrustedRuntimeEnvelope:
    workspace = tmp_path / "workspace"
    uploads = tmp_path / "uploads"
    outputs = tmp_path / "outputs"
    workspace.mkdir(parents=True, exist_ok=True)
    uploads.mkdir(parents=True, exist_ok=True)
    outputs.mkdir(parents=True, exist_ok=True)
    return TrustedRuntimeEnvelope(
        effective_user_id=user,
        outer_thread_id=thread,
        outer_run_id="run-1",
        app_config=FakeAppConfig(),
        workspace_host_path=workspace,
        uploads_host_path=uploads,
        outputs_host_path=outputs,
        workspace_virtual_root="/mnt/user-data/workspace",
        uploads_virtual_root="/mnt/user-data/uploads",
        outputs_virtual_root="/mnt/user-data/outputs",
        parent_sandbox=object(),
    )


class FakeAdapter:
    def __init__(self, envelope: TrustedRuntimeEnvelope) -> None:
        self.envelope = envelope
        self.adapted = 0
        self.initialize_values: list[bool] = []

    async def adapt(self, _runtime, *, initialize_parent_sandbox: bool = True):
        self.adapted += 1
        self.initialize_values.append(initialize_parent_sandbox)
        return self.envelope if initialize_parent_sandbox else replace(self.envelope, parent_sandbox=None)


def _runtime(messages, call_id: str, *, context: dict | None = None):
    return SimpleNamespace(
        state={"messages": list(messages)},
        context=context or {},
        tool_call_id=call_id,
    )


def _call(action: str, call_id: str, **args) -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[{"name": "deep_research", "args": {"action": action, **args}, "id": call_id}],
    )


def _host():
    return build_control_graph_host(fingerprint_verifier=lambda _app: None)


def _command_payload(command: object) -> tuple[dict[str, object], dict[str, object]]:
    assert isinstance(command, Command)
    message = command.update["messages"][0]
    return json.loads(message.content), message.artifact["human_input"]


def _response(request_id: str, *, message_id: str = "human-response", value: str = "profile") -> HumanMessage:
    return HumanMessage(
        content=value,
        id=message_id,
        additional_kwargs={
            "human_input_response": {
                "version": 1,
                "kind": "human_input_response",
                "source": "deep_research",
                "request_id": request_id,
                "response_kind": "text",
                "value": value,
            }
        },
    )


def test_action_specific_schema_is_strict() -> None:
    bundle_id = "b_" + "A" * 43

    assert DeepResearchArgs(action="start").bundle_id is None
    assert DeepResearchArgs(action="resume", bundle_id=bundle_id).bundle_id == bundle_id
    assert DeepResearchArgs(action="resume").bundle_id is None
    with pytest.raises(ValidationError):
        DeepResearchArgs(action="start", bundle_id=bundle_id)
    continuation = DeepResearchArgs(action="refine", bundle_id=bundle_id)
    assert continuation.refinement is None
    assert DeepResearchArgs(action="refine", bundle_id=bundle_id, refinement=None).refinement is None
    with pytest.raises(ValidationError):
        DeepResearchArgs(action="refine")
    with pytest.raises(ValidationError):
        DeepResearchArgs(action="refine", bundle_id=bundle_id, refinement="   ")
    with pytest.raises(ValidationError):
        DeepResearchArgs(action="status", bundle_id="r_" + "A" * 43)
    with pytest.raises(ValidationError):
        DeepResearchArgs(action="cancel", bundle_id=bundle_id, answer="forged")
    with pytest.raises(ValidationError):
        DeepResearchArgs(action="start", implementation_mode="fixture")


@pytest.mark.asyncio
async def test_foreign_bundle_id_is_rejected_before_graph_or_checkpoint_access(tmp_path: Path) -> None:
    adapter = FakeAdapter(_envelope(tmp_path))

    class ForbiddenHost:
        def is_registered(self, _action: str) -> bool:
            raise AssertionError("lifecycle actions must not use GraphHost")

    result = await _fixture_run(
        action="status",
        probe_id=None,
        bundle_id="b_" + "Z" * 43,
        runtime=_runtime([_call("status", "foreign-id")], "foreign-id"),
        adapter=adapter,
        host_factory=ForbiddenHost,
    )

    assert result["action"] == "status"
    assert result["code"] == "unavailable"
    assert result["availability"] == "unavailable"
    assert "bundle_id" not in result
    assert "bundle_id" not in result
    assert adapter.initialize_values == [False]


@pytest.mark.asyncio
async def test_public_bundle_lifecycle_completes_after_one_correlated_resume(tmp_path: Path) -> None:
    adapter = FakeAdapter(_envelope(tmp_path))
    start_user = HumanMessage(content="research question", id="human-start")
    start_ai = _call("start", "call-start")
    started = await _fixture_run(
        action="start",
        probe_id=None,
        runtime=_runtime([start_user, start_ai], "call-start"),
        adapter=adapter,
    )
    start_result, hitl1 = _command_payload(started)
    bundle_id = str(start_result["bundle_id"])

    assert start_result["code"] == "suspended"
    assert start_result["status"] == "suspended"
    assert start_result["availability"] == "available"
    assert start_result["implementation_mode"] == "fixture"
    assert start_result["legal_next_action"] == "resume"
    assert start_result["bundle_id"] == bundle_id

    response = _response(str(hitl1["request_id"]))
    resumed = await _fixture_run(
        action="resume",
        probe_id=None,
        bundle_id=bundle_id,
        runtime=_runtime(
            [start_user, start_ai, response, _call("resume", "call-resume", bundle_id=bundle_id)],
            "call-resume",
        ),
        adapter=adapter,
    )
    assert resumed["code"] == "completed"
    assert resumed["status"] == "completed"
    assert resumed["bundle_id"] == bundle_id
    assert resumed["legal_next_action"] == "refine"

    status = await _fixture_run(
        action="status",
        probe_id=None,
        bundle_id=bundle_id,
        runtime=_runtime([_call("status", "call-status", bundle_id=bundle_id)], "call-status"),
        adapter=adapter,
    )
    assert status["code"] == "completed"
    assert status["status"] == "completed"


@pytest.mark.asyncio
async def test_infra_probe_checkpoint_remains_isolated_from_bundle_lifecycle(tmp_path: Path) -> None:
    host = _host()
    assert host.is_registered("infra_probe")
    assert not any(host.is_registered(action) for action in ("start", "resume", "status", "cancel", "refine"))
    adapter = FakeAdapter(_envelope(tmp_path))
    probe_runtime = _runtime([], "probe-call")
    before = await _fixture_run(
        action="infra_probe",
        probe_id="p1",
        runtime=probe_runtime,
        adapter=adapter,
        host_factory=lambda: host,
    )
    user = HumanMessage(content="research question", id="human-start")
    started = await _fixture_run(
        action="start",
        probe_id=None,
        runtime=_runtime([user, _call("start", "call-start")], "call-start"),
        adapter=adapter,
        host_factory=lambda: host,
    )
    after = await _fixture_run(
        action="infra_probe",
        probe_id="p1",
        runtime=probe_runtime,
        adapter=adapter,
        host_factory=lambda: host,
    )

    control, _request = _command_payload(started)
    assert control["durability"] == "restart_durable"
    assert before["previous_visit"] is None and before["current_visit"] == 1
    assert after["previous_visit"] == 1 and after["current_visit"] == 2


@pytest.mark.asyncio
async def test_early_dispatch_refusals_do_not_mutate_lifecycle(tmp_path: Path) -> None:
    adapter = FakeAdapter(_envelope(tmp_path))
    user = HumanMessage(content="question", id="human-start")
    sibling_ai = AIMessage(
        content="",
        tool_calls=[
            {"name": "deep_research", "args": {"action": "start"}, "id": "call-start"},
            {"name": "other", "args": {}, "id": "other-call"},
        ],
    )
    denied = await _fixture_run(
        action="start",
        probe_id=None,
        runtime=_runtime([user, sibling_ai], "call-start"),
        adapter=adapter,
    )
    assert denied["code"] == "exclusive_control_call_required"
    assert adapter.adapted == 0

    normal_ai = _call("start", "call-start")
    noninteractive = await _fixture_run(
        action="start",
        probe_id=None,
        runtime=_runtime([user, normal_ai], "call-start", context={"non_interactive": True}),
        adapter=adapter,
    )
    assert noninteractive["code"] == "interactive_required"

    im_denied = await _fixture_run(
        action="start",
        probe_id=None,
        runtime=_runtime([user, normal_ai], "call-start", context={"channel_user_id": "secret-channel-user"}),
        adapter=adapter,
    )
    assert im_denied["code"] == "human_input_transport_unavailable"
    assert "secret-channel-user" not in str(im_denied)


@pytest.mark.asyncio
async def test_interaction_refusals_preserve_explicit_status_and_cancel_controls(tmp_path: Path) -> None:
    adapter = FakeAdapter(_envelope(tmp_path))
    user = HumanMessage(content="question", id="human-start")
    started = await _fixture_run(
        action="start",
        probe_id=None,
        runtime=_runtime([user, _call("start", "call-start")], "call-start"),
        adapter=adapter,
    )
    result, _request = _command_payload(started)
    bundle_id = str(result["bundle_id"])

    for context, expected in (
        ({"non_interactive": True}, "interactive_required"),
        ({"channel_name": "known-im"}, "human_input_transport_unavailable"),
    ):
        denied = await _fixture_run(
            action="resume",
            probe_id=None,
            bundle_id=bundle_id,
            runtime=_runtime(
                [_call("resume", f"resume-{expected}", bundle_id=bundle_id)],
                f"resume-{expected}",
                context=context,
            ),
            adapter=adapter,
        )
        assert denied["code"] == expected

        status = await _fixture_run(
            action="status",
            probe_id=None,
            bundle_id=bundle_id,
            runtime=_runtime(
                [_call("status", f"status-{expected}", bundle_id=bundle_id)],
                f"status-{expected}",
                context=context,
            ),
            adapter=adapter,
        )
        assert status["code"] == "suspended"
        assert status["status"] == "suspended"

    cancelled = await _fixture_run(
        action="cancel",
        probe_id=None,
        bundle_id=bundle_id,
        runtime=_runtime(
            [_call("cancel", "cancel-known-im", bundle_id=bundle_id)],
            "cancel-known-im",
            context={"channel_name": "known-im", "non_interactive": True},
        ),
        adapter=adapter,
    )
    assert cancelled["code"] == "cancelled"
    assert adapter.initialize_values[-1] is False


@pytest.mark.asyncio
async def test_distinct_trusted_scopes_receive_independent_bundle_ids(tmp_path: Path) -> None:
    first_adapter = FakeAdapter(_envelope(tmp_path, thread="thread-1"))
    second_adapter = FakeAdapter(_envelope(tmp_path, thread="thread-2"))
    first_user = HumanMessage(content="first question", id="human-first")
    second_user = HumanMessage(content="second question", id="human-second")
    first = await _fixture_run(
        action="start",
        probe_id=None,
        runtime=_runtime([first_user, _call("start", "call-first")], "call-first"),
        adapter=first_adapter,
    )
    second = await _fixture_run(
        action="start",
        probe_id=None,
        runtime=_runtime([second_user, _call("start", "call-second")], "call-second"),
        adapter=second_adapter,
    )
    first_result, _ = _command_payload(first)
    second_result, _ = _command_payload(second)
    assert first_result["bundle_id"] != second_result["bundle_id"]


@pytest.mark.asyncio
async def test_same_start_reprojects_and_different_message_conflicts(tmp_path: Path) -> None:
    adapter = FakeAdapter(_envelope(tmp_path))
    user = HumanMessage(content="question", id="human-start")
    first = await _fixture_run(
        action="start",
        probe_id=None,
        runtime=_runtime([user, _call("start", "call-1")], "call-1"),
        adapter=adapter,
    )
    first_result, first_request = _command_payload(first)
    retry = await _fixture_run(
        action="start",
        probe_id=None,
        runtime=_runtime([user, _call("start", "call-2")], "call-2"),
        adapter=adapter,
    )
    retry_result, retry_request = _command_payload(retry)
    assert retry_result["bundle_id"] == first_result["bundle_id"]
    assert retry_request["request_id"] == first_request["request_id"]
    assert retry.update["messages"][0].tool_call_id == "call-2"

    another = HumanMessage(content="another question", id="human-new")
    conflict = await _fixture_run(
        action="start",
        probe_id=None,
        runtime=_runtime([another, _call("start", "call-3")], "call-3"),
        adapter=adapter,
    )
    assert conflict["code"] == "active_bundle_exists"
    assert conflict["bundle_id"] == first_result["bundle_id"]


@pytest.mark.asyncio
async def test_completed_resume_and_cancel_replay_the_terminal_bundle_projection(tmp_path: Path) -> None:
    adapter = FakeAdapter(_envelope(tmp_path))
    user = HumanMessage(content="question", id="human-start")
    start_ai = _call("start", "call-start")
    started = await _fixture_run(
        action="start",
        probe_id=None,
        runtime=_runtime([user, start_ai], "call-start"),
        adapter=adapter,
    )
    started_result, hitl1 = _command_payload(started)
    bundle_id = str(started_result["bundle_id"])
    response = _response(str(hitl1["request_id"]))
    resumed = await _fixture_run(
        action="resume",
        probe_id=None,
        bundle_id=bundle_id,
        runtime=_runtime(
            [user, start_ai, response, _call("resume", "call-resume", bundle_id=bundle_id)],
            "call-resume",
        ),
        adapter=adapter,
    )
    assert resumed["code"] == "completed"
    replay = await _fixture_run(
        action="resume",
        probe_id=None,
        bundle_id=bundle_id,
        runtime=_runtime(
            [user, start_ai, response, _call("resume", "call-replay", bundle_id=bundle_id)],
            "call-replay",
        ),
        adapter=adapter,
    )
    assert replay["code"] == "completed"

    cancelled = await _fixture_run(
        action="cancel",
        probe_id=None,
        bundle_id=bundle_id,
        runtime=_runtime([_call("cancel", "call-cancel", bundle_id=bundle_id)], "call-cancel"),
        adapter=adapter,
    )
    assert cancelled["code"] == "completed"
    assert cancelled["status"] == "completed"


@pytest.mark.asyncio
async def test_refine_is_not_resume_and_ended_handle_requires_an_explicit_target(tmp_path: Path) -> None:
    adapter = FakeAdapter(_envelope(tmp_path))

    class ForbiddenGraphExecutor:
        def __getattr__(self, name: str) -> object:
            raise AssertionError(f"pending refinement must not initialize graph executor: {name}")

    user = HumanMessage(content="question", id="human-start")
    start_ai = _call("start", "call-start")
    started = await _fixture_run(
        action="start",
        probe_id=None,
        runtime=_runtime([user, start_ai], "call-start"),
        adapter=adapter,
    )
    start_result, hitl1 = _command_payload(started)
    bundle_id = str(start_result["bundle_id"])

    refined = await run_deep_research(
        action="refine",
        probe_id=None,
        bundle_id=bundle_id,
        refinement="Prioritize primary sources",
        runtime=_runtime([_call("refine", "call-refine", bundle_id=bundle_id)], "call-refine"),
        adapter=adapter,
        bundle_graph_executor=ForbiddenGraphExecutor(),
    )
    assert refined["code"] == "refinement_pending"
    assert refined["request_id"] == hitl1["request_id"]
    assert adapter.initialize_values == [True, False]

    response = _response(str(hitl1["request_id"]))
    completed = await _fixture_run(
        action="resume",
        probe_id=None,
        bundle_id=bundle_id,
        runtime=_runtime(
            [user, start_ai, response, _call("resume", "call-resume", bundle_id=bundle_id)],
            "call-resume",
        ),
        adapter=adapter,
    )
    assert completed["status"] == "completed"

    ended_handle = CurrentBundleHandle.from_value(bundle_id)
    implicit = await _fixture_run(
        action="refine",
        probe_id=None,
        refinement="Reopen this research",
        runtime=_runtime(
            [_call("refine", "call-implicit")],
            "call-implicit",
            context={"deep_research_current_bundle_handle": ended_handle},
        ),
        adapter=adapter,
    )
    assert implicit["code"] == "explicit_bundle_id_required"
    assert implicit["availability"] == "unavailable"

    reopened = await _fixture_run(
        action="refine",
        probe_id=None,
        bundle_id=bundle_id,
        refinement="Reopen this research",
        runtime=_runtime([_call("refine", "call-reopen", bundle_id=bundle_id)], "call-reopen"),
        adapter=adapter,
    )
    assert reopened["bundle_id"] == bundle_id
    assert reopened["code"] == "refinement_applied"
    assert reopened["status"] == "completed"
    assert reopened["legal_next_action"] == "start"


@pytest.mark.asyncio
async def test_wrong_scope_is_indistinguishable_from_absence(tmp_path: Path) -> None:
    original_adapter = FakeAdapter(_envelope(tmp_path))
    user = HumanMessage(content="question", id="human-start")
    started = await _fixture_run(
        action="start",
        probe_id=None,
        runtime=_runtime([user, _call("start", "call-start")], "call-start"),
        adapter=original_adapter,
    )
    result, _ = _command_payload(started)
    bundle_id = str(result["bundle_id"])
    wrong_adapter = FakeAdapter(_envelope(tmp_path, thread="other-thread"))
    wrong = await _fixture_run(
        action="status",
        probe_id=None,
        bundle_id=bundle_id,
        runtime=_runtime([_call("status", "call-wrong", bundle_id=bundle_id)], "call-wrong"),
        adapter=wrong_adapter,
    )
    absent = await _fixture_run(
        action="status",
        probe_id=None,
        bundle_id="b_" + "Z" * 43,
        runtime=_runtime([_call("status", "call-absent")], "call-absent"),
        adapter=original_adapter,
    )
    assert wrong["code"] == absent["code"] == "unavailable"
    assert "bundle_id" not in wrong and "bundle_id" not in absent
