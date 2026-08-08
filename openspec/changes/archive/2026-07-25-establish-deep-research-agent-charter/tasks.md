## 1. Charter Sources And Module Routing

- [x] 1.1 Create `openspec/governance/agent-charter/README.md` and `charter.md` with the canonical source hierarchy, policy-routing index, non-authority boundary, and durable-principle admission rule. Add concise `@impl DRC-001` / `@impl DRC-005` traceability at the owning charter surfaces. (`DRC-001`, `DRC-005`)
- [x] 1.2 Create focused local-context, authority-and-projections, participant-outcomes, control-and-recovery, and change-admission policies. Give each a trigger, its required design questions, its non-authority boundary, and the exact owning contract to consult for behavior. (`DRC-001`, `DRC-003`, `DRC-005`)
- [x] 1.3 Add the human-authored primary-module focus gate before the generated block in `agent/AGENTS.md`, including the module-choice table, bounded lookup order, charter link, and the unchanged-root-guide boundary. Do not add nested `AGENTS.md` files. (`DRC-002`, `PRS-009`)
- [x] 1.4 Add concise governance README and OpenSpec authoring pointers to the charter index and Focus Card, without changing root `AGENTS.md` or `CLAUDE.md`. (`DRC-001`, `DRC-004`, `PRS-009`)
- [x] 1.5 Tighten the charter/index, local-context policy, module-guide focus gate, and OpenSpec authoring pointer with a context-expansion admission rule: every expansion answers a named causal question; general orientation, speculative usefulness, and upstream implementation browsing do not admit scope; ambiguous ownership stops for Focus Card clarification. (`DRC-001`, `DRC-002`, `DRC-004`)
- [x] 1.6 Add `agent/CLAUDE.md` as the thin Claude Code compatibility entrypoint importing the authoritative local `AGENTS.md`; do not duplicate, override, or modify the root guides. (`DRC-002`, `PRS-009`)
- [x] 1.7 Add an `agent-information-map` charter policy that assigns the coding-agent guide, Claude import, human/operator README, and OpenSpec authoring context distinct roles; state that line count is the primary deterministic attention budget, while word count remains a review concern. (`DRC-001`, `DRC-006`)
- [x] 1.8 Compact `agent/AGENTS.md` to a coding-agent routing map, keep `agent/CLAUDE.md` a thin import, add an early `## Reading Map` to `agent/README.md`, and reduce `openspec/config.yaml` to short authoring context with pointers to authoritative detail. (`DRC-002`, `DRC-006`)

## 2. Focus Card Admission Check

- [x] 2.1 Add red zero-dependency contract fixtures for the charter checker: a complete fixture passes; missing charter surfaces, missing index links, a missing focus-gate marker, and each missing Focus Card field fail with an actionable path/field diagnostic. (`DRC-004`, `PRS-009`)
- [x] 2.2 Implement `openspec/governance/check_agent_charter.py` to validate only permanent charter navigation and Focus Card shape across active proposals. Keep it standard-library-only, deterministic, and explicit that it does not judge prose or create runtime authority. Add `@impl DRC-004` / `@impl PRS-009` at the checker. (`DRC-004`, `PRS-009`)
- [x] 2.3 Add the checker to `agent/Makefile`'s governance target and keep the focused contract test in the deterministic fast lane. (`DRC-004`)
- [x] 2.4 Extend the zero-dependency checker and red fixtures to retain the stable local-context expansion-gate anchors and Claude Code import entrypoint while preserving its boundary: it verifies durable navigation/anchor presence, not whether a contributor's question is semantically correct. (`DRC-002`, `DRC-004`, `PRS-009`)
- [x] 2.5 Extend the charter checker and focused fixtures for information-map roles, required anchors, and line-count-first warnings/failures: warn at 120/fail above 160 for `agent/AGENTS.md`, warn at 10/fail above 12 for `agent/CLAUDE.md`, warn at 140/fail above 180 for `openspec/config.yaml`, and warn above 500 for `agent/README.md` without a hard README cap. (`DRC-006`)

## 3. Structural And Requirement Synchronization

