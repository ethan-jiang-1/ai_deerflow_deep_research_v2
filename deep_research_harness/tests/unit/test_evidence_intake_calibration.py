"""Deterministic contracts for the separate evidence-intake calibration corpus.

@impl EVH-019
@impl WAN-008
@impl WON-008
"""

from __future__ import annotations

import json
from dataclasses import replace
from types import SimpleNamespace

import pytest

from deerflow_deep_research.agents.capabilities import load_node_agent_capability
from deerflow_deep_research.domain.context import NodeExecutionResult
from deerflow_deep_research.domain.enums import NodeFinishReason
from scripts._demo_core import DemoAppConfig
from scripts.check_test_assets import collect_deterministic_selectors, collect_pytest_selectors
from tests.assets.selection import LIVE_EXPRESSION, LIVE_PATHS
from tests.scenarios import evidence_intake_live
from tests.scenarios.canaries import LIVE_CANARIES, validate_live_canary_deadlines
from tests.scenarios.contracts import ScenarioCase
from tests.scenarios.evidence_intake_calibration import (
    EVIDENCE_INTAKE_CALIBRATION_CASES,
    build_evidence_intake_request,
    evidence_intake_case_requires_web,
    validate_evidence_intake_calibration_cases,
)
from tests.scenarios.evidence_intake_live import evidence_intake_live_scenario, run_evidence_intake_calibration
from tests.scenarios.intake_planning_calibration import CALIBRATION_CASES, CalibrationRisk
from tests.scenarios.live import LiveAttempt, LiveOutcome, LivePreflightError, LiveRubricResult, RubricDisposition
from tests.scenarios.replays import FIRST_WAVE_CASES


def _offline_calibration_summary(capability_id: str) -> str:
    if capability_id in {"wave0-authoritative-source-intake", "wave0-source-intake-repair"}:
        return json.dumps(
            {
                "schema_version": 1,
                "sources": [
                    {
                        "source_id": "source:offline",
                        "canonical_url": "https://example.invalid/offline",
                        "title": "Offline source",
                        "fetch_status": "fetched",
                    }
                ],
                "baseline_facts": [],
                "limitations": "",
            }
        )
    if capability_id in {"wave1-evidence-extraction", "wave1-evidence-extraction-repair"}:
        return json.dumps(
            {
                "schema_version": 1,
                "sources": [
                    {
                        "source_id": "source:offline-a",
                        "canonical_url": "https://example.invalid/offline-a",
                        "title": "Offline source A",
                    },
                    {
                        "source_id": "source:offline-b",
                        "canonical_url": "https://example.invalid/offline-b",
                        "title": "Offline source B",
                    },
                ],
                "claims": [],
                "open_questions": [],
            }
        )
    if capability_id == "wave1-source-diagnostic":
        return json.dumps(
            {
                "schema_version": 1,
                "source_ids": ["source:accepted-a", "source:accepted-b"],
                "sources": [
                    {
                        "source_id": "source:accepted-a",
                        "trust_tier": "medium",
                        "materiality": "primary",
                        "marketing_risk": False,
                        "cross_verification_need": True,
                    },
                    {
                        "source_id": "source:accepted-b",
                        "trust_tier": "medium",
                        "materiality": "primary",
                        "marketing_risk": False,
                        "cross_verification_need": True,
                    },
                ],
            }
        )
    if capability_id == "wave1-claim-verifier":
        return json.dumps(
            {
                "schema_version": 1,
                "claims": [
                    {
                        "claim_id": "claim:w1_evidence_intake",
                        "verdict": "supported",
                        "support_refs": ["source:accepted-a"],
                        "counter_refs": ["source:accepted-b"],
                        "reason": "Offline bounded result.",
                    }
                ],
            }
        )
    raise AssertionError(f"unexpected capability: {capability_id}")


def test_evidence_intake_corpus_has_two_labeled_cases_per_branch_with_declared_bounds() -> None:
    validate_evidence_intake_calibration_cases()

    assert len(EVIDENCE_INTAKE_CALIBRATION_CASES) == 12
    assert {case.branch_id for case in EVIDENCE_INTAKE_CALIBRATION_CASES} == {
        "wave0/worker",
        "wave0/repair",
        "wave1/worker",
        "wave1/repair",
        "wave1/source-diagnostic",
        "wave1/claim-verifier",
    }
    for branch_id in {case.branch_id for case in EVIDENCE_INTAKE_CALIBRATION_CASES}:
        assert {case.risk for case in EVIDENCE_INTAKE_CALIBRATION_CASES if case.branch_id == branch_id} == {
            CalibrationRisk.NORMAL,
            CalibrationRisk.HIGHEST_RISK,
        }
    assert all(case.permitted_degradation == ("limited", "inconclusive") for case in EVIDENCE_INTAKE_CALIBRATION_CASES)
    assert all(case.max_attempts == 1 and case.criterion_ids for case in EVIDENCE_INTAKE_CALIBRATION_CASES)


