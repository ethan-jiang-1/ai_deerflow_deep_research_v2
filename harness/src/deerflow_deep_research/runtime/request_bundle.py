"""Runtime-owned request-bundle profile writer.

@impl HIN-004
@impl REG-010
"""

from __future__ import annotations

import asyncio
import fcntl
import json
import os
import stat
import time
from collections.abc import Awaitable, Callable
from dataclasses import fields, replace
from pathlib import Path
from typing import Any

from deerflow_deep_research.domain.bundle import (
    BUNDLE_HOST_SUBTREE,
    PROFILE_FILENAME,
    REQUEST_SUBTREE,
    RunBundleRef,
    bundle_host_relative_root,
    bundle_profile_path,
)
from deerflow_deep_research.domain.lifecycle import WorkUnitStorageReason
from deerflow_deep_research.domain.profile import (
    ResearchProfile,
    canonical_profile_bytes,
    compute_profile_content_hash,
)
from deerflow_deep_research.domain.state import BundleLocalState, ContentRef
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycleError, BundleStateStore
from deerflow_deep_research.runtime.work_unit_storage import (
    WorkUnitStorageCheck,
    WorkUnitStoreError,
    verify_runtime_work_unit_storage,
)

LOCK_TIMEOUT_SECONDS = 2.0
LOCK_RETRY_SECONDS = 0.025
MAX_PROFILE_BYTES = 16 * 1024
PROFILE_CONTENT_REF_SCHEMA_VERSION = 1
_PROFILE_LOCK = ".profile.lock"
_STAGING_PREFIX = ".profile."
_STAGING_SUFFIX = ".tmp"

# HITL1 may project its bounded profile/interaction facts, but it must never use a
# stale State snapshot to write lifecycle or direction authority back over a newer
# controller transition.
_HITL1_STATE_FIELDS = frozenset(
    {
        "phase",
        "phase_status",
        "waiting_for",
        "terminal_status",
        "terminal_reason",
        "latest_incident",
        "pending_request_id",
        "pending_cursor",
        "pending_request_mode",
        "consumed_request_ids",
        "consumed_message_ids",
        "hitl1_visit_count",
        "profile_ref",
        "research_depth",
        "target_audience",
        "output_format",
        "cost_tolerance",
        "time_budget",
        "must_answer_questions",
        "comparison_required",
        "comparison_subjects",
        "request_language",
        "output_language",
        "degraded_profile",
        "pending_profile",
        "profile_followup_round",
        "proposed_profile",
        "profile_rejection_round",
        "profile_feedback_cursor_message_id",
        "proposal_version",
        "interaction_feedback",
        "execution_trace",
    }
)

StorageVerifier = Callable[..., Awaitable[WorkUnitStorageCheck]]
FaultHook = Callable[[str], None]


def _token() -> str:
    import secrets

    return secrets.token_hex(16)


def _open_directory(parent_fd: int, name: str, *, create: bool) -> int:
    if create:
        try:
            os.mkdir(name, 0o700, dir_fd=parent_fd)
        except FileExistsError:
            pass
    try:
        fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
    except OSError as exc:
        raise WorkUnitStoreError(WorkUnitStorageReason.POSIX_PRIMITIVES_UNAVAILABLE) from exc
    if not stat.S_ISDIR(os.fstat(fd).st_mode):
        os.close(fd)
        raise WorkUnitStoreError(WorkUnitStorageReason.POSIX_PRIMITIVES_UNAVAILABLE)
    return fd


def _require_secure_regular(fd: int) -> None:
    mode = os.fstat(fd).st_mode
    if not stat.S_ISREG(mode) or mode & 0o077:
        raise WorkUnitStoreError(WorkUnitStorageReason.POSIX_PRIMITIVES_UNAVAILABLE)


def _is_staging_name(name: str) -> bool:
    return name.startswith(_STAGING_PREFIX) and name.endswith(_STAGING_SUFFIX)


