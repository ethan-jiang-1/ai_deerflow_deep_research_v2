"""Runtime projector: durable facts in, honest versioned trace pages out.

The checkpoint is the commit authority; the journal is the bounded
causal-detail authority. The projector never fabricates frames from started or
pre-commit facts and never touches the graph. (`LDO-001`, `LDO-002`)
"""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from typing import Any

from deerflow_deep_research.domain.bundle import RunBundleRef
from deerflow_deep_research.domain.run_observation import (
    JournalAvailability,
    ObservationInspectability,
    RunEventCategory,
    RunObservationInspection,
)
from deerflow_deep_research.domain.trace import (
    ActiveVisitProjection,
    TraceFrame,
    TracePage,
)
from deerflow_deep_research.runtime.run_observation import RunObservationStore

_CURSOR_VERSION = "LDT1"
_FINAL_NODE_OUTCOMES = frozenset({"completed", "suspended", "failed"})


def _encode_cursor(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    body = base64.urlsafe_b64encode(raw).decode("ascii")
    digest = hashlib.sha256(raw).hexdigest()[:16]
    return f"{_CURSOR_VERSION}.{body}.{digest}"


def _decode_cursor(token: str, *, bundle_id: str) -> dict[str, Any]:
    try:
        version, body, digest = token.split(".")
        raw = base64.urlsafe_b64decode(body.encode("ascii"))
        if version != _CURSOR_VERSION or hashlib.sha256(raw).hexdigest()[:16] != digest:
            raise ValueError("trace_cursor_version_invalid")
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict) or payload.get("bundle_id") != bundle_id:
            raise ValueError("trace_cursor_bundle_mismatch")
        return payload
    except Exception as exc:
        raise ValueError("trace_cursor_invalid") from exc


@dataclass(frozen=True)
class _Suspension:
    """The checkpoint where the graph's human-interrupt pause is waiting."""

    checkpoint_id: str


@dataclass(frozen=True)
class _Commit:
    checkpoint_id: str
    node: str
    changed: tuple[str, ...]
    route: str | None
    generation: int | None
    terminal: str | None


