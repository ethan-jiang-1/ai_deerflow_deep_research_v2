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
@impl RED-009
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


def _ready_report(mode: str = "fixture") -> ReadinessReport:
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
            diagnostic_location="unavailable",
        ),
        durability_note="No research record was created.",
    )


async def _wait_for(app: DeepResearchDemoTUI, pilot, expected: type, max_wait: float = 8.0) -> None:
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


def _install_isolated_fixture_adapter(monkeypatch: pytest.MonkeyPatch, *, bundle_root: Path) -> None:
    """Keep fixture-graph behavior independent of unsupported local demo data."""
    adapter_type = demo_tui.DemoAdapter
    monkeypatch.setattr(demo_tui, "DemoAdapter", lambda: adapter_type(bundle_root=bundle_root))


async def _type_composer(app: DeepResearchDemoTUI, pilot: Any, text: str) -> None:
    """Enter text into the composer without per-key driver overhead.

    The app dispatches from the composer value at submit time
    (``on_input_submitted`` reads ``Input.Submitted.value``), so assigning the
    value directly is semantically identical to typing while skipping the
    Textual pilot's ~80ms per-key idle/animation wait (316 keys across this
    file ≈ 25s of driver time).
    """
    app.query_one("#composer", demo_tui.Input).value = text
    await pilot.pause()


@pytest.mark.asyncio
async def test_tui_fixture_route_completes_through_shared_experience(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_isolated_fixture_adapter(monkeypatch, bundle_root=tmp_path / "demo-runs")
    app = DeepResearchDemoTUI(mode="fixture")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        assert "fixture-graph" in app.query_one("#banner").render().plain
        await pilot.press("enter")
        await _wait_for(app, pilot, AwaitingInput)
        assert app.last_update.prompt.phase == "hitl1"
        await _type_composer(app, pilot, "profile")
        await pilot.press("enter")
        await _wait_for(app, pilot, Terminal)

    assert app.last_update.outcome == "completed"


@pytest.mark.asyncio
async def test_tui_holds_unadvertised_text_on_choice_prompts(monkeypatch: pytest.MonkeyPatch) -> None:
    """A CHOICE prompt accepts only an exact advertised option id from the composer.

    HITL2 is an autonomous phase and fabricates no pending choice; the current
    typed CHOICE surface is the HITL1 language selection. Any other text is not
    dispatched as a text-kind answer and leaves the prompt awaiting a real
    selection.
    """
    _install_scripted(
        monkeypatch,
        report=_ready_report(),
        updates=[run_updates.awaiting_hitl1_language_choice()],
    )
    app = DeepResearchDemoTUI(mode="fixture")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await pilot.press("enter")
        await _wait_for(app, pilot, AwaitingInput)
        awaiting = app.last_update
        await _type_composer(app, pilot, "not-an-advertised-choice")
        await pilot.press("enter")
        await pilot.pause()

        assert app.last_update is awaiting
        assert app.last_update.prompt.mode == "choice"
        assert app.last_update.prompt.rejection_category is None

    intents = _ScriptedExperience.instances[0].intents
    assert len(intents) == 1
    assert isinstance(intents[0], StartRun)


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
    app = DeepResearchDemoTUI(mode="fixture")
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
    app = DeepResearchDemoTUI(mode="fixture")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await pilot.press("enter")
        await _wait_for(app, pilot, AwaitingInput)
        await _type_composer(app, pilot, "采用建议")
        await pilot.press("enter")
        await _wait_for(app, pilot, Terminal)

    assert _ScriptedExperience.instances[0].intents[1] == AnswerRun(value="采用建议")


@pytest.mark.asyncio
async def test_tui_explicit_cancel_uses_shared_cancel_intent(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _install_isolated_fixture_adapter(monkeypatch, bundle_root=tmp_path / "demo-runs")
    app = DeepResearchDemoTUI(mode="fixture")
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
    app = DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, Fault)
        assert app.query_one("#composer").disabled is True
        assert "Configure a model" in app.last_view.detail

    assert not _Adapter.created


@pytest.mark.asyncio
async def test_tui_real_route_obtains_the_fixed_all_real_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime_modes = _install_scripted(monkeypatch, report=_ready_report("real"), updates=[run_updates.awaiting_hitl1()])
    app = DeepResearchDemoTUI(mode="embedded_smoke")

    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)

    assert runtime_modes == ["real"]


@pytest.mark.asyncio
async def test_tui_runtime_construction_fault_cannot_present_fixture_completion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_scripted(monkeypatch, report=_ready_report("real"), updates=[run_updates.completed()])

    def fail_runtime(**_kwargs: object) -> object:
        raise RuntimeError("demo_runtime_unavailable")

    monkeypatch.setattr(demo_tui, "build_demo_runtime", fail_runtime)
    app = DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, Fault)
        assert app.last_view.heading == "Research could not continue"
        assert app.query_one("#composer").disabled is True

    assert _Adapter.created[0].close_calls == 1


