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
    Path(__file__).parents[1]
    / "fixtures"
    / "retained_run_data"
    / "terminal_result_missing_diagnostic_location.json"
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
