"""Syntax-discovered production owners of real model workflow coverage.

@impl EVH-008
@impl EVH-009
@impl WFO-002
"""

from __future__ import annotations

import ast
from collections.abc import Iterable, Mapping, Set
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from tests.assets.evidence import (
    AssetClass,
    AuthenticityLevel,
    FocusedSelection,
    StableSeam,
    TestEvidenceClaim,
)


class WorkflowOutcomeClass(StrEnum):
    """Closed non-success classes currently exercised at a model-owner seam."""

    KNOWN_INVOCATION_FAILURE = "known-invocation-failure"


@dataclass(frozen=True)
class WorkflowOutcomeEvidence:
    """One declared failure class and its phase, journal, and projection evidence."""

    outcome_class: WorkflowOutcomeClass
    phase_claim_id: str
    journal_claim_id: str
    projection_claim_id: str


@dataclass(frozen=True)
class ModelWorkflowCoverage:
    logical_name: str
    claim_id: str
    outcome_evidence: tuple[WorkflowOutcomeEvidence, ...]

    @property
    def referenced_claim_ids(self) -> tuple[str, ...]:
        return (
            self.claim_id,
            *(
                claim_id
                for outcome in self.outcome_evidence
                for claim_id in (
                    outcome.phase_claim_id,
                    outcome.journal_claim_id,
                    outcome.projection_claim_id,
                )
            ),
        )


class WorkflowCoverageError(ValueError):
    pass


MODEL_WORKFLOW_COVERAGE = (
    ModelWorkflowCoverage(
        "hitl1",
        "workflow-hitl1-zero-tool-bridge",
        (
            WorkflowOutcomeEvidence(
                WorkflowOutcomeClass.KNOWN_INVOCATION_FAILURE,
                "hitl1-typed-failure-incident",
                "run-event-journal-node-agent-bridge-failures",
                "workflow-outcome-hitl1-lifecycle-projection",
            ),
        ),
    ),
    ModelWorkflowCoverage(
        "topic_planning",
        "workflow-topic-planning-zero-tool-bridge",
        (
            WorkflowOutcomeEvidence(
                WorkflowOutcomeClass.KNOWN_INVOCATION_FAILURE,
                "workflow-outcome-topic-planning-known-invocation",
                "run-event-journal-node-agent-bridge-failures",
                "workflow-outcome-topic-planning-lifecycle-projection",
            ),
        ),
    ),
    ModelWorkflowCoverage(
        "wave0",
        "workflow-wave0-worker-bridge",
        (
            WorkflowOutcomeEvidence(
                WorkflowOutcomeClass.KNOWN_INVOCATION_FAILURE,
                "workflow-outcome-wave0-known-invocation",
                "run-event-journal-node-agent-bridge-failures",
                "workflow-outcome-wave0-known-invocation",
            ),
        ),
    ),
    ModelWorkflowCoverage(
        "wave1",
        "workflow-wave1-worker-bridge",
        (
            WorkflowOutcomeEvidence(
                WorkflowOutcomeClass.KNOWN_INVOCATION_FAILURE,
                "workflow-outcome-wave1-known-invocation",
                "run-event-journal-node-agent-bridge-failures",
                "workflow-outcome-wave1-known-invocation",
            ),
        ),
    ),
    ModelWorkflowCoverage(
        "wave2_synthesis",
        "workflow-wave2-zero-tool-bridge",
        (
            WorkflowOutcomeEvidence(
                WorkflowOutcomeClass.KNOWN_INVOCATION_FAILURE,
                "workflow-outcome-wave2-known-invocation",
                "run-event-journal-node-agent-bridge-failures",
                "workflow-outcome-wave2-known-invocation",
            ),
        ),
    ),
    ModelWorkflowCoverage(
        "targeted_evidence",
        "workflow-targeted-evidence-worker-bridge",
        (
            WorkflowOutcomeEvidence(
                WorkflowOutcomeClass.KNOWN_INVOCATION_FAILURE,
                "workflow-outcome-targeted-evidence-known-invocation",
                "run-event-journal-node-agent-bridge-failures",
                "workflow-outcome-targeted-evidence-known-invocation",
            ),
        ),
    ),
    ModelWorkflowCoverage(
        "readiness",
        "workflow-readiness-evidence-critic-bridge",
        (
            WorkflowOutcomeEvidence(
                WorkflowOutcomeClass.KNOWN_INVOCATION_FAILURE,
                "readiness-critic-conservative-failure",
                "run-event-journal-node-agent-bridge-failures",
                "readiness-critic-conservative-failure",
            ),
        ),
    ),
    ModelWorkflowCoverage(
        "final_delivery",
        "nac-final-delivery-composer-success",
        (
            WorkflowOutcomeEvidence(
                WorkflowOutcomeClass.KNOWN_INVOCATION_FAILURE,
                "workflow-outcome-final-delivery-known-invocation",
                "run-event-journal-node-agent-bridge-failures",
                "nac-final-delivery-composer-risk",
            ),
        ),
    ),
)


