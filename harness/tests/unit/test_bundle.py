"""Pure change-02 bundle layout, path containment, and authority boundary.

@impl REG-009
@impl REG-010
@impl REG-016
"""

from __future__ import annotations

import pytest

from deerflow_deep_research.domain.bundle import (
    BUNDLE_ROOT,
    BUNDLE_SUBTREES,
    DIAGNOSTICS_GATE_ATTEMPTS,
    BundleId,
    RunBundleRef,
    bundle_attempt_dir,
    bundle_diagnostics_path,
    canonicalize_source_url,
    dedupe_source_urls,
    is_audit_only,
    new_bundle_id,
    resolve_bundle_contained_path,
    run_bundle_root,
)
from deerflow_deep_research.domain.state import ResearchState

WORK_ID = "g0_wave0_w0000"
ATTEMPT_ID = f"{WORK_ID}_a00"
BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)


def test_bundle_root_is_runtime_bound_and_scope_contained() -> None:
    assert run_bundle_root(BUNDLE) == f"{BUNDLE_ROOT}/scopes/{BUNDLE.scope_bucket}/{BUNDLE.bundle_id.value}"


def test_fresh_bundle_id_is_opaque_and_not_derived_from_a_conversation() -> None:
    """DRH-001: identity allocation is independent of trusted scope inputs."""
    first = new_bundle_id()
    second = new_bundle_id()

    assert isinstance(first, BundleId)
    assert isinstance(second, BundleId)
    assert first != second
    assert BUNDLE.bundle_id.value not in {first.value, second.value}
    assert "thread-1" not in {first.value, second.value}
    with pytest.raises(ValueError, match="bundle_id_invalid"):
        BundleId("r_" + "A" * 43)


def test_runtime_bound_bundle_reference_is_the_only_path_identity() -> None:
    """DRH-001/WOU-011: content consumers receive a selected Bundle, not a locator pair."""
    bundle = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)

    assert bundle.bundle_id.value == "b_" + "A" * 43
    assert set(bundle.__dataclass_fields__) == {"bundle_id", "scope_bucket"}


def test_bundle_declares_minimal_subtrees() -> None:
    assert set(BUNDLE_SUBTREES) == {
        "request",
        "work",
        "evidence",
        "synthesis",
        "review",
        "final",
        "diagnostics",
    }


def test_attempt_dir_scopes_a_worker_write_root() -> None:
    assert bundle_attempt_dir(BUNDLE, WORK_ID, ATTEMPT_ID) == f"{run_bundle_root(BUNDLE)}/work/{WORK_ID}/{ATTEMPT_ID}"


def test_in_containment_write_is_accepted() -> None:
    path = f"{run_bundle_root(BUNDLE)}/work/{WORK_ID}/{ATTEMPT_ID}/outputs/page.html"
    assert resolve_bundle_contained_path(path, bundle=BUNDLE, work_id=WORK_ID, attempt_id=ATTEMPT_ID) == path


def test_out_of_attempt_write_is_rejected() -> None:
    # A worker cannot write into another work/attempt directory.
    path = f"{run_bundle_root(BUNDLE)}/work/g0_wave0_w0001/g0_wave0_w0001_a00/outputs/page.html"
    with pytest.raises(ValueError, match="path_not_contained"):
        resolve_bundle_contained_path(path, bundle=BUNDLE, work_id=WORK_ID, attempt_id=ATTEMPT_ID)


def test_parent_traversal_escape_is_rejected() -> None:
    path = f"{run_bundle_root(BUNDLE)}/work/{WORK_ID}/{ATTEMPT_ID}/../../g0_wave0_w0001/x"
    with pytest.raises(ValueError, match="path_not_contained"):
        resolve_bundle_contained_path(path, bundle=BUNDLE, work_id=WORK_ID, attempt_id=ATTEMPT_ID)


def test_absolute_path_is_rejected() -> None:
    with pytest.raises(ValueError, match="path_not_contained"):
        resolve_bundle_contained_path("/etc/passwd", bundle=BUNDLE, work_id=WORK_ID, attempt_id=ATTEMPT_ID)


def test_diagnostics_path_is_audit_only() -> None:
    path = bundle_diagnostics_path(BUNDLE)
    assert path.endswith(f"diagnostics/{DIAGNOSTICS_GATE_ATTEMPTS}")
    assert is_audit_only(path)


def test_unknown_diagnostic_is_rejected() -> None:
    with pytest.raises(ValueError, match="diagnostic_unknown"):
        bundle_diagnostics_path(BUNDLE, "phase_cursor.json")


def test_canonical_source_url_dedupes_trivial_variants() -> None:
    assert canonicalize_source_url("HTTPS://Example.com/a/") == "https://example.com/a"
    assert canonicalize_source_url("https://example.com/a#frag") == "https://example.com/a"


def test_dedupe_source_urls_collapses_duplicates() -> None:
    deduped = dedupe_source_urls(["https://example.com/a/", "https://example.com/a#x", "https://example.com/b"])
    assert deduped == ("https://example.com/a", "https://example.com/b")


def test_accepted_submission_refs_is_a_ledger_ref_slot() -> None:
    # REG-009: accepted_submission_refs holds references into the validated submission
    # ledger (strings), not ledger records, file paths, or worker text. It is the only
    # slot that marks accepted submissions.
    hints = ResearchState.__annotations__
    assert "accepted_submission_refs" in hints
    # No field treats file existence or worker text as accepted coverage.
    assert "accepted_files" not in hints
    assert "worker_text_accepted" not in hints


def test_no_second_phase_cursor_field_exists() -> None:
    hints = ResearchState.__annotations__
    assert "phase_cursor" not in hints
    assert "rb_status" not in hints
    # diagnostics is not a state field; it lives only in the sandbox bundle as audit-only.
    assert "diagnostics" not in hints
