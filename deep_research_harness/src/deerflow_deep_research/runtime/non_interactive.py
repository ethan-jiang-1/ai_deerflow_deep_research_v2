"""Closed runtime-only inputs for a non-interactive graph start."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NonInteractivePolicy:
    """The only policy shape admitted from trusted runtime context."""

    auto_profile: bool
    auto_proceed: bool

    def __post_init__(self) -> None:
        if self.auto_profile is not True or self.auto_proceed is not True:
            raise ValueError("non_interactive_policy_invalid")

    def graph_value(self) -> dict[str, bool]:
        return {"auto_profile": self.auto_profile, "auto_proceed": self.auto_proceed}


@dataclass(frozen=True)
class StartActionInput:
    """One new Bundle start's closed runtime input.

    ``None`` preserves ordinary interactive execution. A populated policy can only be
    serialized by the graph executor's initial-state invocation.
    """

    non_interactive_policy: NonInteractivePolicy | None = None
