"""Runtime-owned Deep Research Run Bundle publication and scoped discovery.

The module deliberately owns the point where trusted scope, filesystem persistence,
and lifecycle State meet.  It does not keep a durable active pointer or consult an
external checkpoint, session record, or binding.  The private scope bucket holds only
published Bundle directories and transient staging directories.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import secrets
import shutil
import stat
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from deerflow_deep_research.domain.bundle import (
    BUNDLE_SUBTREES,
    DIAGNOSTICS_SUBTREE,
    BundleId,
    RunBundleRef,
    new_bundle_id,
)
from deerflow_deep_research.domain.lifecycle import (
    MAX_START_REQUEST_CHARS,
    AcceptedHumanResponse,
    BundleAvailability,
    BundleControlResult,
    BundleRefinementDisposition,
    BundleRefinementProjection,
    Durability,
    ImplementationMode,
    LegalNextAction,
    LifecycleAction,
    LifecycleStatus,
    LogicalPhase,
    RefinementAdmissionDisposition,
    RefinementOperation,
    ResultCode,
    TerminalReason,
)
from deerflow_deep_research.domain.run_experience import PendingInputProjection, TerminalIncidentProjection
from deerflow_deep_research.domain.state import (
    BundleLocalState,
    PhaseStatus,
    RefinementAdmission,
    admit_bundle_refinement,
    consume_admitted_refinement,
    consume_bundle_response,
)
from deerflow_deep_research.graph.rerun import FullRerunPolicy
from deerflow_deep_research.runtime.bundle_transition import (
    BundleTransitionCoordinator,
    BundleTransitionError,
    BundleTransitionLease,
)

_STATE_FILENAME = "state.json"
_GRAPH_FILENAME = "graph.sqlite"
_STAGING_PREFIX = ".staging-"


class BundleLifecycleError(RuntimeError):
    """A bounded internal failure used by the lifecycle boundary."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class BundleAlreadyActive(BundleLifecycleError):
    def __init__(self, bundle: RunBundleRef) -> None:
        super().__init__("active_bundle_exists")
        self.bundle = bundle


FaultHook = Callable[[str], None]


@dataclass(frozen=True)
class CurrentBundleHandle:
    """Transient caller-local continuation hint that needs lifecycle validation."""

    bundle_id: BundleId

    def __post_init__(self) -> None:
        if not isinstance(self.bundle_id, BundleId):
            raise TypeError("bundle_id_required")

    @classmethod
    def from_value(cls, value: str) -> CurrentBundleHandle:
        return cls(BundleId(value))


