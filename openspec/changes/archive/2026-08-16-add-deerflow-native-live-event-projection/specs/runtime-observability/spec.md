# runtime-observability Specification

> req: RTO-001, RTO-003

## MODIFIED Requirements

### Requirement: Material runtime facts have one safe standard-log projection

At the smallest Deep Research owner of each material admission, lifecycle, phase/node,
work submission, attempt, retry/exhaustion, validation, provider/tool failure,
observation-degradation, cancellation/interruption, and terminal fact, the system
SHALL emit exactly one safe record through the process's standard Python logging
hierarchy. The record SHALL include a bounded event type, outcome, phase when
applicable, the admitted opaque Bundle correlation when available, and only the
applicable bounded work id, attempt id, diagnostic/validation code, or count. It SHALL
use `DEBUG` only for bounded local diagnosis, `INFO` for ordinary admission/boundary/
terminal facts, `WARNING` for recoverable problem, retry, validation rejection, or
observation degradation, and `ERROR` for a classified non-recoverable or
cancelled/blocked/stopped terminal fact.

After safe observation validation, the system SHALL derive live visibility from one
closed predicate. It SHALL accept only: `node` with `started`, `completed`, or
`failed`; `gate` with `completed`, `rejected`, `cancelled`, `stopped`,
`blocked`, or `failed`; `attempt` with `started` or `failed`; `submit` with
`completed`; `retry` with `retrying`; `exhaustion` with `failed`; and
`validation` with `rejected`. A producer SHALL NOT supply a `live_visible` flag,
event type, sink choice, raw writer, or alternate classification.

When one accepted fact has a trusted runtime-bound sink, it SHALL additionally attempt
exactly one independent safe live projection through the current public injected
writer. Runtime adaptation, Bundle lifecycle, node-agent internal detail, successful
validation, terminal-category projection, Journal retention/persistence degradation,
bounded `live_event/degraded` writer-failure observations, and every other existing
material fact SHALL remain log-only. The live projection does not replace, derive, or
imply the standard-log record.

Application owners SHALL obtain `logging.getLogger(__name__)`; DeerFlow startup and
configuration SHALL remain the owner of root handlers, formatters, and the
`TraceContextFilter` that injects current `trace_id` values. Application code SHALL
not reconfigure root logging, create a competing trace filter, rediscover a writer,
or invoke a raw writer outside the one approved opaque sink. A downstream projection
SHALL not duplicate either the log or live projection for the same material fact, and
logging availability, live delivery, or sink failure SHALL not change validation,
routing, retry, persistence, checkpointed State, terminal classification, or a legal
lifecycle action. (`RTO-001`)

The trusted runtime boundary SHALL capture only the current public injected writer and
bind it behind a project-owned non-checkpointed observation projection. Graph/domain
fact owners SHALL not receive the writer. Synchronous owners SHALL use the projection's
synchronous emission method and asynchronous owners SHALL await its asynchronous
emission method; both SHALL result in at most one call to the opaque sink for an
accepted fact.

A missing or non-callable writer SHALL suppress only the live attempt and preserve the
standard log and originating typed result. If the writer raises, the projection SHALL
attempt exactly one separate bounded standard-log observation using the originating
safe phase/correlation plus `operation=live_event`, `outcome=degraded`, and
`code=observation_degraded`; it SHALL include no exception text, SHALL emit no live
event for that degradation, and SHALL preserve the originating typed result. An
`asyncio.CancelledError` SHALL propagate unchanged and SHALL NOT be reclassified as a
degradation.

Every accepted live payload SHALL contain required keys `type`, `phase`,
`operation`, `outcome`, and `bundle_id`, with exact discriminator
`"type": "deep_research.progress.v1"`, and SHALL NOT contain the log-only key
`event_type`. Its complete optional key set SHALL be `work_id`, `attempt_id`,
`code`, `count`, `outer_thread_id`, and `outer_run_id`. `node` and `gate`
SHALL require `attempt_id`; `attempt`, `submit`, `retry`, and `exhaustion`
SHALL require `work_id` and `attempt_id`; `retry` SHALL also require `count`;
and rejected `validation` SHALL require `code`, with work/attempt ids present only
when the originating validator has them. It SHALL contain no Deep Research-supplied
`trace_id`, user identity, credential, request/model/tool content, exception text,
provider payload, full URL, host path, Journal sequence, persistence assertion,
checkpoint data, caller-provided correlation, or unknown key.

An event consumer MAY be absent; filtering, absence, duplicate delivery, reordering,
or delivery failure SHALL remain a transport observation only and SHALL not become a
Bundle/Journal record, State write, retry, route, terminal classification, lifecycle
action, replay source, or recovery input.

#### Scenario: An ordinary graph boundary is logged once at its owner
- **WHEN** an admitted Run enters and completes one material graph-node boundary
- **THEN** the owner emits one bounded `INFO` record for each distinct boundary fact
  with its phase, outcome, and available safe correlation, while downstream
  projections do not duplicate either fact

#### Scenario: A declared live boundary is projected once without replacing its log
- **WHEN** an admitted Run reaches one graph-node start/completion/failure boundary
  in the closed live-visible set with a callable current runtime writer
- **THEN** that owner retains its standard log and attempts one bounded
  `deep_research.progress.v1` payload, while downstream projections duplicate neither

#### Scenario: A log-only material fact stays off the live stream
- **WHEN** runtime adaptation, Bundle lifecycle, node-agent internal detail,
  successful validation, terminal-category projection, or Journal degradation emits
  its existing material standard log
