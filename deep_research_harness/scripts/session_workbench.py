#!/usr/bin/env python3
"""Standalone local terminal workbench for Run Bundle observations and controls.

This is intentionally not a Gateway, Web, upstream terminal, multi-user, or generic
recovery client. It constructs one fixed local profile, supplies no caller-selected
authority, and delegates every Bundle action to the shared lifecycle boundary.

@impl RWB-001
@impl RWB-002
@impl RWB-003
@impl RWB-005
@impl RWB-006
@impl RWB-008
@impl REC-004
"""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from _demo_core import DemoAdapter
from rich.text import Text
from textual import events, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Input, RichLog, Static

from deerflow_deep_research.domain.lifecycle import BundleAvailability, BundleControlResult, LifecycleStatus
from deerflow_deep_research.domain.session_workbench import (
    WorkbenchArtifactView,
    WorkbenchAvailability,
    WorkbenchCatalogView,
    WorkbenchDiscoveryView,
    WorkbenchSessionView,
    WorkbenchTimelineView,
)
from deerflow_deep_research.runtime.session_workbench import LocalBundleWorkbench


@dataclass(frozen=True)
class WorkbenchRenderedState:
    """Reducer-owned Textual state derived only from safe Bundle projections."""

    heading: str
    detail: str
    placeholder: str
    input_mode: Literal["select", "answer", "artifact", "disabled"]
    selected_bundle_id: str | None = None
    can_refresh: bool = False
    can_timeline: bool = False
    can_artifacts: bool = False
    can_cancel: bool = False


def _unavailable_state() -> WorkbenchRenderedState:
    return WorkbenchRenderedState(
        heading="Run Bundle unavailable",
        detail="The selected Deep Research Run Bundle is unavailable.",
        placeholder="Select an available Bundle id",
        input_mode="select",
    )


def _is_available(operation: BundleControlResult | None) -> bool:
    return operation is not None and operation.availability is BundleAvailability.AVAILABLE


def _session_controls(operation: BundleControlResult) -> dict[str, bool]:
    terminal = {
        LifecycleStatus.COMPLETED,
        LifecycleStatus.STOPPED,
        LifecycleStatus.CANCELLED,
        LifecycleStatus.BLOCKED,
    }
    available = operation.availability is BundleAvailability.AVAILABLE
    return {
        "can_refresh": available,
        "can_timeline": available,
        "can_artifacts": available,
        "can_cancel": available and operation.status not in terminal,
    }


def _pending_input_mode(operation: BundleControlResult) -> Literal["answer", "disabled"]:
    pending = operation.pending_input
    if pending is not None and pending.mode == "text":
        return "answer"
    return "disabled"


def render_discovery(view: WorkbenchDiscoveryView) -> WorkbenchRenderedState:
    """Render only lifecycle-projected Bundle facts."""

    if not view.entries:
        return WorkbenchRenderedState(
            heading="Local Run Bundle workbench",
            detail="No active Run Bundle is available from the configured local profile.",
            placeholder="Bundle id",
            input_mode="select",
        )
    lines = ["Active Run Bundles:"]
    for entry in view.entries:
        if entry.availability is not BundleAvailability.AVAILABLE or entry.bundle_id is None:
            continue
        detail = entry.bundle_id
        if entry.status is not None:
            detail += f"  {entry.status.value}"
        if entry.phase is not None:
            detail += f"  {entry.phase.value}"
        lines.append(detail)
    return WorkbenchRenderedState(
        heading="Select a Run Bundle",
        detail="\n".join(lines),
        placeholder="Bundle id",
        input_mode="select",
    )


