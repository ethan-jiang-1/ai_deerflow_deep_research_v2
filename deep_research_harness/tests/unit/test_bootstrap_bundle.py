"""Red tests for the runtime-owned bootstrap bundle store.

@impl BON-001
@impl BON-003
@impl BON-004
@impl BON-005
@impl BON-006
"""

from __future__ import annotations

import fcntl
import os
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from deerflow_deep_research.domain.bootstrap import BootstrapMarker
from deerflow_deep_research.domain.bundle import BUNDLE_SUBTREES, BundleId, RunBundleRef, bundle_host_relative_root
from deerflow_deep_research.domain.lifecycle import WorkUnitStorageReason
from deerflow_deep_research.domain.state import BUNDLE_STATE_SCHEMA_VERSION, BundleLocalState
from deerflow_deep_research.runtime.bootstrap_bundle import (
    LOCK_TIMEOUT_SECONDS,
    BootstrapBundleStore,
)
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle, BundleLifecycleError
from deerflow_deep_research.runtime.work_unit_storage import WorkUnitStorageCheck, WorkUnitStoreError

BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)
_STALE_BUNDLE_ID = BundleId("b_" + "Z" * 43)
_START_MESSAGE_ID = "human-start"
_REQUEST_DIGEST = "d_" + "B" * 43


def _marker(
    *,
    bundle_id: BundleId = BUNDLE.bundle_id,
    start_message_id: str = _START_MESSAGE_ID,
    request_digest: str = _REQUEST_DIGEST,
    state_schema_version: int = BUNDLE_STATE_SCHEMA_VERSION,
) -> BootstrapMarker:
    return BootstrapMarker(
        bundle_id=bundle_id,
        start_message_id=start_message_id,
        request_digest=request_digest,
        state_schema_version=state_schema_version,
    )


def _bundle_state(**overrides: object) -> BundleLocalState:
    values: dict[str, object] = {
        "bundle_id": BUNDLE.bundle_id,
        "implementation_mode": "all_real",
        "start_message_id": _START_MESSAGE_ID,
        "start_request_digest": _REQUEST_DIGEST,
        "schema_version": BUNDLE_STATE_SCHEMA_VERSION,
    }
    values.update(overrides)
    return BundleLocalState(**values)  # type: ignore[arg-type]


async def _ready(*_args: object, **_kwargs: object) -> WorkUnitStorageCheck:
    return WorkUnitStorageCheck("ready", "local_thread_mount")


def _not_ready(*_args: object, **_kwargs: object) -> WorkUnitStorageCheck:
    return WorkUnitStorageCheck("not_ready", "aio_provisioner_unmounted")


def _envelope(workspace: Path) -> SimpleNamespace:
    return SimpleNamespace(workspace_host_path=workspace, parent_sandbox=object(), app_config=object())


async def _store(workspace: Path, **hooks: object) -> BootstrapBundleStore:
    await _published_bundle(workspace)
    return await BootstrapBundleStore.create(
        _envelope(workspace),
        bundle=BUNDLE,
        storage_verifier=_ready,
        **hooks,  # type: ignore[arg-type]
    )


async def _published_bundle(workspace: Path) -> None:
    root = workspace / bundle_host_relative_root(BUNDLE)
    if not root.exists():
        BundleLifecycle(workspace_host_path=workspace)._publish_sync(BUNDLE, _bundle_state())


def _marker_file(workspace: Path) -> Path:
    return workspace / bundle_host_relative_root(BUNDLE) / "request" / "marker.json"


