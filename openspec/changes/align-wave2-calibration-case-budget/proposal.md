# Proposal

## Why

The evidence-judgment calibration corpus still declares the pre-lesson `_ZERO`
resource tier (60 s wall clock / 16 k tokens) for its Wave2 synthesis branches,
while the production `wave2-evidence-synthesis` policy — after observing real
`budget.exhausted` failures — already carries 300 s / 64 k headroom. On the stale
tier, `calibrate-evidence-judgment-wave2-synthesis-repair-normal` timed out twice
in the 2026-09-26 live triage, and a resource-bound failure records no rubric
disposition: the case produced zero calibration data instead of a bounded
judgment result.

## What Changes

- Introduce a Wave2-grade resource tier in the evidence-judgment calibration
  corpus: the four `wave2-synthesis` branch cases (synthesis and repair, normal
  and highest-risk) declare 180 s wall clock / 32 768 tokens, keeping the single
  model call, zero-tool posture, and one-attempt shape unchanged. The values
  match the corpus's existing worker-grade tier (`_WORKER`: 180 s / 32 k) and
  stay under the production branch policy (300 s / 64 k / 4 calls).
- Move the corpus validator from a two-tier expectation (`_WORKER` vs `_ZERO`)
  to a three-tier expectation keyed by branch, preserving fail-closed per-tier
  equality enforcement.
- Update the corpus unit tests: per-branch tier assertion and a fail-closed
  drift case extended to the Wave2 tier.
- No production code, spec, corpus identity, case-count, or live-canary
  changes.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- None. The `evaluation-hardening` requirement for this corpus requires every
  case to declare bounded resources and keeps resource-bound failure a
  live-run failure without rubric disposition; it pins no concrete values, and
  the new tier satisfies every clause unchanged.

## Impact

- Primary implementation: `deep_research_harness/tests/scenarios/evidence_judgment_calibration.py`.
- Tests: `deep_research_harness/tests/unit/test_evidence_judgment_calibration.py`.
- Live-lane effect: the four Wave2 cases gain 3× wall-clock and 2× token
  headroom; completion is verified on the next selected live window rather
  than by this change's deterministic gate.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/`
  gitlink; this change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/tests/scenarios/evidence_judgment_calibration.py`,
  which owns the corpus case resource declarations and their closed validation.
- **Seam classification:** wiring — test-owned calibration resource
  declarations only; no production seam, candidate admission, repair bound,
  tool posture, or lifecycle output changes.
- **Question:** How can the Wave2 calibration cases stop failing on a resource
  ceiling the production layer has already abandoned, without weakening the
  corpus's fail-closed bound contract or touching any production budget?
- **Necessary adjacent/external contracts:** the production
  `_wave2_synthesis_node_agent_policy` (`runtime/research.py`) answers the
  branch-policy headroom lesson this tier must stay under (300 s / 64 k,
  raised after observed `budget.exhausted`); the existing `_WORKER` tier
  answers the corpus's established heavy-grade values (180 s / 32 k); the
  `evaluation-hardening` corpus requirement answers that resource-bound
  failure remains a live-run failure with no rubric disposition.
- **Evidence seam:** focused unit tests prove per-branch tier equality and
  fail-closed drift rejection; a static assertion documents the tier's
  distance to the production ceiling; the next selected live window verifies
  the case completes and records a typed rubric disposition.
- **Not in scope:** production policy values (300 s / 64 k unchanged), the
  intake-and-planning and evidence-intake corpora, other branches' tiers,
  corpus case identities or counts, `LIVE_CANARIES` deadlines, spec deltas,
  and anything under `deerflow/`.
- **Triggered review policies:** none: test-owned calibration resource tier alignment with no candidate, human judgment, control fact, admission/recovery boundary, node-agent role, or lifecycle output change.
