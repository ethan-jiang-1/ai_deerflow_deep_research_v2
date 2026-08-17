"""Upstream governance integration around downstream verification."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def _job_block(workflow: str, job_name: str) -> str:
    match = re.search(rf"\n  {re.escape(job_name)}:\n", workflow)
    assert match is not None, f"missing job {job_name}"
    remainder = workflow[match.end() :]
    next_job = re.search(r"\n  [A-Za-z0-9_-]+:\n", remainder)
    return remainder[: next_job.start()] if next_job else remainder


def test_deterministic_pr_workflow_delegates_to_downstream_verify() -> None:
    workflow = (REPO_ROOT / ".github/workflows/agent-tests.yml").read_text(encoding="utf-8")
    block = _job_block(workflow, "deterministic")
    assert block.count("make install") == 1
    assert block.count("UV_OFFLINE=1 make verify") == 1
    assert block.index("make install") < block.index("UV_OFFLINE=1 make verify")


def test_archive_guidance_keeps_governance_outside_downstream_verify() -> None:
    config = (REPO_ROOT / "openspec/config.yaml").read_text(encoding="utf-8")
    assert config.count("cd deep_research_harness && UV_OFFLINE=1 make verify") == 1
    assert "openspec validate <change-name> --strict" in config
    assert "git diff HEAD --check" in config


def test_upstream_navigation_and_temporary_registry_contracts() -> None:
    readme = (REPO_ROOT / "openspec/README.md").read_text(encoding="utf-8")
    assert "active proposed deltas" not in readme
    assert "changes/archive" in readme
    assert not (REPO_ROOT / "openspec/governance/req-registry.yaml.tmp").exists()
