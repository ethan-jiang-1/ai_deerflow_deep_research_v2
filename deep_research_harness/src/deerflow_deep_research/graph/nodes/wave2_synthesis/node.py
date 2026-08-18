"""Real Wave2 synthesis node — cross-topic synthesis from accepted evidence.

@impl WSN-001
@impl WFO-001
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any

from deerflow_deep_research.domain.lifecycle import LifecycleStatus, TerminalReason
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.run_experience import (
    FailureCertainty,
    NodeProblem,
    RunFailureCode,
    TerminalIncidentProjection,
)
from deerflow_deep_research.domain.state import PhaseStatus, node_state_update
from deerflow_deep_research.domain.synthesis import (
    WAVE2_GATE_PREVIEW_KEY,
    SynthesisEvidence,
    build_wave2_gate_preview,
)
from deerflow_deep_research.domain.wave1 import Wave1OpenQuestionRef
from deerflow_deep_research.domain.workflow_outcomes import (
    InvocationFailure,
    derive_provider_diagnostic_reference,
    invoke_and_normalize,
)

from .materializer import materialize_synthesis
from .prompts import build_synthesis_prompt, build_synthesis_repair_prompt, parse_synthesis_output


def _synthesis_validation_category(error: ValueError) -> str:
    """Project closed parser/semantic failures into repair-safe feedback."""

    code = str(error)
    if code.startswith("synthesis_output_"):
        return "parser_invalid"
    if code.startswith("synthesis_"):
        return "semantic_invalid"
    return "candidate_invalid"


_PRE_MODEL_CATEGORY_RE = re.compile(r"^[a-z]+(?:[._][a-z0-9_]+)*$")
_PRE_MODEL_SNAKE_RE = re.compile(r"^[a-z][a-z0-9_]*(?:_[a-z0-9_]+)*$")


def _pre_model_problem(error: ValueError) -> NodeProblem:
    """Typed incident for a pre-model input-condition failure (BUG-046).

    The pre-model raise sites use closed, self-describing messages (e.g.
    ``synthesis_question_coverage_invalid``). Carry the concrete message as the
    validation category when it already matches the NodeProblem pattern;
    messages whose first segment carries digits (``wave1_...``) are namespaced
    as ``input.<message>`` to stay pattern-safe; anything else falls back to
    the generic bucket from ``_synthesis_validation_category``.
    """

    message = str(error)
    if _PRE_MODEL_CATEGORY_RE.fullmatch(message):
        category = message
    elif _PRE_MODEL_SNAKE_RE.fullmatch(message):
        category = f"input.{message}"
    else:
        category = _synthesis_validation_category(error)
    return NodeProblem(
        code=RunFailureCode.OUTPUT_STRUCTURED_INVALID,
        phase="wave2_synthesis",
        certainty=FailureCertainty.DIRECT,
        validation_category=category,
    )


class SynthesisValidationFailure(ValueError):
    """A typed deterministic validation failure: concrete category plus a
    bounded repair-time detail (missing/duplicated/foreign question ids).

    It IS a ValueError, so existing `except ValueError:` seams keep catching it;
    the concrete category and detail are additionally available to the
    repair-prompt call site and the second-validation terminal call site.
    """

    def __init__(self, category: str, detail: object | None = None) -> None:
        self.category = category
        self.detail = detail
        super().__init__(category)


def _evidence_aliases(evidence: tuple[SynthesisEvidence, ...]) -> dict[str, str]:
    aliases = {item.submission_ref: item.submission_ref for item in evidence}
    for item in evidence:
        try:
            payload = json.loads(item.content)
        except (TypeError, ValueError):
            continue
        pending: list[object] = [payload]
        while pending:
            current = pending.pop()
            if isinstance(current, dict):
                for key in ("source_id", "canonical_url"):
                    value = current.get(key)
                    if isinstance(value, str):
                        aliases[value] = item.submission_ref
                for key in ("support_refs", "counter_refs"):
                    values = current.get(key)
                    if isinstance(values, list):
                        for value in values:
                            if isinstance(value, str):
                                aliases[value] = item.submission_ref
                pending.extend(current.values())
            elif isinstance(current, list):
                pending.extend(current)
    return aliases


def _question_ref_id(ref: object) -> str:
    """Project one projected question id whether it round-tripped as a model or a dict."""

    if isinstance(ref, Wave1OpenQuestionRef):
        return ref.question_id
    if isinstance(ref, Mapping):
        question_id = ref.get("question_id")
        if isinstance(question_id, str):
            return question_id
    raise ValueError("wave1_open_question_projection_invalid")


def _validate_synthesis_semantics(
    output,
    accepted_refs: tuple[str, ...],
    evidence: tuple[SynthesisEvidence, ...],
    *,
    open_question_ids: tuple[str, ...] = (),
):
    accepted = set(accepted_refs)
    aliases = _evidence_aliases(evidence)
    if accepted and not output.findings:
        raise SynthesisValidationFailure("synthesis_findings_required")
    for finding in output.findings:
        normalized_refs = tuple(aliases.get(ref, ref) for ref in finding.backing_refs)
        finding = finding.model_copy(update={"backing_refs": normalized_refs})
        backing_refs = set(normalized_refs)
        if not backing_refs:
            raise SynthesisValidationFailure("synthesis_finding_backing_refs_required")
        if not backing_refs <= accepted:
            raise SynthesisValidationFailure("synthesis_finding_backing_ref_invalid")
    if open_question_ids:
        expected = set(open_question_ids)
        gap_covered: set[str] = set()
        for gap in output.gaps:
            if not gap.search_required:
                if gap.source_questions:
                    raise SynthesisValidationFailure(
                        "synthesis_question_coverage_invalid",
                        detail={"non_searchable_gap_questions": sorted(gap.source_questions)},
                    )
                continue
            overlap = gap_covered & set(gap.source_questions)
            if overlap:
                raise SynthesisValidationFailure(
                    "synthesis_question_coverage_invalid",
                    detail={"duplicated_question_ids": sorted(overlap)},
                )
            gap_covered |= set(gap.source_questions)
        resolved = set(output.resolved_questions)
        both = gap_covered & resolved
        if both:
            raise SynthesisValidationFailure(
                "synthesis_question_coverage_invalid",
                detail={"question_ids_in_both": sorted(both)},
            )
        missing = expected - (gap_covered | resolved)
        foreign = (gap_covered | resolved) - expected
        if missing or foreign:
            raise SynthesisValidationFailure(
                "synthesis_question_coverage_invalid",
                detail={
                    "missing_question_ids": sorted(missing),
                    "foreign_question_ids": sorted(foreign),
                },
            )
    normalized_findings = tuple(
        finding.model_copy(update={"backing_refs": tuple(aliases.get(ref, ref) for ref in finding.backing_refs)})
        for finding in output.findings
    )
    return output.model_copy(update={"findings": normalized_findings})


def _exhausted_update(
    problem: NodeProblem,
    *,
    state: Mapping[str, Any],
    dependencies: NodeBuildDependencies,
) -> dict[str, object]:
    diagnostic_ref = problem.diagnostic_ref
    if problem.provider_observation is not None and diagnostic_ref is None:
        diagnostic_ref = derive_provider_diagnostic_reference(
            bundle_id=str(state["bundle_id"]),
            generation=int(state.get("generation", 0)),
            node_attempt=dependencies.agent_context.attempt_id,
            problem=problem,
        )
    return node_state_update(
        "wave2_synthesis",
        route="exhausted",
        terminal_status=LifecycleStatus.BLOCKED.value,
        phase_status=PhaseStatus.TERMINAL.value,
        terminal_reason=TerminalReason.GATE_BLOCKED.value,
        latest_incident=TerminalIncidentProjection(
            code=problem.code,
            phase=problem.phase,
            certainty=problem.certainty,
            diagnostic_ref=diagnostic_ref,
            provider_observation=problem.provider_observation,
            validation_category=problem.validation_category,
        ).model_dump(mode="json", exclude_none=True),
    )


def build_real(dependencies: NodeBuildDependencies):
    if dependencies.synthesis_bundle is None:
        raise ValueError("synthesis_bundle_capability_missing")
    if dependencies.selected_bundle is None:
        raise ValueError("selected_bundle_context_missing")
    if getattr(dependencies.synthesis_bundle, "bundle", None) != dependencies.selected_bundle.bundle:
        raise ValueError("selected_bundle_context_mismatch")

    async def run(state: dict[str, Any]) -> dict[str, Any]:
        # Pre-model input derivation is guarded (BUG-046): every failure mode
        # here is a data condition (projection parse, open-question coverage,
        # accepted-record resolution, evidence read) that must terminate the
        # node through the typed exhausted route with its concrete category —
        # never escape as an uncaught exception and crash the graph. Only
        # ValueError is caught; cancellation and programming errors propagate.
        try:
            topic_registry = state.get("topic_registry") or ()
            wave0_refs = tuple(state.get("accepted_submission_refs") or ())
            wave1_refs = ()  # Wave1 refs are in the same ledger; for now, all accepted refs
            open_question_ids = tuple(_question_ref_id(ref) for ref in (state.get("wave1_open_questions") or ()))
            open_question_pairs: tuple[tuple[str, str], ...] = ()
            if open_question_ids:
                resolved_texts = await dependencies.synthesis_bundle.read_wave1_open_questions(wave0_refs)
                text_by_id = dict(resolved_texts)
                if any(question_id not in text_by_id for question_id in open_question_ids):
                    raise ValueError("synthesis_question_coverage_invalid")
                open_question_pairs = tuple((question_id, text_by_id[question_id]) for question_id in open_question_ids)
            evidence = await dependencies.synthesis_bundle.read_synthesis_evidence(wave0_refs)
            request = build_synthesis_prompt(
                topic_registry=topic_registry,
                wave0_refs=wave0_refs,
                wave1_refs=wave1_refs,
                evidence=evidence,
                open_questions=open_question_pairs,
            )
        except ValueError as input_error:
            return _exhausted_update(_pre_model_problem(input_error), state=state, dependencies=dependencies)
        outcome = await invoke_and_normalize(
            lambda: dependencies.capabilities.run_agent(context=dependencies.agent_context, request=request),
            phase="wave2_synthesis",
        )
        if isinstance(outcome, InvocationFailure):
            return _exhausted_update(outcome.problem, state=state, dependencies=dependencies)
        result = outcome.result
        try:
            output = _validate_synthesis_semantics(
                parse_synthesis_output(result.summary), wave0_refs, evidence, open_question_ids=open_question_ids
            )
        except ValueError as initial_error:
            validation_category = _synthesis_validation_category(initial_error)
            repair_detail = getattr(initial_error, "detail", None)
            repair_outcome = await invoke_and_normalize(
                lambda: dependencies.capabilities.run_agent(
                    context=dependencies.agent_context,
                    request=build_synthesis_repair_prompt(
                        result.summary,
                        evidence,
                        validation_category=validation_category,
                        open_questions=open_question_pairs,
                        validation_detail=repair_detail,
                    ),
                ),
                phase="wave2_synthesis",
            )
            if isinstance(repair_outcome, InvocationFailure):
                return _exhausted_update(repair_outcome.problem, state=state, dependencies=dependencies)
            repaired = repair_outcome.result
            try:
                output = _validate_synthesis_semantics(
                    parse_synthesis_output(repaired.summary), wave0_refs, evidence, open_question_ids=open_question_ids
                )
            except ValueError as final_error:
                # A still-invalid repaired candidate is a bounded terminal, never
                # an uncaught crash: route exhausted with a typed incident and
                # the concrete semantic category (when the failure is semantic).
                final_category = getattr(final_error, "category", None)
                if final_category is not None:
                    problem = NodeProblem(
                        code=RunFailureCode.OUTPUT_STRUCTURED_INVALID,
                        phase="wave2_synthesis",
                        certainty=FailureCertainty.DIRECT,
                        validation_category=final_category,
                    )
                else:
                    problem = NodeProblem(
                        code=RunFailureCode.OUTPUT_STRUCTURED_INVALID,
                        phase="wave2_synthesis",
                        certainty=FailureCertainty.DIRECT,
                    )
                return _exhausted_update(problem, state=state, dependencies=dependencies)
        await materialize_synthesis(output, dependencies.synthesis_bundle)
        return node_state_update(
            "wave2_synthesis",
            **{WAVE2_GATE_PREVIEW_KEY: build_wave2_gate_preview(output)},
        )

    return run
