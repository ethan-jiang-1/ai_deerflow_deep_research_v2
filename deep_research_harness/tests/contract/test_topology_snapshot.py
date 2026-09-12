from pathlib import Path

from deerflow_deep_research.domain.identifiers import LOGICAL_NODE_SUMMARIES, LogicalPhase
from deerflow_deep_research.graph.topology_snapshot import render_topology_snapshot

AGENT_ROOT = Path(__file__).resolve().parents[2]
NODES_ROOT = AGENT_ROOT / "src" / "deerflow_deep_research" / "graph" / "nodes"


def test_committed_topology_snapshot_matches_normalized_semantics() -> None:
    target = AGENT_ROOT / "docs" / "deep-research-topology.md"
    assert target.read_text(encoding="utf-8") == render_topology_snapshot()
    text = target.read_text(encoding="utf-8")
    assert "dispatch" not in text and "join" not in text
    assert "final_delivery --evidence_blocked--> readiness" in text


def test_workflow_md_titles_project_canonical_node_summaries() -> None:
    for logical_name, summary in LOGICAL_NODE_SUMMARIES.items():
        workflow = NODES_ROOT / logical_name.value / "workflow.md"
        first_line = workflow.read_text(encoding="utf-8").splitlines()[0]
        title, separator, projected = first_line.partition(" — ")
        assert title == f"# {logical_name.value}", f"workflow.md H1 name mismatch: {workflow}"
        assert separator, f"workflow.md H1 lacks em-dash summary: {workflow}"
        assert projected == summary, (
            f"workflow.md H1 summary drift for {logical_name.value}: {projected!r} != {summary!r}"
        )


def test_canonical_summaries_render_into_generated_snapshot() -> None:
    text = render_topology_snapshot()
    for logical_name, summary in LOGICAL_NODE_SUMMARIES.items():
        assert f"- `{logical_name.value}` — {summary}" in text
    assert LogicalPhase.WAVE0.value in text
