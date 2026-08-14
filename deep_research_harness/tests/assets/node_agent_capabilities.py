"""Closed direct-branch denominator for node-agent capability evidence.

@impl NAC-004
@impl EVH-012
@impl NAC-005
@impl EVH-013
@impl NAC-006
@impl EVH-015
@impl NAC-009
@impl CPE-003
@impl EVH-022
"""
# ruff: noqa: E501

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from tests.assets.evidence import AuthenticityLevel, TestEvidenceClaim


@dataclass(frozen=True)
class CapabilityEvidenceRow:
    case_id: str
    capability_id: str
    catalog_source: str
    declaration_source: str
    entrypoint: str
    test_modules: tuple[str, ...]
    success_claim_id: str
    risk_claim_id: str


class FeedbackDisposition(StrEnum):
    """How a bounded branch datum reaches a later model request, if at all."""

    DELIVERED = "delivered"
    PARTIAL = "partial"
    ABSENT = "absent"


class EvidenceClassification(StrEnum):
    """Review classification for one branch-local central evidence claim."""

    COGNITIVE_PROGRAM = "cognitive-program"
    HUMAN_DECISION = "human-decision"
    DETERMINISTIC_GUARDRAIL = "deterministic-guardrail"
    WIRING = "wiring"
    OBSOLETE_DUPLICATE = "obsolete-duplicate"


class EvidenceRole(StrEnum):
    """The three independent deterministic proof obligations per branch."""

    COMPOSITION = "composition"
    FEEDBACK_DISPOSITION = "feedback-disposition"
    GUARDRAIL_ADMISSION = "guardrail-admission"


class EvaluationDisposition(StrEnum):
    """Whether a branch row makes a judgment-dependent model-quality claim."""

    DETERMINISTIC_SUFFICIENT = "deterministic-sufficient"
    JUDGMENT_EVALUATION_REQUIRED = "judgment-evaluation-required"


@dataclass(frozen=True)
class RequestedToolWindow:
    """The tool window requested by one synthetic catalog case."""

    tools_enabled: bool
    minimum_tool_calls: int
    tool_call_limit: int | None


@dataclass(frozen=True)
class CognitiveProgramEvidenceLink:
    """One classified central claim attached to a branch-local proof role."""

    claim_id: str
    role: EvidenceRole
    classification: EvidenceClassification


@dataclass(frozen=True)
class CognitiveProgramEvidenceRow:
    """Test-owned review projection for one current direct model branch."""

    case_id: str
    product_responsibility: str
    bounded_question: str
    trusted_inputs: tuple[str, ...]
    untrusted_inputs: tuple[str, ...]
    capability_id: str
    catalog_builder_id: str
    final_render_seam: str
    requested_tool_window: RequestedToolWindow
    bridge_enforcer: str
    feedback_disposition: FeedbackDisposition
    feedback_recipient_case_id: str | None
    feedback_delivered_data: tuple[str, ...]
    feedback_omitted_data: tuple[str, ...]
    feedback_source_seam: str
    candidate_shape: str
    deterministic_admission_owner: str
    guardrail_claim_id: str
    evidence_links: tuple[CognitiveProgramEvidenceLink, ...]
    evaluation_disposition: EvaluationDisposition
    evaluation_rationale: str
    evaluation_rubric: str | None = None
    nondeterministic_boundary: str | None = None


