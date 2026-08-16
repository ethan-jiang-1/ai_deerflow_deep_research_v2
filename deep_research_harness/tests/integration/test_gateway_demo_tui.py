"""Gateway-default TUI contracts.

@impl RED-001
@impl GOO-001
@impl GOO-002
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from deerflow_deep_research.domain.run_experience import ReadinessCheck, ReadinessReport, RunSnapshot, Working
from tests.fixtures import run_updates

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import demo_tui  # noqa: E402, I001


def _gateway_report() -> ReadinessReport:
    return ReadinessReport(
        mode="real",
        ready=True,
        summary="Selected local Gateway profile is ready.",
        checks=(ReadinessCheck(name="environment", ready=True, detail="selected profile"),),
        durability_note="Gateway lifecycle results remain returned-only at this entrypoint.",
    )


async def _wait_for(app: object, pilot: object, expected: type, max_wait: float = 4.0) -> None:
    elapsed = 0.0
    while elapsed < max_wait and not isinstance(app.last_update, expected):
        await pilot.pause()
        await asyncio.sleep(0.02)
        elapsed += 0.02
    assert isinstance(app.last_update, expected)


class _GatewayExperience:
    started: asyncio.Event | None = None
    release: asyncio.Event | None = None

    def __init__(self, *, transport: object, mode: str, readiness_provider: object, **_kwargs: object) -> None:
        self.transport = transport
        self.mode = mode
        self._readiness_provider = readiness_provider

    async def preflight(self) -> ReadinessReport:
        return self._readiness_provider()

    async def handle(self, _intent: object, observer: object = None) -> object:
        if observer is not None:
            observer(Working(snapshot=RunSnapshot(), action="start", message="waiting for returned result"))
        assert type(self).started is not None
        assert type(self).release is not None
        type(self).started.set()
        await type(self).release.wait()
        return run_updates.provider_fault()


class _GatewayObserver:
    instances: list[_GatewayObserver] = []

    def __init__(self, *, client: object, transport_observer: object = None, **_kwargs: object) -> None:
        self.client = client
        self.transport_observer = transport_observer
        self.closed = False
        type(self).instances.append(self)

    async def aclose(self) -> None:
        self.closed = True


class _GatewayClient:
    instances: list[_GatewayClient] = []

    def __init__(self) -> None:
        type(self).instances.append(self)


@pytest.mark.asyncio
async def test_gateway_tui_requires_profile_before_client_or_local_graph(monkeypatch: pytest.MonkeyPatch) -> None:
    def no_client() -> object:
        pytest.fail("client must not be created")

    monkeypatch.setattr(demo_tui, "HttpGatewayPublicClient", no_client, raising=False)
    monkeypatch.setattr(demo_tui, "DemoAdapter", lambda: pytest.fail("adapter must not be created"))
    app = demo_tui.DeepResearchDemoTUI(mode="gateway", profile=None)

    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Fault)
        assert app.query_one("#composer").disabled is True
        assert app.query_one("#cancel").display is False


@pytest.mark.asyncio
async def test_gateway_tui_hides_cancel_disables_reentry_and_never_renders_fault_as_completion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _GatewayExperience.started = asyncio.Event()
    _GatewayExperience.release = asyncio.Event()
    _GatewayObserver.instances = []
    _GatewayClient.instances = []
    monkeypatch.setattr(
        demo_tui,
        "validate_observer_profile",
        lambda _agent_root, profile: SimpleNamespace(name=profile, ready=True),
        raising=False,
    )
    monkeypatch.setattr(demo_tui, "ResearchRunExperience", _GatewayExperience)
    monkeypatch.setattr(demo_tui, "GatewayObserver", _GatewayObserver, raising=False)
    monkeypatch.setattr(demo_tui, "HttpGatewayPublicClient", _GatewayClient, raising=False)
    monkeypatch.setattr(demo_tui, "DemoAdapter", lambda: pytest.fail("Gateway TUI must not construct DemoAdapter"))
    app = demo_tui.DeepResearchDemoTUI(mode="gateway", profile="demo")

    async with app.run_test() as pilot:
        await _wait_for(app, pilot, demo_tui.Ready)
        assert "Gateway" in app.query_one("#banner").render().plain
        assert app.query_one("#cancel").display is False
        await pilot.press("enter")
        await asyncio.wait_for(_GatewayExperience.started.wait(), timeout=2)
        assert isinstance(app.last_update, Working)
        assert app.query_one("#composer").disabled is True
        assert app.query_one("#cancel").display is False
        _GatewayExperience.release.set()
        await _wait_for(app, pilot, demo_tui.Fault)
        assert "Research complete" not in app.last_view.heading

    assert len(_GatewayClient.instances) == 1
    assert len(_GatewayObserver.instances) == 1


def test_gateway_tui_progress_observer_renders_only_predecessor_approved_fields() -> None:
    class _Log:
        def __init__(self) -> None:
            self.lines: list[str] = []

        def write(self, value: object) -> None:
            self.lines.append(str(value))

    app = demo_tui.DeepResearchDemoTUI(mode="fixture", profile=None)
    log = _Log()
    app.query_one = lambda *_args, **_kwargs: log  # type: ignore[assignment, method-assign]
    app._gateway_progress_observer(
        {
            "type": "deep_research.progress.v1",
            "phase": "wave0",
            "operation": "node",
            "outcome": "started",
            "bundle_id": "b_" + "A" * 43,
        }
    )
    app._gateway_progress_observer({"type": "deep_research.progress.v1"})

    assert any("Deep Research progress: wave0 node started" in line for line in log.lines)
    assert len(log.lines) == 1
