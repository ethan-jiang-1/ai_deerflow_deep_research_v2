# Design

## Context

The evidence-judgment corpus validator enforces **equality** against two
resource tiers: `_WORKER` (180 s / 4 calls / 32 k, targeted-evidence/worker
branch) and `_ZERO` (60 s / 1 call / 16 k, every other branch — twelve cases
including the four `wave2-synthesis` cases). The spec requires each case to
declare bounded resources and keeps resource-bound failure a live-run failure
without rubric disposition; it pins no values. The production
`wave2-evidence-synthesis` policy was raised to 300 s / 64 k after observed
`budget.exhausted` on real output, while the corpus kept the pre-lesson `_ZERO`
values. Healthy-link baseline for a real full synthesis call is ~25 s
(live canary `live-wave2-synthesis`, wall time 24.7 s).

## Goals / Non-Goals

**Goals:**

- Wave2-synthesis branch cases declare a resource tier that survives
  moderately slow (non-catastrophic) provider latency and records a typed
  rubric disposition instead of a bare timeout.
- The tier values trace to existing in-repo facts, not to a new guess.

**Non-Goals:**

- No production budget changes; no changes to other corpora, branches,
  case identities, or counts; no new spec surface (the corpus requirement's
  "declare resource limits" clause is satisfied as-is).
- No attempt to make the case pass during catastrophic provider windows
  (documented 240 s `stream_chunk_timeout` nights defeat any case budget;
  the lane is explicitly selected and a hung call is a live-run failure).

## Decisions

1. **Tier values 180 s / 32 768 tokens, single call, zero tools, one attempt.**
   Rationale: they equal the corpus's existing `_WORKER` heavy grade — the
   in-repo precedent for "this branch's calls are the heavy kind" — and stay
   under the production ceiling (300 s / 64 k / 4 calls) with margin.
   Alternatives considered: (a) mirroring the production ceiling exactly
   (300 s / 64 k) — rejected: cases deliberately run narrower than branch
   policy (`_WORKER` is 180 s against a 900 s production ceiling), and a hung
   single call would burn five minutes of an explicitly selected lane;
   (b) wall-clock-only bump (180 s / 16 k) — rejected: splits the tier from
   the established `_WORKER` grade without evidence for the odd hybrid;
   (c) no change, record the failures as known environmental variance —
   rejected: the production layer's own recorded tuition shows the 60 s / 16 k
   class is too tight for real Wave2 calls, and a resource-bound failure
   yields no calibration data, so the stale tier can waste a live window.
2. **Both wave2 sub-branches (synthesis and repair) take the tier.**
   Rationale: the production policy covers both; splitting them would encode
   an arbitrary distinction the branch policy does not make. The observed
   failure was on repair-normal; synthesis gets the same tier for branch
   uniformity, not because it failed.
3. **Validator moves to a branch-keyed three-tier map, keeping equality.**
   Rationale: the fail-closed equality contract is the corpus's drift guard;
   per-tier equality preserves it exactly. Alternative — ceiling-only
   validation (0 < v ≤ branch policy) — rejected: it invents spec surface the
   corpus requirement does not own and weakens drift detection.
4. **A static unit assertion documents tier-to-ceiling distance** (180 ≤ 300,
   32 768 ≤ 64 000) so a future production raise or tier drift is visible in
   review; it asserts ordering only, not equality, and adds no new governance
   semantics.

## Risks / Trade-offs

- [Longer hung-call burn in a bad window] → a timeout now costs 180 s instead
  of 60 s of an explicitly selected lane; accepted — the lane is opt-in and
  the rubric semantics ("resource-bound failure records no disposition")
  are unchanged.
- [Tier loosened without a clean-window latency sample] → the values are not
  a latency estimate; they propagate the production layer's recorded lesson
  and the corpus's established grade. The next selected live window is the
  verification step recorded in tasks.md; if the case still times out at
  180 s on a healthy link, that is new evidence for a deeper problem, not a
  reason to keep raising the tier.
- [Fail-closed drift test must keep rejecting] → the existing
  `evidence_judgment_calibration_bounds_invalid` mutation test is extended
  to mutate a wave2 case's tier field and must still raise.
