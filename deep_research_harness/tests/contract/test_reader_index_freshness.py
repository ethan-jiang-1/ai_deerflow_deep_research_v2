"""Reader-index freshness spot checks.

``src/deerflow_deep_research/runtime/README.md`` declares the rule itself: when
a row and its module docstring disagree, the docstring wins and the index is
fixed in the same PR. The 2026-09 fresh-agent audit found exactly that rule
broken twice: ``control.py`` was labeled a lifecycle shared control-plane (it
hosts only ``infra_probe``) and ``probe.py`` was labeled opt-in dev tooling (it
is the public ``infra_probe`` wiring). This test pins those two historically
drifted rows plus the docstring-side anchors. If a redesign changes a module's
role, update the docstring, the index row, and this tripwire in the same PR —
a red test here is the tripwire working as intended.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_PACKAGE = REPO_ROOT / "deep_research_harness" / "src" / "deerflow_deep_research" / "runtime"
RUNTIME_README = RUNTIME_PACKAGE / "README.md"
CONTROL_PY = RUNTIME_PACKAGE / "control.py"
PROBE_PY = RUNTIME_PACKAGE / "probe.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _module_row(readme: str, module_name: str) -> str:
    """Return the reader-index table row for one module (prose mentions excluded)."""
    match = re.search(rf"^\| `{re.escape(module_name)}` \|(.*)$", readme, re.MULTILINE)
    assert match is not None, f"runtime/README.md has no index row for {module_name}"
    return match.group(1)


def test_reader_index_declares_the_docstring_wins_rule() -> None:
    """The index keeps its own freshness contract visible to future editors."""
    readme = _text(RUNTIME_README)
    assert "docstring wins" in readme
    assert "not a second authority" in readme


def test_control_py_row_matches_its_probe_host_role() -> None:
    """``control.py`` is the infra_probe host, not a lifecycle control-plane owner."""
    row = _module_row(_text(RUNTIME_README), "control.py")
    assert "infra_probe" in row, f"control.py row lost its infra_probe anchor: {row.strip()}"
    if "lifecycle" in row:
        assert "bypass" in row, (
            "control.py row implies lifecycle ownership without the bypass caveat "
            f"(docstring: infra_probe only): {row.strip()}"
        )


def test_probe_py_row_matches_its_public_wiring_role() -> None:
    """``probe.py`` is the public infra_probe wiring, not opt-in dev tooling."""
    row = _module_row(_text(RUNTIME_README), "probe.py")
    assert "infra_probe" in row, f"probe.py row lost its infra_probe anchor: {row.strip()}"
    assert "opt-in" not in row and "opt in" not in row, (
        f"probe.py row relabeled as opt-in tooling (public advertised action): {row.strip()}"
    )


def test_docstring_side_anchors_still_hold() -> None:
    """The code-side docstrings still carry the claims the index mirrors."""
    control_docstring = _text(CONTROL_PY)
    assert "infra_probe" in control_docstring
    assert "production entry point" in control_docstring
    probe_docstring = _text(PROBE_PY)
    assert "infra_probe" in probe_docstring or "control" in probe_docstring.lower()
