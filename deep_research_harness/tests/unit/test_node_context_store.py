"""NodeContextSnapshot store and capture-seam contracts.

@impl LDO-005
@impl LDO-006
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from deerflow_deep_research.domain.node_context import (
    CapturedResourceLayer,
    EnforcedToolPosture,
    NodeContextActivityFacts,
    NodeContextSnapshot,
    VirtualRootsView,
)
from deerflow_deep_research.runtime.node_context_store import (
    NodeContextCapacityError,
    NodeContextConflictError,
    NodeContextRecorder,
    NodeContextStore,
)


def _snapshot(ordinal: int = 1, *, body: str = "capability body") -> NodeContextSnapshot:
    return NodeContextSnapshot(
        context_id=f"ctx-{ordinal:032x}"[:32],
        bundle_id="b_" + "A" * 43,
        node="wave0",
        attempt_id=f"g0-wave0-a{ordinal}",
        node_agent_ordinal=ordinal,
        created_at=datetime.now(UTC),
        initial_system_policy="system policy text",
        initial_human_message="Objective: compare storage",
        base_policy_layer=CapturedResourceLayer(
            identity="resources/node_agent/runtime_policy.md",
            text="base policy",
            sha256=__import__("hashlib").sha256(b"base policy").hexdigest(),
        ),
        capability_layer=CapturedResourceLayer(
            identity="pkg:capabilities/wave0.md",
            text=body,
            sha256=__import__("hashlib").sha256(body.encode()).hexdigest(),
        ),
        request_objective="Compare storage options",
        request_expected_output="A comparison",
        safe_model_label="configured-model",
        tool_posture=EnforcedToolPosture(
            requested_tool_names=("web_search",),
            enforced_tool_names=("web_search",),
            posture_kind="required",
        ),
        budget={"max_model_calls": 8, "wall_time_seconds": 600},
        virtual_roots=VirtualRootsView(workspace_root="/mnt/user-data/workspace"),
    )


@pytest.mark.asyncio
async def test_store_publishes_atomically_and_reads_back(tmp_path: Path) -> None:
    store = NodeContextStore(bundle_root=tmp_path, bundle_id="b_" + "A" * 43)
    recorder = NodeContextRecorder(store)
    key = await recorder.record(_snapshot())
    assert key == "g0-wave0-a1/0001"

    view = store.read(key)
    assert view is not None
    assert view.snapshot.initial_system_policy == "system policy text"
    assert view.provenance["initial_system_policy"] == "MODEL_VISIBLE"
    assert view.coverage_outcome == "UNAVAILABLE"
    assert view.raw_provider_history == "NOT_RETAINED"

    await recorder.record_activity(key, NodeContextActivityFacts(model_calls=3, tool_calls=1, outcome="completed"))
    view = store.read(key)
    assert view is not None and view.activity is not None
    assert view.activity.model_calls == 3
    assert view.coverage_outcome == "OBSERVED"

    page = store.page()
    assert page.total == 1
    assert page.summaries[0].attempt_id == "g0-wave0-a1"


@pytest.mark.asyncio
async def test_same_identity_conflicts_and_capacity_is_typed(tmp_path: Path) -> None:
    store = NodeContextStore(bundle_root=tmp_path, bundle_id="b_" + "A" * 43, max_contexts_per_bundle=2)
    recorder = NodeContextRecorder(store)
    await recorder.record(_snapshot(ordinal=1))
    with pytest.raises(NodeContextConflictError):
        await recorder.record(_snapshot(ordinal=1, body="different body"))
    await recorder.record(_snapshot(ordinal=2))
    with pytest.raises(NodeContextCapacityError):
        await recorder.record(_snapshot(ordinal=3))


@pytest.mark.asyncio
async def test_collection_index_survives_and_orders_per_segment(tmp_path: Path) -> None:
    store = NodeContextStore(bundle_root=tmp_path, bundle_id="b_" + "A" * 43)
    recorder = NodeContextRecorder(store)
    await recorder.record(_snapshot(ordinal=2))
    await recorder.record(_snapshot(ordinal=1))
    page = store.page()
    keys = [summary.attempt_id for summary in page.summaries]
    assert keys == ["g0-wave0-a1", "g0-wave0-a2"]
    reloaded = NodeContextStore(bundle_root=tmp_path, bundle_id="b_" + "A" * 43)
    assert reloaded.page().total == 2


@pytest.mark.asyncio
async def test_source_reader_reports_match_drift_and_serves_captured_bytes(tmp_path: Path) -> None:
    from types import SimpleNamespace

    from deerflow_deep_research.runtime.node_context_store import NodeSourceReader

    store = NodeContextStore(bundle_root=tmp_path, bundle_id="b_" + "A" * 43)
    recorder = NodeContextRecorder(store)
    await recorder.record(_snapshot(ordinal=1, body="capability body v1"))
    key = "g0-wave0-a1/0001"

    reader = NodeSourceReader(store=store, current_loader=lambda: SimpleNamespace(policy="capability body v1"))
    view = reader.view(key)
    assert view.capability_status == "MATCH"
    assert view.note == "NOT_MODEL_VISIBLE"

    drifted = NodeSourceReader(
        store=store, current_loader=lambda: SimpleNamespace(policy="capability body v2 (edited)")
    )
    view = drifted.view(key)
    assert view.capability_status == "DRIFT"
    stored = store.read(key)
    assert stored is not None and stored.snapshot.capability_layer.text == "capability body v1"

    missing = NodeSourceReader(
        store=store,
        current_loader=lambda: (_ for _ in ()).throw(FileNotFoundError("resource gone")),
    )
    view = missing.view(key)
    assert view.capability_status == "CURRENT_SOURCE_UNAVAILABLE"
