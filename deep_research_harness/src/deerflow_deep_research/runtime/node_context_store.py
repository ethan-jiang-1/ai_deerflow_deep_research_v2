"""Bundle-private node-context snapshot store and its write-only recorder.

The store owns containment, layout, atomic publication, idempotency/conflict,
bounds, and the durable segment→invocations collection index. The bridge only
sees the recorder protocol; it never receives roots, paths, or handles.
(`LDO-005`, `LDO-006`)
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from deerflow_deep_research.domain.node_context import (
    NodeContextActivityFacts,
    NodeContextCollectionPage,
    NodeContextSnapshot,
    NodeContextSummary,
    NodeContextView,
)

_SNAPSHOT_FILENAME = "snapshot.json"
_ACTIVITY_FILENAME = "activity.json"
_INDEX_FILENAME = "index.json"


class NodeContextError(Exception):
    """Typed store failure surfaced to the bridge before any provider call."""


class NodeContextCapacityError(NodeContextError):
    pass


class NodeContextConflictError(NodeContextError):
    pass


def _sha256(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    staged = path.with_name(path.name + ".staged")
    staged.write_text(json.dumps(payload, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    staged.replace(path)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


class NodeContextStore:
    """Bounded, Bundle-private, append-only snapshot collection."""

    def __init__(
        self,
        *,
        bundle_root: Path,
        bundle_id: str,
        max_contexts_per_bundle: int = 256,
        max_snapshot_bytes: int = 512_000,
    ) -> None:
        self._root = bundle_root / "diagnostics" / "node-context"
        self._bundle_id = bundle_id
        self._max_contexts = max_contexts_per_bundle
        self._max_snapshot_bytes = max_snapshot_bytes

    # -- write side (recorder protocol) ------------------------------------

    def record_sync(self, snapshot: NodeContextSnapshot) -> str:
        if len(json.dumps(snapshot.model_dump(mode="json"), ensure_ascii=False)) > self._max_snapshot_bytes:
            raise NodeContextCapacityError("context_capacity_exhausted")
        segments = self._index()
        key = f"{snapshot.attempt_id}/{snapshot.node_agent_ordinal:04d}"
        if key in segments:
            raise NodeContextConflictError("context_identity_conflict")
        if len(segments) >= self._max_contexts:
            raise NodeContextCapacityError("context_capacity_exhausted")
        directory = self._root / snapshot.attempt_id / f"{snapshot.node_agent_ordinal:04d}"
        _atomic_write_json(directory / _SNAPSHOT_FILENAME, snapshot.model_dump(mode="json"))
        segments[key] = snapshot.context_id
        _atomic_write_json(self._root / _INDEX_FILENAME, segments)
        return key

    def record_activity_sync(self, context_key: str, facts: NodeContextActivityFacts) -> None:
        directory = self._root / context_key
        if not (directory / _SNAPSHOT_FILENAME).is_file():
            raise NodeContextError("context_ref_unknown")
        _atomic_write_json(directory / _ACTIVITY_FILENAME, facts.model_dump(mode="json"))

    # -- read side (inspector) ----------------------------------------------

    def page(self, *, limit: int = 50) -> NodeContextCollectionPage:
        segments = self._index()
        summaries: list[NodeContextSummary] = []
        for key in sorted(segments):
            payload = _load_json(self._root / key / _SNAPSHOT_FILENAME)
            if payload is None:
                continue
            snapshot = NodeContextSnapshot.model_validate(payload)
            summaries.append(
                NodeContextSummary(
                    context_id=snapshot.context_id,
                    node=snapshot.node,
                    attempt_id=snapshot.attempt_id,
                    node_agent_ordinal=snapshot.node_agent_ordinal,
                    created_at=snapshot.created_at,
                    capture_quality=snapshot.capture_quality,
                )
            )
        return NodeContextCollectionPage(
            bundle_id=self._bundle_id, summaries=tuple(summaries[:limit]), total=len(summaries)
        )

    def read(self, context_key: str) -> NodeContextView | None:
        payload = _load_json(self._root / context_key / _SNAPSHOT_FILENAME)
        if payload is None:
            return None
        snapshot = NodeContextSnapshot.model_validate(payload)
        activity_payload = _load_json(self._root / context_key / _ACTIVITY_FILENAME)
        activity = NodeContextActivityFacts.model_validate(activity_payload) if activity_payload is not None else None
        return NodeContextView(
            snapshot=snapshot,
            provenance={
                "initial_system_policy": "MODEL_VISIBLE",
                "initial_human_message": "MODEL_VISIBLE",
                "base_policy_layer": "MODEL_VISIBLE",
                "capability_layer": "MODEL_VISIBLE",
                "request_objective": "MODEL_VISIBLE",
                "request_expected_output": "MODEL_VISIBLE",
                "tool_posture": "RUNTIME_ENFORCED",
                "budget": "RUNTIME_ENFORCED",
                "virtual_roots": "RUNTIME_ENFORCED",
                "mount_manifest": "RUNTIME_ENFORCED",
            },
            coverage_outcome="OBSERVED" if activity is not None else "UNAVAILABLE",
            activity=activity,
        )

    # -- internal ------------------------------------------------------------

    def _index(self) -> dict[str, str]:
        payload = _load_json(self._root / _INDEX_FILENAME)
        return payload if isinstance(payload, dict) else {}


class NodeContextRecorder:
    """Write-only façade handed to the bridge; bound to one exact Bundle."""

    def __init__(self, store: NodeContextStore) -> None:
        self._store = store

    async def record(self, snapshot: NodeContextSnapshot) -> str:
        return await asyncio.to_thread(self._store.record_sync, snapshot)

    async def record_activity(self, context_key: str, facts: NodeContextActivityFacts) -> None:
        await asyncio.to_thread(self._store.record_activity_sync, context_key, facts)


class NodeSourceReader:
    """Curated non-runtime source view: registry identity in, drift status out."""

    def __init__(self, *, store: NodeContextStore, current_loader: Any) -> None:
        self._store = store
        self._current_loader = current_loader

    def view(self, context_key: str) -> Any:
        from deerflow_deep_research.domain.node_context import NodeSourceView

        view = self._store.read(context_key)
        if view is None:
            return None
        captured = view.snapshot.capability_layer
        try:
            current = self._current_loader()
        except Exception:
            current = None
        if current is None or not getattr(current, "policy", ""):
            capability_status = "CURRENT_SOURCE_UNAVAILABLE"
        else:
            current_hash = _sha256(current.policy)
            capability_status = "MATCH" if current_hash == captured.sha256 else "DRIFT"
        current_text = getattr(current, "policy", "") if current is not None else ""
        return NodeSourceView(
            node=view.snapshot.node,
            base_policy_status=(
                "MATCH"
                if _sha256(view.snapshot.base_policy_layer.text) == view.snapshot.base_policy_layer.sha256
                else "DRIFT"
            ),
            capability_status=capability_status,  # type: ignore[arg-type]
            capability_identity=captured.identity,
            current_capability_text=current_text or captured.text,
        )
