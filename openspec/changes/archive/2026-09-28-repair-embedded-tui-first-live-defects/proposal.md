# Proposal

## Why

The first live window of the embedded real TUI (runbook-031's debugger over ALL_REAL)
exposed two defects that every headless test missed, because no live-model session had
ever been driven through these paths. First, the recon chat died with an opaque
`（侦察对话调用失败: ValidationError）` on its first tool-calling turn: DeepSeek streams
an empty trailing tool_call delta (`name: ""`, `id: None`) on the same index after the
real call, `_stream_turn`'s accumulate-by-index logic let it clobber the accumulated
call, and `ToolMessage(tool_call_id=call.get("id", ""))` then received `None` (the key
exists, so the default never applied) — a pydantic ValidationError, reproduced
headlessly with a full traceback against the real provider shape. Second, the debugger
composition never reached its own workbench: `_initialize` renders the no-debug-session
first screen, but the following unguarded `elif self.mode == "embedded_smoke":` branch
clobbered it with the 020 recon screen and set `_onboarding = True`, routing composer
input into the recon chat instead of the debug driver — so the launcher's promised
workbench (`--embedded-smoke` + injected `--debug`, runbook-031) was unreachable from
the keyboard.

## What Changes

- `scripts/demo_tui.py` extracts the recon streaming loop into a module-level
  `_stream_chat_turn(model, messages, tools, *, on_text)`; `_stream_turn` delegates.
  Inside the loop, a tool_call delta with neither a name nor an id is skipped instead
  of clobbering the accumulated call, and `tool_call_id` degrades to `""` when `None`.
- The recon chat failure line now includes the exception detail (first line, bounded),
  so the next failure is diagnosable from the screen instead of type-name-only.
- `_initialize`'s 020 recon branch is guarded with `not self.debug_mode`: with
  `--debug` the workbench first screen stands, `_onboarding` stays False, and composer
  Enter routes to `_debug_start` exactly as the fixture workbench already behaves.
- Regression coverage: a scripted-model unit test (no network) replays the exact live
  chunk shape — real call delta plus empty tail — and asserts the tool executes once,
  the ToolMessage carries the real id, and the second round answers; a subprocess probe
  asserts `mode="embedded_smoke", debug_mode=True` mounts the workbench (`_onboarding`
  False, recon placeholder absent). Both red before the fix.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- None. No requirement text changes: runbook-031 already promises the embedded
  workbench, and the recon chat is 020-surface behavior under the existing demo specs;
  this change repairs implementation conformance with what the docs already promise.

## Impact

- Primary implementation: `deep_research_harness/scripts/demo_tui.py`.
- Tests: `deep_research_harness/tests/unit/test_demo_tui_recon_stream.py` (new),
  `deep_research_harness/tests/integration/test_debugger_entry.py`.
- Docs: none — the launcher help and runbook-031 already document the behavior this
  change makes true.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/` gitlink;
  this change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/demo_tui.py` — the
  recon streaming loop (presentation-side tool-call accumulation) and the embedded
  mount router (which screen owns the first contact).
- **Seam classification:** wiring and presentation — no lifecycle, admission, route, or
  node-agent behavior change; the debug driver, runtime, and graph are untouched.
- **Question:** How does the embedded real TUI survive its first live window — recon
  chat tool-calling turns completing, and the debugger composition landing on its own
  workbench — without widening any authority?
- **Necessary adjacent/external contracts:** the provider's streaming chunk shape is an
  external fact (observed live, replayed verbatim in the unit test);
  `run/tui-workflow-debugger.sh`'s `--debug` injection and `research-demo-tui`'s
  launcher requirement own the entry; BUG-075's `load_local_environment` owns how the
  env reaches these paths; BUG-076 and BUG-077 own the ledger records.
- **Evidence seam:** scripted-model unit test at the extracted seam (red with the real
  ValidationError, green after), file-mode subprocess probe for the mount (red with
  `ONBOARDING: True` + recon placeholder, green after), then `UV_OFFLINE=1 make
  verify`, `make tui-journey`, `make debugger-proof`, and the governance gates.
- **Not in scope:** the debug driver's driving semantics, recon tool surface changes,
  live credential validation (needs the operator's live window), any spec delta, and
  anything under `deerflow/`.
- **Triggered review policies:** none: presentation repair with no candidate, human judgment, control fact, admission/recovery boundary, node-agent role, or lifecycle output change.
