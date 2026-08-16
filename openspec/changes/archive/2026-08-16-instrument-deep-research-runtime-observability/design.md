## Context

Deep Research currently has a partial `runtime/events.py` implementation from the
earlier proposal. It validates a `deep_research.progress.v1` payload, retains a
`ProgressEmitter`, and is shaped around a raw LangGraph stream writer. That direction
cannot be completed on the installed DeerFlow version because its public package has
logging configuration, `TraceContextFilter`, and current trace lookup, but no public
custom-event helper. The application has already validated its current DeerFlow
version, so dependency upgrades are explicitly deferred.

The Bundle Event Journal records bounded domain facts through best-effort recorders at
lifecycle, graph, work-unit, validation, and model/tool boundaries. It is not a log
sink or lifecycle owner. This change introduces a common log-only projection contract
without making a second source of truth, a recovery path, or a new live transport.

## Goals / Non-Goals

**Goals:**

- Produce one bounded standard log at the smallest owner that can truthfully state a
  material fact.
- Reuse the installed DeerFlow root logging configuration and its trace filter.
- Join trusted outer thread/run correlation to an admitted Bundle only where the
  runtime boundary already has both facts, while leaving an absent trace absent.
- Keep log delivery best effort and incapable of altering return values,
  cancellation, Journal behavior, routing, retries, State, checkpoints, or recovery.
- Retire raw writer and custom-event surfaces from the partial implementation.

**Non-Goals:**

- Upgrading DeerFlow or adding a custom-event, stream-writer, SSE, Gateway, or file
  transport.
- Configuring handlers, formatters, trace filters, retention, or physical log paths.
- Changing Bundle lifecycle, Journal persistence, graph routing, retry policy,
  checkpointing, or public control APIs.
- Reading or modifying `deerflow/` source or its gitlink.

## Authority And Ownership

| Concern | Fact authority and accountable owner | Writer/projection | Explicitly not owned |
| --- | --- | --- | --- |
| Bundle lifecycle result, route, retry, and terminal state | Existing Bundle lifecycle, graph, engine, and node owners | Their smallest truthful owner emits one log through the shared facade | `runtime/events.py`, logging configuration, Journal, or a log record cannot decide or recover a Run |
| Bounded domain diagnostic evidence | Bundle Event Journal and its existing recorders | Journal may record its own bounded facts independently of logs | Logging cannot claim a Journal append, sequence, health, or history |
| Process handlers, formatters, and trace field | DeerFlow startup/configuration | DeerFlow config installs root handlers/formatters and `TraceContextFilter` | Application modules cannot configure root logging or add an alternate trace filter |
| Current `trace_id` | DeerFlow current trace context | `TraceContextFilter` injects it into records where present | Application code cannot synthesize, persist, or caller-bind it |
| Outer thread/run to Bundle correlation | Trusted runtime boundary after admission/resolution | Safe log extras only at boundaries that possess the trusted association | Tool arguments, graph State, Journal identity, Bundle selection, checkpoints, and recovery |

The standard logging hierarchy is a projection only. It has no acknowledgement,
ordering, replay, persistence, authorization, or control semantics. A log's presence,
absence, filtering, duplication attempt, or sink failure cannot change an existing
owner's fact.

## Log Record Contract

The facade accepts a typed, closed observation supplied by an owner. Its fields are
an event type, phase, operation, closed outcome, and only applicable opaque Bundle,
work, attempt, bounded diagnostic/validation code, or count. The facade maps ordinary
admission, boundary, and terminal facts to `INFO`; recoverable validation rejection,
retry, or observation degradation to `WARNING`; classified non-recoverable,
cancelled, blocked, or stopped terminal facts to `ERROR`; and bounded local diagnosis
only to `DEBUG`.

Each application producer uses `logging.getLogger(__name__)` and supplies no
`trace_id`. Where trusted runtime code has an admitted/resolved Bundle association, it
may provide only opaque `outer_thread_id` and `outer_run_id` extras. DeerFlow's
installed `TraceContextFilter` injects the current `trace_id`; if it has none, the
record has no app-invented replacement.

