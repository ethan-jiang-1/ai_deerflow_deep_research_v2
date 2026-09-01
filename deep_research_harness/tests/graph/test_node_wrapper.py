"""Red tests for the graph node wrapper's BOOTSTRAP_BUNDLE attach/forbid logic.

@impl BON-001
@impl BON-002
@impl NOA-001
"""

from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace
from typing import Any, cast

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from deerflow_deep_research.domain.bootstrap import BootstrapMarker
from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef, bundle_profile_path, run_bundle_root
from deerflow_deep_research.domain.context import GraphContextView, NodeAgentContext
from deerflow_deep_research.domain.enums import NodePhase
from deerflow_deep_research.domain.invocation import GraphInvocationContext, NodeDependencyResolver
from deerflow_deep_research.domain.node_spec import (
    NodeBuildDependencies,
    NodeCapability,
    NodeContracts,
    NodeSpec,
    PolicyRef,
)
from deerflow_deep_research.domain.profile import ResearchProfile
from deerflow_deep_research.domain.run_observation import RunEventCategory
from deerflow_deep_research.domain.state import BUNDLE_STATE_SCHEMA_VERSION, BundleLocalState, ContentRef, ResearchState
from deerflow_deep_research.graph import builder as builder_module
from deerflow_deep_research.graph.builder import _node_wrapper, _route
from deerflow_deep_research.graph.implementation_map import AdapterKind, NodeAdapter
from deerflow_deep_research.graph.nodes.bootstrap import NODE_SPEC as BOOTSTRAP_SPEC
from deerflow_deep_research.runtime.events import RuntimeObservationProjection, make_stream_event_sink

_BUNDLE = RunBundleRef(bundle_id=BundleId("b_" + "A" * 43), scope_bucket="s_" + "B" * 43)
_BUNDLE_ID = _BUNDLE.bundle_id.value
_START_MESSAGE_ID = "human-start"
_REQUEST_DIGEST = "d_" + "B" * 43


class _FakeStore:
    def __init__(self) -> None:
        self.establish_calls = 0
        self.bundle = _BUNDLE
        self._state = BundleLocalState(
            bundle_id=self.bundle.bundle_id,
            implementation_mode="all_real",
            start_message_id=_START_MESSAGE_ID,
            start_request_digest=_REQUEST_DIGEST,
            schema_version=BUNDLE_STATE_SCHEMA_VERSION,
        )

    async def establish_bundle(self, marker: BootstrapMarker) -> None:
        self.establish_calls += 1
        self.marker = marker

    async def read_marker(self) -> BootstrapMarker | None:
        return getattr(self, "marker", None)

    async def read_bundle_state(self) -> BundleLocalState:
        return self._state


class _FakeRequestStore:
    def __init__(self) -> None:
        self.write_calls = 0
        self._state = BundleLocalState(bundle_id=_BUNDLE.bundle_id, implementation_mode="all_real")

    async def read_bundle_state(self) -> BundleLocalState:
        return self._state

    async def read_profile(self, _profile_ref: ContentRef) -> ResearchProfile:
        raise AssertionError("profile read is outside this node-wrapper test")

    async def write_bundle_state(
        self,
        state: BundleLocalState,
        *,
        expected_revision: int,
    ) -> BundleLocalState:
        if expected_revision != self._state.revision:
            raise ValueError("state_revision_conflict")
        self._state = replace(state, revision=expected_revision + 1)
        return self._state

    async def write_profile(self, profile: ResearchProfile) -> ContentRef:
        self.write_calls += 1
        return ContentRef(
            sandbox_path=bundle_profile_path(_BUNDLE),
            content_hash="h_" + "A" * 43,
        )


class _FakeFinalDeliveryStore:
    async def read_readiness_report_plan(self, ref: ContentRef) -> bytes:
        return b"{}"

    async def read_synthesis_evidence(self, accepted_refs: tuple[str, ...]) -> tuple[object, ...]:
        return ()

    async def read_final_artifacts(self, refs: tuple[ContentRef, ContentRef]) -> tuple[bytes, bytes]:
        return (b"report", b"{}")


