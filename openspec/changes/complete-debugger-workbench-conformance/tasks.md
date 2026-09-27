# Tasks

## 1. Composition chooser (RED-013)

- [x] 1.1 Launcher: a bare invocation starts a composition chooser — interactive stdin prompts (fixture debugger / embedded smoke / gateway profile), non-interactive stdin takes the documented default (fixture debugger) without reading stdin, and `DEBUGGER_COMPOSITION` selects non-interactively. Verify: a launcher test through the `DEBUGGER_PYTHON` argv seam asserts the forwarded flags for the default, for `DEBUGGER_COMPOSITION=embedded-smoke`, and for `DEBUGGER_COMPOSITION=gateway`; `bash -n` stays clean. ✓ `test_launcher_chooses_a_composition_when_started_bare` green (red first); gateway without profile exits 2 with guidance
- [x] 1.2 Launcher help documents the chooser and the env seam; the bare-invocation line returns to the usage block. Verify: the `--help` entry tests still pass and assert the chooser line. ✓ help rewritten (chooser + DEBUGGER_COMPOSITION/DEBUGGER_PROFILE); entry tests green

## 2. Node Context pane (RED-014)

- [x] 2.1 Add a dedicated `#node-context` pane (replacing the log dump) rendered from `NodeContextView`, including the fixed coverage strip labels derived from the view's own fields. Verify: a red-first journey assertion checks the pane exists and that opening `/context` fills it with the strip labels for a captured invocation, and states the honest empty coverage when nothing was captured. ✓ strip pinned by `test_node_context_strip_projects_the_fixed_coverage_labels` (CAPTURED/ENFORCED/BOUNDED/OBSERVED-UNAVAILABLE/CURRENT/NOT RETAINED); fixture mode asserts the honest empty state
- [x] 2.2 Keep `/context` as the command that refreshes the pane, and keep the log free of the context dump. Verify: the journey asserts the pane text, not the log text (replace the current step-10 assertion). ✓ step [10] asserts the pane and that the log carries no context dump

## 3. Attach candidates and postures (RED-014)

- [x] 3.1 Present a bounded operator-view candidate list (max five, deterministic order, each with its bundle id and lifecycle-derived posture) and validate the selected candidate through the lifecycle before opening the session; never auto-select. Verify: journey assertions cover (a) a free candidate shown as takeover/available, (b) a live-foreign candidate shown as busy/read-only, (c) an unknown id still denied with a closed reason. ✓ driver postures pinned by test_attach_posture_reports_takeover_rebind_busy_and_unresolvable; harness step [5c] asserts the bounded list shows the retained bundle as [takeover]

## 4. Command palette entries (RED-014)

- [x] 4.1 Register New Run / Attach / Replay as Textual command palette actions dispatching the same typed methods as the buttons and slash commands. Verify: a focused test invokes the provider's commands and asserts the same effect as the button path (session opened / attach attempted / replay rendered). ✓ `test_workbench_palette_actions_match_the_button_path` drives ctrl+p, types the action and asserts the session opens with the Start Step line

## 5. Files pane (RED-014)

- [x] 5.1 Add a Files pane that consumes `OperatorWorkspaceReader` typed pages (bounded listing + selected page content), rendering no host paths. Verify: journey assertions check the pane exists, lists at least one typed page after a session, and never contains an absolute host path. ✓ harness step [10b] green; while wiring it, the step caught a real reader defect (an unresolved trusted root raised ValueError instead of a typed page on symlinked paths) fixed in workspace_reader with a symlinked-root regression test

## 6. Gates

- [ ] 6.1 From the repository root, run `python3 openspec/governance/check_project_gate.py --phase closeout`; from `deep_research_harness/`, independently run `UV_OFFLINE=1 make verify`; then, from the repository root, run `openspec validate complete-debugger-workbench-conformance --strict` and `git diff HEAD --check`. Measure every exit code directly (no `| tail` pipes). Record `git status --porcelain=v1 --untracked-files=all`, `git ls-files --stage deerflow`, `git submodule status -- deerflow`, and `git -C deerflow status --porcelain=v1 --untracked-files=all`, and review `git diff --submodule=short`. Also confirm generation alignment: `openspec --version` equals the `generatedBy` frontmatter in `.agents/skills/*/SKILL.md` (read-only; user-reserved area). Verify: every measured exit code is 0.
- [ ] 6.2 Close BUG-071 per the backlog ritual when every item above lands (move to `_done/_fixed_bugs/`, update both indexes and the `_done` count), and keep the deferred mechanism-level borrow items in `_backlog/todos/`.
