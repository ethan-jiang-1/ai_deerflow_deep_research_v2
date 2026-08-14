"""Repository-tracked CI and OpenSpec delivery contracts.

@impl DER-005
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
DETERMINISTIC_WORKFLOW = Path(".github/workflows/agent-tests.yml")
MANUAL_LIVE_WORKFLOW = Path(".github/workflows/agent-live-evaluation.yml")
PROJECT_SKILL_FILES = (
    Path(".agents/skills/.openspec-target"),
    Path(".agents/skills/openspec-apply-change/SKILL.md"),
    Path(".agents/skills/openspec-archive-change/SKILL.md"),
    Path(".agents/skills/openspec-explore/SKILL.md"),
    Path(".agents/skills/openspec-propose/SKILL.md"),
    Path(".agents/skills/openspec-sync-specs/SKILL.md"),
    Path(".agents/skills/openspec-update-change/SKILL.md"),
    Path(".agents/skills/polish-openspec-change/SKILL.md"),
    Path(".agents/skills/polish-openspec-change/agents/openai.yaml"),
)
REQUIRED_DELIVERY_FILES = (DETERMINISTIC_WORKFLOW, MANUAL_LIVE_WORKFLOW, *PROJECT_SKILL_FILES)


def _git(root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def _delivery_violations(root: Path) -> tuple[str, ...]:
    violations: list[str] = []
    for relative_path in REQUIRED_DELIVERY_FILES:
        path = root / relative_path
        if not path.is_file():
            violations.append(f"missing:{relative_path}")

        staged = _git(root, "ls-files", "--stage", "--", str(relative_path))
        tracked = any(
            line.endswith(f"\t{relative_path}") and line.split()[2] == "0" for line in staged.stdout.splitlines()
        )
        if staged.returncode != 0 or not tracked:
            violations.append(f"untracked:{relative_path}")

        ignored = _git(root, "check-ignore", "--no-index", "--quiet", "--", str(relative_path))
        if ignored.returncode == 0:
            violations.append(f"ignored:{relative_path}")
        elif ignored.returncode != 1:
            violations.append(f"ignore-check-failed:{relative_path}")

    target = root / PROJECT_SKILL_FILES[0]
    if target.is_file() and target.read_text(encoding="utf-8") != "codex\n":
        violations.append("target:not-codex")
    return tuple(violations)


def _write_delivery_fixture(root: Path) -> None:
    for relative_path in REQUIRED_DELIVERY_FILES:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("codex\n" if relative_path == PROJECT_SKILL_FILES[0] else "fixture\n", encoding="utf-8")
    (root / ".gitignore").write_text("", encoding="utf-8")
    assert _git(root, "init", "--quiet").returncode == 0
    assert _git(root, "config", "user.name", "delivery-fixture").returncode == 0
    assert _git(root, "config", "user.email", "delivery-fixture@example.invalid").returncode == 0
    assert _git(root, "add", ".").returncode == 0
    assert _git(root, "commit", "--quiet", "-m", "fixture").returncode == 0


def test_repository_delivery_is_tracked_unignored_and_declares_codex() -> None:
    assert _delivery_violations(REPO_ROOT) == ()

    deterministic = (REPO_ROOT / DETERMINISTIC_WORKFLOW).read_text(encoding="utf-8")
    assert "pull_request:" in deterministic
    assert "UV_OFFLINE=1 make verify" in deterministic
    assert "UV_OFFLINE=1 make test-duration-policy" in deterministic

    manual_live = (REPO_ROOT / MANUAL_LIVE_WORKFLOW).read_text(encoding="utf-8")
    assert "workflow_dispatch:" in manual_live
    assert "pull_request:" not in manual_live
    assert "push:" not in manual_live


@pytest.mark.parametrize(
    ("mutate", "expected"),
    (
        (
            lambda root: _git(root, "rm", "--cached", "--quiet", str(PROJECT_SKILL_FILES[0])),
            f"untracked:{PROJECT_SKILL_FILES[0]}",
        ),
        (
            lambda root: (root / DETERMINISTIC_WORKFLOW).unlink(),
            f"missing:{DETERMINISTIC_WORKFLOW}",
        ),
        (
            lambda root: (root / ".gitignore").write_text(".agents/skills/\n", encoding="utf-8"),
            f"ignored:{PROJECT_SKILL_FILES[0]}",
        ),
    ),
)
def test_repository_delivery_guard_rejects_missing_untracked_and_ignored_artifacts(
    tmp_path: Path,
    mutate: Callable[[Path], object],
    expected: str,
) -> None:
    root = tmp_path / "repository"
    root.mkdir()
    _write_delivery_fixture(root)

    mutate(root)

    assert expected in _delivery_violations(root)
