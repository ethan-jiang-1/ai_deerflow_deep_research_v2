> req: RUS-004, RUS-006

## MODIFIED Requirements

### Requirement: Retained session diagnosis is summarized, correlated, and redacted

For a validated retained lifecycle observation, the session store SHALL maintain a
bounded versioned `run-summary.json` and `diagnostics/events.jsonl` in addition to the
existing manifest/trace. Summary fields SHALL be derived facts only: research id,
timestamps, status/terminal outcome, committed phase, generation, durability, last
trace sequence, closed failure category/reference, event-journal
availability/completeness and latest observed sequence, fixed artifact references, and
the optional `RetainedRecoverySummary` described below. Event fields SHALL be closed
safe categories plus bounded timestamp, sequence, component, event type, severity,
phase, opaque work/attempt/tool/model-call ids, duration, validation/retry/exhaustion
facts, non-reversible correlation fingerprint, and the optional bounded recovery
fields described below.

For a real HITL1 transient provider recovery, the runtime-owned session event journal
SHALL record each observed HITL1 bridge/model invocation, the one scheduled retry with
its exact 1,000 millisecond delay and ordinal, and one exhaustion event only when the
retry budget is actually exhausted. These observations count graph calls to
`run_agent()`, not physical provider HTTP requests; provider SDK retry policy remains
unobserved and outside this requirement. The frozen event contract SHALL add only
optional bounded recovery fields: `recovery_correlation_id`, a distinct
per-bridge/model-invocation opaque attempt id (stored in the existing event attempt
field for bridge/model-invocation events), `provider_category`
(`provider.timeout`, `provider.unavailable`, or `provider.authentication_failed`),
`retry_ordinal`, `backoff_milliseconds`, and `recovery_event_disposition`
(`scheduled` or `exhausted`). `RunEventRecorderProtocol.record()` SHALL accept exactly
those optional closed recovery keyword facts in addition to its existing safe fields;
the runtime recorder adapter SHALL pass them unchanged into the frozen event contract.
Recovery correlation and bridge/model-invocation ids SHALL each match
`[A-Za-z0-9_-]{8,64}`. A correlated bridge/model-invocation event uses the existing
`ATTEMPT` category, carries its distinct attempt id, and has a provider category only
when a classified provider failure result was observed. A scheduled retry uses `RETRY`,
has ordinal one, backoff exactly 1,000 milliseconds, and disposition `scheduled`; an
exhaustion event uses
`EXHAUSTION`, has ordinal one, disposition `exhausted`, and the final transient
provider category. A recovery disposition on a different event category, a different
backoff, or an unbounded/raw identifier is invalid. Legacy event records remain valid
when those fields are absent.

HITL1 receives this recorder through the existing optional graph dependency injection.
Its absence or failure is an unavailable observation and SHALL not change the retry,
blocked-route, checkpoint, or cancellation authority. A cancellation during the
backoff SHALL not cause a post-cancellation recorder write, a synthetic terminal event,
or a promise that a retained cancellation timeline exists.

The frozen, extra-forbid `RetainedRecoverySummary` SHALL contain only trigger category,
trigger invocation ordinal, bridge/model-invocation count, automatic-retry count, and
terminal disposition. It SHALL be absent outside a terminal provider recovery, and its closed
tuple SHALL match the checkpoint projection it copies; it is an inspection projection
and SHALL not decide graph routing, retry, or diagnostic-reference derivation.

A first retry-eligible provider observation creates the recovery correlation id.
Pre-terminal events use that correlation id, not a speculative terminal diagnostic
reference and SHALL never carry the terminal diagnostic reference. For a
provider-diagnostic terminal, `RecordBearingLifecycleFact.diagnostic_ref` SHALL be
present and carry the exact diagnostic reference already stored in the terminal incident,
and its optional `RetainedRecoverySummary` SHALL copy the checkpoint projection's
trigger category/ordinal, bridge/model-invocation counts, and disposition. Every session
publisher, including `ResearchRunExperience` and `runtime/session_operations.py`, SHALL
pass both fields unchanged; the store SHALL copy the diagnostic reference only to the
terminal event, lifecycle trace, summary, inspection projection, and terminal
`RunSessionView.terminal_diagnostic_ref`. It SHALL not derive a replacement or
reconstruct recovery history from events. Legacy non-provider facts with no supplied
incident reference remain valid under their existing behavior.

