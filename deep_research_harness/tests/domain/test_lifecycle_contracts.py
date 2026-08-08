"""Phase-1 contracts for bounded same-Bundle refinement admission.

@impl DRH-005
@impl REG-021
"""

from __future__ import annotations

import copy
import json

import pytest

from deerflow_deep_research.domain.bundle import BundleId
from deerflow_deep_research.domain.lifecycle import (
    RefinementAdmissionDisposition,
    RefinementOperation,
    RefinementReplayReceipt,
)
from deerflow_deep_research.domain.state import (
    BundleLocalState,
    WriterRole,
    admit_bundle_refinement,
    apply_research_update,
    consume_admitted_refinement,
)
from deerflow_deep_research.graph.nodes.rerun.planner import FullRerunPolicy
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle

_BUNDLE_ID = BundleId("b_" + "A" * 43)
_PRODUCTION_POLICY = FullRerunPolicy(max_rerun_generations=2)


def _operation(*, key: str, text: str) -> RefinementOperation:
    return RefinementOperation.from_text(operation_key=key, text=text)


def test_pending_refinement_is_first_write_wins_and_same_operation_replays() -> None:
    state = BundleLocalState(bundle_id=_BUNDLE_ID)
    first = admit_bundle_refinement(
        state,
        _operation(key="operation-1", text="Prioritize primary sources"),
        policy=_PRODUCTION_POLICY,
    )

    assert first.disposition is RefinementAdmissionDisposition.PENDING
    assert first.state.admitted_refinement is not None
    assert first.state.admitted_refinement.text == "Prioritize primary sources"

    replay = admit_bundle_refinement(
        first.state,
        _operation(key="operation-1", text="Prioritize primary sources"),
        policy=_PRODUCTION_POLICY,
    )
    conflict = admit_bundle_refinement(
        first.state,
        _operation(key="operation-2", text="Use primary sources only"),
        policy=_PRODUCTION_POLICY,
    )

    assert replay.disposition is RefinementAdmissionDisposition.PENDING
    assert replay.state == first.state
    assert conflict.disposition is RefinementAdmissionDisposition.CONFLICT
    assert conflict.state == first.state


def test_same_trusted_operation_with_altered_text_fails_closed() -> None:
    first = admit_bundle_refinement(
        BundleLocalState(bundle_id=_BUNDLE_ID),
        _operation(key="operation-1", text="Cover regulation"),
        policy=_PRODUCTION_POLICY,
    )

    altered = admit_bundle_refinement(
        first.state,
        _operation(key="operation-1", text="Cover pricing"),
        policy=_PRODUCTION_POLICY,
    )

    assert altered.disposition is RefinementAdmissionDisposition.CONFLICT
    assert altered.state == first.state


def test_applied_current_round_retains_replay_receipt_and_allows_one_later_pending_direction() -> None:
    first = admit_bundle_refinement(
        BundleLocalState(bundle_id=_BUNDLE_ID),
        _operation(key="operation-1", text="Compare primary sources"),
        policy=_PRODUCTION_POLICY,
    )
    applied = consume_admitted_refinement(first.state, policy=_PRODUCTION_POLICY)

    assert applied.current_refinement is not None
    assert applied.current_refinement.text == "Compare primary sources"
    assert applied.generation == 1
    assert len(applied.refinement_replay_receipts) == 1

    replay = admit_bundle_refinement(
        applied,
        _operation(key="operation-1", text="Compare primary sources"),
        policy=_PRODUCTION_POLICY,
    )
    later = admit_bundle_refinement(
        applied,
        _operation(key="operation-2", text="Add regional comparison"),
        policy=_PRODUCTION_POLICY,
    )

    assert replay.disposition is RefinementAdmissionDisposition.APPLIED
    assert replay.state == applied
    assert later.disposition is RefinementAdmissionDisposition.PENDING
    assert later.state.current_refinement == applied.current_refinement
    assert later.state.admitted_refinement is not None
    assert later.state.admitted_refinement.text == "Add regional comparison"


