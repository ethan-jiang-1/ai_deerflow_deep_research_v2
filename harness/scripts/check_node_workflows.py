#!/usr/bin/env python3
"""Validate non-runtime node-local workflow reader projections.

@impl CNI-005
"""

from __future__ import annotations

import argparse
import ast
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


def logical_nodes(repo_root: Path) -> tuple[str, ...]:
    tree = ast.parse((repo_root / TOPOLOGY_PATH).read_text(encoding="utf-8"), filename=str(TOPOLOGY_PATH))
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "LOGICAL_NODES" for target in statement.targets
        ):
            value = ast.literal_eval(statement.value)
            if not isinstance(value, tuple) or not all(isinstance(node, str) for node in value):
                break
            return value
    raise WorkflowReaderError("topology_logical_nodes_missing")


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
        records.append(load_reader_identity(node, path.read_text(encoding="utf-8")))
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
