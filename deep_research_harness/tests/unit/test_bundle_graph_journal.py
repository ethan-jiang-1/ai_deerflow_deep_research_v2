"""BundleGraph-to-Journal provenance handoff tests.

@impl REJ-006
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from deerflow_deep_research.domain.run_observation import ExecutionProfileEvidence, ObservationInspectability
from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.run_observation import RunObservationStore
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope


def _envelope(tmp_path: Path, *, execution_profile: ExecutionProfileEvidence | None) -> TrustedRuntimeEnvelope:
    return TrustedRuntimeEnvelope(
        effective_user_id="journal-user",
        outer_thread_id="journal-thread",
        outer_run_id="journal-run",
        app_config=object(),
        workspace_host_path=tmp_path,
        uploads_host_path=tmp_path / "uploads",
        outputs_host_path=tmp_path / "outputs",
        workspace_virtual_root="/mnt/user-data/workspace",
        uploads_virtual_root="/mnt/user-data/uploads",
        outputs_virtual_root="/mnt/user-data/outputs",
        parent_sandbox=None,
        progress=None,
        execution_profile=execution_profile,
    )


@pytest.mark.asyncio
async def test_journal_envelope_retains_profile_only_after_lifecycle_admission(tmp_path: Path) -> None:
    """The trusted profile crosses only the admitted Bundle's recorder boundary."""

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(
        scope=("journal-user", "journal-thread"),
        request_text="Research journals",
        implementation_mode="all_real",
    )
    state = await lifecycle.read_state(bundle)
    profile = ExecutionProfileEvidence(profile_id="deepseek-v4-flash", registry_revision="v1")

    journal_envelope = await BundleGraphExecutor._journal_envelope(
        lifecycle=lifecycle,
        bundle=bundle,
        state=state,
        envelope=_envelope(tmp_path, execution_profile=profile),
    )

    assert journal_envelope.execution_profile == profile
    assert journal_envelope.event_recorder_factory is not None
    assert journal_envelope.event_recorder_factory(bundle.bundle_id.value) is not None
    assert journal_envelope.event_recorder_factory("b_" + "B" * 43) is None
    inspection = await RunObservationStore(
        bundle_root=lifecycle.private_root(bundle),
        bundle_id=bundle.bundle_id.value,
    ).inspect(bundle_id=bundle.bundle_id.value)
    assert inspection.inspectability is ObservationInspectability.AVAILABLE
    assert inspection.summary is not None
    assert inspection.summary.execution_profile == profile
    assert inspection.events[0].execution_profile == profile
    assert not hasattr(state, "execution_profile")


@pytest.mark.asyncio
async def test_rejected_start_creates_no_bundle_or_profile_journal(tmp_path: Path) -> None:
    """A pre-admission start rejection has no selected Bundle to observe."""

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    profile = ExecutionProfileEvidence(profile_id="deepseek-v4-flash", registry_revision="v1")
    _envelope(tmp_path, execution_profile=profile)

    with pytest.raises(ValueError, match="start_request_invalid"):
        await lifecycle.start(scope=("journal-user", "journal-thread"), request_text="", implementation_mode="all_real")

    assert await lifecycle.discover_active(scope=("journal-user", "journal-thread")) is None
    journal_manifests = await asyncio.to_thread(lambda: tuple(tmp_path.rglob("journal-manifest.json")))
    assert not journal_manifests
