## Context

See `proposal.md` for motivation. The verified current chain is:

1. `hitl2-node` validates a Wave2-pass predecessor and does not create a human
   interrupt; the real ordinary path selects `proceed` autonomously.
2. The graph topology still contains closed HITL2 route labels and fixture compositions
   exercise them deterministically. These labels are internal graph/test controls.
3. HITL1 remains the current typed pending-input producer. Its text, language choice,
   visible-control, correlation, replay, and multi-round contracts remain active.
4. Five adjacent main specs and `run-lifecycle-walkthrough.md` still project the retired
   HITL2 human menu. Several adapter fixtures construct a synthetic HITL2
   `AwaitingInput`, so stale prose is also being reused as test input.

The accepted specs are normative; archived changes and `_backlog/plans/_archive/` are
provenance only. Runtime code, typed schemas, and deterministic tests establish current
conformance facts but do not silently rewrite the accepted specs.

## Goals / Non-Goals

**Goals:**

- Complete one auditable cutover from conflicting current specs to one autonomous
  HITL2 contract.
- Preserve every still-live HITL1, internal route, rerun, readiness, topology, and
  no-local-inference constraint.
- Replace production-shaped synthetic HITL2 prompt evidence with current HITL1 typed
  choice evidence and explicit autonomous-HITL2 negative evidence.
- Leave a bounded closeout scan that detects the exact stale claims removed by this
  change without turning archived provenance into current authority.

**Non-Goals:**

- Removing `Hitl2Decision`, `hitl2_rerun_payload`, internal topology edges, dormant
  decoder branches, or persisted schema values.
- Migrating or promising support for a real retained bundle that contains an historical
  HITL2 pending request; no such data set or current producer is admitted here.
- Changing graph execution, presentation implementation, public lifecycle APIs, or the
  future activation criteria for a genuine HITL2 human decision.
- Adding a permanent phrase-based governance checker. Exact wording scans are closeout
  evidence; current behavioral tests and owning specs remain the durable guard.

## Decisions

### D1. The owning HITL2 contract wins; adjacent specs are corrected projections

`hitl2-node`, its deterministic node boundary, and autonomous-path tests are the fact
authority for current HITL2 behavior. The five delta specs remove only claims that
grant current user-input authority at HITL2. They do not reinterpret internal route
labels or fixture scenarios as obsolete merely because their enum type is named
`Hitl2Decision`.

Alternative considered: mark every conflicting paragraph as historical in place. This
was rejected because text inside `openspec/specs/` remains approved behavior regardless
of a warning label and would preserve two current authorities.

### D2. Separate current producers from dormant compatibility-shaped decoders

The cutover grades the affected surfaces as follows:

| Surface | Grade | Disposition |
| --- | --- | --- |
| Accepted main capability requirements | Normative cross-boundary contract | Replace stale HITL2 human claims atomically through the five deltas. |
| HITL1 pending request/response and visible controls | Persisted/cross-boundary contract | Preserve unchanged and keep deterministic correlation evidence. |
| HITL2 graph routes, fixture routes, rerun payload, readiness return edge | Internal control and assembly contract | Preserve; explicitly deny interpretation as user options. |
| Synthetic HITL2 `AwaitingInput` test fixtures | Test-private projection | Delete or migrate to current HITL1 language-choice fixtures. |
| Broad typed decoder values that can represent historical HITL2-shaped input | Persisted implementation surface | Leave unchanged but remove the active producer/UX promise; later deletion requires a separate consumer/data migration change. |
| Archived changes and digested backlog material | Historical provenance | Preserve unchanged and exclude from current-authority scans. |

This is a clean break in the accepted interaction contract, authorized by this change:
no current producer may advertise HITL2 input after sync. It is not a persisted-schema
deletion. The dormant decoder is neither advertised nor used as evidence for current
behavior, and this change does not claim that old data is migrated or rejected.

