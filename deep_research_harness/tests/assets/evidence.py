"""Canonical test-evidence vocabulary and synthetic claim validation.

@impl EVH-006
@impl EVH-007
@impl EVH-008
@impl WFO-001
@impl WFO-002
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Set
from dataclasses import dataclass
from enum import StrEnum

from tests.scenarios.evidence_intake_calibration import EVIDENCE_INTAKE_CALIBRATION_CASES
from tests.scenarios.evidence_judgment_calibration import EVIDENCE_JUDGMENT_CALIBRATION_CASES
from tests.scenarios.intake_planning_calibration import CALIBRATION_CASES

CLAIM_ID_RE = re.compile(r"^[a-z][a-z0-9-]{2,63}$")
CASE_ID_RE = re.compile(r"^[a-z][a-z0-9-]{2,127}$")
REQUIREMENT_ID_RE = re.compile(r"^[A-Z]{3}-\d{3}$")
DISCOVERY_ID_RE = re.compile(r"^(?:LIVE|RELEASE)-\d{8}-\d{2}$")
MAX_REQUIREMENT_IDS = 32
MAX_DISCOVERY_IDS = 64
_COGNITIVE_PROGRAM_CASE_IDS = (
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
)
_INTAKE_PLANNING_CALIBRATION_CASES = tuple(
    (
        case.case_id,
        ("EVH-018", "HIN-012" if case.branch_id.startswith("hitl1/") else "TOP-007"),
    )
    for case in CALIBRATION_CASES
)
_EVIDENCE_INTAKE_CALIBRATION_CASES = tuple(
    (
        case.case_id,
        ("EVH-030", "WAN-012" if case.branch_id.startswith("wave0/") else "WON-012"),
    )
    for case in EVIDENCE_INTAKE_CALIBRATION_CASES
)
_EVIDENCE_JUDGMENT_CALIBRATION_CASES = tuple(
    (
        case.case_id,
        (
            ("EVH-021", "REA-002")
            if case.branch_id == "readiness/critic"
            else ("EVH-020", "WSN-006" if case.branch_id.startswith("wave2-") else "TEL-006")
        ),
    )
    for case in EVIDENCE_JUDGMENT_CALIBRATION_CASES
)
SELECTOR_RE = re.compile(
    r"^tests/[A-Za-z0-9_./-]+\.py::"
    r"(?:[A-Za-z_][A-Za-z0-9_]*::)*"
    r"test_[A-Za-z0-9_]+"
    r"(?:\[[^\]\r\n]{1,128}\])?$"
)


class AssetClass(StrEnum):
    CODE_CORRECTNESS = "code-correctness"
    DETERMINISTIC_WORKFLOW_CONFORMANCE = "deterministic-workflow-conformance"
    LIVE_BEHAVIORAL_EVALUATION = "live-behavioral-evaluation"


class StableSeam(StrEnum):
    DOMAIN_ENGINE = "domain-engine"
    NODE_INTERFACE = "node-interface"
    RUNTIME_INTEGRATION = "runtime-integration"
    LIFECYCLE_MIXED_GRAPH = "lifecycle-mixed-graph"
    PUBLIC_ENTRY = "public-entry"


class AuthenticityLevel(StrEnum):
    FAKE_GRAPH = "fake-graph"
    REAL_NODE_FAKE_CAPABILITIES = "real-node-fake-capabilities"
    SCRIPTED_REAL_WORKFLOW = "scripted-real-workflow"
    LIVE_REAL_DEPENDENCIES = "live-real-dependencies"
    FULL_REAL_PIPELINE = "full-real-pipeline"


class FocusedSelection(StrEnum):
    FAST = "fast"
    INTEGRATION = "integration"
    WORKFLOW = "workflow"
    LIVE = "live"
    PERIODIC = "periodic"


class EvidenceClaimError(ValueError):
    pass


@dataclass(frozen=True)
class TestEvidenceClaim:
    claim_id: str
    selector: str
    expected_selection: FocusedSelection
    requirement_ids: tuple[str, ...]
    asset_class: AssetClass
    seam: StableSeam
    authenticity: AuthenticityLevel | None = None
    scenario_case_id: str | None = None
    discovery_ids: tuple[str, ...] = ()

    __test__ = False

    def __post_init__(self) -> None:
        if not isinstance(self.claim_id, str) or not CLAIM_ID_RE.fullmatch(self.claim_id):
            raise ValueError("claim_id_invalid")
        if not isinstance(self.selector, str) or not self.selector or len(self.selector) > 512:
            raise ValueError("claim_selector_invalid")
        if "*" in self.selector or "?" in self.selector:
            raise ValueError("claim_selector_pattern_forbidden")
        if not SELECTOR_RE.fullmatch(self.selector):
            raise ValueError("claim_selector_not_exact")
        _require_enum(self.expected_selection, FocusedSelection, "claim_expected_selection_invalid")
        _require_enum(self.asset_class, AssetClass, "claim_asset_class_invalid")
        _require_enum(self.seam, StableSeam, "claim_seam_invalid")
        if self.authenticity is not None:
            _require_enum(self.authenticity, AuthenticityLevel, "claim_authenticity_invalid")
        allowed_selections = {
            AssetClass.CODE_CORRECTNESS: {
                FocusedSelection.FAST,
                FocusedSelection.INTEGRATION,
                FocusedSelection.PERIODIC,
            },
            AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE: {FocusedSelection.WORKFLOW},
            AssetClass.LIVE_BEHAVIORAL_EVALUATION: {FocusedSelection.LIVE},
        }
        if self.expected_selection not in allowed_selections[self.asset_class]:
            raise ValueError("claim_asset_selection_conflict")
        if not isinstance(self.requirement_ids, tuple):
            raise ValueError("claim_requirement_ids_invalid")
        if not self.requirement_ids or any(
            not isinstance(value, str) or not REQUIREMENT_ID_RE.fullmatch(value) for value in self.requirement_ids
        ):
            raise ValueError("claim_requirement_ids_invalid")
        if len(self.requirement_ids) > MAX_REQUIREMENT_IDS:
            raise ValueError("claim_requirement_ids_oversize")
        if len(set(self.requirement_ids)) != len(self.requirement_ids):
            raise ValueError("claim_requirement_ids_duplicate")
        if self.scenario_case_id is not None and (
            not isinstance(self.scenario_case_id, str) or not CASE_ID_RE.fullmatch(self.scenario_case_id)
        ):
            raise ValueError("claim_scenario_case_id_invalid")
        if not isinstance(self.discovery_ids, tuple):
            raise ValueError("claim_discovery_ids_invalid")
        if any(not isinstance(value, str) or not DISCOVERY_ID_RE.fullmatch(value) for value in self.discovery_ids):
            raise ValueError("claim_discovery_ids_invalid")
        if len(self.discovery_ids) > MAX_DISCOVERY_IDS:
            raise ValueError("claim_discovery_ids_oversize")
        if len(set(self.discovery_ids)) != len(self.discovery_ids):
            raise ValueError("claim_discovery_ids_duplicate")


def _require_enum(value: object, enum_type: type[StrEnum], code: str) -> None:
    if not isinstance(value, enum_type):
        raise ValueError(code)


def validate_evidence_claims(
    claims: Iterable[TestEvidenceClaim],
    *,
    supplied_case_ids: Set[str],
    collected_selectors: Set[str],
) -> None:
    claims = tuple(claims)
    errors: list[str] = []
    claim_ids: set[str] = set()
    for claim in claims:
        if claim.claim_id in claim_ids:
            errors.append(f"duplicate claim id: {claim.claim_id}")
        claim_ids.add(claim.claim_id)

    by_case: dict[str, list[TestEvidenceClaim]] = {case_id: [] for case_id in supplied_case_ids}
    for claim in claims:
        if claim.scenario_case_id is None:
            continue
        if claim.scenario_case_id not in supplied_case_ids:
            errors.append(f"{claim.claim_id}: unknown scenario case {claim.scenario_case_id}")
            continue
        by_case[claim.scenario_case_id].append(claim)

    for case_id, bound_claims in sorted(by_case.items()):
        if len(bound_claims) != 1:
            errors.append(f"scenario case {case_id} resolves to {len(bound_claims)} claims")
            continue
        claim = bound_claims[0]
        if case_id not in claim.selector:
            errors.append(f"{claim.claim_id}: selector does not contain stable case id {case_id}")

    for claim in claims:
        if claim.selector not in collected_selectors:
            errors.append(f"{claim.claim_id}: uncollected selector {claim.selector}")

    selectors: dict[str, str] = {}
    for claim in claims:
        prior = selectors.get(claim.selector)
        if prior is not None and not (
            claim.scenario_case_id is not None
            and any(error.startswith(f"scenario case {claim.scenario_case_id} resolves to") for error in errors)
        ):
            errors.append(f"duplicate selector: {claim.selector} ({prior}, {claim.claim_id})")
        selectors[claim.selector] = claim.claim_id

    if errors:
        raise EvidenceClaimError("\n".join(errors))


def claim_index(claims: Iterable[TestEvidenceClaim]) -> dict[str, TestEvidenceClaim]:
    """Index a central claim catalog while enforcing global identity."""
    indexed: dict[str, TestEvidenceClaim] = {}
    selectors: dict[str, str] = {}
    errors: list[str] = []
    for claim in claims:
        if claim.claim_id in indexed:
            errors.append(f"duplicate claim id: {claim.claim_id}")
        prior = selectors.get(claim.selector)
        if prior is not None:
            errors.append(f"duplicate selector: {claim.selector} ({prior}, {claim.claim_id})")
        indexed[claim.claim_id] = claim
        selectors[claim.selector] = claim.claim_id
    if errors:
        raise EvidenceClaimError("\n".join(errors))
    return indexed


def validate_inventory_claim_references(
    references: Iterable[tuple[str, tuple[str, ...]]],
    *,
    claims: Mapping[str, TestEvidenceClaim],
) -> None:
    """Resolve inventory references and reject conflicting selector metadata."""
    errors: list[str] = []
    referenced_selectors: dict[str, tuple[str, TestEvidenceClaim]] = {}
    for owner_id, claim_ids in references:
        for claim_id in claim_ids:
            claim = claims.get(claim_id)
            if claim is None:
                errors.append(f"{owner_id}: unknown claim {claim_id}")
                continue
            prior = referenced_selectors.get(claim.selector)
            if prior is not None:
                prior_id, prior_claim = prior
                if claim != prior_claim:
                    errors.append(
                        f"{owner_id}: contradictory selector reference {claim.selector}; "
                        f"{prior_id} uses {prior_claim.claim_id}, registered claim is {claim.claim_id}"
                    )
            else:
                referenced_selectors[claim.selector] = (owner_id, claim)
    if errors:
        raise EvidenceClaimError("\n".join(errors))


def validate_claim_selections(
    claims: Iterable[TestEvidenceClaim],
    *,
    focused_selectors: Mapping[FocusedSelection, Set[str]],
) -> None:
    errors: list[str] = []
    missing = set(FocusedSelection) - focused_selectors.keys()
    for selection in sorted(missing, key=lambda value: value.value):
        errors.append(f"missing focused collection: {selection.value}")

    for claim in claims:
        expected = focused_selectors.get(claim.expected_selection)
        if expected is None:
            continue
        if claim.selector not in expected:
            errors.append(
                f"{claim.claim_id}: selector missing from expected {claim.expected_selection.value} selection: "
                f"{claim.selector}"
            )
        for selection, selectors in focused_selectors.items():
            if selection is not claim.expected_selection and claim.selector in selectors:
                errors.append(
                    f"{claim.claim_id}: selector also collected by {selection.value} selection: {claim.selector}"
                )

    if errors:
        raise EvidenceClaimError("\n".join(errors))


def _correctness_claim(
    claim_id: str,
    selector: str,
    seam: StableSeam,
    *,
    requirement_ids: tuple[str, ...] = ("EVH-008",),
    authenticity: AuthenticityLevel | None = None,
    discovery_ids: tuple[str, ...] = (),
) -> TestEvidenceClaim:
    if selector.startswith("tests/integration/"):
        selection = FocusedSelection.INTEGRATION
    elif selector.startswith("tests/scenarios_periodic/"):
        selection = FocusedSelection.PERIODIC
    else:
        selection = FocusedSelection.FAST
    return TestEvidenceClaim(
        claim_id=claim_id,
        selector=selector,
        expected_selection=selection,
        requirement_ids=requirement_ids,
        asset_class=AssetClass.CODE_CORRECTNESS,
        seam=seam,
        authenticity=authenticity,
        discovery_ids=discovery_ids,
    )


EVIDENCE_CLAIMS = (
    TestEvidenceClaim(
        claim_id="workflow-hitl1-zero-tool-bridge",
        selector="tests/integration/test_zero_tool_node_conformance.py::test_hitl1_brief_generation_crosses_real_zero_tool_bridge",
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=("EVH-008", "EVH-009"),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.NODE_INTERFACE,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
    ),
    TestEvidenceClaim(
        claim_id="workflow-topic-planning-zero-tool-bridge",
        selector="tests/integration/test_zero_tool_node_conformance.py::test_topic_planning_crosses_real_zero_tool_bridge",
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=("EVH-008", "EVH-009", "TOP-006", "EVH-015"),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.NODE_INTERFACE,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
    ),
    TestEvidenceClaim(
        claim_id="workflow-wave2-zero-tool-bridge",
        selector="tests/integration/test_zero_tool_node_conformance.py::test_wave2_crosses_real_zero_tool_bridge",
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=("EVH-008", "EVH-009", "WSN-005", "EVH-016"),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.NODE_INTERFACE,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
    ),
    TestEvidenceClaim(
        claim_id="wave2-cognitive-program-production-scenarios",
        selector=(
            "tests/eval/test_cognitive_evaluation_suite.py::"
            "test_wave2_cognitive_program_production_scenarios_record_only_declared_handoffs"
        ),
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=("EVH-029",),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.RUNTIME_INTEGRATION,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
    ),
    TestEvidenceClaim(
        claim_id="workflow-wave0-worker-bridge",
        selector="tests/integration/test_worker_bridge_conformance.py::test_scripted_worker_traverses_real_bridge_tool_policy_artifacts_and_ledger[quick-factual]",
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=("EVH-008", "EVH-009", "WAN-007", "EVH-015"),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.RUNTIME_INTEGRATION,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
        scenario_case_id="quick-factual",
    ),
    TestEvidenceClaim(
        claim_id="workflow-targeted-evidence-worker-bridge",
        selector="tests/integration/test_worker_bridge_conformance.py::test_scripted_worker_traverses_real_bridge_tool_policy_artifacts_and_ledger[targeted_evidence]",
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=("EVH-008", "EVH-009", "NAC-007", "TEL-005", "EVH-016"),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.RUNTIME_INTEGRATION,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
    ),
    TestEvidenceClaim(
        claim_id="workflow-targeted-evidence-critic-bridge",
        selector="tests/integration/test_zero_tool_node_conformance.py::test_targeted_critic_crosses_real_zero_tool_bridge_without_new_recovery",
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=("EVH-008", "EVH-009", "NAC-007", "TEL-005", "EVH-016"),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.NODE_INTERFACE,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
    ),
    TestEvidenceClaim(
        claim_id="workflow-readiness-evidence-critic-bridge",
        selector="tests/integration/test_zero_tool_node_conformance.py::test_readiness_critic_crosses_real_zero_tool_bridge_and_uses_ledger_projection",
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=("EVH-008", "EVH-009", "REA-002", "REA-004", "REA-006", "EVH-021"),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.RUNTIME_INTEGRATION,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
    ),
    TestEvidenceClaim(
        claim_id="nac-final-delivery-composer-success",
        selector=(
            "tests/integration/test_zero_tool_node_conformance.py::"
            "test_final_delivery_scripted_real_bridge_composes_publishes_and_completes_through_gate"
        ),
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=(
            "EVH-008",
            "EVH-009",
            "FID-001",
            "FID-002",
            "FID-003",
            "FID-004",
            "FID-005",
            "NAC-009",
            "NOA-013",
            "EVH-022",
        ),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.LIFECYCLE_MIXED_GRAPH,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
    ),
    TestEvidenceClaim(
        claim_id="nac-final-delivery-composer-risk",
        selector=(
            "tests/integration/test_zero_tool_node_conformance.py::"
            "test_final_delivery_scripted_real_bridge_rejects_plan_violation_before_publication"
        ),
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=(
            "EVH-008",
            "EVH-009",
            "FID-001",
            "FID-002",
            "FID-003",
            "FID-004",
            "FID-005",
            "NAC-009",
            "NOA-013",
            "EVH-022",
        ),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.LIFECYCLE_MIXED_GRAPH,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
    ),
    TestEvidenceClaim(
        claim_id="workflow-wave1-worker-bridge",
        selector="tests/integration/test_worker_bridge_conformance.py::test_scripted_worker_traverses_real_bridge_tool_policy_artifacts_and_ledger[claim-verification]",
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=("EVH-008", "EVH-009", "WON-007", "EVH-015"),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.RUNTIME_INTEGRATION,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
        scenario_case_id="claim-verification",
    ),
    TestEvidenceClaim(
        claim_id="workflow-outcome-hitl1-lifecycle-projection",
        selector="tests/integration/test_hitl1_lifecycle.py::test_lost_bundle_cannot_supply_pending_input_or_be_reactivated",
        expected_selection=FocusedSelection.INTEGRATION,
        requirement_ids=("WFO-001", "WFO-002"),
        asset_class=AssetClass.CODE_CORRECTNESS,
        seam=StableSeam.LIFECYCLE_MIXED_GRAPH,
        authenticity=None,
    ),
    TestEvidenceClaim(
        claim_id="workflow-outcome-topic-planning-lifecycle-projection",
        selector="tests/integration/test_topic_planning_lifecycle.py::test_topic_planning_rejects_missing_selected_bundle_before_agent_invocation",
        expected_selection=FocusedSelection.INTEGRATION,
        requirement_ids=("WFO-001", "WFO-002"),
        asset_class=AssetClass.CODE_CORRECTNESS,
        seam=StableSeam.LIFECYCLE_MIXED_GRAPH,
        authenticity=None,
    ),
    _correctness_claim(
        "workflow-outcome-domain-normalization",
        "tests/domain/test_workflow_outcomes.py::test_known_node_problem_is_preserved_without_exposing_result_payload",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("WFO-001",),
    ),
    _correctness_claim(
        "workflow-outcome-topic-planning-known-invocation",
        "tests/graph/test_topic_planning_node.py::test_known_invocation_problem_survives_topic_planning_terminal_update",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("WFO-001", "WFO-002"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "workflow-outcome-wave0-known-invocation",
        "tests/integration/test_wave0_work_units.py::test_real_wave0_known_invocation_problem_reaches_worker_controller",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("WFO-001", "WFO-002"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "workflow-outcome-wave1-known-invocation",
        "tests/integration/test_wave1_work_units.py::test_real_wave1_known_invocation_problem_reaches_worker_controller",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("WFO-001", "WFO-002"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "workflow-outcome-wave2-known-invocation",
        "tests/graph/test_wave2_synthesis_real.py::test_known_invocation_problem_blocks_wave2_with_a_terminal_incident",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("WFO-001", "WFO-002"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "workflow-outcome-targeted-evidence-known-invocation",
        "tests/graph/test_targeted_evidence_real.py::test_targeted_known_invocation_problem_reaches_worker_controller",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("WFO-001", "WFO-002", "NAC-007", "TEL-005", "EVH-016"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "workflow-outcome-cli-topic-planning-projection",
        "tests/integration/test_demo_real.py::test_cli_renders_topic_planning_timeout_with_only_its_legal_new_start",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("REC-006", "WFO-001"),
    ),
    _correctness_claim(
        "workflow-outcome-cli-controller-projection",
        "tests/integration/test_demo_real.py::test_cli_renders_controller_provider_diagnosis_without_turning_inspection_into_recovery",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("REC-006", "WFO-001"),
    ),
    _correctness_claim(
        "workflow-outcome-tui-controller-projection",
        "tests/integration/test_demo_tui.py::test_tui_renders_controller_provider_diagnosis_without_a_fabricated_fresh_start",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("RED-004", "WFO-001"),
    ),
    _correctness_claim(
        "workflow-outcome-inventory-conformance",
        "tests/contract/test_workflow_node_inventory.py::test_every_discovered_owner_has_success_and_failure_outcome_evidence",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("WFO-002",),
    ),
    TestEvidenceClaim(
        claim_id="workflow-insufficient-evidence-wave0",
        selector="tests/integration/test_adversarial_worker_path.py::test_low_quality_or_unavailable_sources_are_explicitly_degraded[insufficient-evidence]",
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=("EVH-001", "EVH-002", "EVH-008", "EVH-009"),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.RUNTIME_INTEGRATION,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
        scenario_case_id="insufficient-evidence",
    ),
    TestEvidenceClaim(
        claim_id="workflow-prompt-injection-wave0",
        selector="tests/integration/test_adversarial_worker_path.py::test_authority_forging_source_text_cannot_control_ledger_or_gate[prompt-injection]",
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=("EVH-001", "EVH-004", "EVH-008", "EVH-009"),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.RUNTIME_INTEGRATION,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
        scenario_case_id="prompt-injection",
    ),
    TestEvidenceClaim(
        claim_id="workflow-malformed-output-wave2",
        selector="tests/integration/test_zero_tool_node_conformance.py::test_wave2_malformed_output_consumes_repair_and_leaves_no_partial_authority[malformed-output]",
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=("EVH-001", "EVH-008", "EVH-009"),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.NODE_INTERFACE,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
        scenario_case_id="malformed-output",
    ),
    TestEvidenceClaim(
        claim_id="workflow-tool-unavailable-timeout-bridge",
        selector="tests/eval/test_fault_injection.py::test_tool_unavailable_timeout_bridge_fails_closed[tool-unavailable-timeout]",
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=("EVH-001", "EVH-003", "EVH-009"),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.RUNTIME_INTEGRATION,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
        scenario_case_id="tool-unavailable-timeout",
    ),
    TestEvidenceClaim(
        claim_id="workflow-budget-exhaustion-bridge",
        selector="tests/unit/test_node_agent_bridge.py::test_real_bridge_enforces_exact_model_tool_budget_without_publication[budget-exhaustion]",
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=("EVH-001", "EVH-003", "EVH-009"),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.RUNTIME_INTEGRATION,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
        scenario_case_id="budget-exhaustion",
    ),
    TestEvidenceClaim(
        claim_id="workflow-partial-worker-submit-gate",
        selector="tests/integration/test_wave0_work_units.py::test_partial_worker_success_projects_distinct_gate_outcomes_from_authoritative_state[partial-worker-success]",
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=("EVH-001", "EVH-003", "EVH-008", "EVH-009"),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.RUNTIME_INTEGRATION,
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
        scenario_case_id="partial-worker-success",
    ),
    TestEvidenceClaim(
        claim_id="bundle-lifecycle-control-restart",
        selector=(
            "tests/integration/test_hitl1_lifecycle.py::"
            "test_bundle_lifecycle_state_survives_restart_without_external_checkpoint_control["
            "bundle-lifecycle-control]"
        ),
        expected_selection=FocusedSelection.INTEGRATION,
        requirement_ids=("EVH-001", "EVH-003", "EVH-025", "DRH-002", "DRH-008"),
        asset_class=AssetClass.CODE_CORRECTNESS,
        seam=StableSeam.LIFECYCLE_MIXED_GRAPH,
        authenticity=None,
        scenario_case_id="bundle-lifecycle-control",
    ),
    TestEvidenceClaim(
        claim_id="store-prior-authority-fault-matrix",
        selector="tests/unit/test_work_unit_store.py::test_prior_authority_survives_atomic_publication_fault_matrix[sandbox-filesystem-failure]",
        expected_selection=FocusedSelection.FAST,
        requirement_ids=("EVH-001", "EVH-003"),
        asset_class=AssetClass.CODE_CORRECTNESS,
        seam=StableSeam.RUNTIME_INTEGRATION,
        authenticity=None,
        scenario_case_id="sandbox-filesystem-failure",
    ),
    _correctness_claim(
        "live-discovery-workspace-cleanup",
        "tests/unit/test_work_unit_storage.py::test_runtime_verifier_cleanup_is_idempotent_with_real_local_sandbox",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("LIVE-20260717-01",),
    ),
    _correctness_claim(
        "live-discovery-model-construction",
        "tests/unit/test_live_evaluation.py::test_live_model_config_constructs_with_one_retry_authority",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("LIVE-20260717-02",),
    ),
    _correctness_claim(
        "live-discovery-canary-precondition",
        "tests/unit/test_live_evaluation.py::test_live_canary_setup_payloads_satisfy_real_node_parsers",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("LIVE-20260717-03",),
    ),
    _correctness_claim(
        "live-discovery-wave0-prompt-contract",
        "tests/graph/test_wave0_worker.py::test_build_wave0_worker_prompt_carries_topic_constraints",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("LIVE-20260717-04",),
    ),
    _correctness_claim(
        "live-discovery-tool-required",
        "tests/unit/test_node_agent_bridge.py::test_request_requiring_tool_execution_rejects_direct_model_answer",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("LIVE-20260717-06",),
    ),
    _correctness_claim(
        "release-discovery-final-publication",
        (
            "tests/unit/test_final_delivery_real.py::TestRealFinalDelivery::"
            "test_publication_replay_is_idempotent_and_conflicting_content_fails_closed"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-01",),
    ),
    _correctness_claim(
        "release-discovery-profile-budget",
        "tests/graph/test_topic_planning_prompts.py::test_very_quick_overview_limits_plan_to_one_topic",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-02",),
    ),
    _correctness_claim(
        "release-discovery-wave2-structured-repair",
        "tests/graph/test_wave2_synthesis_real.py::test_real_synthesis_repairs_malformed_output_once_without_tools",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-08",),
    ),
    _correctness_claim(
        "release-discovery-topic-bound",
        "tests/graph/test_topic_planning_node.py::test_minimal_quick_profile_repairs_multi_topic_plan_to_exactly_one",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-10",),
    ),
    _correctness_claim(
        "release-discovery-synthesis-semantic-floor",
        "tests/graph/test_wave2_synthesis_real.py::test_real_synthesis_rejects_empty_repair_when_accepted_evidence_exists",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-13",),
    ),
    _correctness_claim(
        "release-discovery-readiness-provenance",
        "tests/unit/test_readiness_real.py::TestRealReadiness::test_canonical_ledger_hash_passes_provenance",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-14",),
    ),
    _correctness_claim(
        "release-discovery-visible-retry-trace",
        "tests/unit/test_release_control_plane.py::test_release_trace_accepts_consecutive_visible_internal_retries",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-15",),
    ),
    _correctness_claim(
        "release-discovery-preflight-retention",
        "tests/unit/test_release_control_plane.py::test_release_preflight_remains_available_without_an_execution_target",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-16",),
    ),
    _correctness_claim(
        "release-discovery-redacted-schema-diagnostics",
        "tests/unit/test_live_evaluation.py::test_live_usage_tracker_reports_synthesis_schema_errors_without_values",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-17",),
    ),
    _correctness_claim(
        "shape-wave0-url-canonicalization",
        "tests/graph/test_wave0_provider_shapes.py::test_wave0_provider_shape[shape-wave0-url-canonicalization]",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-03",),
    ),
    _correctness_claim(
        "shape-wave0-fetch-status-alias",
        "tests/graph/test_wave0_provider_shapes.py::test_wave0_provider_shape[shape-wave0-fetch-status-alias]",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-04",),
    ),
    _correctness_claim(
        "shape-wave0-limitations-list",
        "tests/graph/test_wave0_provider_shapes.py::test_wave0_provider_shape[shape-wave0-limitations-list]",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-05",),
    ),
    _correctness_claim(
        "shape-wave0-partial-source-degradation",
        "tests/graph/test_wave0_provider_shapes.py::test_wave0_provider_shape[shape-wave0-partial-source-degradation]",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-12",),
    ),
    _correctness_claim(
        "shape-wave0-duplicate-source-fail-closed",
        "tests/graph/test_wave0_provider_shapes.py::test_wave0_provider_shape[shape-wave0-duplicate-source-fail-closed]",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-12",),
    ),
    _correctness_claim(
        "shape-wave1-provider-identifiers",
        "tests/unit/test_wave1_provider_shapes.py::test_wave1_provider_shape[shape-wave1-provider-identifiers]",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-07",),
    ),
    _correctness_claim(
        "shape-wave1-source-id-ref-rewrites",
        "tests/unit/test_wave1_provider_shapes.py::test_wave1_provider_shape[shape-wave1-source-id-ref-rewrites]",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-18",),
    ),
    _correctness_claim(
        "shape-wave1-source-order",
        "tests/integration/test_wave1_work_units.py::test_real_wave1_canonicalizes_provider_source_order_before_candidate_validation[shape-wave1-source-order]",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-21",),
    ),
    *(
        _correctness_claim(
            case_id,
            f"tests/graph/test_wave2_provider_shapes.py::test_wave2_provider_shape[{case_id}]",
            StableSeam.NODE_INTERFACE,
            requirement_ids=("EVH-006", "EVH-010"),
            discovery_ids=(discovery_id,),
        )
        for case_id, discovery_id in (
            ("shape-wave2-provider-field-aliases", "RELEASE-20260717-09"),
            ("shape-wave2-gap-priority-alias", "RELEASE-20260717-11"),
            ("shape-wave2-description-string-gaps", "RELEASE-20260717-19"),
            ("shape-wave2-sparse-findings", "RELEASE-20260717-20"),
            ("shape-wave2-relation-endpoints", "RELEASE-20260717-22"),
            ("shape-wave2-singular-affected-topic", "RELEASE-20260717-23"),
            ("shape-wave2-alternate-relation", "RELEASE-20260717-24"),
            ("shape-wave2-missing-gap-identity", "RELEASE-20260717-25"),
        )
    ),
    _correctness_claim(
        "shape-wave2-evidence-alias-binding",
        "tests/graph/test_wave2_synthesis_real.py::test_real_synthesis_maps_source_aliases_to_accepted_record_refs[shape-wave2-evidence-alias-binding]",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-010"),
        discovery_ids=("RELEASE-20260717-20",),
    ),
    TestEvidenceClaim(
        claim_id="live-wave0-provider-tool-selection",
        selector="tests/live/test_canaries.py::test_live_prefix_canary[live-one-topic-wave0]",
        expected_selection=FocusedSelection.LIVE,
        requirement_ids=("EVH-005", "EVH-010"),
        asset_class=AssetClass.LIVE_BEHAVIORAL_EVALUATION,
        seam=StableSeam.LIFECYCLE_MIXED_GRAPH,
        authenticity=AuthenticityLevel.LIVE_REAL_DEPENDENCIES,
        discovery_ids=("LIVE-20260717-05",),
    ),
    TestEvidenceClaim(
        claim_id="live-wave1-focused-provider",
        selector="tests/live/test_canaries.py::test_live_prefix_canary[live-one-topic-wave1]",
        expected_selection=FocusedSelection.LIVE,
        requirement_ids=("EVH-005", "EVH-009"),
        asset_class=AssetClass.LIVE_BEHAVIORAL_EVALUATION,
        seam=StableSeam.RUNTIME_INTEGRATION,
        authenticity=AuthenticityLevel.LIVE_REAL_DEPENDENCIES,
    ),
    TestEvidenceClaim(
        claim_id="live-wave2-focused-provider",
        selector="tests/live/test_canaries.py::test_live_prefix_canary[live-wave2-synthesis]",
        expected_selection=FocusedSelection.LIVE,
        requirement_ids=("EVH-005", "EVH-009"),
        asset_class=AssetClass.LIVE_BEHAVIORAL_EVALUATION,
        seam=StableSeam.RUNTIME_INTEGRATION,
        authenticity=AuthenticityLevel.LIVE_REAL_DEPENDENCIES,
    ),
    TestEvidenceClaim(
        claim_id="live-targeted-focused-provider",
        selector="tests/live/test_canaries.py::test_live_prefix_canary[live-one-gap-targeted-evidence]",
        expected_selection=FocusedSelection.LIVE,
        requirement_ids=("EVH-005", "EVH-009"),
        asset_class=AssetClass.LIVE_BEHAVIORAL_EVALUATION,
        seam=StableSeam.RUNTIME_INTEGRATION,
        authenticity=AuthenticityLevel.LIVE_REAL_DEPENDENCIES,
    ),
    TestEvidenceClaim(
        claim_id="live-gateway-forwarding-proof",
        selector="tests/live/test_gateway_forwarding_proof.py::test_gateway_forwarding_proof",
        expected_selection=FocusedSelection.LIVE,
        requirement_ids=("GOO-002",),
        asset_class=AssetClass.LIVE_BEHAVIORAL_EVALUATION,
        seam=StableSeam.RUNTIME_INTEGRATION,
        authenticity=AuthenticityLevel.LIVE_REAL_DEPENDENCIES,
    ),
    *(
        TestEvidenceClaim(
            claim_id=f"cal-live-{case_id.removeprefix('calibrate-')}",
            selector=(
                "tests/live/test_intake_planning_live_calibration.py::"
                f"test_live_intake_and_planning_calibration[{case_id}]"
            ),
            expected_selection=FocusedSelection.LIVE,
            requirement_ids=requirement_ids,
            asset_class=AssetClass.LIVE_BEHAVIORAL_EVALUATION,
            seam=StableSeam.NODE_INTERFACE,
            authenticity=AuthenticityLevel.LIVE_REAL_DEPENDENCIES,
            scenario_case_id=case_id,
        )
        for case_id, requirement_ids in _INTAKE_PLANNING_CALIBRATION_CASES
    ),
    *(
        TestEvidenceClaim(
            claim_id=f"evidence-intake-live-{case_id.removeprefix('calibrate-evidence-intake-')}",
            selector=(
                f"tests/live/test_evidence_intake_live_calibration.py::test_live_evidence_intake_calibration[{case_id}]"
            ),
            expected_selection=FocusedSelection.LIVE,
            requirement_ids=requirement_ids,
            asset_class=AssetClass.LIVE_BEHAVIORAL_EVALUATION,
            seam=StableSeam.NODE_INTERFACE,
            authenticity=AuthenticityLevel.LIVE_REAL_DEPENDENCIES,
            scenario_case_id=case_id,
        )
        for case_id, requirement_ids in _EVIDENCE_INTAKE_CALIBRATION_CASES
    ),
    *(
        TestEvidenceClaim(
            claim_id=f"ej-live-{index:02d}",
            selector=(
                "tests/live/test_evidence_judgment_live_calibration.py::"
                f"test_live_evidence_judgment_calibration[{case_id}]"
            ),
            expected_selection=FocusedSelection.LIVE,
            requirement_ids=requirement_ids,
            asset_class=AssetClass.LIVE_BEHAVIORAL_EVALUATION,
            seam=StableSeam.NODE_INTERFACE,
            authenticity=AuthenticityLevel.LIVE_REAL_DEPENDENCIES,
            scenario_case_id=case_id,
        )
        for index, (case_id, requirement_ids) in enumerate(_EVIDENCE_JUDGMENT_CALIBRATION_CASES, start=1)
    ),
    *(
        TestEvidenceClaim(
            claim_id=f"final-composition-live-{risk}",
            selector=(
                "tests/live/test_final_composition_live_calibration.py::"
                f"test_live_final_composition_calibration[{case_id}]"
            ),
            expected_selection=FocusedSelection.LIVE,
            requirement_ids=("EVH-022", "FID-001", "FID-003", "NAC-009", "NOA-013"),
            asset_class=AssetClass.LIVE_BEHAVIORAL_EVALUATION,
            seam=StableSeam.NODE_INTERFACE,
            authenticity=AuthenticityLevel.LIVE_REAL_DEPENDENCIES,
            scenario_case_id=case_id,
        )
        for risk, case_id in (
            ("normal", "calibrate-final-composition-normal"),
            ("highest-risk", "calibrate-final-composition-highest-risk"),
        )
    ),
    _correctness_claim(
        "live-report-archive-contract",
        "tests/unit/test_live_evaluation.py::test_live_report_archive_scan_requires_nonempty_schema_valid_reports",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("EVH-005", "EVH-010"),
    ),
    _correctness_claim(
        "release-model-led-smoke-scenario",
        "tests/unit/test_release_control_plane.py::test_release_scenario_owns_the_model_led_chinese_confirmation_transcript",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("EVH-024",),
    ),
    _correctness_claim(
        "release-citation-source-containment",
        (
            "tests/unit/test_release_control_plane.py::"
            "test_release_citation_evidence_fails_closed_for_an_accepted_out_of_set_final_source"
        ),
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("EVH-024",),
    ),
    _correctness_claim(
        "release-model-led-smoke-invariants",
        "tests/unit/test_release_control_plane.py::test_release_runner_reports_the_complete_model_led_smoke_evidence",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("EVH-024",),
    ),
    _correctness_claim(
        "release-bundle-state-and-contained-artifact-observation",
        (
            "tests/unit/test_release_control_plane.py::"
            "test_release_bundle_adapter_reauthorizes_the_public_id_before_observing_artifacts"
        ),
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("EVH-024",),
    ),
    _correctness_claim(
        "release-bundle-loss-no-store-fallback",
        (
            "tests/unit/test_release_control_plane.py::"
            "test_release_bundle_adapter_fails_on_bundle_loss_before_any_store_observation"
        ),
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("EVH-024",),
    ),
    _correctness_claim(
        "release-v2-smoke-attestation",
        (
            "tests/contract/test_release_attestation.py::"
            "test_synthetic_v2_attestation_is_redacted_and_matches_a_complete_smoke_report"
        ),
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("EVH-024",),
    ),
    _correctness_claim(
        "real-recipe-compiles",
        "tests/unit/test_research_runtime_capabilities.py::test_all_real_recipe_compiles",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("EVH-006", "EVH-008"),
    ),
    _correctness_claim(
        "non-interactive-policy-forwarding",
        "tests/unit/test_non_interactive.py::test_tool_allows_declared_non_interactive_policy_for_start",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("EVH-006", "EVH-008"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "non-interactive-policy-closed-admission",
        (
            "tests/unit/test_non_interactive.py::"
            "test_tool_rejects_missing_or_incomplete_non_interactive_policy_before_bundle_publication"
        ),
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("RUO-001",),
    ),
    _correctness_claim(
        "non-interactive-retired-marker-denial",
        ("tests/unit/test_non_interactive.py::test_tool_rejects_the_retired_marker_before_sandbox_or_graph_selection"),
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("RUI-006", "RUO-001"),
    ),
    TestEvidenceClaim(
        claim_id="non-interactive-checkpoint-handoff",
        selector=(
            "tests/blocking_io/test_research_runtime.py::"
            "test_composed_start_persists_policy_once_in_the_selected_bundle_checkpoint"
        ),
        expected_selection=FocusedSelection.INTEGRATION,
        requirement_ids=("RUI-006", "RUO-001"),
        asset_class=AssetClass.CODE_CORRECTNESS,
        seam=StableSeam.LIFECYCLE_MIXED_GRAPH,
    ),
    _correctness_claim(
        "model-resolver-empty-config",
        "tests/unit/test_node_agent_bridge.py::test_default_model_resolver_rejects_empty_model_config",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-006", "EVH-008"),
    ),
    _correctness_claim(
        "graph-host-legacy-checkpointer-refusal",
        ("tests/unit/test_graph_host.py::test_legacy_checkpointer_is_refused_before_action_saver_factory"),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RUI-005",),
    ),
    _correctness_claim(
        "node-agent-retired-endpoint-alias-denial",
        (
            "tests/unit/test_node_agent_bridge.py::"
            "test_retired_selected_endpoint_aliases_are_omitted_even_when_they_match_base_url[openai-api-base-only]"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("NOA-005",),
    ),
    _correctness_claim(
        "demo-adapter-unique-sandbox",
        "tests/unit/test_demo_core.py::test_demo_adapter_provides_legal_unique_sandbox",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-006", "EVH-008"),
    ),
    _correctness_claim(
        "demo-real-prerequisites",
        (
            "tests/unit/test_demo_core.py::"
            "test_real_demo_prerequisites_reject_missing_and_blank_values_before_adapter_construction"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("DPL-001", "DPL-004"),
    ),
    _correctness_claim(
        "demo-real-question-onboarding",
        "tests/integration/test_demo_real.py::test_cli_collects_safe_question_only_after_preflight",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("REC-001", "REC-002", "REC-003"),
    ),
    _correctness_claim(
        "demo-real-returned-suspension-loop",
        "tests/integration/test_demo_real.py::test_cli_follows_only_shared_awaiting_updates_and_preserves_graph_owned_choices",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("REC-001", "REC-002", "REC-003", "RER-001"),
    ),
    _correctness_claim(
        "demo-real-scripted-terminal",
        "tests/integration/test_demo_real.py::test_scripted_cli_is_stdin_free_and_preserves_explicit_question",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("REC-001", "REC-002", "REC-003"),
    ),
    _correctness_claim(
        "demo-real-terminal-redaction",
        "tests/integration/test_demo_run_update_adapters.py::test_shared_failure_never_leaks_raw_exception_into_either_adapter",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("REC-002", "REC-003", "RER-003", "RER-009", "RED-004"),
    ),
    _correctness_claim(
        "demo-real-typed-terminal-projection",
        "tests/integration/test_demo_real.py::test_cli_preserves_typed_terminal_category_without_leaking_source_text[structured-output-terminal]",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("REC-002", "REC-006"),
    ),
    _correctness_claim(
        "demo-autonomous-hitl2",
        "tests/integration/test_demo_cli.py::test_interactive_demo_completes_after_scope_without_a_hitl2_choice",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("ALR-001", "DPL-001", "FCO-001"),
        authenticity=AuthenticityLevel.FAKE_GRAPH,
    ),
    _correctness_claim(
        "hitl2-autonomous-policy",
        "tests/unit/test_hitl2_brief.py::TestHitl2Policy::test_validated_state_recommends_graph_owned_continuation",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("ALR-001", "HIT-001"),
    ),
    _correctness_claim(
        "demo-readme-paste-safe-zsh",
        "tests/contract/test_demo_commands.py::test_readme_setup_commands_are_paste_safe_in_interactive_zsh",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("FCO-001",),
    ),
    _correctness_claim(
        "readme-entry-surfaces",
        "tests/contract/test_demo_commands.py::test_readme_entry_surfaces_route_to_current_detail_owners",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("DRC-006",),
    ),
    _correctness_claim(
        "demo-adapter-invalid-choice-feedback",
        "tests/integration/test_demo_run_update_adapters.py::test_standalone_adapters_render_safe_invalid_choice_feedback_without_wire_data",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("DPL-002", "RER-003"),
    ),
    _correctness_claim(
        "demo-real-local-cancellation",
        "tests/integration/test_demo_real.py::test_cli_propagates_local_cancellation_without_graph_cancel",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("REC-002",),
    ),
    _correctness_claim(
        "run-experience-bootstrap-pending-input",
        "tests/contract/test_run_experience_contract.py::test_start_projects_one_bundle_local_pending_request",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("REG-012", "RER-001", "RER-002", "RUI-007"),
        discovery_ids=("LIVE-20260720-01",),
    ),
    _correctness_claim(
        "run-experience-scripted-policy-projection",
        (
            "tests/contract/test_run_experience_contract.py::"
            "test_scripted_start_projects_policy_once_and_later_actions_do_not_reinject_it"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RER-001",),
    ),
    _correctness_claim(
        "run-experience-auto-profile-trace-observation",
        (
            "tests/contract/test_run_experience_contract.py::"
            "test_policy_trace_marker_is_accepted_as_a_safe_observation[hitl1_auto_profile]"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RER-001",),
    ),
    _correctness_claim(
        "run-experience-auto-proceed-trace-observation",
        (
            "tests/contract/test_run_experience_contract.py::"
            "test_policy_trace_marker_is_accepted_as_a_safe_observation[hitl2_auto_proceed]"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RER-001",),
    ),
    _correctness_claim(
        "run-experience-status-pending-input",
        "tests/contract/test_run_experience_contract.py::test_resume_uses_the_selected_bundle_id_and_returns_the_same_result_contract",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RER-001", "RER-002", "RUI-007"),
    ),
    _correctness_claim(
        "run-experience-semantic-prompts",
        "tests/contract/test_run_experience_contract.py::test_observation_is_published_only_from_a_shared_available_result",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RER-001", "RER-004"),
    ),
    _correctness_claim(
        "run-experience-invalid-choice-recovery",
        "tests/contract/test_run_experience_contract.py::test_unavailable_result_clears_the_local_handle_and_offers_only_a_fresh_start",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RER-003",),
    ),
    _correctness_claim(
        "run-experience-invalid-choice-record-denial",
        "tests/contract/test_run_experience_contract.py::test_malformed_result_fails_closed_without_creating_a_control_projection",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RER-003",),
    ),
    _correctness_claim(
        "run-experience-returned-only-liveness",
        "tests/integration/test_demo_run_update_adapters.py::test_standalone_adapters_render_only_observed_returned_only_wait_facts",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RER-004", "DPL-006"),
    ),
    _correctness_claim(
        "run-experience-safe-failure-projection",
        "tests/contract/test_run_experience_failures.py::test_storage_failure_projects_a_closed_failure_category_without_a_second_lifecycle_source",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RER-003", "NOA-007"),
    ),
    _correctness_claim(
        "run-experience-bounded-diagnostic-journal",
        "tests/contract/test_run_experience_failures.py::test_runtime_exception_is_redacted_as_a_safe_internal_failure",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RER-003", "REG-013"),
    ),
    _correctness_claim(
        "run-experience-shared-adapter-prompt",
        "tests/integration/test_demo_run_update_adapters.py::test_standalone_adapters_render_shared_run_updates_without_lifecycle_wire[hitl1]",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("RER-001", "REC-003", "RED-003"),
    ),
    TestEvidenceClaim(
        claim_id="workflow-real-bootstrap-hitl1-pending-projection",
        selector="tests/integration/test_hitl1_lifecycle.py::test_bundle_local_pending_hitl_survives_a_fresh_lifecycle_instance",
        expected_selection=FocusedSelection.INTEGRATION,
        requirement_ids=("HIN-006", "RER-002", "RER-005", "RUI-007"),
        asset_class=AssetClass.CODE_CORRECTNESS,
        seam=StableSeam.LIFECYCLE_MIXED_GRAPH,
        authenticity=None,
        discovery_ids=("LIVE-20260720-01",),
    ),
    _correctness_claim(
        "hitl1-typed-failure-incident",
        "tests/graph/test_hitl1_node.py::test_typed_bridge_problem_survives_hitl1_blocked_route_without_raw_detail",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("HIN-006", "NOA-007", "REG-013", "WFO-001", "WFO-002"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "run-event-journal-node-agent-bridge-failures",
        "tests/unit/test_node_agent_bridge.py::test_bridge_projects_closed_safe_problem_for_each_runtime_source[model-configuration.model_missing-agent_invocation-None]",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("NOA-007", "RER-003", "WFO-002"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "node-prompt-bridge-conformance",
        "tests/unit/test_node_agent_bridge.py::test_canonical_catalog_case_bridge_prompt_matches_shared_renderer",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("NOA-010", "NPC-001"),
    ),
    _correctness_claim(
        "node-prompt-catalog-inventory",
        "tests/graph/test_prompt_catalog.py::test_catalog_registers_every_direct_node_prompt_builder",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NPC-002",),
    ),
    _correctness_claim(
        "node-prompt-catalog-source-rendering",
        "tests/graph/test_prompt_dump.py::test_source_rendering_remains_available_without_a_local_review_workspace",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NPC-002",),
    ),
    _correctness_claim(
        "cognitive-node-reader-interface",
        "tests/contract/test_node_workflow_reader_interface.py::test_live_reader_inventory_passes",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("CNI-001", "CNI-002", "CNI-003", "CNI-004", "CNI-005"),
    ),
    _correctness_claim(
        "deferred-activation-dossiers",
        "tests/contract/test_deferred_activation_dossiers.py::test_live_dossiers_are_the_exact_non_runtime_activation_denominator",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("CNI-004",),
    ),
    _correctness_claim(
        "run-experience-canonical-architecture",
        "tests/contract/test_live_architecture_contract.py::test_live_repository_satisfies_architecture_contract",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("PRS-005", "PRS-012", "PRS-013", "PRS-014", "PRS-016", "PRS-018", "DER-002"),
    ),
    _correctness_claim(
        "prompt-review-workspace-structure",
        "tests/contract/test_live_architecture_contract.py::test_prompt_review_workspace_is_optional_and_ignored",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("PRS-006", "PRS-011"),
    ),
    _correctness_claim(
        "fixture-production-wheel-isolation",
        "tests/contract/test_live_architecture_contract.py::test_production_wheel_excludes_fixture_package",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("FSI-001", "PRS-001"),
    ),
    _correctness_claim(
        "demo-adapter-close-idempotent",
        "tests/unit/test_demo_core.py::test_demo_adapter_close_is_idempotent",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("DPL-001",),
    ),
    _correctness_claim(
        "demo-local-tavily-tools",
        "tests/unit/test_demo_core.py::test_demo_tavily_tools_are_local_bounded_and_closed",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("DPL-001",),
    ),
    _correctness_claim(
        "demo-tavily-fetch-provenance",
        "tests/unit/test_demo_core.py::test_demo_tavily_fetch_requires_same_run_search",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("DPL-001", "DPL-009"),
    ),
    _correctness_claim(
        "demo-tavily-retry-classification",
        "tests/unit/test_demo_core.py::test_demo_tavily_retry_classification_is_limited_to_transient_read_failures",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("DPL-009",),
    ),
    _correctness_claim(
        "demo-tavily-upper-bound-recovery",
        "tests/unit/test_demo_core.py::test_demo_tavily_search_retries_each_allowed_direct_failure_before_succeeding[http-599]",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("DPL-009",),
    ),
    _correctness_claim(
        "demo-tavily-bounded-fetch-retry",
        "tests/unit/test_demo_core.py::test_demo_tavily_fetch_exhausts_three_transient_read_attempts",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("DPL-009",),
    ),
    _correctness_claim(
        "demo-tavily-backoff-cancellation",
        "tests/unit/test_demo_core.py::test_demo_tavily_cancellation_during_backoff_does_not_start_another_attempt",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("DPL-009",),
    ),
    _correctness_claim(
        "demo-tavily-fetch-only-denied",
        "tests/unit/test_demo_core.py::test_demo_tavily_fetch_only_policy_fails_closed",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("DPL-001",),
    ),
    _correctness_claim(
        "demo-tui-question-onboarding",
        "tests/integration/test_demo_tui.py::test_tui_fixture_route_completes_through_shared_experience",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("RED-001", "RED-002", "RED-003"),
    ),
    _correctness_claim(
        "demo-tui-processing-truthfulness",
        "tests/integration/test_demo_tui.py::test_tui_working_state_shows_no_inferred_trace_progress",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("RED-001", "RER-004"),
    ),
    _correctness_claim(
        "demo-tui-unexpected-error-redaction",
        "tests/integration/test_demo_tui.py::test_tui_preflight_failure_shows_safe_fault_before_question",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("RED-004", "RER-003"),
    ),
    _correctness_claim(
        "demo-tui-cancel-worker",
        "tests/integration/test_demo_tui.py::test_tui_explicit_cancel_uses_shared_cancel_intent",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("RED-003", "RED-004"),
    ),
    _correctness_claim(
        "demo-tui-adapter-ownership",
        "tests/integration/test_demo_tui.py::test_tui_owns_and_closes_one_adapter",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("DPL-001", "RED-001"),
    ),
    _correctness_claim(
        "demo-command-dependency-boundaries",
        "tests/contract/test_demo_commands.py::test_demo_commands_keep_fixture_and_real_dependency_boundaries",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("DPL-005", "DPL-008", "RED-002"),
    ),
    _correctness_claim(
        "local-entry-environment-preflight",
        "tests/scenarios_periodic/test_local_entry_environment.py::test_missing_or_incomplete_entry_environment_stops_before_an_adapter",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("DPL-006",),
    ),
    _correctness_claim(
        "local-entry-environment-prepared-process",
        "tests/scenarios_periodic/test_local_entry_environment.py::test_prepared_entries_preserve_dependency_state_and_keep_launcher_credential_bounded",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("DPL-005", "DPL-006", "LCP-002"),
    ),
    _correctness_claim(
        "demo-explicit-recipe-factories",
        "tests/unit/test_demo_core.py::test_demo_recipe_factories_do_not_expose_a_mode_selector",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("DPL-003",),
    ),
    _correctness_claim(
        "fixture-catalog-explicit-composition",
        "tests/graph/test_topology_and_implementation.py::test_explicit_full_fixture_and_paired_mixed_compositions_preserve_topology_shape",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("FSI-002", "REG-019"),
    ),
    _correctness_claim(
        "public-all-real-host-default",
        "tests/integration/test_research_lifecycle_tool.py::test_public_bundle_lifecycle_completes_after_one_correlated_resume",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("RUI-004", "RUI-006", "REG-019"),
    ),
    _correctness_claim(
        "retired-fixture-binding-rejection",
        "tests/integration/test_session_lifecycle_binding.py::test_contained_journal_does_not_reauthorize_a_lost_bundle",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("REJ-004", "RUI-003"),
    ),
    _correctness_claim(
        "public-skill-all-real-entry",
        "tests/contract/test_public_skill.py::test_committed_skill_is_one_focused_cognitive_controller_workflow",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("DEC-003", "RUI-006"),
    ),
    TestEvidenceClaim(
        claim_id="public-controller-scripted-loader-handoff",
        selector=(
            "tests/integration/test_public_controller_handoff.py::"
            "test_ordinary_loaded_controller_hands_a_new_request_to_the_real_lifecycle[direct]"
        ),
        expected_selection=FocusedSelection.WORKFLOW,
        requirement_ids=("DEC-003", "RUI-006"),
        asset_class=AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
        seam=StableSeam.PUBLIC_ENTRY,
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
    ),
    _correctness_claim(
        "cognitive-evaluation-direction-control-registry",
        "tests/eval/test_cognitive_evaluation_suite.py::"
        "test_source_controlled_v1_registry_exposes_only_the_declared_cases",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("CES-001",),
    ),
    _correctness_claim(
        "agent-soul-identity-honesty",
        "tests/contract/test_public_skill.py::test_agent_soul_is_stable_identity_and_honesty_not_a_second_action_workflow",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("DEC-004",),
    ),
    _correctness_claim(
        "public-lifecycle-wiring-replay",
        "tests/integration/test_public_entry_replay.py::test_prewritten_lifecycle_calls_exercise_tool_wiring_only",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("RUI-006",),
    ),
    _correctness_claim(
        "store-verified-temp-workspace",
        "tests/unit/test_work_unit_store.py::test_store_factory_accepts_verified_temp_workspace",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-006", "EVH-008"),
    ),
    _correctness_claim(
        "tool-resolver-missing-allowed-tools",
        "tests/unit/test_node_agent_bridge.py::test_default_tools_resolver_rejects_missing_allowed_tools",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-006", "EVH-008"),
    ),
    _correctness_claim(
        "worker-policy-tool-specs",
        "tests/unit/test_research_runtime_capabilities.py::test_worker_policies_specify_every_allowed_tool",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-008"),
    ),
    _correctness_claim(
        "distinct-worker-policy-routing",
        "tests/unit/test_research_runtime_capabilities.py::test_all_real_context_routes_distinct_worker_policies",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("EVH-006", "EVH-008"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "budget-large-history-admission",
        "tests/unit/test_budget_middleware.py::test_large_tool_result_history_uses_bounded_admission",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-008"),
    ),
    _correctness_claim(
        "budget-max-model-calls",
        "tests/unit/test_budget_middleware.py::test_max_model_calls_refused_before_handler",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-008"),
    ),
    _correctness_claim(
        "budget-parallel-tool-calls",
        "tests/unit/test_budget_middleware.py::test_parallel_tool_call_limit",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-008"),
    ),
    _correctness_claim(
        "topic-planning-invalid-output",
        "tests/graph/test_topic_planning_node.py::test_repeated_invalid_plan_exhausts_without_topic_state",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-006", "EVH-008", "NAC-006", "TOP-006", "EVH-015"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "gate-fatigue-reset",
        "tests/engine/test_gate_kernel.py::TestFatigue::test_successful_evaluation_resets_prior_failure_fatigue",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("EVH-006", "EVH-008"),
    ),
    _correctness_claim(
        "bootstrap-marker-needs-input",
        "tests/graph/test_bootstrap_node.py::TestBuildRealRoutesOnBinding::test_bound_marker_routes_needs_input_with_no_model_call",
        StableSeam.NODE_INTERFACE,
    ),
    _correctness_claim(
        "bootstrap-divergent-read-back",
        "tests/graph/test_bootstrap_node.py::TestBuildRealRoutesOnBinding::test_divergent_read_back_fails_closed_terminal",
        StableSeam.NODE_INTERFACE,
    ),
    _correctness_claim(
        "hitl1-complete-response",
        "tests/graph/test_hitl1_node.py::test_natural_confirmation_writes_current_proposal_and_routes_accepted",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-008", "HIN-009", "HIN-011", "HIN-014", "HIC-004"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "node-agent-sdk-timeout-origin",
        "tests/unit/test_node_agent_bridge.py::test_admitted_hitl_timeout_wrappers_are_classified_before_connection_wrappers[openai]",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("NOA-001",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "node-agent-transport-timeout-origin-absent",
        "tests/unit/test_node_agent_bridge.py::test_admitted_hitl_timeout_wrappers_are_classified_before_connection_wrappers[httpx]",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("NOA-001",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "node-agent-bridge-budget-timeout-origin",
        "tests/unit/test_node_agent_bridge.py::test_admitted_hitl_bridge_deadline_has_only_bridge_timeout_origin",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("NOA-001",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "workflow-timeout-origin-identity",
        "tests/domain/test_workflow_outcomes.py::test_provider_diagnostic_reference_keeps_v1_identity_without_origins_and_separates_roles",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("WFO-001",),
    ),
    _correctness_claim(
        "workflow-controller-timeout-origin-identity",
        "tests/domain/test_workflow_outcomes.py::test_controller_provider_diagnostic_reference_uses_the_shared_timeout_origin_identity",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("WFO-001",),
    ),
    _correctness_claim(
        "hitl1-timeout-origin-role-propagation",
        "tests/graph/test_hitl1_node.py::test_retry_timeout_origins_remain_in_their_trigger_and_final_roles",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("HIN-001",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "retained-bundle-exact-terminal-diagnostic",
        "tests/contract/test_run_experience_failures.py::test_admitted_terminal_diagnostic_has_no_external_support_fallback",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RER-013",),
    ),
    _correctness_claim(
        "bundle-loss-fresh-start-independence",
        "tests/integration/test_session_operations_lifecycle.py::test_deleted_bundle_is_unavailable_and_fresh_start_is_independent",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("DRH-006",),
    ),
    _correctness_claim(
        "standalone-inspection-command-projection",
        "tests/integration/test_demo_run_update_adapters.py::test_standalone_adapters_render_the_same_retained_observation",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("REC-005", "REC-006"),
    ),
    _correctness_claim(
        "standalone-inspection-observation-projection",
        "tests/integration/test_demo_sessions.py::test_inspect_renders_safe_contained_journal_facts",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("REJ-004",),
    ),
    _correctness_claim(
        "standalone-inspection-command-execution",
        "tests/integration/test_demo_sessions.py::test_inspect_command_reads_only_an_existing_selected_bundle",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RDO-001", "REC-005", "REC-006"),
    ),
    _correctness_claim(
        "standalone-inspection-command-documentation",
        "tests/contract/test_demo_commands.py::test_retained_observation_documentation_uses_the_canonical_inspection_command",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("REC-005", "REC-006"),
    ),
    _correctness_claim(
        "hitl1-run-agent-failure",
        "tests/graph/test_hitl1_node.py::test_run_agent_failure_exhausts_without_partial_state",
        StableSeam.NODE_INTERFACE,
    ),
    _correctness_claim(
        "hitl1-brief-parser-compatibility",
        "tests/graph/test_hitl1_prompts.py::test_initial_and_repair_brief_descriptors_remain_strict_parser_compatible",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("HIN-013",),
    ),
    _correctness_claim(
        "topic-planning-valid-plan",
        "tests/graph/test_topic_planning_node.py::test_valid_plan_routes_next_and_records_registry",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NAC-006", "TOP-006", "EVH-015"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "wave0-complete-lifecycle",
        (
            "tests/integration/test_wave0_work_units.py::"
            "test_real_wave0_artifacts_remain_bound_to_the_selected_run_bundle"
        ),
        StableSeam.RUNTIME_INTEGRATION,
    ),
    _correctness_claim(
        "wave0-all-workers-fail",
        "tests/integration/test_wave0_work_units.py::test_real_wave0_all_workers_fail_without_evidence_publication",
        StableSeam.RUNTIME_INTEGRATION,
    ),
    _correctness_claim(
        "wave1-worker-ledger-success",
        "tests/integration/test_wave1_work_units.py::test_real_wave1_crosses_worker_context_artifact_validator_and_ledger",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-006", "EVH-008", "EVH-010", "NAC-006", "WON-007", "EVH-015"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
        discovery_ids=("RELEASE-20260717-06",),
    ),
    _correctness_claim(
        "wave1-authoritative-wave0-baseline",
        "tests/integration/test_wave1_work_units.py::test_real_wave1_factory_derives_the_authoritative_wave0_baseline_before_dispatch",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("WON-001",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "wave1-review-gate-integrity",
        "tests/integration/test_wave1_work_units.py::test_real_wave1_review_gate_enforces_question_floor_and_review_integrity",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("WON-003", "WON-004"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "wave1-malformed-worker-output",
        "tests/integration/test_wave1_work_units.py::test_real_wave1_malformed_output_becomes_typed_worker_failure_without_ledger[shape-wave1-malformed-submit]",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-006", "EVH-008", "EVH-010"),
        discovery_ids=("RELEASE-20260717-18",),
    ),
    _correctness_claim(
        "wave2-runtime-method-injection-initial",
        (
            "tests/graph/test_cognitive_program_evidence.py::"
            "test_wave2_cognitive_program_keeps_method_in_the_rendered_capability[initial]"
        ),
        StableSeam.NODE_INTERFACE,
        requirement_ids=("WSN-008",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "wave2-runtime-method-injection-repair",
        (
            "tests/graph/test_cognitive_program_evidence.py::"
            "test_wave2_cognitive_program_keeps_method_in_the_rendered_capability[repair]"
        ),
        StableSeam.NODE_INTERFACE,
        requirement_ids=("WSN-008",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "wave2-forged-repair-nonpublication",
        "tests/graph/test_wave2_synthesis_real.py::test_real_synthesis_rejects_forged_repair_without_publishing",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("WSN-008",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "wave2-cognitive-program-live-rejected",
        (
            "tests/eval/test_cognitive_evaluation_suite.py::"
            "test_wave2_cognitive_program_selected_live_admission_rejects_before_runs_root_or_subject"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-029",),
        authenticity=AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
    ),
    _correctness_claim(
        "wave2-canonical-findings",
        "tests/graph/test_wave2_synthesis_real.py::test_real_synthesis_uses_node_context_and_materializes_canonical_findings",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NAC-003", "NAC-004", "EVH-012", "WSN-005", "EVH-016"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "wave2-malformed-output",
        "tests/graph/test_wave2_synthesis_real.py::test_real_synthesis_malformed_output_fails_without_artifact",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NAC-003", "NAC-004", "EVH-012", "WSN-005", "EVH-016"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "nac-targeted-worker-success",
        "tests/graph/test_targeted_evidence_real.py::test_targeted_valid_first_response_does_not_repair",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("NAC-007", "TEL-005", "EVH-016"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "nac-targeted-repair-success",
        "tests/graph/test_targeted_evidence_real.py::test_targeted_invalid_first_response_repairs_once_without_tools[prose]",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("NAC-007", "TEL-005", "EVH-016"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "nac-targeted-repair-risk",
        "tests/graph/test_targeted_evidence_real.py::test_targeted_repair_invocation_problem_reaches_worker_controller",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("NAC-007", "TEL-005", "EVH-016"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "nac-targeted-claim-verifier-success",
        "tests/graph/test_targeted_evidence_real.py::test_claim_verifier_materializes_only_assigned_references",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NAC-007", "TEL-005", "EVH-016"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "nac-targeted-claim-verifier-risk",
        "tests/graph/test_targeted_evidence_real.py::test_claim_verifier_rejects_unassigned_reference_without_artifact",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NAC-007", "TEL-005", "EVH-016"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "npc-evidence-evaluation-catalog",
        "tests/graph/test_node_agent_capability_cohort.py::test_cohort_branch_binding[targeted-evidence/worker]",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NPC-005",),
    ),
    _correctness_claim(
        "targeted-evidence-valid-artifact",
        "tests/graph/test_targeted_evidence_real.py::test_source_diagnostic_uses_node_context_and_materializes_validated_artifact",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NAC-007", "TEL-005", "EVH-016"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "targeted-evidence-malformed-output",
        "tests/graph/test_targeted_evidence_real.py::test_source_diagnostic_malformed_output_fails_without_artifact",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NAC-007", "TEL-005", "EVH-016"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "hitl2-proceed-route",
        "tests/unit/test_hitl2_real.py::TestRealHitl2Factory::test_validated_state_routes_proceed_without_a_human_response",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("ALR-001", "HIT-002"),
    ),
    _correctness_claim(
        "hitl1-checkpointed-auto-profile",
        ("tests/graph/test_hitl1_node.py::test_non_interactive_auto_profile_stays_outside_interactive_confirmation"),
        StableSeam.NODE_INTERFACE,
        requirement_ids=("RUO-002",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "hitl2-checkpointed-auto-proceed",
        (
            "tests/unit/test_hitl2_real.py::"
            "TestRealHitl2Factory::test_checkpointed_auto_proceed_overrides_recommendation_with_an_observation_marker"
        ),
        StableSeam.NODE_INTERFACE,
        requirement_ids=("RUO-002",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "hitl2-malformed-state-rejected",
        "tests/unit/test_hitl2_real.py::TestRealHitl2Factory::test_malformed_state_fails_closed_without_a_human_prompt[state0]",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("ALR-001", "ALR-002", "EVH-003", "EVH-008"),
    ),
    _correctness_claim(
        "hitl1-stale-request-rejected",
        "tests/graph/test_hitl1_node.py::test_response_mismatch_raises",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-003", "EVH-008", "HIN-002"),
    ),
    _correctness_claim(
        "rerun-full-scope-lifecycle",
        "tests/unit/test_rerun_real.py::TestRealRerunFactory::test_full_scope_full_lifecycle",
        StableSeam.NODE_INTERFACE,
    ),
    _correctness_claim(
        "rerun-generation-ceiling",
        "tests/unit/test_rerun_real.py::TestRealRerunFactory::test_generation_at_ceiling_exhausted",
        StableSeam.NODE_INTERFACE,
    ),
    _correctness_claim(
        "readiness-all-clear",
        "tests/unit/test_readiness_real.py::TestRealReadiness::test_all_clear_routes_pass_with_admitted_candidate",
        StableSeam.NODE_INTERFACE,
    ),
    _correctness_claim(
        "readiness-no-evidence",
        "tests/unit/test_readiness_real.py::TestRealReadiness::test_store_integrity_failure_is_structural_and_skips_model",
        StableSeam.NODE_INTERFACE,
    ),
    _correctness_claim(
        "readiness-autonomous-continuation",
        "tests/unit/test_readiness_real.py::TestRealReadiness::test_autonomous_hitl2_requires_no_consumed_request",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("REA-001", "REA-005"),
    ),
    _correctness_claim(
        "readiness-critic-conservative-failure",
        "tests/unit/test_readiness_real.py::TestRealReadiness::test_bridge_failure_projects_repair_without_all_ready",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("REA-002", "REA-004", "REA-006", "EVH-021"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "readiness-critic-rejects-unknown-ref",
        "tests/unit/test_readiness_real.py::TestRealReadiness::test_candidate_rejects_unknown_backing_ref",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("REA-002", "REA-006", "EVH-021"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "readiness-judgment-corpus",
        "tests/unit/test_evidence_judgment_calibration.py::test_evidence_judgment_corpus_has_two_labeled_cases_per_branch_with_declared_bounds",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("REA-002", "EVH-021"),
    ),
    _correctness_claim(
        "final-delivery-completed",
        "tests/unit/test_final_delivery_real.py::TestRealFinalDelivery::test_renders_only_plan_text_and_keeps_completion_gate_owned",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("FID-001", "FID-003", "FID-004"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "final-delivery-empty-evidence",
        "tests/unit/test_final_delivery_real.py::TestRealFinalDelivery::test_empty_accepted_evidence_never_publishes",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("FID-002", "FID-005"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "final-delivery-declared-dependencies",
        (
            "tests/unit/test_final_delivery_real.py::TestRealFinalDelivery::"
            "test_missing_declared_dependencies_fail_before_request_construction"
        ),
        StableSeam.NODE_INTERFACE,
        requirement_ids=("FID-005", "NAC-009"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "final-delivery-zero-tool-policy",
        ("tests/unit/test_research_runtime_capabilities.py::test_zero_tool_policies_remain_independently_bounded"),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("FID-005", "NOA-013"),
    ),
    _correctness_claim(
        "workflow-outcome-final-delivery-known-invocation",
        (
            "tests/unit/test_final_delivery_real.py::TestRealFinalDelivery::"
            "test_bridge_and_publisher_failures_take_one_attempt_without_a_pass_view"
        ),
        StableSeam.NODE_INTERFACE,
        requirement_ids=("FID-002", "FID-004", "EVH-022", "WFO-001", "WFO-002"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "lifecycle-consumed-resume-cancel",
        "tests/integration/test_research_lifecycle_tool.py::test_completed_resume_and_cancel_replay_the_terminal_bundle_projection",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("EVH-003", "EVH-008"),
    ),
    _correctness_claim(
        "bridge-wall-time-timeout",
        "tests/eval/test_fault_injection.py::test_wall_time_timeout_returns_typed_budget_exhausted_outcome",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-003", "EVH-008"),
    ),
    _correctness_claim(
        "store-atomic-publication-replay",
        "tests/unit/test_work_unit_store.py::test_atomic_publication_fault_boundaries_replay_from_last_parent_checkpoint[after_staging_fsync-False]",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-003", "EVH-008"),
    ),
    _correctness_claim(
        "store-conflicting-worker-result",
        "tests/integration/test_work_unit_submit_boundary.py::test_same_hash_replays_and_different_hash_conflicts_at_real_store_boundary",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-003", "EVH-008"),
    ),
    _correctness_claim(
        "provider-subprocess-restart",
        "tests/integration/test_provider_durability.py::test_file_sqlite_probe_survives_a_real_subprocess_restart",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-003", "EVH-008"),
    ),
    _correctness_claim(
        "run-bundle-operations-safe-domain-projections",
        "tests/contract/test_session_operations_contract.py::test_shared_lifecycle_result_has_no_legacy_authority_fields",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("RDO-001", "RDO-004"),
    ),
    _correctness_claim(
        "run-bundle-operations-trusted-resolver",
        "tests/unit/test_session_operation_resolver.py::test_workbench_uses_only_trusted_scope_and_bundle_local_state",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RDO-002", "RUI-002"),
    ),
    _correctness_claim(
        "run-bundle-operations-lifecycle",
        "tests/integration/test_session_operations_lifecycle.py::test_resume_revalidates_bundle_local_pending_request",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("RDO-003", "REG-004", "REG-014"),
    ),
    _correctness_claim(
        "run-bundle-retired-surface-revocation",
        "tests/unit/test_run_session_store.py::test_retired_run_session_store_has_no_compatibility_module",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("DRH-006", "PRS-006", "RUI-003"),
    ),
    _correctness_claim(
        "run-bundle-operations-cli-profile",
        "tests/integration/test_demo_sessions.py::test_demo_sessions_parser_exposes_only_a_bundle_target",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("REC-004", "RDO-001", "RDO-003", "RDO-004"),
    ),
    _correctness_claim(
        "run-bundle-operations-tui",
        "tests/integration/test_demo_tui.py::test_tui_renders_safe_provider_facts_without_recovery_invention",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("RED-005", "RDO-001", "RDO-004"),
    ),
    _correctness_claim(
        "session-workbench-closed-contract",
        "tests/contract/test_session_workbench_contract.py::test_catalog_and_metadata_are_fixed_and_body_free",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("RWB-003", "RSV-001", "RSV-003"),
    ),
    _correctness_claim(
        "session-workbench-broker-ordering",
        "tests/contract/test_session_workbench_runtime.py::test_fixed_artifact_metadata_is_reauthorized_and_never_returns_a_body",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RWB-001", "RWB-002", "RSV-002", "RSV-003"),
    ),
    _correctness_claim(
        "session-workbench-file-sqlite-reopen",
        "tests/integration/test_session_workbench.py::test_workbench_does_not_recover_an_unavailable_bundle_from_its_local_selection",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("RWB-001", "RWB-003", "RSV-001", "RSV-003"),
    ),
    _correctness_claim(
        "session-workbench-terminal-controls",
        "tests/integration/test_session_workbench.py::test_workbench_delegates_a_correlated_answer_without_echoing_or_duplication",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("RWB-002", "RWB-004", "REC-003", "REC-004"),
    ),
    _correctness_claim(
        "checkpoint-strict-msgpack-registration",
        "tests/unit/test_checkpoint_msgpack.py::test_strict_msgpack_blocks_an_unregistered_project_type_but_preserves_the_explicit_types",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RUI-008",),
    ),
    _correctness_claim(
        "canonical-bundle-locator",
        "tests/domain/test_work_unit_bundle.py::test_canonical_attempt_artifact_paths_are_exact",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("RUI-009", "WOU-009"),
    ),
    _correctness_claim(
        "wave0-worker-failure-category",
        "tests/graph/test_work_unit_component.py::test_worker_category_is_separate_from_validation_code",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("WFC-001", "WOU-010"),
    ),
    _correctness_claim(
        "wave0-terminal-diagnosis",
        "tests/engine/test_gate_kernel.py::test_wave0_exhaustion_writes_diagnosis_without_changing_route",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("GAK-007", "RER-008", "WAN-006"),
    ),
    _correctness_claim(
        "delivery-project-catalog",
        "tests/contract/test_asset_checker_contract.py::test_project_catalog_serves_different_marker_queries_once",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("DER-001",),
    ),
    _correctness_claim(
        "delivery-ledger-boundary",
        "tests/domain/test_submission_ledger.py::test_representative_record_chain_round_trips_within_production_limit",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("DER-003",),
    ),
    _correctness_claim(
        "delivery-focused-make-targets",
        "tests/contract/test_verification_gate_contract.py::test_makefile_exposes_exact_non_mutating_verify_composition",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("DER-004",),
    ),
    _correctness_claim(
        "delivery-duration-policy",
        "tests/contract/test_delivery_efficiency_tools.py::test_duration_policy_rejects_unwaived_and_expired_slow_test",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("DER-005",),
    ),
    _correctness_claim(
        "delivery-repository-tracked",
        "tests/contract/test_repository_delivery.py::test_repository_delivery_is_tracked_unignored_and_declares_codex",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("DER-005",),
    ),
    _correctness_claim(
        "delivery-reference-benchmark",
        "tests/contract/test_delivery_efficiency_tools.py::test_reference_benchmark_report_rejects_missing_or_invalid_phase_data",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("DER-006",),
    ),
    _correctness_claim(
        "delivery-impact-metadata",
        "tests/contract/test_asset_checker_contract.py::test_requirement_impact_rejects_duplicate_risk_and_uncollected_selector",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("EVH-011",),
    ),
    _correctness_claim(
        "charter-node-agent-workflow-integrity",
        "tests/contract/test_change_guidance_governance.py::test_node_agent_and_workflow_outcome_reviews_remain_independent",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("DRC-008",),
    ),
    _correctness_claim(
        "charter-control-placement",
        "tests/contract/test_change_guidance_governance.py::test_control_placement_and_existing_reviews_remain_independent",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("DRC-009",),
    ),
    _correctness_claim(
        "charter-operation-guidance",
        "tests/contract/test_change_guidance_governance.py::test_config_requires_advisory_operation_guidance_boundary",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("DRC-010",),
    ),
    _correctness_claim(
        "charter-operation-guidance-probe-record",
        "tests/contract/test_operation_guidance_probe_evidence.py::test_operation_guidance_probe_evidence_has_complete_per_probe_metadata",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("DRC-010",),
    ),
    _correctness_claim(
        "selected-change-closeout-boundary",
        "tests/contract/test_selected_change_closeout.py::test_verify_boundary_emits_exact_committed_range_summary",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("SCC-001",),
    ),
    _correctness_claim(
        "selected-change-closeout-record",
        "tests/contract/test_selected_change_closeout.py::test_record_review_requires_task_led_findings_or_a_stated_limitation",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("SCC-002",),
    ),
    _correctness_claim(
        "selected-change-closeout-no-side-effects",
        "tests/contract/test_selected_change_closeout.py::test_invalid_attestations_do_not_run_git_or_native_archive_or_touch_tasks",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("SCC-003",),
    ),
    _correctness_claim(
        "nac-capability-resource",
        "tests/domain/test_node_agent_capability.py::test_local_resources_load_matching_closed_postures",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("NAC-001",),
    ),
    _correctness_claim(
        "nac-renderer-composition",
        "tests/unit/test_node_cognitive_control_program.py::test_renderer_composes_a_declared_local_capability_after_base_policy",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("NAC-002",),
    ),
    _correctness_claim(
        "nac-runtime-tool-admission",
        "tests/unit/test_node_agent_bridge.py::test_capability_posture_disagreement_fails_before_model_resolution",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("NOA-011", "NAC-003", "NAC-004", "EVH-012"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "nac-cohort-evidence-matrix",
        "tests/graph/test_node_agent_capability_cohort.py::test_cohort_evidence_matrix_has_two_collected_claims_per_branch",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NAC-004", "NAC-009", "CPE-003", "EVH-012", "EVH-022"),
    ),
    _correctness_claim(
        "nac-hitl-brief-success",
        "tests/graph/test_hitl1_node.py::test_first_visit_generates_brief_and_interrupts",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NAC-005", "EVH-013", "HIC-004"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    *(
        _correctness_claim(
            claim_id,
            selector,
            seam,
            requirement_ids=requirement_ids,
            authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
        )
        for claim_id, selector, seam, requirement_ids in (
            (
                "nac-topic-planning-repair-success",
                "tests/graph/test_topic_planning_node.py::test_invalid_plan_retries_once_then_records",
                StableSeam.NODE_INTERFACE,
                ("NAC-006", "TOP-006", "EVH-015"),
            ),
            (
                "nac-topic-planning-repair-risk",
                "tests/graph/test_topic_planning_node.py::test_uncovered_question_is_repaired_then_exhausts",
                StableSeam.NODE_INTERFACE,
                ("NAC-006", "TOP-006", "EVH-015"),
            ),
            (
                "nac-wave1-risk",
                "tests/integration/test_wave1_work_units.py::test_real_wave1_baseline_duplicate_is_not_admitted_as_new_coverage",
                StableSeam.RUNTIME_INTEGRATION,
                ("NAC-006", "WON-007", "EVH-015"),
            ),
            (
                "nac-wave1-repair-success",
                "tests/integration/test_wave1_work_units.py::test_real_wave1_repair_invocation_problem_reaches_worker_controller",
                StableSeam.RUNTIME_INTEGRATION,
                ("NAC-006", "WON-007", "EVH-015"),
            ),
            (
                "nac-wave1-repair-risk",
                "tests/integration/test_wave1_work_units.py::test_real_wave1_malformed_repair_has_no_artifact_admission",
                StableSeam.RUNTIME_INTEGRATION,
                ("NAC-006", "WON-007", "EVH-015"),
            ),
            (
                "nac-wave1-source-diagnostic-success",
                "tests/integration/test_wave1_work_units.py::test_wave1_post_acceptance_critics_materialize_bound_artifacts_and_then_suppress_replay",
                StableSeam.RUNTIME_INTEGRATION,
                ("NAC-006", "WON-003", "EVH-015"),
            ),
            (
                "nac-wave1-source-diagnostic-risk",
                "tests/integration/test_wave1_work_units.py::test_wave1_post_acceptance_retry_dispatches_only_the_missing_critic",
                StableSeam.RUNTIME_INTEGRATION,
                ("NAC-006", "WON-003", "EVH-015"),
            ),
            (
                "nac-wave1-claim-verifier-success",
                "tests/integration/test_wave1_work_units.py::test_wave1_claim_verifier_materializes_one_bound_artifact",
                StableSeam.RUNTIME_INTEGRATION,
                ("NAC-006", "WON-003", "EVH-015"),
            ),
            (
                "nac-wave1-claim-verifier-risk",
                "tests/integration/test_wave1_work_units.py::test_wave1_claim_verifier_invalid_result_retries_only_that_critic",
                StableSeam.RUNTIME_INTEGRATION,
                ("NAC-006", "WON-003", "EVH-015"),
            ),
        )
    ),
    _correctness_claim(
        "nac-hitl-brief-risk",
        "tests/graph/test_hitl1_node.py::test_brief_lifecycle_field_is_repaired_without_route_authority",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NAC-005", "EVH-013", "HIN-013"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "nac-hitl-brief-repair-success",
        "tests/graph/test_hitl1_node.py::test_first_visit_retries_once_on_invalid_brief",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NAC-005", "EVH-013"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "nac-hitl-brief-repair-risk",
        "tests/graph/test_hitl1_node.py::test_brief_failure_exhausts_without_interrupt_or_profile_write",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NAC-005", "EVH-013"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "npc-hitl-profile-catalog",
        "tests/graph/test_node_agent_capability_cohort.py::test_cohort_branch_binding[hitl1/brief]",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NPC-003", "NAC-005"),
    ),
    _correctness_claim(
        "npc-planning-intake-catalog",
        "tests/graph/test_node_agent_capability_cohort.py::test_cohort_branch_binding[topic-planning/plan]",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NPC-004", "NAC-006"),
    ),
    _correctness_claim(
        "npc-wave1-critic-catalog",
        "tests/graph/test_node_agent_capability_cohort.py::test_cohort_branch_binding[wave1/source-diagnostic]",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("NPC-004", "NAC-006"),
    ),
    _correctness_claim(
        "hitl1-profile-interaction-success",
        "tests/graph/test_hitl1_node.py::test_source_constrained_revision_stays_advisory_until_later_natural_confirmation",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("HIN-011", "HIC-004", "EVH-014"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "hitl1-profile-interaction-fallback",
        "tests/graph/test_hitl1_node.py::test_question_ambiguity_and_semantic_fallback_preserve_one_current_proposal",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("HIN-011", "HIC-004", "EVH-014"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    *(
        _correctness_claim(
            claim_id,
            selector,
            seam,
            requirement_ids=("NAC-003", "NAC-004", "EVH-012"),
            authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
        )
        for claim_id, selector, seam in (
            (
                "nac-hitl-success",
                "tests/graph/test_hitl1_node.py::test_semantic_revision_publishes_new_visible_proposal_before_acceptance",
                StableSeam.NODE_INTERFACE,
            ),
            (
                "nac-hitl-risk",
                "tests/graph/test_hitl1_node.py::test_semantic_question_retains_proposal_with_bounded_feedback",
                StableSeam.NODE_INTERFACE,
            ),
            (
                "nac-hitl-repair-success",
                "tests/graph/test_hitl1_node.py::test_semantic_invalid_output_repairs_once_then_preserves_proposal",
                StableSeam.NODE_INTERFACE,
            ),
            (
                "nac-hitl-repair-risk",
                "tests/graph/test_hitl1_node.py::test_repair_slot_transient_has_no_third_call_and_offers_distinct_new_start",
                StableSeam.NODE_INTERFACE,
            ),
            (
                "nac-wave0-success",
                "tests/integration/test_wave0_work_units.py::test_real_wave0_worker_binds_the_required_capability_before_artifact_admission",
                StableSeam.RUNTIME_INTEGRATION,
            ),
            (
                "nac-wave0-repair-success",
                "tests/integration/test_wave0_work_units.py::test_real_wave0_repair_keeps_tools_disabled_and_preserves_worker_admission",
                StableSeam.RUNTIME_INTEGRATION,
            ),
            (
                "nac-wave0-repair-risk",
                "tests/integration/test_wave0_work_units.py::test_real_wave0_malformed_repair_fails_without_artifact_admission",
                StableSeam.RUNTIME_INTEGRATION,
            ),
            (
                "nac-wave2-repair-success",
                "tests/graph/test_wave2_synthesis_real.py::test_real_synthesis_repairs_gaps_only_output_when_accepted_evidence_exists",
                StableSeam.NODE_INTERFACE,
            ),
            (
                "nac-wave2-repair-risk",
                "tests/graph/test_wave2_synthesis_real.py::test_real_synthesis_rejects_gaps_only_repair_without_publishing",
                StableSeam.NODE_INTERFACE,
            ),
        )
    ),
    *(
        _correctness_claim(
            f"cpe-composition-{case_id.replace('/', '-')}",
            f"tests/graph/test_cognitive_program_evidence.py::test_cognitive_program_composition[{case_id}]",
            StableSeam.NODE_INTERFACE,
            requirement_ids=(
                ("CPE-001", "CPE-003", "NPC-006", "NPC-007", "NAC-008", "NAC-009", "FID-001")
                if case_id == "final-delivery/composer"
                else ("CPE-001", "NPC-006", "NAC-008")
            ),
            authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
        )
        for case_id in _COGNITIVE_PROGRAM_CASE_IDS
    ),
    _correctness_claim(
        "cpe-evidence-ledger-closure",
        "tests/graph/test_node_agent_capability_cohort.py::test_cognitive_program_evidence_matrix_closes_the_current_catalog",
        StableSeam.NODE_INTERFACE,
        requirement_ids=(
            "CPE-001",
            "CPE-002",
            "CPE-003",
            "NPC-006",
            "NPC-007",
            "NAC-008",
            "NAC-009",
            "EVH-017",
            "EVH-022",
        ),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "cpe-complete-evidence-board",
        (
            "tests/contract/test_cognitive_program_board.py::"
            "test_board_closes_exact_current_node_branch_and_calibration_denominators"
        ),
        StableSeam.NODE_INTERFACE,
        requirement_ids=("CPE-001", "CPE-004", "EVH-017"),
    ),
    _correctness_claim(
        "consolidation-empty-rollout",
        ("tests/contract/test_requirement_evidence_policy.py::test_consolidation_rollout_is_empty_and_review_only"),
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("EVH-023",),
    ),
    _correctness_claim(
        "intake-planning-calibration-corpus",
        "tests/unit/test_intake_planning_calibration.py::test_calibration_cases_compose_real_zero_tool_branch_requests",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-018", "HIN-012", "TOP-007"),
    ),
    _correctness_claim(
        "intake-planning-calibration-selection",
        "tests/unit/test_intake_planning_calibration.py::test_default_deterministic_selection_excludes_the_live_calibration_collection",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("EVH-018",),
    ),
    _correctness_claim(
        "intake-planning-calibration-report-contract",
        "tests/unit/test_live_evaluation.py::test_live_report_accepts_a_typed_calibration_rubric_result",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("EVH-018",),
    ),
    _correctness_claim(
        "evidence-intake-calibration-corpus",
        "tests/unit/test_evidence_intake_calibration.py::test_evidence_intake_request_composition_preserves_branch_tool_posture",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-019", "WAN-008", "WON-008"),
    ),
    _correctness_claim(
        "evidence-intake-calibration-selection",
        "tests/unit/test_evidence_intake_calibration.py::test_default_deterministic_selection_excludes_both_live_calibration_collections",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("EVH-019",),
    ),
    _correctness_claim(
        "evidence-intake-calibration-report-contract",
        "tests/unit/test_evidence_intake_calibration.py::test_selected_evidence_intake_runner_uses_strict_branch_preflight",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("EVH-019",),
    ),
    _correctness_claim(
        "final-composition-calibration-corpus",
        (
            "tests/unit/test_final_composition_calibration.py::"
            "test_final_composition_corpus_has_normal_and_highest_risk_cases_with_declared_bounds"
        ),
        StableSeam.NODE_INTERFACE,
        requirement_ids=("EVH-022", "FID-001", "FID-003"),
    ),
    _correctness_claim(
        "final-composition-calibration-selection",
        (
            "tests/unit/test_final_composition_calibration.py::"
            "test_final_composition_corpus_is_a_separate_live_only_collection"
        ),
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("EVH-022",),
    ),
    *(
        _correctness_claim(
            f"cpe-feedback-{case_id.replace('/', '-')}",
            f"tests/graph/test_cognitive_program_evidence.py::test_cognitive_program_feedback_disposition[{case_id}]",
            StableSeam.NODE_INTERFACE,
            requirement_ids=(
                ("CPE-002", "CPE-003", "FID-004", "EVH-017", "EVH-022")
                if case_id == "final-delivery/composer"
                else ("CPE-002", "EVH-017")
            ),
            authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
        )
        for case_id in _COGNITIVE_PROGRAM_CASE_IDS
    ),
    *(
        _correctness_claim(
            f"cpe-guardrail-{case_id.replace('/', '-')}",
            f"tests/unit/test_node_agent_bridge.py::test_cognitive_program_guardrail_admission[{case_id}]",
            StableSeam.RUNTIME_INTEGRATION,
            requirement_ids=(
                ("NAC-008", "NAC-009", "NOA-012", "NOA-013", "FID-005", "EVH-017", "EVH-022")
                if case_id == "final-delivery/composer"
                else ("NAC-008", "NOA-012", "EVH-017")
            ),
            authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
        )
        for case_id in _COGNITIVE_PROGRAM_CASE_IDS
    ),
    _correctness_claim(
        "canonical-module-root-governance",
        "tests/contract/test_architecture_governance.py::ArchitectureGovernanceContractTests::test_legacy_compatibility_root_fails",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("PRS-001",),
    ),
    _correctness_claim(
        "retired-test-structure-governance",
        "tests/contract/test_test_structure_retirement.py::test_retained_test_roots_are_non_empty_and_e2e_has_no_active_surface",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("PRS-001",),
    ),
    _correctness_claim(
        "suspended-full-real-execution-surface",
        "tests/contract/test_release_suspension.py::test_full_real_selector_is_retained_but_has_no_active_execution_surface",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("EVH-005",),
    ),
    _correctness_claim(
        "release-evidence-provenance-retirement",
        "tests/contract/test_release_evidence_provenance.py::test_retained_release_provenance_routes_need_no_superseded_report",
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("EVH-005",),
    ),
    _correctness_claim(
        "research-confirmation-advisory-decision",
        "tests/domain/test_research_confirmation.py::test_unconfirmed_model_proposal_remains_one_outstanding_decision",
        StableSeam.DOMAIN_ENGINE,
        requirement_ids=("RCF-001",),
    ),
    _correctness_claim(
        "run-experience-complete-proposal-visibility",
        (
            "tests/integration/test_demo_run_update_adapters.py::"
            "test_standalone_adapters_render_every_complete_proposal_line_before_control"
        ),
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("RER-012",),
    ),
    _correctness_claim(
        "run-experience-active-bundle-start-conflict-projection",
        (
            "tests/contract/test_run_experience_contract.py::"
            "test_available_active_result_projects_a_safe_non_terminal_fault[different-start-conflict]"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RER-014",),
    ),
    _correctness_claim(
        "run-experience-active-bundle-status-projection",
        (
            "tests/contract/test_run_experience_contract.py::"
            "test_available_active_result_projects_a_safe_non_terminal_fault[status-observes-active-bundle]"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RER-014",),
    ),
    _correctness_claim(
        "demo-explicit-real-profile-admission",
        "tests/unit/test_demo_core.py::test_explicit_real_demo_profile_is_single_safe_runtime_configuration",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("DPL-011",),
    ),
    _correctness_claim(
        "all-real-demo-fresh-scope-admission",
        (
            "tests/unit/test_demo_core.py::"
            "test_all_real_demo_adapters_use_fresh_scopes_while_fixture_scope_remains_stable"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("DPL-013",),
    ),
    _correctness_claim(
        "demo-real-calibration-procedure",
        (
            "tests/contract/test_demo_commands.py::"
            "test_embedded_smoke_calibration_documents_an_explicit_observational_procedure"
        ),
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("DPL-012",),
    ),
    _correctness_claim(
        "journal-execution-profile-provenance",
        "tests/unit/test_run_observation_store.py::test_admitted_journal_retains_profile_only_on_matching_admission_and_summary",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("REJ-006",),
    ),
    _correctness_claim(
        "journal-cross-node-validation-attribution",
        (
            "tests/integration/test_wave0_work_units.py::"
            "test_one_bundle_journal_retains_topic_planning_and_wave0_validation_as_observations"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("REJ-007",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "node-agent-budget-stop-attribution",
        (
            "tests/unit/test_node_agent_bridge.py::"
            "test_bridge_uses_unknown_for_untyped_budget_stop_and_keeps_non_budget_failures_unattributed"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("NOA-015",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "topic-planning-validation-observation",
        (
            "tests/graph/test_topic_planning_node.py::"
            "test_invalid_initial_topic_plan_then_repair_records_ordered_closed_codes"
        ),
        StableSeam.NODE_INTERFACE,
        requirement_ids=("TOP-009",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "topic-planning-compact-prompt-envelope",
        (
            "tests/graph/test_topic_planning_prompts.py::"
            "test_initial_and_repair_requests_project_the_compact_topic_plan_envelope"
        ),
        StableSeam.NODE_INTERFACE,
        requirement_ids=("TOP-010",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "topic-planning-output-admission-envelope",
        (
            "tests/unit/test_budget_middleware.py::"
            "test_topic_planning_fixed_demo_render_is_admitted_but_oversized_request_is_not"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("TOP-010",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "topic-planning-retained-compact-candidate",
        ("tests/graph/test_topic_planning_node.py::test_compact_plan_above_old_structured_truncation_routes_next"),
        StableSeam.NODE_INTERFACE,
        requirement_ids=("TOP-010",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "wave0-validation-observation",
        "tests/integration/test_wave0_work_units.py::test_real_wave0_valid_initial_parser_observation_is_closed_and_correlated",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("WAN-010", "WAN-012"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "wave0-completion-envelope",
        "tests/graph/test_wave0_worker.py::test_wave0_initial_and_repair_requests_expose_the_same_closed_completion_contract",
        StableSeam.NODE_INTERFACE,
        requirement_ids=("WAN-011",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "wave1-completion-envelope",
        (
            "tests/unit/test_wave1_critic_prompts.py::TestWave1LocalCriticPrompts::"
            "test_worker_and_repair_render_only_bounded_assignment_and_closed_feedback"
        ),
        StableSeam.NODE_INTERFACE,
        requirement_ids=("WON-011",),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "journal-v3-response-shape-and-post-candidate",
        "tests/unit/test_run_observation_store.py::test_v3_journal_retains_redacted_shape_and_post_candidate_facts",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("REJ-002", "REJ-004", "REJ-006", "REJ-007"),
    ),
    _correctness_claim(
        "wave0-post-candidate-validation-observation",
        (
            "tests/integration/test_wave0_work_units.py::"
            "test_real_wave0_post_candidate_submission_validation_does_not_enter_repair"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("WAN-012", "WOU-012"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "wave1-post-candidate-validation-observation",
        (
            "tests/integration/test_wave1_work_units.py::"
            "test_real_wave1_post_candidate_submission_validation_does_not_enter_repair"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("WON-012", "WOU-012"),
        authenticity=AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
    ),
    _correctness_claim(
        "shared-submit-post-candidate-observation",
        "tests/graph/test_work_unit_component.py::test_component_records_one_post_candidate_fact_for_submission_rejection",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("WOU-012",),
    ),
    _correctness_claim(
        "evidence-intake-explicit-profile-bundle-calibration",
        (
            "tests/unit/test_evidence_intake_calibration.py::"
            "test_offline_evidence_intake_branches_are_explicit_profile_bundle_bound_and_redacted"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("EVH-030", "WAN-012", "WON-012"),
    ),
    _correctness_claim(
        "retained-checkpoint-admission-negative",
        "tests/unit/test_retained_checkpoint_cutover.py::test_unregistered_repair_counts_checkpoint_rejects_before_graph_compile_or_execution",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("GAK-004", "REG-011"),
    ),
    _correctness_claim(
        "retained-checkpoint-gate-replay",
        "tests/unit/test_retained_checkpoint_cutover.py::test_registered_checkpoint_migration_writes_reloads_and_replays_current_gate_facts",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("GAK-004", "REG-011"),
    ),
    _correctness_claim(
        "retained-bundle-admission-negative",
        "tests/unit/test_retained_bundle_cutover.py::test_unregistered_repair_exhausted_bundle_is_unavailable_before_status_projection",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("DRH-002", "REG-011"),
    ),
    _correctness_claim(
        "retained-bundle-migration-reload",
        "tests/unit/test_retained_bundle_cutover.py::test_registered_terminal_migration_preserves_only_identity_and_terminal_status",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("DRH-002",),
    ),
    _correctness_claim(
        "retained-journal-admission-negative",
        "tests/unit/test_retained_journal_cutover.py::test_partial_or_unregistered_old_journal_is_unavailable_before_append_or_projection",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("REJ-002",),
    ),
    _correctness_claim(
        "retained-journal-migration-reload",
        "tests/unit/test_retained_journal_cutover.py::test_registered_complete_v2_journal_migrates_without_inferred_v3_provenance",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("REJ-002",),
    ),
    _correctness_claim(
        "retained-terminal-location-negative",
        "tests/unit/test_retained_terminal_result_cutover.py::test_persisted_terminal_without_location_rejects_before_any_projection",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("RER-009",),
    ),
    _correctness_claim(
        "retained-terminal-location-writers",
        "tests/unit/test_retained_terminal_result_cutover.py::test_verified_provider_publication_writer_retains_bundle_journal_location",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        requirement_ids=("RER-009",),
    ),
    _correctness_claim(
        "runtime-observability-safe-schema",
        "tests/unit/test_events.py::test_safe_observation_schema_rejects_unsafe_fields",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RTO-001", "REJ-005"),
    ),
    _correctness_claim(
        "runtime-observability-observer-isolation",
        "tests/unit/test_events.py::test_safe_observation_isolates_logger_failure_and_propagates_cancellation",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RTO-001", "REJ-005"),
    ),
    _correctness_claim(
        "runtime-observability-trusted-correlation",
        "tests/unit/test_runtime_adapter.py::test_adapt_keeps_trace_binding_with_deerflow_logging",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("RTO-003", "RUI-002"),
    ),
    _correctness_claim(
        "gateway-observer-public-turn-ownership",
        (
            "tests/unit/test_gateway_observer.py::"
            "test_observer_creates_one_fresh_thread_then_reuses_only_its_public_thread_for_follow_up"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("GOO-001",),
    ),
    _correctness_claim(
        "gateway-observer-public-http-shape",
        "tests/unit/test_gateway_observer.py::test_http_client_uses_only_fixed_public_thread_and_stream_shapes",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("GOO-001",),
    ),
    _correctness_claim(
        "gateway-observer-withheld-progress",
        (
            "tests/unit/test_gateway_observer.py::"
            "test_valid_custom_progress_stays_withheld_while_only_typed_tool_result_returns"
        ),
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("GOO-002",),
    ),
    _correctness_claim(
        "gateway-observer-no-terminal-inference",
        "tests/unit/test_gateway_observer.py::test_end_or_assistant_prose_cannot_manufacture_a_lifecycle_result",
        StableSeam.RUNTIME_INTEGRATION,
        requirement_ids=("GOO-002",),
    ),
    _correctness_claim(
        "gateway-profile-observer-readiness",
        (
            "tests/contract/test_local_profiles.py::"
            "test_gateway_observer_readiness_uses_only_the_validated_profile_environment_and_check_mode"
        ),
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("GOO-003",),
    ),
    _correctness_claim(
        "gateway-profile-stderr-capture",
        (
            "tests/contract/test_local_profiles.py::"
            "test_profile_child_capture_is_owner_only_unique_and_announced_before_child_start"
        ),
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("GOO-003",),
    ),
    _correctness_claim(
        "gateway-real-cli-preflight",
        (
            "tests/integration/test_gateway_demo_real.py::"
            "test_default_real_cli_requires_profile_and_rejects_scripted_before_profile_or_gateway_work"
        ),
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("DPL-004",),
    ),
    _correctness_claim(
        "gateway-real-cli-cutover",
        (
            "tests/integration/test_gateway_demo_real.py::"
            "test_default_real_cli_uses_only_ready_profile_gateway_transport_without_local_provider_or_graph"
        ),
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("DPL-004",),
    ),
    _correctness_claim(
        "gateway-real-tui-preflight",
        ("tests/integration/test_gateway_demo_tui.py::test_gateway_tui_requires_profile_before_client_or_local_graph"),
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("RED-001",),
    ),
    _correctness_claim(
        "gateway-real-tui-control-boundary",
        (
            "tests/integration/test_gateway_demo_tui.py::"
            "test_gateway_tui_hides_cancel_disables_reentry_and_never_renders_fault_as_completion"
        ),
        StableSeam.PUBLIC_ENTRY,
        requirement_ids=("RED-001",),
    ),
)


__all__ = [
    "AssetClass",
    "AuthenticityLevel",
    "EVIDENCE_CLAIMS",
    "EvidenceClaimError",
    "FocusedSelection",
    "StableSeam",
    "TestEvidenceClaim",
    "claim_index",
    "validate_evidence_claims",
    "validate_claim_selections",
    "validate_inventory_claim_references",
]
