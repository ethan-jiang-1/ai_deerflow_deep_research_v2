"""Headless debug driving: expiring control lease + at-most-once boundary commands.

The driver composes lifecycle admission and the existing executor; it never
becomes a second lifecycle authority and never fabricates durable facts.
(`LDD-001`..`LDD-005`)
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from deerflow_deep_research.domain.debug_driving import (
    LeasePosture,
)

LEASE_FILENAME = "debug-lease.json"


class ControlLease:
    """Bundle-local expiring lease with generation CAS and owner fencing."""

    def __init__(self, *, private_root: Path, clock: Callable[[], float] = time.time, ttl: float = 300.0) -> None:
        self._path = private_root / LEASE_FILENAME
        self._clock = clock
        self._ttl = ttl

    def _read(self) -> dict[str, Any] | None:
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else None
        except (OSError, ValueError):
            return None

    def _write(self, payload: dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        staged = self._path.with_name(self._path.name + ".staged")
        staged.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        staged.replace(self._path)

    def snapshot(self) -> LeasePosture:
        payload = self._read()
        if payload is None:
            return LeasePosture(owner=None, generation=0, live=False)
        live = float(payload["expires_at"]) > self._clock()
        expires_in = max(0.0, float(payload["expires_at"]) - self._clock())
        return LeasePosture(
            owner=payload["owner"],
            generation=int(payload["generation"]),
            live=live,
            expires_in_seconds=expires_in if live else None,
        )

    def acquire(self, owner: str) -> LeasePosture:
        payload = self._read()
        generation = int(payload["generation"]) if payload else 0
        if payload and float(payload["expires_at"]) > self._clock():
            return self.snapshot()
        self._write({"owner": owner, "generation": generation + 1, "expires_at": self._clock() + self._ttl})
        return self.snapshot()

    def heartbeat(self, owner: str) -> bool:
        payload = self._read()
        if payload is None or payload["owner"] != owner:
            return False
        payload["expires_at"] = self._clock() + self._ttl
        self._write(payload)
        return True

    def release(self, owner: str) -> None:
        payload = self._read()
        if payload and payload["owner"] == owner:
            self._write({**payload, "expires_at": 0.0, "released": True})

    def cas_takeover(self, owner: str, expected_generation: int) -> LeasePosture | None:
        payload = self._read()
        if payload is None:
            generation = 0
        else:
            if float(payload["expires_at"]) > self._clock():
                return None  # live lease: never takeover
            if int(payload["generation"]) != expected_generation:
                return None  # generation moved: stale view
            generation = int(payload["generation"])
        self._write({"owner": owner, "generation": generation + 1, "expires_at": self._clock() + self._ttl})
        return self.snapshot()

    def check_write_allowed(self, owner: str) -> bool:
        payload = self._read()
        if payload is None:
            return True
        return payload["owner"] == owner and float(payload["expires_at"]) > self._clock()


class DebugCommandLedger:
    """Bounded at-most-once ledger for command ids."""

    def __init__(self, path: Path, *, capacity: int = 256) -> None:
        self._path = path
        self._capacity = capacity

    def _load(self) -> dict[str, str]:
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {}
        except (OSError, ValueError):
            return {}

    def seen(self, command_id: str) -> bool:
        return command_id in self._load()

    def mark(self, command_id: str) -> None:
        ledger = self._load()
        ledger[command_id] = "done"
        if len(ledger) > self._capacity:
            for stale in sorted(ledger)[: len(ledger) - self._capacity]:
                ledger.pop(stale, None)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(ledger, sort_keys=True), encoding="utf-8")
