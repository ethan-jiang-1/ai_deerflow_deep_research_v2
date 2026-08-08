"""Syntax-discovered real-bridge workflow ownership contracts.

@impl EVH-008
@impl EVH-009
@impl WFO-002
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from scripts.check_test_assets import collect_pytest_selectors
from tests.assets.evidence import (
    EVIDENCE_CLAIMS,
    AssetClass,
    AuthenticityLevel,
    FocusedSelection,
    StableSeam,
    claim_index,
)
from tests.assets.selection import (
    FAST_EXPRESSION,
    FAST_PATHS,
    INTEGRATION_EXPRESSION,
    INTEGRATION_PATHS,
    WORKFLOW_EXPRESSION,
    WORKFLOW_PATHS,
)
from tests.assets.workflow_nodes import (
    MODEL_WORKFLOW_COVERAGE,
    WorkflowCoverageError,
    WorkflowOutcomeClass,
    discover_run_agent_owners,
    validate_model_workflow_coverage,
)

NODE_ROOT = Path("src/deerflow_deep_research/graph/nodes")
EXPECTED_OWNERS = {
    "hitl1",
    "topic_planning",
    "wave0",
    "wave1",
    "wave2_synthesis",
    "targeted_evidence",
    "readiness",
    "final_delivery",
}


def _collect_focused_selectors() -> dict[FocusedSelection, set[str]]:
    return {
        FocusedSelection.FAST: collect_pytest_selectors(
            paths=FAST_PATHS,
            expression=FAST_EXPRESSION,
            label="workflow inventory fast",
        ),
        FocusedSelection.INTEGRATION: collect_pytest_selectors(
            paths=INTEGRATION_PATHS,
            expression=INTEGRATION_EXPRESSION,
            label="workflow inventory integration",
        ),
        FocusedSelection.WORKFLOW: collect_pytest_selectors(
            paths=WORKFLOW_PATHS,
            expression=WORKFLOW_EXPRESSION,
            label="workflow inventory workflow",
        ),
    }


def test_ast_discovery_finds_exact_loaded_run_agent_owners() -> None:
    assert discover_run_agent_owners(NODE_ROOT) == EXPECTED_OWNERS


def test_every_discovered_owner_has_success_and_failure_outcome_evidence() -> None:
    claims = claim_index(EVIDENCE_CLAIMS)

    validate_model_workflow_coverage(
        MODEL_WORKFLOW_COVERAGE,
        claims=claims,
        discovered_owners=discover_run_agent_owners(NODE_ROOT),
        focused_selectors=_collect_focused_selectors(),
    )

    assert {entry.logical_name for entry in MODEL_WORKFLOW_COVERAGE} == EXPECTED_OWNERS
    assert {outcome.outcome_class for entry in MODEL_WORKFLOW_COVERAGE for outcome in entry.outcome_evidence} == {
        WorkflowOutcomeClass.KNOWN_INVOCATION_FAILURE
    }


def test_direct_lifecycle_projection_can_use_a_deterministic_non_agent_claim() -> None:
    entry = next(entry for entry in MODEL_WORKFLOW_COVERAGE if entry.logical_name == "hitl1")
    projection = claim_index(EVIDENCE_CLAIMS)[entry.outcome_evidence[0].projection_claim_id]

    assert projection.asset_class is AssetClass.CODE_CORRECTNESS
    assert projection.seam is StableSeam.LIFECYCLE_MIXED_GRAPH
    assert projection.authenticity is None
    validate_model_workflow_coverage(
        MODEL_WORKFLOW_COVERAGE,
        claims=claim_index(EVIDENCE_CLAIMS),
        discovered_owners=EXPECTED_OWNERS,
        focused_selectors=_collect_focused_selectors(),
    )


@pytest.mark.parametrize("field", ["asset_class", "authenticity"])
def test_downgraded_workflow_claim_reports_node_id(field: str) -> None:
    claims = claim_index(EVIDENCE_CLAIMS)
    entry = MODEL_WORKFLOW_COVERAGE[0]
    claim = claims[entry.claim_id]
    downgraded = replace(
        claim,
        **(
            {"asset_class": AssetClass.CODE_CORRECTNESS, "expected_selection": FocusedSelection.FAST}
            if field == "asset_class"
            else {"authenticity": AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES}
        ),
    )
    claims[entry.claim_id] = downgraded

    with pytest.raises(WorkflowCoverageError, match=entry.logical_name):
        validate_model_workflow_coverage(
            MODEL_WORKFLOW_COVERAGE,
            claims=claims,
            discovered_owners=EXPECTED_OWNERS,
            focused_selectors=_collect_focused_selectors(),
        )


def test_missing_workflow_selector_reports_node_id() -> None:
    claims = claim_index(EVIDENCE_CLAIMS)
    entry = MODEL_WORKFLOW_COVERAGE[0]
    focused_selectors = _collect_focused_selectors()
    focused_selectors[FocusedSelection.WORKFLOW] = set()

    with pytest.raises(WorkflowCoverageError, match=entry.logical_name):
        validate_model_workflow_coverage(
            MODEL_WORKFLOW_COVERAGE,
            claims=claims,
            discovered_owners=EXPECTED_OWNERS,
            focused_selectors=focused_selectors,
        )


def test_missing_discovered_owner_reports_node_id() -> None:
    entries = MODEL_WORKFLOW_COVERAGE[1:]

    with pytest.raises(WorkflowCoverageError, match="hitl1: discovered run_agent owner lacks workflow coverage"):
        validate_model_workflow_coverage(
            entries,
            claims=claim_index(EVIDENCE_CLAIMS),
            discovered_owners=EXPECTED_OWNERS,
            focused_selectors=_collect_focused_selectors(),
        )


def test_missing_declared_outcome_class_reports_node_id() -> None:
    entry = MODEL_WORKFLOW_COVERAGE[0]
    entries = (replace(entry, outcome_evidence=()), *MODEL_WORKFLOW_COVERAGE[1:])

    with pytest.raises(WorkflowCoverageError, match="hitl1: missing declared outcome class"):
        validate_model_workflow_coverage(
            entries,
            claims=claim_index(EVIDENCE_CLAIMS),
            discovered_owners=EXPECTED_OWNERS,
            focused_selectors=_collect_focused_selectors(),
        )


@pytest.mark.parametrize("role", ["phase", "projection"])
def test_stale_outcome_selector_reports_owner_and_evidence_role(role: str) -> None:
    entry = MODEL_WORKFLOW_COVERAGE[0]
    outcome = entry.outcome_evidence[0]
    claim_id = outcome.phase_claim_id if role == "phase" else outcome.projection_claim_id
    claims = claim_index(EVIDENCE_CLAIMS)
    claim = claims[claim_id]
    claims[claim_id] = replace(
        claim,
        selector="tests/graph/test_stale_workflow_outcome.py::test_missing_outcome_evidence",
    )

    with pytest.raises(
        WorkflowCoverageError,
        match=rf"hitl1: {outcome.outcome_class.value} {role} selector is stale",
    ):
        validate_model_workflow_coverage(
            MODEL_WORKFLOW_COVERAGE,
            claims=claims,
            discovered_owners=EXPECTED_OWNERS,
            focused_selectors=_collect_focused_selectors(),
        )


def test_known_violation_smoke_rejects_empty_or_mis_scoped_discovery(tmp_path: Path) -> None:
    empty_root = tmp_path / "nodes"
    empty_root.mkdir()

    discovered = discover_run_agent_owners(empty_root)
    assert discovered == set()
    with pytest.raises(WorkflowCoverageError, match="hitl1"):
        validate_model_workflow_coverage(
            MODEL_WORKFLOW_COVERAGE,
            claims=claim_index(EVIDENCE_CLAIMS),
            discovered_owners=discovered,
            focused_selectors=_collect_focused_selectors(),
        )


def test_ast_classification_accepts_call_and_method_reference_but_not_name_or_store(tmp_path: Path) -> None:
    root = tmp_path / "nodes"
    for owner, source in {
        "direct": "async def run(c):\n    return await c.run_agent()\n",
        "reference": "def bind(c):\n    return consume(c.run_agent)\n",
        "name_only": "def run_agent():\n    return None\n",
        "store_only": "def bind(c):\n    c.run_agent = None\n",
    }.items():
        package = root / owner
        package.mkdir(parents=True)
        (package / "node.py").write_text(source, encoding="utf-8")

    assert discover_run_agent_owners(root) == {"direct", "reference"}