def render_session(view: WorkbenchSessionView) -> WorkbenchRenderedState:
    """Render a selected Bundle without deriving control from retained observations."""

    operation = view.operation
    if not _is_available(operation) or operation is None or operation.bundle_id is None:
        return _unavailable_state()
    lines: list[str] = []
    if operation.status is not None:
        lines.append(f"Status: {operation.status.value}")
    if operation.phase is not None:
        lines.append(f"Phase: {operation.phase.value}")
    lines.append(f"Durability: {operation.durability.value}")
    lines.append(f"Legal next action: {operation.legal_next_action.value}")
    if view.timeline.availability is WorkbenchAvailability.UNAVAILABLE:
        lines.append("Timeline unavailable.")
    if view.catalog.availability is WorkbenchAvailability.UNAVAILABLE:
        lines.append("Artifact catalog unavailable.")
    if operation.pending_input is not None:
        pending = operation.pending_input
        lines.append(f"Pending request: {pending.request_id}")
        lines.append(f"Pending phase: {pending.pending_phase}")
        return WorkbenchRenderedState(
            heading="Pending local input",
            detail="\n".join(lines),
            placeholder="Type the correlated response" if pending.mode == "text" else "",
            input_mode=_pending_input_mode(operation),
            selected_bundle_id=operation.bundle_id,
            **_session_controls(operation),
        )
    return WorkbenchRenderedState(
        heading="Run Bundle",
        detail="\n".join(lines) if lines else "Current Bundle state is available.",
        placeholder="",
        input_mode="disabled",
        selected_bundle_id=operation.bundle_id,
        **_session_controls(operation),
    )


def render_timeline(view: WorkbenchTimelineView, operation: BundleControlResult | None) -> WorkbenchRenderedState:
    if not _is_available(operation) or operation is None or operation.bundle_id is None:
        return _unavailable_state()
    if view.availability is WorkbenchAvailability.UNAVAILABLE:
        return WorkbenchRenderedState(
            heading="Timeline unavailable",
            detail="The bounded timeline observation is unavailable for this Run Bundle.",
            placeholder="Type the correlated response" if _pending_input_mode(operation) == "answer" else "",
            input_mode=_pending_input_mode(operation),
            selected_bundle_id=operation.bundle_id,
            **_session_controls(operation),
        )
    lines = [
        f"#{entry.sequence} {entry.action} {entry.status} {entry.phase} generation {entry.generation}"
        for entry in view.entries
    ]
    return WorkbenchRenderedState(
        heading="Run Bundle timeline",
        detail="\n".join(lines) if lines else "No bounded lifecycle observations are available.",
        placeholder="Type the correlated response" if _pending_input_mode(operation) == "answer" else "",
        input_mode=_pending_input_mode(operation),
        selected_bundle_id=operation.bundle_id,
        **_session_controls(operation),
    )


def render_catalog(view: WorkbenchCatalogView, operation: BundleControlResult | None) -> WorkbenchRenderedState:
    if not _is_available(operation) or operation is None or operation.bundle_id is None:
        return _unavailable_state()
    if view.availability is WorkbenchAvailability.UNAVAILABLE:
        return WorkbenchRenderedState(
            heading="Artifact catalog unavailable",
            detail="The fixed Bundle artifact catalog is unavailable.",
            placeholder="",
            input_mode="disabled",
            selected_bundle_id=operation.bundle_id,
            **_session_controls(operation),
        )
    lines = [f"{entry.key.value}  {entry.relative_path}  metadata only" for entry in view.entries]
    return WorkbenchRenderedState(
        heading="Fixed artifact catalog",
        detail="\n".join(lines) if lines else "No fixed artifacts are available.",
        placeholder="Artifact key",
        input_mode="artifact",
        selected_bundle_id=operation.bundle_id,
        **_session_controls(operation),
    )


def render_artifact(view: WorkbenchArtifactView, operation: BundleControlResult | None) -> WorkbenchRenderedState:
    if not _is_available(operation) or operation is None or operation.bundle_id is None:
        return _unavailable_state()
    if view.availability is WorkbenchAvailability.UNAVAILABLE or view.metadata is None:
        return WorkbenchRenderedState(
            heading="Artifact unavailable",
            detail="The selected fixed artifact is unavailable.",
            placeholder="Artifact key",
            input_mode="artifact",
            selected_bundle_id=operation.bundle_id,
            **_session_controls(operation),
        )
    metadata = view.metadata
    return WorkbenchRenderedState(
        heading="Artifact metadata",
        detail=(
            f"Key: {metadata.key.value}\n"
            f"Reference: {metadata.relative_path}\n"
            f"Type: {metadata.media_type}\n"
            f"Bytes: {metadata.byte_size}\n"
            "Presentation: metadata only"
        ),
        placeholder="Artifact key",
        input_mode="artifact",
        selected_bundle_id=operation.bundle_id,
        **_session_controls(operation),
    )


