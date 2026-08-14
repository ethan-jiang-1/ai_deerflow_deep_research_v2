"""Phase-1 public refinement result contracts.

@impl RUI-012
"""

from __future__ import annotations

import json
from dataclasses import replace

import pytest

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef
from deerflow_deep_research.domain.lifecycle import (
    BundleAvailability,
    BundleControlResult,
    BundleRefinementDisposition,
    BundleRefinementProjection,
    Durability,
    LifecycleAction,
    LifecycleStatus,
    LogicalPhase,
    RefinementOperation,
    ResultCode,
)
from deerflow_deep_research.domain.state import (
    BundleLocalState,
    PhaseStatus,
    admit_bundle_refinement,
    consume_admitted_refinement,
)
from deerflow_deep_research.graph.nodes.rerun.planner import FullRerunPolicy
from deerflow_deep_research.runtime.bundle_control import BundleControl
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle

_BUNDLE = RunBundleRef(
    bundle_id=BundleId("b_" + "A" * 43),
    scope_bucket="s_" + "B" * 43,
)
_POLICY = FullRerunPolicy(max_rerun_generations=2)


def _state(**overrides: object) -> BundleLocalState:
    return BundleLocalState(bundle_id=_BUNDLE.bundle_id, implementation_mode="all_real", **overrides)


def _operation(*, key: str, text: str) -> RefinementOperation:
    return RefinementOperation.from_text(operation_key=key, text=text)


def _terminal(state: BundleLocalState) -> BundleLocalState:
    return replace(
        state,
        phase_status=PhaseStatus.TERMINAL,
        terminal_status=LifecycleStatus.COMPLETED,
    )


def _result(
    tmp_path,
    state: BundleLocalState,
    *,
    action: LifecycleAction = LifecycleAction.STATUS,
    code: ResultCode | None = None,
    policy: FullRerunPolicy = _POLICY,
):
    return BundleLifecycle(workspace_host_path=tmp_path, rerun_policy=policy).result_for_state(
        action=action,
        bundle=_BUNDLE,
        state=state,
        code=code,
    )


def test_available_results_project_all_refinement_dispositions_without_private_direction_facts(tmp_path) -> None:
    none = _terminal(_state())
    pending = _terminal(
        admit_bundle_refinement(
            _state(),
            _operation(key="operation-1", text="Preserve source quality"),
            policy=_POLICY,
        ).state
    )
    applied = _terminal(
        consume_admitted_refinement(
            admit_bundle_refinement(
                _state(),
                _operation(key="operation-1", text="Preserve source quality"),
                policy=_POLICY,
            ).state,
            policy=_POLICY,
        )
    )
    applied_with_pending = _terminal(
        admit_bundle_refinement(
            applied,
            _operation(key="operation-2", text="Add regulatory comparison"),
            policy=_POLICY,
        ).state
    )

    expected = (
        (none, BundleRefinementDisposition.NONE, None),
        (pending, BundleRefinementDisposition.PENDING, None),
        (applied, BundleRefinementDisposition.APPLIED, 1),
        (applied_with_pending, BundleRefinementDisposition.APPLIED_WITH_PENDING, 1),
    )
    for state, disposition, current_round in expected:
        result = _result(tmp_path, state)
        assert result.refinement is not None
        assert result.refinement.disposition is disposition
        assert result.refinement.current_round == current_round
        assert result.legal_next_action.value == "refine"
        payload = json.dumps(result.model_dump(mode="json", exclude_none=True), sort_keys=True)
        for forbidden in (
            "Preserve source quality",
            "Add regulatory comparison",
            "operation-1",
            "operation-2",
            "operation_key",
            "digest",
            "receipt",
            "path",
            "checkpoint",
            "token",
        ):
            assert forbidden not in payload


def test_submitted_operation_codes_remain_distinct_from_post_call_bundle_projection(tmp_path) -> None:
    pending = admit_bundle_refinement(
        _state(),
        _operation(key="operation-1", text="Preserve source quality"),
        policy=_POLICY,
    ).state
    applied = consume_admitted_refinement(pending, policy=_POLICY)

    pending_result = _result(
        tmp_path,
        pending,
        action=LifecycleAction.REFINE,
        code=ResultCode.REFINEMENT_PENDING,
    )
    conflict_result = _result(
        tmp_path,
        pending,
        action=LifecycleAction.REFINE,
        code=ResultCode.REFINEMENT_CONFLICT,
    )
    replay_result = _result(
        tmp_path,
        applied,
        action=LifecycleAction.REFINE,
        code=ResultCode.REFINEMENT_APPLIED,
    )

    assert pending_result.code is ResultCode.REFINEMENT_PENDING
    assert pending_result.refinement is not None
    assert pending_result.refinement.disposition is BundleRefinementDisposition.PENDING
    assert conflict_result.code is ResultCode.REFINEMENT_CONFLICT
    assert conflict_result.refinement is not None
    assert conflict_result.refinement.disposition is BundleRefinementDisposition.PENDING
    assert replay_result.code is ResultCode.REFINEMENT_APPLIED
    assert replay_result.refinement is not None
    assert replay_result.refinement.disposition is BundleRefinementDisposition.APPLIED