def discover_run_agent_owners(node_root: Path) -> set[str]:
    """Discover node packages that load a ``.run_agent`` method reference."""
    owners: set[str] = set()
    if not node_root.is_dir():
        return owners
    for package in sorted(path for path in node_root.iterdir() if path.is_dir()):
        for source_path in sorted(package.rglob("*.py")):
            try:
                tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
            except (OSError, SyntaxError) as exc:
                raise WorkflowCoverageError(f"{package.name}: cannot inspect {source_path}: {exc}") from exc
            if any(
                isinstance(node, ast.Attribute) and node.attr == "run_agent" and isinstance(node.ctx, ast.Load)
                for node in ast.walk(tree)
            ):
                owners.add(package.name)
                break
    return owners


def validate_model_workflow_coverage(
    entries: Iterable[ModelWorkflowCoverage],
    *,
    claims: Mapping[str, TestEvidenceClaim],
    discovered_owners: Set[str],
    focused_selectors: Mapping[FocusedSelection, Set[str]],
) -> None:
    entries = tuple(entries)
    errors: list[str] = []
    by_owner: dict[str, ModelWorkflowCoverage] = {}
    for entry in entries:
        if entry.logical_name in by_owner:
            errors.append(f"{entry.logical_name}: duplicate workflow inventory entry")
        by_owner[entry.logical_name] = entry

    for owner in sorted(discovered_owners - by_owner.keys()):
        errors.append(f"{owner}: discovered run_agent owner lacks workflow coverage")
    for owner in sorted(by_owner.keys() - discovered_owners):
        errors.append(f"{owner}: workflow coverage has no discovered run_agent owner")

    for entry in entries:
        claim = claims.get(entry.claim_id)
        if claim is None:
            errors.append(f"{entry.logical_name}: unknown workflow claim {entry.claim_id}")
            continue
        if claim.asset_class is not AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE:
            errors.append(f"{entry.logical_name}: {entry.claim_id} is not workflow conformance")
        if claim.expected_selection is not FocusedSelection.WORKFLOW:
            errors.append(f"{entry.logical_name}: {entry.claim_id} is not assigned to workflow selection")
        if claim.authenticity is not AuthenticityLevel.SCRIPTED_REAL_WORKFLOW:
            errors.append(f"{entry.logical_name}: {entry.claim_id} lacks scripted real workflow authenticity")
        workflow_selectors = focused_selectors.get(FocusedSelection.WORKFLOW)
        if workflow_selectors is None:
            errors.append(f"{entry.logical_name}: workflow selection is unavailable")
        elif claim.selector not in workflow_selectors:
            errors.append(f"{entry.logical_name}: uncollected workflow selector {claim.selector}")

        if not entry.outcome_evidence:
            errors.append(f"{entry.logical_name}: missing declared outcome class")
            continue

        declared_classes: set[WorkflowOutcomeClass] = set()
        for outcome in entry.outcome_evidence:
            if not isinstance(outcome.outcome_class, WorkflowOutcomeClass):
                errors.append(f"{entry.logical_name}: invalid declared outcome class")
                continue
            if outcome.outcome_class in declared_classes:
                errors.append(f"{entry.logical_name}: duplicate declared outcome class {outcome.outcome_class.value}")
                continue
            declared_classes.add(outcome.outcome_class)
            _validate_outcome_claim(
                entry.logical_name,
                outcome.outcome_class,
                "phase",
                outcome.phase_claim_id,
                claims,
                focused_selectors,
                errors,
            )
            _validate_outcome_claim(
                entry.logical_name,
                outcome.outcome_class,
                "journal",
                outcome.journal_claim_id,
                claims,
                focused_selectors,
                errors,
            )
            _validate_outcome_claim(
                entry.logical_name,
                outcome.outcome_class,
                "projection",
                outcome.projection_claim_id,
                claims,
                focused_selectors,
                errors,
            )

    if errors:
        raise WorkflowCoverageError("\n".join(errors))


