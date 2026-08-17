"""Cross-lane requirement evidence remains independent and collected.

@impl EVH-008
@impl EVH-009
@impl EVH-010
@impl EVH-023
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from tests.assets.evidence import (
    EVIDENCE_CLAIMS,
    AssetClass,
    AuthenticityLevel,
    FocusedSelection,
    StableSeam,
    TestEvidenceClaim,
)
from tests.assets.requirement_evidence import (
    CONSOLIDATION_DECISIONS,
    REQUIREMENT_EVIDENCE_POLICY,
    ConsolidationDecision,
    ConsolidationReplacement,
    RequirementEvidenceError,
    RequirementImpact,
    collected_deterministic_impl_ids,
    validate_consolidation_decisions,
    validate_requirement_evidence,
)


def _claim(
    claim_id: str,
    requirement_id: str,
    asset_class: AssetClass,
    authenticity: AuthenticityLevel | None,
) -> TestEvidenceClaim:
    selections = {
        AssetClass.CODE_CORRECTNESS: FocusedSelection.FAST,
        AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE: FocusedSelection.WORKFLOW,
        AssetClass.LIVE_BEHAVIORAL_EVALUATION: FocusedSelection.LIVE,
    }
    return TestEvidenceClaim(
        claim_id=claim_id,
        selector=f"tests/unit/test_policy.py::test_{claim_id.replace('-', '_')}",
        expected_selection=selections[asset_class],
        requirement_ids=(requirement_id,),
        asset_class=asset_class,
        seam=StableSeam.RUNTIME_INTEGRATION,
        authenticity=authenticity,
    )


def _evh005_claims() -> tuple[TestEvidenceClaim, ...]:
    return (
        _claim("evh005-deterministic", "EVH-005", AssetClass.CODE_CORRECTNESS, None),
        _claim(
            "evh005-live",
            "EVH-005",
            AssetClass.LIVE_BEHAVIORAL_EVALUATION,
            AuthenticityLevel.LIVE_REAL_DEPENDENCIES,
        ),
    )


def test_cross_lane_policy_accepts_required_independent_evidence() -> None:
    claims = _evh005_claims()
    validate_requirement_evidence(
        policy=(next(item for item in REQUIREMENT_EVIDENCE_POLICY if item.requirement_id == "EVH-005"),),
        claims=claims,
        alive_requirement_ids={"EVH-005", "EVH-006"},
        deterministic_impl_ids={"EVH-005", "EVH-006"},
        collected_selectors={claim.selector for claim in claims},
    )


def test_cross_lane_policy_rejects_missing_live_evidence() -> None:
    claims = _evh005_claims()[:-1]
    with pytest.raises(RequirementEvidenceError, match="EVH-005.*live-behavioral-evaluation"):
        validate_requirement_evidence(
            policy=(next(item for item in REQUIREMENT_EVIDENCE_POLICY if item.requirement_id == "EVH-005"),),
            claims=claims,
            alive_requirement_ids={"EVH-005"},
            deterministic_impl_ids={"EVH-005"},
            collected_selectors={claim.selector for claim in claims},
        )


def test_cross_lane_policy_rejects_missing_collected_deterministic_impl() -> None:
    with pytest.raises(RequirementEvidenceError, match="missing deterministic @impl: EVH-006"):
        validate_requirement_evidence(
            policy=(),
            claims=(),
            alive_requirement_ids={"EVH-006"},
            deterministic_impl_ids=set(),
            collected_selectors=set(),
        )


def test_cross_lane_policy_rejects_unknown_requirement_id() -> None:
    policy = (replace(REQUIREMENT_EVIDENCE_POLICY[0], requirement_id="EVH-999"),)
    with pytest.raises(RequirementEvidenceError, match="unknown policy requirement: EVH-999"):
        validate_requirement_evidence(
            policy=policy,
            claims=(),
            alive_requirement_ids={"EVH-004"},
            deterministic_impl_ids={"EVH-004"},
            collected_selectors=set(),
        )


def test_ordinary_alive_requirement_needs_only_collected_deterministic_impl() -> None:
    validate_requirement_evidence(
        policy=(),
        claims=(),
        alive_requirement_ids={"EVH-006"},
        deterministic_impl_ids={"EVH-006"},
        collected_selectors=set(),
    )


def test_active_delta_impl_is_known_without_becoming_an_unimplemented_main_requirement() -> None:
    validate_requirement_evidence(
        policy=(),
        claims=(),
        alive_requirement_ids={"ABC-001"},
        known_requirement_ids={"ABC-001", "ABC-002"},
        deterministic_impl_ids={"ABC-001", "ABC-002"},
        collected_selectors=set(),
    )


def test_impl_loader_counts_only_collected_test_modules(tmp_path) -> None:
    collected = tmp_path / "tests/unit/test_collected.py"
    uncollected = tmp_path / "tests/unit/test_uncollected.py"
    collected.parent.mkdir(parents=True)
    collected.write_text('"""@impl ABC-001"""\n\ndef test_one(): pass\n', encoding="utf-8")
    uncollected.write_text('"""@impl ABC-002"""\n\ndef test_two(): pass\n', encoding="utf-8")

    assert collected_deterministic_impl_ids(
        tmp_path,
        {"tests/unit/test_collected.py::test_one"},
    ) == {"ABC-001"}


def _consolidation_fixture() -> tuple[
    ConsolidationDecision,
    tuple[TestEvidenceClaim, ...],
    tuple[RequirementImpact, ...],
    set[str],
]:
    displaced = _claim("displaced-proof", "ABC-001", AssetClass.CODE_CORRECTNESS, None)
    retained = _claim("retained-proof", "ABC-001", AssetClass.CODE_CORRECTNESS, None)
    risks = ("candidate cannot bypass admission", "invalid state cannot publish")
    impacts = tuple(
        RequirementImpact("ABC-001", "example-contract", claim.seam, claim.selector, risk)
        for claim in (displaced, retained)
        for risk in risks
    )
    decision = ConsolidationDecision(
        displaced_claim_id=displaced.claim_id,
        displaced_selector=displaced.selector,
        preservation_basis="preserve each named requirement risk at its responsible seam",
        replacements=tuple(
            ConsolidationReplacement(
                retained_claim_id=retained.claim_id,
                requirement_id="ABC-001",
                risk=risk,
            )
            for risk in risks
        ),
    )
    claims = (displaced, retained)
    return decision, claims, impacts, {claim.selector for claim in claims}


def test_consolidation_decision_accepts_complete_same_metadata_risk_replacement() -> None:
    decision, claims, impacts, collected = _consolidation_fixture()

    validate_consolidation_decisions(
        (decision,),
        claims=claims,
        requirement_impacts=impacts,
        collected_selectors=collected,
    )


def test_consolidation_rollout_is_empty_and_review_only() -> None:
    assert CONSOLIDATION_DECISIONS == ()
    validate_consolidation_decisions(
        CONSOLIDATION_DECISIONS,
        claims=EVIDENCE_CLAIMS,
        requirement_impacts=(),
        collected_selectors={claim.selector for claim in EVIDENCE_CLAIMS},
    )
    assert not hasattr(ConsolidationDecision, "delete")
    assert not hasattr(ConsolidationReplacement, "delete")


def test_consolidation_rejects_unknown_or_uncollected_displaced_claim() -> None:
    decision, claims, impacts, collected = _consolidation_fixture()
    with pytest.raises(RequirementEvidenceError, match="unknown displaced claim"):
        validate_consolidation_decisions(
            (replace(decision, displaced_claim_id="unknown-displaced"),),
            claims=claims,
            requirement_impacts=impacts,
            collected_selectors=collected,
        )

    with pytest.raises(RequirementEvidenceError, match="uncollected displaced claim"):
        validate_consolidation_decisions(
            (decision,),
            claims=claims,
            requirement_impacts=impacts,
            collected_selectors=collected - {decision.displaced_selector},
        )


def test_consolidation_rejects_unknown_or_uncollected_retained_claim() -> None:
    decision, claims, impacts, collected = _consolidation_fixture()
    first = decision.replacements[0]
    unknown = replace(first, retained_claim_id="unknown-retained")
    with pytest.raises(RequirementEvidenceError, match="unknown retained claim"):
        validate_consolidation_decisions(
            (replace(decision, replacements=(unknown, *decision.replacements[1:])),),
            claims=claims,
            requirement_impacts=impacts,
            collected_selectors=collected,
        )

    retained = next(claim for claim in claims if claim.claim_id == first.retained_claim_id)
    with pytest.raises(RequirementEvidenceError, match="uncollected retained claim"):
        validate_consolidation_decisions(
            (decision,),
            claims=claims,
            requirement_impacts=impacts,
            collected_selectors=collected - {retained.selector},
        )


def test_consolidation_rejects_self_replacement_and_missing_requirement_risk_pair() -> None:
    decision, claims, impacts, collected = _consolidation_fixture()
    self_replacement = replace(
        decision.replacements[0],
        retained_claim_id=decision.displaced_claim_id,
    )
    with pytest.raises(RequirementEvidenceError, match="self replacement forbidden"):
        validate_consolidation_decisions(
            (replace(decision, replacements=(self_replacement, *decision.replacements[1:])),),
            claims=claims,
            requirement_impacts=impacts,
            collected_selectors=collected,
        )

    with pytest.raises(RequirementEvidenceError, match="missing displaced requirement-risk replacement"):
        validate_consolidation_decisions(
            (replace(decision, replacements=decision.replacements[:-1]),),
            claims=claims,
            requirement_impacts=impacts,
            collected_selectors=collected,
        )


def test_consolidation_rejects_replacement_claim_without_requirement_ownership() -> None:
    decision, claims, impacts, collected = _consolidation_fixture()
    retained = claims[1]
    wrong_owner = replace(retained, requirement_ids=("ABC-002",))

    with pytest.raises(RequirementEvidenceError, match="replacement claim does not own requirement"):
        validate_consolidation_decisions(
            (decision,),
            claims=(claims[0], wrong_owner),
            requirement_impacts=impacts,
            collected_selectors=collected,
        )


@pytest.mark.parametrize(
    "retained",
    [
        pytest.param(
            replace(
                _claim("retained-proof", "ABC-001", AssetClass.CODE_CORRECTNESS, None),
                seam=StableSeam.NODE_INTERFACE,
            ),
            id="seam",
        ),
        pytest.param(
            _claim(
                "retained-proof",
                "ABC-001",
                AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
                AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
            ),
            id="evidence-class",
        ),
        pytest.param(
            _claim(
                "retained-proof",
                "ABC-001",
                AssetClass.CODE_CORRECTNESS,
                AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
            ),
            id="authenticity",
        ),
    ],
)
def test_consolidation_requires_rationale_for_any_evidence_metadata_difference(
    retained: TestEvidenceClaim,
) -> None:
    decision, claims, impacts, collected = _consolidation_fixture()
    original_retained = claims[1]
    updated_impacts = tuple(
        replace(impact, seam=retained.seam) if impact.selector == original_retained.selector else impact
        for impact in impacts
    )

    with pytest.raises(RequirementEvidenceError, match="replacement metadata difference requires rationale"):
        validate_consolidation_decisions(
            (decision,),
            claims=(claims[0], retained),
            requirement_impacts=updated_impacts,
            collected_selectors=(collected - {original_retained.selector}) | {retained.selector},
        )


@pytest.mark.parametrize(
    "basis",
    [
        "reduce the pytest count",
        "balance marker totals",
        "move coverage out of this directory",
        "increase line coverage",
    ],
)
def test_consolidation_rejects_aggregate_only_basis(basis: str) -> None:
    decision, claims, impacts, collected = _consolidation_fixture()

    with pytest.raises(RequirementEvidenceError, match="aggregate consolidation basis forbidden"):
        validate_consolidation_decisions(
            (replace(decision, preservation_basis=basis),),
            claims=claims,
            requirement_impacts=impacts,
            collected_selectors=collected,
        )