class _Resolver:
    def __init__(self, graph_context: GraphContextView, *, request_bundle: _FakeRequestStore | None = None) -> None:
        self._gc = graph_context
        self._request_bundle = request_bundle

    def resolve(self, *, logical_name: str, attempt_id: str, policy: Any) -> NodeBuildDependencies:
        return NodeBuildDependencies(
            graph_context=self._gc,
            agent_context=NodeAgentContext(
                research_scope_id=self._gc.research_scope_id,
                node_name=logical_name,
                attempt_id=attempt_id,
                workspace_root=self._gc.workspace_root,
                attempt_root=self._gc.workspace_root,
                policy_name=policy.name,
            ),
            capabilities=type("_C", (), {"run_agent": lambda self, *, context, request: None})(),
            request_bundle=self._request_bundle,
        )


# NodeDependencyResolver is a runtime_checkable Protocol; _Resolver satisfies it.
assert isinstance(
    _Resolver(
        GraphContextView(research_scope_id=_BUNDLE_ID, workspace_root="/x", uploads_root="/u", outputs_root="/o")
    ),
    NodeDependencyResolver,
)


def _graph_context() -> GraphContextView:
    bundle_root = run_bundle_root(_BUNDLE)
    return GraphContextView(
        research_scope_id=_BUNDLE_ID,
        workspace_root=f"/mnt/user-data/{bundle_root}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root=f"/mnt/user-data/outputs/{bundle_root}",
    )


def _context(
    store: _FakeStore | None,
    *,
    request_bundle: _FakeRequestStore | None = None,
    final_delivery_bundle: _FakeFinalDeliveryStore | None = None,
    resolver_request_bundle: _FakeRequestStore | None = None,
    event_recorder: object | None = None,
    observation_projection: object | None = None,
) -> GraphInvocationContext:
    gc = _graph_context()
    return GraphInvocationContext(
        graph_context=gc,
        dependency_resolver=_Resolver(gc, request_bundle=resolver_request_bundle),  # type: ignore[arg-type]
        bootstrap_bundle=store,
        request_bundle=request_bundle,
        final_delivery_bundle=final_delivery_bundle,
        event_recorder=event_recorder,  # type: ignore[arg-type]
        observation_projection=observation_projection,  # type: ignore[arg-type]
    )


def _state() -> dict[str, Any]:
    return {
        "schema_version": 3,
        "bundle_id": _BUNDLE_ID,
        "start_message_id": _START_MESSAGE_ID,
        "request_digest": _REQUEST_DIGEST,
        "request_text": "question",
        "phase": "bootstrap",
        "generation": 0,
        "execution_trace": (),
    }


def _fixture_bootstrap_factory(_dependencies: NodeBuildDependencies):
    def run(_state: ResearchState) -> dict[str, str]:
        return {"route": "needs_input"}

    return run


def _compile(mode: str):
    adapter = (
        NodeAdapter(factory=BOOTSTRAP_SPEC.real_factory, kind=AdapterKind.REAL, requires_gate=False)
        if mode == "real"
        else NodeAdapter(factory=_fixture_bootstrap_factory, kind=AdapterKind.FIXTURE, requires_gate=False)
    )
    builder = StateGraph(ResearchState, context_schema=GraphInvocationContext)
    builder.add_node("bootstrap", _node_wrapper("bootstrap", BOOTSTRAP_SPEC, adapter, {}))
    builder.add_edge(START, "bootstrap")
    builder.add_conditional_edges("bootstrap", _route, {"needs_input": END, "profile_complete": END, "exhausted": END})
    return builder.compile(checkpointer=InMemorySaver())


class _JournalRecorder:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    async def record(self, **event: object) -> None:
        self.events.append(dict(event))


class _ObservationProjection:
    def __init__(self) -> None:
        self.events: list[dict[str, object]] = []

    def emit(self, fields: dict[str, object], **_kwargs: object) -> None:
        self.events.append(dict(fields))

    async def aemit(self, fields: dict[str, object], **_kwargs: object) -> None:
        self.emit(fields, **_kwargs)


def _config() -> dict:
    return {"configurable": {"thread_id": "t1"}}


class _Req(BaseModel):
    pass


class _Res(BaseModel):
    pass


def _request_bundle_spec(*, declares: bool, seen: list[object]) -> NodeSpec:
    def real_factory(dependencies: NodeBuildDependencies):
        seen.append(dependencies.request_bundle)

        def run(_state: ResearchState) -> dict[str, str]:
            return {"route": "accepted"}

        return run

    return NodeSpec(
        logical_name="hitl1",
        phase=NodePhase.ORCHESTRATION,
        policy=PolicyRef(name="hitl1-profile", version="v1"),
        contracts=NodeContracts(request_type=_Req, result_type=_Res),
        real_factory=real_factory,
        capabilities=frozenset({NodeCapability.REQUEST_BUNDLE}) if declares else frozenset(),
    )


