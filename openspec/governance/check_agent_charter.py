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


def _focus_section(proposal: str, proposal_path: Path) -> str:
    matches = list(re.finditer(r"^## Change Focus\s*$", proposal, flags=re.MULTILINE))
    if len(matches) != 1:
        raise ContractViolation(
            "focus.heading_missing",
            f"proposal must contain exactly one {FOCUS_HEADING!r}: {proposal_path.as_posix()}",
        )
    start = matches[0].end()
    next_heading = re.search(r"^## (?!#)", proposal[start:], flags=re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(proposal)
    return proposal[start:end]


def _validate_focus_card(proposal: str, proposal_path: Path) -> str:
    section = _focus_section(proposal, proposal_path)
    legacy_pattern = re.compile(
        rf"^- \*\*{re.escape(LEGACY_TRIGGERED_POLICIES_FIELD)}:\*\*", re.MULTILINE
    )
    if legacy_pattern.search(section):
        raise ContractViolation(
            "focus.legacy_triggered_policies_field_present",
            f"Focus Card uses the retired field {LEGACY_TRIGGERED_POLICIES_FIELD!r}: "
            f"{proposal_path.as_posix()}",
        )
    for field in FOCUS_FIELDS:
        pattern = re.compile(rf"^- \*\*{re.escape(field)}:\*\*[ \t]*\S", re.MULTILINE)
        if not pattern.search(section):
            raise ContractViolation(
                "focus.field_missing",
                f"Focus Card field {field!r} is missing or empty: {proposal_path.as_posix()}",
            )
    seam_pattern = re.compile(
        rf"^- \*\*{re.escape(SEAM_CLASSIFICATION_FIELD)}:\*\*[ \t]*(?P<value>\S+)(?P<rest>[^\n]*)$",
        re.MULTILINE,
    )
    seam_match = seam_pattern.search(section)
    if seam_match is None:
        raise ContractViolation(
            "focus.field_missing",
            f"Focus Card field {SEAM_CLASSIFICATION_FIELD!r} is missing or empty: {proposal_path.as_posix()}",
        )
    seam_value = seam_match.group("value")
    if seam_value not in SEAM_CLASSIFICATIONS:
        raise ContractViolation(
            "focus.seam_classification_invalid",
            f"{SEAM_CLASSIFICATION_FIELD!r} must be exactly one of "
            f"{', '.join(sorted(SEAM_CLASSIFICATIONS))}, written bare: {proposal_path.as_posix()}",
        )
    if not seam_match.group("rest").strip():
        raise ContractViolation(
            "focus.seam_classification_rationale_missing",
            f"{SEAM_CLASSIFICATION_FIELD!r} must give a short rationale after the value: "
            f"{proposal_path.as_posix()}",
        )
    return section


def _triggered_policies(root: Path, focus_section: str, proposal_path: Path) -> tuple[str, ...]:
    pattern = re.compile(
        rf"^- \*\*{re.escape(TRIGGERED_POLICIES_FIELD)}:\*\*[ \t]*(?P<value>\S[^\n]*)$",
        re.MULTILINE,
    )
    match = pattern.search(focus_section)
    if match is None:
        raise ContractViolation(
            "focus.field_missing",
            f"Focus Card field {TRIGGERED_POLICIES_FIELD!r} is missing or empty: {proposal_path.as_posix()}",
        )

    following_line = next(
        (line for line in focus_section[match.end() :].splitlines() if line.strip()),
        "",
    )
    if following_line and following_line[0].isspace():
        raise ContractViolation(
            "focus.triggered_policies_continuation_invalid",
            f"{TRIGGERED_POLICIES_FIELD!r} must be a single-line comma-separated list: "
            f"{proposal_path.as_posix()}",
        )

    value = match.group("value").strip()
    if value == "none":
        raise ContractViolation(
            "focus.triggered_policies_rationale_missing",
            f"{TRIGGERED_POLICIES_FIELD!r} must give a short rationale after 'none:': {proposal_path.as_posix()}",
        )
    if value.startswith("none:"):
        if not value.removeprefix("none:").strip():
            raise ContractViolation(
                "focus.triggered_policies_rationale_missing",
                f"{TRIGGERED_POLICIES_FIELD!r} must give a short rationale after 'none:': {proposal_path.as_posix()}",
            )
        return ()

    policies = tuple(policy.strip() for policy in value.split(","))
    if not policies or any(not policy or policy not in POLICY_REGISTRY for policy in policies):
        raise ContractViolation(
            "focus.triggered_policy_unknown",
            f"{TRIGGERED_POLICIES_FIELD!r} must list canonical policy names or 'none: <rationale>': "
            f"{proposal_path.as_posix()}",
        )
    for policy in policies:
        document = POLICY_REGISTRY[policy]
        _read_file(root, document.path, code="focus.triggered_policy_document_missing")
    return policies


def _workflow_outcome_review_section(proposal: str, proposal_path: Path) -> str:
    matches = list(re.finditer(r"^## Workflow Outcome Review\s*$", proposal, flags=re.MULTILINE))
    if len(matches) != 1:
        raise ContractViolation(
            "focus.workflow_outcome_review_missing",
            f"proposal selecting {WORKFLOW_OUTCOME_REVIEW_POLICY!r} must contain exactly one "
            f"{WORKFLOW_OUTCOME_REVIEW_HEADING!r}: {proposal_path.as_posix()}",
        )
    start = matches[0].end()
    next_heading = re.search(r"^## (?!#)", proposal[start:], flags=re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(proposal)
    return proposal[start:end]


def _node_agent_review_section(proposal: str, proposal_path: Path) -> str:
    matches = list(re.finditer(r"^## Node Agent Review\s*$", proposal, flags=re.MULTILINE))
    if len(matches) != 1:
        raise ContractViolation(
            "focus.node_agent_review_missing",
            f"proposal selecting {NODE_AGENT_WORKFLOW_INTEGRITY_POLICY!r} must contain exactly one "
            f"{NODE_AGENT_REVIEW_HEADING!r}: {proposal_path.as_posix()}",
        )
    start = matches[0].end()
    next_heading = re.search(r"^## (?!#)", proposal[start:], flags=re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(proposal)
    return proposal[start:end]


def _control_placement_review_section(proposal: str, proposal_path: Path) -> str:
    matches = list(re.finditer(r"^## Control Placement Review\s*$", proposal, flags=re.MULTILINE))
    if len(matches) != 1:
        raise ContractViolation(
            "focus.control_placement_review_missing",
            f"proposal selecting {CONTROL_PLACEMENT_POLICY!r} must contain exactly one "
            f"{CONTROL_PLACEMENT_REVIEW_HEADING!r}: {proposal_path.as_posix()}",
        )
    start = matches[0].end()
    next_heading = re.search(r"^## (?!#)", proposal[start:], flags=re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(proposal)
    return proposal[start:end]


def _table_cells(line: str) -> tuple[str, ...] | None:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return None
    return tuple(cell.strip() for cell in stripped[1:-1].split("|"))


def _is_markdown_separator(cells: tuple[str, ...], columns: tuple[str, ...]) -> bool:
    return len(cells) == len(columns) and all(
        re.fullmatch(r":?-{3,}:?", cell) is not None for cell in cells
    )


def _validate_workflow_outcome_review(proposal: str, proposal_path: Path) -> None:
    section = _workflow_outcome_review_section(proposal, proposal_path)
    table_lines = [line for line in section.splitlines() if _table_cells(line) is not None]
    if len(table_lines) < 3:
        raise ContractViolation(
            "focus.workflow_outcome_review_shape_invalid",
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
            "focus.workflow_outcome_review_shape_invalid",
            f"{WORKFLOW_OUTCOME_REVIEW_HEADING!r} has an invalid table header: {proposal_path.as_posix()}",
        )
    for line in table_lines[2:]:
        cells = _table_cells(line)
        assert cells is not None
        if len(cells) != len(WORKFLOW_OUTCOME_REVIEW_COLUMNS) or any(not cell for cell in cells):
            raise ContractViolation(
                "focus.workflow_outcome_review_shape_invalid",
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
    proposal: str, proposal_path: Path, triggered_policies: tuple[str, ...]
) -> None:
    section = _control_placement_review_section(proposal, proposal_path)
    table_lines = _single_markdown_table_lines(section)
    if table_lines is None or len(table_lines) < 3:
        raise ContractViolation(
            "focus.control_placement_review_shape_invalid",
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
            "focus.control_placement_review_shape_invalid",
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
                "focus.control_placement_review_shape_invalid",
                f"{CONTROL_PLACEMENT_REVIEW_HEADING!r} has an incomplete or duplicate table row: "
                f"{proposal_path.as_posix()}",
            )
        if cells[3] not in CONTROL_PLACEMENT_POSTURES:
            raise ContractViolation(
                "focus.control_placement_review_posture_invalid",
                f"{CONTROL_PLACEMENT_REVIEW_HEADING!r} uses an unsupported design posture {cells[3]!r}: "
                f"{proposal_path.as_posix()}",
            )
        has_human_decision = has_human_decision or cells[3] == "human-decision"

    if has_human_decision and "human-interaction-integrity" not in triggered_policies:
        raise ContractViolation(
            "focus.control_placement_human_interaction_policy_missing",
            f"{CONTROL_PLACEMENT_REVIEW_HEADING!r} with a human-decision row also requires "
            f"'human-interaction-integrity': {proposal_path.as_posix()}",
        )


def _validate_node_agent_review(proposal: str, proposal_path: Path) -> None:
    section = _node_agent_review_section(proposal, proposal_path)
    table_lines = _single_markdown_table_lines(section)
    if table_lines is None or len(table_lines) < 3:
        raise ContractViolation(
            "focus.node_agent_review_shape_invalid",
            f"{NODE_AGENT_REVIEW_HEADING!r} needs exactly one header, separator, and at least one row: "
            f"{proposal_path.as_posix()}",
        )
    header = _table_cells(table_lines[0])
    separator = _table_cells(table_lines[1])
    assert header is not None and separator is not None
    if header != NODE_AGENT_REVIEW_COLUMNS or not _is_markdown_separator(separator, NODE_AGENT_REVIEW_COLUMNS):
        raise ContractViolation(
            "focus.node_agent_review_shape_invalid",
            f"{NODE_AGENT_REVIEW_HEADING!r} has an invalid table header: {proposal_path.as_posix()}",
        )
    for line in table_lines[2:]:
        cells = _table_cells(line)
        assert cells is not None
        if len(cells) != len(NODE_AGENT_REVIEW_COLUMNS) or any(not cell for cell in cells):
            raise ContractViolation(
                "focus.node_agent_review_shape_invalid",
                f"{NODE_AGENT_REVIEW_HEADING!r} has an incomplete table row: {proposal_path.as_posix()}",
            )
        if cells[1] not in NODE_AGENT_CLASSIFICATIONS:
            raise ContractViolation(
                "focus.node_agent_review_classification_invalid",
                f"{NODE_AGENT_REVIEW_HEADING!r} uses an unsupported classification {cells[1]!r}: "
                f"{proposal_path.as_posix()}",
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
        focus_section = _validate_focus_card(proposal, relative_proposal_path)
        triggered_policies = _triggered_policies(root, focus_section, relative_proposal_path)
        if CONTROL_PLACEMENT_POLICY in triggered_policies:
            _validate_control_placement_review(proposal, relative_proposal_path, triggered_policies)
        if NODE_AGENT_WORKFLOW_INTEGRITY_POLICY in triggered_policies:
            _validate_node_agent_review(proposal, relative_proposal_path)
        if WORKFLOW_OUTCOME_REVIEW_POLICY in triggered_policies:
            _validate_workflow_outcome_review(proposal, relative_proposal_path)


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
