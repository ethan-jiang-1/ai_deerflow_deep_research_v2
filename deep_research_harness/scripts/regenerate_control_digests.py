#!/usr/bin/env python3
"""Regenerate or verify runtime-control digests in the source-controlled eval control corpus.

The live-corpus contract (src/deerflow_deep_research/runtime/evaluation/controls.py)
pins each case's runtime_controls to the exact source files they declare by sha256.
When a pinned source file changes (e.g. a prompt or domain module edit), the digest
must be re-pinned deliberately. This script performs that re-pin.

Usage:
    python scripts/regenerate_control_digests.py            # update stale digests in place
    python scripts/regenerate_control_digests.py --check    # verify only; exit non-zero on drift

It edits only the 64-hex digest values inside runtime_controls blocks; the rest of the
case JSON (hand-formatted compact style) is left byte-for-byte untouched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath

CONTROL_ROOT = Path(__file__).resolve().parents[1] / "evals" / "control"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _project_file(relative: str) -> Path:
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != relative:
        raise ValueError(f"unsafe source_path: {relative}")
    target = (PROJECT_ROOT / path).resolve(strict=True)
    try:
        target.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError(f"source_path escapes project root: {relative}") from exc
    if target.is_symlink() or not target.is_file():
        raise ValueError(f"source_path is not a regular file: {relative}")
    return target


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def iter_controls():
    registry_path = CONTROL_ROOT / "registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    for declaration in registry["cases"]:
        case_path = CONTROL_ROOT / declaration["case"]
        raw = case_path.read_text(encoding="utf-8")
        payload = json.loads(raw)
        controls = payload.get("fixture", {}).get("execution", {}).get("runtime_controls", [])
        for index, control in enumerate(controls):
            yield case_path, raw, index, control


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify only; do not write")
    args = parser.parse_args()

    drift: list[str] = []
    rewritten: list[str] = []
    total = 0
    seen_files: dict[Path, str] = {}
    for case_path, raw, index, control in iter_controls():
        try:
            source_path = _project_file(control["source_path"])
        except ValueError as exc:
            print(f"error: {case_path.name}[{index}]: {exc}", file=sys.stderr)
            return 2
        actual = _digest(source_path)
        declared = control.get("digest")
        total += 1
        if declared == actual:
            continue
        old = declared or "<missing>"
        drift.append(f"{case_path.name}[{index}] {control['source_path']} {old[:12]} -> {actual[:12]}")
        if args.check:
            continue
        if old not in raw:
            print(f"error: digest {old} not found verbatim in {case_path.name}", file=sys.stderr)
            return 2
        updated = raw.replace(old, actual)
        if updated == raw:
            print(f"error: replacement was a no-op for {case_path.name}", file=sys.stderr)
            return 2
        seen_files[case_path] = updated

    for case_path, updated in seen_files.items():
        case_path.write_text(updated, encoding="utf-8")
        rewritten.append(case_path.name)

    if args.check:
        if drift:
            print(f"runtime-control digest drift ({len(drift)} of {total}):")
            for line in drift:
                print("  " + line)
            return 1
        print(f"runtime-control digests verified ({total} controls).")
        return 0

    for line in drift:
        print("updated " + line)
    if rewritten:
        print(f"re-pinned {len(rewritten)} case file(s): {', '.join(rewritten)}")
    else:
        print(f"no drift ({total} controls).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
