"""Typed contracts for the local workflow-debug driving surface.

Closed commands, exact-cursor idempotency, and session projections. The driver
is not a lifecycle authority: it drives the one real graph through the existing
executor and lifecycle admission. (`LDD-001`..`LDD-005`, `LDD-010`)
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any, Literal, get_args, get_type_hints

from pydantic import Field

from deerflow_deep_research.domain.human_interaction import InteractionFeedback
from deerflow_deep_research.domain.lifecycle import FrozenContract
from deerflow_deep_research.domain.run_experience import PromptView
from deerflow_deep_research.domain.state import BundleLocalState

DebugCommandKind = Literal[
    "advance_one",
    "drive_until",
    "pause_request",
    "answer",
    "cancel",
    "detach",
    "rerun_node",
]
DriveMode = Literal["step", "run"]
SessionPosture = Literal["running", "pause_requested", "paused_at_boundary", "awaiting_hitl", "terminal"]

ComparisonOperator = Literal["==", "!=", ">=", "<=", ">", "<"]
_COMPARISON_OPERATORS: tuple[str, ...] = ("==", "!=", ">=", "<=", ">", "<")
_MAX_CLAUSES = 8


def _strip_optional(annotation: Any) -> Any:
    args = get_args(annotation)
    if len(args) == 2 and type(None) in args:
        return next(item for item in args if item is not type(None))
    return annotation


def _comparable_kind(annotation: Any) -> str | None:
    """The scalar comparison family of a field annotation; None = not comparable.

    ``bool`` is checked before ``int`` (it is an int subclass); StrEnum fields
    count as ``str`` because their values compare as strings.
    """

    origin = _strip_optional(annotation)
    if origin is bool:
        return "bool"
    if origin is int:
        return "int"
    if origin is str:
        return "str"
    if isinstance(origin, type) and issubclass(origin, str):
        return "str"
    return None


def _value_kind(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, str):
        return "str"
    return "other"


@lru_cache(maxsize=1)
def _state_field_annotations() -> dict[str, Any]:
    return get_type_hints(BundleLocalState)


@lru_cache(maxsize=1)
def breakpoint_condition_fields() -> tuple[str, ...]:
    """The scalar-comparable typed State fields, in declaration order (`LDD-010`).

    This is the single authority both the parser and the workbench rejections
    cite: int/str/bool (and Optional variants) plus StrEnum fields, which
    compare as their string values. Tuple/dict/ref fields can never satisfy a
    comparison, so they stay out instead of becoming always-False traps.
    """

    return tuple(
        name for name, annotation in _state_field_annotations().items() if _comparable_kind(annotation) is not None
    )


class BreakpointClause(FrozenContract):
    """One typed comparison over the durable State; closed grammar (`LDD-010`)."""

    field: str = Field(min_length=1, max_length=64)
    operator: ComparisonOperator
    literal: str | int | bool | None = None


class BreakpointCondition(FrozenContract):
    """A conjunction of typed State comparisons, validated at parse time."""

    clauses: tuple[BreakpointClause, ...] = Field(min_length=1, max_length=_MAX_CLAUSES)


def _parse_literal(token: str, *, annotation: Any) -> str | int | bool | None:
    optional = _strip_optional(annotation) is not annotation
    if token == "none":
        if not optional:
            raise ValueError("breakpoint_condition_invalid: 该字段不可为 none")
        return None
    literal: str | int | bool | None
    if token in {"true", "false"}:
        literal = token == "true"
    elif re.fullmatch(r"-?\d+", token):
        literal = int(token)
    elif token == "and":
        raise ValueError("breakpoint_condition_invalid: and 不能作字面值")
    else:
        literal = token
    kind = _comparable_kind(annotation)
    if literal is not None and kind is not None and _value_kind(literal) != kind:
        raise ValueError(f"breakpoint_condition_invalid: 字面值类型与字段不符（需要 {kind}）")
    return literal


def parse_breakpoint_condition(text: str) -> BreakpointCondition:
    """Parse the closed condition grammar; every deviation is a typed denial.

    Grammar: ``field op value (and field op value)*`` — whitespace tokens, the
    operator from the closed set, the literal typed by the field's declared
    family. Anything outside (unknown or non-comparable fields, stray tokens,
    reserved words, over-long conjunctions) raises ``ValueError`` and never
    produces a contract, so an invalid condition can never reach a drive loop.
    """

    tokens = text.split()
    if not tokens:
        raise ValueError("breakpoint_condition_invalid: 条件为空")
    annotations = _state_field_annotations()
    allowed = set(breakpoint_condition_fields())
    clauses: list[BreakpointClause] = []
    index = 0
    while True:
        if len(tokens) - index < 3:
            raise ValueError("breakpoint_condition_invalid: 语法是 字段 运算符 值 (and …)")
        name, operator, raw_literal = tokens[index], tokens[index + 1], tokens[index + 2]
        index += 3
        if name not in allowed:
            raise ValueError(f"breakpoint_condition_invalid: 未知或不可比较字段 {name}")
        if operator not in _COMPARISON_OPERATORS:
            raise ValueError(f"breakpoint_condition_invalid: 未知运算符 {operator}（闭集 == != >= <= > <）")
        clauses.append(
            BreakpointClause(
                field=name,
                operator=operator,
                literal=_parse_literal(raw_literal, annotation=annotations[name]),  # type: ignore[index]
            )
        )
        if index == len(tokens):
            break
        if tokens[index] != "and":
            raise ValueError("breakpoint_condition_invalid: 子句之间只能用 and 连接")
        index += 1
        if index == len(tokens):
            raise ValueError("breakpoint_condition_invalid: and 之后缺少比较")
        if len(clauses) >= _MAX_CLAUSES:
            raise ValueError(f"breakpoint_condition_invalid: 最多 {_MAX_CLAUSES} 个子句")
    return BreakpointCondition(clauses=tuple(clauses))


def _clause_holds(actual: Any, operator: str, literal: Any) -> bool:
    if actual is None or literal is None:
        # Ordering against None never holds; equality is plain is/is-not.
        if operator == "==":
            return actual is None and literal is None
        if operator == "!=":
            return not (actual is None and literal is None)
        return False
    actual_kind, literal_kind = _value_kind(actual), _value_kind(literal)
    # Mismatched kinds never hold - even for != - so a type-mismatched
    # condition can never surprise-stop a drive; non-scalars stay out too.
    if actual_kind != literal_kind or actual_kind == "other":
        return False
    if operator == "==":
        return bool(actual == literal)
    if operator == "!=":
        return bool(actual != literal)
    if operator == ">":
        return bool(actual > literal)
    if operator == "<":
        return bool(actual < literal)
    if operator == ">=":
        return bool(actual >= literal)
    return bool(actual <= literal)


def evaluate_breakpoint_condition(condition: BreakpointCondition, state: Any) -> bool:
    """Total evaluation: a boolean for any State and any contract, never raises.

    All grammar violations were already denied at parse time; this function
    stays total even for contracts constructed directly, because the driver
    must never see an exception from a stop decision.
    """

    for clause in condition.clauses:
        if not _clause_holds(getattr(state, clause.field, None), clause.operator, clause.literal):
            return False
    return True


def _literal_text(literal: str | int | bool | None) -> str:
    if literal is None:
        return "none"
    if literal is True:
        return "true"
    if literal is False:
        return "false"
    return str(literal)


def format_breakpoint_condition(condition: BreakpointCondition) -> str:
    """Canonical rendering - the text the workbench states back on acceptance."""

    return " and ".join(
        f"{clause.field} {clause.operator} {_literal_text(clause.literal)}" for clause in condition.clauses
    )


class StopPolicy(FrozenContract):
    """Where drive_until stops; breakpoint names a node's post-commit.

    ``auto_hitl`` is an explicit operator drive policy (`LDD-008`): when the
    drive meets a hitl1 profile-confirmation request it may submit 确认 (confirm)
    as an operator-policy answer through the existing semantic intake and run
    on. The contract default is False (a drive stops for a human); the
    workbench turns it on for continuous drives and never for single steps.
    HITL2 direction decisions always wait regardless of this policy.

    ``condition`` (`LDD-010`) gates the breakpoint: with a target, the drive
    stops only where the target has visited AND the condition holds on the
    durable State; without one, at the first boundary where it holds. It is
    None by default (an unconditional policy behaves exactly as before).
    """

    breakpoint_after: str | None = Field(default=None, min_length=1, max_length=32)
    stop_on_hitl: bool = True
    stop_on_failure: bool = True
    stop_on_terminal: bool = True
    auto_hitl: bool = False
    condition: BreakpointCondition | None = None


class DebugCommand(FrozenContract):
    kind: DebugCommandKind
    bundle_id: str = Field(min_length=1, max_length=64)
    command_id: str = Field(min_length=8, max_length=128)
    expected_cursor: str = Field(min_length=8, max_length=256)
    breakpoint: StopPolicy | None = None
    answer_text: str | None = Field(default=None, min_length=1, max_length=16_384)
    option_id: str | None = Field(default=None, min_length=1, max_length=64)


class BoundaryCursor(FrozenContract):
    """Opaque-ish projection of the durable boundary; the driver's write permit."""

    bundle_id: str = Field(min_length=1, max_length=64)
    generation: int = Field(ge=0)
    frame_sequence: int = Field(ge=0)
    checkpoint_id: str | None = Field(default=None, min_length=1, max_length=128)
    next_nodes: tuple[str, ...] = ()

    def token(self) -> str:
        """The write permit: durable boundary identity only.

        ``next_nodes`` is deliberately excluded: it is an operator-facing
        projection of the graph state (and is populated on the stepping path
        only), not part of the boundary identity the permit fences. Including
        it made every command that recomputed the cursor without the graph
        state read as ``stale``.
        """
        import json

        return "BC1." + json.dumps(
            {
                "b": self.bundle_id,
                "g": self.generation,
                "f": self.frame_sequence,
                "c": self.checkpoint_id or "",
            },
            sort_keys=True,
            separators=(",", ":"),
        )


