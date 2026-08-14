"""Regression coverage for main-spec requirement declaration sources.

@impl EVH-010
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
GOVERNANCE_ROOT = PROJECT_ROOT / "openspec" / "governance"
if str(GOVERNANCE_ROOT) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_ROOT))

from check_project_reqs import _header_ids  # noqa: E402

BASELINE_MISSING_MAIN_SPEC_REQUIREMENTS = {
    "bootstrap-node": {"BON-007"},
    "cognitive-evaluation-suite": {"CES-008"},
    "deep-research-agent-charter": {"DRC-011"},
    "deep-research-harness-run-bundles": {
        "DRH-001",
        "DRH-002",
        "DRH-003",
        "DRH-004",
        "DRH-005",
        "DRH-006",
        "DRH-007",
        "DRH-008",
    },
    "demo-pipeline": {"DPL-010"},
    "deployment-configuration": {"DEC-006"},
    "evaluation-hardening": {"EVH-025", "EVH-026"},
    "fixture-source-isolation": {"FSI-003"},
    "hitl1-node": {"HIN-015"},
    "local-configuration-profiles": {"LCP-006"},
    "node-agent-runtime": {"NOA-014"},
    "project-structure": {"PRS-017"},
    "research-cli-onboarding": {"REC-008"},
    "research-demo-tui": {"RED-008"},
    "research-fake-cli-onboarding": {"FCO-002"},
    "research-graph-lifecycle": {"REG-020"},
    "research-local-session-workbench": {"RWB-008"},
    "research-run-experience": {"RER-013"},
    "run-bundle-artifact-view": {"RSV-004"},
    "run-bundle-discovery-and-operations": {"RDO-007"},
    "topic-planning-node": {"TOP-008"},
    "runtime-integration": {"RUI-010", "RUI-011"},
    "wave1-node": {"WON-009"},
    "wave2-synthesis-node": {"WSN-007"},
    "work-unit-kernel": {"WOU-011"},
}


def test_baseline_impl_declarations_are_owned_by_main_spec_headers() -> None:
    missing_by_capability = {
        capability: sorted(
            requirement_ids
            - _header_ids((PROJECT_ROOT / "openspec" / "specs" / capability / "spec.md").read_text(encoding="utf-8"))
        )
        for capability, requirement_ids in BASELINE_MISSING_MAIN_SPEC_REQUIREMENTS.items()
    }

    assert missing_by_capability == {capability: [] for capability in BASELINE_MISSING_MAIN_SPEC_REQUIREMENTS}
