"""Portable Change Guidance candidate identity contracts.

@impl PCG-005
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "openspec/governance/portable_change_guidance_export.py"
SPEC = importlib.util.spec_from_file_location("portable_change_guidance_export", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
export = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = export
SPEC.loader.exec_module(export)


def _candidate(root: Path) -> dict[str, object]:
    (root / "openspec/change-guidance/core").mkdir(parents=True)
    (root / "openspec/change-guidance/core/change-practice.md").write_text("portable\n", encoding="utf-8")
    profile = root / "openspec/change-guidance/profiles/node-agent"
    profile.mkdir(parents=True)
    (profile / "README.md").write_text("portable profile\n", encoding="utf-8")
    kernel = root / "openspec/governance/change_guidance_kernel.py"
    kernel.parent.mkdir(parents=True)
    kernel.write_text("PORTABLE = True\n", encoding="utf-8")
    return export.build_manifest(
        root,
        source_repository="fixture",
        source_revision="fixture-revision",
        snapshot_date="2026-08-17",
        selected_profiles=("node-agent",),
    )


def test_exact_allowlisted_candidate_passes(tmp_path: Path) -> None:
    manifest = _candidate(tmp_path)

    assert manifest["status"] == "portable snapshot"
    export.verify_manifest(tmp_path, manifest)


def test_one_file_tampering_fails(tmp_path: Path) -> None:
    manifest = _candidate(tmp_path)
    (tmp_path / "openspec/change-guidance/core/change-practice.md").write_text("tampered\n", encoding="utf-8")
    with pytest.raises(export.CandidateViolation, match="digest mismatch"):
        export.verify_manifest(tmp_path, manifest)


def test_denylisted_local_path_fails(tmp_path: Path) -> None:
    manifest = _candidate(tmp_path)
    manifest["files"].append({"path": "openspec/change-guidance/local/routes.md", "sha256": "0" * 64})
    with pytest.raises(export.CandidateViolation, match="denylisted"):
        export.verify_manifest(tmp_path, manifest)


def test_portable_markdown_link_cannot_leave_allowlist(tmp_path: Path) -> None:
    _candidate(tmp_path)
    principles = tmp_path / "openspec/change-guidance/core/change-practice.md"
    principles.write_text("[local owner](../local/routes.md)\n", encoding="utf-8")
    manifest = export.build_manifest(
        tmp_path,
        source_repository="fixture",
        source_revision="fixture-revision",
        snapshot_date="2026-08-17",
        selected_profiles=("node-agent",),
    )
    with pytest.raises(export.CandidateViolation, match="leaves selected allowlist"):
        export.verify_manifest(tmp_path, manifest)
