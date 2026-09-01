"""Typed bounded workspace-observation contracts for the local operator reader.

@impl LDO-007
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import Field

from deerflow_deep_research.domain.lifecycle import FrozenContract


class WorkspacePolicyLabel(StrEnum):
    """Why an operator can (or cannot) see an entry — model visibility is orthogonal."""

    MODEL_READ = "MODEL_READ"
    MODEL_WRITE = "MODEL_WRITE"
    OPERATOR_ONLY = "OPERATOR_ONLY"
    RESTRICTED = "RESTRICTED"


class MountRootView(FrozenContract):
    """One operator-visible mount root: alias and posture only, never a host path."""

    alias: str = Field(min_length=1, max_length=64, pattern=r"^[a-z][a-z0-9_-]*$")
    policy_label: WorkspacePolicyLabel
    readable: bool
    writable: bool


class WorkspaceEntry(FrozenContract):
    relative_path: str = Field(min_length=1, max_length=512)
    kind: Literal["dir", "file"]
    byte_size: int | None = Field(default=None, ge=0)
    policy_label: WorkspacePolicyLabel


class WorkspacePage(FrozenContract):
    root_alias: str = Field(min_length=1, max_length=64)
    relative_path: str
    entries: tuple[WorkspaceEntry, ...] = ()
    truncated: bool = False


class FilePreview(FrozenContract):
    root_alias: str = Field(min_length=1, max_length=64)
    relative_path: str
    content: str
    byte_size: int = Field(ge=0)
    truncated: bool = False
    content_hash: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    hash_verified: bool | None = None
    time_posture: Literal["CURRENT", "CAPTURED_AT_NODE_AGENT_INVOCATION"] = "CURRENT"
    policy_label: WorkspacePolicyLabel


class WorkspaceDenial(FrozenContract):
    """A typed refusal; never a guess, never a host path."""

    reason: Literal[
        "unknown_root",
        "absolute_path",
        "path_escape",
        "private_scope",
        "foreign_scope",
        "unsupported_binary",
        "oversize",
        "not_found",
        "unavailable",
    ]
    requested_path: str | None = Field(default=None, min_length=1, max_length=512)
    message: str = Field(min_length=1, max_length=512)