class RequestBundleStore:
    """One verified research-scoped request artifact writer."""

    def __init__(
        self,
        *,
        workspace_host_path: Path,
        bundle: RunBundleRef,
        monotonic: Callable[[], float] = time.monotonic,
        lock_sleep: Callable[[float], None] = time.sleep,
        token_factory: Callable[[], str] = _token,
        fault_hook: FaultHook | None = None,
    ) -> None:
        if not isinstance(bundle, RunBundleRef):
            raise TypeError("bundle_required")
        # The runtime selects this reference before a node receives the store.  Every
        # request artifact therefore resolves under the same already-published Bundle.
        bundle_profile_path(bundle)
        self._workspace_host_path = Path(workspace_host_path)
        self.bundle = bundle
        self._state_store = BundleStateStore(
            root=self._workspace_host_path / bundle_host_relative_root(bundle),
            bundle_id=bundle.bundle_id,
        )
        self._monotonic = monotonic
        self._lock_sleep = lock_sleep
        self._token_factory = token_factory
        self._fault_hook = fault_hook
        self._state_baselines: dict[int, BundleLocalState] = {}

    @classmethod
    async def create(
        cls,
        envelope: Any,
        *,
        bundle: RunBundleRef,
        storage_verifier: StorageVerifier = verify_runtime_work_unit_storage,
        provider: Any = None,
        monotonic: Callable[[], float] = time.monotonic,
        lock_sleep: Callable[[float], None] = time.sleep,
        token_factory: Callable[[], str] = _token,
        fault_hook: FaultHook | None = None,
    ) -> RequestBundleStore:
        if not isinstance(bundle, RunBundleRef):
            raise TypeError("bundle_required")
        check = await storage_verifier(envelope, bundle=bundle, provider=provider)
        if not check.ready:
            try:
                reason = WorkUnitStorageReason(check.reason)
            except ValueError as exc:
                raise WorkUnitStoreError(WorkUnitStorageReason.PROVIDER_UNRECOGNIZED) from exc
            raise WorkUnitStoreError(reason)
        store = cls(
            workspace_host_path=Path(envelope.workspace_host_path),
            bundle=bundle,
            monotonic=monotonic,
            lock_sleep=lock_sleep,
            token_factory=token_factory,
            fault_hook=fault_hook,
        )
        await store.read_bundle_state()
        return store

    async def read_bundle_state(self) -> BundleLocalState:
        """Read the selected Bundle's authoritative lifecycle/profile State."""
        state = await self._state_store.read()
        self._remember_state(state)
        return state

    async def write_bundle_state(
        self,
        state: BundleLocalState,
        *,
        expected_revision: int,
    ) -> BundleLocalState:
        """Re-reduce HITL1's permitted State fields under the shared transition lock."""

        if state.revision != expected_revision:
            raise ValueError("state_revision_invalid")
        baseline = self._state_baselines.get(expected_revision)
        if baseline is None:
            raise ValueError("state_revision_conflict")
        changes = self._permitted_changes(baseline=baseline, desired=state)
        async with self._state_store.transition() as lease:
            current = await self._state_store.read(lease=lease)
            updated = replace(current, **changes)
            if updated == current:
                self._remember_state(current)
                return current
            written = await self._state_store.write(
                updated,
                expected_revision=current.revision,
                lease=lease,
            )
        self._remember_state(written)
        return written

    def _remember_state(self, state: BundleLocalState) -> None:
        self._state_baselines[state.revision] = state
        while len(self._state_baselines) > 8:
            del self._state_baselines[min(self._state_baselines)]

    @staticmethod
    def _permitted_changes(
        *,
        baseline: BundleLocalState,
        desired: BundleLocalState,
    ) -> dict[str, Any]:
        if baseline.bundle_id != desired.bundle_id:
            raise ValueError("bundle_state_identity_mismatch")
        changes = {
            field.name: getattr(desired, field.name)
            for field in fields(BundleLocalState)
            if field.name != "revision" and getattr(baseline, field.name) != getattr(desired, field.name)
        }
        if set(changes) - _HITL1_STATE_FIELDS:
            raise ValueError("request_bundle_state_field_forbidden")
        return changes

    async def write_profile(self, profile: ResearchProfile) -> ContentRef:
        if not isinstance(profile, ResearchProfile):
            raise TypeError("profile_required")
        content = canonical_profile_bytes(profile)
        if len(content) > MAX_PROFILE_BYTES:
            raise ValueError("profile_too_large")
        await self.read_bundle_state()
        try:
            await asyncio.to_thread(self._write_profile_sync, content)
        except (OSError, WorkUnitStoreError):
            await self._raise_if_bundle_unavailable()
            raise
        await self.read_bundle_state()
        return ContentRef(
            sandbox_path=bundle_profile_path(self.bundle),
            content_hash=compute_profile_content_hash(profile),
            schema_version=PROFILE_CONTENT_REF_SCHEMA_VERSION,
            short_summary=self._short_summary(profile),
        )

    async def read_profile(self, profile_ref: ContentRef) -> ResearchProfile:
        """Read the selected Bundle's one canonical, integrity-checked profile."""

        if not isinstance(profile_ref, ContentRef):
            raise TypeError("profile_ref_required")
        if profile_ref.sandbox_path != bundle_profile_path(self.bundle):
            raise ValueError("profile_ref_path_invalid")
        if profile_ref.schema_version != PROFILE_CONTENT_REF_SCHEMA_VERSION:
            raise ValueError("profile_ref_schema_version_invalid")
        try:
            content = await asyncio.to_thread(self._read_profile_sync)
        except (FileNotFoundError, OSError, WorkUnitStoreError):
            await self._raise_if_bundle_unavailable()
            raise
        try:
            profile = ResearchProfile.model_validate(json.loads(content))
        except (TypeError, UnicodeDecodeError, ValueError) as exc:
            raise ValueError("profile_schema_invalid") from exc
        if compute_profile_content_hash(profile) != profile_ref.content_hash:
            raise ValueError("profile_content_hash_mismatch")
        return profile

    async def _raise_if_bundle_unavailable(self) -> None:
        try:
            await self.read_bundle_state()
        except BundleLifecycleError:
            raise

    @staticmethod
    def _short_summary(profile: ResearchProfile) -> str:
        depth = profile.depth.value if profile.depth is not None else "degraded"
        audience = profile.audience.value if profile.audience is not None else "degraded"
        return f"HITL1 profile: depth={depth}; audience={audience}"

    def _fault(self, point: str) -> None:
        if self._fault_hook is not None:
            self._fault_hook(point)

    def _open_request(self) -> tuple[list[int], int]:
        try:
            workspace_fd = os.open(self._workspace_host_path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        except OSError as exc:
            raise WorkUnitStoreError(WorkUnitStorageReason.THREAD_MOUNT_UNAVAILABLE) from exc
        opened = [workspace_fd]
        try:
            current = workspace_fd
            for part in (
                *BUNDLE_HOST_SUBTREE.split("/"),
                self.bundle.scope_bucket,
                self.bundle.bundle_id.value,
                REQUEST_SUBTREE,
            ):
                current = _open_directory(current, part, create=False)
                opened.append(current)
            return opened, current
        except BaseException:
            for fd in reversed(opened):
                os.close(fd)
            raise

    def _open_lock(self, request_fd: int) -> int:
        try:
            fd = -1
            for _ in range(3):
                try:
                    fd = os.open(
                        _PROFILE_LOCK,
                        os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW,
                        0o600,
                        dir_fd=request_fd,
                    )
                    break
                except FileNotFoundError:
                    continue
            if fd < 0:
                raise FileNotFoundError("stable lock could not be opened")
            _require_secure_regular(fd)
            return fd
        except WorkUnitStoreError:
            raise
        except OSError as exc:
            raise WorkUnitStoreError(WorkUnitStorageReason.POSIX_PRIMITIVES_UNAVAILABLE) from exc

    def _acquire_lock(self, lock_fd: int) -> None:
        deadline: float | None = None
        while True:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return
            except BlockingIOError as exc:
                if deadline is None:
                    deadline = self._monotonic() + LOCK_TIMEOUT_SECONDS
                if self._monotonic() >= deadline:
                    raise WorkUnitStoreError(WorkUnitStorageReason.LOCK_TIMEOUT) from exc
                self._lock_sleep(LOCK_RETRY_SECONDS)

    @staticmethod
    def _clean_staging(request_fd: int) -> None:
        for name in os.listdir(request_fd):
            if _is_staging_name(name):
                try:
                    os.unlink(name, dir_fd=request_fd)
                except OSError as exc:
                    raise WorkUnitStoreError(WorkUnitStorageReason.PROBE_CLEANUP_FAILED) from exc

    @staticmethod
    def _read_existing_profile(request_fd: int) -> bytes | None:
        try:
            fd = os.open(PROFILE_FILENAME, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=request_fd)
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise WorkUnitStoreError(WorkUnitStorageReason.POSIX_PRIMITIVES_UNAVAILABLE) from exc
        try:
            _require_secure_regular(fd)
            size = os.fstat(fd).st_size
            if size > MAX_PROFILE_BYTES:
                raise ValueError("profile_too_large")
            chunks: list[bytes] = []
            remaining = size
            while remaining:
                chunk = os.read(fd, min(remaining, 64 * 1024))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            return b"".join(chunks)
        finally:
            os.close(fd)

    def _read_profile_sync(self) -> bytes:
        opened, request_fd = self._open_request()
        try:
            content = self._read_existing_profile(request_fd)
            if content is None:
                raise FileNotFoundError("profile_missing")
            return content
        finally:
            for fd in reversed(opened):
                os.close(fd)

    def _write_profile_sync(self, content: bytes) -> None:
        opened, request_fd = self._open_request()
        lock_fd = -1
        staging_name: str | None = None
        try:
            lock_fd = self._open_lock(request_fd)
            self._acquire_lock(lock_fd)
            self._clean_staging(request_fd)

            existing = self._read_existing_profile(request_fd)
            if existing == content:
                return
            if existing is not None:
                try:
                    os.unlink(PROFILE_FILENAME, dir_fd=request_fd)
                except FileNotFoundError:
                    pass

            self._fault("before_staging_write")
            staging_name = f"{_STAGING_PREFIX}{self._token_factory()}{_STAGING_SUFFIX}"
            staging_fd = os.open(
                staging_name,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW,
                0o600,
                dir_fd=request_fd,
            )
            try:
                _require_secure_regular(staging_fd)
                view = memoryview(content)
                while view:
                    written = os.write(staging_fd, view)
                    view = view[written:]
                os.fsync(staging_fd)
            finally:
                os.close(staging_fd)
            self._fault("after_staging_fsync")
            os.replace(staging_name, PROFILE_FILENAME, src_dir_fd=request_fd, dst_dir_fd=request_fd)
            staging_name = None
            self._fault("after_profile_replace")
            os.fsync(request_fd)
        finally:
            if staging_name is not None:
                try:
                    os.unlink(staging_name, dir_fd=request_fd)
                except FileNotFoundError:
                    pass
            if lock_fd >= 0:
                try:
                    fcntl.flock(lock_fd, fcntl.LOCK_UN)
                finally:
                    os.close(lock_fd)
            for fd in reversed(opened):
                os.close(fd)


__all__ = [
    "LOCK_RETRY_SECONDS",
    "LOCK_TIMEOUT_SECONDS",
    "MAX_PROFILE_BYTES",
    "PROFILE_CONTENT_REF_SCHEMA_VERSION",
    "RequestBundleStore",
]
