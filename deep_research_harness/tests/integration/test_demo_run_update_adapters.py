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
from deerflow_deep_research.runtime.run_diagnostics import DemoDiagnosticJournal
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
        pytest.param(run_updates.awaiting_hitl2(), id="hitl2"),
        pytest.param(run_updates.completed(), id="terminal"),
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


def test_standalone_adapters_render_safe_invalid_choice_feedback_without_wire_data() -> None:
    update = run_updates.awaiting_invalid_hitl2_choice()

    cli = "\n".join(demo_real.render_run_update(update))
    tui = demo_tui.render_run_update(update)

    assert "上一次选择无效；请只输入上方显示的选项 ID，例如 proceed。" in cli
    assert "The last choice was invalid. Enter an advertised option ID, for example proceed." in tui.detail
    assert tui.placeholder == "Choose an advertised option ID"
    assert tui.options == ("proceed", "rerun", "repair", "revise_view", "stop")
    for rendered in (cli, tui.detail):
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
        assert "2.5" in rendered
        assert "traceback" not in rendered.lower()


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
        diagnostics=DemoDiagnosticJournal(path=tmp_path / "records.jsonl"),
    ).handle(StartRun(question="Compare storage options"))

    assert isinstance(update, Fault)
    cli = "\n".join(demo_real.render_run_update(update))
    tui = demo_tui.render_run_update(update).detail
    assert sentinel not in cli
    assert sentinel not in tui
    assert sentinel not in (tmp_path / "records.jsonl").read_text(encoding="utf-8")
