#!/usr/bin/env python3
"""Validate non-runtime node-local workflow reader projections.

@impl CNI-005
@impl NRI-004
"""

from __future__ import annotations

import argparse
import ast
import re
from dataclasses import dataclass
from pathlib import Path

NODE_ROOT = Path("deep_research_harness/src/deerflow_deep_research/graph/nodes")
TOPOLOGY_PATH = Path("deep_research_harness/src/deerflow_deep_research/graph/topology.py")
REQUIRED_FIELDS = (
    "Participation mode",
    "Commitment state",
    "Current operating mechanism",
    "Primary cognitive/control program surface",
    "Deterministic authority boundary",
    "Current model-branch evidence",
)
REQUIRED_HEADINGS = (
    "Node Identity",
    "From Symptoms",
    "Three Cross-Module Facts",
    "Route Facts",
    "Evaluation and Verification Order",
)
AUTHORITY_NOTICE = "Reader interface only. This file is not a runtime resource or configuration."
LLM_NODE_PARTICIPATION_MODE = "bounded cognitive program"
LLM_NODE_ROUTE_HEADING = "LLM-Node Authoring Route"
LLM_NODE_ROUTE_STEPS = (
    "Capability and contract",
    "Prompt and context",
    "Feedback and repair",
    "Proof and evaluation",
    "Deterministic handoff",
)
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\((?P<target>[^)]+)\)")


class WorkflowReaderError(ValueError):
    pass


@dataclass(frozen=True)
class WorkflowIdentityRecord:
    """Validated non-runtime identity fields projected from one reader card."""

    node: str
    product_responsibility: str
    participation_mode: str
    commitment_state: str
    current_operating_mechanism: str
    primary_program_surface: str
    deterministic_authority_boundary: str
    current_model_branch_evidence: str


def _section_after_heading(text: str, heading: str) -> str | None:
    match = re.search(rf"^## {re.escape(heading)}\s*$", text, flags=re.MULTILINE)
    if match is None:
        return None
    next_heading = re.search(r"^## (?!#)", text[match.end() :], flags=re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(text)
    return text[match.end() : end]


def _llm_node_route_step_lines(node: str, text: str) -> tuple[str, ...]:
    if f"> Participation mode: {LLM_NODE_PARTICIPATION_MODE}" not in text:
        return ()
    route = _section_after_heading(text, LLM_NODE_ROUTE_HEADING)
    if route is None:
        raise WorkflowReaderError(f"{node}: llm_authoring_route_heading_missing")

    lines: list[str] = []
    positions: list[int] = []
    for step in LLM_NODE_ROUTE_STEPS:
        match = re.search(
            rf"^\d+\. \*\*{re.escape(step)}:\*\* (?P<detail>.+)$",
            route,
            flags=re.MULTILINE,
        )
        if match is None:
            raise WorkflowReaderError(f"{node}: llm_authoring_route_step_missing:{step}")
        if MARKDOWN_LINK.search(match.group("detail")) is None:
            raise WorkflowReaderError(f"{node}: llm_authoring_route_link_missing:{step}")
        positions.append(match.start())
        lines.append(match.group("detail"))
    if positions != sorted(positions):
        raise WorkflowReaderError(f"{node}: llm_authoring_route_order_invalid")
    return tuple(lines)


def _validate_llm_node_route_links(repo_root: Path, node: str, text: str, path: Path) -> None:
    for detail in _llm_node_route_step_lines(node, text):
        for match in MARKDOWN_LINK.finditer(detail):
            target = match.group("target").split("#", 1)[0]
            if not target or target.startswith(("/", "http://", "https://")):
                raise WorkflowReaderError(f"{node}: llm_authoring_route_link_target_invalid:{target}")
            target_path = (path.parent / target).resolve()
            try:
                target_path.relative_to(repo_root)
            except ValueError as exc:
                raise WorkflowReaderError(f"{node}: llm_authoring_route_link_target_invalid:{target}") from exc
            if not target_path.is_file():
                raise WorkflowReaderError(f"{node}: llm_authoring_route_link_target_missing:{target}")


def logical_nodes(repo_root: Path) -> tuple[str, ...]:
    tree = ast.parse((repo_root / TOPOLOGY_PATH).read_text(encoding="utf-8"), filename=str(TOPOLOGY_PATH))
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "LOGICAL_NODES" for target in statement.targets
        ):
            try:
                value = ast.literal_eval(statement.value)
            except (ValueError, SyntaxError):
                break
            if isinstance(value, tuple) and all(isinstance(node, str) for node in value):
                return value
            break
    # ``LOGICAL_NODES`` is a re-export of the single-source phase list
    # (``domain.identifiers.LOGICAL_PHASE_NAMES``), so the AST literal form is
    # gone; resolve the live value from the same source the graph uses.
    from deerflow_deep_research.graph.topology import LOGICAL_NODES as live_nodes

    return tuple(live_nodes)


