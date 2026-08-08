## Context

The standalone real CLI is a thin presentation adapter over
`ResearchRunExperience`. Its typed `AnswerRun.value` becomes a correlated human-input
message, which the graph resumes into the real HITL1 node. The model is used only to
produce the initial advisory `StructuredBrief`; Python parses and materializes human
profile responses.

The captured run `r_SnrIKUGQhUwUIAWyht4dq_zJLGNftutorg24_bhX62E` demonstrated that this
boundary is technically controlled but not usable: the English-only parser converted
Chinese text into an empty partial profile, HITL1 consumed three empty rounds and
published a degraded empty profile, and later Wave0 failure was retained only as a
generic `research.blocked` fact. The current bundle is useful evidence but its inspect
view is an artifact list, not an operational diagnosis.

This is a downstream-only change. `agent/` retains exclusive ownership; `backend/` and
`frontend/` remain untouched. Existing GraphState, LangGraph interrupts, lifecycle
control result, broker authorization, and raw-diagnostic redaction boundaries remain
authoritative.

## Goals / Non-Goals

**Goals:**

- Make a HITL1 proposal an explicit, checkpointed advisory value that a correlated
  user action can accept deterministically.
- Support a closed, tested localized input vocabulary and structured JSON without
  delegating user-answer interpretation to an LLM.
- Make user-visible prompt state explain what was adopted, missing, rejected, and
  available, including `must_answer` and remaining answer budget.
- Make returned-only CLI state and terminal results operationally legible.
- Make retained run observations diagnosable through safe summary/event projections.
- Preserve no-secret/no-raw-exception/no-raw-message properties end to end.

**Non-Goals:**

- No Gateway, web UI, upstream terminal, API, or generic log aggregation work.
- No arbitrary natural-language understanding or provider-native structured-output
  migration.
- No cross-process continuation for a `same_process` demo run.
- No raw exception stack, prompt, response, model/tool body, URL query, credential, or
  host path in a retained bundle or presentation contract.
- No use of retained observation as graph-control authority.

## Decisions

### A checkpointed proposal is advisory state; explicit acceptance is a human response

Add bounded controller-owned `proposed_profile` state derived only from a validated
`StructuredBrief`. The first HITL1 visit writes it before issuing the interrupt; a
resume does not re-run the brief model call. The proposal carries only the same bounded
profile fields already validated by `StructuredBrief`, not model raw text.

Add `accept_suggestion` as a closed *action response* correlated with the current HITL1
request. `HumanInputRequest` gains a separate bounded `action_ids` field (rather than
overloading the existing HITL2-only typed `options`), while `AcceptedHumanResponse` and
`AnswerRun` gain a discriminated `response_kind=action` branch with an `action_id`.
The generic extractor accepts it only when the pending request advertises that exact
action, and HITL1 accepts it only when the checkpointed proposal is present and complete.
This keeps request correlation, replay protection, and broker revalidation at the
existing human-input seam instead of treating a magic text string as authority.
Presentation adapters render a visible acceptance option and may map the exact localized
phrase “采用建议” to this action before dispatch. Vague text such as “你来定义吧” remains
ordinary text and receives feedback rather than becoming implicit authority.

Alternative rejected: treat the original `StructuredBrief` as final profile directly.
That would violate the existing requirement that model output is advisory and remove a
human checkpoint from scope/cost control.

### Profile parsing remains deterministic and reports recognition separately

Refactor parser output into a frozen bounded result containing `partial`, recognized
field names, and an optional closed rejection category. JSON machine values remain the
most precise path. Free text uses token/phrase boundaries and a curated Chinese-plus-
English alias table per field. A phrase may not populate multiple fields; ambiguous
matches are rejected rather than guessed. `must_answer` has either a visible structured
field or a deterministic proposal/original-question default selected only by the
explicit acceptance flow.

If text produces zero recognized fields and no valid must-answer content, HITL1 keeps
the same request/pending authority and returns a feedback interrupt without incrementing
`profile_followup_round` or consuming response ids. A separate checkpointed
`profile_rejection_round` permits at most three consecutive rejections within the same
ongoing HITL1 intake; each feedback interrupt may receive a fresh request id while the
checkpointed proposal/progress and rejection counter remain correlated. The third records
the presentation category `profile_input_unrecognized`
with structured-input recovery guidance. A recognized response resets this separate
counter. Thus invalid input cannot silently degrade or create an unbounded invisible
loop. Feedback is an observation of parsing, not a new graph route determined by
presentation code.

