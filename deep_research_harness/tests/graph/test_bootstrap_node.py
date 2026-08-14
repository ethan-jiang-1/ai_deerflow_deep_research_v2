"""Red tests for the real bootstrap node factory.

@impl BON-002
@impl BON-003
@impl BON-007
"""

from __future__ import annotations

from typing import Any

import pytest

from deerflow_deep_research.domain.bootstrap import BootstrapMarker
from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef
from deerflow_deep_research.domain.context import GraphContextView, NodeAgentContext
from deerflow_deep_research.domain.lifecycle import LifecycleStatus, TerminalReason
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.state import BUNDLE_STATE_SCHEMA_VERSION, BundleLocalState, PhaseStatus
from deerflow_deep_research.graph.nodes.bootstrap.node import build_real

_DIGEST = "d_" + "b" * 43
_MID = "human-start"
_BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "a" * 43), scope_bucket="s_" + "c" * 43)


def _marker(
    *,
    bundle_id: BundleId = _BUNDLE.bundle_id,
    start_message_id: str = _MID,
    request_digest: str = _DIGEST,
    state_schema_version: int = BUNDLE_STATE_SCHEMA_VERSION,
) -> BootstrapMarker:
    return BootstrapMarker(
        bundle_id=bundle_id,
        start_message_id=start_message_id,
        request_digest=request_digest,
        state_schema_version=state_schema_version,
    )


def _bundle_state(**overrides: object) -> BundleLocalState:
    values: dict[str, object] = {
        "bundle_id": _BUNDLE.bundle_id,
        "implementation_mode": "all_real",
        "start_message_id": _MID,
        "start_request_digest": _DIGEST,
        "schema_version": BUNDLE_STATE_SCHEMA_VERSION,
    }
    values.update(overrides)
    return BundleLocalState(**values)  # type: ignore[arg-type]


class _FakeStore:
    """Controllable bootstrap store: records establish, returns a configured read-back."""

    def __init__(
        self,
        *,
        state: BundleLocalState | None = None,
        read_back: BootstrapMarker | None | str = "same",
    ) -> None:
        # "same" -> return the marker that was established; otherwise return the literal.
        self._state = state or _bundle_state()
        self._read_back = read_back
        self.established: BootstrapMarker | None = None
        self.establish_calls = 0

    async def establish_bundle(self, marker: BootstrapMarker) -> None:
        self.established = marker
        self.establish_calls += 1

    async def read_marker(self) -> BootstrapMarker | None:
        if self._read_back == "same":
            return self.established
        return self._read_back  # type: ignore[return-value]

    async def read_bundle_state(self) -> BundleLocalState:
        return self._state


def _deps(store: _FakeStore) -> NodeBuildDependencies:
    ctx = GraphContextView(
        research_scope_id="r_test",
        workspace_root=f"/mnt/user-data/workspace/deep-research/scopes/{_BUNDLE.scope_bucket}/{_BUNDLE.bundle_id.value}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root="/mnt/user-data/outputs",
    )
    agent_ctx = NodeAgentContext(
        research_scope_id="r_test",
        node_name="bootstrap",
        attempt_id="g0_bootstrap_a01",
        workspace_root=ctx.workspace_root,
        attempt_root=ctx.workspace_root,
        policy_name="skeleton-bootstrap",
    )

    class _Caps:
        async def run_agent(self, *, context: object, request: object) -> object: ...

    return NodeBuildDependencies(
        graph_context=ctx,
        agent_context=agent_ctx,
        capabilities=_Caps(),
        bootstrap_bundle=store,
    )


def _state(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        # These caller-controlled legacy/checkpoint values must not participate in
        # Bootstrap binding. The selected Bundle State is the sole source.
        "bundle_id": "r_" + "z" * 43,
        "start_message_id": "caller-start-message",
        "request_digest": "d_" + "z" * 43,
        "schema_version": 99,
    }
    base.update(overrides)
    return base


class TestBuildRealRoutesOnBinding:
    async def test_bound_marker_routes_needs_input_with_no_model_call(self) -> None:
        store = _FakeStore()
        run = build_real(_deps(store))
        result = await run(_state())
        assert result["route"] == "needs_input"
        assert result["phase"] == "bootstrap"
        assert store.establish_calls == 1
        assert store.established == _marker()

    async def test_caller_route_is_ignored_for_bound_marker(self) -> None:
        # The real node routes from the established binding, not a caller-provided route.
        store = _FakeStore()
        run = build_real(_deps(store))
        result = await run(_state(route="profile_complete"))
        assert result["route"] == "needs_input"

    async def test_legacy_identity_and_checkpoint_fields_cannot_override_bundle_binding(self) -> None:
        store = _FakeStore()
        result = await build_real(_deps(store))(
            _state(
                bundle_id="r_" + "y" * 43,
                start_message_id="caller-override",
                request_digest="d_" + "y" * 43,
                schema_version=77,
            )
        )
        assert result["route"] == "needs_input"
        assert store.established == _marker()

    async def test_divergent_read_back_fails_closed_terminal(self) -> None:
        store = _FakeStore(read_back=_marker(bundle_id=BundleId("b_" + "z" * 43)))
        run = build_real(_deps(store))
        result = await run(_state())
        assert result["route"] == "exhausted"
        assert result["phase_status"] == PhaseStatus.TERMINAL.value
        assert result["terminal_status"] == LifecycleStatus.BLOCKED.value
        assert result["terminal_reason"] == TerminalReason.GATE_BLOCKED.value

    async def test_missing_read_back_fails_closed_terminal(self) -> None:
        store = _FakeStore(read_back=None)
        run = build_real(_deps(store))
        result = await run(_state())
        assert result["route"] == "exhausted"
        assert result["terminal_status"] == LifecycleStatus.BLOCKED.value

    async def test_state_schema_version_mismatch_fails_closed(self) -> None:
        store = _FakeStore(read_back=_marker(state_schema_version=BUNDLE_STATE_SCHEMA_VERSION + 1))
        run = build_real(_deps(store))
        result = await run(_state())
        assert result["route"] == "exhausted"
        assert result["terminal_status"] == LifecycleStatus.BLOCKED.value

    async def test_incomplete_published_bundle_state_fails_closed(self) -> None:
        store = _FakeStore(state=_bundle_state(start_message_id=None))
        result = await build_real(_deps(store))(_state())
        assert result["route"] == "exhausted"
        assert result["terminal_status"] == LifecycleStatus.BLOCKED.value


class TestBuildRealGuards:
    def test_missing_store_raises(self) -> None:
        deps = NodeBuildDependencies(
            graph_context=GraphContextView(
                research_scope_id="r_test",
                workspace_root="/mnt/user-data/workspace/deep-research/x",
                uploads_root="/mnt/user-data/uploads",
                outputs_root="/mnt/user-data/outputs",
            ),
            agent_context=NodeAgentContext(
                research_scope_id="r_test",
                node_name="bootstrap",
                attempt_id="g0_bootstrap_a01",
                workspace_root="/mnt/user-data/workspace/deep-research/x",
                attempt_root="/mnt/user-data/workspace/deep-research/x",
                policy_name="skeleton-bootstrap",
            ),
            capabilities=type("_C", (), {"run_agent": lambda self, *, context, request: None})(),
            bootstrap_bundle=None,
        )
        with pytest.raises(ValueError, match="bootstrap_bundle_capability_missing"):
            build_real(deps)