class LeasePosture(FrozenContract):
    owner: str | None = Field(default=None, min_length=1, max_length=128)
    generation: int = Field(ge=0)
    live: bool
    expires_in_seconds: float | None = None


class PendingOptionView(FrozenContract):
    """One advertised option of a pending choice request."""

    option_id: str = Field(min_length=1, max_length=64)
    label: str = Field(min_length=1, max_length=128)


class PendingRequestView(FrozenContract):
    """Bounded projection of the Bundle's pending human request.

    The request is *carried*, never rebuilt: the driver reads the node-authored
    descriptor from the Bundle's own checkpoint interrupt, so the workbench can
    tell the operator exactly what is being asked (title, guidance, mode,
    advertised options) without re-deriving a prompt (`RED-014`). The parsed
    ``prompt`` card and the node's ``last_feedback`` are carried projections of
    the same node-authored facts (`RED-015`/`LDD-006`): the card parses the
    published hitl1 context schema through the one shared parsing authority and
    stays None when the context does not follow it; the feedback prefers the
    interrupt's own interaction projection and falls back to the Bundle's
    durable state. Neither field is lifecycle authority.
    """

    request_id: str = Field(min_length=1, max_length=128)
    phase: str = Field(min_length=1, max_length=32)
    mode: Literal["text", "choice"]
    title: str = Field(min_length=1, max_length=256)
    context: str = Field(min_length=1, max_length=2_048)
    options: tuple[PendingOptionView, ...] = ()
    prompt: PromptView | None = None
    last_feedback: InteractionFeedback | None = None