COHORT_EVIDENCE = (
    CapabilityEvidenceRow(
        "hitl1/brief",
        "hitl1-profile-brief",
        "graph/nodes/hitl1/prompts.py",
        "graph/nodes/hitl1/capabilities.py",
        "graph/nodes/hitl1/node.py:build_real",
        ("tests/graph/test_hitl1_node.py",),
        "nac-hitl-brief-success",
        "nac-hitl-brief-risk",
    ),
    CapabilityEvidenceRow(
        "hitl1/brief-repair",
        "hitl1-profile-brief-repair",
        "graph/nodes/hitl1/prompts.py",
        "graph/nodes/hitl1/capabilities.py",
        "graph/nodes/hitl1/node.py:build_real",
        ("tests/graph/test_hitl1_node.py",),
        "nac-hitl-brief-repair-success",
        "nac-hitl-brief-repair-risk",
    ),
    CapabilityEvidenceRow(
        "hitl1/semantic-intake",
        "hitl1-semantic-intake",
        "graph/nodes/hitl1/prompts.py",
        "graph/nodes/hitl1/capabilities.py",
        "graph/nodes/hitl1/node.py:build_real",
        ("tests/graph/test_hitl1_node.py",),
        "nac-hitl-success",
        "nac-hitl-risk",
    ),
    CapabilityEvidenceRow(
        "hitl1/semantic-intake-repair",
        "hitl1-semantic-intake-repair",
        "graph/nodes/hitl1/prompts.py",
        "graph/nodes/hitl1/capabilities.py",
        "graph/nodes/hitl1/node.py:build_real",
        ("tests/graph/test_hitl1_node.py",),
        "nac-hitl-repair-success",
        "nac-hitl-repair-risk",
    ),
    CapabilityEvidenceRow(
        "wave0/worker",
        "wave0-authoritative-source-intake",
        "graph/nodes/wave0/prompts.py",
        "graph/nodes/wave0/capabilities.py",
        "graph/nodes/wave0/subgraph.py:run_wave0_work_units_real",
        ("tests/integration/test_wave0_work_units.py", "tests/unit/test_node_agent_bridge.py"),
        "nac-wave0-success",
        "nac-runtime-tool-admission",
    ),
    CapabilityEvidenceRow(
        "wave0/repair",
        "wave0-source-intake-repair",
        "graph/nodes/wave0/prompts.py",
        "graph/nodes/wave0/capabilities.py",
        "graph/nodes/wave0/subgraph.py:run_wave0_work_units_real",
        ("tests/integration/test_wave0_work_units.py",),
        "nac-wave0-repair-success",
        "nac-wave0-repair-risk",
    ),
    CapabilityEvidenceRow(
        "topic-planning/plan",
        "topic-planning-profile-decomposition",
        "graph/nodes/topic_planning/prompts.py",
        "graph/nodes/topic_planning/capabilities.py",
        "graph/nodes/topic_planning/node.py:build_real",
        ("tests/graph/test_topic_planning_node.py",),
        "topic-planning-valid-plan",
        "topic-planning-invalid-output",
    ),
    CapabilityEvidenceRow(
        "topic-planning/plan-repair",
        "topic-planning-plan-repair",
        "graph/nodes/topic_planning/prompts.py",
        "graph/nodes/topic_planning/capabilities.py",
        "graph/nodes/topic_planning/node.py:build_real",
        ("tests/graph/test_topic_planning_node.py",),
        "nac-topic-planning-repair-success",
        "nac-topic-planning-repair-risk",
    ),
    CapabilityEvidenceRow(
        "readiness/critic",
        "readiness-evidence-critic",
        "graph/nodes/readiness/critic.py",
        "graph/nodes/readiness/capabilities.py",
        "graph/nodes/readiness/node.py:build_real",
        ("tests/unit/test_readiness_real.py", "tests/integration/test_zero_tool_node_conformance.py"),
        "workflow-readiness-evidence-critic-bridge",
        "readiness-critic-conservative-failure",
    ),
    CapabilityEvidenceRow(
        "wave1/worker",
        "wave1-evidence-extraction",
        "graph/nodes/wave1/prompts.py",
        "graph/nodes/wave1/capabilities.py",
        "graph/nodes/wave1/subgraph.py:run_wave1_work_units_real",
        ("tests/integration/test_wave1_work_units.py",),
        "wave1-worker-ledger-success",
        "nac-wave1-risk",
    ),
    CapabilityEvidenceRow(
        "wave1/repair",
        "wave1-evidence-extraction-repair",
        "graph/nodes/wave1/prompts.py",
        "graph/nodes/wave1/capabilities.py",
        "graph/nodes/wave1/subgraph.py:run_wave1_work_units_real",
        ("tests/integration/test_wave1_work_units.py",),
        "nac-wave1-repair-success",
        "nac-wave1-repair-risk",
    ),
    CapabilityEvidenceRow(
        "wave1/source-diagnostic",
        "wave1-source-diagnostic",
        "graph/nodes/wave1/prompts.py",
        "graph/nodes/wave1/capabilities.py",
        "graph/nodes/wave1/review.py:build_wave1_gate_review",
        ("tests/integration/test_wave1_work_units.py",),
        "nac-wave1-source-diagnostic-success",
        "nac-wave1-source-diagnostic-risk",
    ),
    CapabilityEvidenceRow(
        "wave1/claim-verifier",
        "wave1-claim-verifier",
        "graph/nodes/wave1/prompts.py",
        "graph/nodes/wave1/capabilities.py",
        "graph/nodes/wave1/review.py:build_wave1_gate_review",
        ("tests/integration/test_wave1_work_units.py",),
        "nac-wave1-claim-verifier-success",
        "nac-wave1-claim-verifier-risk",
    ),
    CapabilityEvidenceRow(
        "wave2-synthesis/synthesis",
        "wave2-evidence-synthesis",
        "graph/nodes/wave2_synthesis/prompts.py",
        "graph/nodes/wave2_synthesis/capabilities.py",
        "graph/nodes/wave2_synthesis/node.py:build_real",
        ("tests/graph/test_wave2_synthesis_real.py",),
        "wave2-canonical-findings",
        "wave2-malformed-output",
    ),
    CapabilityEvidenceRow(
        "wave2-synthesis/repair",
        "wave2-evidence-synthesis-repair",
        "graph/nodes/wave2_synthesis/prompts.py",
        "graph/nodes/wave2_synthesis/capabilities.py",
        "graph/nodes/wave2_synthesis/node.py:build_real",
        ("tests/graph/test_wave2_synthesis_real.py",),
        "nac-wave2-repair-success",
        "nac-wave2-repair-risk",
    ),
    CapabilityEvidenceRow(
        "targeted-evidence/worker",
        "targeted-gap-evidence-retrieval",
        "graph/nodes/targeted_evidence/prompts.py",
        "graph/nodes/targeted_evidence/capabilities.py",
        "graph/nodes/targeted_evidence/subgraph.py:run_gap_workers",
        ("tests/graph/test_targeted_evidence_real.py",),
        "nac-targeted-worker-success",
        "workflow-outcome-targeted-evidence-known-invocation",
    ),
    CapabilityEvidenceRow(
        "targeted-evidence/repair",
        "targeted-gap-evidence-repair",
        "graph/nodes/targeted_evidence/prompts.py",
        "graph/nodes/targeted_evidence/capabilities.py",
        "graph/nodes/targeted_evidence/subgraph.py:run_gap_workers",
        ("tests/graph/test_targeted_evidence_real.py",),
        "nac-targeted-repair-success",
        "nac-targeted-repair-risk",
    ),
    CapabilityEvidenceRow(
        "targeted-evidence/source-diagnostic",
        "targeted-source-diagnostic",
        "graph/nodes/targeted_evidence/prompts.py",
        "graph/nodes/targeted_evidence/capabilities.py",
        "graph/nodes/targeted_evidence/node.py:build_real",
        ("tests/graph/test_targeted_evidence_real.py",),
        "targeted-evidence-valid-artifact",
        "targeted-evidence-malformed-output",
    ),
    CapabilityEvidenceRow(
        "targeted-evidence/claim-verifier",
        "targeted-claim-verifier",
        "graph/nodes/targeted_evidence/prompts.py",
        "graph/nodes/targeted_evidence/capabilities.py",
        "graph/nodes/targeted_evidence/node.py:build_real",
        ("tests/graph/test_targeted_evidence_real.py",),
        "nac-targeted-claim-verifier-success",
        "nac-targeted-claim-verifier-risk",
    ),
    CapabilityEvidenceRow(
        "final-delivery/composer",
        "final-delivery-composer",
        "graph/nodes/final_delivery/composer.py",
        "graph/nodes/final_delivery/capabilities.py",
        "graph/nodes/final_delivery/node.py:build_real",
        ("tests/integration/test_zero_tool_node_conformance.py",),
        "nac-final-delivery-composer-success",
        "nac-final-delivery-composer-risk",
    ),
)

EXPECTED_COHORT_BINDINGS = {
    "hitl1/brief": "hitl1-profile-brief",
    "hitl1/brief-repair": "hitl1-profile-brief-repair",
    "hitl1/semantic-intake": "hitl1-semantic-intake",
    "hitl1/semantic-intake-repair": "hitl1-semantic-intake-repair",
    "wave0/worker": "wave0-authoritative-source-intake",
    "wave0/repair": "wave0-source-intake-repair",
    "topic-planning/plan": "topic-planning-profile-decomposition",
    "topic-planning/plan-repair": "topic-planning-plan-repair",
    "readiness/critic": "readiness-evidence-critic",
    "wave1/worker": "wave1-evidence-extraction",
    "wave1/repair": "wave1-evidence-extraction-repair",
    "wave1/source-diagnostic": "wave1-source-diagnostic",
    "wave1/claim-verifier": "wave1-claim-verifier",
    "wave2-synthesis/synthesis": "wave2-evidence-synthesis",
    "wave2-synthesis/repair": "wave2-evidence-synthesis-repair",
    "targeted-evidence/worker": "targeted-gap-evidence-retrieval",
    "targeted-evidence/repair": "targeted-gap-evidence-repair",
    "targeted-evidence/source-diagnostic": "targeted-source-diagnostic",
    "targeted-evidence/claim-verifier": "targeted-claim-verifier",
    "final-delivery/composer": "final-delivery-composer",
}


