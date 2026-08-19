# Fix Synthesis Claim-Ref Aliases (BUG-059)

## Why

The fourth real mode-004 run (bundle `b_sLVVSNG2v8O9FFI1fbYJyZGESYBVBs3ByO571yciGOg`,
after BUG-058 let wave0/wave1 pass first-try) blocked at wave2_synthesis:
both the initial and the repair candidate failed
`synthesis_finding_backing_ref_invalid`. Root cause (reproduced against the
real model with the bundle's own evidence, 2026-08-19): `_evidence_aliases`
in `wave2_synthesis/node.py` projects model-visible identifiers back to the
submitting record hash, but only recognizes `source_id`, `canonical_url`,
`support_refs`, and `counter_refs` — not `claim_id`. The first-class entities
of a wave1 evidence document are its claims (`claim:w1_c1` …), and the
synthesis model legitimately points a finding's `backing_refs` at the very
claims it synthesized — ids that verifiably exist inside the accepted
evidence — yet the alias blind spot leaves them unprojected and the
`backing_refs <= accepted` check rejects the whole candidate. Bug record:
`_backlog/bugs/BUG-059-synthesis-claim-ref-alias-blindspot.md`.

## What Changes

- **Alias extraction recognizes claim ids.** `_evidence_aliases` adds
  `claim_id` to the dict keys it extracts from each evidence JSON payload
  (alongside `source_id`), mapping every claim id present in accepted
  evidence to that evidence's submission ref. Claim references in
  `backing_refs` then project to an accepted record and pass the existing
  acceptance check; fabricated claim ids (not present in any evidence)
  still fail closed exactly as before.
- No prompt change: the model's behavior (referencing real claim ids) is
  correct; this is purely a deterministic projection blind spot. The
  example in the synthesis prompt stays as-is because the observed model
  already emits valid shapes without following it.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `wave2-synthesis-node`: WSN-004's finding-reference validation gains the
  claim-id alias projection scenario.

## Impact

- `deep_research_harness/src/deerflow_deep_research/graph/nodes/wave2_synthesis/node.py`
  (one key added to `_evidence_aliases`'s extraction tuple)
- Tests: wave2 synthesis unit test for alias extraction and semantic
  validation with claim refs (red-first)
- Bug record: `_backlog/bugs/BUG-059-...` (fix关联 already updated)
- No gate, route, budget, prompt, or state-writer changes; no `deerflow/`
  gitlink changes. The 004 rerun acceptance stays in change `hard-real-auto`
  (task 4.3).

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/src/deerflow_deep_research/graph/nodes/wave2_synthesis/node.py` — `_evidence_aliases` is the deterministic projection the validation composes; the blind spot is exactly there.
- **Seam classification:** deterministic-guardrail — a pure identifier-projection widening at the existing validation boundary; no cognitive responsibility, prompt, or authority changes.
- **Question:** How does a finding that cites claim ids real inside an accepted evidence document get admitted through the same deterministic projection that already admits source ids and URLs, without weakening the fail-closed rejection of fabricated references?
- **Scope honesty:** fixes the observed blocker for the synthesis validation path; does not claim coverage of `question_id` projections (open-question disposition has its own deterministic contract with no observed failure) or of model-invented shorthand ids outside evidence (correctly rejected today).
- **Necessary adjacent/external contracts:** none beyond WSN-004 itself; the acceptance set, gate, and repair budget are untouched.
- **Evidence seam:** `deep_research_harness/tests/unit/test_wave2_synthesis*.py` (alias extraction + semantic validation with claim refs); the real 004 rerun in `hard-real-auto` task 4.3 is the end-to-end evidence.
- **Not in scope:** `question_id` aliases; prompt rewording; gate/budget changes; the BUG-058 wave1 critic (already fixed under `fix-wave1-critic-label-shapes`).
- **Triggered review policies:** change-admission

## deerflow boundary

Ordinary downstream work neither modifies nor source-browses the `deerflow/`
gitlink; this change does not own or approve any `deerflow/` boundary work.
