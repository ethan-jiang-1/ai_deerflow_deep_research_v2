"""Textual adapter coverage through shared run-experience values.

@impl RED-001
@impl RED-002
@impl RED-003
@impl RED-004
@impl RED-005
@impl RED-006
@impl RED-008
@impl RDO-001
@impl RDO-004
@impl REC-006
"""

from __future__ import annotations

import asyncio
import sys
from collections import deque
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from deerflow_deep_research.domain.human_interaction import InteractionFeedback, InteractionFeedbackKind
from deerflow_deep_research.domain.run_experience import (
    AnswerRun,
    AwaitingInput,
    FailureCertainty,
    Fault,
    ReadinessCheck,
    ReadinessReport,
    RunFailure,
    RunFailureCode,
    RunSnapshot,
    SelectControlRun,
    StartRun,
    Terminal,
    Working,
)
from tests.fixtures import run_updates

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import demo_tui  # noqa: E402, I001
from demo_tui import DeepResearchDemoTUI  # noqa: E402


def _ready_report(mode: str = "fake") -> ReadinessReport:
    return ReadinessReport(
        mode=mode,
        ready=True,
        summary="Ready.",
        checks=(ReadinessCheck(name="mode", ready=True, detail=mode),),
        durability_note="Temporary standalone demo.",
    )


def _failed_report() -> ReadinessReport:
    return ReadinessReport(
        mode="real",
        ready=False,
        summary="Local setup failed.",
        checks=(ReadinessCheck(name="model", ready=False, detail="missing", next_action="Configure a model."),),
        failure=RunFailure(
            code=RunFailureCode.CONFIGURATION_MODEL_MISSING,
            certainty=FailureCertainty.DIRECT,
            message="Local setup failed.",
            next_action="Configure a model.",
            retryable=True,
            journal_record_created=False,
        ),
        durability_note="No research record was created.",
    )


async def _wait_for(app: DeepResearchDemoTUI, pilot, expected: type, max_wait: float = 4.0) -> None:
    elapsed = 0.0
    while elapsed < max_wait and not isinstance(app.last_update, expected):
        await pilot.pause()
        await asyncio.sleep(0.02)
        elapsed += 0.02
    assert isinstance(app.last_update, expected)


class _Adapter:
    created: list[_Adapter] = []

    def __init__(self, **_kwargs: Any) -> None:
        self.close_calls = 0
        type(self).created.append(self)

    @classmethod
    def for_real(cls) -> _Adapter:
        """Represent a test environment whose real-demo preflight already passed."""
        return cls()

    async def create_work_unit_store(self, *_args: Any, **_kwargs: Any) -> object:
        return object()

    def close(self) -> None:
        self.close_calls += 1


class _ScriptedExperience:
    updates: deque[object] = deque()
    instances: list[_ScriptedExperience] = []
    wait_started: asyncio.Event | None = None
    release: asyncio.Event | None = None

    def __init__(self, *, transport, mode, readiness_provider, **_kwargs: Any) -> None:
        self._readiness_provider = readiness_provider
        self.intents: list[object] = []
        type(self).instances.append(self)

    async def preflight(self) -> ReadinessReport:
        return self._readiness_provider()

    async def handle(self, intent: object, observer=None) -> object:
        self.intents.append(intent)
        if observer is not None:
            observer(Working(snapshot=RunSnapshot(), action="start", message="waiting for returned result"))
        if type(self).wait_started is not None:
            type(self).wait_started.set()
            assert type(self).release is not None
            await type(self).release.wait()
        return type(self).updates.popleft()


def _install_scripted(
    monkeypatch: pytest.MonkeyPatch,
    *,
    report: ReadinessReport,
    updates: list[object],
) -> list[str]:
    runtime_modes: list[str] = []

    def build_runtime(*, mode: str, adapter: object) -> object:
        runtime_modes.append(mode)
        return SimpleNamespace(adapter=adapter, executor=object())

    _Adapter.created = []
    _ScriptedExperience.updates = deque(updates)
    _ScriptedExperience.instances = []
    _ScriptedExperience.wait_started = None
    _ScriptedExperience.release = None
    monkeypatch.setattr(demo_tui, "DemoAdapter", _Adapter)
    monkeypatch.setattr(demo_tui, "ResearchRunExperience", _ScriptedExperience)
    monkeypatch.setattr(demo_tui, "build_demo_runtime", build_runtime)
    monkeypatch.setattr(demo_tui, "demo_readiness_report", lambda **_kwargs: report)
    return runtime_modes