Rejected responses must still advance the message-selection cursor. Add a bounded
controller-owned `profile_feedback_cursor_message_id`: after a zero-recognition response,
HITL1 records that message id solely as the next interrupt cursor while leaving
`consumed_request_ids`, `consumed_message_ids`, and accepted-answer rounds untouched.
The next descriptor starts after this rejected message and cannot replay it against a
fresh request id. A recognized response, acceptance, cancellation, or terminal result
clears the transient cursor. This deliberately separates *seen and rejected for cursor
progress* from *accepted and consumed for profile authority*.

Alternative rejected: add a few Chinese substrings to the old global synonym loop.
That leaves hidden requirements, ambiguous matches such as `standard depth`, and no
way to distinguish rejected input from an incomplete but accepted response.

### Prompt projection exposes bounded intake facts, not raw context

The versioned HITL1 context gains a safe proposal/progress payload. `ResearchRunExperience`
validates and translates it into `PromptView`: proposal availability, accepted machine
values, missing dimensions including `must_answer`, rejection category/message, remaining
accepted-answer and rejection-retry budgets, stable structured-input example, and the
advertised acceptance action. CLI and TUI consume only `PromptView`; neither parses
LangGraph payloads or derives state.

### Observability is based on committed facts and redacted event categories

`Working` gains only facts the runtime has observed: run reference, last committed
phase, elapsed time, and returned-only delivery mode. CLI periodically redraws or emits
a bounded state line without claiming model/web streaming. Terminal output always emits
outcome, last committed phase, diagnostic reference/category when available, inspect
command, and durability-specific continuation guidance.

The retained store writes a versioned `run-summary.json` atomically after the existing
trace and only from validated facts. It is a derived observation, never a resume cursor.
It contains status, terminal outcome, phase, generation, timestamps, durability,
failure category/reference, and fixed safe artifact references. `diagnostics/events.jsonl`
is bounded and append/snapshot-atomic under the existing session lock. Events contain
closed category, timestamp, phase, optional opaque work/attempt ids, validation code,
retry/exhaustion count, and an opaque fingerprint. Events never contain raw exception or
input/model/tool content.

The runtime owns one per-run `RunEventRecorder` implementation behind a narrow
`record(closed_event)` seam. It allocates the monotonic sequence and serializes append or
snapshot publication under the session-store lock. Runtime dispatch, node wrapper,
node-agent bridge, and work-unit controller emit only typed category facts through the
injected capability; providers, tools, and future pod workers never write session files
directly. A recorder failure is swallowed at this observational seam and cannot alter
worker, ledger, gate, checkpoint, or route decisions. Session inspect and the authorized
workbench first render validated summary/timeline/event facts; legacy/corrupt/missing
pieces remain independently unavailable rather than being inferred.

One runtime-owned deterministic diagnostic-reference helper derives an opaque `diag_`
value from trusted research identity, generation, logical phase, a closed category, and
the applicable terminal correlation (current request id or work/attempt identity), never
from raw answer/model/tool content. It is pure and available even when journal persistence
fails. A blocked node stores that value in its terminal
incident; `RecordBearingLifecycleFact`, trace, summary, and every related event preserve
that exact value rather than each layer inventing a timestamp-derived reference. The
summary includes a closed event-journal availability/completeness field and the latest
observed sequence. If a later event cannot be persisted while summary publication remains
possible, it reports `incomplete`; if no validated journal can be read it reports
`unavailable`, never `complete` by absence.

Alternative rejected: make `inspect` dump bundle files or persist original exceptions.
That is neither novice-readable nor safe for credentials and source content.

### Canonical bundle locators are human-sortable without becoming identity

Every new run receives an immutable trusted physical bundle locator at lifecycle start:

```text
YYYYMMDDHHMM_r_<opaque-research-id>
```

