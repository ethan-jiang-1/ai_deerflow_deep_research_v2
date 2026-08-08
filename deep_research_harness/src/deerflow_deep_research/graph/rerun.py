"""Graph-facing access to the one pure full-rerun compiler.

Runtime graph preparation needs the exact update emitted by the rerun node, but it does
not own or import that node's private implementation surface. This facade preserves the
single compiler while keeping the cross-layer dependency at the graph boundary.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from deerflow_deep_research.domain.lifecycle import RunRefinementSource
from deerflow_deep_research.graph.nodes.rerun.contracts import RerunSource
from deerflow_deep_research.graph.nodes.rerun.planner import (
    FullRerunPolicy,
    FullRerunUpdate,
    compile_full_rerun_update,
)


def compile_run_refinement_update(
    state: Mapping[str, Any],
    *,
    policy: FullRerunPolicy,
    run_refinement: RunRefinementSource,
) -> FullRerunUpdate:
    """Return the rerun node's exact pure update for one admitted direction."""

    return compile_full_rerun_update(
        state,
        source=RerunSource.RUN_REFINEMENT,
        policy=policy,
        run_refinement=run_refinement,
    )


__all__ = ["FullRerunPolicy", "FullRerunUpdate", "compile_run_refinement_update"]
