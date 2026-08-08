"""Transient cross-instance exclusion for one already-published Bundle root.

The directory descriptor is deliberately not a lifecycle record.  It only keeps a
short advisory exclusion while a caller reads, reduces, and publishes Bundle-local
State.  The selected path is reopened with ``O_NOFOLLOW`` before durable work so a
removed or replaced root cannot be used through a detached descriptor.
"""

from __future__ import annotations

import asyncio
import fcntl
import os
import stat
import threading
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

_LOCK_RETRY_SECONDS = 0.01


class BundleTransitionError(RuntimeError):
    """The selected Bundle root cannot safely participate in a transition."""


class _BundleTransitionWaitCancelled(RuntimeError):
    """The off-loop waiter observed cancellation before it acquired the root."""


def _open_directory_no_follow(root: Path) -> tuple[int, tuple[int, int]]:
    try:
        fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as exc:
        raise BundleTransitionError("bundle_unavailable") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISDIR(info.st_mode):
            raise BundleTransitionError("bundle_unavailable")
        return fd, (info.st_dev, info.st_ino)
    except BaseException:
        os.close(fd)
        raise


def _assert_live_root(root: Path, identity: tuple[int, int]) -> None:
    fd, current_identity = _open_directory_no_follow(root)
    try:
        if current_identity != identity:
            raise BundleTransitionError("bundle_unavailable")
    finally:
        os.close(fd)


@dataclass
class BundleTransitionLease:
    """A held directory lock with the identity needed for no-follow liveness checks."""

    _root: Path
    _directory_fd: int
    _identity: tuple[int, int]
    _liveness_root: Path | None = None
    _liveness_identity: tuple[int, int] | None = None
    _released: bool = False

    @property
    def directory_fd(self) -> int:
        if self._released:
            raise BundleTransitionError("bundle_unavailable")
        return self._directory_fd

    def ensure_live(self) -> None:
        """Reject deletion or replacement before a State read or durable write."""

        if self._released:
            raise BundleTransitionError("bundle_unavailable")
        _assert_live_root(self._root, self._identity)
        if self._liveness_root is not None and self._liveness_identity is not None:
            _assert_live_root(self._liveness_root, self._liveness_identity)

    def release(self) -> None:
        """Release the advisory lock and descriptor exactly once off the event loop."""

        if self._released:
            return
        self._released = True
        try:
            fcntl.flock(self._directory_fd, fcntl.LOCK_UN)
        except OSError as exc:
            raise BundleTransitionError("bundle_unavailable") from exc
        finally:
            os.close(self._directory_fd)


def _acquire_sync(
    root: Path,
    liveness_root: Path,
    cancelled: threading.Event,
) -> BundleTransitionLease:
    fd, identity = _open_directory_no_follow(root)
    acquired = False
    try:
        while True:
            if cancelled.is_set():
                raise _BundleTransitionWaitCancelled
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
                break
            except BlockingIOError:
                time.sleep(_LOCK_RETRY_SECONDS)
            except OSError as exc:
                raise BundleTransitionError("bundle_unavailable") from exc
        if cancelled.is_set():
            raise _BundleTransitionWaitCancelled
        liveness_identity = identity
        if liveness_root != root:
            liveness_fd, liveness_identity = _open_directory_no_follow(liveness_root)
            os.close(liveness_fd)
        lease = BundleTransitionLease(
            _root=root,
            _directory_fd=fd,
            _identity=identity,
            _liveness_root=(None if liveness_root == root else liveness_root),
            _liveness_identity=(None if liveness_root == root else liveness_identity),
        )
        lease.ensure_live()
        return lease
    except BaseException:
        if acquired:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            except OSError:
                pass
        os.close(fd)
        raise


async def _release_off_loop(lease: BundleTransitionLease) -> None:
    worker = asyncio.create_task(asyncio.to_thread(lease.release))
    try:
        await asyncio.shield(worker)
    except asyncio.CancelledError:
        await asyncio.shield(worker)
        raise


class BundleTransitionCoordinator:
    """Acquire a short Bundle-root exclusion without retaining lifecycle facts."""

    def __init__(self, *, root: Path, liveness_root: Path | None = None) -> None:
        self._root = Path(root)
        self._liveness_root = Path(liveness_root) if liveness_root is not None else self._root

    @asynccontextmanager
    async def hold(self) -> AsyncIterator[BundleTransitionLease]:
        """Hold the no-follow directory exclusion while a State transition runs."""

        cancelled = threading.Event()
        worker = asyncio.create_task(asyncio.to_thread(_acquire_sync, self._root, self._liveness_root, cancelled))
        try:
            lease = await asyncio.shield(worker)
        except asyncio.CancelledError:
            cancelled.set()
            try:
                await asyncio.shield(worker)
            except _BundleTransitionWaitCancelled:
                pass
            raise
        try:
            yield lease
        finally:
            await _release_off_loop(lease)


__all__ = ["BundleTransitionCoordinator", "BundleTransitionError", "BundleTransitionLease"]
