"""Red tests for max_rerun_generations policy and generation validation.

@impl REN-005

The fixture rerun generation regression (generation 0/1/2 routes through the
bounded fixture policy) is covered by tests/unit/test_rerun_e2e.py
(TestFixtureRerunRegression) and intentionally not duplicated here.
"""

from __future__ import annotations

import pytest

from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.state import ResearchGraphState


class TestMaxRerunGenerationsPolicy:
    def test_node_build_dependencies_has_default(self) -> None:
        """NodeBuildDependencies carries max_rerun_generations with default 2."""
        from deerflow_deep_research.domain.context import GraphContextView, NodeAgentContext

        deps = NodeBuildDependencies(
            graph_context=GraphContextView(
                research_scope_id="b_" + "A" * 43,
                workspace_root="/tmp/ws",
                uploads_root="/tmp/up",
                outputs_root="/tmp/out",
            ),
            agent_context=NodeAgentContext(
                research_scope_id="b_" + "A" * 43,
                node_name="rerun",
                attempt_id="a1",
                workspace_root="/tmp/ws",
                attempt_root="/tmp/ws/rerun",
                policy_name="skeleton-rerun",
            ),
            capabilities=object(),
        )
        # Default should be 2 (from MAX_RERUN_GENERATIONS)
        assert deps.max_rerun_generations == 2

    def test_node_build_dependencies_custom_value(self) -> None:
        """max_rerun_generations can be overridden."""
        from deerflow_deep_research.domain.context import GraphContextView, NodeAgentContext

        deps = NodeBuildDependencies(
            graph_context=GraphContextView(
                research_scope_id="b_" + "A" * 43,
                workspace_root="/tmp/ws",
                uploads_root="/tmp/up",
                outputs_root="/tmp/out",
            ),
            agent_context=NodeAgentContext(
                research_scope_id="b_" + "A" * 43,
                node_name="rerun",
                attempt_id="a1",
                workspace_root="/tmp/ws",
                attempt_root="/tmp/ws/rerun",
                policy_name="skeleton-rerun",
            ),
            capabilities=object(),
            max_rerun_generations=3,
        )
        assert deps.max_rerun_generations == 3

    def test_runtime_resolver_threads_one_policy_instance_to_rerun_dependencies(self) -> None:
        from deerflow_deep_research.domain.context import GraphContextView
        from deerflow_deep_research.domain.node_spec import PolicyRef
        from deerflow_deep_research.graph.nodes.rerun.planner import FullRerunPolicy
        from deerflow_deep_research.runtime.research import RuntimeNodeDependencyResolver

        policy = FullRerunPolicy(max_rerun_generations=1)
        resolver = RuntimeNodeDependencyResolver(
            GraphContextView(
                research_scope_id="b_" + "A" * 43,
                workspace_root="/tmp/ws",
                uploads_root="/tmp/up",
                outputs_root="/tmp/out",
            ),
            full_rerun_policy=policy,
        )

        dependencies = resolver.resolve(
            logical_name="rerun",
            attempt_id="a1",
            policy=PolicyRef(name="skeleton-rerun", version="v1"),
        )

        assert dependencies.full_rerun_policy is policy
        assert dependencies.max_rerun_generations == 1


class TestGenerationValidation:
    def test_generation_0_valid(self) -> None:
        """Generation 0 is always valid."""
        ck = ResearchGraphState(
            bundle_id="b_" + "A" * 43,
            outer_thread_id="thread-1",
            generation=0,
        )
        assert ck.generation == 0

    def test_generation_1_valid(self) -> None:
        """Generation 1 is valid (first rerun)."""
        ck = ResearchGraphState(
            bundle_id="b_" + "A" * 43,
            outer_thread_id="thread-1",
            generation=1,
        )
        assert ck.generation == 1

    def test_generation_3_valid_no_longer_bounded(self) -> None:
        """Generation 3 is now valid — upper bound removed from __post_init__."""
        ck = ResearchGraphState(
            bundle_id="b_" + "A" * 43,
            outer_thread_id="thread-1",
            generation=3,
        )
        assert ck.generation == 3

    def test_generation_negative_raises(self) -> None:
        """Negative generation is still invalid."""
        with pytest.raises(ValueError, match="generation_invalid"):
            ResearchGraphState(
                bundle_id="b_" + "A" * 43,
                outer_thread_id="thread-1",
                generation=-1,
            )
