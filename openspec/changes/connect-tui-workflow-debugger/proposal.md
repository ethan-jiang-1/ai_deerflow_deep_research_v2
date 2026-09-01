## Why

C4a delivered the headless `DebugRunDriver` and C3 the observation surface, but
there is no canonical human entry: an operator must hand-run Python scripts to
reach the debugger workbench. The progressive plan gate (C4b) requires a
repo-owned executable launcher, a first screen with three explicit entries
(New Run / Attach / Replay), composer typed routing that can never be silently
reinterpreted, a Node Context view over the C3 capture surface, and
README/COMMANDS sync — all as a pure presentation adapter with zero new
runtime semantics.

## What Changes

- Add the executable `run/tui-workflow-debugger.sh` canonical entry: resolves
  the harness root from any cwd, no dependency sync/install, no Bundle
  discovery/lifecycle logic; no-arg opens the TUI composition chooser;
  `--fixture`/`--embedded` select the composition; `--attach <bundle_id>`/
  `--replay <bundle_id>` carry explicit intent; `--help` lists equivalent
  Make commands. Explicit Bundle intent is still validated by the TUI/lifecycle.
- Wire the workbench first screen to three explicit entries backed by the
  C4a driver and C3 observation interfaces; New Run consumes the validated
  question draft only; Attach lists lifecycle-verified candidates with
  busy/read-only versus takeover postures; Replay is read-only.
- Wire the Node Context pane to the C3 context/source inspectors and the Files
  pane to `OperatorWorkspaceReader`; all panes consume typed views only.
- Keep slash syntax and button/palette actions normalized to the same typed
  actions at the adapter boundary.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `research-demo-tui`: new RED-013 (canonical launcher entry with fixture/
  embedded/attach/replay intents and zero workspace scan) and RED-014
  (workbench three entries + Node Context pane over the C3 typed views).

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/demo_tui.py`
  owns presentation wiring; the launcher is `deep_research_harness/run/tui-workflow-debugger.sh`; `runtime/debug_driver.py` and the C3 inspectors are consumed as delivered.
- **Seam classification:** wiring; zero runtime/contract change beyond two new
  presentation requirements.
- **Question:** how does an operator reach the debugger workbench canonically
  while every pane stays a thin typed adapter?
- **Necessary adjacent/external contracts:** LDD-001..005 (driver surface consumed as-is), LDO-001..008 (observation surface consumed as-is), RED-003/RED-009/RED-011/RED-012 (existing adapter authority).
- **Evidence seam:** entry tests (launcher from any cwd, flags, help, zero
  scan) + Textual Pilot journeys (three entries, Start Step/Run, HITL answer,
  detach) + three terminal sizes.
- **Not in scope:** new runtime semantics, remote driving, checkpoint editing,
  State mutation, `deerflow/`.
- **Triggered review policies:** local-context, change-admission, authority-and-projections

## Control Placement Review

| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
| How an operator enters the debugger | operator picks fixture/embedded/attach/replay | launcher flag parsing + typed adapter actions | human-decision inputs, deterministic normalization | no workspace scan, no latest claiming, lifecycle validates intent | retires ad-hoc Python-script entry | entry tests |

## Workflow Outcome Review

| Failure class | Fact owner | Recovery owner and bound | Terminal disposition | Legal next action | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- |
| Launcher invoked with unknown flag | flag parser | typed usage error, exit non-zero | no TUI started | re-run with documented flags | entry tests |

## Impact

- Apply adds the launcher, a Make alias, entry tests, demo_tui workbench
  wiring (three entries + Node Context pane), README/COMMANDS sync, and two
  new requirement IDs (RED-013/RED-014). No runtime change.
