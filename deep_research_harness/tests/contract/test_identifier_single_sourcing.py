"""Identifier single-sourcing and dead-code retirement contract.

Asserts that canonical identifiers have exactly one definition in the source
tree, that no module defines the full 11-phase name list inline, and that the
retired symbols/modules are absent. This is the red-first gate for the
single-source identifiers refactor.

@impl WOU-001
"""

from __future__ import annotations

import ast
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[2]
SRC = AGENT_ROOT / "src" / "deerflow_deep_research"

PHASE_NAMES = {
    "bootstrap",
    "hitl1",
    "topic_planning",
    "wave0",
    "wave1",
    "wave2_synthesis",
    "targeted_evidence",
    "hitl2",
    "rerun",
    "readiness",
    "final_delivery",
}
CANONICAL_NAMES = ("BUNDLE_ID_RE", "CONTENT_HASH_RE", "SANDBOX_PATH_RE", "LOGICAL_PHASE_NAMES")
DEAD_NAMES = (
    "make_attempt_id",
    "project_lifecycle_status",
    "GATED_FIELDS",
    "MAX_FAKE_TRACE_ENTRIES",
    "MAX_FAKE_REPAIR_ATTEMPTS",
    "dedupe_source_urls",
)


def _modules() -> list[tuple[Path, ast.Module]]:
    result = []
    for path in sorted(SRC.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        result.append((path, ast.parse(path.read_text(encoding="utf-8"), filename=str(path))))
    return result


def _phase_name_constants(node: ast.AST) -> set[str]:
    """Phase names appearing as DIRECT elements of a tuple/list/literal value.

    Nested content (e.g. TopologyEdge arguments inside the NORMALIZED_EDGES
    tuple) is intentionally ignored: edges reference phases as endpoints, they
    do not define the phase list.
    """
    if isinstance(node, (ast.Tuple, ast.List)):
        elements = node.elts
    elif isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Tuple):
        elements = node.slice.elts
    else:
        return set()
    found: set[str] = set()
    for element in elements:
        if isinstance(element, ast.Constant) and isinstance(element.value, str) and element.value in PHASE_NAMES:
            found.add(element.value)
    return found


def test_canonical_identifiers_are_defined_exactly_once() -> None:
    counts = {name: 0 for name in CANONICAL_NAMES}
    for _path, tree in _modules():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in counts:
                    counts[target.id] += 1
    for name, count in counts.items():
        assert count == 1, f"{name} defined {count} times; expected exactly 1 in domain/identifiers.py"


def test_no_inline_full_phase_list_definitions() -> None:
    offenders: list[str] = []
    for path, tree in _modules():
        for node in ast.walk(tree):
            if isinstance(node, (ast.Tuple, ast.List)):
                if len(_phase_name_constants(node)) >= 10:
                    offenders.append(f"{path.relative_to(AGENT_ROOT)}:{node.lineno}")
            elif isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Tuple):
                if len(_phase_name_constants(node)) >= 10:
                    offenders.append(f"{path.relative_to(AGENT_ROOT)}:{node.lineno}")
    assert not offenders, f"inline 11-phase list definitions: {offenders}"


def test_dead_symbols_are_absent() -> None:
    for path, tree in _modules():
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in DEAD_NAMES:
                raise AssertionError(f"dead symbol still present in {path.relative_to(AGENT_ROOT)}: {node.id}")
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if alias.name.split(".")[-1] in DEAD_NAMES:
                        raise AssertionError(f"dead symbol imported in {path.relative_to(AGENT_ROOT)}: {alias.name}")


def test_dead_modules_are_absent() -> None:
    assert not (SRC / "graph" / "routing.py").exists()
    assert not (SRC / "engine" / "work_units" / "reducers.py").exists()
