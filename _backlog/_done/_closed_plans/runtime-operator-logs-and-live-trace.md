# Plan: DeerFlow-native runtime observability and live trace

> Type: delivery plan | Revised: 2026-08-16 | Status: all three records archived, chain complete

## Alignment Rule

This plan is an index of the actual OpenSpec records, not a second independent
implementation design. Its scope, order, exclusions, rollback rules, and archive
conditions MUST match the listed Change artifacts. A new work item belongs in the
owning Change first and in this plan in the same planning update.

There are exactly three records in this delivery chain:

| Order | OpenSpec record | State | Exact role |
| --- | --- | --- | --- |
| 0 | `instrument-deep-research-runtime-observability` | archived | Implemented safe standard-log baseline; retain it and do not roll it back |
| 1 | `add-deerflow-native-live-event-projection` | archived | Added safe current-pin runtime custom-event emission through public injected `ToolRuntime.stream_writer`; no dependency upgrade |
| 2 | `wire-harness-observability-entrypoints` | archived | Proved public Gateway forwarding, cut over both real entrypoints, and added profile-owned physical `stderr` capture |

The implementation/archive order is therefore:

```text
archived instrument-deep-research-runtime-observability
  -> apply and archive add-deerflow-native-live-event-projection
  -> apply and archive wire-harness-observability-entrypoints
```

There is no separate `1A/1B/1C` sequence, no future uncreated Change, and no pending
dependency upgrade. The former `upgrade-deerflow-custom-event-api` planning record was
removed. Change 1 proved and used the current public injected writer instead.

## Architecture Decision

Deep Research uses DeerFlow's existing observation surfaces and keeps their authority
separate:

```text
DeerFlow Gateway run
  |
  +-- Python logging -> stderr -> profile/deployment capture
  |       trace_id joins request, log line, and supported external trace
  |
  +-- RunJournal / RunEventStore -> public history and Console
  |       outer DeerFlow run, LLM/tool callback, and token facts
  |
  +-- StreamBridge -> public SSE
  |       metadata, messages-tuple, custom, error, end, heartbeat, gap
  |
  +-- reflected Deep Research tool
          |
          +-- Bundle Event Journal
          |       bounded Deep Research domain evidence only
          |
          +-- deep_research.progress.v1
                  best-effort safe projection to DeerFlow custom stream
```

| Surface | Fact authority | Purpose | Explicit limit |
| --- | --- | --- | --- |
| Standard Python log | Existing Deep Research/DeerFlow fact owner | Human-readable operational diagnostics correlated by DeerFlow `trace_id` | Not history, State, recovery, or lifecycle control |
| DeerFlow RunJournal / RunEventStore | Outer DeerFlow run/callback owner | Durable Gateway history and Console observation | Deep Research does not read private `__run_journal` or stores |
| DeerFlow StreamBridge SSE | Gateway transport | Current-run live window | Heartbeat/gap/end are transport facts, not Deep Research outcomes |
| Bundle Event Journal | Deep Research domain fact owners | Bounded selected-Bundle evidence | Not Gateway history, SSE replay, or external lifecycle authority |

No Change in this chain adds a Bundle-local `operator.log`, file tailer, application
heartbeat, raw `StreamWriter`, `ProgressEmitter`, private Gateway store read, event
acknowledgement, custom delivery retry, or file transport fallback.

## Archived Baseline

### `instrument-deep-research-runtime-observability`

This Change is already implemented and archived. It remains the required baseline and
is not reverted merely because later planning was reorganized.

It owns exactly:

- one safe standard-log projection at each declared material runtime fact owner;
- `logging.getLogger(__name__)` use without application root-handler or trace-filter
  configuration;
- trusted outer thread/run and admitted Bundle correlation for logging only;
- closed safe fields, level mapping, redaction, duplicate prevention, logger-failure
  isolation, and cancellation preservation;
- removal of raw writer, partial custom-event, and `ProgressEmitter` compatibility
  paths; and
- preservation of Bundle Journal, State, routing, retry, and lifecycle authority.

It does not own a DeerFlow pin change, runtime custom event, Gateway forwarding,
CLI/TUI observer, heartbeat/gap presentation, or physical file capture.

