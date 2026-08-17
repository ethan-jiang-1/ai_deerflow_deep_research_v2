#!/usr/bin/env python3
"""Reject downstream Harness dependencies on the upstream OpenSpec framework."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

FORBIDDEN = ("openspec/", "../openspec", "openspec.governance")
IGNORED_PARTS = frozenset({".venv", ".pytest_cache", "__pycache__", ".reports"})


def violations(root: Path) -> list[str]:
    harness = root / "deep_research_harness"
    found: list[str] = []
    for path in sorted(harness.rglob("*")):
        if not path.is_file() or IGNORED_PARTS.intersection(path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for token in FORBIDDEN:
            if token in text:
                found.append(f"{path.relative_to(root)}: forbidden downstream dependency {token!r}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path("."))
    args = parser.parse_args()
    found = violations(args.project_root.resolve())
    if found:
        print("\n".join(found), file=sys.stderr)
        return 1
    print("Harness dependency direction passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