The trusted lifecycle start captures the UTC minute before graph invocation, derives
`bundle_directory`, and persists that locator in `ResearchState` with controller-only
ownership before every graph invocation, including an all-fake recipe that only
publishes session metadata. `research_id` remains the sole graph scope, checkpoint
namespace, binding, CLI inspect argument, manifest identity, and correlation identity;
the suffix prevents minute-level collisions. Projection, bootstrap/request stores,
work-unit paths, `ContentRef` values, session publication/inspection/cleanup, and the
workbench derive one root from this checkpointed locator. No caller supplies a directory,
timestamp, or path. The locator grammar is strict, all roots are contained regular
non-symlink directories, and the marker/manifest must bind the exact research id and
locator. A full-fake bundle remains explicitly `session_metadata_only`: its locator does
not imply bootstrap marker, profile, work, or evidence artifact existence.

Old checkpoints that lack `bundle_directory` resolve only to legacy `r_<id>`; they are
not migrated. New-run creation never scans to choose a root. Discovery by research id
may scan the bounded contained parent only to validate old roots or detect duplicate
valid roots; duplicate valid roots fail closed rather than resolving by time or filename.

The existing generic blocked terminal shape is retained: a third rejected response writes
`terminal_status=blocked`, `terminal_reason=gate_blocked`, and a compact incident with
closed `RunFailureCode.INPUT_INVALID_RESPONSE` plus a fixed diagnostic reference. The
presentation-only rejection category `profile_input_unrecognized` is part of bounded
HITL feedback/diagnosis vocabulary, not a second terminal enum. This avoids parallel
terminal taxonomies while preserving an actionable cause.

`list` and `inspect` show both opaque run reference, manifest creation timestamp, and
the safe relative locator label, never a host path. Existing legacy `r_<id>` bundles remain inspectable,
cleanable, and workbench-readable without migration. A duplicate valid directory for
the same research id is unavailable/invalid rather than selected by filename order.

Alternative rejected: prepend time to `research_id` itself. That changes a trusted
opaque graph/checkpoint/binding key into a clock-derived identifier and breaks the
existing identity and path-containment contracts.

## Risks / Trade-offs

- [Additional proposal state adds a checkpoint migration surface] -> bounded optional
  defaults, controller-only ownership, no schema-version bump, and old-checkpoint tests.
- [Localized aliases drift or collide] -> explicit table, token-boundary parsing,
  one-field-only invariant, and fixture coverage for every alias.
- [Invalid response loop can stall] -> feedback retries are bounded separately from
  accepted answer rounds; terminal/UI provides a JSON template and cancellation remains
  graph-owned.
- [Event recording leaks detail] -> sealed event model, strict extra-forbid validators,
  adversarial sentinel tests, and no exception-to-message conversion.
- [Observation races with publication] -> each summary/trace/event file is independently
  validated and atomic; no cross-file consistency claim.
- [Timestamp prefix becomes a second identity] -> the trusted, checkpointed locator is
  only a physical-root selector; `research_id` remains the sole lifecycle identity and
  marker/manifest binding is validated on every root open.
- [CLI progress implies false execution visibility] -> labels say returned-only/local
  wait and report only committed/observed phase.

## Migration Plan

1. Add the canonical locator through lifecycle start, projection, bootstrap,
   request/work-unit paths, retained-session publication, full-fake metadata-only
   behavior, SQLite-reopen/legacy compatibility, and path/manifest binding tests.
2. Add red domain/graph/runtime/CLI/TUI/session tests around the captured failure.
3. Add proposal and parser contracts, controller-owned state defaults/reducers, and
   HITL1 persistence/acceptance/feedback behavior.
4. Extend shared prompt/run contracts and both adapters, then verify all paths against
   the same fixtures.
5. Add retained diagnosis summary/events and update inspect/workbench rendering.
6. Update `agent/README.md`, `agent/AGENTS.md` only if its architectural contract
   changes, backlog cards, requirement registry, evidence metadata, and main specs
   through normal archive sync.
7. If deployment detects an unreadable old optional observation file, retain existing
   inspection semantics and report that file unavailable; no destructive migration is
   needed. Rollback is code rollback: old readers ignore the additional fixed files.

## Open Questions

- Whether the local TUI should offer field widgets immediately or first expose a
  structured JSON composer is an implementation presentation decision. Both must emit
  the same typed `AnswerRun` action/text intent and be covered by the shared prompt
  contract.