class RunTraceProjector:
    """Project one verified Bundle's checkpoints + journal into trace pages."""

    def __init__(self, lifecycle) -> None:  # noqa: ANN001 — runtime composition seam
        self._lifecycle = lifecycle

    async def project_full(
        self, bundle: RunBundleRef, *, live: bool = False, page_size: int | None = None
    ) -> TracePage:
        """Project the whole Bundle. Replay callers keep ``live=False``."""
        return await self._project(bundle, live=live, after_frame_sequence=0, page_size=page_size)

    async def project_incremental(
        self, bundle: RunBundleRef, cursor: str, *, page_size: int | None = None
    ) -> tuple[TracePage, str]:
        """Resume a live read from an opaque cursor token (fail closed on tamper)."""
        payload = _decode_cursor(cursor, bundle_id=bundle.bundle_id.value)
        page = await self._project(
            bundle,
            live=True,
            after_frame_sequence=int(payload.get("frame_sequence", 0)),
            page_size=page_size,
        )
        return page, page.next_cursor or cursor

    # -- internal ----------------------------------------------------------

    async def _project(
        self,
        bundle: RunBundleRef,
        *,
        live: bool,
        after_frame_sequence: int,
        page_size: int | None,
    ) -> TracePage:
        commits, suspension, inspection = await self._collect(bundle)
        return self._build_page(
            bundle.bundle_id.value,
            commits,
            suspension,
            inspection,
            live=live,
            after_frame_sequence=after_frame_sequence,
            page_size=page_size,
        )

    async def _collect(
        self, bundle: RunBundleRef
    ) -> tuple[list[_Commit], _Suspension | None, RunObservationInspection]:
        commits: list[_Commit] = []
        async with self._lifecycle.open_graph_checkpoint(bundle) as saver:
            config = {"configurable": {"thread_id": bundle.bundle_id.value, "checkpoint_ns": ""}}
            tuples = [item async for item in saver.alist(config)]

        suspension: _Suspension | None = None
        prev_values: dict[str, Any] | None = None
        prev_trace: tuple[str, ...] = ()
        for checkpoint_tuple in reversed(tuples):  # oldest first
            values = self._decode_channel_values(saver, checkpoint_tuple.checkpoint)
            raw_trace = values.get("execution_trace") or ()
            trace = tuple(str(item) for item in raw_trace)
            if not trace:
                continue  # input checkpoints commit no boundary
            if len(trace) <= len(prev_trace):
                continue
            for node in trace[len(prev_trace) :]:
                changed = tuple(
                    key for key, value in values.items() if prev_values is not None and prev_values.get(key) != value
                )
                commits.append(
                    _Commit(
                        checkpoint_id=str(checkpoint_tuple.config["configurable"]["checkpoint_id"]),
                        node=node,
                        changed=changed,
                        route=str(values["route"]) if values.get("route") else None,
                        generation=(values["generation"] if isinstance(values.get("generation"), int) else None),
                        terminal=(str(values["terminal_status"]) if values.get("terminal_status") else None),
                    )
                )
            prev_values = values
            prev_trace = trace
        if tuples and (tuples[0].metadata or {}).get("source") is not None:
            newest_values = self._decode_channel_values(saver, tuples[0].checkpoint)
            if newest_values.get("route") == "needs_input":
                checkpoint_id = str(tuples[0].config["configurable"]["checkpoint_id"])
                suspension = _Suspension(checkpoint_id=checkpoint_id)

        store = RunObservationStore(
            bundle_root=self._lifecycle.private_root(bundle),
            bundle_id=bundle.bundle_id.value,
        )
        inspection = await store.inspect(bundle_id=bundle.bundle_id.value)
        return commits, suspension, inspection

    @staticmethod
    def _decode_channel_values(saver: Any, checkpoint: Any) -> dict[str, Any]:
        """Return the checkpoint's channel values, decoding serde-typed entries."""

        raw = (checkpoint or {}).get("channel_values") or {}
        values: dict[str, Any] = {}
        for channel, value in raw.items():
            if isinstance(value, tuple) and len(value) == 2 and isinstance(value[1], (bytes, bytearray)):
                try:
                    values[channel] = saver.serde.loads_typed(value)
                except Exception:  # noqa: S110 — undecodable channels are simply absent
                    continue
            else:
                values[channel] = value
        return values

    def _build_page(
        self,
        bundle_id: str,
        commits: list[_Commit],
        suspension: _Suspension | None,
        inspection: RunObservationInspection,
        *,
        live: bool,
        after_frame_sequence: int,
        page_size: int | None,
    ) -> TracePage:
        events = inspection.events if inspection.inspectability is ObservationInspectability.AVAILABLE else ()
        journal_readable = inspection.inspectability is ObservationInspectability.AVAILABLE
        finalized: list[Any] = [
            event
            for event in events
            if event.category is RunEventCategory.NODE
            and event.outcome in _FINAL_NODE_OUTCOMES
            and event.attempt_id is not None
        ]
        gap_reason: str | None = None
        quality = "complete"
        if not journal_readable:
            quality = "unavailable"
            gap_reason = f"journal_{inspection.inspectability.value}"
        elif inspection.journal_availability is not JournalAvailability.COMPLETE:
            quality = "degraded"
            gap_reason = "journal_evicted_or_damaged"

        frames: list[TraceFrame] = []
        consumed: set[int] = set()
        sequence = 0
        for commit in commits:
            sequence += 1
            match = next(
                (
                    event
                    for event in finalized
                    if id(event) not in consumed and event.phase == commit.node and event.outcome != "suspended"
                ),
                None,
            )
            if match is not None:
                consumed.add(id(match))
            frames.append(
                TraceFrame(
                    bundle_id=bundle_id,
                    frame_sequence=sequence,
                    checkpoint_id=commit.checkpoint_id,
                    visit_id=match.attempt_id if match else None,
                    generation=commit.generation,
                    node=commit.node,
                    outcome="completed",
                    route=commit.route,
                    changed_field_names=commit.changed,
                    duration_ms=match.duration_ms if match else None,
                    pending_input=None,
                    terminal_disposition=commit.terminal,
                    observation_quality=quality,  # type: ignore[arg-type]
                    gap_reason=gap_reason,
                )
            )

        if suspension is not None:
            suspended_event = next(
                (event for event in finalized if id(event) not in consumed and event.outcome == "suspended"),
                None,
            )
            if suspended_event is not None:
                consumed.add(id(suspended_event))
                sequence += 1
                frames.append(
                    TraceFrame(
                        bundle_id=bundle_id,
                        frame_sequence=sequence,
                        checkpoint_id=suspension.checkpoint_id,
                        visit_id=suspended_event.attempt_id,
                        node=suspended_event.phase,
                        outcome="suspended",
                        duration_ms=suspended_event.duration_ms,
                        pending_input=suspended_event.phase,
                        observation_quality=quality,  # type: ignore[arg-type]
                        gap_reason=gap_reason,
                    )
                )

        active: ActiveVisitProjection | None = None
        leftovers = [event for event in finalized if id(event) not in consumed]
        for event in leftovers:
            if event.outcome == "failed":
                sequence += 1
                frames.append(
                    TraceFrame(
                        bundle_id=bundle_id,
                        frame_sequence=sequence,
                        failure_event_sequence=event.sequence,
                        visit_id=event.attempt_id,
                        node=event.phase,
                        outcome="failed",
                        failure_category=event.failure_category,
                        observation_quality=quality,  # type: ignore[arg-type]
                        gap_reason=gap_reason,
                    )
                )
            elif active is None:
                active = ActiveVisitProjection(state="committing", node=event.phase, visit_id=event.attempt_id)
        unmatched_started = [
            event
            for event in events
            if event.category is RunEventCategory.NODE
            and event.outcome == "started"
            and event.attempt_id is not None
            and not any(frame.visit_id == event.attempt_id for frame in frames)
        ]
        if unmatched_started and active is None:
            state = "running" if live and journal_readable else "uncertain"
            active = ActiveVisitProjection(
                state=state,  # type: ignore[arg-type]
                node=unmatched_started[-1].phase,
                visit_id=unmatched_started[-1].attempt_id,
            )

        visible = [frame for frame in frames if frame.frame_sequence > after_frame_sequence]
        if page_size is not None and len(visible) > page_size:
            visible = visible[:page_size]
        last_sequence = visible[-1].frame_sequence if visible else after_frame_sequence
        next_cursor = _encode_cursor({"bundle_id": bundle_id, "frame_sequence": last_sequence, "journal": len(events)})

        return TracePage(
            bundle_id=bundle_id,
            frames=tuple(visible),
            active_visit=active,
            next_cursor=next_cursor,
            observation_quality=quality,  # type: ignore[arg-type]
            gap_reason=gap_reason,
        )
