"""Readiness critic request, candidate admission, and conservative projection.

@impl REA-002
@impl REA-006
"""

from __future__ import annotations

import json
from collections.abc import Iterable

from deerflow_deep_research.domain.context import NodeExecutionRequest
from deerflow_deep_research.domain.synthesis import SynthesisEvidence
from deerflow_deep_research.domain.untrusted import build_untrusted_data_block

from .capabilities import READINESS_EVIDENCE_CRITIC
from .contracts import PerQuestionVerdict, ReadinessCriticOutput

MAX_READINESS_EVIDENCE_BYTES = 8_192


def _bounded_evidence(evidence: Iterable[SynthesisEvidence]) -> tuple[dict[str, object], ...]:
    items = tuple(evidence)
    if not items:
        return ()
    remaining = MAX_READINESS_EVIDENCE_BYTES
    projection: list[dict[str, object]] = []
    for index, item in enumerate(items):
        remaining_items = len(items) - index
        content_limit = max(0, remaining // remaining_items)
        content = item.content.encode("utf-8")[:content_limit].decode("utf-8", "ignore")
        projection.append(
            {
                "submission_ref": item.submission_ref,
                "phase": item.phase,
                "result_contract": item.result_contract,
                "content": content,
                "truncated": item.truncated or len(content.encode("utf-8")) < len(item.content.encode("utf-8")),
            }
        )
        remaining -= len(content.encode("utf-8"))
    return tuple(projection)


def build_readiness_critic_request(
    must_answer_questions: tuple[str, ...],
    evidence: tuple[SynthesisEvidence, ...],
) -> NodeExecutionRequest:
    """Build one bounded, zero-tool critic request from admitted evidence only."""

    questions = tuple(must_answer_questions)
    if any(not isinstance(question, str) or not question.strip() or len(question) > 500 for question in questions):
        raise ValueError("readiness_question_invalid")
    projection = _bounded_evidence(evidence)
    objective = (
        "Assess answerability for exactly the assigned questions using only the accepted evidence records. "
        "Return no route, report prose, checkpoint field, evidence admission, or authority field. "
        "For every question, return exactly one verdict and backing_claim_ids drawn only from submission_ref values. "
        "Use ready_insufficient_judgment for an honest limitation and blocked_repair_required only when targeted "
        "repair is needed.\n\nAssigned questions:\n"
        + json.dumps(questions, ensure_ascii=False, separators=(",", ":"))
        + "\n\nAccepted evidence records:\n"
        + build_untrusted_data_block(
            [json.dumps(projection, ensure_ascii=False, sort_keys=True, separators=(",", ":"))]
        )
    )
    expected = {
        "instruction": "Return exactly one JSON object and no markdown, prose, or code fences.",
        "schema_version": 1,
        "required_keys": ["schema_version", "per_question"],
        "per_question_required_keys": ["question", "verdict", "backing_claim_ids", "limitation_note"],
        "verdicts": ["ready_substantive", "ready_insufficient_judgment", "blocked_repair_required"],
        "bounds": {
            "per_question": f"exactly {len(questions)} entries",
            "backing_claim_ids": "accepted submission refs only",
        },
    }
    return NodeExecutionRequest(
        objective=objective,
        expected_output=json.dumps(expected, sort_keys=True, separators=(",", ":")),
        tools_enabled=False,
        capability_ref=READINESS_EVIDENCE_CRITIC,
    )


def parse_readiness_critic_output(text: str) -> ReadinessCriticOutput:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("readiness_critic_output_empty")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("readiness_critic_output_json_invalid") from exc
    if not isinstance(payload, dict):
        raise ValueError("readiness_critic_output_not_object")
    return ReadinessCriticOutput.model_validate(payload)


def admit_readiness_candidate(
    candidate: ReadinessCriticOutput,
    *,
    must_answer_questions: tuple[str, ...],
    accepted_submission_refs: tuple[str, ...],
) -> ReadinessCriticOutput:
    """Admit only the exact question set and references from the trusted projection."""

    expected_questions = tuple(must_answer_questions)
    observed_questions = tuple(item.question for item in candidate.per_question)
    if len(set(expected_questions)) != len(expected_questions) or len(set(observed_questions)) != len(
        observed_questions
    ):
        raise ValueError("readiness_critic_question_duplicate")
    if set(observed_questions) != set(expected_questions) or len(observed_questions) != len(expected_questions):
        raise ValueError("readiness_critic_question_set_invalid")
    accepted = set(accepted_submission_refs)
    by_question = {item.question: item for item in candidate.per_question}
    admitted: list[PerQuestionVerdict] = []
    for question in expected_questions:
        item = by_question[question]
        if not set(item.backing_claim_ids) <= accepted:
            raise ValueError("readiness_critic_backing_ref_invalid")
        admitted.append(item)
    return ReadinessCriticOutput(schema_version=1, per_question=tuple(admitted))


def conservative_readiness_output(must_answer_questions: tuple[str, ...]) -> ReadinessCriticOutput:
    """Project critic observation failure as disclosed insufficient judgment."""

    return ReadinessCriticOutput(
        schema_version=1,
        per_question=tuple(
            PerQuestionVerdict(
                question=question,
                verdict="ready_insufficient_judgment",
                limitation_note="Readiness critic did not produce an admissible answerability verdict.",
            )
            for question in must_answer_questions
        ),
    )


def checkpointed_critic_summary(output: ReadinessCriticOutput) -> dict[str, object]:
    """Retain only the materializer-consumed admitted projection in graph state."""

    return {
        "schema_version": output.schema_version,
        "per_question": [item.model_dump(mode="json") for item in output.per_question],
    }


__all__ = [
    "admit_readiness_candidate",
    "build_readiness_critic_request",
    "checkpointed_critic_summary",
    "conservative_readiness_output",
    "parse_readiness_critic_output",
]
