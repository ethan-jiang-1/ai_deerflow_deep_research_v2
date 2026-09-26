"""Minimized Wave2 provider shapes through the production parser.

@impl EVH-006
@impl EVH-010
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from deerflow_deep_research.graph.nodes.wave2_synthesis.prompts import parse_synthesis_output
from tests.assets.provider_shapes import load_provider_shape_cases, thaw_provider_shape_payload

CASES = tuple(
    case
    for case in load_provider_shape_cases(Path(__file__).parents[1] / "fixtures/provider_shapes/wave2.json")
    if case.case_id != "shape-wave2-evidence-alias-binding"
)


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.case_id)
def test_wave2_provider_shape(case) -> None:
    output = parse_synthesis_output(json.dumps(thaw_provider_shape_payload(case.payload)))
    observed = {
        "findings": [finding.model_dump(mode="json") for finding in output.findings],
        "relations": [relation.model_dump(mode="json") for relation in output.relations],
        "gaps": [gap.model_dump(mode="json") for gap in output.gaps],
        "summary": output.summary,
    }
    assert observed == thaw_provider_shape_payload(case.expected_payload)


def _synthesis_payload(**overrides: object) -> str:
    payload: dict[str, object] = {
        "schema_version": 1,
        "findings": [],
        "relations": [],
        "gaps": [],
        "summary": "",
    }
    payload.update(overrides)
    return json.dumps(payload)


def test_wave2_schema_invalid_candidate_stays_in_the_closed_vocabulary_with_detail() -> None:
    """@impl WSN-008

    A JSON-valid but schema-invalid model candidate raises a closed
    ``synthesis_output_*`` code with a bounded structured ``detail`` projection,
    so the repair prompt and the rejection log carry concrete field feedback
    instead of an escaped pydantic ``ValidationError`` (bare ``ValueError``
    message, no ``detail``) that lands in the generic ``candidate_invalid``
    bucket.
    """
    from deerflow_deep_research.graph.nodes.wave2_synthesis.node import _synthesis_validation_category
    from deerflow_deep_research.graph.nodes.wave2_synthesis.prompts import SynthesisValidationFailure

    with pytest.raises(ValueError) as excinfo:
        parse_synthesis_output(json.dumps({"findings": []}))
    assert str(excinfo.value).startswith("synthesis_output_")
    assert isinstance(excinfo.value, SynthesisValidationFailure)
    assert _synthesis_validation_category(excinfo.value) == "parser_invalid"
    detail = getattr(excinfo.value, "detail", None)
    errors = detail.get("schema_errors") if isinstance(detail, dict) else None
    assert isinstance(errors, list) and 0 < len(errors) <= 3
    assert errors[0]["loc"] == "schema_version"


def test_wave2_finding_priority_labels_normalize_to_ints() -> None:
    """@impl WSN-001

    Provider string priority labels map to the typed int 1-5 contract before
    validation; integers pass through.
    """
    output = parse_synthesis_output(
        _synthesis_payload(
            findings=[
                {"id": "a", "statement": "S1", "priority": "high", "confidence": "high"},
                {"id": "b", "statement": "S2", "priority": "moderate", "confidence": "medium"},
                {"id": "c", "statement": "S3", "priority": "low", "confidence": "low"},
                {"id": "d", "statement": "S4", "priority": 2, "confidence": "high"},
            ]
        )
    )
    assert [finding.priority for finding in output.findings] == [1, 3, 5, 2]


def test_wave2_gap_priority_labels_normalize_to_ints() -> None:
    """@impl WSN-001"""
    output = parse_synthesis_output(
        _synthesis_payload(
            gaps=[
                {"id": "a", "description": "G1", "priority": "critical"},
                {"id": "b", "description": "G2", "priority": "medium"},
                {"id": "c", "description": "G3", "priority": "low"},
            ]
        )
    )
    assert [gap.priority for gap in output.gaps] == [1, 3, 5]


def test_wave2_gap_prose_questions_fold_into_description() -> None:
    """@impl WSN-001

    Natural-language gap ``source_questions`` fold into the description; only
    ``q:w1_*`` ids stay in the typed refs.
    """
    output = parse_synthesis_output(
        _synthesis_payload(
            gaps=[
                {
                    "id": "a",
                    "description": "Gap about storage cost.",
                    "priority": 1,
                    "source_questions": ["q:w1_storage_cost", "What does storage cost per kWh in 2024?"],
                }
            ]
        )
    )
    gap = output.gaps[0]
    assert gap.source_questions == ("q:w1_storage_cost",)
    assert "What does storage cost per kWh in 2024?" in gap.description


def test_wave2_resolved_questions_keep_only_contract_ids() -> None:
    """@impl WSN-001"""
    output = parse_synthesis_output(
        _synthesis_payload(resolved_questions=["q:w1_a", "Some natural language note", "q:w1_b"])
    )
    assert output.resolved_questions == ("q:w1_a", "q:w1_b")