@pytest.mark.asyncio
async def test_tui_fixture_route_uses_the_graph_runtime_factory(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime_modes = _install_scripted(monkeypatch, report=_ready_report(), updates=[run_updates.awaiting_hitl1()])
    app = DeepResearchDemoTUI(mode="fixture")

    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)

    assert runtime_modes == ["fixture_graph"]


@pytest.mark.asyncio
async def test_tui_working_state_shows_no_inferred_trace_progress(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_scripted(monkeypatch, report=_ready_report(), updates=[run_updates.awaiting_hitl1()])
    _ScriptedExperience.wait_started = asyncio.Event()
    _ScriptedExperience.release = asyncio.Event()
    app = DeepResearchDemoTUI(mode="fixture")
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
    app = DeepResearchDemoTUI(mode="fixture")
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


async def _wait_for_hitl1_prompt(app: DeepResearchDemoTUI, pilot, *, mode: str, max_wait: float = 4.0) -> None:
    elapsed = 0.0
    while elapsed < max_wait and not (
        isinstance(app.last_update, AwaitingInput)
        and app.last_update.prompt.phase == "hitl1"
        and app.last_update.prompt.mode == mode
    ):
        await pilot.pause()
        await asyncio.sleep(0.02)
        elapsed += 0.02
    assert isinstance(app.last_update, AwaitingInput)
    assert app.last_update.prompt.phase == "hitl1"
    assert app.last_update.prompt.mode == mode


@pytest.mark.asyncio
async def test_tui_auto_mode_submits_fixed_scripted_question(monkeypatch: pytest.MonkeyPatch) -> None:
    """@impl RED-010

    010 auto TUI: after preflight the adapter dispatches one scripted start.

    The human never types: the graph-owned policy answers HITL1/HITL2, and the
    default product path is used (no ``profile_intent`` declaration).
    """
    _install_scripted(
        monkeypatch,
        report=_ready_report("real"),
        updates=[run_updates.completed()],
    )
    app = DeepResearchDemoTUI(mode="embedded_smoke", auto=True)
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, Terminal)

    intents = _ScriptedExperience.instances[0].intents
    assert len(intents) == 1
    assert isinstance(intents[0], StartRun)
    assert intents[0].scripted is True
    assert intents[0].profile_intent is None
    assert intents[0].question == demo_tui.DeepResearchDemoTUI.AUTO_QUESTION


@pytest.mark.asyncio
async def test_tui_auto_mode_stays_interactive_when_embedded_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """@impl RED-010

    The auto flag applies only to the direct local real-graph route.
    """
    _install_scripted(
        monkeypatch,
        report=_ready_report(),
        updates=[run_updates.awaiting_hitl1()],
    )
    app = DeepResearchDemoTUI(mode="fixture", auto=True)
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await pilot.press("enter")
        await _wait_for(app, pilot, AwaitingInput)

    intents = _ScriptedExperience.instances[0].intents
    assert isinstance(intents[0], StartRun)
    assert intents[0].scripted is False


def test_tui_attach_and_replay_intents_require_the_fixture_workbench() -> None:
    """RED-014 entries: attach/replay are debugger intents, fixture-only today."""
    parser = demo_tui._build_parser()
    for flag in ("--attach=b_aaaaaaaaaaaaaaaaaaaaaaaa", "--replay=b_aaaaaaaaaaaaaaaaaaaaaaaa"):
        rejected = parser.parse_args([flag])
        with pytest.raises(SystemExit):
            demo_tui._validate_args(parser, rejected)
        accepted = parser.parse_args(["--fixture", flag])
        demo_tui._validate_args(parser, accepted)
        app = demo_tui._build_app(accepted)
        # Carrying an entry intent implies the workbench even without --debug.
        assert app.debug_mode is True
        assert app.mode == "fixture"
    both = parser.parse_args(
        ["--fixture", "--attach=b_aaaaaaaaaaaaaaaaaaaaaaaa", "--replay=b_aaaaaaaaaaaaaaaaaaaaaaaa"]
    )
    with pytest.raises(SystemExit):
        demo_tui._validate_args(parser, both)


def test_tui_auto_flag_is_rejected_outside_embedded_smoke() -> None:
    """@impl RED-010

    The --auto flag is rejected at argument parsing without --embedded-smoke.
    """
    parser = demo_tui._build_parser()
    args = parser.parse_args(["--auto"])
    with pytest.raises(SystemExit):
        demo_tui._validate_args(parser, args)
    accepted = parser.parse_args(["--embedded-smoke", "--auto"])
    demo_tui._validate_args(parser, accepted)  # accepted only with --embedded-smoke


@pytest.mark.asyncio
async def test_tui_renders_advertised_hitl1_language_choice_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """@impl RED-009"""
    _install_scripted(
        monkeypatch,
        report=_ready_report(),
        updates=[run_updates.awaiting_hitl1_language_choice(), run_updates.completed()],
    )
    app = DeepResearchDemoTUI(mode="fixture")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await pilot.press("enter")
        await _wait_for_hitl1_prompt(app, pilot, mode="choice")
        for option_id in ("zh", "en"):
            button = app.query_one(f"#option-{option_id}", demo_tui.Button)
            assert button.display is True
        assert app.query_one("#options").display is True