def _validate_outcome_claim(
    owner: str,
    outcome_class: WorkflowOutcomeClass,
    role: str,
    claim_id: str,
    claims: Mapping[str, TestEvidenceClaim],
    focused_selectors: Mapping[FocusedSelection, Set[str]],
    errors: list[str],
) -> None:
    claim = claims.get(claim_id)
    label = f"{owner}: {outcome_class.value} {role}"
    if claim is None:
        errors.append(f"{label} claim is unknown: {claim_id}")
        return
    if claim.asset_class not in {
        AssetClass.CODE_CORRECTNESS,
        AssetClass.DETERMINISTIC_WORKFLOW_CONFORMANCE,
    }:
        errors.append(f"{label} claim is not deterministic outcome evidence")
    if role == "journal" and claim.seam not in {
        StableSeam.NODE_INTERFACE,
        StableSeam.RUNTIME_INTEGRATION,
    }:
        errors.append(f"{label} claim is not at a journal seam")
    direct_lifecycle_projection = (
        role == "projection"
        and claim.asset_class is AssetClass.CODE_CORRECTNESS
        and claim.seam is StableSeam.LIFECYCLE_MIXED_GRAPH
        and claim.authenticity is None
    )
    if not direct_lifecycle_projection and claim.authenticity not in {
        AuthenticityLevel.REAL_NODE_FAKE_CAPABILITIES,
        AuthenticityLevel.SCRIPTED_REAL_WORKFLOW,
    }:
        errors.append(f"{label} claim lacks real-node authenticity")
    if role == "phase" and claim.seam not in {StableSeam.NODE_INTERFACE, StableSeam.RUNTIME_INTEGRATION}:
        errors.append(f"{label} claim is not at a phase seam")
    if role == "projection" and claim.seam not in {
        StableSeam.NODE_INTERFACE,
        StableSeam.RUNTIME_INTEGRATION,
        StableSeam.LIFECYCLE_MIXED_GRAPH,
    }:
        errors.append(f"{label} claim is not at a lifecycle or worker-controller seam")
    selectors = focused_selectors.get(claim.expected_selection)
    if selectors is None:
        errors.append(f"{label} selection is unavailable: {claim.expected_selection.value}")
    elif claim.selector not in selectors:
        errors.append(f"{label} selector is stale: {claim.selector}")


__all__ = [
    "MODEL_WORKFLOW_COVERAGE",
    "ModelWorkflowCoverage",
    "WorkflowOutcomeClass",
    "WorkflowOutcomeEvidence",
    "WorkflowCoverageError",
    "discover_run_agent_owners",
    "validate_model_workflow_coverage",
]
