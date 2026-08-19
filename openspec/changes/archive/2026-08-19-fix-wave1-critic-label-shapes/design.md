# Design: fix-wave1-critic-label-shapes (BUG-058)

## Context

BUG-058 (see `_backlog/bugs/BUG-058-wave1-critic-bool-fields-string-labels.md`)
blocked the first real mode-004 run at wave1: the real model returns
`"marketing_risk": "low"` where `CriticSourceAssessment` requires `bool`, the
pydantic failure is masked to `wave1_review_output_invalid`, and the gate
repair budget exhausts to `research.blocked`. Three facts drive the design:

1. `SourceDiagnosticResult`/`CriticSourceAssessment` live in
   `domain/critics.py` and are shared by the wave1 review and the targeted
   evidence critic — one normalization at the contract serves both.
2. The targeted critic's prompt already declares
   `"marketing_risk": "boolean"` in a `bounds` block
   (`targeted_evidence/prompts.py`) and its real runs pass — wave1 lacks only
   that declaration.
3. The 003 campaign established the deterministic contract-boundary
   normalization pattern for real-model shapes (`domain/synthesis.py`
   priority `high→1`; `domain/targeted.py` `url→canonical_url`).

## Goals / Non-Goals

Goals:

- A validated wave1 candidate can no longer be deterministically killed by
  label-shaped flags at the critic boundary.
- The closed-map semantics stay deterministic and auditable; ambiguity still
  fails closed.
- The wave1 prompt asks for booleans explicitly (parity with targeted).

Non-Goals:

- No mapping for `medium` (unobserved; genuinely ambiguous for a boolean —
  failing closed forces the bounded repair to re-ask rather than silently
  guessing a semantic).
- No ClaimVerifier/readiness changes (ClaimVerifier has no boolean fields —
  verified 2026-08-19; readiness has no observed failure).
- No change to gate budgets, repair routes, or artifact authority.

## Decisions

- **D1 — normalization lives on the domain model, not the wave1 parser.**
  A pydantic `field_validator(mode="before")` on the two boolean fields of
  `CriticSourceAssessment` normalizes the closed label set for every
  constructor path (wave1 parse, targeted parse, any future consumer).
  Alternative rejected: normalizing inside `parse_wave1_source_diagnostic`
  only (leaves targeted's parse exposed to the same labels; two call sites,
  two copies of the map).
- **D2 — closed map, casefolded, whitespace-stripped.**
  `true` side: `high|yes|true|elevated|needed|required`;
  `false` side: `low|none|no|false|minimal|minor|unlikely|not_needed`.
  The observed provider label (`low`) is covered; each entry is a distinct
  English severity/negation token a model plausibly emits for a flag.
  `medium` is deliberately absent (see Non-Goals). JSON booleans pass through
  untouched.
- **D3 — prompt parity, not prompt creativity.** Copy the targeted critic's
  `bounds` block verbatim into the wave1 expected-output and make the
  objective say "boolean flags (true/false)". The model should emit booleans
  first; D1 is the deterministic safety net, not the primary mechanism.
- **D4 — failure-code split, closed set.** `_canonical_critic_code` maps a
  pydantic `ValidationError` to `wave1_review_output_shape_invalid` (new
  closed code), distinct from JSON decode (`wave1_source_diagnostic_output_json_invalid`)
  and non-object failures. No exception text crosses the boundary — the
  split exists so the next real-shape failure is diagnosable from the event
  journal alone.

## Risks / Trade-offs

- [A future run emits `medium` and blocks again] → Accepted by design:
  evidence-driven posture; the bug flow then decides the mapping with a real
  semantic argument (and the D4 code split makes it visible immediately).
- [Normalization silently weakens the contract] → Mitigated: the map is
  closed and casefolded; anything unmapped raises the typed validation error
  exactly as today; unit tests pin every entry and the fail-closed path.
- [Prompt edit shifts model behavior for the passing targeted path] → None:
  targeted's prompt is untouched; wave1 gains the declaration targeted
  already proves safe.

## Migration Plan

Additive parse-boundary behavior plus a prompt declaration; no persisted
format changes, no rollout or rollback beyond reverting the diff.

## Open Questions

None.
