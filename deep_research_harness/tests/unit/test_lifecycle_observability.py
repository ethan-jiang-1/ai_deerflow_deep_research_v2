"""Trusted lifecycle logging ownership contract.

@impl RTO-001
@impl RTO-003
@impl RUI-002
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from deerflow_deep_research.domain.lifecycle import ImplementationMode, LifecycleAction
from deerflow_deep_research.runtime import bundle_control, bundle_lifecycle, events
from deerflow_deep_research.runtime.bundle_control import BundleControl
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope
from deerflow_deep_research.runtime.session_workbench import BundleWorkbench


@pytest.mark.asyncio
async def test_lifecycle_logs_start_and_only_the_effective_cancel(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observations: list[events.SafeObservation] = []

    def record(observation: events.SafeObservation, **_kwargs: object) -> None:
        observations.append(observation)

    monkeypatch.setattr(bundle_lifecycle, "project_observation", record)
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)

    bundle = await lifecycle.start(
        scope=("alice", "thread-1"),
        request_text="research question",
        implementation_mode=ImplementationMode.ALL_REAL,
    )
    await lifecycle.cancel(scope=("alice", "thread-1"), bundle_id=bundle.bundle_id)
    await lifecycle.cancel(scope=("alice", "thread-1"), bundle_id=bundle.bundle_id)

    assert observations == [
        events.SafeObservation(
            phase="lifecycle",
            operation="start",
            outcome=events.ObservationOutcome.STARTED,
            bundle_id=bundle.bundle_id.value,
        ),
        events.SafeObservation(
            phase="lifecycle",
            operation="cancel",
            outcome=events.ObservationOutcome.CANCELLED,
            bundle_id=bundle.bundle_id.value,
        ),
    ]
    assert all(item.outer_thread_id is None and item.outer_run_id is None for item in observations)


@pytest.mark.asyncio
async def test_lifecycle_logs_trusted_outer_correlation_without_accepting_an_invalid_value(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observations: list[events.SafeObservation] = []

    def record(observation: events.SafeObservation, **_kwargs: object) -> None:
        observations.append(observation)

    monkeypatch.setattr(bundle_lifecycle, "project_observation", record)
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)

    bundle = await lifecycle.start(
        scope=("alice", "thread-1"),
        request_text="research question",
        implementation_mode=ImplementationMode.ALL_REAL,
        log_outer_thread_id="thread-1",
        log_outer_run_id="run-1",
    )
    await lifecycle.cancel(
        scope=("alice", "thread-1"),
        bundle_id=bundle.bundle_id,
        log_outer_thread_id="unsafe/path",
        log_outer_run_id="run-1",
    )

    assert observations == [
        events.SafeObservation(
            phase="lifecycle",
            operation="start",
            outcome=events.ObservationOutcome.STARTED,
            bundle_id=bundle.bundle_id.value,
            outer_thread_id="thread-1",
            outer_run_id="run-1",
        ),
        events.SafeObservation(
            phase="lifecycle",
            operation="cancel",
            outcome=events.ObservationOutcome.CANCELLED,
            bundle_id=bundle.bundle_id.value,
        ),
    ]


def test_bundle_control_accepts_outer_correlation_only_from_the_trusted_envelope() -> None:
    envelope = TrustedRuntimeEnvelope(
        effective_user_id="alice",
        outer_thread_id="thread-1",
        outer_run_id="run-1",
        app_config=object(),
        workspace_host_path=Path("/tmp/workspace"),
        uploads_host_path=Path("/tmp/uploads"),
        outputs_host_path=Path("/tmp/outputs"),
        workspace_virtual_root="/mnt/user-data/workspace",
        uploads_virtual_root="/mnt/user-data/uploads",
        outputs_virtual_root="/mnt/user-data/outputs",
        parent_sandbox=None,
    )

    assert BundleControl._trusted_log_correlation(envelope, scope=("alice", "thread-1")) == (
        "thread-1",
        "run-1",
    )
    assert BundleControl._trusted_log_correlation(
        SimpleNamespace(**envelope.__dict__), scope=("alice", "thread-1")
    ) == (
        None,
        None,
    )
    assert BundleControl._trusted_log_correlation(envelope, scope=("alice", "other-thread")) == (None, None)


@pytest.mark.asyncio
async def test_lifecycle_is_the_single_log_owner_for_gateway_and_workbench_callers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gateway_lifecycle = BundleLifecycle(workspace_host_path=tmp_path / "gateway")
    gateway_bundle = await gateway_lifecycle.start(
        scope=("alice", "thread-1"),
        request_text="gateway research question",
        implementation_mode=ImplementationMode.ALL_REAL,
    )
    workbench_lifecycle = BundleLifecycle(workspace_host_path=tmp_path / "workbench")
    workbench_bundle = await workbench_lifecycle.start(
        scope=("alice", "thread-1"),
        request_text="workbench research question",
        implementation_mode=ImplementationMode.ALL_REAL,
    )
    observations: list[events.SafeObservation] = []

    def record(observation: events.SafeObservation, **_kwargs: object) -> None:
        observations.append(observation)

    monkeypatch.setattr(bundle_lifecycle, "project_observation", record)
    envelope = TrustedRuntimeEnvelope(
        effective_user_id="alice",
        outer_thread_id="thread-1",
        outer_run_id="run-1",
        app_config=object(),
        workspace_host_path=tmp_path / "workspace",
        uploads_host_path=tmp_path / "uploads",
        outputs_host_path=tmp_path / "outputs",
        workspace_virtual_root="/mnt/user-data/workspace",
        uploads_virtual_root="/mnt/user-data/uploads",
        outputs_virtual_root="/mnt/user-data/outputs",
        parent_sandbox=None,
    )

    gateway_result = await BundleControl(lifecycle=gateway_lifecycle).dispatch(
        action=LifecycleAction.CANCEL,
        effective_user_id="alice",
        outer_thread_id="thread-1",
        messages=(),
        tool_call_id="gateway-cancel",
        bundle_id=gateway_bundle.bundle_id.value,
        envelope=envelope,
    )
    workbench_result = await BundleWorkbench(
        lifecycle=workbench_lifecycle,
        scope=("alice", "thread-1"),
    ).cancel(bundle_id=workbench_bundle.bundle_id.value)

    assert gateway_result["code"] == "cancelled"
    assert workbench_result.code.value == "cancelled"
    assert observations == [
        events.SafeObservation(
            phase="lifecycle",
            operation="cancel",
            outcome=events.ObservationOutcome.CANCELLED,
            bundle_id=gateway_bundle.bundle_id.value,
            outer_thread_id="thread-1",
            outer_run_id="run-1",
        ),
        events.SafeObservation(
            phase="lifecycle",
            operation="cancel",
            outcome=events.ObservationOutcome.CANCELLED,
            bundle_id=workbench_bundle.bundle_id.value,
        ),
    ]


def test_bundle_control_has_no_observation_transport() -> None:
    source = Path(bundle_control.__file__).read_text(encoding="utf-8")

    assert "runtime.events" not in source
    assert "get_stream_writer" not in source
    assert "emit_custom_event" not in source
