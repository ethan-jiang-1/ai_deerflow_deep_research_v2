"""Deterministic contracts for deferred cognitive and human-decision dossiers.

@impl CNI-004
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from tests.assets.deferred_activation_dossiers import (
    ACTIVATION_DOSSIERS,
    ActivationDossier,
    DossierValidationError,
    validate_activation_dossiers,
    validate_no_production_imports,
)


def test_live_dossiers_are_the_exact_non_runtime_activation_denominator() -> None:
    validate_activation_dossiers(ACTIVATION_DOSSIERS)

    by_identity = {dossier.identity: dossier for dossier in ACTIVATION_DOSSIERS}
    assert set(by_identity) == {"hitl2"}
    assert by_identity["hitl2"].commitment_state == "conditional/unresolved"
    assert "new separately reviewed behavior change" in by_identity["hitl2"].fresh_change_admission
    assert "introduce-hitl2-human-decision-experience" not in by_identity["hitl2"].fresh_change_admission
    assert all(dossier.active_program_claim is None for dossier in ACTIVATION_DOSSIERS)


@pytest.mark.parametrize(
    ("dossiers", "message"),
    [
        ((), "dossier_denominator_invalid"),
        ((ACTIVATION_DOSSIERS[0], ACTIVATION_DOSSIERS[0]), "duplicate_identity:hitl2"),
        (
            (replace(ACTIVATION_DOSSIERS[0], identity="hitl2/readiness"),),
            "unknown_identity:hitl2/readiness",
        ),
        pytest.param(
            (
                replace(
                    ACTIVATION_DOSSIERS[0],
                    fresh_change_admission="introduce-hitl2-human-decision-experience",
                ),
            ),
            "fresh_change_admission_invalid:hitl2",
            id="dossiers3-wrong_successor:hitl2",
        ),
        (
            (replace(ACTIVATION_DOSSIERS[0], commitment_state="accepted-but-deferred"),),
            "commitment_state_invalid:hitl2",
        ),
        pytest.param(
            (replace(ACTIVATION_DOSSIERS[0], active_program_claim="run_agent"),),
            "active_program_claim_forbidden:hitl2",
            id="dossiers5-active_program_claim_forbidden:readiness",
        ),
        pytest.param(
            (
                replace(
                    ACTIVATION_DOSSIERS[0],
                    deterministic_admission_owner="formatter",
                ),
            ),
            "admission_owner_invalid:hitl2",
            id="dossiers6-admission_owner_invalid:final_delivery",
        ),
    ],
)
def test_dossier_contract_mutations_fail(
    dossiers: tuple[ActivationDossier, ...],
    message: str,
) -> None:
    with pytest.raises(DossierValidationError, match=message):
        validate_activation_dossiers(dossiers)


def test_production_source_never_imports_the_test_owned_dossier_module() -> None:
    validate_no_production_imports(Path(__file__).resolve().parents[3])
