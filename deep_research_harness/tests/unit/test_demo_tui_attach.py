"""Attach projection for recoverable bundles (RED-011, BUG-064).

Presentation-only contract: the scan filters lifecycle-projected RESUME
bundles, the card renders the bounded choice list, and no other state changes.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

from deerflow_deep_research.domain.bundle import BundleId
from deerflow_deep_research.domain.lifecycle import (
    BundleAvailability,
    LegalNextAction,
    LogicalPhase,
)
from deerflow_deep_research.domain.run_experience import ContinueRun

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import demo_tui  # noqa: E402

DemoTui = demo_tui.DeepResearchDemoTUI

BUNDLE_ID = "b_" + "R" * 43


def _result(*, action: LegalNextAction) -> object:
    return SimpleNamespace(
        bundle_id=BundleId(BUNDLE_ID),
        legal_next_action=action,
        phase=LogicalPhase.WAVE1,
        availability=BundleAvailability.AVAILABLE,
    )


def _app_stub(bundle_id: str | None, phase: str = "wave1"):
    return SimpleNamespace(_recoverable_bundle_id=bundle_id, _recoverable_phase=phase)


def test_attach_card_lists_bundle_and_three_choices() -> None:
    app = _app_stub(BUNDLE_ID, phase="wave1")

    lines = DemoTui._attach_card_lines(app)

    assert len(lines) == 2
    assert BUNDLE_ID[:16] in lines[0]
    assert "wave1" in lines[0]
    assert "继续" in lines[1] and "查看" in lines[1] and "新跑" in lines[1]


def test_attach_card_is_empty_without_recoverable_bundle() -> None:
    app = _app_stub(None)

    assert DemoTui._attach_card_lines(app) == ()


async def test_scan_picks_only_resume_legal_bundles() -> None:
    class _Workbench:
        async def discover(self):
            return (
                _result(action=LegalNextAction.REFINE),
                _result(action=LegalNextAction.RESUME),
            )

    class _Adapter:
        def local_bundle_workbench(self):
            return _Workbench()

    app = _app_stub(None)
    app._adapter = _Adapter()

    await DemoTui._scan_recoverable_run(app)

    assert app._recoverable_bundle_id == BUNDLE_ID
    assert app._recoverable_phase == "wave1"


async def test_scan_tolerates_workbench_failures() -> None:
    class _Broken:
        def local_bundle_workbench(self):
            raise RuntimeError("no scope")

    app = _app_stub(None)
    app._adapter = _Broken()

    await DemoTui._scan_recoverable_run(app)

    assert app._recoverable_bundle_id is None


def test_continue_run_intent_carries_the_adopted_bundle_id() -> None:
    intent = ContinueRun(bundle_id=BUNDLE_ID)

    assert intent.kind == "continue"
    assert intent.bundle_id == BUNDLE_ID
