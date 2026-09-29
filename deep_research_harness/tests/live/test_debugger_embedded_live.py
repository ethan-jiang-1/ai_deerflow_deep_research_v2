"""Live self-verification of the debugger workbench over the real embedded graph.

@impl RED-015
@impl RED-016
@impl LDD-007
@impl LDD-008

Runbook-031's operator journey, driven headlessly through the real Textual
workbench with real credentials and the real model/web tools: the typed HITL
card rendered from the real model's proposal, the drive policy's stated
auto-answer, one real node rerun, a real wave0 capture, and the terminal.
Requires the documented ``.env`` three variables and network; deselected from
ordinary runs by the ``requires_llm`` marker and re-bills real API calls on
every execution - run it deliberately, once.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import demo_tui  # noqa: E402, I001
from _demo_core import load_local_environment  # noqa: E402
from demo_tui import DeepResearchDemoTUI  # noqa: E402

pytestmark = pytest.mark.requires_llm

_QUESTION = "Compare renewable energy storage technologies for grid-scale deployment."


async def _wait(pilot, predicate, *, deadline_seconds: float) -> bool:
    elapsed = 0.0
    while elapsed < deadline_seconds:
        await pilot.pause()
        try:
            if predicate():
                return True
        except AssertionError:
            pass
        await asyncio.sleep(1.0)
        elapsed += 1.0
    return False


def _inspect(app: DeepResearchDemoTUI) -> str:
    return app.query_one("#inspect").render().plain


def _log(app: DeepResearchDemoTUI) -> str:
    return app._rich_log_text()


async def _submit_async(app: DeepResearchDemoTUI, pilot, text: str) -> None:
    app.query_one("#composer", demo_tui.Input).value = text
    await pilot.pause()
    await pilot.press("enter")
    await pilot.pause()


async def _terminal_diagnosis(app: DeepResearchDemoTUI) -> str:
    """On an unexpected terminal, surface the typed incident for the operator."""
    try:
        from deerflow_deep_research.domain.bundle import BundleId

        adapter = app._adapter
        bundle = await adapter._bundle_lifecycle.resolve(
            scope=app._debug_scope(adapter), bundle_id=BundleId(app._debug_bundle_id)
        )
        state = await adapter._bundle_lifecycle.read_state(bundle)
        return (
            f"terminal_status={state.terminal_status} reason={state.terminal_reason} incident={state.latest_incident}"
        )
    except asyncio.CancelledError:
        raise
    except (OSError, RuntimeError, ValueError, AttributeError):
        return "terminal diagnosis unavailable"


@pytest.mark.asyncio
async def test_embedded_debugger_rerun_live(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Fast live lane: question → hitl1 → /rerun regenerates the stop (one flash
    round-trip, no wave0). Proves LDD-007 against the real graph cheaply."""
    assert load_local_environment(), "the harness .env must provide the documented variables"
    monkeypatch.setenv("DEERFLOW_DEMO_BUNDLE_ROOT", str(tmp_path / "demo-runs"))

    app = DeepResearchDemoTUI(mode="embedded_smoke", debug_mode=True)
    async with app.run_test(size=(110, 34)) as pilot:
        assert await _wait(pilot, lambda: isinstance(app.last_update, demo_tui.Ready), deadline_seconds=120), (
            f"preflight never reached Ready: {_inspect(app)!r}"
        )
        await _submit_async(app, pilot, _QUESTION)
        assert await _wait(pilot, lambda: "awaiting_hitl" in _inspect(app), deadline_seconds=300), (
            f"the real run never reached hitl1: {_inspect(app)!r} · {await _terminal_diagnosis(app)}"
        )
        cards_before = _log(app).count("→ 等待 hitl1 输入")

        async def _rerun_regenerated() -> bool:
            # The honest operator signal: the stop's card is rewritten (a fresh
            # proposal), not a frame counter - a rerun re-fills the committed
            # visit slot, so the frame count may hold still.
            return _log(app).count("→ 等待 hitl1 输入") > cards_before and "awaiting_hitl" in _inspect(app)

        await _submit_async(app, pilot, "/rerun")
        elapsed = 0.0
        regenerated = False
        while elapsed < 180.0:
            if await _rerun_regenerated():
                regenerated = True
                break
            await asyncio.sleep(2.0)
            elapsed += 2.0
        assert regenerated, (
            f"the live rerun did not regenerate the stop: {_inspect(app)!r} · "
            f"log tail: {_log(app)[-800:]!r} · {await _terminal_diagnosis(app)}"
        )


