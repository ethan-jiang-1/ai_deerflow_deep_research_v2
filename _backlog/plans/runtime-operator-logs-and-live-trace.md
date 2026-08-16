# Plan: DeerFlow-native runtime observability and live trace

> Type: design / postmortem | Revised: 2026-08-15 | Status: ready for two sequential owning OpenSpec changes

## Decision

Do **not** add a Bundle-local `diagnostics/operator.log`, a file tailer, or an
application-owned heartbeat loop. Those would duplicate DeerFlow's normal logging
and real-time observation surfaces.

Deep Research will attach to DeerFlow's existing observability stack. The Bundle
Event Journal remains, but only as the bounded durable record for facts that belong
to the Deep Research domain: generation, phase, work, attempt, validation and its
typed terminal disposition.

```
DeerFlow Gateway run
  |
  +-- Python logging -> stderr / deployment log sink
  |       trace_id joins request, log line and external trace
  |
  +-- RunJournal -> RunEventStore -> /events and Console
  |       host run, LLM/tool callback, token and middleware facts
  |
  +-- StreamBridge SSE -> product UI / CLI live renderer
  |       metadata, custom events, message chunks, error, end, heartbeat
  |
  +-- Deep Research reflected tool / nested graph
          |
          +-- Bundle Event Journal -> selected-Bundle inspection
          |       Deep Research domain evidence only
          |
          +-- emit_custom_event -> DeerFlow custom stream -> SSE `events`
                  safe phase / work / attempt / validation projections
```

These are not competing truth stores. They answer different questions:

| Surface | Fact authority | Consumer | Retention / purpose |
| --- | --- | --- | --- |
| DeerFlow Python log | Process/request diagnostics | operator, log aggregator | human-readable operational record, correlated by `trace_id` |
| DeerFlow RunJournal / RunEventStore | outer DeerFlow run and callback facts | `/events`, Console, audit tooling | durable host-level run history |
| DeerFlow StreamBridge SSE | current run's live projection | UI, TUI, gateway-backed CLI | bounded real-time window, not replay evidence |
| Deep Research Bundle Event Journal | typed research-domain facts | selected-Bundle inspector and regression tests | bounded, redacted, local evidence |

## Runtime-wide instrumentation contract

This is a runtime-wide rule, not a `node_agent_bridge` patch. Every production
module that participates in one of the following Deep Research execution boundaries
must obtain a module logger with `logging.getLogger(__name__)` and emit the
applicable safe record at the fact-owning boundary:

- runtime admission, trusted-envelope adaptation, Bundle lifecycle and graph
  execution;
- phase/node entry and completion, deterministic routing and gate verdicts;
- work-unit submission, attempt start/end, retry/exhaustion, model/provider and tool
  failure classification;
- structured-output and deterministic validation rejection;
- persistence/observation degradation, cancellation, interruption, and typed
  terminal disposition.

"Runtime-wide" does **not** mean one log line per function, loop iteration, token,
prompt, model response, tool argument, file byte, or state mutation. Those are noisy,
sensitive, and often already represented by DeerFlow callbacks. Instrument the
smallest owner that can truthfully state the outcome once; downstream projections do
not repeat it as a new fact.

| Level | Use for | Required safe fields |
| --- | --- | --- |
| `DEBUG` | bounded implementation detail used only during selected local diagnosis | operation, opaque correlation id, count/duration; disabled by default |
| `INFO` | admission, phase/node/attempt boundary, accepted submission, gate route, normal terminal result | event type, short Bundle id where available, phase, work/attempt id, outcome |
| `WARNING` | recoverable provider/tool problem, retry, validation rejection, capped/degraded observation | the `INFO` fields plus closed code and retry/limit count |
| `ERROR` | non-recoverable classified failure or blocked/cancelled/stopped terminal fact | safe category, diagnostic reference, legal next action; never raw exception payload |

The same fact can have two deliberately different projections: a human-readable log
line and, when it represents operator-visible live progress, a safe
`deep_research.progress.v1` custom event. The Bundle Event Journal records only the
typed domain evidence it owns. Neither logging nor custom-event delivery may block,
retry, mutate, or recover the research run.

## Why the previous direction was wrong

The previous plan correctly treated observability as a projection rather than a
controller, but chose a parallel substrate: a second text file in every Bundle,
its own tailer, and an independent 15-second heartbeat. DeerFlow already provides
the corresponding responsibilities:

- standard Python `logging` writes to `stderr`; deployment owns any file or central
  log sink;
