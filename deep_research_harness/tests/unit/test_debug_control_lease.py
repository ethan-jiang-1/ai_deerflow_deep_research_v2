"""Control lease + command ledger smoke contracts.

@impl LDD-002
"""

from __future__ import annotations

from pathlib import Path

from deerflow_deep_research.runtime.debug_driving import (
    ControlLease,
    DebugCommandLedger,
)


def test_lease_acquire_heartbeat_release_and_stale(tmp_path: Path) -> None:
    clock = {"now": 1000.0}
    lease = ControlLease(private_root=tmp_path, clock=lambda: clock["now"], ttl=60.0)

    posture = lease.acquire("owner-1")
    assert posture.live and posture.owner == "owner-1" and posture.generation == 1

    clock["now"] += 30
    assert lease.heartbeat("owner-1") is True
    assert lease.snapshot().expires_in_seconds == 60.0

    lease.release("owner-1")
    assert lease.snapshot().live is False


def test_lease_cas_takeover_gates_on_stale_and_generation(tmp_path: Path) -> None:
    clock = {"now": 1000.0}
    lease = ControlLease(private_root=tmp_path, clock=lambda: clock["now"], ttl=60.0)
    lease.acquire("owner-1")

    # Live lease: never takeover, even with the right generation.
    assert lease.cas_takeover("owner-2", expected_generation=1) is None

    # TTL expiry alone is not enough while the generation view is stale.
    clock["now"] += 120
    assert lease.cas_takeover("owner-2", expected_generation=0) is None

    # Correct stale generation: CAS takeover succeeds and fences the old owner.
    posture = lease.cas_takeover("owner-2", expected_generation=1)
    assert posture is not None and posture.owner == "owner-2" and posture.generation == 2
    assert lease.check_write_allowed("owner-1") is False
    assert lease.check_write_allowed("owner-2") is True


def test_command_ledger_is_at_most_once_within_capacity(tmp_path: Path) -> None:
    ledger = DebugCommandLedger(tmp_path / "commands.json", capacity=4)
    for index in range(6):
        ledger.mark(f"cmd-{index}")
    assert ledger.seen("cmd-5") is True
    assert ledger.seen("cmd-0") is False  # evicted oldest
