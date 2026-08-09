"""Local configuration profile contracts.

@impl LCP-001
@impl LCP-002
@impl LCP-003
@impl LCP-004
@impl LCP-005
@impl LCP-006
@impl PRS-006
@impl PRS-007
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
from ruamel.yaml import YAML

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "deep_research_harness" / "scripts" / "local_profiles.py"
ROOT_UPSTREAM_PATHS = (".gitignore", "Makefile", "README.md", "README_zh.md", "scripts", "backend", "frontend")


def test_profile_module_is_loaded_from_the_canonical_harness_root() -> None:
    """LCP-006: local profiles cannot route through a legacy project root."""
    assert SCRIPT_PATH == REPO_ROOT / "deep_research_harness" / "scripts" / "local_profiles.py"


def _module():
    spec = importlib.util.spec_from_file_location("deep_research_local_profiles", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def agent_project(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    agent = root / "deep_research_harness"
    agent.mkdir(parents=True)
    (root / "profiles").mkdir()
    (root / "scripts").mkdir()
    (root / "scripts" / "serve.sh").write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    (root / "config.yaml").write_text(
        "config_version: 19\n"
        "checkpointer:\n"
        "  type: sqlite\n"
        "database:\n"
        "  backend: postgres\n"
        "  postgres_url: $DATABASE_URL\n",
        encoding="utf-8",
    )
    (root / "extensions_config.json").write_text(
        '{"mcpServers": {}, "skills": {"example": {"enabled": true}}}\n', encoding="utf-8"
    )
    return agent


def _yaml(path: Path) -> dict:
    parser = YAML(typ="safe")
    with path.open(encoding="utf-8") as handle:
        loaded = parser.load(handle)
    assert isinstance(loaded, dict)
    return loaded


def test_profile_structure_is_project_owned_and_hook_free() -> None:
    registry = (REPO_ROOT / "openspec/governance/project-structure.toml").read_text(encoding="utf-8")

    assert 'path = "deep_research_harness/scripts/local_profiles.py"' in registry
    assert 'path = "deep_research_harness/tests/contract/test_local_profiles.py"' in registry
    assert 'path = "profiles"' in registry
    assert 'path = "profiles/README.md"' in registry
    assert 'path = "profiles/.gitignore"' in registry
    assert "profile_handoff.sh" not in registry
    assert 'path = "deep_research_harness/profiles"' not in registry
    assert 'path = "deep_research_harness/.gitignore"' in registry
    assert (REPO_ROOT / "deep_research_harness/.gitignore").read_text(encoding="utf-8") == (
        ".deep-research-demo-runs/\n.reports/\n.pytest_cache/\n.ruff_cache/\n.node-prompt-review/\nevals/runs/\n.venv/\n"
        ".agents/\n.claude/\n"
    )
    assert not (REPO_ROOT / "deep_research_harness/scripts/profile_handoff.sh").exists()
    assert not (REPO_ROOT / "deep_research_harness/profiles").exists()


@pytest.mark.parametrize("name", ["", "Demo", "demo_1", "-demo", "a" * 33, "demo/escape"])
def test_profile_name_rejects_unsafe_values(agent_project: Path, name: str) -> None:
    module = _module()

    with pytest.raises(module.ProfileError, match="profile_name_invalid"):
        module.profile_paths(agent_project, name)


def test_initialize_writes_only_project_profile_paths_and_preserves_root(agent_project: Path) -> None:
    module = _module()
    root = agent_project.parent
    before = {name: (root / name).read_bytes() for name in ("config.yaml", "extensions_config.json")}

    result = module.initialize_profile(agent_project, "demo")
    paths = module.profile_paths(agent_project, "demo")

    assert result.created is True
    assert paths.profile_dir == root / "profiles/demo"
    assert paths.home_dir == root / "profiles/demo/.deer-flow"
    assert paths.sqlite_dir == root / "profiles/demo/.deer-flow/data"
    assert "checkpointer" not in _yaml(paths.config_path)
    assert _yaml(paths.config_path)["database"] == {"backend": "sqlite", "sqlite_dir": str(paths.sqlite_dir)}
    assert json.loads(paths.extensions_path.read_text(encoding="utf-8"))["skills"]["example"]["enabled"] is True
    assert {name: (root / name).read_bytes() for name in before} == before
    assert not paths.home_dir.exists()
    assert not paths.sqlite_dir.exists()


def test_initialize_is_independent_snapshot_and_refuses_partial_pair(agent_project: Path) -> None:
    module = _module()
    root = agent_project.parent
    module.initialize_profile(agent_project, "demo")
    paths = module.profile_paths(agent_project, "demo")
    before = (paths.config_path.read_bytes(), paths.extensions_path.read_bytes())
    (root / "config.yaml").write_text("config_version: 20\ndatabase:\n  backend: memory\n", encoding="utf-8")

    assert module.initialize_profile(agent_project, "demo").created is False
    assert (paths.config_path.read_bytes(), paths.extensions_path.read_bytes()) == before

    partial = module.profile_paths(agent_project, "test")
    partial.profile_dir.mkdir(parents=True)
    partial.config_path.write_text("config_version: 19\n", encoding="utf-8")
    with pytest.raises(module.ProfileError, match="profile_pair_partial"):
        module.initialize_profile(agent_project, "test")
    assert not partial.extensions_path.exists()


def test_missing_root_config_does_not_create_profile(agent_project: Path) -> None:
    module = _module()
    (agent_project.parent / "config.yaml").unlink()

    with pytest.raises(module.ProfileError, match="profile_root_config_missing"):
        module.initialize_profile(agent_project, "demo")

    assert not (agent_project.parent / "profiles/demo").exists()


def test_initialize_uses_empty_extensions_when_root_extensions_are_absent(agent_project: Path) -> None:
    module = _module()
    (agent_project.parent / "extensions_config.json").unlink()

    module.initialize_profile(agent_project, "development")

    paths = module.profile_paths(agent_project, "development")
    assert json.loads(paths.extensions_path.read_text(encoding="utf-8")) == {"mcpServers": {}, "skills": {}}


def test_validation_returns_standard_environment_and_redacted_output(agent_project: Path) -> None:
    module = _module()
    module.initialize_profile(agent_project, "demo")
    result = module.validate_profile(agent_project, "demo")
    output = module.format_profile_check(result)

    assert result.environment == {
        "DEER_FLOW_PROJECT_ROOT": str(agent_project.parent),
        "DEER_FLOW_CONFIG_PATH": str(result.paths.config_path),
        "DEER_FLOW_EXTENSIONS_CONFIG_PATH": str(result.paths.extensions_path),
        "DEER_FLOW_HOME": str(result.paths.home_dir),
    }
    assert "demo" in output
    assert "SQLite" in output
    assert "restart" in output.lower()
    for forbidden in (str(agent_project), str(result.paths.config_path), str(result.paths.home_dir), "DATABASE_URL"):
        assert forbidden not in output


def test_validation_classifies_memory_database_as_ephemeral(agent_project: Path) -> None:
    module = _module()
    module.initialize_profile(agent_project, "test")
    paths = module.profile_paths(agent_project, "test")
    paths.config_path.write_text("config_version: 19\ndatabase:\n  backend: memory\n", encoding="utf-8")

    result = module.validate_profile(agent_project, "test")

    assert result.storage_kind == "memory"
    assert "ephemeral" in module.format_profile_check(result).lower()


@pytest.mark.parametrize(
    ("replacement", "code"),
    [
        ("database:\n  backend: postgres\n", "profile_database_backend"),
        ("database:\n  backend: sqlite\n  sqlite_dir: relative-db\n", "profile_sqlite_isolation"),
        (
            "checkpointer:\n  type: sqlite\ndatabase:\n  backend: sqlite\n  sqlite_dir: PLACEHOLDER\n",
            "profile_legacy_checkpointer",
        ),
    ],
)
def test_validation_rejects_unsupported_persistence(agent_project: Path, replacement: str, code: str) -> None:
    module = _module()
    module.initialize_profile(agent_project, "demo")
    paths = module.profile_paths(agent_project, "demo")
    paths.config_path.write_text(replacement.replace("PLACEHOLDER", str(paths.sqlite_dir)), encoding="utf-8")

    with pytest.raises(module.ProfileError, match=code):
        module.validate_profile(agent_project, "demo")


@pytest.mark.parametrize("path_name", ["profile_dir", "config_path", "extensions_path"])
def test_validation_rejects_symlinked_profile_paths(agent_project: Path, tmp_path: Path, path_name: str) -> None:
    module = _module()
    module.initialize_profile(agent_project, "demo")
    paths = module.profile_paths(agent_project, "demo")
    target = getattr(paths, path_name)
    if target.is_dir():
        for child in target.iterdir():
            child.unlink()
        target.rmdir()
    else:
        target.unlink()
    target.symlink_to(tmp_path / "outside")

    with pytest.raises(module.ProfileError, match="profile_path_unsafe"):
        module.validate_profile(agent_project, "demo")


def test_launch_uses_standard_environment_without_hook_or_skills_override(agent_project: Path) -> None:
    module = _module()
    module.initialize_profile(agent_project, "demo")
    observed: dict[str, object] = {}

    def executor(argv: list[str], env: dict[str, str]) -> None:
        observed["argv"] = argv
        observed["env"] = env

    module.launch_profile(
        agent_project,
        "demo",
        executor=executor,
        base_env={"KEEP": "1", "DEER_FLOW_SKILLS_PATH": "/outside/skills"},
    )

    assert observed["argv"] == [str(agent_project.parent / "scripts" / "serve.sh"), "--dev", "--skip-install"]
    assert observed["env"]["KEEP"] == "1"
    assert "BASH_ENV" not in observed["env"]
    assert "DEERFLOW_PROFILE_ROOT_ENV" not in observed["env"]
    assert "DEER_FLOW_SKILLS_PATH" not in observed["env"]


@pytest.mark.parametrize(
    "key",
    [
        "DEER_FLOW_CONFIG_PATH",
        "DEER_FLOW_EXTENSIONS_CONFIG_PATH",
        "DEER_FLOW_HOME",
        "DEER_FLOW_PROJECT_ROOT",
        "DEER_FLOW_SKILLS_PATH",
    ],
)
def test_root_dotenv_selector_conflict_stops_launch(agent_project: Path, key: str) -> None:
    module = _module()
    module.initialize_profile(agent_project, "demo")
    (agent_project.parent / ".env").write_text(f"OPENAI_API_KEY=secret\n{key}=wrong\n", encoding="utf-8")
    called = False

    def executor(argv: list[str], env: dict[str, str]) -> None:
        nonlocal called
        called = True

    with pytest.raises(module.ProfileError, match="profile_dotenv_conflict") as error:
        module.launch_profile(agent_project, "demo", executor=executor)

    assert key in error.value.detail
    assert "OPENAI_API_KEY=secret" not in error.value.detail
    assert "keep" in error.value.detail.lower()
    assert called is False


@pytest.mark.parametrize("line", ["export OPENAI_API_KEY=literal-token_123\n", "OPENAI_API_KEY='literal-token_123'\n"])
def test_literal_root_dotenv_is_accepted(agent_project: Path, line: str) -> None:
    module = _module()
    module.initialize_profile(agent_project, "demo")
    (agent_project.parent / ".env").write_text(line, encoding="utf-8")
    called = False

    def executor(argv: list[str], env: dict[str, str]) -> None:
        nonlocal called
        called = True

    module.launch_profile(agent_project, "demo", executor=executor)
    assert called is True


@pytest.mark.parametrize(
    "line",
    ["TOKEN=$(whoami)\n", "TOKEN=$HOME\n", "TOKEN=`whoami`\n", "TOKEN=one; echo two\n", "source other.env\n"],
)
def test_shell_like_root_dotenv_stops_launch(agent_project: Path, line: str) -> None:
    module = _module()
    module.initialize_profile(agent_project, "demo")
    (agent_project.parent / ".env").write_text(line, encoding="utf-8")

    with pytest.raises(module.ProfileError, match="profile_dotenv_invalid"):
        module.launch_profile(agent_project, "demo", executor=lambda _argv, _env: pytest.fail("must not launch"))


def test_invalid_launch_does_not_call_executor_or_create_runtime_state(agent_project: Path) -> None:
    module = _module()
    paths = module.profile_paths(agent_project, "demo")
    called = False

    def executor(argv: list[str], env: dict[str, str]) -> None:
        nonlocal called
        called = True

    with pytest.raises(module.ProfileError, match="profile_unknown"):
        module.launch_profile(agent_project, "demo", executor=executor)

    assert called is False
    assert not paths.home_dir.exists()


def test_profiles_are_distinct_and_listing_is_redacted(agent_project: Path) -> None:
    module = _module()
    module.initialize_profile(agent_project, "normal")
    module.initialize_profile(agent_project, "demo")
    normal = module.validate_profile(agent_project, "normal")
    demo = module.validate_profile(agent_project, "demo")

    assert normal.paths.home_dir != demo.paths.home_dir
    assert normal.paths.sqlite_dir != demo.paths.sqlite_dir
    assert str(agent_project) not in module.format_profile_list(module.list_profiles(agent_project))


def test_agent_make_profile_commands_are_setup_gated_and_local_only() -> None:
    output = subprocess.run(
        ["make", "-n", "profile-dev", "PROFILE=demo"],
        cwd=REPO_ROOT / "deep_research_harness",
        text=True,
        capture_output=True,
        check=True,
    ).stdout
    setup = subprocess.run(
        ["make", "-n", "profile-setup"],
        cwd=REPO_ROOT / "deep_research_harness",
        text=True,
        capture_output=True,
        check=True,
    ).stdout
    makefile = (REPO_ROOT / "deep_research_harness" / "Makefile").read_text(encoding="utf-8")

    assert "profile-preflight:" in makefile
    assert "uv run --locked --no-sync --extra operations" in output
    assert 'local_profiles.py launch "demo"' in output
    assert "profile-start" not in makefile
    assert "profile-dev-daemon" not in makefile
    assert "make -C ../deerflow install" in setup
    assert "$(MAKE) install" in makefile
    profile_setup = makefile.split("profile-setup:", 1)[1].split("\n\n", 1)[0]
    assert "uv sync --locked --extra operations" not in profile_setup


def test_profile_guide_and_ignore_rules_are_root_owned() -> None:
    guide = (REPO_ROOT / "profiles" / "README.md").read_text(encoding="utf-8")
    ignore = (REPO_ROOT / "profiles" / ".gitignore").read_text(encoding="utf-8")

    assert "make profile-setup" in guide
    assert "make profile-init PROFILE=demo" in guide
    assert "make profile-dev PROFILE=demo" in guide
    assert "*" in ignore
    assert "!.gitignore" in ignore
    assert "!README.md" in ignore