def test_evidence_intake_corpus_is_disjoint_from_other_calibration_and_scenario_collections() -> None:
    evidence_ids = {case.case_id for case in EVIDENCE_INTAKE_CALIBRATION_CASES}

    assert evidence_ids.isdisjoint({case.case_id for case in CALIBRATION_CASES})
    assert evidence_ids.isdisjoint({scenario.scenario_id for scenario in LIVE_CANARIES})
    assert evidence_ids.isdisjoint({case.case_id for case in FIRST_WAVE_CASES})
    assert all(not isinstance(case, ScenarioCase) for case in EVIDENCE_INTAKE_CALIBRATION_CASES)
    assert validate_live_canary_deadlines(LIVE_CANARIES, job_timeout_seconds=1200)["case_count"] == 6


def test_evidence_intake_request_composition_preserves_branch_tool_posture() -> None:
    for case in EVIDENCE_INTAKE_CALIBRATION_CASES:
        request = build_evidence_intake_request(case)
        requires_web = evidence_intake_case_requires_web(case)

        assert request.tools_enabled is requires_web
        assert request.minimum_tool_calls == (1 if requires_web else 0)
        expected_tool_limit = 3 if case.branch_id == "wave0/worker" else 1 if case.branch_id == "wave1/worker" else None
        assert request.tool_call_limit == expected_tool_limit
        if case.branch_id in {"wave0/worker", "wave0/repair", "wave1/worker", "wave1/repair"}:
            assert request.capability_ref is not None
            capability = load_node_agent_capability(request.capability_ref)
            assert "ledger" in capability.policy.lower()
            assert "ledger" not in request.objective.lower()
            if case.branch_id == "wave1/repair" and case.risk is CalibrationRisk.HIGHEST_RISK:
                assert "baseline URL cannot supply a repaired source" in capability.policy
                assert "baseline URL cannot supply a repaired source" not in request.objective
        else:
            assert "ledger" in request.objective.lower()


def test_evidence_intake_case_validator_fails_closed_on_denominator_or_bound_drift() -> None:
    with pytest.raises(ValueError, match="evidence_intake_calibration_case_identity_invalid"):
        validate_evidence_intake_calibration_cases(EVIDENCE_INTAKE_CALIBRATION_CASES[:-1])
    with pytest.raises(ValueError, match="evidence_intake_calibration_bounds_invalid"):
        validate_evidence_intake_calibration_cases(
            (replace(EVIDENCE_INTAKE_CALIBRATION_CASES[0], max_tool_calls=0), *EVIDENCE_INTAKE_CALIBRATION_CASES[1:])
        )


def test_evidence_intake_live_scenarios_select_the_declared_real_dependency_seam() -> None:
    for case in EVIDENCE_INTAKE_CALIBRATION_CASES:
        scenario = evidence_intake_live_scenario(case)
        requires_web = evidence_intake_case_requires_web(case)

        assert scenario.preconditions["require_web"] is requires_web
        assert scenario.live_requirements == (("model", "web_search") if requires_web else ("model",))
        assert scenario.entrypoint == (
            "direct-model-and-web-node-agent-bridge" if requires_web else "direct-model-node-agent-bridge"
        )


@pytest.mark.asyncio
async def test_selected_evidence_intake_runner_uses_strict_branch_preflight(monkeypatch, tmp_path) -> None:
    worker = next(case for case in EVIDENCE_INTAKE_CALIBRATION_CASES if case.branch_id == "wave0/worker")
    repair = next(case for case in EVIDENCE_INTAKE_CALIBRATION_CASES if case.branch_id == "wave0/repair")

    with pytest.raises(LivePreflightError, match="live_explicit_profile_missing"):
        await run_evidence_intake_calibration(worker, environ={"OPENAI_API_KEY": "test"}, workspace=tmp_path)
    with pytest.raises(LivePreflightError, match="live_explicit_profile_missing"):
        await run_evidence_intake_calibration(repair, environ={}, workspace=tmp_path)

    async def fake_execute(case, scenario, *, environ, workspace):
        del environ, workspace
        return LiveAttempt(
            outcome=LiveOutcome(
                route="candidate-evaluated",
                values={"identity": {"thread_id": "thread", "run_id": "run", "bundle_id": "research"}},
            ),
            error_code=None,
            model_id="openai/test",
            tool_ids=("tavily/web_search",) if scenario.preconditions["require_web"] else (),
            input_tokens=None,
            output_tokens=None,
            cost_usd=None,
            tool_calls=1 if scenario.preconditions["require_web"] else 0,
            wall_time_seconds=0.1,
            diagnostics="test selected branch",
            rubric_result=LiveRubricResult(
                case_id=case.case_id,
                branch_id=case.branch_id,
                criterion_ids=case.criterion_ids,
                disposition=RubricDisposition.PASS,
                rationale="The test fixture proves report selection only.",
            ),
        )

    monkeypatch.setattr("tests.scenarios.evidence_intake_live._execute_case", fake_execute)
    report = await run_evidence_intake_calibration(
        worker,
        environ={
            "DEERFLOW_DEMO_MODEL": "openai-demo",
            "OPENAI_API_KEY": "test",
            "TAVILY_API_KEY": "test",
        },
        workspace=tmp_path,
    )
    assert report.rubric_result is not None
    assert report.rubric_result.case_id == worker.case_id


