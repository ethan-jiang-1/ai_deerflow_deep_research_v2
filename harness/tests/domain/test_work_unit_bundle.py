"""@impl RUI-009, WOU-009 — runtime-bound Bundle path contracts."""

from __future__ import annotations

import pytest

from deerflow_deep_research.domain.bundle import (
    BundleId,
    BundlePathKind,
    RunBundleRef,
    bundle_attempt_dir,
    bundle_evidence_ledger_path,
    bundle_evidence_lock_path,
    bundle_evidence_staging_path,
    bundle_first_work_spec_path,
    bundle_output_path,
    bundle_profile_path,
    bundle_ref_to_virtual,
    bundle_result_path,
    bundle_runtime_alias_probe_path,
    bundle_runtime_fs_probe_paths,
    bundle_work_spec_path,
    classify_bundle_path,
    is_audit_only,
    prelaunch_fs_probe_names,
    relative_to_workspace_path,
    resolve_bundle_contained_path,
    run_bundle_root,
)
from deerflow_deep_research.domain.profile import RequestBundleStoreProtocol, ResearchProfile
from deerflow_deep_research.domain.state import BundleLocalState, ContentRef

WORK_ID = "g0_wave0_w0000"
ATTEMPT_ID = f"{WORK_ID}_a00"
TOKEN = "a" * 32
BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)


def test_work_unit_paths_accept_only_a_runtime_bound_bundle_reference() -> None:
    """WOU-011: evidence stores cannot select a root through legacy arguments."""
    assert bundle_attempt_dir(BUNDLE, WORK_ID, ATTEMPT_ID).endswith(
        f"/{BUNDLE.bundle_id.value}/work/{WORK_ID}/{ATTEMPT_ID}"
    )
    with pytest.raises(TypeError):
        bundle_attempt_dir(BUNDLE, WORK_ID, ATTEMPT_ID, bundle_id=BUNDLE.bundle_id)  # type: ignore[call-arg]


def test_canonical_attempt_artifact_paths_are_exact() -> None:
    root = f"{run_bundle_root(BUNDLE)}/work/{WORK_ID}/{ATTEMPT_ID}"
    assert bundle_attempt_dir(BUNDLE, WORK_ID, ATTEMPT_ID) == root
    assert bundle_work_spec_path(BUNDLE, WORK_ID, ATTEMPT_ID) == f"{root}/work-spec.json"
    assert bundle_first_work_spec_path(BUNDLE, WORK_ID) == f"{root}/work-spec.json"
    assert bundle_result_path(BUNDLE, WORK_ID, ATTEMPT_ID) == f"{root}/result.json"
    assert bundle_output_path(BUNDLE, WORK_ID, ATTEMPT_ID, "claims/a.json") == f"{root}/outputs/claims/a.json"


def test_legacy_bundle_layout_is_not_a_valid_content_reference() -> None:
    old_ref = f"workspace/deep-research/b_{'A' * 43}/work/{WORK_ID}/{ATTEMPT_ID}/result.json"
    with pytest.raises(ValueError, match="bundle_ref"):
        bundle_ref_to_virtual(old_ref)


def test_ledger_lock_and_staging_paths_are_exact() -> None:
    evidence = f"{run_bundle_root(BUNDLE)}/evidence"
    assert bundle_evidence_ledger_path(BUNDLE) == f"{evidence}/submissions.jsonl"
    assert bundle_evidence_lock_path(BUNDLE) == f"{evidence}/.submissions.lock"
    assert bundle_evidence_staging_path(BUNDLE, TOKEN) == f"{evidence}/.submissions.{TOKEN}.tmp"
    with pytest.raises(ValueError, match="probe_token"):
        bundle_evidence_staging_path(BUNDLE, "A" * 32)


def test_runtime_and_prelaunch_probe_names_share_exact_tokens() -> None:
    diagnostics = f"{run_bundle_root(BUNDLE)}/diagnostics"
    assert bundle_runtime_alias_probe_path(BUNDLE, TOKEN) == f"{diagnostics}/.work-unit-probe-{TOKEN}"
    assert bundle_runtime_fs_probe_paths(BUNDLE, TOKEN) == (
        f"{diagnostics}/.work-unit-fsprobe-{TOKEN}.lock",
        f"{diagnostics}/.work-unit-fsprobe-{TOKEN}.src",
        f"{diagnostics}/.work-unit-fsprobe-{TOKEN}.dst",
    )
    assert prelaunch_fs_probe_names(TOKEN) == (
        f".deep-research-work-unit-fsprobe-{TOKEN}.lock",
        f".deep-research-work-unit-fsprobe-{TOKEN}.src",
        f".deep-research-work-unit-fsprobe-{TOKEN}.dst",
    )


