"""Direct Bundle-lifecycle behavior for the local workbench.

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
@impl REG-017
@impl RWB-007
"""

from __future__ import annotations

import inspect
import os
import shutil
from pathlib import Path

import pytest

from deerflow_deep_research.domain.lifecycle import (
    BundleAvailability,
    LifecycleAction,
    LifecycleStatus,
    ResultCode,
)
from deerflow_deep_research.domain.session_workbench import (
    ArtifactCatalogKey,
    WorkbenchAvailability,
)
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.session_workbench import BundleWorkbench, LocalBundleWorkbench

SCOPE = ("local-user", "local-thread")
FOREIGN_SCOPE = ("foreign-user", "foreign-thread")


async def _workbench(tmp_path: Path) -> tuple[BundleLifecycle, BundleWorkbench, LocalBundleWorkbench, str]:
    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(
        scope=SCOPE,
        request_text="Compare public storage options.",
        implementation_mode="all_real",
    )
    bundle_workbench = BundleWorkbench(lifecycle=lifecycle, scope=SCOPE)
    return lifecycle, bundle_workbench, LocalBundleWorkbench(bundle_workbench=bundle_workbench), bundle.bundle_id.value


def _write_contained_artifact(lifecycle: BundleLifecycle, bundle_id: str, relative_path: str, content: bytes) -> Path:
    from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef
    from deerflow_deep_research.runtime.bundle_lifecycle import scope_bucket

    bundle = RunBundleRef(
        bundle_id=BundleId(bundle_id),
        scope_bucket=scope_bucket(effective_user_id=SCOPE[0], outer_thread_id=SCOPE[1]),
    )
    path = lifecycle.private_root(bundle) / relative_path
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    path.write_bytes(content)
    path.chmod(0o600)
    return path


def test_local_workbench_accepts_only_the_direct_bundle_workbench() -> None:
    parameters = inspect.signature(LocalBundleWorkbench).parameters

    assert tuple(parameters) == ("bundle_workbench",)


@pytest.mark.asyncio
async def test_workbench_discovers_and_opens_an_available_bundle_from_trusted_scope(tmp_path: Path) -> None:
    lifecycle, _bundle_workbench, workbench, bundle_id = await _workbench(tmp_path)
    _write_contained_artifact(lifecycle, bundle_id, "request/profile.json", b'{"audience":"practitioner"}')

    discovery = await workbench.discover()
    view = await workbench.open(bundle_id)

    assert [entry.bundle_id for entry in discovery.entries] == [bundle_id]
    assert view.operation is not None
    assert view.operation.bundle_id == bundle_id
    assert view.operation.availability is BundleAvailability.AVAILABLE
    assert view.catalog.availability is WorkbenchAvailability.AVAILABLE
    assert view.catalog.entries[0].relative_path == "request/profile.json"
    assert str(tmp_path) not in view.model_dump_json()
    assert "session_ref" not in view.model_dump_json()
    assert "checkpoint" not in view.model_dump_json()


@pytest.mark.asyncio
async def test_ended_bundle_remains_inspectable_but_is_not_discovered_as_active(tmp_path: Path) -> None:
    lifecycle, _bundle_workbench, workbench, bundle_id = await _workbench(tmp_path)

    cancelled = await workbench.cancel(bundle_id)
    discovery = await workbench.discover()
    view = await workbench.status(bundle_id)

    assert cancelled.status is LifecycleStatus.CANCELLED
    assert discovery.entries == ()
    assert view.operation is not None
    assert view.operation.bundle_id == bundle_id
    assert view.operation.status is LifecycleStatus.CANCELLED
    assert view.operation.availability is BundleAvailability.AVAILABLE


