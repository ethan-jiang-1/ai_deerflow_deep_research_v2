"""Canonical synthetic prompt cases for deterministic review output.

The graph owns node-specific fixture construction. Final prompt rendering remains in
the agents layer, so this registry deliberately returns only ``NodeExecutionRequest``
values and never invokes an agent.

@impl NPC-002
@impl NPC-003
@impl NPC-004
@impl NPC-005
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from deerflow_deep_research.domain.context import NodeExecutionRequest
from deerflow_deep_research.domain.human_interaction import InteractionSubject, ProposalValues
from deerflow_deep_research.domain.readiness import ReadinessReportPlan
from deerflow_deep_research.domain.synthesis import SynthesisEvidence
from deerflow_deep_research.domain.work_units import WorkSpec, compute_work_spec_hash
from deerflow_deep_research.graph.nodes.final_delivery.composer import build_final_delivery_request
from deerflow_deep_research.graph.nodes.hitl1 import prompts as hitl1_prompts
from deerflow_deep_research.graph.nodes.readiness.critic import build_readiness_critic_request
from deerflow_deep_research.graph.nodes.targeted_evidence import prompts as targeted_evidence_prompts
from deerflow_deep_research.graph.nodes.topic_planning import prompts as topic_planning_prompts
from deerflow_deep_research.graph.nodes.wave0 import prompts as wave0_prompts
from deerflow_deep_research.graph.nodes.wave1 import prompts as wave1_prompts
from deerflow_deep_research.graph.nodes.wave2_synthesis import prompts as wave2_synthesis_prompts

SYNTHETIC_FIXTURE_MARKER = "PROMPT_CATALOG_FIXTURE"
VIRTUAL_ATTEMPT_WORKSPACE = "/virtual/deep-research/prompt-catalog/attempt"
_SYNTHETIC_BUNDLE_ID = "b_" + "C" * 43
_SYNTHETIC_SUBMISSION_REF = "h_" + "C" * 43
_QUESTION = f"{SYNTHETIC_FIXTURE_MARKER}: compare grid-scale storage options."
_REPAIR_ERROR = "synthetic_validation_error"
_SYNTHETIC_TOPIC = {
    "topic_id": "prompt-catalog-storage",
    "title": f"{SYNTHETIC_FIXTURE_MARKER}: grid-scale storage",
    "scope": f"{SYNTHETIC_FIXTURE_MARKER}: cost, duration, and deployment trade-offs.",
    "must_answer_bindings": [f"{SYNTHETIC_FIXTURE_MARKER}: which storage options fit the constraints?"],
}


@dataclass(frozen=True)
class PromptCatalogCase:
    """One code-owned prompt-builder variant rendered by the review catalog."""

    case_id: str
    node_name: str
    branch: str
    builder_id: str
    is_repair: bool
    build_request: Callable[[], NodeExecutionRequest]
    attempt_workspace: str = VIRTUAL_ATTEMPT_WORKSPACE

    @property
    def output_path(self) -> str:
        """Return the fixed Markdown path relative to the generated catalog root."""

        return f"{self.case_id}.md"


def _interaction_subject() -> InteractionSubject:
    return InteractionSubject(
        proposal_version=1,
        goal=f"{SYNTHETIC_FIXTURE_MARKER}: decide the research profile.",
        proposal=ProposalValues(
            depth="deep_dive",
            audience="practitioner",
            format="detailed_report",
            cost_tolerance="moderate",
            time_budget="thorough",
            must_answer=(f"{SYNTHETIC_FIXTURE_MARKER}: which storage options fit the constraints?",),
            scope_boundaries=f"{SYNTHETIC_FIXTURE_MARKER}: public evidence only.",
            custom_notes=f"{SYNTHETIC_FIXTURE_MARKER}: show trade-offs clearly.",
        ),
    )


def _planner_inputs() -> topic_planning_prompts.PlannerInputs:
    return topic_planning_prompts.PlannerInputs(
        request_text=_QUESTION,
        research_depth="deep_dive",
        target_audience="practitioner",
        output_format="detailed_report",
        cost_tolerance="moderate",
        time_budget="thorough",
        must_answer_questions=(f"{SYNTHETIC_FIXTURE_MARKER}: which storage options fit the constraints?",),
        degraded_profile=False,
    )


def _wave0_spec() -> WorkSpec:
    payload: dict[str, object] = {
        "schema_version": 1,
        "bundle_id": _SYNTHETIC_BUNDLE_ID,
        "generation": 0,
        "phase": "wave0",
        "work_id": "g0_wave0_w0000",
        "work_ordinal": 0,
        "worker_role": "wave0_intake",
        "scope": (str(_SYNTHETIC_TOPIC["topic_id"]),),
        "result_contract": "wave0.source-intake",
        "result_schema_version": 1,
        "required_outputs": (),
    }
    payload["spec_hash"] = compute_work_spec_hash(payload)
    return WorkSpec.model_validate(payload)


def _synthesis_evidence() -> tuple[SynthesisEvidence, ...]:
    return (
        SynthesisEvidence(
            submission_ref=_SYNTHETIC_SUBMISSION_REF,
            phase="wave1",
            result_contract="wave1.evidence-extraction",
            content=f"{SYNTHETIC_FIXTURE_MARKER}: synthetic accepted evidence only.",
        ),
    )


def _case(
    case_id: str,
    *,
    builder_id: str,
    is_repair: bool,
    build_request: Callable[[], NodeExecutionRequest],
) -> PromptCatalogCase:
    node_name, branch = case_id.split("/", maxsplit=1)
    return PromptCatalogCase(
        case_id=case_id,
        node_name=node_name,
        branch=branch,
        builder_id=builder_id,
        is_repair=is_repair,
        build_request=build_request,
    )


_CASES = (
    _case(
        "final-delivery/composer",
        builder_id="graph/nodes/final_delivery/composer.py::build_final_delivery_request",
        is_repair=False,
        build_request=lambda: build_final_delivery_request(
            ReadinessReportPlan.model_validate(
                {
                    "writable_conclusions": [
                        {
                            "question": _QUESTION,
                            "conclusion_text": f"{SYNTHETIC_FIXTURE_MARKER}: approved conclusion.",
                            "backing_claim_ids": [_SYNTHETIC_SUBMISSION_REF],
                        }
                    ],
                    "mandatory_uncertainties": [
                        {
                            "question": _QUESTION,
                            "limitation": f"{SYNTHETIC_FIXTURE_MARKER}: approved limitation.",
                        }
                    ],
                }
            ),
            _synthesis_evidence(),
        ),
    ),
    _case(
        "hitl1/brief",
        builder_id="graph/nodes/hitl1/prompts.py::build_brief_prompt",
        is_repair=False,
        build_request=lambda: hitl1_prompts.build_brief_prompt(_QUESTION),
    ),
    _case(
        "hitl1/brief-repair",
        builder_id="graph/nodes/hitl1/prompts.py::build_brief_prompt",
        is_repair=True,
        build_request=lambda: hitl1_prompts.build_brief_prompt(_QUESTION, repair_error=_REPAIR_ERROR),
    ),
    _case(
        "hitl1/semantic-intake",
        builder_id="graph/nodes/hitl1/prompts.py::build_semantic_intake_prompt",
        is_repair=False,
        build_request=lambda: hitl1_prompts.build_semantic_intake_prompt(
            original_question=_QUESTION,
            subject=_interaction_subject(),
            reply=f"{SYNTHETIC_FIXTURE_MARKER}: accept the current proposal.",
        ),
    ),
    _case(
        "hitl1/semantic-intake-repair",
        builder_id="graph/nodes/hitl1/prompts.py::build_semantic_intake_prompt",
        is_repair=True,
        build_request=lambda: hitl1_prompts.build_semantic_intake_prompt(
            original_question=_QUESTION,
            subject=_interaction_subject(),
            reply=f"{SYNTHETIC_FIXTURE_MARKER}: accept the current proposal.",
            repair_error=_REPAIR_ERROR,
        ),
    ),
    _case(
        "topic-planning/plan",
        builder_id="graph/nodes/topic_planning/prompts.py::build_planner_prompt",
        is_repair=False,
        build_request=lambda: topic_planning_prompts.build_planner_prompt(_planner_inputs()),
    ),
    _case(
        "topic-planning/plan-repair",
        builder_id="graph/nodes/topic_planning/prompts.py::build_planner_prompt",
        is_repair=True,
        build_request=lambda: topic_planning_prompts.build_planner_prompt(
            _planner_inputs(), repair_error=_REPAIR_ERROR
        ),
    ),
    _case(
        "readiness/critic",
        builder_id="graph/nodes/readiness/critic.py::build_readiness_critic_request",
        is_repair=False,
        build_request=lambda: build_readiness_critic_request(
            (f"{SYNTHETIC_FIXTURE_MARKER}: which storage option is answerable?",),
            _synthesis_evidence(),
        ),
    ),
    _case(
        "targeted-evidence/claim-verifier",
        builder_id="graph/nodes/targeted_evidence/prompts.py::build_claim_verifier_prompt",
        is_repair=False,
        build_request=lambda: targeted_evidence_prompts.build_claim_verifier_prompt(
            claims=(("claim:prompt-catalog", f"{SYNTHETIC_FIXTURE_MARKER}: storage duration affects cost."),),
            assigned_refs=("source:prompt-catalog",),
        ),
    ),
    _case(
        "targeted-evidence/repair",
        builder_id="graph/nodes/targeted_evidence/prompts.py::build_targeted_worker_repair_prompt",
        is_repair=True,
        build_request=lambda: targeted_evidence_prompts.build_targeted_worker_repair_prompt(
            gap_id="gap:prompt-catalog",
            draft=f"{SYNTHETIC_FIXTURE_MARKER}: synthetic targeted-worker draft.",
            validation_error=_REPAIR_ERROR,
        ),
    ),
    _case(
        "targeted-evidence/source-diagnostic",
        builder_id="graph/nodes/targeted_evidence/prompts.py::build_source_diagnostic_prompt",
        is_repair=False,
        build_request=lambda: targeted_evidence_prompts.build_source_diagnostic_prompt(
            source_refs=("source:prompt-catalog",),
            source_contents=(f"{SYNTHETIC_FIXTURE_MARKER}: synthetic source body.",),
        ),
    ),
    _case(
        "targeted-evidence/worker",
        builder_id="graph/nodes/targeted_evidence/prompts.py::build_targeted_worker_prompt",
        is_repair=False,
        build_request=lambda: targeted_evidence_prompts.build_targeted_worker_prompt("gap:prompt-catalog"),
    ),
    _case(
        "wave0/repair",
        builder_id="graph/nodes/wave0/prompts.py::build_wave0_repair_prompt",
        is_repair=True,
        build_request=lambda: wave0_prompts.build_wave0_repair_prompt(
            f"{SYNTHETIC_FIXTURE_MARKER}: synthetic Wave0 draft.",
            ('[{"url":"https://catalog.invalid/source","title":"Synthetic catalog source"}]',),
            assignment=wave0_prompts.build_wave0_assignment_projection(_wave0_spec(), (_SYNTHETIC_TOPIC,)),
            validation_category=wave0_prompts.WAVE0_REPAIR_VALIDATION_CATEGORY,
        ),
    ),
    _case(
        "wave0/worker",
        builder_id="graph/nodes/wave0/prompts.py::build_wave0_worker_prompt",
        is_repair=False,
        build_request=lambda: wave0_prompts.build_wave0_worker_prompt(_wave0_spec(), (_SYNTHETIC_TOPIC,)),
    ),
    _case(
        "wave1/claim-verifier",
        builder_id="graph/nodes/wave1/prompts.py::build_wave1_claim_verifier_prompt",
        is_repair=False,
        build_request=lambda: wave1_prompts.build_wave1_claim_verifier_prompt(
            claims=(
                {
                    "claim_id": "claim:w1_prompt_catalog",
                    "statement": f"{SYNTHETIC_FIXTURE_MARKER}: storage duration affects cost.",
                    "support_refs": ("source:prompt-catalog",),
                    "counter_refs": (),
                },
            ),
            assigned_new_source_ids=("source:prompt-catalog",),
        ),
    ),
    _case(
        "wave1/repair",
        builder_id="graph/nodes/wave1/prompts.py::build_wave1_repair_prompt",
        is_repair=True,
        build_request=lambda: wave1_prompts.build_wave1_repair_prompt(
            f"{SYNTHETIC_FIXTURE_MARKER}: synthetic Wave1 draft.",
            ('[{"url":"https://catalog.invalid/source","title":"Synthetic catalog source"}]',),
            assignment=wave1_prompts.build_wave1_assignment_projection(
                _SYNTHETIC_TOPIC,
                frozenset({"https://catalog.invalid/wave0"}),
            ),
            validation_category=wave1_prompts.WAVE1_REPAIR_PARSE_CATEGORY,
        ),
    ),
    _case(
        "wave1/source-diagnostic",
        builder_id="graph/nodes/wave1/prompts.py::build_wave1_source_diagnostic_prompt",
        is_repair=False,
        build_request=lambda: wave1_prompts.build_wave1_source_diagnostic_prompt(
            observations=(
                {
                    "source_id": "source:prompt-catalog",
                    "canonical_url": "https://catalog.invalid/wave1-source",
                    "title": f"{SYNTHETIC_FIXTURE_MARKER}: synthetic source observation",
                    "is_new_vs_wave0": True,
                },
            ),
        ),
    ),
    _case(
        "wave1/worker",
        builder_id="graph/nodes/wave1/prompts.py::build_wave1_worker_prompt",
        is_repair=False,
        build_request=lambda: wave1_prompts.build_wave1_worker_prompt(
            _SYNTHETIC_TOPIC,
            frozenset({"https://catalog.invalid/wave0"}),
        ),
    ),
    _case(
        "wave2-synthesis/repair",
        builder_id="graph/nodes/wave2_synthesis/prompts.py::build_synthesis_repair_prompt",
        is_repair=True,
        build_request=lambda: wave2_synthesis_prompts.build_synthesis_repair_prompt(
            f"{SYNTHETIC_FIXTURE_MARKER}: synthetic synthesis draft.",
            _synthesis_evidence(),
            validation_category="parser_invalid",
        ),
    ),
    _case(
        "wave2-synthesis/synthesis",
        builder_id="graph/nodes/wave2_synthesis/prompts.py::build_synthesis_prompt",
        is_repair=False,
        build_request=lambda: wave2_synthesis_prompts.build_synthesis_prompt(
            topic_registry=(_SYNTHETIC_TOPIC,),
            wave0_refs=(_SYNTHETIC_SUBMISSION_REF,),
            wave1_refs=(_SYNTHETIC_SUBMISSION_REF,),
            evidence=_synthesis_evidence(),
        ),
    ),
)


def prompt_catalog_cases() -> tuple[PromptCatalogCase, ...]:
    """Return the stable sorted catalog without resolving a model, tool, or runtime."""

    return tuple(sorted(_CASES, key=lambda case: case.case_id))


__all__ = [
    "PromptCatalogCase",
    "SYNTHETIC_FIXTURE_MARKER",
    "VIRTUAL_ATTEMPT_WORKSPACE",
    "prompt_catalog_cases",
]
