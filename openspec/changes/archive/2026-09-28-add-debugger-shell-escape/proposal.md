# Proposal

## Why

The operator directing this change hit the workbench's flexibility wall in its first
live window: paused at a boundary, they wanted to look at the filesystem — what the
run just wrote, what the journal says — and the workbench offered only its typed
panes. The debugger is a local operator tool that runs on the operator's own machine
and terminal, so a bounded shell escape grants the operator no authority they lack;
its value is staying in the flow (no window switching) and cwd anchoring to the exact
bundle being debugged, which is knowledge only the workbench has. The operator's
direction: at every pausable boundary, the filesystem should be inspectable as
flexibly as possible. The graph side stays untouched — model-facing tool authority
remains admission-controlled; this change adds only an operator-side escape.

## What Changes

- The workbench composer gains an operator shell escape: input prefixed with `!`
  runs as a bounded one-shot command instead of being consumed as a research answer
  or a debug command. Works at every posture, including HITL stops.
- The command runs with the operator's own privileges, non-interactive (`stdin` is
  `/dev/null`), with a bounded runtime (default 15s, terminated on overrun) and
  bounded captured output (default 4000 chars, truncation stated). Working directory
  anchors to the live session's Bundle directory when a session is open, else the
  workspace bundle root, else the process cwd.
- Output is rendered in the log verbatim and labelled as operator-invoked content
  (command + working directory); it is not a workbench projection, and no graph
  state, admission decision, or tool authority is derived from it. `/help` and the
  hint line list the capability.
- Spec delta under `research-demo-tui` (ADDED requirement): this extends the
  workbench's documented surface — unlike the preceding conformance repairs, the
  behavior is new and needs its own requirement text.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- None. A new requirement is ADDED under the existing `research-demo-tui` capability
  (operator shell escape at the workbench); the RED-013/RED-014 requirement texts are
  unchanged.

## Impact

- Primary implementation: `deep_research_harness/scripts/demo_tui.py`.
- Tests: `deep_research_harness/tests/unit/test_demo_tui_shell_escape.py` (new),
  `deep_research_harness/tests/integration/test_debugger_entry.py`.
- Docs: in-app `/help` and the workbench hint line (owning surfaces for the
  capability listing); no runbook rewrite required.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/`
  gitlink; this change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/demo_tui.py` —
  the workbench input router and a new pure capture helper; the adapter, driver,
  lifecycle, and graph are untouched.
- **Seam classification:** presentation — an operator-side convenience surface with
  an explicit authority statement; no candidate, human-decision, or cognitive seam is
  involved, and no runtime behavior outside the TUI process changes.
- **Question:** How does the operator inspect the filesystem flexibly at any paused
  boundary without turning the debugger into graph authority or breaking the typed
  pane contracts?
- **Necessary adjacent/external contracts:** `research-demo-tui` owns the workbench
  surface (the delta is ADDED there); the "no host paths" clause in RED-014's pane
  contract is about workbench projections, while the escape renders operator-invoked
  content in the log; `find_bundle_dir` + the adapter's `bundle_root` own the cwd
  anchor; BUG-075/BUG-077 own how the embedded composition reaches this surface.
- **Evidence seam:** unit tests for the capture helper (cwd anchoring, exit code,
  stderr, timeout bound, truncation, non-interactive stdin) red-first via
  ImportError; a run_test probe asserting a `!`-prefixed composer line renders its
  command output as a standalone log line (and is not consumed as a debug command)
  red-first via misroute; then the standard gate ladder.
- **Not in scope:** graph/model tool authority (admission-owned, unchanged), a
  persistent interactive shell, output streaming while the command runs, non-debug
  compositions (the 020 recon chat keeps its own model-bound read-only tools), and
  anything under `deerflow/`.
- **Triggered review policies:** none: presentation surface addition with no candidate, human judgment, control fact, admission/recovery boundary, node-agent role, or lifecycle output change.
