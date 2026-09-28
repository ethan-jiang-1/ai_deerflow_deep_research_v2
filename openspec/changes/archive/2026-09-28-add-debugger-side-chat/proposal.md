# Proposal

## Why

The operator's live-window follow-up to the shell escape: with the workbench now
inspectable (`!` shell, typed panes), the remaining flexibility gap is conversation.
At a HITL stop every composer line is consumed as the formal answer, so a casual
question ("这个 profile 是什么意思？") burns a HITL revision round and gets answered
by the graph's bounded repair loop instead of a conversation. The operator's
direction: the debugger should support normal natural-language conversation too —
without corrupting the answer channel. The recon chat (020 surface) already has the
exact machinery: a credential-backed chat model bound to read-only workspace tools.
This change routes it into the workbench as a side channel.

## What Changes

- The workbench composer gains a side-chat escape: input prefixed with `?` (or the
  full-width `？`) runs as one conversational turn with the operator's chat model
  (the same bounded recon chat: model + read-only workspace tools), at any posture,
  without consuming a pending HITL request, without starting a run, and without
  changing any graph state.
- In debug mode the chat renders to the log only (final answer line); the `#inspect`
  pane stays owned by the debug posture line, and no partial streaming clobbers it.
- The formal HITL answer channel is unchanged: unprefixed lines at a HITL stop remain
  the answer; `?`-prefixed lines never consume a revision round.
- `/help` and the hint line list the capability.
- Spec delta under `research-demo-tui` (ADDED requirement): a new operator-side
  surface on the workbench.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- None. A new requirement is ADDED under the existing `research-demo-tui` capability
  (operator side-chat at the workbench); RED-013/RED-014 texts are unchanged.

## Impact

- Primary implementation: `deep_research_harness/scripts/demo_tui.py`.
- Tests: `deep_research_harness/tests/integration/test_debugger_entry.py`.
- Docs: in-app `/help` and the workbench hint line; no runbook rewrite.
- Ordinary downstream work neither modifies nor source-browses the `deerflow/`
  gitlink; this change owns no such boundary.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/scripts/demo_tui.py` —
  the workbench input router and the existing `_chat_reply` surface's render target;
  the driver, lifecycle, and graph are untouched.
- **Seam classification:** presentation — an operator-side conversation channel with
  an explicit authority statement (the chat model is the operator's own conversational
  model; it holds no graph authority and its output is operator-invoked content).
- **Question:** How does the operator converse naturally at any paused boundary
  without the conversation consuming a HITL round or being mistaken for an answer?
- **Necessary adjacent/external contracts:** the recon chat machinery (`_chat_reply`,
  `_build_chat_model`, `_stream_chat_turn`, `_recon_tools`) owns the conversational
  model and its read-only tools; BUG-075 owns credential visibility; the shell-escape
  change owns the escape-prefix routing pattern (`!`), and `research-demo-tui` owns
  the workbench surface the delta extends; the HITL answer channel is owned by the
  debug-driving spec and stays untouched.
- **Evidence seam:** a run_test probe asserting a `?`-prefixed composer line reaches
  the chat path (the operator turn is recorded in `_chat_history`) without being
  consumed as a debug start — red-first via misroute; then the standard gate ladder.
- **Not in scope:** a persistent chat panel, chat output streaming into the posture
  pane, non-debug compositions (020 recon chat is unchanged), making HITL nodes
  chat-aware (graph authority stays with the graph), and anything under `deerflow/`.
- **Triggered review policies:** none: presentation surface addition with no candidate, human judgment, control fact, admission/recovery boundary, node-agent role, or lifecycle output change.
