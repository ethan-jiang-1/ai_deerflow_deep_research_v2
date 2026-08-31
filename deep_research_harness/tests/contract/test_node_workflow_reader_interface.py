"""Deterministic reader-interface contracts for every logical node.

@impl CNI-001
@impl CNI-002
@impl CNI-003
@impl CNI-004
@impl CNI-005
@impl NRI-003
@impl NRI-004
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from deerflow_deep_research.graph.prompt_catalog import prompt_catalog_cases
from scripts.checks.check_node_workflows import (
    AUTHORITY_NOTICE,
    LLM_NODE_ROUTE_HEADING,
    NODE_ROOT,
    WorkflowReaderError,
    load_reader_identity,
    load_reader_inventory,
    validate_reader_text,
)
from tests.assets.cognitive_program_board import COGNITIVE_PROGRAM_BOARD
from tests.assets.node_agent_capabilities import COGNITIVE_PROGRAM_EVIDENCE, COHORT_EVIDENCE

LLM_NODE_READER_NAMES = (
    "wave2_synthesis",
    "hitl1",
    "topic_planning",
    "wave0",
    "wave1",
    "targeted_evidence",
    "readiness",
    "final_delivery",
)


def _card(node: str) -> str:
    return f"""# {node} — Specific product responsibility

> {AUTHORITY_NOTICE}
> Participation mode: bounded cognitive program
> Commitment state: current accepted
> Current operating mechanism: source-audited current mechanism
> Primary cognitive/control program surface: bounded question
> Deterministic authority boundary: typed materializer
> Current model-branch evidence: audit only

## Node Identity
## From Symptoms
## Three Cross-Module Facts
## Route Facts
## Evaluation and Verification Order

## {LLM_NODE_ROUTE_HEADING}

