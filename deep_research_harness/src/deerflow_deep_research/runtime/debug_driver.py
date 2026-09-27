"""Headless local debug driver over the one real graph.

Composes lifecycle admission, the existing executor's graph/observation
plumbing, and the C3 projector. Owns: start/attach sessions, at-most-once
boundary commands, the expiring control lease, stop policies, and recovery.
(`LDD-001`..`LDD-005`)
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from langgraph.errors import GraphInterrupt
from langgraph.types import Command

from deerflow_deep_research.domain.debug_driving import (
    AttachRequest,
    BoundaryCursor,
    DebugCommand,
    DebugSessionSnapshot,
    DebugSessionUpdate,
    DriveMode,
    LeasePosture,
    SessionPosture,
    StartRequest,
    StopPolicy,
)
from deerflow_deep_research.domain.lifecycle import (
    AcceptedHumanResponse,
    ImplementationMode,
    ResponseKind,
)
from deerflow_deep_research.runtime.debug_driving import ControlLease, DebugCommandLedger
from deerflow_deep_research.runtime.human_input import pending_from_snapshot


class DebugDriverError(Exception):
    """Typed driver failure; message carries the closed reason."""


class DebugRunDriver:
    """Drives the one real graph boundary-by-boundary for a local operator."""

    def __init__(
        self,
        *,
        lifecycle,
        executor,
        envelope: Any,
        scope: tuple[str, str],
        owner: str = "local-debug-operator",
        clock: Callable[[], float] = time.time,
        lease_ttl: float = 300.0,
        implementation_mode: ImplementationMode = ImplementationMode.FIXTURE,
    ) -> None:
        self._lifecycle = lifecycle
        self._executor = executor
        self._envelope = envelope
        self._scope = scope
        self._owner = owner
        self._clock = clock
        self._lease_ttl = lease_ttl
        self._implementation_mode = implementation_mode
        self._sessions: dict[str, dict[str, Any]] = {}

    # -- session open ------------------------------------------------------

    async def open_start(self, request: StartRequest) -> DebugSessionUpdate:
        ledger = None
        from deerflow_deep_research.runtime.bundle_lifecycle import BundleAlreadyActive

        try:
            bundle = await self._lifecycle.start(
                scope=self._scope,
                request_text=request.question,
                implementation_mode=self._implementation_mode,
                start_message_id=request.command_id,
            )
        except BundleAlreadyActive as exc:
            return DebugSessionUpdate(command_id=request.command_id, denied="busy", message=str(exc))
        lease_root = self._lifecycle.private_root(bundle)
        lease = ControlLease(private_root=lease_root, clock=self._clock, ttl=self._lease_ttl)
        lease.acquire(request.owner)
        ledger = DebugCommandLedger(lease_root / "debug-commands.json")
        ledger.mark(request.command_id)
        self._sessions[bundle.bundle_id.value] = {
            "owner": request.owner,
            "mode": request.mode,
            "pause_requested": False,
            "lease": lease,
            "ledger": ledger,
            "stop_policy": StopPolicy(),
        }
        snapshot = await self._snapshot(
            bundle,
            mode=request.mode,
            pause_requested=False,
            lease=lease.snapshot(),
            stop_policy=StopPolicy(),
        )
        return DebugSessionUpdate(snapshot=snapshot, command_id=request.command_id)

    async def open_attach(self, request: AttachRequest) -> DebugSessionUpdate:
        bundle = await self._lifecycle.resolve(
            scope=self._scope,
            bundle_id=__import__("deerflow_deep_research.domain.bundle", fromlist=["BundleId"]).BundleId(
                request.bundle_id
            ),
        )
        if bundle is None:
            return DebugSessionUpdate(
                command_id=f"attach-{request.owner}", denied="not_found", message="bundle not resolvable"
            )
        lease_root = self._lifecycle.private_root(bundle)
        lease = ControlLease(private_root=lease_root, clock=self._clock, ttl=self._lease_ttl)
        posture = lease.snapshot()
        expected = request.expected_lease_generation
        if posture.live:
            # Live-owned: only an exact-generation CAS from the same owner
            # rebinds; everyone else is busy/read-only.
            if request.expected_lease_generation is None or request.owner != posture.owner:
                return DebugSessionUpdate(
                    command_id=f"attach-{request.owner}",
                    denied="busy",
                    message="live debug lease held by another owner",
                )
        taken = lease.cas_takeover(request.owner, expected if expected is not None else posture.generation)
        if taken is None:
            return DebugSessionUpdate(command_id=f"attach-{request.owner}", denied="busy", message="lease live")
        self._sessions[request.bundle_id] = {
            "owner": request.owner,
            "mode": "step",
            "pause_requested": False,
            "lease": lease,
            "ledger": DebugCommandLedger(lease_root / "debug-commands.json"),
            "stop_policy": StopPolicy(),
        }
        snapshot = await self._snapshot(
            bundle, mode="step", pause_requested=False, lease=lease.snapshot(), stop_policy=StopPolicy()
        )
        return DebugSessionUpdate(snapshot=snapshot, command_id=f"attach-{request.owner}")

    # -- command execution ---------------------------------------------------

    async def execute(self, command: DebugCommand) -> DebugSessionUpdate:
        session = self._sessions.get(command.bundle_id)
        if session is None:
            return DebugSessionUpdate(command_id=command.command_id, denied="not_found", message="no session")
        if session["ledger"].seen(command.command_id):
            return DebugSessionUpdate(command_id=command.command_id, denied="duplicate")
        lease: ControlLease = session["lease"]
        if lease.snapshot().live and lease.snapshot().owner != session["owner"]:
            session["ledger"].mark(command.command_id)
            return DebugSessionUpdate(command_id=command.command_id, denied="busy")

        bundle = await self._resolve(command.bundle_id)
        session["_last_command"] = command.command_id
        current_cursor = await self._boundary_cursor(bundle)
        if current_cursor.token() != command.expected_cursor:
            session["ledger"].mark(command.command_id)
            return DebugSessionUpdate(command_id=command.command_id, denied="stale")

        if command.kind == "pause_request":
            session["pause_requested"] = True
            session["ledger"].mark(command.command_id)
            snapshot = await self._snapshot(
                bundle,
                mode=session["mode"],
                pause_requested=True,
                lease=lease.snapshot(),
                stop_policy=session["stop_policy"],
            )
            return DebugSessionUpdate(snapshot=snapshot, command_id=command.command_id)

        if command.kind == "detach":
            if session.get("in_flight"):
                return DebugSessionUpdate(command_id=command.command_id, denied="in_flight")
            lease.release(session["owner"])
            self._sessions.pop(command.bundle_id, None)
            session["ledger"].mark(command.command_id)
            snapshot = await self._snapshot(
                bundle,
                mode=session["mode"],
                pause_requested=False,
                lease=lease.snapshot(),
                stop_policy=session["stop_policy"],
            )
            return DebugSessionUpdate(snapshot=snapshot, command_id=command.command_id)

        if command.kind == "cancel":
            session["ledger"].mark(command.command_id)
            await self._lifecycle.cancel(
                scope=self._scope,
                bundle_id=__import__("deerflow_deep_research.domain.bundle", fromlist=["BundleId"]).BundleId(
                    command.bundle_id
                ),
            )
            snapshot = await self._snapshot(
                bundle,
                mode=session["mode"],
                pause_requested=False,
                lease=lease.snapshot(),
                stop_policy=session["stop_policy"],
            )
            return DebugSessionUpdate(snapshot=snapshot, command_id=command.command_id)

        if command.kind == "answer":
            session["ledger"].mark(command.command_id)
            return await self._answer(command, session, bundle, lease)

        if command.breakpoint is not None:
            session["stop_policy"] = command.breakpoint

        if command.kind == "advance_one":
            session["ledger"].mark(command.command_id)
            return await self._advance(command, session, bundle, lease, single=True)
        if command.kind == "drive_until":
            session["ledger"].mark(command.command_id)
            return await self._drive_until(command, session, bundle, lease)
        return DebugSessionUpdate(command_id=command.command_id, denied="invalid")

    # -- internals -------------------------------------------------------------

    async def _resolve(self, bundle_id: str):
        from deerflow_deep_research.domain.bundle import BundleId

        return await self._lifecycle.resolve(scope=self._scope, bundle_id=BundleId(bundle_id))

    async def _answer(self, command: DebugCommand, session, bundle, lease: ControlLease) -> DebugSessionUpdate:
        state = await self._lifecycle.read_state(bundle)
        request_id = state.pending_request_id
        if not request_id or command.answer_text is None:
            return DebugSessionUpdate(command_id=command.command_id, denied="invalid")
        response = AcceptedHumanResponse(
            request_id=request_id,
            message_id=f"msg-{command.command_id}",
            value=command.answer_text,
            response_kind=ResponseKind.TEXT,
        )
        update = await self._invoke_once(bundle, lease, session, resume_payload=response.model_dump(mode="json"))
        return update

    async def _drive_until(self, command: DebugCommand, session, bundle, lease: ControlLease) -> DebugSessionUpdate:
        if command.breakpoint is not None:
            session["stop_policy"] = command.breakpoint
        policy: StopPolicy = session["stop_policy"]
        last: DebugSessionUpdate | None = None
        for _ in range(64):
            if session["pause_requested"]:
                break
            last = await self._advance(command, session, bundle, lease, single=False)
            if last.snapshot is None:
                return last
            cursor = last.snapshot.cursor
            if policy.stop_on_terminal and last.snapshot.posture == "terminal":
                break
            if (
                policy.breakpoint_after
                and cursor.next_nodes
                and policy.breakpoint_after in (node for node in cursor.next_nodes)
            ):
                break
            if policy.breakpoint_after and last.committed_node == policy.breakpoint_after:
                break
        return last  # type: ignore[return-value]

    async def _advance(
        self, command: DebugCommand, session, bundle, lease: ControlLease, *, single: bool
    ) -> DebugSessionUpdate:
        session["in_flight"] = True
        try:
            return await self._invoke_once(bundle, lease, session, resume_payload=None)
        finally:
            session["in_flight"] = False

    async def _invoke_once(
        self, bundle, lease: ControlLease, session, *, resume_payload: dict[str, Any] | None
    ) -> DebugSessionUpdate:
        async with self._lifecycle.execution_exclusion(bundle) as execution_lease:
            execution_lease.ensure_live()
            async with self._lifecycle.open_graph_checkpoint(bundle) as saver:
                graph = self._executor._recipe.builder.compile(checkpointer=saver)
                config = self._executor._config(bundle)
                snapshot = await graph.aget_state(config)
                fresh = not (snapshot and snapshot.values)
                next_nodes = tuple(snapshot.next or ()) if snapshot else ()
                if len(next_nodes) > 1:
                    raise DebugDriverError("topology_guard_multi_visit")
                target = next_nodes[0] if next_nodes else None
                state = await self._lifecycle.read_state(bundle)
                journal_envelope = await self._executor._journal_envelope(
                    lifecycle=self._lifecycle, bundle=bundle, state=state, envelope=self._envelope
                )
                graph_context = await self._executor._context(envelope=journal_envelope, bundle=bundle)
                if fresh:
                    from deerflow_deep_research.runtime.human_input import SelectedStartMessage

                    start_message = SelectedStartMessage(
                        message_id=f"start-{int(self._clock())}",
                        text=self._sessions[bundle.bundle_id.value].get("question", "Research"),
                    )
                    initial = self._executor._initial_graph_state(
                        bundle=bundle, state=state, start_message=start_message
                    )
                    invocation = graph.ainvoke(
                        initial,
                        config=config,
                        context=graph_context,
                        interrupt_after=[target] if target else None,
                    )
                elif resume_payload is not None:
                    invocation = graph.ainvoke(
                        Command(resume=resume_payload),
                        config=config,
                        context=graph_context,
                        interrupt_after=[target] if target else None,
                    )
                else:
                    if target is None:
                        return await self._terminal_update(bundle, lease, session)
                    invocation = graph.ainvoke(None, config=config, context=graph_context, interrupt_after=[target])
                try:
                    await invocation
                except GraphInterrupt:
                    raise
                execution_lease.ensure_live()
                post = await graph.aget_state(config)
                post_values = post.values if isinstance(post.values, dict) else {}
                pending = pending_from_snapshot(post)
                await self._lifecycle.sync_graph_progress(
                    bundle=bundle,
                    values=dict(post_values),
                    pending=pending,
                )
                committed = post_values.get("execution_trace") or ()
                committed_node = committed[-1] if committed else None
                session["pause_requested"] = False
                lease.heartbeat(session["owner"])
                snapshot = await self._snapshot(
                    bundle,
                    mode=session["mode"],
                    pause_requested=False,
                    lease=lease.snapshot(),
                    stop_policy=session["stop_policy"],
                    next_nodes=tuple(post.next or ()),
                )
                return DebugSessionUpdate(
                    snapshot=snapshot,
                    command_id=session.get("_last_command", "advance"),
                    committed_node=committed_node,
                )

    async def _terminal_update(self, bundle, lease, session) -> DebugSessionUpdate:
        snapshot = await self._snapshot(
            bundle,
            mode=session["mode"],
            pause_requested=False,
            lease=lease.snapshot(),
            stop_policy=session["stop_policy"],
            next_nodes=(),
        )
        return DebugSessionUpdate(snapshot=snapshot, command_id="advance")

    async def _boundary_cursor(self, bundle, *, next_nodes: tuple[str, ...] = ()) -> BoundaryCursor:
        """Project the durable boundary; ``next_nodes`` is projection-only.

        The write permit fences the durable identity (bundle, generation,
        frame, checkpoint) only, so the next-node projection never takes part
        in staleness. Exactly one source supplies it: the stepping path reads
        it from the compiled graph state. The trace-frame projection does not
        carry it (BUG-070), and no fallback pretends otherwise.
        """
        from deerflow_deep_research.runtime.trace_projector import RunTraceProjector

        page = await RunTraceProjector(self._lifecycle).project_full(bundle, live=True)
        last = page.frames[-1] if page.frames else None
        state = await self._lifecycle.read_state(bundle)
        return BoundaryCursor(
            bundle_id=bundle.bundle_id.value,
            generation=state.generation,
            frame_sequence=len(page.frames),
            checkpoint_id=last.checkpoint_id if last else None,
            next_nodes=next_nodes,
        )

    async def attach_posture(self, bundle_id: str, *, owner: str | None = None) -> str:
        """Read-only attach posture for one bundle (no takeover, no writes).

        RED-014's Attach entry needs candidate postures before anything is
        acquired. Returns one of ``unresolvable`` (no such bundle in this
        scope), ``takeover`` (no live lease), ``rebind`` (live lease held by
        this owner, so a generation CAS rebinds) or ``busy`` (live lease held
        by another owner; observation stays read-only). Lease semantics stay in
        the driver, so callers never read the lease themselves.
        """
        bundle = await self._resolve(bundle_id)
        if bundle is None:
            return "unresolvable"
        lease = ControlLease(private_root=self._lifecycle.private_root(bundle), clock=self._clock, ttl=self._lease_ttl)
        posture = lease.snapshot()
        if not posture.live:
            return "takeover"
        return "rebind" if posture.owner == (owner or self._owner) else "busy"

    async def session_snapshot(self, bundle_id: str) -> DebugSessionSnapshot | None:
        """Current snapshot of one live session, or None when this driver holds none.

        The debug workbench's client surface: callers read the session posture
        and cursor token through this method instead of reaching into the
        driver's private session table.
        """
        session = self._sessions.get(bundle_id)
        if session is None:
            return None
        bundle = await self._resolve(bundle_id)
        if bundle is None:
            return None
        return await self._snapshot(
            bundle,
            mode=session["mode"],
            pause_requested=bool(session.get("pause_requested")),
            lease=session["lease"].snapshot(),
            stop_policy=session["stop_policy"],
        )

    async def _snapshot(
        self,
        bundle,
        *,
        mode: DriveMode,
        pause_requested: bool,
        lease: LeasePosture,
        stop_policy: StopPolicy,
        next_nodes: tuple[str, ...] = (),
    ) -> DebugSessionSnapshot:
        cursor = await self._boundary_cursor(bundle, next_nodes=next_nodes)
        state = await self._lifecycle.read_state(bundle)
        from deerflow_deep_research.runtime.trace_projector import RunTraceProjector

        page = await RunTraceProjector(self._lifecycle).project_full(bundle, live=True)
        pending_request_id = state.pending_request_id
        if pending_request_id:
            posture: SessionPosture = "awaiting_hitl"
        elif state.terminal_status is not None:
            posture = "terminal"
        elif pause_requested:
            posture = "pause_requested"
        else:
            posture = "running" if page.active_visit is not None else "paused_at_boundary"
        return DebugSessionSnapshot(
            bundle_id=bundle.bundle_id.value,
            cursor=cursor,
            mode=mode,
            posture=posture,
            stop_policy=stop_policy,
            pause_requested=pause_requested,
            lease=lease,
            pending_request_id=pending_request_id,
        )
