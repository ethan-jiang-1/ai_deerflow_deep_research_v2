"""Wave2 synthesis agent prompt and output parser.

@impl WSN-001
@impl WSN-005
@impl WSN-008
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable

from pydantic import ValidationError

from deerflow_deep_research.domain.context import NodeExecutionRequest
from deerflow_deep_research.domain.synthesis import SynthesisEvidence, SynthesisResult
from deerflow_deep_research.domain.untrusted import build_untrusted_data_block

from .capabilities import WAVE2_EVIDENCE_SYNTHESIS, WAVE2_EVIDENCE_SYNTHESIS_REPAIR


class SynthesisValidationFailure(ValueError):
    """A typed deterministic validation failure: concrete category plus a
    bounded repair-time detail.

    Raised by the output parser (schema-invalid candidates) and the semantic
    validator (coverage/backing-refs bookkeeping). It IS a ValueError, so
    existing ``except ValueError:`` seams keep catching it; the concrete
    category and detail are additionally available to the repair-prompt call
    site and the second-validation terminal call site. Schema-invalid
    candidates therefore stay inside the closed ``synthesis_output_*``
    vocabulary instead of escaping as bare pydantic ``ValidationError``
    messages that collapse into the generic ``candidate_invalid`` bucket.
    """

    def __init__(self, category: str, detail: object | None = None) -> None:
        self.category = category
        self.detail = detail
        super().__init__(category)


_SCHEMA_DETAIL_MAX_ERRORS = 3
_SCHEMA_DETAIL_MAX_MSG_CHARS = 120


def _schema_detail(exc: ValidationError) -> dict[str, object]:
    """Bounded projection of the first pydantic errors for repair feedback."""
    errors = [
        {
            "loc": ".".join(str(part) for part in error.get("loc", ())),
            "type": str(error.get("type", "invalid")),
            "msg": str(error.get("msg", ""))[:_SCHEMA_DETAIL_MAX_MSG_CHARS],
        }
        for error in exc.errors()[:_SCHEMA_DETAIL_MAX_ERRORS]
    ]
    return {"schema_errors": errors}


# Derived limits: the built request must always satisfy the domain objective cap
# (NodeExecutionRequest.objective) and the wave2 admission envelope
# (total_token_budget 64_000 minus per_call_output_token_cap 16_384 minus the
# trusted system prompt ~1_268 and the expected-output contract ~1_468). The
# invariant is locked by
# test_synthesis_prompts_bound_evidence_projection_within_request_limits.
_MAX_OBJECTIVE_CHARS = 16_384
_MAX_OBJECTIVE_UTF8_BYTES = 44_800
_EVIDENCE_PROJECTION_START_BYTES = 32_768
_EVIDENCE_PROJECTION_FLOOR_BYTES = 1_024


def _project_evidence(evidence: tuple[SynthesisEvidence, ...], byte_budget: int) -> list[dict[str, object]]:
    """Deterministically truncate evidence contents under one shared byte budget."""

    items: list[dict[str, object]] = [item.model_dump(mode="json") for item in evidence]
    remaining = max(0, byte_budget)
    for index, item in enumerate(items):
        content = str(item.get("content") or "")
        limit = max(0, remaining // max(1, len(items) - index))
        truncated_content = content.encode("utf-8")[:limit].decode("utf-8", "ignore")
        item["content"] = truncated_content
        item["truncated"] = bool(item.get("truncated")) or len(truncated_content) < len(content)
        remaining -= len(truncated_content.encode("utf-8"))
    return items


def _within_request_caps(objective: str) -> bool:
    return len(objective) <= _MAX_OBJECTIVE_CHARS and len(objective.encode("utf-8")) <= _MAX_OBJECTIVE_UTF8_BYTES


def _fitted_objective(
    evidence: Iterable[SynthesisEvidence],
    build_objective: Callable[[str], str],
) -> str:
    """Build an objective whose evidence projection fits the request caps.

    Accepted evidence grows with every targeted-evidence round and previously
    overflowed the domain objective cap as an unclassified pydantic
    ValidationError (BUG-049). The projection budget shrinks geometrically
    until the serialized objective fits both caps; at the floor an oversized
    trusted scaffolding raises a typed, classifiable ValueError instead.
    """

    materialized = tuple(evidence)
    budget = _EVIDENCE_PROJECTION_START_BYTES
    while True:
        payload_json = json.dumps(
            _project_evidence(materialized, budget),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        objective = build_objective(payload_json)
        if _within_request_caps(objective) or budget <= _EVIDENCE_PROJECTION_FLOOR_BYTES:
            if _within_request_caps(objective):
                return objective
            raise ValueError("synthesis_evidence_projection_overflow")
        budget = max(_EVIDENCE_PROJECTION_FLOOR_BYTES, budget * 3 // 4)


def _expected_synthesis_output() -> str:
    return json.dumps(
        {
            "instruction": (
                "Return exactly one JSON object and no markdown, prose, or code fences. "
                "Return findings, relations, gaps, and a summary — NOT a wave1 claims "
                "verdict list (no `claims[]` with claim_id/verdict/support_refs/"
                "counter_refs/reason)."
            ),
            "schema_version": 1,
            "required_keys": ["schema_version", "findings", "relations", "gaps", "summary"],
            "optional_keys": ["resolved_questions"],
            "finding_required_keys": [
                "finding_id",
                "statement",
                "priority",
                "affected_topics",
                "backing_refs",
                "confidence",
                "search_required",
            ],
            "confidence_values": ["high", "medium", "low", "tentative"],
            "relation_required_keys": [
                "relation_id",
                "source_finding",
                "target_finding",
                "relation_type",
            ],
            "relation_type_values": ["supports", "contradicts", "extends", "qualifies"],
            "gap_required_keys": [
                "gap_id",
                "description",
                "priority",
                "affected_topics",
                "search_required",
            ],
            "gap_optional_keys": ["source_questions"],
            "example": {
                "schema_version": 1,
                "findings": [
                    {
                        "finding_id": "f_1",
                        "statement": "One bounded fact from the accepted evidence.",
                        "priority": 1,
                        "affected_topics": ["topic_a"],
                        "backing_refs": ["q:w1_source_a"],
                        "confidence": "high",
                        "search_required": False,
                    }
                ],
                "relations": [
                    {
                        "relation_id": "r_1",
                        "source_finding": "f_1",
                        "target_finding": "f_1",
                        "relation_type": "supports",
                    }
                ],
                "gaps": [
                    {
                        "gap_id": "gap_1",
                        "description": "A question not answerable from accepted evidence.",
                        "priority": 3,
                        "affected_topics": ["topic_a"],
                        "search_required": True,
                        "source_questions": ["q:w1_q1"],
                    }
                ],
                "summary": "One bounded summary.",
                "resolved_questions": ["q:w1_q2"],
            },
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def build_synthesis_prompt(
    topic_registry: Iterable[dict] | None = None,
    wave0_refs: Iterable[str] = (),
    wave1_refs: Iterable[str] = (),
    evidence: Iterable[SynthesisEvidence] = (),
    open_questions: Iterable[tuple[str, str]] = (),
) -> NodeExecutionRequest:
    """Build a bounded synthesis request from accumulated evidence."""
    topics = list(topic_registry or [])
    topic_names = [t.get("title", t.get("topic_id", "")) for t in topics if isinstance(t, dict)]
    question_pairs = [{"question_id": question_id, "question": question} for question_id, question in open_questions][
        :64
    ]
    assignment = json.dumps(
        {
            "accepted_submission_refs": {
                "wave0": sorted(wave0_refs),
                "wave1": sorted(wave1_refs),
            },
            "topics": topic_names[:10],
            "open_questions": question_pairs,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    disposition_contract = ""
    if question_pairs:
        disposition_contract = (
            "\n\nWave1 open-question disposition (closed output contract): every question in the trusted "
            "assignment's open_questions MUST be disposed exactly once — referenced by exactly one gap with "
            "search_required=true through that gap's source_questions list, or listed in resolved_questions. "
            "A question id MUST NOT appear twice or in both places, and no id absent from the assignment may "
            "be used."
        )
    objective = (
        "Use the activated accepted-evidence synthesis capability for this bounded assignment and closed output "
        "contract. The trusted assignment below identifies only graph-assigned topics, accepted submission "
        "references, and Wave1 open questions resolved from accepted evidence.\n\nTrusted assignment:\n"
        + assignment
        + disposition_contract
        + "\n\nUntrusted accepted evidence (deterministically truncated to the request budget):\n"
    )
    objective = _fitted_objective(
        evidence,
        lambda evidence_json: objective + build_untrusted_data_block([evidence_json]),
    )
    return NodeExecutionRequest(
        objective=objective,
        expected_output=_expected_synthesis_output(),
        tools_enabled=False,
        capability_ref=WAVE2_EVIDENCE_SYNTHESIS,
    )


def parse_synthesis_output(text: str) -> SynthesisResult:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("synthesis_output_empty")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("synthesis_output_json_invalid") from exc
    if not isinstance(payload, dict):
        raise ValueError("synthesis_output_not_object")
    try:
        return SynthesisResult.model_validate(payload)
    except ValidationError as exc:
        raise SynthesisValidationFailure("synthesis_output_schema_invalid", detail=_schema_detail(exc)) from exc


def build_synthesis_repair_prompt(
    draft: str,
    evidence: Iterable[SynthesisEvidence] = (),
    *,
    validation_category: str,
    open_questions: Iterable[tuple[str, str]] = (),
    validation_detail: object | None = None,
) -> NodeExecutionRequest:
    question_pairs = [{"question_id": question_id, "question": question} for question_id, question in open_questions][
        :64
    ]
    disposition_contract = ""
    if question_pairs:
        disposition_contract = (
            "\n\nWave1 open-question disposition (closed output contract): every question in the trusted "
            "assignment's open_questions MUST be disposed exactly once — referenced by exactly one gap with "
            "search_required=true through that gap's source_questions list, or listed in resolved_questions. "
            "A question id MUST NOT appear twice or in both places, and no id absent from the assignment may "
            "be used."
        )
    trusted = ""
    if question_pairs or validation_detail is not None:
        trusted = "\n\nTrusted open questions and validation detail:\n" + json.dumps(
            {"open_questions": question_pairs, "validation_detail": validation_detail},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    draft_text = draft[:8_192] if isinstance(draft, str) else ""
    prefix = (
        "Use the activated zero-tool structured repair capability for one bounded assignment and closed output "
        "contract. The trusted validation category below is a parser or semantic category only.\n\n"
        f"Trusted validation category: {validation_category}"
        + disposition_contract
        + trusted
        + "\n\nUntrusted draft and accepted evidence (deterministically truncated to the request budget):\n"
    )
    objective = _fitted_objective(
        evidence,
        lambda evidence_json: (
            prefix + build_untrusted_data_block(["model_draft:\n" + draft_text, "accepted_evidence:\n" + evidence_json])
        ),
    )
    return NodeExecutionRequest(
        objective=objective,
        expected_output=_expected_synthesis_output(),
        tools_enabled=False,
        capability_ref=WAVE2_EVIDENCE_SYNTHESIS_REPAIR,
    )
