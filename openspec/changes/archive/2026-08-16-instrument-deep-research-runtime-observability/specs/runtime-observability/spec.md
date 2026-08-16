# runtime-observability Specification

> req: RTO-001, RTO-003

## Purpose

Define one safe, trace-correlated standard-log projection of material Deep Research
runtime facts without allowing logging to become lifecycle authority or live transport.

## ADDED Requirements

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

Application owners SHALL obtain `logging.getLogger(__name__)`; DeerFlow startup and
configuration SHALL remain the owner of root handlers, formatters, and the
`TraceContextFilter` that injects current `trace_id` values. Application code SHALL
not reconfigure root logging, create a competing trace filter, write a raw stream
payload, or emit a custom event. A downstream projection SHALL not produce another
record for the same material fact, and logging availability or handler failure SHALL
not change validation, routing, retry, persistence, checkpointed State, terminal
classification, or a legal lifecycle action. (`RTO-001`)

#### Scenario: An ordinary graph boundary is logged once at its owner
- **WHEN** an admitted Run enters and completes one material graph-node boundary
- **THEN** the owner emits one bounded `INFO` record for each distinct boundary fact
  with its phase, outcome, and available safe correlation, while downstream
  projections do not duplicate either fact

#### Scenario: A recoverable validation rejection remains safe and non-controlling
- **WHEN** a deterministic validation boundary rejects a candidate that is eligible
  for its existing bounded recovery
- **THEN** its owner emits one `WARNING` record containing only the applicable closed
  validation code and safe correlation, and the existing validator/controller remains
  the sole owner of recovery and route selection

#### Scenario: A logging sink failure cannot change a Run
- **WHEN** the configured logging path rejects or loses a material record
- **THEN** the existing producer result, Journal behavior, retry/route, and typed
  lifecycle outcome remain unchanged, and no Bundle-local logging fallback is created

#### Scenario: Sensitive or noisy data is not a log fact
- **WHEN** a producer has raw prompt/model/tool content, a provider payload, an
  exception body, a token chunk, or a repeated loop detail available
- **THEN** it emits none of that data at `INFO`, `WARNING`, or `ERROR` and emits no
  duplicate material record because of the repeated path

### Requirement: Trusted correlation joins standard logs without authority expansion

Only the trusted runtime boundary SHALL derive the association among the current outer
DeerFlow thread id, outer run id, an admitted opaque Bundle id, and the DeerFlow trace
context currently available to its configured log filter. At the admitted Bundle
boundary and on later material facts where that association is available, a safe log
projection SHALL make only the opaque Bundle and trusted outer-run correlations
searchable. DeerFlow's trace filter SHALL supply `trace_id` when available; absence
SHALL remain absent rather than being guessed or bound by Deep Research.

The association SHALL not be accepted from tool arguments, copied into graph State,
used to select or recover a Bundle, or treated as Event Journal identity. It SHALL
exclude user identity, credentials, request/model/tool content, full URLs, host paths,
and private Gateway store data. (`RTO-003`)

#### Scenario: Trusted admission correlation can be searched without selecting a Run
- **WHEN** a trusted runtime admits a Bundle with current outer thread/run correlation
  and DeerFlow has a current trace when it configures the record
- **THEN** its safe admission log joins those opaque values to the Bundle id so
  operators can locate the corresponding outer Run, without granting any lookup,
  recovery, or lifecycle authority to the projection

#### Scenario: An absent trace is not replaced
- **WHEN** DeerFlow has no current trace while a material fact is logged
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
- **THEN** that value is not used to create observability correlation and the existing
  trusted-runtime validation behavior remains unchanged
