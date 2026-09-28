# Design

## Context

The embedded real TUI met its first live model today (BUG-075's fix let the launcher
reach preflight-green). Two defects surfaced immediately. The recon chat's first
tool-calling turn failed with `ValidationError` — and the screen showed only the
exception type name, because the handler prints `type(exc).__name__` and swallows the
message. A headless replay against the real provider produced the full traceback:
DeepSeek's streaming response ends the tool call with an empty delta
(`{name: "", args: {}, id: None, type: "tool_call", index: 0}`) after the real
`{name: "list_workspace", args: {}, id: "call_00_…"}`; accumulate-by-index keeps only
the last, and `call.get("id", "")` returns `None` (the key exists with a None value),
which `ToolMessage` rejects. Separately, the operator who launched the debugger
composition never saw it: `_initialize` renders the no-debug-session screen, then the
unguarded `elif self.mode == "embedded_smoke":` branch overwrote it with the 020 recon
screen and set `_onboarding = True`, so composer Enter went to the recon chat. Fixture
debug never hit this because fixture mode does not enter that elif branch.

## Goals / Non-Goals

**Goals:**

- Recon chat completes tool-calling turns against the real provider's streaming shape.
- The debugger composition (`--embedded-smoke` with injected `--debug`) lands on its
  own workbench first screen, with composer Enter starting a debug session.
- Failures stop being opaque: the recon failure line carries the exception detail.
- Both defects regression-locked red-first without any live network in tests.

**Non-Goals:**

- No change to the debug driver, runtime, graph, or admission semantics.
- No recon tool surface change (the three read-only tools stay as they are).
- No spec deltas and no launcher changes; no changes under `deerflow/`.

## Decisions

1. **Extract the streaming loop into module-level `_stream_chat_turn(model, messages,
   tools, *, on_text)`.** Rationale: the bug lives in the loop's accumulation logic,
   which was inline inside a Textual method and only testable through a live model.
   A module-level helper takes a scripted model (deterministic, no network) and
   `_stream_turn` delegates with a render callback — behavior shared by construction,
   and the unit test replays the exact observed chunk sequence. Alternative — testing
   `_chat_reply` through a running app with the real key — rejected: non-deterministic,
   costs the operator's quota, and cannot run on CI.
2. **Skip tool_call deltas that have neither a name nor an id.** Rationale: such a
   delta carries no information (it is the provider's terminator for the streamed
   call); clobbering the accumulated call with it lost the real name and id. Merging
   args incrementally was considered and rejected: no observed provider shape needs
   it, and the minimal rule keeps the loop's contract narrow.
3. **`tool_call_id=call.get("id") or ""`.** Rationale: `dict.get(key, default)` does
   not protect against an explicit `None` value — the actual trap. The `or` form
   degrades honestly; the model then sees a valid ToolMessage and can answer.
4. **Guard the 020 recon branch with `not self.debug_mode`.** Rationale: the branch
   above already renders the workbench first screen for every debug composition;
   clobbering it (and setting `_onboarding`, which reroutes composer Enter) is what
   made the embedded debugger unreachable from the keyboard. The auto branch keeps
   its own guard (`self.auto` implies the 010 scripted run, never debug). Alternative
   — moving the recon branch before the debug branches — rejected: it would leave
   `_onboarding = True` for debug sessions and reintroduce the composer misroute.

## Risks / Trade-offs

- [The scripted unit test could drift from the real provider shape] → the chunk
  sequence in the test is transcribed from the live traceback captured today
  (BUG-076 card records it); if the provider changes again, the failure line now
  shows the exception detail instead of a bare type name.
- [Recon behavior changes for debug sessions] → with `--debug`, composer Enter now
  starts a debug session instead of chatting; that is the documented contract
  (launcher help + runbook-030/031), and the plain 020 TUI (no `--debug`) is
  unchanged — the full deterministic gate and both TUI journey suites prove it.
- [Extraction moves shared behavior] → `_stream_turn` had exactly one caller (the
  recon chat); delegation keeps the render side effect identical, and the full gate
  covers the research-path streams untouched by this change.
