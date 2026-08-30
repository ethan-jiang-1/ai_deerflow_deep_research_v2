"""Standalone local workbench integration over shared Bundle results.

@impl RWB-001
@impl RWB-002
@impl RWB-003
@impl RWB-005
@impl RWB-006
@impl RWB-008
@impl RSV-001
@impl RSV-002
@impl RSV-003
@impl RSV-004
"""

from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from deerflow_deep_research.domain.lifecycle import (
    BundleAvailability,
    BundleControlResult,
    BundleRefinementProjection,
    Durability,
    LegalNextAction,
    LifecycleAction,
    LifecycleStatus,
    LogicalPhase,
    ResultCode,
)
from deerflow_deep_research.domain.run_experience import PendingInputProjection
from deerflow_deep_research.domain.run_observation import JournalIncompleteReason
from deerflow_deep_research.domain.session_workbench import (
    ArtifactCatalogKey,
    WorkbenchArtifactMetadata,
    WorkbenchArtifactView,
    WorkbenchAvailability,
    WorkbenchCatalogView,
    WorkbenchDiagnosisView,
    WorkbenchDiscoveryView,
    WorkbenchSessionView,
    WorkbenchTimelineEntry,
    WorkbenchTimelineView,
)

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import session_workbench  # noqa: E402, I001
from session_workbench import LocalBundleWorkbenchTUI  # noqa: E402

BUNDLE_ID = "b_" + "A" * 43
ANSWER_SENTINEL = "secret=answer-sentinel /Users/alice/private postgres://credential"


@pytest.mark.asyncio
async def test_workbench_does_not_recover_an_unavailable_bundle_from_its_local_selection() -> None:
    from deerflow_deep_research.runtime.session_workbench import BundleWorkbench

    workbench = BundleWorkbench()
    result = await workbench.status(bundle_id=BUNDLE_ID)

    assert result.availability == "unavailable"
    assert result.bundle_id is None


def _operation(
    *,
    action: LifecycleAction = LifecycleAction.STATUS,
    pending: bool = True,
    unavailable: bool = False,
    status: LifecycleStatus | None = None,
) -> BundleControlResult:
    if unavailable:
        return BundleControlResult(
            action=action,
            code=ResultCode.UNAVAILABLE,
            availability=BundleAvailability.UNAVAILABLE,
            durability=Durability.UNAVAILABLE,
            legal_next_action=LegalNextAction.START,
        )
    resolved_status = status or (LifecycleStatus.SUSPENDED if pending else LifecycleStatus.COMPLETED)
    return BundleControlResult(
        action=action,
        code=ResultCode.SUSPENDED if pending else ResultCode(resolved_status.value),
        availability=BundleAvailability.AVAILABLE,
        durability=Durability.RESTART_DURABLE,
        bundle_id=BUNDLE_ID,
        status=resolved_status,
        phase=LogicalPhase.HITL1,
        generation=0,
        request_id="drh_pending" if pending else None,
        pending_input=(
            PendingInputProjection(
                request_id="drh_pending",
                pending_phase="hitl1",
                generation=0,
                mode="text",
            )
            if pending
            else None
        ),
        refinement=BundleRefinementProjection(disposition="none"),
        legal_next_action=LegalNextAction.RESUME if pending else LegalNextAction.REFINE,
    )


def _session(operation: BundleControlResult) -> WorkbenchSessionView:
    if operation.availability is BundleAvailability.UNAVAILABLE:
        return WorkbenchSessionView(
            operation=operation,
            timeline=WorkbenchTimelineView(availability=WorkbenchAvailability.UNAVAILABLE),
            catalog=WorkbenchCatalogView(availability=WorkbenchAvailability.UNAVAILABLE),
        )
    return WorkbenchSessionView(
        operation=operation,
        timeline=WorkbenchTimelineView(
            availability=WorkbenchAvailability.AVAILABLE,
            entries=(
                WorkbenchTimelineEntry(
                    sequence=1,
                    timestamp=datetime(2026, 7, 22, tzinfo=UTC),
                    action="start",
                    status="suspended",
                    phase="bootstrap",
                    generation=0,
                    pending_phase="hitl1",
                    pending_mode="text",
                    pending_request_id="drh_pending",
                ),
            ),
        ),
        catalog=WorkbenchCatalogView(
            availability=WorkbenchAvailability.AVAILABLE,
            entries=(
                WorkbenchArtifactMetadata(
                    key=ArtifactCatalogKey.REQUEST_PROFILE,
                    relative_path="request/profile.json",
                    media_type="application/json",
                    byte_size=22,
                ),
            ),
        ),
    )


