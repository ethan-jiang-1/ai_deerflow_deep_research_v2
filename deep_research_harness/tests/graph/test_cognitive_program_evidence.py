"""Branch-local deterministic proof for active cognitive-program evidence.

@impl CPE-001
@impl CPE-002
@impl NPC-006
@impl NAC-008
@impl EVH-017
@impl CPE-003
@impl NPC-007
@impl NAC-009
@impl EVH-022
"""

from __future__ import annotations

import pytest

from deerflow_deep_research.agents.node_cognitive_control_program import render_node_cognitive_control_program
from deerflow_deep_research.graph.prompt_catalog import prompt_catalog_cases
from tests.assets.node_agent_capabilities import (
    COGNITIVE_PROGRAM_EVIDENCE,
    EvaluationDisposition,
    FeedbackDisposition,
    RequestedToolWindow,
)

EXPECTED_FEEDBACK = {
    "hitl1/brief": (
        FeedbackDisposition.DELIVERED,
        "hitl1/brief-repair",
        ("structured_output_invalid",),
        (),
        "graph/nodes/hitl1/node.py::_generate_brief",
    ),
    "hitl1/brief-repair": (
        FeedbackDisposition.ABSENT,
        None,
        (),
        (),
        "graph/nodes/hitl1/node.py::_generate_brief",
    ),
    "hitl1/semantic-intake": (
        FeedbackDisposition.DELIVERED,
        "hitl1/semantic-intake-repair",
        ("semantic_candidate_invalid",),
        (),
        "graph/nodes/hitl1/node.py::_classify_proposal_reply",
    ),
    "hitl1/semantic-intake-repair": (
        FeedbackDisposition.ABSENT,
        None,
        (),
        (),
        "graph/nodes/hitl1/node.py::_classify_proposal_reply",
    ),
    "topic-planning/plan": (
        FeedbackDisposition.DELIVERED,
        "topic-planning/plan-repair",
        ("repair_error",),
        (),
        "graph/nodes/topic_planning/node.py::_generate_plan",
    ),
    "topic-planning/plan-repair": (
        FeedbackDisposition.ABSENT,
        None,
        (),
        (),
        "graph/nodes/topic_planning/node.py::_generate_plan",
    ),
    "readiness/critic": (
        FeedbackDisposition.ABSENT,
        None,
        (),
        (),
        "graph/nodes/readiness/node.py::build_real",
    ),
    "wave0/worker": (
        FeedbackDisposition.PARTIAL,
        "wave0/repair",
        ("assignment_projection", "initial_structured_output_invalid", "draft", "untrusted_tool_results"),
        ("raw_parse_error", "submission_validation_codes", "artifact_validation_detail"),
        "graph/nodes/wave0/subgraph.py::run_wave0_work_units_real",
    ),
    "wave0/repair": (
        FeedbackDisposition.ABSENT,
        None,
        (),
        (),
        "graph/nodes/wave0/subgraph.py::run_wave0_work_units_real",
    ),
    "wave1/worker": (
        FeedbackDisposition.PARTIAL,
        "wave1/repair",
        (
            "assignment_projection",
            "initial_structured_output_invalid_or_local_semantic_validation_failed",
            "draft",
            "untrusted_tool_results",
        ),
        ("raw_parse_error", "submission_validation_codes", "artifact_validation_detail"),
        "graph/nodes/wave1/subgraph.py::_wave1_worker",
    ),
    "wave1/repair": (
        FeedbackDisposition.ABSENT,
        None,
        (),
        (),
        "graph/nodes/wave1/subgraph.py::_wave1_worker",
    ),
    "wave1/source-diagnostic": (
        FeedbackDisposition.ABSENT,
        None,
        (),
        (),
        "graph/nodes/wave1/review.py::_dispatch_missing_reviews",
    ),
    "wave1/claim-verifier": (
        FeedbackDisposition.ABSENT,
        None,
        (),
        (),
        "graph/nodes/wave1/review.py::_dispatch_missing_reviews",
    ),
    "wave2-synthesis/synthesis": (
        FeedbackDisposition.PARTIAL,
        "wave2-synthesis/repair",
        ("draft", "accepted_evidence", "closed_validation_category"),
        ("raw_exception",),
        "graph/nodes/wave2_synthesis/node.py::build_real",
    ),
    "wave2-synthesis/repair": (
        FeedbackDisposition.ABSENT,
        None,
        (),
        (),
        "graph/nodes/wave2_synthesis/node.py::build_real",
    ),
    "targeted-evidence/worker": (
        FeedbackDisposition.DELIVERED,
        "targeted-evidence/repair",
        ("draft", "validation_error"),
        (),
        "graph/nodes/targeted_evidence/subgraph.py::run_gap_workers",
    ),
    "targeted-evidence/repair": (
        FeedbackDisposition.ABSENT,
        None,
        (),
        (),
        "graph/nodes/targeted_evidence/subgraph.py::run_gap_workers",
    ),
    "targeted-evidence/source-diagnostic": (
        FeedbackDisposition.ABSENT,
        None,
        (),
        (),
        "graph/nodes/targeted_evidence/subgraph.py::dispatch_critic",
    ),
    "targeted-evidence/claim-verifier": (
        FeedbackDisposition.ABSENT,
        None,
        (),
        (),
        "graph/nodes/targeted_evidence/subgraph.py::dispatch_critic",
    ),
    "final-delivery/composer": (
        FeedbackDisposition.ABSENT,
        None,
        (),
        (),
        "graph/nodes/final_delivery/node.py::build_real",
    ),
}