- **THEN** it emits no live payload and no downstream owner reclassifies it

#### Scenario: Caller cannot declare a fact live-visible
- **WHEN** a producer supplies a live-visibility flag, event type, sink choice, raw
  writer, or an operation/outcome pair outside the closed predicate
- **THEN** the live candidate is rejected without reinterpreting the runtime fact

#### Scenario: Log and live discriminators cannot be confused
- **WHEN** an otherwise safe live candidate contains `event_type`, omits `type`, or
  supplies any `type` other than `deep_research.progress.v1`
- **THEN** the live candidate is rejected while its independently valid standard log
  and originating typed result remain unchanged

#### Scenario: An incomplete operation-specific payload is rejected
- **WHEN** a live candidate omits a common required key or an operation-specific work,
  attempt, retry-count, or validation-code field
- **THEN** the live candidate is rejected without changing its independently valid
  standard log or originating typed result

#### Scenario: A recoverable validation rejection remains safe and non-controlling
- **WHEN** a deterministic validation boundary rejects a candidate that is eligible
  for its existing bounded recovery
- **THEN** its owner emits one `WARNING` record and one bounded live attempt containing
  only the applicable closed validation code and safe correlation, while the existing
  validator/controller remains the sole owner of recovery and route selection

#### Scenario: A logging sink failure cannot change a Run
- **WHEN** the configured logging path rejects or loses a material record while the
  trusted live sink is callable
- **THEN** the existing producer result, Journal behavior, retry/route, and typed
  lifecycle outcome remain unchanged, and the independent live attempt still occurs
  once without a Bundle-local logging fallback

#### Scenario: A live sink failure cannot change a Run
- **WHEN** the approved opaque sink's writer raises while projecting a material fact
- **THEN** the existing producer result, Journal behavior, retry/route, and typed
  lifecycle outcome remain unchanged; one bounded log-only
  `live_event/degraded` observation is attempted without exception text; and no
  recursive event, retry, or Bundle-local fallback is created

#### Scenario: Cancellation is not degradation
- **WHEN** an asynchronous live projection receives `asyncio.CancelledError`
- **THEN** cancellation propagates unchanged and no degradation observation is created

#### Scenario: Sensitive or noisy data is not a log fact
- **WHEN** a producer has raw prompt/model/tool content, a provider payload, an
  exception body, a token chunk, or a repeated loop detail available
- **THEN** it emits none of that data at `INFO`, `WARNING`, or `ERROR`, emits no
  such live payload, and emits no duplicate material projection

### Requirement: Trusted correlation joins standard logs without authority expansion

Only the trusted runtime boundary SHALL derive the association among the current outer
DeerFlow thread id, outer run id, an admitted opaque Bundle id, and the DeerFlow trace
context currently available to its configured log filter. At the admitted Bundle
boundary and on later material facts where that association is available, a safe log
or independently safe live projection SHALL make only the opaque Bundle and trusted
outer-run correlations searchable. DeerFlow's trace filter SHALL supply `trace_id`
when available; absence SHALL remain absent rather than being guessed or bound by Deep
Research.

The association SHALL not be accepted from tool arguments, copied into graph State,
used to select or recover a Bundle, or treated as Event Journal identity. It SHALL
exclude user identity, credentials, request/model/tool content, full URLs, host paths,
and private Gateway store data. (`RTO-003`)

#### Scenario: Trusted admission correlation can be searched without selecting a Run
- **WHEN** a trusted runtime admits a Bundle with current outer thread/run correlation
  and DeerFlow has a current trace when it configures the record
- **THEN** its safe admission log and any declared live payload join only those opaque
  values to the Bundle id, without granting lookup, recovery, or lifecycle authority

#### Scenario: An absent trace is not replaced
- **WHEN** DeerFlow has no current trace while a material fact is projected
- **THEN** application code supplies no synthetic trace value and the existing Run
  behavior remains unchanged

#### Scenario: Lifecycle logging is emitted only by its owner
- **WHEN** `BundleControl` has both a trusted envelope and an admitted or resolved
  Bundle lifecycle result
- **THEN** `BundleLifecycle` remains the source of exactly one standard-log record for
  Gateway and Local Session Workbench callers, and `BundleControl` emits no duplicate

#### Scenario: Caller-supplied correlation cannot enter a projection
- **WHEN** a caller supplies a trace, run, thread, Bundle, path, or identity value
  outside the trusted runtime boundary
- **THEN** that value is not used to create log or live correlation and the existing
  trusted-runtime validation behavior remains unchanged

#### Scenario: A runtime writer is unavailable
- **WHEN** a declared live-visible fact occurs without a callable writer captured from
  the trusted current `ToolRuntime`
- **THEN** its standard log and typed result remain unchanged and no writer
  rediscovery, private store, retry, acknowledgement, or compatibility fallback is used

#### Scenario: Delivery disorder is not a lifecycle fact
- **WHEN** a live delivery is missing, duplicate, or reordered for an admitted Run
- **THEN** Deep Research creates no replacement event, Journal record, State write,
  recovery, or terminal inference from that transport condition

#### Scenario: Live payload rejects unsafe correlation and content
- **WHEN** a producer offers caller-supplied correlation or any raw content,
  credential, path, provider payload, exception detail, or Journal fact
- **THEN** the live candidate is rejected without emitting a replacement payload or
  changing the originating fact owner's existing typed result