_NO_TOOLS = RequestedToolWindow(tools_enabled=False, minimum_tool_calls=0, tool_call_limit=None)
_WAVE0_TOOLS = RequestedToolWindow(tools_enabled=True, minimum_tool_calls=1, tool_call_limit=3)
_ONE_RETRIEVAL = RequestedToolWindow(tools_enabled=True, minimum_tool_calls=1, tool_call_limit=1)
_FINAL_RENDER_SEAM = "agents/node_cognitive_control_program.py::render_node_cognitive_control_program"
_BRIDGE_ENFORCER = "runtime/node_agent_bridge.py::RuntimeNodeAgentBridge._validate_capability_window"
_DETERMINISTIC_EVALUATION_RATIONALE = "No model-quality claim is asserted; deterministic evidence is sufficient."
_JUDGMENT_EVALUATIONS = {
    "hitl1/brief": (
        "Deterministic evidence proves composition and non-admission, not whether a model makes "
        "a conservative, usable profile proposal.",
        "Evaluate advisory scope, bounded profile fidelity, and decision-ready must-answer questions.",
    ),
    "hitl1/brief-repair": (
        "Deterministic evidence proves repair containment and non-admission, not whether a model "
        "repairs without broadening the intake assignment.",
        "Evaluate same-assignment repair, closed candidate shape, and absence of invented "
        "requirements or lifecycle authority.",
    ),
    "hitl1/semantic-intake": (
        "Deterministic evidence proves parser and resolver boundaries, not whether a model "
        "faithfully distinguishes a human reply's intent.",
        "Evaluate explicit confirmation, complete constrained revision, proposal-question "
        "handling, and clarification for ambiguity.",
    ),
    "hitl1/semantic-intake-repair": (
        "Deterministic evidence proves repair bounds and resolver authority, not whether a model "
        "preserves ambiguity while repairing a semantic candidate.",
        "Evaluate same-context repair, legal single intent, ambiguity preservation, and absence "
        "of action or route authority.",
    ),
    "topic-planning/plan": (
        "Deterministic evidence proves materialization and non-publication boundaries, not whether "
        "a model creates a useful profile-faithful decomposition.",
        "Evaluate confirmed-profile fidelity, explicit must-answer coverage, distinct scopes, "
        "and conservative degraded-profile handling.",
    ),
    "topic-planning/plan-repair": (
        "Deterministic evidence proves one-repair exhaustion and materializer authority, not "
        "whether a model repairs a plan without broadening it.",
        "Evaluate same-profile repair, validation-fact response, complete coverage, and absence "
        "of sources, identifiers, state, or route authority.",
    ),
    "readiness/critic": (
        "Deterministic evidence proves the ledger projection, capability posture, and admission boundary, not whether "
        "a model correctly distinguishes supported answers from honest insufficiency or targeted repair needs.",
        "Evaluate exact question coverage, evidence-grounded ready and insufficient verdicts, conservative repair "
        "classification, and the absence of route or ledger authority.",
    ),
    "wave0/worker": (
        "Deterministic evidence proves request containment and controller admission, not whether a model "
        "selects assignment-relevant independent source metadata.",
        "Evaluate assignment relevance, independent source proposals, untrusted retrieval handling, "
        "and honest degradation.",
    ),
    "wave0/repair": (
        "Deterministic evidence proves parser-only repair containment and non-admission, not whether a model "
        "repairs a source candidate without invention.",
        "Evaluate same-assignment repair, non-invention from untrusted observations, and absence "
        "of lifecycle authority.",
    ),
    "wave1/worker": (
        "Deterministic evidence proves baseline and provenance validation, not whether a model makes useful "
        "bounded new-evidence judgments.",
        "Evaluate baseline exclusion, new-source provenance, counterevidence, and honest open-question uncertainty.",
    ),
    "wave1/repair": (
        "Deterministic evidence proves local-semantic repair containment and non-admission, not whether a model "
        "repairs evidence without broadening it.",
        "Evaluate same-assignment repair, baseline non-promotion, non-broadening, and absence of lifecycle authority.",
    ),
    "wave1/source-diagnostic": (
        "Deterministic evidence proves review binding and materializer authority, not whether a model makes a "
        "decision-ready assignment-bound source classification.",
        "Evaluate exact assigned-source scope, uncertainty-aware classification, and review-only limits.",
    ),
    "wave1/claim-verifier": (
        "Deterministic evidence proves review binding and gate ownership, not whether a model makes a useful "
        "bounded claim-support judgment.",
        "Evaluate exact claim and source-reference scope, uncertainty, and review-only limits.",
    ),
    "wave2-synthesis/synthesis": (
        "Deterministic evidence proves accepted-evidence composition and non-admission, not whether a model makes a conservative synthesis judgment.",
        "Evaluate evidence-grounded findings and relations, honest gaps, uncertainty, and absence of projection authority.",
    ),
    "wave2-synthesis/repair": (
        "Deterministic evidence proves repair containment and non-publication, not whether a model repairs a synthesis without inventing support.",
        "Evaluate same-assignment repair, closed validation feedback, honest gaps, and absence of routing authority.",
    ),
    "targeted-evidence/worker": (
        "Deterministic evidence proves one-gap retrieval posture and controller admission, not whether a model makes a useful provenance-bound evidence judgment.",
        "Evaluate same-gap retrieval, observed provenance, uncertainty, honest non-resolution, and no lifecycle authority.",
    ),
    "targeted-evidence/repair": (
        "Deterministic evidence proves same-gap repair containment and non-admission, not whether a model repairs without adding evidence.",
        "Evaluate same-gap repair, retained provenance, honest limitation, and absence of ledger or route authority.",
    ),
    "targeted-evidence/source-diagnostic": (
        "Deterministic evidence proves assigned-reference validation and materializer ownership, not whether a model makes a conservative source diagnostic.",
        "Evaluate assigned-reference scope, uncertainty, provenance-bound classification, and review-only limits.",
    ),
    "targeted-evidence/claim-verifier": (
        "Deterministic evidence proves reference containment and materializer ownership, not whether a model makes a useful bounded claim judgment.",
        "Evaluate assigned-reference scope, support or counterevidence, uncertainty, and review-only limits.",
    ),
    "final-delivery/composer": (
        "Deterministic evidence proves request, parser, renderer, publisher, and gate containment, not whether a model chooses a useful report layout.",
        "Evaluate complete approved-entry ordering, conclusion and uncertainty presentation, and exact citation-binding preservation.",
    ),
}
_JUDGMENT_BOUNDARY = (
    "A live result evaluates only an untrusted candidate; deterministic parser, validator, materializer, "
    "controller, ledger, gate, checkpoint, and route owners retain authority."
)