class _Workbench:
    def __init__(self, *, unavailable: bool = False, stale_resume: bool = False) -> None:
        self.unavailable = unavailable
        self.stale_resume = stale_resume
        self.current = _operation(unavailable=unavailable)
        self.calls: list[tuple[str, object, object | None]] = []

    async def discover(self) -> WorkbenchDiscoveryView:
        self.calls.append(("discover", None, None))
        return WorkbenchDiscoveryView(entries=() if self.unavailable else (self.current,))

    async def open(self, bundle_id: str) -> WorkbenchSessionView:
        self.calls.append(("open", bundle_id, None))
        return _session(self.current)

    async def status(self, bundle_id: str) -> WorkbenchSessionView:
        self.calls.append(("status", bundle_id, None))
        return _session(self.current)

    async def timeline(self, bundle_id: str) -> WorkbenchTimelineView:
        self.calls.append(("timeline", bundle_id, None))
        return _session(self.current).timeline

    async def catalog(self, bundle_id: str) -> WorkbenchCatalogView:
        self.calls.append(("catalog", bundle_id, None))
        return _session(self.current).catalog

    async def view_artifact(self, bundle_id: str, key: ArtifactCatalogKey | str) -> WorkbenchArtifactView:
        self.calls.append(("artifact", bundle_id, key))
        if self.unavailable or key != ArtifactCatalogKey.REQUEST_PROFILE.value:
            return WorkbenchArtifactView(availability=WorkbenchAvailability.UNAVAILABLE)
        return WorkbenchArtifactView(
            availability=WorkbenchAvailability.AVAILABLE,
            metadata=_session(self.current).catalog.entries[0],
        )

    async def resume(
        self,
        bundle_id: str,
        *,
        expected_request_id: str,
        answer: str,
    ) -> BundleControlResult:
        self.calls.append(("resume", (bundle_id, expected_request_id), answer))
        self.current = _operation(
            action=LifecycleAction.RESUME,
            pending=False,
            unavailable=self.stale_resume,
        )
        return self.current

    async def cancel(self, bundle_id: str) -> BundleControlResult:
        self.calls.append(("cancel", bundle_id, None))
        self.current = _operation(
            action=LifecycleAction.CANCEL,
            pending=False,
            status=LifecycleStatus.CANCELLED,
        )
        return self.current


async def _wait_for(app: LocalBundleWorkbenchTUI, pilot, predicate, max_wait: float = 4.0) -> None:
    elapsed = 0.0
    while elapsed < max_wait and not predicate():
        await pilot.pause()
        await asyncio.sleep(0.02)
        elapsed += 0.02
    assert predicate()


@pytest.mark.asyncio
async def test_workbench_discovers_selects_and_navigates_safe_timeline_and_metadata() -> None:
    workbench = _Workbench()
    app = LocalBundleWorkbenchTUI(workbench=workbench)
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, lambda: workbench.calls == [("discover", None, None)])
        composer = app.query_one("#composer")
        composer.value = BUNDLE_ID
        await pilot.press("enter")
        await _wait_for(app, pilot, lambda: len(workbench.calls) == 2)
        assert app.selected_bundle_id == BUNDLE_ID
        assert app.selected_operation == _operation()

        await pilot.click("#timeline")
        await _wait_for(app, pilot, lambda: len(workbench.calls) == 3)
        assert "#1" in app.last_rendered.detail

        await pilot.click("#artifacts")
        await _wait_for(app, pilot, lambda: len(workbench.calls) == 4)
        assert app.input_mode == "artifact"
        composer.value = ArtifactCatalogKey.REQUEST_PROFILE.value
        await pilot.press("enter")
        await _wait_for(app, pilot, lambda: len(workbench.calls) == 5)
        output = app.last_rendered.detail
        assert "request/profile.json" in output
        assert "metadata only" in output
        assert "secret" not in output

    assert [call[0] for call in workbench.calls] == ["discover", "open", "timeline", "catalog", "artifact"]


@pytest.mark.asyncio
async def test_workbench_delegates_a_correlated_answer_without_echoing_or_duplication() -> None:
    workbench = _Workbench()
    app = LocalBundleWorkbenchTUI(workbench=workbench)
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, lambda: len(workbench.calls) == 1)
        composer = app.query_one("#composer")
        composer.value = BUNDLE_ID
        await pilot.press("enter")
        await _wait_for(app, pilot, lambda: len(workbench.calls) == 2)

        composer.value = ANSWER_SENTINEL
        await pilot.press("enter")
        await _wait_for(app, pilot, lambda: len(workbench.calls) == 3)
        assert app.input_mode == "disabled"
        assert ANSWER_SENTINEL not in app.last_rendered.detail
        await pilot.press("enter")
        await pilot.pause()
        assert len(workbench.calls) == 3

    assert workbench.calls[2] == ("resume", (BUNDLE_ID, "drh_pending"), ANSWER_SENTINEL)


@pytest.mark.asyncio
async def test_workbench_delegates_cancel_as_a_bundle_action() -> None:
    workbench = _Workbench()
    app = LocalBundleWorkbenchTUI(workbench=workbench)
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, lambda: len(workbench.calls) == 1)
        composer = app.query_one("#composer")
        composer.value = BUNDLE_ID
        await pilot.press("enter")
        await _wait_for(app, pilot, lambda: len(workbench.calls) == 2)
        await pilot.click("#cancel")
        await _wait_for(app, pilot, lambda: len(workbench.calls) == 3)

    assert workbench.calls[2] == ("cancel", BUNDLE_ID, None)
    assert app.last_rendered.detail.startswith("Status: cancelled")


