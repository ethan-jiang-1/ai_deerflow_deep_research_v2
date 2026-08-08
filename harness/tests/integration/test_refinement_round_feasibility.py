"""Fixture-only proof of the production rerun writer's checkpoint behavior.

@impl REG-021
"""

from __future__ import annotations

from contextlib import aclosing
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from deerflow_deep_research.domain.bundle import RunBundleRef, run_bundle_root
from deerflow_deep_research.domain.context import GraphContextView, NodeAgentContext
from deerflow_deep_research.domain.invocation import GraphInvocationContext
from deerflow_deep_research.domain.node_spec import NodeBuildDependencies
from deerflow_deep_research.domain.state import PhaseStatus, node_state_update
from deerflow_deep_research.runtime.bundle_lifecycle import BundleLifecycle
from tests.fixtures.recipes import fixture_recipe


class _ForbiddenExternalCapabilities:
    async def run_agent(self, *, context, request):  # noqa: ANN001, ARG002
        raise AssertionError("graph feasibility probe must not call a model or provider")


@dataclass
class _RecordingResolver:
    graph_context: GraphContextView
    calls: list[str] = field(default_factory=list)

    def resolve(self, *, logical_name, attempt_id, policy):  # noqa: ANN001
        self.calls.append(logical_name)
        return NodeBuildDependencies(
            graph_context=self.graph_context,
            agent_context=NodeAgentContext(
                research_scope_id=self.graph_context.research_scope_id,
                node_name=logical_name,
                attempt_id=attempt_id,
                workspace_root=self.graph_context.workspace_root,
                attempt_root=f"{self.graph_context.workspace_root}/{attempt_id}",
                policy_name=policy.name,
            ),
            capabilities=_ForbiddenExternalCapabilities(),
        )


def _terminal_snapshot(bundle: RunBundleRef) -> dict[str, object]:
    return {
        "schema_version": 2,
        "bundle_id": bundle.bundle_id.value,
        "start_message_id": "fixture-start",
        "request_digest": "d_" + "R" * 43,
        "request_text": "Fixture terminal snapshot.",
        "phase": "final_delivery",
        "route": "pass",
        "phase_status": PhaseStatus.TERMINAL.value,
        "terminal_status": "completed",
        "generation": 0,
        "repair_counts": {},
        "wave0_results": (),
        "wave1_results": (),
        "consumed_request_ids": (),
        "consumed_message_ids": (),
        "execution_trace": ("final_delivery",),
    }


def _full_rerun_update(*, terminal_generation: int) -> dict[str, object]:
    return {
        **node_state_update("rerun", route="topic_planning"),
        "synthesis_ref": None,
        "decision_brief_ref": None,
        "report_refs": (),
        "repair_counts": {},
        "hitl2_rerun_payload": None,
        "generation": terminal_generation + 1,
        "parent_generation": terminal_generation,
        "pending_work_ids": (),
        "active_topic_filter": (),
        "gate_attempts_by_phase": {},
        "repair_budget_by_phase": {},
        "rerun_scope": "full",
        "rerun_reason": "fixture probe",
        "phase_status": PhaseStatus.WAITING.value,
        "terminal_status": None,
        "terminal_reason": None,
    }


def _sqlite_relative_paths(tmp_path: Path) -> set[str]:
    return {path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*.sqlite")}


@pytest.mark.asyncio
async def test_rerun_writer_prepares_same_bundle_topic_planning_without_precommit_execution(tmp_path: Path) -> None:
    """REG-021: the production writer queues the existing rerun edge without running it."""

    lifecycle = BundleLifecycle(workspace_host_path=tmp_path)
    bundle = await lifecycle.start(scope=("fixture-user", "fixture-thread"), request_text="Fixture question.")
    root = lifecycle.private_root(bundle)
    graph_context = GraphContextView(
        research_scope_id=bundle.bundle_id.value,
        workspace_root=f"/mnt/user-data/{run_bundle_root(bundle)}",
        uploads_root="/mnt/user-data/uploads",
        outputs_root="/mnt/user-data/outputs/deep-research",
    )
    resolver = _RecordingResolver(graph_context)
    context = GraphInvocationContext(graph_context, resolver)
    config = {"configurable": {"thread_id": bundle.bundle_id.value, "checkpoint_ns": ""}}

    async with lifecycle.open_graph_checkpoint(bundle) as saver:
        graph = fixture_recipe().builder.compile(checkpointer=saver)
        await graph.aupdate_state(config, _terminal_snapshot(bundle), as_node="final_delivery")
        terminal = await graph.aget_state(config)

        assert terminal.values["bundle_id"] == bundle.bundle_id.value
        assert terminal.values["phase"] == "final_delivery"
        assert terminal.values["terminal_status"] == "completed"
        assert terminal.next == ()
        assert resolver.calls == []
        assert {path.name for path in root.parent.iterdir() if path.is_dir()} == {bundle.bundle_id.value}
        assert _sqlite_relative_paths(tmp_path) == {(root / "graph.sqlite").relative_to(tmp_path).as_posix()}

        await lifecycle.sync_graph_progress(bundle=bundle, values=dict(terminal.values), pending=None)
        state_before_preparation = await lifecycle.read_state(bundle)
        files_before_preparation = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}

        await graph.aupdate_state(
            config,
            _full_rerun_update(terminal_generation=int(terminal.values["generation"])),
            as_node="rerun",
        )
        prepared = await graph.aget_state(config)

        assert prepared.values["bundle_id"] == bundle.bundle_id.value
        assert prepared.values["generation"] == 1
        assert prepared.values["phase"] == "rerun"
        assert prepared.values["route"] == "topic_planning"
        assert prepared.next == ("topic_planning",)
        assert [task.name for task in prepared.tasks] == ["topic_planning"]
        assert resolver.calls == []
        assert not prepared.values.get("topic_refs")
        assert not prepared.values.get("report_refs")
        assert await lifecycle.read_state(bundle) == state_before_preparation
        assert {
            path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()
        } == files_before_preparation

        # A prepared checkpoint alone is not a public lifecycle transition.  The
        # later Bundle-bound round protocol owns the matching State CAS.
        precommit_projection = await lifecycle.sync_graph_progress(
            bundle=bundle,
            values=dict(prepared.values),
            pending=None,
        )
        assert precommit_projection == state_before_preparation

        async with aclosing(graph.astream(None, config=config, context=context, stream_mode="updates")) as updates:
            first_update = await anext(updates)

    assert tuple(first_update) == ("topic_planning",)
    assert resolver.calls == ["topic_planning"]
