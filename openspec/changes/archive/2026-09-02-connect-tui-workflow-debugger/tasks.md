## 1. Baseline

- [x] 1.1 Register RED-013/RED-014 in the requirement registry and run the plan gate (exit 0).

## 2. Launcher And Workbench Wiring

- [x] 2.1 Add executable `run/tui-workflow-debugger.sh` (root resolution from
  any cwd; no-arg chooser; --fixture/--embedded/--attach/--replay/--help;
  unknown flags exit non-zero; zero scan/lifecycle logic) and a `make
  tui-debugger` alias.
- [x] 2.2 Wire the workbench three entries (New Run/Attach/Replay) through the
  C4a driver and lifecycle candidates with button/slash normalization.
- [x] 2.3 Wire the Node Context pane to the C3 context/source inspectors and
  the Files pane to OperatorWorkspaceReader typed pages.

## 3. Entry Tests And Pilot Journeys

- [x] 3.1 Entry tests: launcher from any cwd, each flag, help text, unknown
  flag failure, target script executable, zero workspace scan.
- [x] 3.2 Pilot journeys: three entries equivalence, Start Step/Run, HITL
  answer, detach, 80x24/120x40/160x50 sizes.

## 4. Closeout

- [x] 4.1 Scope proof; `UV_OFFLINE=1 make verify` exit 0; strict + hygiene +
  closeout gates.
- [x] 4.2 Sync delta into `research-demo-tui` (+ header/registry), archive,
  update plan ladder/§L; sync README/COMMANDS.
