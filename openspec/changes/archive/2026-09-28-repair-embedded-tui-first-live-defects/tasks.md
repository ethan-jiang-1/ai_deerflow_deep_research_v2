# Tasks

## 1. Red-first regression tests

- [x] 1.1 Add a scripted-model unit test (`tests/unit/test_demo_tui_recon_stream.py`) that replays the live DeepSeek chunk shape — real tool_call delta `{name: "list_workspace", id: "call_00_…"}` followed by the empty trailing delta `{name: "", id: None}` on the same index — and asserts the tool executes once, the fed-back ToolMessage carries the real id, and the second round's answer is returned. Verify: run `cd deep_research_harness && .venv/bin/python -m pytest tests/unit/test_demo_tui_recon_stream.py -q`; red first via ImportError on the not-yet-extracted `_stream_chat_turn`, and the same test against the pre-fix inline logic reproduces the operator's pydantic `ValidationError` (captured headlessly against the real provider before this change). ✓
- [x] 1.2 Add a subprocess probe (`tests/integration/test_debugger_entry.py`) that mounts `DeepResearchDemoTUI(mode="embedded_smoke", debug_mode=True)` and asserts the workbench first screen stands (`_onboarding` False, recon placeholder absent). Verify: red first — `ONBOARDING: True` with the recon placeholder `随便聊，或说「开始 Deep Research」`. ✓

## 2. Repair

- [x] 2.1 Extract the recon streaming loop into module-level `_stream_chat_turn(model, messages, tools, *, on_text)`; inside it, skip tool_call deltas with neither a name nor an id, and degrade a `None` tool_call_id to `""`. Verify: task 1.1's tests turn green. ✓ 2/2 green
- [x] 2.2 Make `_stream_turn` delegate to `_stream_chat_turn` with a render callback, and make the recon failure line include the exception's first message line (bounded) instead of the bare type name. Verify: task 1.1 stays green; the failure-line change is covered by the same unit seam (the helper propagates real errors). ✓
- [x] 2.3 Guard `_initialize`'s 020 recon branch with `not self.debug_mode` so the debugger composition keeps its workbench first screen and composer routing. Verify: task 1.2's probe turns green. ✓ `ONBOARDING: False`, recon placeholder gone

## 3. Gates

- [x] 3.1 From `deep_research_harness/`, independently run `UV_OFFLINE=1 make verify`, `make tui-journey`, and `make debugger-proof`; from the repository root, run `python3 openspec/governance/check_project_gate.py --phase closeout`, `openspec validate repair-embedded-tui-first-live-defects --strict`, `python3 openspec/governance/check_doc_hygiene.py`, and `git diff HEAD --check`. Measure every exit code directly (no `| tail` pipelines). Record the gitlink checks and confirm `openspec --version` equals the `generatedBy` frontmatter (read-only; `.agents/skills/` is a user-reserved area). Verify: every measured exit code is 0. ✓ verify 0 (2741 fast + 356 integration/4 pre-existing skips + 35 workflow), journey 0, debugger-proof 0 (all five lanes), closeout 0, strict 0, hygiene 0, diff-check 0, gitlink ceebf97f unchanged, openspec 1.13.1 aligned
