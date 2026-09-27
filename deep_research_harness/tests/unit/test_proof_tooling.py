"""The evidence tooling must fail loudly, not quietly.

@impl DRS-001
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[2]
RECEIPT = HARNESS / "scripts" / "proof_receipt.py"
MUTATION = HARNESS / "scripts" / "mutation_check.py"


def _run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=HARNESS,
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
    )


def test_receipt_self_test_rejects_planted_registry_violations() -> None:
    """The registry loader and the staleness rule have to fail on planted defects."""
    result = _run(RECEIPT, "self-test")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "surface map total" in result.stdout


def test_mutation_lane_self_test_reports_a_toothless_mutation() -> None:
    """A no-op mutation must be reported GREEN so the lane can fail on it."""
    result = _run(MUTATION, "--self-test")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "toothless mutation is reported GREEN" in result.stdout


def test_mutation_lane_fails_when_an_anchor_no_longer_matches(tmp_path: Path) -> None:
    """A rotted mutation entry must fail the lane instead of being skipped."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("mutation_check", MUTATION)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)

    rotted = module.Mutation(
        id="rotted",
        file="scripts/demo_tui.py",
        old="this anchor does not exist anywhere",
        new="",
        selector="tests/unit/test_proof_tooling.py",
        removes="nothing",
    )
    assert module.apply_mutation(rotted) == "ANCHOR-MISSING"


def test_receipt_verify_reports_a_missing_receipt(tmp_path: Path) -> None:
    """An absent receipt is not a pass."""
    result = _run(RECEIPT, "verify", "--lane", "verify")
    if (HARNESS.parent / ".proof" / "receipts" / "verify.json").is_file():
        assert result.returncode in {0, 1}
    else:
        assert result.returncode == 1
        assert "no receipt" in result.stdout
