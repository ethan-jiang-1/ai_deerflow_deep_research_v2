# Stage 4 Apply - A-003 Rubric / Runner Authority

> Change: `reconcile-evaluation-rubric-authority`
> Apply authorization: user instruction `APPLY`, 2026-08-13
> Status: **APPLY AND ARCHIVE COMPLETE - STAGE 5 NOT AUTHORIZED**

## Authorization And Boundary

The explicit `APPLY` instruction authorizes execution of this change's checked task
sequence: conformance inspection, delta-spec synchronization, validation, and
alignment-ledger evidence. It does not authorize edits to application code, typed
contracts, fixtures, registries, prompts, tests, governance executables,
`openspec/config.yaml`, `CONTEXT.md`, ADRs, archived changes, or `deerflow/`.

If the inspected Case-to-subject-to-model handoff violates the selected A-003 Option A
boundary, this apply records `DEFERRED-CODE-CHANGE` and stops implementation
conformance work. It does not repair the code or add a regression test. Archive remains
separately unauthorized at apply time; the user later granted distinct archive
authorization, recorded in `07-a003-archive-closeout-review.md`.

## Apply Baseline

| Fact | Observation | Evidence boundary |
| --- | --- | --- |
| Repository HEAD | `09a2e3b7525d65e9c0e56d93c20735727be31e04` | Observed immediately before apply work. |
| Active changes | `reconcile-evaluation-rubric-authority` only; OpenSpec reports 4/4 planning artifacts and 0/21 tasks complete. | CLI state, not a completion claim. |
| Pre-existing worktree changes | The progressive ledger is modified; Stage 3 re-audit records, Stage 4 planning records, and this active change are untracked. | These predate apply work and are preserved. |
| DeerFlow gitlink | Index mode `160000` and `git submodule status` both report `66b9e7f21212490cf92fafac137542b9deb06615`; nested worktree porcelain is empty. | Git metadata only. DeerFlow source was not opened or modified. |
| Submodule diff | `git diff --submodule=short` contains only the existing progressive-ledger diff; no gitlink pointer change. | Manual bounded observation, not automatic protection. |

## Control-Placement Apply Review

The apply agent re-read the selected Option A record, Stage 3 A-003 conflict evidence,
the change proposal and Control Placement Review, design, CES/EVH/HITL1 deltas, tasks,
and `openspec/policies/control-placement.md`.

| Review question | Result | Control / evidence consequence |
| --- | --- | --- |
| Is a new quality controller introduced? | No. | The existing deterministic registry admission evaluator remains the only permitted control comparison; the Runner remains `completed`/`failed` only. |
| Which data are permitted at admission? | Rubric identity/version and the unique criterion-ID set only. | Read the actual loader and retain `schema_version` only as a current format check, not as a new approved normative fact. |
| May IDs occur after admission? | Yes, only as non-model control metadata. | Inspect whether the subject/model handoff interprets them as quality instruction, scoring, or a verdict before any spec sync. |
| What is prohibited? | Criterion prose, weights, thresholds, evaluator guidance, quality disposition, and any ID used as model-facing quality semantics. | Record `DEFERRED-CODE-CHANGE` and stop code-conformance work if observed. |
| Does existing focused evidence prove invalid-Rubric loader rejection? | No. | Re-run existing evidence and disclose this gap; do not create a new fixture or test in this alignment-only change. |

No new actionable task was found. The existing tasks already require the real handoff
inspection, bounded evidence statement, explicit defer action, and later sync. The
next action is task 2.1, not an implementation edit.

## Adjustment Record: A-003

| Field | Apply-time record |
| --- | --- |
| Before | CES unqualifiedly prohibited a Case-linked Rubric as execution input, while EVH required Rubric criterion validation for cognitive-program admission. |
| Intended after | CES, EVH, and HITL1 share the selected five-part boundary: identity/version and unique IDs are deterministic admission metadata; Rubric content and cognitive judgment remain review-only; Runner status remains `completed`/`failed`. |
| Risk | “Metadata” could become an unchecked channel for model-facing quality guidance or a Runner quality result. |
| Possible side effect | Current fixture propagation could disclose a code/spec gap; the main specs may become internally aligned while current code requires a separately authorized correction. |
| Control / stop condition | Inspect the direct consumer chain; record `DEFERRED-CODE-CHANGE` instead of modifying frozen runtime/test paths if prohibited content or quality semantics cross it. |
| Verification boundary | Source inspection, existing focused deterministic evidence, OpenSpec/governance checks, and the existing full deterministic suite. No live/paid evaluation or uninspected-route claim. |
| Current/required gap owner | Any handoff violation belongs to a separate, red-before-green code-and-test change. Stage 6 owns terminology propagation after the relevant decisions close. |
| Applied / verified | Applied by normal sync to the three owning main specs; 3.4 records one required answer and no deferred code change from the bounded inspected path. Strict OpenSpec, governance, whitespace, focused suite, and `UV_OFFLINE=1 make verify` passed. The completed change was archived at `openspec/changes/archive/2026-08-13-reconcile-evaluation-rubric-authority/`. |

## Post-Apply Evidence

| Field | Observed result |
| --- | --- |
| Changed delta paths | `openspec/changes/reconcile-evaluation-rubric-authority/specs/cognitive-evaluation-suite/spec.md`, `openspec/changes/reconcile-evaluation-rubric-authority/specs/evaluation-hardening/spec.md`, and `openspec/changes/reconcile-evaluation-rubric-authority/specs/hitl1-node/spec.md`. |
| Changed main-spec paths | `openspec/specs/cognitive-evaluation-suite/spec.md`, `openspec/specs/evaluation-hardening/spec.md`, and `openspec/specs/hitl1-node/spec.md`. |
| Applied content | CES now defines the five-part boundary and execution-only Runner statuses; EVH Wave0/Wave1/Wave2 and HITL1 name `review_criteria` as unique criterion-ID control metadata and prohibit quality-input use. Detailed merge evidence: `03-a003-main-spec-sync.md`. |
| No-code confirmation | `git diff HEAD -- deep_research_harness` and its whitespace check were empty; current status names no `deep_research_harness/` path. `git diff HEAD -- deerflow`, submodule diff, and nested DeerFlow status were empty. This is a worktree observation, not a future write barrier. |
| Observed side effects | **None observed within the performed checks.** The focused suite passed 56 tests; the complete offline verification passed its deterministic collections. No prohibited Rubric-content/quality crossing was found in the bounded handoff inspection. |
| Evidence bound on no observed side effect | No source-controlled invalid-Rubric registry fixture exists; only Wave2 has scripted real-node/bridge prompt evidence; HITL1/Wave0/Wave1 lack equivalent real-node prompt observation; no live/credentialed route was run. Passing deterministic checks do not prove those uninspected routes. |
| Remaining mismatch | No required/current mismatch was found in the bounded local path, so no `DEFERRED-CODE-CHANGE` is open for this apply. The stated evidence limits remain follow-up candidates, not a disguised conformance claim. |
| Deferred code/test gap owner | None for an observed violation. A future change that creates a Rubric-derived consumer or expands the handoff owns a red deterministic handoff test before implementation; Stage 6 separately owns terminology propagation without claiming universal runtime proof. |
| Verification evidence | `04-a003-synced-required-current-disposition.md`, `05-a003-structural-governance-verification.md`, and `06-a003-full-deterministic-verification.md`. |
