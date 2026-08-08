## 1. Source-Faithful Rendering

- [x] 1.1 Add red-before-green deterministic tests for a pure agents-owned final
  phase-prompt renderer, then extract it from the bridge and prove the bridge uses
  the same system/user message without changing runtime-only metadata.
- [x] 1.2 Add a graph-owned canonical prompt-case registry with safe fixtures for
  every top-level `graph/nodes/**/prompts.py` builder that directly constructs a
  `NodeExecutionRequest`; the inventory test must reject an unregistered builder,
  a missing initial/repair variant for a `repair_error` builder, or an
  unsafe/non-deterministic fixture.
- [x] 1.3 Add a deterministic canonical-case bridge conformance test with fake
  model/tool bindings that captures the constructed agent system policy and child
  human message, then compares both exactly with the shared renderer for that same
  graph-owned case.

## 2. Review Catalog

- [x] 2.1 Add a bounded `scripts/prompt_dump.py` adapter plus `make prompt-dump` and
  `make prompt-dump-check`; add deterministic tests for write/check behavior,
  stable ordering, literal fenced prompt text, fixed output containment, exact-tree
  stale/unexpected-path handling, a fast-lane committed-catalog freshness check using
  the same adapter, and no model/tool/network execution.
- [x] 2.2 Generate and commit the complete `agent/node_prompts/` Markdown catalog
  and a concise index that identifies it as generated review output and distinguishes
  requested tool policy from runtime-resolved tools.
- [x] 2.3 Document how contributors refresh and inspect node prompt diffs in the
  focused testing reference without presenting generated artifacts as runtime
  authority.

## 3. Governance And Evidence

- [x] 3.1 Register `NPC-001`, `NPC-002`, `NOA-010`, and `PRS-011` with wording that
  preserves the agents-renderer/graph-case ownership split; register the renderer,
  graph registry, script, tests, and generated root in project structure; update
  requirement-evidence claims and impacts for the new deterministic seams.

## 4. Verification

- [x] 4.1 Run focused renderer, canonical-case bridge, catalog, generator, and
  architecture tests, including `make prompt-dump-check`, while completing the
  preceding tasks.
- [x] 4.2 Run `openspec validate make-node-prompts-auditable --strict`, all
  governance checks, `cd agent && UV_OFFLINE=1 make verify`, `git diff --check`, and
  record the final status before completion.
  Completed 2026-07-27: strict OpenSpec validation, the complete governance suite,
  and whitespace checks passed. `UV_OFFLINE=1 make verify` passed with 1,857 fast
  tests, 153 integration tests (four expected Gateway-stack skips), and 16 workflow
  tests. `git status --porcelain=v1 --untracked-files=all` recorded only the seven
  in-progress `establish-node-agent-capabilities` planning edits; no untracked files,
  `backend/`, or `frontend/` changes were present.
