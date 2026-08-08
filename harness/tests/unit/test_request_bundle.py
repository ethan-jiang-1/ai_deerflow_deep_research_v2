"""Runtime-owned request-bundle profile writer.

@impl HIN-004
@impl REG-010
"""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from deerflow_deep_research.domain.bundle import (
    BundleId,
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
from deerflow_deep_research.runtime import request_bundle as request_bundle_module
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycleError
from deerflow_deep_research.runtime.request_bundle import MAX_PROFILE_BYTES, RequestBundleStore
from deerflow_deep_research.runtime.work_unit_storage import WorkUnitStorageCheck, WorkUnitStoreError

BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)
BUNDLE_ID = BUNDLE.bundle_id.value


async def _ready(*_args: object, **_kwargs: object) -> WorkUnitStorageCheck:
    return WorkUnitStorageCheck("ready", "local_thread_mount")


def _envelope(workspace: Path) -> SimpleNamespace:
    return SimpleNamespace(workspace_host_path=workspace, parent_sandbox=object(), app_config=object())


async def _store(workspace: Path, **hooks: object) -> RequestBundleStore:
    await _published_bundle(workspace)
    return await RequestBundleStore.create(
        _envelope(workspace),
        bundle=BUNDLE,
        storage_verifier=_ready,
        **hooks,  # type: ignore[arg-type]
    )


def _profile(**overrides: object) -> ResearchProfile:
    payload: dict[str, object] = {
        "depth": "standard",
        "audience": "practitioner",
        "format": "detailed_report",
        "cost_tolerance": "moderate",
        "time_budget": "standard",
        "must_answer": ("Q1",),
        "scope_boundaries": "Grid scale only.",
        "custom_notes": "Prefer recent sources.",
    }
    payload.update(overrides)
    return ResearchProfile(**payload)


async def _published_bundle(workspace: Path) -> None:
    from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle

    root = workspace / bundle_host_relative_root(BUNDLE)
    if not root.exists():
        BundleLifecycle(workspace_host_path=workspace)._publish_sync(BUNDLE)


def _profile_file(workspace: Path, bundle: RunBundleRef = BUNDLE) -> Path:
    return workspace / bundle_host_relative_root(bundle) / "request" / "profile.json"


async def test_write_profile_publishes_canonical_json_and_content_ref(tmp_path: Path) -> None:
    store = await _store(tmp_path)
    profile = _profile(depth="deep_dive", audience="domain_expert")
    ref = await store.write_profile(profile)

    path = _profile_file(tmp_path)
    assert path.read_bytes() == canonical_profile_bytes(profile)
    assert path.stat().st_mode & 0o777 == 0o600
    assert ref.sandbox_path == bundle_profile_path(BUNDLE)
    assert ref.content_hash == compute_profile_content_hash(profile)
    assert ref.schema_version == 1
    assert "deep_dive" in ref.short_summary
    assert str(tmp_path) not in str(ref)


async def test_write_profile_retains_v2_comparison_and_language_facts_on_reload(tmp_path: Path) -> None:
    store = await _store(tmp_path)
    profile = _profile(
        schema_version=2,
        comparison_required=True,
        comparison_subjects=("lithium-ion batteries", "vanadium redox flow batteries"),
        request_language="en",
        output_language="zh",
    )

    await store.write_profile(profile)
    reloaded = ResearchProfile.model_validate(json.loads(_profile_file(tmp_path).read_text(encoding="utf-8")))

    assert reloaded.schema_version == 2
    assert reloaded.comparison_subjects is not None
    assert reloaded.comparison_subjects.subjects == ("lithium-ion batteries", "vanadium redox flow batteries")
    assert reloaded.request_language == "en"
    assert reloaded.output_language == "zh"


async def test_read_profile_returns_the_selected_canonical_profile_with_scope_and_notes(tmp_path: Path) -> None:
    store = await _store(tmp_path)
    profile = _profile(
        scope_boundaries="Only grid-scale storage; exclude household batteries.",
        custom_notes="Prioritize evidence published after 2024.",
    )
    profile_ref = await store.write_profile(profile)

    loaded = await store.read_profile(profile_ref)

    assert loaded == profile
    assert loaded.scope_boundaries == "Only grid-scale storage; exclude household batteries."
    assert loaded.custom_notes == "Prioritize evidence published after 2024."


async def test_read_profile_refuses_a_cross_bundle_or_wrong_schema_reference(tmp_path: Path) -> None:
    store = await _store(tmp_path)
    profile_ref = await store.write_profile(_profile())
    other_bundle = RunBundleRef(bundle_id=BundleId("b_" + "C" * 43), scope_bucket=BUNDLE.scope_bucket)

    with pytest.raises(ValueError, match="profile_ref_path_invalid"):
        await store.read_profile(replace(profile_ref, sandbox_path=bundle_profile_path(other_bundle)))
    with pytest.raises(ValueError, match="profile_ref_schema_version_invalid"):
        await store.read_profile(replace(profile_ref, schema_version=2))


async def test_read_profile_refuses_a_missing_tampered_or_oversized_canonical_artifact(tmp_path: Path) -> None:
    store = await _store(tmp_path)
    profile = _profile()
    profile_ref = await store.write_profile(profile)
    profile_file = _profile_file(tmp_path)

    profile_file.unlink()
    with pytest.raises(FileNotFoundError, match="profile_missing"):
        await store.read_profile(profile_ref)

    await store.write_profile(profile)
    profile_file.write_bytes(canonical_profile_bytes(_profile(custom_notes="A different durable note.")))
    with pytest.raises(ValueError, match="profile_content_hash_mismatch"):
        await store.read_profile(profile_ref)

    profile_file.write_bytes(b"x" * (MAX_PROFILE_BYTES + 1))
    with pytest.raises(ValueError, match="profile_too_large"):
        await store.read_profile(profile_ref)


