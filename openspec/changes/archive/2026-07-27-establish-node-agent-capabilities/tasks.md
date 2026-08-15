## 1. Entry Gate

- [x] 1.1 Confirm the archived `define-node-agent-workflow-governance` and
  `make-node-prompts-auditable` contracts remain the accepted baseline and that no
  active competing delta changes the required catalog/runtime surface. Record the
  protected-path and worktree baseline before modifying the cohort.
  - Verified 2026-07-28: both predecessor changes are archived and their main-spec
    contracts are accepted; no competing active delta exists; `backend/` and
    `frontend/` are clean, while this change and its backlog tracking plan are the
    only modified surfaces.
- [x] 1.2 Run `cd agent && UV_OFFLINE=1 make verify` before modifying the cohort;
  stop and resolve or separately authorize any remaining lifecycle-compatibility
  failure rather than treating focused capability checks as a substitute.
  - Verified 2026-07-28: the full offline deterministic gate passed (1857 fast,
    153 integration with 4 expected Gateway-stack skips, and 16 workflow tests).

## 2. Capability Kernel

- [x] 2.1 Add red deterministic tests for `NodeAgentCapabilityRef`, bounded local
  package/resource identity, the exclusive `legacy`-without-ref versus
  `required`-with-one-ref binding invariant, the stripped bounded version-1 JSON
  metadata header (including unknown-field rejection) and body-size limits, both
  closed tool postures, the exact six-case cohort and ten-case legacy inventory,
  invalid binding rejection before node invocation, missing/mismatched resource
  typed non-success before model-visible work, and absence of a generic/default
  capability. (`NAC-001`, `NAC-003`)
- [x] 2.2 Add the frozen domain reference plus agents-owned validated resource loader
  and typed capability projection; validate the package-local metadata/body split and
  the binding/ref invariant; preserve graph ownership of declarations; and keep
  parser/evaluator/materializer, recovery, catalog, and evidence metadata out of
  `NodeExecutionRequest`. (`NAC-001`)
- [x] 2.3 Add red deterministic renderer tests for ordered base-policy, local
  capability-policy, trusted assignment/output, and delimited untrusted-data layers;
  reject arbitrary full-system-prompt replacement without resolving runtime facts.
  (`NAC-002`)
- [x] 2.4 Implement the shared renderer composition and migrate its bridge seam to
  consume the typed capability projection without duplicating prompt text. (`NAC-002`)
- [x] 2.5 Add recording-bridge red tests for capability/request/`ExecutionPolicy`
  posture agreement, the configured-tool intersection, no permitted Wave0
  alternative, and forbidden-tool visibility; then enforce those checks before
  `build_node_agent` or dispatch. (`NOA-011`)

## 3. First Vertical Cohort

- [x] 3.1 Add the `hitl1-semantic-intake` and `hitl1-semantic-intake-repair`
  declarations/resources; migrate `hitl1/semantic-intake` and its repair case; and
  prove scripted real-node success plus malformed-candidate repair/exhaustion without
  granting lifecycle authority. (`NAC-003`)
  - Verified 2026-07-28: real HITL1 success, malformed-output repair, and repair
    exhaustion paths assert their exact capability refs and retain node-owned outcomes.
- [x] 3.2 Add distinct `wave0-authoritative-source-intake` and
  `wave0-source-intake-repair` declarations/resources; migrate `wave0/worker` and
  `wave0/repair`; and prove one permitted retrieval alternative binds for the normal
  case while repair has no model-visible tool, with typed artifact/ledger admission
  and existing failure behavior through the real worker seam. (`NAC-003`, `NOA-011`)
  - Verified 2026-07-28: real-worker success, repair, and malformed-repair tests
    capture both refs, typed artifact/ledger admission, and the zero-tool repair bound.