def validate_reader_text(node: str, text: str) -> None:
    lines = text.splitlines()
    title = next((line for line in lines if line.startswith("# ")), "")
    if not title.startswith(f"# {node} — ") or not title.removeprefix(f"# {node} — ").strip():
        raise WorkflowReaderError(f"{node}: title_product_responsibility_invalid")
    if AUTHORITY_NOTICE not in text:
        raise WorkflowReaderError(f"{node}: authority_notice_missing")

    positions: list[int] = []
    for field in REQUIRED_FIELDS:
        marker = f"> {field}:"
        try:
            positions.append(lines.index(next(line for line in lines if line.startswith(marker))))
        except StopIteration as exc:
            raise WorkflowReaderError(f"{node}: field_missing:{field}") from exc
    if positions != sorted(positions):
        raise WorkflowReaderError(f"{node}: identity_field_order_invalid")
    if any("node-agent" in line or "no-agent" in line for line in lines[: positions[0]]):
        raise WorkflowReaderError(f"{node}: charter_identity_forbidden")

    heading_positions: list[int] = []
    for heading in REQUIRED_HEADINGS:
        marker = f"## {heading}"
        try:
            heading_positions.append(lines.index(marker))
        except ValueError as exc:
            raise WorkflowReaderError(f"{node}: heading_missing:{heading}") from exc
    if heading_positions != sorted(heading_positions):
        raise WorkflowReaderError(f"{node}: heading_order_invalid")
    _llm_node_route_step_lines(node, text)


def load_reader_identity(node: str, text: str) -> WorkflowIdentityRecord:
    """Load identity fields only after the existing reader shape gate passes."""

    validate_reader_text(node, text)
    lines = text.splitlines()
    title = next(line for line in lines if line.startswith(f"# {node} — "))
    values = {
        field: next(line for line in lines if line.startswith(f"> {field}:")).split(":", 1)[1].strip()
        for field in REQUIRED_FIELDS
    }
    if any(not value for value in values.values()):
        raise WorkflowReaderError(f"{node}: identity_field_value_missing")
    return WorkflowIdentityRecord(
        node=node,
        product_responsibility=title.removeprefix(f"# {node} — ").strip(),
        participation_mode=values["Participation mode"],
        commitment_state=values["Commitment state"],
        current_operating_mechanism=values["Current operating mechanism"],
        primary_program_surface=values["Primary cognitive/control program surface"],
        deterministic_authority_boundary=values["Deterministic authority boundary"],
        current_model_branch_evidence=values["Current model-branch evidence"],
    )


def load_reader_inventory(repo_root: Path) -> tuple[WorkflowIdentityRecord, ...]:
    records: list[WorkflowIdentityRecord] = []
    for node in logical_nodes(repo_root):
        path = repo_root / NODE_ROOT / node / "workflow.md"
        if not path.is_file():
            raise WorkflowReaderError(f"{node}: workflow_missing")
        text = path.read_text(encoding="utf-8")
        records.append(load_reader_identity(node, text))
        _validate_llm_node_route_links(repo_root, node, text, path)
    return tuple(records)


def validate_reader_inventory(repo_root: Path) -> None:
    load_reader_inventory(repo_root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    try:
        validate_reader_inventory(args.root.resolve())
    except (OSError, SyntaxError, ValueError, WorkflowReaderError) as exc:
        print(f"node workflow reader check failed: {exc}")
        return 1
    print("node workflow reader check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
