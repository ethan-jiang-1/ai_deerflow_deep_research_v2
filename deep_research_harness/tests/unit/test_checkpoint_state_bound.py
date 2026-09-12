"""The hard checkpoint-size bound is enforced on the live write and read path.

@impl REG-008
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from langgraph.checkpoint.base import empty_checkpoint
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from deerflow_deep_research.domain.lifecycle import (
    LifecycleAction,
    LifecycleStatus,
    ResultCode,
    TerminalReason,
)
from deerflow_deep_research.domain.run_experience import (
    FailureCertainty,
    RunFailureCode,
    TerminalIncidentProjection,
)
from deerflow_deep_research.domain.state import (
    MAX_CHECKPOINT_STATE_BYTES,
    MAX_WORK_UNIT_BLOCK_BYTES,
    RESEARCH_STATE_SCHEMA_VERSION,
    CheckpointStateBoundExceeded,
    serialize_research_state,
    validate_checkpoint_values,
)
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle, BundleLifecycleError
from deerflow_deep_research.runtime.checkpoint import build_deep_research_checkpoint_serde

BUNDLE_ID = "b_" + "A" * 43
_SCOPE = ("bound-user", "bound-thread")
_BOUND_READ_SCOPE = ("bound-read-user", "bound-read-thread")
_BLOCK_SCOPE = ("bound-block-user", "bound-block-thread")
_OVER = "x" * (MAX_CHECKPOINT_STATE_BYTES + 1)
_BIG = "y" * (MAX_CHECKPOINT_STATE_BYTES // 2)


def _checkpoint(request_text: str) -> dict[str, Any]:
    checkpoint = empty_checkpoint()
    checkpoint["channel_values"] = {
        "schema_version": RESEARCH_STATE_SCHEMA_VERSION,
        "request_text": request_text,
    }
    return checkpoint


def _config(bundle_id: str) -> dict[str, dict[str, str]]:
    return {"configurable": {"thread_id": bundle_id, "checkpoint_ns": ""}}


def _rows(database: Path, table: str, columns: str) -> list[tuple[Any, ...]]:
    connection = sqlite3.connect(f"{database.as_uri()}?mode=ro", uri=True)
    try:
        return connection.execute(f"SELECT {columns} FROM {table} ORDER BY rowid").fetchall()
    finally:
        connection.close()


async def test_over_bound_checkpoint_write_is_rejected_without_persisting_a_row(tmp_path: Path) -> None:
    database = tmp_path / "graph.sqlite"
    config = _config(BUNDLE_ID)
    async with AsyncSqliteSaver.from_conn_string(str(database)) as saver:
        await saver.aput(config, _checkpoint("a normal question"), {}, {"request_text": "1"})
        before = _rows(database, "checkpoints", "checkpoint_id, type, checkpoint")
        saver.serde = build_deep_research_checkpoint_serde()
        with pytest.raises(CheckpointStateBoundExceeded):
            await saver.aput(config, _checkpoint(_OVER), {}, {"request_text": "2"})
    assert _rows(database, "checkpoints", "checkpoint_id, type, checkpoint") == before
    assert before  # the retained checkpoint is still the single normal one


async def test_over_bound_single_write_is_rejected_without_persisting_a_row(tmp_path: Path) -> None:
    database = tmp_path / "graph.sqlite"
    config = _config(BUNDLE_ID)
    async with AsyncSqliteSaver.from_conn_string(str(database)) as saver:
        config = await saver.aput(config, _checkpoint("a normal question"), {}, {"request_text": "1"})
        before = _rows(database, "writes", "task_id, idx, channel, type, value")
        saver.serde = build_deep_research_checkpoint_serde()
        with pytest.raises(CheckpointStateBoundExceeded):
            await saver.aput_writes(config, [("wave0", {"oversized": _OVER})], task_id="task-1")
    assert _rows(database, "writes", "task_id, idx, channel, type, value") == before


def test_work_unit_block_bound_is_strictly_below_the_whole_state_bound() -> None:
    assert MAX_WORK_UNIT_BLOCK_BYTES < MAX_CHECKPOINT_STATE_BYTES


def test_legal_sub_blocks_cannot_bypass_the_whole_state_bound() -> None:
    values = {
        "schema_version": RESEARCH_STATE_SCHEMA_VERSION,
        # Each entry is under the per-block bound, but the aggregate is over.
        "notes": [_BIG, _BIG, _BIG, _BIG],
    }
    assert len(json.dumps(values)) > MAX_CHECKPOINT_STATE_BYTES
    with pytest.raises(CheckpointStateBoundExceeded):
        validate_checkpoint_values(values)


def test_over_bound_update_reports_the_owning_phase() -> None:
    with pytest.raises(CheckpointStateBoundExceeded) as excinfo:
        validate_checkpoint_values(
            {"schema_version": RESEARCH_STATE_SCHEMA_VERSION, "request_text": _OVER},
            phase="wave1",
        )
    assert excinfo.value.phase == "wave1"


def test_legacy_checkpoint_is_still_rejected_by_the_shared_validator() -> None:
    with pytest.raises(ValueError, match="checkpoint_schema_legacy"):
        validate_checkpoint_values({"schema_version": RESEARCH_STATE_SCHEMA_VERSION, "repair_counts": {}})


def test_representative_live_state_stays_far_under_the_bound() -> None:
    """Calibration guard: the largest retained store was 7,905 B against a 65,536 B bound.

    A representative max-shaped live state must keep at least 4x headroom; a change that
    inflates the state toward the bound fails here before it can start rejecting runs.
    """

    values: dict[str, Any] = {
        "schema_version": RESEARCH_STATE_SCHEMA_VERSION,
        "readiness_critic_summary": {"note": "c" * 1_622},
        "proposed_profile": {"note": "p" * 1_563},
        "attempts_by_id": {f"g0_wave1_w{i:04d}_a01": {"summary": "a" * 48} for i in range(32)},
        "topic_registry": [{"topic": "t" * 40} for _ in range(32)],
        "report_refs": [{"path": "r" * 60} for _ in range(16)],
        "accepted_submission_refs": ["h_" + "A" * 43 for _ in range(16)],
    }
    assert len(serialize_research_state(values)) <= MAX_CHECKPOINT_STATE_BYTES // 4


async def test_retained_over_bound_checkpoint_is_rejected_before_graph_compile(tmp_path: Path) -> None:
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(
        scope=_BOUND_READ_SCOPE,
        request_text="Reject a retained over-bound checkpoint.",
        implementation_mode="fixture",
    )
    database = lifecycle.private_root(bundle) / "graph.sqlite"
    async with AsyncSqliteSaver.from_conn_string(str(database)) as saver:
        await saver.aput(_config(bundle.bundle_id.value), _checkpoint(_OVER), {}, {"request_text": "1"})
    with pytest.raises(BundleLifecycleError, match="bundle_graph_over_bound"):
        async with lifecycle.open_graph_checkpoint(bundle):
            pass


async def test_internal_block_persists_blocked_with_a_precise_incident(tmp_path: Path) -> None:
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(
        scope=_BLOCK_SCOPE,
        request_text="Block this run.",
        implementation_mode="fixture",
    )
    incident = TerminalIncidentProjection(
        code=RunFailureCode.CHECKPOINT_INCONSISTENT,
        phase="wave1",
        certainty=FailureCertainty.DIRECT,
    )
    state = await lifecycle.record_internal_block(bundle=bundle, incident=incident)
    assert state.terminal_status is LifecycleStatus.BLOCKED
    assert state.terminal_reason is TerminalReason.INTERNAL_BLOCKED
    assert state.latest_incident is not None
    assert state.latest_incident.code is RunFailureCode.CHECKPOINT_INCONSISTENT

    result = lifecycle.result_for_state(
        action=LifecycleAction.RESUME,
        bundle=bundle,
        state=state,
        code=ResultCode.CHECKPOINT_INCONSISTENT,
    )
    assert result.status is LifecycleStatus.BLOCKED
    assert result.terminal_incident is not None
    assert result.terminal_incident.code is RunFailureCode.CHECKPOINT_INCONSISTENT

    # A blocked terminal is not reopened or auto-restarted.
    assert await lifecycle.record_internal_block(bundle=bundle, incident=incident) == state
