## Context

The archived profile-brief migration established local capability policies and
independent evidence for profile generation and repair. The existing HITL1 semantic
tests separately cover confirmation, revision, question, clarification, malformed
output, transient exhaustion, and cancellation. They do not yet state or exercise one
reviewable lifecycle acceptance set that verifies the people-facing outcome across
those journeys, including a revision with explicit first-party source/citation
constraints. Source inspection also establishes one deterministic presentation gap:
`build_proposal_context()` currently tells a person to provide a complete JSON profile
and repeats `accept_suggestion` in context data even when a complete proposal is
already available for natural confirmation.

The closest causal owner is the HITL1 node: it creates correlated interrupts, calls
the zero-tool semantic capability, and deterministically admits candidates. The
domain human-interaction contract supplies safe candidate and projection types.
`evaluation-hardening` owns how the focused test claims become evidence. Existing
checkpointed proposal, profile, route, and feedback fields remain the sole facts;
the change adds no projection authority or state schema.

## Goals / Non-Goals

**Goals:**

- Prove the complete current-proposal lifecycle with deterministic multi-visit
  transcripts at `build_real`, using fake capabilities rather than a live model.
- Demonstrate that natural confirmation is accepted only by graph-owned code; that
  a complete revision carrying first-party-source/citation constraints becomes a
  visible new proposal before later acceptance; and that question and ambiguity keep
  a current proposal actionable.
- Demonstrate that semantic failure remains a bounded non-terminal fallback with a
  concise, useful, non-schema-facing recovery message and visible control.
- Replace the confirmed complete-proposal JSON instruction and duplicated context
  action token with ordinary natural confirmation/revision/question guidance, while
  retaining `HumanInputRequest.action_ids` and `InteractionProjection.controls` as
  the trusted adapter binding and visible control; make no claim that fake semantic
  results prove live response quality.

**Non-Goals:**

- No prompt-quality claim from fake capability results, no live/provider evaluation,
  and no change to model capability assets, tool posture, provider retry bounds, or
  cancellation semantics.
- No graph route, state-schema, checkpoint, adapter, API, backend, frontend, or
  remaining-legacy-branch change.

## Decisions

### 1. Use a scripted multi-visit real-node transcript as the acceptance seam

The suite will invoke `hitl1.node.build_real` with the existing fake capability and
request-store infrastructure. Each interrupt response will be correlated to the
descriptor produced by the preceding visit, then the next visit will receive the
prior checkpoint update. Assertions will cover model request posture, state, route,
proposal version, persisted profile writes, feedback, and visible control.

This is the lowest seam that proves the node/domain/interrupt handoff together while
remaining deterministic and zero-API. Pure domain tests cannot prove correlation or
the node's actual materialization path; a LangGraph or adapter test would expand the
surface without proving more of the causal contract.

### 2. Make source and citation constraints ordinary revised proposal data

The revision scenario will use a valid full `ProposalValues` candidate whose
`must_answer`, `scope_boundaries`, or `custom_notes` explicitly asks for first-party
sources and citations. HITL1 must render that candidate as a new advisory proposal
and require a later correlated confirmation. The semantic candidate cannot attach
citations, research findings, route data, action ids, or checkpoint instructions.

This verifies that a person can refine research constraints through the actual
proposal contract without repurposing semantic feedback as research output. An
alternative to add a separate citation field is rejected: it would alter the profile
schema and widen this evidence-focused change.

### 3. Separate deterministic presentation/fallback proof from model-language quality

The focused transcript will assert that complete-proposal context contains neither
the JSON instruction nor duplicated action token, while the descriptor retains its
trusted action id and interaction control. It will also assert that closed
semantic-invalid/unavailable feedback is bounded and contains no schema/JSON or
hidden-action-token instruction. Scripted question and clarification candidates must
retain their proposal/control and carry bounded candidate text, but that text is not a
live-model quality sample. Existing `HIC-003` remains the contract for what a valid
proposal explanation may contain.

Exact full-message snapshots are rejected because they would make the test own
presentation copy rather than the typed feedback contract. A generic semantic-content
filter is also rejected: it would create a new, locale-sensitive control layer and
would not be honestly proven by a scripted fake result.

### 4. Add two new, non-overlapping central evidence claims

One collected selector will cover the accepted confirmation/revision/question/
ambiguity lifecycle, and another will cover exhausted semantic failure recovery.
They receive unique central claim ids and the new `HIN-011`, `HIC-004`, and
`EVH-014` requirement IDs. Existing capability claims remain evidence for migration,
not substitutes for lifecycle acceptance.

## Risks / Trade-offs

- [A long transcript becomes brittle because it encodes incidental interrupt payloads]
  -> Assert typed state, correlated request identity, selected human-visible fields,
  and forbidden leakage rather than every serialized payload byte.
- [A fake semantic result could be mistaken for live language-quality proof]
  -> Label claims as real-node/fake-capabilities deterministic authenticity; assert
  only the deterministic presentation/fallback text and candidate admission path.
- [A discovered defect invites a broader interaction redesign]
  -> Fix only the demonstrated owner-level gap; any new route, adapter, schema, or
  public-interface need stops this change for a separately proposed boundary.
- [The new evidence duplicates existing semantic tests]
  -> Keep existing focused tests; the new suite owns only cross-visit acceptance and
  has distinct central claim selectors.

## Migration Plan

1. Add the two red acceptance transcript tests and their central evidence claims.
2. Replace the confirmed complete-proposal context leak, then make only any further
   focused HITL1/domain correction that a required transcript demonstrates.
3. Run focused HITL1 and evidence checks, then the offline agent verification and
   OpenSpec/governance checks.

Rollback removes the new transcript tests/claims and any tightly coupled correction;
there is no persisted data, migration, API, or provider configuration to revert.

## Open Questions

None. The existing proposal, candidate, feedback, and recovery owners set the
boundary; implementation determines only whether a narrow correction is necessary.