- `logging.enhance` provides the shared `trace_id` in logs, response headers, and
  supported tracing metadata;
- `RunJournal` records the framework's persistent run/LLM/tool callback history;
- `StreamBridge` provides SSE live events, a 15-second heartbeat, replay cursor, and
  explicit stream-gap semantics.

The old `operator.log` would therefore make log completeness, rotation, failure
handling, human formatting, and liveness semantics application responsibilities for
no new authoritative fact. It must not be implemented.

## Verified current gap

The standalone `demo_real` route is a direct local graph composition, not a
Gateway run. Its `DemoAdapter` constructs `TrustedRuntimeEnvelope(progress=None)`.
Consequently it is intentionally outside DeerFlow's `StreamBridge`, outer
`RunJournal`, request trace context, and Console lifecycle. The existing
`ProgressEmitter` also writes raw `get_stream_writer()` payloads rather than the
DeerFlow-supported custom-event helper.

This explains the 35-minute result-only wait: no real-time subscriber exists on
that path. It is an execution-entry problem, not evidence that JSONL needs a text
sidecar.

## Target behavior

### 1. A gateway-backed real-run observer is the primary operator path

The credentialed end-to-end demo must invoke the configured DeerFlow Gateway through
its supported streaming client/API and render the returned SSE stream. It must not
call the graph through `DemoLifecycleTransport` and then try to reconstruct progress
from local files.

The renderer may present safe, concise lines such as phase transitions, attempt
outcomes, validation rejection codes, terminal outcomes, and a liveness indication
on a received DeerFlow heartbeat. It is a pure SSE consumer: no polling of graph
state, no implicit resume/cancel, no fabricated "still running" state, and no
interpretation of an SSE gap as a terminal failure.

The direct graph invocation can remain as an explicitly labelled embedded smoke
surface while it is useful for deterministic local tests. It must not be called an
end-to-end DeerFlow observability demo and must not claim Gateway-run history,
Console data, trace correlation, or SSE liveness.

### 2. Human-readable logs use DeerFlow's Python logging path

Application modules emit operational diagnostics through
`logging.getLogger(__name__)`, never debug `print` and never a Bundle-local file
writer. Log fields are bounded and safe: event type, short Bundle id, phase, work
or attempt id, typed code, and outcome. Raw prompts, model/tool output, request
headers, credentials, full URLs, and absolute host paths remain prohibited.

Gateway configuration enables `logging.enhance.enabled: true` and JSON output for
end-to-end/operator environments. A deployment or local launcher may capture
`stderr` into a rotated file, but that file is a deployment artifact outside the
Bundle and not an application persistence contract. The `trace_id` is the primary
cross-layer log key.

### 2a. Every local demo has a known physical log location

For a Harness-owned standalone demo, the local launcher/bootstrap installs one
additional file sink for the process's normal Python logging hierarchy. Its stable
root is:

```text
deep_research_harness/.deep-research-demo-runs/logs/
```

The directory already belongs to ignored local demo state. It is deliberately a
**sibling** of `workspace/`, `uploads/`, and `outputs/`, never a child of
`workspace/`: the latter is mapped into the agent sandbox, so an agent or a tool
could read, modify, or delete an operator log.

Each invocation gets a fresh, printed absolute path, for example:

```text
.deep-research-demo-runs/logs/demo-real-20260815T094512Z-pid48291.jsonl
```

The file contains the same logger records sent to `stderr`, in DeerFlow's
trace-correlated JSON format, and is process-scoped rather than Bundle-scoped. The
launcher creates the directory with `0700` and files with `0600`; a bounded rotating
handler limits an individual process file and the launcher enforces a declared total
local retention budget without deleting an active process's file. It prints the path
before the first model/provider call so an operator can immediately `tail -f` it.

This file is a physical sink for normal logging, not a new event format, replay
source, Bundle artifact, lifecycle API, or replacement for SSE. The future Gateway
profile launcher follows the same rule at its profile-owned local runtime-log root;
production containers continue to send `stderr` to their deployment logging system.

### 3. Live domain progress is a DeerFlow custom event

Replace raw stream-writer emission with DeerFlow's supported
`emit_custom_event` / `aemit_custom_event` path. Every payload has a non-empty,
versioned type such as `deep_research.progress.v1` and a strict safe schema. The
minimum projection contains an opaque research/bundle correlation value where
available, phase, operation, outcome, and closed diagnostic/validation code.

