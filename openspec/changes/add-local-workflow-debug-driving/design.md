## Context

C3 delivered the observation surface. Existing driving truth:
`BundleGraphExecutor` owns execution exclusion and natural resume (REG-023);
E4 proved one compiled graph accepts per-call `interrupt_after` across
bootstrap pause → HITL typed resume → run-to-terminal on the same
saver/thread; the lifecycle owns admission, suspension truth, and recovery;
there is no boundary-stepping surface and no ownership story for intentional
pauses (they look like orphans to natural resume).

## Goals / Non-Goals

**Goals:** headless `DebugRunDriver` with at-most-once boundary commands, a
fencing control lease, fixed start compositions, breakpoint/pause stop policy,
attach/detach/restart recovery, and a topology guard — all proven by the
deterministic fixture matrix. **Non-Goals:** Textual wiring (C4b), remote
driving, breakpoint persistence, State mutation, observation-schema changes.

## Decisions

### D1. Driver wraps the executor; it never replaces lifecycle

`DebugRunDriver(lifecycle, executor_factory, *, clock, lease_ttl,
heartbeat_interval)` composes the existing lifecycle admission + executor
execution with debug semantics. Open start/attach reuse lifecycle admission
and verification verbatim; the driver adds only boundary control. Contracts
(`DebugCommand`, `DebugSessionSnapshot`, `BoundaryCursor`, typed denials) live
in `domain/debug_driving.py`; the driver, lease, and command ledger live in
`runtime/debug_driving.py`.

### D2. Control lease is a Bundle-private expiring file fact with CAS

Lease record (owner id, generation, expires_at via injectable clock, cursor)
lives beside the Bundle state under lifecycle-private storage, written through
small lifecycle-adjacent primitives with atomic replace. Heartbeat renews
`expires_at`; `stale = now > expires_at`. Takeover = atomic compare-and-swap
on (generation, cursor) performed only when stale AND no live execution
exclusion (executor reports exclusion liveness). Old owners are fenced by
generation mismatch on every subsequent write. The lease never touches
ResearchState and never blocks observers.

### D3. At-most-once via command ledger + expected cursor

Each executed mutation appends `(command_id → outcome)` to a Bundle-local
ledger; duplicates return the recorded denial/result. `expected_cursor`
mismatch is a typed stale denial before any execution. `advance_one` compiles
the canonical recipe once per driver (cached), invokes with
`interrupt_after=[next_node]` under the executor's execution exclusion renewed
throughout the invocation, and stops at the first committed boundary.
`drive_until` loops `advance_one` internally until the stop policy matches.

### D4. Start composition and detach are driver-owned semantics

Start Step = `open_start` (bundle admission; exact handle out) then exactly one
`advance_one` keyed by a start command id — retries coalesce. Start Run =
`open_start` then `drive_until` with the default stop policy (HITL/failure/
terminal). Detach is legal only when no invocation is in flight; it releases
the lease and leaves durable truth untouched. Crash semantics: no fabricated
detach/cancel; the stale lease + checkpoint tell the recovery story.

### D5. Topology guard

The driver asserts `len(snapshot.next) <= 1` at each boundary and that each
superstep commits exactly the stepped node; violation → typed step contract
failure (no silent multi-node advance).

## Risks / Trade-offs

- **[Risk] Lease file adds a writer to Bundle-private storage.** → Atomic
  replace under the lifecycle's established private-root discipline; never
  touches State/checkpoint.
- **[Risk] Drive-until long loops starve the event loop.** → Loop awaits the
  executor's own async boundaries; no blocking I/O added.
- **[Risk] Command ledger growth.** → Bounded retention of the last N command
  records (duplicate detection window documented).

## Migration Plan

1. Red: matrix tests against the absent driver fail deterministically.
2. Domain contracts → lease → driver (advance, drive, pause, answer, cancel,
   detach) → recovery fixtures.
3. Green matrix + full gate; sync new main spec; archive; C4b unblocked.
