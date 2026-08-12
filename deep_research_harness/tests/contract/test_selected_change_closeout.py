"""Deterministic contracts for selected-change closeout evidence.

@impl SCC-001
@impl SCC-002
@impl SCC-003
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
COMMAND = REPO_ROOT / "openspec/guardrails/selected_change_closeout.py"
CHANGE_NAME = "active-change"
TASK_LABEL = "Implement follow-up"


def _git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _write_json(path: Path, content: dict[str, object]) -> Path:
    path.write_text(json.dumps(content), encoding="utf-8")
    return path


def _project(tmp_path: Path) -> tuple[Path, str, str]:
    root = tmp_path / "project"
    change_root = root / "openspec/changes" / CHANGE_NAME
    change_root.mkdir(parents=True)
    (change_root / "tasks.md").write_text(
        "## Tasks\n\n- [ ] Implement follow-up\n- [x] Completed work\n",
        encoding="utf-8",
    )
    (root / "subject.txt").write_text("base\n", encoding="utf-8")
    _git(root, "init")
    _git(root, "config", "user.email", "closeout@example.test")
    _git(root, "config", "user.name", "Closeout Fixture")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "base")
    base_commit = _git(root, "rev-parse", "HEAD")
    (root / "subject.txt").write_text("head\n", encoding="utf-8")
    _git(root, "add", "subject.txt")
    _git(root, "commit", "-m", "head")
    head_commit = _git(root, "rev-parse", "HEAD")
    return root, base_commit, head_commit


def _attestation(root: Path, base_commit: str, head_commit: str) -> dict[str, str]:
    return {
        "change_name": CHANGE_NAME,
        "repository_identity": str(root.resolve()),
        "base_commit": base_commit,
        "head_commit": head_commit,
    }


def _run(
    root: Path,
    operation: str,
    attestation: dict[str, object],
    *,
    review: dict[str, object] | None = None,
    output: Path | None = None,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    input_root = root.parent / "command-inputs"
    input_root.mkdir(exist_ok=True)
    attestation_path = _write_json(input_root / "attestation.json", attestation)
    arguments = [sys.executable, str(COMMAND), operation, "--attestation", str(attestation_path)]
    if review is not None:
        review_path = _write_json(input_root / "review.json", review)
        arguments.extend(["--review", str(review_path)])
    if output is not None:
        arguments.extend(["--output", str(output)])
    return subprocess.run(
        arguments,
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )


def _receipt(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_verify_boundary_emits_exact_committed_range_summary(tmp_path: Path) -> None:
    root, base_commit, head_commit = _project(tmp_path)

    receipt = _receipt(_run(root, "verify-boundary", _attestation(root, base_commit, head_commit)))

    exact_diff = subprocess.run(
        ["git", "diff", "--binary", base_commit, head_commit],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout
    changed_paths = _git(root, "diff", "--name-only", "-z", base_commit, head_commit).split("\0")
    assert receipt == {
        "schema_version": "selected-change-closeout/v1",
        "result": "boundary-verified",
        "change_name": CHANGE_NAME,
        "repository_identity": str(root.resolve()),
        "base_commit": base_commit,
        "head_commit": head_commit,
        "range": f"{base_commit}..{head_commit}",
        "diff_summary": {
            "changed_path_count": len([path for path in changed_paths if path]),
            "sha256": hashlib.sha256(exact_diff).hexdigest(),
        },
    }
    assert not (root / "openspec/changes" / CHANGE_NAME / "guardrail-evidence").exists()


@pytest.mark.parametrize(
    ("case", "condition"),
    (
        ("unknown-change", "unknown-change"),
        ("missing-field", "missing-field"),
        ("repository-mismatch", "repository-mismatch"),
        ("unknown-commit", "unknown-commit"),
        ("non-ancestor", "non-ancestor"),
        ("head-drift", "head-drift"),
        ("dirty-worktree", "dirty-worktree"),
    ),
)
def test_verify_boundary_rejects_each_closed_invalid_condition(tmp_path: Path, case: str, condition: str) -> None:
    root, base_commit, head_commit = _project(tmp_path)
    attestation: dict[str, object] = _attestation(root, base_commit, head_commit)

    if case == "unknown-change":
        attestation["change_name"] = "missing-change"
    elif case == "missing-field":
        del attestation["base_commit"]
    elif case == "repository-mismatch":
        attestation["repository_identity"] = str(root / "different-repository")
    elif case == "unknown-commit":
        attestation["head_commit"] = "0" * 40
    elif case == "non-ancestor":
        _git(root, "checkout", "-b", "side", base_commit)
        (root / "side.txt").write_text("side\n", encoding="utf-8")
        _git(root, "add", "side.txt")
        _git(root, "commit", "-m", "side")
        side_commit = _git(root, "rev-parse", "HEAD")
        _git(root, "checkout", "-")
        attestation["base_commit"] = side_commit
    elif case == "head-drift":
        (root / "later.txt").write_text("later\n", encoding="utf-8")
        _git(root, "add", "later.txt")
        _git(root, "commit", "-m", "later")
    elif case == "dirty-worktree":
        (root / "uncommitted.txt").write_text("dirty\n", encoding="utf-8")

    receipt = _receipt(_run(root, "verify-boundary", attestation))

    assert receipt == {
        "schema_version": "selected-change-closeout/v1",
        "result": "missing-boundary",
        "condition": condition,
    }


def test_record_review_requires_task_led_findings_or_a_stated_limitation(tmp_path: Path) -> None:
    root, base_commit, head_commit = _project(tmp_path)
    attestation = _attestation(root, base_commit, head_commit)
    tasks_path = root / "openspec/changes" / CHANGE_NAME / "tasks.md"
    original_tasks = tasks_path.read_text(encoding="utf-8")
    output = root / "openspec/changes" / CHANGE_NAME / "guardrail-evidence/review-required.json"

    receipt = _receipt(
        _run(
            root,
            "record-review",
            attestation,
            review={"disposition": "review-required", "task_references": [TASK_LABEL]},
            output=output,
        )
    )

    assert receipt["schema_version"] == "selected-change-closeout/v1"
    assert receipt["disposition"] == "review-required"
    assert receipt["task_references"] == [TASK_LABEL]
    assert receipt["boundary"]["result"] == "boundary-verified"
    assert json.loads(output.read_text(encoding="utf-8")) == receipt
    assert tasks_path.read_text(encoding="utf-8") == original_tasks


@pytest.mark.parametrize(
    ("review", "condition"),
    (
        ({"disposition": "clear", "task_references": [TASK_LABEL]}, "unsupported-disposition"),
        ({"disposition": "review-required", "task_references": ["Completed work"]}, "unknown-unchecked-task"),
        ({"disposition": "inconclusive", "evidence_limitation": ""}, "missing-evidence-limitation"),
    ),
)
def test_record_review_rejects_semantic_or_incomplete_payloads(
    tmp_path: Path, review: dict[str, object], condition: str
) -> None:
    root, base_commit, head_commit = _project(tmp_path)
    attestation = _attestation(root, base_commit, head_commit)
    tasks_path = root / "openspec/changes" / CHANGE_NAME / "tasks.md"
    original_tasks = tasks_path.read_text(encoding="utf-8")
    rejected_output = root / "openspec/changes" / CHANGE_NAME / "guardrail-evidence" / f"{condition}.json"

    rejected = _receipt(_run(root, "record-review", attestation, review=review, output=rejected_output))

    assert rejected == {
        "schema_version": "selected-change-closeout/v1",
        "result": "invalid-review",
        "condition": condition,
    }
    assert not rejected_output.exists()
    assert tasks_path.read_text(encoding="utf-8") == original_tasks


def test_record_review_rejects_escaping_paths_and_rechecks_before_write(tmp_path: Path) -> None:
    root, base_commit, head_commit = _project(tmp_path)
    attestation = _attestation(root, base_commit, head_commit)
    review = {"disposition": "inconclusive", "evidence_limitation": "No independent reviewer was available."}
    outside_output = root.parent / "outside-closeout.json"

    escaped = _receipt(_run(root, "record-review", attestation, review=review, output=outside_output))
    assert escaped == {
        "schema_version": "selected-change-closeout/v1",
        "result": "invalid-review",
        "condition": "output-path-outside-evidence",
    }
    assert not outside_output.exists()

    # A path under the change root but outside guardrail-evidence/ (e.g. a change
    # artifact such as tasks.md) must not become the review-record write target.
    tasks_path = root / "openspec/changes" / CHANGE_NAME / "tasks.md"
    original_tasks = tasks_path.read_text(encoding="utf-8")
    overwrite = _receipt(_run(root, "record-review", attestation, review=review, output=tasks_path))
    assert overwrite == {
        "schema_version": "selected-change-closeout/v1",
        "result": "invalid-review",
        "condition": "output-path-outside-evidence",
    }
    assert tasks_path.read_text(encoding="utf-8") == original_tasks

    _receipt(_run(root, "verify-boundary", attestation))
    (root / "state-changed-after-receipt.txt").write_text("dirty\n", encoding="utf-8")
    record_output = root / "openspec/changes" / CHANGE_NAME / "guardrail-evidence/stale.json"
    stale = _receipt(_run(root, "record-review", attestation, review=review, output=record_output))
    assert stale == {
        "schema_version": "selected-change-closeout/v1",
        "result": "missing-boundary",
        "condition": "dirty-worktree",
    }
    assert not record_output.exists()


def test_record_review_ignores_prose_containing_checkbox_marker(tmp_path: Path) -> None:
    root, base_commit, head_commit = _project(tmp_path)
    tasks_path = root / "openspec/changes" / CHANGE_NAME / "tasks.md"
    tasks_path.write_text(
        "## Tasks\n\n- [ ] Real work item\n\n"
        "Prose that mentions the `- [ ]` marker is not a task.\n",
        encoding="utf-8",
    )
    attestation = _attestation(root, base_commit, head_commit)
    output = root / "openspec/changes" / CHANGE_NAME / "guardrail-evidence/review.json"

    # The old parser would have extracted "marker is not a task." from the prose
    # line; the anchored parser ignores it, so referencing it is not a valid task.
    rejected = _receipt(
        _run(
            root,
            "record-review",
            attestation,
            review={"disposition": "review-required", "task_references": ["marker is not a task."]},
            output=output,
        )
    )
    assert rejected == {
        "schema_version": "selected-change-closeout/v1",
        "result": "invalid-review",
        "condition": "unknown-unchecked-task",
    }
    assert not output.exists()


def test_invalid_attestations_do_not_run_git_or_native_archive_or_touch_tasks(tmp_path: Path) -> None:
    root, base_commit, head_commit = _project(tmp_path)
    tasks_path = root / "openspec/changes" / CHANGE_NAME / "tasks.md"
    original_tasks = tasks_path.read_text(encoding="utf-8")
    bin_path = root / "bin"
    bin_path.mkdir()
    calls_path = root / "tool-calls.log"
    for command in ("git", "openspec"):
        wrapper = bin_path / command
        wrapper.write_text(
            f"#!/bin/sh\nprintf '%s\\n' {command!r} >> {str(calls_path)!r}\nexit 97\n",
            encoding="utf-8",
        )
        wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR)
    environment = {**os.environ, "PATH": f"{bin_path}{os.pathsep}{os.environ['PATH']}"}
    incomplete = _attestation(root, base_commit, head_commit)
    del incomplete["base_commit"]

    receipt = _receipt(_run(root, "verify-boundary", incomplete, environment=environment))

    assert receipt == {
        "schema_version": "selected-change-closeout/v1",
        "result": "missing-boundary",
        "condition": "missing-field",
    }
    assert not calls_path.exists()
    assert tasks_path.read_text(encoding="utf-8") == original_tasks
    assert not (root / "openspec/changes" / CHANGE_NAME / "guardrail-evidence").exists()
