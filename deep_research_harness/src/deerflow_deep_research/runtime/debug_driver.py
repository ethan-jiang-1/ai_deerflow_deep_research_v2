"""Headless local debug driver over the one real graph.

Composes lifecycle admission, the existing executor's graph/observation
plumbing, and the C3 projector. Owns: start/attach sessions, at-most-once
boundary commands, the expiring control lease, stop policies, and recovery.
(`LDD-001`..`LDD-005`)
"""

from __future__ import annotations

import asyncio
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


async def publish_lifecycle_observation(
    lifecycle: Any,
    publisher: Any | None,
    bundle: Any,
    *,
    action: str,
    trace_delta: tuple[str, ...] = (),
) -> None:
    """Publish one durable lifecycle observation for a debug-driven Bundle.

    LDD-003 requires a debug run to behave like an ordinary run, and ordinary
    runs publish a lifecycle observation per accepted control result. Without
    this the retained run summary stays at the establishment fact, so operator
    views that read it (DPL-014's workspace report) called a cancelled Bundle
    resumable. Shared with the workbench's recovery cancel, which reaches the
    lifecycle without holding a driver session.

    Best-effort by contract: an observation failure never fails the command.
    """
    if publisher is None:
        return
    from deerflow_deep_research.domain.run_observation import RecordBearingLifecycleFact

    try:
        state = await lifecycle.read_state(bundle)
        terminal = getattr(state, "terminal_status", None)
        if terminal is not None:
            status = terminal.value
        else:
            status = "suspended" if getattr(state, "waiting_for", None) else "active"
        fact = RecordBearingLifecycleFact(
            bundle_id=bundle.bundle_id.value,
            action=action,
            status=status,
            phase=state.phase.value,
            generation=state.generation,
            durability="restart_durable",
            trace_delta=trace_delta,
            terminal_outcome=status if status in {"completed", "stopped", "cancelled", "blocked"} else None,
        )
    except asyncio.CancelledError:
        raise
    except (OSError, RuntimeError, TypeError, ValueError, AttributeError):
        return
    try:
        await publisher.publish(fact)
    except asyncio.CancelledError:
        raise
    except (OSError, RuntimeError, TypeError, ValueError):
        return


def _pending_request_view(pending: Any, *, state_feedback: Any = None) -> Any:
    """Project a checkpoint interrupt into the bounded request view (never rebuilt).

    RED-015/LDD-006: the view also carries the parsed hitl1 prompt card (one
    shared parsing authority; None when the context is not the published
    schema) and the node's last feedback — the interrupt's own interaction
    projection first, the Bundle's durable-state feedback second. Both are
    carried projections; neither is lifecycle authority.
    """
    if pending is None:
        return None
    from deerflow_deep_research.domain.debug_driving import PendingOptionView, PendingRequestView
    from deerflow_deep_research.domain.human_interaction import InteractionFeedback
    from deerflow_deep_research.runtime.run_experience import hitl1_prompt_card

    request = pending.request
    prompt = hitl1_prompt_card(request, request_id=request.request_id) if pending.phase == "hitl1" else None
    feedback = None if request.interaction is None else request.interaction.feedback
    if feedback is None and state_feedback is not None:
        try:
            feedback = (
                state_feedback
                if isinstance(state_feedback, InteractionFeedback)
                else InteractionFeedback.model_validate(state_feedback)
            )
        except (TypeError, ValueError):
            feedback = None
    return PendingRequestView(
        request_id=request.request_id,
        phase=pending.phase,
        mode=request.mode.value,
        title=request.title,
        context=request.context,
        options=tuple(PendingOptionView(option_id=str(option.id), label=option.label) for option in request.options),
        prompt=prompt,
        last_feedback=feedback,
    )


def _view_with_state_feedback(view: Any, state_feedback: Any) -> Any:
    """Fill a carried view's missing last_feedback from the durable state.

    LDD-006 fallback channel: a re-prompt without an interaction projection
    (an incomplete proposal) leaves the node's reply to the operator's last
    answer only in the Bundle's durable state. Carried projection only.
    """
    if view is None or view.last_feedback is not None or state_feedback is None:
        return view
    from deerflow_deep_research.domain.human_interaction import InteractionFeedback

    try:
        feedback = (
            state_feedback
            if isinstance(state_feedback, InteractionFeedback)
            else InteractionFeedback.model_validate(state_feedback)
        )
    except (TypeError, ValueError):
        return view
    return view.model_copy(update={"last_feedback": feedback})