def _cognitive_links(case_id: str) -> tuple[CognitiveProgramEvidenceLink, ...]:
    claim_suffix = case_id.replace("/", "-")
    return (
        CognitiveProgramEvidenceLink(
            claim_id=f"cpe-composition-{claim_suffix}",
            role=EvidenceRole.COMPOSITION,
            classification=EvidenceClassification.COGNITIVE_PROGRAM,
        ),
        CognitiveProgramEvidenceLink(
            claim_id=f"cpe-feedback-{claim_suffix}",
            role=EvidenceRole.FEEDBACK_DISPOSITION,
            classification=EvidenceClassification.WIRING,
        ),
        CognitiveProgramEvidenceLink(
            claim_id=f"cpe-guardrail-{claim_suffix}",
            role=EvidenceRole.GUARDRAIL_ADMISSION,
            classification=EvidenceClassification.DETERMINISTIC_GUARDRAIL,
        ),
        CognitiveProgramEvidenceLink(
            claim_id="nac-cohort-evidence-matrix",
            role=EvidenceRole.COMPOSITION,
            classification=EvidenceClassification.OBSOLETE_DUPLICATE,
        ),
    )


def _cognitive_row(
    case_id: str,
    *,
    product_responsibility: str,
    bounded_question: str,
    trusted_inputs: tuple[str, ...],
    untrusted_inputs: tuple[str, ...],
    capability_id: str,
    catalog_builder_id: str,
    requested_tool_window: RequestedToolWindow,
    feedback_disposition: FeedbackDisposition,
    feedback_source_seam: str,
    candidate_shape: str,
    deterministic_admission_owner: str,
    feedback_recipient_case_id: str | None = None,
    feedback_delivered_data: tuple[str, ...] = (),
    feedback_omitted_data: tuple[str, ...] = (),
) -> CognitiveProgramEvidenceRow:
    links = _cognitive_links(case_id)
    guardrail_claim_id = next(link.claim_id for link in links if link.role is EvidenceRole.GUARDRAIL_ADMISSION)
    judgment_evaluation = _JUDGMENT_EVALUATIONS.get(case_id)
    return CognitiveProgramEvidenceRow(
        case_id=case_id,
        product_responsibility=product_responsibility,
        bounded_question=bounded_question,
        trusted_inputs=trusted_inputs,
        untrusted_inputs=untrusted_inputs,
        capability_id=capability_id,
        catalog_builder_id=catalog_builder_id,
        final_render_seam=_FINAL_RENDER_SEAM,
        requested_tool_window=requested_tool_window,
        bridge_enforcer=_BRIDGE_ENFORCER,
        feedback_disposition=feedback_disposition,
        feedback_recipient_case_id=feedback_recipient_case_id,
        feedback_delivered_data=feedback_delivered_data,
        feedback_omitted_data=feedback_omitted_data,
        feedback_source_seam=feedback_source_seam,
        candidate_shape=candidate_shape,
        deterministic_admission_owner=deterministic_admission_owner,
        guardrail_claim_id=guardrail_claim_id,
        evidence_links=links,
        evaluation_disposition=(
            EvaluationDisposition.JUDGMENT_EVALUATION_REQUIRED
            if judgment_evaluation is not None
            else EvaluationDisposition.DETERMINISTIC_SUFFICIENT
        ),
        evaluation_rationale=(
            judgment_evaluation[0] if judgment_evaluation is not None else _DETERMINISTIC_EVALUATION_RATIONALE
        ),
        evaluation_rubric=judgment_evaluation[1] if judgment_evaluation is not None else None,
        nondeterministic_boundary=_JUDGMENT_BOUNDARY if judgment_evaluation is not None else None,
    )


