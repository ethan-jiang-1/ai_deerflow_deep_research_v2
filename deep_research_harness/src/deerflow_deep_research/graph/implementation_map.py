"""Explicit node-adapter selection for graph composition.

Production owns the selection interface but never discovers fixture adapters.  Test and
demo composition roots may inject an externally built catalog through this interface.

@impl REG-001
@impl REG-019
@impl FSI-002
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType

from deerflow_deep_research.domain.gate import GateDefinition
from deerflow_deep_research.domain.node_spec import UNAVAILABLE_REAL_FACTORY, NodeFactory, NodeSpec


class AdapterKind(StrEnum):
    REAL = "real"
    FIXTURE = "fixture"


class ImplementationMapError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"[{code}] {detail}")
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class NodeAdapter:
    """One concrete adapter supplied to the graph composition seam."""

    factory: NodeFactory
    kind: AdapterKind
    requires_gate: bool

    def __post_init__(self) -> None:
        if not callable(self.factory):
            raise TypeError("adapter factory must be callable")
        if not isinstance(self.kind, AdapterKind):
            raise TypeError("adapter kind must be an AdapterKind")
        if not isinstance(self.requires_gate, bool):
            raise TypeError("adapter requires_gate must be a bool")


AdapterSelection = Mapping[str, NodeAdapter] | Iterable[tuple[str, NodeAdapter]]

# This production-owned fact is deliberately independent of fixture definitions.  A
# selected adapter carries the same fact so injected fixture and mixed selections can
# be validated without production importing the fixture catalog.
REAL_GATED_NODES = frozenset({"wave0", "wave1", "wave2_synthesis", "final_delivery"})


def all_real_adapters(specs: Mapping[str, NodeSpec]) -> Mapping[str, NodeAdapter]:
    """Construct the only production-owned adapter selection."""

    selected: dict[str, NodeAdapter] = {}
    for logical_name, spec in specs.items():
        if spec.logical_name != logical_name:
            raise ImplementationMapError("implementation_spec_mismatch", logical_name)
        if spec.real_factory is UNAVAILABLE_REAL_FACTORY:
            raise ImplementationMapError(
                "implementation_unavailable",
                f"real implementation unavailable for {logical_name}",
            )
        selected[logical_name] = NodeAdapter(
            factory=spec.real_factory,
            kind=AdapterKind.REAL,
            requires_gate=logical_name in REAL_GATED_NODES,
        )
    return MappingProxyType(selected)


def _normalize_selection(adapters: AdapterSelection | None) -> dict[str, NodeAdapter]:
    if adapters is None:
        raise ImplementationMapError("implementation_selection_required", "adapter selection is required")
    try:
        entries = tuple(adapters.items()) if isinstance(adapters, Mapping) else tuple(adapters)
    except TypeError as exc:
        raise ImplementationMapError("implementation_adapter_invalid", "adapter selection must be iterable") from exc
    names: list[str] = []
    normalized: dict[str, NodeAdapter] = {}
    for entry in entries:
        if not isinstance(entry, tuple) or len(entry) != 2:
            raise ImplementationMapError("implementation_adapter_invalid", "selection entries must be (name, adapter)")
        logical_name, adapter = entry
        if not isinstance(logical_name, str) or not isinstance(adapter, NodeAdapter):
            raise ImplementationMapError("implementation_adapter_invalid", str(logical_name))
        names.append(logical_name)
        normalized[logical_name] = adapter
    duplicate_names = sorted({name for name in names if names.count(name) > 1})
    if duplicate_names:
        raise ImplementationMapError(
            "implementation_map_duplicate",
            f"duplicate adapters: {', '.join(duplicate_names)}",
        )
    return normalized


def resolve_implementations(
    specs: Mapping[str, NodeSpec],
    adapters: AdapterSelection | None,
) -> Mapping[str, NodeAdapter]:
    """Validate one complete explicit selection before graph construction."""

    selected = _normalize_selection(adapters)
    spec_names = set(specs)
    adapter_names = set(selected)
    missing = spec_names - adapter_names
    if missing:
        raise ImplementationMapError("implementation_map_incomplete", f"missing adapters: {', '.join(sorted(missing))}")
    unknown = adapter_names - spec_names
    if unknown:
        raise ImplementationMapError("implementation_map_unknown", f"unknown adapters: {', '.join(sorted(unknown))}")

    resolved: dict[str, NodeAdapter] = {}
    for logical_name, spec in specs.items():
        if spec.logical_name != logical_name:
            raise ImplementationMapError("implementation_spec_mismatch", logical_name)
        adapter = selected[logical_name]
        if adapter.kind is AdapterKind.REAL:
            if spec.real_factory is UNAVAILABLE_REAL_FACTORY:
                raise ImplementationMapError(
                    "implementation_unavailable",
                    f"real implementation unavailable for {logical_name}",
                )
            if adapter.factory is not spec.real_factory:
                raise ImplementationMapError("implementation_real_factory_mismatch", logical_name)
        resolved[logical_name] = adapter
    return MappingProxyType(resolved)


def validate_gate_definitions(
    adapters: Mapping[str, NodeAdapter],
    gate_defs: Mapping[str, GateDefinition] | None,
) -> Mapping[str, GateDefinition]:
    """Require one gate definition for exactly every gated selected adapter."""

    if gate_defs is None:
        raise ImplementationMapError("gate_definitions_required", "gate definitions are required")
    if not isinstance(gate_defs, Mapping):
        raise ImplementationMapError("gate_definition_invalid", "gate definitions must be a mapping")
    adapter_names = set(adapters)
    expected_names = {name for name, adapter in adapters.items() if adapter.requires_gate}
    gate_names = set(gate_defs)
    unknown = gate_names - adapter_names
    if unknown:
        raise ImplementationMapError("gate_definitions_unknown", f"unknown gates: {', '.join(sorted(unknown))}")
    extraneous = gate_names - expected_names
    if extraneous:
        raise ImplementationMapError(
            "gate_definitions_extraneous",
            f"extraneous gates: {', '.join(sorted(extraneous))}",
        )
    missing = expected_names - gate_names
    if missing:
        raise ImplementationMapError("gate_definitions_incomplete", f"missing gates: {', '.join(sorted(missing))}")

    resolved: dict[str, GateDefinition] = {}
    for logical_name in sorted(expected_names):
        gate_def = gate_defs[logical_name]
        if not isinstance(gate_def, GateDefinition):
            raise ImplementationMapError("gate_definition_invalid", logical_name)
        if gate_def.phase != logical_name:
            raise ImplementationMapError("gate_definition_mismatch", logical_name)
        resolved[logical_name] = gate_def
    return MappingProxyType(resolved)


__all__ = [
    "AdapterKind",
    "ImplementationMapError",
    "NodeAdapter",
    "AdapterSelection",
    "REAL_GATED_NODES",
    "all_real_adapters",
    "resolve_implementations",
    "validate_gate_definitions",
]