- [x] 3.3 Add `wave2-evidence-synthesis` and
  `wave2-evidence-synthesis-repair` declarations/resources; migrate both Wave2
  catalog cases; set the normal request to `tools_enabled=false`; bind
  `wave2_synthesis` to a dedicated zero-tool runtime policy rather than the HITL1
  bridge; and prove accepted-evidence-only synthesis plus malformed-output
  repair/terminal behavior through the real node seam. (`NAC-003`, `NOA-011`)
  - Verified 2026-07-28: real synthesis and repair/terminal tests assert both refs
    and zero-tool requests; a direct runtime test proves dedicated policy injection.
- [x] 3.4 Add source-backed inventory tests that enumerate the six migrated direct
  catalog cases and the named ten-case legacy set, including every case's exact
  package identity and resource filename. Fail on a missing/misplaced reference or
  resource, a legacy request carrying a ref, unapproved migration, inferred
  capability, or posture that differs from the builder/request window. (`NAC-003`)
  - Verified 2026-07-28: inventory locks six case IDs, capability IDs, packages,
    resource names, postures, request windows, and the closed ten-case legacy set.

## 4. Review And Evidence Surfaces

- [x] 4.1 Extend the accepted prompt catalog so every migrated case displays its
  capability ID, local source path, ordered four-layer projection, and
  requested-versus-runtime tool posture without becoming runtime authority.
  (`NAC-002`, `NAC-003`)
- [x] 4.2 Add the test-owned six-row branch-by-behavior-by-authenticity matrix and
  checker coverage for a missing/duplicate/unknown case, missing or identical
  success/high-risk claim IDs, uncollected claims, wrong-branch claims, and
  aggregate-substitute evidence. (`NAC-004`, `EVH-012`)
  - Verified 2026-07-28: each row records catalog/declaration/entrypoint sources,
    real-node authenticity, and independent collected success/risk claims; negative
    fixtures reject the listed omissions and substitutions.
- [x] 4.3 Register the domain and agents capability contracts, permit the
  `capabilities.py`/`capabilities/` node-package grammar, and require the exact HITL1,
  Wave0, and Wave2 capability locations in the structure registry; add architecture
  fixtures for local placement, escaping paths, and forbidden reverse/upstream
  placement. (`PRS-012`)
- [x] 4.4 Add the `NAC` requirement prefix and register `NAC-001` through `NAC-004`,
  `NOA-011`, `PRS-012`, and `EVH-012`; align requirement impacts, test selectors, and
  production `@impl` annotations with the owning deltas. (`NAC-001`, `NAC-002`,
  `NAC-003`, `NAC-004`, `NOA-011`, `PRS-012`, `EVH-012`)
  - Verified 2026-07-28: registry, claims, requirement impacts, and collected
    deterministic `@impl` annotations resolve all seven IDs.

## 5. Verification And Handoff

- [x] 5.1 Run the narrow declaration/resource, renderer, bridge posture, migrated
  HITL1/Wave0/Wave2 (including the Wave2 policy injection), catalog, evidence-matrix,
  architecture, and requirement-governance tests while completing the preceding tasks;
  fix only cohort-local conformance gaps.
  - Verified 2026-07-28: 187 focused tests passed, followed by `make test-assets`
    (175 central claims and 2065 deterministic tests).
- [x] 5.2 Run `cd agent && UV_OFFLINE=1 make verify`,
  `openspec validate establish-node-agent-capabilities --strict`, and
  `git diff HEAD --check`; record `git status --porcelain=v1 --untracked-files=all`
  and confirm `backend/` and `frontend/` remain clean before marking the cohort
  accepted.
  - Verified 2026-07-28: full offline verification passed (1889 fast, 160
    integration, 16 workflow; asset catalog 175 central claims / 2065 deterministic
    tests), strict OpenSpec validation and `git diff HEAD --check` passed, and
    `backend/` plus `frontend/` are clean. The recorded worktree contains only this
    change, its generated prompt artifacts, and the tracked remediation plan.
