"""Composition-injected bounded read surface for the local operator.

The reader owns only filesystem observation inside roots that composition
explicitly entrusted to it. It knows nothing about bundles, lifecycle, leases,
or driving: path selection can never bind a run, change a cursor, or grant
control. Host paths never cross the interface. (`LDO-007`)
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from deerflow_deep_research.domain.workspace import (
    FilePreview,
    MountRootView,
    WorkspaceDenial,
    WorkspaceEntry,
    WorkspacePage,
    WorkspacePolicyLabel,
)

_DEFAULT_TEXT_SUFFIXES = frozenset(
    {".md", ".txt", ".json", ".jsonl", ".csv", ".yaml", ".yml", ".py", ".toml", ".html", ".log"}
)


@dataclass(frozen=True)
class _TrustedRoot:
    host_path: Path
    policy_label: WorkspacePolicyLabel
    readable: bool
    writable: bool


class OperatorWorkspaceReader:
    """Read-only, policy-labeled, escape-proof listing/preview over trusted roots."""

    def __init__(
        self,
        *,
        roots: Mapping[str, Mapping[str, object]],
        max_entries: int = 500,
        max_preview_bytes: int = 65_536,
        verify_hash: bool = False,
        text_suffixes: frozenset[str] = _DEFAULT_TEXT_SUFFIXES,
    ) -> None:
        self._roots: dict[str, _TrustedRoot] = {}
        for alias, spec in roots.items():
            self._roots[alias] = _TrustedRoot(
                # Canonicalize once: containment checks and entry relative paths
                # compare against resolution results, so an unresolved root (for
                # example a symlinked temporary directory) would otherwise raise
                # instead of returning a typed page or denial.
                host_path=Path(str(spec["path"])).resolve(strict=False),
                policy_label=WorkspacePolicyLabel(str(spec["label"])),
                readable=bool(spec.get("readable", True)),
                writable=bool(spec.get("writable", False)),
            )
        self._max_entries = max_entries
        self._max_preview_bytes = max_preview_bytes
        self._verify_hash = verify_hash
        self._text_suffixes = text_suffixes

    # -- observation -------------------------------------------------------

    def list_roots(self) -> tuple[MountRootView, ...]:
        return tuple(
            MountRootView(
                alias=alias,
                policy_label=root.policy_label,
                readable=root.readable,
                writable=root.writable,
            )
            for alias, root in sorted(self._roots.items())
        )

    def list(self, root_alias: str, relative_path: str = ".") -> WorkspacePage | WorkspaceDenial:
        root = self._roots.get(root_alias)
        if root is None:
            return self._deny("unknown_root", relative_path)
        target = self._resolve(root, relative_path)
        if isinstance(target, WorkspaceDenial):
            return target
        if not target.exists():
            return self._deny("not_found", relative_path)
        if not target.is_dir():
            return self._deny("unavailable", relative_path, "requested path is not a directory")
        if not root.readable:
            return self._deny("private_scope", relative_path, "root is not operator-readable")

        try:
            children = sorted(target.iterdir(), key=lambda item: item.name)
        except OSError:
            return self._deny("unavailable", relative_path, "directory unreadable")

        truncated = len(children) > self._max_entries
        entries: list[WorkspaceEntry] = []
        for child in children[: self._max_entries]:
            relative = child.relative_to(root.host_path).as_posix()
            if child.is_dir():
                entries.append(
                    WorkspaceEntry(
                        relative_path=relative,
                        kind="dir",
                        policy_label=root.policy_label,
                    )
                )
            else:
                try:
                    size = child.stat().st_size
                except OSError:
                    size = None
                entries.append(
                    WorkspaceEntry(
                        relative_path=relative,
                        kind="file",
                        byte_size=size,
                        policy_label=root.policy_label,
                    )
                )
        return WorkspacePage(
            root_alias=root_alias,
            relative_path=relative_path,
            entries=tuple(entries),
            truncated=truncated,
        )

    def preview(self, root_alias: str, relative_path: str) -> FilePreview | WorkspaceDenial:
        root = self._roots.get(root_alias)
        if root is None:
            return self._deny("unknown_root", relative_path)
        target = self._resolve(root, relative_path)
        if isinstance(target, WorkspaceDenial):
            return target
        if not root.readable:
            return self._deny("private_scope", relative_path, "root is not operator-readable")
        if not target.exists() or not target.is_file():
            return self._deny("not_found", relative_path)
        if target.suffix.lower() not in self._text_suffixes:
            return self._deny("unsupported_binary", relative_path)
        try:
            byte_size = target.stat().st_size
        except OSError:
            return self._deny("unavailable", relative_path, "stat failed")
        if byte_size > self._max_preview_bytes:
            return self._deny("oversize", relative_path)
        try:
            payload = target.read_bytes()
        except OSError:
            return self._deny("unavailable", relative_path, "read failed")

        digest = hashlib.sha256(payload).hexdigest()
        try:
            verified = hashlib.sha256(target.read_bytes()).hexdigest() == digest
        except OSError:
            verified = False
        truncated = False
        text = payload.decode("utf-8", errors="replace")
        return FilePreview(
            root_alias=root_alias,
            relative_path=relative_path,
            content=text,
            byte_size=byte_size,
            truncated=truncated,
            content_hash=digest,
            hash_verified=verified,
            time_posture="CURRENT",
            policy_label=root.policy_label,
        )

    # -- internal ----------------------------------------------------------

    def _resolve(self, root: _TrustedRoot, relative_path: str) -> Path | WorkspaceDenial:
        requested = Path(relative_path)
        if requested.is_absolute() or relative_path.startswith("~"):
            return self._deny("absolute_path", relative_path)
        if ".." in requested.parts:
            return self._deny("path_escape", relative_path)
        candidate = root.host_path / requested
        try:
            resolved = candidate.resolve(strict=False)
            container = root.host_path.resolve(strict=False)
        except OSError:
            return self._deny("unavailable", relative_path, "resolution failed")
        if resolved != container and container not in resolved.parents:
            # Symlink or other indirection escaping the trusted root.
            return self._deny("path_escape", relative_path)
        if resolved.is_file():
            # Re-check after resolution: the final target must still sit inside.
            pass
        if os.path.sep != "/" and ".." in os.path.normpath(relative_path).split(os.path.sep):
            return self._deny("path_escape", relative_path)
        return resolved

    def _deny(
        self,
        reason: str,
        requested_path: str | None,
        message: str | None = None,
    ) -> WorkspaceDenial:
        return WorkspaceDenial(
            reason=reason,  # type: ignore[arg-type]
            requested_path=requested_path,
            message=message or reason.replace("_", " "),
        )
