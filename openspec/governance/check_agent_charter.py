#!/usr/bin/env python3
"""Validate permanent Deep Research Agent Charter navigation and admission anchors.

This checker deliberately validates only stable locations, links, admission anchors,
the mechanical shape of an active change's Focus Card, and bounded entry-document
budgets. It does not judge architectural prose and it does not create runtime
authority.

@impl DRC-004
@impl DRC-006
@impl DRC-008
@impl DRC-009
@impl DRC-010
@impl PRS-009
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

CHARTER_ROOT = Path("openspec/agent-charter")
LEGACY_CHARTER_ROOT = Path("openspec/governance/agent-charter")
POLICY_ROOT = Path("openspec/policies")
CONFIG_PATH = Path("openspec/config.yaml")
GUIDE_PATH = Path("deep_research_harness/AGENTS.md")
CLAUDE_GUIDE_PATH = Path("deep_research_harness/CLAUDE.md")
README_PATH = Path("deep_research_harness/README.md")
DOCS_INDEX_PATH = Path("deep_research_harness/docs/README.md")
FOCUSED_DOC_PATHS = (
    Path("deep_research_harness/docs/runtime-architecture.md"),
    Path("deep_research_harness/docs/local-operations.md"),
    Path("deep_research_harness/docs/testing-and-evaluation.md"),
)
CHANGES_ROOT = Path("openspec/changes")
FOCUS_BEGIN = "<!-- BEGIN: DEEP-RESEARCH-FOCUS-GATE -->"
FOCUS_END = "<!-- END: DEEP-RESEARCH-FOCUS-GATE -->"
GENERATED_BEGIN = "<!-- BEGIN GENERATED: PROJECT-STRUCTURE -->"
CONTEXT_EXPANSION_HEADING = "## Context Expansion Gate"
CONTEXT_EXPANSION_SENTENCE = "A possible future use is not enough to expand scope."
PROGRAM_ROUTE_ANCHOR = "Program form: `## Program Focus` with at least two"
FOCUS_HEADING = "## Change Focus"
FOCUS_FIELDS = (
    "Primary module / causal owner",
    "Seam classification",
    "Question",
    "Necessary adjacent/external contracts",
    "Evidence seam",
    "Not in scope",
    "Triggered review policies",
)
PROGRAM_FOCUS_HEADING = "## Program Focus"
PROGRAM_FOCUS_FIELDS = (
    "Program outcome",
    "Candidate / obligation budget",
    "Declared workstream order",
    "Program decision authority",
    "Shared archive invariant",
    "Program failure / recovery",
    "Split / expansion rule",
    "Not in scope",
)
WORKSTREAM_FOCUS_PREFIX = "### Workstream Focus: "
WORKSTREAM_FIELDS = (
    *FOCUS_FIELDS,
    "Candidate / obligation IDs",
    "Target / retirement",
    "Surface grade",
    "Decision authority",
    "Negative path / recovery",
)
WORKSTREAM_ID_PATTERN = re.compile(r"[a-z][a-z0-9-]*")
SEAM_CLASSIFICATION_FIELD = "Seam classification"
SEAM_CLASSIFICATIONS = frozenset(
    {"cognitive-program", "human-decision", "deterministic-guardrail", "wiring"}
)
TRIGGERED_POLICIES_FIELD = "Triggered review policies"
LEGACY_TRIGGERED_POLICIES_FIELD = "Triggered charter policies"
WORKFLOW_OUTCOME_REVIEW_POLICY = "workflow-outcome-review"
WORKFLOW_OUTCOME_REVIEW_HEADING = "## Workflow Outcome Review"
WORKFLOW_OUTCOME_REVIEW_COLUMNS = (
    "Failure class",
    "Fact owner",
    "Recovery owner and bound",
    "Terminal disposition",
    "Legal next action",
    "Deterministic evidence seam",
)
NODE_AGENT_WORKFLOW_INTEGRITY_POLICY = "node-agent-workflow-integrity"
NODE_AGENT_REVIEW_HEADING = "## Node Agent Review"
NODE_AGENT_REVIEW_COLUMNS = (
    "Surface",
    "Classification",
    "Bounded cognitive question or no-agent rationale",
    "Input authority boundary",
    "Tool posture and runtime enforcer",
    "Candidate result and deterministic admission owner",
    "Failure owner and bound",
    "Deterministic evidence seam",
)
NODE_AGENT_CLASSIFICATIONS = frozenset({"node-agent", "no-agent"})
CONTROL_PLACEMENT_POLICY = "control-placement"
CONTROL_PLACEMENT_REVIEW_HEADING = "## Control Placement Review"
CONTROL_PLACEMENT_TASKS_RULE = "When `Triggered review policies` includes `control-placement`, tasks.md MUST retain"
APPLY_GUIDANCE = "Review control-placement only when the selected proposal declares it; guidance is advisory."
ARCHIVE_GUIDANCE = "Before archive, review control-placement only when the selected proposal declares it; guidance is advisory."
OPERATION_GUIDANCE_ADVISORY_BOUNDARY = "does not execute commands, create or complete tasks, or block native operations"
CLOSEOUT_EVIDENCE_GUIDANCE = "openspec/guardrails/selected_change_closeout.py verifies only caller-declared committed ranges"
CONTROL_PLACEMENT_REVIEW_COLUMNS = (
    "Changed decision or fact",
    "Cognitive candidate or human judgment",
    "Direct fact and deterministic owner/evaluator",
    "Design posture",
    "Protected invariant or legal recovery",
    "Reuse or complexity removed/avoided",
    "Deterministic evidence seam",
)
CONTROL_PLACEMENT_POSTURES = frozenset(
    {"advisory", "bounded-repair", "human-decision", "non-bypassable"}
)


@dataclass(frozen=True)
class PolicyDocument:
    """Canonical policy documentation route, without behavioral authority."""

    path: Path
    index_link: str


@dataclass(frozen=True)
class WorkstreamFocus:
    """A workstream section within an active bounded program proposal."""

    stable_id: str
    section: str


def _policy_document(name: str) -> PolicyDocument:
    return PolicyDocument(
        path=POLICY_ROOT / f"{name}.md",
        index_link=f"../policies/{name}.md",
    )


POLICY_REGISTRY = {
    "local-context": _policy_document("local-context"),
    "authority-and-projections": _policy_document("authority-and-projections"),
    "participant-outcomes": _policy_document("participant-outcomes"),
    "human-interaction-integrity": _policy_document("human-interaction-integrity"),
    "control-and-recovery": _policy_document("control-and-recovery"),
    WORKFLOW_OUTCOME_REVIEW_POLICY: _policy_document(WORKFLOW_OUTCOME_REVIEW_POLICY),
    NODE_AGENT_WORKFLOW_INTEGRITY_POLICY: _policy_document(NODE_AGENT_WORKFLOW_INTEGRITY_POLICY),
    "change-admission": _policy_document("change-admission"),
    "agent-information-map": _policy_document("agent-information-map"),
    CONTROL_PLACEMENT_POLICY: _policy_document(CONTROL_PLACEMENT_POLICY),
}
POLICY_LIBRARY_INDEX = POLICY_ROOT / "README.md"
INFORMATION_MAP_POLICY = POLICY_ROOT / "agent-information-map.md"
INFORMATION_MAP_POLICY_ANCHORS = (
    "## Reader Roles",
    "## Line Budgets",
    "deep_research_harness/docs/README.md",
    "runtime-architecture.md",
    "local-operations.md",
    "testing-and-evaluation.md",
    "word-count",
)
GUIDE_INFORMATION_MAP_ANCHORS = (
    "## Information Map",
    "README.md",
    "project-structure.toml",
)
CONFIG_INFORMATION_MAP_ANCHORS = (
    "## Default Context Boundary",
    "not a project manual",
)
README_READING_MAP = "## Reading Map"
LINE_BUDGETS = (
    (GUIDE_PATH, 120, 160, False),
    (CLAUDE_GUIDE_PATH, 10, 12, False),
    (CONFIG_PATH, 140, 180, False),
    (README_PATH, 200, None, True),
)


class ContractViolation(Exception):
    """A deterministic charter navigation violation."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


