"""Thin adapter so the graph layer can invoke gate evaluation without importing
from ``engine`` directly (architecture rule: graph → nodes → engine).

@impl GAK-003
@impl GAK-005
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from deerflow_deep_research.domain.gate import GateDefinition
from deerflow_deep_research.domain.state import WriterRole, apply_research_update
from deerflow_deep_research.domain.synthesis import WAVE2_GATE_PREVIEW_KEY, Wave2GatePreview
from deerflow_deep_research.domain.wave1 import (
    MAX_WAVE1_OPEN_QUESTION_PROJECTION,
    WAVE1_GATE_REVIEW_KEY,
    Wave1GateReview,
    Wave1OpenQuestionRef,
)
from deerflow_deep_research.engine.gate_kernel import (
    evaluate_gate,
    gate_result_to_state_update,
)
from deerflow_deep_research.engine.real_gates import (
    build_final_delivery_real_gate_def,
    build_wave0_real_gate_def,
    build_wave1_real_gate_def,
    build_wave2_real_gate_def,
)


def _normalize_projected_ref(ref: object) -> Wave1OpenQuestionRef:
    """Re-validate a projection entry whether it round-tripped as a model or a dict."""

    if isinstance(ref, Wave1OpenQuestionRef):
        return ref
    if isinstance(ref, Mapping):
        return Wave1OpenQuestionRef.model_validate(ref)
    raise ValueError("wave1_open_question_projection_invalid")


def _project_wave1_open_questions(review: Wave1GateReview, existing: object) -> tuple[Wave1OpenQuestionRef, ...]:
    """Merge the review's refs into the checkpointed projection; fail closed on overflow."""

    by_id = {ref.question_id: ref for ref in (_normalize_projected_ref(ref) for ref in existing or ())}
    for ref in (ref for row in review.rows for ref in row.open_questions):
        by_id.setdefault(ref.question_id, ref)
    merged = tuple(sorted(by_id.values(), key=lambda ref: (ref.work_id, ref.question_id)))
    if len(merged) > MAX_WAVE1_OPEN_QUESTION_PROJECTION:
        raise ValueError("wave1_open_question_projection_overflow")
    return merged


def evaluate_gate_for_node(
    state: Mapping[str, Any],
    logical_name: str,
    gate_def: GateDefinition,
) -> dict[str, Any]:
    """Run gate evaluation for *logical_name* and return a state update dict."""
    gate_result = evaluate_gate(state, logical_name, gate_def)
    update = gate_result_to_state_update(gate_result, logical_name, state)
    preview = state.get(WAVE2_GATE_PREVIEW_KEY)
    if logical_name == "wave2_synthesis" and isinstance(preview, Wave2GatePreview):
        gap_update = apply_research_update(
            state,
            {"unresolved_gaps": preview.searchable_gap_ids},
            writer=WriterRole.GATE,
        )
        update = {**update, **gap_update}
    wave1_review = state.get(WAVE1_GATE_REVIEW_KEY)
    if logical_name == "wave1" and isinstance(wave1_review, Wave1GateReview):
        question_update = apply_research_update(
            state,
            {"wave1_open_questions": _project_wave1_open_questions(wave1_review, state.get("wave1_open_questions"))},
            writer=WriterRole.GATE,
        )
        update = {**update, **question_update}
    return update


def all_real_gate_defs() -> dict[str, GateDefinition]:
    """Return the explicit production gate map for the all-real recipe."""
    return {
        "wave0": real_wave0_gate_def(),
        "wave1": real_wave1_gate_def(),
        "wave2_synthesis": real_wave2_gate_def(),
        "final_delivery": real_final_delivery_gate_def(),
    }


def real_wave0_gate_def() -> GateDefinition:
    """Return the real Wave0 ``GateDefinition`` (completion/drain only)."""
    return build_wave0_real_gate_def()


def real_wave1_gate_def() -> GateDefinition:
    """Return the real Wave1 ``GateDefinition`` (completion/drain only)."""
    return build_wave1_real_gate_def()


def real_wave2_gate_def() -> GateDefinition:
    """Return the real Wave2 ``GateDefinition`` (searchable-gap routing)."""
    return build_wave2_real_gate_def()


def real_final_delivery_gate_def() -> GateDefinition:
    """Return the real final delivery ``GateDefinition``."""
    return build_final_delivery_real_gate_def()


__all__ = [
    "all_real_gate_defs",
    "evaluate_gate_for_node",
    "real_final_delivery_gate_def",
    "real_wave0_gate_def",
    "real_wave1_gate_def",
    "real_wave2_gate_def",
]