def _write_marker_file(workspace: Path, content: bytes, *, mode: int = 0o600) -> None:
    path = _marker_file(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    os.chmod(path, mode)


class TestEstablishAndRead:
    async def test_read_before_establish_is_none(self, tmp_path: Path) -> None:
        store = await _store(tmp_path)
        assert await store.read_marker() is None

    async def test_establish_writes_marker_bound_to_identity(self, tmp_path: Path) -> None:
        store = await _store(tmp_path)
        marker = _marker()
        await store.establish_bundle(marker)
        assert _marker_file(tmp_path).read_bytes() == marker.canonical_json()
        assert await store.read_marker() == marker

    async def test_marker_is_mode_0600_regular_under_request(self, tmp_path: Path) -> None:
        store = await _store(tmp_path)
        await store.establish_bundle(_marker())
        path = _marker_file(tmp_path)
        assert path.is_file()
        assert stat_mode(path) & 0o777 == 0o600
        assert not path.is_symlink()

    async def test_establish_rejects_group_or_world_writable_existing_marker(self, tmp_path: Path) -> None:
        await _published_bundle(tmp_path)
        _write_marker_file(tmp_path, _marker().canonical_json(), mode=0o644)
        store = await _store(tmp_path)
        with pytest.raises(WorkUnitStoreError) as exc:
            await store.establish_bundle(_marker())
        assert exc.value.reason is WorkUnitStorageReason.POSIX_PRIMITIVES_UNAVAILABLE

    async def test_establish_rejects_symlink_marker(self, tmp_path: Path) -> None:
        await _published_bundle(tmp_path)
        path = _marker_file(tmp_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        target = tmp_path / "elsewhere"
        target.write_bytes(b"x")
        os.symlink(target, path)
        store = await _store(tmp_path)
        with pytest.raises(WorkUnitStoreError):
            await store.establish_bundle(_marker())


class TestLifecyclePublication:
    async def test_fresh_bundle_is_published_only_after_state_and_content_roots_exist(self, tmp_path: Path) -> None:
        """DRH-001: discovery cannot observe a partial Bundle publication."""
        lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
        bundle = await lifecycle.start(
            scope=("user-1", "thread-1"),
            request_text="Research batteries",
            implementation_mode="all_real",
        )

        root = lifecycle.private_root(bundle)
        assert root.name == bundle.bundle_id.value
        assert (root / "state.json").is_file()
        assert {child.name for child in root.iterdir()} >= {"state.json", *BUNDLE_SUBTREES}

    async def test_failed_staged_bundle_is_never_discoverable(self, tmp_path: Path) -> None:
        """DRH-001: an initialization failure leaves no selectable partial directory."""

        def fail(point: str) -> None:
            raise RuntimeError(point)

        lifecycle = BundleLifecycle(workspace_host_path=tmp_path, fault_hook=fail)

        with pytest.raises(RuntimeError):
            await lifecycle.start(
                scope=("user-1", "thread-1"),
                request_text="Research batteries",
                implementation_mode="all_real",
            )
        assert await lifecycle.discover_active(scope=("user-1", "thread-1")) is None


def test_bootstrap_store_accepts_only_a_preselected_bundle_reference(tmp_path: Path) -> None:
    """BON-006: Bootstrap cannot derive or override a Bundle root."""
    bundle = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)

    store = BootstrapBundleStore(workspace_host_path=tmp_path, bundle=bundle)
    assert store.bundle == bundle
    with pytest.raises(TypeError):
        BootstrapBundleStore(workspace_host_path=tmp_path, bundle=bundle, bundle_id="r_" + "A" * 43)  # type: ignore[call-arg]


class TestBundleLifecycleBinding:
    async def test_store_reads_the_previously_published_bundle_state(self, tmp_path: Path) -> None:
        store = await _store(tmp_path)
        assert await store.read_bundle_state() == _bundle_state()

    async def test_unpublished_bundle_cannot_create_a_marker_or_root(self, tmp_path: Path) -> None:
        store = BootstrapBundleStore(workspace_host_path=tmp_path, bundle=BUNDLE)
        with pytest.raises(BundleLifecycleError, match="bundle_unavailable"):
            await store.establish_bundle(_marker())
        assert not (tmp_path / bundle_host_relative_root(BUNDLE)).exists()

    async def test_marker_must_match_the_preselected_bundle_state_before_write(self, tmp_path: Path) -> None:
        store = await _store(tmp_path)
        with pytest.raises(ValueError, match="bootstrap_binding_invalid"):
            await store.establish_bundle(_marker(bundle_id=_STALE_BUNDLE_ID))
        assert not _marker_file(tmp_path).exists()

    async def test_bundle_loss_during_marker_write_is_unavailable_and_never_recreates_root(
        self,
        tmp_path: Path,
    ) -> None:
        def delete_bundle(point: str) -> None:
            if point == "after_staging_fsync":
                shutil.rmtree(tmp_path / bundle_host_relative_root(BUNDLE))

        store = await _store(tmp_path, fault_hook=delete_bundle)
        with pytest.raises(BundleLifecycleError, match="bundle_unavailable"):
            await store.establish_bundle(_marker())
        assert not (tmp_path / bundle_host_relative_root(BUNDLE)).exists()


class TestRecoveryAndIdempotence:
    async def test_partial_directory_with_no_marker_is_completed(self, tmp_path: Path) -> None:
        await _published_bundle(tmp_path)
        store = await _store(tmp_path)
        await store.establish_bundle(_marker())
        assert await store.read_marker() == _marker()

    async def test_stale_marker_is_replaced(self, tmp_path: Path) -> None:
        await _published_bundle(tmp_path)
        _write_marker_file(tmp_path, _marker(bundle_id=_STALE_BUNDLE_ID).canonical_json())
        store = await _store(tmp_path)
        await store.establish_bundle(_marker())
        assert await store.read_marker() == _marker()
        assert _marker_file(tmp_path).read_bytes() == _marker().canonical_json()

    async def test_corrupt_marker_is_replaced(self, tmp_path: Path) -> None:
        await _published_bundle(tmp_path)
        _write_marker_file(tmp_path, b"not json")
        store = await _store(tmp_path)
        await store.establish_bundle(_marker())
        assert await store.read_marker() == _marker()

    async def test_matching_marker_re_establishment_is_idempotent(self, tmp_path: Path) -> None:
        store = await _store(tmp_path)
        marker = _marker()
        await store.establish_bundle(marker)
        snapshot = _marker_file(tmp_path).read_bytes()
        await store.establish_bundle(marker)  # second time: no-op
        assert _marker_file(tmp_path).read_bytes() == snapshot
        assert await store.read_marker() == marker

    async def test_stale_staging_is_cleaned_before_write(self, tmp_path: Path) -> None:
        await _published_bundle(tmp_path)
        staging = _marker_file(tmp_path).parent / ".marker.deadbeef.tmp"
        staging.write_bytes(b"stale")
        store = await _store(tmp_path)
        await store.establish_bundle(_marker())
        assert not staging.exists()
        assert await store.read_marker() == _marker()

    async def test_fault_after_staging_cleans_up_and_leaves_no_marker(self, tmp_path: Path) -> None:
        def fault(_point: str) -> None:
            raise RuntimeError("boom")

        store = await _store(tmp_path, fault_hook=fault, token_factory=lambda: "a" * 32)
        with pytest.raises(RuntimeError):
            await store.establish_bundle(_marker())
        assert not _marker_file(tmp_path).exists()
        # No leftover staging.
        request_dir = _marker_file(tmp_path).parent
        assert not any(name.startswith(".marker.") for name in os.listdir(request_dir))


class TestCreateReadiness:
    async def test_unsupported_provider_fails_closed_before_write(self, tmp_path: Path) -> None:
        async def _verifier(*_a: object, **_k: object) -> WorkUnitStorageCheck:
            return _not_ready()

        with pytest.raises(WorkUnitStoreError) as exc:
            await BootstrapBundleStore.create(
                _envelope(tmp_path),
                bundle=BUNDLE,
                storage_verifier=_verifier,
            )
        assert exc.value.code.value == "work_unit_storage_unavailable"
        assert not (tmp_path / "deep-research").exists()


class TestLockContention:
    async def test_real_lock_contention_releases_within_deadline(self, tmp_path: Path) -> None:
        ticks = iter([0.0, 0.0, 0.0, LOCK_TIMEOUT_SECONDS + 1])
        store_a = await _store(tmp_path)
        store_b = await _store(tmp_path, monotonic=lambda: next(ticks), lock_sleep=lambda _s: None)
        marker = _marker()

        # Hold the bootstrap lock from another store while store_b establishes.
        opened, request_fd = store_a._open_request()
        lock_fd = store_a._open_lock(request_fd)
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            with pytest.raises(WorkUnitStoreError) as exc:
                await store_b.establish_bundle(marker)
            assert exc.value.reason is WorkUnitStorageReason.LOCK_TIMEOUT
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
            os.close(lock_fd)
            for fd in reversed(opened):
                os.close(fd)

        # After release, establishment succeeds.
        await store_b.establish_bundle(marker)
        assert await store_b.read_marker() == marker


def stat_mode(path: Path) -> int:
    return os.stat(path).st_mode
