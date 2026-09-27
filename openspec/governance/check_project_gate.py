#!/usr/bin/env python3
"""OpenSpec root governance gate — orchestration-only aggregate over the six
registered component checkers.

This script owns NO rule semantics. Every semantic check lives in a component
checker; this gate only invokes the components from the repository root,
preserves their exact exit codes, prints one line per component with its exit
code and captured output, and aggregates to a final 0/1. It never parses delta
headers, requirement titles, or the registry, and it never writes anything.

Phases:

- `closeout` — runs the six default component checkers from the repository
  root, runs ALL of them even when one fails, and exits 0 only when every
  component exits 0. Fails closed on a missing/empty checker inventory, a
  missing checker file, or an unreadable registry.
- `plan --change NAME` — sequences the read-only admission owners for one
  active change: the Change Guidance checker (Focus Card / Program Focus
  grammar), the specification checker's selected-change scope (delta headers
  and titles), the requirement checker's planning scope (reservation /
  already-assigned / collision / reused-retired), and native strict change
  validation (MODIFIED requirement/scenario preservation). All subprocesses
  run from the repository root; each exact exit status is printed and
  propagated into the final exit code. Plan does NOT run unrelated
  project-wide full-tree checkers.

The hard stop this gate provides is in-repository workflow enforcement only:
it does not and cannot block a direct native `openspec archive` invocation
(external CLI is unmodifiable).

@impl DRC-010
@impl EVH-005
@impl PRS-009
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Fixed inventory: the registered OpenSpec component checkers.
# Keep the order stable; closeout aggregates these and nothing else.
CHECKER_NAMES: tuple[str, ...] = (
    "check_project_reqs.py",
    "check_project_specs.py",
    "check_project_architecture.py",
    "check_change_guidance.py",
    "check_project_req_coverage.py",
    "check_harness_dependency_direction.py",
    "check_proof_receipts.py",
)
REGISTRY_RELATIVE = Path("openspec") / "governance" / "req-registry.yaml"


def _default_root() -> Path:
    """Repository root derived from this script's location (openspec/governance/)."""
    return Path(__file__).resolve().parent.parent.parent


def _component_script(root: Path, name: str) -> Path:
    return root / "openspec" / "governance" / name


