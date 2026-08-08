"""Deterministic inventory and safety checks for prompt review cases.

@impl NPC-002
@impl NPC-003
@impl NPC-004
@impl NPC-007
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

from deerflow_deep_research.domain.context import NodeExecutionRequest
from deerflow_deep_research.graph.prompt_catalog import (
    SYNTHETIC_FIXTURE_MARKER,
    VIRTUAL_ATTEMPT_WORKSPACE,
    prompt_catalog_cases,
)

SOURCE_ROOT = Path(__file__).resolve().parents[2] / "src" / "deerflow_deep_research"
_REQUEST_BUILDER_PATHS = (
    *(SOURCE_ROOT / "graph" / "nodes").glob("*/prompts.py"),
    SOURCE_ROOT / "graph" / "nodes" / "readiness" / "critic.py",
    SOURCE_ROOT / "graph" / "nodes" / "final_delivery" / "composer.py",
)


def _direct_prompt_builders() -> set[str]:
    """Return every node-local function that directly creates a phase request."""

    builders: set[str] = set()
    for path in sorted(_REQUEST_BUILDER_PATHS):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        relative_path = path.relative_to(SOURCE_ROOT).as_posix()
        for function in (node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))):
            creates_request = any(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "NodeExecutionRequest"
                for node in ast.walk(function)
            )
            if creates_request:
                builders.add(f"{relative_path}::{function.name}")
    return builders


def _repair_parameter_builders() -> set[str]:
    builders: set[str] = set()
    for path in sorted((SOURCE_ROOT / "graph" / "nodes").glob("*/prompts.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        relative_path = path.relative_to(SOURCE_ROOT).as_posix()
        for function in (node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))):
            creates_request = any(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "NodeExecutionRequest"
                for node in ast.walk(function)
            )
            arguments = (*function.args.posonlyargs, *function.args.args, *function.args.kwonlyargs)
            if creates_request and any(argument.arg == "repair_error" for argument in arguments):
                builders.add(f"{relative_path}::{function.name}")
    return builders


def test_catalog_registers_every_direct_node_prompt_builder() -> None:
    cases = prompt_catalog_cases()

    assert {case.builder_id for case in cases} == _direct_prompt_builders()
    assert len({case.case_id for case in cases}) == len(cases)
    assert tuple(case.case_id for case in cases) == tuple(sorted(case.case_id for case in cases))


def test_catalog_covers_initial_and_repair_branches_for_optional_repair_builders() -> None:
    cases = prompt_catalog_cases()
    optional_repair_builders = _repair_parameter_builders()

    assert {case.builder_id for case in cases if not case.is_repair} >= optional_repair_builders
    assert {case.builder_id for case in cases if case.is_repair} >= optional_repair_builders


def test_catalog_cases_are_safe_deterministic_synthetic_requests() -> None:
    cases = prompt_catalog_cases()
    first = tuple(case.build_request().model_dump(mode="json") for case in cases)
    second = tuple(case.build_request().model_dump(mode="json") for case in cases)
    serialized = json.dumps(first, ensure_ascii=True, sort_keys=True)

    assert first == second
    assert all(isinstance(case.build_request(), NodeExecutionRequest) for case in cases)
    assert all(case.attempt_workspace == VIRTUAL_ATTEMPT_WORKSPACE for case in cases)
    assert SYNTHETIC_FIXTURE_MARKER in serialized
    for forbidden in ("/Users/", "TAVILY_API_KEY", "api_key", "sk-"):
        assert forbidden not in serialized
