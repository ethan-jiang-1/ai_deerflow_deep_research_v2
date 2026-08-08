"""POSIX feasibility evidence for the future Bundle-local coordination adapter.

@impl REG-021
"""

from __future__ import annotations

import asyncio
import fcntl
import os
import select
import signal
import stat
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pytest

from deerflow_deep_research.domain.bundle import RunBundleRef, new_bundle_id
from deerflow_deep_research.domain.lifecycle import WorkUnitStorageReason
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle, scope_bucket
from deerflow_deep_research.runtime.work_unit_storage import WorkUnitStoreError
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore


class _DirectoryWaitCancelled(RuntimeError):
    pass


def _open_directory_no_follow(path: Path) -> int:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        if not stat.S_ISDIR(os.fstat(fd).st_mode):
            raise RuntimeError("directory_required")
        return fd
    except BaseException:
        os.close(fd)
        raise


def _acquire_directory_lock(path: Path, cancelled: threading.Event | None = None) -> int:
    fd = _open_directory_no_follow(path)
    try:
        while True:
            if cancelled is not None and cancelled.is_set():
                raise _DirectoryWaitCancelled
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return fd
            except BlockingIOError:
                time.sleep(0.01)
    except BaseException:
        os.close(fd)
        raise


def _release_directory_lock(fd: int) -> None:
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


@dataclass(frozen=True)
class _DirectoryCoordinatorProbe:
    """Test-only composition of the existing no-follow and advisory-lock primitives."""

    directory: Path

    @contextmanager
    def held(self) -> Iterator[None]:
        fd = _acquire_directory_lock(self.directory)
        try:
            yield
        finally:
            _release_directory_lock(fd)


def _wait_for_byte(fd: int, *, timeout: float) -> bool:
    ready, _, _ = select.select((fd,), (), (), timeout)
    if not ready:
        return False
    return os.read(fd, 1) == b"1"


def _reap_or_terminate(pid: int) -> int:
    completed_pid, status = os.waitpid(pid, os.WNOHANG)
    if completed_pid == 0:
        os.kill(pid, signal.SIGTERM)
        _, status = os.waitpid(pid, 0)
    return status


def _fork_holder_until_release(directory: Path) -> tuple[int, int, int]:
    acquired_reader, acquired_writer = os.pipe()
    release_reader, release_writer = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(acquired_reader)
        os.close(release_writer)
        try:
            with _DirectoryCoordinatorProbe(directory).held():
                os.write(acquired_writer, b"1")
                os.read(release_reader, 1)
        finally:
            os.close(acquired_writer)
            os.close(release_reader)
        os._exit(0)
    os.close(acquired_writer)
    os.close(release_reader)
    return pid, acquired_reader, release_writer


def _fork_directory_contender(directory: Path) -> tuple[int, int]:
    acquired_reader, acquired_writer = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(acquired_reader)
        try:
            with _DirectoryCoordinatorProbe(directory).held():
                os.write(acquired_writer, b"1")
        finally:
            os.close(acquired_writer)
        os._exit(0)
    os.close(acquired_writer)
    return pid, acquired_reader


def _assert_forked_processes_serialize_directory(directory: Path) -> None:
    holder_pid, holder_acquired, release_holder = _fork_holder_until_release(directory)
    contender_pid: int | None = None
    contender_acquired = -1
    try:
        assert _wait_for_byte(holder_acquired, timeout=2)
        contender_pid, contender_acquired = _fork_directory_contender(directory)
        assert not _wait_for_byte(contender_acquired, timeout=0.1)
        os.write(release_holder, b"1")
        assert _wait_for_byte(contender_acquired, timeout=2)
    finally:
        try:
            os.write(release_holder, b"1")
        except OSError:
            pass
        os.close(holder_acquired)
        os.close(release_holder)
        assert os.WIFEXITED(_reap_or_terminate(holder_pid))
        if contender_pid is not None:
            os.close(contender_acquired)
            assert os.WIFEXITED(_reap_or_terminate(contender_pid))


def _fork_holder_for_termination(directory: Path) -> tuple[int, int]:
    acquired_reader, acquired_writer = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(acquired_reader)
        try:
            with _DirectoryCoordinatorProbe(directory).held():
                os.write(acquired_writer, b"1")
                time.sleep(60)
        finally:
            os.close(acquired_writer)
        os._exit(0)
    os.close(acquired_writer)
    return pid, acquired_reader


async def _cancelled_directory_waiter(directory: Path) -> None:
    cancelled = threading.Event()
    worker = asyncio.create_task(asyncio.to_thread(_acquire_directory_lock, directory, cancelled))
    try:
        fd = await asyncio.shield(worker)
    except asyncio.CancelledError:
        cancelled.set()
        try:
            await asyncio.shield(worker)
        except _DirectoryWaitCancelled:
            pass
        raise
    else:
        _release_directory_lock(fd)


