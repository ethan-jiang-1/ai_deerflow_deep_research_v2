"""CLI and TUI presentation adapters consume only shared RunUpdate fixtures.

@impl REC-003
@impl RED-003
@impl DPL-002
@impl RER-003
@impl RER-001
@impl RER-006
@impl RER-007
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

from deerflow_deep_research.domain.run_experience import AwaitingInput, Fault, StartRun, Working
from deerflow_deep_research.domain.run_observation import (
    ObservationInspectability,
    RetentionState,
    RunObservationView,
)
from deerflow_deep_research.runtime.run_experience import ResearchRunExperience
from tests.fixtures import run_updates

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import demo_real  # noqa: E402, I001
import demo_tui  # noqa: E402, I001


@pytest.mark.parametrize(
    "update",
    [
        pytest.param(run_updates.awaiting_hitl1(), id="hitl1"),
        pytest.param(run_updates.awaiting_hitl1_language_choice(), id="hitl1-choice"),
        pytest.param(run_updates.completed(), id="terminal"),
        pytest.param(run_updates.auto_profile_terminal(), id="terminal-auto-profile"),
        pytest.param(run_updates.provider_fault(), id="fault"),
    ],
)
def test_standalone_adapters_render_shared_run_updates_without_lifecycle_wire(update: object) -> None:
    cli_lines = demo_real.render_run_update(update)
    tui_view = demo_tui.render_run_update(update)

    assert cli_lines
    assert tui_view.heading
    rendered = "\n".join(cli_lines) + "\n" + tui_view.detail
    assert "ToolMessage" not in rendered
    assert "human_input" not in rendered
    assert "traceback" not in rendered.lower()


def test_tui_pipeline_tracker_renders_presentation_only_trace_steps() -> None:
    from rich.console import Console

    tracker = demo_tui._pipeline_tracker(
        ("hitl1", "hitl1_auto_profile", "hitl2", "hitl2_auto_proceed", "final_delivery"),
        pending=None,
    )
    console = Console(record=True, width=80)
    console.print(tracker)
    rendered = console.export_text()
    assert "hitl1_auto_profile" not in rendered
    assert "hitl2_auto_proceed" not in rendered
    assert "自动建档" in rendered
    assert "自动决策" in rendered


def test_standalone_adapters_render_safe_invalid_choice_feedback_without_wire_data() -> None:
    """Invalid-choice feedback is proved on the current HITL1 language CHOICE surface.

    HITL2 is an autonomous graph phase and fabricates no pending choice, so the
    typed-choice retry projection is exercised with the advertised zh/en
    options instead of retired HITL2 route labels.
    """
    update = run_updates.awaiting_invalid_language_choice()

    cli = "\n".join(demo_real.render_run_update(update))
    tui = demo_tui.render_run_update(update)

    assert "上一次选择无效；请只输入上方显示的选项 ID，例如 zh。" in cli
    assert "The last choice was invalid. Enter an advertised option ID, for example zh." in tui.detail
    assert tui.placeholder == "Choose an advertised option ID"
    assert tui.options == ("zh", "en")
    for rendered in (cli, tui.detail):
        assert "proceed" not in rendered
        assert "proceed: secret=displayed-consequence" not in rendered
        assert "human_input" not in rendered
        assert "traceback" not in rendered.lower()


def test_standalone_adapters_render_every_complete_proposal_line_before_control() -> None:
    """@impl RER-012"""
    update = run_updates.awaiting_complete_typed_hitl1()
    cli = "\n".join(demo_real.render_run_update(update))
    tui = demo_tui.render_run_update(update).detail

    assert len(update.prompt.proposed_scope) == 17
    for line in update.prompt.proposed_scope:
        assert line in cli
        assert line in tui
    assert cli.index("output_language: zh") < cli.index("Start with the current proposal")
    assert tui.index("output_language: zh") < tui.index("Start with the current proposal")


def test_standalone_adapters_render_the_same_retained_observation() -> None:
    update = run_updates.awaiting_hitl1()
    observation = RunObservationView(
        bundle_id=run_updates.BUNDLE_ID,
        inspectability=ObservationInspectability.AVAILABLE,
        retention_state=RetentionState.RETAINED,
        durability="same_process",
    )
    retained_update = update.model_copy(
        update={"snapshot": update.snapshot.model_copy(update={"observation": observation})}
    )

    assert isinstance(retained_update, AwaitingInput)
    cli = "\n".join(demo_real.render_run_update(retained_update))
    tui = demo_tui.render_run_update(retained_update).detail
    expected = 'make demo-sessions DEMO_ARGS="inspect ' + run_updates.BUNDLE_ID + '"'

    for rendered in (cli, tui):
        assert expected in rendered
        assert "same_process" in rendered
    assert "retained" in cli


def test_standalone_adapters_render_only_observed_returned_only_wait_facts() -> None:
    update = Working(
        snapshot=run_updates.awaiting_hitl1().snapshot.model_copy(
            update={"elapsed_seconds": 2.5, "lifecycle_phase": "bootstrap"}
        ),
        action="start",
        message="Waiting for lifecycle return (returned-only mode).",
    )
    cli = "\n".join(demo_real.render_run_update(update))
    tui = demo_tui.render_run_update(update).detail

    for rendered in (cli, tui):
        assert "bootstrap" in rendered
        assert "traceback" not in rendered.lower()
    # The TUI drops elapsed seconds (semantics over counters); the CLI keeps them.
    assert "2.5" not in tui
    assert "2.5" in cli


def test_terminal_receipt_is_inspectable_but_honest_about_same_process_durability() -> None:
    observation = RunObservationView(
        bundle_id=run_updates.BUNDLE_ID,
        inspectability=ObservationInspectability.AVAILABLE,
        retention_state=RetentionState.RETAINED,
        durability="same_process",
    )
    completed = run_updates.completed()
    update = completed.model_copy(
        update={"snapshot": completed.snapshot.model_copy(update={"observation": observation})}
    )

    cli = "\n".join(demo_real.render_run_update(update))
    tui = demo_tui.render_run_update(update).detail
    for rendered in (cli, tui):
        assert "inspect" in rendered.lower() or "查看" in rendered
        assert "process exit" in rendered.lower() or "进程退出" in rendered


@pytest.mark.asyncio
async def test_shared_failure_never_leaks_raw_exception_into_either_adapter(tmp_path: Path) -> None:
    sentinel = "provider body secret=sentinel /Users/alice/private"

    class ExplodingTransport:
        async def dispatch(self, **_kwargs: Any) -> object:
            raise RuntimeError(sentinel)

    update = await ResearchRunExperience(
        transport=ExplodingTransport(),
        mode="real",
    ).handle(StartRun(question="Compare storage options"))

    assert isinstance(update, Fault)
    cli = "\n".join(demo_real.render_run_update(update))
    tui = demo_tui.render_run_update(update).detail
    assert sentinel not in cli
    assert sentinel not in tui
    assert not (tmp_path / "records.jsonl").exists()


def _write_journal_bundle(
    root: Path,
    *,
    scope: str,
    bundle: str,
    updated_at: str,
    events: list[dict[str, Any]],
) -> Path:
    bundle_dir = root / "workspace" / "deep-research" / "scopes" / scope / bundle
    diag = bundle_dir / "diagnostics"
    diag.mkdir(parents=True)
    (diag / "run-summary.json").write_text(
        json.dumps({"status": "active", "updated_at": updated_at, "bundle_id": bundle}),
        encoding="utf-8",
    )
    (diag / "events.jsonl").write_text(
        "\n".join(json.dumps(event) for event in events) + "\n",
        encoding="utf-8",
    )
    return bundle_dir


def test_live_progress_lines_reports_active_bundle_journal(tmp_path: Path) -> None:
    bundle = _write_journal_bundle(
        tmp_path,
        scope="s_demo",
        bundle="b_demo",
        updated_at="2026-08-21T11:00:00Z",
        events=[
            {"category": "node", "outcome": "started", "phase": "bootstrap", "timestamp": "2026-08-21T10:59:50Z"},
            {"category": "node", "outcome": "completed", "phase": "bootstrap", "timestamp": "2026-08-21T10:59:50Z"},
            {"category": "node", "outcome": "started", "phase": "wave0", "timestamp": "2026-08-21T10:59:56Z"},
            {
                "category": "model_tool",
                "outcome": "completed",
                "phase": "wave0",
                "usage_tokens": {"total_tokens": 10415},
                "timestamp": "2026-08-21T11:00:27Z",
            },
            {"category": "node", "outcome": "completed", "phase": "wave0", "timestamp": "2026-08-21T11:00:27Z"},
            {"category": "node", "outcome": "started", "phase": "wave1", "timestamp": "2026-08-21T11:00:27Z"},
        ],
    )
    assert bundle.is_dir()

    lines = demo_tui.live_progress_lines(tmp_path)
    assert lines
    text = "\n".join(lines)
    assert "进度: bootstrap → wave0 → wave1（进行中）" in text
    assert "接下来" in text
    assert "最近:" in text
    # counters are omitted (semantics over counters)
    assert "模型调用:" not in text
    assert "journal 事件:" not in text


def test_live_progress_lines_picks_most_recent_active_bundle(tmp_path: Path) -> None:
    _write_journal_bundle(
        tmp_path,
        scope="s_old",
        bundle="b_old",
        updated_at="2026-08-21T09:00:00Z",
        events=[
            {"category": "node", "outcome": "started", "phase": "bootstrap", "timestamp": "2026-08-21T09:00:00Z"},
            {"category": "node", "outcome": "completed", "phase": "bootstrap", "timestamp": "2026-08-21T09:00:01Z"},
        ],
    )
    _write_journal_bundle(
        tmp_path,
        scope="s_new",
        bundle="b_new",
        updated_at="2026-08-21T11:05:00Z",
        events=[
            {"category": "node", "outcome": "started", "phase": "wave2_synthesis", "timestamp": "2026-08-21T11:05:00Z"},
        ],
    )

    lines = demo_tui.live_progress_lines(tmp_path)
    text = "\n".join(lines)
    assert "b_new" not in text  # bundle id is not rendered; the *phase* is what matters
    assert "wave2_synthesis（进行中）" in text
    assert "bootstrap" not in text  # the older bundle was not selected


def test_live_progress_lines_returns_empty_without_active_bundle(tmp_path: Path) -> None:
    assert demo_tui.live_progress_lines(None) == ()
    assert demo_tui.live_progress_lines(tmp_path) == ()
    (tmp_path / "workspace" / "deep-research" / "scopes").mkdir(parents=True)
    assert demo_tui.live_progress_lines(tmp_path) == ()


def test_find_bundle_dir_and_report_path(tmp_path: Path) -> None:
    bundle_dir = _write_journal_bundle(
        tmp_path,
        scope="s_demo",
        bundle="b_report",
        updated_at="2026-08-21T12:00:00Z",
        events=[
            {"category": "node", "outcome": "started", "phase": "bootstrap", "timestamp": "2026-08-21T12:00:00Z"},
            {"category": "node", "outcome": "completed", "phase": "bootstrap", "timestamp": "2026-08-21T12:00:01Z"},
        ],
    )
    final = bundle_dir / "final"
    final.mkdir()
    (final / "report.md").write_text("# Report\n", encoding="utf-8")

    assert demo_tui.find_bundle_dir(tmp_path, "b_report") == bundle_dir
    assert demo_tui.find_bundle_dir(tmp_path, "b_missing") is None
    assert demo_tui.find_bundle_dir(None, "b_report") is None

    report = demo_tui.report_path(tmp_path, "b_report")
    assert report is not None and report.name == "report.md" and report.is_file()
    assert demo_tui.report_path(tmp_path, "b_missing") is None
    assert demo_tui.report_path(tmp_path, None) is None


def test_render_terminal_includes_report_path_when_provided(tmp_path: Path) -> None:
    completed = run_updates.completed()
    view = demo_tui.render_run_update(completed, report_path=tmp_path / "final" / "report.md")
    assert view.terminal
    assert "Report:" in view.detail
    assert "report.md" in view.detail

    view_without = demo_tui.render_run_update(completed)
    assert "Report:" not in view_without.detail


def test_render_hitl1_rejection_surfaces_last_typed_and_formats() -> None:
    update = run_updates.awaiting_hitl1()
    prompt = update.prompt
    rejected = update.model_copy(
        update={"prompt": prompt.model_copy(update={"rejection_category": "profile_input_unrecognized"})}
    )

    view = demo_tui.render_run_update(rejected, last_typed="some unclear text")
    assert "你输入的是: some unclear text" in view.detail
    assert "字段: 值" in view.detail
    assert "快捷按钮" in view.detail

    view_without = demo_tui.render_run_update(rejected)
    assert "你输入的是" not in view_without.detail
