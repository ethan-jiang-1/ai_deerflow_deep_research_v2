"""Complete test-owned node, branch, and evaluation evidence board.

@impl CPE-001
@impl CPE-004
@impl EVH-017
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from tests.assets.evidence import (
    AssetClass,
    AuthenticityLevel,
    FocusedSelection,
    TestEvidenceClaim,
)
from tests.assets.node_agent_capabilities import (
    COGNITIVE_PROGRAM_EVIDENCE,
    CapabilityEvidenceRow,
    CognitiveProgramEvidenceRow,
    EvidenceClassification,
    validate_cognitive_program_evidence,
)
from tests.assets.node_conformance import NodeConformance
from tests.assets.requirement_evidence import RequirementImpact
from tests.assets.workflow_nodes import ModelWorkflowCoverage


class CognitiveProgramBoardError(ValueError):
    pass


@dataclass(frozen=True)
class NodeEvidenceLink:
    """One collected central claim selected for a node-level proof purpose."""

    claim_id: str
    classification: EvidenceClassification


@dataclass(frozen=True)
class NodeEvidenceRow:
    """Review projection for one logical node's product responsibility."""

    logical_name: str
    product_responsibility: str
    participation_mode: str
    commitment_state: str
    current_operating_mechanism: str
    cognitive_or_control_hypothesis: str
    deterministic_authority: str
    branch_ids: tuple[str, ...]
    evidence_links: tuple[NodeEvidenceLink, ...]
    live_evaluation_applicability: str
    known_limitation: str


@dataclass(frozen=True)
class BranchEvaluationLink:
    """Exact calibration-case to central live-claim join for one branch."""

    calibration_case_id: str
    central_claim_id: str


@dataclass(frozen=True)
class BranchEvidenceReview:
    """Evaluation applicability and limitation for one direct model branch."""

    branch_id: str
    evaluation_links: tuple[BranchEvaluationLink, ...]
    known_limitation: str


@dataclass(frozen=True)
class CognitiveProgramEvidenceBoard:
    """Compact review projection over current node and branch evidence owners."""

    node_rows: tuple[NodeEvidenceRow, ...]
    branch_rows: tuple[CognitiveProgramEvidenceRow, ...]
    branch_reviews: tuple[BranchEvidenceReview, ...]


def _node_link(claim_id: str, classification: EvidenceClassification) -> NodeEvidenceLink:
    return NodeEvidenceLink(claim_id=claim_id, classification=classification)


