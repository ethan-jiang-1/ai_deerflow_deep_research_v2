# Proposal

## Why

The workbench could step a run but could not answer the questions this harness
actually raises while debugging: what is this harness composed of, which objects
can I debug, what did a node produce, and - for the real composition - what was
the model actually given and allowed? Runbook-031 promised that `/context` shows
the exact initial prompt, runtime MD bytes and enforced tools/budget, while the
pane rendered only a summary line. Two id-taking entries also dead-ended: a bare
`/replay` printed a usage line instead of listing candidates, and the first
screen's action list omitted the newer commands.

## What Changes

- **Exploration surface**: `/harness` (composition name, recipe revision,
  compatibility fingerprint, per-node kinds, prerequisites, logical ladder,
  trusted roots with policy labels, readable projections), `/targets` (scope,
  every Bundle with status/phase/frames/generation and attach posture, plus the
  live session's posture and pending item), `/inspect <id>` (state, frame
  sequence, typed work-unit records, delivery artifact, observation summary).
- **Captured context is readable**: `/context` lists each captured invocation
  with its model/tool counts, enforced tools, budget and mounts, and
  `/context <node>#<n>` drills into that invocation: objective, expected output,
  initial system policy, initial human message, base-policy and capability layers
  (identity, sha256, size and content excerpt), requested versus enforced tools
  with posture, budget, output schema, virtual roots and mounts, activity, the
  coverage strip, and the NOT RETAINED raw-history label.
- **No dead ends**: a bare `/replay` lists bounded candidates like `/attach`, and
  the no-session prompt lists both start compositions and the id-taking entries.
- **One-command evidence**: `make debugger-proof` runs the driver matrix, entry
  contract, workbench tests, journey harness and the fifteen-journey operator
  experience suite.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `research-demo-tui`: `RED-014` gains the exploration-surface and
  captured-content clauses plus two scenarios.

## Impact

- Primary owner: `scripts/demo_tui.py` (presentation over existing typed readers:
  lifecycle state, trace projector, Node Context store, the adapter's typed
  work-unit store).
- Verification: a workbench test asserts the captured invocation's enforcement
  facts, layer identities and content, and the drill-down; the journey harness
  (23 checkpoints) and a new fifteen-journey experience suite cover the operator
  path; `make debugger-proof` runs the whole chain.
- Measured state before the change: `make verify` 0, `make tui-journey` 0,
  `make debugger-proof` 0 (17 + 10 + 65 tests, 23 checkpoints, 15 experiences),
  closeout gate 0, doc hygiene clean.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/`
  gitlink; this change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** `scripts/demo_tui.py` for what the operator
  can see and reach.
- **Seam classification:** wiring - every fact is read through an existing typed
  owner (lifecycle state, trace projector, Node Context store, typed work-unit
  store, the recipe the executor already holds); no new authority and no prompt
  is rebuilt.
- **Question:** How does the debugger let an operator see the harness it drives
  and every object it could debug - including what a captured model invocation
  was given and allowed - without inventing a second authority?
- **Necessary adjacent/external contracts:** `RED-014` owns the workbench
  surface; `ResearchGraphRecipe` answers composition facts; the lifecycle and
  trace projector answer Bundle facts; `adapter.create_work_unit_store` answers
  typed work-unit records; `NodeContextStore` answers captured content.
- **Evidence seam:** the workbench test for captured content and drill-down, the
  journey harness, and the operator experience suite (each journey independent) -
  all wired into `make verify` / `make tui-journey` / `make debugger-proof`.
- **Not in scope:** driver semantics (unchanged this round), lifecycle/experience
  behaviour, evaluation tooling, and anything under `deerflow/`.
- **Triggered review policies:** none: presentation and read-only projection, with no candidate, human judgment, control fact, admission/recovery boundary, node-agent role, or lifecycle output change.
