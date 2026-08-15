"""Deterministic contracts for the Deep Research Change Guidance gate.

@impl DRC-001
@impl DRC-002
@impl DRC-003
@impl DRC-004
@impl DRC-005
@impl DRC-006
@impl DRC-007
@impl DRC-008
@impl DRC-009
@impl DRC-010
@impl DRC-011
@impl PRS-009
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER = REPO_ROOT / "openspec" / "governance" / "check_change_guidance.py"
CHARTER_ROOT = Path("openspec/change-guidance")
LEGACY_CHARTER_ROOT = Path("openspec/governance/agent-charter")
RETIRED_GUIDANCE_ROOTS = (
    Path("openspec/agent-charter"),
    Path("openspec/policies"),
    Path("openspec/guardrails"),
)
POLICY_ROOT = CHARTER_ROOT / "policies"
CLAUDE_GUIDE_PATH = Path("deep_research_harness/CLAUDE.md")
README_PATH = Path("deep_research_harness/README.md")
DOCS_INDEX_PATH = Path("deep_research_harness/docs/README.md")
FOCUSED_DOC_PATHS = (
    Path("deep_research_harness/docs/runtime-architecture.md"),
    Path("deep_research_harness/docs/local-operations.md"),
    Path("deep_research_harness/docs/testing-and-evaluation.md"),
)
FOCUS_BEGIN = "<!-- BEGIN: DEEP-RESEARCH-FOCUS-GATE -->"
FOCUS_END = "<!-- END: DEEP-RESEARCH-FOCUS-GATE -->"
CONTEXT_EXPANSION_HEADING = "## Context Expansion Gate"
CONTEXT_EXPANSION_SENTENCE = "A possible future use is not enough to expand scope."
PROGRAM_ROUTE_ANCHOR = "Program form: `## Program Focus` with at least two"
CLAUDE_IMPORT = "@AGENTS.md"
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
SEAM_CLASSIFICATION_FIELD = "Seam classification"
SEAM_CLASSIFICATIONS = (
    "cognitive-program",
    "human-decision",
    "deterministic-guardrail",
    "wiring",
)
TRIGGERED_POLICIES_FIELD = "Triggered review policies"
LEGACY_TRIGGERED_POLICIES_FIELD = "Triggered charter policies"
WORKFLOW_OUTCOME_POLICY = "workflow-outcome-review"
WORKFLOW_OUTCOME_REVIEW_HEADING = "## Workflow Outcome Review"
NODE_AGENT_WORKFLOW_INTEGRITY_POLICY = "node-agent-workflow-integrity"
NODE_AGENT_REVIEW_HEADING = "## Node Agent Review"
CONTROL_PLACEMENT_POLICY = "control-placement"
CONTROL_PLACEMENT_REVIEW_HEADING = "## Control Placement Review"
CONTROL_PLACEMENT_TASKS_RULE = "When `Triggered review policies` includes `control-placement`, tasks.md MUST retain"
APPLY_GUIDANCE = "Review control-placement only when the selected proposal declares it; guidance is advisory."
ARCHIVE_GUIDANCE = (
    "Before archive, review control-placement only when the selected proposal declares it; guidance is advisory."
)
OPERATION_GUIDANCE_ADVISORY_BOUNDARY = "does not execute commands, create or complete tasks, or block native operations"
CLOSEOUT_EVIDENCE_GUIDANCE = (
    "openspec/governance/closeout-evidence/selected_change_closeout.py verifies only caller-declared committed ranges"
)
CONTROL_PLACEMENT_REVIEW_COLUMNS = (
    "Changed decision or fact",
    "Cognitive candidate or human judgment",
    "Direct fact and deterministic owner/evaluator",
    "Design posture",
    "Protected invariant or legal recovery",
    "Reuse or complexity removed/avoided",
    "Deterministic evidence seam",
)
CONTROL_PLACEMENT_POSTURES = (
    "advisory",
    "bounded-repair",
    "human-decision",
    "non-bypassable",
)
CHARTER_POLICY_NAMES = (
    "local-context",
    "authority-and-projections",
    "participant-outcomes",
    "human-interaction-integrity",
    "control-and-recovery",
    WORKFLOW_OUTCOME_POLICY,
    NODE_AGENT_WORKFLOW_INTEGRITY_POLICY,
    "change-admission",
    "agent-information-map",
)
POLICY_NAMES = (*CHARTER_POLICY_NAMES, CONTROL_PLACEMENT_POLICY)
POLICY_PATHS = {name: POLICY_ROOT / f"{name}.md" for name in POLICY_NAMES}
WARNING_BUDGETS = (
    (Path("deep_research_harness/AGENTS.md"), 120),
    (CLAUDE_GUIDE_PATH, 10),
    (Path("openspec/config.yaml"), 140),
    (README_PATH, 201),
)
HARD_BUDGETS = (
    (Path("deep_research_harness/AGENTS.md"), 161),
    (CLAUDE_GUIDE_PATH, 13),
    (Path("openspec/config.yaml"), 181),
)


def _write(root: Path, relative_path: Path | str, text: str = "") -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _replace(root: Path, relative_path: Path | str, old: str, new: str) -> None:
    path = root / relative_path
    path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


def _pad_to_lines(root: Path, relative_path: Path, target: int) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    lines.extend("fixture filler" for _ in range(target - len(lines)))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _workflow_outcome_review_record() -> str:
    return (
        f"{WORKFLOW_OUTCOME_REVIEW_HEADING}\n\n"
        "| Failure class | Fact owner | Recovery owner and bound | "
        "Terminal disposition | Legal next action | Deterministic evidence seam |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        "| provider.timeout | fixture phase | one bounded retry | blocked | fresh start | fixture test |\n"
    )


def _node_agent_review_record(*, classification: str = "node-agent") -> str:
    return (
        f"{NODE_AGENT_REVIEW_HEADING}\n\n"
        "| Surface | Classification | Bounded cognitive question or no-agent rationale | "
        "Input authority boundary | Tool posture and runtime enforcer | "
        "Candidate result and deterministic admission owner | Failure owner and bound | "
        "Deterministic evidence seam |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| fixture node | "
        f"{classification} | "
        "fixture bounded question | trusted fixture input | fixture runtime policy | "
        "typed fixture candidate and parser | fixture owner with one bound | fixture test |\n"
    )


def _control_placement_review_record(*, posture: str = "advisory") -> str:
    return (
        f"{CONTROL_PLACEMENT_REVIEW_HEADING}\n\n"
        "| Changed decision or fact | Cognitive candidate or human judgment | "
        "Direct fact and deterministic owner/evaluator | Design posture | "
        "Protected invariant or legal recovery | Reuse or complexity removed/avoided | "
        "Deterministic evidence seam |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        "| fixture decision | fixture candidate | fixture fact and owner | "
        f"{posture} | fixture invariant | fixture reuse | fixture test |\n"
    )


def _workstream_control_placement_review_record(*, posture: str = "advisory") -> str:
    return _control_placement_review_record(posture=posture).replace(
        CONTROL_PLACEMENT_REVIEW_HEADING,
        "#### Control Placement Review",
        1,
    )


def _workstream_workflow_outcome_review_record() -> str:
    return _workflow_outcome_review_record().replace(
        WORKFLOW_OUTCOME_REVIEW_HEADING,
        "#### Workflow Outcome Review",
        1,
    )


def _workstream_node_agent_review_record(*, classification: str = "node-agent") -> str:
    return _node_agent_review_record(classification=classification).replace(
        NODE_AGENT_REVIEW_HEADING,
        "#### Node Agent Review",
        1,
    )


def _focus_card(
    *,
    triggered_policies: str = "none: fixture documentation rationale",
    seam_classification: str = "deterministic-guardrail",
    include_workflow_outcome_review: bool = False,
    include_node_agent_review: bool = False,
    node_agent_classification: str = "node-agent",
    include_control_placement_review: bool = False,
    control_placement_posture: str = "advisory",
) -> str:
    field_values = {field: "fixture" for field in FOCUS_FIELDS}
    field_values[SEAM_CLASSIFICATION_FIELD] = f"{seam_classification} — fixture rationale"
    field_values[TRIGGERED_POLICIES_FIELD] = triggered_policies
    fields = "\n".join(f"- **{field}:** {field_values[field]}" for field in FOCUS_FIELDS)
    reviews = ""
    if include_node_agent_review:
        reviews += _node_agent_review_record(classification=node_agent_classification)
    if include_workflow_outcome_review:
        reviews += _workflow_outcome_review_record()
    if include_control_placement_review:
        reviews += _control_placement_review_record(posture=control_placement_posture)
    return f"## Change Focus\n\n{fields}\n\n{reviews}"


def _program_focus(
    *,
    budget: str = "OR-C01, TA-C01",
    declared_workstream_order: str = "alpha, beta",
    workstreams: tuple[tuple[str, str, str], ...] = (
        ("alpha", "owner-alpha", "OR-C01"),
        ("beta", "owner-beta", "TA-C01"),
    ),
    policies_by_workstream: dict[str, str] | None = None,
    reviews_by_workstream: dict[str, str] | None = None,
) -> str:
    program_values = {field: "fixture" for field in PROGRAM_FOCUS_FIELDS}
    program_values["Candidate / obligation budget"] = budget
    program_values["Declared workstream order"] = declared_workstream_order
    program_fields = "\n".join(f"- **{field}:** {program_values[field]}" for field in PROGRAM_FOCUS_FIELDS)
    workstream_sections = []
    policies_by_workstream = policies_by_workstream or {}
    reviews_by_workstream = reviews_by_workstream or {}
    for stable_id, owner, candidate_ids in workstreams:
        values = {field: "fixture" for field in WORKSTREAM_FIELDS}
        values["Primary module / causal owner"] = owner
        values[SEAM_CLASSIFICATION_FIELD] = "deterministic-guardrail — fixture rationale"
        values[TRIGGERED_POLICIES_FIELD] = policies_by_workstream.get(
            stable_id,
            "none: fixture documentation rationale",
        )
        values["Candidate / obligation IDs"] = candidate_ids
        fields = "\n".join(f"- **{field}:** {values[field]}" for field in WORKSTREAM_FIELDS)
        review = reviews_by_workstream.get(stable_id, "")
        workstream_sections.append(f"{WORKSTREAM_FOCUS_PREFIX}{stable_id}\n\n{fields}\n\n{review}".rstrip())
    return f"{PROGRAM_FOCUS_HEADING}\n\n{program_fields}\n\n" + "\n\n".join(workstream_sections) + "\n"


def _project(root: Path) -> None:
    links = "\n".join(f"- [policy](policies/{name}.md)" for name in POLICY_NAMES)
    _write(
        root,
        CHARTER_ROOT / "README.md",
        "# Deep Research Change Guidance\n\n"
        "## Start Here\n\n"
        "Read `deep_research_harness/AGENTS.md` and `principles.md`.\n\n"
        "## Policy Route\n\n"
        f"{links}\n",
    )
    _write(
        root,
        CHARTER_ROOT / "principles.md",
        "# Deep Research Change Guidance\n\n> authority: guidance only; never runtime control\n\n## Product Boundary\n",
    )
    _write(root, CHARTER_ROOT / "node-edit-map.md", "# Node Edit Map\n")
    _write(
        root,
        "openspec/README.md",
        "# OpenSpec\n\nconfig.yaml\nspecs/\nchanges/\nchange-guidance/README.md\ngovernance/\n",
    )
    for name in POLICY_NAMES:
        extra = ""
        if name == "local-context":
            extra = (
                f"\n{CONTEXT_EXPANSION_HEADING}\n{CONTEXT_EXPANSION_SENTENCE}\n"
                f"\n{PROGRAM_ROUTE_ANCHOR} registered Workstream Focus records.\n"
            )
        if name == "change-admission":
            extra = f"\n{PROGRAM_ROUTE_ANCHOR} registered Workstream Focus records.\n"
        if name == "agent-information-map":
            extra = (
                "\n## Reader Roles\n"
                "deep_research_harness/docs/README.md\n"
                "runtime-architecture.md\n"
                "local-operations.md\n"
                "testing-and-evaluation.md\n"
                "\n## Line Budgets\nword-count\n"
            )
        _write(
            root,
            POLICY_PATHS[name],
            f"# {name}\n\n> trigger: fixture\n> authority: guidance only\n{extra}\n## Boundary\n",
        )
    _write(
        root,
        "deep_research_harness/AGENTS.md",
        "# Deep Research\n\n"
        f"{FOCUS_BEGIN}\n"
        "Read `../openspec/change-guidance/README.md`.\n"
        "Choose one primary module and record `## Change Focus`.\n\n"
        f"{CONTEXT_EXPANSION_SENTENCE}\n\n"
        f"{PROGRAM_ROUTE_ANCHOR} registered Workstream Focus records.\n\n"
        "| Central question | Primary owner to inspect first |\n"
        "| --- | --- |\n"
        "| Fixture | `domain/` |\n"
        f"{FOCUS_END}\n\n"
        "## Information Map\n\n"
        "README.md\nproject-structure.toml\n\n"
        "<!-- BEGIN GENERATED: PROJECT-STRUCTURE -->\n"
        "fixture\n"
        "<!-- END GENERATED: PROJECT-STRUCTURE -->\n",
    )
    _write(
        root,
        CLAUDE_GUIDE_PATH,
        f"# Deep Research Guidance\n\nClaude Code imports the local guide below.\n\n{CLAUDE_IMPORT}\n",
    )
    _write(
        root,
        "openspec/config.yaml",
        "## Default Context Boundary\n"
        "not a project manual\n"
        "rules:\n"
        "  proposal:\n"
        '    - "Use openspec/change-guidance/README.md and `## Change Focus` '
        "with Primary module / causal owner and Triggered review policies. "
        f'{CONTEXT_EXPANSION_SENTENCE}"\n'
        f'    - "{PROGRAM_ROUTE_ANCHOR} registered Workstream Focus records."\n'
        '    - "control-placement requires `## Control Placement Review`."\n'
        '    - "workflow-outcome-review requires `## Workflow Outcome Review`."\n'
        '    - "node-agent-workflow-integrity requires `## Node Agent Review` and only routes admission."\n'
        "  tasks:\n"
        f'    - "{CONTROL_PLACEMENT_TASKS_RULE} durable review tasks."\n'
        "operations:\n"
        "  apply:\n"
        "    guidance:\n"
        f'      - "{APPLY_GUIDANCE}"\n'
        f'      - "For a selected control-placement change, {CLOSEOUT_EVIDENCE_GUIDANCE}; its evidence is '
        'non-authoritative and does not change native archive authority."\n'
        f'      - "{OPERATION_GUIDANCE_ADVISORY_BOUNDARY}"\n'
        "  archive:\n"
        "    guidance:\n"
        f'      - "{ARCHIVE_GUIDANCE}"\n'
        f'      - "{OPERATION_GUIDANCE_ADVISORY_BOUNDARY}"\n',
    )
    _write(
        root,
        README_PATH,
        "# Deep Research\n\n## Reading Map\n\n"
        "Read AGENTS.md for code changes.\n"
        "docs/README.md\n"
        "docs/runtime-architecture.md\n"
        "docs/local-operations.md\n"
        "docs/testing-and-evaluation.md\n",
    )
    _write(
        root,
        DOCS_INDEX_PATH,
        "\n".join(path.name for path in FOCUSED_DOC_PATHS) + "\n",
    )
    for path in FOCUSED_DOC_PATHS:
        _write(root, path, "# Focused documentation\n")
    _write(root, "openspec/changes/change-one/.openspec.yaml", "schema: spec-driven\n")
    _write(root, "openspec/changes/change-one/proposal.md", _focus_card())


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CHECKER), str(root)], text=True, capture_output=True, check=False)


def _assert_error(root: Path, code: str) -> None:
    result = _run(root)
    assert result.returncode == 1, result.stdout
    assert code in result.stderr


def test_complete_change_guidance_and_focus_card_pass(tmp_path: Path) -> None:
    _project(tmp_path)

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "change guidance governance passed" in result.stdout.lower()


def test_complete_program_focus_with_registered_workstreams_passes(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(tmp_path, "openspec/changes/change-one/proposal.md", _program_focus())

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr


def test_mixed_ordinary_and_program_focus_fails_closed(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _program_focus() + "\n" + _focus_card(),
    )

    _assert_error(tmp_path, "program.mode_invalid")


@pytest.mark.parametrize(
    "field",
    PROGRAM_FOCUS_FIELDS,
)
def test_program_focus_requires_each_field(tmp_path: Path, field: str) -> None:
    _project(tmp_path)
    proposal = _program_focus()
    value = "fixture"
    if field == "Candidate / obligation budget":
        value = "OR-C01, TA-C01"
    elif field == "Declared workstream order":
        value = "alpha, beta"
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        proposal.replace(f"- **{field}:** {value}\n", "", 1),
    )

    _assert_error(tmp_path, "program.field_missing")


@pytest.mark.parametrize(
    "field",
    WORKSTREAM_FIELDS,
)
def test_workstream_focus_requires_each_field(tmp_path: Path, field: str) -> None:
    _project(tmp_path)
    proposal = _program_focus()
    value = "fixture"
    if field == "Primary module / causal owner":
        value = "owner-alpha"
    elif field == SEAM_CLASSIFICATION_FIELD:
        value = "deterministic-guardrail — fixture rationale"
    elif field == TRIGGERED_POLICIES_FIELD:
        value = "none: fixture documentation rationale"
    elif field == "Candidate / obligation IDs":
        value = "OR-C01"
    workstream_start = proposal.index(f"{WORKSTREAM_FOCUS_PREFIX}alpha")
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        proposal[:workstream_start] + proposal[workstream_start:].replace(f"- **{field}:** {value}\n", "", 1),
    )

    _assert_error(tmp_path, "program.workstream_field_missing")


@pytest.mark.parametrize(
    ("replacement", "code"),
    (
        ("Alpha", "program.workstream_id_invalid"),
        ("alpha_beta", "program.workstream_id_invalid"),
    ),
)
def test_program_focus_rejects_invalid_workstream_ids(
    tmp_path: Path,
    replacement: str,
    code: str,
) -> None:
    _project(tmp_path)
    proposal = _program_focus().replace(f"{WORKSTREAM_FOCUS_PREFIX}alpha", f"{WORKSTREAM_FOCUS_PREFIX}{replacement}")
    _write(tmp_path, "openspec/changes/change-one/proposal.md", proposal)

    _assert_error(tmp_path, code)


def test_program_focus_accepts_the_declared_stable_id_pattern(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _program_focus(
            declared_workstream_order="alpha-, beta",
            workstreams=(
                ("alpha-", "owner-alpha", "OR-C01"),
                ("beta", "owner-beta", "TA-C01"),
            ),
        ),
    )

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr


def test_program_focus_rejects_duplicate_workstream_id(tmp_path: Path) -> None:
    _project(tmp_path)
    proposal = _program_focus().replace(f"{WORKSTREAM_FOCUS_PREFIX}beta", f"{WORKSTREAM_FOCUS_PREFIX}alpha")
    _write(tmp_path, "openspec/changes/change-one/proposal.md", proposal)

    _assert_error(tmp_path, "program.workstream_id_duplicate")


def test_program_focus_rejects_duplicate_workstream_owner(tmp_path: Path) -> None:
    _project(tmp_path)
    proposal = _program_focus().replace("owner-beta", "owner-alpha")
    _write(tmp_path, "openspec/changes/change-one/proposal.md", proposal)

    _assert_error(tmp_path, "program.workstream_owner_duplicate")


def test_program_focus_requires_at_least_two_workstreams(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _program_focus(
            budget="OR-C01",
            declared_workstream_order="alpha",
            workstreams=(("alpha", "owner-alpha", "OR-C01"),),
        ),
    )

    _assert_error(tmp_path, "program.workstream_count_invalid")


@pytest.mark.parametrize(
    "declared_workstream_order",
    ("alpha", "alpha, missing"),
)
def test_program_focus_requires_exact_workstream_registration(
    tmp_path: Path,
    declared_workstream_order: str,
) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _program_focus(declared_workstream_order=declared_workstream_order),
    )

    _assert_error(tmp_path, "program.workstream_registration_mismatch")


def test_program_focus_rejects_duplicate_candidate_or_obligation_id(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _program_focus(
            workstreams=(
                ("alpha", "owner-alpha", "OR-C01"),
                ("beta", "owner-beta", "OR-C01"),
            )
        ),
    )

    _assert_error(tmp_path, "program.candidate_id_duplicate")


@pytest.mark.parametrize(
    "budget",
    ("OR-C01", "OR-C01, TA-C01, EC-C01"),
)
def test_program_focus_requires_budget_to_match_workstream_union(tmp_path: Path, budget: str) -> None:
    _project(tmp_path)
    _write(tmp_path, "openspec/changes/change-one/proposal.md", _program_focus(budget=budget))

    _assert_error(tmp_path, "program.candidate_budget_mismatch")


@pytest.mark.parametrize(
    ("budget", "declared_workstream_order", "code"),
    (
        ("OR-C01, OR-C01", "alpha, beta", "program.candidate_budget_duplicate"),
        ("OR-C01, TA-C01", "alpha, alpha", "program.workstream_order_duplicate"),
    ),
)
def test_program_focus_requires_unique_budget_and_order_entries(
    tmp_path: Path,
    budget: str,
    declared_workstream_order: str,
    code: str,
) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _program_focus(
            budget=budget,
            declared_workstream_order=declared_workstream_order,
        ),
    )

    _assert_error(tmp_path, code)


@pytest.mark.parametrize(
    ("policy_name", "workstream_review"),
    (
        (CONTROL_PLACEMENT_POLICY, _workstream_control_placement_review_record),
        (WORKFLOW_OUTCOME_POLICY, _workstream_workflow_outcome_review_record),
        (NODE_AGENT_WORKFLOW_INTEGRITY_POLICY, _workstream_node_agent_review_record),
    ),
)
def test_program_workstream_accepts_its_own_selected_policy_review(
    tmp_path: Path,
    policy_name: str,
    workstream_review: Callable[[], str],
) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _program_focus(
            policies_by_workstream={"alpha": policy_name},
            reviews_by_workstream={"alpha": workstream_review()},
        ),
    )

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("policy_name", "workstream_review", "program_review", "code"),
    (
        (
            CONTROL_PLACEMENT_POLICY,
            _workstream_control_placement_review_record,
            _control_placement_review_record,
            "program.workstream_control_placement_review_missing",
        ),
        (
            WORKFLOW_OUTCOME_POLICY,
            _workstream_workflow_outcome_review_record,
            _workflow_outcome_review_record,
            "program.workstream_workflow_outcome_review_missing",
        ),
        (
            NODE_AGENT_WORKFLOW_INTEGRITY_POLICY,
            _workstream_node_agent_review_record,
            _node_agent_review_record,
            "program.workstream_node_agent_review_missing",
        ),
    ),
)
@pytest.mark.parametrize("borrowed_review", ("program", "sibling"))
def test_program_workstream_cannot_borrow_a_selected_policy_review(
    tmp_path: Path,
    borrowed_review: str,
    policy_name: str,
    workstream_review: Callable[[], str],
    program_review: Callable[[], str],
    code: str,
) -> None:
    _project(tmp_path)
    reviews = {"beta": workstream_review()}
    proposal = _program_focus(
        policies_by_workstream={"alpha": policy_name},
        reviews_by_workstream=reviews if borrowed_review == "sibling" else {},
    )
    if borrowed_review == "program":
        proposal += "\n" + program_review()
    _write(tmp_path, "openspec/changes/change-one/proposal.md", proposal)

    _assert_error(tmp_path, code)


@pytest.mark.parametrize("policy_name", POLICY_NAMES)
def test_missing_policy_fails_with_its_path(tmp_path: Path, policy_name: str) -> None:
    _project(tmp_path)
    (tmp_path / POLICY_PATHS[policy_name]).unlink()

    _assert_error(tmp_path, "guidance.policy_members_mismatch")


def test_missing_index_link_fails(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(
        tmp_path,
        CHARTER_ROOT / "README.md",
        "(policies/local-context.md)",
        "(policies/other.md)",
    )

    _assert_error(tmp_path, "charter.index_link_missing")


def test_second_policy_index_fails_closed(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(tmp_path, POLICY_ROOT / "README.md", "# Duplicate policy index\n")

    _assert_error(tmp_path, "guidance.policy_index_present")


def test_legacy_charter_tree_does_not_substitute_for_the_canonical_tree(tmp_path: Path) -> None:
    _project(tmp_path)
    legacy_root = tmp_path / LEGACY_CHARTER_ROOT
    legacy_root.parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / CHARTER_ROOT).rename(legacy_root)

    result = _run(tmp_path)

    assert result.returncode == 1, result.stdout
    assert "guidance.retired_tree_present" in result.stderr


def test_duplicate_legacy_charter_tree_fails_closed(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(tmp_path, LEGACY_CHARTER_ROOT / "README.md", "# Legacy Charter\n")

    _assert_error(tmp_path, "guidance.retired_tree_present")


@pytest.mark.parametrize("retired_root", RETIRED_GUIDANCE_ROOTS)
def test_retired_guidance_roots_fail_closed(tmp_path: Path, retired_root: Path) -> None:
    _project(tmp_path)
    _write(tmp_path, retired_root / "legacy.md", "# Retired route\n")

    _assert_error(tmp_path, "guidance.retired_tree_present")


def test_duplicate_guidance_tree_fails_closed(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(tmp_path, "openspec/agent-charter/README.md", "# Duplicate Guidance\n")

    _assert_error(tmp_path, "guidance.retired_tree_present")


def test_extra_guidance_member_fails_closed(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(tmp_path, CHARTER_ROOT / "unregistered.md", "# Extra guidance\n")

    _assert_error(tmp_path, "guidance.root_members_mismatch")


def test_extra_policy_member_fails_closed(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(tmp_path, POLICY_ROOT / "unregistered.md", "# Extra policy\n")

    _assert_error(tmp_path, "guidance.policy_members_mismatch")


def test_missing_focus_gate_fails(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, "deep_research_harness/AGENTS.md", FOCUS_BEGIN, "")

    _assert_error(tmp_path, "guide.focus_gate_missing")


@pytest.mark.parametrize(
    ("relative_path", "code"),
    (
        (Path("openspec/config.yaml"), "config.program_route_missing"),
        (POLICY_PATHS["local-context"], "charter.program_route_local_context_missing"),
        (POLICY_PATHS["change-admission"], "charter.program_route_change_admission_missing"),
        (Path("deep_research_harness/AGENTS.md"), "guide.program_route_missing"),
    ),
)
def test_program_route_requires_each_authoring_anchor(
    tmp_path: Path,
    relative_path: Path,
    code: str,
) -> None:
    _project(tmp_path)
    _replace(tmp_path, relative_path, PROGRAM_ROUTE_ANCHOR, "missing-program-route")

    _assert_error(tmp_path, code)


def test_missing_context_expansion_policy_anchor_fails(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(
        tmp_path,
        POLICY_PATHS["local-context"],
        CONTEXT_EXPANSION_HEADING,
        "",
    )

    _assert_error(tmp_path, "charter.context_expansion_policy_missing")


def test_missing_context_expansion_guide_anchor_fails(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, "deep_research_harness/AGENTS.md", CONTEXT_EXPANSION_SENTENCE, "")

    _assert_error(tmp_path, "guide.context_expansion_rule_missing")


def test_missing_context_expansion_authoring_anchor_fails(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, "openspec/config.yaml", CONTEXT_EXPANSION_SENTENCE, "")

    _assert_error(tmp_path, "config.context_expansion_rule_missing")


def test_config_requires_triggered_policy_rule(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, "openspec/config.yaml", TRIGGERED_POLICIES_FIELD, "")

    _assert_error(tmp_path, "config.triggered_policies_rule_missing")


def test_config_rejects_legacy_triggered_policy_field(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, "openspec/config.yaml", TRIGGERED_POLICIES_FIELD, LEGACY_TRIGGERED_POLICIES_FIELD)

    _assert_error(tmp_path, "config.legacy_triggered_policies_rule_present")


def test_config_requires_workflow_outcome_review_rule(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, "openspec/config.yaml", WORKFLOW_OUTCOME_POLICY, "")

    _assert_error(tmp_path, "config.workflow_outcome_review_rule_missing")


def test_config_requires_node_agent_workflow_integrity_rule(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, "openspec/config.yaml", NODE_AGENT_WORKFLOW_INTEGRITY_POLICY, "missing-policy")

    _assert_error(tmp_path, "config.node_agent_workflow_integrity_rule_missing")


def test_config_requires_control_placement_task_obligation(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, "openspec/config.yaml", CONTROL_PLACEMENT_TASKS_RULE, "missing-task-rule")

    _assert_error(tmp_path, "config.control_placement_task_rule_missing")


def test_config_requires_distinct_apply_operation_guidance(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, "openspec/config.yaml", APPLY_GUIDANCE, "missing-apply-guidance")

    _assert_error(tmp_path, "config.operation_apply_guidance_missing")


def test_config_requires_distinct_archive_operation_guidance(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, "openspec/config.yaml", ARCHIVE_GUIDANCE, "missing-archive-guidance")

    _assert_error(tmp_path, "config.operation_archive_guidance_missing")


def test_config_requires_selection_limited_operation_guidance(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, "openspec/config.yaml", "only when the selected proposal declares it", "unconditionally")

    _assert_error(tmp_path, "config.operation_guidance_selection_boundary_missing")


def test_config_requires_advisory_operation_guidance_boundary(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, "openspec/config.yaml", OPERATION_GUIDANCE_ADVISORY_BOUNDARY, "missing-advisory-boundary")

    _assert_error(tmp_path, "config.operation_guidance_advisory_boundary_missing")


def test_config_requires_selected_change_closeout_evidence_route(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, "openspec/config.yaml", CLOSEOUT_EVIDENCE_GUIDANCE, "missing-closeout-evidence-route")

    _assert_error(tmp_path, "config.closeout_evidence_guidance_missing")


def test_missing_claude_code_entrypoint_fails(tmp_path: Path) -> None:
    _project(tmp_path)
    (tmp_path / CLAUDE_GUIDE_PATH).unlink()

    _assert_error(tmp_path, "guide.claude_entrypoint_missing")


def test_claude_code_entrypoint_requires_the_authoritative_import(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, CLAUDE_GUIDE_PATH, CLAUDE_IMPORT, "@OTHER.md")

    _assert_error(tmp_path, "guide.claude_import_missing")


def test_information_map_policy_requires_budget_anchor(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(
        tmp_path,
        POLICY_PATHS["agent-information-map"],
        "## Line Budgets",
        "",
    )

    _assert_error(tmp_path, "charter.information_map_policy_missing")


def test_module_guide_requires_information_map(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, "deep_research_harness/AGENTS.md", "## Information Map", "")

    _assert_error(tmp_path, "guide.information_map_missing")


def test_readme_requires_an_early_reading_map(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(tmp_path, README_PATH, "\n".join(["fixture"] * 81) + "\n## Reading Map\n")

    _assert_error(tmp_path, "readme.reading_map_position")


@pytest.mark.parametrize("path", (DOCS_INDEX_PATH, *FOCUSED_DOC_PATHS))
def test_readme_requires_stable_human_document_links(tmp_path: Path, path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, README_PATH, path.relative_to("deep_research_harness").as_posix(), "missing.md")

    _assert_error(tmp_path, "readme.docs_link_missing")


@pytest.mark.parametrize("path", FOCUSED_DOC_PATHS)
def test_documentation_index_requires_each_focused_link(tmp_path: Path, path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, DOCS_INDEX_PATH, path.name, "missing.md")

    _assert_error(tmp_path, "docs.index_link_missing")


def test_documentation_index_requires_focused_documents_to_exist(tmp_path: Path) -> None:
    _project(tmp_path)
    (tmp_path / FOCUSED_DOC_PATHS[0]).unlink()

    _assert_error(tmp_path, "docs.focused_document_missing")


def test_config_requires_information_map_boundary(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(tmp_path, "openspec/config.yaml", "## Default Context Boundary", "")

    _assert_error(tmp_path, "config.information_map_missing")


@pytest.mark.parametrize(("relative_path", "line_count"), WARNING_BUDGETS)
def test_line_budget_warns_before_hard_limit(tmp_path: Path, relative_path: Path, line_count: int) -> None:
    _project(tmp_path)
    _pad_to_lines(tmp_path, relative_path, line_count)

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "entry.line_budget_warning" in result.stderr
    assert relative_path.as_posix() in result.stderr


@pytest.mark.parametrize(("relative_path", "line_count"), HARD_BUDGETS)
def test_line_budget_fails_after_hard_limit(tmp_path: Path, relative_path: Path, line_count: int) -> None:
    _project(tmp_path)
    _pad_to_lines(tmp_path, relative_path, line_count)

    _assert_error(tmp_path, "entry.line_budget_exceeded")


@pytest.mark.parametrize("field", FOCUS_FIELDS)
def test_missing_focus_card_field_fails(tmp_path: Path, field: str) -> None:
    _project(tmp_path)
    if field == TRIGGERED_POLICIES_FIELD:
        value = "none: fixture documentation rationale"
    elif field == SEAM_CLASSIFICATION_FIELD:
        value = "deterministic-guardrail — fixture rationale"
    else:
        value = "fixture"
    _replace(tmp_path, "openspec/changes/change-one/proposal.md", f"- **{field}:** {value}\n", "")

    _assert_error(tmp_path, "focus.field_missing")


@pytest.mark.parametrize(
    "seam_value",
    (
        "cognitive",
        "Cognitive-program",
        "runtime-gate",
        "`deterministic-guardrail`",
        "deterministic-guardrail, wiring",
    ),
)
def test_seam_classification_rejects_each_invalid_value(tmp_path: Path, seam_value: str) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(seam_classification=seam_value),
    )

    _assert_error(tmp_path, "focus.seam_classification_invalid")


def test_seam_classification_requires_a_rationale(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card().replace(
            "- **Seam classification:** deterministic-guardrail — fixture rationale",
            "- **Seam classification:** deterministic-guardrail",
        ),
    )

    _assert_error(tmp_path, "focus.seam_classification_rationale_missing")


@pytest.mark.parametrize("seam_value", SEAM_CLASSIFICATIONS)
def test_seam_classification_accepts_each_closed_value(tmp_path: Path, seam_value: str) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(seam_classification=seam_value),
    )

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr


def test_none_triggered_policy_requires_a_rationale(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        "none: fixture documentation rationale",
        "none",
    )

    _assert_error(tmp_path, "focus.triggered_policies_rationale_missing")


def test_legacy_triggered_policy_field_fails_closed(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        TRIGGERED_POLICIES_FIELD,
        LEGACY_TRIGGERED_POLICIES_FIELD,
    )

    _assert_error(tmp_path, "focus.legacy_triggered_policies_field_present")


def test_triggered_policy_continuation_line_fails_closed(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        "none: fixture documentation rationale",
        f"{CONTROL_PLACEMENT_POLICY},\n  {WORKFLOW_OUTCOME_POLICY}",
    )

    _assert_error(tmp_path, "focus.triggered_policies_continuation_invalid")


def test_unknown_triggered_policy_fails_closed(tmp_path: Path) -> None:
    _project(tmp_path)
    _replace(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        "none: fixture documentation rationale",
        "unregistered-policy",
    )

    _assert_error(tmp_path, "focus.triggered_policy_unknown")


def test_selected_cross_cutting_policy_requires_an_available_document(tmp_path: Path) -> None:
    _project(tmp_path)
    (tmp_path / POLICY_PATHS[CONTROL_PLACEMENT_POLICY]).unlink()
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(
            triggered_policies=CONTROL_PLACEMENT_POLICY,
            include_control_placement_review=True,
        ),
    )

    _assert_error(tmp_path, "guidance.policy_members_mismatch")


def test_selected_cross_cutting_policy_with_a_complete_review_record_passes(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(
            triggered_policies=CONTROL_PLACEMENT_POLICY,
            include_control_placement_review=True,
        ),
    )

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr


def test_workflow_outcome_policy_requires_its_review_record(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(triggered_policies=WORKFLOW_OUTCOME_POLICY),
    )

    _assert_error(tmp_path, "focus.workflow_outcome_review_missing")


def test_workflow_outcome_review_requires_a_complete_table(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(
            triggered_policies=WORKFLOW_OUTCOME_POLICY,
            include_workflow_outcome_review=True,
        ).replace("fixture test", ""),
    )

    _assert_error(tmp_path, "focus.workflow_outcome_review_shape_invalid")


def test_workflow_outcome_policy_with_a_complete_review_record_passes(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(
            triggered_policies=WORKFLOW_OUTCOME_POLICY,
            include_workflow_outcome_review=True,
        ),
    )

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr


def test_node_agent_workflow_policy_requires_its_review_record(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(triggered_policies=NODE_AGENT_WORKFLOW_INTEGRITY_POLICY),
    )

    _assert_error(tmp_path, "focus.node_agent_review_missing")


@pytest.mark.parametrize(
    "replacement",
    (
        "| Surface | Classification | Bounded question | Input authority boundary | "
        "Tool posture and runtime enforcer | Candidate result and deterministic admission owner | "
        "Failure owner and bound | Deterministic evidence seam |",
        "fixture runtime policy | typed fixture candidate and parser | fixture owner with one bound |  |",
    ),
)
def test_node_agent_review_requires_an_exact_complete_table(tmp_path: Path, replacement: str) -> None:
    _project(tmp_path)
    proposal = _focus_card(
        triggered_policies=NODE_AGENT_WORKFLOW_INTEGRITY_POLICY,
        include_node_agent_review=True,
    )
    target = (
        "| Surface | Classification | Bounded cognitive question or no-agent rationale | "
        "Input authority boundary | Tool posture and runtime enforcer | "
        "Candidate result and deterministic admission owner | Failure owner and bound | "
        "Deterministic evidence seam |"
        if replacement.startswith("| Surface")
        else (
            "fixture runtime policy | typed fixture candidate and parser | "
            "fixture owner with one bound | fixture test |"
        )
    )
    _write(tmp_path, "openspec/changes/change-one/proposal.md", proposal.replace(target, replacement))

    _assert_error(tmp_path, "focus.node_agent_review_shape_invalid")


def test_node_agent_review_rejects_an_unknown_classification(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(
            triggered_policies=NODE_AGENT_WORKFLOW_INTEGRITY_POLICY,
            include_node_agent_review=True,
            node_agent_classification="agentish",
        ),
    )

    _assert_error(tmp_path, "focus.node_agent_review_classification_invalid")


@pytest.mark.parametrize("classification", ("node-agent", "no-agent"))
def test_node_agent_policy_accepts_each_closed_classification(tmp_path: Path, classification: str) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(
            triggered_policies=NODE_AGENT_WORKFLOW_INTEGRITY_POLICY,
            include_node_agent_review=True,
            node_agent_classification=classification,
        ),
    )

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr


def test_control_placement_policy_requires_exactly_one_review_heading(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(triggered_policies=CONTROL_PLACEMENT_POLICY),
    )

    _assert_error(tmp_path, "focus.control_placement_review_missing")

    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(
            triggered_policies=CONTROL_PLACEMENT_POLICY,
            include_control_placement_review=True,
        )
        + _control_placement_review_record(),
    )

    _assert_error(tmp_path, "focus.control_placement_review_missing")


def test_control_placement_review_requires_exactly_one_table(tmp_path: Path) -> None:
    _project(tmp_path)
    duplicate_table = _control_placement_review_record().replace(f"{CONTROL_PLACEMENT_REVIEW_HEADING}\n\n", "")
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(
            triggered_policies=CONTROL_PLACEMENT_POLICY,
            include_control_placement_review=True,
        )
        + duplicate_table,
    )

    _assert_error(tmp_path, "focus.control_placement_review_shape_invalid")


@pytest.mark.parametrize(
    "replacement",
    (
        "| Changed decision or fact | Candidate | Direct fact and deterministic owner/evaluator | "
        "Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | "
        "Deterministic evidence seam |",
        "| --- | --- | --- | --- | --- | invalid |",
        "| fixture decision | fixture candidate | fixture fact and owner | advisory | fixture invariant | "
        "fixture reuse |  |",
    ),
)
def test_control_placement_review_requires_an_exact_complete_table(tmp_path: Path, replacement: str) -> None:
    _project(tmp_path)
    proposal = _focus_card(
        triggered_policies=CONTROL_PLACEMENT_POLICY,
        include_control_placement_review=True,
    )
    if replacement.startswith("| Changed"):
        target = "| " + " | ".join(CONTROL_PLACEMENT_REVIEW_COLUMNS) + " |"
    elif replacement.startswith("| ---"):
        target = "| --- | --- | --- | --- | --- | --- | --- |"
    else:
        target = (
            "| fixture decision | fixture candidate | fixture fact and owner | advisory | fixture invariant | "
            "fixture reuse | fixture test |"
        )
    _write(tmp_path, "openspec/changes/change-one/proposal.md", proposal.replace(target, replacement))

    _assert_error(tmp_path, "focus.control_placement_review_shape_invalid")


def test_control_placement_review_requires_at_least_one_row(tmp_path: Path) -> None:
    _project(tmp_path)
    proposal = _focus_card(
        triggered_policies=CONTROL_PLACEMENT_POLICY,
        include_control_placement_review=True,
    )
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        proposal.replace(
            "| fixture decision | fixture candidate | fixture fact and owner | advisory | fixture invariant | "
            "fixture reuse | fixture test |\n",
            "",
        ),
    )

    _assert_error(tmp_path, "focus.control_placement_review_shape_invalid")


@pytest.mark.parametrize("posture", ("open-ended", "Advisory", "runtime-gate", ""))
def test_control_placement_review_rejects_each_invalid_posture(tmp_path: Path, posture: str) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(
            triggered_policies=CONTROL_PLACEMENT_POLICY,
            include_control_placement_review=True,
            control_placement_posture=posture,
        ),
    )

    expected_code = (
        "focus.control_placement_review_shape_invalid"
        if not posture
        else "focus.control_placement_review_posture_invalid"
    )
    _assert_error(tmp_path, expected_code)


@pytest.mark.parametrize("posture", CONTROL_PLACEMENT_POSTURES)
def test_control_placement_policy_accepts_each_closed_posture(tmp_path: Path, posture: str) -> None:
    _project(tmp_path)
    policies = CONTROL_PLACEMENT_POLICY
    if posture == "human-decision":
        policies = f"{policies}, human-interaction-integrity"
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(
            triggered_policies=policies,
            include_control_placement_review=True,
            control_placement_posture=posture,
        ),
    )

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr


def test_human_decision_control_placement_requires_interaction_integrity(tmp_path: Path) -> None:
    _project(tmp_path)
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(
            triggered_policies=CONTROL_PLACEMENT_POLICY,
            include_control_placement_review=True,
            control_placement_posture="human-decision",
        ),
    )

    _assert_error(tmp_path, "focus.control_placement_human_interaction_policy_missing")


def test_node_agent_and_workflow_outcome_reviews_remain_independent(tmp_path: Path) -> None:
    _project(tmp_path)
    policies = f"{NODE_AGENT_WORKFLOW_INTEGRITY_POLICY}, {WORKFLOW_OUTCOME_POLICY}"
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(
            triggered_policies=policies,
            include_node_agent_review=True,
        ),
    )

    _assert_error(tmp_path, "focus.workflow_outcome_review_missing")

    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(
            triggered_policies=policies,
            include_node_agent_review=True,
            include_workflow_outcome_review=True,
        ),
    )

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr


def test_control_placement_and_existing_reviews_remain_independent(tmp_path: Path) -> None:
    _project(tmp_path)
    policies = ", ".join(
        (
            CONTROL_PLACEMENT_POLICY,
            NODE_AGENT_WORKFLOW_INTEGRITY_POLICY,
            WORKFLOW_OUTCOME_POLICY,
        )
    )
    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(
            triggered_policies=policies,
            include_control_placement_review=True,
        ),
    )

    _assert_error(tmp_path, "focus.node_agent_review_missing")

    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(
            triggered_policies=policies,
            include_control_placement_review=True,
            include_node_agent_review=True,
        ),
    )

    _assert_error(tmp_path, "focus.workflow_outcome_review_missing")

    _write(
        tmp_path,
        "openspec/changes/change-one/proposal.md",
        _focus_card(
            triggered_policies=policies,
            include_control_placement_review=True,
            include_node_agent_review=True,
            include_workflow_outcome_review=True,
        ),
    )

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr


def test_active_change_without_proposal_does_not_pass_by_skipping_scan(tmp_path: Path) -> None:
    _project(tmp_path)
    (tmp_path / "openspec/changes/change-one/proposal.md").unlink()

    _assert_error(tmp_path, "focus.proposal_missing")


def test_no_active_changes_is_valid_after_charter_archive(tmp_path: Path) -> None:
    _project(tmp_path)
    for path in (tmp_path / "openspec/changes/change-one").iterdir():
        path.unlink()
    (tmp_path / "openspec/changes/change-one").rmdir()

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
