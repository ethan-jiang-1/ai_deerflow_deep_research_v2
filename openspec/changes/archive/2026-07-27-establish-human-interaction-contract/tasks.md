## 1. Contract And Governance

- [x] 1.1 Add the frozen domain human-interaction contracts, pure candidate resolution, and focused domain tests for confirmation, revision, question, clarification, invalid candidates, and visible controls.
- [x] 1.2 Extend lifecycle, run-experience, session-operation, and checkpoint contracts with typed interaction projections, control selection, safe defaults, ownership entries, and compatibility tests.
- [x] 1.3 Register requirement IDs and the new source/test paths; add the human-interaction-integrity charter policy and route it from the charter index.

## 2. Semantic HITL1 Flow

- [x] 2.1 Add zero-tool semantic-intake prompt/result parsing and bounded three-call recovery helpers with deterministic scripted-result tests.
- [x] 2.2 Integrate candidate resolution into HITL1 while preserving graph-owned action/correlation authority, checkpoint-safe feedback, fresh proposal confirmation, and old partial-profile behavior.
- [x] 2.3 Add graph and lifecycle transcript tests for natural confirmation, revision, question, ambiguity, malformed output, transient exhaustion, cancellation, and old checkpoint compatibility.

## 3. Trusted Control Binding

- [x] 3.1 Make ResearchRunExperience project typed interaction facts and bind SelectControlRun only to a current advertised action; add stale/forged-control tests.
- [x] 3.2 Extend local session projections and broker resume handling to project and revalidate visible controls under the existing lock; add broker and workbench contract tests.

## 4. Adapter Experience

- [x] 4.1 Replace CLI magic acceptance input with natural-language guidance and numbered shared control selection; add deterministic CLI transcript tests for the reported failure path.
- [x] 4.2 Replace TUI text alias/action construction with shared visible-control dispatch and add adapter conformance tests.
- [x] 4.3 Update local operator-facing documentation for natural proposal interaction and bounded fallback without documenting hidden transport tokens.

## 5. Verification

- [x] 5.1 Run focused domain, graph, runtime, broker, CLI, and TUI tests while completing each preceding task.
- [x] 5.2 Run `openspec validate establish-human-interaction-contract --strict`, governance checks, `cd agent && UV_OFFLINE=1 make verify`, and `git diff --check`; record results before completion.

## Verification Record

- 2026-07-27: `openspec validate establish-human-interaction-contract --strict` passed.
- 2026-07-27: `python3 openspec/governance/check_project_reqs.py .` passed with 251 registered IDs, zero orphan IDs, and both active changes strict-valid. The active `establish-node-agent-capabilities` delta required pending ownership registration for `NAC-001` through `NAC-004`, `NOA-011`, `PRS-012`, and `EVH-012` before any complete gate could run.
- 2026-07-27: `cd agent && UV_OFFLINE=1 make verify` passed: governance, lock, lint, formatting, test-asset, and requirement-coverage gates passed; fast `1857/1857`, integration `157` selected tests, and workflow `16/16` passed.
- 2026-07-27: `git diff --check` passed; `backend/` and `frontend/` have no modified paths.
