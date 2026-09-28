# Tasks

## 1. Red-first regression tests

- [x] 1.1 Add unit tests (`tests/unit/test_demo_tui_shell_escape.py`) pinning the capture helper contract: cwd anchoring (`pwd` equals the given directory), nonzero exit reported, stderr captured, runtime bound with termination (`sleep 5` at a 1s bound), output truncation with an explicit note, and non-interactive stdin (`cat` hits EOF immediately). Verify: run `cd deep_research_harness && .venv/bin/python -m pytest tests/unit/test_demo_tui_shell_escape.py -q`; red first via ImportError on the not-yet-written `_capture_shell_output`. ✓ 6/6 red with ImportError
- [x] 1.2 Add a run_test probe (`tests/integration/test_debugger_entry.py`) that mounts the embedded debugger, submits `!echo marker-shell-escape` from the composer, and asserts the marker appears as a standalone log output line (the plain input echo does not count). Verify: red first — the line is consumed as a debug start instead of the escape. ✓ Red in 10.3s (misroute into `_debug_start`)

## 2. Implementation

- [x] 2.1 Add module-level `_capture_shell_output(command, cwd, *, timeout_s=15, max_chars=4000)` in `scripts/demo_tui.py`: `subprocess.run` with `shell=True`, `executable="/bin/bash"`, `stdin=DEVNULL`, timeout termination, stderr section, exit-code suffix when nonzero, truncation note. Verify: task 1.1 turns green. ✓
- [x] 2.2 Route `!`-prefixed composer input in debug mode to a new `_shell_escape` worker method before answer/debug routing; anchor cwd to the live session's Bundle directory (else the workspace bundle root); render output in the log labelled with the command and cwd. Verify: task 1.2 turns green. ✓
- [x] 2.3 List the capability in `/help` and the workbench hint line. Verify: `_debug_help` output names the escape; hint line stays within the small-terminal budget. ✓ Both updated; journey ladder 16 checkpoints green

## 3. Gates

- [x] 3.1 From `deep_research_harness/`, independently run `UV_OFFLINE=1 make verify`, `make tui-journey`, and `make debugger-proof`; from the repository root, run `python3 openspec/governance/check_project_gate.py --phase closeout`, `openspec validate add-debugger-shell-escape --strict`, `python3 openspec/governance/check_doc_hygiene.py`, and `git diff HEAD --check`. Measure every exit code directly (no `| tail` pipelines). Record the gitlink checks and confirm `openspec --version` equals the `generatedBy` frontmatter (read-only; `.agents/skills/` is a user-reserved area). Verify: every measured exit code is 0. ✓ verify 0 (2747 fast + 357 integration/4 pre-existing skips + 35 workflow), journey 0, debugger-proof 0 (all five lanes), closeout 0, strict 0, hygiene 0, diff-check 0, gitlink ceebf97f unchanged, openspec 1.13.1 aligned
