## Pre-Apply Polish Log

- 2026-07-21, round 1: reconciled the proposal with the current runtime boundary. Discovery
  now requires a private owner index; historical operations resolve an envelope from
  validated scope-addressed DeerFlow facilities rather than a nonexistent historical
  `ToolRuntime`; reopened resume has checkpoint-derived prompt/response correlation and
  handler-lock revalidation.
- 2026-07-21, round 2: added the missing lifecycle safety constraints. A profile-owned
  recipe fingerprint now prevents fake/real recipe drift, the existing retained-root
  dispatch lock serializes local mutations across processes, and cleanup revokes an
  operation binding/index before deleting its bundle. Round 3 will review artifact
  coherence, migrations, and test coverage before declaring Apply-ready.
- 2026-07-21, round 3: made private publication and retention failure-safe. Binding
  metadata is staged before retained-bundle publication and indexed only afterwards;
  discovery is isolated by owner plus profile, and a failed cleanup deletion downgrades
  the remaining bundle to inspection-only. Round 4 will perform final coherence and
  implementation-seam review.
- 2026-07-21, round 4: resolved the legacy command-contract conflict. `demo-sessions`
  retains `list`/`inspect`/`cleanup`, while profile-mediated operations have explicit
  command shapes; resume takes its answer from stdin and validates an opaque request id.
  The next pass is a final validation/readiness audit.
- 2026-07-21, round 5: bounded the last persistence and liveness edges. Owner/profile
  indexes cap at retained-session capacity and safely reap only unreferenced staged
  metadata; shared local mutation locking has a 30-second bounded acquisition path.
- 2026-07-21, round 6: final cross-artifact audit passed. The proposal, design, seven
  delta specs, task ordering, legacy-command compatibility, runtime/profile factory
  boundary, and governance checks are coherent. The change is **Apply-ready**; no
  implementation task has been marked complete.

## Current Implementation Checkpoint

> Updated: 2026-07-21
>
> Completed in this session: 1.1-1.4. Focused domain/runtime evidence now
> covers frozen projections, redaction, private discovery, recipe mismatch,
> bounded index capacity, staged-record reconciliation, bundle-first activation,
> and no-sandbox historical read resolution (60 tests green).
>
> Completed in this session: 2.1-2.7. The operation-enabled file-SQLite profile
> now has fresh-process restart and contention evidence; the broker, lifecycle
> dispatch, bounded retained-root lease, retention revocation, and staged-index
> reconciliation all have focused fail-closed coverage (77 tests green).
>
> Completed in this session: 3.1-3.3. `demo-sessions` preserves its legacy
> observation commands and now routes fixed-profile discovery/open/status/
> resume/cancel through an injected broker; the fake TUI consumes the same safe
> projection and does not create a second lifecycle controller (20 CLI/TUI/
> lifecycle tests green).
>
> Completed in this session: 4.1-4.2. The structure registry and generated guide
> now enumerate the new operation modules and focused tests; test-evidence claims,
> README limits, and the session/workbench roadmap are synchronized.
>
> Active vertical slice: tasks 4.3-4.4. Next, run the complete deterministic,
> OpenSpec, requirement/spec/architecture, drift-smoke, and diff checks.
>
> 2026-07-22 verification continuation: the full gate exposed a pre-existing
> canonical-id fixture mismatch in `test_work_unit_control.py`; the identical
> failure reproduces at `HEAD`. The fixture now derives the canonical id for
> its fixed `alice/thread-1` envelope, preserving the production mismatch
> denial. The focused file is green (17 passed); complete deterministic and
> governance verification is in progress. `backend/` and `frontend/` were
> clean at the protected-path baseline and remain outside this change.
>
> 2026-07-22 task 4.3 complete: the current focused session/CLI/TUI/runtime
> suite passed (129 tests), and `UV_OFFLINE=1 make verify` passed: fast 1594
> passed (2 deselected), integration/blocking-I/O 118 passed (4 existing
> Gateway-stack skips, 14 deselected), and workflow 15 passed (1726
> deselected). Protected-path final status remains clean for `backend/` and
> `frontend/`.
>
> 2026-07-22 task 4.4 complete: strict OpenSpec validation passed; project
> requirement, spec, and architecture checks passed; focused provider- and
> recipe-drift smoke evidence passed (2 tests); and `git diff HEAD --check`
> passed with protected paths still clean. Credentialed live preflight passed
> for the configured model and web providers. Live canaries remain supplemental
> external acceptance evidence and were not run as part of this deterministic
> change gate.

## 1. Contracts And Trusted Resolution