_AUTO_HITL_MAX_STREAK = 2


def auto_hitl_eligible(pending: Any) -> bool:
    """LDD-008: only hitl1 text requests are auto-answerable by a drive policy.

    HITL2 direction decisions and choice prompts always wait for a human,
    regardless of the drive policy.
    """
    return pending is not None and pending.phase == "hitl1" and pending.mode == "text"


def auto_hitl_should_stop(streak: int) -> bool:
    """LDD-008 bound: after this many consecutive unaccepted auto-answers the
    drive stops and surfaces the node's reply for a human answer."""
    return streak >= _AUTO_HITL_MAX_STREAK


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
        observation_publisher: Any | None = None,
    ) -> None:
        self._lifecycle = lifecycle
        self._executor = executor
        self._envelope = envelope
        self._scope = scope
        self._owner = owner
        self._clock = clock
        self._lease_ttl = lease_ttl
        self._implementation_mode = implementation_mode
        self._observation_publisher = observation_publisher
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
            # BUG-079: the graph's fresh start reads the question from this
            # session carrier; without it the run silently executes on the
            # "Research" fallback instead of the operator's question.
            "question": request.question,
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
        await self._publish_observation(bundle, action="start")
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
            "pending_request": await self._read_pending_request(bundle),
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
            session["pending_request"] = None
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
            return await self._with_observation(
                bundle, DebugSessionUpdate(snapshot=snapshot, command_id=command.command_id), action="cancel"
            )

        if command.kind == "answer":
            session["ledger"].mark(command.command_id)
            return await self._with_observation(
                bundle, await self._answer(command, session, bundle, lease), action="resume"
            )

        if command.kind == "rerun_node":
            if session.get("in_flight"):
                session["ledger"].mark(command.command_id)
                return DebugSessionUpdate(command_id=command.command_id, denied="in_flight")
            session["ledger"].mark(command.command_id)
            return await self._with_observation(
                bundle, await self._rerun(command, session, bundle, lease), action="rerun"
            )

        if command.breakpoint is not None:
            session["stop_policy"] = command.breakpoint

        if command.kind == "advance_one":
            session["ledger"].mark(command.command_id)
            return await self._with_observation(
                bundle, await self._advance(command, session, bundle, lease, single=True), action="resume"
            )
        if command.kind == "drive_until":
            session["ledger"].mark(command.command_id)
            return await self._with_observation(
                bundle, await self._drive_until(command, session, bundle, lease), action="resume"
            )
        return DebugSessionUpdate(command_id=command.command_id, denied="invalid")

    # -- internals -------------------------------------------------------------

    async def _read_pending_request(self, bundle) -> Any:
        """Read the pending human request from the Bundle's own checkpoint.

        The read-only counterpart of the invocation path: attaching to a paused
        Bundle must still tell the operator what it is waiting for. A read
        failure never blocks the attach - it just leaves the request unknown.
        """
        from deerflow_deep_research.runtime.human_input import HumanInputError, pending_from_snapshot

        try:
            async with self._lifecycle.open_graph_checkpoint(bundle) as saver:
                graph = self._executor._recipe.builder.compile(checkpointer=saver)
                snapshot = await graph.aget_state(self._executor._config(bundle))
        except asyncio.CancelledError:
            raise
        except (OSError, RuntimeError, ValueError):
            return None
        try:
            return _pending_request_view(pending_from_snapshot(snapshot) if snapshot else None)
        except (HumanInputError, TypeError, ValueError):
            return None

    async def _publish_observation(self, bundle, *, action: str, trace_delta: tuple[str, ...] = ()) -> None:
        """Publish this command's lifecycle observation (see the module helper)."""
        await publish_lifecycle_observation(
            self._lifecycle,
            self._observation_publisher,
            bundle,
            action=action,
            trace_delta=trace_delta,
        )

    async def _with_observation(self, bundle, update: DebugSessionUpdate, *, action: str) -> DebugSessionUpdate:
        """Publish for an accepted command; a denial changes nothing to observe."""
        if update.denied is None:
            await self._publish_observation(bundle, action=action)
        return update

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
        # LDD-008: the auto-answer streak and the answered-request facts are
        # per-drive; a fresh drive starts with a clean bound.
        session["auto_hitl_streak"] = 0
        session["auto_hitl_answers"] = ()

        async def _settle_hitl(update: DebugSessionUpdate, pause_pending: bool) -> tuple[DebugSessionUpdate, bool]:
            """Answer eligible hitl1 stops under the explicit policy (bounded).

            HITL2, choice prompts, and the unaccepted-answer bound always fall
            back to the human.
            """
            while (
                update.snapshot.posture == "awaiting_hitl"
                and policy.auto_hitl
                and auto_hitl_eligible(update.snapshot.pending_request)
                and not auto_hitl_should_stop(int(session.get("auto_hitl_streak", 0) or 0))
            ):
                streak = int(session.get("auto_hitl_streak", 0) or 0) + 1
                session["auto_hitl_streak"] = streak
                answers = tuple(session.get("auto_hitl_answers") or ()) + ((update.snapshot.pending_request_id or ""),)
                session["auto_hitl_answers"] = answers
                update = await self._auto_answer(
                    session, bundle, lease, request_id=update.snapshot.pending_request_id, ordinal=len(answers)
                )
                if update.snapshot is None:
                    return update, pause_pending
                pause_pending = pause_pending or bool(session["pause_requested"])
                session["pause_requested"] = False
            return update, pause_pending

        # Seed: a drive typed at a HITL stop answers it (if the policy allows)
        # or stops - it never blind-advances a pending interrupt.
        pause_pending = bool(session["pause_requested"])
        session["pause_requested"] = False
        current = await self.session_snapshot(bundle.bundle_id.value)
        if current is not None and current.posture == "awaiting_hitl":
            last, pause_pending = await _settle_hitl(
                DebugSessionUpdate(snapshot=current, command_id=command.command_id), pause_pending
            )
            if last.snapshot is None:
                return last
            if last.snapshot.posture in {"awaiting_hitl", "terminal"}:
                return last
        last: DebugSessionUpdate | None = None
        for _ in range(64):
            # A pause takes effect at the next committed boundary (LDD-002), so
            # a pending pause makes this drive advance exactly one boundary and
            # stop - it never refuses to advance and never returns nothing.
            pause_pending = pause_pending or bool(session["pause_requested"])
            session["pause_requested"] = False
            last = await self._advance(command, session, bundle, lease, single=False)
            if last.snapshot is None:
                return last
            last, pause_pending = await _settle_hitl(last, pause_pending)
            if last.snapshot is None:
                return last
            posture = last.snapshot.posture
            if posture == "terminal":
                break
            if posture == "awaiting_hitl":
                break
            if pause_pending:
                break
            if policy.breakpoint_after:
                # A single advance may span several node visits (a committed
                # node followed by an interrupting one), so the breakpoint
                # matches when the named node has VISITED per the durable
                # trace - never only when it happens to be the last visit.
                state_now = await self._lifecycle.read_state(bundle)
                if policy.breakpoint_after in tuple(getattr(state_now, "execution_trace", None) or ()):
                    break
        return last  # type: ignore[return-value]

    async def _auto_answer(
        self, session, bundle, lease: ControlLease, *, request_id: str | None, ordinal: int
    ) -> DebugSessionUpdate:
        """Submit 确认 as an operator-policy answer (LDD-008); never silent."""
        if not request_id:
            return DebugSessionUpdate(command_id=f"auto-hitl-{ordinal}", denied="invalid")
        response = AcceptedHumanResponse(
            request_id=request_id,
            message_id=f"msg-auto-hitl-{ordinal}-{int(self._clock())}",
            value="确认",
            response_kind=ResponseKind.TEXT,
        )
        return await self._invoke_once(bundle, lease, session, resume_payload=response.model_dump(mode="json"))

    async def _rerun(self, command: DebugCommand, session, bundle, lease: ControlLease) -> DebugSessionUpdate:
        """LDD-007: rewind to just before the last committed node, re-execute it,
        and stop at the next stop (HITL/terminal).

        The rewind is expressed as a graph drive through the same executor and
        saver (checkpoint history fork); durable State follows through the
        controller's own projection sync. The driver writes no state directly,
        and the journal gains the rerun observation via the command action.
        """
        state = await self._lifecycle.read_state(bundle)
        trace = tuple(getattr(state, "execution_trace", None) or ())
        if not trace:
            return DebugSessionUpdate(
                command_id=command.command_id, denied="invalid", message="nothing committed to rerun"
            )
        tail = trace[-1]
        waiting_for = getattr(state, "waiting_for", None)
        if waiting_for and tail == waiting_for and len(trace) > 1:
            # The pending node's own visit sits at the trace tail on graphs that
            # record a visit while interrupted; the rerun target is the last
            # COMMITTED node before it, so the stop regenerates through a real
            # commit (fresh frame, rewritten card) instead of re-interrupting
            # in place.
            tail = trace[-2]
        fork_id = await self._find_rewind_point(bundle, tail)
        if fork_id is None:
            return DebugSessionUpdate(
                command_id=command.command_id, denied="invalid", message=f"no rewind point before {tail}"
            )
        session["in_flight"] = True
        try:
            update = await self._invoke_once(bundle, lease, session, resume_payload=None, fork_checkpoint_id=fork_id)
            if update.snapshot is None:
                return update
            # Run to the next stop so the operator faces the fresh result of
            # the rerun node (a regenerated HITL request, or the terminal), not
            # an intermediate pause.
            for _ in range(8):
                posture = update.snapshot.posture
                if posture in {"awaiting_hitl", "terminal"} or bool(session["pause_requested"]):
                    break
                update = await self._invoke_once(bundle, lease, session, resume_payload=None)
            return update
        finally:
            session["in_flight"] = False

    async def _find_rewind_point(self, bundle, tail: str) -> str | None:
        """Locate the checkpoint just before ``tail`` last committed (read-only).

        History is newest-first, so the first snapshot whose pending node is the
        rerun target is the latest state that had not yet executed it.
        """
        try:
            async with self._lifecycle.open_graph_checkpoint(bundle) as saver:
                graph = self._executor._recipe.builder.compile(checkpointer=saver)
                config = self._executor._config(bundle)
                async for historical in graph.aget_state_history(config):
                    if tuple(historical.next or ()) == (tail,):
                        return historical.config["configurable"]["checkpoint_id"]
        except asyncio.CancelledError:
            raise
        except (OSError, RuntimeError, ValueError):
            return None
        return None

    async def _advance(
        self, command: DebugCommand, session, bundle, lease: ControlLease, *, single: bool
    ) -> DebugSessionUpdate:
        session["in_flight"] = True
        try:
            return await self._invoke_once(bundle, lease, session, resume_payload=None)
        finally:
            session["in_flight"] = False

    async def _invoke_once(
        self,
        bundle,
        lease: ControlLease,
        session,
        *,
        resume_payload: dict[str, Any] | None,
        fork_checkpoint_id: str | None = None,
    ) -> DebugSessionUpdate:
        async with self._lifecycle.execution_exclusion(bundle) as execution_lease:
            execution_lease.ensure_live()
            async with self._lifecycle.open_graph_checkpoint(bundle) as saver:
                graph = self._executor._recipe.builder.compile(checkpointer=saver)
                config = self._executor._config(bundle)
                if fork_checkpoint_id is not None:
                    # LDD-007 rewind drive: resume the thread from the pinned
                    # historical checkpoint (the state just before the node
                    # last committed) so the invocation re-executes that node.
                    config = {
                        **config,
                        "configurable": {**config["configurable"], "checkpoint_id": fork_checkpoint_id},
                    }
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
                # The operator must not guess what a HITL stop is asking: carry the
                # node-authored request itself (title/guidance/mode/options).
                session["pending_request"] = _pending_request_view(pending)
                await self._lifecycle.sync_graph_progress(
                    bundle=bundle,
                    values=dict(post_values),
                    pending=pending,
                )
                committed = post_values.get("execution_trace") or ()
                committed_node = committed[-1] if committed else None
                # A pause requested while this boundary was in flight is honored
                # by the drive loop at this boundary, so it is not cleared here.
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
        session = self._sessions.get(bundle.bundle_id.value) or {}
        return DebugSessionSnapshot(
            bundle_id=bundle.bundle_id.value,
            cursor=cursor,
            mode=mode,
            posture=posture,
            stop_policy=stop_policy,
            pause_requested=pause_requested,
            lease=lease,
            pending_request_id=pending_request_id,
            pending_request=_view_with_state_feedback(session.get("pending_request"), state.interaction_feedback),
            auto_hitl_answers=tuple(session.get("auto_hitl_answers") or ()),
        )
