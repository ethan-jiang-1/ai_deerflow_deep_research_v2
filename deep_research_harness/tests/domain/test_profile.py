"""HITL1 research profile domain contracts.

@impl HIN-001
@impl HIN-003
"""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from deerflow_deep_research.domain.profile import (
    ComparisonSubjects,
    CostTolerance,
    OutputFormat,
    PartialResearchProfile,
    RequestLanguage,
    ResearchDepth,
    ResearchProfile,
    StructuredBrief,
    SupportedLanguage,
    TargetAudience,
    TimeBudget,
    canonical_profile_json,
    derive_comparison_intake_seed,
    finalize_profile,
    merge_profile_progress,
    missing_dimensions,
    normalize_clear_confirmation,
    parse_profile_input,
    parse_profile_response,
    read_legacy_profile,
)


def _complete_profile(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "depth": "standard",
        "audience": "practitioner",
        "format": "detailed_report",
        "cost_tolerance": "moderate",
        "time_budget": "standard",
        "must_answer": ("What matters most?",),
        "scope_boundaries": "Use grid-scale deployment only.",
        "custom_notes": "Prefer recent sources.",
    }
    payload.update(overrides)
    return payload


def test_closed_enums_are_stable_machine_values() -> None:
    assert {item.value for item in ResearchDepth} == {
        "quick_overview",
        "standard",
        "deep_dive",
        "exhaustive",
    }
    assert {item.value for item in TargetAudience} == {
        "layperson",
        "practitioner",
        "domain_expert",
        "executive",
    }
    assert {item.value for item in OutputFormat} == {
        "executive_brief",
        "detailed_report",
        "annotated_bibliography",
        "faq",
    }
    assert {item.value for item in CostTolerance} == {"minimal", "moderate", "extensive"}
    assert {item.value for item in TimeBudget} == {"very_quick", "standard", "thorough", "overnight"}


def test_profile_contracts_are_frozen_extra_forbid_and_schema_version_one() -> None:
    brief = StructuredBrief(
        brief_summary="A scoped research request.",
        **_complete_profile(),
    )
    assert brief.schema_version == 1
    with pytest.raises(ValidationError):
        StructuredBrief(brief_summary="x", unexpected=True, **_complete_profile())
    with pytest.raises(ValidationError):
        brief.brief_summary = "changed"  # type: ignore[misc]

    partial = PartialResearchProfile(depth="quick_overview")
    assert partial.schema_version == 1
    with pytest.raises(ValidationError):
        partial.depth = ResearchDepth.STANDARD  # type: ignore[misc]


def test_profile_bounds_and_final_completeness() -> None:
    profile = ResearchProfile(**_complete_profile(must_answer=["Q1", "Q2"]))
    assert profile.must_answer == ("Q1", "Q2")

    with pytest.raises(ValidationError, match="must_answer"):
        ResearchProfile(**_complete_profile(must_answer=[]))
    with pytest.raises(ValidationError, match="must_answer"):
        ResearchProfile(**_complete_profile(must_answer=["x" * 257]))
    with pytest.raises(ValidationError):
        ResearchProfile(**_complete_profile(scope_boundaries="x" * 2049))
    with pytest.raises(ValidationError):
        ResearchProfile(**_complete_profile(custom_notes="x" * 1025))
    with pytest.raises(ValidationError, match="profile_incomplete"):
        ResearchProfile(depth="standard", must_answer=("Q1",))

    degraded = ResearchProfile(depth="standard", must_answer=("Q1",), degraded_profile=True)
    assert degraded.degraded_profile is True
    assert missing_dimensions(degraded) == ("audience", "format", "cost_tolerance", "time_budget")