@pytest.mark.asyncio
async def test_tui_fake_route_completes_through_shared_experience() -> None:
    app = DeepResearchDemoTUI(mode="fake")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        assert "full-fake" in app.query_one("#banner").render().plain
        await pilot.press("enter")
        await _wait_for(app, pilot, AwaitingInput)
        assert app.last_update.prompt.phase == "hitl1"
        await pilot.press(*"profile")
        await pilot.press("enter")
        await _wait_for(app, pilot, Terminal)

    assert app.last_update.outcome == "completed"


@pytest.mark.asyncio
async def test_tui_forwards_unadvertised_choice_to_graph_owned_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_scripted(
        monkeypatch,
        report=_ready_report(),
        updates=[run_updates.awaiting_hitl2(), run_updates.provider_fault()],
    )
    app = DeepResearchDemoTUI(mode="fake")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await pilot.press("enter")
        await _wait_for(app, pilot, AwaitingInput)
        await pilot.press(*"not-an-advertised-choice")
        await pilot.press("enter")
        await _wait_for(app, pilot, Fault)

    intents = _ScriptedExperience.instances[0].intents
    assert isinstance(intents[0], StartRun)
    assert isinstance(intents[1], AnswerRun)
    assert intents[1].value == "not-an-advertised-choice"


@pytest.mark.asyncio
async def test_tui_selects_visible_control_and_keeps_natural_text_as_text(monkeypatch: pytest.MonkeyPatch) -> None:
    """@impl RED-007"""
    _install_scripted(
        monkeypatch,
        report=_ready_report(),
        updates=[
            run_updates.awaiting_hitl1(
                feedback=InteractionFeedback(
                    kind=InteractionFeedbackKind.SEMANTIC_INVALID,
                    message="The current proposal remains available after invalid semantic output.",
                )
            ),
            run_updates.completed(),
        ],
    )
    app = DeepResearchDemoTUI(mode="fake")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await pilot.press("enter")
        await _wait_for(app, pilot, AwaitingInput)
        assert "Start with the current proposal" in app.last_view.detail
        assert "current proposal remains available" in app.last_view.detail
        await pilot.click("#accept")
        await _wait_for(app, pilot, Terminal)

    assert _ScriptedExperience.instances[0].intents[1] == SelectControlRun(control_id="accept_current_proposal")

    _install_scripted(
        monkeypatch,
        report=_ready_report(),
        updates=[run_updates.awaiting_hitl1(), run_updates.completed()],
    )
    app = DeepResearchDemoTUI(mode="fake")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await pilot.press("enter")
        await _wait_for(app, pilot, AwaitingInput)
        await pilot.press(*"采用建议")
        await pilot.press("enter")
        await _wait_for(app, pilot, Terminal)

    assert _ScriptedExperience.instances[0].intents[1] == AnswerRun(value="采用建议")


@pytest.mark.asyncio
async def test_tui_explicit_cancel_uses_shared_cancel_intent() -> None:
    app = DeepResearchDemoTUI(mode="fake")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await pilot.press("enter")
        await _wait_for(app, pilot, AwaitingInput)
        await pilot.click("#cancel")
        await _wait_for(app, pilot, Terminal)

    assert app.last_update.outcome == "cancelled"


@pytest.mark.asyncio
async def test_tui_preflight_failure_shows_safe_fault_before_question(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_scripted(monkeypatch, report=_failed_report(), updates=[])
    app = DeepResearchDemoTUI(mode="real")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, Fault)
        assert app.query_one("#composer").disabled is True
        assert "Configure a model" in app.last_view.detail

    assert not _Adapter.created


@pytest.mark.asyncio
async def test_tui_real_route_obtains_the_fixed_all_real_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime_modes = _install_scripted(monkeypatch, report=_ready_report("real"), updates=[run_updates.awaiting_hitl1()])
    app = DeepResearchDemoTUI(mode="real")

    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)

    assert runtime_modes == ["real"]


@pytest.mark.asyncio
async def test_tui_runtime_construction_fault_cannot_present_full_fake_completion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_scripted(monkeypatch, report=_ready_report("real"), updates=[run_updates.completed()])

    def fail_runtime(**_kwargs: object) -> object:
        raise RuntimeError("demo_runtime_unavailable")

    monkeypatch.setattr(demo_tui, "build_demo_runtime", fail_runtime)
    app = DeepResearchDemoTUI(mode="real")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, Fault)
        assert app.last_view.heading == "Research could not continue"
        assert app.query_one("#composer").disabled is True

    assert _Adapter.created[0].close_calls == 1