async def test_read_profile_refuses_a_symlink_or_schema_invalid_artifact_without_leaking_contents(
    tmp_path: Path,
) -> None:
    store = await _store(tmp_path)
    profile_ref = await store.write_profile(_profile())
    profile_file = _profile_file(tmp_path)
    outside = tmp_path / "outside-secret"
    outside.write_text('{"custom_notes":"secret"}', encoding="utf-8")
    profile_file.unlink()
    profile_file.symlink_to(outside)

    with pytest.raises(WorkUnitStoreError) as excinfo:
        await store.read_profile(profile_ref)
    assert excinfo.value.reason is WorkUnitStorageReason.POSIX_PRIMITIVES_UNAVAILABLE
    assert "secret" not in str(excinfo.value)

    profile_file.unlink()
    profile_file.write_text('{"schema_version":99}', encoding="utf-8")
    os.chmod(profile_file, 0o600)
    with pytest.raises(ValueError, match="profile_schema_invalid"):
        await store.read_profile(profile_ref)


async def test_write_profile_uses_asyncio_to_thread(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[str] = []

    async def fake_to_thread(func, *args, **kwargs):  # type: ignore[no-untyped-def]
        calls.append(func.__name__)
        return func(*args, **kwargs)

    monkeypatch.setattr(request_bundle_module.asyncio, "to_thread", fake_to_thread)
    store = await _store(tmp_path)
    calls.clear()
    await store.write_profile(_profile())
    assert calls == ["_read_sync", "_write_profile_sync", "_read_sync"]


async def test_fault_cleans_same_directory_staging(tmp_path: Path) -> None:
    def fault(point: str) -> None:
        if point == "after_staging_fsync":
            raise RuntimeError("boom")

    store = await _store(tmp_path, fault_hook=fault, token_factory=lambda: "a" * 32)
    with pytest.raises(RuntimeError, match="boom"):
        await store.write_profile(_profile())

    request_dir = _profile_file(tmp_path).parent
    assert request_dir.is_dir()
    assert not _profile_file(tmp_path).exists()
    assert not tuple(request_dir.glob(".profile.*.tmp"))


async def test_bundle_loss_during_profile_write_returns_unavailable_without_recreating_the_bundle(
    tmp_path: Path,
) -> None:
    """HIN-004: a lost selected Bundle cannot be recreated by content publication."""

    root = tmp_path / bundle_host_relative_root(BUNDLE)

    def delete_bundle(point: str) -> None:
        if point == "after_staging_fsync":
            shutil.rmtree(root)

    store = await _store(tmp_path, fault_hook=delete_bundle)
    with pytest.raises(BundleLifecycleError, match="bundle_unavailable"):
        await store.write_profile(_profile())

    assert not root.exists()


async def test_existing_symlink_or_cross_research_path_fails_without_host_path_leak(tmp_path: Path) -> None:
    await _published_bundle(tmp_path)
    profile_file = _profile_file(tmp_path)
    outside = tmp_path / "outside-secret"
    outside.write_bytes(b"secret")
    profile_file.symlink_to(outside)
    store = await _store(tmp_path)
    with pytest.raises(WorkUnitStoreError) as excinfo:
        await store.write_profile(_profile())
    assert excinfo.value.reason is WorkUnitStorageReason.POSIX_PRIMITIVES_UNAVAILABLE
    assert str(tmp_path) not in str(excinfo.value)
    assert outside.read_bytes() == b"secret"

    other_bundle = RunBundleRef(bundle_id=BundleId("b_" + "B" * 43), scope_bucket=BUNDLE.scope_bucket)
    other_file = _profile_file(tmp_path, other_bundle)
    assert not other_file.exists()


async def test_store_create_rejects_unverified_workspace_before_write(tmp_path: Path) -> None:
    async def unavailable(*_args: object, **_kwargs: object) -> WorkUnitStorageCheck:
        return WorkUnitStorageCheck("not_ready", "workspace_alias_mismatch")

    with pytest.raises(WorkUnitStoreError) as excinfo:
        await RequestBundleStore.create(
            _envelope(tmp_path),
            bundle=BUNDLE,
            storage_verifier=unavailable,
        )
    assert excinfo.value.reason is WorkUnitStorageReason.WORKSPACE_ALIAS_MISMATCH
    assert not await request_bundle_module.asyncio.to_thread(os.listdir, tmp_path)


def test_store_rejects_a_missing_runtime_bundle_reference(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="bundle_required"):
        RequestBundleStore(workspace_host_path=tmp_path, bundle="../escape")  # type: ignore[arg-type]


def test_profile_path_can_be_derived_from_only_a_selected_runtime_bundle_reference() -> None:
    """DRH-001: initial content has one selected Bundle identity."""
    bundle = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)

    assert bundle_profile_path(bundle) == (
        f"workspace/deep-research/scopes/{bundle.scope_bucket}/{bundle.bundle_id.value}/request/profile.json"
    )
    assert set(bundle.__dataclass_fields__) == {"bundle_id", "scope_bucket"}
    assert "bundle_directory" not in bundle.__dataclass_fields__


def test_request_store_accepts_only_a_preselected_bundle_reference(tmp_path: Path) -> None:
    """HIN-015: profile writes cannot override a selected Bundle."""
    bundle = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)

    store = RequestBundleStore(workspace_host_path=tmp_path, bundle=bundle)
    assert store.bundle == bundle
    with pytest.raises(TypeError):
        RequestBundleStore(workspace_host_path=tmp_path, bundle=bundle, bundle_id=BUNDLE_ID)  # type: ignore[call-arg]
