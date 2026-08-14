"""Fixed-path loader for source-controlled Evaluation Cases.

@impl CES-001
@impl CES-007
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

from deerflow_deep_research.domain.evaluation import ControlIdentity, EvaluationCase

from .runner import CaseRegistry


def default_control_root() -> Path:
    return Path(__file__).resolve().parents[4] / "evals" / "control"


def load_case_registry(control_root: Path | None = None) -> CaseRegistry:
    """Load only the reviewed registry and contained artifacts below the fixed control root."""

    root = (control_root or default_control_root()).resolve(strict=True)
    registry_path = root / "registry.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        declarations = registry["cases"]
    except (OSError, UnicodeDecodeError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("evaluation_control_registry_invalid") from exc
    if not isinstance(declarations, list) or not declarations:
        raise ValueError("evaluation_control_registry_invalid")
    cases = tuple(_load_case(root, declaration) for declaration in declarations)
    for case, declaration in zip(cases, declarations, strict=True):
        _verify_runtime_controls(root, case)
        _verify_case_rubric(root, case, declaration["rubric"])
    return CaseRegistry(cases)


def _load_case(root: Path, declaration: Any) -> EvaluationCase:
    if not isinstance(declaration, dict):
        raise ValueError("evaluation_control_registry_invalid")
    required = {"case", "contract", "rubric", "protocol"}
    if set(declaration) != required:
        raise ValueError("evaluation_control_registry_invalid")
    case_path = _contained_file(root, declaration["case"])
    try:
        payload = json.loads(case_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("evaluation_case_declaration_invalid") from exc
    controls = tuple(
        ControlIdentity(
            kind=kind,
            version=_control_version(path := _contained_file(root, declaration[kind])),
            digest=hashlib.sha256(path.read_bytes()).hexdigest(),
        )
        for kind in ("case", "contract", "rubric", "protocol")
    )
    try:
        return EvaluationCase.model_validate({**payload, "controls": controls})
    except (TypeError, ValueError) as exc:
        raise ValueError("evaluation_case_declaration_invalid") from exc


def _verify_runtime_controls(root: Path, case: EvaluationCase) -> None:
    """Keep live corpus controls tied to the exact source files they declare."""

    plan = case.execution_plan
    if plan is None:
        return
    project_root = root.parents[1]
    for control in plan.runtime_controls:
        source = _contained_project_file(project_root, control.source_path)
        actual_digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if actual_digest != control.digest:
            raise ValueError("evaluation_runtime_control_digest_mismatch")


def _verify_case_rubric(root: Path, case: EvaluationCase, declared_rubric: Any) -> None:
    """Bind a typed cognitive-program scenario set to its source-controlled rubric."""

    if case.subject not in {
        "hitl1_cognitive_program",
        "wave0_cognitive_program",
        "wave1_cognitive_program",
        "wave2_cognitive_program",
    }:
        return
    rubric_path = _contained_file(root, declared_rubric)
    try:
        rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
        criteria = rubric["criteria"]
        criterion_ids = tuple(item["id"] for item in criteria)
    except (OSError, UnicodeDecodeError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("evaluation_cognitive_program_rubric_invalid") from exc
    if case.subject == "hitl1_cognitive_program":
        scenarios = case.hitl1_cognitive_program_fixture.scenarios
    elif case.subject == "wave0_cognitive_program":
        scenarios = case.wave0_cognitive_program_fixture.scenarios
    elif case.subject == "wave1_cognitive_program":
        scenarios = case.wave1_cognitive_program_fixture.scenarios
    else:
        scenarios = case.wave2_cognitive_program_fixture.scenarios
    expected_ids = {criterion_id for scenario in scenarios for criterion_id in scenario.review_criteria}
    if (
        rubric.get("schema_version") != 1
        or rubric.get("case_id") != case.case_id
        or rubric.get("version") != case.version
        or set(criterion_ids) != expected_ids
        or len(set(criterion_ids)) != len(criterion_ids)
    ):
        raise ValueError("evaluation_cognitive_program_rubric_invalid")


def _contained_file(root: Path, relative: Any) -> Path:
    if not isinstance(relative, str) or not relative:
        raise ValueError("evaluation_control_path_invalid")
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != relative:
        raise ValueError("evaluation_control_path_invalid")
    target = (root / path).resolve(strict=True)
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError("evaluation_control_path_invalid") from exc
    if target.is_symlink() or not target.is_file():
        raise ValueError("evaluation_control_path_invalid")
    return target


def _contained_project_file(project_root: Path, relative: str) -> Path:
    path = PurePosixPath(relative)
    target = (project_root / path).resolve(strict=True)
    try:
        target.relative_to(project_root)
    except ValueError as exc:
        raise ValueError("evaluation_runtime_control_path_invalid") from exc
    if target.is_symlink() or not target.is_file():
        raise ValueError("evaluation_runtime_control_path_invalid")
    return target


def _control_version(path: Path) -> str:
    stem = path.stem
    marker = stem.rfind("-v")
    return stem[marker + 1 :] if marker >= 0 else "v1"