def _final_delivery_bundle_spec(*, seen: list[object]) -> NodeSpec:
    def real_factory(dependencies: NodeBuildDependencies):
        seen.append(dependencies.final_delivery_bundle)

        def run(_state: ResearchState) -> dict[str, str]:
            return {"route": "accepted"}

        return run

    return NodeSpec(
        logical_name="hitl1",
        phase=NodePhase.ORCHESTRATION,
        policy=PolicyRef(name="final-delivery-composer", version="v1"),
        contracts=NodeContracts(request_type=_Req, result_type=_Res),
        real_factory=real_factory,
        capabilities=frozenset({NodeCapability.FINAL_DELIVERY_BUNDLE}),
    )


def _fixture_factory(seen: list[object], attribute: str):
    def build(dependencies: NodeBuildDependencies):
        seen.append(getattr(dependencies, attribute))

        def run(_state: ResearchState) -> dict[str, str]:
            return {"route": "accepted"}

        return run

    return build


def _compile_custom(spec: NodeSpec, adapter: NodeAdapter):
    builder = StateGraph(ResearchState, context_schema=GraphInvocationContext)
    builder.add_node("hitl1", _node_wrapper("hitl1", spec, adapter, {}))
    builder.add_edge(START, "hitl1")
    builder.add_conditional_edges("hitl1", _route, {"accepted": END})
    return builder.compile(checkpointer=InMemorySaver())


class TestWrapperBootstrapBundleAttach:
    async def test_real_factory_with_store_attaches_and_routes(self) -> None:
        store = _FakeStore()
        graph = _compile("real")
        await graph.ainvoke(_state(), config=_config(), context=_context(store))
        assert store.establish_calls == 1

    async def test_real_factory_without_store_fails_before_factory(self) -> None:
        graph = _compile("real")
        with pytest.raises(ValueError, match="bootstrap_bundle_capability_missing"):
            await graph.ainvoke(_state(), config=_config(), context=_context(None))

    async def test_fixture_adapter_without_store_runs_and_does_not_touch_store(self) -> None:
        graph = _compile("fixture")
        store = _FakeStore()  # present on context but fixture adapter must not use it
        await graph.ainvoke(_state(), config=_config(), context=_context(store))
        assert store.establish_calls == 0


class TestWrapperRequestBundleAttach:
    async def test_real_declaring_factory_gets_request_bundle(self) -> None:
        seen: list[object] = []
        spec = _request_bundle_spec(declares=True, seen=seen)
        request_store = _FakeRequestStore()
        graph = _compile_custom(spec, NodeAdapter(spec.real_factory, AdapterKind.REAL, requires_gate=False))
        await graph.ainvoke(_state(), config=_config(), context=_context(None, request_bundle=request_store))
        assert seen == [request_store]

    async def test_real_declaring_factory_without_request_bundle_fails_before_factory(self) -> None:
        seen: list[object] = []
        spec = _request_bundle_spec(declares=True, seen=seen)
        graph = _compile_custom(spec, NodeAdapter(spec.real_factory, AdapterKind.REAL, requires_gate=False))
        with pytest.raises(ValueError, match="request_bundle_capability_missing"):
            await graph.ainvoke(_state(), config=_config(), context=_context(None))
        assert seen == []


class TestWrapperFinalDeliveryBundleAttach:
    async def test_real_declaring_factory_gets_final_delivery_bundle(self) -> None:
        seen: list[object] = []
        spec = _final_delivery_bundle_spec(seen=seen)
        graph = _compile_custom(spec, NodeAdapter(spec.real_factory, AdapterKind.REAL, requires_gate=False))
        store = _FakeFinalDeliveryStore()
        await graph.ainvoke(_state(), config=_config(), context=_context(None, final_delivery_bundle=store))
        assert seen == [store]

    async def test_real_declaring_factory_without_final_delivery_bundle_fails_before_factory(self) -> None:
        seen: list[object] = []
        spec = _final_delivery_bundle_spec(seen=seen)
        graph = _compile_custom(spec, NodeAdapter(spec.real_factory, AdapterKind.REAL, requires_gate=False))
        with pytest.raises(ValueError, match="final_delivery_bundle_capability_missing"):
            await graph.ainvoke(_state(), config=_config(), context=_context(None))
        assert seen == []


