"""One mixed same-Bundle direction-to-planning workflow.

@impl DRH-005
@impl TOP-006
@impl TOP-008
"""

from __future__ import annotations

import json
import secrets
import time
from dataclasses import replace
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage

from deerflow_deep_research.agents.capabilities import load_node_agent_capability
from deerflow_deep_research.domain.lifecycle import ImplementationMode, LifecycleStatus
from deerflow_deep_research.domain.profile import ResearchProfile, profile_state_fields
from deerflow_deep_research.domain.state import PhaseStatus
from deerflow_deep_research.graph.nodes.topic_planning.capabilities import TOPIC_PLANNING_PROFILE_DECOMPOSITION
from deerflow_deep_research.runtime.bootstrap_bundle import BootstrapBundleStore
from deerflow_deep_research.runtime.bundle_graph import BundleGraphExecutor
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from deerflow_deep_research.runtime.node_agent_bridge import RuntimeNodeAgentBridge
from deerflow_deep_research.runtime.request_bundle import RequestBundleStore
from deerflow_deep_research.runtime.work_unit_storage_probe import WorkUnitStorageCheck
from deerflow_deep_research.runtime.work_unit_store import WorkUnitStore
from tests.fixtures.fake_models import CapturingChatModel, ai_message
from tests.fixtures.recipes import mixed_recipe
from tests.fixtures.runtime import local_runtime_envelope


def _topic_plan() -> str:
    return json.dumps(
        {
            "schema_version": 1,
            "topics": [
                {
                    "title": "Grid storage safety evidence",
                    "scope": "Stationary grid storage safety incidents and mitigations",
                    "must_answer_bindings": ["Which safety risks should a grid-storage decision address?"],
                    "search_dimensions": ["incident evidence", "mitigation evidence"],
                    "exclusions": ["Passenger electric vehicles"],
                }
            ],
        }
    )


def _profile() -> ResearchProfile:
    return ResearchProfile(
        schema_version=2,
        depth="deep_dive",
        audience="practitioner",
        format="detailed_report",
        cost_tolerance="moderate",
        time_budget="thorough",
        must_answer=("Which safety risks should a grid-storage decision address?",),
        scope_boundaries="Grid-connected stationary storage only; exclude passenger vehicles.",
        custom_notes="Keep lifecycle trade-offs visible alongside incident evidence.",
        comparison_required=False,
        request_language="en",
        output_language="en",
    )


class _FixtureRuntimeAdapter:
    def __init__(self, envelope: object) -> None:
        self.envelope = envelope
        self.initialization: list[bool] = []

    async def adapt(self, _runtime: object, *, initialize_parent_sandbox: bool = True) -> object:
        self.initialization.append(initialize_parent_sandbox)
        return self.envelope


class _TopicPlanningBridgeFactory:
    def __init__(self) -> None:
        self.models: list[CapturingChatModel] = []
        self.policies: list[object] = []
        self.tool_resolution_attempts = 0

    def __call__(self, *, envelope: object, policy: object, tools_resolver: object) -> RuntimeNodeAgentBridge:
        del tools_resolver
        self.policies.append(policy)
        model = CapturingChatModel(reply=ai_message(_topic_plan()), seen=[])
        self.models.append(model)

        def tools_must_not_resolve(_envelope: object, _policy: object) -> tuple[object, ...]:
            self.tool_resolution_attempts += 1
            raise AssertionError("topic planning resolved a zero-tool capability")

        return RuntimeNodeAgentBridge(
            envelope=envelope,
            policy=policy,
            model_resolver=lambda _envelope: model,
            tools_resolver=tools_must_not_resolve,
        )


async def _work_unit_store(envelope: object, *, bundle: object, **_kwargs: object) -> WorkUnitStore:
    return WorkUnitStore(
        workspace_host_path=envelope.workspace_host_path,
        bundle=bundle,
        clock=lambda: datetime(2026, 8, 7, tzinfo=UTC),
        monotonic=time.monotonic,
        lock_sleep=time.sleep,
        token_factory=lambda: secrets.token_hex(16),
        fault_hook=None,
    )


async def _storage_ready(*_args: object, **_kwargs: object) -> WorkUnitStorageCheck:
    return WorkUnitStorageCheck("ready", "local_thread_mount")


async def _request_bundle_store(envelope: object, *, bundle: object, **_kwargs: object) -> RequestBundleStore:
    return await RequestBundleStore.create(envelope, bundle=bundle, storage_verifier=_storage_ready)


async def _stage_terminal_round(
    *,
    lifecycle: BundleLifecycle,
    bundle: object,
    executor: BundleGraphExecutor,
    profile_fields: dict[str, object],
) -> None:
    config = executor._config(bundle)
    async with lifecycle.open_graph_checkpoint(bundle) as saver:
        graph = executor._recipe.builder.compile(checkpointer=saver)
        await graph.aupdate_state(
            config,
            {
                "schema_version": 3,
                "bundle_id": bundle.bundle_id.value,
                "start_message_id": "fixture-start",
                "request_digest": "d_" + "R" * 43,
                "request_text": "Research grid-scale storage safety.",
                "phase": "final_delivery",
                "route": "pass",
                "phase_status": PhaseStatus.TERMINAL.value,
                "terminal_status": LifecycleStatus.COMPLETED.value,
                "generation": 0,
                "wave0_results": (),
                "wave1_results": (),
                "consumed_request_ids": (),
                "consumed_message_ids": (),
                "execution_trace": ("final_delivery",),
                **profile_fields,
            },
            as_node="final_delivery",
        )
        terminal = await graph.aget_state(config)
    await lifecycle.sync_graph_progress(bundle=bundle, values=dict(terminal.values), pending=None)


