"""Immutable deterministic routing data for a fixture recipe."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from deerflow_deep_research.domain.lifecycle import (
    BootstrapRoute,
    FinalVerdict,
    GateVerdict,
    Hitl2Decision,
    ReadinessVerdict,
    SynthesisVerdict,
)

_MAX_SEQUENCE_LENGTH = 256


def _enum_sequence(values: Iterable[object], enum_type: type, field_name: str) -> tuple[object, ...]:
    try:
        converted = tuple(value if isinstance(value, enum_type) else enum_type(value) for value in values)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid fixture route for {field_name}") from exc
    if not converted or len(converted) > _MAX_SEQUENCE_LENGTH:
        raise ValueError(f"invalid fixture route sequence for {field_name}")
    return converted


@dataclass(frozen=True)
class FixtureScenario:
    """Complete deterministic route scenario bound at fixture recipe construction."""

    bootstrap: tuple[BootstrapRoute, ...] = (BootstrapRoute.NEEDS_INPUT,)
    wave0: tuple[GateVerdict, ...] = (GateVerdict.PASS,)
    wave1: tuple[GateVerdict, ...] = (GateVerdict.PASS,)
    wave2_synthesis: tuple[SynthesisVerdict, ...] = (SynthesisVerdict.PASS,)
    hitl2: tuple[Hitl2Decision, ...] = (Hitl2Decision.PROCEED,)
    readiness: tuple[ReadinessVerdict, ...] = (ReadinessVerdict.PASS,)
    final_delivery: tuple[FinalVerdict, ...] = (FinalVerdict.PASS,)

    def __post_init__(self) -> None:
        object.__setattr__(self, "bootstrap", _enum_sequence(self.bootstrap, BootstrapRoute, "bootstrap"))
        object.__setattr__(self, "wave0", _enum_sequence(self.wave0, GateVerdict, "wave0"))
        object.__setattr__(self, "wave1", _enum_sequence(self.wave1, GateVerdict, "wave1"))
        object.__setattr__(
            self,
            "wave2_synthesis",
            _enum_sequence(self.wave2_synthesis, SynthesisVerdict, "wave2_synthesis"),
        )
        object.__setattr__(self, "hitl2", _enum_sequence(self.hitl2, Hitl2Decision, "hitl2"))
        object.__setattr__(self, "readiness", _enum_sequence(self.readiness, ReadinessVerdict, "readiness"))
        object.__setattr__(self, "final_delivery", _enum_sequence(self.final_delivery, FinalVerdict, "final_delivery"))
        if self.wave0[-1] is not GateVerdict.PASS or self.wave1[-1] is not GateVerdict.PASS:
            raise ValueError("wave fixture must converge to pass")
        if self.wave2_synthesis[-1] is not SynthesisVerdict.PASS:
            raise ValueError("synthesis fixture must converge to pass")
        if self.readiness[-1] is not ReadinessVerdict.PASS:
            raise ValueError("readiness fixture must converge to pass")
        if self.final_delivery[-1] is not FinalVerdict.PASS:
            raise ValueError("final fixture must converge to pass")

    def value_for_visit(self, phase: str, visit_count: int) -> str:
        values = getattr(self, phase, None)
        if not isinstance(values, tuple) or not values:
            raise ValueError(f"fixture sequence missing for {phase}")
        index = min(visit_count, len(values) - 1)
        value = values[index]
        return value.value if hasattr(value, "value") else str(value)


__all__ = ["FixtureScenario"]
