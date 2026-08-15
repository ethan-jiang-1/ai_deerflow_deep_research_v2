"""Pure real Wave1 review-gate rules.

@impl WON-004
"""

from __future__ import annotations

import pytest

from deerflow_deep_research.domain.wave1 import (
    WAVE1_GATE_REVIEW_KEY,
    OpenQuestionState,
    Wave1GateReview,
    Wave1GateReviewRow,
)
from deerflow_deep_research.domain.work_units import WORK_UNIT_GATE_VIEW_KEY, WorkUnitGateView
from deerflow_deep_research.engine.gate_kernel import evaluate_gate
from deerflow_deep_research.engine.real_gates import build_wave1_real_gate_def

WORK_ID = "g0_wave1_w0000"
ATTEMPT_ID = f"{WORK_ID}_a00"
RECORD_HASH = "h_" + "W" * 43


def _view(*, drained: bool = True, accepted: bool = True) -> WorkUnitGateView:
    return WorkUnitGateView(
        drained=drained,
        planned_work_ids=(WORK_ID,),
        terminal_attempt_by_work_id={WORK_ID: ATTEMPT_ID} if drained else {},
        accepted_record_by_work_id={WORK_ID: RECORD_HASH} if accepted else {},
        failure_summaries=(),
    )


def _review(
    *,
    new_urls: int = 2,
    source_review: bool = True,
    claim_review: bool = True,
    questions: tuple[OpenQuestionState, ...] = (),
    record_hash: str = RECORD_HASH,
) -> Wave1GateReview:
    return Wave1GateReview(
        rows=(
            Wave1GateReviewRow(
                work_id=WORK_ID,
                accepted_record_hash=record_hash,
                distinct_new_url_count=new_urls,
                source_diagnostic_present=source_review,
                claim_verifier_present=claim_review,
                open_question_states=questions,
            ),
        )
    )


def _state(**updates):
    return {
        "generation": 0,
        "gate_attempts_by_phase": {},
        "repair_budget_by_phase": {},
        "latest_gate_feedback": None,
        WORK_UNIT_GATE_VIEW_KEY: _view(),
        WAVE1_GATE_REVIEW_KEY: _review(),
        **updates,
    }


def test_real_wave1_review_gate_passes_only_with_floor_reviews_and_allowed_questions() -> None:
    result = evaluate_gate(_state(), "wave1", build_wave1_real_gate_def())

    assert result.verdict.value == "pass"
    assert result.route == "pass"


@pytest.mark.parametrize(
    "review",
    [
        pytest.param(_review(new_urls=1), id="source-floor"),
        pytest.param(_review(source_review=False), id="source-review-missing"),
        pytest.param(_review(claim_review=False), id="claim-review-missing"),
    ],
)
def test_real_wave1_review_gate_routes_repair_for_each_repairable_review_failure(review) -> None:
    result = evaluate_gate(_state(**{WAVE1_GATE_REVIEW_KEY: review}), "wave1", build_wave1_real_gate_def())

    assert result.verdict.value == "repair"
    assert result.route == "repair"


def test_real_wave1_review_gate_defers_targeted_questions_to_synthesis() -> None:
    result = evaluate_gate(
        _state(**{WAVE1_GATE_REVIEW_KEY: _review(questions=(OpenQuestionState.TARGETED_SEARCH,))}),
        "wave1",
        build_wave1_real_gate_def(),
    )

    assert result.verdict.value == "pass"
    assert result.route == "pass"


def test_real_wave1_review_rules_noop_while_structural_completion_is_absent() -> None:
    result = evaluate_gate(
        _state(**{WORK_UNIT_GATE_VIEW_KEY: _view(drained=False, accepted=False), WAVE1_GATE_REVIEW_KEY: None}),
        "wave1",
        build_wave1_real_gate_def(),
    )

    assert result.verdict.value == "repair"
    assert tuple(failure.rule_name for failure in result.failures) == ("work_unit_completion",)


def test_real_wave1_review_projection_mismatch_fails_before_route_evaluation() -> None:
    with pytest.raises(ValueError, match="wave1_gate_review_gate_view_mismatch"):
        evaluate_gate(
            _state(**{WAVE1_GATE_REVIEW_KEY: _review(record_hash="h_" + "X" * 43)}),
            "wave1",
            build_wave1_real_gate_def(),
        )


def test_real_wave1_source_floor_exhausts_under_existing_budget_kernel() -> None:
    result = evaluate_gate(
        _state(
            repair_budget_by_phase={"wave1": 0},
            **{WAVE1_GATE_REVIEW_KEY: _review(new_urls=1)},
        ),
        "wave1",
        build_wave1_real_gate_def(),
    )

    assert result.verdict.value == "blocked"
    assert result.route == "exhausted"
