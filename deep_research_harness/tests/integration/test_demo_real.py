"""Deterministic shared-interface coverage for the standalone real CLI.

@impl REC-001
@impl REC-002
@impl REC-003
@impl REC-005
@impl REC-006
@impl REC-008
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
from deerflow_deep_research.domain.profile import RequestLanguage, derive_comparison_intake_seed
from deerflow_deep_research.domain.run_experience import (
    AnswerRun,
    FailureCertainty,
    Fault,
    ProviderObservation,
    ReadinessCheck,
    ReadinessReport,
    RunFailure,
    RunFailureCode,
    RunSnapshot,
    SelectControlRun,
    StartRun,
    Working,
)
from tests.fixtures import run_updates

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import demo_real  # noqa: E402, I001


def _ready_report() -> ReadinessReport:
    return ReadinessReport(
        mode="real",
        ready=True,
        summary="Ready for a deterministic presentation test.",
        checks=(ReadinessCheck(name="mode", ready=True, detail="real"),),
        durability_note="Temporary standalone demo.",
    )


def _failed_report() -> ReadinessReport:
    return ReadinessReport(
        mode="real",
        ready=False,
        summary="Model setup is missing.",
        checks=(ReadinessCheck(name="model", ready=False, detail="missing", next_action="Configure a model."),),
        failure=RunFailure(
            code=RunFailureCode.CONFIGURATION_MODEL_MISSING,
            certainty=FailureCertainty.DIRECT,
            message="Model setup is missing.",
            next_action="Configure a model.",
            retryable=True,
            journal_record_created=False,
            diagnostic_location="unavailable",
        ),
        durability_note="No research record was created.",
    )


class _Adapter:
    created: list[_Adapter] = []

    def __init__(self) -> None:
        self.closed = False
        type(self).created.append(self)

    @classmethod
    def for_real(cls) -> _Adapter:
        """Represent a test environment whose real-demo preflight already passed."""
        return cls()

    async def create_work_unit_store(self, *_args: Any, **_kwargs: Any) -> object:
        return object()

    def close(self) -> None:
        self.closed = True


class _ScriptedExperience:
    updates: deque[object] = deque()
    instances: list[_ScriptedExperience] = []
    block_dispatch = False
    started: asyncio.Event | None = None

    def __init__(self, *, transport, mode, readiness_provider, **_kwargs: Any) -> None:
        self.transport = transport
        self.mode = mode
        self._readiness_provider = readiness_provider
        self.intents: list[object] = []
        type(self).instances.append(self)

    async def preflight(self) -> ReadinessReport:
        return self._readiness_provider()

    async def handle(self, intent: object, observer=None) -> object:
        self.intents.append(intent)
        if observer is not None:
            action = "start" if isinstance(intent, StartRun) else "resume"
            observer(Working(snapshot=RunSnapshot(), action=action, message="waiting"))
        if type(self).block_dispatch:
            assert type(self).started is not None
            type(self).started.set()
            await asyncio.Event().wait()
        return type(self).updates.popleft()


def _install_experience(
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
    _ScriptedExperience.block_dispatch = False
    _ScriptedExperience.started = None
    monkeypatch.setattr(demo_real, "DemoAdapter", _Adapter)
    monkeypatch.setattr(demo_real, "ResearchRunExperience", _ScriptedExperience)
    monkeypatch.setattr(demo_real, "build_demo_runtime", build_runtime)
    monkeypatch.setattr(demo_real, "demo_readiness_report", lambda **_kwargs: report)
    return runtime_modes


def test_cli_collects_safe_question_only_after_preflight(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _install_experience(monkeypatch, report=_ready_report(), updates=[])
    answers = iter(("  ", "Compare \x1b[31mstorage\x1b[0m costs"))
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    assert demo_real.select_question(question=None, scripted=False) == "Compare \x1b[31mstorage\x1b[0m costs"
    output = capsys.readouterr().out
    assert "不能为空" in output
    assert "\x1b" not in output

    with pytest.raises(demo_real.CliInputError):
        demo_real.select_question(question="  ", scripted=False)

    monkeypatch.setattr("builtins.input", lambda _prompt: (_ for _ in ()).throw(EOFError))
    assert asyncio.run(demo_real.run_demo(question=None, scripted=False, embedded_smoke=True)) == 130
    assert not _Adapter.created


@pytest.mark.asyncio
async def test_cli_follows_only_shared_awaiting_updates_and_preserves_graph_owned_choices(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _install_experience(
        monkeypatch,
        report=_ready_report(),
        updates=[run_updates.awaiting_hitl1(), run_updates.awaiting_hitl2(), run_updates.completed()],
    )
    answers = iter(("profile answer", "not-an-advertised-choice"))
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    assert await demo_real.run_demo(question="Research storage", scripted=False, embedded_smoke=True) == 0

    intents = _ScriptedExperience.instances[0].intents
    assert isinstance(intents[0], StartRun)
    assert isinstance(intents[1], AnswerRun)
    assert isinstance(intents[2], AnswerRun)
    assert intents[2].value == "not-an-advertised-choice"
    output = capsys.readouterr().out
    assert "Confirm research scope" in output
    assert "rerun:" in output
    assert "研究流程已完成" in output
    assert _Adapter.created[0].closed is True


@pytest.mark.asyncio
async def test_cli_obtains_the_fixed_all_real_runtime_after_preflight(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime_modes = _install_experience(monkeypatch, report=_ready_report(), updates=[run_updates.completed()])

    assert await demo_real.run_demo(question="Compare storage approaches", scripted=False, embedded_smoke=True) == 0
    assert runtime_modes == ["real"]


@pytest.mark.asyncio
async def test_cli_runtime_construction_fault_cannot_render_full_fake_completion(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _install_experience(monkeypatch, report=_ready_report(), updates=[run_updates.completed()])

    def fail_runtime(**_kwargs: object) -> object:
        raise RuntimeError("demo_runtime_unavailable")

    monkeypatch.setattr(demo_real, "build_demo_runtime", fail_runtime)

    assert await demo_real.run_demo(question="Compare storage approaches", scripted=False, embedded_smoke=True) == 1
    output = capsys.readouterr().out
    assert "本地演示无法启动" in output
    assert "研究流程已完成" not in output
    assert _ScriptedExperience.instances[0].intents == []
    assert _Adapter.created[0].closed is True


def test_cli_selects_numbered_visible_control_without_rewriting_natural_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl REC-007"""
    update = run_updates.awaiting_hitl1(
        feedback=InteractionFeedback(
            kind=InteractionFeedbackKind.SEMANTIC_UNAVAILABLE,
            message="The proposal is still available after a temporary interpretation failure.",
        )
    )
    answers = iter(("1", "采用建议"))
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    selected = demo_real._ask_answer(update)
    natural_text = demo_real._ask_answer(update)

    assert selected == SelectControlRun(control_id="accept_current_proposal")
    assert natural_text == AnswerRun(value="采用建议")
    rendered = "\n".join(demo_real.render_run_update(update))
    assert "1. Start with the current proposal" in rendered
    assert "temporary interpretation failure" in rendered


