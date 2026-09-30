"""The graph-checkpoint boundary must not rewrite who owns a failure.

A caller-body exception (graph execution inside the ``async with``) is the
caller's causal fact; only setup-phase failures are Bundle-availability facts.

BUG-081: the wide ``except (OSError, RuntimeError, ValueError)`` used to wrap
the whole context including the yielded body, so a graph-node guard error such
as ``ValueError("hitl2_state_invalid")`` surfaced as ``bundle_unavailable``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef
from deerflow_deep_research.domain.state import BundleLocalState

BUNDLE = RunBundleRef(
    bundle_id=BundleId("b_" + "A" * 43),
    scope_bucket="s_" + "B" * 43,
)


def _published_lifecycle(tmp_path: Path):
    from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle

    BundleLifecycle(workspace_host_path=tmp_path)._publish_sync(
        BUNDLE, BundleLocalState(bundle_id=BUNDLE.bundle_id, implementation_mode="all_real")
    )
    return BundleLifecycle(workspace_host_path=tmp_path)


@pytest.mark.asyncio
async def test_open_graph_checkpoint_does_not_mask_a_caller_body_failure(tmp_path: Path) -> None:
    """A body exception keeps its own type; it is not a bundle-availability fact."""

    lifecycle = _published_lifecycle(tmp_path)
    with pytest.raises(ValueError, match="hitl2_state_invalid"):
        async with lifecycle.open_graph_checkpoint(BUNDLE):
            raise ValueError("hitl2_state_invalid")


@pytest.mark.asyncio
async def test_open_graph_checkpoint_does_not_mask_a_caller_body_os_error(tmp_path: Path) -> None:
    """The same transparency applies to every exception class the boundary wraps in setup."""

    lifecycle = _published_lifecycle(tmp_path)
    with pytest.raises(RuntimeError, match="graph_node_failure"):
        async with lifecycle.open_graph_checkpoint(BUNDLE):
            raise RuntimeError("graph_node_failure")
