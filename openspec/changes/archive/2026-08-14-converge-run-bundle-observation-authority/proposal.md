## Why

Current Bundle-local lifecycle code already owns Run existence, refinement admission,
and Bundle-loss truth, but the `research-run-session` and
`research-session-lifecycle-binding` capabilities, their registry rows, and their
evidence annotations still describe deleted session stores, brokers, bindings, and
checkpoint recovery. The remaining state-only `BundleLifecycle.refine()` wrapper also
lets the Local Session Workbench bypass the canonical `RefinementAdmission` result.

## What Changes

- Retire the `research-session-lifecycle-binding` and `research-run-session`
  capabilities only after each still-valid observation, diagnostic, and anti-recovery
  rule has one current Bundle, Journal, workbench, or worker-failure owner. Deprecated
  `RES-*`/`RUS-*` IDs will not be reused.
- Rename the semantics-preserving `research-session-discovery-and-operations` and
  `research-session-artifact-view` capabilities to their Run Bundle names, retaining
  their requirement IDs and bounded discovery/artifact behavior without a temporary
  dual capability.
- Migrate the Local Session Workbench and its internal focused consumers from the
  state-only compatibility wrapper to `RefinementAdmission`, preserving the same
  `BundleControlResult` projection and all existing conflict, idempotency, restart,
  replay, textless-continuation, and Bundle-loss outcomes; then remove the wrapper.
- Move requirement registry, `@impl`, test-evidence, documentation, and structural
  references to the current owners. Retained anti-resurrection tests gain explicit
  planted violations rather than disappearing with the retired names.

## Capabilities

### New Capabilities

- `run-bundle-discovery-and-operations`: retains the existing `RDO-*` scoped
  discovery and typed operation contract under its current Bundle-only name.
- `run-bundle-artifact-view`: retains the existing `RSV-*` fixed contained artifact
  view contract under its current Bundle-only name.

### Modified Capabilities

- `research-run-session`: transfers or deprecates its `RUS-*` requirements and then
  retires the obsolete mixed-authority capability.
- `research-session-lifecycle-binding`: transfers anti-recovery guards and then
  retires the deleted binding mechanism and its positive registry claims.
- `research-session-discovery-and-operations`: transfers its unchanged `RDO-*`
  contract to `run-bundle-discovery-and-operations` and retires the session-named
  capability path without a dual route.
- `research-session-artifact-view`: transfers its unchanged `RSV-*` contract to
  `run-bundle-artifact-view` and retires the session-named capability path without a
  dual route.

## Impact

- `deep_research_harness/src/deerflow_deep_research/runtime/bundle_lifecycle.py`,
  `runtime/session_workbench.py`, the canonical-admission comment in
  `runtime/bundle_control.py`, current observation/workbench contracts, focused
  lifecycle/workbench tests, and requirement-evidence metadata
- Main specs and registry paths for Bundle lifecycle, Event Journal, Local Session
  Workbench, the two renamed Bundle capabilities, and retired session/binding
  capabilities
- No root-package Python export, external supported API, persisted Run schema/reader,
  credentialed live lane, or `deerflow/` gitlink source is changed

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/runtime/bundle_lifecycle.py`; it owns trusted-scope Bundle selection, `RefinementAdmission`, and the single State mutation boundary.
- **Seam classification:** deterministic-guardrail because the change removes a compatibility projection while preserving the lifecycle's non-bypassable admission, typed outcome, and no-recovery boundaries.
- **Question:** How can the current Bundle lifecycle become the only refinement-admission handoff while session/binding residue and their evidence move to the actual Bundle, Journal, workbench, and worker-failure owners without changing legal next actions?
- **Necessary adjacent/external contracts:** `deep-research-harness-run-bundles` answers State authority, refinement, and Bundle-loss outcomes; `run-event-journal` answers retained observation/no-recovery ownership; `research-local-session-workbench` answers local projection of the typed control result; renamed `RDO`/`RSV` capabilities answer scoped discovery and fixed artifact access; `runtime-integration` answers why a trusted-scope bucket and checkpoint namespace cannot become identity, an index, or recovery; requirement registry, project structure, and test-evidence metadata answer exact ID/path/evidence migration. No DeerFlow interface is required or admitted.
- **Evidence seam:** focused Bundle lifecycle, workbench, observation-separation, retired-import, and requirement/structure governance tests; each retained guard keeps a planted deleted-module, control-method, or owner-mapping violation.
- **Not in scope:** retained Run/Journal schema migration or old-record cutover, external Python support, new session/binding/broker APIs, checkpoint/provider recovery, public tool schema changes, new human controls, live evaluation, or modifying/source-browsing `deerflow/`.
- **Triggered review policies:** authority-and-projections, participant-outcomes, human-interaction-integrity, control-and-recovery, workflow-outcome-review, control-placement, change-admission

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Refinement admission handed to the local workbench | A Primary User supplies bounded refinement text, but never a lifecycle result or State mutation | `BundleLifecycle.admit_refinement()` owns `RefinementAdmission` and State transition validation | human-decision | The workbench projects only its shared typed result; duplicate, conflict, active, exhausted, and unavailable outcomes retain their existing legal next action | Reuses one admission result and removes the state-only wrapper as a competing consumer contract | Workbench/lifecycle integration tests for pending response separation, replay, conflict, and textless continuation |
| Journal, diagnostics, and retired binding names after Bundle loss | No candidate or judgment | Bundle-local State and `DRH-006` own availability; `REJ-004` owns read-only observation denial | non-bypassable | A lost Bundle is unavailable and no binding, checkpoint, index, Journal, or diagnostic can reopen or recover it | Moves guards to current owners and removes an obsolete capability authority | Observation-lifecycle separation and planted retired-module/control-method violations |
| Session-named capability records | No candidate or judgment | Current Bundle/Journal/workbench specs and requirement registry establish the exact owner-to-ID mapping | non-bypassable | Each retained clause has one current owner; retired IDs are deprecated, never repurposed | Removes duplicate capability authority and temporary dual paths | Strict spec/requirement coverage, registry mapping tests, and known-invalid orphan/duplicate fixtures |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Missing, foreign, corrupt, or deleted Bundle selected for refinement or inspection | Bundle-local State through `BundleLifecycle` | No recovery from Journal, binding, checkpoint, cache, or retained artifact | Typed unavailable/denied result with no State or graph mutation | Start an independent Run only when the lifecycle allows it | Bundle-loss and observation-separation integration tests |
| Replayed, conflicting, active, or exhausted refinement | `RefinementAdmission` and Bundle-local State | Existing lifecycle CAS/replay/continuation rules only; no workbench retry or inference | Existing pending, conflict, blocked, or applied typed projection | The typed result's already-declared legal action | Refinement admission, round-recovery, and workflow suites |
| Retired session/binding import or Journal control API appears | Current structure and `DRH-006`/`REJ-004` guard owners | No runtime recovery; remove the violating surface before merge | Deterministic guard failure | Restore the current owner-only boundary | Planted import/path and Journal-control negative tests |
