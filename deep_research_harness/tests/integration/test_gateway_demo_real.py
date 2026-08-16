"""Gateway-default real CLI contracts.

@impl DPL-004
@impl GOO-001
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from deerflow_deep_research.domain.run_experience import ReadinessCheck, ReadinessReport
from tests.fixtures import run_updates

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import demo_real  # noqa: E402, I001


def _gateway_ready_report() -> ReadinessReport:
    return ReadinessReport(
        mode="real",
        ready=True,
        summary="Selected local Gateway profile is ready.",
        checks=(ReadinessCheck(name="profile", ready=True, detail="demo"),),
        durability_note="Gateway lifecycle results remain returned-only at this entrypoint.",
    )


class _GatewayExperience:
    instances: list[_GatewayExperience] = []
    next_update: object = run_updates.completed()

    def __init__(self, *, transport: object, mode: str, readiness_provider: object, **_kwargs: object) -> None:
        self.transport = transport
        self.mode = mode
        self._readiness_provider = readiness_provider
        self.intents: list[object] = []
        type(self).instances.append(self)

    async def preflight(self) -> ReadinessReport:
        return self._readiness_provider()

    async def handle(self, intent: object, observer: object = None) -> object:
        self.intents.append(intent)
        return type(self).next_update


class _GatewayTransport:
    instances: list[_GatewayTransport] = []

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

    async def aclose(self) -> None:
        return None


def _install_gateway_path(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    profile_calls: list[str] = []
    _GatewayExperience.instances = []
    _GatewayExperience.next_update = run_updates.completed()
    _GatewayTransport.instances = []
    _GatewayClient.instances = []
    monkeypatch.setattr(
        demo_real,
        "validate_observer_profile",
        lambda _agent_root, profile: profile_calls.append(profile) or SimpleNamespace(name=profile, ready=True),
        raising=False,
    )
    monkeypatch.setattr(demo_real, "ResearchRunExperience", _GatewayExperience)
    monkeypatch.setattr(demo_real, "GatewayObserver", _GatewayTransport, raising=False)
    monkeypatch.setattr(demo_real, "HttpGatewayPublicClient", _GatewayClient, raising=False)
    return profile_calls


@pytest.mark.asyncio
async def test_default_real_cli_requires_profile_and_rejects_scripted_before_profile_or_gateway_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile_calls = _install_gateway_path(monkeypatch)

    assert await demo_real.run_demo(question="Compare storage costs.", scripted=False, profile=None) == 2
    assert await demo_real.run_demo(question="Compare storage costs.", scripted=True, profile="demo") == 2

    assert profile_calls == []
    assert _GatewayClient.instances == []
    assert _GatewayTransport.instances == []


@pytest.mark.asyncio
async def test_default_real_cli_uses_only_ready_profile_gateway_transport_without_local_provider_or_graph(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    profile_calls = _install_gateway_path(monkeypatch)
    monkeypatch.delenv("DEERFLOW_DEMO_MODEL", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    class _ForbiddenAdapter:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            raise AssertionError("default Gateway CLI must not construct DemoAdapter")

    monkeypatch.setattr(demo_real, "DemoAdapter", _ForbiddenAdapter)

    assert await demo_real.run_demo(question="Compare storage costs.", scripted=False, profile="demo") == 0

    assert profile_calls == ["demo"]
    assert len(_GatewayClient.instances) == 1
    assert len(_GatewayTransport.instances) == 1
    assert _GatewayTransport.instances[0].closed is True
    assert _GatewayExperience.instances[0].mode == "real"


@pytest.mark.asyncio
async def test_default_real_cli_does_not_report_completion_without_a_typed_lifecycle_result(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _install_gateway_path(monkeypatch)
    _GatewayExperience.next_update = run_updates.provider_fault()

    assert await demo_real.run_demo(question="Compare storage costs.", scripted=False, profile="demo") == 1
    assert "研究流程已完成" not in capsys.readouterr().out


def test_default_cli_does_not_import_the_embedded_runtime_from_its_gateway_path() -> None:
    source = (SCRIPTS / "demo_real.py").read_text(encoding="utf-8")

    assert "def _run_embedded_smoke" in source
    assert source.index("def _run_gateway_demo") < source.index("def _run_embedded_smoke")
    gateway_source = source[source.index("def _run_gateway_demo") : source.index("def _run_embedded_smoke")]
    for forbidden in ("DemoAdapter", "DemoLifecycleTransport", "build_demo_runtime", "demo_readiness_report"):
        assert forbidden not in gateway_source


def test_gateway_progress_observer_renders_only_predecessor_approved_fields(capsys: pytest.CaptureFixture[str]) -> None:
    demo_real._gateway_progress_observer(
        {
            "type": "deep_research.progress.v1",
            "phase": "wave0",
            "operation": "node",
            "outcome": "started",
            "bundle_id": "b_" + "A" * 43,
        }
    )
    demo_real._gateway_progress_observer({"type": "deep_research.progress.v1"})
    out = capsys.readouterr().out
    assert "Deep Research progress: wave0 node started" in out
    assert "b_" in out
    assert "deep_research.progress.v1" not in out.replace("Deep Research progress:", "")
    assert "wave0 node started" in out
