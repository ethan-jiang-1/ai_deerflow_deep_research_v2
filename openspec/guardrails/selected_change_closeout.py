"""Bounded, local evidence for one selected OpenSpec change.

This command verifies only caller-declared committed Git ranges. It is not an
OpenSpec hook and does not assess review quality or archive readiness.

@impl SCC-001
@impl SCC-002
@impl SCC-003
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "selected-change-closeout/v1"
REQUIRED_ATTESTATION_FIELDS = (
    "change_name",
    "repository_identity",
    "base_commit",
    "head_commit",
)


@dataclass(frozen=True)
class Attestation:
    change_name: str
    repository_identity: str
    base_commit: str
    head_commit: str


def _result(result: str, condition: str) -> dict[str, str]:
    return {
        "schema_version": SCHEMA_VERSION,
        "result": result,
        "condition": condition,
    }


def _read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _parse_attestation(value: Any) -> Attestation | None:
    if not isinstance(value, dict):
        return None
    fields = []
    for field in REQUIRED_ATTESTATION_FIELDS:
        field_value = value.get(field)
        if not isinstance(field_value, str) or not field_value.strip():
            return None
        fields.append(field_value)
    return Attestation(*fields)


def _planning_home(start: Path) -> Path | None:
    for candidate in (start, *start.parents):
        if (candidate / "openspec/changes").is_dir():
            return candidate
    return None


def _active_change_root(change_name: str) -> Path | None:
    if Path(change_name).name != change_name or change_name in {"", ".", ".."}:
        return None
    planning_home = _planning_home(Path.cwd().resolve())
    if planning_home is None:
        return None
    change_root = planning_home / "openspec/changes" / change_name
    return change_root.resolve() if change_root.is_dir() else None


def _git(repository: Path, *arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=False,
        capture_output=True,
    )


def _git_stdout(repository: Path, *arguments: str) -> bytes | None:
    result = _git(repository, *arguments)
    return result.stdout if result.returncode == 0 else None


def _resolved_commit(repository: Path, commit: str) -> str | None:
    output = _git_stdout(repository, "rev-parse", "--verify", f"{commit}^{{commit}}")
    return output.decode("ascii").strip() if output is not None else None


def _verify_boundary(attestation: Attestation) -> tuple[dict[str, object], Path | None]:
    change_root = _active_change_root(attestation.change_name)
    if change_root is None:
        return _result("missing-boundary", "unknown-change"), None

    declared_repository = Path(attestation.repository_identity)
    if not declared_repository.is_absolute():
        return _result("missing-boundary", "repository-mismatch"), None
    current_repository = _git_stdout(Path.cwd(), "rev-parse", "--show-toplevel")
    attested_repository = _git_stdout(declared_repository, "rev-parse", "--show-toplevel")
    if current_repository is None or attested_repository is None:
        return _result("missing-boundary", "repository-mismatch"), None
    canonical_declared = declared_repository.resolve()
    canonical_current = Path(current_repository.decode("utf-8").strip()).resolve()
    canonical_attested = Path(attested_repository.decode("utf-8").strip()).resolve()
    if canonical_declared != canonical_current or canonical_declared != canonical_attested:
        return _result("missing-boundary", "repository-mismatch"), None

    base_commit = _resolved_commit(canonical_declared, attestation.base_commit)
    head_commit = _resolved_commit(canonical_declared, attestation.head_commit)
    if base_commit is None or head_commit is None:
        return _result("missing-boundary", "unknown-commit"), None
    ancestry = _git(canonical_declared, "merge-base", "--is-ancestor", base_commit, head_commit)
    if ancestry.returncode != 0:
        return _result("missing-boundary", "non-ancestor"), None
    current_head = _resolved_commit(canonical_declared, "HEAD")
    if current_head != head_commit:
        return _result("missing-boundary", "head-drift"), None
    worktree_status = _git_stdout(canonical_declared, "status", "--porcelain")
    if worktree_status is None or worktree_status:
        return _result("missing-boundary", "dirty-worktree"), None
    diff = _git_stdout(canonical_declared, "diff", "--binary", base_commit, head_commit)
    changed_paths = _git_stdout(canonical_declared, "diff", "--name-only", "-z", base_commit, head_commit)
    if diff is None or changed_paths is None:
        return _result("missing-boundary", "unknown-commit"), None
    return (
        {
            "schema_version": SCHEMA_VERSION,
            "result": "boundary-verified",
            "change_name": attestation.change_name,
            "repository_identity": str(canonical_declared),
            "base_commit": base_commit,
            "head_commit": head_commit,
            "range": f"{base_commit}..{head_commit}",
            "diff_summary": {
                "changed_path_count": len([path for path in changed_paths.split(b"\0") if path]),
                "sha256": hashlib.sha256(diff).hexdigest(),
            },
        },
        change_root,
    )


UNCHECKED_TASK_LINE = re.compile(r"^\s*(?:[-*+])\s+\[ \]\s+(.+?)\s*$")


def _unchecked_task_labels(change_root: Path) -> set[str]:
    tasks_path = change_root / "tasks.md"
    try:
        task_lines = tasks_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return set()
    return {
        match.group(1).strip()
        for line in task_lines
        if (match := UNCHECKED_TASK_LINE.match(line)) and match.group(1).strip()
    }


def _validate_review(review: Any, change_root: Path, output: Path) -> tuple[dict[str, object] | None, dict[str, str] | None]:
    evidence_root = change_root / "guardrail-evidence"
    if not output.is_relative_to(evidence_root):
        return None, _result("invalid-review", "output-path-outside-evidence")
    if not isinstance(review, dict):
        return None, _result("invalid-review", "missing-review-payload")
    disposition = review.get("disposition")
    if disposition not in {"review-required", "inconclusive"}:
        return None, _result("invalid-review", "unsupported-disposition")
    if disposition == "review-required":
        references = review.get("task_references")
        if not isinstance(references, list) or not references or not all(
            isinstance(reference, str) and reference.strip() for reference in references
        ):
            return None, _result("invalid-review", "missing-task-reference")
        if not set(references).issubset(_unchecked_task_labels(change_root)):
            return None, _result("invalid-review", "unknown-unchecked-task")
        return {"disposition": disposition, "task_references": references}, None
    limitation = review.get("evidence_limitation")
    if not isinstance(limitation, str) or not limitation.strip():
        return None, _result("invalid-review", "missing-evidence-limitation")
    return {"disposition": disposition, "evidence_limitation": limitation}, None


def _print(record: dict[str, object]) -> None:
    print(json.dumps(record, sort_keys=True))


def _verify_boundary_command(attestation_path: Path) -> int:
    attestation = _parse_attestation(_read_json(attestation_path))
    if attestation is None:
        _print(_result("missing-boundary", "missing-field"))
        return 0
    receipt, _ = _verify_boundary(attestation)
    _print(receipt)
    return 0


def _record_review_command(attestation_path: Path, review_path: Path, output_argument: Path) -> int:
    attestation = _parse_attestation(_read_json(attestation_path))
    if attestation is None:
        _print(_result("missing-boundary", "missing-field"))
        return 0
    change_root = _active_change_root(attestation.change_name)
    if change_root is None:
        _print(_result("missing-boundary", "unknown-change"))
        return 0
    output = output_argument.resolve()
    review, invalid_review = _validate_review(_read_json(review_path), change_root, output)
    if invalid_review is not None:
        _print(invalid_review)
        return 0

    boundary, verified_change_root = _verify_boundary(attestation)
    if boundary["result"] != "boundary-verified" or verified_change_root is None:
        _print(boundary)
        return 0
    record = {"schema_version": SCHEMA_VERSION, "result": "review-recorded", "boundary": boundary, **review}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
    _print(record)
    return 0


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    verify = commands.add_parser("verify-boundary")
    verify.add_argument("--attestation", type=Path, required=True)
    record = commands.add_parser("record-review")
    record.add_argument("--attestation", type=Path, required=True)
    record.add_argument("--review", type=Path, required=True)
    record.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    arguments = _arguments()
    if arguments.operation == "verify-boundary":
        return _verify_boundary_command(arguments.attestation)
    return _record_review_command(arguments.attestation, arguments.review, arguments.output)


if __name__ == "__main__":
    raise SystemExit(main())