def _read_file(root: Path, relative_path: Path, *, code: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise ContractViolation(code, f"required file is missing: {relative_path.as_posix()}")
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ContractViolation(code, f"cannot read {relative_path.as_posix()}: {exc}") from exc


def _require_fragment(text: str, fragment: str, *, code: str, detail: str) -> None:
    if fragment not in text:
        raise ContractViolation(code, detail)


def _validate_charter_tree(root: Path) -> None:
    index_path = CHARTER_ROOT / "README.md"
    charter_path = CHARTER_ROOT / "charter.md"
    index = _read_file(root, index_path, code="charter.path_missing")
    charter = _read_file(root, charter_path, code="charter.path_missing")

    legacy_root = root / LEGACY_CHARTER_ROOT
    if legacy_root.exists() or legacy_root.is_symlink():
        raise ContractViolation(
            "charter.legacy_tree_present",
            f"legacy charter tree must be absent: {LEGACY_CHARTER_ROOT.as_posix()}",
        )

    nested_policy_root = root / CHARTER_ROOT / "policies"
    if nested_policy_root.exists() or nested_policy_root.is_symlink():
        raise ContractViolation(
            "charter.nested_policy_tree_present",
            f"charter tree must not contain nested policy prose: {(CHARTER_ROOT / 'policies').as_posix()}",
        )

    _require_fragment(
        index,
        "charter.md",
        code="charter.index_link_missing",
        detail=f"charter index does not link to {charter_path.as_posix()}",
    )
    _require_fragment(
        index,
        "## Policy Route",
        code="charter.index_route_missing",
        detail=f"charter index lacks a policy route: {index_path.as_posix()}",
    )
    _require_fragment(
        charter,
        "authority: guidance only",
        code="charter.authority_boundary_missing",
        detail=f"charter lacks its non-authority boundary: {charter_path.as_posix()}",
    )

    policy_index = _read_file(root, POLICY_LIBRARY_INDEX, code="charter.path_missing")
    _require_fragment(
        policy_index,
        "../agent-charter/README.md",
        code="charter.policy_library_route_missing",
        detail=f"policy library does not route contributors to {index_path.as_posix()}",
    )
    for policy, document in POLICY_REGISTRY.items():
        policy_text = _read_file(root, document.path, code="charter.path_missing")
        _require_fragment(
            index,
            document.index_link,
            code="charter.index_link_missing",
            detail=f"charter index does not link to {document.path.as_posix()}",
        )
        _require_fragment(
            policy_index,
            f"]({document.path.name})",
            code="charter.policy_library_link_missing",
            detail=f"policy library does not link to {document.path.as_posix()}",
        )
        _require_fragment(
            policy_text,
            "> trigger:",
            code="charter.policy_trigger_missing",
            detail=f"policy lacks a trigger: {document.path.as_posix()}",
        )
        _require_fragment(
            policy_text,
            "authority: guidance only",
            code="charter.policy_boundary_missing",
            detail=f"policy lacks its non-authority boundary: {document.path.as_posix()}",
        )

    local_context_path = POLICY_ROOT / "local-context.md"
    local_context = _read_file(root, local_context_path, code="charter.path_missing")
    _require_fragment(
        local_context,
        CONTEXT_EXPANSION_HEADING,
        code="charter.context_expansion_policy_missing",
        detail=f"local-context policy lacks its context-expansion gate: {local_context_path.as_posix()}",
    )
    _require_fragment(
        local_context,
        PROGRAM_ROUTE_ANCHOR,
        code="charter.program_route_local_context_missing",
        detail=f"local-context policy lacks the bounded-program route: {local_context_path.as_posix()}",
    )
    change_admission_path = POLICY_ROOT / "change-admission.md"
    change_admission = _read_file(root, change_admission_path, code="charter.path_missing")
    _require_fragment(
        change_admission,
        PROGRAM_ROUTE_ANCHOR,
        code="charter.program_route_change_admission_missing",
        detail=f"change-admission policy lacks the bounded-program route: {change_admission_path.as_posix()}",
    )


def _validate_focus_gate(root: Path) -> None:
    guide = _read_file(root, GUIDE_PATH, code="guide.missing")
    begin_count = guide.count(FOCUS_BEGIN)
    end_count = guide.count(FOCUS_END)
    if begin_count != 1 or end_count != 1:
        raise ContractViolation(
            "guide.focus_gate_missing",
            f"module guide must contain exactly one focus-gate marker pair: {GUIDE_PATH.as_posix()}",
        )

    begin = guide.index(FOCUS_BEGIN)
    end = guide.index(FOCUS_END, begin)
    if end <= begin:
        raise ContractViolation(
            "guide.focus_gate_order",
            f"focus-gate markers are out of order: {GUIDE_PATH.as_posix()}",
        )
    generated = guide.find(GENERATED_BEGIN)
    if generated != -1 and begin > generated:
        raise ContractViolation(
            "guide.focus_gate_position",
            f"focus gate must appear before the generated structure block: {GUIDE_PATH.as_posix()}",
        )

    focus_gate = guide[begin:end]
    _require_fragment(
        focus_gate,
        "agent-charter/README.md",
        code="guide.focus_gate_link_missing",
        detail=f"focus gate does not link to the charter index: {GUIDE_PATH.as_posix()}",
    )
    _require_fragment(
        focus_gate,
        "Primary owner to inspect first",
        code="guide.module_route_missing",
        detail=f"focus gate lacks the primary-module routing table: {GUIDE_PATH.as_posix()}",
    )
    _require_fragment(
        focus_gate,
        CONTEXT_EXPANSION_SENTENCE,
        code="guide.context_expansion_rule_missing",
        detail=f"focus gate lacks its context-expansion rule: {GUIDE_PATH.as_posix()}",
    )
    _require_fragment(
        focus_gate,
        PROGRAM_ROUTE_ANCHOR,
        code="guide.program_route_missing",
        detail=f"focus gate lacks the bounded-program route: {GUIDE_PATH.as_posix()}",
    )


def _validate_claude_guide(root: Path) -> None:
    claude_guide = _read_file(root, CLAUDE_GUIDE_PATH, code="guide.claude_entrypoint_missing")
    if not re.search(r"^@AGENTS\.md\s*$", claude_guide, flags=re.MULTILINE):
        raise ContractViolation(
            "guide.claude_import_missing",
            f"Claude Code entrypoint must import AGENTS.md: {CLAUDE_GUIDE_PATH.as_posix()}",
        )


def _validate_authoring_pointer(root: Path) -> None:
    config = _read_file(root, CONFIG_PATH, code="config.missing")
    if LEGACY_TRIGGERED_POLICIES_FIELD in config:
        raise ContractViolation(
            "config.legacy_triggered_policies_rule_present",
            f"OpenSpec configuration uses the retired field {LEGACY_TRIGGERED_POLICIES_FIELD!r}: "
            f"{CONFIG_PATH.as_posix()}",
        )
    _require_fragment(
        config,
        "openspec/agent-charter/README.md",
        code="config.charter_pointer_missing",
        detail=f"OpenSpec configuration lacks the charter pointer: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        FOCUS_HEADING,
        code="config.focus_rule_missing",
        detail=f"OpenSpec configuration lacks the Focus Card rule: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        FOCUS_FIELDS[0],
        code="config.focus_rule_missing",
        detail=f"OpenSpec configuration lacks the primary-module field: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        TRIGGERED_POLICIES_FIELD,
        code="config.triggered_policies_rule_missing",
        detail=f"OpenSpec configuration lacks the triggered-policy rule: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        CONTROL_PLACEMENT_POLICY,
        code="config.control_placement_review_rule_missing",
        detail=f"OpenSpec configuration lacks the control-placement review rule: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        CONTROL_PLACEMENT_REVIEW_HEADING,
        code="config.control_placement_review_rule_missing",
        detail=f"OpenSpec configuration lacks the Control Placement Review record rule: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        CONTROL_PLACEMENT_TASKS_RULE,
        code="config.control_placement_task_rule_missing",
        detail=f"OpenSpec configuration lacks the control-placement task obligation: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        "only when the selected proposal declares it",
        code="config.operation_guidance_selection_boundary_missing",
        detail=(
            "OpenSpec operation guidance must limit control-placement review to the selected proposal: "
            f"{CONFIG_PATH.as_posix()}"
        ),
    )
    _require_fragment(
        config,
        APPLY_GUIDANCE,
        code="config.operation_apply_guidance_missing",
        detail=f"OpenSpec configuration lacks the apply operation guidance: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        ARCHIVE_GUIDANCE,
        code="config.operation_archive_guidance_missing",
        detail=f"OpenSpec configuration lacks the archive operation guidance: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        OPERATION_GUIDANCE_ADVISORY_BOUNDARY,
        code="config.operation_guidance_advisory_boundary_missing",
        detail=f"OpenSpec operation guidance lacks its advisory boundary: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        CLOSEOUT_EVIDENCE_GUIDANCE,
        code="config.closeout_evidence_guidance_missing",
        detail=(
            "OpenSpec operation guidance lacks the caller-declared committed-range route: "
            f"{CONFIG_PATH.as_posix()}"
        ),
    )
    _require_fragment(
        config,
        WORKFLOW_OUTCOME_REVIEW_POLICY,
        code="config.workflow_outcome_review_rule_missing",
        detail=f"OpenSpec configuration lacks the workflow-outcome review rule: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        NODE_AGENT_WORKFLOW_INTEGRITY_POLICY,
        code="config.node_agent_workflow_integrity_rule_missing",
        detail=(
            "OpenSpec configuration lacks the node-agent workflow-integrity rule: "
            f"{CONFIG_PATH.as_posix()}"
        ),
    )
    _require_fragment(
        config,
        NODE_AGENT_REVIEW_HEADING,
        code="config.node_agent_workflow_integrity_rule_missing",
        detail=f"OpenSpec configuration lacks the Node Agent Review record rule: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        CONTEXT_EXPANSION_SENTENCE,
        code="config.context_expansion_rule_missing",
        detail=f"OpenSpec configuration lacks its context-expansion rule: {CONFIG_PATH.as_posix()}",
    )
    _require_fragment(
        config,
        PROGRAM_ROUTE_ANCHOR,
        code="config.program_route_missing",
        detail=f"OpenSpec configuration lacks the bounded-program route: {CONFIG_PATH.as_posix()}",
    )


def _line_count(text: str) -> int:
    return len(text.splitlines())


def _validate_human_docs(root: Path, readme: str) -> None:
    for path in (DOCS_INDEX_PATH, *FOCUSED_DOC_PATHS):
        relative_to_module = path.relative_to("deep_research_harness").as_posix()
        _require_fragment(
            readme,
            relative_to_module,
            code="readme.docs_link_missing",
            detail=f"README does not link to {relative_to_module}: {README_PATH.as_posix()}",
        )

    docs_index = _read_file(root, DOCS_INDEX_PATH, code="docs.index_missing")
    for path in FOCUSED_DOC_PATHS:
        _read_file(root, path, code="docs.focused_document_missing")
        _require_fragment(
            docs_index,
            path.name,
            code="docs.index_link_missing",
            detail=f"documentation index does not link to {path.name}: {DOCS_INDEX_PATH.as_posix()}",
        )


def _validate_information_map(root: Path) -> list[str]:
    policy = _read_file(root, INFORMATION_MAP_POLICY, code="charter.path_missing")
    for anchor in INFORMATION_MAP_POLICY_ANCHORS:
        _require_fragment(
            policy,
            anchor,
            code="charter.information_map_policy_missing",
            detail=(f"information-map policy lacks required anchor {anchor!r}: {INFORMATION_MAP_POLICY.as_posix()}"),
        )

    guide = _read_file(root, GUIDE_PATH, code="guide.missing")
    for anchor in GUIDE_INFORMATION_MAP_ANCHORS:
        _require_fragment(
            guide,
            anchor,
            code="guide.information_map_missing",
            detail=f"module guide lacks information-map anchor {anchor!r}: {GUIDE_PATH.as_posix()}",
        )

    readme = _read_file(root, README_PATH, code="readme.missing")
    matches = list(re.finditer(r"^## Reading Map\s*$", readme, flags=re.MULTILINE))
    if len(matches) != 1:
        raise ContractViolation(
            "readme.reading_map_missing",
            f"README must contain exactly one {README_READING_MAP!r}: {README_PATH.as_posix()}",
        )
    reading_map_line = readme[: matches[0].start()].count("\n") + 1
    if reading_map_line > 80:
        raise ContractViolation(
            "readme.reading_map_position",
            f"{README_READING_MAP!r} must start within the first 80 lines, found line {reading_map_line}: "
            f"{README_PATH.as_posix()}",
        )
    _validate_human_docs(root, readme)

    config = _read_file(root, CONFIG_PATH, code="config.missing")
    for anchor in CONFIG_INFORMATION_MAP_ANCHORS:
        _require_fragment(
            config,
            anchor,
            code="config.information_map_missing",
            detail=f"OpenSpec configuration lacks information-map anchor {anchor!r}: {CONFIG_PATH.as_posix()}",
        )

    documents = {
        GUIDE_PATH: guide,
        CLAUDE_GUIDE_PATH: _read_file(root, CLAUDE_GUIDE_PATH, code="guide.claude_entrypoint_missing"),
        CONFIG_PATH: config,
        README_PATH: readme,
    }
    warnings: list[str] = []
    for path, warning_at, maximum, warning_is_exclusive in LINE_BUDGETS:
        line_count = _line_count(documents[path])
        warning_reached = line_count > warning_at if warning_is_exclusive else line_count >= warning_at
        if maximum is not None and line_count > maximum:
            raise ContractViolation(
                "entry.line_budget_exceeded",
                f"{path.as_posix()} has {line_count} lines; maximum is {maximum}",
            )
        if warning_reached:
            operator = "above" if warning_is_exclusive else "at or above"
            warnings.append(
                f"[entry.line_budget_warning] {path.as_posix()} has {line_count} lines "
                f"({operator} warning threshold {warning_at})"
            )
    return warnings


def _section_after_heading(proposal: str, match: re.Match[str], *, maximum_level: int) -> str:
    start = match.end()
    next_heading = re.search(rf"^#{{1,{maximum_level}}} (?!#)", proposal[start:], flags=re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(proposal)
    return proposal[start:end]


def _field_value(section: str, field: str) -> str | None:
    pattern = re.compile(
        rf"^- \*\*{re.escape(field)}:\*\*[ \t]*(?P<value>\S[^\n]*)$",
        re.MULTILINE,
    )
    match = pattern.search(section)
    return match.group("value").strip() if match else None


def _scoped_code(code_prefix: str, suffix: str) -> str:
    if code_prefix == "program.workstream":
        return f"program.workstream_{suffix}"
    return f"{code_prefix}.{suffix}"


def _validate_required_fields(
    section: str,
    fields: tuple[str, ...],
    *,
    code: str,
    record_name: str,
    proposal_path: Path,
) -> None:
    for field in fields:
        if _field_value(section, field) is None:
            raise ContractViolation(
                code,
                f"{record_name} field {field!r} is missing or empty: {proposal_path.as_posix()}",
            )


def _validate_legacy_triggered_policies_field(
    section: str,
    *,
    code: str,
    record_name: str,
    proposal_path: Path,
) -> None:
    pattern = re.compile(rf"^- \*\*{re.escape(LEGACY_TRIGGERED_POLICIES_FIELD)}:\*\*", re.MULTILINE)
    if pattern.search(section):
        raise ContractViolation(
            code,
            f"{record_name} uses the retired field {LEGACY_TRIGGERED_POLICIES_FIELD!r}: "
            f"{proposal_path.as_posix()}",
        )


def _validate_seam_classification(
    section: str,
    *,
    code_prefix: str,
    record_name: str,
    proposal_path: Path,
) -> None:
    seam_value = _field_value(section, SEAM_CLASSIFICATION_FIELD)
    if seam_value is None:
        raise ContractViolation(
            _scoped_code(code_prefix, "field_missing"),
            f"{record_name} field {SEAM_CLASSIFICATION_FIELD!r} is missing or empty: "
            f"{proposal_path.as_posix()}",
        )
    value, _, rationale = seam_value.partition(" ")
    if value not in SEAM_CLASSIFICATIONS:
        raise ContractViolation(
            _scoped_code(code_prefix, "seam_classification_invalid"),
            f"{SEAM_CLASSIFICATION_FIELD!r} must be exactly one of "
            f"{', '.join(sorted(SEAM_CLASSIFICATIONS))}, written bare: {proposal_path.as_posix()}",
        )
    if not rationale.strip():
        raise ContractViolation(
            _scoped_code(code_prefix, "seam_classification_rationale_missing"),
            f"{SEAM_CLASSIFICATION_FIELD!r} must give a short rationale after the value: "
            f"{proposal_path.as_posix()}",
        )


def _triggered_policies(
    root: Path,
    focus_section: str,
    proposal_path: Path,
    *,
    code_prefix: str = "focus",
    record_name: str = "Focus Card",
) -> tuple[str, ...]:
    value = _field_value(focus_section, TRIGGERED_POLICIES_FIELD)
    if value is None:
        raise ContractViolation(
            _scoped_code(code_prefix, "field_missing"),
            f"{record_name} field {TRIGGERED_POLICIES_FIELD!r} is missing or empty: {proposal_path.as_posix()}",
        )

    field_pattern = re.compile(
        rf"^- \*\*{re.escape(TRIGGERED_POLICIES_FIELD)}:\*\*[ \t]*(?P<value>\S[^\n]*)$",
        re.MULTILINE,
    )
    match = field_pattern.search(focus_section)
    assert match is not None
    following_line = next(
        (line for line in focus_section[match.end() :].splitlines() if line.strip()),
        "",
    )
    if following_line and following_line[0].isspace():
        raise ContractViolation(
            _scoped_code(code_prefix, "triggered_policies_continuation_invalid"),
            f"{TRIGGERED_POLICIES_FIELD!r} must be a single-line comma-separated list: "
            f"{proposal_path.as_posix()}",
        )

    if value == "none":
        raise ContractViolation(
            _scoped_code(code_prefix, "triggered_policies_rationale_missing"),
            f"{TRIGGERED_POLICIES_FIELD!r} must give a short rationale after 'none:': {proposal_path.as_posix()}",
        )
    if value.startswith("none:"):
        if not value.removeprefix("none:").strip():
            raise ContractViolation(
                _scoped_code(code_prefix, "triggered_policies_rationale_missing"),
                f"{TRIGGERED_POLICIES_FIELD!r} must give a short rationale after 'none:': "
                f"{proposal_path.as_posix()}",
            )
        return ()

    policies = tuple(policy.strip() for policy in value.split(","))
    if not policies or any(not policy or policy not in POLICY_REGISTRY for policy in policies):
        raise ContractViolation(
            _scoped_code(code_prefix, "triggered_policy_unknown"),
            f"{TRIGGERED_POLICIES_FIELD!r} must list canonical policy names or 'none: <rationale>': "
            f"{proposal_path.as_posix()}",
        )
    for policy in policies:
        document = POLICY_REGISTRY[policy]
        _read_file(
            root,
            document.path,
            code=_scoped_code(code_prefix, "triggered_policy_document_missing"),
        )
    return policies


def _review_section(
    container: str,
    *,
    heading: str,
    level: int,
    code: str,
    proposal_path: Path,
) -> str:
    expected_heading = f"{'#' * level} {heading}"
    matches = list(re.finditer(rf"^{re.escape(expected_heading)}\s*$", container, flags=re.MULTILINE))
    if len(matches) != 1:
        raise ContractViolation(
            code,
            f"proposal selecting {heading!r} must contain exactly one {expected_heading!r}: "
            f"{proposal_path.as_posix()}",
        )
    return _section_after_heading(container, matches[0], maximum_level=level)


def _table_cells(line: str) -> tuple[str, ...] | None:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return None
    return tuple(cell.strip() for cell in stripped[1:-1].split("|"))


def _is_markdown_separator(cells: tuple[str, ...], columns: tuple[str, ...]) -> bool:
    return len(cells) == len(columns) and all(
        re.fullmatch(r":?-{3,}:?", cell) is not None for cell in cells
    )


def _validate_workflow_outcome_review(
    section: str,
    proposal_path: Path,
    *,
    code_prefix: str,
) -> None:
    table_lines = [line for line in section.splitlines() if _table_cells(line) is not None]
    if len(table_lines) < 3:
        raise ContractViolation(
            _scoped_code(code_prefix, "workflow_outcome_review_shape_invalid"),
            f"{WORKFLOW_OUTCOME_REVIEW_HEADING!r} needs a header, separator, and at least one row: "
            f"{proposal_path.as_posix()}",
        )
    header = _table_cells(table_lines[0])
    separator = _table_cells(table_lines[1])
    assert header is not None and separator is not None
    if header != WORKFLOW_OUTCOME_REVIEW_COLUMNS or not _is_markdown_separator(
        separator, WORKFLOW_OUTCOME_REVIEW_COLUMNS
    ):
        raise ContractViolation(
            _scoped_code(code_prefix, "workflow_outcome_review_shape_invalid"),
            f"{WORKFLOW_OUTCOME_REVIEW_HEADING!r} has an invalid table header: {proposal_path.as_posix()}",
        )
    for line in table_lines[2:]:
        cells = _table_cells(line)
        assert cells is not None
        if len(cells) != len(WORKFLOW_OUTCOME_REVIEW_COLUMNS) or any(not cell for cell in cells):
            raise ContractViolation(
                _scoped_code(code_prefix, "workflow_outcome_review_shape_invalid"),
                f"{WORKFLOW_OUTCOME_REVIEW_HEADING!r} has an incomplete table row: {proposal_path.as_posix()}",
            )


def _single_markdown_table_lines(section: str) -> list[str] | None:
    table_blocks: list[list[str]] = []
    current_block: list[str] = []
    for line in section.splitlines():
        if _table_cells(line) is None:
            if current_block:
                table_blocks.append(current_block)
                current_block = []
            continue
        current_block.append(line)
    if current_block:
        table_blocks.append(current_block)
    return table_blocks[0] if len(table_blocks) == 1 else None


def _validate_control_placement_review(
    section: str,
    proposal_path: Path,
    triggered_policies: tuple[str, ...],
    *,
    code_prefix: str,
) -> None:
    table_lines = _single_markdown_table_lines(section)
    if table_lines is None or len(table_lines) < 3:
        raise ContractViolation(
            _scoped_code(code_prefix, "control_placement_review_shape_invalid"),
            f"{CONTROL_PLACEMENT_REVIEW_HEADING!r} needs exactly one header, separator, and at least one row: "
            f"{proposal_path.as_posix()}",
        )
    header = _table_cells(table_lines[0])
    separator = _table_cells(table_lines[1])
    assert header is not None and separator is not None
    if header != CONTROL_PLACEMENT_REVIEW_COLUMNS or not _is_markdown_separator(
        separator, CONTROL_PLACEMENT_REVIEW_COLUMNS
    ):
        raise ContractViolation(
            _scoped_code(code_prefix, "control_placement_review_shape_invalid"),
            f"{CONTROL_PLACEMENT_REVIEW_HEADING!r} has an invalid table header: {proposal_path.as_posix()}",
        )

    has_human_decision = False
    for line in table_lines[2:]:
        cells = _table_cells(line)
        assert cells is not None
        if (
            len(cells) != len(CONTROL_PLACEMENT_REVIEW_COLUMNS)
            or any(not cell for cell in cells)
            or cells == CONTROL_PLACEMENT_REVIEW_COLUMNS
            or _is_markdown_separator(cells, CONTROL_PLACEMENT_REVIEW_COLUMNS)
        ):
            raise ContractViolation(
                _scoped_code(code_prefix, "control_placement_review_shape_invalid"),
                f"{CONTROL_PLACEMENT_REVIEW_HEADING!r} has an incomplete or duplicate table row: "
                f"{proposal_path.as_posix()}",
            )
        if cells[3] not in CONTROL_PLACEMENT_POSTURES:
            raise ContractViolation(
                _scoped_code(code_prefix, "control_placement_review_posture_invalid"),
                f"{CONTROL_PLACEMENT_REVIEW_HEADING!r} uses an unsupported design posture {cells[3]!r}: "
                f"{proposal_path.as_posix()}",
            )
        has_human_decision = has_human_decision or cells[3] == "human-decision"

    if has_human_decision and "human-interaction-integrity" not in triggered_policies:
        raise ContractViolation(
            _scoped_code(code_prefix, "control_placement_human_interaction_policy_missing"),
            f"{CONTROL_PLACEMENT_REVIEW_HEADING!r} with a human-decision row also requires "
            f"'human-interaction-integrity': {proposal_path.as_posix()}",
        )


def _validate_node_agent_review(section: str, proposal_path: Path, *, code_prefix: str) -> None:
    table_lines = _single_markdown_table_lines(section)
    if table_lines is None or len(table_lines) < 3:
        raise ContractViolation(
            _scoped_code(code_prefix, "node_agent_review_shape_invalid"),
            f"{NODE_AGENT_REVIEW_HEADING!r} needs exactly one header, separator, and at least one row: "
            f"{proposal_path.as_posix()}",
        )
    header = _table_cells(table_lines[0])
    separator = _table_cells(table_lines[1])
    assert header is not None and separator is not None
    if header != NODE_AGENT_REVIEW_COLUMNS or not _is_markdown_separator(separator, NODE_AGENT_REVIEW_COLUMNS):
        raise ContractViolation(
            _scoped_code(code_prefix, "node_agent_review_shape_invalid"),
            f"{NODE_AGENT_REVIEW_HEADING!r} has an invalid table header: {proposal_path.as_posix()}",
        )
    for line in table_lines[2:]:
        cells = _table_cells(line)
        assert cells is not None
        if len(cells) != len(NODE_AGENT_REVIEW_COLUMNS) or any(not cell for cell in cells):
            raise ContractViolation(
                _scoped_code(code_prefix, "node_agent_review_shape_invalid"),
                f"{NODE_AGENT_REVIEW_HEADING!r} has an incomplete table row: {proposal_path.as_posix()}",
            )
        if cells[1] not in NODE_AGENT_CLASSIFICATIONS:
            raise ContractViolation(
                _scoped_code(code_prefix, "node_agent_review_classification_invalid"),
                f"{NODE_AGENT_REVIEW_HEADING!r} uses an unsupported classification {cells[1]!r}: "
                f"{proposal_path.as_posix()}",
            )


def _validate_selected_policy_reviews(
    review_container: str,
    triggered_policies: tuple[str, ...],
    proposal_path: Path,
    *,
    review_level: int,
    code_prefix: str,
) -> None:
    if CONTROL_PLACEMENT_POLICY in triggered_policies:
        section = _review_section(
            review_container,
            heading="Control Placement Review",
            level=review_level,
            code=_scoped_code(code_prefix, "control_placement_review_missing"),
            proposal_path=proposal_path,
        )
        _validate_control_placement_review(
            section,
            proposal_path,
            triggered_policies,
            code_prefix=code_prefix,
        )
    if NODE_AGENT_WORKFLOW_INTEGRITY_POLICY in triggered_policies:
        section = _review_section(
            review_container,
            heading="Node Agent Review",
            level=review_level,
            code=_scoped_code(code_prefix, "node_agent_review_missing"),
            proposal_path=proposal_path,
        )
        _validate_node_agent_review(section, proposal_path, code_prefix=code_prefix)
    if WORKFLOW_OUTCOME_REVIEW_POLICY in triggered_policies:
        section = _review_section(
            review_container,
            heading="Workflow Outcome Review",
            level=review_level,
            code=_scoped_code(code_prefix, "workflow_outcome_review_missing"),
            proposal_path=proposal_path,
        )
        _validate_workflow_outcome_review(section, proposal_path, code_prefix=code_prefix)


def _comma_separated_values(
    value: str,
    *,
    invalid_code: str,
    duplicate_code: str,
    label: str,
    proposal_path: Path,
    validator: re.Pattern[str] | None = None,
) -> tuple[str, ...]:
    values = tuple(item.strip() for item in value.split(","))
    if not values or any(not item or (validator is not None and validator.fullmatch(item) is None) for item in values):
        raise ContractViolation(
            invalid_code,
            f"{label} must be a non-empty comma-separated list: {proposal_path.as_posix()}",
        )
    if len(values) != len(set(values)):
        raise ContractViolation(
            duplicate_code,
            f"{label} must not repeat an identifier: {proposal_path.as_posix()}",
        )
    return values


def _workstream_sections(proposal: str, program_match: re.Match[str], proposal_path: Path) -> tuple[WorkstreamFocus, ...]:
    matches = list(re.finditer(r"^### Workstream Focus:(?P<stable_id>[^\n]*)$", proposal, flags=re.MULTILINE))
    if len(matches) < 2:
        raise ContractViolation(
            "program.workstream_count_invalid",
            f"Program Focus needs at least two Workstream Focus records: {proposal_path.as_posix()}",
        )
    if any(match.start() < program_match.end() for match in matches):
        raise ContractViolation(
            "program.mode_invalid",
            f"Workstream Focus records must follow {PROGRAM_FOCUS_HEADING!r}: {proposal_path.as_posix()}",
        )

    workstreams: list[WorkstreamFocus] = []
    stable_ids: set[str] = set()
    for match in matches:
        raw_stable_id = match.group("stable_id")
        stable_id = raw_stable_id.strip()
        if not raw_stable_id.startswith(" ") or WORKSTREAM_ID_PATTERN.fullmatch(stable_id) is None:
            raise ContractViolation(
                "program.workstream_id_invalid",
                f"Workstream Focus has an invalid stable ID {stable_id!r}: {proposal_path.as_posix()}",
            )
        if stable_id in stable_ids:
            raise ContractViolation(
                "program.workstream_id_duplicate",
                f"Workstream Focus repeats stable ID {stable_id!r}: {proposal_path.as_posix()}",
            )
        stable_ids.add(stable_id)
        workstreams.append(
            WorkstreamFocus(
                stable_id=stable_id,
                section=_section_after_heading(proposal, match, maximum_level=3),
            )
        )
    return tuple(workstreams)


def _validate_program_proposal(root: Path, proposal: str, proposal_path: Path) -> None:
    program_matches = list(re.finditer(r"^## Program Focus\s*$", proposal, flags=re.MULTILINE))
    if len(program_matches) != 1:
        raise ContractViolation(
            "program.mode_invalid",
            f"program proposal must contain exactly one {PROGRAM_FOCUS_HEADING!r}: {proposal_path.as_posix()}",
        )
    program_section = _section_after_heading(proposal, program_matches[0], maximum_level=3)
    _validate_required_fields(
        program_section,
        PROGRAM_FOCUS_FIELDS,
        code="program.field_missing",
        record_name="Program Focus",
        proposal_path=proposal_path,
    )
    program_values = {
        field: _field_value(program_section, field)
        for field in PROGRAM_FOCUS_FIELDS
    }
    assert all(value is not None for value in program_values.values())
    budget = _comma_separated_values(
        program_values["Candidate / obligation budget"] or "",
        invalid_code="program.candidate_budget_invalid",
        duplicate_code="program.candidate_budget_duplicate",
        label="Candidate / obligation budget",
        proposal_path=proposal_path,
    )
    declared_order = _comma_separated_values(
        program_values["Declared workstream order"] or "",
        invalid_code="program.workstream_order_invalid",
        duplicate_code="program.workstream_order_duplicate",
        label="Declared workstream order",
        proposal_path=proposal_path,
        validator=WORKSTREAM_ID_PATTERN,
    )

    workstreams = _workstream_sections(proposal, program_matches[0], proposal_path)
    workstream_ids = tuple(workstream.stable_id for workstream in workstreams)
    if declared_order != workstream_ids:
        raise ContractViolation(
            "program.workstream_registration_mismatch",
            f"Declared workstream order must exactly match Workstream Focus records: {proposal_path.as_posix()}",
        )

    owners: set[str] = set()
    candidate_ids: list[str] = []
    for workstream in workstreams:
        _validate_legacy_triggered_policies_field(
            workstream.section,
            code="program.workstream_legacy_triggered_policies_field_present",
            record_name=f"Workstream Focus {workstream.stable_id!r}",
            proposal_path=proposal_path,
        )
        _validate_required_fields(
            workstream.section,
            WORKSTREAM_FIELDS,
            code="program.workstream_field_missing",
            record_name=f"Workstream Focus {workstream.stable_id!r}",
            proposal_path=proposal_path,
        )
        _validate_seam_classification(
            workstream.section,
            code_prefix="program.workstream",
            record_name=f"Workstream Focus {workstream.stable_id!r}",
            proposal_path=proposal_path,
        )
        owner = _field_value(workstream.section, "Primary module / causal owner")
        assert owner is not None
        if owner in owners:
            raise ContractViolation(
                "program.workstream_owner_duplicate",
                f"Workstream Focus repeats primary module / causal owner {owner!r}: {proposal_path.as_posix()}",
            )
        owners.add(owner)
        workstream_candidate_ids = _comma_separated_values(
            _field_value(workstream.section, "Candidate / obligation IDs") or "",
            invalid_code="program.candidate_id_invalid",
            duplicate_code="program.candidate_id_duplicate",
            label=f"Workstream Focus {workstream.stable_id!r} Candidate / obligation IDs",
            proposal_path=proposal_path,
        )
        if any(candidate_id in candidate_ids for candidate_id in workstream_candidate_ids):
            raise ContractViolation(
                "program.candidate_id_duplicate",
                f"Candidate / obligation IDs must be unique across workstreams: {proposal_path.as_posix()}",
            )
        candidate_ids.extend(workstream_candidate_ids)
        triggered_policies = _triggered_policies(
            root,
            workstream.section,
            proposal_path,
            code_prefix="program.workstream",
            record_name=f"Workstream Focus {workstream.stable_id!r}",
        )
        _validate_selected_policy_reviews(
            workstream.section,
            triggered_policies,
            proposal_path,
            review_level=4,
            code_prefix="program.workstream",
        )

    if set(budget) != set(candidate_ids):
        raise ContractViolation(
            "program.candidate_budget_mismatch",
            f"Candidate / obligation budget must exactly match the workstream union: {proposal_path.as_posix()}",
        )


def _validate_ordinary_proposal(root: Path, proposal: str, proposal_path: Path) -> None:
    matches = list(re.finditer(r"^## Change Focus\s*$", proposal, flags=re.MULTILINE))
    if len(matches) != 1:
        raise ContractViolation(
            "focus.heading_missing",
            f"proposal must contain exactly one {FOCUS_HEADING!r}: {proposal_path.as_posix()}",
        )
    focus_section = _section_after_heading(proposal, matches[0], maximum_level=2)
    _validate_legacy_triggered_policies_field(
        focus_section,
        code="focus.legacy_triggered_policies_field_present",
        record_name="Focus Card",
        proposal_path=proposal_path,
    )
    _validate_required_fields(
        focus_section,
        FOCUS_FIELDS,
        code="focus.field_missing",
        record_name="Focus Card",
        proposal_path=proposal_path,
    )
    _validate_seam_classification(
        focus_section,
        code_prefix="focus",
        record_name="Focus Card",
        proposal_path=proposal_path,
    )
    triggered_policies = _triggered_policies(root, focus_section, proposal_path)
    _validate_selected_policy_reviews(
        proposal,
        triggered_policies,
        proposal_path,
        review_level=2,
        code_prefix="focus",
    )


def _validate_active_changes(root: Path) -> None:
    changes_root = root / CHANGES_ROOT
    if not changes_root.exists():
        return
    if not changes_root.is_dir():
        raise ContractViolation(
            "focus.changes_root_kind",
            f"changes root is not a directory: {CHANGES_ROOT.as_posix()}",
        )

    active_changes = sorted(
        path
        for path in changes_root.iterdir()
        if path.is_dir() and path.name != "archive" and not path.name.startswith(".")
    )
    for change_root in active_changes:
        proposal_path = change_root / "proposal.md"
        if not proposal_path.is_file():
            raise ContractViolation(
                "focus.proposal_missing",
                f"active change lacks proposal.md: {proposal_path.relative_to(root).as_posix()}",
            )
        try:
            proposal = proposal_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise ContractViolation(
                "focus.proposal_unreadable",
                f"cannot read active proposal {proposal_path.relative_to(root).as_posix()}: {exc}",
            ) from exc
        relative_proposal_path = proposal_path.relative_to(root)
        program_count = len(re.findall(r"^## Program Focus\s*$", proposal, flags=re.MULTILINE))
        workstream_count = len(re.findall(r"^### Workstream Focus:", proposal, flags=re.MULTILINE))
        if program_count or workstream_count:
            if program_count != 1 or re.search(r"^## Change Focus\s*$", proposal, flags=re.MULTILINE):
                raise ContractViolation(
                    "program.mode_invalid",
                    "ordinary and program proposal forms are exclusive: "
                    f"{relative_proposal_path.as_posix()}",
                )
            _validate_program_proposal(root, proposal, relative_proposal_path)
        else:
            _validate_ordinary_proposal(root, proposal, relative_proposal_path)


def validate(root: Path) -> list[str]:
    if not root.is_dir():
        raise ContractViolation("root.missing", f"project root is not a directory: {root}")
    _validate_charter_tree(root)
    _validate_focus_gate(root)
    _validate_claude_guide(root)
    _validate_authoring_pointer(root)
    warnings = _validate_information_map(root)
    _validate_active_changes(root)
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".", help="repository root to validate")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    try:
        warnings = validate(root)
    except ContractViolation as exc:
        print(f"[{exc.code}] {exc.detail}", file=sys.stderr)
        return 1
    for warning in warnings:
        print(warning, file=sys.stderr)
    print("Agent charter governance passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
