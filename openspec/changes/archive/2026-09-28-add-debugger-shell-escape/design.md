# Design

## Context

The operator's live-window feedback: at a paused boundary the filesystem is the thing
you want to look at (what did the run write; what does the journal say), and the typed
panes — deliberately bounded — do not answer arbitrary questions. The debugger is D8's
local operator tool: it runs on the operator's machine, inside the operator's
terminal, with the operator's own privileges. A `!`-style shell escape (the classic
TUI convention) therefore adds flexibility without adding authority; the workbench's
real contribution is knowing WHERE to anchor (the live session's Bundle directory)
and keeping the operator in the flow with bounded, labelled output.

The authority line stays exactly where the repo's design reviews drew it: model-facing
tool authority is admission-controlled and untouched — the escape is the human
operator's own machine power, never graph authority.

## Goals / Non-Goals

**Goals:**

- `!<command>` from the composer runs at any posture (including HITL stops), without
  being consumed as a research answer or a debug command.
- Bounded by construction: non-interactive stdin, runtime bound with termination,
  output size cap with an explicit truncation note, exit code reported.
- cwd anchoring: live session's Bundle directory → workspace bundle root → process
  cwd, so plain `ls`/`cat` answer the operator's actual question.
- Honest rendering: verbatim output in the log, labelled operator-invoked with the
  command and cwd; `/help` and the hint line list the capability.

**Non-Goals:**

- No persistent interactive shell, no output streaming, no TTY allocation.
- No graph/model tool authority change (admission-owned; the escape is never exposed
  to nodes or agents).
- No change to the typed pane contracts (output renders in the log); no change to the
  020 recon chat; nothing under `deerflow/`.

## Decisions

1. **`!` prefix in the composer, routed before answer/debug routing.** Rationale: at
   a HITL stop every keystroke line is otherwise consumed as the formal answer; the
   escape must be reachable exactly when the operator is paused. The prefix is the
   established TUI convention; answers that genuinely begin with `!` can be typed
   with a leading space. Rationale for debug-only scope: the 020 recon chat already
   has its own (model-bound, read-only) inspection tools, and the operator asked for
   the debugger surface.
2. **One-shot bounded capture, not a persistent shell.** Rationale: a persistent
   shell inside Textual needs a PTY, breaks the log's rendering contract, and adds
   state the workbench would have to own; a one-shot `subprocess.run` with
   `stdin=DEVNULL`, a runtime bound, and a size cap gives the flexibility (`pipes`,
   `redirects`, `jq`, `head`) with none of the ownership. Each escape is fresh —
   `cd` does not persist, and the rendered cwd line tells the operator where they
   are.
3. **Render into the log, labelled — not into a typed pane.** Rationale: RED-014's
   pane contracts (typed pages, no host paths) stay pure; the log is already the
   rolling surface for operator-visible narration and already shows the bundle root.
   The label `[cwd: …]` plus the `!` prefix mark the content as operator-invoked, so
   no one can mistake it for graph state.
4. **Pure helper `_capture_shell_output(command, cwd, *, timeout_s, max_chars)`.**
   Rationale: bounds become testable deterministically (`pwd` anchoring, `false`
   exit code, stderr capture, `sleep` timeout, `yes | head` truncation, `cat` stdin
   EOF) without any TUI or network; the app method only resolves the cwd anchor and
   renders.

## Risks / Trade-offs

- [The escape runs with full operator privileges, including secrets in the process
  environment] → true of the operator's own terminal too; the escape adds no
  privilege. The workbench renders output verbatim — an operator who prints their own
  key has exercised their own machine, not widened the graph's authority. Stated in
  the requirement rather than pretended away.
- [`cd` does not persist between escapes] → each escape states its cwd; operators
  chain with `cd x && ls`. Persistent state would reintroduce shell ownership.
- [A long-running command blocks one work group] → runtime bound (15s default)
  terminates it, and the worker is exclusive to the debug group only; the UI stays
  responsive and the timeout is reported.
- [Answers that begin with `!` can no longer be typed literally] → a leading space
  submits the line verbatim; documented in `/help`.
