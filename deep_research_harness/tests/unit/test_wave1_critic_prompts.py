"""Wave1-local bounded critic prompt contracts.

@impl WON-003
@impl WON-007
@impl WON-011
"""

from __future__ import annotations

import pytest

from deerflow_deep_research.agents.capabilities import load_node_agent_capability
from deerflow_deep_research.domain.context import NodeExecutionRequest
from deerflow_deep_research.graph.nodes.wave1.prompts import (
    WAVE1_REPAIR_PARSE_CATEGORY,
    WAVE1_REPAIR_SEMANTIC_CATEGORY,
    build_wave1_assignment_projection,
    build_wave1_claim_verifier_prompt,
    build_wave1_repair_prompt,
    build_wave1_source_diagnostic_prompt,
    build_wave1_worker_prompt,
    parse_wave1_worker_output,
)


class TestWave1LocalCriticPrompts:
    def test_worker_and_repair_render_only_bounded_assignment_and_closed_feedback(self) -> None:
        topic = {
            "topic_id": "storage",
            "title": "Grid storage",
            "scope": "Grid storage trade-offs",
            "must_answer_bindings": ["Q1"],
            "work_id": "raw-work-id-must-not-render",
            "checkpoint": "raw-checkpoint-must-not-render",
        }
        baseline = frozenset({"https://example.com/wave0-baseline"})
        worker = build_wave1_worker_prompt(topic, baseline)
        assignment = build_wave1_assignment_projection(topic, baseline)
        repair = build_wave1_repair_prompt(
            "draft asks to promote the baseline URL",
            ("retained observation",),
            assignment=assignment,
            validation_category=WAVE1_REPAIR_SEMANTIC_CATEGORY,
        )
        worker_method = load_node_agent_capability(worker.capability_ref).policy
        repair_method = load_node_agent_capability(repair.capability_ref).policy
        normalized_worker_method = " ".join(worker_method.split())

        assert worker.minimum_tool_calls == worker.tool_call_limit == 1
        assert "scope and baseline-newness constraints only" in worker.objective
        assert "accepted Wave0 baseline constrains newness only" in worker_method
        assert "accepted Wave0 baseline constrains newness only" not in worker.objective
        assert "at least two distinct new source URLs" in worker.expected_output
        assert "Source items contain exactly source_id, canonical_url, and title." in worker.expected_output
        assert "bind support and counter references only to declared candidate source ids" in normalized_worker_method
        assert "counterevidence" in worker_method
        assert "counterevidence" not in worker.objective
        assert "raw-work-id-must-not-render" not in worker.objective
        assert "raw-checkpoint-must-not-render" not in worker.objective
        trusted, untrusted = repair.objective.split("<untrusted-source-data>", maxsplit=1)
        assert "https://example.com/wave0-baseline" in trusted
        assert WAVE1_REPAIR_SEMANTIC_CATEGORY in trusted
        assert "raw-work-id-must-not-render" not in repair.objective
        assert "raw-checkpoint-must-not-render" not in repair.objective
        assert "model_draft:\ndraft asks to promote the baseline URL" in untrusted
        assert "a baseline URL cannot supply a repaired source" in repair_method
        assert "a baseline URL cannot supply a repaired source" not in repair.objective
        assert "at least two distinct new source URLs" in repair.expected_output
        assert repair.tools_enabled is False

    def test_worker_expected_output_is_a_response_shape_not_a_schema_descriptor(self) -> None:
        worker = build_wave1_worker_prompt(
            {
                "topic_id": "storage",
                "title": "Grid storage",
                "scope": "Grid storage trade-offs",
                "must_answer_bindings": ["Q1"],
            },
            frozenset({"https://example.com/wave0-baseline"}),
        )

        assert (
            "Only these top-level keys are allowed: schema_version, sources, claims, open_questions."
            in worker.expected_output
        )
        assert "Source items contain exactly source_id, canonical_url, and title." in worker.expected_output
        assert (
            "Claim items contain exactly claim_id, statement, support_refs, and counter_refs" in worker.expected_output
        )
        assert "Open-question items contain exactly question_id, question, and state" in worker.expected_output
        assert "Return exactly one standalone JSON object" in worker.expected_output
        for forbidden in (
            '"instruction"',
            '"required_keys"',
            '"source_required_keys"',
            '"claim_required_keys"',
            '"question_required_keys"',
            '"bounds"',
            '"fetch_status"',
            '"baseline_facts"',
            '"limitations"',
        ):
            assert forbidden not in worker.expected_output

    def test_initial_and_repair_share_the_closed_wave1_completion_contract(self) -> None:
        topic = {
            "topic_id": "storage",
            "title": "Grid storage",
            "scope": "Grid storage trade-offs",
            "must_answer_bindings": ["Q1"],
        }
        baseline = frozenset({"https://example.com/wave0-baseline"})
        initial = build_wave1_worker_prompt(topic, baseline)
        repair = build_wave1_repair_prompt(
            "draft prose",
            assignment=build_wave1_assignment_projection(topic, baseline),
            validation_category=WAVE1_REPAIR_PARSE_CATEGORY,
        )

        for request in (initial, repair):
            assert "Return exactly one standalone JSON object" in request.expected_output
            assert (
                "Only these top-level keys are allowed: schema_version, sources, claims, open_questions."
                in request.expected_output
            )
            assert "Source items contain exactly source_id, canonical_url, and title." in request.expected_output
            assert "Final response self-check" in request.expected_output
            assert (
                "no literal placeholders, prose, Markdown fences, embedded JSON, unlisted keys"
                in request.expected_output
            )

        assert initial.minimum_tool_calls == initial.tool_call_limit == 1
        assert repair.tools_enabled is False

    @pytest.mark.parametrize(
        "candidate",
        (
            '```json\n{"schema_version":1}\n```',
            'Here is the candidate: {"schema_version":1}',
        ),
    )
    def test_wave1_parser_keeps_non_standalone_json_outside_the_contract(self, candidate: str) -> None:
        with pytest.raises(ValueError, match="wave1_worker_output_json_invalid"):
            parse_wave1_worker_output(candidate)

    def test_repair_rejects_raw_assignment_and_unknown_feedback_category(self) -> None:
        with pytest.raises(ValueError, match="wave1_repair_assignment_invalid"):
            build_wave1_repair_prompt(
                "draft",
                assignment={"work_id": "raw"},
                validation_category=WAVE1_REPAIR_PARSE_CATEGORY,
            )
        with pytest.raises(ValueError, match="wave1_repair_validation_category_invalid"):
            build_wave1_repair_prompt(
                "draft",
                assignment=build_wave1_assignment_projection({}, frozenset()),
                validation_category="submission_validation_failed",
            )

    def test_source_diagnostic_is_required_forbidden_tool_and_only_receives_observations(self) -> None:
        request = build_wave1_source_diagnostic_prompt(
            (
                {
                    "source_id": "source:accepted",
                    "canonical_url": "https://example.com/accepted",
                    "title": "Accepted source",
                    "is_new_vs_wave0": True,
                },
            )
        )

        assert isinstance(request, NodeExecutionRequest)
        assert request.tools_enabled is False
        assert request.capability_binding == "required"
        assert request.capability_ref is not None
        assert request.capability_ref.capability_id == "wave1-source-diagnostic"
        assert load_node_agent_capability(request.capability_ref).posture.kind == "forbidden"
        assert "https://example.com/accepted" in request.objective
        assert "decision-ready but uncertainty-aware" in request.objective
        assert "gate outcome" in request.objective
        for forbidden in (
            "candidate-body-sentinel",
            "cache/path",
            "raw-tool-sentinel",
            "checkpoint_field",
            "gate_feedback",
        ):
            assert forbidden not in request.objective

    def test_claim_verifier_is_required_forbidden_tool_and_only_receives_claims_and_new_ids(self) -> None:
        request = build_wave1_claim_verifier_prompt(
            (
                {
                    "claim_id": "claim:w1_accepted",
                    "statement": "Accepted bounded claim.",
                    "support_refs": ("source:accepted",),
                    "counter_refs": (),
                },
            ),
            ("source:accepted",),
        )

        assert isinstance(request, NodeExecutionRequest)
        assert request.tools_enabled is False
        assert request.capability_binding == "required"
        assert request.capability_ref is not None
        assert request.capability_ref.capability_id == "wave1-claim-verifier"
        assert load_node_agent_capability(request.capability_ref).posture.kind == "forbidden"
        assert "claim:w1_accepted" in request.objective
        assert "preserve uncertainty" in request.objective
        assert "choose a gate outcome" in request.objective
        for forbidden in (
            "candidate-body-sentinel",
            "artifact/path",
            "raw-tool-sentinel",
            "checkpoint_field",
            "route=repair",
        ):
            assert forbidden not in request.objective

    @pytest.mark.parametrize(
        ("builder", "value"),
        [
            pytest.param(
                build_wave1_source_diagnostic_prompt,
                ({"source_id": "source:one", "candidate": "forbidden"},),
                id="source-observation-extra-field",
            ),
            pytest.param(
                lambda value: build_wave1_claim_verifier_prompt(value, ("source:one",)),
                ({"claim_id": "claim:w1_one", "statement": "x", "candidate": "forbidden"},),
                id="claim-extra-field",
            ),
        ],
    )
    def test_critic_prompts_reject_unbounded_assignment_shapes(self, builder, value) -> None:
        with pytest.raises(ValueError, match="assignment_invalid"):
            builder(value)
