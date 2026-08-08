"""Focused collection and central-claim checker contracts.

@impl EVH-006
@impl EVH-009
@impl EVH-011
@impl DER-001
"""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from deerflow_deep_research.graph.topology import LOGICAL_NODES
from scripts import check_test_assets
from scripts.check_node_workflows import load_reader_inventory
from scripts.check_test_assets import collect_pytest_selectors
from tests.assets.cognitive_program_board import COGNITIVE_PROGRAM_BOARD
from tests.assets.evidence import (
    EVIDENCE_CLAIMS,
    AssetClass,
    EvidenceClaimError,
    FocusedSelection,
    StableSeam,
    TestEvidenceClaim,
    claim_index,
    validate_claim_selections,
)
from tests.assets.inventory import CoverageError
from tests.assets.node_agent_capabilities import COHORT_EVIDENCE
from tests.assets.node_conformance import NODE_CONFORMANCE
from tests.assets.requirement_evidence import (
    REQUIREMENT_IMPACTS,
    ConsolidationDecision,
    RequirementEvidenceError,
    RequirementImpact,
    validate_requirement_impacts,
)
from tests.assets.selection import (
    FAST_EXPRESSION,
    FAST_PATHS,
    INTEGRATION_EXPRESSION,
    INTEGRATION_PATHS,
)
from tests.assets.workflow_nodes import MODEL_WORKFLOW_COVERAGE
from tests.scenarios.evidence_intake_calibration import EVIDENCE_INTAKE_CALIBRATION_CASES
from tests.scenarios.evidence_judgment_calibration import EVIDENCE_JUDGMENT_CALIBRATION_CASES
from tests.scenarios.final_composition_calibration import FINAL_COMPOSITION_CALIBRATION_CASES
from tests.scenarios.intake_planning_calibration import CALIBRATION_CASES

SELECTOR = "tests/unit/test_example.py::test_example"
REPO_ROOT = Path(__file__).resolve().parents[3]
CALIBRATION_REGISTRIES = (
    CALIBRATION_CASES,
    EVIDENCE_INTAKE_CALIBRATION_CASES,
    EVIDENCE_JUDGMENT_CALIBRATION_CASES,
    FINAL_COMPOSITION_CALIBRATION_CASES,
)


def _claim(**overrides: object) -> TestEvidenceClaim:
    values: dict[str, object] = {
        "claim_id": "example-correctness",
        "selector": SELECTOR,
        "expected_selection": FocusedSelection.FAST,
        "requirement_ids": ("EVH-006",),
        "asset_class": AssetClass.CODE_CORRECTNESS,
        "seam": StableSeam.DOMAIN_ENGINE,
    }
    values.update(overrides)
    return TestEvidenceClaim(**values)


def _selections(**overrides: set[str]) -> dict[FocusedSelection, set[str]]:
    values = {selection: set() for selection in FocusedSelection}
    values[FocusedSelection.FAST] = {SELECTOR}
    values.update(overrides)
    return values


def _validate_cognitive_gate(
    *,
    board=COGNITIVE_PROGRAM_BOARD,
    calibration_registries=CALIBRATION_REGISTRIES,
    consolidation_decisions=(),
) -> None:
    claims = claim_index(EVIDENCE_CLAIMS)
    check_test_assets.validate_cognitive_evidence_gate(
        board=board,
        logical_nodes=LOGICAL_NODES,
        reader_records=load_reader_inventory(REPO_ROOT),
        cohort_rows=COHORT_EVIDENCE,
        workflow_coverage=MODEL_WORKFLOW_COVERAGE,
        node_conformance=NODE_CONFORMANCE,
        claims=claims,
        requirement_impacts=REQUIREMENT_IMPACTS,
        calibration_registries=calibration_registries,
        consolidation_decisions=consolidation_decisions,
        collected_selectors={claim.selector for claim in claims.values()},
    )


_DISPLACED_BOARD_CLAIM = next(claim for claim in EVIDENCE_CLAIMS if claim.claim_id == "cpe-complete-evidence-board")
_INCOMPLETE_CONSOLIDATION = ConsolidationDecision(
    displaced_claim_id=_DISPLACED_BOARD_CLAIM.claim_id,
    displaced_selector=_DISPLACED_BOARD_CLAIM.selector,
    preservation_basis="preserve every named requirement risk",
    replacements=(),
)


def test_integrated_cognitive_evidence_gate_uses_four_validated_registries() -> None:
    _validate_cognitive_gate()