## Archived Change 1

### `add-deerflow-native-live-event-projection`

Change 1 was implemented, synced, archived, and committed at the unchanged DeerFlow
pin. It introduced no dependency-only unit and no framework upgrade.

It owns exactly:

1. Prove the unchanged DeerFlow nested `HEAD`, root index gitlink, and registry lock at
   `66b9e7f21212490cf92fafac137542b9deb06615`, plus the public
   `ToolRuntime.stream_writer` and `get_current_trace_id()` call shapes, without
   source/package browsing.
2. At trusted `ToolRuntime` adaptation, reduce the public writer immediately to an
   opaque project-owned custom-event sink. After Bundle admission, bind only that sink
   plus trusted Bundle/thread/run correlation into the non-checkpointed observation
   projection passed to fact owners; never expose or directly call the raw writer.
3. Derive live visibility only inside `runtime/events.py` from the exact closed
   operation/outcome predicate: `node` started/completed/failed; `gate`
   completed/rejected/cancelled/stopped/blocked/failed; `attempt` started/failed;
   `submit` completed; `retry` retrying; `exhaustion` failed; and `validation`
   rejected. Producers cannot supply a `live_visible` flag, event type, or sink choice;
   all other material facts stay log-only.
4. Attempt one event with exact discriminator
   `"type": "deep_research.progress.v1"` for each accepted fact through DeerFlow's
   predecessor-owned opaque sink in addition to its existing
   standard log. The live payload never uses log-only `event_type`; always requires
   `type`, `phase`, `operation`, `outcome`, and admitted `bundle_id`; requires
   `attempt_id` for node/gate, `work_id` plus `attempt_id` for
   attempt/submit/retry/exhaustion, `count` for retry, and `code` for rejected
   validation; and permits validation work/attempt ids and trusted outer correlation
   only when available.
5. Attach only admitted Bundle and trusted outer thread/run correlation; do not supply
   application `trace_id`, raw content, caller correlation, Journal sequence, State,
   persistence, or recovery claims.
6. Keep log and event attempts independent and best-effort. Logger failure does not
    suppress an otherwise valid event attempt; writer exception does not suppress the
    original standard log. A writer exception attempts one separate bounded log-only
    observation with the original safe phase/correlation plus `operation=live_event`,
    `outcome=degraded`, and `code=observation_degraded`, without exception text or a
    recursive event. Missing consumer, duplicate/reordered/lost delivery, or subscriber
    failure changes no producer result, Journal, State, route, retry, terminal
    disposition, or lifecycle action; `CancelledError` still propagates without being
    reclassified as degradation.
7. Replace the absolute custom-event source ban only with a narrow allowlist for
    writer capture at `runtime/runtime_adapter.py`, opaque sink use and the closed
    predicate inside `runtime/events.py`, and the exact event type. Retain bans on
    direct writer calls/exposure, producer event controls, `get_stream_writer`,
    `ProgressEmitter`, unsafe fields, private Gateway stores, compatibility wrappers,
    custom retry, and acknowledgement paths. Prove guard sensitivity with safe
    test-owned planted violations and require the restored baseline to pass.

Change 1 explicitly does not own Gateway SSE forwarding, the SSE channel name,
heartbeat/gap behavior, CLI/TUI rendering, physical log capture, private RunJournal
access, Bundle Journal changes, or lifecycle/retry/route changes.

### Change 1 archive result

- Archived in commit `3edba72` after focused, fast, workflow, governance, strict
  OpenSpec, and diff gates passed. The two known full-suite failures were reproduced
  at baseline and recorded in the archived verification evidence.
- Nested `HEAD`, root gitlink, registry lock, package metadata, and `uv.lock` remained
  unchanged. Successful Change 1 archive publishes only the runtime emission contract;
  it makes no Gateway delivery claim.

## Active Change 2

### `wire-harness-observability-entrypoints`

Change 2 is now the only active Change. It consumes the archived predecessor event
contract without redefining its schema or fact owners.

It owns exactly:

