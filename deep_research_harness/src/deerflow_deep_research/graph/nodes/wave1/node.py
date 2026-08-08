"""Real Wave1 evidence extraction node.

@impl WON-001
@impl WON-002
@impl WON-005
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from deerflow_deep_research.domain.lifecycle import LogicalPhase
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.state import node_state_update
from deerflow_deep_research.domain.work_units import WORK_UNIT_GATE_VIEW_KEY, canonicalize_source_url

from .review import WAVE1_GATE_REVIEW_KEY, build_wave1_gate_review
from .subgraph import WAVE1_REAL_POLICY, run_wave1_work_units_real


def build_real(dependencies: NodeBuildDependencies):
    if dependencies.work_units is None:
        raise ValueError("work_unit_capability_missing")
    if dependencies.selected_bundle is None:
        raise ValueError("selected_bundle_context_missing")
    if getattr(dependencies.work_units.store, "bundle", None) != dependencies.selected_bundle.bundle:
        raise ValueError("selected_bundle_context_mismatch")

    async def run(state: dict[str, Any]) -> dict[str, Any]:
        topic_registry = state.get("topic_registry") or ()
        accepted_refs = state.get("accepted_submission_refs") or ()
        records = await dependencies.work_units.store.load_records()
        records_by_hash = {record.record_hash: record for record in records}
        bundle_id = state.get("bundle_id")
        generation = state.get("generation", 0)
        if not isinstance(bundle_id, str) or not isinstance(generation, int):
            raise ValueError("wave1_baseline_state_identity_invalid")

        wave0_urls: set[str] = set()
        wave0_record_count = 0
        for record_hash in accepted_refs:
            try:
                record = records_by_hash[record_hash]
            except KeyError as exc:
                raise ValueError("wave1_baseline_record_missing") from exc
            if record.phase is not LogicalPhase.WAVE0:
                continue
            if record.bundle_id != bundle_id or record.generation != generation:
                raise ValueError("wave1_baseline_record_identity_mismatch")
            wave0_record_count += 1
            for source in record.source_refs:
                wave0_urls.add(canonicalize_source_url(source.canonical_url))
        if wave0_record_count == 0:
            raise ValueError("wave1_baseline_wave0_records_missing")

        active_topic_filter = state.get("active_topic_filter") or ()
        topic_filter: tuple[str, ...] | None = tuple(active_topic_filter) if active_topic_filter else None

        result = await run_wave1_work_units_real(
            state,
            controller=dependencies.work_units,
            topic_registry=topic_registry,
            capabilities=dependencies.capabilities,
            wave0_urls=frozenset(wave0_urls),
            topic_filter=topic_filter,
            clock=lambda: datetime.now(UTC),
            event_recorder=dependencies.event_recorder,
        )
        review = await build_wave1_gate_review(
            dependencies.work_units,
            gate_view=result.gate_view,
            policy=WAVE1_REAL_POLICY,
        )
        return {
            **node_state_update("wave1"),
            **result.parent_update,
            WORK_UNIT_GATE_VIEW_KEY: result.gate_view,
            WAVE1_GATE_REVIEW_KEY: review,
        }

    return run
