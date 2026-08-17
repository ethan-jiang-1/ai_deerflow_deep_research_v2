#!/usr/bin/env python3
"""Verify a digest-bound portable Change Guidance candidate.

@impl PCG-005
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

CORE_ROOT = PurePosixPath("openspec/change-guidance/core")
PROFILES_ROOT = PurePosixPath("openspec/change-guidance/profiles")
KERNEL_PATH = PurePosixPath("openspec/governance/change_guidance_kernel.py")
DENYLIST_PARTS = frozenset(
    {"local", "product", "config.yaml", "specs", "changes", "archive", "tests", "evidence"}
)
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\((?P<target>[^)]+)\)")


class CandidateViolation(ValueError):
    pass


def _portable_paths(root: Path, selected_profiles: tuple[str, ...]) -> tuple[PurePosixPath, ...]:
    paths = [
        PurePosixPath(path.relative_to(root).as_posix())
        for path in sorted((root / CORE_ROOT).rglob("*"))
        if path.is_file()
    ]
    for profile in selected_profiles:
        profile_root = root / PROFILES_ROOT / profile
        if not profile_root.is_dir():
            raise CandidateViolation(f"selected profile is missing: {profile}")
        paths.extend(
            PurePosixPath(path.relative_to(root).as_posix())
            for path in sorted(profile_root.rglob("*"))
            if path.is_file()
        )
    paths.append(KERNEL_PATH)
    return tuple(sorted(paths))


def _validate_allowlist_path(path: PurePosixPath, selected_profiles: tuple[str, ...]) -> None:
    if path == KERNEL_PATH or path.is_relative_to(CORE_ROOT):
        return
    if any(path.is_relative_to(PROFILES_ROOT / profile) for profile in selected_profiles):
        return
    raise CandidateViolation(f"denylisted or non-allowlisted candidate path: {path}")


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest(
    root: Path,
    *,
    source_repository: str,
    source_revision: str,
    snapshot_date: str,
    selected_profiles: tuple[str, ...],
) -> dict[str, Any]:
    if len(selected_profiles) != len(set(selected_profiles)):
        raise CandidateViolation("selected profiles must be unique")
    paths = _portable_paths(root, selected_profiles)
    return {
        "status": "portable snapshot",
        "sourceRepository": source_repository,
        "sourceRevision": source_revision,
        "snapshotDate": snapshot_date,
        "selectedProfiles": list(selected_profiles),
        "files": [{"path": str(path), "sha256": _digest(root / path)} for path in paths],
    }


def verify_manifest(root: Path, manifest: dict[str, Any]) -> None:
    if manifest.get("status") != "portable snapshot":
        raise CandidateViolation("manifest status must be 'portable snapshot'")
    profiles_value = manifest.get("selectedProfiles")
    if not isinstance(profiles_value, list) or any(not isinstance(item, str) for item in profiles_value):
        raise CandidateViolation("selectedProfiles must be a string list")
    selected_profiles = tuple(profiles_value)
    expected_paths = _portable_paths(root, selected_profiles)
    files = manifest.get("files")
    if not isinstance(files, list):
        raise CandidateViolation("files must be a list")
    entries: dict[PurePosixPath, str] = {}
    for entry in files:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise CandidateViolation("each file entry needs a relative path")
        path = PurePosixPath(entry["path"])
        if path.is_absolute() or ".." in path.parts or path in entries:
            raise CandidateViolation(f"invalid or duplicate candidate path: {path}")
        if DENYLIST_PARTS.intersection(path.parts):
            raise CandidateViolation(f"denylisted candidate path: {path}")
        _validate_allowlist_path(path, selected_profiles)
        digest = entry.get("sha256")
        if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise CandidateViolation(f"invalid SHA-256 for {path}")
        entries[path] = digest
    if tuple(sorted(entries)) != expected_paths:
        raise CandidateViolation("manifest file set does not equal the selected portable allowlist")
    for path, expected_digest in entries.items():
        source = root / path
        if _digest(source) != expected_digest:
            raise CandidateViolation(f"candidate digest mismatch: {path}")
        if source.suffix != ".md":
            continue
        text = source.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            target = match.group("target").split("#", 1)[0]
            if not target or re.match(r"[a-z]+://", target):
                continue
            resolved = PurePosixPath((path.parent / target).as_posix())
            if ".." in resolved.parts or resolved not in entries:
                raise CandidateViolation(f"portable Markdown link leaves selected allowlist: {path} -> {target}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        verify_manifest(args.project_root.resolve(), manifest)
    except (CandidateViolation, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"portable candidate invalid: {exc}", file=sys.stderr)
        return 1
    print("Portable Change Guidance snapshot verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
