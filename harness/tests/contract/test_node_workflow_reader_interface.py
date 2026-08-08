"""Deterministic reader-interface contracts for every logical node.

@impl CNI-001
@impl CNI-002
@impl CNI-003
@impl CNI-004
@impl CNI-005
@impl NRI-003
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from scripts.check_node_workflows import (
    AUTHORITY_NOTICE,
    WorkflowReaderError,
    load_reader_identity,
    load_reader_inventory,
    validate_reader_text,
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
"""


def test_live_reader_inventory_passes() -> None:
    from scripts.check_node_workflows import validate_reader_inventory

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