def test_same_text_from_a_new_operation_is_conflict_only_while_pending_then_becomes_later_admission() -> None:
    first = admit_bundle_refinement(
        BundleLocalState(bundle_id=_BUNDLE_ID),
        _operation(key="operation-1", text="Preserve citations"),
        policy=_PRODUCTION_POLICY,
    )
    conflict = admit_bundle_refinement(
        first.state,
        _operation(key="operation-2", text="Preserve citations"),
        policy=_PRODUCTION_POLICY,
    )
    applied = consume_admitted_refinement(first.state, policy=_PRODUCTION_POLICY)
    later = admit_bundle_refinement(
        applied,
        _operation(key="operation-2", text="Preserve citations"),
        policy=_PRODUCTION_POLICY,
    )

    assert conflict.disposition is RefinementAdmissionDisposition.CONFLICT
    assert later.disposition is RefinementAdmissionDisposition.PENDING
    assert later.state.admitted_refinement is not None
    assert later.state.admitted_refinement.operation_key == "operation-2"


def test_legacy_text_only_pending_same_text_is_effect_free() -> None:
    legacy = BundleLocalState(
        bundle_id=_BUNDLE_ID,
        admitted_refinement={"text": "Keep the legal scope"},
        revision=7,
    )

    replay = admit_bundle_refinement(
        legacy,
        _operation(key="operation-1", text="Keep the legal scope"),
        policy=_PRODUCTION_POLICY,
    )

    assert replay.disposition is RefinementAdmissionDisposition.PENDING
    assert replay.state == legacy
    assert replay.state.revision == 7


def _pre_change_mapping(*, bundle_id: BundleId = _BUNDLE_ID) -> dict[str, object]:
    """Return a literal complete schema-v3 mapping from before Phase 1."""

    return {
        "schema_version": 3,
        "bundle_id": bundle_id.value,
        "generation": 0,
        "revision": 7,
        "phase": "bootstrap",
        "phase_status": "in_progress",
        "start_message_id": None,
        "start_request_digest": None,
        "waiting_for": None,
        "terminal_status": None,
        "terminal_reason": None,
        "latest_incident": None,
        "pending_request_id": None,
        "pending_cursor": None,
        "pending_request_mode": None,
        "consumed_request_ids": [],
        "consumed_message_ids": [],
        "admitted_refinement": {"text": "Preserve the original scope"},
        "refinement_round": 0,
        "hitl1_visit_count": 0,
        "profile_ref": None,
        "research_depth": "",
        "target_audience": "",
        "output_format": "",
        "cost_tolerance": "",
        "time_budget": "",
        "must_answer_questions": [],
        "comparison_required": False,
        "comparison_subjects": [],
        "request_language": "",
        "output_language": "",
        "degraded_profile": False,
        "pending_profile": None,
        "profile_followup_round": 0,
        "proposed_profile": None,
        "profile_rejection_round": 0,
        "profile_feedback_cursor_message_id": "",
        "proposal_version": 0,
        "interaction_feedback": None,
        "execution_trace": [],
    }


def test_pre_change_bundle_mapping_defaults_new_refinement_fields_without_mutating_input() -> None:
    mapping = _pre_change_mapping()
    before = copy.deepcopy(mapping)

    state = BundleLocalState.from_mapping(mapping)

    assert state.revision == 7
    assert state.current_refinement is None
    assert state.refinement_replay_receipts == ()
    assert mapping == before


@pytest.mark.asyncio
async def test_pre_change_state_store_read_preserves_literal_bytes_and_revision(tmp_path) -> None:
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=("alice", "old-state"), request_text="Question")
    state_path = lifecycle.private_root(bundle) / "state.json"
    mapping = _pre_change_mapping(bundle_id=bundle.bundle_id)
    state_path.write_text(json.dumps(mapping, indent=2, sort_keys=True), encoding="utf-8")
    before = state_path.read_bytes()

    observed = await lifecycle.read_state(bundle)

    assert observed.revision == 7
    assert observed.current_refinement is None
    assert observed.refinement_replay_receipts == ()
    assert state_path.read_bytes() == before


