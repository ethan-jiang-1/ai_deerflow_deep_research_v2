"""Active main-spec governance contracts.

@impl EVH-010
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHECKER = Path(__file__).resolve().parents[3] / "openspec" / "governance" / "check_project_specs.py"


def _write(root: Path, path: str, text: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def _project(tmp_path: Path) -> Path:
    _write(
        tmp_path,
        "openspec/specs/example/spec.md",
        "> req: ABC-001\n\n## Purpose\n\nCurrent behavior.\n\n## Requirements\n",
    )
    return tmp_path


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CHECKER), str(root)], text=True, capture_output=True, check=False)


def test_empty_and_archive_placeholder_purpose_fail(tmp_path: Path) -> None:
    root = _project(tmp_path)
    _write(
        root,
        "openspec/specs/example/spec.md",
        "> req: ABC-001\n\n## Purpose\n\nTBD - created by archiving\n\n## Requirements\n",
    )
    result = _run(root)
    assert result.returncode == 1
    assert "placeholder Purpose" in result.stderr


def test_historical_active_terminology_fails_but_archives_are_excluded(tmp_path: Path) -> None:
    root = _project(tmp_path)
    _write(root, "openspec/changes/archive/old/specs/example/spec.md", "Change 08 skeleton remains fake")
    assert _run(root).returncode == 0
    _write(root, "deep_research_harness/README.md", "Change 08 skeleton remains fake")
    result = _run(root)
    assert result.returncode == 1
    assert "Historical terminology" in result.stderr