@pytest.mark.asyncio
async def test_tui_fake_route_remains_outside_the_graph_runtime_factory(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime_modes = _install_scripted(monkeypatch, report=_ready_report(), updates=[run_updates.awaiting_hitl1()])
    app = DeepResearchDemoTUI(mode="fake")

    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)

    assert runtime_modes == []


@pytest.mark.asyncio
async def test_tui_working_state_shows_no_inferred_trace_progress(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_scripted(monkeypatch, report=_ready_report(), updates=[run_updates.awaiting_hitl1()])
    _ScriptedExperience.wait_started = asyncio.Event()
    _ScriptedExperience.release = asyncio.Event()
    app = DeepResearchDemoTUI(mode="fake")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await pilot.press("enter")
        await asyncio.wait_for(_ScriptedExperience.wait_started.wait(), timeout=2)
        assert isinstance(app.last_update, Working)
        assert app.last_view.completed_trace == ()
        assert app.query_one("#composer").disabled is True
        _ScriptedExperience.release.set()
        await _wait_for(app, pilot, AwaitingInput)


@pytest.mark.asyncio
async def test_tui_owns_and_closes_one_adapter(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_scripted(monkeypatch, report=_ready_report(), updates=[])
    app = DeepResearchDemoTUI(mode="fake")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)

    assert len(_Adapter.created) == 1
    assert _Adapter.created[0].close_calls == 1


def test_tui_renders_safe_provider_facts_without_recovery_invention() -> None:
    update = run_updates.nonretryable_http_provider_terminal()

    rendered = demo_tui.render_run_update(update).detail

    assert "internal.unexpected" in rendered
    assert "deepseek-v4-pro" in rendered
    assert "https://api.example.test" in rendered
    assert "400" in rendered
    assert "support_journal" not in rendered
    assert "Retained observation is unavailable" in rendered
    assert "make demo-real" not in rendered
    assert "demo-sessions" not in rendered
    assert "automatic retries" not in rendered.lower()


def test_tui_marks_matching_inspection_as_read_only_and_suppresses_generic_fresh_action() -> None:
    update = run_updates.exhausted_provider_terminal()

    rendered = demo_tui.render_run_update(update).detail

    assert "provider.timeout" in rendered
    assert "Automatic retries: 1" in rendered
    assert "make demo-real" in rendered
    assert "from deep_research_harness/" in rendered
    assert "Read-only diagnosis" in rendered
    assert 'make demo-sessions DEMO_ARGS="inspect ' + run_updates.BUNDLE_ID + '"' in rendered
    assert "可启动一个独立的新研究运行" not in rendered
    assert "bridge_wall_time_budget" in rendered
    assert "provider_sdk_timeout" in rendered


def test_tui_renders_controller_provider_diagnosis_without_a_fabricated_fresh_start() -> None:
    """@impl RED-004
    @impl WFO-001
    """
    rendered = demo_tui.render_run_update(run_updates.controller_provider_terminal()).detail

    assert "Category: provider.timeout" in rendered
    assert "Phase: wave0" in rendered
    assert "Worker failure category: agent_invocation" in rendered
    assert "Diagnostic: " + run_updates.DIAGNOSTIC_REF in rendered
    assert "Read-only diagnosis" in rendered
    assert "Fresh run from deep_research_harness/" not in rendered
    assert "resume" not in rendered.lower()


def test_tui_omits_unsafe_endpoint_components_from_a_provider_terminal() -> None:
    update = run_updates.exhausted_provider_terminal()
    assert update.failure is not None
    unsafe_observation = update.failure.provider_observation.model_construct(
        configured_service_label="deepseek-v4-pro",
        configured_endpoint_authority="https://api.example.test/v1?token=secret#fragment",
        response_kind="no_response",
        http_status=None,
    )
    failure = update.failure.model_copy(
        update={
            "message": "question=private answer=private prompt=private raw-diagnostic=private",
            "provider_observation": unsafe_observation,
        }
    )
    unsafe_update = update.model_copy(update={"failure": failure})

    rendered = demo_tui.render_run_update(unsafe_update).detail

    assert "deepseek-v4-pro" in rendered
    for unsafe in ("/v1", "token=secret", "fragment", "question=private", "answer=private", "prompt=private"):
        assert unsafe not in rendered
