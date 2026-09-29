"""Navigation and command documentation integrity contracts.

These contracts derive expected commands from the authoritative Makefile and
local-operations text instead of hardcoding duplicated strings, so a future
target edit updates the documentation contract rather than silently breaking
a second copy.

@impl PRS-004
@impl DPL-005
@impl DPL-006
@impl LCP-002
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
AGENT_ROOT = REPO_ROOT / "deep_research_harness"
MAKEFILE = AGENT_ROOT / "Makefile"
ROOT_README = REPO_ROOT / "README.md"
HARNESS_README = AGENT_ROOT / "README.md"
LOCAL_OPERATIONS = AGENT_ROOT / "docs" / "local-operations.md"
RUN_README = AGENT_ROOT / "run" / "README.md"
BACKLOG_README = REPO_ROOT / "_backlog" / "README.md"
ROOT_AGENTS = REPO_ROOT / "AGENTS.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_deerflow_guide_surfaces_exist_and_digest_is_not_distributed() -> None:
    """Root guidance routes framework understanding to real read-only guide surfaces."""
    assert (REPO_ROOT / "deerflow/AGENTS.md").is_file()
    assert (REPO_ROOT / "deerflow/backend/AGENTS.md").is_file()
    agents = _text(ROOT_AGENTS)
    readme = _text(ROOT_README)
    assert "deerflow/_digest" not in agents
    assert "deerflow/_digest" not in readme
    assert "deerflow/AGENTS.md" in agents or "backend/AGENTS.md" in agents


def test_demo_real_examples_require_profile() -> None:
    """Every documented demo-real invocation carries the Makefile-required PROFILE."""
    makefile = _text(MAKEFILE)
    demo_real_target = re.search(r"^demo-real:.*?(?=^demo-real-embedded-smoke:)", makefile, re.MULTILINE | re.DOTALL)
    assert demo_real_target is not None
    assert "PROFILE" in demo_real_target.group(0)
    assert "DEERFLOW_DEMO_MODEL" not in demo_real_target.group(0)

    for readme in (ROOT_README, HARNESS_README, LOCAL_OPERATIONS, RUN_README):
        text = _text(readme)
        for line in text.splitlines():
            if re.search(r"make demo-real(?:-scripted)?(?:\s|$)", line) and "make demo-real-embedded-smoke" not in line:
                assert "PROFILE=" in line, f"demo-real example without PROFILE= in {readme.name}: {line.strip()}"
                assert "DEERFLOW_DEMO_MODEL" not in line, _make_var_leak_message(readme, line)


def _make_var_leak_message(readme: Path, line: str) -> str:
    return f"DEERFLOW_DEMO_MODEL used as make var in {readme.name}: {line.strip()}"


def test_demo_real_scripted_is_not_labeled_as_the_real_flow() -> None:
    """The demo-real-scripted entry is documented as scripted/embedded-smoke calibration."""
    makefile = _text(MAKEFILE)
    head, _, _ = makefile.partition("demo-real-scripted:")
    comment = head.rsplit("#", 1)[-1].strip()
    assert "embedded smoke" in comment
    assert "真实流程" not in _text(ROOT_README)


def test_backlog_paths_are_checkout_relative() -> None:
    """Backlog navigation uses this checkout's real submodule locations, not a retired root."""
    backlog = _text(BACKLOG_README)
    assert "/Users/bowhead/ai_deerflow_deep_research/" not in backlog
    assert "deerflow/backend" in backlog
    assert "deerflow/frontend" in backlog
    assert "deerflow/_digest" not in backlog


def test_cold_start_routing_reaches_the_entry_command_chooser() -> None:
    """A cold start reaches the entry-command chooser from resident guidance, not by guessing.

    Root AGENTS.md is the file every agent host loads before any work, so it must name the
    cheat sheet; otherwise the caller has to infer which of several "CLI"/"TUI" surfaces is
    meant. It must also route environment setup through the Makefile entry: a bare `uv sync`
    installs no demo extras and touches the global uv cache the Makefile deliberately avoids.
    """
    agents = _text(ROOT_AGENTS)
    assert "deep_research_harness/COMMANDS.md" in agents, (
        "root AGENTS.md must link the entry-command chooser so a cold start can pick a command"
    )
    assert "make install" in agents, "root AGENTS.md must route environment setup through make install"
    assert "uv sync" not in agents, (
        "root AGENTS.md must not present a bare uv sync recipe: it installs no demo extras and "
        "bypasses the Makefile's workspace uv cache"
    )
    assert "deep_research_harness/COMMANDS.md" in _text(ROOT_README), (
        "the product entry page must also route to the entry-command chooser"
    )
    commands = _text(AGENT_ROOT / "COMMANDS.md")
    assert "make demo-tui-real-auto" in commands, "the 010 auto-TUI entry must stay indexed in the chooser"
    assert "demo-tui-real-auto:" in _text(MAKEFILE), "the indexed 010 auto-TUI entry must remain a real target"


def test_commands_cheatsheet_make_targets_exist() -> None:
    """Every backticked `make <target>` the cheat sheet hands an operator is a real target."""
    makefile = _text(MAKEFILE)
    targets = set(re.findall(r"^([A-Za-z0-9_.-]+):", makefile, re.MULTILINE))
    referenced = {
        match.group(1)
        for span in re.findall(r"`([^`]+)`", _text(AGENT_ROOT / "COMMANDS.md"))
        for match in re.finditer(r"\bmake\s+([a-z][a-z0-9-]*)", span)
    }
    missing = sorted(target for target in referenced if target not in targets)
    assert not missing, f"COMMANDS.md names make targets that do not exist: {missing}"