Alternative considered: delete the dormant enum/schema support now. That would expand
the change into a persisted compatibility migration without an enumerated retained-data
population or a runtime need, so it is deferred explicitly rather than performed
silently.

### D3. Migrate tests by semantic responsibility, not by string substitution

Choice rendering, exact option submission, invalid option feedback, and typed answer
binding are proved with the current HITL1 language-choice fixture. HITL2-specific
evidence proves the opposite property: a valid HITL2 visit produces route/progress and
no `PendingResearchInterrupt`, `AwaitingInput`, Answer intent, or option menu.

The refinement-admission test that currently fabricates an HITL2 pending subject is
migrated to a valid HITL1 pending subject because its causal question is whether an
independent Run direction preserves a current correlated response, not whether HITL2
can interrupt. Tests of explicit decoder validation that use `phase="hitl2"` only as a
negative/type-boundary input may remain when their names and assertions do not claim a
current producer or user journey.

Alternative considered: keep the synthetic fixture as a generic adapter example. This
was rejected because it makes a removed product interaction look production-shaped and
duplicates coverage already supplied by HITL1 choice tests.

### D4. Synchronize registry and reader documentation in the same closeout boundary

Apply updates the `REN-001` and `REN-006` registry summaries so the registry remains a
projection of accepted requirements. The lifecycle walkthrough replaces “the second
human stop” with autonomous HITL2 validation and keeps later readiness/rerun topology
truth. No new requirement ID is introduced.

The closeout audit is scoped to current authority and reader surfaces only:
`openspec/specs/`, `openspec/governance/req-registry.yaml`,
`deep_research_harness/docs/run-lifecycle-walkthrough.md`, and the directly affected
test fixtures. It excludes `openspec/changes/archive/` and
`_backlog/plans/_archive/`. Before apply, the exact stale clauses provide a known red
baseline; after sync, the same bounded scan must return no current-human-HITL2 claim.

Alternative considered: rewrite archived changes. This was rejected because archives
must retain provenance and are not current authority.

## Risks / Trade-offs

- **[Risk] A broad cleanup deletes valid internal HITL2 topology.** -> Delta specs and
  diff review retain closed route labels, fixture route coverage, rerun compiler input,
  and readiness `repair_hitl2` explicitly.
- **[Risk] Removing a wire-compatibility sentence is mistaken for decoder/schema
  deletion.** -> Runtime and persisted schema are out of scope; diff and test selection
  must show no production-code changes.
- **[Risk] A stale test is renamed but still fabricates a second human stop.** -> The
  fixture audit checks constructors and usages of `awaiting_hitl2`, `phase="hitl2"`, and
  HITL2 `PromptOption` values, then classifies each remaining occurrence by semantic
  responsibility.
- **[Risk] Exact phrase scans miss paraphrased drift.** -> The scan is only closeout
  evidence; scenario-level autonomous tests and the owning specs provide the durable
  semantic guard.
- **[Risk] Main specs, registry, walkthrough, and tests land partially.** -> Treat their
  synchronization as one migration boundary; failed validation leaves the change
  active for repair and no partial archive is allowed.

## Migration Plan

1. Capture the current red baseline: enumerate the stale clauses in the five main
   specs, registry, walkthrough, and synthetic prompt fixtures.
2. Apply the five deltas, update the two registry summaries, and revise the walkthrough.
3. Migrate/delete synthetic HITL2 prompt fixtures and tests while retaining focused
   HITL1 typed-adapter and autonomous HITL2 evidence.
4. Run focused deterministic tests, the bounded current-authority scan, doc hygiene,
   Harness verification, OpenSpec governance, strict validation, and diff checks.
5. Sync the deltas into main specs and archive only when all five capabilities and
   adjacent projections are coherent. On failure, keep the change active and repair or
   revert the entire contract/document/test-fixture set; no data rollback is required
   because runtime and persisted state do not change.
