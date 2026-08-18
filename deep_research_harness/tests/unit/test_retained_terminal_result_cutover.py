"""Cutover guards for persisted/public terminal diagnostic locations.

@impl RER-009
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError

from deerflow_deep_research.domain.run_experience import (
    FailureCertainty,
    ProviderObservation,
    RunFailure,
    RunFailureCode,
    RunSnapshot,
    RunUpdate,
)
from deerflow_deep_research.runtime.run_experience import ResearchRunExperience
from scripts.retained_run_data_migration import InventoryRecord, MigrationSource, RetainedDataInventory, run_inventory

FIXTURE = (
    Path(__file__).parents[1] / "fixtures" / "retained_run_data" / "terminal_result_missing_diagnostic_location.json"
)


def _digest(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def test_persisted_terminal_without_location_rejects_before_any_projection() -> None:
    legacy = json.loads(FIXTURE.read_text(encoding="utf-8"))

    with pytest.raises(ValidationError, match="diagnostic_location"):
        RunFailure.model_validate(legacy)

    with pytest.raises(ValidationError, match="diagnostic_location"):
        TypeAdapter(RunUpdate).validate_python(
            {
                "kind": "fault",
                "snapshot": RunSnapshot().model_dump(mode="json"),
                "failure": legacy,
            }
        )


def test_current_non_provider_terminal_writer_explicitly_marks_location_unavailable() -> None:
    experience = object.__new__(ResearchRunExperience)
    experience._observation_view = None
    experience._lifecycle_phase = "bootstrap"

    failure = experience._failure(RunFailureCode.CONFIGURATION_MODEL_MISSING)

    assert failure.diagnostic_location == "unavailable"
    assert failure.journal_record_created is False
    assert failure.diagnostic_ref is None


def test_verified_provider_publication_writer_retains_bundle_journal_location() -> None:
    experience = object.__new__(ResearchRunExperience)
    experience._lifecycle_phase = "hitl1"

    failure = experience._failure(
        RunFailureCode.PROVIDER_TIMEOUT,
        certainty=FailureCertainty.DIRECT,
        diagnostic_ref="diag_ABCDEFGHIJKL",
        provider_observation=ProviderObservation(response_kind="no_response"),
        diagnostic_location="bundle_journal",
        journal_record_created=True,
    )

    assert failure.diagnostic_location == "bundle_journal"
    assert failure.journal_record_created is True


def test_missing_location_terminal_remains_reject_only_in_inventory(tmp_path: Path) -> None:
    source = MigrationSource(
        family="terminal_result",
        schema=1,
        identity="terminal-missing-location",
        payload=FIXTURE.read_bytes(),
    )
    record = InventoryRecord(
        family=source.family,
        source_schema=source.schema,
        identity=source.identity,
        source_digest=_digest(source.payload),
        disposition="reject",
        output_digest=None,
    )

    report = run_inventory(
        RetainedDataInventory(version=1, records=(record,)),
        sources=(source,),
        output_directory=tmp_path / "output",
    )

    assert report.rejected == 1
    assert not (tmp_path / "output").exists()


# ---------------------------------------------------------------------------
# Journal truth for gate-blocked terminals (BUG-036)
# ---------------------------------------------------------------------------

BUNDLE_ID = "b_" + "G" * 43
DIAG_REF = "diag_gateblocked0001"


def _blocked_control(diagnostic_ref: str | None):
    from deerflow_deep_research.domain.lifecycle import (
        BundleAvailability,
        BundleControlResult,
        BundleRefinementProjection,
        LifecycleAction,
        LifecycleStatus,
        LogicalPhase,
        ResultCode,
        TerminalReason,
    )
    from deerflow_deep_research.domain.run_experience import TerminalIncidentProjection

    return BundleControlResult(
        action=LifecycleAction.START,
        code=ResultCode.BLOCKED,
        availability=BundleAvailability.AVAILABLE,
        durability="restart_durable",
        bundle_id=BUNDLE_ID,
        status=LifecycleStatus.BLOCKED,
        phase=LogicalPhase.WAVE2_SYNTHESIS,
        generation=0,
        terminal_reason=TerminalReason.GATE_BLOCKED,
        terminal_incident=TerminalIncidentProjection(
            code=RunFailureCode.RESEARCH_BLOCKED,
            phase="wave2_synthesis",
            certainty=FailureCertainty.DIRECT,
            diagnostic_ref=diagnostic_ref,
        ),
        refinement=BundleRefinementProjection(disposition="none"),
    )


def _experience_with_observation(terminal_diagnostic_ref: str | None):
    from deerflow_deep_research.domain.run_observation import ObservationInspectability, RunObservationView

    experience = object.__new__(ResearchRunExperience)
    experience._observation_view = RunObservationView(
        bundle_id=BUNDLE_ID,
        inspectability=ObservationInspectability.AVAILABLE,
        durability="restart_durable",
        terminal_diagnostic_ref=terminal_diagnostic_ref,
    )
    experience._lifecycle_phase = "wave2_synthesis"
    return experience


def test_gate_blocked_terminal_with_published_reference_reports_journal_created() -> None:
    """@impl RER-009 — publication truth, not incident class, decides location."""

    experience = _experience_with_observation(DIAG_REF)
    failure = experience._failure_for_terminal(
        _blocked_control(diagnostic_ref=None),
        terminal_diagnostic_ref=DIAG_REF,
    )

    assert failure is not None
    assert failure.diagnostic_location == "bundle_journal"
    assert failure.journal_record_created is True
    assert failure.diagnostic_ref == DIAG_REF


def test_gate_blocked_terminal_without_verified_publication_reports_unavailable() -> None:
    experience = _experience_with_observation("diag_different0001")
    failure = experience._failure_for_terminal(
        _blocked_control(diagnostic_ref=None),
        terminal_diagnostic_ref=DIAG_REF,
    )

    assert failure is not None
    assert failure.diagnostic_location == "unavailable"
    assert failure.journal_record_created is False


def test_gate_blocked_terminal_without_observation_view_reports_unavailable() -> None:
    experience = _experience_with_observation(None)
    experience._observation_view = None
    failure = experience._failure_for_terminal(
        _blocked_control(diagnostic_ref=None),
        terminal_diagnostic_ref=DIAG_REF,
    )

    assert failure is not None
    assert failure.diagnostic_location == "unavailable"
    assert failure.journal_record_created is False


def test_provider_diagnostic_without_reference_fails_closed_at_the_contract() -> None:
    """The domain contract rejects a provider incident without a reference
    before the run-experience layer could ever project it."""

    from deerflow_deep_research.domain.run_experience import ProviderObservation, TerminalIncidentProjection

    with pytest.raises(ValidationError, match="provider_terminal_requires_diagnostic_ref"):
        TerminalIncidentProjection(
            code=RunFailureCode.PROVIDER_TIMEOUT,
            phase="wave2_synthesis",
            certainty=FailureCertainty.DIRECT,
            provider_observation=ProviderObservation(response_kind="no_response"),
        )
