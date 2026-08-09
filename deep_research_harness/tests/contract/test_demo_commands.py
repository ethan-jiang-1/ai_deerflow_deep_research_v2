"""Command contracts for the standalone fake and real demos.

@impl DPL-005
@impl DPL-008
@impl RED-002
@impl DPL-006
"""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
AGENT_ROOT = REPO_ROOT / "deep_research_harness"
MAKEFILE = AGENT_ROOT / "Makefile"
REAL_RESEARCH_LAUNCHER = AGENT_ROOT / "run" / "real-research.sh"
FIXTURE_PYTHONPATH = "PYTHONPATH=src_fake$${PYTHONPATH:+:$$PYTHONPATH}"
DRY_RUN_FIXTURE_PYTHONPATH = "PYTHONPATH=src_fake${PYTHONPATH:+:$PYTHONPATH}"


def _target_body(makefile: str, target: str) -> str:
    lines = makefile.splitlines()
    start = next(index for index, line in enumerate(lines) if line.startswith(f"{target}:"))
    command_lines: list[str] = []
    for line in lines[start + 1 :]:
        if not line.startswith("\t"):
            break
        command_lines.append(line)
    return "\n".join(command_lines)


def _dry_run_command(target: str, script: str) -> str:
    completed = subprocess.run(
        ["make", "--dry-run", target],
        cwd=AGENT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return next(line for line in completed.stdout.splitlines() if f"python scripts/{script}" in line)


def test_demo_commands_keep_fake_and_real_dependency_boundaries() -> None:
    """@impl DPL-005
    @impl RED-002
    """
    makefile = MAKEFILE.read_text(encoding="utf-8")
    readme = (AGENT_ROOT / "README.md").read_text(encoding="utf-8")
    operations = (AGENT_ROOT / "docs/local-operations.md").read_text(encoding="utf-8")

    assert "demo-fixture-graph demo-real demo-real-scripted demo-tui demo-tui-fake" in makefile
    real_cli = " ".join(
        (
            "env -u VIRTUAL_ENV uv run $(LOCAL_ENV_ARG) --extra operations --extra demo-real",
            "python scripts/demo_real.py $(DEMO_ARGS)",
        )
    )
    assert real_cli in makefile
    real_tui = " ".join(
        (
            "env -u VIRTUAL_ENV uv run $(LOCAL_ENV_ARG) --extra operations --extra demo-real --extra demo-tui",
            "python scripts/demo_tui.py $(DEMO_ARGS)",
        )
    )
    assert real_tui in makefile
    fake_tui = " ".join(
        (
            f"env -u VIRTUAL_ENV {FIXTURE_PYTHONPATH} uv run --extra operations --extra demo-tui",
            "python scripts/demo_tui.py --fake $(DEMO_ARGS)",
        )
    )
    assert fake_tui in makefile
    for target in (
        "demo",
        "demo-scripted",
        "demo-fixture-graph",
        "demo-tui-fake",
        "demo-sessions",
        "session-workbench",
    ):
        assert FIXTURE_PYTHONPATH in _target_body(makefile, target)
    for target in ("demo-real", "demo-real-scripted", "demo-tui"):
        assert FIXTURE_PYTHONPATH not in _target_body(makefile, target)
    assert "install:\n\tuv sync --locked --extra operations --extra demo-tui" in makefile
    assert "make demo-tui-fake" in readme
    assert "make demo-fixture-graph" in readme
    assert "deterministic graph-composition verification" in readme
    assert "full fake" in readme
    assert "docs/local-operations.md" in readme
    assert "TAVILY_API_KEY" in operations


def test_make_commands_scope_fixture_source_to_fixture_children() -> None:
    fixture_targets = {
        "demo": "demo.py",
        "demo-scripted": "demo.py",
        "demo-fixture-graph": "demo_fixture_graph.py",
        "demo-tui-fake": "demo_tui.py",
        "demo-sessions": "demo_sessions.py",
        "session-workbench": "session_workbench.py",
    }
    for target, script in fixture_targets.items():
        command = _dry_run_command(target, script)
        assert command.startswith(f"env -u VIRTUAL_ENV {DRY_RUN_FIXTURE_PYTHONPATH} uv run")

    real_targets = {
        "demo-real": "demo_real.py",
        "demo-real-scripted": "demo_real.py",
        "demo-tui": "demo_tui.py",
    }
    for target, script in real_targets.items():
        command = _dry_run_command(target, script)
        assert "src_fake" not in command


def test_fixture_graph_make_help_is_a_distinct_graph_verification_route() -> None:
    completed = subprocess.run(
        ["make", "demo-fixture-graph", "DEMO_ARGS=--help"],
        cwd=AGENT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "deterministic fixture-graph composition verification" in completed.stdout.lower()
    normalized = " ".join(completed.stdout.split())
    assert "not a replacement for make demo, make demo-scripted, or make demo-tui-fake" in normalized
    assert "--fake" not in completed.stdout


def test_readme_setup_commands_are_paste_safe_in_interactive_zsh() -> None:
    """@impl FCO-001"""
    readme = (AGENT_ROOT / "README.md").read_text(encoding="utf-8")
    setup = readme.split("## Quick Start", 1)[1].split("## Frequent Commands", 1)[0]

    assert "cd deep_research_harness\nmake install\nmake lock-check\nUV_OFFLINE=1 make verify" in setup
    assert "make install #" not in setup
    assert "UV_OFFLINE=1 make verify #" not in setup


def test_real_research_launcher_selects_a_configured_flash_model() -> None:
    launcher = REAL_RESEARCH_LAUNCHER.read_text(encoding="utf-8")

    assert "DEERFLOW_DEMO_MODEL=${DEERFLOW_DEMO_MODEL:-deepseek-v4-flash}" in launcher
    assert 'cd "$project_root"' in launcher
    assert 'python scripts/demo_real.py --scripted --question "$question"' in launcher
    assert "uv run --env-file .env --extra operations --extra demo-real" in launcher


def test_demo_help_describes_retained_inspection_without_promising_resume() -> None:
    """Run references are retained observations, not a second lifecycle contract."""
    scripts = AGENT_ROOT / "scripts"
    rendered_help = "\n".join(
        (scripts / name).read_text(encoding="utf-8") for name in ("demo.py", "demo_real.py", "demo_tui.py")
    )

    assert "temporary demo" not in rendered_help.lower()
    assert "durable session" not in rendered_help.lower()
    assert "inspection never resumes execution" in rendered_help
    assert "inspection is not cross-process resume" in rendered_help


def test_session_workbench_command_starts_only_the_fixed_local_profile_surface() -> None:
    """@impl RWB-001
    @impl RWB-004
    @impl REC-003
    """
    makefile = MAKEFILE.read_text(encoding="utf-8")
    script = (AGENT_ROOT / "scripts" / "session_workbench.py").read_text(encoding="utf-8")

    assert "session-workbench: profile-preflight" in makefile
    assert (
        f"env -u VIRTUAL_ENV {FIXTURE_PYTHONPATH} uv run --locked --no-sync --extra operations --extra demo-tui "
        "python scripts/session_workbench.py $(DEMO_ARGS)"
    ) in makefile
    assert "not a Gateway, Web, upstream terminal, multi-user, or generic" in script
    assert "--profile" not in script
    assert "--path" not in script