Buffered pre-terminal events SHALL receive durable sequence numbers in causal order and
be written before any terminal event, lifecycle trace, or summary is published. If a
pre-terminal flush fails, the store SHALL mark the journal `incomplete`, SHALL NOT append
any remaining buffered pre-terminal events after the terminal, and SHALL continue
terminal publication when terminal files remain writable. Recorder failure SHALL never
alter graph, checkpoint, or route authority.

`RunSessionView` SHALL add an optional bounded `terminal_diagnostic_ref`. It SHALL be
absent for non-terminal and legacy views, and for a published provider-diagnostic
terminal it SHALL equal the supplied incident reference. Terminal publication SHALL
replace an older suspended or otherwise stale in-memory projection for the same research
id; a caller cannot infer terminal inspectability from a matching research id alone.

The diagnostic event journal SHALL record the runtime dispatch, graph node, worker
attempt, model/tool boundary, validation, submit, retry/exhaustion, and terminal
lifecycle facts that the runtime actually observes. One deterministic runtime-owned
diagnostic reference SHALL be carried unchanged from a provider-diagnostic terminal
incident through its terminal event, lifecycle trace, summary, inspection projection,
and terminal session view; no pre-terminal correlated event, session publisher, or
presentation adapter may create or copy a competing reference. The store SHALL not write user input,
prompt/model/tool body, URL, absolute path, credential, exception text, traceback, or
arbitrary payload. Each additional file SHALL be atomically written and independently
validated; its absence/corruption SHALL be an unavailable observation, not a lifecycle
inference. Instrumentation failure SHALL never alter worker, ledger, gate, checkpoint,
or graph route authority. If event recording fails after valid observation begins, the
summary SHALL report `incomplete`; missing/corrupt journal data is `unavailable`, not
silent completion. (`RUS-004`, `RUS-006`)

For every new run, the retained session store SHALL publish to the same checkpointed
canonical bundle locator used by graph/bootstrap/work-unit artifacts, named
`YYYYMMDDHHMM_r_<research-id>` from the trusted lifecycle-start UTC minute. The
`research_id` suffix SHALL remain the sole graph, checkpoint, lifecycle-binding, and
inspect identity; the locator is only a human-sortable physical-root selector. Lookup
by research id SHALL validate contained non-symlink candidate roots, strict locator
grammar, and marker/manifest identity; it SHALL support old checkpoints with absent
locator through legacy `r_<research-id>` roots without migration and fail closed if
more than one valid candidate represents the same research id. Inspection/list
projection SHALL expose the manifest created time and safe relative locator label
without accepting a caller-supplied path or treating the directory timestamp as
authority. (`RUS-004`)

The manifest SHALL record the selected relative locator label and validate it against
the containing directory and checkpoint/session fact before publication or inspection.
A full-fake retained session may use the locator for metadata only; absent real marker
or content artifacts remain an explicit `session_metadata_only` layout rather than a
corrupt or implicitly materialized graph bundle. (`RUS-004`)

#### Scenario: Wave worker exhaustion is inspectable
- **WHEN** all Wave0 attempts terminally fail and the returned lifecycle is blocked at
  `wave0`
- **THEN** inspection can show the terminal summary, a correlated diagnostic reference,
  and bounded runtime/node/attempt categories without any raw worker exception

#### Scenario: Execution timeline orders observed components
- **WHEN** a real run enters a node, starts a worker attempt, receives
  model/tool/validation results, retries, and becomes terminal
- **THEN** its event journal orders those safe events by monotonic sequence and UTC
  timestamp with one run correlation identity

#### Scenario: Terminal reference is one correlated value
- **WHEN** HITL1 terminally rejects a third unrecognized response or a Wave0 attempt
  exhausts