class TestWrapperJournalEvents:
    async def test_wrapper_projects_each_node_boundary_once_without_state_mutation(self) -> None:
        observation_projection = _ObservationProjection()
        graph = _compile("fixture")

        result = await graph.ainvoke(
            _state(),
            config=_config(),
            context=_context(None, observation_projection=observation_projection),
        )

        assert result["route"] == "needs_input"
        assert observation_projection.events == [
            {
                "phase": "bootstrap",
                "operation": "node",
                "outcome": "started",
                "attempt_id": "g0-bootstrap-a1",
                "bundle_id": _BUNDLE_ID,
            },
            {
                "phase": "bootstrap",
                "operation": "node",
                "outcome": "completed",
                "attempt_id": "g0-bootstrap-a1",
                "bundle_id": _BUNDLE_ID,
            },
        ]

    async def test_wrapper_projects_each_live_node_boundary_once_through_the_runtime_sink(self) -> None:
        payloads: list[object] = []
        projection = RuntimeObservationProjection(
            bundle_id=_BUNDLE_ID,
            event_sink=make_stream_event_sink(payloads.append),
        )
        graph = _compile("fixture")

        result = await graph.ainvoke(
            _state(),
            config=_config(),
            context=_context(None, observation_projection=projection),
        )

        assert result["route"] == "needs_input"
        assert [(payload["operation"], payload["outcome"]) for payload in payloads] == [
            ("node", "started"),
            ("node", "completed"),
        ]

    async def test_projection_keeps_suspension_distinct_from_failure(self) -> None:
        """REJ-011: the live projection carries `suspended`, never relabeled `failed`."""

        projection = _ObservationProjection()
        context = _context(None, observation_projection=projection)

        await builder_module._record_node_event(
            context,
            bundle_id=_BUNDLE_ID,
            category=RunEventCategory.NODE,
            phase="hitl1",
            attempt_id="g0-hitl1-a1",
            outcome="suspended",
        )

        assert [payload["outcome"] for payload in projection.events] == ["suspended"]
        assert all(payload.get("code") != "provider_failed" for payload in projection.events)

    async def test_wrapper_projects_a_gate_verdict_without_changing_its_state_update(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        observation_projection = _ObservationProjection()

        def fixture_factory(_dependencies: NodeBuildDependencies):
            return lambda _state: {}

        spec = NodeSpec(
            logical_name="hitl1",
            phase=NodePhase.ORCHESTRATION,
            policy=PolicyRef(name="hitl1-profile", version="v1"),
            contracts=NodeContracts(request_type=_Req, result_type=_Res),
            real_factory=fixture_factory,
        )
        monkeypatch.setattr(builder_module, "evaluate_gate_for_node", lambda *_args: {"route": "accepted"})
        wrapper = _node_wrapper(
            "hitl1",
            spec,
            NodeAdapter(fixture_factory, AdapterKind.FIXTURE, requires_gate=False),
            {"hitl1": cast(object, object())},
        )

        result = await wrapper(
            _state(),
            SimpleNamespace(context=_context(None, observation_projection=observation_projection)),
        )

        assert result == {"route": "accepted"}
        assert observation_projection.events[-1] == {
            "phase": "hitl1",
            "operation": "gate",
            "outcome": "completed",
            "attempt_id": "g0-hitl1-a1",
            "bundle_id": _BUNDLE_ID,
        }

    async def test_wrapper_uses_async_node_and_sync_gate_live_projections_once(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        payloads: list[object] = []
        projection = RuntimeObservationProjection(
            bundle_id=_BUNDLE_ID,
            event_sink=make_stream_event_sink(payloads.append),
        )

        def fixture_factory(_dependencies: NodeBuildDependencies):
            return lambda _state: {}

        spec = NodeSpec(
            logical_name="hitl1",
            phase=NodePhase.ORCHESTRATION,
            policy=PolicyRef(name="hitl1-profile", version="v1"),
            contracts=NodeContracts(request_type=_Req, result_type=_Res),
            real_factory=fixture_factory,
        )
        monkeypatch.setattr(builder_module, "evaluate_gate_for_node", lambda *_args: {"route": "accepted"})
        wrapper = _node_wrapper(
            "hitl1",
            spec,
            NodeAdapter(fixture_factory, AdapterKind.FIXTURE, requires_gate=False),
            {"hitl1": cast(object, object())},
        )

        result = await wrapper(
            _state(),
            SimpleNamespace(context=_context(None, observation_projection=projection)),
        )

        assert result == {"route": "accepted"}
        assert [(payload["operation"], payload["outcome"]) for payload in payloads] == [
            ("node", "started"),
            ("node", "completed"),
            ("gate", "completed"),
        ]

    async def test_wrapper_records_node_start_and_completion_without_gaining_control_authority(self) -> None:
        recorder = _JournalRecorder()
        graph = _compile("fixture")

        await graph.ainvoke(_state(), config=_config(), context=_context(None, event_recorder=recorder))

        assert [(event["category"], event["outcome"], event["phase"]) for event in recorder.events] == [
            ("node", "started", "bootstrap"),
            ("node", "completed", "bootstrap"),
        ]
        assert all(event["attempt_id"] == "g0-bootstrap-a1" for event in recorder.events)

    async def test_wrapper_records_safe_unknown_boundary_failure_and_preserves_the_exception(self) -> None:
        recorder = _JournalRecorder()
        seen: list[object] = []
        spec = _request_bundle_spec(declares=False, seen=seen)

        def failing_factory(_dependencies: NodeBuildDependencies):
            async def run(_state: ResearchState) -> dict[str, str]:
                raise RuntimeError("raw exception text must not enter the journal")

            return run

        graph = _compile_custom(spec, NodeAdapter(failing_factory, AdapterKind.FIXTURE, requires_gate=False))
        with pytest.raises(RuntimeError, match="raw exception"):
            await graph.ainvoke(_state(), config=_config(), context=_context(None, event_recorder=recorder))

        assert recorder.events[-1]["outcome"] == "failed"
        assert recorder.events[-1]["failure_category"] == "internal.unexpected"
        assert recorder.events[-1]["worker_failure_category"] == "unknown"
        assert "raw exception" not in str(recorder.events)

    async def test_wrapper_records_human_interrupt_suspension_without_internal_unexpected(self) -> None:
        """@impl REJ-011
        @bug BUG-063

        A node visit suspended by the graph's human-interrupt signal is a normal
        suspension awaiting recovery: the journal records the attempt as
        suspended rather than an unexpected internal failure, and the signal
        still propagates to the graph machinery.
        """
        from langgraph.errors import GraphInterrupt

        recorder = _JournalRecorder()
        spec = _request_bundle_spec(declares=False, seen=[])

        def suspending_factory(_dependencies: NodeBuildDependencies):
            async def run(_state: ResearchState) -> dict[str, str]:
                raise GraphInterrupt()

            return run

        graph = _compile_custom(spec, NodeAdapter(suspending_factory, AdapterKind.FIXTURE, requires_gate=False))
        await graph.ainvoke(_state(), config=_config(), context=_context(None, event_recorder=recorder))

        suspension_events = [event for event in recorder.events if event["outcome"] == "suspended"]
        assert suspension_events, recorder.events
        assert all(event.get("failure_category") != "internal.unexpected" for event in suspension_events)
        assert all(event.get("worker_failure_category") != "unknown" for event in suspension_events)

    async def test_fixture_declaring_factory_does_not_receive_request_bundle(self) -> None:
        seen: list[object] = []
        spec = _request_bundle_spec(declares=True, seen=seen)
        graph = _compile_custom(
            spec,
            NodeAdapter(_fixture_factory(seen, "request_bundle"), AdapterKind.FIXTURE, requires_gate=False),
        )
        await graph.ainvoke(_state(), config=_config(), context=_context(None, request_bundle=_FakeRequestStore()))
        assert seen == [None]

    async def test_dependency_request_bundle_without_declaration_fails(self) -> None:
        seen: list[object] = []
        spec = _request_bundle_spec(declares=False, seen=seen)
        graph = _compile_custom(spec, NodeAdapter(spec.real_factory, AdapterKind.REAL, requires_gate=False))
        with pytest.raises(ValueError, match="request_bundle_capability_undeclared"):
            await graph.ainvoke(
                _state(),
                config=_config(),
                context=_context(None, resolver_request_bundle=_FakeRequestStore()),
            )
        assert seen == []
