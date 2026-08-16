## Context

See [proposal.md](proposal.md) for motivation. The current DeerFlow pin is
`66b9e7f21212490cf92fafac137542b9deb06615`. Public runtime introspection proves its
`ToolRuntime` constructor receives `stream_writer: StreamWriter` and its installed
`get_current_trace_id()` remains a zero-argument compatibility surface. The pin does
not publish `deerflow.utils.custom_events`; this change does not require that module.

The archived log-only baseline already validates one `SafeObservation`, attaches only
trusted Bundle/outer correlation, and emits a best-effort standard log. Source guards
currently reject every writer/custom-event path. The Bundle Event Journal,
checkpointed State, and existing retry, route, and lifecycle contracts remain the sole
execution and recovery authorities.

## Goals / Non-Goals

**Goals:**

- Use the current public injected writer without changing DeerFlow, package metadata,
  or `uv.lock`.
- Add one bounded live projection from the existing safe-observation boundary.
- Prove one writer capture path, one invocation path, closed payload admission, owner
  uniqueness, cancellation, and failure isolation.

**Non-Goals:**

- Do not inspect, patch, upgrade, vendor, or modify DeerFlow.
- Do not rediscover the writer through runnable context or a private Gateway store.
- Do not make live payloads a Journal record, persisted history, replay source, State
  field, lifecycle action, retry signal, route input, or Bundle selector.
- Do not configure root logging, add a file sink, or add a presentation renderer.

## Decisions

### Keep the current dependency boundary fixed

The nested DeerFlow `HEAD`, root index gitlink, and
`openspec/governance/project-structure.toml` lock remain at the current hash. The
public API contract verifies only the installed `ToolRuntime.stream_writer` signature
and `get_current_trace_id()`; it does not import missing convenience helpers or read
source/package paths.

This directly serves the current runtime and avoids turning an observability feature
into a dependency migration. No compatibility wrapper for absent DeerFlow helpers is
created because the project sink owns a different, narrower responsibility: payload
admission and isolation around the already public writer.

### Capture once and invoke in one opaque sink

`RuntimeAdapter` is the only application boundary allowed to read
`runtime.stream_writer`. It accepts the capability only when callable and passes it
once to a factory in `runtime/events.py`. The factory returns an opaque sink; the raw
writer is stored only inside that sink and is invoked only by that sink.

The trusted envelope may carry the project-owned sink but never the raw writer. After
Bundle admission, `BundleGraph` binds the sink, admitted Bundle id, and trusted outer
thread/run ids into the existing non-checkpointed observation projection.
`GraphInvocationContext`, `NodeBuildDependencies`, and fact owners receive only that
projection.

Direct writer access elsewhere, `get_stream_writer`, a second emitter, graph-to-runtime
imports, State/checkpoint serialization, caller-supplied sinks, and private Gateway
lookups remain forbidden.

### Extend the existing projection instead of adding a parallel owner route

The existing log projection becomes a runtime observation projection with synchronous
and asynchronous emission methods. Both methods:

1. validate one `SafeObservation`;
2. attempt the existing standard log independently;
3. derive live visibility from the closed operation/outcome predicate;
4. derive the exact live payload from the validated observation plus trusted
   Bundle/outer correlation; and
5. ask the opaque sink to invoke the current writer at most once.

Synchronous owners call the synchronous method. Async owners await the asynchronous
method; the current writer remains a synchronous callback and is invoked inline, as
required by its public `StreamWriter` surface. No thread or blocking wait is added.
If the writer raises `asyncio.CancelledError`, it propagates because cancellation is
not an observation failure.

### Reuse one closed observation as the sole payload input

Producers continue to construct only `SafeObservation`. They cannot supply
`live_visible`, event type, raw payload, sink choice, Bundle/outer correlation, or
`trace_id`.

Every accepted live payload contains:

- required `type="deep_research.progress.v1"`, `phase`, `operation`, `outcome`,
  and admitted `bundle_id`;
- optional `work_id`, `attempt_id`, `code`, `count`, `outer_thread_id`, and
  `outer_run_id`; and
- no `event_type`, unknown key, raw content, exception text, path, credential,
  provider payload, Journal/checkpoint fact, or Deep Research-supplied trace id.

`node` and `gate` require `attempt_id`; `attempt`, `submit`, `retry`, and
`exhaustion` require `work_id` plus `attempt_id`; `retry` also requires
`count`; rejected `validation` requires `code`, with its work/attempt ids included
only when its owner already has them.

The closed live-visible predicate accepts only:

- `node`: `started`, `completed`, `failed`;
- `gate`: `completed`, `rejected`, `cancelled`, `stopped`, `blocked`, `failed`;
- `attempt`: `started`, `failed`;
- `submit`: `completed`;
- `retry`: `retrying`;
- `exhaustion`: `failed`; and
- `validation`: `rejected`.

Runtime adaptation, Bundle lifecycle, node-agent internal detail, successful
validation, terminal-category projection, Journal degradation, and writer-degradation
observations remain log-only.

### Keep log and live attempts independent

Logger failure does not suppress an otherwise valid writer attempt. Writer failure does
not suppress the original standard log or originating result. A non-cancellation writer
exception triggers one separate bounded log-only observation with the originating safe
phase/correlation plus `operation=live_event`, `outcome=degraded`, and
`code=observation_degraded`. It includes no exception text and is excluded from the
live predicate, preventing recursion.

Neither projection result controls Journal append, State write, retry, route, terminal
classification, or lifecycle action. There is no retry, acknowledgement, fallback
writer, or file sink. At-most-once refers to one writer invocation per accepted fact,
not delivery receipt.

### Narrow the source guard and prove sensitivity

The absolute writer/event ban becomes a focused allowlist:

- only `runtime/runtime_adapter.py` may read `.stream_writer`;
- only `runtime/events.py` may store and invoke the writer;
- only `runtime/events.py` may contain
  `"type": "deep_research.progress.v1"`; and
- graph/domain contracts and producers may contain none of the raw-writer or
  live-control vocabulary.

Guards retain bans on `get_stream_writer`, `ProgressEmitter`, old event names,
producer `live_visible`/event-type/sink controls, unsafe payload fields, custom retry,
Bundle/Journal event authority, root logging configuration, and private Gateway access.
Each guard class receives a safe test-owned planted violation to prove it fails, then
the fixture is restored and the baseline must pass.

## Risks / Trade-offs

- [The current writer is absent in embedded or test execution] -> Keep the standard-log
  path active and create no sink.
- [The current writer rejects a payload] -> Preserve the originating result, attempt one
  bounded log-only degradation observation, and add no retry or fallback.
- [A producer attempts to control live visibility or correlation] -> Reject the live
  candidate at the closed validator while preserving its independent valid log.
- [A direct writer call spreads beyond the sink] -> Source guards and planted
  violations fail the architecture contract.
- [Live delivery is filtered, duplicated, or reordered] -> Treat it only as transport
  behavior; create no Journal/State/recovery consequence.

## Migration Plan

1. Prove the current pin, gitlink, registry lock, package metadata, and `uv.lock`
   remain unchanged and add the current public-writer contract.
2. Add red payload, predicate, missing-writer, logger/writer failure, cancellation, and
   no-side-effect tests at the runtime-adapter and observation-projection seams.
3. Implement the opaque sink, trusted capture/binding, projection methods, owner
   integration, and focused source guards.
4. Run focused suites, architecture/requirements governance, full offline verification,
   strict OpenSpec validation, diff checks, and final unchanged-pin inspection.