@pytest.mark.asyncio
async def test_unknown_artifact_key_stops_before_lifecycle_or_filesystem_work(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _lifecycle, bundle_workbench, _workbench_view, _bundle_id = await _workbench(tmp_path)

    async def unexpected_available_bundle(_bundle_id: str) -> None:
        raise AssertionError("artifact key reached lifecycle authorization")

    monkeypatch.setattr(bundle_workbench, "_available_bundle", unexpected_available_bundle)

    view = await bundle_workbench.view_artifact(bundle_id="not-a-bundle", key="../../etc/passwd")

    assert view.availability is WorkbenchAvailability.UNAVAILABLE


@pytest.mark.asyncio
async def test_fixed_artifact_metadata_is_reauthorized_and_never_returns_a_body(tmp_path: Path) -> None:
    lifecycle, _bundle_workbench, workbench, bundle_id = await _workbench(tmp_path)
    content = b'{"audience":"practitioner"}'
    _write_contained_artifact(lifecycle, bundle_id, "request/profile.json", content)

    view = await workbench.view_artifact(bundle_id, ArtifactCatalogKey.REQUEST_PROFILE)

    assert view.availability is WorkbenchAvailability.AVAILABLE
    assert view.metadata is not None
    assert view.metadata.byte_size == len(content)
    assert view.metadata.relative_path == "request/profile.json"
    assert "audience" not in view.model_dump_json()
    assert "body" not in view.model_dump_json()


@pytest.mark.asyncio
async def test_symlink_or_broad_permission_artifact_is_unavailable_without_metadata(tmp_path: Path) -> None:
    lifecycle, _bundle_workbench, workbench, bundle_id = await _workbench(tmp_path)
    profile = _write_contained_artifact(lifecycle, bundle_id, "request/profile.json", b"safe")
    profile.chmod(0o644)

    broad = await workbench.view_artifact(bundle_id, ArtifactCatalogKey.REQUEST_PROFILE)
    profile.chmod(0o600)
    profile.unlink()
    external = tmp_path / "outside.json"
    external.write_text("outside")
    os.symlink(external, profile)
    linked = await workbench.view_artifact(bundle_id, ArtifactCatalogKey.REQUEST_PROFILE)

    assert broad.availability is WorkbenchAvailability.UNAVAILABLE
    assert broad.metadata is None
    assert linked.availability is WorkbenchAvailability.UNAVAILABLE
    assert linked.metadata is None


@pytest.mark.asyncio
async def test_foreign_or_deleted_bundle_reveals_no_operation_or_artifact_facts(tmp_path: Path) -> None:
    lifecycle, _bundle_workbench, workbench, bundle_id = await _workbench(tmp_path)
    _write_contained_artifact(lifecycle, bundle_id, "request/profile.json", b"safe")
    foreign = LocalBundleWorkbench(bundle_workbench=BundleWorkbench(lifecycle=lifecycle, scope=FOREIGN_SCOPE))

    foreign_view = await foreign.open(bundle_id)
    from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef
    from deerflow_deep_research.runtime.bundle_lifecycle import scope_bucket

    bundle = RunBundleRef(
        bundle_id=BundleId(bundle_id),
        scope_bucket=scope_bucket(effective_user_id=SCOPE[0], outer_thread_id=SCOPE[1]),
    )
    shutil.rmtree(lifecycle.private_root(bundle))
    lost_view = await workbench.open(bundle_id)
    lost_artifact = await workbench.view_artifact(bundle_id, ArtifactCatalogKey.REQUEST_PROFILE)

    assert foreign_view.operation is not None
    assert foreign_view.operation.availability is BundleAvailability.UNAVAILABLE
    assert foreign_view.operation.bundle_id is None
    assert lost_view.operation is not None
    assert lost_view.operation.availability is BundleAvailability.UNAVAILABLE
    assert lost_view.operation.bundle_id is None
    assert lost_artifact.availability is WorkbenchAvailability.UNAVAILABLE
    assert lost_artifact.metadata is None


@pytest.mark.asyncio
async def test_resume_revalidates_current_pending_request_without_a_session_broker(tmp_path: Path) -> None:
    lifecycle, _bundle_workbench, workbench, bundle_id = await _workbench(tmp_path)
    from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef
    from deerflow_deep_research.runtime.bundle_lifecycle import scope_bucket

    bundle = RunBundleRef(
        bundle_id=BundleId(bundle_id),
        scope_bucket=scope_bucket(effective_user_id=SCOPE[0], outer_thread_id=SCOPE[1]),
    )
    await lifecycle.set_pending_request(bundle=bundle, request_id="drh_pending")

    stale = await workbench.resume(bundle_id, expected_request_id="drh_stale", answer="not accepted")
    accepted = await workbench.resume(bundle_id, expected_request_id="drh_pending", answer="accepted")

    assert stale.code is ResultCode.RESPONSE_MISMATCH
    assert stale.request_id == "drh_pending"
    assert accepted.action is LifecycleAction.RESUME
    assert accepted.availability is BundleAvailability.AVAILABLE
    assert accepted.request_id is None


@pytest.mark.asyncio
async def test_timeline_remains_an_unavailable_observation_without_inference(tmp_path: Path) -> None:
    lifecycle, _bundle_workbench, workbench, bundle_id = await _workbench(tmp_path)
    _write_contained_artifact(lifecycle, bundle_id, "diagnostics/lifecycle.jsonl", b"not-a-trace")

    timeline = await workbench.timeline(bundle_id)

    assert timeline.availability is WorkbenchAvailability.UNAVAILABLE
    assert timeline.entries == ()
