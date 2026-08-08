"""Pure HITL1 research-profile contracts.

@impl HIN-001
@impl HIN-003
@impl HIN-004
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import unicodedata
from collections.abc import Mapping
from enum import StrEnum
from typing import Any, Literal, Protocol, runtime_checkable

from pydantic import ConfigDict, Field, field_validator, model_validator

from deerflow_deep_research.domain.lifecycle import FrozenContract
from deerflow_deep_research.domain.state import BundleLocalState, ContentRef

MAX_MUST_ANSWER = 8
MAX_QUESTION_CHARS = 256
MAX_SCOPE_CHARS = 2_048
MAX_NOTES_CHARS = 1_024
MAX_BRIEF_SUMMARY_CHARS = 512
PROFILE_SCHEMA_VERSION = 2
LEGACY_PROFILE_SCHEMA_VERSION = 1
MAX_COMPARISON_SUBJECT_CHARS = 256


class ResearchDepth(StrEnum):
    QUICK_OVERVIEW = "quick_overview"
    STANDARD = "standard"
    DEEP_DIVE = "deep_dive"
    EXHAUSTIVE = "exhaustive"


class TargetAudience(StrEnum):
    LAYPERSON = "layperson"
    PRACTITIONER = "practitioner"
    DOMAIN_EXPERT = "domain_expert"
    EXECUTIVE = "executive"


class OutputFormat(StrEnum):
    EXECUTIVE_BRIEF = "executive_brief"
    DETAILED_REPORT = "detailed_report"
    ANNOTATED_BIBLIOGRAPHY = "annotated_bibliography"
    FAQ = "faq"


class CostTolerance(StrEnum):
    MINIMAL = "minimal"
    MODERATE = "moderate"
    EXTENSIVE = "extensive"


class TimeBudget(StrEnum):
    VERY_QUICK = "very_quick"
    STANDARD = "standard"
    THOROUGH = "thorough"
    OVERNIGHT = "overnight"


class RequestLanguage(StrEnum):
    ZH = "zh"
    EN = "en"
    UNSPECIFIED = "unspecified"
    LEGACY_UNSPECIFIED = "legacy_unspecified"


class SupportedLanguage(StrEnum):
    ZH = "zh"
    EN = "en"


def _normalize_subject(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("comparison_subjects_invalid")
    normalized = " ".join(unicodedata.normalize("NFKC", value).split())
    if not 1 <= len(normalized) <= MAX_COMPARISON_SUBJECT_CHARS:
        raise ValueError("comparison_subjects_invalid")
    return normalized


class ComparisonSubjects(FrozenContract):
    """Ordered, canonical comparison scope supplied by a user or local parser."""

    subjects: tuple[str, str]

    @field_validator("subjects", mode="before")
    @classmethod
    def normalize_subjects(cls, value: Any) -> tuple[str, str]:
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            raise ValueError("comparison_subjects_cardinality_invalid")
        return (_normalize_subject(value[0]), _normalize_subject(value[1]))

    @model_validator(mode="after")
    def require_distinct_subjects(self) -> ComparisonSubjects:
        if self.subjects[0].casefold() == self.subjects[1].casefold():
            raise ValueError("comparison_subjects_distinct_invalid")
        return self


class ComparisonIntakeSeed(FrozenContract):
    """Immutable local facts derived from the original request."""

    comparison_required: bool
    comparison_subjects: ComparisonSubjects | None = None
    request_language: RequestLanguage
    output_language: SupportedLanguage | None = None


_CHINESE_COMPARISON_MARKERS = re.compile(r"比较|对比")
_ENGLISH_COMPARISON_MARKERS = re.compile(r"\b(?:compare|comparison|versus|vs)\b", flags=re.IGNORECASE)
_CHINESE_COMPARISON_PAIR = re.compile(
    r"(?:比较|对比)\s*(?P<first>.+?)\s*(?:和|与|vs)\s*(?P<second>.+)",
    flags=re.IGNORECASE,
)
_ENGLISH_COMPARISON_PAIR = re.compile(
    r"\b(?:compare|comparison)\s+(?P<first>.+?)\s+(?:and|with|vs|versus)\s+(?P<second>.+)",
    flags=re.IGNORECASE,
)
_SUBJECT_LIST_SEPARATOR = re.compile(r"[、,，;；]")
_CLEAR_CONFIRMATIONS = frozenset(
    {
        "可以",
        "好的",
        "同意",
        "确认",
        "可以,我觉得你说的挺好",
        "yes",
        "yes please",
        "looks good",
        "i agree",
        "confirm",
        "confirmed",
    }
)


def derive_comparison_intake_seed(request_text: str) -> ComparisonIntakeSeed:
    """Derive only the reviewed local comparison and language facts."""

    normalized = unicodedata.normalize("NFKC", request_text if isinstance(request_text, str) else "")
    if any("\u4e00" <= character <= "\u9fff" for character in normalized):
        request_language = RequestLanguage.ZH
        output_language: SupportedLanguage | None = SupportedLanguage.ZH
    elif re.search(r"[A-Za-z]", normalized):
        request_language = RequestLanguage.EN
        output_language = SupportedLanguage.EN
    else:
        request_language = RequestLanguage.UNSPECIFIED
        output_language = None

    comparison_required = bool(
        _CHINESE_COMPARISON_MARKERS.search(normalized) or _ENGLISH_COMPARISON_MARKERS.search(normalized)
    )
    subjects: ComparisonSubjects | None = None
    if comparison_required:
        match = _CHINESE_COMPARISON_PAIR.search(normalized) or _ENGLISH_COMPARISON_PAIR.search(normalized)
        if match is not None:
            try:
                candidates = (match.group("first"), match.group("second"))
                if not any(_SUBJECT_LIST_SEPARATOR.search(candidate) for candidate in candidates):
                    subjects = ComparisonSubjects(subjects=candidates)
            except ValueError:
                subjects = None
    return ComparisonIntakeSeed(
        comparison_required=comparison_required,
        comparison_subjects=subjects,
        request_language=request_language,
        output_language=output_language,
    )


def normalize_clear_confirmation(reply: str) -> bool:
    """Recognize exactly the finite local confirmation set before semantic intake."""

    if not isinstance(reply, str):
        return False
    normalized = " ".join(unicodedata.normalize("NFKC", reply).split()).casefold().strip()
    normalized = normalized.rstrip(".!?。！？").strip()
    return normalized in _CLEAR_CONFIRMATIONS


_DIMENSION_FIELDS = ("depth", "audience", "format", "cost_tolerance", "time_budget")
_REQUIRED_FIELDS = (*_DIMENSION_FIELDS, "must_answer")


class _ProfileBase(FrozenContract):
    model_config = ConfigDict(frozen=True, extra="forbid")

    # An absent schema in retained checkpoint values denotes the former v1 payload.
    # New HITL1 writes explicitly seed schema v2 before profile materialization.
    schema_version: Literal[1, 2] = LEGACY_PROFILE_SCHEMA_VERSION
    must_answer: tuple[str, ...] = Field(default=(), max_length=MAX_MUST_ANSWER)
    scope_boundaries: str = Field(default="", max_length=MAX_SCOPE_CHARS)
    custom_notes: str = Field(default="", max_length=MAX_NOTES_CHARS)
    comparison_required: bool = False
    comparison_subjects: ComparisonSubjects | None = None
    request_language: RequestLanguage = RequestLanguage.LEGACY_UNSPECIFIED
    output_language: SupportedLanguage | None = None

    @field_validator("comparison_subjects", mode="before")
    @classmethod
    def coerce_comparison_subjects(cls, value: Any) -> Any:
        if isinstance(value, (tuple, list)):
            return {"subjects": value}
        return value

    @field_validator("must_answer", mode="before")
    @classmethod
    def normalize_questions(cls, value: Any) -> tuple[str, ...]:
        if value is None:
            return ()
        if isinstance(value, str):
            value = (value,)
        if not isinstance(value, (tuple, list)):
            raise ValueError("must_answer_invalid")
        normalized: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError("must_answer_invalid")
            text = item.strip()
            if not text or len(text) > MAX_QUESTION_CHARS:
                raise ValueError("must_answer_invalid")
            normalized.append(text)
        if len(normalized) > MAX_MUST_ANSWER:
            raise ValueError("must_answer_invalid")
        return tuple(normalized)


class StructuredBrief(_ProfileBase):
    brief_summary: str = Field(min_length=1, max_length=MAX_BRIEF_SUMMARY_CHARS)
    depth: ResearchDepth
    audience: TargetAudience
    format: OutputFormat
    cost_tolerance: CostTolerance
    time_budget: TimeBudget
    must_answer: tuple[str, ...] = Field(min_length=1, max_length=MAX_MUST_ANSWER)


class PartialResearchProfile(_ProfileBase):
    depth: ResearchDepth | None = None
    audience: TargetAudience | None = None
    format: OutputFormat | None = None
    cost_tolerance: CostTolerance | None = None
    time_budget: TimeBudget | None = None


class ProfileParseResult(FrozenContract):
    """Deterministic, bounded recognition result for one HITL1 text response."""

    partial: PartialResearchProfile
    recognized_fields: tuple[str, ...] = Field(default=(), max_length=10)

    @model_validator(mode="after")
    def fields_match_partial(self) -> ProfileParseResult:
        allowed = frozenset(
            (
                *_DIMENSION_FIELDS,
                "must_answer",
                "scope_boundaries",
                "custom_notes",
                "comparison_subjects",
                "output_language",
            )
        )
        if len(set(self.recognized_fields)) != len(self.recognized_fields) or set(self.recognized_fields) - allowed:
            raise ValueError("recognized_fields_invalid")
        return self


class ResearchProfile(PartialResearchProfile):
    degraded_profile: bool = False

    @model_validator(mode="after")
    def require_complete_profile_unless_degraded(self) -> ResearchProfile:
        if self.degraded_profile:
            return self
        missing = missing_dimensions(self)
        if missing:
            raise ValueError(f"profile_incomplete:{','.join(missing)}")
        return self


@runtime_checkable
class RequestBundleStoreProtocol(Protocol):
    async def read_profile(self, profile_ref: ContentRef) -> ResearchProfile: ...

    async def write_profile(self, profile: ResearchProfile) -> ContentRef: ...

    async def read_bundle_state(self) -> BundleLocalState: ...

    async def write_bundle_state(
        self,
        state: BundleLocalState,
        *,
        expected_revision: int,
    ) -> BundleLocalState: ...


def _canonical_value(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, FrozenContract):
        return _canonical_value(value.model_dump(mode="python"))
    if isinstance(value, Mapping):
        return {str(key): _canonical_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_canonical_value(item) for item in value]
    return value


def canonical_profile_bytes(profile: ResearchProfile) -> bytes:
    if not isinstance(profile, ResearchProfile):
        raise TypeError("profile_required")
    return json.dumps(
        _canonical_value(profile),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_profile_json(profile: ResearchProfile) -> str:
    return canonical_profile_bytes(profile).decode("utf-8")


def compute_profile_content_hash(profile: ResearchProfile) -> str:
    digest = hashlib.sha256(canonical_profile_bytes(profile)).digest()
    return "h_" + base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def missing_dimensions(profile: PartialResearchProfile | ResearchProfile) -> tuple[str, ...]:
    missing = [field for field in _DIMENSION_FIELDS if getattr(profile, field) is None]
    if not profile.must_answer:
        missing.append("must_answer")
    if profile.schema_version == PROFILE_SCHEMA_VERSION:
        if profile.comparison_required and profile.comparison_subjects is None:
            missing.append("comparison_subjects")
        if profile.output_language is None:
            missing.append("output_language")
    return tuple(missing)


def merge_profile_progress(
    current: PartialResearchProfile | Mapping[str, Any] | None,
    incoming: PartialResearchProfile | Mapping[str, Any],
) -> PartialResearchProfile:
    base = PartialResearchProfile.model_validate(current or {})
    update = (
        incoming if isinstance(incoming, PartialResearchProfile) else PartialResearchProfile.model_validate(incoming)
    )
    payload = base.model_dump(mode="python")
    for field in _DIMENSION_FIELDS:
        value = getattr(update, field)
        if value is not None:
            payload[field] = value
    if update.must_answer:
        payload["must_answer"] = update.must_answer
    if update.scope_boundaries:
        payload["scope_boundaries"] = update.scope_boundaries
    if update.custom_notes:
        payload["custom_notes"] = update.custom_notes
    if update.comparison_subjects is not None:
        payload["comparison_subjects"] = update.comparison_subjects
    if update.output_language is not None:
        payload["output_language"] = update.output_language
    return PartialResearchProfile.model_validate(payload)


def finalize_profile(profile: PartialResearchProfile | Mapping[str, Any], *, degraded: bool = False) -> ResearchProfile:
    progress = (
        profile if isinstance(profile, PartialResearchProfile) else PartialResearchProfile.model_validate(profile)
    )
    return ResearchProfile.model_validate(progress.model_dump(mode="python") | {"degraded_profile": degraded})


def profile_state_fields(profile: ResearchProfile, profile_ref: ContentRef) -> dict[str, Any]:
    if not isinstance(profile_ref, ContentRef):
        raise TypeError("profile_ref_required")
    return {
        "profile_ref": profile_ref,
        "research_depth": profile.depth.value if profile.depth is not None else "",
        "target_audience": profile.audience.value if profile.audience is not None else "",
        "output_format": profile.format.value if profile.format is not None else "",
        "cost_tolerance": profile.cost_tolerance.value if profile.cost_tolerance is not None else "",
        "time_budget": profile.time_budget.value if profile.time_budget is not None else "",
        "must_answer_questions": profile.must_answer,
        "comparison_required": profile.comparison_required,
        "comparison_subjects": profile.comparison_subjects.subjects if profile.comparison_subjects is not None else (),
        "request_language": profile.request_language.value,
        "output_language": profile.output_language.value if profile.output_language is not None else "",
        "degraded_profile": profile.degraded_profile,
        "pending_profile": None,
        "profile_followup_round": 0,
        "proposed_profile": None,
        "profile_rejection_round": 0,
        "profile_feedback_cursor_message_id": "",
        "proposal_version": 0,
        "interaction_feedback": None,
    }


_ENUMS: dict[str, type[StrEnum]] = {
    "depth": ResearchDepth,
    "audience": TargetAudience,
    "format": OutputFormat,
    "cost_tolerance": CostTolerance,
    "time_budget": TimeBudget,
}

_JSON_ALIASES = {
    "research_depth": "depth",
    "target_audience": "audience",
    "output_format": "format",
    "must_answer_questions": "must_answer",
}

_TEXT_SYNONYMS: dict[str, dict[str, tuple[str, ...]]] = {
    "depth": {
        "quick_overview": ("quick overview", "quick_overview", "brief overview", "快速概览", "快速"),
        "standard": ("standard depth", "standard-depth", "标准深度"),
        "deep_dive": ("deep dive", "deep_dive", "深度研究", "深度"),
        "exhaustive": ("exhaustive", "详尽", "穷尽"),
    },
    "audience": {
        "layperson": ("layperson", "general audience", "non expert", "non-expert", "普通读者"),
        "practitioner": ("practitioner", "practitioners", "实践者"),
        "domain_expert": ("domain expert", "domain_expert", "expert audience", "领域专家"),
        "executive": ("executive", "executives", "管理者", "高管"),
    },
    "format": {
        "executive_brief": ("executive brief", "executive_brief", "执行摘要"),
        "detailed_report": ("detailed report", "detailed_report", "详细报告"),
        "annotated_bibliography": ("annotated bibliography", "annotated_bibliography", "注释书目"),
        "faq": ("faq", "q&a", "q and a", "问答"),
    },
    "cost_tolerance": {
        "minimal": ("minimal cost", "minimal", "最低成本"),
        "moderate": ("moderate cost", "moderate", "适中成本"),
        "extensive": ("extensive cost", "extensive", "高成本"),
    },
    "time_budget": {
        "very_quick": ("very quick", "very_quick", "很快"),
        "standard": ("standard time", "standard timeline", "标准时间"),
        "thorough": ("thorough", "充分"),
        "overnight": ("overnight", "隔夜"),
    },
}


def _enum_or_none(enum_type: type[StrEnum], value: Any) -> StrEnum | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower().replace(" ", "_").replace("-", "_")
    try:
        return enum_type(normalized)
    except ValueError:
        return None


def _parse_json_response(text: str) -> dict[str, Any]:
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("profile_response_json_invalid") from exc
    if not isinstance(raw, dict):
        raise ValueError("profile_response_json_invalid")
    allowed = (
        set(_REQUIRED_FIELDS)
        | {"scope_boundaries", "custom_notes", "schema_version", "comparison_subjects", "output_language"}
        | set(_JSON_ALIASES)
    )
    extra = set(raw) - allowed
    if extra:
        raise ValueError("profile_response_extra_fields")
    normalized: dict[str, Any] = {}
    for key, value in raw.items():
        field = _JSON_ALIASES.get(key, key)
        if field in _ENUMS:
            enum_value = _enum_or_none(_ENUMS[field], value)
            if enum_value is not None:
                normalized[field] = enum_value
            continue
        if field == "output_language":
            language = _enum_or_none(SupportedLanguage, value)
            if language is not None:
                normalized[field] = language
            continue
        normalized[field] = value
    return normalized


def _contains_phrase(text: str, phrase: str) -> bool:
    if any("\u4e00" <= character <= "\u9fff" for character in phrase):
        return phrase in text
    normalized = re.escape(phrase.lower()).replace(r"\ ", r"[\s_-]+")
    return re.search(rf"(?<![a-z0-9]){normalized}(?![a-z0-9])", text) is not None


def _parse_text_response(text: str) -> dict[str, Any]:
    lowered = text.lower().replace("_", " ")
    payload: dict[str, Any] = {}
    for field, values in _TEXT_SYNONYMS.items():
        matches: list[tuple[str, int]] = []
        for value, phrases in values.items():
            lengths = [len(phrase) for phrase in phrases if _contains_phrase(lowered, phrase)]
            if lengths:
                matches.append((value, max(lengths)))
        if matches:
            longest = max(length for _, length in matches)
            winners = {value for value, length in matches if length == longest}
            if len(winners) == 1:
                payload[field] = winners.pop()

    must_match = re.search(r"must\s+answer\s*:?\s*(?P<body>.+)$", text, flags=re.IGNORECASE)
    if must_match:
        body = must_match.group("body")
        questions = [item.strip(" ;.") for item in re.split(r"\s+(?:and|&)\s+|[,;\n]+", body) if item.strip(" ;.")]
        if questions:
            payload["must_answer"] = tuple(questions[:MAX_MUST_ANSWER])
    return payload


def parse_profile_input(text: str, *, allow_comparison_pair: bool = False) -> ProfileParseResult:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("profile_response_empty")
    stripped = text.strip()
    payload = _parse_json_response(stripped) if stripped.startswith(("{", "[")) else _parse_text_response(stripped)
    if allow_comparison_pair and not payload:
        pair = re.fullmatch(r"\s*(?P<first>[^|]+?)\s*\|\s*(?P<second>[^|]+?)\s*", stripped)
        if pair is not None:
            payload["comparison_subjects"] = (pair.group("first"), pair.group("second"))
    partial = PartialResearchProfile.model_validate(payload)
    recognized = tuple(
        field
        for field in (
            *_DIMENSION_FIELDS,
            "must_answer",
            "scope_boundaries",
            "custom_notes",
            "comparison_subjects",
            "output_language",
        )
        if (getattr(partial, field) if field in _DIMENSION_FIELDS else getattr(partial, field))
    )
    return ProfileParseResult(partial=partial, recognized_fields=recognized)


def parse_profile_response(text: str) -> PartialResearchProfile:
    """Compatibility wrapper for callers that only need the parsed profile."""
    return parse_profile_input(text).partial


def read_legacy_profile(payload: Mapping[str, Any]) -> ResearchProfile:
    """Read v1 retained content without manufacturing v2 intake facts."""

    if not isinstance(payload, Mapping) or payload.get("schema_version", LEGACY_PROFILE_SCHEMA_VERSION) != 1:
        raise ValueError("legacy_profile_required")
    legacy = dict(payload)
    legacy.pop("comparison_required", None)
    legacy.pop("comparison_subjects", None)
    legacy.pop("request_language", None)
    legacy.pop("output_language", None)
    legacy["schema_version"] = LEGACY_PROFILE_SCHEMA_VERSION
    return ResearchProfile.model_validate(legacy)


__all__ = [
    "ComparisonIntakeSeed",
    "ComparisonSubjects",
    "CostTolerance",
    "LEGACY_PROFILE_SCHEMA_VERSION",
    "OutputFormat",
    "PartialResearchProfile",
    "ProfileParseResult",
    "ResearchDepth",
    "ResearchProfile",
    "RequestLanguage",
    "RequestBundleStoreProtocol",
    "StructuredBrief",
    "SupportedLanguage",
    "TargetAudience",
    "TimeBudget",
    "canonical_profile_bytes",
    "canonical_profile_json",
    "compute_profile_content_hash",
    "derive_comparison_intake_seed",
    "finalize_profile",
    "merge_profile_progress",
    "missing_dimensions",
    "normalize_clear_confirmation",
    "parse_profile_response",
    "parse_profile_input",
    "profile_state_fields",
    "read_legacy_profile",
]
