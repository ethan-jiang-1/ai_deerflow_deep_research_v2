"""Runtime recipe and node-capability contracts.

These tests exercise graph composition and policy construction only.  Bundle
lifecycle selection belongs to ``runtime.bundle_lifecycle`` and is covered at
that boundary rather than through the retired action-handler API.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from deerflow_deep_research.agents.policies import ProviderObservationAdmission
from deerflow_deep_research.domain.bundle import BundleId, RunBundleRef
from deerflow_deep_research.domain.lifecycle import ImplementationMode
from deerflow_deep_research.runtime.node_agent_bridge import RuntimeNodeAgentBridge
from deerflow_deep_research.runtime.projection import project_research_scope
from deerflow_deep_research.runtime.research import ResearchGraphRecipe
from deerflow_deep_research.runtime.runtime_adapter import TrustedRuntimeEnvelope
from tests.fixtures.recipes import fixture_recipe, mixed_recipe

_BUNDLE_ID = "b_" + "A" * 43
_BUNDLE = RunBundleRef(bundle_id=BundleId(_BUNDLE_ID), scope_bucket="s_" + "B" * 43)


class _FakeAppConfig:
    checkpointer = None
    database = None


class _Sandbox:
    id = "sandbox-1"
    sandbox_id = "sandbox-1"


def _envelope() -> TrustedRuntimeEnvelope:
    return TrustedRuntimeEnvelope(
        effective_user_id="alice",
        outer_thread_id="thread-1",
        outer_run_id="run-1",
        app_config=_FakeAppConfig(),
        workspace_host_path=Path("/tmp/users/alice/workspace"),
        uploads_host_path=Path("/tmp/users/alice/uploads"),
        outputs_host_path=Path("/tmp/users/alice/outputs"),
        workspace_virtual_root="/mnt/user-data/workspace",
        uploads_virtual_root="/mnt/user-data/uploads",
        outputs_virtual_root="/mnt/user-data/outputs",
        parent_sandbox=_Sandbox(),
    )


def _graph_context():
    return project_research_scope(_envelope(), bundle=_BUNDLE)


def test_recipe_detects_real_hitl1_and_requires_real_bootstrap() -> None:
    recipe = mixed_recipe(real_nodes=("bootstrap", "hitl1"))
    assert recipe.requires_bootstrap_bundle is True
    assert recipe.requires_request_bundle is True
    assert recipe.requires_node_agent_bridge is True

    with pytest.raises(ValueError, match="hitl1_real_requires_bootstrap_real"):
        mixed_recipe(real_nodes=("hitl1",))


def test_recipe_compatibility_fingerprint_is_stable_and_detects_implementation_drift() -> None:
    first = fixture_recipe()
    second = fixture_recipe()
    changed = mixed_recipe(real_nodes=("bootstrap", "hitl1"))

    assert first.compatibility_fingerprint == second.compatibility_fingerprint
    assert first.compatibility_fingerprint != changed.compatibility_fingerprint
    assert first.implementation_mode is ImplementationMode.FIXTURE
    assert changed.implementation_mode is ImplementationMode.MIXED


def test_all_real_recipe_compiles() -> None:
    recipe = ResearchGraphRecipe.all_real()
    assert recipe.implementation_mode is ImplementationMode.ALL_REAL
    assert recipe.requires_publication_bundle is True
    assert recipe.requires_final_delivery_bundle is True
    assert recipe.builder.compile() is not None


def test_recipe_requires_predecessor_real_nodes() -> None:
    with pytest.raises(ValueError, match="topic_planning_real_requires_hitl1_real"):
        mixed_recipe(real_nodes=("topic_planning",))
    with pytest.raises(ValueError, match="wave0_real_requires_topic_planning_real"):
        mixed_recipe(real_nodes=("wave0",))
    with pytest.raises(ValueError, match="wave1_real_requires_wave0_and_targeted_evidence_real"):
        mixed_recipe(real_nodes=("wave1",))
    with pytest.raises(ValueError, match="hitl2_real_requires_wave2_synthesis_real"):
        mixed_recipe(real_nodes=("hitl2",))


def test_worker_policies_specify_every_allowed_tool() -> None:
    from deerflow_deep_research.runtime.research import _wave0_worker_policy, _wave1_worker_policy

    for policy in (_wave0_worker_policy(_graph_context()), _wave1_worker_policy(_graph_context())):
        assert policy.allowed_tool_names
        for tool_name in policy.allowed_tool_names:
            spec = policy.spec_for(tool_name)
            assert spec is not None, f"{policy.policy_name}: missing spec for {tool_name}"
            assert spec.is_eligible, f"{policy.policy_name}: ineligible spec for {tool_name}"


def test_all_real_context_routes_distinct_worker_policies() -> None:
    from deerflow_deep_research.runtime.research import _build_wave0_capabilities, _build_wave1_capabilities

    envelope = _envelope()
    graph_context = _graph_context()
    wave0 = _build_wave0_capabilities(envelope, graph_context, None)
    wave1 = _build_wave1_capabilities(envelope, graph_context, None)

    assert isinstance(wave0, RuntimeNodeAgentBridge)
    assert isinstance(wave1, RuntimeNodeAgentBridge)
    assert wave0.policy.policy_name == "wave0-source-intake"
    assert wave1.policy.policy_name == "wave1-evidence-extraction"
    assert wave0.policy is not wave1.policy


def test_zero_tool_policies_remain_independently_bounded() -> None:
    from deerflow_deep_research.runtime.research import (
        _final_delivery_node_agent_policy,
        _hitl1_node_agent_policy,
        _readiness_node_agent_policy,
        _topic_planning_node_agent_policy,
        _wave2_synthesis_node_agent_policy,
    )

    graph_context = _graph_context()
    policies = (
        _hitl1_node_agent_policy(graph_context),
        _topic_planning_node_agent_policy(graph_context),
        _readiness_node_agent_policy(graph_context),
        _wave2_synthesis_node_agent_policy(graph_context),
        _final_delivery_node_agent_policy(graph_context),
    )

    assert all(policy.allowed_tool_names == frozenset() for policy in policies)
    assert all(policy.budget.max_model_calls >= 1 for policy in policies)
    assert policies[0].provider_observation_admission is ProviderObservationAdmission.CONFIGURED_MODEL_SERVICE
    assert policies[1].provider_observation_admission is ProviderObservationAdmission.CONFIGURED_MODEL_SERVICE
    assert policies[2].provider_observation_admission is ProviderObservationAdmission.DENIED
    assert len({policy.policy_name for policy in policies}) == len(policies)


def test_topic_planning_policy_has_its_own_calibrated_output_envelope() -> None:
    """@impl TOP-010

    Planning alone carries the wider retained structured candidate.
    """
    from deerflow_deep_research.runtime.research import _topic_planning_node_agent_policy

    policy = _topic_planning_node_agent_policy(_graph_context())

    assert policy.allowed_tool_names == frozenset()
    assert policy.budget.max_model_calls == 1
    assert policy.budget.per_call_output_token_cap == 4_096
    assert policy.budget.structured_result_bytes == 16_384
    assert policy.budget.total_token_budget == 12_288
    assert policy.budget.wall_time_seconds == 60.0
