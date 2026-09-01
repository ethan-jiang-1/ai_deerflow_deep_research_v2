"""OperatorWorkspaceReader bounded-read contract.

@impl LDO-007
"""

from __future__ import annotations

from pathlib import Path

from deerflow_deep_research.domain.workspace import (
    FilePreview,
    WorkspaceDenial,
    WorkspacePage,
    WorkspacePolicyLabel,
)
from deerflow_deep_research.runtime.workspace_reader import OperatorWorkspaceReader

BUNDLE_HOST = "b_" + "A" * 43


def _reader(tmp_path: Path, **kwargs: object) -> OperatorWorkspaceReader:
    workspace = tmp_path / "workspace"
    (workspace / "evidence").mkdir(parents=True)
    (workspace / "evidence" / "source_001.md").write_text("source one", encoding="utf-8")
    (workspace / "evidence" / "data.bin").write_bytes(b"\x00\x01\x02\x03")
    (workspace / "report.md").write_text("# Report\n" + "x" * 40, encoding="utf-8")
    private = tmp_path / "private"
    private.mkdir()
    (private / "state.json").write_text('{"secret": true}', encoding="utf-8")
    roots = {
        "workspace": {
            "path": workspace,
            "label": WorkspacePolicyLabel.MODEL_READ,
            "readable": True,
            "writable": False,
        },
        "bundle": {
            "path": tmp_path / "bundle",
            "label": WorkspacePolicyLabel.OPERATOR_ONLY,
            "readable": True,
            "writable": False,
        },
        "restricted": {
            "path": private,
            "label": WorkspacePolicyLabel.RESTRICTED,
            "readable": False,
            "writable": False,
        },
    }
    return OperatorWorkspaceReader(roots=roots, **kwargs)  # type: ignore[arg-type]


def test_list_roots_enumerates_mounts_with_labels_without_host_paths(tmp_path: Path) -> None:
    reader = _reader(tmp_path)
    roots = reader.list_roots()

    assert [root.alias for root in roots] == ["bundle", "restricted", "workspace"]
    labels = {root.alias: root.policy_label for root in roots}
    assert labels["workspace"] is WorkspacePolicyLabel.MODEL_READ
    assert labels["bundle"] is WorkspacePolicyLabel.OPERATOR_ONLY
    assert labels["restricted"] is WorkspacePolicyLabel.RESTRICTED
    assert all(str(tmp_path) not in str(root) for root in roots)


def test_list_and_preview_happy_path_are_relative_and_labeled(tmp_path: Path) -> None:
    reader = _reader(tmp_path)

    page = reader.list("workspace", "evidence")
    assert isinstance(page, WorkspacePage)
    assert page.root_alias == "workspace"
    assert [entry.relative_path for entry in page.entries] == ["evidence/data.bin", "evidence/source_001.md"]
    assert all(entry.policy_label is WorkspacePolicyLabel.MODEL_READ for entry in page.entries)

    preview = reader.preview("workspace", "evidence/source_001.md")
    assert isinstance(preview, FilePreview)
    assert preview.content == "source one"
    assert preview.time_posture == "CURRENT"
    assert preview.content_hash
    assert preview.hash_verified is True
    assert str(tmp_path) not in str(preview)


def test_absolute_and_escape_paths_are_typed_denied(tmp_path: Path) -> None:
    reader = _reader(tmp_path)

    for bad in ("/etc/passwd", "../private/state.json", "evidence/../../../private/state.json"):
        denial = reader.preview("workspace", bad)
        assert isinstance(denial, WorkspaceDenial), bad
        assert denial.reason in {"path_escape", "absolute_path"}
        listing = reader.list("workspace", bad)
        assert isinstance(listing, WorkspaceDenial), bad

    link = tmp_path / "workspace" / "evidence" / "escape.lnk"
    link.symlink_to(tmp_path / "private" / "state.json")
    denial = reader.preview("workspace", "evidence/escape.lnk")
    assert isinstance(denial, WorkspaceDenial)
    assert denial.reason == "path_escape"


def test_unknown_root_not_found_and_oversize_are_typed_denials(tmp_path: Path) -> None:
    reader = _reader(tmp_path)

    assert reader.list("unknown-root", ".").reason == "unknown_root"  # type: ignore[union-attr]
    assert reader.preview("workspace", "evidence/missing.md").reason == "not_found"  # type: ignore[union-attr]

    big = tmp_path / "workspace" / "big.txt"
    big.write_text("y" * 200_000, encoding="utf-8")
    denial = reader.preview("workspace", "big.txt")
    assert isinstance(denial, WorkspaceDenial)
    assert denial.reason == "oversize"


def test_binary_and_restricted_roots_are_denied_without_leakage(tmp_path: Path) -> None:
    reader = _reader(tmp_path)

    binary = reader.preview("workspace", "evidence/data.bin")
    assert isinstance(binary, WorkspaceDenial)
    assert binary.reason == "unsupported_binary"

    restricted_listing = reader.list("restricted", ".")
    assert isinstance(restricted_listing, WorkspaceDenial)
    assert restricted_listing.reason == "private_scope"
    restricted_preview = reader.preview("restricted", "state.json")
    assert isinstance(restricted_preview, WorkspaceDenial)

    for model in (binary, restricted_listing, restricted_preview):
        assert "secret" not in str(model)
        assert str(tmp_path / "private") not in str(model)


def test_foreign_root_content_is_unreachable_through_another_alias(tmp_path: Path) -> None:
    reader = _reader(tmp_path)

    denial = reader.preview("bundle", "../workspace/report.md")
    assert isinstance(denial, WorkspaceDenial)
    assert denial.reason in {"path_escape", "absolute_path"}


def test_hash_detects_post_preview_modification(tmp_path: Path) -> None:
    reader = _reader(tmp_path, verify_hash=True)

    preview = reader.preview("workspace", "report.md")
    assert isinstance(preview, FilePreview)
    assert preview.hash_verified is True
