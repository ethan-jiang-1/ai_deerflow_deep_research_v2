# Tasks

## 1. Red-first regression test

- [x] 1.1 Add a run_test probe (`tests/integration/test_debugger_entry.py`) that mounts the embedded debugger, submits `?随便聊聊怎么样` from the composer, and asserts the operator turn reaches the chat path (recorded in `_chat_history`). Verify: red first — the line is consumed as a debug start instead (`CHAT_SEEN: False`). ✓ Red in 10.7s (misroute into `_debug_start`)

## 2. Implementation

- [x] 2.1 Route `?`/`？`-prefixed composer input in debug mode to `_chat_reply` before answer/debug routing (composer cleared, chat worker in the debug group). Verify: task 1.1 turns green. ✓ `CHAT_SEEN: True`, history records the operator turn
- [x] 2.2 In debug mode render the chat to the log only (echo + final answer line; no partial streaming into the posture pane). Verify: task 1.1 stays green; posture pane untouched by the chat path. ✓ Partials suppressed in debug mode; log-only rendering
- [x] 2.3 List the capability in `/help` and the workbench hint line. Verify: `_debug_help` output names the side chat; hint line stays within the small-terminal budget. ✓ Both updated; journey ladder 16 checkpoints green

## 3. Gates

- [x] 3.1 From `deep_research_harness/`, independently run `UV_OFFLINE=1 make verify`, `make tui-journey`, and `make debugger-proof`; from the repository root, run `python3 openspec/governance/check_project_gate.py --phase closeout`, `openspec validate add-debugger-side-chat --strict`, `python3 openspec/governance/check_doc_hygiene.py`, and `git diff HEAD --check`. Measure every exit code directly (no `| tail` pipelines). Record the gitlink checks and confirm `openspec --version` equals the `generatedBy` frontmatter (read-only; `.agents/skills/` is a user-reserved area). Verify: every measured exit code is 0. ✓ verify 0 (2747 fast + 358 integration/4 pre-existing skips + 35 workflow), journey 0, debugger-proof 0 (all five lanes), closeout 0, strict 0, hygiene 0, diff-check 0, gitlink ceebf97f unchanged, openspec 1.13.1 aligned
