"""Current node-language surface contract.

@impl NC-C02
@impl OR-C03
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = ROOT / "deep_research_harness" / "src" / "deerflow_deep_research"
TEST_ROOT = ROOT / "deep_research_harness" / "tests"
SCRIPT_ROOT = ROOT / "deep_research_harness" / "scripts"
MAIN_SPEC_PATHS = tuple(
    ROOT / "openspec" / "specs" / capability / "spec.md"
    for capability in (
        "node-agent-capabilities",
        "node-agent-runtime",
        "node-prompt-catalog",
        "cognitive-program-evidence",
        "workflow-failure-outcomes",
        "research-run-experience",
    )
)
POLICY_AND_RECORD_PATHS = (
    ROOT
    / "deep_research_harness"
    / "src"
    / "deerflow_deep_research"
    / "resources"
    / "node_agent"
    / "runtime_policy.md",
    ROOT / "deep_research_harness" / "docs" / "testing-and-evaluation.md",
    ROOT / "openspec" / "governance" / "req-registry.yaml",
)
_RETIRED_PATTERNS = (
    re.compile("Phase" + " Agent"),
    re.compile("phase" + "-agent"),
    re.compile("Phase" + "Agent"),
    re.compile("phase" + "_agent"),
    re.compile("PHASE" + "_AGENT"),
    re.compile("_".join(("capability", "binding"))),
)
_WFO_LEGACY_SCENARIO = "#### Scenario: A direct phase preserves a closed " + "phase" + "-agent stop"


def _current_surface_paths() -> tuple[Path, ...]:
    return tuple(
        sorted(
            {
                *SOURCE_ROOT.rglob("*.py"),
                *TEST_ROOT.rglob("*.py"),
                *SCRIPT_ROOT.rglob("*.py"),
                *MAIN_SPEC_PATHS,
                *POLICY_AND_RECORD_PATHS,
            }
        )
    )


def _retired_identity_violations() -> set[str]:
    violations: set[str] = set()
    for path in _current_surface_paths():
        assert path.is_file(), path
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if path == MAIN_SPEC_PATHS[4] and line == _WFO_LEGACY_SCENARIO:
                continue
            if any(pattern.search(line) for pattern in _RETIRED_PATTERNS):
                violations.add(f"{path.relative_to(ROOT)}:{line_number}")
    return violations


def test_current_node_language_has_no_retired_identity_or_capability_contract() -> None:
    assert _retired_identity_violations() == set()


def test_node_edit_map_keeps_only_its_explicit_retired_term_supersession_note() -> None:
    node_edit_map = ROOT / "openspec" / "change-guidance" / "node-edit-map.md"
    text = node_edit_map.read_text(encoding="utf-8")

    assert text.count("Phase" + " Agent") == 1
    assert "superseded by node-agent /" in text
    assert "MD controller" in text
