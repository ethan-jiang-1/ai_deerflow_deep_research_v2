"""Blocking-I/O and cancellation guards for the bootstrap bundle store.

@impl BON-001
@impl BON-003
"""

from __future__ import annotations

import asyncio
import fcntl
import os
import shutil
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from deerflow_deep_research.domain.bootstrap import BootstrapMarker
from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, run_bundle_root
from deerflow_deep_research.domain.state import BUNDLE_STATE_SCHEMA_VERSION, BundleLocalState
from deerflow_deep_research.runtime.bootstrap_bundle import BootstrapBundleStore
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle, BundleLifecycleError
from deerflow_deep_research.runtime.work_unit_storage_probe import WorkUnitStorageCheck

BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)


def _marker() -> BootstrapMarker:
    return BootstrapMarker(
        bundle_id=BUNDLE.bundle_id,
        start_message_id="human-start",
        request_digest="d_" + "B" * 43,
        state_schema_version=BUNDLE_STATE_SCHEMA_VERSION,
    )


def _bundle_state() -> BundleLocalState:
    return BundleLocalState(
        bundle_id=BUNDLE.bundle_id,
        implementation_mode="all_real",
        start_message_id="human-start",
        start_request_digest="d_" + "B" * 43,
        schema_version=BUNDLE_STATE_SCHEMA_VERSION,
    )


async def _ready(*_args: object, **_kwargs: object) -> WorkUnitStorageCheck:
    return WorkUnitStorageCheck("ready", "local_thread_mount")


async def _store(tmp_path: Path, **hooks: object) -> BootstrapBundleStore:
    BundleLifecycle(workspace_host_path=tmp_path)._publish_sync(BUNDLE, _bundle_state())
    envelope = SimpleNamespace(workspace_host_path=tmp_path, parent_sandbox=object(), app_config=object())
    return await BootstrapBundleStore.create(
        envelope,
        bundle=BUNDLE,
        storage_verifier=_ready,
        **hooks,  # type: ignore[arg-type]
    )


def _marker_file(tmp_path: Path) -> Path:
    return tmp_path / run_bundle_root(BUNDLE).removeprefix("workspace/") / "request" / "marker.json"


async def test_establish_filesystem_work_does_not_block_event_loop(tmp_path: Path) -> None:
    def slow_fault(point: str) -> None:
        if point == "after_staging_fsync":
            time.sleep(0.1)

    store = await _store(tmp_path, fault_hook=slow_fault)
    ticks = 0

    async def heartbeat() -> None:
        nonlocal ticks
        for _ in range(10):
            await asyncio.sleep(0.01)
            ticks += 1

    await asyncio.gather(store.establish_bundle(_marker()), heartbeat())
    assert ticks == 10
    assert await store.read_marker() == _marker()


async def test_read_marker_does_not_block_event_loop(tmp_path: Path) -> None:
    store = await _store(tmp_path)
    await store.establish_bundle(_marker())
    ticks = 0

    async def heartbeat() -> None:
        nonlocal ticks
        for _ in range(10):
            await asyncio.sleep(0.01)
            ticks += 1

    _, _ = await asyncio.gather(store.read_marker(), heartbeat())
    assert ticks == 10


async def test_cancellation_after_staging_aborts_without_partial_marker(tmp_path: Path) -> None:
    entered = threading.Event()
    release = threading.Event()

    def block_after_fsync(point: str) -> None:
        if point == "after_staging_fsync":
            entered.set()
            release.wait(timeout=1)

    store = await _store(tmp_path, fault_hook=block_after_fsync)
    task = asyncio.create_task(store.establish_bundle(_marker()))
    assert await asyncio.to_thread(entered.wait, 1)
    task.cancel()
    await asyncio.sleep(0)
    assert not task.done()
    release.set()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert not _marker_file(tmp_path).exists()
    request_dir = _marker_file(tmp_path).parent
    assert not any(name.startswith(".marker.") for name in os.listdir(request_dir))


async def test_cancellation_before_lock_stops_retry_and_leaves_no_marker(tmp_path: Path) -> None:
    store = await _store(tmp_path)
    lock = _marker_file(tmp_path).parent / ".bootstrap.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    try:
        task = asyncio.create_task(store.establish_bundle(_marker()))
        await asyncio.sleep(0.05)
        task.cancel()
        started = time.monotonic()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert time.monotonic() - started < 0.25
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    assert not _marker_file(tmp_path).exists()


async def test_bundle_loss_during_blocking_marker_write_returns_unavailable(tmp_path: Path) -> None:
    def delete_bundle(point: str) -> None:
        if point == "after_staging_fsync":
            shutil.rmtree(tmp_path / run_bundle_root(BUNDLE).removeprefix("workspace/"))

    store = await _store(tmp_path, fault_hook=delete_bundle)
    with pytest.raises(BundleLifecycleError, match="bundle_unavailable"):
        await store.establish_bundle(_marker())
    assert not (tmp_path / run_bundle_root(BUNDLE).removeprefix("workspace/")).exists()
