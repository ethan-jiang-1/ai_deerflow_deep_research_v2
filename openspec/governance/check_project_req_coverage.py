#!/usr/bin/env python3
"""Verify requirement IDs have executable implementation evidence.

Application behavior is evidenced by deterministic test modules. OpenSpec-only
governance behavior may instead be evidenced by its implementing governance script.

@impl EVH-009
@impl EVH-010
"""

from __future__ import annotations

import ast
import io
import re
import sys
import tokenize
from pathlib import Path

from check_project_reqs import collect_active_main_requirements, parse_registry_ids

ID_RE = re.compile(r"[A-Z]{3}-\d{3}")
RANGE_RE = re.compile(r"([A-Z]{3})-(\d{3})\.\.(\d{3})")
REQ_HEADER_RE = re.compile(r"^\s*>\s*req:\s*(.+)$", re.MULTILINE)
REGISTRY_RE = re.compile(r"^([A-Z]{3}-\d{3}):", re.MULTILINE)
IMPL_LINE_RE = re.compile(r"@impl\s+([^\n]+)")


def _expand_ids(text: str) -> set[str]:
    ids = set(ID_RE.findall(text))
    for prefix, start, end in RANGE_RE.findall(text):
        first, last = int(start), int(end)
        if first <= last:
            ids.update(f"{prefix}-{value:03d}" for value in range(first, last + 1))
    return ids


def _declared_requirements(root: Path, entries: dict[str, str]) -> tuple[set[str], list[str]]:
    return collect_active_main_requirements(root, entries)


def _docstring_references(
    root: Path, paths: list[Path], *, require_test: bool
) -> tuple[set[str], list[str]]:
    references: set[str] = set()
    parse_errors: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            parse_errors.append(f"{path.relative_to(root)}:{exc.lineno}: test parse failed")
            continue
        has_test = any(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
            for node in ast.walk(tree)
        )
        if require_test and not has_test:
            continue
        docstrings: list[str] = []
        module_docstring = ast.get_docstring(tree, clean=False)
        if module_docstring:
            docstrings.append(module_docstring)
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                docstring = ast.get_docstring(node, clean=False)
                if docstring:
                    docstrings.append(docstring)
        for docstring in docstrings:
            for payload in IMPL_LINE_RE.findall(docstring):
                references.update(_expand_ids(payload))
    return references, parse_errors


def _evidence_references(root: Path) -> tuple[set[str], list[str]]:
    test_root = root / "deep_research_harness" / "tests"
    test_paths = sorted(test_root.rglob("test_*.py")) if test_root.exists() else []
    governance_root = root / "openspec" / "governance"
    governance_paths = sorted(governance_root.glob("*.py")) if governance_root.exists() else []
    references, errors = _docstring_references(root, test_paths, require_test=True)
    governance_references, governance_errors = _docstring_references(
        root, governance_paths, require_test=False
    )
    references.update(governance_references)
    errors.extend(governance_errors)
    return references, errors


def _source_location(root: Path, path: Path, line: int | None = None) -> str:
    relative = path.relative_to(root).as_posix()
    return f"{relative}:{line}" if line is not None else relative


def _docstring_records(tree: ast.AST) -> list[tuple[int | None, str]]:
    records: list[tuple[int | None, str]] = []
    module_docstring = ast.get_docstring(tree, clean=False)
    if module_docstring:
        first = getattr(tree, "body", [None])[0]
        records.append((getattr(first, "lineno", None), module_docstring))
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            docstring = ast.get_docstring(node, clean=False)
            if docstring:
                first = getattr(node, "body", [None])[0]
                records.append((getattr(first, "lineno", None), docstring))
    return records


def _production_references(root: Path, registered: set[str], retired: set[str]) -> list[str]:
    errors: list[str] = []
    source_root = root / "deep_research_harness" / "src"
    if not source_root.exists():
        return errors

    for path in sorted(source_root.rglob("*.py")):
        location = _source_location(root, path)
        try:
            with tokenize.open(path) as handle:
                source = handle.read()
        except (OSError, SyntaxError, UnicodeError) as exc:
            errors.append(f"production source decode failed: {location}: {exc}")
            continue

        try:
            tokens = tuple(tokenize.generate_tokens(io.StringIO(source).readline))
        except (IndentationError, SyntaxError, tokenize.TokenError) as exc:
            error_line = None
            if len(getattr(exc, "args", ())) > 1 and isinstance(exc.args[1], tuple):
                error_line = exc.args[1][0]
            errors.append(f"production source tokenize failed: {_source_location(root, path, error_line)}: {exc}")
            continue

        try:
            tree = ast.parse(source, filename=location)
        except (IndentationError, SyntaxError) as exc:
            errors.append(f"production source parse failed: {_source_location(root, path, exc.lineno)}: {exc.msg}")
            continue

        discoveries = _docstring_records(tree)
        discoveries.extend(
            (token.start[0], token.string) for token in tokens if token.type == tokenize.COMMENT
        )
        for line, text in discoveries:
            for payload in IMPL_LINE_RE.findall(text):
                for requirement_id in _expand_ids(payload):
                    source_location = _source_location(root, path, line)
                    if requirement_id not in registered:
                        errors.append(f"unknown production requirement: {requirement_id} at {source_location}")
                    elif requirement_id in retired:
                        errors.append(f"retired production requirement: {requirement_id} at {source_location}")
    return errors


def check(root: Path) -> list[str]:
    registry = root / "openspec" / "governance" / "req-registry.yaml"
    if not registry.exists():
        return [f"registry missing: {registry}"]
    entries = parse_registry_ids(registry.read_text(encoding="utf-8"))
    registered = set(entries)
    retired = {requirement_id for requirement_id, value in entries.items() if "DEPRECATED" in str(value).upper()}
    required, ownership_errors = _declared_requirements(root, entries)
    references, errors = _evidence_references(root)
    errors.extend(ownership_errors)
    errors.extend(_production_references(root, registered, retired))
    for requirement_id in sorted(references - registered):
        errors.append(f"unknown evidence requirement: {requirement_id}")
    for requirement_id in sorted(required - references):
        errors.append(f"uncovered requirement: {requirement_id}")
    return errors


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
    errors = check(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Requirement implementation evidence passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