@pytest.mark.workflow
async def test_public_refine_applies_one_direction_to_canonical_profile_topic_planning(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A public direction reaches one real planner in the same Bundle, not a quality claim."""
    envelope = local_runtime_envelope(tmp_path)
    lifecycle = BundleLifecycle(workspace_host_path=envelope.workspace_host_path)
    scope = (envelope.effective_user_id, envelope.outer_thread_id)
    bundle = await lifecycle.start(
        scope=scope,
        request_text="Research grid-scale storage safety.",
        implementation_mode=ImplementationMode.MIXED,
    )
    profile = _profile()
    request_store = await RequestBundleStore.create(envelope, bundle=bundle, storage_verifier=_storage_ready)
    profile_ref = await request_store.write_profile(profile)
    baseline = await request_store.read_bundle_state()
    profile_fields = profile_state_fields(profile, profile_ref)
    await request_store.write_bundle_state(
        replace(baseline, **profile_fields),
        expected_revision=baseline.revision,
    )

    bridge_factory = _TopicPlanningBridgeFactory()

    async def bootstrap_store_without_provider(_cls: object, runtime_envelope: object, *, bundle: object) -> object:
        return BootstrapBundleStore(workspace_host_path=runtime_envelope.workspace_host_path, bundle=bundle)

    from deerflow_deep_research.runtime import bundle_graph as bundle_graph_module

    monkeypatch.setattr(
        bundle_graph_module.BootstrapBundleStore,
        "create",
        classmethod(bootstrap_store_without_provider),
    )
    executor = BundleGraphExecutor(
        recipe=mixed_recipe(
            real_nodes=("bootstrap", "hitl1", "topic_planning"),
            work_unit_store_factory=_work_unit_store,
            request_bundle_store_factory=_request_bundle_store,
            node_agent_bridge_factory=bridge_factory,
        )
    )
    await _stage_terminal_round(
        lifecycle=lifecycle,
        bundle=bundle,
        executor=executor,
        profile_fields=profile_fields,
    )

    profile_reads: list[tuple[object, object]] = []
    original_read_profile = RequestBundleStore.read_profile

    async def observe_profile_read(self: RequestBundleStore, ref: object) -> ResearchProfile:
        profile_reads.append((self.bundle, ref))
        return await original_read_profile(self, ref)

    monkeypatch.setattr(RequestBundleStore, "read_profile", observe_profile_read)

    from deerflow_deep_research import tool as public_tool

    adapter = _FixtureRuntimeAdapter(envelope)
    runtime = SimpleNamespace(
        state={
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "deep_research",
                            "args": {
                                "action": "refine",
                                "bundle_id": bundle.bundle_id.value,
                                "refinement": "Give documented safety incidents additional focus.",
                            },
                            "id": "direction-effect-refine",
                        }
                    ],
                )
            ]
        },
        context={},
        tool_call_id="direction-effect-refine",
    )
    monkeypatch.setattr(public_tool, "RuntimeAdapter", lambda: adapter)
    monkeypatch.setattr(public_tool, "_production_bundle_graph_executor", lambda: executor)

    assert public_tool.deep_research_tool.coroutine is not None
    payload = json.loads(
        await public_tool.deep_research_tool.coroutine(
            action="refine",
            bundle_id=bundle.bundle_id.value,
            refinement="Give documented safety incidents additional focus.",
            runtime=runtime,
        )
    )

    state = await lifecycle.read_state(bundle)
    async with lifecycle.open_graph_checkpoint(bundle) as saver:
        snapshot = await executor._recipe.builder.compile(checkpointer=saver).aget_state(executor._config(bundle))

    assert payload["code"] == "refinement_applied"
    assert payload["bundle_id"] == bundle.bundle_id.value
    assert state.bundle_id == bundle.bundle_id
    assert state.current_refinement is not None
    assert state.current_refinement.text == "Give documented safety incidents additional focus."
    assert state.generation == 1
    assert snapshot.values["bundle_id"] == bundle.bundle_id.value
    assert tuple(snapshot.values["topic_refs"]) == ("grid-storage-safety-evidence",)
    assert profile_reads == [(bundle, profile_ref)]
    assert adapter.initialization == [False]
    assert bridge_factory.tool_resolution_attempts == 0
    planner_models = [
        model
        for policy, model in zip(bridge_factory.policies, bridge_factory.models, strict=True)
        if policy.policy_name == "topic-planning-structured-plan"
    ]
    assert len(planner_models) == 1
    assert all(policy.allowed_tool_names == frozenset() for policy in bridge_factory.policies)

    rendered_messages = planner_models[0].seen[0]
    assert load_node_agent_capability(TOPIC_PLANNING_PROFILE_DECOMPOSITION).policy.strip() in rendered_messages[0]
    for value in (
        profile.scope_boundaries,
        profile.custom_notes,
        "Give documented safety incidents additional focus.",
    ):
        assert value in rendered_messages[1]
