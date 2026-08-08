## 1. Binding Contracts And Private Store

- [x] 1.1 Add red-before-green domain/runtime tests for frozen binding references, trusted scope facts, provider fingerprints, durability classes, non-enumerated private-root behavior, bounded unavailable/denied outcomes, and sentinel redaction. (`RES-001`, `RES-004`)
- [x] 1.2 Implement pure binding contracts and typed fail-closed error/result projections under the canonical domain ownership boundary, with `@impl RES-001` through `RES-004` annotations and no runtime imports. (`RES-001`, `RES-002`, `RES-003`, `RES-004`)
- [x] 1.3 Implement owner-only no-follow private binding persistence below the non-enumerated local retained root with atomic create/refresh/invalidate, explicit lock ordering, no cross-user enumeration, and all filesystem work off the event loop. (`RES-001`, `RES-004`)

## 2. Checkpoint Reopen And Lifecycle Resolution

- [x] 2.1 Add red-before-green file-SQLite restart tests for binding creation, provider reopen, checkpoint identity/schema validation, suspended and terminal status projection, and same-process provider denial after restart. (`RES-002`, `RUI-004`)
- [x] 2.2 Implement the read-only runtime checkpoint verifier through the official async checkpointer context and current trusted AppConfig, rejecting provider drift, missing/corrupt binding, namespace mismatch, and invalid checkpoint without fallback probing or a public operation surface. (`RES-002`, `RUI-004`, `REG-004`)
- [x] 2.3 Add red-before-green lifecycle tests proving supplied research ids must equal the trusted canonical id, foreign ids open no checkpoint, and read-only verification neither consumes pending input nor invokes a graph node. (`RES-003`, `REG-004`, `RUI-006`)
- [x] 2.4 Integrate canonical-id rejection and the narrow read-only verifier without new public commands, a reconstructed thread/sandbox envelope, caller-supplied authority fields, sandbox initialization for checkpoint inspection, or manifest/trace control reads. (`RES-003`, `RUI-006`, `REG-014`)

## 3. Session Projection And Compatibility

- [x] 3.1 Add red-before-green manifest/inspection tests for the safe opaque binding reference, legacy inspection-only bundles, unavailable binding truth, and scans proving no user/thread/provider/path/checkpoint leakage. (`RUS-001`, `RES-001`, `RES-004`)
- [x] 3.2 Extend the runtime run-session projection/store so binding availability is observable but never a lifecycle controller; preserve manifest/trace inspection compatibility and refuse automatic legacy backfill. (`RUS-001`, `REG-014`)
- [x] 3.3 Add end-to-end scripted lifecycle evidence that binds a real checkpointed fake run, closes/reopens the provider through the private read-only verifier, and proves no node invocation or pending consumption occurs. (`RES-002`, `RES-003`, `REG-014`)

## 4. Structure, Documentation, And Evidence

- [x] 4.1 Register any new domain/runtime binding modules and tests in project-structure governance, render the generated `agent/AGENTS.md` block, and add dependency-direction checks. (`RES-001`, `RES-004`)
- [x] 4.2 Update `agent/README.md` and the run-bundle/session plan with exact durability, no-resume-until-operation-surface, binding-failure, and provider-restart semantics; do not document unimplemented discovery/workbench commands. (`RES-001`, `RES-002`, `RES-003`)
- [x] 4.3 Extend requirement/test-evidence coverage with redaction, scope-isolation, stale-binding, provider-drift, and SQLite restart selectors; record supplemental credentialed-provider acceptance as non-blocking. (`RES-001`, `RES-002`, `RES-003`, `RES-004`)

## 5. Verification

- [x] 5.1 Run focused domain/runtime/lifecycle restart tests, then from repository root run `cd agent && UV_OFFLINE=1 make verify`; record baseline/final protected-path status and confirm `backend/` and `frontend/` remain untouched.
- [x] 5.2 Run `openspec validate establish-deep-research-session-lifecycle-binding --strict`, applicable requirement/architecture checks, binding provider-drift smoke cases, and `git diff HEAD --check` from repository root.
- [x] 5.3 When an approved real durable provider is configured, run a bounded start-to-HITL and process-reopen verifier acceptance without recording secrets or raw checkpoint data; otherwise record a safe preflight skip that does not block deterministic completion. (`RES-002`, `RES-003`)
