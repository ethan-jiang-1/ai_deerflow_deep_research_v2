#!/usr/bin/env python3
"""Validate the dev-harness doc layer without external packages.

@impl PRS-020

Three mechanically checkable doc-layer rules:

1. ADR index <-> directory consistency: every ``NNNN-*.md`` in
   ``deep_research_harness/docs/adr/`` (excluding ``README.md``) is listed in the
   index table, and every ADR listed in the index exists on disk.
2. Entry-chain relative links resolve: every relative Markdown link in the
   entry-chain documents points to an existing file. ``http(s)``, ``mailto:``,
   bare ``#anchor``, and angle-bracket targets are ignored.
3. Entry-chain documents are UTF-8 and end with a trailing newline.

This checker is self-contained and standalone: it is NOT aggregated into
``check_project_gate.py`` (PRS-009 owns the six-component closeout) and is NOT
wired into the Harness ``make verify`` gate, which stays application-independent.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

ADR_DIR = Path("deep_research_harness/docs/adr")
ADR_INDEX = ADR_DIR / "README.md"
ENTRY_DOCS: tuple[str, ...] = (
    "AGENTS.md",
    "deep_research_harness/AGENTS.md",
    "deep_research_harness/CLAUDE.md",
    "deep_research_harness/README.md",
    "deep_research_harness/docs/README.md",
    "openspec/README.md",
)

ADR_FILE_RE = re.compile(r"^\d{4}-.*\.md$")
INDEX_ROW_RE = re.compile(r"^\|\s*(\d{4})\s*\|")
MARKDOWN_LINK_RE = re.compile(r"\]\(([^)\s][^)]*)\)")


def _adr_ids(adir: Path) -> set[str]:
    return {
        path.name[:4]
        for path in adir.glob("*.md")
        if path.name != "README.md" and ADR_FILE_RE.match(path.name)
    }


def _indexed_ids(index: Path) -> set[str]:
    text = index.read_text(encoding="utf-8")
    return {
        match.group(1)
        for line in text.splitlines()
        if (match := INDEX_ROW_RE.match(line))
    }


def _rule_adr_index(root: Path) -> list[str]:
    index = root / ADR_INDEX
    if not index.is_file():
        return [f"ADR index missing: {ADR_INDEX.as_posix()}"]
    present = _adr_ids(root / ADR_DIR)
    indexed = _indexed_ids(index)
    problems: list[str] = []
    missing = sorted(present - indexed)
    orphan = sorted(indexed - present)
    if missing:
        problems.append(f"ADR present but missing from index: {', '.join(missing)}")
    if orphan:
        problems.append(f"ADR index lists missing file: {', '.join(orphan)}")
    return problems


def _rule_links(root: Path) -> list[str]:
    problems: list[str] = []
    for rel in ENTRY_DOCS:
        doc = root / rel
        if not doc.is_file():
            problems.append(f"entry-chain document missing: {rel}")
            continue
        text = doc.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_RE.finditer(text):
            target = match.group(1).strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#", "<")):
                continue
            path_part = target.split("#", 1)[0].split("?", 1)[0].strip()
            if not path_part:
                continue
            resolved = (doc.parent / path_part).resolve()
            if not resolved.exists():
                problems.append(f"broken relative link in {rel}: {target}")
    return problems


def _rule_encoding_newline(root: Path) -> list[str]:
    problems: list[str] = []
    for rel in ENTRY_DOCS:
        doc = root / rel
        if not doc.is_file():
            continue  # missing doc already reported by the link rule
        try:
            text = doc.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append(f"non-UTF-8 entry-chain document: {rel}")
            continue
        if not text.endswith("\n"):
            problems.append(f"entry-chain document missing trailing newline: {rel}")
    return problems


def violations(root: Path) -> list[str]:
    found: list[str] = []
    found.extend(_rule_adr_index(root))
    found.extend(_rule_links(root))
    found.extend(_rule_encoding_newline(root))
    return found


def _self_test() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        def write_entry(rel: str, content: str) -> None:
            doc = base / rel
            doc.parent.mkdir(parents=True, exist_ok=True)
            doc.write_text(content, encoding="utf-8")

        # Clean fixture: one ADR + matching index entry; entries with a valid link.
        (base / ADR_DIR).mkdir(parents=True)
        (base / ADR_DIR / "0001-alpha.md").write_text("body\n", encoding="utf-8")
        (base / ADR_DIR / "README.md").write_text(
            "# ADR Index\n\n| 编号 | 一句话 | 生命周期 |\n|---|---|---|\n| 0001 | a | current |\n",
            encoding="utf-8",
        )
        for rel in ENTRY_DOCS:
            write_entry(rel, f"# T\n\n[self]({rel.rsplit('/', 1)[-1]})\n")

        if violations(base):
            errors.append("self-test: clean fixture must have zero violations")

        # Rule 1 negative: orphan index entry (lists 0002 which does not exist).
        index = base / ADR_DIR / "README.md"
        index.write_text(
            index.read_text(encoding="utf-8") + "| 0002 | b | current |\n",
            encoding="utf-8",
        )
        if not any("0002" in v for v in _rule_adr_index(base)):
            errors.append("self-test: ADR index orphan not detected")

        # Rule 2 negative: broken relative link.
        write_entry("deep_research_harness/README.md", "# T\n\nsee [gone.md](gone.md)\n")
        if not any("gone.md" in v for v in _rule_links(base)):
            errors.append("self-test: broken link not detected")

        # Rule 3 negative: missing trailing newline.
        write_entry("openspec/README.md", "# no newline")
        if not any("trailing newline" in v for v in _rule_encoding_newline(base)):
            errors.append("self-test: missing trailing newline not detected")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true", help="run negative-control fixtures")
    args = parser.parse_args()

    if args.self_test:
        errs = _self_test()
        if errs:
            print("doc-hygiene self-test FAILED:", file=sys.stderr)
            print("\n".join(f"- {e}" for e in errs), file=sys.stderr)
            return 1
        print("doc-hygiene self-test passed.")
        return 0

    found = violations(args.project_root.resolve())
    if found:
        print("doc-layer hygiene violations:", file=sys.stderr)
        print("\n".join(f"- {v}" for v in found), file=sys.stderr)
        return 1
    print("doc-layer hygiene passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