1. Add `runtime/gateway_observer.py` as the single public thread/run-stream boundary,
   using DeerFlow's public thread creation and
   `POST /api/threads/{thread_id}/runs/stream` interfaces with
   `assistant_id=deep-research`.
2. Use `httpx` plus explicitly declared `httpx-sse` structured parsing. Admit only
   bounded `metadata`, `messages-tuple`, `custom`, `error`, `end`, heartbeat, and gap
   records; import no private Gateway module or store.
3. Preserve the existing shared typed run experience by accepting only a validated
   returned `deep_research` tool result. Safe assistant text remains presentation;
   tool arguments, other tool results, and raw model/provider payloads are dropped.
4. Treat heartbeat as liveness, gap/disconnect as an incomplete live window, and SSE
   `end` as outer Gateway-turn completion only. None of them proves a Deep Research
   lifecycle outcome or authorizes retry/resume/cancel.
5. Prove one predecessor-owned `deep_research.progress.v1` payload from the reflected
   tool reaches DeerFlow's public SSE `custom` channel before enabling progress-event
   rendering.
6. Cut the default real path in `scripts/demo_real.py` and real mode of
   `scripts/demo_tui.py` to the selected ready Gateway profile. Preserve `--question`,
   `--scripted`, typed prompts/results, and explicit user follow-up turns.
7. Leave fixture CLI/TUI graph behavior unchanged. Retain local all-real graph
   composition only behind an explicit embedded-smoke selection whose banner/help/docs
   deny Gateway history, Console, trace, liveness, and forwarding claims.
8. Replace local model/Tavily checks on Gateway-backed paths with selected profile,
   Gateway health, public-entry, trace-correlated JSON logging, and durable history
   readiness. Local model/Tavily checks remain only for embedded smoke.
9. Extend `scripts/local_profiles.py` to launch the unchanged upstream stack as a child
   and tee its existing `stderr` to both inherited `stderr` and a secure bounded
   process log family under `.deep-research-demo-runs/logs/`.
10. Create log directories/files with owner-only permissions, print the absolute base
    path before provider work, isolate concurrent launches, rotate/bound inactive logs,
    protect active files, preserve signals/exit status, and disable only file capture
    when capture fails.
11. Register the Gateway observer, focused evidence, and bounded `httpx_sse` runtime
    import in project-structure governance and update operator documentation.

Change 2 explicitly does not own the runtime event taxonomy/payload, DeerFlow source or
gitlink, generic remote/authenticated Gateway support, raw writers, private
`__run_journal`, Bundle Journal/history changes, graph State, lifecycle/retry/route
control, SSE replay, acknowledgement, dedupe authority, or a file/tailer/heartbeat
fallback.

### Change 2 archive and rollback

- Deterministic structured-SSE, typed-result, CLI, TUI, profile, capture, source-guard,
  requirement, and architecture evidence must pass before the bounded live smoke.
- If nested custom-event forwarding fails, keep progress rendering disabled and leave
  the Change active for repair, or explicitly re-scope all Change artifacts before a
  reduced archive. Coarse events do not silently satisfy the original claim.
- Capture failure must preserve normal `stderr`, the Gateway process, and every Deep
  Research outcome.
- Archive only when both real entrypoints use the public path, fixture behavior remains
  unchanged, physical logs remain deployment artifacts, and the final diff/tasks/
  evidence match the approved Change scope.

## Implementation Signal

The current execution signal is precise:

- [x] Keep archived `instrument-deep-research-runtime-observability`; no rollback.
- [x] Apply and archive `add-deerflow-native-live-event-projection` at the unchanged
  current pin.
- [x] Apply and archive `wire-harness-observability-entrypoints` as the only remaining
  Change.
- [x] Remove the redundant open `upgrade-deerflow-custom-event-api` planning record
  after confirming its useful obligations are present in Change 1.

Reference basis:
`/Users/bowhead/deer-flow/_digest/observability/00-overview.md`,
`01-logging-and-trace-context.md`, `02-run-events-and-journal.md`,
`05-live-streaming.md`, `08-direct-usage.md`, `09-observability-for-your-app.md`, and
the public Gateway API/stream digest under `_digest/operations/integration/`.
