"""Debug workbench Pilot journey: --debug fixture composition end to end.

@impl RED-013
@impl RED-014
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import demo_tui  # noqa: E402, I001
from demo_tui import DeepResearchDemoTUI  # noqa: E402, I001
from tests.integration.test_demo_tui import (  # noqa: E402, I001
    _install_isolated_fixture_adapter,
    _wait_for,
    _type_composer,
)

_WAIT = 20.0


@pytest.mark.asyncio
async def test_debug_journey_start_step_hitl_answer_detach(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """--debug workbench: question → Start Step → HITL answer → detach."""
    _install_isolated_fixture_adapter(monkeypatch, bundle_root=tmp_path / "demo-runs")
    app = DeepResearchDemoTUI(mode="fixture", debug_mode=True)
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready, max_wait=_WAIT)

        # Operator types a question and submits → debug session opens.
        await _type_composer(app, pilot, "Compare renewable storage technologies")
        await pilot.press("enter")
        await pilot.pause()
        assert app._debug_driver is not None, "debug session must open on submit"
        assert app._debug_bundle_id is not None
        assert app._node_context_holder["recorder"] is not None

        # Start Step committed bootstrap; the hitl1 pause projects as a card.
        # The composer Enter advances into hitl1 (which interrupts).
        await _type_composer(app, pilot, "advance")
        await pilot.press("enter")
        await pilot.pause()

        # hitl1 is now awaiting input → the composer answer resumes.
        await _type_composer(app, pilot, "Use the default profile.")
        await pilot.press("enter")
        await pilot.pause()

        # /context reads the C3 store.
        await _type_composer(app, pilot, "/context")
        await pilot.press("enter")
        await pilot.pause()

        # /detach ends the session cleanly.
        await _type_composer(app, pilot, "/detach")
        await pilot.press("enter")
        await pilot.pause()
        assert app._debug_driver is None, "detach must clear the driver session"