@pytest.mark.parametrize("row", COGNITIVE_PROGRAM_EVIDENCE, ids=lambda row: row.case_id)
def test_cognitive_program_composition(row) -> None:
    """Each ledger row joins one catalog builder to its final rendered capability."""

    catalog_case = next(case for case in prompt_catalog_cases() if case.case_id == row.case_id)
    request = catalog_case.build_request()
    rendered = render_node_cognitive_control_program(request, attempt_workspace=catalog_case.attempt_workspace)

    assert catalog_case.builder_id == row.catalog_builder_id
    assert request.capability_ref is not None
    assert request.capability_ref.capability_id == row.capability_id
    assert row.requested_tool_window == RequestedToolWindow(
        tools_enabled=request.tools_enabled,
        minimum_tool_calls=request.minimum_tool_calls,
        tool_call_limit=request.tool_call_limit,
    )
    assert rendered.capability is not None
    assert rendered.capability.ref == request.capability_ref
    assert request.objective in rendered.user_message
    assert request.expected_output in rendered.user_message
    assert catalog_case.attempt_workspace in rendered.user_message


@pytest.mark.parametrize("case_id", ("wave1/worker", "wave1/repair"))
def test_wave1_cognitive_program_keeps_method_in_the_rendered_capability(case_id: str) -> None:
    """@impl WON-010"""

    catalog_case = next(case for case in prompt_catalog_cases() if case.case_id == case_id)
    request = catalog_case.build_request()
    rendered = render_node_cognitive_control_program(request, attempt_workspace=catalog_case.attempt_workspace)

    assert rendered.capability is not None
    assert rendered.capability.policy.strip() in rendered.system_policy
    assert "activated" in request.objective
    assert "Wave0 baseline constrains newness" not in request.objective
    if case_id == "wave1/worker":
        assert "exactly one retrieval" in rendered.system_policy
        assert "exactly one web search" not in request.objective
    else:
        assert "This is a zero-tool repair" in rendered.system_policy
        assert "Do not retrieve" not in request.objective


@pytest.mark.parametrize(
    ("case_id", "method_markers"),
    (
        pytest.param(
            "wave2-synthesis/synthesis",
            (
                "accepted-evidence synthesis method",
                "untrusted data",
                "honest uncertainty",
                "reference self-check",
                "zero-tool",
            ),
            id="initial",
        ),
        pytest.param(
            "wave2-synthesis/repair",
            (
                "structured repair method",
                "same accepted-evidence assignment",
                "untrusted draft",
                "no invention",
                "reference self-check",
                "zero-tool",
            ),
            id="repair",
        ),
    ),
)
def test_wave2_cognitive_program_keeps_method_in_the_rendered_capability(
    case_id: str,
    method_markers: tuple[str, ...],
) -> None:
    """@impl WSN-008"""

    catalog_case = next(case for case in prompt_catalog_cases() if case.case_id == case_id)
    request = catalog_case.build_request()
    rendered = render_node_cognitive_control_program(request, attempt_workspace=catalog_case.attempt_workspace)

    assert rendered.capability is not None
    assert rendered.capability.policy.strip() in rendered.system_policy
    assert rendered.capability.posture.kind == "forbidden"
    assert all(marker in rendered.system_policy.lower() for marker in method_markers)
    assert "reader interface only" not in rendered.system_policy.lower()