This emits onto the LangGraph custom stream and callback path so DeerFlow can expose
it as the SSE `events` stream. Emission remains best-effort and cannot alter graph
routing, retries, gates, Bundle state, or terminal results.

Workstream 1C owns only the safe emission attempt. After it archives, workstream 2
adds the integration contract that proves an event emitted from the reflected nested
Deep Research tool becomes one correctly typed Gateway SSE `events` record. If that
forwarding contract is not supported by the installed DeerFlow version, do not add a
file fallback disguised as the same feature. Keep the immediate UI at the verified
coarse Gateway event granularity and record the direct graph-registration migration
condition separately.

### 4. Keep the Bundle Event Journal as domain evidence

The Bundle Event Journal continues to record only the typed facts the outer framework
cannot intrinsically own: admitted Bundle identity, generation, phase, work/attempt
correlation, deterministic validation outcomes, research gate decisions, and typed
terminal diagnostic references. It remains bounded, redacted, selected-Bundle-only,
and non-authoritative for lifecycle control.

It is not an append-only replacement for DeerFlow `RunEventStore`, and its inspector
is not a replacement for `/events`, Console, tracing, or SSE. A readable inspector
may render its existing rows; it must not maintain a second textual event file.

### 5. Correlation and boundary rules

The owning change must define the safe, explicit mapping among outer DeerFlow
`thread_id` / `run_id`, request `trace_id`, and the Deep Research `bundle_id`.
The mapping must be established only by the trusted runtime boundary and persist no
credentials or user/model content. Operators must be able to go from a Bundle
diagnostic reference to its Gateway run without guessing from timestamps.

Do not read `runtime.context["__run_journal"]` or otherwise reach into a private
Gateway store from Deep Research. This repository currently has a guard against that
coupling. DeerFlow's automatic RunJournal remains valuable without it. A future
project-owned adapter may record selected domain audit facts in the host journal
only after an explicit public-API compatibility decision; it is not part of this
change by default.

## Workstreams and actual change order

This plan has two behavioral workstreams, not two interchangeable change names. The
first workstream was physically split after the installed DeerFlow pin was found to
lack the public custom-event helpers. Its archived log-only slice is retained; it is
not a failed implementation and MUST NOT be reverted.

| Order | Workstream / actual OpenSpec record | Status | Owns | Does not own |
| --- | --- | --- | --- | --- |
| 1A | `instrument-deep-research-runtime-observability` | archived | Safe standard logging, trusted log correlation, fact-owner inventory, and removal of raw writer/custom-event compatibility paths | DeerFlow upgrade, custom-event runtime transport, Gateway SSE, entrypoint logging or rendering |
| 1B | `upgrade-deerflow-custom-event-api` | active, not applied | Published public-helper preflight and the synchronized DeerFlow gitlink/registry-lock update | Runtime event behavior, SSE forwarding, presentation, or DeerFlow source changes |
| 1C | `add-deerflow-native-live-event-projection` | active, not applied | Safe `deep_research.progress.v1` emission from the existing runtime fact owners after 1B, with deterministic no-side-effect evidence | Gateway SSE forwarding proof, heartbeats/gaps, entrypoints, physical logs, or renderers |
| 2 | `wire-harness-observability-entrypoints` | future, not created | Physical local log sink, Gateway SSE forwarding proof, heartbeat/gap read-only presentation, and the operator observer | Runtime event taxonomy, safe event payload schema, gitlink update, Journal/lifecycle authority |

The required order is `1A archived -> 1B apply/archive -> 1C apply/archive -> 2
create/apply/archive`. Workstream 1 closes on deterministic log/event behavior alone.
Only workstream 2 consumes that archived event contract to prove it reaches Gateway
SSE and to render it. If forwarding is unavailable, workstream 1 remains valid while
workstream 2 stops or is re-scoped without reopening the runtime contract.

## Implementation order and evidence

1. Keep archived `instrument-deep-research-runtime-observability` as the completed
   standard-log baseline. Do not revert it or alter its historical record.
2. Apply `upgrade-deerflow-custom-event-api` only after its published public-helper
   preflight passes. It changes the pin and lock together, but adds no runtime event.
3. Apply `add-deerflow-native-live-event-projection` after 1B. It adds the bounded
   runtime event contract and deterministic payload/failure/duplicate evidence; it
   makes no Gateway delivery or renderer claim.
4. Archive 1C only after focused deterministic tests, full offline verification,
   strict validation, and scope review pass.
5. Only then create `wire-harness-observability-entrypoints`. It consumes the
   archived runtime event contract, proves event-to-SSE forwarding, adds the
   gateway-backed observer and physical log bootstrap, and remains read-only with
   respect to lifecycle control.
