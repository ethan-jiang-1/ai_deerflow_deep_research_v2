"""Contracts for the canonical deterministic verification composition.

@impl EVH-009
@impl EVH-010
@impl DER-004
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
AGENT_ROOT = REPO_ROOT / "deep_research_harness"
MAKEFILE = AGENT_ROOT / "Makefile"


def _job_block(workflow: str, job_name: str) -> str:
    match = re.search(rf"\n  {re.escape(job_name)}:\n", workflow)
    assert match is not None, f"missing job {job_name}"
    remainder = workflow[match.end() :]
    next_job = re.search(r"\n  [A-Za-z0-9_-]+:\n", remainder)
    return remainder[: next_job.start()] if next_job else remainder


def test_makefile_exposes_exact_non_mutating_verify_composition() -> None:
    text = MAKEFILE.read_text(encoding="utf-8")

    assert re.search(r"^\.PHONY:.*\bgovernance\b.*\bverify\b", text, re.MULTILINE)
    assert "install:\n\tuv sync --locked --extra operations --extra demo-tui" in text
    assert "governance:\n" in text
    assert (
        "\tpython3 ../openspec/governance/check_project_reqs.py ..\n"
        "\tpython3 ../openspec/governance/check_project_specs.py ..\n"
        "\tpython3 ../openspec/governance/check_project_architecture.py .." in text
    )
    assert "\tpython3 ../openspec/governance/check_agent_charter.py .." in text
    assert "verify: export UV_NO_SYNC := 1" in text
    assert (
        "verify: governance lock-check lint test-assets test-req-coverage test-fast test-integration test-workflow"
    ) in text
    assert not re.search(r"^verify:\n\t", text, re.MULTILINE)
    assert ("\t\ttests/assets tests/contract tests/domain tests/engine tests/unit tests/graph tests/eval \\\n") in text
    assert "--durations=20 --junitxml=.reports/test-fast.xml" in text
    assert "PYTEST := python -m pytest" in text
    for target in ("test-intake", "test-retained-observation", "test-work-unit", "test-strict-checkpoint"):
        assert re.search(rf"^{target}:\n\t@started=.* elapsed:", text, re.MULTILINE)
    assert (
        "test-duration-policy:\n"
        "\tuv run --extra operations python scripts/check_test_durations.py .reports/test-fast.xml"
    ) in text
    assert (
        'uv run --extra operations --extra demo-tui $(PYTEST) -m "not (requires_llm or release_e2e or postgres)"'
    ) in text


def test_deterministic_pr_workflow_delegates_without_forking_component_gates() -> None:
    pr_workflow = (REPO_ROOT / ".github/workflows/agent-tests.yml").read_text(encoding="utf-8")

    assert "agent-release-e2e.yml" not in pr_workflow
    assert not (REPO_ROOT / ".github/workflows/agent-release-e2e.yml").exists()

    block = _job_block(pr_workflow, "deterministic")
    assert block.count("uv sync --locked --extra operations --extra demo-tui") == 1
    assert block.count("UV_OFFLINE=1 make verify") == 1
    for component in (
        "make lock-check",
        "make lint",
        "make test-assets",
        "make test-req-coverage",
        "make test-fast",
        "make test-integration",
        "make test-workflow",
    ):
        assert component not in block

    assert block.count("UV_OFFLINE=1 make test-duration-policy") == 1


def test_archive_guidance_has_one_canonical_command_and_separate_finalization() -> None:
    config = (REPO_ROOT / "openspec/config.yaml").read_text(encoding="utf-8")

    assert config.count("cd deep_research_harness && UV_OFFLINE=1 make verify") == 1
    assert "openspec validate <change-name> --strict" in config
    assert "git diff HEAD --check" in config
    assert "git status --porcelain=v1 --untracked-files=all" in config
    for checker in ("check_project_reqs.py", "check_project_specs.py", "check_project_architecture.py"):
        assert f"python3 openspec/governance/{checker}" not in config


def test_temporary_requirement_registry_copy_is_absent() -> None:
    assert not (REPO_ROOT / "openspec/governance/req-registry.yaml.tmp").exists()
