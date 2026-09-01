"""Finalized-node retention priority inside the bounded journal.

@impl LDO-004
"""

from __future__ import annotations

from pathlib import Path

import pytest

from deerflow_deep_research.domain.run_observation import ObservationInspectability, RunEventCategory
from deerflow_deep_research.runtime.run_observation import (
    RunObservationRecorder,
    RunObservationStore,
)

_BUNDLE_ID = "b_" + "A" * 43


@pytest.mark.asyncio
async def test_finalized_node_facts_survive_capacity_eviction(tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundle"
    (bundle_root / "diagnostics").mkdir(mode=0o700, parents=True)
    store = RunObservationStore(bundle_root=bundle_root, bundle_id=_BUNDLE_ID)
    recorder = RunObservationRecorder(store=store, bundle_id=_BUNDLE_ID)
    await recorder.establish(generation=0, phase="bootstrap", durability="restart_durable")

    finalized_phases = [f"wave{index}" for index in range(12)]
    for phase in finalized_phases:
        await recorder.record(category=RunEventCategory.NODE, phase=phase, attempt_id=f"g0-{phase}-a1", outcome="started")
        await recorder.record(category=RunEventCategory.NODE, phase=phase, attempt_id=f"g0-{phase}-a1", outcome="completed")
    for index in range(400):
        await recorder.record(
            category=RunEventCategory.MODEL_TOOL,
            phase=f"wave{index % 12}",
            attempt_id=f"g0-model-{index}",
            outcome="started",
        )

    journal = await store.inspect(bundle_id=_BUNDLE_ID)
    assert journal.inspectability is ObservationInspectability.AVAILABLE
    assert len(journal.events) <= 256
    retained_finalized = {
        event.phase
        for event in journal.events
        if event.category is RunEventCategory.NODE and event.outcome == "completed"
    }
    assert retained_finalized == set(finalized_phases)
    assert journal.summary is not None
    assert journal.summary.journal_availability.value in {"complete", "incomplete"}
