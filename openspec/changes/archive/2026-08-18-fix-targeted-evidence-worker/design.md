# Design: fix-targeted-evidence-worker

## Context

See proposal.md — Why. Two independent defects in the wave2 repair loop
(BUG-045, verified against the preserved 003 bundle and code):

1. `run_gap_workers.worker` (`graph/nodes/targeted_evidence/subgraph.py`)
   builds `source_refs` in model output order; `CandidateResult`'s
   `validate_source_refs` requires `(source_id, canonical_url)` lexicographic
   order → every real-model candidate raises `source_refs_not_canonical` →
   plain exception → WORKER_FAILED → 9/9 attempts exhausted, zero ledger
   records. `wave1/subgraph.py` sorts (`sorted(output.sources, key=...)`);
   `wave0/subgraph.py` has the same latent defect (escaped by luck: fixture
   output `src_1..N` was already ordered).
2. `build_targeted_worker_prompt(gap_id)` passes only the bare gap id (e.g.
   `gap:gap_1`) with one allowed search; the model cannot know what to search
   (it reported this 9/9 times; all searches returned methodology articles).
   The gap descriptions exist in the canonical `synthesis/findings.json`
   artifact, readable via `store.read_synthesis_gaps()` (the readiness node
   already uses this same bounded read).

## Goals / Non-Goals

Goals:
- Targeted candidates pass the submission boundary: worker sorts source refs
  canonically (wave1 pattern); wave0 same defensive sort.
- Worker requests carry the assigned gap's bounded description as context so
  one search can target the gap's substance.
- Gap descriptions never participate in routing (TEL-001 id-only authority
  unchanged; descriptions join only at request-build time).

Non-Goals:
- No wave2 gate, budget, or convergence-gate changes.
- No change to the repair request, critics, materializer, or validator.
- No change to `materialize_gap_intents` (id-only intents stay).

## Decisions

### D1. Sort source refs in the worker before building the candidate

In `run_gap_workers.worker`: `ordered = tuple(sorted(output.sources,
key=lambda s: (s.source_id, s.canonical_url)))` then enumerate `ordered` for
cache write / metas / refs (mirrors `wave1/subgraph.py`). Same one-line pattern
applied to `wave0/subgraph.py`. Rationale: the validator's canonical order is
the authoritative contract; sorting at the worker is the smallest fix and keeps
the validator strict for every other producer.

### D2. Join gap descriptions at request-build time, bounded, fail-soft

- In `run_gap_workers`, before running workers: read
  `controller.store.read_synthesis_gaps()` in try/except (same posture as
  readiness `node.py`): on failure, an empty description map — workers still
  run with id-only context (today's behavior), never crash the loop.
- Build `desc_by_id = {g.gap_id: g.description for g in records}` and capture
  it in the worker closure.
- `build_targeted_worker_prompt(gap_id, gap_description: str | None)`:
  append the description to the objective bounded to
  `MAX_TARGETED_GAP_DESCRIPTION_CHARS` (truncate; no untrusted block needed —
  it is the synthesis artifact's own description, and readiness already treats
  it as trusted report context). `None`/empty → omit the description sentence
  (id-only, honest).
- Routing untouched: `materialize_gap_intents` still consumes only
  `unresolved_gaps` ids; descriptions never enter WorkIntent scope or gate
  state.

Why not alternatives:
- *Extend WorkIntent/WorkSpec with a description field* — rejected: touches the
  work-unit kernel, spec hashing, replay, and every producer; the description
  is worker-context, not a scheduling dimension.
- *Put description into `scope` tuple* — rejected: `scope` semantics are
  identifiers (GAP_ID_RE-validated); smuggling prose in would weaken the
  projection contract.
- *Have the model fetch the gap body itself* — rejected: the worker has one
  search and no fetch authority for the bundle; trusted join is deterministic.

### D3. Spec delta on `targeted-evidence-loop` (TEL-002) only

The behavior contract changes in the targeted worker requirement. `work-unit-kernel`
already enforces canonical source-ref order via the validator (no delta needed;
the fix is the worker conforming). `low-scale-real-auto` LSA-001's convergence
promise becomes reachable but its text doesn't change.

## Risks / Trade-offs

- [Risk] Sorting changes cache file numbering (source-0..N now sorted order) →
  acceptable: names are per-attempt artifacts, refs are content-addressed;
  wave1 already does this.
- [Risk] Description in prompt could bias the worker → mitigated: bounded,
  from the synthesis artifact's own gap body, read-only context; routing stays
  id-driven.
- [Risk] store read failure degrades context → mitigated: fail-soft to
  id-only (current behavior), loop continues.

## Verification

- New tests in `tests/graph/test_targeted_evidence_real.py`:
  (1) worker returns TWO sources in reverse canonical order → ledger record
  admitted, `source_refs` sorted (red before fix: candidate rejected,
  WORKER_FAILED, zero records);
  (2) `build_targeted_worker_prompt` with description → objective contains the
  bounded description; without → id-only;
  (3) node-level: gap record present in store → worker request carries it.
- wave0: unit test with unsorted 2-source output → admitted (defensive).
- Full gate `UV_NO_CACHE=1 make verify` + `openspec validate --strict`.
- Real 003 run (after BUG-044 change is also in) should show targeted
  submissions in the ledger and, ideally, gap convergence.
