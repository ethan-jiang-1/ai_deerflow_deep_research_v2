# Design: fix-synthesis-claim-ref-aliases (BUG-059)

## Context

BUG-059 blocked the fourth real mode-004 run at wave2_synthesis: the synthesis
model cites `claim:w1_c*` ids — first-class entities verifiably present inside
the accepted wave1 evidence document — but `_evidence_aliases` extracts only
`source_id`, `canonical_url`, and `support_refs`/`counter_refs` values, so claim
refs never project to an accepted submission ref and the whole candidate fails
`synthesis_finding_backing_ref_invalid`. Reproduced against the real model with
the bundle's own evidence (19 findings; 14 source-id refs passed the alias map,
6 claim refs hit the blind spot).

## Goals / Non-Goals

Goals:

- A finding citing real claim ids inside accepted evidence passes reference
  validation through the same deterministic projection as source ids.
- Fabricated claim ids (absent from all evidence) keep failing closed.
- One-line widening of an existing extraction — no new authority, prompt, or
  budget surface.

Non-Goals:

- No `question_id` alias (open-question disposition has its own deterministic
  contract — `source_questions`/`resolved_questions` — with no observed
  failure; widening without evidence would blur two distinct validation
  paths).
- No prompt change: the model's referencing behavior is correct; the defect is
  the projection blind spot.
- No change to the acceptance set, gate budget, or repair loop.

## Decisions

- **D1 — add `claim_id` to the existing extraction keys.** `_evidence_aliases`
  walks every dict in each evidence payload and already collects
  `source_id`/`canonical_url` values; adding `claim_id` to that key tuple
  gives every claim in accepted evidence the same projection as source ids.
  Alternative rejected: a dedicated claim registry built at wave1 acceptance
  time — more surface, same effect, and the alias map already exists for
  exactly this purpose.
- **D2 — fail-closed semantics unchanged.** Only ids actually present inside
  accepted evidence contents enter the map; anything else still falls through
  to the `backing_refs <= accepted` rejection. No fuzzy matching, no prefix
  inference.

## Risks / Trade-offs

- [A model invents `claim:`-prefixed ids that coincidentally collide across
  two evidence documents] → Not new: the same collision property already
  exists for `source_id`; the map keeps last-writer-wins per document walk and
  validation only needs membership, not uniqueness.
- [Claim refs project to the evidence's record hash, hiding which claim backed
  the finding] → Accepted: identical granularity to source-id refs today; the
  finding→evidence binding is what the contract requires.

## Migration Plan

Additive deterministic projection; no persisted format changes.

## Open Questions

None.