class DebugSessionSnapshot(FrozenContract):
    bundle_id: str = Field(min_length=1, max_length=64)
    cursor: BoundaryCursor
    mode: DriveMode
    posture: SessionPosture
    stop_policy: StopPolicy
    pause_requested: bool = False
    lease: LeasePosture
    pending_request_id: str | None = Field(default=None, min_length=1, max_length=128)
    pending_request: PendingRequestView | None = None
    auto_hitl_answers: tuple[str, ...] = Field(default=(), max_length=16)
    watch_hits: tuple[str, ...] = Field(default=(), max_length=8)


class DebugSessionUpdate(FrozenContract):
    """Result of one executed command: new snapshot, or a typed denial."""

    snapshot: DebugSessionSnapshot | None = None
    denied: Literal[None, "stale", "duplicate", "busy", "invalid", "not_found", "in_flight"] = None
    message: str | None = Field(default=None, min_length=1, max_length=512)
    committed_node: str | None = Field(default=None, min_length=1, max_length=32)
    command_id: str = Field(min_length=8, max_length=128)


class StartRequest(FrozenContract):
    question: str = Field(min_length=1, max_length=16_384)
    mode: DriveMode
    owner: str = Field(min_length=1, max_length=128)
    command_id: str = Field(min_length=8, max_length=128)


class AttachRequest(FrozenContract):
    bundle_id: str = Field(min_length=1, max_length=64)
    owner: str = Field(min_length=1, max_length=128)
    expected_lease_generation: int | None = Field(default=None, ge=0)