- [x] 1.1 Add red-before-green domain/runtime tests for frozen discovery/operation projections, indistinguishable denial, bounded owner-index entries, recipe-fingerprint mismatch, artifact refs, authorized pending-input views, and sentinel redaction. (`RDO-001`, `RDO-004`, `RES-001`)
- [x] 1.2 Implement pure `domain/session_operations.py` projections and operation inputs with `@impl RDO-001` through `RDO-004`, retaining no raw scope, provider, path, checkpoint, recipe, or answer fields; permit only the validated bounded pending-input display projection. (`RDO-001`, `RDO-004`)
- [x] 1.3 Version the private binding for staged owner/profile-index activation, bounded index capacity/staged-record reconciliation, and a profile-owned recipe-compatibility fingerprint; activate only after bundle publication, preserve phase-2 records as inspection/read-only-verifier-only, and never backfill them. (`RES-001`, `RES-004`, `RUS-001`)
- [x] 1.4 Implement and test a runtime-owned historical resolver from trusted operation access plus verified binding. Runtime access uses public path/sandbox facilities; local-profile access uses only its fixed owned path/sandbox factories. It MUST NOT synthesize a historical `ToolRuntime`, open a provider before recipe verification, or construct a sandbox for read-only work. (`RDO-002`, `RUI-002`, `RUI-006`)

## 2. Broker And Lifecycle Operations

- [x] 2.1 Add red-before-green file-SQLite subprocess restart evidence through the operation-enabled local profile, plus owner-index scope-isolation, provider/recipe drift, corrupt-binding, and read-only no-sandbox/no-node tests. (`RDO-001`, `RDO-002`, `RDO-004`, `RES-002`)
- [x] 2.2 Implement the authorized `runtime/session_operations.py` broker using the phase-2 binding/verifier and official current provider; discover only private-index entries and keep open/status bounded and read-only. (`RDO-001`, `RDO-004`, `RUS-003`)
- [x] 2.3 Route authorized resume/cancel only through current lifecycle handlers and the trusted resolver. Resume MUST derive a bounded prompt and internal response from the current interrupt, compare an expected request id, preserve duplicate-response idempotency, and revalidate under the handler namespace lock before mutation. (`RDO-003`, `REG-004`, `REG-014`)
- [x] 2.4 Route local broker resume/cancel through the established retained-root dispatch lease shared with normal local lifecycle dispatch, with a bounded <=30-second acquisition; prove two fresh processes cannot consume one pending interrupt, contention fails before provider/sandbox/graph work, and no lock is held by list/open/status. (`RDO-003`, `RUS-001`, `RES-004`)
- [x] 2.5 Reconcile retention with bindings: revoke the validated matching binding and owner-index entry before deleting an eligible unlocked bundle; prove revocation failure safely skips deletion, a deletion failure downgrades the retained manifest to inspection-only, and generic checkpoint rows remain untouched. (`RUS-001`, `RUS-003`, `RES-004`)
- [x] 2.6 Prove partial publication never activates discovery before a retained bundle exists, the owner/profile index stays at capacity, only unreferenced staged records are reaped, and a profile cannot enumerate another profile's entries even under one local principal. (`RDO-001`, `RDO-004`, `RES-001`)
- [x] 2.7 Prove foreign/unknown references, unavailable historical context, same-process providers, legacy phase-2 bindings, and recipe mismatch cannot select a namespace, initialize an unnecessary sandbox, or reveal session existence. (`RDO-002`, `RDO-004`, `RUI-002`)

## 3. Local Adapters And Compatibility

- [x] 3.1 Add local CLI tests for injected-broker discovery/open/status/operation availability, authorized pending-input display, durable-profile restart truth, stdin-only resume answers, and separate legacy inspection-only sessions, including path/provider/content sentinel scans. (`REC-004`, `RUS-003`, `RDO-004`)
- [x] 3.2 Preserve `demo-sessions` legacy `list`/`inspect`/`cleanup` behavior and add only profile-mediated `discover`, `open`, `status`, `cancel`, and `resume --request-id` operations. Resume MUST read the answer from stdin, never argv/output/retained records; no Gateway schema, caller-selected authority/recipe, or production API command is introduced. (`REC-004`, `RDO-001`, `RDO-003`)
- [x] 3.3 Add TUI contract tests and adapt its controls to the same broker projection without a parallel lifecycle controller. (`RED-005`, `RDO-001`, `RDO-004`)

## 4. Governance, Documentation, And Verification

- [x] 4.1 Register `domain/session_operations.py`, `runtime/session_operations.py`, and new focused test paths in project structure, render `agent/AGENTS.md`, and add requirement/test-evidence coverage at the domain, runtime, lifecycle, and retention seams. (`RDO-001`, `RDO-002`, `RDO-003`, `RDO-004`, `RES-004`)
- [x] 4.2 Update `agent/README.md` and the session/workbench plan with implemented local-operation limits, durable-profile/recipe compatibility semantics, retention revocation, and the continued absence of Gateway/Web workbench operations.
- [x] 4.3 Run focused deterministic tests, then `cd agent && UV_OFFLINE=1 make verify`; record protected-path baseline/final status and confirm `backend/` and `frontend/` remain untouched.
- [x] 4.4 Run strict OpenSpec, requirement/spec/architecture checks, provider-drift and recipe-drift smoke evidence, and `git diff HEAD --check`; record credentialed-provider acceptance as supplemental or a safe preflight skip.