_NODE_ROWS = (
    NodeEvidenceRow(
        logical_name="bootstrap",
        product_responsibility="Bind trusted bootstrap input to the research lifecycle",
        participation_mode="deterministic control",
        commitment_state="intentional controller exclusion",
        current_operating_mechanism="source-audited bootstrap bundle binding controller",
        cognitive_or_control_hypothesis=(
            "Bind one validated bootstrap bundle and route only from its trusted marker without model work."
        ),
        deterministic_authority="bootstrap handler writes validated initial state and typed route",
        branch_ids=(),
        evidence_links=(
            _node_link("bootstrap-marker-needs-input", EvidenceClassification.WIRING),
            _node_link("bootstrap-divergent-read-back", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
        ),
        live_evaluation_applicability="not applicable; the controller has no current direct model branch",
        known_limitation="Static conformance does not establish that an external request is semantically correct.",
    ),
    NodeEvidenceRow(
        logical_name="hitl1",
        product_responsibility="Turn a human request into an approved research profile",
        participation_mode="bounded cognitive program",
        commitment_state="current accepted",
        current_operating_mechanism="source-audited active model loop with graph-owned human input",
        cognitive_or_control_hypothesis=(
            "Propose and repair a bounded profile or semantic reply candidate while graph-owned input remains "
            "authoritative."
        ),
        deterministic_authority="profile parser/domain and graph handler publish profile and route",
        branch_ids=(
            "hitl1/brief",
            "hitl1/brief-repair",
            "hitl1/semantic-intake",
            "hitl1/semantic-intake-repair",
        ),
        evidence_links=(
            _node_link("workflow-hitl1-zero-tool-bridge", EvidenceClassification.COGNITIVE_PROGRAM),
            _node_link("hitl1-typed-failure-incident", EvidenceClassification.WIRING),
            _node_link("workflow-outcome-hitl1-lifecycle-projection", EvidenceClassification.WIRING),
            _node_link("hitl1-complete-response", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
            _node_link("hitl1-run-agent-failure", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
        ),
        live_evaluation_applicability=(
            "four branch-local calibration selectors are collected; no live result or model quality is asserted"
        ),
        known_limitation="Deterministic proof cannot assess whether a proposed profile captures the user's intent.",
    ),
    NodeEvidenceRow(
        logical_name="topic_planning",
        product_responsibility="Decompose a confirmed profile into a research-plan candidate",
        participation_mode="bounded cognitive program",
        commitment_state="current accepted",
        current_operating_mechanism="source-audited active zero-tool planner and repair loop",
        cognitive_or_control_hypothesis=(
            "Produce or repair a bounded TopicPlan candidate from the confirmed profile without publication authority."
        ),
        deterministic_authority="`domain/topics.py` materializes ids, coverage, state, and route",
        branch_ids=("topic-planning/plan", "topic-planning/plan-repair"),
        evidence_links=(
            _node_link("workflow-topic-planning-zero-tool-bridge", EvidenceClassification.COGNITIVE_PROGRAM),
            _node_link("workflow-outcome-topic-planning-known-invocation", EvidenceClassification.WIRING),
            _node_link("workflow-outcome-topic-planning-lifecycle-projection", EvidenceClassification.WIRING),
            _node_link("topic-planning-valid-plan", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
            _node_link("topic-planning-invalid-output", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
        ),
        live_evaluation_applicability=(
            "two branch-local calibration selectors are collected; no live result or model quality is asserted"
        ),
        known_limitation="Deterministic coverage cannot assess the usefulness of the proposed decomposition.",
    ),
    NodeEvidenceRow(
        logical_name="wave0",
        product_responsibility="Acquire authoritative-source evidence for assigned work",
        participation_mode="bounded cognitive program",
        commitment_state="current accepted",
        current_operating_mechanism="source-audited retrieval worker with zero-tool repair",
        cognitive_or_control_hypothesis=(
            "Retrieve a bounded authoritative-source candidate and repair only its retained draft when required."
        ),
        deterministic_authority="work-unit validator, controller, ledger, and gate admit evidence and route",
        branch_ids=("wave0/worker", "wave0/repair"),
        evidence_links=(
            _node_link("workflow-wave0-worker-bridge", EvidenceClassification.COGNITIVE_PROGRAM),
            _node_link("workflow-outcome-wave0-known-invocation", EvidenceClassification.WIRING),
            _node_link("wave0-complete-lifecycle", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
            _node_link("wave0-all-workers-fail", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
        ),
        live_evaluation_applicability=(
            "two branch-local calibration selectors are collected; no live result or model quality is asserted"
        ),
        known_limitation="Collected selectors do not establish source usefulness or live retrieval quality.",
    ),
    NodeEvidenceRow(
        logical_name="wave1",
        product_responsibility="Extract source-grounded evidence and bounded repair candidates",
        participation_mode="bounded cognitive program",
        commitment_state="current accepted",
        current_operating_mechanism=(
            "baseline-aware retrieval worker, zero-tool repair, and two bound zero-tool critics"
        ),
        cognitive_or_control_hypothesis=(
            "Extend the accepted baseline with bounded evidence and review artifacts without gaining ledger authority."
        ),
        deterministic_authority=(
            "validator, controller, ledger, review materializer, and gate own admission and route"
        ),
        branch_ids=(
            "wave1/worker",
            "wave1/repair",
            "wave1/source-diagnostic",
            "wave1/claim-verifier",
        ),
        evidence_links=(
            _node_link("workflow-wave1-worker-bridge", EvidenceClassification.COGNITIVE_PROGRAM),
            _node_link("workflow-outcome-wave1-known-invocation", EvidenceClassification.WIRING),
            _node_link("wave1-worker-ledger-success", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
            _node_link("wave1-malformed-worker-output", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
        ),
        live_evaluation_applicability=(
            "four branch-local calibration selectors are collected; no live result or model quality is asserted"
        ),
        known_limitation="Deterministic joins cannot assess extraction completeness or critic judgment quality.",
    ),
    NodeEvidenceRow(
        logical_name="wave2_synthesis",
        product_responsibility="Synthesize accepted evidence into findings and research gaps",
        participation_mode="bounded cognitive program",
        commitment_state="current accepted",
        current_operating_mechanism="runtime-loaded accepted-evidence method and zero-tool structured-repair loop",
        cognitive_or_control_hypothesis=(
            "Use runtime-loaded methods to propose one accepted-evidence candidate or one bounded repair "
            "without retrieval."
        ),
        deterministic_authority="semantic admission, gate preview, gate, and builder own publication and route",
        branch_ids=("wave2-synthesis/synthesis", "wave2-synthesis/repair"),
        evidence_links=(
            _node_link("workflow-wave2-zero-tool-bridge", EvidenceClassification.COGNITIVE_PROGRAM),
            _node_link("workflow-outcome-wave2-known-invocation", EvidenceClassification.WIRING),
            _node_link("wave2-canonical-findings", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
            _node_link("wave2-malformed-output", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
        ),
        live_evaluation_applicability=(
            "two branch-local quality selectors and one selected-live-ineligible deterministic Wave2 corpus "
            "are collected"
        ),
        known_limitation=(
            "Deterministic handoff proof cannot establish synthesis usefulness, gap prioritization, or provider "
            "quality."
        ),
    ),
    NodeEvidenceRow(
        logical_name="targeted_evidence",
        product_responsibility="Resolve a gate-projected evidence gap",
        participation_mode="bounded cognitive program",
        commitment_state="current accepted",
        current_operating_mechanism="source-audited retrieval, repair, and read-only critic branches",
        cognitive_or_control_hypothesis=(
            "Retrieve or repair evidence for one named gap and produce read-only diagnostics bound to accepted refs."
        ),
        deterministic_authority="worker admission, critic materializer, ledger, and builder own effects and route",
        branch_ids=(
            "targeted-evidence/worker",
            "targeted-evidence/repair",
            "targeted-evidence/source-diagnostic",
            "targeted-evidence/claim-verifier",
        ),
        evidence_links=(
            _node_link("workflow-targeted-evidence-worker-bridge", EvidenceClassification.COGNITIVE_PROGRAM),
            _node_link("workflow-outcome-targeted-evidence-known-invocation", EvidenceClassification.WIRING),
            _node_link("targeted-evidence-valid-artifact", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
            _node_link("targeted-evidence-malformed-output", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
        ),
        live_evaluation_applicability=(
            "four branch-local calibration selectors are collected; no live result or model quality is asserted"
        ),
        known_limitation="Selector provenance cannot establish same-gap retrieval or critic judgment quality.",
    ),
    NodeEvidenceRow(
        logical_name="hitl2",
        product_responsibility="Resolve a conditional research decision before delivery",
        participation_mode="human decision/authorization",
        commitment_state="conditional/unresolved",
        current_operating_mechanism="source-audited autonomous continuation",
        cognitive_or_control_hypothesis=(
            "Retain autonomous continuation until a non-inferable preference or irreversible authorization is admitted."
        ),
        deterministic_authority="typed choice validation and graph handler own any legal route",
        branch_ids=(),
        evidence_links=(
            _node_link("deferred-activation-dossiers", EvidenceClassification.HUMAN_DECISION),
            _node_link("hitl2-proceed-route", EvidenceClassification.WIRING),
            _node_link("hitl2-malformed-state-rejected", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
        ),
        live_evaluation_applicability="not applicable; no current interaction or direct model branch exists",
        known_limitation="The board proves only the conditional boundary, not an implemented human choice.",
    ),
    NodeEvidenceRow(
        logical_name="rerun",
        product_responsibility="Apply a validated rerun scope to research control",
        participation_mode="deterministic control",
        commitment_state="intentional controller exclusion",
        current_operating_mechanism="source-audited rerun-scope controller",
        cognitive_or_control_hypothesis=(
            "Validate one rerun scope, reset only its owned control facts, and select a legal deterministic route."
        ),
        deterministic_authority="rerun handler validates scope, writes control state, and returns route",
        branch_ids=(),
        evidence_links=(
            _node_link("rerun-full-scope-lifecycle", EvidenceClassification.WIRING),
            _node_link("rerun-generation-ceiling", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
        ),
        live_evaluation_applicability="not applicable; the controller has no current direct model branch",
        known_limitation="Static controller proof does not establish the value of a requested rerun scope.",
    ),
    NodeEvidenceRow(
        logical_name="readiness",
        product_responsibility="Judge per-question evidence sufficiency and answerability",
        participation_mode="bounded cognitive program",
        commitment_state="current accepted",
        current_operating_mechanism="source-audited active zero-tool evidence critic",
        cognitive_or_control_hypothesis=(
            "Classify each must-answer question against admitted evidence while hard rules retain route authority."
        ),
        deterministic_authority="hard rules, materializer, and graph handler own verdict admission and route",
        branch_ids=("readiness/critic",),
        evidence_links=(
            _node_link("workflow-readiness-evidence-critic-bridge", EvidenceClassification.COGNITIVE_PROGRAM),
            _node_link("readiness-critic-conservative-failure", EvidenceClassification.WIRING),
            _node_link("readiness-all-clear", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
            _node_link("readiness-no-evidence", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
        ),
        live_evaluation_applicability=(
            "three branch-local calibration selectors are collected; no live result or model quality is asserted"
        ),
        known_limitation="Deterministic admission cannot establish the critic's answerability judgment quality.",
    ),
    NodeEvidenceRow(
        logical_name="final_delivery",
        product_responsibility="Compose and communicate a report from accepted research state",
        participation_mode="bounded cognitive program",
        commitment_state="current accepted",
        current_operating_mechanism="source-audited active zero-tool layout composer",
        cognitive_or_control_hypothesis=(
            "Choose a bounded layout over approved report entries while rendering and publication stay deterministic."
        ),
        deterministic_authority=(
            "integrity gate and publisher own validation, publication, terminal status, and route"
        ),
        branch_ids=("final-delivery/composer",),
        evidence_links=(
            _node_link("nac-final-delivery-composer-success", EvidenceClassification.COGNITIVE_PROGRAM),
            _node_link("workflow-outcome-final-delivery-known-invocation", EvidenceClassification.WIRING),
            _node_link("nac-final-delivery-composer-risk", EvidenceClassification.WIRING),
            _node_link("final-delivery-completed", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
            _node_link("final-delivery-empty-evidence", EvidenceClassification.DETERMINISTIC_GUARDRAIL),
        ),
        live_evaluation_applicability=(
            "two branch-local calibration selectors are collected; no live result or model quality is asserted"
        ),
        known_limitation="Collected selectors do not establish that a model chose the most useful report layout.",
    ),
)


_BRANCH_BY_ID = {row.case_id: row for row in COGNITIVE_PROGRAM_EVIDENCE}


def _evaluation(calibration_case_id: str, central_claim_id: str) -> BranchEvaluationLink:
    return BranchEvaluationLink(calibration_case_id=calibration_case_id, central_claim_id=central_claim_id)


def _review(branch_id: str, *links: BranchEvaluationLink) -> BranchEvidenceReview:
    return BranchEvidenceReview(
        branch_id=branch_id,
        evaluation_links=tuple(links),
        known_limitation=_BRANCH_BY_ID[branch_id].evaluation_rationale,
    )


_BRANCH_REVIEWS = (
    _review(
        "hitl1/brief",
        _evaluation("calibrate-hitl1-brief-normal", "cal-live-hitl1-brief-normal"),
        _evaluation("calibrate-hitl1-brief-highest-risk", "cal-live-hitl1-brief-highest-risk"),
    ),
    _review(
        "hitl1/brief-repair",
        _evaluation("calibrate-hitl1-brief-repair-normal", "cal-live-hitl1-brief-repair-normal"),
        _evaluation(
            "calibrate-hitl1-brief-repair-highest-risk",
            "cal-live-hitl1-brief-repair-highest-risk",
        ),
    ),
    _review(
        "hitl1/semantic-intake",
        _evaluation("calibrate-hitl1-semantic-intake-normal", "cal-live-hitl1-semantic-intake-normal"),
        _evaluation(
            "calibrate-hitl1-semantic-intake-highest-risk",
            "cal-live-hitl1-semantic-intake-highest-risk",
        ),
    ),
    _review(
        "hitl1/semantic-intake-repair",
        _evaluation(
            "calibrate-hitl1-semantic-intake-repair-normal",
            "cal-live-hitl1-semantic-intake-repair-normal",
        ),
        _evaluation(
            "calibrate-hitl1-semantic-intake-repair-highest-risk",
            "cal-live-hitl1-semantic-intake-repair-highest-risk",
        ),
    ),
    _review(
        "topic-planning/plan",
        _evaluation("calibrate-topic-planning-plan-normal", "cal-live-topic-planning-plan-normal"),
        _evaluation(
            "calibrate-topic-planning-plan-highest-risk",
            "cal-live-topic-planning-plan-highest-risk",
        ),
    ),
    _review(
        "topic-planning/plan-repair",
        _evaluation(
            "calibrate-topic-planning-plan-repair-normal",
            "cal-live-topic-planning-plan-repair-normal",
        ),
        _evaluation(
            "calibrate-topic-planning-plan-repair-highest-risk",
            "cal-live-topic-planning-plan-repair-highest-risk",
        ),
    ),
    _review(
        "readiness/critic",
        _evaluation("calibrate-evidence-judgment-readiness-critic-supported", "ej-live-13"),
        _evaluation("calibrate-evidence-judgment-readiness-critic-insufficient", "ej-live-14"),
        _evaluation("calibrate-evidence-judgment-readiness-critic-repair-required", "ej-live-15"),
    ),
    _review(
        "wave0/worker",
        _evaluation(
            "calibrate-evidence-intake-wave0-worker-normal",
            "evidence-intake-live-wave0-worker-normal",
        ),
        _evaluation(
            "calibrate-evidence-intake-wave0-worker-highest-risk",
            "evidence-intake-live-wave0-worker-highest-risk",
        ),
    ),
    _review(
        "wave0/repair",
        _evaluation(
            "calibrate-evidence-intake-wave0-repair-normal",
            "evidence-intake-live-wave0-repair-normal",
        ),
        _evaluation(
            "calibrate-evidence-intake-wave0-repair-highest-risk",
            "evidence-intake-live-wave0-repair-highest-risk",
        ),
    ),
    _review(
        "wave1/worker",
        _evaluation(
            "calibrate-evidence-intake-wave1-worker-normal",
            "evidence-intake-live-wave1-worker-normal",
        ),
        _evaluation(
            "calibrate-evidence-intake-wave1-worker-highest-risk",
            "evidence-intake-live-wave1-worker-highest-risk",
        ),
    ),
    _review(
        "wave1/repair",
        _evaluation(
            "calibrate-evidence-intake-wave1-repair-normal",
            "evidence-intake-live-wave1-repair-normal",
        ),
        _evaluation(
            "calibrate-evidence-intake-wave1-repair-highest-risk",
            "evidence-intake-live-wave1-repair-highest-risk",
        ),
    ),
    _review(
        "wave1/source-diagnostic",
        _evaluation(
            "calibrate-evidence-intake-wave1-source-diagnostic-normal",
            "evidence-intake-live-wave1-source-diagnostic-normal",
        ),
        _evaluation(
            "calibrate-evidence-intake-wave1-source-diagnostic-highest-risk",
            "evidence-intake-live-wave1-source-diagnostic-highest-risk",
        ),
    ),
    _review(
        "wave1/claim-verifier",
        _evaluation(
            "calibrate-evidence-intake-wave1-claim-verifier-normal",
            "evidence-intake-live-wave1-claim-verifier-normal",
        ),
        _evaluation(
            "calibrate-evidence-intake-wave1-claim-verifier-highest-risk",
            "evidence-intake-live-wave1-claim-verifier-highest-risk",
        ),
    ),
    _review(
        "wave2-synthesis/synthesis",
        _evaluation("calibrate-evidence-judgment-wave2-synthesis-synthesis-normal", "ej-live-01"),
        _evaluation(
            "calibrate-evidence-judgment-wave2-synthesis-synthesis-highest-risk",
            "ej-live-02",
        ),
    ),
    _review(
        "wave2-synthesis/repair",
        _evaluation("calibrate-evidence-judgment-wave2-synthesis-repair-normal", "ej-live-03"),
        _evaluation("calibrate-evidence-judgment-wave2-synthesis-repair-highest-risk", "ej-live-04"),
    ),
    _review(
        "targeted-evidence/worker",
        _evaluation("calibrate-evidence-judgment-targeted-evidence-worker-normal", "ej-live-05"),
        _evaluation(
            "calibrate-evidence-judgment-targeted-evidence-worker-highest-risk",
            "ej-live-06",
        ),
    ),
    _review(
        "targeted-evidence/repair",
        _evaluation("calibrate-evidence-judgment-targeted-evidence-repair-normal", "ej-live-07"),
        _evaluation(
            "calibrate-evidence-judgment-targeted-evidence-repair-highest-risk",
            "ej-live-08",
        ),
    ),
    _review(
        "targeted-evidence/source-diagnostic",
        _evaluation(
            "calibrate-evidence-judgment-targeted-evidence-source-diagnostic-normal",
            "ej-live-09",
        ),
        _evaluation(
            "calibrate-evidence-judgment-targeted-evidence-source-diagnostic-highest-risk",
            "ej-live-10",
        ),
    ),
    _review(
        "targeted-evidence/claim-verifier",
        _evaluation(
            "calibrate-evidence-judgment-targeted-evidence-claim-verifier-normal",
            "ej-live-11",
        ),
        _evaluation(
            "calibrate-evidence-judgment-targeted-evidence-claim-verifier-highest-risk",
            "ej-live-12",
        ),
    ),
    _review(
        "final-delivery/composer",
        _evaluation("calibrate-final-composition-normal", "final-composition-live-normal"),
        _evaluation(
            "calibrate-final-composition-highest-risk",
            "final-composition-live-highest-risk",
        ),
    ),
)


COGNITIVE_PROGRAM_BOARD = CognitiveProgramEvidenceBoard(
    node_rows=_NODE_ROWS,
    branch_rows=COGNITIVE_PROGRAM_EVIDENCE,
    branch_reviews=_BRANCH_REVIEWS,
)


_BRANCH_PREFIX_OWNERS = {
    "hitl1": "hitl1",
    "topic-planning": "topic_planning",
    "wave0": "wave0",
    "wave1": "wave1",
    "wave2-synthesis": "wave2_synthesis",
    "targeted-evidence": "targeted_evidence",
    "readiness": "readiness",
    "final-delivery": "final_delivery",
}
_EXPECTED_EVALUATION_BINDINGS = {
    link.calibration_case_id: (review.branch_id, link.central_claim_id)
    for review in _BRANCH_REVIEWS
    for link in review.evaluation_links
}
_GENERIC_PRODUCT_IDENTITIES = {
    "agent",
    "controller",
    "logical node",
    "model node",
    "no-agent",
    "node-agent",
}


def _branch_owner(branch_id: str) -> str | None:
    return _BRANCH_PREFIX_OWNERS.get(branch_id.partition("/")[0])


def _unique(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def validate_cognitive_program_board(
    board: CognitiveProgramEvidenceBoard,
    *,
    logical_nodes: tuple[str, ...],
    reader_records: tuple[object, ...],
    cohort_rows: tuple[CapabilityEvidenceRow, ...],
    workflow_coverage: tuple[ModelWorkflowCoverage, ...],
    node_conformance: tuple[NodeConformance, ...],
    claims: Mapping[str, TestEvidenceClaim],
    requirement_impacts: tuple[RequirementImpact, ...],
    calibration_cases: tuple[object, ...],
    collected_selectors: set[str],
) -> None:
    """Validate exact joins while leaving every source owner authoritative."""

    try:
        validate_cognitive_program_evidence(
            board.branch_rows,
            cohort_rows,
            claims,
            collected_selectors=collected_selectors,
        )
    except ValueError as exc:
        raise CognitiveProgramBoardError(str(exc)) from exc

    branch_ids = tuple(row.case_id for row in board.branch_rows)
    review_ids = tuple(review.branch_id for review in board.branch_reviews)
    if (
        len(review_ids) != len(branch_ids)
        or len(set(review_ids)) != len(review_ids)
        or set(review_ids) != set(branch_ids)
    ):
        raise CognitiveProgramBoardError("branch review denominator invalid")

    node_ids = tuple(row.logical_name for row in board.node_rows)
    if node_ids != tuple(logical_nodes) or len(set(node_ids)) != len(node_ids):
        raise CognitiveProgramBoardError("node denominator invalid")

    readers = {getattr(record, "node", None): record for record in reader_records}
    if len(readers) != len(reader_records) or set(readers) != set(logical_nodes):
        raise CognitiveProgramBoardError("reader denominator invalid")
    workflows = {row.logical_name: row for row in workflow_coverage}
    if len(workflows) != len(workflow_coverage):
        raise CognitiveProgramBoardError("workflow coverage denominator invalid")
    conformance = {row.logical_name: row for row in node_conformance}
    if len(conformance) != len(node_conformance) or set(conformance) != set(logical_nodes):
        raise CognitiveProgramBoardError("node conformance denominator invalid")

    expected_branches_by_node = {
        node: tuple(branch_id for branch_id in branch_ids if _branch_owner(branch_id) == node) for node in logical_nodes
    }
    active_nodes = {node for node, branches in expected_branches_by_node.items() if branches}
    if set(workflows) != active_nodes:
        raise CognitiveProgramBoardError("workflow coverage denominator invalid")

    impacts_by_selector: dict[str, list[RequirementImpact]] = {}
    for impact in requirement_impacts:
        impacts_by_selector.setdefault(impact.selector, []).append(impact)

    for row in board.node_rows:
        required_identity = (
            row.product_responsibility,
            row.participation_mode,
            row.commitment_state,
            row.current_operating_mechanism,
            row.cognitive_or_control_hypothesis,
            row.deterministic_authority,
        )
        if not all(required_identity):
            raise CognitiveProgramBoardError(f"{row.logical_name}: node identity field missing")
        normalized_product = row.product_responsibility.strip().lower()
        if normalized_product in _GENERIC_PRODUCT_IDENTITIES or "node-agent" in normalized_product:
            raise CognitiveProgramBoardError(f"{row.logical_name}: product responsibility invalid")
        if not row.live_evaluation_applicability:
            raise CognitiveProgramBoardError(f"{row.logical_name}: live evaluation applicability missing")
        if not row.known_limitation:
            raise CognitiveProgramBoardError(f"{row.logical_name}: known limitation missing")

        for branch_id in row.branch_ids:
            if _branch_owner(branch_id) != row.logical_name:
                raise CognitiveProgramBoardError(f"{row.logical_name}: branch owner invalid")
        if row.branch_ids != expected_branches_by_node[row.logical_name]:
            raise CognitiveProgramBoardError(f"{row.logical_name}: branch owner invalid")

        reader = readers[row.logical_name]
        reader_values = (
            getattr(reader, "product_responsibility", None),
            getattr(reader, "participation_mode", None),
            getattr(reader, "commitment_state", None),
            getattr(reader, "current_operating_mechanism", None),
            getattr(reader, "deterministic_authority_boundary", None),
        )
        board_values = (
            row.product_responsibility,
            row.participation_mode,
            row.commitment_state,
            row.current_operating_mechanism,
            row.deterministic_authority,
        )
        if board_values != reader_values:
            raise CognitiveProgramBoardError(f"{row.logical_name}: reader identity mismatch")

        node_conformance_row = conformance[row.logical_name]
        expected_claim_ids = (
            node_conformance_row.success_claim_id,
            node_conformance_row.risk_claim_id,
        )
        workflow = workflows.get(row.logical_name)
        if workflow is not None:
            expected_claim_ids = (*workflow.referenced_claim_ids, *expected_claim_ids)
        elif row.logical_name == "hitl2":
            expected_claim_ids = ("deferred-activation-dossiers", *expected_claim_ids)
        expected_claim_ids = _unique(expected_claim_ids)

        actual_claim_ids = tuple(link.claim_id for link in row.evidence_links)
        if len(actual_claim_ids) != len(set(actual_claim_ids)):
            raise CognitiveProgramBoardError(f"{row.logical_name}: duplicate node claim")
        for link in row.evidence_links:
            if not isinstance(link.classification, EvidenceClassification):
                raise CognitiveProgramBoardError(f"{row.logical_name}: node claim classification invalid")
            claim = claims.get(link.claim_id)
            if claim is None:
                raise CognitiveProgramBoardError(f"{row.logical_name}: unknown node claim {link.claim_id}")
            if claim.selector not in collected_selectors:
                raise CognitiveProgramBoardError(f"{row.logical_name}: uncollected node claim {link.claim_id}")
            if link.claim_id not in expected_claim_ids:
                raise CognitiveProgramBoardError(f"{row.logical_name}: node claim owner invalid")
            if link.classification is EvidenceClassification.OBSOLETE_DUPLICATE:
                raise CognitiveProgramBoardError(f"{row.logical_name}: obsolete duplicate cannot close node proof")
            if link.classification is EvidenceClassification.HUMAN_DECISION:
                if row.logical_name != "hitl2" or link.claim_id != "deferred-activation-dossiers":
                    raise CognitiveProgramBoardError(f"{row.logical_name}: human-decision node proof invalid")
                impacts = impacts_by_selector.get(claim.selector, ())
                if not any(
                    impact.requirement_id == "CNI-004" and impact.owning_contract == "cognitive-node-interface"
                    for impact in impacts
                ):
                    raise CognitiveProgramBoardError("hitl2: human-decision requirement impact missing")
            elif (
                row.logical_name not in active_nodes and link.classification is EvidenceClassification.COGNITIVE_PROGRAM
            ):
                raise CognitiveProgramBoardError(f"{row.logical_name}: false active cognitive program")

        if set(actual_claim_ids) != set(expected_claim_ids):
            raise CognitiveProgramBoardError(f"{row.logical_name}: node proof denominator invalid")
        if workflow is not None:
            primary = next(link for link in row.evidence_links if link.claim_id == workflow.claim_id)
            if primary.classification is not EvidenceClassification.COGNITIVE_PROGRAM:
                raise CognitiveProgramBoardError(f"{row.logical_name}: active cognitive proof classification invalid")

    case_ids = tuple(getattr(case, "case_id", None) for case in calibration_cases)
    expected_case_ids = set(_EXPECTED_EVALUATION_BINDINGS)
    if len(case_ids) != 41 or len(set(case_ids)) != len(case_ids) or set(case_ids) != expected_case_ids:
        raise CognitiveProgramBoardError("calibration case denominator invalid")
    cases = {case.case_id: case for case in calibration_cases}
    for case_id, (expected_branch, _claim_id) in _EXPECTED_EVALUATION_BINDINGS.items():
        if getattr(cases[case_id], "branch_id", None) != expected_branch:
            raise CognitiveProgramBoardError("calibration case denominator invalid")

    linked_case_ids: list[str] = []
    for review in board.branch_reviews:
        if not review.known_limitation:
            raise CognitiveProgramBoardError(f"{review.branch_id}: known limitation missing")
        for link in review.evaluation_links:
            case = cases.get(link.calibration_case_id)
            if case is None:
                raise CognitiveProgramBoardError("unknown calibration case")
            if getattr(case, "branch_id", None) != review.branch_id:
                raise CognitiveProgramBoardError("evaluation case belongs to a different branch")
            expected_branch, expected_claim_id = _EXPECTED_EVALUATION_BINDINGS[link.calibration_case_id]
            if expected_branch != review.branch_id:
                raise CognitiveProgramBoardError("evaluation case belongs to a different branch")
            claim = claims.get(link.central_claim_id)
            if claim is None:
                raise CognitiveProgramBoardError("unknown central evaluation claim")
            if claim.selector not in collected_selectors:
                raise CognitiveProgramBoardError("uncollected central evaluation claim")
            if link.central_claim_id != expected_claim_id or claim.scenario_case_id != link.calibration_case_id:
                raise CognitiveProgramBoardError("central evaluation claim mapping invalid")
            if (
                claim.expected_selection is not FocusedSelection.LIVE
                or claim.asset_class is not AssetClass.LIVE_BEHAVIORAL_EVALUATION
                or claim.authenticity is not AuthenticityLevel.LIVE_REAL_DEPENDENCIES
            ):
                raise CognitiveProgramBoardError("central evaluation claim classification invalid")
            linked_case_ids.append(link.calibration_case_id)

    if (
        len(linked_case_ids) != 41
        or len(set(linked_case_ids)) != len(linked_case_ids)
        or set(linked_case_ids) != expected_case_ids
    ):
        raise CognitiveProgramBoardError("calibration link denominator invalid")

    claims_by_case: dict[str, list[TestEvidenceClaim]] = {case_id: [] for case_id in expected_case_ids}
    for claim in claims.values():
        if claim.scenario_case_id in claims_by_case:
            claims_by_case[claim.scenario_case_id].append(claim)
    if any(
        len(bound_claims) != 1 or bound_claims[0].claim_id != _EXPECTED_EVALUATION_BINDINGS[case_id][1]
        for case_id, bound_claims in claims_by_case.items()
    ):
        raise CognitiveProgramBoardError("central evaluation claim denominator invalid")


__all__ = [
    "COGNITIVE_PROGRAM_BOARD",
    "BranchEvaluationLink",
    "BranchEvidenceReview",
    "CognitiveProgramBoardError",
    "CognitiveProgramEvidenceBoard",
    "NodeEvidenceLink",
    "NodeEvidenceRow",
    "validate_cognitive_program_board",
]