def test_active_pending_direction_requires_resume_only_for_a_human_subject(tmp_path) -> None:
    pending = admit_bundle_refinement(
        _state(),
        _operation(key="operation-1", text="Preserve source quality"),
        policy=_POLICY,
    ).state
    waiting = replace(pending, pending_request_id="request-1", waiting_for="hitl1")

    active_result = _result(tmp_path, pending)
    waiting_result = _result(tmp_path, waiting)

    assert active_result.refinement is not None
    assert active_result.refinement.disposition is BundleRefinementDisposition.PENDING
    assert active_result.legal_next_action.value == "status"
    assert waiting_result.refinement is not None
    assert waiting_result.refinement.disposition is BundleRefinementDisposition.PENDING
    assert waiting_result.legal_next_action.value == "resume"


@pytest.mark.parametrize(
    "state_builder",
    (
        lambda: _state(generation=1),
        lambda: replace(
            consume_admitted_refinement(
                admit_bundle_refinement(
                    _state(),
                    _operation(key="operation-1", text="Applied direction"),
                    policy=_POLICY,
                ).state,
                policy=_POLICY,
            ),
        ),
        lambda: _state(
            generation=1,
            admitted_refinement=_operation(key="operation-1", text="Pending direction"),
        ),
        lambda: replace(
            consume_admitted_refinement(
                admit_bundle_refinement(
                    _state(),
                    _operation(key="operation-1", text="Applied direction"),
                    policy=_POLICY,
                ).state,
                policy=_POLICY,
            ),
            admitted_refinement=_operation(key="operation-2", text="Pending direction"),
        ),
    ),
)
def test_exhausted_terminal_projects_fresh_start_for_every_refinement_disposition(tmp_path, state_builder) -> None:
    result = _result(
        tmp_path,
        _terminal(state_builder()),
        policy=FullRerunPolicy(max_rerun_generations=1),
    )

    assert result.refinement is not None
    assert result.legal_next_action.value == "start"


def test_result_rejects_applied_code_for_a_bundle_without_a_committed_current_round(tmp_path) -> None:
    pending = admit_bundle_refinement(
        _state(),
        _operation(key="operation-1", text="Preserve source quality"),
        policy=_POLICY,
    ).state

    with pytest.raises(ValueError, match="refinement_applied_requires_current_round"):
        _result(
            tmp_path,
            pending,
            action=LifecycleAction.REFINE,
            code=ResultCode.REFINEMENT_APPLIED,
        )


def test_result_rejects_a_current_round_ahead_of_its_public_generation() -> None:
    with pytest.raises(ValueError, match="refinement_current_round_generation_mismatch"):
        BundleControlResult(
            action=LifecycleAction.STATUS,
            code=ResultCode.STATUS_OK,
            availability=BundleAvailability.AVAILABLE,
            durability=Durability.RESTART_DURABLE,
            bundle_id=_BUNDLE.bundle_id.value,
            status=LifecycleStatus.ACTIVE,
            phase=LogicalPhase.BOOTSTRAP,
            generation=1,
            refinement=BundleRefinementProjection(
                disposition=BundleRefinementDisposition.APPLIED,
                current_round=2,
            ),
        )


async def _commit_current_round(
    lifecycle: BundleLifecycle,
    *,
    scope: tuple[str, str],
    bundle: RunBundleRef,
    operation_key: str,
    text: str,
) -> BundleLocalState:
    admitted = await lifecycle.admit_refinement(
        scope=scope,
        text=text,
        operation_key=operation_key,
        bundle_id=bundle.bundle_id,
    )
    current = consume_admitted_refinement(admitted.state, policy=_POLICY)
    store = lifecycle._state_store(bundle)
    async with store.transition() as lease:
        return await store.write(current, expected_revision=admitted.state.revision, lease=lease)


@pytest.mark.asyncio
async def test_bundle_control_distinguishes_new_pending_direction_from_current_or_retained_replay(tmp_path) -> None:
    scope = ("alice", "result-contract")
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path, rerun_policy=_POLICY)
    bundle = await lifecycle.start(scope=scope, request_text="Question", implementation_mode="all_real")
    first_current = await _commit_current_round(
        lifecycle,
        scope=scope,
        bundle=bundle,
        operation_key="operation-1",
        text="Preserve source quality",
    )
    controller = BundleControl(lifecycle=lifecycle)

    later = await controller.dispatch(
        action=LifecycleAction.REFINE,
        effective_user_id=scope[0],
        outer_thread_id=scope[1],
        messages=(),
        tool_call_id="operation-2",
        bundle_id=bundle.bundle_id.value,
        refinement="Add regulatory comparison",
    )
    assert later["code"] == "refinement_pending"
    assert later["refinement"] == {"disposition": "applied_with_pending", "current_round": 1}

    before_invalid = await lifecycle.read_state(bundle)
    invalid = await controller.dispatch(
        action=LifecycleAction.REFINE,
        effective_user_id=scope[0],
        outer_thread_id=scope[1],
        messages=(),
        tool_call_id="unused-for-textless",
        bundle_id=bundle.bundle_id.value,
        refinement=None,
    )
    assert invalid["code"] == "invalid_transition"
    assert (await lifecycle.read_state(bundle)) == before_invalid

    second_current = consume_admitted_refinement(before_invalid, policy=_POLICY)
    store = lifecycle._state_store(bundle)
    async with store.transition() as lease:
        await store.write(second_current, expected_revision=before_invalid.revision, lease=lease)
    replay = await controller.dispatch(
        action=LifecycleAction.REFINE,
        effective_user_id=scope[0],
        outer_thread_id=scope[1],
        messages=(),
        tool_call_id="operation-1",
        bundle_id=bundle.bundle_id.value,
        refinement="Preserve source quality",
    )
    assert first_current.current_refinement is not None
    assert replay["code"] == "refinement_applied"
    assert replay["refinement"] == {"disposition": "applied", "current_round": 2}
