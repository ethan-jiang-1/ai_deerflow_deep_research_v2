"""Closed runtime-only inputs for a non-interactive graph start."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class NonInteractivePolicy:
    """The only policy shape admitted from trusted runtime context.

    ``profile_intent`` optionally declares the research intent of an automatic
    run (``minimal``; absent = today's behavior). It is included in the graph
    value only when set, so an absent intent keeps the current state shape.
    """

    auto_profile: bool
    auto_proceed: bool
    profile_intent: Literal["minimal"] | None = None

    def __post_init__(self) -> None:
        if self.auto_profile is not True or self.auto_proceed is not True:
            raise ValueError("non_interactive_policy_invalid")
        if self.profile_intent is not None and self.profile_intent != "minimal":
            raise ValueError("non_interactive_policy_invalid")

    def graph_value(self) -> dict[str, bool | str]:
        value: dict[str, bool | str] = {
            "auto_profile": self.auto_profile,
            "auto_proceed": self.auto_proceed,
        }
        if self.profile_intent is not None:
            value["profile_intent"] = self.profile_intent
        return value


@dataclass(frozen=True)
class StartActionInput:
    """One new Bundle start's closed runtime input.

    ``None`` preserves ordinary interactive execution. A populated policy can only be
    serialized by the graph executor's initial-state invocation.
    """

    non_interactive_policy: NonInteractivePolicy | None = None
