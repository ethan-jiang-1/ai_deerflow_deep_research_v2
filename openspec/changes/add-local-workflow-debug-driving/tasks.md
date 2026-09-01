## 1. Baseline

- [ ] 1.1 Run `python3 openspec/governance/check_project_gate.py --phase plan --change add-local-workflow-debug-driving` and verify exit 0 after registering LDD-001..005.

## 2. Contracts

- [ ] 2.1 Register LDD-001..005 in the requirement registry (no other ID churn).
- [ ] 2.2 Add domain contracts: closed `DebugCommand` set, `DebugSessionSnapshot`,
  `BoundaryCursor`, typed denial/update models with command id/cursor fields.

## 3. Driver, Lease, Execution

- [ ] 3.1 Implement the Bundle-local expiring control lease: owner/generation/
  TTL/heartbeat/stale detection, atomic CAS takeover gated on (stale AND no live
  execution exclusion), generation fencing of old owners.
- [ ] 3.2 Implement `DebugRunDriver`: `open_start`/`open_attach`/`execute` over
  the existing executor; per-invocation `interrupt_after` with execution
  exclusion renewed through commit; `advance_one` single-boundary commit;
  `drive_until` stop policy (breakpoint/HITL/failure/terminal/pause);
  `pause_request`; `answer` via existing correlation; `cancel` via lifecycle;
  `detach` at committed boundary; command ledger for duplicate/stale handling.
- [ ] 3.3 Fix start compositions (Step = open + one bootstrap advance; Run =
  open + drive_until) with idempotent retries, and add the topology guard.

## 4. Falsifiable Matrix

- [ ] 4.1 Headless fixtures: start admission (exact handle first; Step commits
  bootstrap once), fixture step-through ≥9 boundaries, HITL suspended segment +
  typed answer, mode switches, post-node breakpoint, pause honesty.
- [ ] 4.2 Concurrency/recovery fixtures: natural-resume fencing; second
  debugger busy; stale-lease + no-exclusion CAS takeover; long node outliving
  TTL; boundary crash restart via CAS without advancing; mid-node crash
  uncertainty; double-click duplicate/stale; detach semantics (in-flight busy,
  boundary success, no cancel fact); two-process single-writer proof.

## 5. Closeout

- [ ] 5.1 Scope proof (`git diff --name-only`, submodule untouched) and
  `UV_OFFLINE=1 make verify` exit 0.
- [ ] 5.2 `openspec validate --strict`, doc hygiene, closeout gate; sync new
  main spec; archive; update plan ladder/§L.
