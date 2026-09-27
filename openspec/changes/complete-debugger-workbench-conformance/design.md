# Design

## Context

RED-013/RED-014 own the surface; the driver, lifecycle, lease, and workspace
reader already exist. The workbench is a Textual app in `scripts/demo_tui.py`
whose `mode` (and therefore its adapter, transport, and experience) is fixed at
construction, and a launcher script that forwards flags to it. There is no
lifecycle-level "list retained bundles" API: the existing operator inventory is
a script that reads the local demo workspace and is explicitly "not a lifecycle
authority".

## Goals / Non-Goals

**Goals:**

- The documented entry and panes exist and are asserted headlessly.
- Every new surface reuses an existing owning contract; no second authority is
  created and no "latest bundle" is silently selected.

**Non-Goals:**

- No runtime/lifecycle API additions, no spec wording changes, no embedded or
  real-graph debug driving.

## Decisions

1. **The composition chooser lives in the launcher, not in the TUI.** Rationale:
   `DeepResearchDemoTUI.__init__` builds its adapter/transport/experience for a
   fixed mode, so an in-TUI chooser would have to tear that down and rebuild
   mid-session — a re-init surface with real failure modes for no added value.
   The launcher already owns flag forwarding. Interactive stdin (`[ -t 0 ]`)
   gets a prompt; non-interactive stdin takes the documented default (fixture
   debugger) so agents and CI stay deterministic; `DEBUGGER_COMPOSITION` names
   the choice explicitly for scripts (and gives the regression test a seam).
2. **The Node Context pane derives its strip from `NodeContextView`, never from
   re-derived facts.** The view already carries `coverage_initial_context`,
   `coverage_runtime_posture`, `coverage_inner_activity`, `coverage_outcome`,
   `coverage_files`, and `raw_provider_history`; the pane renders exactly those
   labels so a coverage claim cannot drift from the store.
3. **Attach candidates are a bounded operator view, then lifecycle-validated.**
   The candidate list is read from the adapter's own demo workspace (bounded to
   the five most recent records), presented explicitly with each bundle id and
   its lease posture (live+other owner → busy/read-only; free → takeover), and
   every selection is resolved through the lifecycle before use. The list never
   auto-selects "the latest" - the operator picks. Alternatives: adding a
   lifecycle listing API (rejected: new contract surface for a display need), or
   keeping the single-id form only (rejected: RED-014 asks for candidates).
4. **Palette entries are the same typed methods as buttons and slash commands.**
   A Textual `COMMANDS` provider dispatches `_debug_new_run` / `_debug_attach` /
   `_debug_replay`; id-carrying actions read the composer draft exactly like the
   buttons, so all three paths converge on one implementation.
5. **The Files pane consumes `OperatorWorkspaceReader` pages.** No host path is
   rendered; the pane lists the reader's typed pages and renders the selected
   page's bounded content.

## Risks / Trade-offs

- [A bounded workspace listing in the TUI could look like the forbidden scan] →
  it is explicit, bounded, displayed, and never auto-selected; the pane label
  says "operator view, not a lifecycle authority", and the harness asserts that
  a candidate is only used after lifecycle resolution.
- [Textual pane layout churn could break existing widget queries] → the journey
  harness and the existing TUI integration tests query the affected widgets;
  both run in `make verify`.
- [Chooser prompts could hang a non-interactive caller] → prompting is gated on
  `[ -t 0 ]`; non-tty always takes the default without reading stdin.