1. **Capability and contract:** [capability](capabilities.py) and [contract](contracts.py)
2. **Prompt and context:** [prompt](prompts.py)
3. **Feedback and repair:** [repair](node.py)
4. **Proof and evaluation:** [proof](../../../../../tests/graph/test_fixture.py)
5. **Deterministic handoff:** [handoff](node.py)
"""


def test_live_reader_inventory_passes() -> None:
    from scripts.checks.check_node_workflows import validate_reader_inventory

    validate_reader_inventory(Path(__file__).resolve().parents[3])


def test_activated_reader_identities_report_current_zero_tool_programs() -> None:
    records = {record.node: record for record in load_reader_inventory(Path(__file__).resolve().parents[3])}

    readiness = records["readiness"]
    assert readiness.participation_mode == "bounded cognitive program"
    assert readiness.commitment_state == "current accepted"
    assert readiness.current_operating_mechanism == "source-audited active zero-tool evidence critic"
    assert readiness.current_model_branch_evidence == "audit only; readiness/critic direct branch"

    final_delivery = records["final_delivery"]
    assert final_delivery.participation_mode == "bounded cognitive program"
    assert final_delivery.commitment_state == "current accepted"
    assert final_delivery.current_operating_mechanism == "source-audited active zero-tool layout composer"
    assert final_delivery.current_model_branch_evidence == "audit only; final-delivery/composer direct branch"

    hitl2 = records["hitl2"]
    assert hitl2.participation_mode == "human decision/authorization"
    assert hitl2.commitment_state == "conditional/unresolved"
    assert hitl2.current_model_branch_evidence == "audit only; no direct branch observed"


def test_reader_identity_loader_is_an_immutable_projection_of_validated_fields() -> None:
    record = load_reader_identity("wave2_synthesis", _card("wave2_synthesis"))

    assert record.node == "wave2_synthesis"
    assert record.product_responsibility == "Specific product responsibility"
    assert record.commitment_state == "current accepted"
    assert record.deterministic_authority_boundary == "typed materializer"
    with pytest.raises(FrozenInstanceError):
        record.commitment_state = "changed"  # type: ignore[misc]


def test_llm_reader_paths_and_direct_branch_inventory_reuse_existing_authorities() -> None:
    root = Path(__file__).resolve().parents[3]
    model_rows = tuple(
        row for row in COGNITIVE_PROGRAM_BOARD.node_rows if row.participation_mode == "bounded cognitive program"
    )
    reader_paths = tuple(NODE_ROOT / row.logical_name / "workflow.md" for row in model_rows)
    board_branch_ids = {branch_id for row in model_rows for branch_id in row.branch_ids}
    prompt_catalog_ids = {case.case_id for case in prompt_catalog_cases()}
    cohort_ids = {row.case_id for row in COHORT_EVIDENCE}
    evidence_ids = {row.case_id for row in COGNITIVE_PROGRAM_EVIDENCE}
    reader_model_names = {
        record.node
        for record in load_reader_inventory(root)
        if record.participation_mode == "bounded cognitive program"
    }

    assert len(reader_paths) == 8
    assert all((root / path).is_file() for path in reader_paths)
    assert reader_model_names == {row.logical_name for row in model_rows}
    assert len(board_branch_ids) == 20
    assert board_branch_ids == prompt_catalog_ids == cohort_ids == evidence_ids


def test_each_direct_branch_reuses_its_existing_capability_prompt_feedback_and_proof_authorities() -> None:
    catalog = {case.case_id: case for case in prompt_catalog_cases()}
    cohort = {row.case_id: row for row in COHORT_EVIDENCE}
    evidence = {row.case_id: row for row in COGNITIVE_PROGRAM_EVIDENCE}
    reviews = {review.branch_id: review for review in COGNITIVE_PROGRAM_BOARD.branch_reviews}

    assert set(catalog) == set(cohort) == set(evidence) == set(reviews)
    for case_id, catalog_case in catalog.items():
        cohort_row = cohort[case_id]
        evidence_row = evidence[case_id]
        review = reviews[case_id]

        assert catalog_case.build_request().capability_ref is not None
        assert evidence_row.capability_id == cohort_row.capability_id
        assert evidence_row.capability_id == catalog_case.build_request().capability_ref.capability_id
        assert evidence_row.catalog_builder_id == catalog_case.builder_id
        assert evidence_row.feedback_source_seam
        assert evidence_row.candidate_shape
        assert evidence_row.deterministic_admission_owner
        assert cohort_row.test_modules
        assert evidence_row.evidence_links
        assert evidence_row.evaluation_rationale
        assert review.known_limitation


@pytest.mark.parametrize(
    ("node", "participation_mode"),
    (
        ("rerun", "deterministic control"),
        ("hitl2", "human decision/authorization"),
    ),
)
def test_non_model_readers_do_not_fabricate_an_llm_prompt_route(node: str, participation_mode: str) -> None:
    text = _card(node).replace(
        "> Participation mode: bounded cognitive program",
        f"> Participation mode: {participation_mode}",
    )
    text = text[: text.index(f"## {LLM_NODE_ROUTE_HEADING}")]

    validate_reader_text(node, text)


@pytest.mark.parametrize("node", LLM_NODE_READER_NAMES)
@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (
            lambda text: text.replace("2. **Prompt and context:** [prompt](prompts.py)\n", ""),
            "llm_authoring_route_step_missing:Prompt and context",
        ),
        (
            lambda text: text.replace(
                "3. **Feedback and repair:** [repair](node.py)",
                "3. **Feedback and repair:** repair",
            ),
            "llm_authoring_route_link_missing:Feedback and repair",
        ),
        (
            lambda text: text.replace(
                "4. **Proof and evaluation:** [proof](../../../../../tests/graph/test_fixture.py)\n"
                "5. **Deterministic handoff:** [handoff](node.py)",
                "5. **Deterministic handoff:** [handoff](node.py)\n"
                "4. **Proof and evaluation:** [proof](../../../../../tests/graph/test_fixture.py)",
            ),
            "llm_authoring_route_order_invalid",
        ),
    ],
)
def test_required_llm_node_reader_routes_reject_missing_or_demoted_owners(
    node: str,
    mutator: object,
    message: str,
) -> None:
    with pytest.raises(WorkflowReaderError, match=message):
        validate_reader_text(node, mutator(_card(node)))  # type: ignore[operator]


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda text: text.replace("## Route Facts\n", ""), "heading_missing:Route Facts"),
        (
            lambda text: text.replace("> Commitment state:", "> Missing commitment state:"),
            "field_missing:Commitment state",
        ),
        (lambda text: text.replace(AUTHORITY_NOTICE, ""), "authority_notice_missing"),
        (lambda text: text.replace("Specific product responsibility", "node-agent"), "charter_identity_forbidden"),
        (
            lambda text: text.replace(
                "## From Symptoms\n## Three",
                "## Three Cross-Module Facts\n## From Symptoms\n## Three",
            ),
            "heading_order_invalid",
        ),
    ],
)
def test_reader_shape_mutations_fail(mutator: object, message: str) -> None:
    with pytest.raises(WorkflowReaderError, match=message):
        validate_reader_text("wave2_synthesis", mutator(_card("wave2_synthesis")))  # type: ignore[operator]
