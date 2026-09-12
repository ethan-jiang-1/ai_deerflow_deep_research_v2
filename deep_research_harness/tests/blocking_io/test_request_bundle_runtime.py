"""Event-loop blocking guard for canonical request-profile reads.

@impl TOP-004
@impl TOP-008
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from types import SimpleNamespace

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, bundle_host_relative_root
from deerflow_deep_research.domain.profile import ResearchProfile, SupportedLanguage
from deerflow_deep_research.domain.state import BundleLocalState
from deerflow_deep_research.runtime import request_bundle as request_bundle_module
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.request_bundle import RequestBundleStore
from deerflow_deep_research.runtime.work_unit_storage_probe import WorkUnitStorageCheck

BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)


async def _ready(*_args: object, **_kwargs: object) -> WorkUnitStorageCheck:
    return WorkUnitStorageCheck("ready", "local_thread_mount")


def _profile() -> ResearchProfile:
    return ResearchProfile(
        depth="standard",
        audience="practitioner",
        format="detailed_report",
        cost_tolerance="moderate",
        time_budget="standard",
        must_answer=("Q1",),
        scope_boundaries="Grid scale only.",
        custom_notes="Prefer recent sources.",
        output_language=SupportedLanguage.EN,
    )


async def _store(workspace: Path) -> RequestBundleStore:
    BundleLifecycle(workspace_host_path=workspace)._publish_sync(
        BUNDLE, BundleLocalState(bundle_id=BUNDLE.bundle_id, implementation_mode="all_real")
    )
    envelope = SimpleNamespace(workspace_host_path=workspace, parent_sandbox=object(), app_config=object())
    return await RequestBundleStore.create(envelope, bundle=BUNDLE, storage_verifier=_ready)


async def test_read_profile_filesystem_work_does_not_block_event_loop(
    monkeypatch,
    tmp_path: Path,
) -> None:
    store = await _store(tmp_path)
    profile = _profile()
    profile_ref = await store.write_profile(profile)
    original_read = request_bundle_module.os.read

    def slow_read(fd: int, count: int) -> bytes:
        time.sleep(0.1)
        return original_read(fd, count)

    monkeypatch.setattr(request_bundle_module.os, "read", slow_read)
    ticks = 0

    async def heartbeat() -> None:
        nonlocal ticks
        for _ in range(10):
            await asyncio.sleep(0.01)
            ticks += 1

    loaded, _ = await asyncio.gather(store.read_profile(profile_ref), heartbeat())

    assert loaded == profile
    assert ticks == 10
    assert (tmp_path / bundle_host_relative_root(BUNDLE) / "request" / "profile.json").is_file()
