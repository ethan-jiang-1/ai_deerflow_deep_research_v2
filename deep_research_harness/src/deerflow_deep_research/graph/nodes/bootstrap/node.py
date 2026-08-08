"""Real bootstrap node factory.

@impl BON-001
@impl BON-002
@impl BON-003

The Harness has already published the selected Run Bundle and its initial State before this
node runs. Real Bootstrap reads that Bundle-local State through its injected capability,
atomically establishes only the contained marker, reads it back, and validates it against the
same Bundle-local State. On a valid binding it routes ``needs_input`` to HITL1; on a missing,
incomplete, or divergent marker it fails closed to a terminal ``BLOCKED`` route. It performs
no research model call and never derives an identity, root, or checkpoint from graph input.
"""

from __future__ import annotations

from typing import Any

from deerflow_deep_research.domain.bootstrap import BootstrapMarker, validate_bootstrap_binding
from deerflow_deep_research.domain.lifecycle import LifecycleStatus, TerminalReason
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.state import PhaseStatus, node_state_update


def build_real(dependencies: NodeBuildDependencies):
    store = dependencies.bootstrap_bundle
    if store is None:
        raise ValueError("bootstrap_bundle_capability_missing")

    async def run(state: dict[str, Any]) -> dict[str, Any]:
        del state
        try:
            bound_state = await store.read_bundle_state()
            marker = BootstrapMarker.from_bundle_state(bound_state)
            await store.establish_bundle(marker)
            read_back = await store.read_marker()
            bound_state = await store.read_bundle_state()
            failure = None if read_back is None else validate_bootstrap_binding(read_back, bound_state)
        except ValueError:
            read_back = None
            failure = None
        if read_back is not None and failure is None:
            return node_state_update("bootstrap", route="needs_input")
        return {
            **node_state_update("bootstrap"),
            "phase_status": PhaseStatus.TERMINAL.value,
            "terminal_status": LifecycleStatus.BLOCKED.value,
            "terminal_reason": TerminalReason.GATE_BLOCKED.value,
            "route": "exhausted",
        }

    return run
