"""Human test-evidence guidance stays aligned without copying catalogs.

@impl EVH-001
@impl EVH-002
@impl EVH-005
@impl EVH-009
@impl EVH-010
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
AGENT_ROOT = REPO_ROOT / "deep_research_harness"


def test_testing_reference_owns_test_evidence_vocabulary_and_agent_guide_routes_to_policy() -> None:
    readme = (AGENT_ROOT / "docs/testing-and-evaluation.md").read_text(encoding="utf-8")
    guide = (AGENT_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    openspec_config = (REPO_ROOT / "openspec/config.yaml").read_text(encoding="utf-8")

    assert "TestEvidenceClaim" in readme
    assert "scripted case" in readme
    assert re.search(r"provider-shape\s+fixture", readme)
    assert re.search(r"persisted\s+trace replay", readme, flags=re.IGNORECASE)
    assert "evidence-v1" in readme
    assert "release-attestation-2026-07-17.json" in readme
    assert "scenarios_suspended/test_evh_024_release_acceptance.py" in readme
    assert "does not prove a current release result" in readme
    assert "test-entry-environment-regression" in readme
    assert "tests/scenarios_periodic/" in readme
    assert "180-second per-scenario duration" in readme
    assert "test-evidence-policy.md" in openspec_config
    assert "lowest responsible test seam" in readme
    assert "openspec/" not in guide


def test_live_baseline_and_workflow_disclose_current_partial_lane() -> None:
    baseline = (AGENT_ROOT / "docs/live-evaluation-baseline-2026-07-17.md").read_text(encoding="utf-8")
    workflow = (REPO_ROOT / ".github/workflows/agent-live-evaluation.yml").read_text(encoding="utf-8")

    assert "Four cases passed" in baseline
    assert "Wave2 synthesis failed closed" in baseline
    assert "targeted evidence failed closed" in baseline
    assert "workflow_dispatch:" in workflow
    assert "schedule:" not in workflow


def test_governance_bootstrap_pointers_remain_concise_and_aligned() -> None:
    config = (REPO_ROOT / "openspec/config.yaml").read_text(encoding="utf-8")
    governance = (REPO_ROOT / "openspec/governance/README.md").read_text(encoding="utf-8")

    assert "openspec/governance/test-evidence-policy.md" in config
    assert "test-evidence-policy.md" in governance
    assert "evaluation-hardening" in config
    assert "evaluation-hardening" in governance
