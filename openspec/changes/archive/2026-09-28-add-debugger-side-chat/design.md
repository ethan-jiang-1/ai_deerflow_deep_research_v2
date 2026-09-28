# Design

## Context

The workbench's composer is overloaded by design: at a HITL stop, an unprefixed line
IS the formal answer, and that contract is what keeps step/replay semantics
trustworthy. The operator's live feedback shows the cost: casual conversation gets
consumed as an answer, burns a bounded revision round, and comes back as the graph's
repair ask — with real model latency on every round. The 020 recon chat already
implements free conversation (chat model + read-only workspace tools) for the plain
TUI; the workbench simply never routed to it.

## Goals / Non-Goals

**Goals:**

- `?`/`？`-prefixed composer lines converse with the operator's chat model at any
  workbench posture, including HITL stops and mid-drive.
- The formal answer channel is untouched: unprefixed lines at a HITL stop remain the
  answer; a chat turn never consumes a revision round or changes graph state.
- Debug-mode rendering keeps the posture pane authoritative: chat lands in the log
  (echo + final answer), with no partial streaming into `#inspect`.

**Non-Goals:**

- No persistent chat panel, no streaming into the posture pane.
- No change to the 020 recon chat or non-debug compositions.
- No HITL-node changes — the graph's answer processing stays exactly as it is, and
  the chat model never gains graph authority.
- Nothing under `deerflow/`; no driver or lifecycle changes.

## Decisions

1. **`?`/`？` prefix, routed before the debug echo/answer routing.** Rationale: the
   escape must be reachable exactly at the postures where the answer channel is
   armed (HITL stops), and it must win over the answer interpretation. Full-width
   `？` is included because Chinese sentences start with it naturally. Rationale for
   not auto-detecting "chat vs answer" with a model: the answer channel must stay
   deterministic — an LLM classifier in the path would make step/replay semantics
   uncertain and burn latency on every answer.
2. **Reuse the recon chat machinery wholesale.** Rationale: `_chat_reply` already
   resolves the credential-backed model (BUG-075's loader makes it visible), binds
   the three read-only workspace tools, keeps bounded history, and fails honestly.
   The workbench chat is the same operator-side conversation — same model, same
   tools, same authority (none over the graph).
3. **Log-only rendering in debug mode; partials suppressed.** Rationale: the
   `#inspect` pane is owned by the debug posture line (an earlier repair), so chat
   partials must not stream there; the final answer line lands in the log next to
   the `你:` echo. Non-debug rendering is unchanged.
4. **Escape-style routing symmetric with `!`.** Rationale: the shell escape
   established the pattern — a prefix that means "this line is for the operator's
   own tools, not for the graph". `!` = machine, `?` = model; everything unprefixed
   remains graph channel.

## Risks / Trade-offs

- [A real answer that begins with `?`/`？` is misread as chat] → a leading space
  submits the line verbatim; documented in `/help`. HITL answers that genuinely start
  with a question mark are rare, and the failed-answer repair loop would surface it.
- [The chat model call fails (no credentials, provider error)] → `_chat_reply`
  already fails honestly in the log with the exception detail (the recon failure
  line); the pending HITL request is untouched either way.
- [Chat during an active drive] → the chat worker is exclusive to the debug group,
  so it queues behind a running drive; the answer channel is unaffected.