def test_canonical_profile_json_is_stable_and_rejects_wrong_type() -> None:
    profile = ResearchProfile(**_complete_profile())
    encoded = canonical_profile_json(profile)
    assert encoded == json.dumps(json.loads(encoded), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    assert json.loads(encoded)["schema_version"] == 1
    with pytest.raises(TypeError, match="profile_required"):
        canonical_profile_json(PartialResearchProfile(depth="standard"))  # type: ignore[arg-type]


def test_parse_profile_response_accepts_json_and_ignores_unknown_enum_values() -> None:
    parsed = parse_profile_response(
        json.dumps(
            {
                "depth": "superficial",
                "target_audience": "domain_expert",
                "output_format": "annotated_bibliography",
                "cost_tolerance": "extensive",
                "time_budget": "overnight",
                "must_answer_questions": ["Q1"],
            }
        )
    )
    assert parsed.depth is None
    assert parsed.audience is TargetAudience.DOMAIN_EXPERT
    assert parsed.format is OutputFormat.ANNOTATED_BIBLIOGRAPHY
    assert parsed.cost_tolerance is CostTolerance.EXTENSIVE
    assert parsed.time_budget is TimeBudget.OVERNIGHT
    assert parsed.must_answer == ("Q1",)

    with pytest.raises(ValueError, match="profile_response_json_invalid"):
        parse_profile_response("[1, 2]")
    with pytest.raises(ValueError, match="profile_response_extra_fields"):
        parse_profile_response('{"depth":"standard","host_path":"/tmp/x"}')


def test_parse_profile_response_is_deterministic_for_free_text() -> None:
    parsed = parse_profile_response(
        "standard depth, for practitioners, detailed report, moderate cost, standard time; must answer: Q1 and Q2"
    )
    assert parsed == PartialResearchProfile(
        depth=ResearchDepth.STANDARD,
        audience=TargetAudience.PRACTITIONER,
        format=OutputFormat.DETAILED_REPORT,
        cost_tolerance=CostTolerance.MODERATE,
        time_budget=TimeBudget.STANDARD,
        must_answer=("Q1", "Q2"),
    )

    unknown = parse_profile_response("depth=superficial; must answer: Q1")
    assert unknown.depth is None
    assert unknown.must_answer == ("Q1",)


def test_parse_profile_input_recognizes_chinese_aliases_without_cross_dimension_guessing() -> None:
    parsed = parse_profile_input("标准深度，面向实践者，详细报告，适中成本，标准时间")
    assert parsed.partial.depth is ResearchDepth.STANDARD
    assert parsed.partial.audience is TargetAudience.PRACTITIONER
    assert parsed.partial.format is OutputFormat.DETAILED_REPORT
    assert parsed.partial.cost_tolerance is CostTolerance.MODERATE
    assert parsed.partial.time_budget is TimeBudget.STANDARD
    assert parsed.recognized_fields == ("depth", "audience", "format", "cost_tolerance", "time_budget")

    ambiguous = parse_profile_input("standard")
    assert ambiguous.recognized_fields == ()


def test_merge_and_finalize_profile_progress() -> None:
    current = PartialResearchProfile(depth="quick_overview", must_answer=("Old",))
    incoming = PartialResearchProfile(audience="layperson", must_answer=("New",))
    merged = merge_profile_progress(current, incoming)
    assert merged.depth is ResearchDepth.QUICK_OVERVIEW
    assert merged.audience is TargetAudience.LAYPERSON
    assert merged.must_answer == ("New",)
    with pytest.raises(ValidationError, match="profile_incomplete"):
        finalize_profile(merged)
    assert finalize_profile(merged, degraded=True).degraded_profile is True


def test_comparison_subjects_are_canonical_ordered_pairs() -> None:
    subjects = ComparisonSubjects(subjects=("  Lithium-ion\u3000batteries ", "Vanadium redox flow batteries"))
    assert subjects.subjects == ("Lithium-ion batteries", "Vanadium redox flow batteries")

    with pytest.raises(ValidationError, match="comparison_subjects"):
        ComparisonSubjects(subjects=("one", "two", "three"))  # type: ignore[arg-type]
    with pytest.raises(ValidationError, match="comparison_subjects"):
        ComparisonSubjects(subjects=("same", "SAME"))


def test_v2_profile_requires_typed_comparison_and_language_facts() -> None:
    base = _complete_profile(
        schema_version=2,
        request_language=RequestLanguage.ZH,
        output_language=SupportedLanguage.ZH,
        comparison_required=True,
    )
    with pytest.raises(ValidationError, match="profile_incomplete:comparison_subjects"):
        ResearchProfile(**base)

    profile = ResearchProfile(
        **base,
        comparison_subjects=("锂离子电池", "全钒液流电池"),
    )
    assert profile.comparison_subjects is not None
    assert missing_dimensions(profile) == ()
    assert json.loads(canonical_profile_json(profile))["schema_version"] == 2

    reordered = profile.model_copy(
        update={"comparison_subjects": ComparisonSubjects(subjects=("全钒液流电池", "锂离子电池"))}
    )
    assert canonical_profile_json(profile) != canonical_profile_json(reordered)


def test_local_intake_seed_and_bounded_pair_input_are_deterministic() -> None:
    chinese = derive_comparison_intake_seed("比较锂离子电池和全钒液流电池的成本")
    assert chinese.comparison_required is True
    assert chinese.comparison_subjects is not None
    assert chinese.comparison_subjects.subjects == ("锂离子电池", "全钒液流电池的成本")
    assert chinese.request_language is RequestLanguage.ZH
    assert chinese.output_language is SupportedLanguage.ZH

    generic = derive_comparison_intake_seed("Compare two energy storage approaches")
    assert generic.comparison_required is True
    assert generic.comparison_subjects is None
    assert generic.request_language is RequestLanguage.EN

    unsupported = derive_comparison_intake_seed("12345")
    assert unsupported.request_language is RequestLanguage.UNSPECIFIED
    assert unsupported.output_language is None

    parsed = parse_profile_input("lithium-ion batteries | vanadium redox flow batteries", allow_comparison_pair=True)
    assert parsed.partial.comparison_subjects is not None
    assert parsed.partial.comparison_subjects.subjects == ("lithium-ion batteries", "vanadium redox flow batteries")
    assert parsed.recognized_fields == ("comparison_subjects",)
    assert parse_profile_input("lithium-ion batteries | vanadium redox flow batteries").recognized_fields == ()


@pytest.mark.parametrize("reply", ["可以", "好的！", "同意。", "yes", "YES PLEASE!", "looks good?"])
def test_clear_confirmation_is_a_closed_normalized_set(reply: str) -> None:
    assert normalize_clear_confirmation(reply) is True


@pytest.mark.parametrize("reply", ["yes, but change the format", "可以，不过请改范围", "confirm later"])
def test_clear_confirmation_rejects_modifying_text(reply: str) -> None:
    assert normalize_clear_confirmation(reply) is False


def test_legacy_profile_reader_retains_v1_without_inferred_facts() -> None:
    legacy = read_legacy_profile(_complete_profile(schema_version=1))
    assert legacy.schema_version == 1
    assert legacy.request_language is RequestLanguage.LEGACY_UNSPECIFIED
    assert legacy.comparison_required is False
    assert legacy.comparison_subjects is None
    assert legacy.output_language is None
