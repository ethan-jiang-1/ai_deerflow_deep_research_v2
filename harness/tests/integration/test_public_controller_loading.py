"""Dedicated-Agent composition for the real ordinary controller route.

@impl DEC-003
@impl DEC-004
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
AGENT_CONFIG_SOURCE = REPO_ROOT / "deep_research_harness" / "config" / "agent-template" / "config.yaml"
PUBLIC_SKILL_SOURCE = (
    REPO_ROOT / "deep_research_harness" / "config" / "public-skill" / "deep-research-controller" / "SKILL.md"
)


def test_dedicated_agent_exposes_the_real_controller_loader_and_lifecycle_tools() -> None:
    """The template's configured groups resolve to the two required public tools."""

    from deerflow.config.app_config import AppConfig
    from deerflow.tools import get_available_tools

    agent_config = yaml.safe_load(AGENT_CONFIG_SOURCE.read_text(encoding="utf-8"))
    app_config = AppConfig.model_validate(
        {
            "models": [
                {
                    "name": "ordinary-loader-test-model",
                    "display_name": "Ordinary loader test model",
                    "use": "langchain_openai:ChatOpenAI",
                    "model": "gpt-4o-mini",
                    "api_key": "test-only-key",
                }
            ],
            "sandbox": {"use": "deerflow.sandbox.local:LocalSandboxProvider"},
            "tool_groups": [{"name": "deep-research-control"}, {"name": "file:read"}],
            "tools": [
                {
                    "name": "deep_research",
                    "group": "deep-research-control",
                    "use": "deerflow_deep_research.tool:deep_research_tool",
                },
                {
                    "name": "read_file",
                    "group": "file:read",
                    "use": "deerflow.sandbox.tools:read_file_tool",
                },
            ],
        }
    )

    assert agent_config["tool_groups"] == ["deep-research-control", "file:read"]
    resolved_names = {
        tool.name
        for tool in get_available_tools(
            groups=agent_config["tool_groups"],
            include_mcp=False,
            app_config=app_config,
        )
    }
    assert {"deep_research", "read_file"} <= resolved_names
    assert "allowed-tools:" not in PUBLIC_SKILL_SOURCE.read_text(encoding="utf-8")
