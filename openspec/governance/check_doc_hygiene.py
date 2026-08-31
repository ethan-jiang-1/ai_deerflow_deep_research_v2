#!/usr/bin/env python3
"""Validate the dev-harness doc layer without external packages.

@impl PRS-020

Four mechanically checkable doc-layer rules:

1. ADR index <-> directory consistency: every ``NNNN-*.md`` in
   ``deep_research_harness/docs/adr/`` (excluding ``README.md``) is listed in the
   index table, and every ADR listed in the index exists on disk.
2. Relative links resolve: every relative Markdown link in the entry-chain
   documents and in the docs-layer documents points to an existing file.
   ``http(s)``, ``mailto:``, bare ``#anchor``, and angle-bracket targets are
   ignored.
3. Entry-chain and docs-layer documents are UTF-8 and end with a trailing newline.
4. Docs-layer scope completeness: every Markdown document actually present under
   ``deep_research_harness/docs/`` is registered in ``DOC_LAYER_DOCS``, so coverage
   cannot silently shrink when new documents are added. Registered but absent
   documents are reported by rules 2 and 3 instead.

A docs-layer document is a Markdown document under ``deep_research_harness/docs/``
— the top-level ``docs/*.md`` documents and the ``docs/adr/*.md`` decision
records. Non-Markdown files under that tree are out of scope. The scope is an
explicit enumeration: adding a docs document without registering it here turns
rule 4 red on the next run.

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
DOCS_TREE = Path("deep_research_harness/docs")
ADR_INDEX = ADR_DIR / "README.md"
ENTRY_DOCS: tuple[str, ...] = (
    "AGENTS.md",
    "deep_research_harness/AGENTS.md",
    "deep_research_harness/CLAUDE.md",
    "deep_research_harness/README.md",
    "deep_research_harness/docs/README.md",
    "openspec/README.md",
)
DOC_LAYER_DOCS: tuple[str, ...] = (
    # docs/ top-level markdown documents.
    "deep_research_harness/docs/README.md",
    "deep_research_harness/docs/cognitive-evaluation-suite.md",
    "deep_research_harness/docs/deep-research-topology.md",
    "deep_research_harness/docs/live-evaluation-baseline-2026-07-17.md",
    "deep_research_harness/docs/local-operations.md",
    "deep_research_harness/docs/regression-descent.md",
    "deep_research_harness/docs/run-lifecycle-walkthrough.md",
    "deep_research_harness/docs/runtime-architecture.md",
    "deep_research_harness/docs/testing-and-evaluation.md",
    # docs/adr/ decision records and their index.
    "deep_research_harness/docs/adr/0001-real-smoke-test-completes-a-bounded-research-outcome.md",
    "deep_research_harness/docs/adr/0002-tui-is-the-primary-user-interface.md",
    "deep_research_harness/docs/adr/0003-deployment-owns-research-service-configuration.md",
    "deep_research_harness/docs/adr/0004-system-owns-routine-research-recovery.md",
    "deep_research_harness/docs/adr/0005-every-new-research-has-a-lightweight-confirmation.md",
    "deep_research_harness/docs/adr/0006-layered-support-disclosure.md",
    "deep_research_harness/docs/adr/0007-primary-user-research-sessions-are-durable.md",
    "deep_research_harness/docs/adr/0008-start-with-a-local-first-tui.md",
    "deep_research_harness/docs/adr/0009-research-completes-with-an-interpretable-report.md",
    "deep_research_harness/docs/adr/0010-completed-reports-remain-portable-in-local-first.md",
    "deep_research_harness/docs/adr/0011-node-cognitive-control-is-a-first-class-program.md",
    "deep_research_harness/docs/adr/0012-node-control-contract-precedes-implementation.md",
    "deep_research_harness/docs/adr/0013-cognitive-evaluations-live-outside-pytest.md",
    "deep_research_harness/docs/adr/0014-cognitive-evaluations-have-four-honest-outcomes.md",
    "deep_research_harness/docs/adr/0015-runner-and-evaluator-are-separate-programs.md",
    "deep_research_harness/docs/adr/0016-evaluation-agent-is-review-only.md",
    "deep_research_harness/docs/adr/0017-node-runs-lead-flow-runs.md",
    "deep_research_harness/docs/adr/0018-evaluation-runs-use-fresh-isolated-bundles.md",
    "deep_research_harness/docs/adr/0019-keep-v1-evaluation-review-simple.md",
    "deep_research_harness/docs/adr/0020-runner-executes-once.md",
    "deep_research_harness/docs/adr/0021-runner-cases-and-bundles-have-explicit-observations.md",
    "deep_research_harness/docs/adr/0022-people-initiate-evaluation-review.md",
    "deep_research_harness/docs/adr/0023-reviews-are-separate-immutable-records.md",
    "deep_research_harness/docs/adr/0024-review-records-are-traceable.md",
    "deep_research_harness/docs/adr/0025-rubrics-are-case-specific-review-authorities.md",
    "deep_research_harness/docs/adr/0026-evaluation-control-and-run-data-are-separate.md",
    "deep_research_harness/docs/adr/0027-model-led-research-confirmation-uses-deterministic-fact-admission.md",
    "deep_research_harness/docs/adr/0028-deep-research-harness-is-the-downstream-module-root.md",
    "deep_research_harness/docs/adr/README.md",
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


def _read_utf8(doc: Path) -> tuple[str | None, str | None]:
    """Return (text, None) or (None, problem) for an undecodable document."""
    try:
        return doc.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        return None, "not UTF-8 decodable"


def _rule_links(root: Path) -> list[str]:
    problems: list[str] = []
    for kind, rels in (("entry-chain", ENTRY_DOCS), ("docs-layer", DOC_LAYER_DOCS)):
        for rel in rels:
            doc = root / rel
            if not doc.is_file():
                problems.append(f"{kind} document missing: {rel}")
                continue
            text, decode_problem = _read_utf8(doc)
            if text is None:
                problems.append(f"non-UTF-8 {kind} document, links not checked: {rel}")
                continue
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
    for kind, rels in (("entry-chain", ENTRY_DOCS), ("docs-layer", DOC_LAYER_DOCS)):
        for rel in rels:
            doc = root / rel
            if not doc.is_file():
                continue  # missing doc already reported by the link rule
            text, decode_problem = _read_utf8(doc)
            if text is None:
                problems.append(f"non-UTF-8 {kind} document: {rel}")
                continue
            if not text.endswith("\n"):
                problems.append(f"{kind} document missing trailing newline: {rel}")
    return problems


def _rule_docs_scope(root: Path) -> list[str]:
    """Reject present docs-tree markdown that the registered scope omits."""
    tree = root / DOCS_TREE
    if not tree.is_dir():
        return []
    registered = set(DOC_LAYER_DOCS)
    problems: list[str] = []
    for path in sorted(tree.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        if rel not in registered:
            problems.append(f"docs-layer markdown not in registered scope: {rel}")
    return problems


def violations(root: Path) -> list[str]:
    found: list[str] = []
    found.extend(_rule_adr_index(root))
    found.extend(_rule_links(root))
    found.extend(_rule_encoding_newline(root))
    found.extend(_rule_docs_scope(root))
    return found


def _self_test() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        def write_doc(rel: str, content: str) -> None:
            doc = base / rel
            doc.parent.mkdir(parents=True, exist_ok=True)
            doc.write_text(content, encoding="utf-8")

        # Clean fixture: every registered document exists with a valid self link,
        # and the ADR index lists every registered ADR id. Derived from the
        # constants so the fixture follows future scope changes.
        for rel in ENTRY_DOCS:
            write_doc(rel, f"# T\n\n[self]({rel.rsplit('/', 1)[-1]})\n")
        adr_ids: list[str] = []
        for rel in DOC_LAYER_DOCS:
            name = rel.rsplit("/", 1)[-1]
            write_doc(rel, f"# T\n\n[self]({name})\n")
            if ADR_FILE_RE.match(name):
                adr_ids.append(name[:4])
        index_rows = "".join(f"| {adr_id} | a | current |\n" for adr_id in sorted(adr_ids))
        write_doc(
            ADR_INDEX.as_posix(),
            "# ADR Index\n\n| 编号 | 一句话 | 生命周期 |\n|---|---|---|\n" + index_rows,
        )

        if violations(base):
            errors.append("self-test: clean fixture must have zero violations")

        # Rule 1 negative: orphan index entry (lists an absent ADR id).
        index = base / ADR_INDEX
        original_index = index.read_text(encoding="utf-8")
        index.write_text(original_index + "| 9999 | b | current |\n", encoding="utf-8")
        if not any("9999" in v for v in _rule_adr_index(base)):
            errors.append("self-test: ADR index orphan not detected")
        index.write_text(original_index, encoding="utf-8")

        # Rule 2 negative (entry-chain): broken relative link.
        write_doc("deep_research_harness/README.md", "# T\n\nsee [gone.md](gone.md)\n")
        if not any("gone.md" in v for v in _rule_links(base)):
            errors.append("self-test: broken link not detected")

        # Rule 3 negative (entry-chain): missing trailing newline.
        write_doc("openspec/README.md", "# no newline")
        if not any("trailing newline" in v for v in _rule_encoding_newline(base)):
            errors.append("self-test: missing trailing newline not detected")

        # Rule 2 negative (docs-layer): broken relative link.
        write_doc(
            "deep_research_harness/docs/local-operations.md",
            "# T\n\nsee [gone.md](gone.md)\n",
        )
        if not any("gone.md" in v for v in _rule_links(base)):
            errors.append("self-test: docs-layer broken link not detected")

        # Rule 3 negative (docs-layer): missing trailing newline.
        write_doc("deep_research_harness/docs/regression-descent.md", "# no newline")
        if not any(
            "docs-layer document missing trailing newline" in v
            for v in _rule_encoding_newline(base)
        ):
            errors.append("self-test: docs-layer missing trailing newline not detected")

        # Rule 3 negative (docs-layer): non-UTF-8 bytes.
        bad = base / "deep_research_harness/docs/cognitive-evaluation-suite.md"
        bad.write_bytes(b"\xff\xfe binary")
        if not any(
            "non-UTF-8 docs-layer document" in v
            for v in _rule_encoding_newline(base)
        ):
            errors.append("self-test: docs-layer non-UTF-8 not detected")

        # Rule 4 negative: present docs markdown missing from the registered scope.
        write_doc("deep_research_harness/docs/zz-unregistered.md", "# extra\n")
        if not any("zz-unregistered.md" in v for v in _rule_docs_scope(base)):
            errors.append("self-test: unregistered docs-layer markdown not detected")

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