def test_production_receipt_capacity_retains_each_committed_operation_and_rejects_lower_policy_mismatch() -> None:
    first = admit_bundle_refinement(
        BundleLocalState(bundle_id=_BUNDLE_ID),
        _operation(key="operation-1", text="First direction"),
        policy=_PRODUCTION_POLICY,
    )
    first_applied = consume_admitted_refinement(first.state, policy=_PRODUCTION_POLICY)
    second = admit_bundle_refinement(
        first_applied,
        _operation(key="operation-2", text="Second direction"),
        policy=_PRODUCTION_POLICY,
    )
    second_applied = consume_admitted_refinement(second.state, policy=_PRODUCTION_POLICY)

    assert tuple(receipt.operation_key for receipt in second_applied.refinement_replay_receipts) == (
        "operation-1",
        "operation-2",
    )
    assert (
        admit_bundle_refinement(
            second_applied,
            _operation(key="operation-1", text="First direction"),
            policy=_PRODUCTION_POLICY,
        ).disposition
        is RefinementAdmissionDisposition.APPLIED
    )
    assert (
        admit_bundle_refinement(
            first_applied,
            _operation(key="operation-1", text="Altered current direction"),
            policy=_PRODUCTION_POLICY,
        ).disposition
        is RefinementAdmissionDisposition.CONFLICT
    )
    assert (
        admit_bundle_refinement(
            second_applied,
            _operation(key="operation-1", text="Altered retained direction"),
            policy=_PRODUCTION_POLICY,
        ).disposition
        is RefinementAdmissionDisposition.CONFLICT
    )
    with pytest.raises(ValueError, match="refinement_replay_receipt_capacity_exceeded"):
        admit_bundle_refinement(
            second_applied,
            _operation(key="operation-3", text="Third direction"),
            policy=FullRerunPolicy(max_rerun_generations=1),
        )


def test_state_rejects_conflicting_reuse_of_one_operation_key_across_current_and_receipt() -> None:
    first = admit_bundle_refinement(
        BundleLocalState(bundle_id=_BUNDLE_ID),
        _operation(key="operation-1", text="Original direction"),
        policy=_PRODUCTION_POLICY,
    )
    applied = consume_admitted_refinement(first.state, policy=_PRODUCTION_POLICY)
    assert applied.current_refinement is not None

    with pytest.raises(ValueError, match="refinement_current_operation_conflict"):
        BundleLocalState(
            bundle_id=_BUNDLE_ID,
            generation=1,
            refinement_round=1,
            current_refinement=applied.current_refinement,
            refinement_replay_receipts=(
                RefinementReplayReceipt(
                    operation_key="operation-1",
                    text_digest="0" * 64,
                    round=1,
                    generation=1,
                ),
            ),
        )


def test_lifecycle_and_state_reject_policy_above_the_public_generation_ceiling(tmp_path) -> None:
    high = FullRerunPolicy(max_rerun_generations=3)

    with pytest.raises(ValueError, match="public_generation_ceiling_exceeded"):
        admit_bundle_refinement(
            BundleLocalState(bundle_id=_BUNDLE_ID),
            _operation(key="operation-1", text="Direction"),
            policy=high,
        )
    with pytest.raises(ValueError, match="public_generation_ceiling_exceeded"):
        BundleLifecycle(workspace_host_path=tmp_path, rerun_policy=high)


def test_generation_ceiling_and_lower_trusted_policy_bound_admission_and_receipts() -> None:
    lower = FullRerunPolicy(max_rerun_generations=1)
    first = admit_bundle_refinement(
        BundleLocalState(bundle_id=_BUNDLE_ID),
        _operation(key="operation-1", text="First direction"),
        policy=lower,
    )
    applied = consume_admitted_refinement(first.state, policy=lower)
    exhausted = admit_bundle_refinement(
        applied,
        _operation(key="operation-2", text="Later direction"),
        policy=lower,
    )

    assert applied.generation == 1
    assert len(applied.refinement_replay_receipts) == 1
    assert exhausted.disposition is RefinementAdmissionDisposition.EXHAUSTED
    assert exhausted.state == applied


@pytest.mark.parametrize("writer", (WriterRole.PLANNER, WriterRole.WORKER, WriterRole.REPAIR, WriterRole.SUBMIT))
def test_non_controller_writers_cannot_mutate_current_round_refinement_projection(writer: WriterRole) -> None:
    with pytest.raises(ValueError, match="writer_not_authorized"):
        apply_research_update(
            {"generation": 1},
            {"current_refinement": {"text": "untrusted"}},
            writer=writer,
        )
