"""Bounded retained observations that cannot control a Run Bundle.

The store deliberately knows neither a trusted scope nor a Bundle path.  A runtime
caller may publish already-validated lifecycle facts for diagnostics, but this module
cannot discover, authorize, reopen, or mutate a Run Bundle.  Records use a derived
storage key so the retained filesystem layout is not a secondary Bundle locator.

@impl RUS-001
@impl RUS-002
@impl RUS-004
@impl RUS-007
@impl RES-001
@impl RES-004
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import stat
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from deerflow_deep_research.domain.run_observation import (
    MAX_EVENT_RECORDS,
    MAX_TRACE_RECORDS,
    MAX_TRACE_SNAPSHOT_BYTES,
    JournalAvailability,
    LifecycleTraceRecord,
    ObservationCategory,
    ObservationInspectability,
    RecordBearingLifecycleFact,
    RetainedDiagnosticRecord,
    RetentionState,
    RunEvent,
    RunEventCategory,
    RunObservationInspection,
    RunObservationManifest,
    RunObservationView,
    RunSummary,
    TerminalDiagnosticProjection,
)

RETAINED_ROOT_NAME = ".reports/deep-research-diagnostics"
_OBSERVATIONS_DIRECTORY = "observations"
_MANIFEST_FILENAME = "manifest.json"
_SUMMARY_FILENAME = "run-summary.json"
_DIAGNOSTICS_DIRECTORY = "diagnostics"
_LIFECYCLE_FILENAME = "lifecycle.jsonl"
_EVENTS_FILENAME = "events.jsonl"
_DIAGNOSTIC_FILENAME = "records.jsonl"


class RunObservationError(RuntimeError):
    """A bounded observation persistence failure, never a lifecycle outcome."""


class RunObservationStore:
    """Persist and inspect diagnostics through one observation-only interface.

    The interface intentionally has no scope, Bundle selector, or control method.
    ``bundle_id`` is accepted only to hash a retained observation key or to render the
    observation's bounded identity.  It never maps to a Run Bundle directory.
    """

    def __init__(self, *, retained_root: Path) -> None:
        self._root = Path(retained_root)
        self._locks: dict[str, asyncio.Lock] = {}

    @staticmethod
    def project_default_root(project_root: Path) -> Path:
        """Return the one diagnostics root without identifying any Run Bundle."""

        return Path(project_root) / RETAINED_ROOT_NAME

    async def publish(self, fact: RecordBearingLifecycleFact) -> RunObservationView:
        """Persist a bounded observation without validating or touching a Bundle."""

        if not isinstance(fact, RecordBearingLifecycleFact):
            raise TypeError("run_observation_fact_required")
        async with self._lock_for(fact.bundle_id):
            try:
                return await asyncio.to_thread(self._publish_sync, fact)
            except (OSError, ValueError, RunObservationError):
                return RunObservationView(
                    bundle_id=fact.bundle_id,
                    inspectability=ObservationInspectability.UNAVAILABLE,
                    durability="unavailable",
                    observation_category=ObservationCategory.PERSISTENCE_UNAVAILABLE,
                )

    async def inspect(self, *, bundle_id: str) -> RunObservationInspection:
        """Read an observation by its opaque key; never use it as Run authority."""

        if not _valid_bundle_id(bundle_id):
            return RunObservationInspection(
                inspectability=ObservationInspectability.INVALID_REFERENCE,
                observation_category=ObservationCategory.RECORD_INVALID,
            )
        async with self._lock_for(bundle_id):
            try:
                return await asyncio.to_thread(self._inspect_sync, bundle_id)
            except (OSError, ValueError, RunObservationError):
                return RunObservationInspection(
                    bundle_id=bundle_id,
                    inspectability=ObservationInspectability.UNAVAILABLE,
                    observation_category=ObservationCategory.RECORD_INVALID,
                )

    async def record_event(
        self,
        *,
        bundle_id: str,
        category: RunEventCategory,
        phase: str,
        work_id: str | None = None,
        attempt_id: str | None = None,
        validation_code: str | None = None,
        worker_failure_category: str | None = None,
        retry_count: int | None = None,
        diagnostic_ref: str | None = None,
        recovery_correlation_id: str | None = None,
        provider_category: str | None = None,
        retry_ordinal: int | None = None,
        backoff_milliseconds: int | None = None,
        recovery_event_disposition: str | None = None,
    ) -> None:
        """Append a redacted event only to an already-published observation."""

        if not _valid_bundle_id(bundle_id):
            return
        async with self._lock_for(bundle_id):
            try:
                await asyncio.to_thread(
                    self._record_event_sync,
                    bundle_id,
                    category,
                    phase,
                    work_id,
                    attempt_id,
                    validation_code,
                    worker_failure_category,
                    retry_count,
                    diagnostic_ref,
                    recovery_correlation_id,
                    provider_category,
                    retry_ordinal,
                    backoff_milliseconds,
                    recovery_event_disposition,
                )
            except (OSError, ValueError, RunObservationError):
                # Observations cannot perturb graph or lifecycle execution.
                return

    async def cleanup(self) -> tuple[str, ...]:
        """Keep retention lifecycle-free; no observation can delete a Bundle."""

        return ()

    def _publish_sync(self, fact: RecordBearingLifecycleFact) -> RunObservationView:
        root = self._record_root(fact.bundle_id)
        diagnostics = root / _DIAGNOSTICS_DIRECTORY
        self._ensure_directory(self._root)
        self._ensure_directory(self._root / _OBSERVATIONS_DIRECTORY)
        self._ensure_directory(root)
        self._ensure_directory(diagnostics)

        existing = self._read_model(root / _MANIFEST_FILENAME, RunObservationManifest)
        if existing is not None and existing.bundle_id != fact.bundle_id:
            raise RunObservationError("observation_manifest_mismatch")
        created_at = existing.created_at if existing is not None else datetime.now(UTC)
        now = datetime.now(UTC)
        diagnostics_records = self._read_lines(diagnostics / _DIAGNOSTIC_FILENAME, RetainedDiagnosticRecord)
        if fact.diagnostic_ref is not None and not any(
            record.reference == fact.diagnostic_ref for record in diagnostics_records
        ):
            diagnostics_records = (*diagnostics_records, self._diagnostic_record(fact, now))
            self._atomic_write(diagnostics / _DIAGNOSTIC_FILENAME, self._encode_lines(diagnostics_records))

        events = self._read_lines(diagnostics / _EVENTS_FILENAME, RunEvent)
        event = RunEvent(
            sequence=len(events) + 1,
            timestamp=now,
            category=RunEventCategory.TERMINAL if fact.terminal_outcome is not None else RunEventCategory.LIFECYCLE,
            phase=fact.phase,
            validation_code=fact.failure_category,
            worker_failure_category=fact.worker_failure_category,
            diagnostic_ref=fact.diagnostic_ref,
        )
        events = (*events, event)
        if len(events) > MAX_EVENT_RECORDS:
            events = events[-MAX_EVENT_RECORDS:]
            events = tuple(item.model_copy(update={"sequence": index}) for index, item in enumerate(events, start=1))
        self._atomic_write(diagnostics / _EVENTS_FILENAME, self._encode_lines(events))

        trace = self._read_lines(diagnostics / _LIFECYCLE_FILENAME, LifecycleTraceRecord)
        trace = (
            *trace,
            LifecycleTraceRecord(
                sequence=len(trace) + 1,
                timestamp=now,
                action=fact.action,
                phase=fact.phase,
                status=fact.status,
                generation=fact.generation,
                trace_delta=fact.trace_delta,
                pending_phase=fact.pending_phase,
                pending_mode=fact.pending_mode,
                pending_request_id=fact.pending_request_id,
                terminal_outcome=fact.terminal_outcome,
                failure_category=fact.failure_category,
                worker_failure_category=fact.worker_failure_category,
                diagnostic_ref=fact.diagnostic_ref,
                retained_recovery_summary=fact.retained_recovery_summary,
            ),
        )
        if len(trace) > MAX_TRACE_RECORDS:
            trace = trace[-MAX_TRACE_RECORDS:]
            trace = tuple(item.model_copy(update={"sequence": index}) for index, item in enumerate(trace, start=1))
        self._atomic_write(diagnostics / _LIFECYCLE_FILENAME, self._encode_lines(trace))

        summary = RunSummary(
            bundle_id=fact.bundle_id,
            status=fact.status,
            phase=fact.phase,
            generation=fact.generation,
            updated_at=now,
            durability=fact.durability,
            terminal_outcome=fact.terminal_outcome,
            failure_category=fact.failure_category,
            worker_failure_category=fact.worker_failure_category,
            diagnostic_ref=fact.diagnostic_ref,
            journal_availability=JournalAvailability.COMPLETE,
            latest_event_sequence=events[-1].sequence,
            retained_recovery_summary=fact.retained_recovery_summary,
        )
        self._atomic_write(root / _SUMMARY_FILENAME, self._encode_model(summary))
        manifest = RunObservationManifest(
            bundle_id=fact.bundle_id,
            created_at=created_at,
            updated_at=now,
            retention_state=RetentionState.RETAINED,
            durability=fact.durability,
            diagnostic_path=("diagnostics/records.jsonl" if diagnostics_records else None),
            summary_path="run-summary.json",
            events_path="diagnostics/events.jsonl",
        )
        self._atomic_write(root / _MANIFEST_FILENAME, self._encode_model(manifest))
        return RunObservationView(
            bundle_id=fact.bundle_id,
            inspectability=ObservationInspectability.AVAILABLE,
            retention_state=manifest.retention_state,
            durability=fact.durability,
            terminal_diagnostic_ref=fact.diagnostic_ref,
        )

    def _inspect_sync(self, bundle_id: str) -> RunObservationInspection:
        root = self._record_root(bundle_id)
        if not root.exists():
            return RunObservationInspection(bundle_id=bundle_id, inspectability=ObservationInspectability.NOT_FOUND)
        self._require_directory(root)
        manifest = self._read_model(root / _MANIFEST_FILENAME, RunObservationManifest)
        if manifest is None or manifest.bundle_id != bundle_id:
            raise RunObservationError("observation_manifest_invalid")
        summary = self._read_model(root / _SUMMARY_FILENAME, RunSummary)
        events = self._read_lines(root / _DIAGNOSTICS_DIRECTORY / _EVENTS_FILENAME, RunEvent)
        diagnostics = self._read_lines(root / _DIAGNOSTICS_DIRECTORY / _DIAGNOSTIC_FILENAME, RetainedDiagnosticRecord)
        terminal = self._terminal_diagnostic(summary, diagnostics)
        return RunObservationInspection(
            bundle_id=bundle_id,
            inspectability=ObservationInspectability.AVAILABLE,
            retention_state=manifest.retention_state,
            durability=manifest.durability,
            summary=summary,
            events=events,
            journal_availability=(
                summary.journal_availability if summary is not None else JournalAvailability.UNAVAILABLE
            ),
            terminal_diagnostic_ref=(terminal.reference if terminal is not None else None),
            terminal_diagnostic=terminal,
        )

    def _record_event_sync(
        self,
        bundle_id: str,
        category: RunEventCategory,
        phase: str,
        work_id: str | None,
        attempt_id: str | None,
        validation_code: str | None,
        worker_failure_category: str | None,
        retry_count: int | None,
        diagnostic_ref: str | None,
        recovery_correlation_id: str | None,
        provider_category: str | None,
        retry_ordinal: int | None,
        backoff_milliseconds: int | None,
        recovery_event_disposition: str | None,
    ) -> None:
        root = self._record_root(bundle_id)
        manifest = self._read_model(root / _MANIFEST_FILENAME, RunObservationManifest)
        if manifest is None or manifest.bundle_id != bundle_id:
            return
        diagnostics = root / _DIAGNOSTICS_DIRECTORY
        self._require_directory(diagnostics)
        events = self._read_lines(diagnostics / _EVENTS_FILENAME, RunEvent)
        if len(events) >= MAX_EVENT_RECORDS:
            return
        event = RunEvent(
            sequence=len(events) + 1,
            timestamp=datetime.now(UTC),
            category=category,
            phase=phase,
            work_id=work_id,
            attempt_id=attempt_id,
            validation_code=validation_code,
            worker_failure_category=worker_failure_category,
            retry_count=retry_count,
            diagnostic_ref=diagnostic_ref,
            recovery_correlation_id=recovery_correlation_id,
            provider_category=provider_category,
            retry_ordinal=retry_ordinal,
            backoff_milliseconds=backoff_milliseconds,
            recovery_event_disposition=recovery_event_disposition,
        )
        self._atomic_write(diagnostics / _EVENTS_FILENAME, self._encode_lines((*events, event)))

    @staticmethod
    def _diagnostic_record(fact: RecordBearingLifecycleFact, now: datetime) -> RetainedDiagnosticRecord:
        assert fact.diagnostic_ref is not None
        assert fact.failure_category is not None
        return RetainedDiagnosticRecord(
            reference=fact.diagnostic_ref,
            time=now,
            action=fact.action,
            phase=fact.phase,
            category=fact.failure_category,
            recovery_trigger_timeout_origin=fact.recovery_trigger_timeout_origin,
            final_timeout_origin=fact.final_timeout_origin,
        )

    @staticmethod
    def _terminal_diagnostic(
        summary: RunSummary | None,
        diagnostics: tuple[RetainedDiagnosticRecord, ...],
    ) -> TerminalDiagnosticProjection | None:
        if summary is None or summary.diagnostic_ref is None:
            return None
        matching = [record for record in diagnostics if record.reference == summary.diagnostic_ref]
        if len(matching) != 1:
            return None
        record = matching[0]
        return TerminalDiagnosticProjection(
            reference=record.reference,
            category=record.category,
            phase=record.phase,
            recovery_trigger_timeout_origin=record.recovery_trigger_timeout_origin,
            final_timeout_origin=record.final_timeout_origin,
        )

    def _record_root(self, bundle_id: str) -> Path:
        return self._root / _OBSERVATIONS_DIRECTORY / _observation_key(bundle_id)

    def _lock_for(self, bundle_id: str) -> asyncio.Lock:
        return self._locks.setdefault(_observation_key(bundle_id), asyncio.Lock())

    @staticmethod
    def _read_model(path: Path, model: type[Any]) -> Any | None:
        try:
            return model.model_validate_json(RunObservationStore._read_bytes(path))
        except FileNotFoundError:
            return None

    @staticmethod
    def _read_lines(path: Path, model: type[Any]) -> tuple[Any, ...]:
        try:
            raw = RunObservationStore._read_bytes(path)
        except FileNotFoundError:
            return ()
        records = tuple(model.model_validate_json(line) for line in raw.splitlines() if line)
        if len(records) > MAX_TRACE_RECORDS:
            raise RunObservationError("observation_record_limit_exceeded")
        return records

    @staticmethod
    def _read_bytes(path: Path) -> bytes:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        fd = os.open(path, flags)
        try:
            metadata = os.fstat(fd)
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_mode & 0o077:
                raise RunObservationError("observation_file_unsafe")
            if metadata.st_size > MAX_TRACE_SNAPSHOT_BYTES:
                raise RunObservationError("observation_file_too_large")
            with os.fdopen(fd, "rb", closefd=False) as stream:
                data = stream.read(MAX_TRACE_SNAPSHOT_BYTES + 1)
            if len(data) > MAX_TRACE_SNAPSHOT_BYTES:
                raise RunObservationError("observation_file_too_large")
            return data
        finally:
            os.close(fd)

    @staticmethod
    def _encode_model(value: Any) -> bytes:
        return value.model_dump_json(exclude_none=True).encode("utf-8")

    @staticmethod
    def _encode_lines(records: tuple[Any, ...]) -> bytes:
        data = b"".join(
            json.dumps(
                record.model_dump(mode="json", exclude_none=True),
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            + b"\n"
            for record in records
        )
        if len(data) > MAX_TRACE_SNAPSHOT_BYTES:
            raise RunObservationError("observation_snapshot_too_large")
        return data

    @staticmethod
    def _ensure_directory(path: Path) -> None:
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        RunObservationStore._require_directory(path)

    @staticmethod
    def _require_directory(path: Path) -> None:
        metadata = path.lstat()
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode) or metadata.st_mode & 0o077:
            raise RunObservationError("observation_directory_unsafe")

    @staticmethod
    def _atomic_write(path: Path, data: bytes) -> None:
        if len(data) > MAX_TRACE_SNAPSHOT_BYTES:
            raise RunObservationError("observation_write_too_large")
        RunObservationStore._require_directory(path.parent)
        fd, staged = tempfile.mkstemp(prefix=".observation-", suffix=".tmp", dir=path.parent)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "wb", closefd=False) as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.close(fd)
            os.replace(staged, path)
            os.chmod(path, 0o600)
            metadata = path.lstat()
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode) or metadata.st_mode & 0o077:
                raise RunObservationError("observation_file_unsafe")
        except BaseException:
            try:
                os.close(fd)
            except OSError:
                pass
            try:
                os.unlink(staged)
            except FileNotFoundError:
                pass
            raise


class RunObservationRecorder:
    """A producer-facing event adapter with no Bundle path or lifecycle capability."""

    def __init__(self, *, store: RunObservationStore, bundle_id: str) -> None:
        self._store = store
        self._bundle_id = bundle_id

    async def record(self, **event: Any) -> None:
        await self._store.record_event(bundle_id=self._bundle_id, **event)


class RetainedRunObservationPublisher:
    """Small publishing adapter used by presentation code after lifecycle projection."""

    def __init__(self, store: RunObservationStore) -> None:
        self._store = store

    async def publish(self, fact: RecordBearingLifecycleFact) -> RunObservationView:
        return await self._store.publish(fact)

    async def close(self) -> None:
        await self._store.cleanup()


def _observation_key(bundle_id: str) -> str:
    return hashlib.sha256(("deep-research-observation/v1:" + bundle_id).encode("ascii")).hexdigest()


def _valid_bundle_id(bundle_id: object) -> bool:
    try:
        RecordBearingLifecycleFact(
            bundle_id=bundle_id,
            action="status",
            status="suspended",
            phase="bootstrap",
            generation=0,
            durability="unavailable",
        )
    except (TypeError, ValueError):
        return False
    return True


__all__ = [
    "RETAINED_ROOT_NAME",
    "RetainedRunObservationPublisher",
    "RunObservationError",
    "RunObservationRecorder",
    "RunObservationStore",
]
