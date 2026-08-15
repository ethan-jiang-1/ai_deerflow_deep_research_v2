"""Current node-language surface contract.

@impl DRC-013
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from scripts.check_node_language import NodeLanguageError, scan_tracked_language

ROOT = Path(__file__).resolve().parents[3]


def _git(root: Path, *arguments: str) -> None:
    subprocess.run(["git", *arguments], cwd=root, check=True, capture_output=True)


def _tracked_fixture(root: Path) -> None:
    root.mkdir()
    _git(root, "init")
    _git(root, "config", "user.email", "language@example.test")
    _git(root, "config", "user.name", "Language Fixture")
    for relative_path in (
        "current.txt",
        "openspec/changes/archive/old.txt",
        "_backlog/_done/closed.txt",
        "unfamiliar.extension",
    ):
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"current vocabulary\n")
    os.symlink("current-target", root / "link-value")
    _git(root, "add", ".")


def test_current_node_language_has_no_retired_identity_or_capability_contract() -> None:
    report = scan_tracked_language(ROOT)

    assert "deerflow" in report.gitlink_paths
    assert "deep_research_harness/tests/contract/test_node_language_contract.py" in report.checked_paths


@pytest.mark.parametrize(
    ("relative_path", "token"),
    (
        ("current.txt", b"Phase" + b" Agent"),
        ("openspec/changes/archive/old.txt", b"MD" + b" controller"),
        ("_backlog/_done/closed.txt", b"capability" + b"_binding"),
        ("unfamiliar.extension", b"phase" + b"-agent"),
        ("unfamiliar.extension", b"D" + b"PT"),
        ("link-value", b"Phase" + b" Agent"),
    ),
)
def test_tracked_language_guard_rejects_assembled_residuals_in_every_surface(
    tmp_path: Path, relative_path: str, token: bytes
) -> None:
    root = tmp_path / "repository"
    _tracked_fixture(root)
    path = root / relative_path
    if path.is_symlink():
        path.unlink()
        os.symlink(os.fsdecode(token), path)
    else:
        path.write_bytes(token)

    with pytest.raises(NodeLanguageError, match=f"language.retired_label:.*{relative_path}"):
        scan_tracked_language(root)


def test_tracked_language_guard_fails_closed_for_missing_materialized_file(tmp_path: Path) -> None:
    root = tmp_path / "repository"
    _tracked_fixture(root)
    (root / "current.txt").unlink()

    with pytest.raises(NodeLanguageError, match="language.materialized_file_invalid:current.txt"):
        scan_tracked_language(root)