COGNITIVE_PROGRAM_EVIDENCE = (
    _cognitive_row(
        "hitl1/brief",
        product_responsibility="Advisory profile-brief proposal",
        bounded_question="Produce one structured brief for the original research question.",
        trusted_inputs=("original_question",),
        untrusted_inputs=("model_summary",),
        capability_id="hitl1-profile-brief",
        catalog_builder_id="graph/nodes/hitl1/prompts.py::build_brief_prompt",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.DELIVERED,
        feedback_recipient_case_id="hitl1/brief-repair",
        feedback_delivered_data=("structured_output_invalid",),
        feedback_source_seam="graph/nodes/hitl1/node.py::_generate_brief",
        candidate_shape="StructuredBrief",
        deterministic_admission_owner="graph/nodes/hitl1/node.py::parse_brief_output",
    ),
    _cognitive_row(
        "hitl1/brief-repair",
        product_responsibility="Repair one advisory profile-brief proposal",
        bounded_question="Repair only the malformed structured brief for the original question.",
        trusted_inputs=("original_question", "structured_output_invalid"),
        untrusted_inputs=("initial_model_summary", "repair_model_summary"),
        capability_id="hitl1-profile-brief-repair",
        catalog_builder_id="graph/nodes/hitl1/prompts.py::build_brief_prompt",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.ABSENT,
        feedback_source_seam="graph/nodes/hitl1/node.py::_generate_brief",
        candidate_shape="StructuredBrief",
        deterministic_admission_owner="graph/nodes/hitl1/node.py::parse_brief_output",
    ),
    _cognitive_row(
        "hitl1/semantic-intake",
        product_responsibility="Interpret one reply against the current proposal",
        bounded_question="Return one bounded semantic intent for the supplied reply and proposal.",
        trusted_inputs=("original_question", "interaction_subject"),
        untrusted_inputs=("human_reply", "model_summary"),
        capability_id="hitl1-semantic-intake",
        catalog_builder_id="graph/nodes/hitl1/prompts.py::build_semantic_intake_prompt",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.DELIVERED,
        feedback_recipient_case_id="hitl1/semantic-intake-repair",
        feedback_delivered_data=("semantic_candidate_invalid",),
        feedback_source_seam="graph/nodes/hitl1/node.py::_classify_proposal_reply",
        candidate_shape="SemanticCandidate",
        deterministic_admission_owner="graph/nodes/hitl1/node.py::resolve_semantic_candidate",
    ),
    _cognitive_row(
        "hitl1/semantic-intake-repair",
        product_responsibility="Repair one malformed semantic intent",
        bounded_question="Repair the semantic candidate using the same reply and proposal.",
        trusted_inputs=("original_question", "interaction_subject", "semantic_candidate_invalid"),
        untrusted_inputs=("human_reply", "initial_model_summary", "repair_model_summary"),
        capability_id="hitl1-semantic-intake-repair",
        catalog_builder_id="graph/nodes/hitl1/prompts.py::build_semantic_intake_prompt",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.ABSENT,
        feedback_source_seam="graph/nodes/hitl1/node.py::_classify_proposal_reply",
        candidate_shape="SemanticCandidate",
        deterministic_admission_owner="graph/nodes/hitl1/node.py::resolve_semantic_candidate",
    ),
    _cognitive_row(
        "topic-planning/plan",
        product_responsibility="Confirmed-profile topic-plan proposal",
        bounded_question="Decompose the confirmed profile into a bounded TopicPlan.",
        trusted_inputs=("planner_inputs", "confirmed_profile"),
        untrusted_inputs=("model_summary",),
        capability_id="topic-planning-profile-decomposition",
        catalog_builder_id="graph/nodes/topic_planning/prompts.py::build_planner_prompt",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.DELIVERED,
        feedback_recipient_case_id="topic-planning/plan-repair",
        feedback_delivered_data=("repair_error",),
        feedback_source_seam="graph/nodes/topic_planning/node.py::_generate_plan",
        candidate_shape="TopicPlan",
        deterministic_admission_owner="domain/topics.py::materialize_topic_plan",
    ),
    _cognitive_row(
        "topic-planning/plan-repair",
        product_responsibility="Repair one bounded TopicPlan",
        bounded_question="Repair the invalid plan against the same profile and validation facts.",
        trusted_inputs=("planner_inputs", "repair_error"),
        untrusted_inputs=("initial_model_summary", "repair_model_summary"),
        capability_id="topic-planning-plan-repair",
        catalog_builder_id="graph/nodes/topic_planning/prompts.py::build_planner_prompt",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.ABSENT,
        feedback_source_seam="graph/nodes/topic_planning/node.py::_generate_plan",
        candidate_shape="TopicPlan",
        deterministic_admission_owner="domain/topics.py::materialize_topic_plan",
    ),
    _cognitive_row(
        "readiness/critic",
        product_responsibility="Per-question accepted-evidence answerability candidate",
        bounded_question="Classify each supplied must-answer question using only the admitted evidence projection.",
        trusted_inputs=("must_answer_questions", "accepted_submission_refs"),
        untrusted_inputs=("accepted_evidence_content", "model_summary"),
        capability_id="readiness-evidence-critic",
        catalog_builder_id="graph/nodes/readiness/critic.py::build_readiness_critic_request",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.ABSENT,
        feedback_source_seam="graph/nodes/readiness/node.py::build_real",
        candidate_shape="ReadinessCriticOutput",
        deterministic_admission_owner="graph/nodes/readiness/critic.py::admit_readiness_candidate",
    ),
    _cognitive_row(
        "wave0/worker",
        product_responsibility="Authoritative source-intake candidate",
        bounded_question="Retrieve and propose bounded source metadata for one assigned topic.",
        trusted_inputs=("topic_assignment_projection",),
        untrusted_inputs=("tool_results", "model_summary"),
        capability_id="wave0-authoritative-source-intake",
        catalog_builder_id="graph/nodes/wave0/prompts.py::build_wave0_worker_prompt",
        requested_tool_window=_WAVE0_TOOLS,
        feedback_disposition=FeedbackDisposition.PARTIAL,
        feedback_recipient_case_id="wave0/repair",
        feedback_delivered_data=(
            "assignment_projection",
            "initial_structured_output_invalid",
            "draft",
            "untrusted_tool_results",
        ),
        feedback_omitted_data=("raw_parse_error", "submission_validation_codes", "artifact_validation_detail"),
        feedback_source_seam="graph/nodes/wave0/subgraph.py::run_wave0_work_units_real",
        candidate_shape="CandidateResult",
        deterministic_admission_owner="graph/components/work_units.py::run_fixture_work_unit_component",
    ),
    _cognitive_row(
        "wave0/repair",
        product_responsibility="Repair one bounded source-intake candidate",
        bounded_question="Reformat the supplied draft and retained observations without retrieval.",
        trusted_inputs=("topic_assignment_projection", "initial_structured_output_invalid"),
        untrusted_inputs=("worker_draft", "retained_tool_observations", "repair_model_summary"),
        capability_id="wave0-source-intake-repair",
        catalog_builder_id="graph/nodes/wave0/prompts.py::build_wave0_repair_prompt",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.ABSENT,
        feedback_source_seam="graph/nodes/wave0/subgraph.py::run_wave0_work_units_real",
        candidate_shape="CandidateResult",
        deterministic_admission_owner="graph/components/work_units.py::run_fixture_work_unit_component",
    ),
    _cognitive_row(
        "wave1/worker",
        product_responsibility="Baseline-aware evidence-extraction candidate",
        bounded_question="Retrieve and propose evidence beyond the assigned Wave0 baseline.",
        trusted_inputs=("topic_baseline_assignment_projection",),
        untrusted_inputs=("tool_results", "model_summary"),
        capability_id="wave1-evidence-extraction",
        catalog_builder_id="graph/nodes/wave1/prompts.py::build_wave1_worker_prompt",
        requested_tool_window=_ONE_RETRIEVAL,
        feedback_disposition=FeedbackDisposition.PARTIAL,
        feedback_recipient_case_id="wave1/repair",
        feedback_delivered_data=(
            "assignment_projection",
            "initial_structured_output_invalid_or_local_semantic_validation_failed",
            "draft",
            "untrusted_tool_results",
        ),
        feedback_omitted_data=("raw_parse_error", "submission_validation_codes", "artifact_validation_detail"),
        feedback_source_seam="graph/nodes/wave1/subgraph.py::_wave1_worker",
        candidate_shape="CandidateResult",
        deterministic_admission_owner="graph/components/work_units.py::run_fixture_work_unit_component",
    ),
    _cognitive_row(
        "wave1/repair",
        product_responsibility="Repair one bounded Wave1 evidence candidate",
        bounded_question="Reformat the supplied draft and retained observations without retrieval.",
        trusted_inputs=("topic_baseline_assignment_projection", "closed_pre_persistence_validation_category"),
        untrusted_inputs=("worker_draft", "retained_tool_observations", "repair_model_summary"),
        capability_id="wave1-evidence-extraction-repair",
        catalog_builder_id="graph/nodes/wave1/prompts.py::build_wave1_repair_prompt",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.ABSENT,
        feedback_source_seam="graph/nodes/wave1/subgraph.py::_wave1_worker",
        candidate_shape="CandidateResult",
        deterministic_admission_owner="graph/components/work_units.py::run_fixture_work_unit_component",
    ),
    _cognitive_row(
        "wave1/source-diagnostic",
        product_responsibility="Bound accepted-source diagnostic artifact",
        bounded_question="Classify only the accepted new-source observations for one Wave1 work attempt.",
        trusted_inputs=("accepted_record_identity", "accepted_new_source_selection"),
        untrusted_inputs=("source_observations", "model_summary"),
        capability_id="wave1-source-diagnostic",
        catalog_builder_id="graph/nodes/wave1/prompts.py::build_wave1_source_diagnostic_prompt",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.ABSENT,
        feedback_source_seam="graph/nodes/wave1/review.py::_dispatch_missing_reviews",
        candidate_shape="SourceDiagnosticResult",
        deterministic_admission_owner="graph/nodes/wave1/review.py::materialize_wave1_review_artifact",
    ),
    _cognitive_row(
        "wave1/claim-verifier",
        product_responsibility="Bound accepted-claim verification artifact",
        bounded_question="Assess only accepted claims against their assigned new-source identities.",
        trusted_inputs=("accepted_record_identity", "accepted_claims", "assigned_new_source_ids"),
        untrusted_inputs=("claim_statements", "model_summary"),
        capability_id="wave1-claim-verifier",
        catalog_builder_id="graph/nodes/wave1/prompts.py::build_wave1_claim_verifier_prompt",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.ABSENT,
        feedback_source_seam="graph/nodes/wave1/review.py::_dispatch_missing_reviews",
        candidate_shape="ClaimVerifierResult",
        deterministic_admission_owner="graph/nodes/wave1/review.py::materialize_wave1_review_artifact",
    ),
    _cognitive_row(
        "wave2-synthesis/synthesis",
        product_responsibility="Bounded accepted-evidence synthesis candidate",
        bounded_question="From the assigned accepted evidence, propose one supported findings, relations, and honest-gaps candidate.",
        trusted_inputs=("trusted topic assignment", "accepted submission refs", "closed output contract"),
        untrusted_inputs=("accepted evidence", "initial model candidate"),
        capability_id="wave2-evidence-synthesis",
        catalog_builder_id="graph/nodes/wave2_synthesis/prompts.py::build_synthesis_prompt",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.PARTIAL,
        feedback_recipient_case_id="wave2-synthesis/repair",
        feedback_delivered_data=("draft", "accepted_evidence", "closed_validation_category"),
        feedback_omitted_data=("raw_exception",),
        feedback_source_seam="graph/nodes/wave2_synthesis/node.py::build_real",
        candidate_shape="SynthesisResult",
        deterministic_admission_owner=(
            "graph/nodes/wave2_synthesis/node.py::_validate_synthesis_semantics -> "
            "graph/nodes/wave2_synthesis/materializer.py::materialize_synthesis"
        ),
    ),
    _cognitive_row(
        "wave2-synthesis/repair",
        product_responsibility="One structured accepted-evidence synthesis repair candidate",
        bounded_question="Repair one invalid draft against the same assignment without retrieval or invention.",
        trusted_inputs=("same trusted assignment", "closed validation category", "closed output contract"),
        untrusted_inputs=("accepted evidence", "initial model draft", "repair model candidate"),
        capability_id="wave2-evidence-synthesis-repair",
        catalog_builder_id="graph/nodes/wave2_synthesis/prompts.py::build_synthesis_repair_prompt",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.ABSENT,
        feedback_source_seam="graph/nodes/wave2_synthesis/node.py::build_real",
        candidate_shape="SynthesisResult",
        deterministic_admission_owner=(
            "graph/nodes/wave2_synthesis/node.py::_validate_synthesis_semantics -> "
            "graph/nodes/wave2_synthesis/materializer.py::materialize_synthesis"
        ),
    ),
    _cognitive_row(
        "targeted-evidence/worker",
        product_responsibility="Gap-scoped targeted evidence candidate",
        bounded_question="Retrieve evidence for one assigned gap and return a same-gap candidate.",
        trusted_inputs=("work_spec", "gap_id"),
        untrusted_inputs=("tool_results", "model_summary"),
        capability_id="targeted-gap-evidence-retrieval",
        catalog_builder_id="graph/nodes/targeted_evidence/prompts.py::build_targeted_worker_prompt",
        requested_tool_window=_ONE_RETRIEVAL,
        feedback_disposition=FeedbackDisposition.DELIVERED,
        feedback_recipient_case_id="targeted-evidence/repair",
        feedback_delivered_data=("draft", "validation_error"),
        feedback_source_seam="graph/nodes/targeted_evidence/subgraph.py::run_gap_workers",
        candidate_shape="CandidateResult",
        deterministic_admission_owner="graph/components/work_units.py::run_fixture_work_unit_component",
    ),
    _cognitive_row(
        "targeted-evidence/repair",
        product_responsibility="Repair one gap-scoped targeted evidence candidate",
        bounded_question="Repair the same-gap draft using the named validation error without retrieval.",
        trusted_inputs=("gap_id", "worker_draft", "validation_error"),
        untrusted_inputs=("initial_model_summary", "repair_model_summary"),
        capability_id="targeted-gap-evidence-repair",
        catalog_builder_id="graph/nodes/targeted_evidence/prompts.py::build_targeted_worker_repair_prompt",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.ABSENT,
        feedback_source_seam="graph/nodes/targeted_evidence/subgraph.py::run_gap_workers",
        candidate_shape="CandidateResult",
        deterministic_admission_owner="graph/components/work_units.py::run_fixture_work_unit_component",
    ),
    _cognitive_row(
        "targeted-evidence/source-diagnostic",
        product_responsibility="Source-diagnostic artifact candidate",
        bounded_question="Diagnose only the assigned source references and supplied contents.",
        trusted_inputs=("assigned_source_refs",),
        untrusted_inputs=("source_contents", "model_summary"),
        capability_id="targeted-source-diagnostic",
        catalog_builder_id="graph/nodes/targeted_evidence/prompts.py::build_source_diagnostic_prompt",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.ABSENT,
        feedback_source_seam="graph/nodes/targeted_evidence/subgraph.py::dispatch_critic",
        candidate_shape="SourceDiagnostic",
        deterministic_admission_owner="graph/nodes/targeted_evidence/materializer.py::materialize_source_diagnostic",
    ),
    _cognitive_row(
        "targeted-evidence/claim-verifier",
        product_responsibility="Assigned-reference claim-verifier artifact candidate",
        bounded_question="Verify only supplied claims against their assigned references.",
        trusted_inputs=("assigned_claims", "assigned_reference_ids"),
        untrusted_inputs=("model_summary",),
        capability_id="targeted-claim-verifier",
        catalog_builder_id="graph/nodes/targeted_evidence/prompts.py::build_claim_verifier_prompt",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.ABSENT,
        feedback_source_seam="graph/nodes/targeted_evidence/subgraph.py::dispatch_critic",
        candidate_shape="ClaimVerifierArtifact",
        deterministic_admission_owner="graph/nodes/targeted_evidence/materializer.py::materialize_claim_verifier",
    ),
    _cognitive_row(
        "final-delivery/composer",
        product_responsibility="Readiness-bounded final report layout candidate",
        bounded_question="Order every approved conclusion and mandatory uncertainty without changing its content.",
        trusted_inputs=("readiness_report_plan_entry_ids", "accepted_submission_refs"),
        untrusted_inputs=("accepted_evidence_content", "model_summary"),
        capability_id="final-delivery-composer",
        catalog_builder_id="graph/nodes/final_delivery/composer.py::build_final_delivery_request",
        requested_tool_window=_NO_TOOLS,
        feedback_disposition=FeedbackDisposition.ABSENT,
        feedback_source_seam="graph/nodes/final_delivery/node.py::build_real",
        candidate_shape="FinalDeliveryLayoutCandidate",
        deterministic_admission_owner="graph/nodes/final_delivery/composer.py::admit_layout_candidate",
    ),
)


