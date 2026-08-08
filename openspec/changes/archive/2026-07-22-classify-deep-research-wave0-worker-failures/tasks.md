## 0. Scope And Feedback Loop

- [x] 0.1 Record BUG-005 evidence and the controller-boundary/non-root-cause statement in this change; add a focused deterministic red-capable test matrix for bridge invocation, Wave0 parse/repair, submission validation, and exhaustion aggregation.

## 1. Closed Failure Contract

> Progress 2026-07-23: red-green coverage now proves per-attempt categories, typed
> submission conversion, persisted mixed aggregation, event schema compatibility, and
> no-ledger validation failure behavior (61 focused tests passing). Gate terminal
> projection and legacy diagnosis coverage remain before the implementation tasks close.

- [x] 1.1 Write red domain/component tests for exact per-attempt categories, separate `mixed` aggregate, invalid/free-form rejection, legacy absent-category reads, historical retry aggregation, retry/gate non-interference, and no raw diagnostic content crossing terminal projections (WFC-001, WOU-010, RUS-005).
- [x] 1.2 Add the smallest frozen controller-owned per-attempt/aggregate contracts, `SubmissionValidationFailure` carrying only ordered closed validation codes, and a pure helper over checkpointed `AttemptRef` history; add a distinct event field (not `validation_code`) and map the specified safe node-agent `RunFailureCode` table without accepting raw exceptions, worker data, or model/tool output (WFC-001, WOU-010, RUS-005).

## 2. Wave0 And Retained Diagnosis

- [x] 2.1 Update the real Wave0 worker adapter to classify non-successful node-agent responses and parser/repair failures; preserve typed submission validation at its lower seam, then have the shared component convert only that typed rejection to its existing terminal/retry path. Keep infrastructure/storage/ledger failures unchanged (WFC-001, WAN-006).
- [x] 2.2 Carry the closed per-attempt class through the distinct attempt-event field and checkpoint history, then have the Wave0 exhausted gate purely derive the aggregate into a separate terminal-incident diagnosis field; project it through safe run updates, summary/inspect/workbench, and honest `mixed` aggregation without changing retry, gate, ledger, checkpoint, or lifecycle authority (GAK-007, RUS-005, RER-008, WOU-010).
- [x] 2.3 Add deterministic lowest-seam and Wave0 exhaustion regressions for each class, same-class aggregation, mixed aggregation, legacy observations, and redaction; register requirement evidence.

## 3. Documentation And Verification

- [x] 3.1 Update BUG-005, the active observability postmortem plan, relevant `agent/AGENTS.md`/README guidance if public diagnosis output changes, the requirement registry (including WFC-001 and WAN-006), and test-evidence metadata; keep the original provider/tool root cause explicitly unknown.
- [x] 3.2 Run focused red-green tests, `cd agent && make format`, lint, test-assets, requirement coverage, `UV_OFFLINE=1 make verify`, strict OpenSpec validation, and `git diff HEAD --check`; confirm no `backend/` or `frontend/` paths changed.