@pytest.mark.asyncio
async def test_tui_submits_typed_option_when_an_advertised_language_button_is_clicked(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl RED-009"""
    _install_scripted(
        monkeypatch,
        report=_ready_report(),
        updates=[run_updates.awaiting_hitl1_language_choice(), run_updates.completed()],
    )
    app = DeepResearchDemoTUI(mode="fixture")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await pilot.press("enter")
        await _wait_for_hitl1_prompt(app, pilot, mode="choice")
        await pilot.click("#option-zh")
        await _wait_for(app, pilot, Terminal)

    intents = _ScriptedExperience.instances[0].intents
    assert isinstance(intents[1], AnswerRun)
    assert intents[1].response_kind == "option"
    assert intents[1].option_id == "zh"
    assert intents[1].value == "zh"


@pytest.mark.asyncio
async def test_tui_exact_match_composer_entry_answers_hitl1_language_choice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl RED-009"""
    _install_scripted(
        monkeypatch,
        report=_ready_report(),
        updates=[run_updates.awaiting_hitl1_language_choice(), run_updates.completed()],
    )
    app = DeepResearchDemoTUI(mode="fixture")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await pilot.press("enter")
        await _wait_for_hitl1_prompt(app, pilot, mode="choice")
        await _type_composer(app, pilot, "zh")
        await pilot.press("enter")
        await _wait_for(app, pilot, Terminal)

    intents = _ScriptedExperience.instances[0].intents
    assert isinstance(intents[1], AnswerRun)
    assert intents[1].response_kind == "option"
    assert intents[1].option_id == "zh"
    assert intents[1].value == "zh"


@pytest.mark.asyncio
async def test_tui_non_matching_composer_text_is_not_dispatched_for_hitl1_language_choice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl RED-009

    Non-matching text during a HITL1 CHOICE prompt dispatches no answer at all,
    and the option group disappears once the prompt returns to TEXT mode with
    free-text semantic intake intact.
    """
    _install_scripted(
        monkeypatch,
        report=_ready_report(),
        updates=[
            run_updates.awaiting_hitl1_language_choice(),
            run_updates.awaiting_hitl1(),
            run_updates.completed(),
        ],
    )
    app = DeepResearchDemoTUI(mode="fixture")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await pilot.press("enter")
        await _wait_for_hitl1_prompt(app, pilot, mode="choice")
        await _type_composer(app, pilot, "not-a-language")
        await pilot.press("enter")
        for _ in range(5):
            await pilot.pause()
        assert isinstance(app.last_update, AwaitingInput)
        assert app.last_update.prompt.mode == "choice"
        assert len(_ScriptedExperience.instances[0].intents) == 1

        await pilot.click("#option-en")
        await _wait_for_hitl1_prompt(app, pilot, mode="text")
        # hitl1 TEXT prompts now advertise quick-revision buttons (020 UX).
        assert app.query_one("#options").display is True
        await _type_composer(app, pilot, "make it quick")
        await pilot.press("enter")
        await _wait_for(app, pilot, Terminal)

    intents = _ScriptedExperience.instances[0].intents
    assert isinstance(intents[1], AnswerRun)
    assert intents[1].response_kind == "option"
    assert intents[1].option_id == "en"
    assert isinstance(intents[2], AnswerRun)
    assert intents[2].response_kind == "text"
    assert intents[2].value == "make it quick"


@pytest.mark.asyncio
async def test_tui_rich_log_text_extracts_middle_conversation() -> None:
    from rich.text import Text as RichText
    from textual.widgets import RichLog

    app = demo_tui.DeepResearchDemoTUI(mode="fixture")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        log = app.query_one("#log", RichLog)
        log.write(RichText("第一行对话"))
        log.write(RichText("第二行进度"))
        await pilot.pause()

        text = app._rich_log_text()
        assert "第一行对话" in text
        assert "第二行进度" in text


@pytest.mark.asyncio
async def test_tui_embedded_smoke_recon_starts_with_empty_composer(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_scripted(monkeypatch, report=_ready_report("real"), updates=[run_updates.awaiting_hitl1()])
    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        assert app.query_one("#composer").value == ""
        assert app._onboarding is True


@pytest.mark.asyncio
async def test_tui_fixture_prefills_example_question(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_scripted(monkeypatch, report=_ready_report("fixture"), updates=[run_updates.awaiting_hitl1()])
    app = demo_tui.DeepResearchDemoTUI(mode="fixture")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        assert app.query_one("#composer").value == demo_tui.DeepResearchDemoTUI._EXAMPLE_QUESTION


def test_research_trigger_classification() -> None:
    for trigger in (
        "start deep research",
        "deep research",
        "开始 Deep Research",
        "开始深度研究",
        "我要让你 deep research",
        "  Deep Research  ",
    ):
        assert demo_tui.is_research_trigger(trigger), trigger
    for casual in (
        "what is deep research?",
        "什么是 deep research",
        "how do I start?",
        "hello there",
        "开始",
        "deep research 是什么",
    ):
        assert not demo_tui.is_research_trigger(casual), casual


def test_env_inspect_classification() -> None:
    for command in ("env", "环境", "看看环境", "bundle 日志在哪", "where are the runs"):
        assert demo_tui.is_env_inspect(command), command
    for casual in ("hello", "开始 deep research", "今天天气"):
        assert not demo_tui.is_env_inspect(casual), casual


@pytest.mark.asyncio
async def test_tui_onboarding_chat_does_not_start_research(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_scripted(monkeypatch, report=_ready_report("real"), updates=[run_updates.awaiting_hitl1()])
    monkeypatch.setattr(demo_tui.DeepResearchDemoTUI, "_build_chat_model", lambda self: None)
    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await _type_composer(app, pilot, "hello there")
        await pilot.press("enter")
        await pilot.pause()

    assert _ScriptedExperience.instances[0].intents == []
    assert app._onboarding is True


@pytest.mark.asyncio
async def test_tui_onboarding_trigger_starts_fixed_research(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_scripted(monkeypatch, report=_ready_report("real"), updates=[run_updates.awaiting_hitl1()])
    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await _type_composer(app, pilot, "start deep research")
        await pilot.press("enter")
        await _wait_for(app, pilot, AwaitingInput)

    intents = _ScriptedExperience.instances[0].intents
    assert len(intents) == 1
    assert isinstance(intents[0], StartRun)
    assert intents[0].question == demo_tui.DeepResearchDemoTUI.AUTO_QUESTION
    assert intents[0].scripted is False


@pytest.mark.asyncio
async def test_tui_recon_start_button_dispatches_fixed_research(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_scripted(monkeypatch, report=_ready_report("real"), updates=[run_updates.awaiting_hitl1()])
    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        assert app.query_one("#start-research").display is True
        await pilot.click("#start-research")
        await _wait_for(app, pilot, AwaitingInput)

    intents = _ScriptedExperience.instances[0].intents
    assert len(intents) == 1
    assert isinstance(intents[0], StartRun)
    assert intents[0].question == demo_tui.DeepResearchDemoTUI.AUTO_QUESTION


@pytest.mark.asyncio
async def test_tui_returns_to_recon_after_research_completes(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_scripted(monkeypatch, report=_ready_report("real"), updates=[run_updates.completed()])
    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await _type_composer(app, pilot, "start deep research")
        await pilot.press("enter")
        await _wait_for(app, pilot, Terminal)
        await pilot.pause()

        assert app._onboarding is True
        assert app._last_terminal_bundle is not None
        assert app.query_one("#composer").disabled is False
        assert app.query_one("#start-research").display is True
        assert "侦察模式" in app.last_view.detail
        assert "报告" in app.last_view.detail or "bundle" in app.last_view.detail


@pytest.mark.asyncio
async def test_tui_recon_loop_supports_second_research_round(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_scripted(
        monkeypatch,
        report=_ready_report("real"),
        updates=[run_updates.completed(), run_updates.awaiting_hitl1()],
    )
    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await _type_composer(app, pilot, "start deep research")
        await pilot.press("enter")
        await _wait_for(app, pilot, Terminal)
        await pilot.pause()
        # back in recon; start a second round via trigger phrase
        await _type_composer(app, pilot, "start deep research")
        await pilot.press("enter")
        await _wait_for(app, pilot, AwaitingInput)

    intents = _ScriptedExperience.instances[0].intents
    assert len(intents) == 2
    assert all(isinstance(i, StartRun) for i in intents)
    assert intents[1].question == demo_tui.DeepResearchDemoTUI.AUTO_QUESTION


@pytest.mark.asyncio
async def test_tui_hitl1_quick_revision_button_dispatches_text_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_scripted(
        monkeypatch,
        report=_ready_report(),
        updates=[run_updates.awaiting_hitl1(), run_updates.completed()],
    )
    app = demo_tui.DeepResearchDemoTUI(mode="fixture")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await pilot.press("enter")
        await _wait_for_hitl1_prompt(app, pilot, mode="text")
        await pilot.click("#revision-depth-quick")
        await _wait_for(app, pilot, Terminal)

    intents = _ScriptedExperience.instances[0].intents
    assert len(intents) == 2
    assert isinstance(intents[1], AnswerRun)
    assert intents[1].response_kind == "text"
    assert intents[1].value == "depth: quick_overview"


@pytest.mark.asyncio
async def test_tui_hitl1_input_is_echoed_before_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:

    _install_scripted(
        monkeypatch,
        report=_ready_report(),
        updates=[run_updates.awaiting_hitl1(), run_updates.completed()],
    )
    app = demo_tui.DeepResearchDemoTUI(mode="fixture")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await pilot.press("enter")
        await _wait_for_hitl1_prompt(app, pilot, mode="text")
        await _type_composer(app, pilot, "depth: deep dive")
        await pilot.press("enter")
        await _wait_for(app, pilot, Terminal)

    assert app._last_typed == "depth: deep dive"
    # The echo line is written to the log before dispatch; it is later cleared by
    # the terminal render. The durable "you typed X" path is exercised by the
    # rejection-detail rendering (last_typed surfaced on rejection).


def test_env_inspect_recognizes_workspace_phrasing() -> None:
    for command in ("workspace", "当前 workspace", "工作区", "工作区在哪", "workspace 目录"):
        assert demo_tui.is_env_inspect(command), command


@pytest.mark.asyncio
async def test_tui_env_command_shows_workspace_structure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:

    _install_scripted(monkeypatch, report=_ready_report("real"), updates=[])
    monkeypatch.setattr(_Adapter, "bundle_root", tmp_path, raising=False)
    # Build a tiny workspace skeleton so env has something to show.
    scopes = tmp_path / "workspace" / "deep-research" / "scopes" / "s_demo"
    (scopes / "b_demo").mkdir(parents=True)
    (scopes / "b_demo" / "state.json").write_text('{"terminal_status": "completed"}', encoding="utf-8")
    (scopes / "b_demo" / "final").mkdir(parents=True)
    (scopes / "b_demo" / "final" / "report.md").write_text("# R", encoding="utf-8")
    (tmp_path / "workspace" / "soft-bundles").mkdir(parents=True)

    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await _type_composer(app, pilot, "workspace")
        await pilot.press("enter")
        await pilot.pause()
        log_text = app._rich_log_text()
        assert "workspace" in log_text
        assert "deep-research/" in log_text
        assert "b_demo" in log_text
        assert "completed" in log_text


def test_list_directory_renders_entries_with_sizes(tmp_path: Path) -> None:
    (tmp_path / "deep-research").mkdir()
    (tmp_path / "scopes").mkdir()
    (tmp_path / "note.md").write_text("x", encoding="utf-8")

    lines = demo_tui._list_directory(tmp_path, tmp_path)
    text = "\n".join(lines)
    assert "deep-research/" in text
    assert "note.md" in text


def test_cat_file_previews_json_and_tails_jsonl(tmp_path: Path) -> None:
    (tmp_path / "state.json").write_text('{"a": 1}', encoding="utf-8")
    (tmp_path / "events.jsonl").write_text("\n".join(f'{{"n": {i}}}' for i in range(20)), encoding="utf-8")

    json_lines = demo_tui._cat_file(tmp_path / "state.json", tmp_path)
    assert "a" in "\n".join(json_lines)

    jsonl_lines = demo_tui._cat_file(tmp_path / "events.jsonl", tmp_path)
    text = "\n".join(jsonl_lines)
    assert "尾部" in text
    assert '{"n": 19}' in text


def test_inspect_bundle_summarizes_state_and_report(tmp_path: Path) -> None:
    bundle = tmp_path / "b_demo"
    (bundle / "diagnostics").mkdir(parents=True)
    (bundle / "state.json").write_text(
        '{"terminal_status": "completed", "phase": "final_delivery", "phase_status": "terminal",'
        ' "hitl1_visit_count": 2, "must_answer_questions": ["q1"]}',
        encoding="utf-8",
    )
    (bundle / "diagnostics" / "run-summary.json").write_text(
        '{"journal_availability": "complete", "latest_event_sequence": 30, "dropped_event_count": 0}',
        encoding="utf-8",
    )
    (bundle / "work").mkdir()
    (bundle / "work" / "g0_wave0_w0000").mkdir()
    (bundle / "final").mkdir()
    (bundle / "final" / "report.md").write_text("# R", encoding="utf-8")

    lines = demo_tui._inspect_bundle(bundle)
    text = "\n".join(lines)
    assert "completed" in text
    assert "journal: complete" in text
    assert "g0_wave0_w0000" in text
    assert "report.md" in text


@pytest.mark.asyncio
async def test_tui_slash_ls_renders_persistent_inspect_panel(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _install_scripted(monkeypatch, report=_ready_report("real"), updates=[])
    monkeypatch.setattr(_Adapter, "bundle_root", tmp_path, raising=False)
    (tmp_path / "workspace" / "deep-research").mkdir(parents=True)

    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await _type_composer(app, pilot, "/ls")
        await pilot.press("enter")
        await pilot.pause()
        panel = app.query_one("#inspect").content
        text = str(panel.plain)
        assert "deep-research" in text


@pytest.mark.asyncio
async def test_tui_slash_command_never_dispatches_research_during_hitl1(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_scripted(
        monkeypatch,
        report=_ready_report("real"),
        updates=[run_updates.awaiting_hitl1()],
    )
    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await _type_composer(app, pilot, "start deep research")
        await pilot.press("enter")
        await _wait_for_hitl1_prompt(app, pilot, mode="text")
        intents_before = len(_ScriptedExperience.instances[0].intents)

        await _type_composer(app, pilot, "/ls")
        await pilot.press("enter")
        await pilot.pause()

        assert len(_ScriptedExperience.instances[0].intents) == intents_before
        assert isinstance(app.last_update, AwaitingInput)


@pytest.mark.asyncio
async def test_tui_input_echo_persists_in_inspect_panel(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_scripted(
        monkeypatch,
        report=_ready_report("real"),
        updates=[run_updates.awaiting_hitl1(), run_updates.awaiting_hitl1()],
    )
    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await _type_composer(app, pilot, "start deep research")
        await pilot.press("enter")
        await _wait_for_hitl1_prompt(app, pilot, mode="text")
        await _type_composer(app, pilot, "quick overview")
        await pilot.press("enter")
        await _wait_for(app, pilot, demo_tui.AwaitingInput)
        await pilot.pause()

        panel = str(app.query_one("#inspect").content.plain)
        assert "你: quick overview" in panel


@pytest.mark.asyncio
async def test_tui_hitl1_feedback_surfaces_in_persistent_panel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    update = run_updates.awaiting_hitl1()
    prompt = update.prompt
    rejected = update.model_copy(
        update={"prompt": prompt.model_copy(update={"rejection_category": "profile_input_unrecognized"})}
    )
    _install_scripted(monkeypatch, report=_ready_report("real"), updates=[run_updates.awaiting_hitl1(), rejected])
    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await _type_composer(app, pilot, "start deep research")
        await pilot.press("enter")
        await _wait_for_hitl1_prompt(app, pilot, mode="text")
        await _type_composer(app, pilot, "random text")
        await pilot.press("enter")
        await _wait_for(app, pilot, demo_tui.AwaitingInput)
        await pilot.pause()

        panel = str(app.query_one("#inspect").content.plain)
        assert "你: random text" in panel
        assert "未识别" in panel


def test_recon_tools_are_read_only_and_contained(tmp_path: Path) -> None:
    (tmp_path / "deep-research").mkdir()
    (tmp_path / "note.md").write_text("hello", encoding="utf-8")
    (tmp_path / ".." / "outside.txt").write_text("secret", encoding="utf-8")

    tools = {tool.name: tool for tool in demo_tui._recon_tools(tmp_path)}

    listing = tools["list_workspace"].invoke({"path": ""})
    assert "deep-research" in listing
    assert "note.md" in listing

    content = tools["read_workspace_file"].invoke({"path": "note.md"})
    assert "hello" in content

    escaped = tools["read_workspace_file"].invoke({"path": "../outside.txt"})
    assert "越界" in escaped
    assert "secret" not in escaped

    bad = tools["list_workspace"].invoke({"path": "../../etc"})
    assert "越界" in bad


def test_recon_inspect_bundle_tool_summarizes_bundle(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    bundle = workspace / "deep-research" / "scopes" / "s_demo" / "b_demo"
    (bundle / "final").mkdir(parents=True)
    (bundle / "state.json").write_text(
        '{"terminal_status": "completed", "phase": "final_delivery", "phase_status": "terminal",'
        ' "hitl1_visit_count": 0, "must_answer_questions": ["q"]}',
        encoding="utf-8",
    )
    (bundle / "final" / "report.md").write_text("# R", encoding="utf-8")

    tools = {tool.name: tool for tool in demo_tui._recon_tools(workspace)}
    result = tools["inspect_bundle"].invoke({"bundle_id": "b_demo"})
    assert "completed" in result
    assert "report.md" in result

    missing = tools["inspect_bundle"].invoke({"bundle_id": "b_nope"})
    assert "未找到" in missing


class _FakeStreamModel:
    """Minimal async-stream model for _stream_turn tests."""

    def __init__(self, *rounds: list[Any]) -> None:
        self._rounds = list(rounds)
        self._cursor = 0

    async def astream(self, messages: list[Any]) -> Any:
        del messages
        chunks = self._rounds[min(self._cursor, len(self._rounds) - 1)]
        self._cursor += 1
        for chunk in chunks:
            yield chunk


@pytest.mark.asyncio
async def test_stream_turn_renders_chunks_and_returns_full_text(monkeypatch: pytest.MonkeyPatch) -> None:
    from langchain_core.messages import AIMessageChunk

    _install_scripted(monkeypatch, report=_ready_report("real"), updates=[])
    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    model = _FakeStreamModel([AIMessageChunk(content="hello "), AIMessageChunk(content="world")])

    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        text = await app._stream_turn(model, [], [], echo="你: hi")
        await pilot.pause()
        assert text == "hello world"
        panel = str(app.query_one("#inspect").content.plain)
        assert "你: hi" in panel
        assert "AI: hello world" in panel


@pytest.mark.asyncio
async def test_stream_turn_executes_tool_call_inline(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from langchain_core.messages import AIMessageChunk

    (tmp_path / "deep-research").mkdir()
    _install_scripted(monkeypatch, report=_ready_report("real"), updates=[])
    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    tools = demo_tui._recon_tools(tmp_path)
    _ = None

    tool_chunk = AIMessageChunk(
        content="",
        tool_calls=[
            {
                "name": "list_workspace",
                "args": {},
                "id": "call-1",
                "type": "tool_call",
            }
        ],
    )
    model = _FakeStreamModel(
        [tool_chunk],
        [AIMessageChunk(content="workspace 里有 deep-research。")],
    )

    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        text = await app._stream_turn(model, [], tools, echo="你: 看看")
        await pilot.pause()
        assert "deep-research" in text
        panel = str(app.query_one("#inspect").content.plain)
        assert "AI:" in panel


@pytest.mark.asyncio
async def test_tui_processing_timer_ticks_seconds_in_panel(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_scripted(
        monkeypatch,
        report=_ready_report("real"),
        updates=[run_updates.awaiting_hitl1(), run_updates.awaiting_hitl1()],
    )
    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await _type_composer(app, pilot, "start deep research")
        await pilot.press("enter")
        await _wait_for_hitl1_prompt(app, pilot, mode="text")
        await _type_composer(app, pilot, "quick overview")
        await pilot.press("enter")
        await pilot.pause()
        # no update returned yet -> the timer line should show elapsed seconds
        app._tick_pending()
        panel = str(app.query_one("#inspect").content.plain)
        assert "正在处理" in panel
        assert "s）" in panel
        # once the next AwaitingInput lands, the timer stops and the panel shows feedback
        await _wait_for(app, pilot, demo_tui.AwaitingInput)
        app._stop_pending_timer()
        assert app._pending_timer is None


def test_last_model_call_state_detects_inflight_call(tmp_path: Path) -> None:
    """@impl RED-012 The narration source is the exact bound bundle directory."""

    bundle = tmp_path / "workspace" / "deep-research" / "scopes" / "s_demo" / "b_demo"
    diag = bundle / "diagnostics"
    diag.mkdir(parents=True)
    (diag / "run-summary.json").write_text(
        '{"status": "active", "updated_at": "2026-08-22T01:00:00Z"}', encoding="utf-8"
    )
    (diag / "events.jsonl").write_text(
        '{"category": "node", "phase": "wave0", "outcome": "started", "timestamp": "2026-08-22T01:00:00Z"}\n'
        '{"category": "model_tool", "phase": "wave0", "outcome": "started", "timestamp": "2026-08-22T01:00:01Z"}\n',
        encoding="utf-8",
    )

    outcome, stamp = demo_tui._last_model_call_state(bundle)
    assert outcome == "started"
    assert stamp > 0

    (diag / "events.jsonl").write_text(
        '{"category": "model_tool", "phase": "wave0", "outcome": "completed", "timestamp": "2026-08-22T01:00:02Z"}\n',
        encoding="utf-8",
    )
    outcome, _ = demo_tui._last_model_call_state(bundle)
    assert outcome == "completed"

    assert demo_tui._last_model_call_state(None) == (None, 0.0)


@pytest.mark.asyncio
async def test_tui_blocked_terminal_tells_user_failure_not_completed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from deerflow_deep_research.domain.run_experience import FailureCertainty, RunFailure, RunFailureCode

    failed = run_updates.completed().model_copy(
        update={
            "outcome": "blocked",
            "failure": RunFailure(
                code=RunFailureCode.RESEARCH_BLOCKED,
                certainty=FailureCertainty.DIRECT,
                message="当前研究步骤超出已设置的资源预算。",
                next_action="调整研究范围或预算设置后，启动新的研究运行。",
                retryable=False,
                diagnostic_location="unavailable",
                journal_record_created=False,
            ),
        }
    )
    _install_scripted(monkeypatch, report=_ready_report("real"), updates=[failed])
    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        await _type_composer(app, pilot, "start deep research")
        await pilot.press("enter")
        await _wait_for(app, pilot, demo_tui.Terminal)
        await pilot.pause()

        assert "失败" in app.last_view.detail
        assert "已完成" not in app.last_view.detail
        assert "资源预算" in app.last_view.detail
        assert "重新触发" in app.last_view.detail
        assert app._onboarding is True


def test_live_progress_lines_narrates_a_suspended_visit_as_awaiting_recovery(tmp_path: Path) -> None:
    """@impl RED-012 A bound suspended visit is narrated as awaiting recovery.

    The narration source is the exact bundle the session binds to — recency or
    status never select it. A suspended node visit is not completed and not
    failed; it is shown as awaiting recovery.
    """
    bound = tmp_path / "workspace" / "deep-research" / "scopes" / "s_demo" / "b_bound"
    bound.mkdir(parents=True)
    (bound / "diagnostics").mkdir()
    (bound / "diagnostics" / "run-summary.json").write_text(
        '{"status": "suspended", "updated_at": "2026-08-22T02:00:00Z"}', encoding="utf-8"
    )
    (bound / "diagnostics" / "events.jsonl").write_text(
        '{"category": "node", "outcome": "completed", "phase": "hitl1", "timestamp": "2026-08-22T02:00:00Z"}\n'
        '{"category": "node", "outcome": "completed", "phase": "topic_planning", "timestamp": "2026-08-22T02:00:00Z"}\n'
        '{"category": "node", "outcome": "completed", "phase": "wave0", "timestamp": "2026-08-22T02:00:01Z"}\n'
        '{"category": "node", "outcome": "suspended", "phase": "wave1", "timestamp": "2026-08-22T02:00:02Z"}\n',
        encoding="utf-8",
    )

    lines = demo_tui.live_progress_lines(tmp_path, bundle_id="b_bound")
    text = "\n".join(lines)
    assert "wave1（待恢复）" in text
    assert "wave0" in text and "wave1（进行中）" not in text
    assert "接下来" in text


@pytest.mark.asyncio
async def test_tui_rolling_feed_appends_new_events_incrementally(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:

    _install_scripted(monkeypatch, report=_ready_report("real"), updates=[])
    monkeypatch.setattr(_Adapter, "bundle_root", tmp_path, raising=False)
    bundle = tmp_path / "workspace" / "deep-research" / "scopes" / "s_demo" / "b_demo"
    diag = bundle / "diagnostics"
    diag.mkdir(parents=True)
    (diag / "run-summary.json").write_text(
        '{"status": "suspended", "updated_at": "2026-08-22T04:00:00Z"}', encoding="utf-8"
    )
    events = diag / "events.jsonl"
    events.write_text(
        '{"category": "node", "phase": "wave0", "outcome": "completed", "timestamp": "2026-08-22T04:00:00Z"}\n',
        encoding="utf-8",
    )

    app = demo_tui.DeepResearchDemoTUI(mode="embedded_smoke")
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        app._session_bundle_id = "b_demo"
        app._render_live_activity()
        await pilot.pause()
        # second batch: a new event arrives -> appended, not duplicated
        events.write_text(
            '{"category": "node", "phase": "wave0", "outcome": "completed", "timestamp": "2026-08-22T04:00:00Z"}\n'
            '{"category": "node", "phase": "wave1", "outcome": "completed", "timestamp": "2026-08-22T04:00:01Z"}\n',
            encoding="utf-8",
        )
        app._render_live_activity()
        await pilot.pause()
        text = app._rich_log_text()
        assert text.count("wave0 完成") == 1
        assert "wave1 完成" in text


def test_build_app_wires_debug_flag_into_the_workbench() -> None:
    """`--debug` must reach the app: the C4b CLI wiring was dropped in main()."""
    parser = demo_tui._build_parser()
    debug_app = demo_tui._build_app(parser.parse_args(["--fixture", "--debug"]))
    assert debug_app.mode == "fixture"
    assert debug_app.debug_mode is True
    plain_app = demo_tui._build_app(parser.parse_args(["--fixture"]))
    assert plain_app.mode == "fixture"
    assert plain_app.debug_mode is False


def test_node_context_strip_projects_the_fixed_coverage_labels() -> None:
    """RED-014 coverage strip: every label is projected from the stored view."""
    import hashlib
    from datetime import UTC, datetime

    from deerflow_deep_research.domain.node_context import (
        CapturedResourceLayer,
        EnforcedToolPosture,
        NodeContextSnapshot,
        NodeContextView,
        VirtualRootsView,
    )

    def _digest(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    snapshot = NodeContextSnapshot(
        context_id="ctx-" + "0" * 28,
        bundle_id="b_" + "A" * 43,
        node="wave0",
        attempt_id="g0-wave0-a1",
        node_agent_ordinal=1,
        created_at=datetime.now(UTC),
        initial_system_policy="system policy text",
        initial_human_message="Objective: compare storage",
        base_policy_layer=CapturedResourceLayer(
            identity="resources/node_agent/runtime_policy.md", text="base policy", sha256=_digest("base policy")
        ),
        capability_layer=CapturedResourceLayer(
            identity="pkg:capabilities/wave0.md", text="capability body", sha256=_digest("capability body")
        ),
        request_objective="Compare storage options",
        request_expected_output="A comparison",
        safe_model_label="configured-model",
        tool_posture=EnforcedToolPosture(
            requested_tool_names=("web_search",),
            enforced_tool_names=("web_search",),
            posture_kind="required",
        ),
        budget={"max_model_calls": 8},
        virtual_roots=VirtualRootsView(workspace_root="/mnt/user-data/workspace"),
    )
    captured = DeepResearchDemoTUI._node_context_strip(NodeContextView(snapshot=snapshot))
    for label in (
        "INITIAL CAPTURED",
        "RUNTIME ENFORCED",
        "ACTIVITY BOUNDED",
        "OUTCOME UNAVAILABLE",
        "FILES CURRENT",
        "RAW PROVIDER HISTORIES NOT RETAINED",
    ):
        assert label in captured, f"coverage strip missing {label!r}: {captured!r}"

    observed = DeepResearchDemoTUI._node_context_strip(NodeContextView(snapshot=snapshot, coverage_outcome="OBSERVED"))
    assert "OUTCOME OBSERVED" in observed
    degraded = DeepResearchDemoTUI._node_context_strip(
        NodeContextView(snapshot=snapshot, coverage_initial_context="DEGRADED")
    )
    assert "INITIAL DEGRADED" in degraded