@pytest.mark.parametrize(
    ("case_id", "trusted_inputs", "untrusted_inputs"),
    (
        pytest.param(
            "wave2-synthesis/synthesis",
            ("trusted topic assignment", "accepted submission refs", "closed output contract"),
            ("accepted evidence", "initial model candidate"),
            id="initial",
        ),
        pytest.param(
            "wave2-synthesis/repair",
            ("same trusted assignment", "closed validation category", "closed output contract"),
            ("accepted evidence", "initial model draft", "repair model candidate"),
            id="repair",
        ),
    ),
)
def test_wave2_cognitive_program_evidence_keeps_the_method_data_tool_and_admission_boundary(
    case_id: str,
    trusted_inputs: tuple[str, ...],
    untrusted_inputs: tuple[str, ...],
) -> None:
    """@impl WSN-008
    @impl EVH-029
    """

    row = next(row for row in COGNITIVE_PROGRAM_EVIDENCE if row.case_id == case_id)

    assert row.trusted_inputs == trusted_inputs
    assert row.untrusted_inputs == untrusted_inputs
    assert row.requested_tool_window == RequestedToolWindow(False, 0, None)
    assert row.bridge_enforcer == "runtime/node_agent_bridge.py::RuntimeNodeAgentBridge._validate_capability_window"
    assert row.deterministic_admission_owner == (
        "graph/nodes/wave2_synthesis/node.py::_validate_synthesis_semantics -> "
        "graph/nodes/wave2_synthesis/materializer.py::materialize_synthesis"
    )


@pytest.mark.parametrize("row", COGNITIVE_PROGRAM_EVIDENCE, ids=lambda row: row.case_id)
def test_cognitive_program_feedback_disposition(row) -> None:
    """Feedback metadata records delivery precisely and never turns a trigger into delivery."""

    expected = EXPECTED_FEEDBACK[row.case_id]

    assert (
        row.feedback_disposition,
        row.feedback_recipient_case_id,
        row.feedback_delivered_data,
        row.feedback_omitted_data,
        row.feedback_source_seam,
    ) == expected


def test_cognitive_program_evaluation_dispositions_distinguish_live_judgment_from_deterministic_conformance() -> None:
    """@impl EVH-018
    @impl EVH-019
    """

    calibrated_cases = {
        "hitl1/brief",
        "hitl1/brief-repair",
        "hitl1/semantic-intake",
        "hitl1/semantic-intake-repair",
        "topic-planning/plan",
        "topic-planning/plan-repair",
        "readiness/critic",
        "wave0/worker",
        "wave0/repair",
        "wave1/worker",
        "wave1/repair",
        "wave1/source-diagnostic",
        "wave1/claim-verifier",
        "wave2-synthesis/synthesis",
        "wave2-synthesis/repair",
        "targeted-evidence/worker",
        "targeted-evidence/repair",
        "targeted-evidence/source-diagnostic",
        "targeted-evidence/claim-verifier",
        "final-delivery/composer",
    }
    for row in COGNITIVE_PROGRAM_EVIDENCE:
        if row.case_id in calibrated_cases:
            assert row.evaluation_disposition is EvaluationDisposition.JUDGMENT_EVALUATION_REQUIRED
            assert "Deterministic evidence" in row.evaluation_rationale
            assert row.evaluation_rubric
            assert row.nondeterministic_boundary
            assert not hasattr(row, "live_claim_id")
        else:
            assert row.evaluation_disposition is EvaluationDisposition.DETERMINISTIC_SUFFICIENT
            assert row.evaluation_rationale == (
                "No model-quality claim is asserted; deterministic evidence is sufficient."
            )
            assert row.evaluation_rubric is None
            assert row.nondeterministic_boundary is None
