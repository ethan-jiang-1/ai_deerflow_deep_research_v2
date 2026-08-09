## Why

The real CLI and TUI render the approved read-only command
`make demo-sessions DEMO_ARGS="inspect <bundle-id>"`, but `demo_sessions.py` accepts
only a one-argument spelling. Copying the rendered command therefore fails in argparse
before any retained observation can be inspected, while README and local operations
document the incompatible form.

## What Changes

- Restore the existing `inspect <bundle-id>` command grammar in the read-only
  inspection entry and reject the old one-argument spelling rather than maintaining
  two command contracts.
- Preserve the `RunObservationStore.inspect()` result as the sole source of available,
  invalid, missing, and corrupt inspection outcomes; successful inspection exits zero
  and unavailable inspection remains a bounded nonzero result.
- Align entry help, README, and local operations with the renderer's existing canonical
  command, add a Harness-root subprocess regression using a retained observation, and
  correct the test-owned execution claim so it names that real command boundary.
- Keep inspection read-only: it neither discovers a Bundle nor starts graph, provider,
  sandbox, lifecycle, or recovery work.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- None. Existing `research-cli-onboarding` requirements `REC-005` and `REC-006`
  already require this grammar and read-only outcome; this change restores their
  implementation and documentation conformance.

## Impact

- Primary implementation: `deep_research_harness/scripts/demo_sessions.py`.
- Adjacent projections: `scripts/_terminal_failure_presentation.py`, the standalone
  CLI/TUI renderers, `README.md`, and `docs/local-operations.md`.
- Evidence: focused parser/read-only and documentation contracts, plus a real
  Harness-root `make demo-sessions` subprocess contract. The test-owned execution
  claim will name the process contract rather than a direct `run()` call.
- No public DeerFlow interface, graph topology, Bundle lifecycle behavior, or
  `deerflow/`, `backend/`, or `frontend/` source changes.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/demo_sessions.py`,
  which admits the local inspection grammar and projects the typed read-only result.
- **Question:** How can the command copied from shared CLI/TUI output execute exactly
  one safe `inspect <bundle-id>` observation without creating a second command or
  lifecycle-control authority?
- **Necessary adjacent/external contracts:** `_terminal_failure_presentation.py`
  answers the canonical rendered spelling; `RunObservationStore.inspect()` answers the
  authoritative availability and read-only facts; `research-cli-onboarding` owns the
  existing `REC-005`/`REC-006` contract; README and local operations publish, but do
  not define, that contract.
- **Evidence seam:** A Harness-root child process invokes the exact rendered Make
  command against an observation created by the public store API and proves safe
  output plus zero/nonzero disposition; focused direct coverage separately proves the
  entry calls only `RunObservationStore.inspect()` and cannot gain lifecycle authority;
  documentation coverage keeps both published operator routes on that same grammar.
- **Not in scope:** Bundle discovery, arbitrary path/profile input, session references,
  cross-process resume, retry, cancellation, refinement, graph/provider construction,
  or modifications under `deerflow/`, `backend/`, or `frontend/`.
- **Triggered review policies:** control-placement, participant-outcomes, workflow-outcome-review

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| Inspection command target | An operator supplies an opaque Bundle id after the literal `inspect` verb; no cognitive candidate selects a Bundle | `demo_sessions.py` parses the closed grammar, then `RunObservationStore.inspect()` validates the id and reads the retained observation | non-bypassable | One argument form is rejected; accepted input can only select one observation and cannot become a lifecycle action | One canonical grammar aligns renderer, parser, help, and documents without an alias parser | Harness-root subprocess proves grammar/output/exit; a focused store spy proves only `inspect()` is called |
| Inspection availability projection | No participant can declare an observation available or infer a recovery | `RunObservationInspection` from `RunObservationStore.inspect()` owns availability and safe facts; the command maps it to exit zero or bounded nonzero | non-bypassable | Unavailable observation exposes no resume, retry, provider, graph, or control path | Reuses the existing typed inspection result rather than adding a session broker or second controller | Focused dispatch tests prove inspect-only authority; the child process proves safe output and exit disposition |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| The rendered inspection command is malformed or uses the retired one-argument form | `demo_sessions.py` parser owns command-shape admission | No retry or alias fallback; argparse rejects before observation access | Bounded nonzero command usage failure | Use the documented `inspect <bundle-id>` grammar or request `--help` | Subprocess test proves the canonical command succeeds and retired spelling is rejected |
| The requested observation is invalid, missing, unavailable, or corrupt | `RunObservationStore.inspect()` returns the typed `RunObservationInspection` fact | No inspection command recovery, provider call, graph start, or lifecycle operation | Bounded unavailable observation with nonzero exit | Use only a currently returned lifecycle action for a distinct Run; inspection itself cannot resume or repair | Store-backed focused tests prove inspect-only dispatch; child process proves safe bounded output and disposition |