- [x] 3.1 Finalize the append-only requirement registry: retain retired `AIC-001..003` and `PRS-008` with their supersession marker; register `DRC-001..005` and `PRS-009` without reuse. (`DRC-001`, `DRC-005`, `PRS-009`)
- [x] 3.2 Register the charter tree, checker, and focused test in `openspec/governance/project-structure.toml`; add `PRS-009` to the structure requirement set; update the project-structure delta and architecture-governance fixtures as required. (`PRS-009`)
- [x] 3.3 Render the controlled `agent/AGENTS.md` structure block through the existing architecture checker and verify that the human-authored focus gate stays outside that block. (`PRS-009`)
- [x] 3.4 Register `agent/CLAUDE.md` under `PRS-009`, revise the corresponding requirement-registry wording and project-structure delta, then render the generated guide so the canonical path stays synchronized. (`PRS-009`)
- [x] 3.5 Register the information-map policy and revise the project-structure delta/main-spec synchronization, architecture policy, renderer, and architecture fixtures so the generated `agent/AGENTS.md` block is a compact locator while TOML remains the exact path inventory. (`PRS-004`, `PRS-009`)

## 4. Active Change Migration

- [x] 4.1 Add a primary-module Focus Card to `harden-real-demo-provider-recovery`, naming its causal owner, named adjacent/runtime contracts, evidence seams, and explicit exclusions; do not alter that change's retry design. (`DRC-004`)
- [x] 4.2 Run the charter checker against every active change and correct any missing card or navigation surface without adding a second active interaction-charter change. (`DRC-004`)

## 5. Verification And Handoff

- [x] 5.1 Run the focused charter contract test and each root governance checker; include a known-invalid fixture proving the new checker cannot pass merely because no active proposal was scanned. (`DRC-004`, `PRS-009`)
- [x] 5.2 Pass `cd agent && UV_OFFLINE=1 make verify`, then from the repository root run `openspec validate establish-deep-research-agent-charter --strict` and `git diff HEAD --check`. Active pending IDs now have contract coverage and are accepted without being misclassified as missing main-spec ownership.
- [x] 5.3 Confirm the final protected-path status keeps `backend/`, `frontend/`, root `AGENTS.md`, and root `CLAUDE.md` unchanged, and document the charter index as the future starting point for Deep Research work. (`DRC-002`, `PRS-009`)
- [x] 5.4 Re-run focused charter and architecture checks, strict OpenSpec validation, line-budget warning coverage, formatter, and protected-path/diff checks after tasks 1.5 through 1.8, 2.4 through 2.5, and 3.4 through 3.5. Keep task 5.2 open until the separate pending-requirement governance defect is fixed. (`DRC-002`, `DRC-004`, `DRC-006`, `PRS-004`, `PRS-009`)

## 6. Human README Decomposition

- [x] 6.1 Create `agent/docs/README.md` as the human-facing docs index and move the
  root README's detailed runtime architecture, local operations, and testing/evaluation
  reference into `runtime-architecture.md`, `local-operations.md`, and
  `testing-and-evaluation.md` respectively. Preserve factual content and existing
  authoritative links; do not create a second runtime or test authority. (`DRC-006`)
- [x] 6.2 Reduce `agent/README.md` to product orientation, quick start, a compact
  high-frequency command route, and an early Reading Map that links the docs index and
  all three focused documents. (`DRC-006`)
- [x] 6.3 Register the docs index and focused documents in
  `project-structure.toml`, revise the project-structure delta and architecture
  fixtures, and keep the generated coding-agent locator compact. (`PRS-009`)
- [x] 6.4 Extend charter and documentation contract fixtures/checks for the stable
  root-map and docs-index links, move test-evidence vocabulary assertions to the
  testing reference, and lower the root README warning threshold to more than 200
  lines without imposing a hard cap. (`DRC-006`, `PRS-009`)
- [x] 6.5 Run focused documentation/charter/architecture checks, then
  `cd agent && UV_OFFLINE=1 make verify`, strict OpenSpec validation, and
  `git diff HEAD --check`; re-confirm protected paths. (`DRC-006`, `PRS-009`)
