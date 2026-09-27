"""Mutation lane: apply each registered mutation and require its guard to go red.

A guard nobody can make fail is not evidence, so this lane fails when a mutation
leaves its selector green or when its anchor no longer matches the file (change
`add-evidence-receipts-and-proof-lanes`).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HARNESS))
from tests.mutations.registry import MUTATIONS, Mutation  # noqa: E402

SENTINEL = "mutation-check: every guard went red"


def _run_selector(selector: str) -> int:
    run = subprocess.run(
        [sys.executable, "-m", "pytest", selector, "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=HARNESS,
        capture_output=True,
        text=True,
        check=False,
    )
    Path("/tmp").joinpath("mutation-last.log").write_text((run.stdout or "") + (run.stderr or ""), encoding="utf-8")
    return run.returncode


def apply_mutation(mutation: Mutation) -> str:
    """Return RED, GREEN or ANCHOR-MISSING; always restores the file."""
    path = HARNESS / mutation.file
    original = path.read_text(encoding="utf-8")
    if mutation.old not in original:
        return "ANCHOR-MISSING"
    path.write_text(original.replace(mutation.old, mutation.new, 1), encoding="utf-8")
    try:
        return "RED" if _run_selector(mutation.selector) != 0 else "GREEN"
    finally:
        path.write_text(original, encoding="utf-8")


def self_test() -> int:
    """A planted toothless mutation must be reported GREEN, which fails the lane."""
    toothless = Mutation(
        id="self-test-toothless",
        file="scripts/mutation_check.py",
        old='SENTINEL = "mutation-check: every guard went red"',
        new='SENTINEL = "mutation-check: every guard went red"  # no-op',
        selector="tests/integration/test_debug_driver_matrix.py::test_drive_until_stops_at_the_hitl_boundary_once",
        removes="nothing at all",
    )
    verdict = apply_mutation(toothless)
    if verdict != "GREEN":
        print(f"self-test FAILED: a no-op mutation was reported {verdict}, expected GREEN")
        return 1
    print("mutation-check self-test: OK (a toothless mutation is reported GREEN and fails the lane)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", default="")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()

    selected = [m for m in MUTATIONS if args.only.lower() in m.id.lower()]
    bad: list[str] = []
    for mutation in selected:
        verdict = apply_mutation(mutation)
        mark = "RED  " if verdict == "RED" else f"*** {verdict} ***"
        print(f"  [{mark}] {mutation.id}  ({mutation.removes})")
        if verdict != "RED":
            bad.append(mutation.id)
    print(f"mutations: {len(selected) - len(bad)}/{len(selected)} went red")
    for mutation_id in bad:
        print(f"  no teeth: {mutation_id} (see /tmp/mutation-last.log)")
    if bad:
        print("MUTATION CHECK FAILED: a guard stayed green")
        return 1
    print(SENTINEL)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
