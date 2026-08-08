"""Process-local generic infrastructure-probe host.

@impl RUI-006
@impl RUI-004

The default reflected tool retains one GraphHost only for its independent generic
infrastructure probe. Deep Research lifecycle actions bypass this host entirely and
go through the Bundle lifecycle boundary. This module never retains request envelopes,
provider contexts, namespaces, or other request authority.
"""

from __future__ import annotations

from deerflow_deep_research.runtime.graph_host import GraphHost
from deerflow_deep_research.runtime.probe import InfraProbeHandler

_default_host: GraphHost | None = None


def build_control_graph_host(**kwargs: object) -> GraphHost:
    """Build the isolated generic host used solely by ``infra_probe``."""

    host = GraphHost(**kwargs)
    host.register(InfraProbeHandler())
    return host


def get_default_graph_host() -> GraphHost:
    """Return the lazily created process-local default control host."""
    global _default_host
    if _default_host is None:
        _default_host = build_control_graph_host()
    return _default_host


def reset_default_graph_host(host: GraphHost | None = None) -> None:
    """Replace the process-local reference, for deterministic isolated tests."""
    global _default_host
    _default_host = host


__all__ = ["build_control_graph_host", "get_default_graph_host", "reset_default_graph_host"]