class BundleStateStore:
    """Atomic, revision-checked State file store for one already-selected Bundle."""

    def __init__(self, *, root: Path, bundle_id: BundleId) -> None:
        self._root = Path(root)
        self._bundle_id = bundle_id
        self._coordinator = BundleTransitionCoordinator(root=self._root)

    async def initialize(self, state: BundleLocalState) -> BundleLocalState:
        self._validate_state(state)
        return await self._run_sync(self._initialize_sync, state, None)

    async def read(self, *, lease: BundleTransitionLease | None = None) -> BundleLocalState:
        return await self._run_sync(self._read_sync, lease)

    async def write(
        self,
        state: BundleLocalState,
        *,
        expected_revision: int,
        lease: BundleTransitionLease,
    ) -> BundleLocalState:
        self._validate_state(state)
        if not isinstance(expected_revision, int) or expected_revision < 0:
            raise ValueError("state_revision_invalid")
        if not isinstance(lease, BundleTransitionLease):
            raise TypeError("bundle_transition_lease_required")
        return await self._run_sync(self._write_sync, state, expected_revision, lease)

    @asynccontextmanager
    async def transition(self) -> AsyncIterator[BundleTransitionLease]:
        """Serialize one State read/reduce/write across runtime instances/processes."""

        try:
            async with self._coordinator.hold() as lease:
                yield lease
        except BundleTransitionError as exc:
            raise BundleLifecycleError("bundle_unavailable") from exc

    @staticmethod
    async def _run_sync(function: Callable[..., BundleLocalState], *args: Any) -> BundleLocalState:
        try:
            return await asyncio.to_thread(function, *args)
        except BundleTransitionError as exc:
            raise BundleLifecycleError("bundle_unavailable") from exc

    def _validate_state(self, state: BundleLocalState) -> None:
        if not isinstance(state, BundleLocalState):
            raise TypeError("bundle_state_required")
        if state.bundle_id != self._bundle_id:
            raise ValueError("bundle_state_identity_mismatch")

    @property
    def _state_path(self) -> Path:
        return self._root / _STATE_FILENAME

    def _ensure_root(self, lease: BundleTransitionLease | None = None) -> None:
        if lease is not None:
            lease.ensure_live()
            return
        if self._root.is_symlink() or not self._root.is_dir():
            raise BundleLifecycleError("bundle_unavailable")

    def _initialize_sync(self, state: BundleLocalState, lease: BundleTransitionLease | None) -> BundleLocalState:
        self._ensure_root(lease)
        if self._state_path.exists():
            existing = self._read_sync(lease)
            if existing != state:
                raise ValueError("bundle_state_already_initialized")
            return existing
        self._write_atomic(state, lease)
        return state

    def _read_sync(self, lease: BundleTransitionLease | None = None) -> BundleLocalState:
        self._ensure_root(lease)
        try:
            if lease is None:
                path = self._state_path
                if path.is_symlink() or not path.is_file():
                    raise BundleLifecycleError("bundle_unavailable")
                raw = path.read_bytes()
            else:
                raw = self._read_from_lease(lease)
            value = json.loads(raw)
            state = BundleLocalState.from_mapping(value)
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise BundleLifecycleError("bundle_state_invalid") from exc
        self._validate_state(state)
        return state

    def _write_sync(
        self,
        state: BundleLocalState,
        expected_revision: int,
        lease: BundleTransitionLease | None = None,
    ) -> BundleLocalState:
        current = self._read_sync(lease)
        if current.revision != expected_revision:
            raise ValueError("state_revision_conflict")
        next_state = replace(state, revision=expected_revision + 1)
        self._write_atomic(next_state, lease)
        return next_state

    @staticmethod
    def _read_from_lease(lease: BundleTransitionLease) -> bytes:
        try:
            fd = os.open(_STATE_FILENAME, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=lease.directory_fd)
        except OSError as exc:
            raise BundleLifecycleError("bundle_unavailable") from exc
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                raise BundleLifecycleError("bundle_unavailable")
            remaining = info.st_size
            chunks: list[bytes] = []
            while remaining:
                chunk = os.read(fd, min(remaining, 64 * 1024))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            raw = b"".join(chunks)
            if len(raw) != info.st_size:
                raise BundleLifecycleError("bundle_state_invalid")
            return raw
        finally:
            os.close(fd)

    def _write_atomic(self, state: BundleLocalState, lease: BundleTransitionLease | None = None) -> None:
        self._ensure_root(lease)
        payload = json.dumps(state.to_mapping(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        temporary_name = f".state.{secrets.token_hex(16)}.tmp"
        temporary = self._root / temporary_name
        try:
            if lease is None:
                fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
            else:
                fd = os.open(
                    temporary_name,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW,
                    0o600,
                    dir_fd=lease.directory_fd,
                )
            try:
                view = memoryview(payload)
                while view:
                    written = os.write(fd, view)
                    view = view[written:]
                os.fsync(fd)
            finally:
                os.close(fd)
            # Recheck after staging so deletion cannot cause a replacement root.
            self._ensure_root(lease)
            if lease is None:
                os.replace(temporary, self._state_path)
                BundleLifecycle._fsync_directory(self._root)
            else:
                os.replace(
                    temporary_name,
                    _STATE_FILENAME,
                    src_dir_fd=lease.directory_fd,
                    dst_dir_fd=lease.directory_fd,
                )
                os.fsync(lease.directory_fd)
                lease.ensure_live()
        except OSError as exc:
            try:
                if lease is None:
                    temporary.unlink()
                else:
                    os.unlink(temporary_name, dir_fd=lease.directory_fd)
            except OSError:
                pass
            raise BundleLifecycleError("bundle_unavailable") from exc
        except BaseException:
            try:
                if lease is None:
                    temporary.unlink()
                else:
                    os.unlink(temporary_name, dir_fd=lease.directory_fd)
            except OSError:
                pass
            raise


def scope_bucket(*, effective_user_id: str, outer_thread_id: str) -> str:
    """Create a private containment bucket from trusted scope only.

    It is intentionally neither a public identity nor a durable lifecycle record.
    Length-prefixing makes the tuple encoding unambiguous before hashing.
    """

    values = (effective_user_id, outer_thread_id)
    if any(not isinstance(value, str) or not value or len(value) > 256 for value in values):
        raise ValueError("trusted_scope_invalid")
    payload = b"".join(len(value.encode("utf-8")).to_bytes(4, "big") + value.encode("utf-8") for value in values)
    return "s_" + base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).decode("ascii").rstrip("=")


class BundleLifecycle:
    """Create and discover available Run Bundles inside trusted scope.

    Transient directory exclusions serialize scope publication and terminal-to-active
    commits. They are neither persisted nor read by discovery, so Bundle-local State
    remains the only lifecycle truth.
    """

    def __init__(
        self,
        *,
        workspace_host_path: Path,
        fault_hook: FaultHook | None = None,
        rerun_policy: FullRerunPolicy | None = None,
    ) -> None:
        self._workspace_host_path = Path(workspace_host_path)
        self._fault_hook = fault_hook
        self._rerun_policy = rerun_policy or FullRerunPolicy()
        if self._rerun_policy.max_rerun_generations > 2:
            raise ValueError("public_generation_ceiling_exceeded")

    @property
    def rerun_policy(self) -> FullRerunPolicy:
        """Return the immutable capacity policy selected by trusted composition."""

        return self._rerun_policy

    async def start(
        self,
        *,
        scope: tuple[str, str],
        request_text: str,
        start_message_id: str | None = None,
        implementation_mode: ImplementationMode = ImplementationMode.ALL_REAL,
    ) -> RunBundleRef:
        """Atomically publish a fresh initialized Bundle when no active Bundle exists."""

        bucket = self._bucket_for(scope)
        if not isinstance(request_text, str) or not request_text.strip() or len(request_text) > MAX_START_REQUEST_CHARS:
            raise ValueError("start_request_invalid")
        async with self.scope_exclusion(scope=scope) as scope_lease:
            active = await self.discover_active(scope=scope)
            if active is not None:
                raise BundleAlreadyActive(active)
            bundle = RunBundleRef(bundle_id=new_bundle_id(), scope_bucket=bucket)
            initial_state = BundleLocalState(
                bundle_id=bundle.bundle_id,
                start_message_id=start_message_id,
                start_request_digest=self.request_digest(request_text),
                implementation_mode=implementation_mode,
            )
            scope_lease.ensure_live()
            await asyncio.to_thread(self._publish_sync, bundle, initial_state, scope_lease)
            scope_lease.ensure_live()
            return bundle

    async def discover_active(self, *, scope: tuple[str, str]) -> RunBundleRef | None:
        """Select exactly one active Bundle from its trusted private bucket."""

        bucket = self._bucket_for(scope)
        return await asyncio.to_thread(self._discover_active_sync, bucket)

    async def resolve_active(
        self,
        *,
        scope: tuple[str, str],
        handle: CurrentBundleHandle | None,
    ) -> RunBundleRef | None:
        """Validate a Handle or select the sole active Bundle in the trusted scope."""

        bucket = self._bucket_for(scope)
        if handle is None:
            return await self.discover_active(scope=scope)
        if not isinstance(handle, CurrentBundleHandle):
            raise TypeError("bundle_handle_invalid")
        candidate = RunBundleRef(bundle_id=handle.bundle_id, scope_bucket=bucket)
        try:
            state = await self.read_state(candidate)
        except BundleLifecycleError:
            # A Handle that points outside this scope must not disclose that a Bundle
            # exists elsewhere. It is simply unavailable in the current scope.
            return None
        return candidate if state.is_active else None

    async def resolve(
        self,
        *,
        scope: tuple[str, str],
        bundle_id: BundleId | None = None,
        handle: CurrentBundleHandle | None = None,
    ) -> RunBundleRef | None:
        """Resolve an explicit available Bundle or the one active scoped Bundle."""

        return await self._resolve_for_control(scope=scope, bundle_id=bundle_id, handle=handle)

    async def read_state(self, bundle: RunBundleRef) -> BundleLocalState:
        """Read the selected Bundle-local State without any external fallback."""

        return await self._state_store(bundle).read()

    @asynccontextmanager
    async def scope_exclusion(self, *, scope: tuple[str, str]) -> AsyncIterator[BundleTransitionLease]:
        """Serialize fresh publication and ended reactivation without scope facts."""

        bucket = self._bucket_for(scope)
        root = await asyncio.to_thread(self._ensure_scope_root_sync, bucket)
        coordinator = BundleTransitionCoordinator(root=root)
        try:
            async with coordinator.hold() as lease:
                lease.ensure_live()
                yield lease
        except BundleTransitionError as exc:
            raise BundleLifecycleError("bundle_scope_unavailable") from exc

    @asynccontextmanager
    async def execution_exclusion(self, bundle: RunBundleRef) -> AsyncIterator[BundleTransitionLease]:
        """Hold a Bundle-local graph-execution exclusion without a lock file."""

        if not isinstance(bundle, RunBundleRef):
            raise TypeError("bundle_required")
        root = self.private_root(bundle)
        coordinator = BundleTransitionCoordinator(
            root=root / DIAGNOSTICS_SUBTREE,
            liveness_root=root,
        )
        try:
            async with coordinator.hold() as lease:
                lease.ensure_live()
                yield lease
        except BundleTransitionError as exc:
            raise BundleLifecycleError("bundle_unavailable") from exc

    @asynccontextmanager
    async def open_graph_checkpoint(
        self,
        bundle: RunBundleRef,
        *,
        lease: BundleTransitionLease | None = None,
    ) -> AsyncIterator[Any]:
        """Open the selected Bundle's recoverable graph store with no fallback.

        The caller receives only the saver object.  The SQLite path remains private to
        the lifecycle boundary and availability is checked again after the connection
        opens, so a removed Bundle cannot become a new replacement checkpoint root.
        """

        if not isinstance(bundle, RunBundleRef):
            raise TypeError("bundle_required")
        store = self._state_store(bundle)
        await store.read(lease=lease)
        database_path = self.private_root(bundle) / _GRAPH_FILENAME
        await asyncio.to_thread(self._prepare_graph_checkpoint_sync, bundle, lease)
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

        try:
            async with AsyncSqliteSaver.from_conn_string(str(database_path)) as saver:
                await store.read(lease=lease)
                yield saver
        except asyncio.CancelledError:
            raise
        except BundleLifecycleError:
            raise
        except (OSError, RuntimeError, ValueError) as exc:
            raise BundleLifecycleError("bundle_unavailable") from exc

    async def set_pending_request(
        self,
        *,
        bundle: RunBundleRef,
        request_id: str,
        suspension_cursor: str | None = None,
    ) -> BundleLocalState:
        """Record one current correlated human-input request in Bundle-local State."""

        if not isinstance(request_id, str) or not request_id or len(request_id) > 128:
            raise ValueError("pending_request_id_invalid")
        return await self._mutate_state(
            bundle,
            lambda state: replace(
                state,
                phase=LogicalPhase.HITL1,
                phase_status=PhaseStatus.WAITING,
                waiting_for="hitl1",
                pending_request_id=request_id,
                pending_cursor=suspension_cursor or state.start_message_id,
            ),
        )

    async def cancel(
        self,
        *,
        scope: tuple[str, str],
        bundle_id: BundleId | None = None,
        handle: CurrentBundleHandle | None = None,
    ) -> BundleLocalState:
        """Apply the one terminal cancel transition to a selected available Bundle."""

        bundle = await self._resolve_for_control(scope=scope, bundle_id=bundle_id, handle=handle)
        if bundle is None:
            raise BundleLifecycleError("bundle_unavailable")
        return await self._mutate_state(
            bundle,
            lambda state: (
                state
                if not state.is_active
                else replace(
                    state,
                    phase_status=PhaseStatus.TERMINAL,
                    terminal_status=LifecycleStatus.CANCELLED,
                    waiting_for=None,
                    pending_request_id=None,
                    pending_cursor=None,
                    pending_request_mode=None,
                )
            ),
        )

    async def resume(
        self,
        *,
        scope: tuple[str, str],
        response: AcceptedHumanResponse,
        bundle_id: BundleId | None = None,
        handle: CurrentBundleHandle | None = None,
    ) -> BundleLocalState:
        """Consume only the latest correlated response from the selected Bundle."""

        bundle = await self._resolve_for_control(scope=scope, bundle_id=bundle_id, handle=handle)
        if bundle is None:
            raise BundleLifecycleError("bundle_unavailable")
        try:
            return await self._mutate_state(bundle, lambda state: consume_bundle_response(state, response))
        except ValueError as exc:
            if str(exc) == "response_mismatch":
                raise BundleLifecycleError("response_mismatch") from exc
            raise

    async def admit_refinement(
        self,
        *,
        scope: tuple[str, str],
        text: str | None,
        operation_key: str | None,
        bundle_id: BundleId | None = None,
        handle: CurrentBundleHandle | None = None,
    ) -> RefinementAdmission:
        """Admit or select one bounded refinement without starting graph work."""

        if text is None and bundle_id is None:
            raise ValueError("textless_refinement_requires_bundle_id")
        if text is not None and (not isinstance(operation_key, str) or not operation_key):
            raise ValueError("refinement_operation_key_required")
        refinement = RefinementOperation.from_text(operation_key=operation_key, text=text) if text is not None else None
        bucket = self._bucket_for(scope)
        if bundle_id is None and handle is not None:
            candidate = RunBundleRef(bundle_id=handle.bundle_id, scope_bucket=bucket)
            try:
                candidate_state = await self.read_state(candidate)
            except BundleLifecycleError:
                raise BundleLifecycleError("bundle_unavailable") from None
            if not candidate_state.is_active:
                raise BundleLifecycleError("explicit_bundle_id_required")
            bundle = candidate
        elif bundle_id is None:
            bundle = await self.discover_active(scope=scope)
        else:
            bundle = await self._explicit_bundle(scope=scope, bundle_id=bundle_id)
        if bundle is None:
            raise BundleLifecycleError("bundle_unavailable")

        if refinement is None:
            return await self._select_terminal_pending_refinement(bundle)
        return await self._admit_state_refinement(scope=scope, bundle=bundle, refinement=refinement)

    async def end(
        self,
        *,
        bundle: RunBundleRef,
        terminal_status: LifecycleStatus = LifecycleStatus.COMPLETED,
    ) -> BundleLocalState:
        """Runtime-internal terminal transition used by graph completion/cancellation."""

        if terminal_status not in {
            LifecycleStatus.COMPLETED,
            LifecycleStatus.STOPPED,
            LifecycleStatus.CANCELLED,
            LifecycleStatus.BLOCKED,
        }:
            raise ValueError("terminal_status_invalid")

        return await self._mutate_state(
            bundle,
            lambda state: replace(
                state,
                phase_status=PhaseStatus.TERMINAL,
                terminal_status=terminal_status,
                waiting_for=None,
                pending_request_id=None,
            ),
        )

    async def sync_graph_progress(
        self,
        *,
        bundle: RunBundleRef,
        values: dict[str, Any],
        pending: Any | None,
    ) -> BundleLocalState:
        """Mirror bounded graph progress into the selected Bundle State.

        The graph checkpoint is itself Bundle-contained, but public lifecycle facts
        remain projected from ``state.json``.  This method copies only the closed
        phase/pending/terminal/trace facts after the graph has committed them.
        """

        try:
            phase = LogicalPhase(values.get("phase", LogicalPhase.BOOTSTRAP))
            raw_status = values.get("phase_status", PhaseStatus.IN_PROGRESS)
            phase_status = PhaseStatus(raw_status)
            raw_terminal = values.get("terminal_status")
            terminal = LifecycleStatus(raw_terminal) if raw_terminal is not None else None
            raw_reason = values.get("terminal_reason")
            terminal_reason = TerminalReason(raw_reason) if raw_reason is not None else None
            raw_incident = values.get("latest_incident")
            terminal_incident = (
                TerminalIncidentProjection.model_validate(raw_incident) if raw_incident is not None else None
            )
            generation = int(values.get("generation", 0))
            trace = tuple(str(item) for item in values.get("execution_trace", ()))
        except (TypeError, ValueError) as exc:
            raise BundleLifecycleError("bundle_graph_invalid") from exc
        if terminal not in {
            None,
            LifecycleStatus.COMPLETED,
            LifecycleStatus.STOPPED,
            LifecycleStatus.CANCELLED,
            LifecycleStatus.BLOCKED,
        }:
            raise BundleLifecycleError("bundle_graph_invalid")
        if len(trace) > 256:
            raise BundleLifecycleError("bundle_graph_invalid")

        graph_round_token = values.get("refinement_round_token")

        def apply(state: BundleLocalState) -> BundleLocalState:
            if not self._graph_progress_is_authorized(
                state=state,
                generation=generation,
                round_token=graph_round_token,
                phase_status=phase_status,
                terminal_status=terminal,
            ):
                return state
            if pending is not None:
                request = pending.request
                return replace(
                    state,
                    generation=generation,
                    phase=phase,
                    phase_status=PhaseStatus.WAITING,
                    terminal_status=None,
                    terminal_reason=None,
                    latest_incident=None,
                    waiting_for=pending.phase,
                    pending_request_id=request.request_id,
                    pending_cursor=pending.suspension_cursor,
                    pending_request_mode=request.mode,
                    execution_trace=trace,
                )
            return replace(
                state,
                generation=generation,
                phase=phase,
                phase_status=phase_status,
                terminal_status=terminal,
                terminal_reason=terminal_reason,
                latest_incident=terminal_incident,
                waiting_for=None,
                pending_request_id=None,
                pending_cursor=None,
                pending_request_mode=None,
                execution_trace=trace,
            )

        return await self._mutate_state(bundle, apply)

    @staticmethod
    def _graph_progress_is_authorized(
        *,
        state: BundleLocalState,
        generation: int,
        round_token: object,
        phase_status: PhaseStatus,
        terminal_status: LifecycleStatus | None,
    ) -> bool:
        """Fence stale graph snapshots from replacing current lifecycle facts."""

        if state.terminal_status is not None:
            return (
                generation == state.generation
                and phase_status is PhaseStatus.TERMINAL
                and terminal_status is state.terminal_status
            )
        if state.current_refinement is not None:
            return (
                generation == state.generation
                and isinstance(round_token, str)
                and round_token == state.current_refinement.round_token
            )
        return True

    async def status(
        self,
        *,
        scope: tuple[str, str],
        bundle_id: BundleId | None = None,
        handle: CurrentBundleHandle | None = None,
    ) -> BundleControlResult:
        """Return a bounded availability result after Bundle-local validation."""

        try:
            bundle = await self._resolve_for_control(scope=scope, bundle_id=bundle_id, handle=handle)
            if bundle is None:
                return self._unavailable_result(action=LifecycleAction.STATUS)
            state = await self.read_state(bundle)
            return self.result_for_state(action=LifecycleAction.STATUS, bundle=bundle, state=state)
        except BundleLifecycleError as exc:
            code = ResultCode.AMBIGUOUS if exc.code == "bundle_discovery_ambiguous" else ResultCode.UNAVAILABLE
            return self._unavailable_result(action=LifecycleAction.STATUS, code=code)

    @staticmethod
    def _unavailable_result(
        *,
        action: LifecycleAction,
        code: ResultCode = ResultCode.UNAVAILABLE,
    ) -> BundleControlResult:
        return BundleControlResult(
            action=action,
            code=code,
            availability=BundleAvailability.UNAVAILABLE,
            durability=Durability.UNAVAILABLE,
            legal_next_action=LegalNextAction.START,
        )

    def result_for_state(
        self,
        *,
        action: LifecycleAction,
        bundle: RunBundleRef,
        state: BundleLocalState,
        code: ResultCode | None = None,
    ) -> BundleControlResult:
        """Project one validated Bundle State without leaking its runtime locator."""

        refinement = self._refinement_projection(state)
        if state.is_active:
            waiting = state.pending_request_id is not None
            status = LifecycleStatus.SUSPENDED if waiting else LifecycleStatus.ACTIVE
            result_code = code or (ResultCode.SUSPENDED if waiting else ResultCode.ACTIVE)
            if waiting:
                next_action = LegalNextAction.RESUME
            elif state.admitted_refinement is not None or state.current_refinement is not None:
                next_action = LegalNextAction.STATUS
            else:
                next_action = LegalNextAction.REFINE
            pending_input = (
                PendingInputProjection(
                    request_id=state.pending_request_id,
                    pending_phase=state.waiting_for or state.phase.value,
                    generation=state.generation,
                    mode=(state.pending_request_mode.value if state.pending_request_mode is not None else "text"),
                )
                if waiting
                else None
            )
        else:
            waiting = False
            status = state.terminal_status
            if status is None:
                raise BundleLifecycleError("bundle_state_invalid")
            result_code = code or ResultCode(status.value)
            next_action = (
                LegalNextAction.REFINE
                if self._rerun_policy.allows_next_full_rerun(state.generation)
                else LegalNextAction.START
            )
            pending_input = None
        return BundleControlResult(
            implementation_mode=state.implementation_mode,
            action=action,
            code=result_code,
            availability=BundleAvailability.AVAILABLE,
            durability=Durability.RESTART_DURABLE,
            bundle_id=bundle.bundle_id.value,
            status=status,
            phase=state.phase,
            generation=state.generation,
            request_id=state.pending_request_id if waiting else None,
            pending_input=pending_input,
            terminal_reason=state.terminal_reason,
            terminal_incident=state.latest_incident,
            refinement=refinement,
            legal_next_action=next_action,
            execution_trace=state.execution_trace,
        )

    @staticmethod
    def _refinement_projection(state: BundleLocalState) -> BundleRefinementProjection:
        """Project only the public direction disposition from persisted State."""

        if state.current_refinement is not None:
            disposition = (
                BundleRefinementDisposition.APPLIED_WITH_PENDING
                if state.admitted_refinement is not None
                else BundleRefinementDisposition.APPLIED
            )
            return BundleRefinementProjection(
                disposition=disposition,
                current_round=state.current_refinement.round,
            )
        if state.admitted_refinement is not None:
            return BundleRefinementProjection(disposition=BundleRefinementDisposition.PENDING)
        return BundleRefinementProjection(disposition=BundleRefinementDisposition.NONE)

    def private_root(self, bundle: RunBundleRef) -> Path:
        """Return a runtime-private root for a preselected Bundle reference."""

        if not isinstance(bundle, RunBundleRef):
            raise TypeError("bundle_required")
        return self._scope_root(bundle.scope_bucket) / bundle.bundle_id.value

    def _state_store(self, bundle: RunBundleRef) -> BundleStateStore:
        return BundleStateStore(root=self.private_root(bundle), bundle_id=bundle.bundle_id)

    def _prepare_graph_checkpoint_sync(
        self,
        bundle: RunBundleRef,
        lease: BundleTransitionLease | None = None,
    ) -> None:
        if lease is not None:
            lease.ensure_live()
        root = self.private_root(bundle)
        if root.is_symlink() or not root.is_dir():
            raise BundleLifecycleError("bundle_unavailable")
        database = root / _GRAPH_FILENAME
        if database.exists() and (database.is_symlink() or not database.is_file()):
            raise BundleLifecycleError("bundle_unavailable")
        if lease is not None:
            lease.ensure_live()

    async def commit_prepared_refinement_round(
        self,
        *,
        bundle: RunBundleRef,
        expected_state: BundleLocalState,
        lease: BundleTransitionLease,
    ) -> BundleLocalState:
        """CAS one pending direction after its matching checkpoint writer prepared it."""

        if not isinstance(expected_state, BundleLocalState):
            raise TypeError("bundle_state_required")
        store = self._state_store(bundle)
        lease.ensure_live()
        current = await store.read(lease=lease)
        if current != expected_state:
            raise BundleLifecycleError("state_revision_conflict")
        try:
            applied = consume_admitted_refinement(current, policy=self._rerun_policy)
        except ValueError as exc:
            raise BundleLifecycleError("refinement_transition_invalid") from exc
        lease.ensure_live()
        return await store.write(applied, expected_revision=current.revision, lease=lease)

    async def _mutate_state(
        self,
        bundle: RunBundleRef,
        mutation: Callable[[BundleLocalState], BundleLocalState],
    ) -> BundleLocalState:
        store = self._state_store(bundle)
        async with store.transition() as lease:
            current = await store.read(lease=lease)
            updated = mutation(current)
            if updated == current:
                return current
            return await store.write(updated, expected_revision=current.revision, lease=lease)

    async def _admit_state_refinement(
        self,
        *,
        scope: tuple[str, str],
        bundle: RunBundleRef,
        refinement: RefinementOperation,
    ) -> RefinementAdmission:
        store = self._state_store(bundle)
        async with store.transition() as lease:
            current = await store.read(lease=lease)
            if not current.is_active:
                # An explicit available ended Bundle may admit a pending direction
                # only when no different active Bundle occupies the trusted scope.
                # Phase 1 intentionally leaves graph work and consumption pending.
                active = await self.discover_active(scope=scope)
                if active is not None and active != bundle:
                    raise BundleAlreadyActive(active)
            admission = admit_bundle_refinement(current, refinement, policy=self._rerun_policy)
            if admission.state == current:
                return admission
            written = await store.write(admission.state, expected_revision=current.revision, lease=lease)
            return RefinementAdmission(
                state=written,
                disposition=admission.disposition,
                newly_admitted=admission.newly_admitted,
            )

    async def _select_terminal_pending_refinement(self, bundle: RunBundleRef) -> RefinementAdmission:
        """Validate the narrow textless selection form under the shared exclusion."""

        store = self._state_store(bundle)
        async with store.transition() as lease:
            current = await store.read(lease=lease)
            if current.is_active or current.admitted_refinement is None:
                raise ValueError("refinement_continuation_invalid")
            if not self._rerun_policy.allows_next_full_rerun(current.generation):
                return RefinementAdmission(
                    state=current,
                    disposition=RefinementAdmissionDisposition.EXHAUSTED,
                )
            return RefinementAdmission(
                state=current,
                disposition=RefinementAdmissionDisposition.PENDING,
            )

    async def _explicit_bundle(self, *, scope: tuple[str, str], bundle_id: BundleId) -> RunBundleRef | None:
        if not isinstance(bundle_id, BundleId):
            raise TypeError("bundle_id_required")
        bundle = RunBundleRef(bundle_id=bundle_id, scope_bucket=self._bucket_for(scope))
        try:
            await self.read_state(bundle)
        except BundleLifecycleError:
            return None
        return bundle

    async def _resolve_for_control(
        self,
        *,
        scope: tuple[str, str],
        bundle_id: BundleId | None,
        handle: CurrentBundleHandle | None,
    ) -> RunBundleRef | None:
        if bundle_id is not None:
            return await self._explicit_bundle(scope=scope, bundle_id=bundle_id)
        return await self.resolve_active(scope=scope, handle=handle)

    def _bucket_for(self, scope: tuple[str, str]) -> str:
        if not isinstance(scope, tuple) or len(scope) != 2:
            raise ValueError("trusted_scope_invalid")
        return scope_bucket(effective_user_id=scope[0], outer_thread_id=scope[1])

    @staticmethod
    def request_digest(request_text: str) -> str:
        payload = request_text.encode("utf-8")
        return "d_" + base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).decode("ascii").rstrip("=")

    def _scope_root(self, bucket: str) -> Path:
        # Bundle ids and buckets are validated domain values. The directory layout is
        # private to this runtime boundary and never becomes a tool/result locator.
        return self._workspace_host_path / "deep-research" / "scopes" / bucket

    def _ensure_scope_root_sync(self, bucket: str) -> Path:
        """Create and validate the trusted scope directory before locking it."""

        scope_root = self._scope_root(bucket)
        try:
            scope_root.mkdir(mode=0o700, parents=True, exist_ok=True)
        except OSError as exc:
            raise BundleLifecycleError("bundle_storage_unavailable") from exc
        if scope_root.is_symlink() or not scope_root.is_dir():
            raise BundleLifecycleError("bundle_storage_unavailable")
        return scope_root

    def _fault(self, point: str) -> None:
        if self._fault_hook is not None:
            self._fault_hook(point)

    def _publish_sync(
        self,
        bundle: RunBundleRef,
        initial_state: BundleLocalState | None = None,
        scope_lease: BundleTransitionLease | None = None,
    ) -> None:
        scope_root = self._ensure_scope_root_sync(bundle.scope_bucket)
        if scope_lease is not None:
            scope_lease.ensure_live()

        root = self.private_root(bundle)
        staging = scope_root / f"{_STAGING_PREFIX}{bundle.bundle_id.value}"
        if root.exists() or staging.exists():
            raise BundleLifecycleError("bundle_id_collision")
        try:
            staging.mkdir(mode=0o700)
            for subtree in BUNDLE_SUBTREES:
                (staging / subtree).mkdir(mode=0o700)
            self._write_initial_state(staging, initial_state or BundleLocalState(bundle_id=bundle.bundle_id))
            self._fault("before_bundle_publish")
            if scope_lease is not None:
                scope_lease.ensure_live()
            os.replace(staging, root)
            self._fsync_directory(scope_root)
            if scope_lease is not None:
                scope_lease.ensure_live()
        except OSError as exc:
            # A staging Bundle has never been discoverable, so loss here cannot be
            # repaired by publishing a replacement root.
            if staging.exists() and not staging.is_symlink():
                try:
                    shutil.rmtree(staging)
                except OSError:
                    pass
            raise BundleLifecycleError("bundle_storage_unavailable") from exc
        except BaseException:
            # Staging is private and has never been published. A failed creation is
            # therefore invisible to scoped discovery and cannot be a control target.
            if staging.exists() and not staging.is_symlink():
                try:
                    shutil.rmtree(staging)
                except OSError:
                    pass
            raise

    @staticmethod
    def _fsync_directory(directory: Path) -> None:
        try:
            fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        except OSError as exc:
            raise BundleLifecycleError("bundle_storage_unavailable") from exc
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    @staticmethod
    def _write_initial_state(root: Path, state: BundleLocalState) -> None:
        payload = json.dumps(state.to_mapping(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        temporary = root / ".state.initial.tmp"
        try:
            fd = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
            try:
                view = memoryview(payload)
                while view:
                    written = os.write(fd, view)
                    view = view[written:]
                os.fsync(fd)
            finally:
                os.close(fd)
            os.replace(temporary, root / _STATE_FILENAME)
            BundleLifecycle._fsync_directory(root)
        except BaseException:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass
            raise

    def _discover_active_sync(self, bucket: str) -> RunBundleRef | None:
        root = self._scope_root(bucket)
        if not root.exists():
            return None
        if root.is_symlink() or not root.is_dir():
            raise BundleLifecycleError("bundle_scope_unavailable")
        active: list[RunBundleRef] = []
        try:
            entries = tuple(root.iterdir())
        except OSError as exc:
            raise BundleLifecycleError("bundle_scope_unavailable") from exc
        for entry in entries:
            if entry.name.startswith("."):
                continue
            if entry.is_symlink() or not entry.is_dir():
                raise BundleLifecycleError("bundle_candidate_invalid")
            try:
                candidate = RunBundleRef(bundle_id=BundleId(entry.name), scope_bucket=bucket)
                state = self._read_state_sync(candidate)
            except (OSError, ValueError, json.JSONDecodeError, BundleLifecycleError) as exc:
                raise BundleLifecycleError("bundle_candidate_unavailable") from exc
            if state.bundle_id != candidate.bundle_id:
                raise BundleLifecycleError("bundle_candidate_invalid")
            if state.is_active:
                active.append(candidate)
        if len(active) > 1:
            raise BundleLifecycleError("bundle_discovery_ambiguous")
        return active[0] if active else None

    def _read_state_sync(self, bundle: RunBundleRef) -> BundleLocalState:
        root = self.private_root(bundle)
        state_path = root / _STATE_FILENAME
        if root.is_symlink() or not root.is_dir() or state_path.is_symlink() or not state_path.is_file():
            raise BundleLifecycleError("bundle_unavailable")
        try:
            raw = state_path.read_bytes()
            value = json.loads(raw)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise BundleLifecycleError("bundle_unavailable") from exc
        try:
            state = BundleLocalState.from_mapping(value)
        except (TypeError, ValueError) as exc:
            raise BundleLifecycleError("bundle_state_invalid") from exc
        if state.bundle_id != bundle.bundle_id:
            raise BundleLifecycleError("bundle_state_identity_mismatch")
        return state


__all__ = [
    "BundleAlreadyActive",
    "BundleLifecycle",
    "BundleLifecycleError",
    "BundleStateStore",
    "CurrentBundleHandle",
    "scope_bucket",
]