def validate_cohort_evidence(
    rows: tuple[CapabilityEvidenceRow, ...],
    claims: Mapping[str, TestEvidenceClaim],
    *,
    collected_selectors: set[str],
) -> None:
    errors: list[str] = []
    if len(rows) != 20 or len({row.case_id for row in rows}) != len(rows):
        errors.append("cohort rows must be twenty unique direct cases")
    if len({row.capability_id for row in rows}) != len(rows):
        errors.append("cohort rows must use unique capabilities")
    bindings = {row.case_id: row.capability_id for row in rows}
    if bindings != EXPECTED_COHORT_BINDINGS:
        errors.append("cohort rows contain an unknown or missing capability binding")
    for row in rows:
        if not all((row.catalog_source, row.declaration_source, row.entrypoint, row.test_modules)):
            errors.append(f"{row.case_id}: source and entrypoint metadata is required")
        if row.success_claim_id == row.risk_claim_id:
            errors.append(f"{row.case_id}: claim ids must differ")
        resolved: list[TestEvidenceClaim] = []
        for claim_id in (row.success_claim_id, row.risk_claim_id):
            claim = claims.get(claim_id)
            if claim is None:
                errors.append(f"{row.case_id}: unknown claim {claim_id}")
                continue
            resolved.append(claim)
            if claim.selector not in collected_selectors:
                errors.append(f"{row.case_id}: uncollected claim {claim_id}")
            if not any(claim.selector.startswith(f"{module}::") for module in row.test_modules):
                errors.append(f"{row.case_id}: claim {claim_id} belongs to a different branch seam")
            allowed_authenticity = (
                {AuthenticityLevel.SCRIPTED_REAL_WORKFLOW}
                if row.case_id == "final-delivery/composer"
                else {
                    AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
                    AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
                }
                if row.case_id == "readiness/critic"
                else {AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES}
            )
            if claim.authenticity not in allowed_authenticity:
                errors.append(f"{row.case_id}: claim {claim_id} lacks real-node deterministic authenticity")
            expected_requirements = (
                {"FID-001", "FID-003", "NAC-009", "NOA-013", "EVH-022"}
                if row.case_id == "final-delivery/composer"
                else {"NAC-007", "EVH-016"}
                if row.case_id.startswith("targeted-evidence/")
                else (
                    {"REA-002", "REA-004", "REA-006", "EVH-021"}
                    if row.case_id == "readiness/critic"
                    else (
                        {"NAC-005", "EVH-013"}
                        if row.case_id in {"hitl1/brief", "hitl1/brief-repair"}
                        else (
                            {"NAC-006", "EVH-015"}
                            if row.case_id
                            in {
                                "topic-planning/plan",
                                "topic-planning/plan-repair",
                                "wave1/worker",
                                "wave1/repair",
                                "wave1/source-diagnostic",
                                "wave1/claim-verifier",
                            }
                            else {"NAC-003", "NAC-004", "EVH-012"}
                        )
                    )
                )
            )
            if not expected_requirements.issubset(claim.requirement_ids):
                errors.append(f"{row.case_id}: claim {claim_id} lacks cohort requirement ownership")
        if len(resolved) == 2 and resolved[0].selector == resolved[1].selector:
            errors.append(f"{row.case_id}: success and risk claims share a selector")
    if errors:
        raise ValueError("\n".join(errors))