@pytest.mark.parametrize(
    ("board", "calibration_registries", "consolidation_decisions", "message"),
    [
        pytest.param(
            replace(COGNITIVE_PROGRAM_BOARD, node_rows=COGNITIVE_PROGRAM_BOARD.node_rows[:-1]),
            CALIBRATION_REGISTRIES,
            (),
            "node denominator invalid",
            id="missing-board-row",
        ),
        pytest.param(
            COGNITIVE_PROGRAM_BOARD,
            ((), (), (), ()),
            (),
            "calibration registry invalid",
            id="mis-scoped-calibration-source",
        ),
        pytest.param(
            replace(
                COGNITIVE_PROGRAM_BOARD,
                branch_reviews=(
                    replace(
                        COGNITIVE_PROGRAM_BOARD.branch_reviews[0],
                        evaluation_links=COGNITIVE_PROGRAM_BOARD.branch_reviews[0].evaluation_links[:-1],
                    ),
                    *COGNITIVE_PROGRAM_BOARD.branch_reviews[1:],
                ),
            ),
            CALIBRATION_REGISTRIES,
            (),
            "calibration link denominator invalid",
            id="missing-calibration-link",
        ),
        pytest.param(
            replace(
                COGNITIVE_PROGRAM_BOARD,
                branch_reviews=(
                    replace(
                        COGNITIVE_PROGRAM_BOARD.branch_reviews[0],
                        evaluation_links=(
                            COGNITIVE_PROGRAM_BOARD.branch_reviews[-1].evaluation_links[0],
                            *COGNITIVE_PROGRAM_BOARD.branch_reviews[0].evaluation_links[1:],
                        ),
                    ),
                    *COGNITIVE_PROGRAM_BOARD.branch_reviews[1:],
                ),
            ),
            CALIBRATION_REGISTRIES,
            (),
            "evaluation case belongs to a different branch",
            id="cross-branch-calibration-link",
        ),
        pytest.param(
            replace(
                COGNITIVE_PROGRAM_BOARD,
                branch_reviews=(
                    replace(
                        COGNITIVE_PROGRAM_BOARD.branch_reviews[0],
                        evaluation_links=(
                            replace(
                                COGNITIVE_PROGRAM_BOARD.branch_reviews[0].evaluation_links[0],
                                central_claim_id="missing-central-evaluation",
                            ),
                            *COGNITIVE_PROGRAM_BOARD.branch_reviews[0].evaluation_links[1:],
                        ),
                    ),
                    *COGNITIVE_PROGRAM_BOARD.branch_reviews[1:],
                ),
            ),
            CALIBRATION_REGISTRIES,
            (),
            "unknown central evaluation claim",
            id="missing-central-claim-link",
        ),
        pytest.param(
            replace(
                COGNITIVE_PROGRAM_BOARD,
                node_rows=(
                    replace(
                        COGNITIVE_PROGRAM_BOARD.node_rows[0],
                        evidence_links=(COGNITIVE_PROGRAM_BOARD.node_rows[1].evidence_links[0],),
                    ),
                    *COGNITIVE_PROGRAM_BOARD.node_rows[1:],
                ),
            ),
            CALIBRATION_REGISTRIES,
            (),
            "bootstrap: node claim owner invalid",
            id="invalid-node-proof",
        ),
        pytest.param(
            COGNITIVE_PROGRAM_BOARD,
            CALIBRATION_REGISTRIES,
            (_INCOMPLETE_CONSOLIDATION,),
            "missing displaced requirement-risk replacement",
            id="incomplete-consolidation",
        ),
    ],
)
def test_integrated_cognitive_evidence_gate_rejects_invalid_join_sources(
    board,
    calibration_registries,
    consolidation_decisions,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        _validate_cognitive_gate(
            board=board,
            calibration_registries=calibration_registries,
            consolidation_decisions=consolidation_decisions,
        )


def test_claim_resolves_only_to_its_expected_focused_selection() -> None:
    validate_claim_selections((_claim(),), focused_selectors=_selections())


def test_missing_expected_selector_reports_claim_and_lane() -> None:
    with pytest.raises(EvidenceClaimError, match="example-correctness.*fast"):
        validate_claim_selections(
            (_claim(),),
            focused_selectors=_selections(fast=set()),
        )


def test_selector_in_another_focused_lane_is_rejected() -> None:
    with pytest.raises(EvidenceClaimError, match="example-correctness.*integration"):
        validate_claim_selections(
            (_claim(),),
            focused_selectors=_selections(integration={SELECTOR}),
        )


def test_missing_focused_collection_is_rejected() -> None:
    selections = _selections()
    del selections[FocusedSelection.LIVE]

    with pytest.raises(EvidenceClaimError, match="missing focused collection: live"):
        validate_claim_selections((_claim(),), focused_selectors=selections)


def test_changed_expected_lane_cannot_pass_on_old_collection() -> None:
    integration_claim = replace(_claim(), expected_selection=FocusedSelection.INTEGRATION)

    with pytest.raises(EvidenceClaimError, match="example-correctness.*integration"):
        validate_claim_selections((integration_claim,), focused_selectors=_selections())


def test_subprocess_collector_smoke_rejects_empty_or_mis_scoped_collection(tmp_path: Path) -> None:
    test_file = tmp_path / "test_known.py"
    test_file.write_text(
        "import pytest\n\n@pytest.mark.workflow\ndef test_known_collector_smoke():\n    pass\n",
        encoding="utf-8",
    )
    command = (sys.executable, "-m", "pytest")

    collected = collect_pytest_selectors(
        paths=("test_known.py",),
        expression="workflow",
        label="known-smoke",
        agent_root=tmp_path,
        command=command,
    )
    assert collected == {"test_known.py::test_known_collector_smoke"}

    with pytest.raises(CoverageError, match="mis-scoped-smoke pytest collection failed"):
        collect_pytest_selectors(
            paths=("test_known.py",),
            expression="not workflow",
            label="mis-scoped-smoke",
            agent_root=tmp_path,
            command=command,
        )


def test_requirement_impact_rejects_duplicate_risk_and_uncollected_selector() -> None:
    claim = _claim(requirement_ids=("DER-001",))
    impacts = (
        RequirementImpact(
            requirement_id="DER-001",
            owning_contract="deep-research-delivery-efficiency",
            seam=StableSeam.DOMAIN_ENGINE,
            selector=SELECTOR,
            risk="collector cache returns a stale lane",
        ),
        RequirementImpact(
            requirement_id="DER-001",
            owning_contract="deep-research-delivery-efficiency",
            seam=StableSeam.DOMAIN_ENGINE,
            selector=SELECTOR,
            risk="collector cache returns a stale lane",
        ),
    )

    with pytest.raises(RequirementEvidenceError, match="duplicate impact risk"):
        validate_requirement_impacts(
            impacts,
            claims=(claim,),
            known_requirement_ids={"DER-001"},
            collected_selectors={SELECTOR},
        )

    stale = (
        RequirementImpact(
            requirement_id="DER-001",
            owning_contract="deep-research-delivery-efficiency",
            seam=StableSeam.DOMAIN_ENGINE,
            selector="tests/unit/test_example.py::test_stale",
            risk="collector cache returns a stale lane",
        ),
    )
    with pytest.raises(RequirementEvidenceError, match="impact selector is not collected"):
        validate_requirement_impacts(
            stale,
            claims=(claim,),
            known_requirement_ids={"DER-001"},
            collected_selectors={SELECTOR},
        )


def test_requirement_impact_requires_escalation_for_live_claim() -> None:
    claim = _claim(
        requirement_ids=("DER-001",),
        asset_class=AssetClass.LIVE_BEHAVIORAL_EVALUATION,
        expected_selection=FocusedSelection.LIVE,
        authenticity=None,
    )
    impact = RequirementImpact(
        requirement_id="DER-001",
        owning_contract="deep-research-delivery-efficiency",
        seam=StableSeam.DOMAIN_ENGINE,
        selector=SELECTOR,
        risk="provider-only timing observation",
    )

    with pytest.raises(RequirementEvidenceError, match="missing impact escalation rationale"):
        validate_requirement_impacts(
            (impact,),
            claims=(claim,),
            known_requirement_ids={"DER-001"},
            collected_selectors={SELECTOR},
        )


def test_model_led_smoke_requirement_impacts_use_collected_appropriate_selectors() -> None:
    """@impl RCF-001
    @impl HIN-014
    @impl EVH-024
    @impl RER-012
    @impl PRS-016
    """
    expected_selections = {
        (
            "RCF-001",
            "tests/domain/test_research_confirmation.py::test_unconfirmed_model_proposal_remains_one_outstanding_decision",
        ): FocusedSelection.FAST,
        (
            "HIN-014",
            "tests/graph/test_hitl1_node.py::test_natural_confirmation_writes_current_proposal_and_routes_accepted",
        ): FocusedSelection.FAST,
        (
            "RER-012",
            "tests/integration/test_demo_run_update_adapters.py::"
            "test_standalone_adapters_render_every_complete_proposal_line_before_control",
        ): FocusedSelection.INTEGRATION,
        (
            "PRS-016",
            "tests/contract/test_live_architecture_contract.py::test_live_repository_satisfies_architecture_contract",
        ): FocusedSelection.FAST,
        (
            "EVH-024",
            "tests/unit/test_release_control_plane.py::test_release_runner_reports_the_complete_model_led_smoke_evidence",
        ): FocusedSelection.FAST,
        (
            "EVH-024",
            "tests/unit/test_release_control_plane.py::"
            "test_release_bundle_adapter_reauthorizes_the_public_id_before_observing_artifacts",
        ): FocusedSelection.FAST,
        (
            "EVH-024",
            "tests/unit/test_release_control_plane.py::"
            "test_release_bundle_adapter_fails_on_bundle_loss_before_any_store_observation",
        ): FocusedSelection.FAST,
    }
    claim_index(EVIDENCE_CLAIMS)
    claims_by_selector = {claim.selector: claim for claim in EVIDENCE_CLAIMS}
    impacts = tuple(
        impact
        for impact in REQUIREMENT_IMPACTS
        if impact.requirement_id in {"RCF-001", "HIN-014", "EVH-024", "RER-012", "PRS-016"}
    )

    assert {(impact.requirement_id, impact.selector) for impact in impacts} == set(expected_selections)
    collected_by_selection = {
        FocusedSelection.FAST: collect_pytest_selectors(
            paths=FAST_PATHS,
            expression=FAST_EXPRESSION,
            label="model-led-smoke-fast",
        ),
        FocusedSelection.INTEGRATION: collect_pytest_selectors(
            paths=INTEGRATION_PATHS,
            expression=INTEGRATION_EXPRESSION,
            label="model-led-smoke-integration",
        ),
    }
    for impact in impacts:
        claim = claims_by_selector[impact.selector]
        expected_selection = expected_selections[(impact.requirement_id, impact.selector)]

        assert impact.requirement_id in claim.requirement_ids
        assert impact.seam is claim.seam
        assert claim.expected_selection is expected_selection
        assert impact.selector in collected_by_selection[expected_selection]

    assert {
        expected_selections[(impact.requirement_id, impact.selector)]
        for impact in impacts
        if impact.requirement_id == "EVH-024"
    } == {FocusedSelection.FAST}


def test_collector_caches_only_successful_identical_queries(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[tuple[str, ...]] = []

    def successful_run(command: list[str], **_: object) -> object:
        calls.append(tuple(command))
        return type("Result", (), {"returncode": 0, "stdout": "test_sample.py::test_ok\n", "stderr": ""})()

    check_test_assets.reset_collection_cache()
    monkeypatch.setattr(check_test_assets.subprocess, "run", successful_run)
    kwargs = {
        "paths": ("test_sample.py",),
        "expression": "workflow",
        "label": "cache-smoke",
        "agent_root": tmp_path,
        "command": (sys.executable, "-m", "pytest"),
    }
    assert check_test_assets.collect_pytest_selectors(**kwargs) == {"test_sample.py::test_ok"}
    assert check_test_assets.collect_pytest_selectors(**kwargs) == {"test_sample.py::test_ok"}
    assert len(calls) == 1


def test_collector_does_not_cache_failure_or_hide_default_command(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls = 0

    def failed_run(_command: list[str], **_: object) -> object:
        nonlocal calls
        calls += 1
        return type("Result", (), {"returncode": 1, "stdout": "", "stderr": "broken"})()

    check_test_assets.reset_collection_cache()
    monkeypatch.setattr(check_test_assets.subprocess, "run", failed_run)
    with pytest.raises(CoverageError, match="failure-smoke pytest collection failed"):
        check_test_assets.collect_pytest_selectors(
            paths=("test_sample.py",), expression="workflow", label="failure-smoke", agent_root=tmp_path
        )
    with pytest.raises(CoverageError, match="failure-smoke pytest collection failed"):
        check_test_assets.collect_pytest_selectors(
            paths=("test_sample.py",), expression="workflow", label="failure-smoke", agent_root=tmp_path
        )
    assert calls == 2
    assert check_test_assets.DEFAULT_COLLECTION_COMMAND == (sys.executable,)


def test_project_catalog_serves_different_marker_queries_once(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0

    def catalog_run(command: list[str], **_: object) -> object:
        nonlocal calls
        calls += 1
        Path(command[-1]).write_text(
            json.dumps(
                [
                    {"nodeid": "tests/contract/test_fast.py::test_fast", "markers": []},
                    {"nodeid": "tests/integration/test_flow.py::test_flow", "markers": ["workflow"]},
                ]
            ),
            encoding="utf-8",
        )
        return type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    check_test_assets.reset_collection_cache()
    monkeypatch.setattr(check_test_assets.subprocess, "run", catalog_run)
    assert check_test_assets.collect_pytest_selectors(paths=("tests",), expression="not workflow", label="fast") == {
        "tests/contract/test_fast.py::test_fast"
    }
    assert check_test_assets.collect_pytest_selectors(paths=("tests",), expression="workflow", label="workflow") == {
        "tests/integration/test_flow.py::test_flow"
    }
    assert calls == 1
    check_test_assets.reset_collection_cache()