def _run(arguments: list[str], cwd: Path | None = None) -> tuple[int, str]:
    """Run one subprocess; returns (exit_code, output).

    `cwd` is the explicit working directory. Production callers always pass
    the resolved repository root (see `run_closeout`/`run_plan`), so every
    subprocess runs with cwd=repo root rather than inheriting an ambiguous
    caller cwd. Test runners may ignore `cwd` but must accept it.
    """
    try:
        completed = subprocess.run(
            arguments,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return 127, f"command not found: {arguments[0]}"
    except OSError as exc:
        return 126, f"failed to run {arguments[0]}: {exc}"
    output = completed.stdout or ""
    if completed.stderr:
        output += completed.stderr
    return completed.returncode, output


def _safe_run(runner, arguments: list[str], cwd: Path) -> tuple[int, str]:
    """Normalize any runner result into (exit_code, output) without crashing.

    The default `_run` already catches OSError; this wrapper additionally
    protects against injected runners that raise, so a runner failure fails
    closed with a useful captured result rather than aborting the gate.
    """
    try:
        return runner(arguments, cwd=cwd)
    except FileNotFoundError:
        return 127, f"command not found: {arguments[0]}"
    except OSError as exc:
        return 126, f"failed to run {arguments[0]}: {exc}"


def _registry_readable(root: Path) -> bool:
    try:
        return (root / REGISTRY_RELATIVE).is_file() and (root / REGISTRY_RELATIVE).read_text(
            encoding="utf-8"
        ).strip() != ""
    except (OSError, UnicodeError):
        return False


def _print_component(name: str, exit_code: int, output: str) -> None:
    print(f"[{name}] exit={exit_code}")
    if output:
        for line in output.rstrip("\n").split("\n"):
            print(f"  {line}")


def run_closeout(
    root: Path,
    runner=_run,
    checker_names: tuple[str, ...] | None = None,
) -> int:
    """Run every registered component checker; exit 0 only when all exit 0.

    `runner` and `checker_names` are injectable for deterministic tests;
    production callers use the default subprocess runner and the registered inventory.
    Every subprocess is invoked with an explicit cwd of the resolved
    repository root (never inherited from the caller's cwd).
    """
    names = CHECKER_NAMES if checker_names is None else checker_names
    if not names:
        print("Gate inventory is empty: no component checkers registered.", file=sys.stderr)
        return 1
    missing = [name for name in names if not _component_script(root, name).is_file()]
    if missing:
        print(f"Gate inventory references missing checker(s): {', '.join(missing)}", file=sys.stderr)
        return 1
    if not _registry_readable(root):
        print(f"Gate registry is missing or unreadable: {REGISTRY_RELATIVE}", file=sys.stderr)
        return 1

    all_zero = True
    for name in names:
        script = _component_script(root, name)
        # The proof-receipt checker runs in enforce mode at closeout (PRS-009): a
        # missing or stale receipt for a touched surface is a failure, not a warning.
        arguments = [sys.executable, str(script)]
        if name == "check_proof_receipts.py":
            arguments += ["--mode", "enforce"]
            # A closeout that has a selected-change attestation hands it over; without
            # one the checker reports 'no selected change' and exits 0.
            attestation = os.environ.get("PROOF_ATTESTATION", "")
            if attestation:
                arguments += ["--attestation", attestation]
        exit_code, output = _safe_run(runner, arguments, cwd=root)
        _print_component(name, exit_code, output)
        if exit_code != 0:
            all_zero = False
    if all_zero:
        print("OpenSpec governance closeout passed: every registered component checker exited 0.")
        return 0
    print("OpenSpec governance closeout failed: at least one component checker exited non-zero.", file=sys.stderr)
    return 1


def run_plan(root: Path, change_name: str, runner=_run) -> int:
    """Sequence the read-only admission owners for one selected active change.

    Every subprocess runs with an explicit cwd of the resolved repository
    root (never inherited from the caller's cwd).
    """
    if not change_name:
        print("--phase plan requires --change <name>.", file=sys.stderr)
        return 1
    missing = [name for name in CHECKER_NAMES if not _component_script(root, name).is_file()]
    if missing:
        print(f"Gate inventory references missing checker(s): {', '.join(missing)}", file=sys.stderr)
        return 1
    if not _registry_readable(root):
        print(f"Gate registry is missing or unreadable: {REGISTRY_RELATIVE}", file=sys.stderr)
        return 1

    steps: list[tuple[str, list[str]]] = [
        (
            "change-guidance",
            [sys.executable, str(_component_script(root, "check_change_guidance.py"))],
        ),
        (
            "delta-specs",
            [sys.executable, str(_component_script(root, "check_project_specs.py")), "--change", change_name],
        ),
        (
            "requirement-reservation",
            [sys.executable, str(_component_script(root, "check_project_reqs.py")), "--change", change_name],
        ),
        (
            "strict-validation",
            ["openspec", "validate", change_name, "--strict"],
        ),
    ]

    all_zero = True
    for label, arguments in steps:
        exit_code, output = _safe_run(runner, arguments, cwd=root)
        _print_component(label, exit_code, output)
        if exit_code != 0:
            all_zero = False
    if all_zero:
        print(f"OpenSpec planning admission passed for change {change_name}.")
        return 0
    print(f"OpenSpec planning admission failed for change {change_name}.", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        type=Path,
        default=None,
        help="repository root (default: derived from this script's location)",
    )
    parser.add_argument("--phase", choices=("plan", "closeout"), required=True)
    parser.add_argument(
        "--change",
        metavar="NAME",
        default=None,
        help="required for --phase plan: the active change to admit",
    )
    args = parser.parse_args()
    root = (args.project_root or _default_root()).resolve()
    if args.phase == "plan":
        return run_plan(root, args.change or "")
    if args.change is not None:
        print("--change is only valid with --phase plan.", file=sys.stderr)
        return 1
    return run_closeout(root)


if __name__ == "__main__":
    raise SystemExit(main())
