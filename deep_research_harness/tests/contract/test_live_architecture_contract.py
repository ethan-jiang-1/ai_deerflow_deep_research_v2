"""Run the permanent architecture checker against the live repository.

@impl PRS-005
@impl PRS-010
@impl PRS-011
@impl PRS-006
@impl PRS-012
@impl PRS-013
@impl PRS-014
@impl PRS-015
@impl PRS-016
@impl PRS-018
@impl DER-002
@impl FSI-001
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def test_live_repository_satisfies_architecture_contract() -> None:
    checker = importlib.import_module("openspec.governance.check_project_architecture")
    checker.check_project(REPO_ROOT)


def test_production_wheel_excludes_fixture_package() -> None:
    agent_root = REPO_ROOT / "deep_research_harness"
    with tempfile.TemporaryDirectory() as temporary:
        result = subprocess.run(
            ["uv", "build", "--wheel", "--out-dir", temporary],
            cwd=agent_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, result.stderr
        wheels = list(Path(temporary).glob("*.whl"))
        assert len(wheels) == 1
        with zipfile.ZipFile(wheels[0]) as archive:
            members = archive.namelist()
    assert any(member.startswith("deerflow_deep_research/") for member in members)
    assert not any(member.startswith("deerflow_deep_research_fixtures/") for member in members)


def test_fixture_package_is_available_only_to_the_test_process() -> None:
    assert importlib.util.find_spec("deerflow_deep_research_fixtures") is not None

    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import importlib.util; "
            "raise SystemExit(0 if importlib.util.find_spec('deerflow_deep_research_fixtures') is None else 1)",
        ],
        cwd=REPO_ROOT / "deep_research_harness",
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr


def test_prompt_review_workspace_is_optional_and_ignored() -> None:
    manifest = tomllib.loads((REPO_ROOT / "openspec/governance/project-structure.toml").read_text(encoding="utf-8"))
    required_paths = {entry["path"] for entry in manifest["required_paths"]}

    assert "deep_research_harness/node_prompts" not in required_paths
    assert "deep_research_harness/.node-prompt-review" not in required_paths
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", "deep_research_harness/.node-prompt-review/README.md"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert ignored.returncode == 0, ignored.stderr
