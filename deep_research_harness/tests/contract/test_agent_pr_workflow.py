"""Agent PR workflow delegates to the canonical deterministic gate.

@impl EVH-009
"""

from pathlib import Path


def test_agent_pr_workflow_delegates_to_canonical_deterministic_gate() -> None:
    workflow = Path("../.github/workflows/agent-tests.yml").read_text(encoding="utf-8")

    assert "pull_request:" in workflow
    assert workflow.count('      - "deep_research_harness/**"') == 2
    assert workflow.count("working-directory: deep_research_harness") == 1
    assert "working-directory: agent" not in workflow
    assert "agent-release-e2e.yml" not in workflow
    assert workflow.count("make install") == 1
    assert "uv sync --locked --extra operations --extra demo-tui" not in workflow
    assert workflow.index("make install") < workflow.index("UV_OFFLINE=1 make verify")
    assert workflow.count("UV_OFFLINE=1 make verify") == 1
    assert workflow.count("UV_OFFLINE=1 make test-duration-policy") == 1
    for component in (
        "make lock-check",
        "make lint",
        "make test-assets",
        "make test-req-coverage",
        "make test-fast",
        "make test-integration",
        "make test-workflow",
    ):
        assert component not in workflow
