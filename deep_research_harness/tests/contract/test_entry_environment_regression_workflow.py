"""Maintained periodic entry-environment workflow contracts.

@impl EVH-032
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = REPO_ROOT / ".github/workflows/agent-entry-environment-regression.yml"

EXPECTED_PATHS = (
    '      - "deep_research_harness/Makefile"',
    '      - "deep_research_harness/pyproject.toml"',
    '      - "deep_research_harness/uv.lock"',
    '      - "deep_research_harness/run/**"',
    '      - "deep_research_harness/scripts/**"',
    '      - "deep_research_harness/src/**"',
    '      - "deep_research_harness/src_fake/**"',
    '      - "deep_research_harness/tests/scenarios_periodic/**"',
    '      - ".github/workflows/agent-entry-environment-regression.yml"',
)


def test_periodic_workflow_has_exact_paths_cadence_and_offline_target() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert workflow.startswith("name: Deep Research Entry Environment Regression\n")
    assert "pull_request:\n    paths:" in workflow
    assert "push:\n    branches: [master]\n    paths:" in workflow
    assert 'schedule:\n    - cron: "17 3 * * *"' in workflow
    assert "workflow_dispatch:" in workflow
    assert all(workflow.count(path) == 2 for path in EXPECTED_PATHS)
    assert workflow.count("working-directory: deep_research_harness") == 1
    assert workflow.count("make install") == 1
    assert workflow.index("make install") < workflow.index("UV_OFFLINE=1 make test-entry-environment-regression")
    assert workflow.count("UV_OFFLINE=1 make test-entry-environment-regression") == 1
    assert "requires_llm" not in workflow
    assert "release_e2e" not in workflow
    assert "secrets." not in workflow


def test_periodic_workflow_is_distinct_from_the_rapid_deterministic_workflow() -> None:
    periodic = WORKFLOW.read_text(encoding="utf-8")
    rapid = (REPO_ROOT / ".github/workflows/agent-tests.yml").read_text(encoding="utf-8")

    assert "Deep Research Deterministic Tests" in rapid
    assert "Deep Research Entry Environment Regression" not in rapid
    assert "test-entry-environment-regression" not in rapid
    assert "make verify" not in periodic
