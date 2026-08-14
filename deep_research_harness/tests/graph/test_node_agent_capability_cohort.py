"""Direct production-builder inventory for the node capability cohorts.

@impl NAC-003
@impl NAC-004
@impl NAC-005
@impl EVH-013
@impl NAC-006
@impl EVH-015
@impl NAC-007
@impl NPC-005
@impl EVH-016
@impl NAC-009
@impl CPE-003
@impl EVH-022
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from deerflow_deep_research.agents.capabilities import load_node_agent_capability
from deerflow_deep_research.agents.node_cognitive_control_program import render_node_cognitive_control_program
from deerflow_deep_research.graph.prompt_catalog import prompt_catalog_cases
from tests.assets.evidence import (
    EVIDENCE_CLAIMS,
    claim_index,
)
from tests.assets.node_agent_capabilities import (
    COGNITIVE_PROGRAM_EVIDENCE,
    COHORT_EVIDENCE,
    CognitiveProgramEvidenceLink,
    EvaluationDisposition,
    EvidenceClassification,
    EvidenceRole,
    validate_cognitive_program_evidence,
    validate_cohort_evidence,
)

EXPECTED = {
    "hitl1/brief": (
        "hitl1-profile-brief",
        "deerflow_deep_research.graph.nodes.hitl1",
        "capabilities/hitl1-profile-brief.md",
        "forbidden",
    ),
    "hitl1/brief-repair": (
        "hitl1-profile-brief-repair",
        "deerflow_deep_research.graph.nodes.hitl1",
        "capabilities/hitl1-profile-brief-repair.md",
        "forbidden",
    ),
    "hitl1/semantic-intake": (
        "hitl1-semantic-intake",
        "deerflow_deep_research.graph.nodes.hitl1",
        "capabilities/hitl1-semantic-intake.md",
        "forbidden",
    ),
    "hitl1/semantic-intake-repair": (
        "hitl1-semantic-intake-repair",
        "deerflow_deep_research.graph.nodes.hitl1",
        "capabilities/hitl1-semantic-intake-repair.md",
        "forbidden",
    ),
    "wave0/worker": (
        "wave0-authoritative-source-intake",
        "deerflow_deep_research.graph.nodes.wave0",
        "capabilities/wave0-authoritative-source-intake.md",
        "required",
    ),
    "wave0/repair": (
        "wave0-source-intake-repair",
        "deerflow_deep_research.graph.nodes.wave0",
        "capabilities/wave0-source-intake-repair.md",
        "forbidden",
    ),
    "topic-planning/plan": (
        "topic-planning-profile-decomposition",
        "deerflow_deep_research.graph.nodes.topic_planning",
        "capabilities/topic-planning-profile-decomposition.md",
        "forbidden",
    ),
    "topic-planning/plan-repair": (
        "topic-planning-plan-repair",
        "deerflow_deep_research.graph.nodes.topic_planning",
        "capabilities/topic-planning-plan-repair.md",
        "forbidden",
    ),
    "readiness/critic": (
        "readiness-evidence-critic",
        "deerflow_deep_research.graph.nodes.readiness",
        "capabilities/readiness-evidence-critic.md",
        "forbidden",
    ),
    "wave1/worker": (
        "wave1-evidence-extraction",
        "deerflow_deep_research.graph.nodes.wave1",
        "capabilities/wave1-evidence-extraction.md",
        "required",
    ),
    "wave1/repair": (
        "wave1-evidence-extraction-repair",
        "deerflow_deep_research.graph.nodes.wave1",
        "capabilities/wave1-evidence-extraction-repair.md",
        "forbidden",
    ),
    "wave1/source-diagnostic": (
        "wave1-source-diagnostic",
        "deerflow_deep_research.graph.nodes.wave1",
        "capabilities/wave1-source-diagnostic.md",
        "forbidden",
    ),
    "wave1/claim-verifier": (
        "wave1-claim-verifier",
        "deerflow_deep_research.graph.nodes.wave1",
        "capabilities/wave1-claim-verifier.md",
        "forbidden",
    ),
    "wave2-synthesis/synthesis": (
        "wave2-evidence-synthesis",
        "deerflow_deep_research.graph.nodes.wave2_synthesis",
        "capabilities/wave2-evidence-synthesis.md",
        "forbidden",
    ),
    "wave2-synthesis/repair": (
        "wave2-evidence-synthesis-repair",
        "deerflow_deep_research.graph.nodes.wave2_synthesis",
        "capabilities/wave2-evidence-synthesis-repair.md",
        "forbidden",
    ),
    "targeted-evidence/worker": (
        "targeted-gap-evidence-retrieval",
        "deerflow_deep_research.graph.nodes.targeted_evidence",
        "capabilities/targeted-gap-evidence-retrieval.md",
        "required",
    ),
    "targeted-evidence/repair": (
        "targeted-gap-evidence-repair",
        "deerflow_deep_research.graph.nodes.targeted_evidence",
        "capabilities/targeted-gap-evidence-repair.md",
        "forbidden",
    ),
    "targeted-evidence/source-diagnostic": (
        "targeted-source-diagnostic",
        "deerflow_deep_research.graph.nodes.targeted_evidence",
        "capabilities/targeted-source-diagnostic.md",
        "forbidden",
    ),
    "targeted-evidence/claim-verifier": (
        "targeted-claim-verifier",
        "deerflow_deep_research.graph.nodes.targeted_evidence",
        "capabilities/targeted-claim-verifier.md",
        "forbidden",
    ),
    "final-delivery/composer": (
        "final-delivery-composer",
        "deerflow_deep_research.graph.nodes.final_delivery",
        "capabilities/composer.md",
        "forbidden",
    ),
}
LEGACY: set[str] = set()


@pytest.mark.parametrize("case_id", sorted(EXPECTED))
def test_cohort_branch_binding(case_id: str) -> None:
    request = next(case.build_request() for case in prompt_catalog_cases() if case.case_id == case_id)
    capability_id, package, resource, posture = EXPECTED[case_id]
    assert request.capability_ref is not None
    assert request.capability_ref.capability_id == capability_id
    assert request.capability_ref.package == package
    assert request.capability_ref.resource == resource
    assert load_node_agent_capability(request.capability_ref).posture.kind == posture


@pytest.mark.parametrize("case_id", sorted(EXPECTED))
def test_cohort_branch_high_risk_tool_posture(case_id: str) -> None:
    request = next(case.build_request() for case in prompt_catalog_cases() if case.case_id == case_id)
    _capability_id, _package, _resource, posture = EXPECTED[case_id]
    if posture == "required":
        assert request.tools_enabled and request.minimum_tool_calls >= 1 and request.tool_call_limit is not None
    else:
        assert not request.tools_enabled
        assert request.minimum_tool_calls == 0 and request.tool_call_limit is None


def test_wave1_capability_declares_exact_runtime_policy_subset() -> None:
    request = next(case.build_request() for case in prompt_catalog_cases() if case.case_id == "wave1/worker")
    assert request.capability_ref is not None
    assert tuple(sorted(load_node_agent_capability(request.capability_ref).posture.allowed_tool_names)) == (
        "duckduckgo_search",
        "firecrawl_scrape",
        "jina_ai",
        "tavily_extract",
        "tavily_search",
        "web_fetch",
        "web_search",
    )


def test_targeted_worker_capability_declares_exact_runtime_policy_subset() -> None:
    request = next(
        case.build_request() for case in prompt_catalog_cases() if case.case_id == "targeted-evidence/worker"
    )
    assert request.capability_ref is not None
    assert tuple(sorted(load_node_agent_capability(request.capability_ref).posture.allowed_tool_names)) == (
        "duckduckgo_search",
        "firecrawl_scrape",
        "jina_ai",
        "tavily_extract",
        "tavily_search",
        "web_fetch",
        "web_search",
    )


@pytest.mark.parametrize(
    ("case_id", "method_markers"),
    [
        pytest.param(
            "wave0/worker",
            (
                "source-intake method",
                "untrusted data",
                "honest shortfall",
                "standalone json object",
                "final response self-check",
            ),
            id="wave0-initial",
        ),
        pytest.param(
            "wave0/repair",
            (
                "repair method",
                "untrusted draft",
                "no evidence invention",
                "standalone json object",
                "final response self-check",
            ),
            id="wave0-repair",
        ),
        pytest.param(
            "wave1/worker",
            (
                "evidence-extraction method",
                "wave0 baseline",
                "untrusted data",
                "standalone json object",
                "final response self-check",
            ),
            id="wave1-initial",
        ),
        pytest.param(
            "wave1/repair",
            (
                "evidence-extraction repair method",
                "untrusted draft",
                "no invention",
                "standalone json object",
                "final response self-check",
            ),
            id="wave1-repair",
        ),
        pytest.param(
            "topic-planning/plan",
            ("decomposition method", "scope_boundaries", "custom_notes", "current_round_direction", "self-check"),
            id="initial",
        ),
        pytest.param(
            "topic-planning/plan-repair",
            ("repair method", "same assignment", "validation feedback", "self-check"),
            id="repair",
        ),
    ],
)
def test_runtime_renderer_injects_the_exact_capability_method(
    case_id: str,
    method_markers: tuple[str, ...],
) -> None:
    """TOP-006/WAN-009/WON-010: renderer, not file presence, supplies the method."""
    catalog_case = next(case for case in prompt_catalog_cases() if case.case_id == case_id)
    request = catalog_case.build_request()
    rendered = render_node_cognitive_control_program(request, attempt_workspace=catalog_case.attempt_workspace)

    assert rendered.capability is not None
    assert rendered.capability.policy.strip() in rendered.system_policy
    assert request.objective in rendered.user_message
    assert request.expected_output in rendered.user_message
    if case_id in {"wave0/worker", "wave1/worker"}:
        assert request.minimum_tool_calls == 1
        assert rendered.capability.posture.kind == "required"
    else:
        assert request.tools_enabled is False
        assert rendered.capability.posture.kind == "forbidden"
    assert "# wave0 workflow" not in rendered.system_policy.lower()
    assert all(marker in rendered.system_policy.lower() for marker in method_markers)


@pytest.mark.parametrize(
    "case_id",
    ("hitl1/brief", "hitl1/brief-repair", "hitl1/semantic-intake", "hitl1/semantic-intake-repair"),
)
def test_hitl1_runtime_renderer_injects_the_exact_capability_method(case_id: str) -> None:
    """HIN-016: the runtime renderer, rather than resource presence, owns the method."""

    catalog_case = next(case for case in prompt_catalog_cases() if case.case_id == case_id)
    request = catalog_case.build_request()
    rendered = render_node_cognitive_control_program(request, attempt_workspace=catalog_case.attempt_workspace)

    assert rendered.capability is not None
    assert rendered.capability.policy.strip() in rendered.system_policy
    assert request.objective in rendered.user_message
    assert request.expected_output in rendered.user_message
    assert request.tools_enabled is False
    assert rendered.capability.posture.kind == "forbidden"
    assert "# hitl1" not in rendered.system_policy.lower()


@pytest.mark.parametrize("case_id", ("hitl1/brief", "hitl1/brief-repair"))
def test_hitl1_brief_method_stays_compatible_with_the_strict_output_contract(case_id: str) -> None:
    """HIN-016: preserve the BUG-023 parser/capability compatibility seam."""

    catalog_case = next(case for case in prompt_catalog_cases() if case.case_id == case_id)
    request = catalog_case.build_request()
    rendered = render_node_cognitive_control_program(request, attempt_workspace=catalog_case.attempt_workspace)

    assert rendered.capability is not None
    assert "output contract compatibility" in rendered.system_policy.lower()
    assert "brief_summary_language" not in rendered.system_policy
    assert "brief_summary_language" not in request.expected_output


def test_catalog_inventory_has_no_inferred_capability() -> None:
    cases = {case.case_id: case.build_request() for case in prompt_catalog_cases()}
    assert set(cases) == set(EXPECTED)
    assert all(request.capability_ref is not None for request in cases.values())


def test_cohort_evidence_matrix_has_two_collected_claims_per_branch() -> None:
    claims = claim_index(EVIDENCE_CLAIMS)
    validate_cohort_evidence(COHORT_EVIDENCE, claims, collected_selectors={claim.selector for claim in claims.values()})


def test_cognitive_program_evidence_matrix_closes_the_current_catalog() -> None:
    claims = claim_index(EVIDENCE_CLAIMS)
    validate_cognitive_program_evidence(
        COGNITIVE_PROGRAM_EVIDENCE,
        COHORT_EVIDENCE,
        claims,
        collected_selectors={claim.selector for claim in claims.values()},
    )


@pytest.mark.parametrize(
    ("rows", "claim_mutation", "message"),
    [
        pytest.param(COGNITIVE_PROGRAM_EVIDENCE[:-1], None, "final-delivery/composer", id="missing-row"),
        pytest.param(
            (
                COGNITIVE_PROGRAM_EVIDENCE[0],
                replace(COGNITIVE_PROGRAM_EVIDENCE[1], case_id=COGNITIVE_PROGRAM_EVIDENCE[0].case_id),
                *COGNITIVE_PROGRAM_EVIDENCE[2:],
            ),
            None,
            "hitl1/brief: duplicate ledger row",
            id="duplicate-case",
        ),
        pytest.param(
            (replace(COGNITIVE_PROGRAM_EVIDENCE[0], case_id="wave0/all"), *COGNITIVE_PROGRAM_EVIDENCE[1:]),
            None,
            "wave0/all: grouped or stale ledger row",
            id="grouped-row",
        ),
        pytest.param(
            (replace(COGNITIVE_PROGRAM_EVIDENCE[0], case_id="retired/worker"), *COGNITIVE_PROGRAM_EVIDENCE[1:]),
            None,
            "retired/worker: grouped or stale ledger row",
            id="stale-row",
        ),
        pytest.param(
            (
                replace(
                    COGNITIVE_PROGRAM_EVIDENCE[0],
                    evidence_links=(
                        replace(COGNITIVE_PROGRAM_EVIDENCE[0].evidence_links[0], claim_id="missing-cognitive-claim"),
                        *COGNITIVE_PROGRAM_EVIDENCE[0].evidence_links[1:],
                    ),
                ),
                *COGNITIVE_PROGRAM_EVIDENCE[1:],
            ),
            None,
            "hitl1/brief: unknown claim missing-cognitive-claim",
            id="unknown-claim",
        ),
        pytest.param(
            COGNITIVE_PROGRAM_EVIDENCE,
            "wrong-seam",
            "hitl1/brief: claim .* belongs to a different branch seam",
            id="wrong-seam",
        ),
        pytest.param(
            (
                replace(
                    COGNITIVE_PROGRAM_EVIDENCE[0],
                    evidence_links=(
                        CognitiveProgramEvidenceLink(
                            claim_id="nac-cohort-evidence-matrix",
                            role=EvidenceRole.COMPOSITION,
                            classification=EvidenceClassification.OBSOLETE_DUPLICATE,
                        ),
                        *COGNITIVE_PROGRAM_EVIDENCE[0].evidence_links[1:],
                    ),
                ),
                *COGNITIVE_PROGRAM_EVIDENCE[1:],
            ),
            "aggregate-substitute",
            "hitl1/brief: obsolete duplicate cannot close composition",
            id="aggregate-substituted",
        ),
        pytest.param(
            (
                replace(
                    COGNITIVE_PROGRAM_EVIDENCE[0],
                    evidence_links=tuple(
                        link
                        for link in COGNITIVE_PROGRAM_EVIDENCE[0].evidence_links
                        if link.role is not EvidenceRole.FEEDBACK_DISPOSITION
                    ),
                ),
                *COGNITIVE_PROGRAM_EVIDENCE[1:],
            ),
            None,
            "hitl1/brief: missing feedback-disposition evidence role",
            id="incomplete-roles",
        ),
        pytest.param(
            (
                replace(
                    COGNITIVE_PROGRAM_EVIDENCE[0],
                    evaluation_disposition=EvaluationDisposition.DETERMINISTIC_SUFFICIENT,
                    evaluation_rationale="No model-quality claim is asserted; deterministic evidence is sufficient.",
                    evaluation_rubric=None,
                    nondeterministic_boundary=None,
                ),
                *COGNITIVE_PROGRAM_EVIDENCE[1:],
            ),
            None,
            "hitl1/brief: judgment evaluation cannot be closed by deterministic evidence",
            id="deterministic-quality-substitute",
        ),
    ],
)
def test_cognitive_program_evidence_rejects_invalid_rows(rows, claim_mutation: str | None, message: str) -> None:
    claims = claim_index(EVIDENCE_CLAIMS)
    if claim_mutation == "wrong-seam":
        first_link = COGNITIVE_PROGRAM_EVIDENCE[0].evidence_links[0]
        claims[first_link.claim_id] = replace(
            claims[first_link.claim_id],
            selector=(
                "tests/graph/test_cognitive_program_evidence.py::test_cognitive_program_composition[wave0/worker]"
            ),
        )
    with pytest.raises(ValueError, match=message):
        validate_cognitive_program_evidence(
            rows,
            COHORT_EVIDENCE,
            claims,
            collected_selectors={claim.selector for claim in claims.values()},
        )


@pytest.mark.parametrize(
    ("rows", "claims", "collected_selectors", "message"),
    [
        pytest.param(COHORT_EVIDENCE[:-1], None, None, "twenty unique direct cases", id="missing-row"),
        pytest.param(
            (COHORT_EVIDENCE[0], replace(COHORT_EVIDENCE[1], case_id=COHORT_EVIDENCE[0].case_id), *COHORT_EVIDENCE[2:]),
            None,
            None,
            "twenty unique direct cases",
            id="duplicate-case",
        ),
        pytest.param(
            (replace(COHORT_EVIDENCE[0], success_claim_id="missing-claim"), *COHORT_EVIDENCE[1:]),
            None,
            None,
            "unknown claim",
            id="unknown-claim",
        ),
        pytest.param(
            (replace(COHORT_EVIDENCE[0], capability_id="unknown-capability"), *COHORT_EVIDENCE[1:]),
            None,
            None,
            "unknown or missing capability binding",
            id="unknown-capability",
        ),
        pytest.param(
            (replace(COHORT_EVIDENCE[0], risk_claim_id=COHORT_EVIDENCE[0].success_claim_id), *COHORT_EVIDENCE[1:]),
            None,
            None,
            "claim ids must differ",
            id="identical-claims",
        ),
        pytest.param(COHORT_EVIDENCE, None, set(), "uncollected claim", id="uncollected-claim"),
        pytest.param(
            COHORT_EVIDENCE,
            "wrong-branch",
            None,
            "different branch seam",
            id="wrong-branch-claim",
        ),
        pytest.param(
            COHORT_EVIDENCE,
            "aggregate-substitute",
            None,
            "different branch seam",
            id="aggregate-substitute",
        ),
    ],
)
def test_cohort_evidence_matrix_rejects_invalid_rows(
    rows,
    claims,
    collected_selectors,
    message: str,
) -> None:
    indexed = claim_index(EVIDENCE_CLAIMS)
    if claims == "wrong-branch":
        indexed[COHORT_EVIDENCE[0].success_claim_id] = replace(
            indexed[COHORT_EVIDENCE[0].success_claim_id],
            selector="tests/graph/test_wave0_worker.py::test_build_wave0_worker_prompt_carries_topic_constraints",
        )
    if claims == "aggregate-substitute":
        indexed[COHORT_EVIDENCE[0].success_claim_id] = replace(
            indexed[COHORT_EVIDENCE[0].success_claim_id],
            selector="tests/graph/test_node_agent_capability_cohort.py::test_cohort_branch_binding[hitl1/semantic-intake]",
        )
    if collected_selectors is None:
        collected_selectors = {claim.selector for claim in indexed.values()}

    with pytest.raises(ValueError, match=message):
        validate_cohort_evidence(rows, indexed, collected_selectors=collected_selectors)
