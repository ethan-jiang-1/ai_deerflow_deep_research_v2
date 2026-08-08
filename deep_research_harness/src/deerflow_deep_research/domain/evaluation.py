"""Pure contracts for manually invoked cognitive evaluation.

@impl CES-001
@impl CES-003
@impl CES-004
@impl CES-005
@impl CES-006
@impl EVH-029
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class _FrozenContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ControlIdentity(_FrozenContract):
    kind: Literal["case", "contract", "rubric", "protocol"]
    version: str = Field(min_length=1, max_length=128)
    digest: str = Field(pattern=r"^[a-f0-9]{64}$")


class ExecutionBounds(_FrozenContract):
    timeout_seconds: int = Field(ge=1, le=900)
    max_model_calls: int = Field(ge=0, le=50)
    max_tool_calls: int = Field(ge=0, le=200)


class RuntimeControlDigest(_FrozenContract):
    """One source-controlled runtime surface an evaluation subject must report."""

    name: str = Field(pattern=r"^[a-z][a-z0-9_]{2,63}$")
    source_path: str = Field(min_length=1, max_length=512)
    digest: str = Field(pattern=r"^[a-f0-9]{64}$")

    @field_validator("source_path")
    @classmethod
    def _require_project_relative_source(cls, value: str) -> str:
        path = PurePosixPath(value)
        if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
            raise ValueError("evaluation_runtime_control_path_invalid")
        return value


class EvaluationExecutionPlan(_FrozenContract):
    """Fixed repetition, source identity, and telemetry requirements for a live corpus."""

    repeat_count: int = Field(ge=2, le=5)
    runtime_controls: tuple[RuntimeControlDigest, ...] = Field(min_length=1, max_length=8)
    required_resource_fields: tuple[str, ...] = Field(min_length=1, max_length=24)

    @field_validator("runtime_controls")
    @classmethod
    def _require_unique_runtime_controls(
        cls, controls: tuple[RuntimeControlDigest, ...]
    ) -> tuple[RuntimeControlDigest, ...]:
        if len({control.name for control in controls}) != len(controls):
            raise ValueError("evaluation_runtime_control_names_duplicate")
        return controls

    @field_validator("required_resource_fields")
    @classmethod
    def _require_unique_resource_fields(cls, fields: tuple[str, ...]) -> tuple[str, ...]:
        if any(not field or len(field) > 64 for field in fields):
            raise ValueError("evaluation_resource_fields_invalid")
        if len(set(fields)) != len(fields):
            raise ValueError("evaluation_resource_fields_duplicate")
        return fields


ControllerAction = Literal["start", "resume", "status", "cancel", "refine"]


class ControllerEvaluationScenario(_FrozenContract):
    """A bounded ordinary-turn controller choice and its forbidden effects."""

    scenario_id: str = Field(pattern=r"^[a-z][a-z0-9-]{2,63}$")
    subject_state: str = Field(min_length=1, max_length=128)
    user_turn: str = Field(min_length=1, max_length=4_096)
    expected_action: ControllerAction | None = None
    expects_clarification: bool
    expected_result: str = Field(min_length=1, max_length=128)
    target_rule: str = Field(min_length=1, max_length=512)
    forbidden_calls: tuple[ControllerAction, ...]
    forbidden_effects: tuple[str, ...] = Field(min_length=1, max_length=16)
    review_criteria: tuple[str, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def _require_one_cognitive_outcome(self) -> ControllerEvaluationScenario:
        if (self.expected_action is None) != self.expects_clarification:
            raise ValueError("controller_evaluation_outcome_invalid")
        if self.expected_action is not None and self.expected_action in self.forbidden_calls:
            raise ValueError("controller_evaluation_expected_call_forbidden")
        if len(set(self.forbidden_calls)) != len(self.forbidden_calls):
            raise ValueError("controller_evaluation_forbidden_calls_duplicate")
        if len(set(self.forbidden_effects)) != len(self.forbidden_effects):
            raise ValueError("controller_evaluation_forbidden_effects_duplicate")
        if len(set(self.review_criteria)) != len(self.review_criteria):
            raise ValueError("controller_evaluation_review_criteria_duplicate")
        return self


_CONTROLLER_SCENARIO_IDS = frozenset(
    {
        "new-request",
        "correlated-answer",
        "mid-suspension-direction",
        "status",
        "explicit-stop",
        "terminal-queued-direction-continuation",
        "exhausted-terminal-no-direction",
        "exhausted-terminal-queued-direction",
        "ambiguous-terminal-follow-up",
        "ambiguous-criticism",
        "profile-note-non-mutation",
        "clarified-same-run-direction",
        "active-conflict",
        "precommit-recovery-conflict",
        "ended-explicit-target",
        "unavailable-target",
        "mixed-answer-direction",
    }
)


class ControllerEvaluationFixture(_FrozenContract):
    execution: EvaluationExecutionPlan
    scenarios: tuple[ControllerEvaluationScenario, ...] = Field(min_length=1, max_length=24)

    @model_validator(mode="after")
    def _require_complete_controller_coverage(self) -> ControllerEvaluationFixture:
        identifiers = {scenario.scenario_id for scenario in self.scenarios}
        if identifiers != _CONTROLLER_SCENARIO_IDS or len(identifiers) != len(self.scenarios):
            raise ValueError("controller_evaluation_scenarios_incomplete")
        return self


TopicPlanningCaseKind = Literal[
    "canonical_notes",
    "baseline",
    "direction",
    "adversarial_control_text",
    "ambiguity_boundary",
    "invalid_draft_repair",
]


class TopicPlanningEvaluationScenario(_FrozenContract):
    """One bounded production planner assignment and candidate-review target."""

    scenario_id: str = Field(pattern=r"^[a-z][a-z0-9-]{2,63}$")
    case_kind: TopicPlanningCaseKind
    request_text: str = Field(min_length=1, max_length=4_096)
    scope_boundaries: str = Field(min_length=1, max_length=4_096)
    custom_notes: str = Field(min_length=1, max_length=4_096)
    current_direction: str | None = Field(default=None, min_length=1, max_length=4_096)
    contrast_group: str | None = Field(default=None, min_length=1, max_length=128)
    seed_invalid_draft: str | None = Field(default=None, min_length=1, max_length=4_096)
    expected_capability_ids: tuple[
        Literal["topic-planning-profile-decomposition", "topic-planning-plan-repair"], ...
    ] = Field(min_length=1, max_length=2)
    expected_assignment_fragments: tuple[str, ...] = Field(min_length=1, max_length=8)
    forbidden_effects: tuple[str, ...] = Field(min_length=1, max_length=16)
    review_criteria: tuple[str, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def _require_bounded_repair_shape(self) -> TopicPlanningEvaluationScenario:
        repair_capability = "topic-planning-plan-repair"
        if self.case_kind == "invalid_draft_repair":
            if self.seed_invalid_draft is None or repair_capability not in self.expected_capability_ids:
                raise ValueError("topic_planning_repair_case_invalid")
        elif self.seed_invalid_draft is not None or repair_capability in self.expected_capability_ids:
            raise ValueError("topic_planning_nonrepair_case_invalid")
        if len(set(self.expected_capability_ids)) != len(self.expected_capability_ids):
            raise ValueError("topic_planning_capabilities_duplicate")
        if len(set(self.forbidden_effects)) != len(self.forbidden_effects):
            raise ValueError("topic_planning_forbidden_effects_duplicate")
        if len(set(self.review_criteria)) != len(self.review_criteria):
            raise ValueError("topic_planning_review_criteria_duplicate")
        return self


_TOPIC_PLANNING_CASE_KINDS = frozenset(
    {
        "canonical_notes",
        "baseline",
        "direction",
        "adversarial_control_text",
        "ambiguity_boundary",
        "invalid_draft_repair",
    }
)


class TopicPlanningEvaluationFixture(_FrozenContract):
    execution: EvaluationExecutionPlan
    scenarios: tuple[TopicPlanningEvaluationScenario, ...] = Field(min_length=1, max_length=12)

    @model_validator(mode="after")
    def _require_complete_topic_planning_coverage(self) -> TopicPlanningEvaluationFixture:
        kinds = {scenario.case_kind for scenario in self.scenarios}
        identifiers = {scenario.scenario_id for scenario in self.scenarios}
        if kinds != _TOPIC_PLANNING_CASE_KINDS or len(identifiers) != len(self.scenarios):
            raise ValueError("topic_planning_evaluation_scenarios_incomplete")
        contrast = [scenario for scenario in self.scenarios if scenario.contrast_group == "direction-focus"]
        if (
            len(contrast) != 2
            or {scenario.case_kind for scenario in contrast} != {"baseline", "direction"}
            or sum(scenario.current_direction is None for scenario in contrast) != 1
        ):
            raise ValueError("topic_planning_direction_contrast_invalid")
        return self


HITL1CognitiveProgramCaseKind = Literal[
    "normal-confirmation",
    "complete-revision",
    "proposal-question",
    "ambiguity",
    "adversarial-input",
    "malformed-candidate-repair",
]


class HITL1CognitiveProgramScenario(_FrozenContract):
    """One bounded HITL1 cognitive-program assignment and review target."""

    scenario_id: str = Field(pattern=r"^[a-z][a-z0-9-]{2,63}$")
    case_kind: HITL1CognitiveProgramCaseKind
    original_question: str = Field(min_length=1, max_length=4_096)
    current_proposal: dict[str, Any] | None = None
    human_reply: str | None = Field(default=None, min_length=1, max_length=4_096)
    seed_invalid_draft: str | None = Field(default=None, min_length=1, max_length=4_096)
    expected_capability_ids: tuple[
        Literal[
            "hitl1-profile-brief",
            "hitl1-profile-brief-repair",
            "hitl1-semantic-intake",
            "hitl1-semantic-intake-repair",
        ],
        ...,
    ] = Field(min_length=1, max_length=2)
    expected_assignment_fragments: tuple[str, ...] = Field(min_length=1, max_length=8)
    forbidden_effects: tuple[str, ...] = Field(min_length=1, max_length=16)
    review_criteria: tuple[str, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def _require_closed_handoff_shape(self) -> HITL1CognitiveProgramScenario:
        if self.scenario_id != self.case_kind:
            raise ValueError("hitl1_cognitive_program_scenario_id_invalid")
        if self.case_kind == "malformed-candidate-repair":
            if self.seed_invalid_draft is None or "hitl1-semantic-intake-repair" not in self.expected_capability_ids:
                raise ValueError("hitl1_cognitive_program_repair_case_invalid")
        elif self.seed_invalid_draft is not None or "hitl1-semantic-intake-repair" in self.expected_capability_ids:
            raise ValueError("hitl1_cognitive_program_nonrepair_case_invalid")
        if self.case_kind == "normal-confirmation":
            if self.current_proposal is None or self.human_reply is None:
                raise ValueError("hitl1_cognitive_program_confirmation_case_invalid")
        elif self.case_kind != "malformed-candidate-repair" and (
            self.current_proposal is None or self.human_reply is None
        ):
            raise ValueError("hitl1_cognitive_program_semantic_case_invalid")
        if len(set(self.expected_capability_ids)) != len(self.expected_capability_ids):
            raise ValueError("hitl1_cognitive_program_capabilities_duplicate")
        if len(set(self.forbidden_effects)) != len(self.forbidden_effects):
            raise ValueError("hitl1_cognitive_program_forbidden_effects_duplicate")
        if len(set(self.review_criteria)) != len(self.review_criteria):
            raise ValueError("hitl1_cognitive_program_review_criteria_duplicate")
        return self


_HITL1_COGNITIVE_PROGRAM_CASE_KINDS = frozenset(
    {
        "normal-confirmation",
        "complete-revision",
        "proposal-question",
        "ambiguity",
        "adversarial-input",
        "malformed-candidate-repair",
    }
)


class HITL1CognitiveProgramFixture(_FrozenContract):
    execution: EvaluationExecutionPlan
    scenarios: tuple[HITL1CognitiveProgramScenario, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def _require_complete_hitl1_cognitive_program_coverage(self) -> HITL1CognitiveProgramFixture:
        kinds = {scenario.case_kind for scenario in self.scenarios}
        identifiers = {scenario.scenario_id for scenario in self.scenarios}
        if kinds != _HITL1_COGNITIVE_PROGRAM_CASE_KINDS or len(identifiers) != len(self.scenarios):
            raise ValueError("hitl1_cognitive_program_scenarios_incomplete")
        return self


Wave0CognitiveProgramCaseKind = Literal[
    "normal-bounded-retrieval-handoff",
    "adversarial-retrieved-instruction",
    "retrieval-shortfall",
    "malformed-initial-candidate-one-repair",
    "post-candidate-validation-rejection",
]


class Wave0CognitiveProgramScenario(_FrozenContract):
    """One closed source-intake handoff scenario for the production Wave0 node."""

    scenario_id: str = Field(pattern=r"^[a-z][a-z0-9-]{2,63}$")
    case_kind: Wave0CognitiveProgramCaseKind
    assignment: dict[str, str] = Field(min_length=1)
    retrieved_observation: str | None = Field(default=None, min_length=1, max_length=8_192)
    initial_candidate: str | None = Field(default=None, min_length=1, max_length=8_192)
    expected_capability_ids: tuple[Literal["wave0-authoritative-source-intake", "wave0-source-intake-repair"], ...] = (
        Field(min_length=1, max_length=2)
    )
    expected_assignment_fragments: tuple[str, ...] = Field(min_length=1, max_length=8)
    forbidden_effects: tuple[str, ...] = Field(min_length=1, max_length=16)
    review_criteria: tuple[str, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def _require_closed_wave0_handoff_shape(self) -> Wave0CognitiveProgramScenario:
        if self.scenario_id != self.case_kind:
            raise ValueError("wave0_cognitive_program_scenario_id_invalid")
        repair_capability = "wave0-source-intake-repair"
        if self.case_kind == "malformed-initial-candidate-one-repair":
            if self.initial_candidate is None or repair_capability not in self.expected_capability_ids:
                raise ValueError("wave0_cognitive_program_repair_case_invalid")
        elif self.initial_candidate is not None or repair_capability in self.expected_capability_ids:
            raise ValueError("wave0_cognitive_program_nonrepair_case_invalid")
        if self.case_kind != "normal-bounded-retrieval-handoff" and self.retrieved_observation is None:
            raise ValueError("wave0_cognitive_program_observation_missing")
        if len(set(self.expected_capability_ids)) != len(self.expected_capability_ids):
            raise ValueError("wave0_cognitive_program_capabilities_duplicate")
        if len(set(self.forbidden_effects)) != len(self.forbidden_effects):
            raise ValueError("wave0_cognitive_program_forbidden_effects_duplicate")
        if len(set(self.review_criteria)) != len(self.review_criteria):
            raise ValueError("wave0_cognitive_program_review_criteria_duplicate")
        return self


_WAVE0_COGNITIVE_PROGRAM_CASE_KINDS = frozenset(
    {
        "normal-bounded-retrieval-handoff",
        "adversarial-retrieved-instruction",
        "retrieval-shortfall",
        "malformed-initial-candidate-one-repair",
        "post-candidate-validation-rejection",
    }
)


class Wave0CognitiveProgramFixture(_FrozenContract):
    execution: EvaluationExecutionPlan
    scenarios: tuple[Wave0CognitiveProgramScenario, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def _require_complete_wave0_cognitive_program_coverage(self) -> Wave0CognitiveProgramFixture:
        kinds = {scenario.case_kind for scenario in self.scenarios}
        identifiers = {scenario.scenario_id for scenario in self.scenarios}
        if kinds != _WAVE0_COGNITIVE_PROGRAM_CASE_KINDS or len(identifiers) != len(self.scenarios):
            raise ValueError("wave0_cognitive_program_scenarios_incomplete")
        return self


Wave1CognitiveProgramCaseKind = Literal[
    "normal-bounded-retrieval-handoff",
    "adversarial-retrieved-instruction",
    "baseline-duplicate-containment",
    "malformed-initial-candidate-one-repair",
    "local-semantic-candidate-one-repair",
    "post-candidate-validation-rejection",
]


class Wave1CognitiveProgramScenario(_FrozenContract):
    """One closed extraction/repair handoff scenario for the production Wave1 node."""

    scenario_id: str = Field(pattern=r"^[a-z][a-z0-9-]{2,63}$")
    case_kind: Wave1CognitiveProgramCaseKind
    assignment: dict[str, str] = Field(min_length=1)
    wave0_baseline_urls: tuple[str, ...] = ()
    retrieved_observation: str = Field(min_length=1, max_length=8_192)
    initial_candidate: str | None = Field(default=None, min_length=1, max_length=8_192)
    expected_capability_ids: tuple[Literal["wave1-evidence-extraction", "wave1-evidence-extraction-repair"], ...] = (
        Field(min_length=1, max_length=2)
    )
    expected_assignment_fragments: tuple[str, ...] = Field(min_length=1, max_length=8)
    forbidden_effects: tuple[str, ...] = Field(min_length=1, max_length=16)
    review_criteria: tuple[str, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def _require_closed_wave1_handoff_shape(self) -> Wave1CognitiveProgramScenario:
        if self.scenario_id != self.case_kind:
            raise ValueError("wave1_cognitive_program_scenario_id_invalid")
        repair_kinds = {
            "malformed-initial-candidate-one-repair",
            "local-semantic-candidate-one-repair",
        }
        repair_capability = "wave1-evidence-extraction-repair"
        if self.case_kind in repair_kinds:
            if self.initial_candidate is None or repair_capability not in self.expected_capability_ids:
                raise ValueError("wave1_cognitive_program_repair_case_invalid")
        elif self.initial_candidate is not None or repair_capability in self.expected_capability_ids:
            raise ValueError("wave1_cognitive_program_nonrepair_case_invalid")
        if self.case_kind == "baseline-duplicate-containment" and not self.wave0_baseline_urls:
            raise ValueError("wave1_cognitive_program_baseline_missing")
        if len(set(self.expected_capability_ids)) != len(self.expected_capability_ids):
            raise ValueError("wave1_cognitive_program_capabilities_duplicate")
        if len(set(self.wave0_baseline_urls)) != len(self.wave0_baseline_urls):
            raise ValueError("wave1_cognitive_program_baseline_duplicate")
        if len(set(self.forbidden_effects)) != len(self.forbidden_effects):
            raise ValueError("wave1_cognitive_program_forbidden_effects_duplicate")
        if len(set(self.review_criteria)) != len(self.review_criteria):
            raise ValueError("wave1_cognitive_program_review_criteria_duplicate")
        return self


_WAVE1_COGNITIVE_PROGRAM_CASE_KINDS = frozenset(
    {
        "normal-bounded-retrieval-handoff",
        "adversarial-retrieved-instruction",
        "baseline-duplicate-containment",
        "malformed-initial-candidate-one-repair",
        "local-semantic-candidate-one-repair",
        "post-candidate-validation-rejection",
    }
)


class Wave1CognitiveProgramFixture(_FrozenContract):
    execution: EvaluationExecutionPlan
    scenarios: tuple[Wave1CognitiveProgramScenario, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def _require_complete_wave1_cognitive_program_coverage(self) -> Wave1CognitiveProgramFixture:
        kinds = {scenario.case_kind for scenario in self.scenarios}
        identifiers = {scenario.scenario_id for scenario in self.scenarios}
        if kinds != _WAVE1_COGNITIVE_PROGRAM_CASE_KINDS or len(identifiers) != len(self.scenarios):
            raise ValueError("wave1_cognitive_program_scenarios_incomplete")
        return self


Wave2CognitiveProgramCaseKind = Literal[
    "normal-accepted-evidence-synthesis",
    "instruction-like-evidence-containment",
    "honest-uncertainty-with-backed-finding",
    "malformed-initial-candidate-one-repair",
    "invalid-repaired-candidate-non-publication",
]


class Wave2CognitiveProgramScenario(_FrozenContract):
    """One closed accepted-evidence synthesis/repair handoff scenario."""

    scenario_id: str = Field(pattern=r"^[a-z][a-z0-9-]{2,63}$")
    case_kind: Wave2CognitiveProgramCaseKind
    assignment: dict[str, str] = Field(min_length=1)
    accepted_submission_refs: tuple[str, ...] = Field(min_length=1, max_length=4)
    accepted_evidence: tuple[str, ...] = Field(min_length=1, max_length=4)
    initial_candidate: str | None = Field(default=None, min_length=1, max_length=8_192)
    repair_candidate: str | None = Field(default=None, min_length=1, max_length=8_192)
    expected_capability_ids: tuple[Literal["wave2-evidence-synthesis", "wave2-evidence-synthesis-repair"], ...] = Field(
        min_length=1, max_length=2
    )
    expected_assignment_fragments: tuple[str, ...] = Field(min_length=1, max_length=8)
    forbidden_effects: tuple[
        Literal[
            "tool_call",
            "evidence_admission",
            "artifact_write",
            "gap_projection",
            "gate_control",
            "route_selection",
            "lifecycle_mutation",
            "provider_quality_claim",
        ],
        ...,
    ] = Field(min_length=1, max_length=8)
    review_criteria: tuple[str, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def _require_closed_wave2_handoff_shape(self) -> Wave2CognitiveProgramScenario:
        if self.scenario_id != self.case_kind:
            raise ValueError("wave2_cognitive_program_scenario_id_invalid")
        if len(self.accepted_submission_refs) != len(self.accepted_evidence):
            raise ValueError("wave2_cognitive_program_evidence_assignment_invalid")
        if len(set(self.accepted_submission_refs)) != len(self.accepted_submission_refs):
            raise ValueError("wave2_cognitive_program_evidence_refs_duplicate")
        repair_kinds = {
            "malformed-initial-candidate-one-repair",
            "invalid-repaired-candidate-non-publication",
        }
        expected_initial = ("wave2-evidence-synthesis",)
        expected_repair = ("wave2-evidence-synthesis", "wave2-evidence-synthesis-repair")
        if self.case_kind in repair_kinds:
            if (
                self.initial_candidate is None
                or self.repair_candidate is None
                or self.expected_capability_ids != expected_repair
            ):
                raise ValueError("wave2_cognitive_program_repair_case_invalid")
        elif (
            self.initial_candidate is not None
            or self.repair_candidate is not None
            or self.expected_capability_ids != expected_initial
        ):
            raise ValueError("wave2_cognitive_program_nonrepair_case_invalid")
        if len(set(self.forbidden_effects)) != len(self.forbidden_effects):
            raise ValueError("wave2_cognitive_program_forbidden_effects_duplicate")
        if len(set(self.review_criteria)) != len(self.review_criteria):
            raise ValueError("wave2_cognitive_program_review_criteria_duplicate")
        return self


_WAVE2_COGNITIVE_PROGRAM_CASE_KINDS = frozenset(
    {
        "normal-accepted-evidence-synthesis",
        "instruction-like-evidence-containment",
        "honest-uncertainty-with-backed-finding",
        "malformed-initial-candidate-one-repair",
        "invalid-repaired-candidate-non-publication",
    }
)


class Wave2CognitiveProgramFixture(_FrozenContract):
    execution: EvaluationExecutionPlan
    scenarios: tuple[Wave2CognitiveProgramScenario, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def _require_complete_wave2_cognitive_program_coverage(self) -> Wave2CognitiveProgramFixture:
        kinds = {scenario.case_kind for scenario in self.scenarios}
        identifiers = {scenario.scenario_id for scenario in self.scenarios}
        if kinds != _WAVE2_COGNITIVE_PROGRAM_CASE_KINDS or len(identifiers) != len(self.scenarios):
            raise ValueError("wave2_cognitive_program_scenarios_incomplete")
        return self


class EvaluationCase(_FrozenContract):
    case_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,63}$")
    version: str = Field(min_length=1, max_length=128)
    subject: Literal[
        "hitl1_brief",
        "hitl1_cognitive_program",
        "wave0_cognitive_program",
        "wave1_cognitive_program",
        "wave2_cognitive_program",
        "wave0_worker",
        "bounded_flow",
        "public_controller",
        "topic_planning",
    ]
    fixture: dict[str, Any]
    required_services: tuple[Literal["model", "web"], ...]
    bounds: ExecutionBounds
    controls: tuple[ControlIdentity, ...]

    @field_validator("controls")
    @classmethod
    def _require_complete_controls(cls, controls: tuple[ControlIdentity, ...]) -> tuple[ControlIdentity, ...]:
        if tuple(control.kind for control in controls) != ("case", "contract", "rubric", "protocol"):
            raise ValueError("evaluation_case_controls_invalid")
        return controls

    @model_validator(mode="after")
    def _require_cognitive_corpus_contract(self) -> EvaluationCase:
        if self.subject == "public_controller":
            fixture = self.controller_fixture
            _validate_execution_plan(
                fixture.execution,
                expected_control_names={"skill_digest", "soul_digest", "tool_schema_digest"},
            )
        elif self.subject == "topic_planning":
            fixture = self.topic_planning_fixture
            _validate_execution_plan(
                fixture.execution,
                expected_control_names={"initial_capability_digest", "repair_capability_digest", "topic_schema_digest"},
            )
        elif self.subject == "hitl1_cognitive_program":
            fixture = self.hitl1_cognitive_program_fixture
            _validate_execution_plan(
                fixture.execution,
                expected_control_names={
                    "brief_capability_digest",
                    "brief_repair_capability_digest",
                    "semantic_intake_capability_digest",
                    "semantic_repair_capability_digest",
                    "profile_schema_digest",
                    "semantic_candidate_schema_digest",
                },
            )
        elif self.subject == "wave0_cognitive_program":
            fixture = self.wave0_cognitive_program_fixture
            _validate_execution_plan(
                fixture.execution,
                expected_control_names={
                    "source_intake_capability_digest",
                    "source_intake_repair_capability_digest",
                    "worker_schema_digest",
                },
            )
        elif self.subject == "wave1_cognitive_program":
            fixture = self.wave1_cognitive_program_fixture
            _validate_execution_plan(
                fixture.execution,
                expected_control_names={
                    "evidence_extraction_capability_digest",
                    "evidence_extraction_repair_capability_digest",
                    "worker_schema_digest",
                },
            )
        elif self.subject == "wave2_cognitive_program":
            fixture = self.wave2_cognitive_program_fixture
            if self.required_services:
                raise ValueError("wave2_cognitive_program_live_service_dependency_forbidden")
            if self.bounds.max_tool_calls != 0:
                raise ValueError("wave2_cognitive_program_tool_dependency_forbidden")
            _validate_execution_plan(
                fixture.execution,
                expected_control_names={
                    "synthesis_capability_digest",
                    "synthesis_repair_capability_digest",
                    "synthesis_result_schema_digest",
                },
            )
        return self

    @property
    def execution_plan(self) -> EvaluationExecutionPlan | None:
        if self.subject == "public_controller":
            return self.controller_fixture.execution
        if self.subject == "topic_planning":
            return self.topic_planning_fixture.execution
        if self.subject == "hitl1_cognitive_program":
            return self.hitl1_cognitive_program_fixture.execution
        if self.subject == "wave0_cognitive_program":
            return self.wave0_cognitive_program_fixture.execution
        if self.subject == "wave1_cognitive_program":
            return self.wave1_cognitive_program_fixture.execution
        if self.subject == "wave2_cognitive_program":
            return self.wave2_cognitive_program_fixture.execution
        return None

    @property
    def controller_fixture(self) -> ControllerEvaluationFixture:
        if self.subject != "public_controller":
            raise ValueError("controller_evaluation_fixture_unavailable")
        return ControllerEvaluationFixture.model_validate(self.fixture)

    @property
    def topic_planning_fixture(self) -> TopicPlanningEvaluationFixture:
        if self.subject != "topic_planning":
            raise ValueError("topic_planning_evaluation_fixture_unavailable")
        return TopicPlanningEvaluationFixture.model_validate(self.fixture)

    @property
    def hitl1_cognitive_program_fixture(self) -> HITL1CognitiveProgramFixture:
        if self.subject != "hitl1_cognitive_program":
            raise ValueError("hitl1_cognitive_program_fixture_unavailable")
        return HITL1CognitiveProgramFixture.model_validate(self.fixture)

    @property
    def wave0_cognitive_program_fixture(self) -> Wave0CognitiveProgramFixture:
        if self.subject != "wave0_cognitive_program":
            raise ValueError("wave0_cognitive_program_fixture_unavailable")
        return Wave0CognitiveProgramFixture.model_validate(self.fixture)

    @property
    def wave1_cognitive_program_fixture(self) -> Wave1CognitiveProgramFixture:
        if self.subject != "wave1_cognitive_program":
            raise ValueError("wave1_cognitive_program_fixture_unavailable")
        return Wave1CognitiveProgramFixture.model_validate(self.fixture)

    @property
    def wave2_cognitive_program_fixture(self) -> Wave2CognitiveProgramFixture:
        if self.subject != "wave2_cognitive_program":
            raise ValueError("wave2_cognitive_program_fixture_unavailable")
        return Wave2CognitiveProgramFixture.model_validate(self.fixture)


_COMMON_COGNITIVE_RESOURCE_FIELDS = {
    "provider",
    "model",
    "composed_prompt_digest",
    "input_tokens",
    "output_tokens",
    "cost_usd",
    "latency_ms",
}


def _validate_execution_plan(plan: EvaluationExecutionPlan, *, expected_control_names: set[str]) -> None:
    control_names = {control.name for control in plan.runtime_controls}
    if control_names != expected_control_names:
        raise ValueError("evaluation_runtime_controls_invalid")
    required_fields = set(plan.required_resource_fields)
    if not (_COMMON_COGNITIVE_RESOURCE_FIELDS | expected_control_names).issubset(required_fields):
        raise ValueError("evaluation_resource_fields_incomplete")


class ExecutionStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"


class EvidenceLayer(StrEnum):
    DETERMINISTIC_HANDOFF = "deterministic_handoff"
    CREDENTIALED_LIVE_QUALITY = "credentialed_live_quality"


class ReviewResult(StrEnum):
    PASS = "pass"
    LIMITED = "limited"
    INCONCLUSIVE = "inconclusive"
    FAILED = "failed"


class SubjectExecution(_FrozenContract):
    output: dict[str, Any]
    artifacts: dict[str, Any] = Field(default_factory=dict)
    resource_use: dict[str, int | float | str | bool] = Field(default_factory=dict)

    @field_validator("artifacts")
    @classmethod
    def _require_contained_artifact_names(cls, artifacts: dict[str, Any]) -> dict[str, Any]:
        for name in artifacts:
            path = Path(name)
            if path.is_absolute() or ".." in path.parts or not name:
                raise ValueError("evaluation_artifact_path_invalid")
        return artifacts


class FailureDetail(_FrozenContract):
    code: str = Field(pattern=r"^[a-z0-9_]{3,64}$")
    phase: str = Field(pattern=r"^[a-z0-9_.-]{3,128}$")


class EvaluationBundleManifest(_FrozenContract):
    schema_version: Literal[1] = 1
    execution_id: str = Field(pattern=r"^e_[a-f0-9]{32}$")
    case_id: str
    case_version: str
    status: ExecutionStatus
    evidence_layer: EvidenceLayer = EvidenceLayer.DETERMINISTIC_HANDOFF
    controls: tuple[ControlIdentity, ...]
    content_digests: dict[str, str]
    failure: FailureDetail | None = None

    @field_validator("content_digests")
    @classmethod
    def _require_content_digests(cls, values: dict[str, str]) -> dict[str, str]:
        if not values or any(not name or len(digest) != 64 for name, digest in values.items()):
            raise ValueError("bundle_content_digests_invalid")
        return values


class ExecutionResult(_FrozenContract):
    execution_id: str
    status: ExecutionStatus
    bundle_path: Path


class ReviewSubmission(_FrozenContract):
    bundle_path: Path
    evaluator: str = Field(min_length=1, max_length=128)
    result: ReviewResult
    evidence: tuple[str, ...] = Field(min_length=1, max_length=16)
    confidence: Literal["low", "medium", "high"]
    unknowns: tuple[str, ...]
    variance: tuple[str, ...] = Field(default=(), max_length=16)
    owning_seam: str = Field(min_length=1, max_length=256)
    follow_up: str = Field(min_length=1, max_length=1024)
    controls: tuple[ControlIdentity, ...]


class ReviewRecord(_FrozenContract):
    review_id: str
    path: Path
    bundle_digest: str
    evaluator: str
    result: ReviewResult
    reviewed_at: datetime
    case_id: str
    case_version: str
    evidence_layer: EvidenceLayer = EvidenceLayer.DETERMINISTIC_HANDOFF
    controls: tuple[ControlIdentity, ...]
    evidence: tuple[str, ...]
    confidence: Literal["low", "medium", "high"]
    unknowns: tuple[str, ...]
    variance: tuple[str, ...]
    owning_seam: str
    follow_up: str


class EvaluationOperationResult(_FrozenContract):
    operation: Literal["run", "review"]
    reference: str | None = None
    status: str | None = None
    diagnostic: str | None = Field(default=None, max_length=128)