The facade rejects or drops raw prompts, model/tool content or arguments, provider
payloads, credentials, request headers, full URLs/query strings, absolute paths,
stack traces, arbitrary exception messages, checkpoint/internal-wire values, and
token or repeated loop/state-write content. It also rejects unknown keys and refuses
to make an additional log at a downstream adapter for an already-owned fact.

`logger.log()` is invoked in a narrow best-effort boundary. A handler failure is
suppressed after preserving `asyncio.CancelledError`; there is no retry, fallback
handler, file, event store, or Journal write. This catches direct test-injected logger
failures while normal logging configuration retains responsibility for its own sink
behavior.

## Projection Flow

```text
existing fact owner
  -> typed safe observation (non-checkpointed only)
  -> runtime/events.py validates and logs via owner module logger
  -> DeerFlow root handler + TraceContextFilter project the configured record

Bundle Journal recorder (independent bounded evidence) ----> Journal
```

`RuntimeAdapter` creates the trusted envelope. `BundleControl` binds safe outer
thread/run correlation only after its existing admission or resolution succeeds.
`BundleLifecycle` is the sole lifecycle-log producer for Gateway and Local Session
Workbench callers; `BundleControl` produces no duplicate. For graph and work owners,
the runtime-created facade crosses through `GraphInvocationContext` and
`NodeBuildDependencies` as a non-checkpointed domain protocol. It is never serialized
into graph State, a checkpoint, or a Journal identity.

## Failure, Cancellation, And Recovery

| Case | Detection and owner | Action | Terminal invariant and evidence |
| --- | --- | --- | --- |
| Logger/handler failure | Facade observes a direct logging exception | Suppress only its own failure; re-raise cancellation | Producer's return value, Journal behavior, route/retry, and lifecycle result are unchanged; injected-failure test proves it |
| No current trace | DeerFlow trace context/filter has no trace | Emit no replacement trace field | Existing record and Run remain valid; absent-trace test proves no fabricated value |
| Unsafe or malformed observation | Facade validation | Drop log only | Existing owner fact remains unchanged; allowlist/redaction test proves it |
| Duplicate projection attempt | Owner inventory and focused adapter tests | Do not add a downstream projection | Exactly one owner-local record per material fact; lifecycle/graph tests prove it |
| Cancellation | Existing producer owns cancellation | Propagate `asyncio.CancelledError` untouched | Existing cancellation outcome and legal next action remain unchanged; cancellation test proves it |

## Compatibility And Retirement

The partial `ProgressEmitter`, event payload type, event-only projection, injectable
event sink, and raw writer invocation are not established public APIs. They are
retired in this active change rather than preserved as compatibility routes. Any
existing tests and assets that describe them are rewritten to the log-only contract.

`RTO-002` was allocated for the removed custom-event requirement. Apply retires it in
the requirement registry with its existing no-reuse semantics; it is deliberately not
represented as an active delta requirement. This planning update does not mutate the
registry because it is not an OpenSpec planning artifact.

The change does not alter public DeerFlow surfaces. A future, separately approved
change may reassess an installed DeerFlow upgrade and custom-event support after
compatibility and regression review.

## Guards And Evidence

- Focused unit tests validate the closed log schema, level map, redaction, direct
  logger failure isolation, and cancellation propagation.
- Runtime and lifecycle tests validate trusted correlation, absent trace honesty, and
  exactly one lifecycle log from `BundleLifecycle` for both entry paths.
- Graph/work/node-agent tests validate non-checkpointed propagation, owner-local
  logging, and unchanged results/recovery.
- Negative source/behavior tests forbid `get_stream_writer`, direct writer calls,
  custom-event imports/helpers, `ProgressEmitter`, private Gateway journals, and raw
  sensitive values in normal log projection code.
- Full verification, strict OpenSpec validation, requirement-registry validation, and
  git/submodule status evidence prove the change did not alter `deerflow/`.