@pytest.mark.asyncio
async def test_scripted_cli_is_stdin_free_and_preserves_explicit_question(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _install_experience(monkeypatch, report=_ready_report(), updates=[run_updates.completed(), run_updates.completed()])
    monkeypatch.setattr("builtins.input", lambda _prompt: (_ for _ in ()).throw(AssertionError("stdin is forbidden")))

    assert await demo_real.run_demo(question=None, scripted=True, embedded_smoke=True) == 0
    assert await demo_real.run_demo(question="Compare storage costs", scripted=True, embedded_smoke=True) == 0

    first, second = (instance.intents[0] for instance in _ScriptedExperience.instances)
    assert isinstance(first, StartRun) and first.scripted is True
    assert isinstance(second, StartRun) and second.scripted is True
    assert first.question == demo_real.SCRIPTED_DEFAULT_QUESTION
    assert second.question == "Compare storage costs"
    assert "自动策略" in capsys.readouterr().out


async def test_scripted_cli_declares_minimal_intent_by_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl DPL-003 — absent explicit selection, embedded-smoke scripted stays minimal."""

    _install_experience(monkeypatch, report=_ready_report(), updates=[run_updates.completed()])

    assert await demo_real.run_demo(question="Compare storage costs", scripted=True, embedded_smoke=True) == 0

    start = _ScriptedExperience.instances[0].intents[0]
    assert isinstance(start, StartRun)
    assert start.profile_intent == "minimal"


async def test_scripted_cli_explicit_none_intent_omits_the_declaration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """@impl DPL-003, HRA-001 — --profile-intent none runs the default product path."""

    _install_experience(monkeypatch, report=_ready_report(), updates=[run_updates.completed()])

    assert (
        await demo_real.run_demo(
            question="Compare China and US EV battery market in 2024.",
            scripted=True,
            embedded_smoke=True,
            profile_intent="none",
        )
        == 0
    )

    start = _ScriptedExperience.instances[0].intents[0]
    assert isinstance(start, StartRun)
    assert start.profile_intent is None


def test_profile_intent_selection_is_rejected_outside_embedded_smoke_scripted(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """@impl DPL-003 — an explicit intent selection is a usage error off its route."""

    for argv in (
        ["demo_real.py", "--profile-intent", "none"],
        ["demo_real.py", "--embedded-smoke", "--profile-intent", "none"],
    ):
        monkeypatch.setattr(sys, "argv", argv)
        with pytest.raises(SystemExit) as excinfo:
            demo_real.main()
        assert excinfo.value.code == 2
        assert "--profile-intent" in capsys.readouterr().err


def test_scripted_real_question_has_a_supported_language_and_explicit_comparison_pair() -> None:
    seed = derive_comparison_intake_seed(demo_real.SCRIPTED_DEFAULT_QUESTION)

    assert seed.request_language is RequestLanguage.EN
    assert seed.comparison_required is True
    assert seed.comparison_subjects is not None


@pytest.mark.asyncio
async def test_cli_stops_before_question_when_preflight_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_experience(monkeypatch, report=_failed_report(), updates=[])
    monkeypatch.setattr(
        "builtins.input",
        lambda _prompt: (_ for _ in ()).throw(AssertionError("question must not be asked")),
    )

    assert await demo_real.run_demo(question=None, scripted=False, embedded_smoke=True) == 2
    assert not _Adapter.created
    assert _ScriptedExperience.instances[0].intents == []


@pytest.mark.asyncio
async def test_cli_propagates_local_cancellation_without_graph_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_experience(monkeypatch, report=_ready_report(), updates=[])
    _ScriptedExperience.block_dispatch = True
    _ScriptedExperience.started = asyncio.Event()

    task = asyncio.create_task(demo_real.run_demo(question="Research storage", scripted=False, embedded_smoke=True))
    await asyncio.wait_for(_ScriptedExperience.started.wait(), timeout=2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    intents = _ScriptedExperience.instances[0].intents
    assert len(intents) == 1 and isinstance(intents[0], StartRun)
    assert _Adapter.created[0].closed is True


def test_cli_deduplicates_returned_only_waiting_heartbeat(capsys: pytest.CaptureFixture[str]) -> None:
    observer = demo_real._dispatch_observer()
    waiting = Working(snapshot=RunSnapshot(), action="start", message="waiting for lifecycle result")

    observer(waiting)
    observer(waiting)

    assert capsys.readouterr().out.count("waiting for lifecycle result") == 1


def test_cli_renders_a_fault_bundle_without_exposing_raw_lifecycle_details() -> None:
    update = Fault(
        snapshot=RunSnapshot(
            bundle_id=run_updates.BUNDLE_ID,
            durability="restart_durable",
            lifecycle_phase="hitl1",
        ),
        failure=RunFailure(
            code=RunFailureCode.PROTOCOL_INVALID_RESULT,
            phase="hitl1",
            certainty=FailureCertainty.DIRECT,
            message="raw lifecycle payload must not be displayed",
            next_action="Query the selected Bundle through lifecycle control.",
            retryable=False,
            journal_record_created=False,
            diagnostic_location="unavailable",
        ),
    )

    rendered = "\n".join(demo_real.render_run_update(update))

    assert f"Run Bundle: {run_updates.BUNDLE_ID}" in rendered
    assert "持久性: restart_durable" in rendered
    assert "raw lifecycle payload" not in rendered
    assert "可恢复当前运行" not in rendered


def test_cli_renders_one_safe_fresh_start_and_matching_read_only_diagnosis() -> None:
    update = run_updates.exhausted_provider_terminal()
    assert update.failure is not None
    normal_rendered = "\n".join(demo_real.render_run_update(update))
    assert "bridge_wall_time_budget" in normal_rendered
    assert "provider_sdk_timeout" in normal_rendered
    unsafe_observation = ProviderObservation.model_construct(
        configured_service_label="deepseek-v4-pro",
        configured_endpoint_authority="https://api.example.test/v1?token=secret#fragment",
        response_kind="no_response",
        http_status=None,
    )
    unsafe_failure = update.failure.model_copy(
        update={
            "message": "question=private answer=private prompt=private raw-diagnostic=private",
            "provider_observation": unsafe_observation,
        }
    )
    unsafe_update = update.model_copy(update={"failure": unsafe_failure})

    rendered = "\n".join(demo_real.render_run_update(unsafe_update))

    assert "provider.timeout" in rendered
    assert "deepseek-v4-pro" in rendered
    assert "2" in rendered and "1" in rendered
    assert "make demo-real" in rendered
    assert 'make demo-sessions DEMO_ARGS="inspect ' + run_updates.BUNDLE_ID + '"' in rendered
    assert "只读诊断" in rendered
    assert "bridge_wall_time_budget" in rendered
    assert "provider_sdk_timeout" not in rendered
    assert "可启动一个独立的新研究运行" not in rendered
    for unsafe in (
        "/v1",
        "token=secret",
        "fragment",
        "question=private",
        "answer=private",
        "prompt=private",
        "raw-diagnostic=private",
    ):
        assert unsafe not in rendered
    assert "可恢复当前运行" not in rendered


@pytest.mark.parametrize(
    ("update", "category", "legal_next_action"),
    (
        pytest.param(
            run_updates.exhausted_provider_terminal(),
            "provider.timeout",
            "新启动: make demo-real",
            id="provider-terminal",
        ),
        pytest.param(
            run_updates.typed_hitl1_terminal(code=RunFailureCode.OUTPUT_STRUCTURED_INVALID),
            "output.structured_invalid",
            "下一步: 重新开始该研究；若持续出现，请提供诊断引用。",
            id="structured-output-terminal",
        ),
        pytest.param(
            run_updates.typed_hitl1_terminal(code=RunFailureCode.RESEARCH_BLOCKED),
            "research.blocked",
            "下一步: 根据提示检查前提条件或提供诊断引用。",
            id="generic-blocked-terminal",
        ),
    ),
)
def test_cli_preserves_typed_terminal_category_without_leaking_source_text(
    update,
    category: str,
    legal_next_action: str,
) -> None:
    """@impl REC-002
    @impl REC-006
    """
    rendered = "\n".join(demo_real.render_run_update(update))

    assert f"结果类别: {category}" in rendered
    assert "已知阶段: hitl1" in rendered
    assert "诊断引用: " + run_updates.DIAGNOSTIC_REF in rendered
    assert "持久性: same_process" in rendered
    assert legal_next_action in rendered
    assert "可恢复当前运行" not in rendered
    for unsafe in (
        "question=private",
        "prompt=private",
        "provider-body=private",
        "secret.example.test",
        "token=secret",
        "exception=private",
    ):
        assert unsafe not in rendered


def test_cli_renders_topic_planning_timeout_with_only_its_legal_new_start() -> None:
    """@impl REC-006
    @impl WFO-001
    """
    rendered = "\n".join(demo_real.render_run_update(run_updates.exhausted_provider_terminal(phase="topic_planning")))

    assert "provider.timeout" in rendered
    assert "topic_planning" in rendered
    assert "恢复处置: exhausted" in rendered
    assert "诊断引用: " + run_updates.DIAGNOSTIC_REF in rendered
    assert "新启动: make demo-real" in rendered
    assert "可恢复当前运行" not in rendered
    assert "下一步:" not in rendered


def test_cli_renders_controller_provider_diagnosis_without_turning_inspection_into_recovery() -> None:
    """@impl REC-006
    @impl WFO-001
    """
    rendered = "\n".join(demo_real.render_run_update(run_updates.controller_provider_terminal()))

    assert "provider.timeout" in rendered
    assert "wave0" in rendered
    assert "agent_invocation" in rendered
    assert "诊断引用: " + run_updates.DIAGNOSTIC_REF in rendered
    assert "只读诊断" in rendered
    assert "新启动: make demo-real" not in rendered
    assert "可恢复当前运行" not in rendered


def test_cli_does_not_offer_inspection_for_a_stale_terminal_observation() -> None:
    rendered = "\n".join(
        demo_real.render_run_update(run_updates.exhausted_provider_terminal(matching_observation=False))
    )

    assert "make demo-real" in rendered
    assert "demo-sessions" not in rendered


def test_cli_does_not_offer_inspection_for_an_unavailable_terminal_observation() -> None:
    rendered = "\n".join(
        demo_real.render_run_update(run_updates.exhausted_provider_terminal(observation_available=False))
    )

    assert "make demo-real" in rendered
    assert "demo-sessions" not in rendered


def test_cli_uses_the_same_static_command_after_the_repair_slot_is_consumed() -> None:
    rendered = "\n".join(demo_real.render_run_update(run_updates.repair_slot_provider_terminal()))

    assert "retry_not_started_budget_consumed" in rendered
    assert "自动重试: 0 次" in rendered
    assert "make demo-real" in rendered
    assert "下一步:" not in rendered
