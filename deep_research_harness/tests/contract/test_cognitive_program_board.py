"""Exact node, branch, and evaluation joins for the cognitive-program board.

@impl CPE-001
@impl CPE-004
@impl EVH-017
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from deerflow_deep_research.graph.topology import LOGICAL_NODES
from tests.assets.cognitive_program_board import (
    COGNITIVE_PROGRAM_BOARD,
    BranchEvidenceReview,
    CognitiveProgramBoardError,
    CognitiveProgramEvidenceBoard,
    NodeEvidenceLink,
    validate_cognitive_program_board,
)
from tests.assets.evidence import EVIDENCE_CLAIMS, TestEvidenceClaim, claim_index
from tests.assets.node_agent_capabilities import (
    COHORT_EVIDENCE,
    CognitiveProgramEvidenceLink,
    EvidenceClassification,
    EvidenceRole,
)
from tests.assets.node_conformance import NODE_CONFORMANCE
from tests.assets.requirement_evidence import REQUIREMENT_IMPACTS
from tests.assets.workflow_nodes import MODEL_WORKFLOW_COVERAGE
from tests.scenarios.evidence_intake_calibration import EVIDENCE_INTAKE_CALIBRATION_CASES
from tests.scenarios.evidence_judgment_calibration import EVIDENCE_JUDGMENT_CALIBRATION_CASES
from tests.scenarios.final_composition_calibration import FINAL_COMPOSITION_CALIBRATION_CASES
from tests.scenarios.intake_planning_calibration import CALIBRATION_CASES

REPO_ROOT = Path(__file__).resolve().parents[3]
CALIBRATION_CASES_BY_REGISTRY = (
    CALIBRATION_CASES,
    EVIDENCE_INTAKE_CALIBRATION_CASES,
    EVIDENCE_JUDGMENT_CALIBRATION_CASES,
    FINAL_COMPOSITION_CALIBRATION_CASES,
)
ALL_CALIBRATION_CASES = tuple(case for registry in CALIBRATION_CASES_BY_REGISTRY for case in registry)


def _reader_records():
    from scripts.checks.check_node_workflows import load_reader_inventory

    return load_reader_inventory(REPO_ROOT)


def _validate(
    board: CognitiveProgramEvidenceBoard = COGNITIVE_PROGRAM_BOARD,
    *,
    calibration_cases: tuple[object, ...] = ALL_CALIBRATION_CASES,
    claims: dict[str, TestEvidenceClaim] | None = None,
    collected_selectors: set[str] | None = None,
) -> None:
    claims = claim_index(EVIDENCE_CLAIMS) if claims is None else claims
    if collected_selectors is None:
        collected_selectors = {claim.selector for claim in claims.values()}
    validate_cognitive_program_board(
        board,
        logical_nodes=LOGICAL_NODES,
        reader_records=_reader_records(),
        cohort_rows=COHORT_EVIDENCE,
        workflow_coverage=MODEL_WORKFLOW_COVERAGE,
        node_conformance=NODE_CONFORMANCE,
        claims=claims,
        requirement_impacts=REQUIREMENT_IMPACTS,
        calibration_cases=calibration_cases,
        collected_selectors=collected_selectors,
    )


def test_board_closes_exact_current_node_branch_and_calibration_denominators() -> None:
    _validate()

    assert tuple(row.logical_name for row in COGNITIVE_PROGRAM_BOARD.node_rows) == LOGICAL_NODES
    assert len(COGNITIVE_PROGRAM_BOARD.branch_rows) == 20
    assert len(COGNITIVE_PROGRAM_BOARD.branch_reviews) == 20
    assert sum(len(review.evaluation_links) for review in COGNITIVE_PROGRAM_BOARD.branch_reviews) == 41


@pytest.mark.parametrize(
    ("board", "calibration_cases", "message"),
    [
        pytest.param(
            replace(COGNITIVE_PROGRAM_BOARD, node_rows=COGNITIVE_PROGRAM_BOARD.node_rows[:-1]),
            ALL_CALIBRATION_CASES,
            "node denominator invalid",
            id="missing-node",
        ),
        pytest.param(
            replace(
                COGNITIVE_PROGRAM_BOARD,
                node_rows=(
                    COGNITIVE_PROGRAM_BOARD.node_rows[0],
                    replace(
                        COGNITIVE_PROGRAM_BOARD.node_rows[1],
                        logical_name=COGNITIVE_PROGRAM_BOARD.node_rows[0].logical_name,
                    ),
                    *COGNITIVE_PROGRAM_BOARD.node_rows[2:],
                ),
            ),
            ALL_CALIBRATION_CASES,
            "node denominator invalid",
            id="duplicate-node",
        ),
        pytest.param(
            replace(COGNITIVE_PROGRAM_BOARD, branch_rows=COGNITIVE_PROGRAM_BOARD.branch_rows[:-1]),
            ALL_CALIBRATION_CASES,
            "missing ledger row",
            id="missing-branch-row",
        ),
        pytest.param(
            replace(COGNITIVE_PROGRAM_BOARD, branch_reviews=COGNITIVE_PROGRAM_BOARD.branch_reviews[:-1]),
            ALL_CALIBRATION_CASES,
            "branch review denominator invalid",
            id="missing-branch-review",
        ),
        pytest.param(
            replace(
                COGNITIVE_PROGRAM_BOARD,
                branch_reviews=tuple(
                    replace(review, evaluation_links=()) for review in COGNITIVE_PROGRAM_BOARD.branch_reviews
                ),
            ),
            (),
            "calibration case denominator invalid",
            id="self-consistently-empty-calibration-source",
        ),
        pytest.param(
            COGNITIVE_PROGRAM_BOARD,
            (*ALL_CALIBRATION_CASES[:-1], ALL_CALIBRATION_CASES[0]),
            "calibration case denominator invalid",
            id="duplicate-and-missing-calibration-case",
        ),
    ],
)
def test_board_rejects_incomplete_or_self_consistent_denominators(
    board: CognitiveProgramEvidenceBoard,
    calibration_cases: tuple[object, ...],
    message: str,
) -> None:
    with pytest.raises(CognitiveProgramBoardError, match=message):
        _validate(board, calibration_cases=calibration_cases)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("product_responsibility", "node-agent", "product responsibility invalid"),
        ("product_responsibility", "", "node identity field missing"),
        ("participation_mode", "", "node identity field missing"),
        ("commitment_state", "", "node identity field missing"),
        ("current_operating_mechanism", "", "node identity field missing"),
        ("cognitive_or_control_hypothesis", "", "node identity field missing"),
        ("deterministic_authority", "", "node identity field missing"),
        ("live_evaluation_applicability", "", "live evaluation applicability missing"),
        ("known_limitation", "", "known limitation missing"),
    ],
)
def test_board_rejects_missing_or_generic_node_identity(field: str, value: str, message: str) -> None:
    row = replace(COGNITIVE_PROGRAM_BOARD.node_rows[0], **{field: value})
    board = replace(COGNITIVE_PROGRAM_BOARD, node_rows=(row, *COGNITIVE_PROGRAM_BOARD.node_rows[1:]))

    with pytest.raises(CognitiveProgramBoardError, match=message):
        _validate(board)


def test_board_rejects_false_active_loop_and_wrong_branch_owner() -> None:
    bootstrap = replace(
        COGNITIVE_PROGRAM_BOARD.node_rows[0],
        participation_mode="bounded cognitive program",
        commitment_state="current accepted",
        branch_ids=("hitl1/brief",),
    )
    board = replace(COGNITIVE_PROGRAM_BOARD, node_rows=(bootstrap, *COGNITIVE_PROGRAM_BOARD.node_rows[1:]))

    with pytest.raises(CognitiveProgramBoardError, match="bootstrap: branch owner invalid"):
        _validate(board)


def test_board_rejects_under_specified_or_human_classified_active_branch() -> None:
    first = COGNITIVE_PROGRAM_BOARD.branch_rows[0]
    without_feedback = replace(
        first,
        evidence_links=tuple(
            link for link in first.evidence_links if link.role is not EvidenceRole.FEEDBACK_DISPOSITION
        ),
    )
    with pytest.raises(CognitiveProgramBoardError, match="missing feedback-disposition evidence role"):
        _validate(
            replace(COGNITIVE_PROGRAM_BOARD, branch_rows=(without_feedback, *COGNITIVE_PROGRAM_BOARD.branch_rows[1:]))
        )

    human_classified = replace(
        first,
        evidence_links=(
            CognitiveProgramEvidenceLink(
                claim_id=first.evidence_links[0].claim_id,
                role=first.evidence_links[0].role,
                classification=EvidenceClassification.HUMAN_DECISION,
            ),
            *first.evidence_links[1:],
        ),
    )
    with pytest.raises(CognitiveProgramBoardError, match="human-decision cannot close an active branch"):
        _validate(
            replace(COGNITIVE_PROGRAM_BOARD, branch_rows=(human_classified, *COGNITIVE_PROGRAM_BOARD.branch_rows[1:]))
        )


def test_board_rejects_unknown_uncollected_and_wrong_owner_node_proof() -> None:
    first_row = COGNITIVE_PROGRAM_BOARD.node_rows[0]
    first_link = first_row.evidence_links[0]

    unknown = replace(first_row, evidence_links=(replace(first_link, claim_id="missing-board-claim"),))
    with pytest.raises(CognitiveProgramBoardError, match="unknown node claim"):
        _validate(replace(COGNITIVE_PROGRAM_BOARD, node_rows=(unknown, *COGNITIVE_PROGRAM_BOARD.node_rows[1:])))

    claims = claim_index(EVIDENCE_CLAIMS)
    collected = {claim.selector for claim in claims.values()}
    collected.remove(claims[first_link.claim_id].selector)
    with pytest.raises(CognitiveProgramBoardError, match="uncollected node claim"):
        _validate(claims=claims, collected_selectors=collected)

    hitl1_link = COGNITIVE_PROGRAM_BOARD.node_rows[1].evidence_links[0]
    wrong_owner = replace(first_row, evidence_links=(NodeEvidenceLink(hitl1_link.claim_id, hitl1_link.classification),))
    with pytest.raises(CognitiveProgramBoardError, match="bootstrap: node claim owner invalid"):
        _validate(replace(COGNITIVE_PROGRAM_BOARD, node_rows=(wrong_owner, *COGNITIVE_PROGRAM_BOARD.node_rows[1:])))


def test_board_rejects_missing_or_cross_branch_evaluation_link() -> None:
    first = COGNITIVE_PROGRAM_BOARD.branch_reviews[0]
    missing = replace(first, evaluation_links=first.evaluation_links[:-1])
    with pytest.raises(CognitiveProgramBoardError, match="calibration link denominator invalid"):
        _validate(
            replace(COGNITIVE_PROGRAM_BOARD, branch_reviews=(missing, *COGNITIVE_PROGRAM_BOARD.branch_reviews[1:]))
        )

    last_link = COGNITIVE_PROGRAM_BOARD.branch_reviews[-1].evaluation_links[0]
    crossed = replace(first, evaluation_links=(last_link, *first.evaluation_links[1:]))
    with pytest.raises(CognitiveProgramBoardError, match="evaluation case belongs to a different branch"):
        _validate(
            replace(COGNITIVE_PROGRAM_BOARD, branch_reviews=(crossed, *COGNITIVE_PROGRAM_BOARD.branch_reviews[1:]))
        )


def test_board_is_review_metadata_and_cannot_authorize_deletion() -> None:
    assert not hasattr(COGNITIVE_PROGRAM_BOARD, "delete")
    assert not hasattr(BranchEvidenceReview, "delete")
