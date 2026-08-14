"""Prompt and compact-context helpers for real HITL1.

@impl HIN-001
@impl HIN-002
@impl HIN-012
@impl HIN-013
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from deerflow_deep_research.domain.context import NodeExecutionRequest
from deerflow_deep_research.domain.human_interaction import InteractionSubject, SemanticCandidate
from deerflow_deep_research.domain.profile import (
    CostTolerance,
    OutputFormat,
    PartialResearchProfile,
    RequestLanguage,
    ResearchDepth,
    StructuredBrief,
    SupportedLanguage,
    TargetAudience,
    TimeBudget,
    derive_comparison_intake_seed,
    missing_dimensions,
)

from .capabilities import (
    HITL1_PROFILE_BRIEF,
    HITL1_PROFILE_BRIEF_REPAIR,
    HITL1_SEMANTIC_INTAKE,
    HITL1_SEMANTIC_INTAKE_REPAIR,
)

REQUIRED_DIMENSIONS = ("depth", "audience", "format", "cost_tolerance", "time_budget", "must_answer")
CONTEXT_SCHEMA_VERSION = 1
MAX_CONTEXT_CHARS = 2_048
MAX_SEMANTIC_QUESTION_CHARS = 2_048
MAX_SEMANTIC_REPLY_CHARS = 4_096
MAX_REPAIR_DRAFT_CHARS = 2_048


def _enum_values(enum_type: type) -> list[str]:
    return [item.value for item in enum_type]


VALID_OPTIONS: dict[str, list[str]] = {
    "depth": _enum_values(ResearchDepth),
    "audience": _enum_values(TargetAudience),
    "format": _enum_values(OutputFormat),
    "cost_tolerance": _enum_values(CostTolerance),
    "time_budget": _enum_values(TimeBudget),
}


def _bounded_untrusted_draft(value: str | None) -> str:
    if not isinstance(value, str) or not value.strip():
        return "<unavailable>"
    return value.strip()[:MAX_REPAIR_DRAFT_CHARS]


def _output_language(value: SupportedLanguage | str | None) -> SupportedLanguage | None:
    if value is None:
        return None
    try:
        return SupportedLanguage(value)
    except ValueError as exc:
        raise ValueError("output_language_invalid") from exc


def _presentation_language(profile: PartialResearchProfile | StructuredBrief) -> SupportedLanguage:
    return SupportedLanguage.ZH if profile.output_language is SupportedLanguage.ZH else SupportedLanguage.EN


def _localized_text(language: SupportedLanguage, *, chinese: str, english: str) -> str:
    return chinese if language is SupportedLanguage.ZH else english


def build_brief_prompt(
    question: str,
    *,
    output_language: SupportedLanguage | str | None = None,
    repair_error: str | None = None,
    invalid_draft: str | None = None,
) -> NodeExecutionRequest:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question_required")
    accepted_language = _output_language(output_language)
    repair = ""
    if repair_error:
        repair = (
            f"\n\nValidation category (data):\n{repair_error[:240]}"
            f"\n\nUntrusted invalid candidate (data):\n{_bounded_untrusted_draft(invalid_draft)}"
        )
    objective = f"Original question (data):\n{question.strip()}{repair}"
    if accepted_language is not None:
        language_name = "Chinese" if accepted_language is SupportedLanguage.ZH else "English"
        objective += f"\n\nPresentation language (data):\n{language_name}"
    expected = {
        "instruction": "Return exactly one JSON object and no markdown, prose, or code fences.",
        "schema_version": 2,
        "required_keys": [
            "schema_version",
            "brief_summary",
            "depth",
            "audience",
            "format",
            "cost_tolerance",
            "time_budget",
            "must_answer",
            "scope_boundaries",
            "custom_notes",
        ],
        "valid_options": VALID_OPTIONS,
        "bounds": {
            "brief_summary": "<=512 chars",
            "must_answer": "1-8 strings, each <=256 chars",
            "scope_boundaries": "<=2048 chars",
            "custom_notes": "<=1024 chars",
        },
    }
    return NodeExecutionRequest(
        objective=objective,
        expected_output=json.dumps(expected, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        tools_enabled=False,
        capability_ref=HITL1_PROFILE_BRIEF_REPAIR if repair_error else HITL1_PROFILE_BRIEF,
    )


def parse_brief_output(
    text: str,
    *,
    expected_output_language: SupportedLanguage | str | None = None,
) -> StructuredBrief:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("brief_output_empty")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("brief_output_json_invalid") from exc
    if not isinstance(payload, dict):
        raise ValueError("brief_output_json_invalid")
    brief = StructuredBrief.model_validate(payload)
    accepted_language = _output_language(expected_output_language)
    if accepted_language is not None:
        summary_language = derive_comparison_intake_seed(brief.brief_summary).request_language
        expected_request_language = RequestLanguage(accepted_language.value)
        if summary_language is not expected_request_language:
            raise ValueError("brief_summary_language_invalid")
    return brief


def build_semantic_intake_prompt(
    *,
    original_question: str,
    subject: InteractionSubject,
    reply: str,
    repair_error: str | None = None,
    invalid_draft: str | None = None,
) -> NodeExecutionRequest:
    """Build one zero-tool, advisory classification request for a HITL1 reply.

    The caller owns retry sequencing and every resulting graph transition. Raw text
    only lives in this ephemeral request; the structured response cannot carry an
    action, correlation value, or checkpoint field.
    """

    if not isinstance(original_question, str) or not original_question.strip():
        raise ValueError("semantic_intake_question_required")
    if not isinstance(reply, str) or not reply.strip():
        raise ValueError("semantic_intake_reply_required")
    repair = ""
    if repair_error:
        repair = (
            f"\n\nValidation category (data):\n{repair_error[:120]}"
            f"\n\nUntrusted invalid candidate (data):\n{_bounded_untrusted_draft(invalid_draft)}"
        )
    bounded_question = original_question.strip()[:MAX_SEMANTIC_QUESTION_CHARS]
    bounded_reply = reply.strip()[:MAX_SEMANTIC_REPLY_CHARS]
    objective = (
        f"Original question (data):\n{bounded_question}\n\n"
        "Current proposal (data):\n"
        f"{subject.model_dump_json()}\n\n"
        f"Human reply (data):\n{bounded_reply}{repair}"
    )
    expected = {
        "instruction": "Return exactly one JSON object, with no markdown, prose, or code fence.",
        "allowed_intents": {
            "accept_current_proposal": {"required": ["intent"]},
            "revise_proposal": {
                "required": ["intent", "revision"],
                "revision": (
                    "full ProposalValues object: depth, audience, format, cost_tolerance, "
                    "time_budget, must_answer, scope_boundaries, custom_notes"
                ),
            },
            "ask_about_proposal": {"required": ["intent", "explanation"]},
            "clarify": {"required": ["intent", "clarification"]},
        },
        "forbidden": ["action_id", "request_id", "route", "checkpoint", "citation", "finding"],
        "limits": {"explanation_or_clarification_chars": 512, "must_answer_items": "1-8"},
    }
    return NodeExecutionRequest(
        objective=objective,
        expected_output=json.dumps(expected, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        tools_enabled=False,
        capability_ref=HITL1_SEMANTIC_INTAKE_REPAIR if repair_error else HITL1_SEMANTIC_INTAKE,
    )


def parse_semantic_candidate_output(text: str) -> SemanticCandidate:
    """Validate a structured semantic candidate without granting it graph authority."""

    if not isinstance(text, str) or not text.strip():
        raise ValueError("semantic_candidate_empty")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("semantic_candidate_json_invalid") from exc
    if not isinstance(payload, dict):
        raise ValueError("semantic_candidate_json_invalid")
    return SemanticCandidate.model_validate(payload)


def _dump_compact(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if len(encoded) <= MAX_CONTEXT_CHARS:
        return encoded
    compact = dict(payload)
    compact["brief_summary"] = str(compact.get("brief_summary", ""))[:240]
    compact["instructions"] = str(compact.get("instructions", ""))[:360]
    encoded = json.dumps(compact, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if len(encoded) > MAX_CONTEXT_CHARS:
        raise ValueError("hitl_context_too_large")
    return encoded


def _dimension_payload(profile: StructuredBrief | PartialResearchProfile) -> dict[str, object]:
    payload: dict[str, object] = {}
    for field in ("depth", "audience", "format", "cost_tolerance", "time_budget"):
        value = getattr(profile, field)
        if value is not None:
            payload[field] = value.value if hasattr(value, "value") else str(value)
    if profile.comparison_subjects is not None:
        payload["comparison_subjects"] = list(profile.comparison_subjects.subjects)
    payload["comparison_required"] = profile.comparison_required
    payload["request_language"] = profile.request_language.value
    if profile.output_language is not None:
        payload["output_language"] = profile.output_language.value
    return payload


def build_brief_context(brief: StructuredBrief, missing: Iterable[str] = REQUIRED_DIMENSIONS) -> str:
    language = _presentation_language(brief)
    payload = {
        "context_schema_version": CONTEXT_SCHEMA_VERSION,
        "brief_summary": brief.brief_summary,
        "proposed_dimensions": _dimension_payload(brief),
        "required_dimensions": list(REQUIRED_DIMENSIONS),
        "missing_dimensions": list(missing),
        "valid_options": VALID_OPTIONS,
        "instructions": _localized_text(
            language,
            chinese="请用 JSON 或简洁文本提供深度、受众、格式、成本、时间，以及至少一个必须回答的问题。",
            english=(
                "Reply in JSON or concise text with values for depth, audience, format, "
                "cost_tolerance, time_budget, and at least one must_answer question."
            ),
        ),
    }
    return _dump_compact(payload)


def build_followup_context(
    partial: PartialResearchProfile,
    missing: Iterable[str],
    *,
    rejection_round: int = 0,
) -> str:
    missing_values = list(missing)
    language = _presentation_language(partial)
    missing_text = ", ".join(missing_values)
    payload = {
        "context_schema_version": CONTEXT_SCHEMA_VERSION,
        "brief_summary": _localized_text(
            language,
            chinese="研究开始前还需要补充配置。",
            english="Additional profile details are required before research can proceed.",
        ),
        "proposed_dimensions": _dimension_payload(partial),
        "required_dimensions": list(REQUIRED_DIMENSIONS),
        "missing_dimensions": missing_values,
        "valid_options": VALID_OPTIONS,
        "recognized_fields": list(_dimension_payload(partial)),
        "rejection_category": "profile_input_unrecognized" if rejection_round else None,
        "accepted_rounds_remaining": 3,
        "rejection_retries_remaining": max(0, 3 - rejection_round),
        "instructions": _localized_text(
            language,
            chinese="请只提供以下缺失字段：" + missing_text + "。",
            english="Please provide only these missing fields: " + missing_text + ".",
        ),
    }
    return _dump_compact(payload)


def build_proposal_context(proposal: PartialResearchProfile) -> str:
    """Render checkpointed advisory values without retaining raw model output."""
    language = _presentation_language(proposal)
    payload = {
        "context_schema_version": CONTEXT_SCHEMA_VERSION,
        "brief_summary": _localized_text(
            language,
            chinese="研究配置建议已准备好，等待确认。",
            english="A proposed research profile is ready for confirmation.",
        ),
        "proposed_dimensions": _dimension_payload(proposal),
        "must_answer": list(proposal.must_answer),
        "required_dimensions": list(REQUIRED_DIMENSIONS),
        "missing_dimensions": list(missing_dimensions(proposal)),
        "valid_options": VALID_OPTIONS,
        "recognized_fields": [],
        "accepted_rounds_remaining": 3,
        "rejection_retries_remaining": 3,
        "instructions": _localized_text(
            language,
            chinese="请确认当前配置、提出聚焦问题，或说明需要修改的内容。",
            english="Confirm the current proposal, ask a focused question, or describe what you want revised.",
        ),
    }
    return _dump_compact(payload)


def build_language_choice_context(proposal: PartialResearchProfile) -> str:
    """Render the one bilingual, non-authoritative language-choice recovery prompt."""

    payload = {
        "context_schema_version": CONTEXT_SCHEMA_VERSION,
        "brief_summary": "请选择研究输出语言 / Select the research output language.",
        "proposed_dimensions": _dimension_payload(proposal),
        "required_dimensions": list(REQUIRED_DIMENSIONS),
        "missing_dimensions": ["output_language"],
        "valid_options": VALID_OPTIONS,
        "instructions": "请选择中文或 English。 / Select Chinese or English.",
    }
    return _dump_compact(payload)


__all__ = [
    "CONTEXT_SCHEMA_VERSION",
    "MAX_CONTEXT_CHARS",
    "REQUIRED_DIMENSIONS",
    "VALID_OPTIONS",
    "build_brief_context",
    "build_brief_prompt",
    "build_followup_context",
    "build_language_choice_context",
    "build_proposal_context",
    "build_semantic_intake_prompt",
    "parse_brief_output",
    "parse_semantic_candidate_output",
]