@pytest.mark.asyncio
async def test_embedded_debugger_live_journey(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """One real embedded debug run: card, stated auto-answer, rerun, capture, terminal."""
    assert load_local_environment(), "the harness .env must provide the documented variables"
    for name in ("DEEPSEEK_API_KEY", "TAVILY_API_KEY", "DEERFLOW_DEMO_MODEL"):
        assert os.environ.get(name), f"{name} must be present (existence only is checked)"
    monkeypatch.setenv("DEERFLOW_DEMO_BUNDLE_ROOT", str(tmp_path / "demo-runs"))

    app = DeepResearchDemoTUI(mode="embedded_smoke", debug_mode=True)
    async with app.run_test(size=(110, 34)) as pilot:
        assert await _wait(pilot, lambda: isinstance(app.last_update, demo_tui.Ready), deadline_seconds=120), (
            f"preflight never reached Ready: {_inspect(app)!r}"
        )

        # Start Step over a real research question.
        await _submit_async(app, pilot, _QUESTION)
        assert await _wait(pilot, lambda: "awaiting_hitl" in _inspect(app), deadline_seconds=300), (
            f"the real run never reached hitl1: {_inspect(app)!r} · {await _terminal_diagnosis(app)}"
        )
        log = _log(app)
        assert "→ 等待 hitl1 输入" in log, log[-600:]
        assert "context_schema_version" not in log, "machine JSON must never render (RED-015)"
        # The typed card renders from one of its branches: schema-parsed fields,
        # the interaction projection's legal-input guidance, or the proposal
        # scope lines - any one proves the card, not the payload.
        assert any(
            marker in log for marker in ("剩余可接受轮次", "缺少", "请确认", "三种合法输入", "depth:", "must_answer")
        ), f"the real proposal card must render typed fields: {log[-600:]}"

        # LDD-007 live: rerun the last committed node (on the real graph the
        # pending hitl1 visit is itself the trace tail, so this regenerates the
        # proposal) and land on a fresh request at a later frame.
        cards_before = _log(app).count("→ 等待 hitl1 输入")

        async def _rerun_regenerated() -> bool:
            # The honest operator signal: the stop's card is rewritten (a fresh
            # proposal), not a frame counter - a rerun re-fills the committed
            # visit slot, so the frame count may hold still.
            return _log(app).count("→ 等待 hitl1 输入") > cards_before and "awaiting_hitl" in _inspect(app)

        await _submit_async(app, pilot, "/rerun")
        elapsed = 0.0
        regenerated = False
        while elapsed < 300.0:
            if await _rerun_regenerated():
                regenerated = True
                break
            await asyncio.sleep(2.0)
            elapsed += 2.0
        assert regenerated, f"the live rerun did not regenerate the stop: {_inspect(app)!r}"

        # LDD-008 live: the default drive answers proposals as stated operator
        # policy and runs on. When the graph legitimately falls back to the
        # human (the unaccepted-answer bound, or a generation rerun re-asking
        # after a provider hiccup), the probe plays the human - the fallback
        # must be visible in the log and the human touches must stay bounded.
        await _submit_async(app, pilot, "/run")
        deadline = 1800.0
        elapsed = 0.0
        human_touches = 0
        dwell = 0.0
        while elapsed < deadline:
            await pilot.pause()
            inspect = _inspect(app)
            log_now = _log(app)
            if "姿态: terminal" in inspect:
                break
            if "连续推进中" in inspect:
                # The drive pulses honest liveness while it runs; the stale
                # pre-drive posture is not a stop.
                dwell = 0.0
                await asyncio.sleep(2.0)
                elapsed += 2.0
                continue
            if "awaiting_hitl" in inspect and "hitl2" in inspect:
                dwell = 0.0
                await _submit_async(app, pilot, "proceed")
            elif "awaiting_hitl" in inspect and "hitl1" in inspect:
                dwell += 2.0
                if dwell >= 90.0:
                    # The policy fell back to the human: the stop must say so.
                    assert "回答已消费" in log_now or "hitl1 回复" in log_now or "剩余" in log_now, (
                        f"the fallback stop must state the consumption outcome: {log_now[-800:]}"
                    )
                    human_touches += 1
                    assert human_touches <= 4, f"too many human fallbacks: {log_now[-800:]}"
                    dwell = 0.0
                    await _submit_async(app, pilot, "确认")
            else:
                dwell = 0.0
            await asyncio.sleep(2.0)
            elapsed += 2.0
        assert "姿态: terminal" in _inspect(app), (
            f"the live drive never reached terminal: {_inspect(app)!r} · {await _terminal_diagnosis(app)} · "
            f"log tail: {_log(app)[-800:]!r}"
        )
        final_log = _log(app)
        assert "drive 策略代答" in final_log, "the auto-answer must be stated, never silent (RED-016)"

        # RED-015 live: a real wave0 (or later LLM-bearing node) capture exists.
        from deerflow_deep_research.domain.bundle import BundleId
        from deerflow_deep_research.runtime.node_context_store import NodeContextStore

        adapter = app._adapter
        bundle = await adapter._bundle_lifecycle.resolve(
            scope=app._debug_scope(adapter), bundle_id=BundleId(app._debug_bundle_id)
        )
        page = NodeContextStore(
            bundle_root=adapter._bundle_lifecycle.private_root(bundle),
            bundle_id=app._debug_bundle_id,
        ).page()
        assert page.total >= 1, "a real LLM-bearing node must have captured its context"