6. Add bounded live smoke evidence only in workstream 2, after its deterministic
   Gateway/entrypoint tests pass. Capture trace/run/Bundle correlation and final
   diagnostic reference without treating SSE as history or recovery authority.

## Risks and guards

| Risk | Guard |
| --- | --- |
| A second event authority reappears | No Bundle `operator.log`; each surface's fact authority is fixed above; tests keep projections unable to mutate lifecycle state. |
| Nested custom events do not reach SSE | Gateway integration contract is a hard admission check; use verified coarse events rather than a private file fallback. |
| Sensitive content reaches logs/events | Whitelist fields before emission/logging; test secrets, prompts, URL queries, paths, and long model text. |
| Real demo still bypasses DeerFlow | Separate embedded smoke from Gateway-backed observer in command name, documentation, and test fixture. |
| Operators mistake SSE for history | Renderer handles heartbeat/gap as transport facts; diagnosis/replay uses RunEventStore and Bundle inspection. |
| Direct private journal dependency | Preserve the existing guard. Any exception requires a separately approved compatibility design. |
| Local logs become an unbounded application store | Keep application logs on stderr; rotation/collection stays with the launcher or deployment environment. |
| An agent can tamper with an operator log | Put local logs beside, never inside, the sandbox-mapped `workspace/`; enforce owner-only directory/file permissions. |

## Related work

This supersedes the previous `operator.log` proposal and addresses BUG-030's missing
live visibility. BUG-029 and the Wave1 validation work still require typed safe
Bundle events and deterministic regressions; observability must expose those facts,
not replace their owning fixes.

Reference basis: `/Users/bowhead/deer-flow/_digest/observability/00-overview.md`,
`01-logging-and-trace-context.md`, `02-run-events-and-journal.md`,
`05-live-streaming.md`, `08-direct-usage.md`, and
`09-observability-for-your-app.md`.

## Delivery progress

- [x] Establish the DeerFlow-native observability decision and reject Bundle-local `operator.log` / tailer / independent heartbeat.
- [x] Freeze the two-workstream order: 1A/1B/1C runtime work first, then the
  separate entrypoint-wiring change.
- [x] Fix the local physical-log location and containment rule: `.deep-research-demo-runs/logs/`, sibling to sandbox `workspace/`.

### Workstream 1: Runtime instrumentation

- [x] Archive `instrument-deep-research-runtime-observability` as the completed
  standard-log baseline; it is not rolled back.
- [ ] Apply and archive `upgrade-deerflow-custom-event-api` as the public API and
  reproducible dependency prerequisite.
- [ ] Apply and archive `add-deerflow-native-live-event-projection` as the remaining
  safe custom-event runtime contract, with deterministic no-side-effect evidence.
- [ ] Preserve Bundle Journal authority and prove no private Gateway event-store /
  `__run_journal` dependency, raw writer, or `ProgressEmitter` returns.

### Workstream 2: `wire-harness-observability-entrypoints`

- [ ] Open this change only after `add-deerflow-native-live-event-projection` is
  archived; consume its approved runtime event contract without redefining it.
- [ ] Implement one idempotent Harness logging bootstrap for supported demo/CLI/TUI launchers that preserves standard `stderr` logging and prints the absolute physical log path before provider work.
- [ ] Create process-scoped JSON logs under `.deep-research-demo-runs/logs/` with `0700` directory / `0600` file permissions, concurrency isolation, bounded rotation, and total retention that protects active files.
- [ ] Add entrypoint tests proving the physical file receives the same safe trace-correlated record as `stderr`, and a file-sink failure does not alter execution or lifecycle outcome.
- [ ] Configure/preflight DeerFlow trace-correlated logging and SQL-backed history where Gateway/Console observation is claimed.
- [ ] Add a Gateway integration test proving `deep_research.progress.v1` reaches SSE `events`, and that heartbeat/gap presentation remains read-only.
- [ ] Add the gateway-backed operator observer and render safe live progress; label or retire the direct embedded demo's former end-to-end-observability claim.
- [ ] Update local operations documentation with exact log locations, `tail -f` usage, trace/run/Bundle correlation, and the separate role of SSE, RunEventStore, and Bundle inspection.
- [ ] Run focused tests, `UV_OFFLINE=1 make verify`, strict OpenSpec validation, `git diff HEAD --check`, bounded live smoke evidence, then archive Change 2 with recorded evidence.
