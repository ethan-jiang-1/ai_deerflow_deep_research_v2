"""Requirement registry ownership lifecycle contracts.

@impl EVH-010
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHECKER = Path(__file__).resolve().parents[3] / "openspec" / "governance" / "check_project_reqs.py"


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CHECKER), str(root)], capture_output=True, text=True, check=False)


def _registry(root: Path, entries: str) -> None:
    _write(root, "openspec/governance/req-registry.yaml", entries)


def _main_spec(root: Path, capability: str, requirement_ids: str) -> None:
    _write(root, f"openspec/specs/{capability}/spec.md", f"> req: {requirement_ids}\n")


def _active_delta(root: Path, change: str, capability: str, requirement_ids: str) -> None:
    _write(root, f"openspec/changes/{change}/specs/{capability}/spec.md", f"> req: {requirement_ids}\n")


def test_main_and_pending_requirement_headers_can_share_a_capability(tmp_path: Path) -> None:
    _registry(
        tmp_path,
        "ABC-001: example — accepted\nABC-002: example — pending\n",
    )
    _main_spec(tmp_path, "example", "ABC-001")
    _active_delta(tmp_path, "add-pending", "example", "ABC-001, ABC-002")

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr


def test_pending_only_capability_does_not_need_a_main_spec_before_archive(tmp_path: Path) -> None:
    _registry(tmp_path, "PEN-001: pending-capability — pending behavior\n")
    _active_delta(tmp_path, "introduce-pending", "pending-capability", "PEN-001")

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr


def test_pending_header_in_a_different_capability_does_not_satisfy_ownership(tmp_path: Path) -> None:
    _registry(
        tmp_path,
        "ABC-001: example — accepted\nABC-002: example — pending\n",
    )
    _main_spec(tmp_path, "example", "ABC-001")
    _active_delta(tmp_path, "wrong-owner", "other", "ABC-002")

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "main spec header missing owned IDs: example: ABC-002" in result.stderr


def test_registered_requirement_missing_from_main_and_active_delta_fails(tmp_path: Path) -> None:
    _registry(
        tmp_path,
        "ABC-001: example — accepted\nABC-002: example — missing\n",
    )
    _main_spec(tmp_path, "example", "ABC-001")

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "main spec header missing owned IDs: example: ABC-002" in result.stderr


def test_active_delta_cannot_reuse_a_retired_requirement(tmp_path: Path) -> None:
    _registry(tmp_path, "ABC-001: example — retired [DEPRECATED]\n")
    _active_delta(tmp_path, "reuse-retired", "example", "ABC-001")

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "Reused retired IDs" in result.stderr
    assert "ABC-001" in result.stderr


def test_duplicate_main_spec_owner_is_rejected(tmp_path: Path) -> None:
    _registry(tmp_path, "ABC-001: example — accepted\n")
    _main_spec(tmp_path, "example", "ABC-001")
    _main_spec(tmp_path, "duplicate", "ABC-001")

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "Duplicate IDs" in result.stderr
    assert "ABC-001" in result.stderr


def test_orphan_registry_requirement_is_rejected(tmp_path: Path) -> None:
    _registry(
        tmp_path,
        "ABC-001: example — accepted\nABC-002: example — orphaned\n",
    )
    _main_spec(tmp_path, "example", "ABC-001")

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "Orphan IDs" in result.stderr
    assert "ABC-002" in result.stderr
