# Proposal

## Why

The closed agent-support plan left phases 1–3 (local machine-readable diagnostics,
controller/node cognitive evaluation, public-tool diagnostic reads) strictly
conditional on phase 0: prove a *real* consumability or semantic failure first,
then pick the smallest owner — never build on an assumed gap. Phase 0 never ran;
its work stayed in the ledger as a todo. Its precondition has since landed: the
receipts machinery (lane registry, receipt runner, closeout binding) is live, and
the walkthrough instruments it names — the debugger exploration console
(`/harness`, `/targets`, `/inspect`, `/context`) — are delivered and journey-proven.
Running the two read-only walks now converts three conditional branches from
"someone believes there is a gap" into "here is the measured evidence and the
go/no-go".

## What Changes

- **Walkthrough A (coding-agent path, read-only replay)**: take one recent
  replayable fault (candidate: BUG-072 — the operator inventory reported a
  cancelled bundle as resumable while the demo-CLI integration test rode the
  ambient workspace) and, starting from the symptom text alone, independently
  locate the causal owner, the owning main spec, the narrowest reddenable test,
  the verification commands, and the current ADR. Record every actual friction:
  guessing, evidence not found, command output unsafe to parse. Compare the
  navigation result against what the real fix did.
- **Walkthrough B (dedicated-agent path, read-only case walk)**: walk a
  registered direction-change case (`public-controller-direction-loop@v1`) through
  the scripted journey and the exploration console: intent mapping, the loaded
  controller skill, the typed result, honest presentation, forbidden actions —
  explicitly distinguishing what local records can prove from what only a real
  model run could (no silent live reruns; credential lanes stay UNVERIFIED).
- **Deliverable**: a one-page evidence table (input; bound bundle/case and
  version; expected vs actual; authoritative result; proof strength; gap owner;
  lowest red seam) plus a go/no-go per phase-1/2/3 branch, recorded in the
  backlog todo. Every claimed friction must quote the navigation step that
  produced it; every verdict must cite a table row.
- No product, runtime, lifecycle, or gate behavior changes.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- None. `skip_specs: true` — this change is evidence collection plus a ledger
  decision record; each phase that earns a "go" carries its own change with the
  owning spec delta.

## Impact

- New: walkthrough notes and the evidence table under this change's directory
  (`evidence/`).
- Touched: `_backlog/todos/todo-agent-support-walkthroughs-and-diagnostics.md`
  (phase-0 outcome and per-branch decisions; ledger index/count consistency per
  the backlog ritual).
- No application code, specs, tests, or Makefile changes; no runtime behavior.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/`
  gitlink; this change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** the agent-support evidence question of this
  repository's existing support surfaces — the harness entry guide, the node
  `workflow.md` readers, the debugger exploration console, the eval case
  registry, and the proof lanes — which together answer "can each kind of agent
  independently walk its shortest path and know the boundary of its evidence".
  The deliverable (evidence table + go/no-go) lands in this change's evidence
  files and the backlog todo.
- **Seam classification:** wiring — two read-only replays/walks and a recorded
  decision; no authority over runtime behavior, no admission decision, and no
  gate verdict. The go/no-go is a ledger fact for humans, not an enforcement.
- **Question:** Do the two real paths fail today in ways that phases 1–3 would
  actually fix — and for each measured failure, which owner and which lowest red
  seam would carry the fix?
- **Necessary adjacent/external contracts:** the debugger exploration console
  (`scripts/demo_tui.py` driving `domain/debug_driving.py` +
  `runtime/debug_driver.py` projections) as the walkthrough instrument; the eval
  case registry (`evals/control/registry.json` with
  `public-controller-direction-loop@v1`) as the case source; the proof-lane
  registry and receipt runner (`proof-lanes.toml`, `scripts/proof_receipt.py`)
  as the evidence form; the closed plan and the backlog todo as the decision
  record being completed.
- **Evidence seam:** the walkthrough transcripts themselves — each friction row
  quotes the exact navigation step (command, output, missing evidence), each
  table row states proof strength (receipt-backed / recorded / UNVERIFIED), and
  the two lanes the walks exercise carry fresh receipts at closeout.
- **Not in scope:** implementing any phase-1/2/3 branch (each is its own change,
  opened only where this change says go), real-model or networked runs without a
  human-approved budget, rewriting `AGENTS.md` or batch-adding skills/ADRs, any
  runtime/lifecycle/observer behavior, and anything under `deerflow/`.
- **Triggered review policies:** none: read-only evidence collection and a ledger decision record with no candidate human judgment control fact admission/recovery boundary node-agent role or lifecycle output change.
