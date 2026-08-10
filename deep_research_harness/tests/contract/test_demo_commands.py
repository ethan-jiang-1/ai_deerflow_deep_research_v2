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
    assert "ENTRY_RUN = PYTHONDONTWRITEBYTECODE=1 env -u VIRTUAL_ENV uv run --locked --no-sync" in makefile
    assert (
        "install:\n\tenv -u VIRTUAL_ENV uv sync --locked --extra operations --extra demo-tui --extra demo-real"
        in makefile
    )
    for target in (
        "demo",
        "demo-scripted",
        "demo-fixture-graph",
        "demo-real",
        "demo-real-scripted",
        "demo-tui",
        "demo-tui-fake",
        "demo-sessions",
        "session-workbench",
    ):
        assert f"{target}: entry-preflight" in makefile

    real_cli = " ".join(
        (
            "$(ENTRY_RUN) $(LOCAL_ENV_ARG) --extra operations --extra demo-real",
            "python scripts/demo_real.py $(DEMO_ARGS)",
        )
    )
    assert real_cli in makefile
    real_tui = " ".join(
        (
            "$(ENTRY_RUN) $(LOCAL_ENV_ARG) --extra operations --extra demo-real --extra demo-tui",
            "python scripts/demo_tui.py $(DEMO_ARGS)",
        )
    )
    assert real_tui in makefile
    fake_tui = " ".join(
        (
            f"{FIXTURE_PYTHONPATH} $(ENTRY_RUN) --extra operations --extra demo-tui",
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
        assert command.startswith(
            f"{DRY_RUN_FIXTURE_PYTHONPATH} PYTHONDONTWRITEBYTECODE=1 env -u VIRTUAL_ENV uv run --locked --no-sync"
        )

    real_targets = {
        "demo-real": "demo_real.py",
        "demo-real-scripted": "demo_real.py",
        "demo-tui": "demo_tui.py",
    }
    for target, script in real_targets.items():
        command = _dry_run_command(target, script)
        assert "src_fake" not in command
        assert "PYTHONDONTWRITEBYTECODE=1 env -u VIRTUAL_ENV uv run --locked --no-sync" in command


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


def test_readme_entry_surfaces_route_to_current_detail_owners() -> None:
    """@impl DRC-006"""
    readme = (AGENT_ROOT / "README.md").read_text(encoding="utf-8")

    assert readme.index("## Entry Surfaces") < readme.index("## Reading Map")
    surfaces = readme.split("## Entry Surfaces", 1)[1].split("## Reading Map", 1)[0]

    for heading in (
        "Surface",
        "Primary reader/user",
        "Purpose",
        "Actual composition",
        "Explicit non-goal",
    ):
        assert heading in surfaces

    for route in (
        "Dedicated Agent + reflected `deep_research` tool",
        "Standalone operator CLI",
        "Demo TUI visualizer",
        "Full-fake demonstrations",
        "Fixture-graph verification",
        "Configured-fixture local workbench",
    ):
        assert route in surfaces

    normalized_surfaces = surfaces.lower()
    for distinction in (
        "all real",
        "not a versioned product cli",
        "not a current primary user tui",
        "presentation, not fixture-graph verification",
        "configured fixture demo profile",
        "not a generic product ui",
    ):
        assert distinction in normalized_surfaces

    for detail_owner in (
        "docs/local-operations.md",
        "docs/runtime-architecture.md",
        "docs/testing-and-evaluation.md",
    ):
        assert detail_owner in surfaces


def test_retained_observation_documentation_uses_the_canonical_inspection_command() -> None:
    """@impl REC-005
    @impl REC-006
    """
    command = 'make demo-sessions DEMO_ARGS="inspect <bundle-id>"'
    retired = "DEMO_ARGS='<bundle_id>'"

    for path in (AGENT_ROOT / "README.md", AGENT_ROOT / "docs/local-operations.md"):
        document = path.read_text(encoding="utf-8")
        assert command in document
        assert retired not in document


def test_real_research_launcher_selects_a_configured_flash_model() -> None:
    launcher = REAL_RESEARCH_LAUNCHER.read_text(encoding="utf-8")

    assert "DEERFLOW_DEMO_MODEL=${DEERFLOW_DEMO_MODEL:-deepseek-v4-flash}" in launcher
    assert 'cd "$project_root"' in launcher
    assert 'python scripts/demo_real.py --scripted --question "$question"' in launcher
    assert "make entry-preflight" in launcher
    assert (
        "env -u VIRTUAL_ENV PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync "
        "--env-file .env --extra operations --extra demo-real"
    ) in launcher


def test_real_entries_reject_an_unselected_profile_before_adapter_or_bundle_composition() -> None:
    """@impl DPL-011

    The resolver is exercised with credentials but no selector. The entry-source
    assertions then keep that preflight on the only path before adapter creation,
    which is the first code able to create a local Bundle lifecycle.
    """

    import sys

    scripts = str(AGENT_ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from _demo_core import demo_readiness_report

    report = demo_readiness_report(
        mode="real",
        environ={"DEEPSEEK_API_KEY": "test-key", "TAVILY_API_KEY": "test-web-key"},
    )
    assert report.ready is False
    assert report.failure is not None
    assert report.failure.code.value == "configuration.model_missing"
    assert report.failure.journal_record_created is False

    cli = (AGENT_ROOT / "scripts" / "demo_real.py").read_text(encoding="utf-8")
    tui = (AGENT_ROOT / "scripts" / "demo_tui.py").read_text(encoding="utf-8")
    for source, preflight, rejection, adapter in (
        (
            cli,
            "report = await experience.preflight()",
            "if not report.ready:\n        return 2",
            "adapter = DemoAdapter.for_real()",
        ),
        (
            tui,
            "report = await self._experience.preflight()",
            "if not report.ready:\n            self.apply_run_update",
            'adapter = DemoAdapter.for_real() if self.mode == "real" else DemoAdapter()',
        ),
    ):
        assert source.index(preflight) < source.index(rejection) < source.index(adapter)

    launcher = REAL_RESEARCH_LAUNCHER.read_text(encoding="utf-8")
    assert "DEERFLOW_DEMO_MODEL=${DEERFLOW_DEMO_MODEL:-deepseek-v4-flash}" in launcher
    assert "export DEERFLOW_DEMO_MODEL" in launcher


def test_real_demo_calibration_documents_an_explicit_observational_procedure() -> None:
    """@impl DPL-012"""

    calibration_command = "DEERFLOW_DEMO_MODEL=<profile> make demo-real-scripted"
    inspection_command = 'make demo-sessions DEMO_ARGS="inspect <bundle-id>"'
    documents = (
        AGENT_ROOT / "README.md",
        AGENT_ROOT / "docs" / "local-operations.md",
        AGENT_ROOT / "run" / "README.md",
    )

    for path in documents:
        document = path.read_text(encoding="utf-8")
        normalized = " ".join(document.split())
        assert "## Bounded Real-Demo Calibration" in document
        assert calibration_command in document
        assert inspection_command in document
        assert "fresh Run Bundle" in normalized
        assert "does not qualify a model" in normalized
        assert "does not select or change a default model" in normalized

    makefile = MAKEFILE.read_text(encoding="utf-8")
    assert "DEERFLOW_DEMO_MODEL" not in _target_body(makefile, "demo-real-scripted")


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

    assert "session-workbench: entry-preflight" in makefile
    assert (
        f"{FIXTURE_PYTHONPATH} $(ENTRY_RUN) --extra operations --extra demo-tui "
        "python scripts/session_workbench.py $(DEMO_ARGS)"
    ) in makefile
    assert "not a Gateway, Web, upstream terminal, multi-user, or generic" in script
    assert "--profile" not in script
    assert "--path" not in script