- **THEN** the returned terminal incident, lifecycle trace, summary, event timeline,
  CLI receipt, and inspect view expose the same opaque diagnostic reference when
  available

#### Scenario: Journal failure remains visible but non-authoritative
- **WHEN** an event write fails after at least one validated run observation
- **THEN** graph/checkpoint/ledger decisions are unchanged and a later valid summary
  marks the journal `incomplete` rather than implying a complete timeline

#### Scenario: New retained directory sorts by creation time
- **WHEN** a validated run first publishes at `2026-07-22T03:59:53Z` with research id
  `r_abc`
- **THEN** its physical bundle directory begins `202607220359_r_abc`, while its
  manifest, inspect argument, binding, and checkpoint identity remain exactly `r_abc`

#### Scenario: Legacy bundle remains inspectable
- **WHEN** an existing contained bundle is named only `r_<research-id>` and its
  manifest validates
- **THEN** inspect, cleanup, and authorized workbench observation continue to resolve
  it without directory migration or a changed lifecycle identity

#### Scenario: Duplicate directory identities fail closed
- **WHEN** both a legacy or timestamp-prefixed directory and another valid candidate
  claim the same manifest research id
- **THEN** lookup marks the session unavailable and does not choose one by timestamp or
  filename ordering

#### Scenario: Legacy inspection remains honest
- **WHEN** a retained bundle predates summary/events files
- **THEN** inspect shows validated existing facts and marks diagnosis observations
  unavailable without fabricating a status or modifying the bundle

#### Scenario: Redaction rejects unsafe event content
- **WHEN** an event recorder is offered a secret, host path, raw answer, or traceback
- **THEN** validation rejects or redacts it before persistence and no inspection view
  emits it

#### Scenario: Timeout retry is visible in retained inspection
- **WHEN** HITL1 times out once and its retry succeeds
- **THEN** the retained timeline contains two closed bridge/model-invocation observations
  and one scheduled retry observation with retry ordinal one and 1,000 milliseconds,
  correlated by one recovery id and without a terminal exhaustion event or diagnostic
  reference

#### Scenario: Exhausted provider recovery has one correlated terminal diagnosis
- **WHEN** both bounded HITL1 bridge/model invocations fail transiently
- **THEN** inspection orders attempt, retry, attempt, exhaustion, and terminal facts
  by monotonic durable sequence; the recovery id joins the pre-terminal facts, which
  carry no terminal diagnostic reference, and the terminal incident's diagnostic
  reference and retained recovery summary are copied unchanged only through the terminal
  record-bearing fact and terminal projections, without raw provider data

#### Scenario: Pre-terminal flush failure preserves terminal causality
- **WHEN** one buffered recovery observation cannot be durably flushed before a valid
  provider-diagnostic terminal is published
- **THEN** the summary marks the journal `incomplete`, no remaining buffered
  pre-terminal observation is appended after the terminal, and the terminal event,
  trace, summary, and matching terminal session view retain the incident reference when
  their files remain writable

#### Scenario: Every publisher preserves the terminal reference
- **WHEN** an authorized local session operation republishes a blocked
  provider-recovery control result
- **THEN** its trace, summary, and terminal event retain the exact incident diagnostic
  reference and retained recovery summary rather than deriving either from events

#### Scenario: Stale session view cannot impersonate a terminal record
- **WHEN** a same-research session view from an earlier suspension lacks or has a
  different `terminal_diagnostic_ref`
- **THEN** terminal publication replaces that projection, and consumers cannot use the
  stale view to claim inspection for the provider-diagnostic terminal

#### Scenario: Cancellation does not masquerade as exhaustion
- **WHEN** cancellation interrupts the fixed provider backoff before the second call
- **THEN** `CancelledError` remains the lifecycle outcome; no second attempt,
  exhaustion event, terminal provider incident, or retained cancellation timeline is
  promised, although a previously durable scheduled-retry observation may remain

#### Scenario: Old bundles remain inspection-safe
- **WHEN** a bundle has no provider recovery observations
- **THEN** inspection reports the existing validated summary and timeline without
  inferring a retry count or rewriting the bundle
