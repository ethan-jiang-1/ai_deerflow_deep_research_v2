"""Suspended full-real selector boundary.

@impl EVH-023
@impl EVH-024
@impl EVH-005
@impl EVH-032
"""

from __future__ import annotations

from pathlib import Path

from scripts.check_test_assets import collect_pytest_selectors
from tests.assets.evidence import EVIDENCE_CLAIMS, AssetClass, FocusedSelection
from tests.assets.selection import FAST_EXPRESSION, FAST_PATHS, PERIODIC_EXPRESSION, PERIODIC_PATHS

AGENT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = AGENT_ROOT.parent
SUSPENDED_SELECTOR = "tests/scenarios_suspended/test_evh_024_release_acceptance.py::test_full_real_release_acceptance"


def _collect(paths: tuple[str, ...], expression: str) -> set[str]:
    return collect_pytest_selectors(
        paths=paths,
        expression=expression,
        label="release suspension",
        allow_empty=True,
    )


def test_full_real_selector_is_retained_but_has_no_active_execution_surface() -> None:
    suspended_root = AGENT_ROOT / "tests/scenarios_suspended"
    assert (suspended_root / "test_evh_024_release_acceptance.py").is_file()
    assert _collect(("tests",), "release_e2e") == {SUSPENDED_SELECTOR}
    assert "release" not in {selection.value for selection in FocusedSelection}
    assert "release-acceptance" not in {asset_class.value for asset_class in AssetClass}
    assert SUSPENDED_SELECTOR not in {claim.selector for claim in EVIDENCE_CLAIMS}

    makefile = (AGENT_ROOT / "Makefile").read_text(encoding="utf-8")
    pr_workflow = (REPO_ROOT / ".github/workflows/agent-tests.yml").read_text(encoding="utf-8")
    assert "test-release-e2e" not in makefile
    assert "scenarios_suspended" not in makefile
    assert not (REPO_ROOT / ".github/workflows/agent-release-e2e.yml").exists()
    assert "agent-release-e2e.yml" not in pr_workflow

    pytest_config = (AGENT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "release_e2e: retained suspended full-real selector marker" in pytest_config
    assert _collect(PERIODIC_PATHS, PERIODIC_EXPRESSION) != {SUSPENDED_SELECTOR}

    suspended_readme = (suspended_root / "README.md").read_text(encoding="utf-8")
    assert "_backlog/_done/_suspended_plans/evh-024-release-acceptance-diagnosis.md" in suspended_readme
    assert "less than ten seconds" in suspended_readme.replace("\n", " ")


def test_bundle_authority_control_plane_remains_in_the_fast_lane() -> None:
    fast = _collect(FAST_PATHS, FAST_EXPRESSION)

    assert (
        "tests/unit/test_release_control_plane.py::test_release_scenario_owns_the_model_led_chinese_confirmation_transcript"
        in fast
    )
    assert (
        "tests/unit/test_release_control_plane.py::"
        "test_release_bundle_adapter_reauthorizes_the_public_id_before_observing_artifacts"
    ) in fast
    assert (AGENT_ROOT / "tests/scenarios/release.py").is_file()
    assert (AGENT_ROOT / "scripts/release_preflight.py").is_file()
