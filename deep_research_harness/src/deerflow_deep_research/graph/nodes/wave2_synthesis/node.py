"""Real Wave2 synthesis node — cross-topic synthesis from accepted evidence.

@impl WSN-001
@impl WFO-001
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from deerflow_deep_research.domain.lifecycle import LifecycleStatus, TerminalReason
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.run_experience import NodeProblem, TerminalIncidentProjection
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
        raise ValueError("synthesis_findings_required")
    for finding in output.findings:
        normalized_refs = tuple(aliases.get(ref, ref) for ref in finding.backing_refs)
        finding = finding.model_copy(update={"backing_refs": normalized_refs})
        backing_refs = set(normalized_refs)
        if not backing_refs:
            raise ValueError("synthesis_finding_backing_refs_required")
        if not backing_refs <= accepted:
            raise ValueError("synthesis_finding_backing_ref_invalid")
    if open_question_ids:
        expected = set(open_question_ids)
        gap_covered: set[str] = set()
        for gap in output.gaps:
            if not gap.search_required:
                if gap.source_questions:
                    raise ValueError("synthesis_question_coverage_invalid")
                continue
            if gap_covered & set(gap.source_questions):
                raise ValueError("synthesis_question_coverage_invalid")
            gap_covered |= set(gap.source_questions)
        resolved = set(output.resolved_questions)
        if gap_covered & resolved:
            raise ValueError("synthesis_question_coverage_invalid")
        if (gap_covered | resolved) != expected:
            raise ValueError("synthesis_question_coverage_invalid")
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
            repair_outcome = await invoke_and_normalize(
                lambda: dependencies.capabilities.run_agent(
                    context=dependencies.agent_context,
                    request=build_synthesis_repair_prompt(
                        result.summary,
                        evidence,
                        validation_category=validation_category,
                    ),
                ),
                phase="wave2_synthesis",
            )
            if isinstance(repair_outcome, InvocationFailure):
                return _exhausted_update(repair_outcome.problem, state=state, dependencies=dependencies)
            repaired = repair_outcome.result
            output = _validate_synthesis_semantics(
                parse_synthesis_output(repaired.summary), wave0_refs, evidence, open_question_ids=open_question_ids
            )
        await materialize_synthesis(output, dependencies.synthesis_bundle)
        return node_state_update(
            "wave2_synthesis",
            **{WAVE2_GATE_PREVIEW_KEY: build_wave2_gate_preview(output)},
        )

    return run
