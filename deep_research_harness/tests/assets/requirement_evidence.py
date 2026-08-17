"""Small cross-lane requirement-evidence policy and pure validator.

@impl EVH-008
@impl EVH-009
@impl EVH-010
@impl EVH-011
@impl EVH-023
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

from tests.assets.evidence import AssetClass, AuthenticityLevel, StableSeam, TestEvidenceClaim

REQUIREMENT_ID_RE = re.compile(r"[A-Z]{3}-\d{3}")
REQUIREMENT_RANGE_RE = re.compile(r"([A-Z]{3})-(\d{3})\.\.(\d{3})")
IMPL_LINE_RE = re.compile(r"@impl\s+([^\n]+)")


class RequirementEvidenceError(ValueError):
    pass


@dataclass(frozen=True)
class RequiredEvidence:
    asset_class: AssetClass
    authenticity: AuthenticityLevel | None = None


@dataclass(frozen=True)
class RequirementEvidenceRule:
    requirement_id: str
    required_evidence: tuple[RequiredEvidence, ...]


@dataclass(frozen=True)
class RequirementImpact:
    """One smallest sufficient proof selected for a changed requirement."""

    requirement_id: str
    owning_contract: str
    seam: StableSeam
    selector: str
    risk: str
    escalation_rationale: str | None = None


@dataclass(frozen=True)
class ConsolidationReplacement:
    """One retained claim preserving an exact displaced requirement-risk pair."""

    retained_claim_id: str
    requirement_id: str
    risk: str
    metadata_difference_rationale: str | None = None


@dataclass(frozen=True)
class ConsolidationDecision:
    """Review-only proposal to replace one collected central evidence claim."""

    displaced_claim_id: str
    displaced_selector: str
    preservation_basis: str
    replacements: tuple[ConsolidationReplacement, ...]


CONSOLIDATION_DECISIONS: tuple[ConsolidationDecision, ...] = ()


REQUIREMENT_EVIDENCE_POLICY = (
    RequirementEvidenceRule(
        requirement_id="EVH-004",
        required_evidence=(
            RequiredEvidence(
                AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
                AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
            ),
        ),
    ),
    RequirementEvidenceRule(
        requirement_id="EVH-005",
        required_evidence=(
            RequiredEvidence(AssetClass.CODE_CORRECTNESS),
            RequiredEvidence(
                AssetClass.LIVE_BEHAVIORAL_EVALUATION,
                AuthenticityLevel.LIVE_REAL_DEPENDENCIES,
            ),
        ),
    ),
    RequirementEvidenceRule(
        requirement_id="EVH-008",
        required_evidence=(
            RequiredEvidence(
                AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
                AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
            ),
        ),
    ),
)

REQUIREMENT_IMPACTS = (
    RequirementImpact(
        "DER-001",
        "deep-research-delivery-efficiency",
        StableSeam.DOMAIN_ENGINE,
        "tests/contract/test_asset_checker_contract.py::test_project_catalog_serves_different_marker_queries_once",
        "lane queries reuse one validated catalog",
    ),
    RequirementImpact(
        "DER-003",
        "deep-research-delivery-efficiency",
        StableSeam.DOMAIN_ENGINE,
        "tests/domain/test_submission_ledger.py::test_representative_record_chain_round_trips_within_production_limit",
        "representative linkage proof does not require full-limit construction",
    ),
    RequirementImpact(
        "DER-004",
        "deep-research-delivery-efficiency",
        StableSeam.PUBLIC_ENTRY,
        "tests/contract/test_verification_gate_contract.py::test_makefile_exposes_exact_non_mutating_verify_composition",
        "focused commands cannot replace complete verification",
    ),
    RequirementImpact(
        "DER-005",
        "deep-research-delivery-efficiency",
        StableSeam.DOMAIN_ENGINE,
        "tests/contract/test_delivery_efficiency_tools.py::test_duration_policy_rejects_unwaived_and_expired_slow_test",
        "slow tests require a bounded exact waiver",
    ),
    RequirementImpact(
        "DER-005",
        "deep-research-delivery-efficiency",
        StableSeam.PUBLIC_ENTRY,
        "tests/contract/test_repository_delivery.py::test_repository_delivery_is_tracked_unignored_and_declares_codex",
        "a clean clone could otherwise depend on ignored local CI workflows or OpenSpec lifecycle skills",
    ),
    RequirementImpact(
        "DER-006",
        "deep-research-delivery-efficiency",
        StableSeam.DOMAIN_ENGINE,
        "tests/contract/test_delivery_efficiency_tools.py::test_reference_benchmark_report_rejects_missing_or_invalid_phase_data",
        "benchmark phase attribution cannot be malformed",
    ),
    RequirementImpact(
        "NOA-010",
        "node-agent-runtime",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_node_agent_bridge.py::test_canonical_catalog_case_bridge_prompt_matches_shared_renderer",
        "the runtime bridge cannot fork final prompt text from the review projection",
    ),
    RequirementImpact(
        "NAC-001",
        "node-agent-capabilities",
        StableSeam.DOMAIN_ENGINE,
        "tests/domain/test_node_agent_capability.py::test_local_resources_load_matching_closed_postures",
        "the local capability resource cannot bypass its closed metadata posture",
    ),
    RequirementImpact(
        "NAC-002",
        "node-agent-capabilities",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_node_cognitive_control_program.py::test_renderer_composes_a_declared_local_capability_after_base_policy",
        "the static capability policy must remain ordered after base policy",
    ),
    RequirementImpact(
        "NAC-003",
        "node-agent-capabilities",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/integration/test_wave0_work_units.py::test_real_wave0_worker_binds_the_required_capability_before_artifact_admission",
        "a required Wave0 capability must stay bound through artifact admission",
    ),
    RequirementImpact(
        "NAC-004",
        "node-agent-capabilities",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_node_agent_capability_cohort.py::test_cohort_evidence_matrix_has_two_collected_claims_per_branch",
        "the cohort cannot replace independent branch evidence with aggregate coverage",
    ),
    RequirementImpact(
        "NAC-005",
        "node-agent-capabilities",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_hitl1_node.py::test_brief_lifecycle_field_is_repaired_without_route_authority",
        "a model lifecycle field can trigger repair but cannot select a route or accept research",
    ),
    RequirementImpact(
        "NAC-006",
        "node-agent-capabilities",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_node_agent_capability_cohort.py::test_cohort_evidence_matrix_has_two_collected_claims_per_branch",
        "the fourteen-branch planning and initial-intake cohort cannot omit either Wave1 critic or substitute "
        "aggregate coverage",
    ),
    RequirementImpact(
        "NOA-011",
        "node-agent-runtime",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_node_agent_bridge.py::test_capability_posture_disagreement_fails_before_model_resolution",
        "a tool-posture disagreement must fail before model-visible work",
    ),
    RequirementImpact(
        "EVH-012",
        "evaluation-hardening",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_node_agent_capability_cohort.py::test_cohort_evidence_matrix_has_two_collected_claims_per_branch",
        "each migrated branch needs separate collected success and risk proof",
    ),
    RequirementImpact(
        "EVH-013",
        "evaluation-hardening",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_hitl1_node.py::test_brief_failure_exhausts_without_interrupt_or_profile_write",
        "an exhausted profile repair cannot publish partial state or lifecycle authority",
    ),
    RequirementImpact(
        "HIN-011",
        "hitl1-node",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_hitl1_node.py::test_source_constrained_revision_stays_advisory_until_later_natural_confirmation",
        "a semantic candidate cannot publish a source-constrained revision before later graph-owned confirmation",
    ),
    RequirementImpact(
        "HIN-009",
        "hitl1-node",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_hitl1_node.py::test_natural_confirmation_writes_current_proposal_and_routes_accepted",
        "a natural reply can only materialize the current checkpointed proposal through graph admission",
    ),
    RequirementImpact(
        "HIN-011",
        "hitl1-node",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_hitl1_node.py::test_natural_confirmation_writes_current_proposal_and_routes_accepted",
        "a scripted semantic candidate cannot create profile state beyond the current proposal",
    ),
    RequirementImpact(
        "HIC-004",
        "human-interaction-contract",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_hitl1_node.py::test_first_visit_generates_brief_and_interrupts",
        "complete-proposal context cannot replace the trusted visible action with JSON or an action token",
    ),
    RequirementImpact(
        "HIC-004",
        "human-interaction-contract",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_hitl1_node.py::test_natural_confirmation_writes_current_proposal_and_routes_accepted",
        "a scripted semantic candidate proves deterministic admission rather than live-language quality",
    ),
    RequirementImpact(
        "NOA-001",
        "node-agent-runtime",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_node_agent_bridge.py::test_admitted_hitl_timeout_wrappers_are_classified_before_connection_wrappers[openai]",
        "the supported SDK timeout remains distinct while transport timeout keeps no invented origin",
    ),
    RequirementImpact(
        "NOA-001",
        "node-agent-runtime",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_node_agent_bridge.py::test_admitted_hitl_bridge_deadline_has_only_bridge_timeout_origin",
        "the bridge deadline cannot be attributed to the provider SDK timeout branch",
    ),
    RequirementImpact(
        "EVH-014",
        "evaluation-hardening",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_hitl1_node.py::test_question_ambiguity_and_semantic_fallback_preserve_one_current_proposal",
        "semantic exhaustion needs its own collected lifecycle-fallback claim rather than an aggregate count",
    ),
    RequirementImpact(
        "EVH-015",
        "evaluation-hardening",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_node_agent_capability_cohort.py::test_cohort_evidence_matrix_has_two_collected_claims_per_branch",
        "each newly migrated Wave1 critic retains distinct direct normal and highest-risk deterministic proof",
    ),
    RequirementImpact(
        "NAC-007",
        "node-agent-capabilities",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/graph/test_targeted_evidence_real.py::test_targeted_valid_first_response_does_not_repair",
        "the targeted retrieval capability cannot bypass the existing work-unit admission seam",
    ),
    RequirementImpact(
        "NPC-005",
        "node-prompt-catalog",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_node_agent_capability_cohort.py::test_cohort_branch_binding[targeted-evidence/worker]",
        "the catalog must project the targeted worker's local capability rather than a legacy request",
    ),
    RequirementImpact(
        "WSN-005",
        "wave2-synthesis-node",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_wave2_synthesis_real.py::test_real_synthesis_uses_node_context_and_materializes_canonical_findings",
        "Wave2 findings cannot cite outside the accepted evidence assignment",
    ),
    RequirementImpact(
        "WSN-008",
        "wave2-synthesis-node",
        StableSeam.NODE_INTERFACE,
        (
            "tests/graph/test_cognitive_program_evidence.py::"
            "test_wave2_cognitive_program_keeps_method_in_the_rendered_capability[initial]"
        ),
        "the initial runtime-loaded method could otherwise drift out of the rendered Wave2 context",
    ),
    RequirementImpact(
        "TEL-005",
        "targeted-evidence-loop",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_targeted_evidence_real.py::test_claim_verifier_rejects_unassigned_reference_without_artifact",
        "a critic cannot materialize an unassigned reference",
    ),
    RequirementImpact(
        "EVH-016",
        "evaluation-hardening",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_node_agent_capability_cohort.py::test_cohort_evidence_matrix_has_two_collected_claims_per_branch",
        "the closed evidence-evaluation cohort cannot substitute aggregate coverage for branch proof",
    ),
    RequirementImpact(
        "EVH-029",
        "evaluation-hardening",
        StableSeam.RUNTIME_INTEGRATION,
        (
            "tests/eval/test_cognitive_evaluation_suite.py::"
            "test_wave2_cognitive_program_production_scenarios_record_only_declared_handoffs"
        ),
        (
            "the closed Wave2 corpus could otherwise report materialization or gate effects instead of its "
            "bounded handoff facts"
        ),
    ),
    RequirementImpact(
        "NPC-001",
        "node-prompt-catalog",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_node_agent_bridge.py::test_canonical_catalog_case_bridge_prompt_matches_shared_renderer",
        "the shared renderer remains the only final-message formatting seam",
    ),
    RequirementImpact(
        "NPC-002",
        "node-prompt-catalog",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_prompt_catalog.py::test_catalog_registers_every_direct_node_prompt_builder",
        "a direct node prompt builder cannot silently lose its review case",
    ),
    RequirementImpact(
        "NPC-002",
        "node-prompt-catalog",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_prompt_dump.py::test_source_rendering_remains_available_without_a_local_review_workspace",
        "source rendering must remain available without a local review workspace",
    ),
    RequirementImpact(
        "NPC-003",
        "node-prompt-catalog",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_node_agent_capability_cohort.py::test_cohort_branch_binding[hitl1/brief]",
        "the profile-brief catalog case must project its required local capability reference",
    ),
    RequirementImpact(
        "NPC-004",
        "node-prompt-catalog",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_node_agent_capability_cohort.py::test_cohort_branch_binding[wave1/source-diagnostic]",
        "the eight planning and initial-intake catalog cases cannot hide the Wave1 critic capability reference",
    ),
    RequirementImpact(
        "TOP-006",
        "topic-planning-node",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_topic_planning_node.py::test_valid_plan_routes_next_and_records_registry",
        "a planner candidate cannot bypass confirmed-profile coverage or zero-tool posture",
    ),
    RequirementImpact(
        "TOP-010",
        "topic-planning-node",
        StableSeam.NODE_INTERFACE,
        (
            "tests/graph/test_topic_planning_prompts.py::"
            "test_initial_and_repair_requests_project_the_compact_topic_plan_envelope"
        ),
        "initial and repair prompts could drift from the compact candidate contract",
    ),
    RequirementImpact(
        "TOP-010",
        "topic-planning-node",
        StableSeam.RUNTIME_INTEGRATION,
        (
            "tests/unit/test_budget_middleware.py::"
            "test_topic_planning_fixed_demo_render_is_admitted_but_oversized_request_is_not"
        ),
        "the final rendered request could be rejected before the provider or exceed the local admission budget",
    ),
    RequirementImpact(
        "TOP-010",
        "topic-planning-node",
        StableSeam.NODE_INTERFACE,
        ("tests/graph/test_topic_planning_node.py::test_compact_plan_above_old_structured_truncation_routes_next"),
        "a retained compact candidate could still be clipped before parser/materializer state admission",
    ),
    RequirementImpact(
        "WAN-007",
        "wave0-node",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/integration/test_wave0_work_units.py::test_real_wave0_worker_binds_the_required_capability_before_artifact_admission",
        "Wave0 retrieval bounds cannot widen before validator and ledger admission",
    ),
    RequirementImpact(
        "WON-007",
        "wave1-node",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/integration/test_wave1_work_units.py::test_real_wave1_baseline_duplicate_is_not_admitted_as_new_coverage",
        "a Wave1 baseline URL cannot be represented as newly admitted coverage",
    ),
    RequirementImpact(
        "WAN-008",
        "wave0-node",
        StableSeam.NODE_INTERFACE,
        "tests/unit/test_evidence_intake_calibration.py::test_evidence_intake_request_composition_preserves_branch_tool_posture",
        "Wave0 calibration renders bounded source-intake criteria without widening retrieval or admission authority",
    ),
    RequirementImpact(
        "WON-008",
        "wave1-node",
        StableSeam.NODE_INTERFACE,
        "tests/unit/test_evidence_intake_calibration.py::test_evidence_intake_request_composition_preserves_branch_tool_posture",
        "Wave1 calibration keeps baseline, provenance, repair, and critic scope distinct from admission "
        "and gate authority",
    ),
    RequirementImpact(
        "WON-001",
        "wave1-node",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/integration/test_wave1_work_units.py::test_real_wave1_factory_derives_the_authoritative_wave0_baseline_before_dispatch",
        "a real Wave1 dispatch cannot substitute an empty or checkpoint-derived baseline for accepted Wave0 records",
    ),
    RequirementImpact(
        "WON-003",
        "wave1-node",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/integration/test_wave1_work_units.py::test_real_wave1_review_gate_enforces_question_floor_and_review_integrity",
        "a malformed bound critic artifact cannot become a retryable candidate or route input",
    ),
    RequirementImpact(
        "WON-004",
        "wave1-node",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/integration/test_wave1_work_units.py::test_real_wave1_review_gate_enforces_question_floor_and_review_integrity",
        "Wave1 gate review integrity must fail before routing while repairable floor and question facts retain "
        "existing routes",
    ),
    RequirementImpact(
        "PRS-011",
        "project-structure",
        StableSeam.DOMAIN_ENGINE,
        "tests/contract/test_live_architecture_contract.py::test_prompt_review_workspace_is_optional_and_ignored",
        "prompt review output cannot become a required structural path or a tracked source-like tree",
    ),
    RequirementImpact(
        "CNI-001",
        "cognitive-node-interface",
        StableSeam.NODE_INTERFACE,
        "tests/contract/test_node_workflow_reader_interface.py::test_live_reader_inventory_passes",
        "every logical node retains one fixed non-runtime reader interface",
    ),
    RequirementImpact(
        "CNI-002",
        "cognitive-node-interface",
        StableSeam.NODE_INTERFACE,
        "tests/contract/test_node_workflow_reader_interface.py::test_live_reader_inventory_passes",
        "topology inventory cannot silently omit a logical node or use a Charter identity",
    ),
    RequirementImpact(
        "CNI-003",
        "cognitive-node-interface",
        StableSeam.NODE_INTERFACE,
        "tests/contract/test_node_workflow_reader_interface.py::test_live_reader_inventory_passes",
        "reader structure retains an explicit deterministic authority boundary",
    ),
    RequirementImpact(
        "CNI-004",
        "cognitive-node-interface",
        StableSeam.NODE_INTERFACE,
        "tests/contract/test_node_workflow_reader_interface.py::test_live_reader_inventory_passes",
        "deferred and controller cards retain distinct participation and commitment fields",
    ),
    RequirementImpact(
        "CNI-004",
        "cognitive-node-interface",
        StableSeam.NODE_INTERFACE,
        "tests/contract/test_deferred_activation_dossiers.py::test_live_dossiers_are_the_exact_non_runtime_activation_denominator",
        "deferred activation dossiers cannot lose their exact identities, authority boundary, or non-runtime status",
    ),
    RequirementImpact(
        "CNI-005",
        "cognitive-node-interface",
        StableSeam.NODE_INTERFACE,
        "tests/contract/test_node_workflow_reader_interface.py::test_live_reader_inventory_passes",
        "the reader checker rejects missing or malformed non-runtime projections",
    ),
    RequirementImpact(
        "ALR-001",
        "agent-led-research-decisions",
        StableSeam.NODE_INTERFACE,
        "tests/unit/test_hitl2_brief.py::TestHitl2Policy::test_validated_state_recommends_graph_owned_continuation",
        "ordinary validated state selects only the graph-owned autonomous route",
    ),
    RequirementImpact(
        "ALR-002",
        "agent-led-research-decisions",
        StableSeam.NODE_INTERFACE,
        "tests/unit/test_hitl2_real.py::TestRealHitl2Factory::test_validated_state_routes_proceed_without_a_human_response",
        "ordinary HITL2 continuation creates no pending human-input artifact",
    ),
    RequirementImpact(
        "ALR-001",
        "agent-led-research-decisions",
        StableSeam.PUBLIC_ENTRY,
        "tests/integration/test_demo_cli.py::test_interactive_demo_completes_after_scope_without_a_hitl2_choice",
        "public fake demo does not transfer its fixture route choice to the user",
    ),
    RequirementImpact(
        "FCO-001",
        "research-fake-cli-onboarding",
        StableSeam.PUBLIC_ENTRY,
        "tests/contract/test_demo_commands.py::test_readme_setup_commands_are_paste_safe_in_interactive_zsh",
        "quick-start commands do not pass prose or a shell comment to Make",
    ),
    RequirementImpact(
        "DRC-006",
        "deep-research-agent-charter",
        StableSeam.PUBLIC_ENTRY,
        "tests/contract/test_demo_commands.py::test_readme_entry_surfaces_route_to_current_detail_owners",
        "a first-time reader could otherwise conflate the product, operator, demo, "
        "verification, and workbench surfaces",
    ),
    RequirementImpact(
        "REA-001",
        "readiness-node",
        StableSeam.NODE_INTERFACE,
        "tests/unit/test_readiness_real.py::TestRealReadiness::test_store_integrity_failure_is_structural_and_skips_model",
        "an unreadable or integrity-invalid accepted record must block before a model call",
    ),
    RequirementImpact(
        "REA-002",
        "readiness-node",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/integration/test_zero_tool_node_conformance.py::test_readiness_critic_crosses_real_zero_tool_bridge_and_uses_ledger_projection",
        "the readiness critic must receive only accepted ledger evidence through its zero-tool capability boundary",
    ),
    RequirementImpact(
        "REA-004",
        "readiness-node",
        StableSeam.NODE_INTERFACE,
        "tests/unit/test_readiness_real.py::TestRealReadiness::test_bridge_failure_projects_repair_without_all_ready",
        "a bridge failure cannot silently restore an all-ready route",
    ),
    RequirementImpact(
        "REA-006",
        "readiness-node",
        StableSeam.NODE_INTERFACE,
        "tests/unit/test_readiness_real.py::TestRealReadiness::test_candidate_rejects_unknown_backing_ref",
        "an out-of-projection backing reference must not enter the materializer projection",
    ),
    RequirementImpact(
        "EVH-021",
        "evaluation-hardening",
        StableSeam.NODE_INTERFACE,
        "tests/unit/test_evidence_judgment_calibration.py::test_evidence_judgment_corpus_has_two_labeled_cases_per_branch_with_declared_bounds",
        "readiness judgment labels must remain bounded and distinct from deterministic bridge conformance",
    ),
    RequirementImpact(
        "FID-001",
        "final-delivery-node",
        StableSeam.NODE_INTERFACE,
        (
            "tests/unit/test_final_delivery_real.py::TestRealFinalDelivery::"
            "test_renders_only_plan_text_and_keeps_completion_gate_owned"
        ),
        "a layout candidate cannot supply report prose or bypass deterministic rendering of the admitted plan",
    ),
    RequirementImpact(
        "FID-002",
        "final-delivery-node",
        StableSeam.NODE_INTERFACE,
        "tests/unit/test_final_delivery_real.py::TestRealFinalDelivery::test_empty_accepted_evidence_never_publishes",
        "missing accepted evidence cannot publish artifacts or fabricate a passing final-attempt view",
    ),
    RequirementImpact(
        "FID-003",
        "final-delivery-node",
        StableSeam.NODE_INTERFACE,
        (
            "tests/unit/test_final_delivery_real.py::TestRealFinalDelivery::"
            "test_renders_only_plan_text_and_keeps_completion_gate_owned"
        ),
        "candidate ordering cannot alter approved conclusion, uncertainty, or citation-binding content",
    ),
    RequirementImpact(
        "FID-004",
        "final-delivery-node",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        (
            "tests/integration/test_zero_tool_node_conformance.py::"
            "test_final_delivery_scripted_real_bridge_composes_publishes_and_completes_through_gate"
        ),
        "the composer and publisher cannot write completed lifecycle facts before the final gate passes",
    ),
    RequirementImpact(
        "FID-005",
        "final-delivery-node",
        StableSeam.NODE_INTERFACE,
        (
            "tests/unit/test_final_delivery_real.py::TestRealFinalDelivery::"
            "test_missing_declared_dependencies_fail_before_request_construction"
        ),
        "missing narrow reader or publisher capabilities must fail before request construction or model invocation",
    ),
    RequirementImpact(
        "NAC-009",
        "node-agent-capabilities",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_node_agent_capability_cohort.py::test_cohort_evidence_matrix_has_two_collected_claims_per_branch",
        "the final composer cannot inherit another branch's capability or aggregate deterministic evidence",
    ),
    RequirementImpact(
        "NPC-007",
        "node-prompt-catalog",
        StableSeam.NODE_INTERFACE,
        ("tests/graph/test_cognitive_program_evidence.py::test_cognitive_program_composition[final-delivery/composer]"),
        "the final composer catalog projection cannot diverge from its production request builder and capability",
    ),
    RequirementImpact(
        "NOA-013",
        "node-agent-runtime",
        StableSeam.RUNTIME_INTEGRATION,
        ("tests/unit/test_node_agent_bridge.py::test_cognitive_program_guardrail_admission[final-delivery/composer]"),
        "the final composer cannot reach model dispatch with a widened tool window or mismatched capability posture",
    ),
    RequirementImpact(
        "CPE-003",
        "cognitive-program-evidence",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_node_agent_capability_cohort.py::test_cognitive_program_evidence_matrix_closes_the_current_catalog",
        "the exact direct-branch ledger cannot omit or aggregate the final-delivery composer row",
    ),
    RequirementImpact(
        "EVH-022",
        "evaluation-hardening",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        (
            "tests/integration/test_zero_tool_node_conformance.py::"
            "test_final_delivery_scripted_real_bridge_rejects_plan_violation_before_publication"
        ),
        "scripted workflow conformance cannot let a plan-violating candidate publish or bypass the final gate",
    ),
    RequirementImpact(
        "EVH-022",
        "evaluation-hardening",
        StableSeam.NODE_INTERFACE,
        (
            "tests/unit/test_final_composition_calibration.py::"
            "test_final_composition_corpus_has_normal_and_highest_risk_cases_with_declared_bounds"
        ),
        "the labeled composition corpus must retain its exact two-case denominator, bounds, and preservation rubric",
    ),
    RequirementImpact(
        "EVH-022",
        "evaluation-hardening",
        StableSeam.NODE_INTERFACE,
        (
            "tests/live/test_final_composition_live_calibration.py::"
            "test_live_final_composition_calibration[calibrate-final-composition-normal]"
        ),
        "only a selected credentialed production-bridge invocation can assess the model's preferred-layout choice",
        (
            "Credentialed model judgment is supplemental; deterministic tests separately prove exact text and "
            "citation preservation plus the absence of publication and lifecycle authority."
        ),
    ),
    RequirementImpact(
        "EVH-011",
        "evaluation-hardening",
        StableSeam.DOMAIN_ENGINE,
        "tests/contract/test_asset_checker_contract.py::test_requirement_impact_rejects_duplicate_risk_and_uncollected_selector",
        "evidence metadata cannot overclaim stale or duplicate proof",
    ),
    RequirementImpact(
        "RER-003",
        "research-run-experience",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/contract/test_run_experience_contract.py::test_unavailable_result_clears_the_local_handle_and_offers_only_a_fresh_start",
        "a local invalid-choice denial must retain the validated suspension without publishing or leaking input",
    ),
    RequirementImpact(
        "RER-003",
        "research-run-experience",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/contract/test_run_experience_contract.py::test_malformed_result_fails_closed_without_creating_a_control_projection",
        "a malformed denial carrying lifecycle fields must not bind a session or fabricate a terminal result",
    ),
    RequirementImpact(
        "WFO-001",
        "workflow-failure-outcomes",
        StableSeam.DOMAIN_ENGINE,
        "tests/domain/test_workflow_outcomes.py::test_known_node_problem_is_preserved_without_exposing_result_payload",
        "normalized known failures retain their safe category without retaining a result payload",
    ),
    RequirementImpact(
        "WFO-001",
        "workflow-failure-outcomes",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        "tests/integration/test_topic_planning_lifecycle.py::test_topic_planning_rejects_missing_selected_bundle_before_agent_invocation",
        "a direct phase timeout retains one bounded incident through lifecycle and session projection",
    ),
    RequirementImpact(
        "WFO-001",
        "workflow-failure-outcomes",
        StableSeam.DOMAIN_ENGINE,
        "tests/domain/test_workflow_outcomes.py::test_controller_provider_diagnostic_reference_uses_the_shared_timeout_origin_identity",
        "controller-derived failures use the same role-bound timeout-origin identity as direct callers",
    ),
    RequirementImpact(
        "HIN-001",
        "hitl1-node",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_hitl1_node.py::test_retry_timeout_origins_remain_in_their_trigger_and_final_roles",
        "retry-trigger and final timeout origins cannot collapse into one terminal observation",
    ),
    RequirementImpact(
        "HIN-013",
        "hitl1-node",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_hitl1_prompts.py::test_initial_and_repair_brief_descriptors_remain_strict_parser_compatible",
        "model-visible brief fields, enum values, and bounds cannot drift from strict parser admission",
    ),
    RequirementImpact(
        "HIN-013",
        "hitl1-node",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_hitl1_node.py::test_brief_lifecycle_field_is_repaired_without_route_authority",
        "an invalid brief candidate cannot publish profile or checkpoint authority after bounded repair",
    ),
    RequirementImpact(
        "RDO-001",
        "run-bundle-discovery-and-operations",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/integration/test_demo_sessions.py::test_inspect_command_reads_only_an_existing_selected_bundle",
        "the inspection command must resolve only one existing selected Bundle without invoking execution",
    ),
    RequirementImpact(
        "RER-013",
        "research-run-experience",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/contract/test_run_experience_failures.py::test_admitted_terminal_diagnostic_has_no_external_support_fallback",
        "a supplied diagnostic reference must be written before any retained projection cites it",
    ),
    RequirementImpact(
        "DRH-006",
        "deep-research-harness-run-bundles",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/integration/test_session_operations_lifecycle.py::test_deleted_bundle_is_unavailable_and_fresh_start_is_independent",
        "a deleted Bundle cannot reopen or prevent an independent fresh Run",
    ),
    RequirementImpact(
        "RER-009",
        "research-run-experience",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        "tests/integration/test_demo_run_update_adapters.py::test_shared_failure_never_leaks_raw_exception_into_either_adapter",
        "a failed bundle publication must retain the original reference and observed origin roles "
        "in its legal fallback",
    ),
    RequirementImpact(
        "REC-005",
        "research-cli-onboarding",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        "tests/integration/test_demo_run_update_adapters.py::test_standalone_adapters_render_the_same_retained_observation",
        "CLI and TUI must derive one module-local inspection action from the shared session view",
    ),
    RequirementImpact(
        "REC-005",
        "research-cli-onboarding",
        StableSeam.PUBLIC_ENTRY,
        "tests/contract/test_demo_commands.py::test_retained_observation_documentation_uses_the_canonical_inspection_command",
        "operator documentation could retain a one-argument command that the shared renderer does not publish",
    ),
    RequirementImpact(
        "REC-006",
        "research-cli-onboarding",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        "tests/integration/test_demo_run_update_adapters.py::test_standalone_adapters_render_the_same_retained_observation",
        "provider-terminal presentation cannot turn an inspection command into recovery authority",
    ),
    RequirementImpact(
        "REC-006",
        "research-cli-onboarding",
        StableSeam.PUBLIC_ENTRY,
        "tests/contract/test_demo_commands.py::test_retained_observation_documentation_uses_the_canonical_inspection_command",
        "operator documentation could present a retired inspection spelling as a recovery-capable alternate route",
    ),
    RequirementImpact(
        "REC-002",
        "research-cli-onboarding",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        "tests/integration/test_demo_real.py::test_cli_preserves_typed_terminal_category_without_leaking_source_text[structured-output-terminal]",
        "a non-provider terminal category cannot be replaced with untrusted source text",
    ),
    RequirementImpact(
        "REC-006",
        "research-cli-onboarding",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        "tests/integration/test_demo_real.py::test_cli_preserves_typed_terminal_category_without_leaking_source_text[structured-output-terminal]",
        "a typed terminal must retain only its existing legal next action without claiming resume",
    ),
    RequirementImpact(
        "WFO-002",
        "workflow-failure-outcomes",
        StableSeam.DOMAIN_ENGINE,
        "tests/contract/test_workflow_node_inventory.py::test_every_discovered_owner_has_success_and_failure_outcome_evidence",
        "syntax-discovered model owners fail closed without declared phase, journal, and projection evidence",
    ),
    RequirementImpact(
        "CPE-001",
        "cognitive-program-evidence",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_node_agent_capability_cohort.py::test_cognitive_program_evidence_matrix_closes_the_current_catalog",
        "the twenty-branch ledger cannot omit readiness, final delivery, or a critic branch or replace an exact "
        "catalog identity with a group",
    ),
    RequirementImpact(
        "CPE-004",
        "cognitive-program-evidence",
        StableSeam.NODE_INTERFACE,
        (
            "tests/contract/test_cognitive_program_board.py::"
            "test_board_closes_exact_current_node_branch_and_calibration_denominators"
        ),
        "the exact eleven-node, twenty-branch, and forty-one-case denominators cannot substitute for one another",
    ),
    RequirementImpact(
        "CPE-002",
        "cognitive-program-evidence",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_node_agent_capability_cohort.py::test_cognitive_program_evidence_matrix_closes_the_current_catalog",
        "a branch cannot close deterministic evidence with an uncollected, wrong-seam, or obsolete aggregate claim",
    ),
    RequirementImpact(
        "NPC-006",
        "node-prompt-catalog",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_node_agent_capability_cohort.py::test_cognitive_program_evidence_matrix_closes_the_current_catalog",
        "the catalog's synthetic branch composition cannot diverge from the ledger's exact builder and capability join",
    ),
    RequirementImpact(
        "NAC-008",
        "node-agent-capabilities",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_node_agent_capability_cohort.py::test_cognitive_program_evidence_matrix_closes_the_current_catalog",
        "a review row cannot assign a capability or deterministic admission handoff to the wrong direct branch",
    ),
    RequirementImpact(
        "NOA-012",
        "node-agent-runtime",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_node_agent_bridge.py::test_cognitive_program_guardrail_admission[wave0/worker]",
        "a required worker tool window cannot bypass capability and execution-policy admission before model dispatch",
    ),
    RequirementImpact(
        "EVH-017",
        "evaluation-hardening",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_node_agent_capability_cohort.py::test_cognitive_program_evidence_matrix_closes_the_current_catalog",
        "Wave1 critic materialization and gate guardrails cannot be represented as critic or source-quality evidence",
    ),
    RequirementImpact(
        "EVH-017",
        "evaluation-hardening",
        StableSeam.NODE_INTERFACE,
        (
            "tests/contract/test_cognitive_program_board.py::"
            "test_board_closes_exact_current_node_branch_and_calibration_denominators"
        ),
        "conditional human-decision proof cannot close an active model branch or claim an implemented interaction",
    ),
    RequirementImpact(
        "EVH-023",
        "evaluation-hardening",
        StableSeam.DOMAIN_ENGINE,
        ("tests/contract/test_requirement_evidence_policy.py::test_consolidation_rollout_is_empty_and_review_only"),
        "no selector retirement is accepted or authorized without exact collected requirement-risk replacement",
    ),
    RequirementImpact(
        "HIN-012",
        "hitl1-node",
        StableSeam.NODE_INTERFACE,
        "tests/unit/test_intake_planning_calibration.py::test_calibration_cases_compose_real_zero_tool_branch_requests",
        "calibration prompt composition cannot widen an advisory profile or semantic-intake candidate into authority",
    ),
    RequirementImpact(
        "TOP-007",
        "topic-planning-node",
        StableSeam.NODE_INTERFACE,
        "tests/unit/test_intake_planning_calibration.py::test_calibration_cases_compose_real_zero_tool_branch_requests",
        "calibration prompt composition cannot turn confirmed-profile planning or repair into "
        "topic publication authority",
    ),
    RequirementImpact(
        "EVH-018",
        "evaluation-hardening",
        StableSeam.DOMAIN_ENGINE,
        "tests/unit/test_intake_planning_calibration.py::test_default_deterministic_selection_excludes_the_live_calibration_collection",
        "the dedicated live corpus must remain outside deterministic selection and the canonical canary collection",
    ),
    RequirementImpact(
        "EVH-018",
        "evaluation-hardening",
        StableSeam.NODE_INTERFACE,
        "tests/live/test_intake_planning_live_calibration.py::test_live_intake_and_planning_calibration[calibrate-hitl1-brief-normal]",
        "a selected model invocation must retain stable case and rubric reporting without changing "
        "profile or route authority",
        "Only a credentialed selected invocation can assess the model-candidate judgment rubric; "
        "deterministic tests prove its request and authority boundaries separately.",
    ),
    RequirementImpact(
        "EVH-019",
        "evaluation-hardening",
        StableSeam.DOMAIN_ENGINE,
        "tests/unit/test_evidence_intake_calibration.py::test_default_deterministic_selection_excludes_both_live_calibration_collections",
        "the dedicated evidence-intake corpus must remain separate from deterministic selection and canonical canaries",
    ),
    RequirementImpact(
        "EVH-019",
        "evaluation-hardening",
        StableSeam.NODE_INTERFACE,
        (
            "tests/live/test_evidence_intake_live_calibration.py::"
            "test_live_evidence_intake_calibration[calibrate-evidence-intake-wave0-worker-normal]"
        ),
        "a selected model-and-web invocation must retain exact branch posture and typed rubric reporting "
        "without lifecycle authority",
        "Only a credentialed selected invocation can assess the model-candidate judgment rubric; deterministic "
        "tests prove branch composition and authority boundaries separately.",
    ),
    RequirementImpact(
        "PRS-001",
        "project-structure",
        StableSeam.DOMAIN_ENGINE,
        "tests/contract/test_test_structure_retirement.py::test_retained_test_roots_are_non_empty_and_e2e_has_no_active_surface",
        "retired test scaffolding must not leave an active registry, lane, or suspended-selector gap",
    ),
    RequirementImpact(
        "EVH-005",
        "evaluation-hardening",
        StableSeam.PUBLIC_ENTRY,
        "tests/contract/test_release_suspension.py::test_full_real_selector_is_retained_but_has_no_active_execution_surface",
        "the retained full-real selector must have no active workflow, target, or evidence path",
    ),
    RequirementImpact(
        "EVH-005",
        "evaluation-hardening",
        StableSeam.PUBLIC_ENTRY,
        "tests/contract/test_release_evidence_provenance.py::test_retained_release_provenance_routes_need_no_superseded_report",
        "dated baseline, accepted attestation, and regression-descent routes must remain discoverable "
        "without the retired report",
    ),
    RequirementImpact(
        "PRS-006",
        "project-structure",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_run_session_store.py::test_retired_run_session_store_has_no_compatibility_module",
        "a retired run-session module cannot return as a second structural root or lifecycle authority",
    ),
    RequirementImpact(
        "FSI-001",
        "fixture-source-isolation",
        StableSeam.DOMAIN_ENGINE,
        "tests/contract/test_live_architecture_contract.py::test_production_wheel_excludes_fixture_package",
        "a production wheel could otherwise ship the non-production fixture package",
    ),
    RequirementImpact(
        "FSI-002",
        "fixture-source-isolation",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_topology_and_implementation.py::test_explicit_full_fixture_and_paired_mixed_compositions_preserve_topology_shape",
        "fixture and mixed recipes could otherwise bypass complete explicit catalog composition",
    ),
    RequirementImpact(
        "DPL-003",
        "demo-pipeline",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_demo_core.py::test_demo_recipe_factories_do_not_expose_a_mode_selector",
        "a demo factory could otherwise recover caller-controlled mode selection or an implicit fixture fallback",
    ),
    RequirementImpact(
        "DPL-005",
        "demo-pipeline",
        StableSeam.PUBLIC_ENTRY,
        "tests/scenarios_periodic/test_local_entry_environment.py::test_prepared_entries_preserve_dependency_state_and_keep_launcher_credential_bounded",
        "an explicit install could omit a declared demo extra and leave a supported entry to synchronize it itself",
    ),
    RequirementImpact(
        "DPL-006",
        "demo-pipeline",
        StableSeam.PUBLIC_ENTRY,
        "tests/scenarios_periodic/test_local_entry_environment.py::test_missing_or_incomplete_entry_environment_stops_before_an_adapter",
        "a missing or incomplete project environment could reach a demo adapter or cause implicit synchronization",
    ),
    RequirementImpact(
        "LCP-002",
        "local-configuration-profiles",
        StableSeam.PUBLIC_ENTRY,
        "tests/scenarios_periodic/test_local_entry_environment.py::test_prepared_entries_preserve_dependency_state_and_keep_launcher_credential_bounded",
        "profile-gated workbench readiness could depend on a partial optional-extra environment or mutate it at launch",
    ),
    RequirementImpact(
        "DPL-008",
        "demo-pipeline",
        StableSeam.PUBLIC_ENTRY,
        "tests/contract/test_demo_commands.py::test_demo_commands_keep_fixture_and_real_dependency_boundaries",
        "fixture source could otherwise leak onto a real or production launch path",
    ),
    RequirementImpact(
        "DPL-009",
        "demo-pipeline",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_demo_core.py::test_demo_tavily_retry_classification_is_limited_to_transient_read_failures",
        "only named transient failures may consume the direct read retry budget",
    ),
    RequirementImpact(
        "DPL-009",
        "demo-pipeline",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_demo_core.py::test_demo_tavily_fetch_exhausts_three_transient_read_attempts",
        "a direct Tavily fetch cannot exceed its three attempts, 60-second deadline, or one-/two-second backoff",
    ),
    RequirementImpact(
        "DPL-009",
        "demo-pipeline",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_demo_core.py::test_demo_tavily_cancellation_during_backoff_does_not_start_another_attempt",
        "cancellation during backoff cannot start a later direct provider call",
    ),
    RequirementImpact(
        "RUI-004",
        "runtime-integration",
        StableSeam.PUBLIC_ENTRY,
        "tests/integration/test_research_lifecycle_tool.py::test_public_bundle_lifecycle_completes_after_one_correlated_resume",
        "the default GraphHost could otherwise register a caller-selected or fixture recipe",
    ),
    RequirementImpact(
        "RUI-005",
        "runtime-integration",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_graph_host.py::test_legacy_checkpointer_is_refused_before_action_saver_factory",
        "a legacy deployment section could otherwise reach the generic saver factory and select durability",
    ),
    RequirementImpact(
        "RUI-006",
        "runtime-integration",
        StableSeam.PUBLIC_ENTRY,
        "tests/unit/test_non_interactive.py::test_tool_rejects_the_retired_marker_before_sandbox_or_graph_selection",
        "a retired trusted marker could otherwise initialize runtime resources or fall back to interactive dispatch",
    ),
    RequirementImpact(
        "RUI-006",
        "runtime-integration",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        (
            "tests/blocking_io/test_research_runtime.py::"
            "test_composed_start_persists_policy_once_in_the_selected_bundle_checkpoint"
        ),
        "a later lifecycle action could otherwise replace the selected Bundle checkpoint's admitted policy",
    ),
    RequirementImpact(
        "RUO-001",
        "runtime-operations",
        StableSeam.PUBLIC_ENTRY,
        (
            "tests/unit/test_non_interactive.py::"
            "test_tool_rejects_missing_or_incomplete_non_interactive_policy_before_bundle_publication"
        ),
        "malformed trusted context could otherwise publish a Bundle or bypass interactive admission",
    ),
    RequirementImpact(
        "RUO-001",
        "runtime-operations",
        StableSeam.PUBLIC_ENTRY,
        "tests/unit/test_non_interactive.py::test_tool_rejects_the_retired_marker_before_sandbox_or_graph_selection",
        "a retired trusted marker could otherwise bypass its named interactive-required denial",
    ),
    RequirementImpact(
        "RUO-001",
        "runtime-operations",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        (
            "tests/blocking_io/test_research_runtime.py::"
            "test_composed_start_persists_policy_once_in_the_selected_bundle_checkpoint"
        ),
        "a valid policy could otherwise be lost before the initial graph checkpoint write",
    ),
    RequirementImpact(
        "NOA-005",
        "node-agent-runtime",
        StableSeam.RUNTIME_INTEGRATION,
        (
            "tests/unit/test_node_agent_bridge.py::"
            "test_retired_selected_endpoint_aliases_are_omitted_even_when_they_match_base_url[openai-api-base-only]"
        ),
        "a retired selected-config alias could otherwise become a safe-looking endpoint observation",
    ),
    RequirementImpact(
        "RUO-002",
        "runtime-operations",
        StableSeam.NODE_INTERFACE,
        ("tests/graph/test_hitl1_node.py::test_non_interactive_auto_profile_stays_outside_interactive_confirmation"),
        "HITL1 could otherwise bypass its own admissible profile path without leaving bounded observation evidence",
    ),
    RequirementImpact(
        "RUO-002",
        "runtime-operations",
        StableSeam.NODE_INTERFACE,
        (
            "tests/unit/test_hitl2_real.py::"
            "TestRealHitl2Factory::test_checkpointed_auto_proceed_overrides_recommendation_with_an_observation_marker"
        ),
        "HITL2 could otherwise retain an autonomous rerun recommendation despite checkpointed auto-proceed",
    ),
    RequirementImpact(
        "RER-001",
        "research-run-experience",
        StableSeam.RUNTIME_INTEGRATION,
        (
            "tests/contract/test_run_experience_contract.py::"
            "test_scripted_start_projects_policy_once_and_later_actions_do_not_reinject_it"
        ),
        "a presentation adapter could otherwise omit scripted intent or become a later policy writer",
    ),
    RequirementImpact(
        "RER-001",
        "research-run-experience",
        StableSeam.RUNTIME_INTEGRATION,
        (
            "tests/contract/test_run_experience_contract.py::"
            "test_policy_trace_marker_is_accepted_as_a_safe_observation[hitl1_auto_profile]"
        ),
        "a bounded graph audit marker could otherwise be rejected as a lifecycle control fact",
    ),
    RequirementImpact(
        "REJ-004",
        "run-event-journal",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/integration/test_session_lifecycle_binding.py::test_contained_journal_does_not_reauthorize_a_lost_bundle",
        "a contained Journal could otherwise be mistaken for authority after Bundle loss",
    ),
    RequirementImpact(
        "DEC-003",
        "deployment-configuration",
        StableSeam.PUBLIC_ENTRY,
        "tests/contract/test_public_skill.py::test_committed_skill_is_one_focused_cognitive_controller_workflow",
        "the public skill could otherwise advertise fixture execution instead of the fixed all-real lifecycle",
    ),
    RequirementImpact(
        "DEC-004",
        "deployment-configuration",
        StableSeam.PUBLIC_ENTRY,
        "tests/contract/test_public_skill.py::test_agent_soul_is_stable_identity_and_honesty_not_a_second_action_workflow",
        "the provisioned Agent SOUL could otherwise duplicate the controller's action workflow",
    ),
    RequirementImpact(
        "RCF-001",
        "research-confirmation",
        StableSeam.DOMAIN_ENGINE,
        "tests/domain/test_research_confirmation.py::test_unconfirmed_model_proposal_remains_one_outstanding_decision",
        "an advisory model proposal could otherwise become accepted research facts without a current user decision",
    ),
    RequirementImpact(
        "HIN-014",
        "hitl1-node",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_hitl1_node.py::test_natural_confirmation_writes_current_proposal_and_routes_accepted",
        (
            "a correlated natural confirmation could otherwise bypass the admitted current proposal "
            "before profile publication"
        ),
    ),
    RequirementImpact(
        "RER-012",
        "research-run-experience",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        "tests/integration/test_demo_run_update_adapters.py::test_standalone_adapters_render_every_complete_proposal_line_before_control",
        "a material proposal constraint could otherwise disappear before the person selects the existing control",
    ),
    RequirementImpact(
        "RER-014",
        "research-run-experience",
        StableSeam.RUNTIME_INTEGRATION,
        (
            "tests/contract/test_run_experience_contract.py::"
            "test_available_active_result_projects_a_safe_non_terminal_fault[different-start-conflict]"
        ),
        "an available active Bundle could otherwise be presented as an invalid protocol or a false terminal outcome",
    ),
    RequirementImpact(
        "RER-014",
        "research-run-experience",
        StableSeam.RUNTIME_INTEGRATION,
        (
            "tests/contract/test_run_experience_contract.py::"
            "test_available_active_result_projects_a_safe_non_terminal_fault[status-observes-active-bundle]"
        ),
        "a status result for an active Bundle could otherwise invent a resume prompt or terminal result",
    ),
    RequirementImpact(
        "EVH-024",
        "evaluation-hardening",
        StableSeam.PUBLIC_ENTRY,
        "tests/unit/test_release_control_plane.py::test_release_runner_reports_the_complete_model_led_smoke_evidence",
        "a release report could otherwise omit bounded proof that the model-led smoke path completed",
    ),
    RequirementImpact(
        "EVH-024",
        "evaluation-hardening",
        StableSeam.PUBLIC_ENTRY,
        (
            "tests/unit/test_release_control_plane.py::"
            "test_release_bundle_adapter_reauthorizes_the_public_id_before_observing_artifacts"
        ),
        "a release runner could otherwise observe a matching result without reauthorizing its selected Bundle",
    ),
    RequirementImpact(
        "EVH-024",
        "evaluation-hardening",
        StableSeam.PUBLIC_ENTRY,
        (
            "tests/unit/test_release_control_plane.py::"
            "test_release_bundle_adapter_fails_on_bundle_loss_before_any_store_observation"
        ),
        "a deleted selected Bundle could otherwise reach an artifact or retained-record fallback",
    ),
    RequirementImpact(
        "DPL-011",
        "demo-pipeline",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_demo_core.py::test_explicit_real_demo_profile_is_single_safe_runtime_configuration",
        (
            "registry ordering could otherwise choose a credential-backed profile or "
            "expose its configuration at composition"
        ),
    ),
    RequirementImpact(
        "DPL-012",
        "demo-pipeline",
        StableSeam.PUBLIC_ENTRY,
        (
            "tests/contract/test_demo_commands.py::"
            "test_embedded_smoke_calibration_documents_an_explicit_observational_procedure"
        ),
        (
            "operator guidance could otherwise invoke an unselected profile or treat "
            "one diagnostic run as a default decision"
        ),
    ),
    RequirementImpact(
        "DPL-013",
        "demo-pipeline",
        StableSeam.RUNTIME_INTEGRATION,
        (
            "tests/unit/test_demo_core.py::"
            "test_all_real_demo_adapters_use_fresh_scopes_while_fixture_scope_remains_stable"
        ),
        (
            "a later all-real demo could otherwise select an earlier process's active Bundle "
            "through its stable local scope"
        ),
    ),
    RequirementImpact(
        "REJ-006",
        "run-event-journal",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_run_observation_store.py::test_admitted_journal_retains_profile_only_on_matching_admission_and_summary",
        (
            "execution-profile provenance could otherwise escape its admitted Bundle "
            "Journal boundary or include sensitive configuration"
        ),
    ),
    RequirementImpact(
        "REJ-007",
        "run-event-journal",
        StableSeam.RUNTIME_INTEGRATION,
        (
            "tests/integration/test_wave0_work_units.py::"
            "test_one_bundle_journal_retains_topic_planning_and_wave0_validation_as_observations"
        ),
        "cross-node validation evidence could otherwise leak candidate detail or become checkpoint and admission state",
    ),
    RequirementImpact(
        "NOA-015",
        "node-agent-runtime",
        StableSeam.RUNTIME_INTEGRATION,
        (
            "tests/unit/test_node_agent_bridge.py::"
            "test_bridge_uses_unknown_for_untyped_budget_stop_and_keeps_non_budget_failures_unattributed"
        ),
        "raw budget-stop detail could otherwise escape the bridge or be attributed to an unrelated normalized failure",
    ),
    RequirementImpact(
        "TOP-009",
        "topic-planning-node",
        StableSeam.NODE_INTERFACE,
        (
            "tests/graph/test_topic_planning_node.py::"
            "test_invalid_initial_topic_plan_then_repair_records_ordered_closed_codes"
        ),
        "planner parser evidence could otherwise lose initial-versus-repair order or retain an untrusted draft",
    ),
    RequirementImpact(
        "WAN-010",
        "wave0-node",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/integration/test_wave0_work_units.py::test_real_wave0_valid_initial_parser_observation_is_closed_and_correlated",
        "Wave0 parser evidence could otherwise be lost before candidate admission or lose work/attempt correlation",
    ),
    RequirementImpact(
        "REJ-002",
        "run-event-journal",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_run_observation_store.py::test_v3_journal_retains_redacted_shape_and_post_candidate_facts",
        "a Journal event could conflate a worker response boundary with a later submit rejection",
    ),
    RequirementImpact(
        "REJ-004",
        "run-event-journal",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_run_observation_store.py::test_v3_journal_retains_redacted_shape_and_post_candidate_facts",
        "read-only inspection could expose response content rather than closed diagnostic facts",
    ),
    RequirementImpact(
        "REJ-006",
        "run-event-journal",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_run_observation_store.py::test_v3_journal_retains_redacted_shape_and_post_candidate_facts",
        "a versioned Journal update could drop safe profile provenance while recording a new validation fact",
    ),
    RequirementImpact(
        "REJ-007",
        "run-event-journal",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_run_observation_store.py::test_v3_journal_retains_redacted_shape_and_post_candidate_facts",
        "a v3 validation projection could retain parser detail instead of its closed shape and canonical code",
    ),
    RequirementImpact(
        "WAN-011",
        "wave0-node",
        StableSeam.NODE_INTERFACE,
        "tests/graph/test_wave0_worker.py::test_wave0_initial_and_repair_requests_expose_the_same_closed_completion_contract",
        "initial and repair prompts could drift into different output envelopes or tool postures",
    ),
    RequirementImpact(
        "WAN-012",
        "wave0-node",
        StableSeam.RUNTIME_INTEGRATION,
        (
            "tests/integration/test_wave0_work_units.py::"
            "test_real_wave0_post_candidate_submission_validation_does_not_enter_repair"
        ),
        "a later submit rejection could be mislabeled as a worker repair or re-enter model recovery",
    ),
    RequirementImpact(
        "WON-011",
        "wave1-node",
        StableSeam.NODE_INTERFACE,
        (
            "tests/unit/test_wave1_critic_prompts.py::TestWave1LocalCriticPrompts::"
            "test_worker_and_repair_render_only_bounded_assignment_and_closed_feedback"
        ),
        "initial and repair requests could lose the shared closed final envelope while retaining stale tool context",
    ),
    RequirementImpact(
        "WON-012",
        "wave1-node",
        StableSeam.RUNTIME_INTEGRATION,
        (
            "tests/integration/test_wave1_work_units.py::"
            "test_real_wave1_post_candidate_submission_validation_does_not_enter_repair"
        ),
        "a parser-accepted candidate could conceal its later deterministic rejection or trigger a second repair",
    ),
    RequirementImpact(
        "WOU-012",
        "work-unit-kernel",
        StableSeam.RUNTIME_INTEGRATION,
        (
            "tests/graph/test_work_unit_component.py::"
            "test_component_records_one_post_candidate_fact_for_submission_rejection"
        ),
        (
            "successful submit paths could fabricate a failure fact or rejected candidates "
            "could lose their distinct boundary"
        ),
    ),
    RequirementImpact(
        "EVH-030",
        "evaluation-hardening",
        StableSeam.RUNTIME_INTEGRATION,
        (
            "tests/unit/test_evidence_intake_calibration.py::"
            "test_offline_evidence_intake_branches_are_explicit_profile_bundle_bound_and_redacted"
        ),
        "calibration setup could resolve a bridge without a selected Bundle, profile provenance, or redacted Journal",
    ),
    RequirementImpact(
        "EVH-030",
        "evaluation-hardening",
        StableSeam.NODE_INTERFACE,
        (
            "tests/live/test_evidence_intake_live_calibration.py::"
            "test_live_evidence_intake_calibration[calibrate-evidence-intake-wave0-worker-normal]"
        ),
        "only a credentialed explicit-profile branch call can observe a real model's final response distribution",
        (
            "The deterministic Bundle-bound proof covers authority and redaction; this opt-in "
            "call covers only model output behavior."
        ),
    ),
    RequirementImpact(
        "GAK-004",
        "gate-kernel",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_retained_checkpoint_cutover.py::test_registered_checkpoint_migration_writes_reloads_and_replays_current_gate_facts",
        "checkpoint cutover could leave a second repair counter or reset gate-owned attempt and budget facts",
    ),
    RequirementImpact(
        "REG-011",
        "research-graph-lifecycle",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_retained_bundle_cutover.py::test_unregistered_repair_exhausted_bundle_is_unavailable_before_status_projection",
        "an incompatible retained Bundle could be projected or replaced before the lifecycle schema guard",
    ),
    RequirementImpact(
        "DRH-002",
        "deep-research-harness-run-bundles",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_retained_bundle_cutover.py::test_registered_terminal_migration_preserves_only_identity_and_terminal_status",
        "a terminal migration could lose Bundle identity/status or invent a replacement lifecycle reason",
    ),
    RequirementImpact(
        "REJ-002",
        "run-event-journal",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_retained_journal_cutover.py::test_partial_or_unregistered_old_journal_is_unavailable_before_append_or_projection",
        "an old or partial Journal could be appended or projected as current retained evidence",
    ),
    RequirementImpact(
        "RER-009",
        "research-run-experience",
        StableSeam.LIFECYCLE_MIXED_GRAPH,
        "tests/unit/test_retained_terminal_result_cutover.py::test_persisted_terminal_without_location_rejects_before_any_projection",
        "a missing terminal location could be guessed by a participant or become an external recovery path",
    ),
    RequirementImpact(
        "RTO-001",
        "runtime-observability",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_events.py::test_safe_observation_schema_rejects_unsafe_fields",
        "an owner-local log projection could admit free-form or sensitive fields instead of the closed safe record",
    ),
    RequirementImpact(
        "RTO-003",
        "runtime-observability",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_runtime_adapter.py::test_adapt_keeps_trace_binding_with_deerflow_logging",
        "application trace binding could become a Bundle selector or fabricated durable correlation",
    ),
    RequirementImpact(
        "REJ-005",
        "run-event-journal",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_events.py::test_safe_observation_schema_rejects_unsafe_fields",
        "a raw stream-writer payload could become a second unvalidated Journal-like progress record",
    ),
    RequirementImpact(
        "RUI-002",
        "runtime-integration",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_runtime_adapter.py::test_adapt_keeps_trace_binding_with_deerflow_logging",
        "untrusted trace correlation could cross the runtime boundary as identity or recovery authority",
    ),
    RequirementImpact(
        "GOO-001",
        "gateway-operator-observer",
        StableSeam.RUNTIME_INTEGRATION,
        (
            "tests/unit/test_gateway_observer.py::"
            "test_observer_creates_one_fresh_thread_then_reuses_only_its_public_thread_for_follow_up"
        ),
        (
            "a caller or prior turn could choose the thread instead of the current observer owning "
            "fresh-start and follow-up use"
        ),
    ),
    RequirementImpact(
        "GOO-001",
        "gateway-operator-observer",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_gateway_observer.py::test_http_client_uses_only_fixed_public_thread_and_stream_shapes",
        "the observer could drift to a proxy, private API, caller-selected origin, or non-public request envelope",
    ),
    RequirementImpact(
        "GOO-002",
        "gateway-operator-observer",
        StableSeam.RUNTIME_INTEGRATION,
        (
            "tests/unit/test_gateway_observer.py::"
            "test_valid_custom_progress_stays_withheld_while_only_typed_tool_result_returns"
        ),
        (
            "a valid but unproven custom event could bypass the forwarding proof and become a "
            "lifecycle or presentation authority"
        ),
    ),
    RequirementImpact(
        "GOO-002",
        "gateway-operator-observer",
        StableSeam.RUNTIME_INTEGRATION,
        ("tests/live/test_gateway_forwarding_proof.py::test_gateway_forwarding_proof"),
        (
            "nested forwarding is unproven until a bounded configured-Gateway probe receives a "
            "predecessor-owned progress event on the public SSE custom channel with matching "
            "thread/run/Bundle correlation"
        ),
        escalation_rationale=(
            "the deterministic decoder fixtures cannot prove that the reflected tool's "
            "predecessor-owned event actually reaches the public SSE custom channel, so one "
            "bounded live probe is the only smallest sufficient proof"
        ),
    ),
    RequirementImpact(
        "GOO-002",
        "gateway-operator-observer",
        StableSeam.RUNTIME_INTEGRATION,
        "tests/unit/test_gateway_observer.py::test_end_or_assistant_prose_cannot_manufacture_a_lifecycle_result",
        "outer stream end or assistant prose could be mistaken for a typed Deep Research outcome",
    ),
    RequirementImpact(
        "GOO-003",
        "gateway-operator-observer",
        StableSeam.PUBLIC_ENTRY,
        (
            "tests/contract/test_local_profiles.py::"
            "test_gateway_observer_readiness_uses_only_the_validated_profile_environment_and_check_mode"
        ),
        (
            "observer readiness could mutate configuration, inspect credentials, or admit a profile "
            "without its selected public entry check"
        ),
    ),
    RequirementImpact(
        "GOO-003",
        "gateway-operator-observer",
        StableSeam.PUBLIC_ENTRY,
        (
            "tests/contract/test_local_profiles.py::"
            "test_profile_child_capture_is_owner_only_unique_and_announced_before_child_start"
        ),
        (
            "process logging could leak permissions, race concurrent launches, or alter the Gateway "
            "child command and inherited stderr"
        ),
    ),
    RequirementImpact(
        "DPL-004",
        "demo-pipeline",
        StableSeam.PUBLIC_ENTRY,
        (
            "tests/integration/test_gateway_demo_real.py::"
            "test_default_real_cli_requires_profile_and_rejects_scripted_before_profile_or_gateway_work"
        ),
        "Gateway-default scripted policy or a missing profile could open a public turn before explicit admission",
    ),
    RequirementImpact(
        "DPL-004",
        "demo-pipeline",
        StableSeam.PUBLIC_ENTRY,
        (
            "tests/integration/test_gateway_demo_real.py::"
            "test_default_real_cli_uses_only_ready_profile_gateway_transport_without_local_provider_or_graph"
        ),
        (
            "the default CLI could silently retain local provider preflight or construct an embedded "
            "graph instead of the ready Gateway path"
        ),
    ),
    RequirementImpact(
        "RED-001",
        "research-demo-tui",
        StableSeam.PUBLIC_ENTRY,
        ("tests/integration/test_gateway_demo_tui.py::test_gateway_tui_requires_profile_before_client_or_local_graph"),
        "the real TUI could create a client or local graph before its selected Gateway profile is ready",
    ),
    RequirementImpact(
        "RED-001",
        "research-demo-tui",
        StableSeam.PUBLIC_ENTRY,
        (
            "tests/integration/test_gateway_demo_tui.py::"
            "test_gateway_tui_hides_cancel_disables_reentry_and_never_renders_fault_as_completion"
        ),
        "Gateway TUI controls or a transport fault could create a local cancellation or synthetic completion claim",
    ),
)


def validate_requirement_impacts(
    impacts: tuple[RequirementImpact, ...],
    *,
    claims: tuple[TestEvidenceClaim, ...],
    known_requirement_ids: set[str],
    collected_selectors: set[str],
) -> None:
    """Reject impact metadata that cannot prove a smallest distinct risk."""
    claim_by_selector = {claim.selector: claim for claim in claims}
    by_requirement: dict[str, list[RequirementImpact]] = {}
    errors: list[str] = []
    for impact in impacts:
        if impact.requirement_id not in known_requirement_ids:
            errors.append(f"unknown impact requirement: {impact.requirement_id}")
        if not impact.owning_contract or not impact.risk:
            errors.append(f"invalid impact metadata: {impact.requirement_id}")
        if not isinstance(impact.seam, StableSeam):
            errors.append(f"invalid impact seam: {impact.requirement_id}")
        if impact.selector not in collected_selectors:
            errors.append(f"impact selector is not collected: {impact.selector}")
        claim = claim_by_selector.get(impact.selector)
        if claim is None:
            errors.append(f"impact selector has no claim: {impact.selector}")
        elif claim.seam is not impact.seam:
            errors.append(f"impact seam does not match claim: {impact.selector}")
        by_requirement.setdefault(impact.requirement_id, []).append(impact)

    for requirement_id, entries in by_requirement.items():
        if len(entries) > 3:
            errors.append(f"impact layer budget exceeded: {requirement_id}")
        risks = [entry.risk for entry in entries]
        if len(risks) != len(set(risks)):
            errors.append(f"duplicate impact risk: {requirement_id}")
        for entry in entries:
            claim = claim_by_selector.get(entry.selector)
            if (
                claim is not None
                and claim.asset_class
                in {
                    AssetClass.LIVE_BEHAVIORAL_EVALUATION,
                }
                and not entry.escalation_rationale
            ):
                errors.append(f"missing impact escalation rationale: {entry.selector}")
    if errors:
        raise RequirementEvidenceError("\n".join(errors))


def validate_consolidation_decisions(
    decisions: tuple[ConsolidationDecision, ...],
    *,
    claims: tuple[TestEvidenceClaim, ...],
    requirement_impacts: tuple[RequirementImpact, ...],
    collected_selectors: set[str],
) -> None:
    """Require exact collected replacement proof for every displaced named risk."""

    claims_by_id = {claim.claim_id: claim for claim in claims}
    impacts_by_selector: dict[str, list[RequirementImpact]] = {}
    for impact in requirement_impacts:
        impacts_by_selector.setdefault(impact.selector, []).append(impact)

    seen_displaced: set[str] = set()
    for decision in decisions:
        if decision.displaced_claim_id in seen_displaced:
            raise RequirementEvidenceError(f"duplicate displaced claim: {decision.displaced_claim_id}")
        seen_displaced.add(decision.displaced_claim_id)

        basis = decision.preservation_basis.strip().lower()
        aggregate_terms = ("count", "marker", "directory", "line coverage", "coverage percentage")
        if not basis or (
            any(term in basis for term in aggregate_terms) and not ("requirement" in basis and "risk" in basis)
        ):
            raise RequirementEvidenceError("aggregate consolidation basis forbidden")

        displaced = claims_by_id.get(decision.displaced_claim_id)
        if displaced is None:
            raise RequirementEvidenceError(f"unknown displaced claim: {decision.displaced_claim_id}")
        if displaced.selector != decision.displaced_selector:
            raise RequirementEvidenceError(f"displaced selector mismatch: {decision.displaced_claim_id}")
        if displaced.selector not in collected_selectors:
            raise RequirementEvidenceError(f"uncollected displaced claim: {decision.displaced_claim_id}")

        displaced_impacts = tuple(impacts_by_selector.get(displaced.selector, ()))
        if not displaced_impacts:
            raise RequirementEvidenceError(f"displaced claim has no requirement impact: {decision.displaced_claim_id}")
        displaced_pairs = {(impact.requirement_id, impact.risk): impact for impact in displaced_impacts}
        if len(displaced_pairs) != len(displaced_impacts):
            raise RequirementEvidenceError(f"duplicate displaced requirement-risk pair: {decision.displaced_claim_id}")
        for impact in displaced_impacts:
            if impact.requirement_id not in displaced.requirement_ids:
                raise RequirementEvidenceError(
                    f"displaced claim does not own requirement: {decision.displaced_claim_id} {impact.requirement_id}"
                )

        covered_pairs: set[tuple[str, str]] = set()
        seen_replacements: set[tuple[str, str, str]] = set()
        for replacement in decision.replacements:
            retained = claims_by_id.get(replacement.retained_claim_id)
            if retained is None:
                raise RequirementEvidenceError(f"unknown retained claim: {replacement.retained_claim_id}")
            if retained.selector not in collected_selectors:
                raise RequirementEvidenceError(f"uncollected retained claim: {replacement.retained_claim_id}")
            if replacement.retained_claim_id == decision.displaced_claim_id:
                raise RequirementEvidenceError(f"self replacement forbidden: {decision.displaced_claim_id}")
            if replacement.requirement_id not in retained.requirement_ids:
                raise RequirementEvidenceError(
                    f"replacement claim does not own requirement: "
                    f"{replacement.retained_claim_id} {replacement.requirement_id}"
                )

            pair = (replacement.requirement_id, replacement.risk)
            displaced_impact = displaced_pairs.get(pair)
            if displaced_impact is None:
                raise RequirementEvidenceError(
                    f"replacement does not map displaced requirement-risk: "
                    f"{replacement.requirement_id} {replacement.risk}"
                )
            retained_impact = next(
                (
                    impact
                    for impact in impacts_by_selector.get(retained.selector, ())
                    if (impact.requirement_id, impact.risk) == pair
                    and impact.owning_contract == displaced_impact.owning_contract
                ),
                None,
            )
            if retained_impact is None:
                raise RequirementEvidenceError(
                    f"retained requirement-risk impact missing: "
                    f"{replacement.retained_claim_id} {replacement.requirement_id} {replacement.risk}"
                )

            replacement_identity = (
                replacement.retained_claim_id,
                replacement.requirement_id,
                replacement.risk,
            )
            if replacement_identity in seen_replacements:
                raise RequirementEvidenceError(f"duplicate consolidation replacement: {replacement.retained_claim_id}")
            seen_replacements.add(replacement_identity)

            metadata_differs = (
                retained.seam is not displaced.seam
                or retained.asset_class is not displaced.asset_class
                or retained.authenticity is not displaced.authenticity
            )
            rationale = replacement.metadata_difference_rationale
            if metadata_differs and (rationale is None or not rationale.strip()):
                raise RequirementEvidenceError(
                    f"replacement metadata difference requires rationale: {replacement.retained_claim_id}"
                )
            if rationale is not None and (not rationale.strip() or len(rationale) > 512):
                raise RequirementEvidenceError(
                    f"replacement metadata difference rationale invalid: {replacement.retained_claim_id}"
                )
            covered_pairs.add(pair)

        missing_pairs = set(displaced_pairs) - covered_pairs
        if missing_pairs:
            missing = ", ".join(f"{requirement_id}:{risk}" for requirement_id, risk in sorted(missing_pairs))
            raise RequirementEvidenceError(f"missing displaced requirement-risk replacement: {missing}")


def validate_requirement_evidence(
    *,
    policy: tuple[RequirementEvidenceRule, ...],
    claims: tuple[TestEvidenceClaim, ...],
    alive_requirement_ids: set[str],
    known_requirement_ids: set[str] | None = None,
    deterministic_impl_ids: set[str],
    collected_selectors: set[str],
) -> None:
    known_requirement_ids = alive_requirement_ids if known_requirement_ids is None else known_requirement_ids
    missing_impl = sorted(alive_requirement_ids - deterministic_impl_ids)
    if missing_impl:
        raise RequirementEvidenceError(f"missing deterministic @impl: {','.join(missing_impl)}")
    unknown_impl = sorted(deterministic_impl_ids - known_requirement_ids)
    if unknown_impl:
        raise RequirementEvidenceError(f"unknown deterministic @impl: {','.join(unknown_impl)}")

    seen_rules: set[str] = set()
    for rule in policy:
        if rule.requirement_id not in alive_requirement_ids:
            raise RequirementEvidenceError(f"unknown policy requirement: {rule.requirement_id}")
        if rule.requirement_id in seen_rules:
            raise RequirementEvidenceError(f"duplicate policy requirement: {rule.requirement_id}")
        seen_rules.add(rule.requirement_id)
        matching = tuple(
            claim
            for claim in claims
            if rule.requirement_id in claim.requirement_ids and claim.selector in collected_selectors
        )
        for required in rule.required_evidence:
            if not any(
                claim.asset_class is required.asset_class
                and (required.authenticity is None or claim.authenticity is required.authenticity)
                for claim in matching
            ):
                suffix = f"/{required.authenticity.value}" if required.authenticity is not None else ""
                raise RequirementEvidenceError(
                    f"requirement evidence missing: {rule.requirement_id} {required.asset_class.value}{suffix}"
                )


def collected_deterministic_impl_ids(agent_root: Path, selectors: set[str]) -> set[str]:
    paths = {selector.split("::", 1)[0] for selector in selectors}
    requirement_ids: set[str] = set()
    for relative_path in sorted(paths):
        path = agent_root / relative_path
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        docstrings = [ast.get_docstring(tree, clean=False) or ""]
        docstrings.extend(
            ast.get_docstring(node, clean=False) or ""
            for node in ast.walk(tree)
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        )
        for docstring in docstrings:
            for payload in IMPL_LINE_RE.findall(docstring):
                requirement_ids.update(_expand_requirement_ids(payload))
    return requirement_ids


def _expand_requirement_ids(value: str) -> set[str]:
    ids = set(REQUIREMENT_ID_RE.findall(value))
    for prefix, start, end in REQUIREMENT_RANGE_RE.findall(value):
        if int(start) <= int(end):
            ids.update(f"{prefix}-{number:03d}" for number in range(int(start), int(end) + 1))
    return ids


__all__ = [
    "CONSOLIDATION_DECISIONS",
    "ConsolidationDecision",
    "ConsolidationReplacement",
    "REQUIREMENT_EVIDENCE_POLICY",
    "REQUIREMENT_IMPACTS",
    "RequiredEvidence",
    "RequirementEvidenceError",
    "RequirementEvidenceRule",
    "RequirementImpact",
    "collected_deterministic_impl_ids",
    "validate_consolidation_decisions",
    "validate_requirement_evidence",
    "validate_requirement_impacts",
]
