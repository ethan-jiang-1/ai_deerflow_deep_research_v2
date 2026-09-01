## 1. Baseline And Evidence

- [x] 1.1 Re-verify the C3 dated facts on this tree (openspec empty; 256 bound;
  spike at `scripts/experiments/tui_trace.py`; visit-id reuse; in-memory
  counters; bridge seam between render and `ainvoke`) and record in `evidence.md`.
- [x] 1.2 Run `python3 openspec/governance/check_project_gate.py --phase plan --change add-local-workflow-debug-observation` from the repository root and verify exit 0 after registering LDO-001..008.

## 2. Trace Contract And Projector

- [ ] 2.1 Add domain contract models (`TraceFrame`, `TracePage`,
  `ActiveVisitProjection`, `TraceReadCursor`, quality/gap enums) with the closed
  field set, versioning, and fail-closed unknown-version behavior.
- [ ] 2.2 Implement `RunTraceProjector` over verified Bundle refs: checkpoint
  boundary cursor, journal causal facts, frame identity rules, quality/degraded
  detection, pagination, and opaque cursor resume; no graph launch or scan.
- [ ] 2.3 Emit wrapper-measured monotonic `duration_ms` per invocation segment
  on finalized outcome events (including the `GraphInterrupt` path), and raise
  finalized-node eviction priority above plain start/model-tool success within
  the existing bound, disclosing drops via manifest/TracePage.

## 3. Node Context Capture, Store, And Inspectors

- [ ] 3.1 Define `NodeContextSnapshot` contract plus page/view/source-view and
  denial models with provenance labels and the fixed coverage projection.
- [ ] 3.2 Implement the write-only recorder protocol, Bundle-private bounded
  snapshot store (containment, atomic publication, idempotency/conflict,
  capacity, durable segment→invocations collection index), and wire the
  composition-injected recorder into the bridge capture seam after rendering and
  admission, before `agent.ainvoke`/first provider call, failing closed with
  typed reasons.
- [ ] 3.3 Persist bounded per-invocation model/tool activity facts (counts,
  budget stop, safe outcomes) from the existing middleware counters, distinct
  from context counts, on finalized outcomes.
- [ ] 3.4 Implement the context inspector and curated source reader with
  MATCH/DRIFT/CURRENT_SOURCE_UNAVAILABLE/CONTEXT_NOT_CAPTURED semantics and
  NOT_RETAINED presentation for raw provider histories.

## 4. Operator Workspace Reader

- [ ] 4.1 Implement `OperatorWorkspaceReader` (composition-injected trusted
  roots/policy; relative paths and verified refs only; typed pages/previews/
  denials; mount/root enumeration with MODEL_READ/MODEL_WRITE/OPERATOR_ONLY/
  RESTRICTED labels; CURRENT vs CAPTURED time semantics; hash verification).
- [ ] 4.2 Retire `scripts/experiments/tui_trace.py` in favor of formal interface
  tests (delete the file and its experiment references).

## 5. Fixtures And Acceptance

- [ ] 5.1 Projector fixtures: replay/live isomorphism on a Journal-complete
  Bundle; HITL multi-segment preservation; pre-commit completed → failed frame;
  uncertain active projection; degradation (missing/malformed/evicted);
  capacity eviction disclosure; two-Bundle isolation; privacy sentinels absent
  from default pages.
- [ ] 5.2 Context fixtures: renderer/bridge/provider-spy proof of
  capture-before-first-provider-call; capture-failure → zero provider calls;
  multi-invocation/multi-provider-call distinction; source DRIFT; legacy
  CONTEXT_NOT_CAPTURED; capacity exhaustion; eviction-orphan impossibility.
- [ ] 5.3 Workspace fixtures: tree/command equivalence; escape/private/foreign
  denial without leakage; CURRENT/CAPTURED distinction; hash verification.
- [ ] 5.4 Timing fixture: artificial HITL pause does not change any segment
  `duration_ms`.
- [ ] 5.5 Run the focused seams then the full gate; record results in
  `evidence.md`.

## 6. Closeout And Scope Proof

- [ ] 6.1 Verify scope via `git diff --name-only` (no topology/route/public API
  change beyond declared surfaces; `deerflow/` untouched).
- [ ] 6.2 Run `UV_OFFLINE=1 make verify`; run `openspec validate
  add-local-workflow-debug-observation --strict`, doc hygiene, and the closeout
  gate; verify all exit 0.
- [ ] 6.3 Sync the new capability spec into `openspec/specs/`, archive the
  change, and update the progressive plan ladder and §L with real results.