@pytest.mark.asyncio
async def test_offline_evidence_intake_branches_are_explicit_profile_bundle_bound_and_redacted(
    monkeypatch, tmp_path
) -> None:
    """@impl EVH-030
    @impl WAN-012
    @impl WON-012

    This exercises every branch through the production projection seam while replacing
    only the paid bridge and web dependency with deterministic local doubles.
    """

    environ = {"DEERFLOW_DEMO_MODEL": "openai-demo", "OPENAI_API_KEY": "test", "TAVILY_API_KEY": "test"}
    worker = next(case for case in EVIDENCE_INTAKE_CALIBRATION_CASES if case.branch_id == "wave0/worker")
    with pytest.raises(LivePreflightError, match="live_explicit_profile_missing"):
        await run_evidence_intake_calibration(worker, environ={"OPENAI_API_KEY": "test"}, workspace=tmp_path)
    assert not tuple(tmp_path.rglob("state.json"))

    profile = evidence_intake_live._explicit_profile(environ, requires_web=True)
    app_config = DemoAppConfig(models=(profile.model_config,))
    assert len(app_config.models) == 1
    assert profile.evidence.profile_id == "openai-demo"
    assert profile.evidence.registry_revision == "v1"

    contexts = []

    class OfflineCapabilities:
        async def run_agent(self, *, context, request):
            contexts.append(context)
            assert context.bundle_context is not None
            capability_id = request.capability_ref.capability_id if request.capability_ref is not None else None
            return NodeExecutionResult(
                finish_reason=NodeFinishReason.SUCCESS,
                summary=_offline_calibration_summary(str(capability_id)),
            )

    def build_offline_capabilities(*_args, **_kwargs):
        return OfflineCapabilities()

    monkeypatch.setattr(evidence_intake_live, "_build_wave0_capabilities", build_offline_capabilities)
    monkeypatch.setattr(evidence_intake_live, "_build_wave1_capabilities", build_offline_capabilities)
    monkeypatch.setattr(evidence_intake_live.canaries, "_LiveWebSearch", lambda _key: SimpleNamespace(calls=1))

    for case in EVIDENCE_INTAKE_CALIBRATION_CASES:
        attempt = await evidence_intake_live._execute_case(
            case,
            evidence_intake_live.evidence_intake_live_scenario(case),
            environ=environ,
            workspace=tmp_path,
        )

        assert attempt.outcome is not None
        assert attempt.rubric_result is not None
        assert "profile=openai-demo revision=v1" in attempt.diagnostics
        if case.branch_id in {"wave0/worker", "wave0/repair", "wave1/worker", "wave1/repair"}:
            assert "response_shape=json_object validation_codes=none" in attempt.diagnostics
        else:
            assert "response_shape=not_applicable validation_codes=none" in attempt.diagnostics

    assert len(contexts) == len(EVIDENCE_INTAKE_CALIBRATION_CASES)
    journals = tuple(sorted(tmp_path.rglob("events.jsonl")))
    assert len(journals) == len(EVIDENCE_INTAKE_CALIBRATION_CASES)
    for journal_path in journals:
        events = tuple(json.loads(line) for line in journal_path.read_text(encoding="utf-8").splitlines())
        assert events[0]["execution_profile"] == {"profile_id": "openai-demo", "registry_revision": "v1"}
        validation_events = tuple(event for event in events if event["category"] == "validation")
        if validation_events:
            assert len(validation_events) == 1
            assert validation_events[0]["response_shape"] == "json_object"
            assert validation_events[0]["validation_stage"] in {"initial", "repair"}
        assert all("https://example.invalid" not in json.dumps(event) for event in events)


def test_default_deterministic_selection_excludes_both_live_calibration_collections() -> None:
    evidence_selectors = {
        (f"tests/live/test_evidence_intake_live_calibration.py::test_live_evidence_intake_calibration[{case.case_id}]")
        for case in EVIDENCE_INTAKE_CALIBRATION_CASES
    }

    assert evidence_selectors.isdisjoint(collect_deterministic_selectors())
    live_selectors = collect_pytest_selectors(paths=LIVE_PATHS, expression=LIVE_EXPRESSION, label="live evidence")
    assert evidence_selectors <= live_selectors