def validate_cognitive_program_evidence(
    rows: tuple[CognitiveProgramEvidenceRow, ...],
    cohort_rows: tuple[CapabilityEvidenceRow, ...],
    claims: Mapping[str, TestEvidenceClaim],
    *,
    collected_selectors: set[str],
) -> None:
    """Validate the branch-ledger projection against its catalog and cohort owners."""

    from deerflow_deep_research.graph.prompt_catalog import prompt_catalog_cases

    errors: list[str] = []
    catalog = {case.case_id: case for case in prompt_catalog_cases()}
    catalog_ids = set(catalog)
    cohort_bindings = {row.case_id: row.capability_id for row in cohort_rows}
    cohort_ids = set(cohort_bindings)
    if catalog_ids != cohort_ids:
        for case_id in sorted(catalog_ids - cohort_ids):
            errors.append(f"{case_id}: missing cohort row")
        for case_id in sorted(cohort_ids - catalog_ids):
            errors.append(f"{case_id}: stale cohort row")

    ledger_by_case: dict[str, CognitiveProgramEvidenceRow] = {}
    for row in rows:
        if row.case_id in ledger_by_case:
            errors.append(f"{row.case_id}: duplicate ledger row")
            continue
        ledger_by_case[row.case_id] = row

    ledger_ids = set(ledger_by_case)
    for case_id in sorted(ledger_ids - catalog_ids):
        errors.append(f"{case_id}: grouped or stale ledger row")
    for case_id in sorted(catalog_ids - ledger_ids):
        errors.append(f"{case_id}: missing ledger row")

    required_roles = {
        EvidenceRole.COMPOSITION,
        EvidenceRole.FEEDBACK_DISPOSITION,
        EvidenceRole.GUARDRAIL_ADMISSION,
    }
    for case_id, row in ledger_by_case.items():
        catalog_case = catalog.get(case_id)
        cohort_capability = cohort_bindings.get(case_id)
        if catalog_case is None or cohort_capability is None:
            continue
        request = catalog_case.build_request()
        if row.capability_id != cohort_capability:
            errors.append(f"{case_id}: capability binding does not match cohort")
        if request.capability_ref is None or row.capability_id != request.capability_ref.capability_id:
            errors.append(f"{case_id}: capability binding does not match catalog")
        if row.catalog_builder_id != catalog_case.builder_id:
            errors.append(f"{case_id}: catalog builder does not match catalog")
        if row.final_render_seam != _FINAL_RENDER_SEAM:
            errors.append(f"{case_id}: final render seam is not canonical")
        if row.bridge_enforcer != _BRIDGE_ENFORCER:
            errors.append(f"{case_id}: bridge enforcer is not canonical")
        if row.requested_tool_window != RequestedToolWindow(
            tools_enabled=request.tools_enabled,
            minimum_tool_calls=request.minimum_tool_calls,
            tool_call_limit=request.tool_call_limit,
        ):
            errors.append(f"{case_id}: requested tool window does not match catalog")
        if not all(
            (
                row.product_responsibility,
                row.bounded_question,
                row.trusted_inputs,
                row.untrusted_inputs,
                row.feedback_source_seam,
                row.candidate_shape,
                row.deterministic_admission_owner,
            )
        ):
            errors.append(f"{case_id}: cognitive-program review metadata is required")

        if row.feedback_disposition is FeedbackDisposition.DELIVERED:
            if row.feedback_recipient_case_id is None or not row.feedback_delivered_data or row.feedback_omitted_data:
                errors.append(f"{case_id}: delivered feedback requires a recipient and bounded delivered data")
        elif row.feedback_disposition is FeedbackDisposition.PARTIAL:
            if (
                row.feedback_recipient_case_id is None
                or not row.feedback_delivered_data
                or not row.feedback_omitted_data
            ):
                errors.append(f"{case_id}: partial feedback requires recipient, delivered data, and omitted data")
        elif row.feedback_disposition is FeedbackDisposition.ABSENT:
            if row.feedback_recipient_case_id is not None or row.feedback_delivered_data:
                errors.append(f"{case_id}: absent feedback cannot name a recipient or delivered data")
        else:
            errors.append(f"{case_id}: feedback disposition is invalid")

        links_by_role: dict[EvidenceRole, list[CognitiveProgramEvidenceLink]] = {role: [] for role in required_roles}
        for link in row.evidence_links:
            if link.role not in required_roles:
                errors.append(f"{case_id}: unknown evidence role {link.role}")
                continue
            if not isinstance(link.classification, EvidenceClassification):
                errors.append(f"{case_id}: evidence link classification is invalid")
                continue
            links_by_role[link.role].append(link)
            if link.classification is EvidenceClassification.HUMAN_DECISION:
                errors.append(f"{case_id}: human-decision cannot close an active branch")
            claim = claims.get(link.claim_id)
            if claim is None:
                errors.append(f"{case_id}: unknown claim {link.claim_id}")
                continue
            if claim.selector not in collected_selectors:
                errors.append(f"{case_id}: uncollected claim {link.claim_id}")
            if link.classification is EvidenceClassification.OBSOLETE_DUPLICATE:
                continue
            if case_id not in claim.selector:
                errors.append(f"{case_id}: claim {link.claim_id} belongs to a different branch seam")

        for role, links in links_by_role.items():
            closing_links = [
                link
                for link in links
                if link.classification
                not in {
                    EvidenceClassification.HUMAN_DECISION,
                    EvidenceClassification.OBSOLETE_DUPLICATE,
                }
            ]
            has_obsolete_duplicate = any(
                link.classification is EvidenceClassification.OBSOLETE_DUPLICATE for link in links
            )
            if has_obsolete_duplicate and not closing_links:
                errors.append(f"{case_id}: obsolete duplicate cannot close {role.value}")
            if not closing_links:
                errors.append(f"{case_id}: missing {role.value} evidence role")
            elif len(closing_links) != 1:
                errors.append(f"{case_id}: multiple {role.value} evidence links")
        guardrail_links = links_by_role[EvidenceRole.GUARDRAIL_ADMISSION]
        if row.guardrail_claim_id not in {link.claim_id for link in guardrail_links}:
            errors.append(f"{case_id}: guardrail claim must be linked to guardrail-admission")

        if (
            case_id in _JUDGMENT_EVALUATIONS
            and row.evaluation_disposition is not EvaluationDisposition.JUDGMENT_EVALUATION_REQUIRED
        ):
            errors.append(f"{case_id}: judgment evaluation cannot be closed by deterministic evidence")
        elif row.evaluation_disposition is EvaluationDisposition.DETERMINISTIC_SUFFICIENT:
            if (
                row.evaluation_rationale != _DETERMINISTIC_EVALUATION_RATIONALE
                or row.evaluation_rubric is not None
                or row.nondeterministic_boundary is not None
            ):
                errors.append(f"{case_id}: deterministic evaluation disposition is incomplete")
        elif row.evaluation_disposition is EvaluationDisposition.JUDGMENT_EVALUATION_REQUIRED:
            if not all((row.evaluation_rationale, row.evaluation_rubric, row.nondeterministic_boundary)):
                errors.append(f"{case_id}: judgment evaluation disposition requires a rubric and boundary")
        else:
            errors.append(f"{case_id}: evaluation disposition is invalid")

    if errors:
        raise ValueError("\n".join(errors))


__all__ = [
    "COGNITIVE_PROGRAM_EVIDENCE",
    "COHORT_EVIDENCE",
    "CapabilityEvidenceRow",
    "CognitiveProgramEvidenceLink",
    "CognitiveProgramEvidenceRow",
    "EvidenceClassification",
    "EvidenceRole",
    "EvaluationDisposition",
    "FeedbackDisposition",
    "RequestedToolWindow",
    "validate_cognitive_program_evidence",
    "validate_cohort_evidence",
]