def test_bundle_relative_virtual_and_workspace_relative_conversion() -> None:
    ref = bundle_result_path(BUNDLE, WORK_ID, ATTEMPT_ID)
    assert bundle_ref_to_virtual(ref) == f"/mnt/user-data/{ref}"
    assert relative_to_workspace_path(ref) == ref.removeprefix("workspace/")
    with pytest.raises(ValueError, match="bundle_ref"):
        bundle_ref_to_virtual("/tmp/host-secret")


@pytest.mark.parametrize(
    "bad",
    [
        "../result.json",
        "/result.json",
        "outputs/../result.json",
        "outputs//result.json",
        "outputs/./result.json",
        "outputs\\result.json",
    ],
)
def test_output_path_rejects_noncanonical_or_escaping_relative_paths(bad: str) -> None:
    with pytest.raises(ValueError, match="output"):
        bundle_output_path(BUNDLE, WORK_ID, ATTEMPT_ID, bad)


def test_work_attempt_identity_mismatch_is_rejected() -> None:
    with pytest.raises(ValueError, match="attempt_id"):
        bundle_attempt_dir(BUNDLE, WORK_ID, "g0_wave0_w0001_a00")
    with pytest.raises(ValueError, match="work_id"):
        bundle_attempt_dir(BUNDLE, "loose-work", ATTEMPT_ID)


def test_containment_rejects_absolute_host_and_cross_attempt_paths() -> None:
    allowed = bundle_result_path(BUNDLE, WORK_ID, ATTEMPT_ID)
    assert resolve_bundle_contained_path(allowed, bundle=BUNDLE, work_id=WORK_ID, attempt_id=ATTEMPT_ID) == allowed
    for path in ("/etc/passwd", bundle_evidence_ledger_path(BUNDLE)):
        with pytest.raises(ValueError, match="path_not_contained"):
            resolve_bundle_contained_path(path, bundle=BUNDLE, work_id=WORK_ID, attempt_id=ATTEMPT_ID)


def test_probe_paths_are_audit_only_and_never_authority() -> None:
    alias = bundle_runtime_alias_probe_path(BUNDLE, TOKEN)
    fs_lock, _, _ = bundle_runtime_fs_probe_paths(BUNDLE, TOKEN)
    assert is_audit_only(alias)
    assert is_audit_only(fs_lock)
    assert classify_bundle_path(alias) is BundlePathKind.AUDIT
    assert classify_bundle_path(bundle_evidence_ledger_path(BUNDLE)) is BundlePathKind.EVIDENCE
    assert classify_bundle_path(bundle_result_path(BUNDLE, WORK_ID, ATTEMPT_ID)) is BundlePathKind.CONTENT


def test_profile_path_is_request_scoped_content() -> None:
    path = bundle_profile_path(BUNDLE)
    assert path == f"{run_bundle_root(BUNDLE)}/request/profile.json"
    assert classify_bundle_path(path) is BundlePathKind.CONTENT
    assert resolve_bundle_contained_path(path, bundle=BUNDLE) == path


def test_request_bundle_store_protocol_is_pure_and_runtime_checkable() -> None:
    class Store:
        async def read_profile(self, _profile_ref: ContentRef) -> ResearchProfile:
            raise AssertionError("profile read is outside this protocol test")

        async def read_bundle_state(self) -> BundleLocalState:
            return BundleLocalState(bundle_id=BUNDLE.bundle_id)

        async def write_bundle_state(
            self,
            state: BundleLocalState,
            *,
            expected_revision: int,
        ) -> BundleLocalState:
            return state

        async def write_profile(self, profile: ResearchProfile) -> ContentRef:
            return ContentRef(sandbox_path=bundle_profile_path(BUNDLE), content_hash="h_" + "A" * 43)

    assert isinstance(Store(), RequestBundleStoreProtocol)
    assert "host" not in RequestBundleStoreProtocol.write_profile.__annotations__


@pytest.mark.parametrize("name", ["queue.json", "index.json", "status.json", "claims.queue"])
def test_dpt_control_files_are_not_registered_bundle_paths(name: str) -> None:
    path = f"{run_bundle_root(BUNDLE)}/work/{name}"
    assert classify_bundle_path(path) is BundlePathKind.UNKNOWN
