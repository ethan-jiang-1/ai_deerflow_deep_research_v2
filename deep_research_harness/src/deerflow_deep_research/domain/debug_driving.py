"""Typed contracts for the local workflow-debug driving surface.

Closed commands, exact-cursor idempotency, and session projections. The driver
is not a lifecycle authority: it drives the one real graph through the existing
executor and lifecycle admission. (`LDD-001`..`LDD-005`)
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from deerflow_deep_research.domain.lifecycle import FrozenContract

DebugCommandKind = Literal[
    "advance_one",
    "drive_until",
    "pause_request",
    "answer",
    "cancel",
    "detach",
]
DriveMode = Literal["step", "run"]
SessionPosture = Literal["running", "pause_requested", "paused_at_boundary", "awaiting_hitl", "terminal"]


class StopPolicy(FrozenContract):
    """Where drive_until stops; breakpoint names a node's post-commit."""

    breakpoint_after: str | None = Field(default=None, min_length=1, max_length=32)
    stop_on_hitl: bool = True
    stop_on_failure: bool = True
    stop_on_terminal: bool = True


class DebugCommand(FrozenContract):
    kind: DebugCommandKind
    bundle_id: str = Field(min_length=1, max_length=64)
    command_id: str = Field(min_length=8, max_length=128)
    expected_cursor: str = Field(min_length=8, max_length=256)
    breakpoint: StopPolicy | None = None
    answer_text: str | None = Field(default=None, min_length=1, max_length=16_384)
    option_id: str | None = Field(default=None, min_length=1, max_length=64)


class BoundaryCursor(FrozenContract):
    """Opaque-ish projection of the durable boundary; the driver's write permit."""

    bundle_id: str = Field(min_length=1, max_length=64)
    generation: int = Field(ge=0)
    frame_sequence: int = Field(ge=0)
    checkpoint_id: str | None = Field(default=None, min_length=1, max_length=128)
    next_nodes: tuple[str, ...] = ()

    def token(self) -> str:
        """The write permit: durable boundary identity only.

        ``next_nodes`` is deliberately excluded: it is an operator-facing
        projection of the graph state (and is populated on the stepping path
        only), not part of the boundary identity the permit fences. Including
        it made every command that recomputed the cursor without the graph
        state read as ``stale``.
        """
        import json

        return "BC1." + json.dumps(
            {
                "b": self.bundle_id,
                "g": self.generation,
                "f": self.frame_sequence,
                "c": self.checkpoint_id or "",
            },
            sort_keys=True,
            separators=(",", ":"),
        )


class LeasePosture(FrozenContract):
    owner: str | None = Field(default=None, min_length=1, max_length=128)
    generation: int = Field(ge=0)
    live: bool
    expires_in_seconds: float | None = None


class DebugSessionSnapshot(FrozenContract):
    bundle_id: str = Field(min_length=1, max_length=64)
    cursor: BoundaryCursor
    mode: DriveMode
    posture: SessionPosture
    stop_policy: StopPolicy
    pause_requested: bool = False
    lease: LeasePosture
    pending_request_id: str | None = Field(default=None, min_length=1, max_length=128)


class DebugSessionUpdate(FrozenContract):
    """Result of one executed command: new snapshot, or a typed denial."""

    snapshot: DebugSessionSnapshot | None = None
    denied: Literal[None, "stale", "duplicate", "busy", "invalid", "not_found", "in_flight"] = None
    message: str | None = Field(default=None, min_length=1, max_length=512)
    committed_node: str | None = Field(default=None, min_length=1, max_length=32)
    command_id: str = Field(min_length=8, max_length=128)


class StartRequest(FrozenContract):
    question: str = Field(min_length=1, max_length=16_384)
    mode: DriveMode
    owner: str = Field(min_length=1, max_length=128)
    command_id: str = Field(min_length=8, max_length=128)


class AttachRequest(FrozenContract):
    bundle_id: str = Field(min_length=1, max_length=64)
    owner: str = Field(min_length=1, max_length=128)
    expected_lease_generation: int | None = Field(default=None, ge=0)
