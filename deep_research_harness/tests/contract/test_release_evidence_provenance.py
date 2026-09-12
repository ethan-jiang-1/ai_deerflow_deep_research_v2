"""Retained release-evidence routes remain discoverable after report retirement.

@impl EVH-005
"""

from __future__ import annotations

import json
from pathlib import Path

DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs"
EVIDENCE_ROOT = DOCS_ROOT / "evidence"
BASELINE = EVIDENCE_ROOT / "live-evaluation-baseline-2026-07-17.md"
ATTESTATION = EVIDENCE_ROOT / "release-attestation-2026-07-17.json"
REGRESSION_DESCENT = DOCS_ROOT / "regression-descent.md"
RETIRED_PARITY_REPORT_STEM = "d" + "pt" + "-invariant-parity-release-report-"


def test_retained_release_provenance_routes_need_no_superseded_report() -> None:
    assert not tuple(DOCS_ROOT.glob(f"{RETIRED_PARITY_REPORT_STEM}*.md"))

    baseline = BASELINE.read_text(encoding="utf-8")
    assert "legacy report schema" in baseline
    assert "observational evidence, not a release pass" in baseline
    assert "blocked after 3 internal attempts; no accepted record" in baseline
    assert "historical full-real acceptance proof is separately preserved" in baseline

    attestation = json.loads(ATTESTATION.read_text(encoding="utf-8"))
    assert attestation["scenario_id"] == "release-full-real-acceptance"
    assert attestation["source_observation_date"] == "2026-07-17"
    assert all(attestation["source_run"]["hard_invariants"].values())
    assert attestation["attestation_scan"] == {
        "credential_values_absent": True,
        "raw_host_paths_absent": True,
    }

    regression_descent = REGRESSION_DESCENT.read_text(encoding="utf-8")
    for discovery_id in (
        "LIVE-20260717-01",
        "LIVE-20260717-04",
        "LIVE-20260717-05",
        "RELEASE-20260717-01",
    ):
        assert discovery_id in regression_descent
    assert "provider-only-live" in regression_descent
    assert "Every live or release discovery is classified at the lowest stable seam." in regression_descent