def _retained_root() -> Path:
    return Path(__file__).resolve().parents[1] / ".deep-research-demo-runs"


async def build_local_workbench() -> tuple[LocalBundleWorkbench, DemoAdapter]:
    """Construct the fixed local profile without a session/binding controller."""

    adapter = DemoAdapter(retained_root=_retained_root(), operation_enabled=True)
    try:
        await adapter.open()
        return LocalBundleWorkbench(bundle_workbench=adapter.local_bundle_workbench()), adapter
    except BaseException:
        await adapter.aclose()
        raise


class LocalBundleWorkbenchTUI(App[None]):
    """Thin Textual reducer over ``LocalBundleWorkbench`` Bundle projections."""

    CSS = """
    Screen { layout: vertical; background: #10141a; color: #e6edf3; }
    #banner { height: 3; padding: 1 2; background: #0f4c5c; color: #ecfeff; text-style: bold; }
    #heading { height: auto; margin: 1 2 0 2; color: #f9d976; text-style: bold; }
    #log { height: 1fr; border: round #536471; margin: 0 2; padding: 0 1; }
    #controls { height: 3; margin: 0 2; }
    #actions { height: 3; margin: 0 2 1 2; }
    #composer { width: 1fr; }
    #discover, #refresh, #timeline, #artifacts, #cancel { margin-left: 1; }
    """

    BINDINGS = [("ctrl+c", "quit", "Quit")]
    _WORKER_GROUP = "local-session-workbench"

    def __init__(self, *, workbench: LocalBundleWorkbench | Any | None = None) -> None:
        super().__init__()
        self._workbench = workbench
        self._adapter: DemoAdapter | None = None
        self.selected_bundle_id: str | None = None
        self.selected_operation: BundleControlResult | None = None
        self.last_session: WorkbenchSessionView | None = None
        self.last_rendered = WorkbenchRenderedState(
            heading="Checking local profile",
            detail="Preparing the configured local Run Bundle profile.",
            placeholder="",
            input_mode="disabled",
        )
        self.input_mode: Literal["select", "answer", "artifact", "disabled"] = "disabled"

    def compose(self) -> ComposeResult:
        yield Static(id="banner")
        yield Static(id="heading")
        yield RichLog(id="log", wrap=True, markup=False, max_lines=100)
        with Horizontal(id="controls"):
            yield Input(placeholder="Bundle id", id="composer")
            yield Button("Discover", id="discover")
            yield Button("Refresh", id="refresh")
            yield Button("Timeline", id="timeline")
            yield Button("Artifacts", id="artifacts")
        with Horizontal(id="actions"):
            yield Button("Cancel", id="cancel", variant="error")

    def on_mount(self) -> None:
        self.query_one("#banner", Static).update(Text("Deep Research local Run Bundle workbench", style="bold cyan"))
        self._render(self.last_rendered)
        if self._workbench is None:
            self._initialize()
        else:
            self._discover()

    def on_unmount(self) -> None:
        if self._adapter is not None:
            self._adapter.close()
            self._adapter = None

    def _render(self, rendered: WorkbenchRenderedState) -> None:
        self.last_rendered = rendered
        self.input_mode = rendered.input_mode
        composer = self.query_one("#composer", Input)
        composer.disabled = rendered.input_mode == "disabled"
        composer.placeholder = rendered.placeholder
        self.query_one("#heading", Static).update(Text(rendered.heading, style="bold yellow"))
        log = self.query_one("#log", RichLog)
        log.clear()
        if rendered.detail:
            log.write(Text(rendered.detail))
        for widget_id, enabled in (
            ("#refresh", rendered.can_refresh),
            ("#timeline", rendered.can_timeline),
            ("#artifacts", rendered.can_artifacts),
            ("#cancel", rendered.can_cancel),
        ):
            button = self.query_one(widget_id, Button)
            button.disabled = not enabled
            button.display = enabled
        self.query_one("#discover", Button).disabled = self._workbench is None
        if rendered.input_mode != "disabled":
            composer.focus()

    @work(group=_WORKER_GROUP, exclusive=True, exit_on_error=False)
    async def _initialize(self) -> None:
        try:
            workbench, adapter = await build_local_workbench()
            self._workbench = workbench
            self._adapter = adapter
            await self._discover_impl()
        except asyncio.CancelledError:
            raise
        except (OSError, RuntimeError, TypeError, ValueError):
            self._render(_unavailable_state())

    @work(group=_WORKER_GROUP, exclusive=True, exit_on_error=False)
    async def _discover(self) -> None:
        await self._discover_impl()

    async def _discover_impl(self) -> None:
        workbench = self._workbench
        if workbench is None:
            self._render(_unavailable_state())
            return
        try:
            view = await workbench.discover()
            if not isinstance(view, WorkbenchDiscoveryView):
                raise ValueError("workbench_discovery_invalid")
            self.selected_bundle_id = None
            self.selected_operation = None
            self.last_session = None
            self._render(render_discovery(view))
        except asyncio.CancelledError:
            raise
        except (OSError, RuntimeError, TypeError, ValueError):
            self._render(_unavailable_state())

    @work(group=_WORKER_GROUP, exclusive=True, exit_on_error=False)
    async def _open(self, bundle_id: str) -> None:
        workbench = self._workbench
        if workbench is None:
            self._render(_unavailable_state())
            return
        try:
            view = await workbench.open(bundle_id)
            if not isinstance(view, WorkbenchSessionView):
                raise ValueError("workbench_open_invalid")
            self._apply_session(view)
        except asyncio.CancelledError:
            raise
        except (OSError, RuntimeError, TypeError, ValueError):
            self._render(_unavailable_state())

    @work(group=_WORKER_GROUP, exclusive=True, exit_on_error=False)
    async def _refresh(self) -> None:
        workbench = self._workbench
        bundle_id = self.selected_bundle_id
        if workbench is None or bundle_id is None:
            self._render(_unavailable_state())
            return
        try:
            view = await workbench.status(bundle_id)
            if not isinstance(view, WorkbenchSessionView):
                raise ValueError("workbench_status_invalid")
            self._apply_session(view)
        except asyncio.CancelledError:
            raise
        except (OSError, RuntimeError, TypeError, ValueError):
            self._render(_unavailable_state())

    @work(group=_WORKER_GROUP, exclusive=True, exit_on_error=False)
    async def _timeline(self) -> None:
        workbench = self._workbench
        bundle_id = self.selected_bundle_id
        if workbench is None or bundle_id is None:
            self._render(_unavailable_state())
            return
        try:
            view = await workbench.timeline(bundle_id)
            if not isinstance(view, WorkbenchTimelineView):
                raise ValueError("workbench_timeline_invalid")
            self._render(render_timeline(view, self.selected_operation))
        except asyncio.CancelledError:
            raise
        except (OSError, RuntimeError, TypeError, ValueError):
            self._render(_unavailable_state())

    @work(group=_WORKER_GROUP, exclusive=True, exit_on_error=False)
    async def _catalog(self) -> None:
        workbench = self._workbench
        bundle_id = self.selected_bundle_id
        if workbench is None or bundle_id is None:
            self._render(_unavailable_state())
            return
        try:
            view = await workbench.catalog(bundle_id)
            if not isinstance(view, WorkbenchCatalogView):
                raise ValueError("workbench_catalog_invalid")
            self._render(render_catalog(view, self.selected_operation))
        except asyncio.CancelledError:
            raise
        except (OSError, RuntimeError, TypeError, ValueError):
            self._render(_unavailable_state())

    @work(group=_WORKER_GROUP, exclusive=True, exit_on_error=False)
    async def _artifact(self, key: str) -> None:
        workbench = self._workbench
        bundle_id = self.selected_bundle_id
        if workbench is None or bundle_id is None:
            self._render(_unavailable_state())
            return
        try:
            view = await workbench.view_artifact(bundle_id, key)
            if not isinstance(view, WorkbenchArtifactView):
                raise ValueError("workbench_artifact_invalid")
            self._render(render_artifact(view, self.selected_operation))
        except asyncio.CancelledError:
            raise
        except (OSError, RuntimeError, TypeError, ValueError):
            self._render(_unavailable_state())

    @work(group=_WORKER_GROUP, exclusive=True, exit_on_error=False)
    async def _resume(self, answer: str) -> None:
        workbench = self._workbench
        operation = self.selected_operation
        if workbench is None or operation is None or operation.bundle_id is None or operation.pending_input is None:
            self._render(_unavailable_state())
            return
        try:
            result = await workbench.resume(
                operation.bundle_id,
                expected_request_id=operation.pending_input.request_id,
                answer=answer,
            )
            if not isinstance(result, BundleControlResult):
                raise ValueError("workbench_resume_invalid")
            self._apply_operation(result)
        except asyncio.CancelledError:
            raise
        except (OSError, RuntimeError, TypeError, ValueError):
            self._render(_unavailable_state())

    @work(group=_WORKER_GROUP, exclusive=True, exit_on_error=False)
    async def _cancel(self) -> None:
        workbench = self._workbench
        operation = self.selected_operation
        if workbench is None or operation is None or operation.bundle_id is None:
            self._render(_unavailable_state())
            return
        try:
            result = await workbench.cancel(operation.bundle_id)
            if not isinstance(result, BundleControlResult):
                raise ValueError("workbench_cancel_invalid")
            self._apply_operation(result)
        except asyncio.CancelledError:
            raise
        except (OSError, RuntimeError, TypeError, ValueError):
            self._render(_unavailable_state())

    def _apply_session(self, view: WorkbenchSessionView) -> None:
        self.last_session = view
        operation = view.operation
        if not _is_available(operation) or operation is None or operation.bundle_id is None:
            self.selected_bundle_id = None
            self.selected_operation = None
        else:
            self.selected_bundle_id = operation.bundle_id
            self.selected_operation = operation
        self._render(render_session(view))

    def _apply_operation(self, operation: BundleControlResult) -> None:
        if not _is_available(operation) or operation.bundle_id is None:
            self.selected_bundle_id = None
            self.selected_operation = None
            self.last_session = None
            self._render(_unavailable_state())
            return
        self.selected_bundle_id = operation.bundle_id
        self.selected_operation = operation
        self.last_session = None
        self._render(
            render_session(
                WorkbenchSessionView(
                    operation=operation,
                    timeline=WorkbenchTimelineView(availability=WorkbenchAvailability.UNAVAILABLE),
                    catalog=WorkbenchCatalogView(availability=WorkbenchAvailability.UNAVAILABLE),
                )
            )
        )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        raw_value = event.value
        value = raw_value.strip()
        if not value:
            return
        event.input.value = ""
        if self.input_mode == "select":
            self._open(value)
        elif self.input_mode == "answer":
            self._resume(raw_value)
        elif self.input_mode == "artifact":
            self._artifact(value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "discover":
            self._discover()
        elif event.button.id == "refresh":
            self._refresh()
        elif event.button.id == "timeline":
            self._timeline()
        elif event.button.id == "artifacts":
            self._catalog()
        elif event.button.id == "cancel":
            self._cancel()

    def on_key(self, event: events.Key) -> None:
        """Prevent a disabled response surface from falling through to a button."""

        if event.key == "enter" and self.input_mode == "disabled":
            event.stop()
            event.prevent_default()


def _build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="Open the standalone local Deep Research Run Bundle workbench.",
        epilog="This local operator surface is not Gateway, Web, upstream terminal, or generic recovery.",
    )


def main() -> None:
    _build_parser().parse_args()
    app = LocalBundleWorkbenchTUI()
    try:
        app.run()
    finally:
        if app._adapter is not None:
            app._adapter.close()


if __name__ == "__main__":
    main()
