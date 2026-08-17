"""Process evidence for the prepared local demo-entry environment.

@impl DPL-005
@impl DPL-006
@impl LCP-002
@impl EVH-031
@impl EVH-032
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.periodic

REPO_ROOT = Path(__file__).resolve().parents[3]
AGENT_ROOT = REPO_ROOT / "deep_research_harness"
DEERFLOW_ROOT = REPO_ROOT / "deerflow"
CHILD_SECRET_KEYS = ("DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "TAVILY_API_KEY")
ENTRY_SETUP_MESSAGE = "Run 'make install' from deep_research_harness/."


def _copy_harness(tmp_path: Path) -> Path:
    copied_root = tmp_path / "repo"
    copied_harness = copied_root / "deep_research_harness"
    shutil.copytree(
        AGENT_ROOT,
        copied_harness,
        ignore=shutil.ignore_patterns(
            ".venv",
            ".env",
            ".deep-research-demo-runs",
            ".reports",
            ".pytest_cache",
            ".ruff_cache",
            ".node-prompt-review",
            "__pycache__",
        ),
    )
    # Local profile content is gitignored developer state and must never reach
    # the copied project; the test constructs the profile it checks itself.
    (copied_root / "profiles").mkdir()

    # The copied project uses the existing editable source path but never writes to it.
    os.symlink(DEERFLOW_ROOT, copied_root / "deerflow", target_is_directory=True)
    return copied_harness


def _write_hermetic_project_config(project: Path) -> None:
    """Deterministically construct the root config and the checked demo profile.

    The copied project must not depend on the developer machine's gitignored
    ``profiles/``, ``config.yaml``, or ``.env`` content: the launcher's minimal
    root config and the ``profile-check`` target's demo profile are test-owned
    fixtures with an isolated SQLite location.
    """
    copied_root = project.parent
    (copied_root / "config.yaml").write_text(
        "models:\n"
        "- name: deepseek-v4-flash\n"
        "  use: deerflow.models.patched_deepseek:PatchedChatDeepSeek\n"
        "  model: deepseek-v4-flash\n"
        "  api_key: $DEEPSEEK_API_KEY\n"
        "  base_url: https://api.deepseek.com/v1\n"
        "tools:\n"
        "- name: web_search\n"
        "  group: web\n"
        "  use: deerflow.community.tavily.tools:web_search_tool\n"
        "  api_key: $TAVILY_API_KEY\n"
        "  max_results: 5\n"
        "sandbox:\n"
        "  use: deerflow.sandbox.local:LocalSandboxProvider\n"
        "  allow_host_bash: true\n"
        "config_version: 19\n",
        encoding="utf-8",
    )
    demo_profile = copied_root / "profiles" / "demo"
    demo_profile.mkdir(parents=True, exist_ok=True)
    sqlite_dir = demo_profile / ".deer-flow" / "data"
    (demo_profile / "config.yaml").write_text(
        f"database:\n  backend: sqlite\n  sqlite_dir: {sqlite_dir}\n",
        encoding="utf-8",
    )
    (demo_profile / "extensions_config.json").write_text("{}\n", encoding="utf-8")


def _child_environment(*, foreign_virtual_env: bool = False) -> dict[str, str]:
    environment = os.environ.copy()
    for key in CHILD_SECRET_KEYS:
        environment.pop(key, None)
    environment.pop("VIRTUAL_ENV", None)
    environment.pop("UV_NO_SYNC", None)
    if foreign_virtual_env:
        environment["VIRTUAL_ENV"] = "/tmp/foreign-project/.venv"
    return environment


def _run(project: Path, *arguments: str, foreign_virtual_env: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["make", *arguments],
        cwd=project,
        env=_child_environment(foreign_virtual_env=foreign_virtual_env),
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )


def _launcher(project: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "run/real-research.sh"],
        cwd=project,
        env=_child_environment(foreign_virtual_env=True),
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )


def _setup_state(project: Path) -> tuple[str, tuple[tuple[str, int, int, str], ...]]:
    lock_digest = hashlib.sha256((project / "uv.lock").read_bytes()).hexdigest()
    environment_root = project / ".venv"
    entries: list[tuple[str, int, int, str]] = []
    for path in sorted(environment_root.rglob("*")):
        relative = path.relative_to(environment_root).as_posix()
        if path.is_symlink():
            entries.append((relative, 0, 0, f"link:{os.readlink(path)}"))
        elif path.is_dir():
            entries.append((relative, 0, path.stat().st_mtime_ns, "directory"))
        else:
            stat = path.stat()
            entries.append((relative, stat.st_size, stat.st_mtime_ns, "file"))
    return lock_digest, tuple(entries)


def _assert_state_unchanged(project: Path, command) -> subprocess.CompletedProcess[str]:
    before = _setup_state(project)
    completed = command()
    after = _setup_state(project)
    before_entries = dict((entry[0], entry[1:]) for entry in before[1])
    after_entries = dict((entry[0], entry[1:]) for entry in after[1])
    changed = sorted(
        path
        for path in before_entries.keys() | after_entries.keys()
        if before_entries.get(path) != after_entries.get(path)
    )
    assert after == before, completed.stdout + completed.stderr + "\nchanged environment entries: " + repr(changed[:20])
    return completed


def test_missing_or_incomplete_entry_environment_stops_before_an_adapter(tmp_path: Path) -> None:
    project = _copy_harness(tmp_path)

    missing = _run(project, "demo-scripted", "DEMO_ARGS=--help", foreign_virtual_env=True)

    assert missing.returncode != 0
    assert ENTRY_SETUP_MESSAGE in missing.stdout
    assert "full-fake standalone demo" not in missing.stdout
    assert "uv sync" not in missing.stdout

    setup = _run(project, "install")
    assert setup.returncode == 0, setup.stdout + setup.stderr
    complete = _run(project, "entry-preflight", foreign_virtual_env=True)
    assert complete.returncode == 0, complete.stdout + complete.stderr

    tavily_metadata = next((project / ".venv").rglob("tavily_python-*.dist-info"))
    tavily_metadata.rename(tavily_metadata.with_name(tavily_metadata.name + ".missing"))
    incomplete = _run(project, "demo-scripted", "DEMO_ARGS=--help", foreign_virtual_env=True)

    assert incomplete.returncode != 0
    assert ENTRY_SETUP_MESSAGE in incomplete.stdout
    assert "full-fake standalone demo" not in incomplete.stdout
    assert "uv sync" not in incomplete.stdout


def test_prepared_entries_preserve_dependency_state_and_keep_launcher_credential_bounded(tmp_path: Path) -> None:
    project = _copy_harness(tmp_path)
    setup = _run(project, "install")
    assert setup.returncode == 0, setup.stdout + setup.stderr
    assert _run(project, "entry-preflight", foreign_virtual_env=True).returncode == 0
    _write_hermetic_project_config(project)

    help_result = _assert_state_unchanged(
        project,
        lambda: _run(project, "demo", "DEMO_ARGS=--help", foreign_virtual_env=True),
    )
    assert help_result.returncode == 0, help_result.stdout + help_result.stderr

    fake = _assert_state_unchanged(project, lambda: _run(project, "demo-scripted", foreign_virtual_env=True))
    assert fake.returncode == 0, fake.stdout + fake.stderr
    bundle_match = re.search(r"Run Bundle: (b_[A-Za-z0-9_-]+)", fake.stdout)
    assert bundle_match is not None, fake.stdout
    bundle_id = bundle_match.group(1)

    fixture_graph = _assert_state_unchanged(
        project,
        lambda: _run(project, "demo-fixture-graph", foreign_virtual_env=True),
    )
    assert fixture_graph.returncode == 0, fixture_graph.stdout + fixture_graph.stderr

    inspection = _assert_state_unchanged(
        project,
        lambda: _run(project, "demo-sessions", f"DEMO_ARGS=inspect {bundle_id}", foreign_virtual_env=True),
    )
    assert inspection.returncode == 0, inspection.stdout + inspection.stderr
    assert "Event Journal is read-only; lifecycle controls remain independent." in inspection.stdout

    profile_check = _assert_state_unchanged(
        project,
        lambda: _run(project, "profile-check", "PROFILE=demo", foreign_virtual_env=True),
    )
    assert profile_check.returncode == 0, profile_check.stdout + profile_check.stderr

    workbench_help = _assert_state_unchanged(
        project,
        lambda: _run(project, "session-workbench", "DEMO_ARGS=--help", foreign_virtual_env=True),
    )
    assert workbench_help.returncode == 0, workbench_help.stdout + workbench_help.stderr

    # The test-owned empty dotenv prevents a developer credential file from reaching the launcher.
    (project / ".env").write_text("", encoding="utf-8")
    launcher = _assert_state_unchanged(project, lambda: _launcher(project))
    assert launcher.returncode != 0
    assert "本地前提检查已就绪" in launcher.stdout
    assert "结果类别: research.blocked" in launcher.stdout
    assert "TAVILY_API_KEY" not in launcher.stdout
    assert "DEEPSEEK_API_KEY" not in launcher.stdout

    before_concurrent = _setup_state(project)
    first = subprocess.Popen(
        ["make", "demo", "DEMO_ARGS=--help"],
        cwd=project,
        env=_child_environment(foreign_virtual_env=True),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    second = subprocess.Popen(
        ["make", "demo-sessions", "DEMO_ARGS=--help"],
        cwd=project,
        env=_child_environment(foreign_virtual_env=True),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    first_output, first_error = first.communicate(timeout=180)
    second_output, second_error = second.communicate(timeout=180)
    assert first.returncode == 0, first_output + first_error
    assert second.returncode == 0, second_output + second_error
    assert _setup_state(project) == before_concurrent
