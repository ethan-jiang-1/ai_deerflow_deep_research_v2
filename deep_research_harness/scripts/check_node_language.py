#!/usr/bin/env python3
"""Reject retired external workflow labels from every tracked text surface.

The scanner consumes Git-index modes rather than a path or suffix allowlist. Ordinary
files and symbolic-link values are text surfaces; a Gitlink is a metadata pointer and
is reported without reading its worktree.

@impl DRC-013
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

GITLINK_MODE = b"160000"
ORDINARY_FILE_MODES = frozenset({b"100644", b"100755"})
SYMLINK_MODE = b"120000"
RETIRED_PATTERNS = (
    re.compile(b"phase" + rb"(?:[ _-]?agent)", flags=re.IGNORECASE),
    re.compile(b"md" + rb"(?:[ _-]?controller)", flags=re.IGNORECASE),
    re.compile(b"capability" + rb"(?:[ _-]?binding)", flags=re.IGNORECASE),
    re.compile(rb"(?<![A-Za-z0-9])" + b"d" + b"pt" + rb"(?![A-Za-z0-9])", flags=re.IGNORECASE),
)


class NodeLanguageError(ValueError):
    """A tracked working-tree entry cannot satisfy the vocabulary contract."""


@dataclass(frozen=True)
class NodeLanguageScan:
    """The checked materialized text entries and metadata-only Gitlinks."""

    checked_paths: tuple[str, ...]
    gitlink_paths: tuple[str, ...]


def _git_index_entries(root: Path) -> tuple[tuple[bytes, bytes], ...]:
    result = subprocess.run(
        ["git", "ls-files", "--stage", "-z"],
        cwd=root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise NodeLanguageError(f"language.git_index_unavailable:{detail or root}")

    entries: list[tuple[bytes, bytes]] = []
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        metadata, separator, path = record.partition(b"\t")
        fields = metadata.split()
        if not separator or len(fields) != 3 or not path:
            raise NodeLanguageError("language.git_index_record_invalid")
        mode, _object_id, stage = fields
        if stage != b"0":
            raise NodeLanguageError(f"language.git_index_stage_invalid:{os.fsdecode(path)}")
        entries.append((mode, path))
    return tuple(entries)


def _entry_bytes(root: Path, mode: bytes, path_bytes: bytes) -> bytes:
    relative_path = os.fsdecode(path_bytes)
    path = root / relative_path
    if mode in ORDINARY_FILE_MODES:
        if not path.is_file() or path.is_symlink():
            raise NodeLanguageError(f"language.materialized_file_invalid:{relative_path}")
        try:
            return path.read_bytes()
        except OSError as exc:
            raise NodeLanguageError(f"language.materialized_file_unreadable:{relative_path}:{exc}") from exc
    if mode == SYMLINK_MODE:
        if not path.is_symlink():
            raise NodeLanguageError(f"language.materialized_symlink_invalid:{relative_path}")
        try:
            return os.fsencode(os.readlink(path))
        except OSError as exc:
            raise NodeLanguageError(f"language.materialized_symlink_unreadable:{relative_path}:{exc}") from exc
    decoded_mode = mode.decode("ascii", errors="replace")
    raise NodeLanguageError(f"language.tracked_mode_unsupported:{decoded_mode}:{relative_path}")


def scan_tracked_language(root: Path) -> NodeLanguageScan:
    """Scan every materialized tracked text entry and return Gitlink metadata paths."""

    checked_paths: list[str] = []
    gitlink_paths: list[str] = []
    violations: list[str] = []
    for mode, path_bytes in _git_index_entries(root):
        relative_path = os.fsdecode(path_bytes)
        if mode == GITLINK_MODE:
            gitlink_paths.append(relative_path)
            continue
        payload = _entry_bytes(root, mode, path_bytes)
        if any(pattern.search(payload) for pattern in RETIRED_PATTERNS):
            violations.append(relative_path)
        checked_paths.append(relative_path)

    if violations:
        raise NodeLanguageError(f"language.retired_label:{','.join(sorted(violations))}")
    return NodeLanguageScan(tuple(sorted(checked_paths)), tuple(sorted(gitlink_paths)))


def main() -> int:
    try:
        report = scan_tracked_language(Path(__file__).resolve().parents[2])
    except NodeLanguageError as exc:
        print(f"node-language check failed: {exc}")
        return 1
    print(
        "node-language check passed: "
        f"{len(report.checked_paths)} materialized entries, {len(report.gitlink_paths)} Gitlink metadata entries"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