def _published_bundle(lifecycle: BundleLifecycle, *, thread_id: str) -> RunBundleRef:
    bundle = RunBundleRef(
        bundle_id=new_bundle_id(),
        scope_bucket=scope_bucket(effective_user_id="fixture-user", outer_thread_id=thread_id),
    )
    lifecycle._publish_sync(bundle)
    return bundle


def _store(workspace: Path, bundle: RunBundleRef) -> WorkUnitStore:
    return WorkUnitStore(
        workspace_host_path=workspace,
        bundle=bundle,
        clock=lambda: datetime(2026, 7, 14, tzinfo=UTC),
        monotonic=time.monotonic,
        lock_sleep=time.sleep,
        token_factory=lambda: "f" * 32,
        fault_hook=None,
    )


def test_directory_lock_primitives_serialize_scope_and_bundle_and_release_dead_holder(tmp_path: Path) -> None:
    """REG-021: no-follow directory locks add no scope record or lifecycle write."""

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = _published_bundle(lifecycle, thread_id="fixture-thread")
    root = lifecycle.private_root(bundle)
    scope_root = root.parent
    baseline_state = (root / "state.json").read_bytes()

    assert {entry.name for entry in scope_root.iterdir()} == {bundle.bundle_id.value}
    _assert_forked_processes_serialize_directory(scope_root)
    _assert_forked_processes_serialize_directory(root)

    holder_pid, holder_acquired = _fork_holder_for_termination(root)
    holder_status: int | None = None
    try:
        assert _wait_for_byte(holder_acquired, timeout=2)
        os.kill(holder_pid, signal.SIGTERM)
        _, holder_status = os.waitpid(holder_pid, 0)
        assert os.WIFSIGNALED(holder_status)
        with _DirectoryCoordinatorProbe(root).held():
            pass
    finally:
        os.close(holder_acquired)
        if holder_status is None:
            _reap_or_terminate(holder_pid)

    assert {entry.name for entry in scope_root.iterdir()} == {bundle.bundle_id.value}
    assert (root / "state.json").read_bytes() == baseline_state
    assert not (root / "graph.sqlite").exists()
    assert not any(path.name.endswith(".lock") for path in scope_root.iterdir())


@pytest.mark.asyncio
async def test_cancelled_directory_waiter_releases_without_bundle_state_or_checkpoint_write(tmp_path: Path) -> None:
    """REG-021: cancellation only releases a transient directory descriptor."""

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = _published_bundle(lifecycle, thread_id="cancelled-waiter")
    root = lifecycle.private_root(bundle)
    baseline_state = (root / "state.json").read_bytes()
    held_scope_fd = _acquire_directory_lock(root.parent)
    try:
        waiter = asyncio.create_task(_cancelled_directory_waiter(root.parent))
        await asyncio.sleep(0.05)
        assert not waiter.done()
        waiter.cancel()
        with pytest.raises(asyncio.CancelledError):
            await waiter
    finally:
        _release_directory_lock(held_scope_fd)

    assert (root / "state.json").read_bytes() == baseline_state
    assert not (root / "graph.sqlite").exists()


def test_fresh_no_follow_reopen_detects_removed_or_replaced_bundle_before_publish(tmp_path: Path) -> None:
    """REG-021: a detached descriptor cannot publish after root loss or replacement."""

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    removed_bundle = _published_bundle(lifecycle, thread_id="removed-root")
    removed_root = lifecycle.private_root(removed_bundle)
    removed_state = (removed_root / "state.json").read_bytes()
    held_removed_fd = _open_directory_no_follow(removed_root)
    displaced_removed_root = removed_root.with_name(f"{removed_root.name}-removed")
    try:
        os.rename(removed_root, displaced_removed_root)
        with pytest.raises(WorkUnitStoreError) as removed:
            _store(tmp_path, removed_bundle)._require_live_bundle(held_removed_fd)
        assert removed.value.reason is WorkUnitStorageReason.POSIX_PRIMITIVES_UNAVAILABLE
    finally:
        os.close(held_removed_fd)
    assert (displaced_removed_root / "state.json").read_bytes() == removed_state
    assert not (displaced_removed_root / "graph.sqlite").exists()

    replacement_bundle = _published_bundle(lifecycle, thread_id="replacement-root")
    replacement_root = lifecycle.private_root(replacement_bundle)
    replacement_state = (replacement_root / "state.json").read_bytes()
    held_replacement_fd = _open_directory_no_follow(replacement_root)
    displaced_replacement_root = replacement_root.with_name(f"{replacement_root.name}-old")
    try:
        os.rename(replacement_root, displaced_replacement_root)
        replacement_root.mkdir(mode=0o700)
        with pytest.raises(WorkUnitStoreError) as replaced:
            _store(tmp_path, replacement_bundle)._require_live_bundle(held_replacement_fd)
        assert replaced.value.reason is WorkUnitStorageReason.POSIX_PRIMITIVES_UNAVAILABLE
    finally:
        os.close(held_replacement_fd)

    assert (displaced_replacement_root / "state.json").read_bytes() == replacement_state
    assert not (replacement_root / "graph.sqlite").exists()
    assert not (displaced_replacement_root / "graph.sqlite").exists()