@pytest.mark.asyncio
async def test_workbench_renders_unavailable_stale_answer_without_recovery_claim() -> None:
    stale = _Workbench(stale_resume=True)
    app = LocalBundleWorkbenchTUI(workbench=stale)
    async with app.run_test() as pilot:
        await _wait_for(app, pilot, lambda: len(stale.calls) == 1)
        composer = app.query_one("#composer")
        composer.value = BUNDLE_ID
        await pilot.press("enter")
        await _wait_for(app, pilot, lambda: len(stale.calls) == 2)
        composer.value = ANSWER_SENTINEL
        await pilot.press("enter")
        await _wait_for(app, pilot, lambda: len(stale.calls) == 3)
        assert app.last_rendered.heading == "Run Bundle unavailable"
        assert BUNDLE_ID not in app.last_rendered.detail
        assert ANSWER_SENTINEL not in app.last_rendered.detail
        assert "resume" not in app.last_rendered.detail.lower()


def test_workbench_parser_accepts_no_caller_selected_profile_or_path_authority() -> None:
    parser = session_workbench._build_parser()
    assert vars(parser.parse_args([])) == {}
    for forbidden in ("--profile", "--path", "--provider", "--session-ref", "--bundle-root"):
        with pytest.raises(SystemExit):
            parser.parse_args([forbidden, "secret=sentinel"])


@pytest.mark.asyncio
async def test_fixed_workbench_profile_exposes_only_a_bundle_workbench(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}
    bundle_workbench = object()

    class FixedProfileAdapter:
        def __init__(self, *, bundle_root: Path) -> None:
            captured["bundle_root"] = bundle_root

        async def open(self) -> None:
            captured["opened"] = True

        async def aclose(self) -> None:
            captured["closed"] = True

        def local_bundle_workbench(self) -> object:
            captured["bundle_workbench_requested"] = True
            return bundle_workbench

    monkeypatch.setattr(session_workbench, "_bundle_root", lambda: tmp_path)
    monkeypatch.setattr(session_workbench, "DemoAdapter", FixedProfileAdapter)

    workbench, adapter = await session_workbench.build_local_workbench()

    assert workbench is not None
    assert captured["bundle_root"] == tmp_path
    assert captured["opened"] is True
    assert captured["bundle_workbench_requested"] is True
    assert workbench._bundle_workbench is bundle_workbench
    await adapter.aclose()


def test_rendered_workbench_state_is_pure_and_does_not_include_sensitive_authority_fields() -> None:
    rendered = session_workbench.render_session(_session(_operation()))

    assert rendered.input_mode == "answer"
    assert rendered.selected_bundle_id == BUNDLE_ID
    assert "provider" not in rendered.detail.lower()
    assert "checkpoint" not in rendered.detail.lower()
    assert ANSWER_SENTINEL not in rendered.detail


def test_workbench_journal_projection_renders_only_safe_incomplete_reasons() -> None:
    rendered = session_workbench.render_diagnosis(
        WorkbenchDiagnosisView(
            availability=WorkbenchAvailability.AVAILABLE,
            incomplete_reasons=(
                JournalIncompleteReason.LEGACY,
                JournalIncompleteReason.CAPACITY,
                JournalIncompleteReason.PERSISTENCE,
            ),
        ),
        _operation(),
    )

    assert "Incomplete because: legacy, capacity, persistence" in rendered.detail
    assert "manifest" not in rendered.detail.lower()
    assert "journal-manifest.json" not in rendered.detail


@pytest.mark.asyncio
async def test_diagnosis_is_available_for_a_suspended_bundle_with_complete_journal(tmp_path) -> None:
    """@impl RWB-009
    @bug BUG-064

    A suspended bundle whose journal is present and consistent yields an
    available read-only diagnosis regardless of its non-terminal status: an
    operator can inspect what a recoverable run was doing before resuming or
    discarding it.
    """
    from _demo_core import DemoAdapter

    from deerflow_deep_research.runtime.run_observation import RunObservationStore

    adapter = DemoAdapter(bundle_root=tmp_path)
    try:
        await adapter.open()
        workbench = adapter.local_bundle_workbench()
        lifecycle = adapter._bundle_lifecycle
        bundle = await lifecycle.start(
            scope=workbench._scope,
            request_text="Recover a stalled research run.",
            implementation_mode="all_real",
        )
        await lifecycle.sync_graph_progress(
            bundle=bundle,
            values={
                "phase": "wave1",
                "phase_status": "in_progress",
                "generation": 0,
                "execution_trace": ("bootstrap", "hitl1", "topic_planning", "wave0", "wave1"),
            },
            pending=None,
        )
        store = RunObservationStore(
            bundle_root=lifecycle.private_root(bundle),
            bundle_id=bundle.bundle_id.value,
        )
        await store._establish(generation=0, phase="bootstrap", durability="restart_durable")
        diagnosis = await workbench.diagnosis(bundle_id=bundle.bundle_id.value)
    finally:
        await adapter.aclose()

    assert diagnosis.availability is WorkbenchAvailability.AVAILABLE
    assert diagnosis.summary is not None
