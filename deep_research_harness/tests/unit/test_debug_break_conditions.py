"""LDD-010: typed breakpoint conditions — closed grammar, parse-time denials,
total evaluation.

A condition is a conjunction of typed comparisons over the durable State's
scalar-comparable fields (StrEnum fields compare as their string values).
Parsing rejects everything outside the closed grammar; evaluation is total
(returns a boolean for any State and any contract, never raises into a drive
loop).
"""

from __future__ import annotations

import pytest

from deerflow_deep_research.domain.bundle import BundleId
from deerflow_deep_research.domain.debug_driving import (
    BreakpointClause,
    BreakpointCondition,
    StopPolicy,
    breakpoint_condition_fields,
    evaluate_breakpoint_condition,
    format_breakpoint_condition,
    parse_breakpoint_condition,
)
from deerflow_deep_research.domain.identifiers import LogicalPhase
from deerflow_deep_research.domain.lifecycle import ImplementationMode
from deerflow_deep_research.domain.state import BundleLocalState


def _state(**overrides) -> BundleLocalState:
    values: dict = {
        "bundle_id": BundleId("b_" + "A" * 43),
        "implementation_mode": ImplementationMode.ALL_REAL,
        "generation": 2,
        "phase": LogicalPhase.WAVE0,
        "research_depth": "deep_dive",
        "degraded_profile": False,
        "waiting_for": None,
    }
    values.update(overrides)
    return BundleLocalState(**values)


def _deny(text: str) -> None:
    with pytest.raises(ValueError, match="breakpoint_condition_invalid"):
        parse_breakpoint_condition(text)


# -- parse: closed grammar, typed denials (Task 1.1) -------------------------


def test_the_field_allowlist_is_the_scalar_comparable_subset() -> None:
    fields = breakpoint_condition_fields()
    assert "generation" in fields
    assert "phase" in fields  # StrEnum compares as its string value
    assert "research_depth" in fields
    assert "degraded_profile" in fields
    assert "waiting_for" in fields
    # Non-scalar fields never enter a condition: comparing them is always-False.
    assert "execution_trace" not in fields
    assert "must_answer_questions" not in fields
    assert "latest_incident" not in fields
    assert "bundle_id" not in fields


def test_valid_conjunctions_parse_into_the_closed_contract() -> None:
    condition = parse_breakpoint_condition("generation >= 2 and phase == wave0")
    assert condition.clauses == (
        BreakpointClause(field="generation", operator=">=", literal=2),
        BreakpointClause(field="phase", operator="==", literal="wave0"),
    )


def test_none_bool_and_string_literals_parse_with_their_types() -> None:
    assert parse_breakpoint_condition("waiting_for != none").clauses[0].literal is None
    assert parse_breakpoint_condition("degraded_profile == true").clauses[0].literal is True
    assert parse_breakpoint_condition("research_depth == deep").clauses[0].literal == "deep"


def test_unknown_fields_are_denied_at_parse_time() -> None:
    _deny("not_a_state_field == 1")


def test_non_comparable_fields_are_denied_at_parse_time() -> None:
    # A tuple field can never satisfy a comparison; parse denies it instead.
    _deny("execution_trace == wave0")


def test_operators_outside_the_closed_set_are_denied() -> None:
    _deny("generation = 2")
    _deny("generation ~= 2")
    _deny("generation equals 2")


def test_literal_kinds_must_match_the_field_kind() -> None:
    _deny("generation == 1x")  # int field wants an int literal
    _deny("phase == 5")  # str field wants a str literal
    _deny("degraded_profile == maybe")  # bool field wants true/false


def test_none_literals_require_an_optional_field() -> None:
    _deny("generation == none")  # generation is int, not Optional[int]
    parse_breakpoint_condition("waiting_for == none")  # Optional[str] accepts none


def test_literals_cannot_contain_spaces_or_reserved_words() -> None:
    _deny("research_depth == hello world")  # a 4th token is not "and"
    _deny("waiting_for == and")  # the separator keyword is never a literal


def test_malformed_conjunctions_are_denied() -> None:
    _deny("generation >=")
    _deny("generation >= 2 and")
    _deny("and generation >= 2")
    _deny("")


def test_more_than_eight_clauses_are_denied() -> None:
    _deny(" and ".join(["generation >= 1"] * 9))


def test_format_round_trips_through_the_parser() -> None:
    text = "generation >= 2 and phase == wave0 and waiting_for != none"
    assert format_breakpoint_condition(parse_breakpoint_condition(text)) == text


# -- evaluation: total, deterministic (Task 1.2) -----------------------------


def test_equalities_hold_across_str_enum_str_bool_and_none() -> None:
    assert evaluate_breakpoint_condition(parse_breakpoint_condition("phase == wave0"), _state())
    assert evaluate_breakpoint_condition(parse_breakpoint_condition("research_depth == deep_dive"), _state())
    assert evaluate_breakpoint_condition(parse_breakpoint_condition("generation == 2"), _state())
    assert evaluate_breakpoint_condition(parse_breakpoint_condition("waiting_for == none"), _state())
    assert not evaluate_breakpoint_condition(parse_breakpoint_condition("degraded_profile == true"), _state())


def test_ordering_within_one_family_is_numeric_or_lexicographic() -> None:
    assert evaluate_breakpoint_condition(parse_breakpoint_condition("generation > 1"), _state())
    assert evaluate_breakpoint_condition(parse_breakpoint_condition("research_depth < standard"), _state())


def test_none_ordering_never_holds() -> None:
    assert not evaluate_breakpoint_condition(parse_breakpoint_condition("waiting_for >= x"), _state())
    assert not evaluate_breakpoint_condition(
        BreakpointCondition(clauses=(BreakpointClause(field="generation", operator=">", literal=None),)), _state()
    )


def test_direct_construction_stays_total_and_never_raises() -> None:
    # Direct construction bypasses parse-time validation; evaluation must
    # still be total. Mismatched kinds never hold - even for !=, so a
    # type-mismatched condition can never surprise-stop a drive.
    state = _state()
    mismatched_eq = BreakpointCondition(clauses=(BreakpointClause(field="research_depth", operator="==", literal=5),))
    mismatched_ne = BreakpointCondition(clauses=(BreakpointClause(field="research_depth", operator="!=", literal=5),))
    unknown_field = BreakpointCondition(clauses=(BreakpointClause(field="nope", operator="==", literal=1),))
    assert evaluate_breakpoint_condition(mismatched_eq, state) is False
    assert evaluate_breakpoint_condition(mismatched_ne, state) is False
    assert evaluate_breakpoint_condition(unknown_field, state) is False


def test_a_conjunction_short_circuits_on_its_first_false_clause() -> None:
    condition = parse_breakpoint_condition("generation >= 2 and phase == hitl1")
    assert evaluate_breakpoint_condition(condition, _state()) is False
    condition = parse_breakpoint_condition("generation >= 2 and phase == wave0")
    assert evaluate_breakpoint_condition(condition, _state()) is True


def test_stop_policy_carries_the_condition_additively() -> None:
    default = StopPolicy()
    assert default.condition is None
    policy = StopPolicy(condition=parse_breakpoint_condition("generation >= 2"))
    assert policy.condition is not None and policy.breakpoint_after is None
