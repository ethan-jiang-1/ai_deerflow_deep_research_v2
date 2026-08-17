"""Retired test scaffolding remains outside the current test surface.

@impl PRS-001
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.check_test_assets import collect_pytest_selectors
from tests.assets.evidence import EVIDENCE_CLAIMS
from tests.assets.selection import FAST_PATHS, INTEGRATION_PATHS, LIVE_PATHS, PERIODIC_PATHS, WORKFLOW_PATHS

AGENT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = AGENT_ROOT.parent
RETIRED_E2E_DIRECTORY = "deep_research_harness/tests/e2e"
RETAINED_NON_EMPTY_DIRECTORIES = (
    "deep_research_harness/config",
    "deep_research_harness/docker",
    "deep_research_harness/scripts",
    "deep_research_harness/src/deerflow_deep_research/resources",
    "deep_research_harness/tests/fixtures",
    "deep_research_harness/tests/graph",
    "deep_research_harness/tests/integration",
    "deep_research_harness/tests/scenarios_periodic",
    "deep_research_harness/tests/unit",
)
SUSPENDED_SELECTOR = "tests/scenarios_suspended/test_evh_024_release_acceptance.py::test_full_real_release_acceptance"


def _tracked_residents(directory: str) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "ls-files", "--", directory],
        check=True,
        capture_output=True,
        text=True,
    )
    return {path for path in result.stdout.splitlines() if not path.endswith("/.gitkeep")}


def _collect(paths: tuple[str, ...], expression: str) -> set[str]:
    return collect_pytest_selectors(
        paths=paths,
        expression=expression,
        label="test structure retirement",
        allow_empty=True,
    )


def test_retained_test_roots_are_non_empty_and_e2e_has_no_active_surface() -> None:
    for directory in RETAINED_NON_EMPTY_DIRECTORIES:
        assert _tracked_residents(directory), directory

    assert not (REPO_ROOT / RETIRED_E2E_DIRECTORY).exists()

    active_paths = FAST_PATHS + INTEGRATION_PATHS + LIVE_PATHS + PERIODIC_PATHS + WORKFLOW_PATHS
    assert "tests/e2e" not in active_paths
    assert _collect(("tests",), "release_e2e") == {SUSPENDED_SELECTOR}
    assert (AGENT_ROOT / "tests/scenarios_suspended/test_evh_024_release_acceptance.py").is_file()
    assert SUSPENDED_SELECTOR not in {claim.selector for claim in EVIDENCE_CLAIMS}
