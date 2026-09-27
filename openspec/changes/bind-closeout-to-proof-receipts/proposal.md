# Proposal

## Why

The companion change (`add-evidence-receipts-and-proof-lanes`) makes receipts cheap
and hard to fake, but a receipt nobody checks is advice again. This repository has
already paid for that lesson three times in one session: a suite that rode ambient
state, a commit that landed with a red gate because the commit was chained after
it, and a runbook promise no assertion pinned. Closeout is where the repository
decides a change is done, so closeout is where a receipt must become binding.

## What Changes

- Register `openspec/governance/check_proof_receipts.py` as a component checker of
  the same OpenSpec root governance aggregate.
- `closeout` requires a runner-produced receipt for every lane whose declared
  surfaces intersect the change's touched files: exit zero, clean tree, a revision
  that still covers those surfaces, a transcript whose digest matches and whose
  text carries the lane's success sentinel.
- A caller-declared claim never satisfies it, and every missing or stale receipt
  names the exact rerun command.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `project-structure`: `PRS-009` extends the aggregate's registered component set
  with the proof-receipt checker and its closeout obligation, plus two scenarios
  (a stale or missing receipt blocks closeout; a caller-declared claim never
  satisfies it).

## Impact

- New: `openspec/governance/check_proof_receipts.py`; touched:
  `openspec/governance/check_project_gate.py` (component inventory and its
  printed wording), `openspec/governance/required-paths.toml` (inventory),
  `openspec/governance/selected-change-closeout.md` if it restates the
  composition, and the local guidance's Delivery Lanes sentence.
- Roll-out: the checker lands in warn-only mode for a measured window (run against
  recent archived changes to size false positives) before closeout treats a
  missing receipt as a failure; the tasks carry both steps.
- Requires the companion change's runner and registry; it has no effect without a
  lane registry to read.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/`
  gitlink; this change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** the OpenSpec root governance aggregate
  (`openspec/governance/`), which owns what a closeout verdict aggregates.
- **Seam classification:** deterministic-guardrail - a gate rule and its verdict,
  with no runtime behavior, no candidate, and no human decision inside the check.
- **Question:** What must a closeout verify so that "done" cannot travel further
  than the evidence that produced it?
- **Necessary adjacent/external contracts:** `PRS-009` owns the aggregate's
  composition and the registered component set; the companion change owns the lane
  registry and the receipt format (`proof-lanes.toml`,
  `scripts/proof_receipt.py`); git owns the revision diff used for staleness.
- **Evidence seam:** the checker's own focused tests - a change with a stale
  receipt fails, a change with a fresh receipt passes, a hand-written claim fails
  - plus a planted-violation negative control and a measured warn-only window
  against recent archived changes.
- **Not in scope:** runtime or lifecycle behavior, the lane definitions
  themselves, and anything under `deerflow/`.
- **Triggered review policies:** change-admission, authority-and-projections
  This change alters the closeout verdict and the aggregate's registered component set,
  so it carries the `PRS-009` delta for review before apply.
