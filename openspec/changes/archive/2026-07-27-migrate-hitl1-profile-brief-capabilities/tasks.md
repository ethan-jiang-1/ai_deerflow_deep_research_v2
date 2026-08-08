## 1. Entry Gate

- [x] 1.1 Confirm `establish-node-agent-capabilities` has been spec-synced and
  archived, its full offline verification is recorded, and `backend/`/`frontend/`
  are clean before changing the second cohort.
- [x] 1.2 Run `cd agent && UV_OFFLINE=1 make verify` before modifying HITL1; record
  the deterministic baseline, then run `UV_OFFLINE=1 make prompt-dump-check` and
  record the current generated prompt-catalog state.

## 2. HITL1 Capability Migration

- [x] 2.1 Add red deterministic declaration/resource tests for
  `hitl1-profile-brief` and `hitl1-profile-brief-repair`: exact package/resource
  identity, bounded version-1 metadata, forbidden posture, and no capability metadata
  authority. (`NAC-005`)
- [x] 2.2 Add the two HITL1-local refs and Markdown policies; express conservative
  advisory profile construction separately from schema-only repair. (`NAC-005`)
- [x] 2.3 Add red builder and recording-bridge tests proving both requests are
  required, zero-tool, and rejected before model-visible work on a posture mismatch.
  (`NAC-005`, `NOA-011`)
- [x] 2.4 Migrate `build_brief_prompt` and its repair branch to the exact refs while
  preserving the existing assignment/output contract, parser, and bridge policy.
  (`NAC-005`)

## 3. Lifecycle And Review Evidence

- [x] 3.1 Add scripted real-HITL1-node proof that a valid brief yields an advisory
  proposal only, with no accepted profile, route, or checkpoint authority. (`NAC-005`,
  `EVH-013`)
- [x] 3.2 Add malformed-brief repair and exhausted-repair journeys proving one repair
  remains zero-tool and cannot publish partial profile or lifecycle authority.
  (`NAC-005`, `EVH-013`)
- [x] 3.3 Extend the catalog, exact migrated/legacy inventory, and generated
  `agent/node_prompts/` projection to the two brief cases; assert eight migrated and
  exactly eight legacy cases. Regenerate with `cd agent && UV_OFFLINE=1 make
  prompt-dump`, then require `UV_OFFLINE=1 make prompt-dump-check` to pass.
  (`NPC-003`, `NAC-005`)
- [x] 3.4 Extend the test-owned capability matrix with two HITL1 brief rows, distinct
  collected success/risk central claims, and negative fixtures for row or selector
  drift. (`EVH-013`)
- [x] 3.5 Register the two local resources and focused evidence paths in
  `project-structure.toml`; add architecture fixtures for exact local placement.
  (`PRS-013`)
- [x] 3.6 Register `NAC-005`, `NPC-003`, `EVH-013`, and `PRS-013`; align central
  claims, requirement impacts, and collected `@impl` annotations. (`NAC-005`,
  `NPC-003`, `EVH-013`, `PRS-013`)

## 4. Verification And Handoff

- [x] 4.1 Run the new or amended focused capability loader/renderer/bridge and HITL1
  lifecycle test selectors, then require `cd agent && UV_OFFLINE=1 make
  prompt-dump-check test-assets governance test-req-coverage` to pass. Confirm the
  focused selectors prove both normal and repair/exhaustion paths and the asset check
  rejects missing, duplicate, unknown, uncollected, or aggregate-substitute brief
  claims; fix only second-cohort conformance gaps.
- [x] 4.2 Run `cd agent && UV_OFFLINE=1 make verify`,
  `openspec validate migrate-hitl1-profile-brief-capabilities --strict`, and
  `git diff HEAD --check`; record worktree status and confirm `backend/` and
  `frontend/` remain clean.
