"""Contracts for user-scoped Deep Research Agent provisioning.

@impl DEC-004
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIGURE_PATH = REPO_ROOT / "deep_research_harness/scripts/configure.py"
AGENT_CONFIG_SOURCE = REPO_ROOT / "deep_research_harness/config/agent-template/config.yaml"
AGENT_SOUL_SOURCE = REPO_ROOT / "deep_research_harness/config/agent-template/SOUL.md"
AGENT_RELATIVE = Path("users/default/agents/deep-research")
VALID_FILE_READ_CONFIG = """\
tool_groups:
  - name: file:read
tools:
  - name: read_file
    group: file:read
    use: deerflow.sandbox.tools:read_file_tool
"""


def _module():
    spec = importlib.util.spec_from_file_location("deep_research_agent_configure", CONFIGURE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def project(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "backend").mkdir()
    (root / "skills/public").mkdir(parents=True)
    (root / "skills/custom").mkdir(parents=True)
    (root / "config.yaml").write_text(
        "config_version: 19\nagents_api:\n  enabled: false\n" + VALID_FILE_READ_CONFIG + "skills: {}\n",
        encoding="utf-8",
    )
    (root / "extensions_config.json").write_text('{"mcpServers": {}, "skills": {}}\n', encoding="utf-8")
    home = root / ".runtime-home"
    env = {
        "DEER_FLOW_CONFIG_PATH": str(root / "config.yaml"),
        "DEER_FLOW_EXTENSIONS_CONFIG_PATH": str(root / "extensions_config.json"),
        "DEER_FLOW_SKILLS_PATH": str(root / "skills"),
        "DEER_FLOW_HOME": str(home),
    }
    return root, env


def _write_effective_config(root: Path, body: str) -> None:
    (root / "config.yaml").write_text(
        "config_version: 19\nagents_api:\n  enabled: false\n" + body + "skills: {}\n",
        encoding="utf-8",
    )


def _enable_agents_api(root: Path) -> None:
    config = root / "config.yaml"
    config.write_text(config.read_text(encoding="utf-8").replace("enabled: false", "enabled: true"), encoding="utf-8")


def test_nonproduction_auth_disabled_materializes_only_default_user_agent(
    project: tuple[Path, dict[str, str]],
) -> None:
    root, env = project
    env["DEER_FLOW_AUTH_DISABLED"] = "1"
    module = _module()
    home = Path(env["DEER_FLOW_HOME"])
    target = home / AGENT_RELATIVE

    first = module.execute_configuration(root, env, mode="apply", online_detector=lambda: False)
    second = module.execute_configuration(root, env, mode="apply", online_detector=lambda: False)

    assert (target / "config.yaml").read_bytes() == AGENT_CONFIG_SOURCE.read_bytes()
    assert (target / "SOUL.md").read_bytes() == AGENT_SOUL_SOURCE.read_bytes()
    assert first.summary["agent_status"] == "ready"
    assert first.entry_status == "ready"
    assert second.changed is False
    assert not (home / "agents/deep-research").exists()
    assert not (home / "users" / "arbitrary").exists()

    module.rollback_configuration(first.manifest_path, online_detector=lambda: False)

    assert not target.exists()
    assert not (home / "agents/deep-research").exists()


@pytest.mark.parametrize(("key", "value"), [("DEER_FLOW_ENV", "production"), ("ENVIRONMENT", "prod")])
def test_production_refuses_auth_disabled_agent_provisioning_before_every_write(
    project: tuple[Path, dict[str, str]], key: str, value: str
) -> None:
    root, env = project
    env.update({"DEER_FLOW_AUTH_DISABLED": "1", key: value})
    before = ((root / "config.yaml").read_bytes(), (root / "extensions_config.json").read_bytes())
    module = _module()

    with pytest.raises(module.ConfigureError, match="entry.auth_disabled_production"):
        module.execute_configuration(root, env, mode="apply", online_detector=lambda: False)

    assert ((root / "config.yaml").read_bytes(), (root / "extensions_config.json").read_bytes()) == before
    assert not (Path(env["DEER_FLOW_HOME"]) / "users").exists()


def test_offline_cli_rejects_user_id_without_writing_any_user_agent(
    project: tuple[Path, dict[str, str]],
) -> None:
    root, env = project
    result = subprocess.run(
        [
            sys.executable,
            str(CONFIGURE_PATH),
            "--project-root",
            str(root),
            "--user-id",
            "arbitrary-user",
        ],
        check=False,
        capture_output=True,
        text=True,
        env=os.environ | env,
    )

    assert result.returncode != 0
    assert "--user-id" in result.stderr
    assert not (Path(env["DEER_FLOW_HOME"]) / "users").exists()


def test_authenticated_current_user_api_fixture_matches_gateway_request_and_response() -> None:
    fixture = _module().authenticated_agent_api_fixture()
    soul = AGENT_SOUL_SOURCE.read_text(encoding="utf-8").strip()

    assert fixture == {
        "method": "POST",
        "path": "/api/agents",
        "status_code": 201,
        "request": {
            "name": "deep-research",
            "description": "Graph-controlled Deep Research",
            "tool_groups": ["deep-research-control", "file:read"],
            "skills": ["deep-research-controller"],
            "soul": soul,
        },
        "response": {
            "name": "deep-research",
            "description": "Graph-controlled Deep Research",
            "model": None,
            "tool_groups": ["deep-research-control", "file:read"],
            "skills": ["deep-research-controller"],
            "soul": soul,
        },
    }
    assert "user_id" not in json.dumps(fixture)


def test_invalid_file_read_prerequisite_keeps_dedicated_entry_not_ready_without_a_reduced_agent(
    project: tuple[Path, dict[str, str]],
) -> None:
    root, env = project
    env["DEER_FLOW_AUTH_DISABLED"] = "1"
    target = Path(env["DEER_FLOW_HOME"]) / AGENT_RELATIVE
    cases = (
        ("tool_groups: []\ntools: []\n", "file_read_group_missing"),
        (
            "tool_groups:\n  - name: file:read\n  - name: file:read\n"
            "tools:\n  - name: read_file\n    group: file:read\n"
            "    use: deerflow.sandbox.tools:read_file_tool\n",
            "file_read_group_ambiguous",
        ),
        ("tool_groups:\n  - name: file:read\ntools: []\n", "file_read_tool_missing"),
        (
            "tool_groups:\n  - name: file:read\n"
            "tools:\n  - name: read_file\n    group: file:read\n"
            "    use: deerflow.sandbox.tools:ls_tool\n",
            "file_read_tool_misbound",
        ),
    )

    for config_body, expected_issue in cases:
        _write_effective_config(root, config_body)
        result = _module().execute_configuration(root, env, mode="apply", online_detector=lambda: False)

        assert result.runtime_config_ready is True
        assert result.summary["public_skill_status"] == "ready"
        assert result.entry_status == "not_ready"
        assert result.summary["agent_status"] == "not_ready"
        assert result.summary["entry_issues"] == [expected_issue]
        assert not target.exists()
        assert "deep-research-control" in (root / "config.yaml").read_text(encoding="utf-8")
        assert (root / "skills/public/deep-research-controller/SKILL.md").is_file()


def test_invalid_file_read_prerequisite_never_replaces_existing_agent_files(
    project: tuple[Path, dict[str, str]],
) -> None:
    root, env = project
    env["DEER_FLOW_AUTH_DISABLED"] = "1"
    target = Path(env["DEER_FLOW_HOME"]) / AGENT_RELATIVE
    target.mkdir(parents=True)
    (target / "config.yaml").write_bytes(AGENT_CONFIG_SOURCE.read_bytes())
    (target / "SOUL.md").write_bytes(AGENT_SOUL_SOURCE.read_bytes())
    before = ((target / "config.yaml").read_bytes(), (target / "SOUL.md").read_bytes())
    _write_effective_config(root, "tool_groups: []\ntools: []\n")

    result = _module().execute_configuration(root, env, mode="apply", online_detector=lambda: False)

    assert result.entry_status == "not_ready"
    assert result.summary["entry_issues"] == ["file_read_group_missing"]
    assert ((target / "config.yaml").read_bytes(), (target / "SOUL.md").read_bytes()) == before


def test_invalid_file_read_prerequisite_hides_authenticated_agent_fixture(
    project: tuple[Path, dict[str, str]],
) -> None:
    root, env = project
    _enable_agents_api(root)
    _write_effective_config(root, "tool_groups: []\ntools: []\n")

    result = _module().execute_configuration(root, env, mode="apply", online_detector=lambda: False)

    assert result.entry_status == "not_ready"
    assert result.summary["agent_status"] == "not_ready"
    assert result.summary["entry_issues"] == ["file_read_group_missing"]
    assert "authenticated_agent_api" not in result.summary
    assert not (Path(env["DEER_FLOW_HOME"]) / "users").exists()


def test_file_read_group_is_operator_owned_and_rollback_does_not_claim_it(
    project: tuple[Path, dict[str, str]],
) -> None:
    root, env = project
    env["DEER_FLOW_AUTH_DISABLED"] = "1"
    before = (root / "config.yaml").read_bytes()
    module = _module()

    result = module.execute_configuration(root, env, mode="apply", online_detector=lambda: False)

    assert result.manifest_path is not None
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    yaml_target = next(target for target in manifest["targets"] if target["kind"] == "yaml")
    assert yaml_target["owned_after"] == {
        "group": {
            "name": "deep-research-control",
            "x-deerflow-deep-research-owner": "v1",
        },
        "tool": {
            "name": "deep_research",
            "group": "deep-research-control",
            "use": "deerflow_deep_research.tool:deep_research_tool",
            "x-deerflow-deep-research-owner": "v1",
        },
    }
    assert "file:read" not in json.dumps(yaml_target["owned_after"])

    module.rollback_configuration(result.manifest_path, online_detector=lambda: False)

    assert (root / "config.yaml").read_bytes() == before


def test_offline_rollback_never_removes_authenticated_api_created_agent(
    project: tuple[Path, dict[str, str]],
) -> None:
    root, env = project
    _enable_agents_api(root)
    module = _module()
    applied = module.execute_configuration(root, env, mode="apply", online_detector=lambda: False)
    api_agent = Path(env["DEER_FLOW_HOME"]) / "users/authenticated-user/agents/deep-research"
    api_agent.mkdir(parents=True)
    (api_agent / "config.yaml").write_text("name: deep-research\ndescription: API owned\n", encoding="utf-8")
    (api_agent / "SOUL.md").write_text("API-owned state\n", encoding="utf-8")
    before = ((api_agent / "config.yaml").read_bytes(), (api_agent / "SOUL.md").read_bytes())

    module.rollback_configuration(applied.manifest_path, online_detector=lambda: False)

    assert ((api_agent / "config.yaml").read_bytes(), (api_agent / "SOUL.md").read_bytes()) == before


def test_disabled_agents_api_is_diagnosed_without_being_enabled(
    project: tuple[Path, dict[str, str]],
) -> None:
    root, env = project
    module = _module()
    result = module.execute_configuration(root, env, mode="apply", online_detector=lambda: False)

    assert result.runtime_config_ready is True
    assert result.summary["agent_status"] == "not_ready"
    assert result.summary["entry_issues"] == ["agents_api_disabled"]
    assert result.summary["authenticated_agent_api"] == module.authenticated_agent_api_fixture()
    assert "enabled: false" in (root / "config.yaml").read_text(encoding="utf-8")
    assert not (Path(env["DEER_FLOW_HOME"]) / "users").exists()


def test_authenticated_agent_is_unknown_offline_and_does_not_block_global_tool(
    project: tuple[Path, dict[str, str]],
) -> None:
    root, env = project
    _enable_agents_api(root)
    result = _module().execute_configuration(root, env, mode="apply", online_detector=lambda: False)

    assert result.runtime_config_ready is True
    assert result.entry_status == "unknown"
    assert result.summary["agent_status"] == "unknown"
    assert result.summary["entry_issues"] == ["authenticated_agent_unverifiable"]
    assert result.summary["authenticated_agent_api"] == _module().authenticated_agent_api_fixture()
    assert not (Path(env["DEER_FLOW_HOME"]) / "users").exists()


def test_foreign_default_user_agent_is_refused_without_overwrite(
    project: tuple[Path, dict[str, str]],
) -> None:
    root, env = project
    env["DEER_FLOW_AUTH_DISABLED"] = "1"
    target = Path(env["DEER_FLOW_HOME"]) / AGENT_RELATIVE
    target.mkdir(parents=True)
    (target / "config.yaml").write_text("name: deep-research\ndescription: Foreign\n", encoding="utf-8")
    (target / "SOUL.md").write_text("Foreign state\n", encoding="utf-8")
    before = ((target / "config.yaml").read_bytes(), (target / "SOUL.md").read_bytes())
    module = _module()

    with pytest.raises(module.ConfigureError, match="entry.agent_ownership_conflict"):
        module.execute_configuration(root, env, mode="apply", online_detector=lambda: False)

    assert ((target / "config.yaml").read_bytes(), (target / "SOUL.md").read_bytes()) == before


def test_legacy_shared_agent_is_reported_and_never_migrated_or_overwritten(
    project: tuple[Path, dict[str, str]],
) -> None:
    root, env = project
    module = _module()
    module.execute_configuration(root, env, mode="apply", online_detector=lambda: False)
    env["DEER_FLOW_AUTH_DISABLED"] = "1"
    legacy = Path(env["DEER_FLOW_HOME"]) / "agents/deep-research"
    legacy.mkdir(parents=True)
    (legacy / "config.yaml").write_text("name: deep-research\n", encoding="utf-8")
    before = (legacy / "config.yaml").read_bytes()

    checked = module.execute_configuration(root, env, mode="check", online_detector=lambda: True)

    assert checked.runtime_config_ready is True
    assert checked.summary["agent_status"] == "not_ready"
    assert checked.summary["entry_issues"] == ["legacy_shared_agent"]
    with pytest.raises(module.ConfigureError, match="entry.legacy_shared_agent"):
        module.execute_configuration(root, env, mode="apply", online_detector=lambda: False)
    assert (legacy / "config.yaml").read_bytes() == before
    assert not (Path(env["DEER_FLOW_HOME"]) / AGENT_RELATIVE).exists()


@pytest.mark.parametrize("name", ["", "deep_research", "../deep-research", "deep research", "深度研究"])
def test_invalid_agent_name_is_rejected(name: str) -> None:
    module = _module()

    with pytest.raises(module.ConfigureError, match="entry.agent_name_invalid"):
        module.validate_agent_name(name)
