"""Closed non-runtime activation dossier for the unresolved HITL2 boundary.

@impl CNI-004
"""

from __future__ import annotations

import ast
from collections.abc import Iterable
from dataclasses import dataclass, fields
from pathlib import Path


class DossierValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ActivationDossier:
    """One planning-only record for a separately admitted activation."""

    identity: str
    product_responsibility: str
    participation_mode: str
    commitment_state: str
    current_mechanism: str
    trusted_input_boundary: str
    untrusted_input_boundary: str
    candidate_or_choice_boundary: str
    deterministic_admission_owner: str
    failure_posture: str
    proof_seam: str
    fresh_change_admission: str
    activation_precondition: str
    active_program_claim: str | None = None


_EXPECTED_DOSSIERS = (
    ActivationDossier(
        identity="hitl2",
        product_responsibility=(
            "Offer a user decision only for a genuine non-inferable preference or irreversible authorization."
        ),
        participation_mode="human-decision/authorization",
        commitment_state="conditional/unresolved",
        current_mechanism=(
            "The real handler validates the Wave2-pass predecessor and applies the autonomous proceed route."
        ),
        trusted_input_boundary=(
            "Validated Wave2-pass state and the trusted future trigger producer named by a later Scope Card."
        ),
        untrusted_input_boundary=(
            "Any future human response or optional model-assisted explanation remains untrusted until typed validation."
        ),
        candidate_or_choice_boundary=(
            "A future typed human choice may express a product action, never a raw internal route identifier."
        ),
        deterministic_admission_owner=(
            "The HITL2 boundary validator and graph handler validate an accepted typed choice and write its "
            "legal route."
        ),
        failure_posture=(
            "Without a user-approved trigger, retain autonomous continuation and do not create an interrupt, "
            "prompt, or model loop."
        ),
        proof_seam="tests/unit/test_hitl2_real.py::TestRealHitl2Factory::test_validated_state_routes_proceed_without_a_human_response",
        fresh_change_admission=(
            "A new separately reviewed behavior change is required after the product precondition is approved; "
            "an archived no-change disposition cannot activate an interaction."
        ),
        activation_precondition=(
            "A user approves the genuine non-inferable preference or irreversible authorization and its "
            "visible outcome."
        ),
    ),
)

ACTIVATION_DOSSIERS = _EXPECTED_DOSSIERS


def validate_activation_dossiers(dossiers: Iterable[ActivationDossier]) -> None:
    """Validate exact planning records without loading them in production code."""
    dossiers = tuple(dossiers)
    expected_by_identity = {dossier.identity: dossier for dossier in _EXPECTED_DOSSIERS}
    identities = [dossier.identity for dossier in dossiers]
    for identity in identities:
        if identity not in expected_by_identity:
            raise DossierValidationError(f"unknown_identity:{identity}")
        if identities.count(identity) != 1:
            raise DossierValidationError(f"duplicate_identity:{identity}")
    if set(identities) != set(expected_by_identity) or len(dossiers) != len(expected_by_identity):
        raise DossierValidationError("dossier_denominator_invalid")

    for dossier in dossiers:
        expected = expected_by_identity[dossier.identity]
        for field in fields(ActivationDossier):
            actual_value = getattr(dossier, field.name)
            expected_value = getattr(expected, field.name)
            if actual_value == expected_value:
                continue
            if field.name == "fresh_change_admission":
                raise DossierValidationError(f"fresh_change_admission_invalid:{dossier.identity}")
            if field.name == "commitment_state":
                raise DossierValidationError(f"commitment_state_invalid:{dossier.identity}")
            if field.name == "deterministic_admission_owner":
                raise DossierValidationError(f"admission_owner_invalid:{dossier.identity}")
            if field.name == "active_program_claim":
                raise DossierValidationError(f"active_program_claim_forbidden:{dossier.identity}")
            raise DossierValidationError(f"dossier_content_invalid:{dossier.identity}:{field.name}")


def validate_no_production_imports(repo_root: Path) -> None:
    """Reject an accidental production dependency on planning-only dossier data."""
    source_root = repo_root / "deep_research_harness" / "src"
    for source_path in source_root.rglob("*.py"):
        tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported = (alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported = (node.module or "",)
            else:
                continue
            if any(name == "tests.assets.deferred_activation_dossiers" for name in imported):
                raise DossierValidationError(f"production_dossier_import:{source_path.relative_to(repo_root)}")


__all__ = [
    "ACTIVATION_DOSSIERS",
    "ActivationDossier",
    "DossierValidationError",
    "validate_activation_dossiers",
    "validate_no_production_imports",
]
