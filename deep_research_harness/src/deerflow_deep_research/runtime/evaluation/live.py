"""Manually selected, bounded live entrypoints for the two V1 evaluation Cases.

This module deliberately does not construct provider clients or production node
dependencies. The caller must explicitly construct those bindings and select a Case.
"""

from __future__ import annotations

import os
from collections.abc import Mapping

from .contracts import ExecutionResult
from .runner import CaseAdmissionError, CognitiveEvaluationRunner

_V1_LIVE_CASES = frozenset(
    {
        ("hitl1-brief", "v1"),
        ("hitl1-cognitive-program", "v1"),
        ("wave0-worker", "v1"),
        ("public-controller-direction-loop", "v1"),
        ("topic-planning-direction-loop", "v1"),
    }
)
_MODEL_CREDENTIALS = ("ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY", "OPENAI_API_KEY")


class SelectedLivePreflightError(RuntimeError):
    pass


def preflight_selected_live_case(
    *, required_services: tuple[str, ...], environ: Mapping[str, str] | None = None
) -> None:
    """Reject a live selection before it can invoke a model or web branch."""

    environment = os.environ if environ is None else environ
    if "model" in required_services and not any(environment.get(name, "").strip() for name in _MODEL_CREDENTIALS):
        raise SelectedLivePreflightError("live_model_credentials_missing")
    if "web" in required_services and not environment.get("TAVILY_API_KEY", "").strip():
        raise SelectedLivePreflightError("live_web_credentials_missing")


async def run_selected_live_case(
    *,
    runner: CognitiveEvaluationRunner,
    case_id: str,
    version: str,
    environ: Mapping[str, str] | None = None,
):
    """Run one explicit V1 Case once after credential preflight; never retry or review."""

    if (case_id, version) not in _V1_LIVE_CASES:
        raise CaseAdmissionError("evaluation_live_case_not_registered")
    case = runner.registry.resolve(case_id=case_id, version=version)
    preflight_selected_live_case(required_services=case.required_services, environ=environ)
    return await runner._run_selected_live(case_id=case_id, version=version)


async def run_selected_live_case_series(
    *,
    runner: CognitiveEvaluationRunner,
    case_id: str,
    version: str,
    environ: Mapping[str, str] | None = None,
) -> tuple[ExecutionResult, ...]:
    """Run the case's declared repetitions as fresh explicit executions, never retries."""

    if (case_id, version) not in _V1_LIVE_CASES:
        raise CaseAdmissionError("evaluation_live_case_not_registered")
    case = runner.registry.resolve(case_id=case_id, version=version)
    preflight_selected_live_case(required_services=case.required_services, environ=environ)
    repetitions = case.execution_plan.repeat_count if case.execution_plan is not None else 1
    executions: list[ExecutionResult] = []
    for _ in range(repetitions):
        executions.append(await runner._run_selected_live(case_id=case_id, version=version))
    return tuple(executions)
