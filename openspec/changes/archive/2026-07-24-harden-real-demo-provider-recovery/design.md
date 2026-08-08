## Context

`BUG-008` recorded a real standalone run that reached `hitl1`, started one bridge/model
invocation, and terminated as `provider.timeout` after its 30-second wall-time budget.
The current HITL1 loop uses its second invocation only to repair malformed
structured output; any non-success agent result goes straight to the existing
blocked route. Although retained events support a `retry_count` field, this path
does not write retry/exhaustion observations, and the shared failure/CLI contracts
cannot say whether a retry occurred.

The current event store buffers observations made before the first returned lifecycle
record, but its publication path currently appends them after its terminal event and
derives another diagnostic reference. The current shared failure projection is built
after session publication. A design that merely asks all events to share a future
terminal reference would therefore create contradictory order and authority.

The affected layers are the real HITL1 graph node, typed terminal/failure projection,
retained event observation, safe real-demo model identity, and standalone CLI/TUI
presentation. The checkpointed `ResearchState.latest_incident` remains lifecycle
authority; retained files remain observation only. No upstream DeerFlow, Gateway,
Web, configuration surface, sandbox mount, MCP, ACP, skill, or task-subagent
integration changes are in scope.

## Goals / Non-Goals

Goals:

- Recover one first-attempt HITL1 transient provider result before terminal blocking
  under a deterministic bounded policy.
- Preserve a compact, closed terminal account of HITL1 bridge/model invocations, recovery
  disposition, configured-service label, and observed response fact from the graph
  result through retained inspection and terminal presentation.
- Give people and AI consumers one legal fresh-start action while preserving
  `same_process` truth and redaction guarantees.

Non-goals:

- Retrying authentication, configuration, tool-policy, structured-output, or
  unknown failures.
- Changing any downstream phase, adding generic resume after a same-process exit,
  changing provider SDK retry policy, or exposing raw exceptions/provider payloads.
- Treating retained events as graph control data or increasing the 30-second
  per-invocation wall-time limit.
- Claiming live retry progress through the returned-only CLI/TUI wait loop, showing a
  full endpoint URL, or placing prompt/user text in a command, diagnostic, or
  terminal projection.

## Decisions

### Graph-owned, closed retry state machine

HITL1 owns the policy because it owns the brief-generation visit, the shared
two-invocation ceiling, and the existing blocked route. It does not introduce an
engine-level retry abstraction because no other phase adopts this policy.

A result is retry-eligible only when the trusted `NodeAgentContext` identifies
`node_name=hitl1`, its request is zero-tool, and the bridge directly returns
`provider.timeout` or `provider.unavailable` together with its valid
`ProviderObservation`. A code alone, a legacy problem without that observation, or a
result from any other node is not admission to this recovery path and follows the
existing fail-closed route.

The visit has exactly two possible `run_agent()` invocations and one fixed
`1,000 ms` backoff. Its bridge/model-invocation wait budget is therefore at most 61
seconds: two existing 30-second bridge wall-time budgets plus one 1-second backoff.
Local scheduling overhead and SDK-internal provider requests are outside that observed
budget and cannot authorize another graph call.

| First invocation | Second invocation or action | Terminal recovery facts |
| --- | --- | --- |
| retry-eligible transient | wait 1,000 ms, repeat the identical initial brief request | none if valid; otherwise `exhausted` or `retry_followed_by_terminal_failure` |
| valid but malformed output | existing repair request | none unless the repair call returns a transient provider result, then `retry_not_started_budget_consumed` |
| non-transient failure | no second call | absent |
| cancellation during backoff | propagate `CancelledError`; no second call | no terminal incident or exhaustion fact |

`exhausted` means both calls ended in retry-eligible transient provider categories.
`retry_followed_by_terminal_failure` means the automatic retry occurred but its
second call ended in a non-transient typed failure or invalid structured result.
`retry_not_started_budget_consumed` means a transient provider result occurred on the
repair call after the first call already consumed the other visit slot. In every case,
the terminal's final failure category remains the actual final category; recovery
facts explain history rather than replacing it.

This keeps retries in the graph-owned control layer, where phase policy and the
existing blocked route are explicit. Placing retry in `RuntimeNodeAgentBridge`
would hide invocation count from the node, make different phases inherit a policy
they did not opt into, and make structured-repair and provider-retry budgets hard to
compose.

### Narrow provider classification and safe service facts

The bridge remains a one-call boundary and never retries. The new classification,
observation, label, and authority behavior is admitted only for a trusted
`NodeAgentContext.node_name=hitl1` together with
`NodeExecutionRequest.tools_enabled=false`; all other node/request pairs retain their
existing mapping. This prevents a zero-tool request in another phase, or a tool HTTP
failure, from being represented as the configured HITL1 model service.

For that exact invocation, the bridge maps its own wall-time expiry, a direct public
`httpx.TimeoutException`, or a direct public `openai.APITimeoutError` to
`provider.timeout` with `no_response`. It maps `provider.unavailable` only from a
direct `ConnectionError`, direct `httpx.NetworkError`, direct public
`openai.APIConnectionError`, an allowlisted connection-related `OSError` errno
(`ECONNABORTED`, `ECONNREFUSED`, `ECONNRESET`, `ENETDOWN`, `ENETUNREACH`,
`EHOSTDOWN`, `EHOSTUNREACH`, or `ETIMEDOUT` when defined on the platform), or a
supported status (`408`, `429`, `500`, `502`, `503`, or `504`) carried directly by
either public `httpx.HTTPStatusError` or public `openai.APIStatusError`. The classifier
checks `httpx.TimeoutException` and `openai.APITimeoutError` before their broader
transport/connection classes, and checks a naked inner `TimeoutError` before the generic
`OSError` branch, so each timeout remains correctly classified and a naked inner timeout
remains unclassified even when it carries `ETIMEDOUT`. `401` and `403` from a trusted
typed status carrier remain authentication failures; all unsupported statuses and
unclassified exceptions fail closed as their existing non-transient category.

The bridge treats those SDK classes as a closed, direct exception boundary: it SHALL
not walk a cause/context chain, inspect a response body, headers, request URL, or a
generic exception attribute. From a typed public status carrier it reads only
`httpx.HTTPStatusError.response.status_code` or `openai.APIStatusError.status_code`,
validates the bounded integer `[100, 599]`, and then discards the carrier.
Every direct public `httpx.HTTPStatusError` or `openai.APIStatusError` from the admitted
HITL1 invocation still carries that safe status observation, including a non-retryable
status. That observation explains a visible provider response without changing retry
eligibility or the redaction boundary. `agent/pyproject.toml` declares both
`httpx>=0.28,<0.29` and `openai>=2.45,<3` as direct runtime dependencies and lock
metadata is refreshed with both declarations; the classifier never relies on an
incidental transitive installation.

The zero-tool bridge wall-time mapping must be distinguishable from a `TimeoutError`
raised by the invoked agent or unrelated local code. It uses an explicit Python 3.12
deadline scope and checks that scope's expired state before returning
`provider.timeout`; a naked inner `TimeoutError` is unclassified and takes the
existing fail-closed path. This prevents a local defect from consuming HITL1's one
automatic provider retry.

`ProviderObservation` is a frozen, extra-forbid projection with an optional bounded
`configured_service_label`, optional `configured_endpoint_authority`, `response_kind`
(`no_response` or `http_response`), and an HTTP status only for `http_response`. The
default resolver identifies the exact selected `app_config.models[0]` configuration,
passes its `name` explicitly to `create_chat_model`, and uses only that selected
`ModelConfig.name` as its possible label. It may derive an endpoint authority only from
that selected configuration's `base_url`, `openai_api_base`, or `api_base` values: every
present candidate must parse as an absolute `http` or `https` URL with no user info and
a valid host and port. A normal path, query, or fragment is permitted in the configured
URL but is discarded before candidates normalize to one lower-case
`scheme://host[:non-default-port]` authority of at most 253 ASCII characters. An absent,
invalid, credential-bearing, or conflicting candidate leaves the authority absent. This
does not inspect a model object or provider response. That resolver returns a frozen
runtime-only `ResolvedNodeModel` binding of the model and its possible label/authority.
A custom resolver may return the same explicit binding, but an existing raw-model return
remains accepted and has no label or authority; the bridge never guesses either from a
model object, provider class, model attribute, a config-list entry other than the exact
selected configuration, `ModelConfig.model`, or a provider-supplied display string. A
label is absent when the binding is missing or fails its bounds. A timeout or connection
failure SHALL state `no_response`; a classified public HTTP response SHALL state its
bounded integer status. For that admitted HITL1 zero-tool invocation, the bridge SHALL
attach this observation to every classified provider result when the safe fact exists
and to every direct public HTTP response branch, including a non-retryable status. Full
URLs, base URL paths, queries, fragments, user info, provider bodies, credentials, and
exception text never enter `NodeProblem`.

`domain/run_experience.py` remains the canonical domain module for the frozen
`ProviderObservation` and `ProviderRecoveryProjection` validators, so the bridge,
HITL1 checkpoint, and run experience share one typed interface. The existing
`domain/run_session.py` owns a smaller `RetainedRecoverySummary` projection containing
only trigger category/ordinal, attempt counts, and disposition for inspection. Runtime
copies it from the validated checkpoint projection; it cannot own checkpoint writes,
retries, diagnostics, presentation, or control decisions.

### Declared raw-classifier import boundary

The bridge's direct public `httpx` and OpenAI SDK carrier checks are intentional raw
binding dependencies, not incidental transitive imports. The structural registry,
its `project-structure` requirement, and the architecture checker therefore admit
exactly `httpx` and `openai` only for
`runtime/node_agent_bridge.py`. Other runtime modules and every other layer remain
unable to import either namespace. This makes the direct dependency visible in both
the lockfile and the mechanical boundary rather than concealing it with a dynamic
import or broadening raw provider access across the runtime layer.

### Checkpoint-owned recovery facts and terminal projection

`ResearchState.latest_incident` is the sole owner of terminal recovery facts. Its
frozen `ProviderRecoveryProjection` nests the retry trigger category, its safe
`ProviderObservation`, trigger invocation ordinal, model-invocation count,
automatic-retry count, and one of the three terminal dispositions above. The trigger
category is only `provider.timeout` or `provider.unavailable`; its observation must
match the classified response shape. `exhausted` and
`retry_followed_by_terminal_failure` require trigger invocation one, while
`retry_not_started_budget_consumed` requires trigger invocation two. The incident
also retains the final call's safe provider observation only when the bridge supplied
one, including a non-retryable public HTTP response; a legacy `PermissionError`
authentication result therefore does not fabricate an observation. Otherwise the
recovery projection's trigger observation is the only provider observation shown.
The recovery projection is absent when no retry-eligible transient provider result
occurred. Its validation table is all-or-nothing: a zero-valued or guessed history,
an impossible count/disposition/trigger-ordinal tuple, or a mismatched provider
category or response shape is invalid.

HITL1 derives one opaque diagnostic reference before writing every provider-diagnostic
terminal incident. Its canonical input is exactly the research id, generation, stable
HITL1 node-attempt identity, final category, and, where present, the recovery trigger
category/ordinal, model-invocation count, automatic-retry count, disposition, and the
trigger/final observation response kind plus bounded HTTP status. It excludes the
configured-service label, configured endpoint authority, question, prompt, raw
exception, response body, full URL, credential, and every other presentation field.
Changing only a label or authority therefore cannot change the reference.
`ResearchRunExperience` copies the same facts and reference into `RunFailure`; it does
not reconstruct history from the journal. `RunFailure.recovery_action` is the closed
optional machine field `fresh_start` for the two dispositions whose final category
remains a transient provider failure: `exhausted` and
`retry_not_started_budget_consumed`. It is absent for
`retry_followed_by_terminal_failure`. When `fresh_start` is present, its generic
`next_action` is only congruent explanatory text; presentation suppresses it as a
separate action and renders the one static fresh-start command. Its existing
retryability value means a distinct new start may be attempted, never that the failed
graph can resume.

Returned-only `Working` updates retain their current local-wait meaning. They do not
claim that a retry is in progress because no streamed graph observation is available.
This is intentionally a typed result projection rather than derived inspection logic:
terminal CLI/TUI rendering and machine consumers receive the same facts as retained
observation, without reading bundle files or creating lifecycle authority.

### Causal observation without a competing diagnostic reference

The graph builder already injects its optional runtime-owned event recorder into
`NodeBuildDependencies`; HITL1 consumes that existing observation capability rather
than opening a session path or adding a new control seam. The existing
`RunEventRecorderProtocol.record()` interface in `domain/invocation.py` grows only the
optional closed keyword facts `recovery_correlation_id`, `provider_category`,
`retry_ordinal`, `backoff_milliseconds`, and `recovery_event_disposition`; the
`RunSessionStore` adapter and `RunEvent` validate the same fields. Recorder absence or
failure never changes graph routing. A first retry-eligible failure creates one opaque
recovery correlation id. Each HITL1 bridge/model invocation gets a distinct opaque
attempt id. Attempt and retry events carry the recovery correlation, closed provider
category when observed, retry ordinal, exact backoff milliseconds, and a closed
scheduled/exhausted outcome as applicable. They count graph calls to `run_agent()`, not
physical provider HTTP requests; SDK-internal retries remain unobserved and outside the
policy.

The retained event contract bounds a recovery correlation id and bridge/model-invocation
attempt id to opaque ASCII `[A-Za-z0-9_-]` values of 8--64 characters. A correlated
bridge/model-invocation attempt has its distinct attempt id and carries a closed
provider category only when a classified provider result was observed. A scheduled
retry has ordinal one, exactly 1,000 backoff milliseconds, and disposition `scheduled`;
an exhaustion event has ordinal one, disposition `exhausted`, and the final transient
provider category. These pairings reject a raw exception string, a different delay, or
a recovery disposition on the wrong event category without turning the journal into a
controller.

Cancellation is not a recovery terminal and must remain prompt. HITL1 records the
scheduled retry before entering the cancellable backoff, then propagates
`CancelledError` without awaiting, shielding, synthesizing, or forcing a post-cancel
recorder write. A previously durable scheduled observation may remain visible, but a
cancelled backoff does not promise a retained event, a terminal incident, or an
inspection timeline. This avoids making a projection I/O path delay or reinterpret
graph cancellation.

Successful recovery has no terminal diagnostic reference. Its events are correlated
only by recovery id. On a provider-diagnostic blocked terminal, the terminal incident's
reference and its optional bounded `RetainedRecoverySummary` projection are passed
through `RecordBearingLifecycleFact` to every publisher (`ResearchRunExperience` and
local session operations), then to the terminal event, trace, summary, inspect view,
and terminal-correlated session view. The summary is copied from the validated
checkpoint projection, never derived from events. No publisher derives a replacement
diagnostic reference. Pre-terminal events carry only the recovery correlation and never
the future terminal reference; only the terminal event and terminal projections copy
that reference.

Buffered pre-terminal events receive durable sequence numbers and are written before
any terminal event, trace, or summary is published, preserving
`attempt -> retry -> attempt -> exhaustion -> terminal` causal order. If pre-terminal
flush fails, the store marks the journal incomplete, does not append remaining buffered
pre-terminal events after the terminal, and continues terminal publication whenever its
terminal files remain writable. That failure never changes graph routing. Legacy events
and bundles remain valid when all new optional fields are absent.

### Diagnostic record handoff is honest under publication failure

A provider-diagnostic terminal reference must resolve to one honest safe record
whenever local storage is available. A provider-diagnostic terminal is a blocked
terminal carrying either a provider-recovery projection or a final safe
`ProviderObservation`; `diagnostic_location` is required for every such terminal and
remains absent for legacy terminals with neither. `ResearchRunExperience` first
validates the checkpoint incident and creates `RecordBearingLifecycleFact` with its
exact pre-derived reference and optional retained summary before calling any publisher
or generic diagnostic helper. A successful retained-session publication then marks the
shared failure's `diagnostic_location` as `session_bundle` and
`research_record_created=true`; that terminal publication replaces any older
suspended-session projection and returns a `RunSessionView.terminal_diagnostic_ref`
equal to the incident reference. Presentation renders an inspect command only when the
shared terminal contains an available session with the same research id and matching
terminal reference.

If retained publication is unavailable, `ResearchRunExperience` asks the support
journal to write the same already-derived reference, never a replacement. A successful
fallback marks `support_journal` and keeps `research_record_created=false`; an
unavailable write marks `unavailable` and also keeps it false. It constructs the final
`RunFailure` only after that result is known. The CLI and TUI show only those typed
fields and never read a bundle to fill a gap. This keeps diagnostics useful without
making the publisher, journal, or presentation an authority over the terminal incident.

### Presentation offers a fresh start, never a false resume

On every provider-diagnostic terminal result, standalone CLI and TUI state the final
safe category, phase, bridge/model-invocation count, recovery facts when present,
diagnostic reference/location, inspection command when applicable, and durability
truth. They render the final safe provider observation when present; otherwise they
render the recovery-trigger observation labelled as such, and render both with distinct
labels when both are available. They map only the shared `fresh_start` action to the
static command `make demo-real` and explicitly say to run it from `agent/`. When that
action is present, they suppress generic `next_action` as a second actionable control;
`retry_followed_by_terminal_failure` instead retains its final-category action and
offers no fabricated command. The command contains no question, answer, prompt,
diagnostic body, or URL; it starts a distinct run that asks for a question again.
An inspect command may appear only as a clearly labelled read-only diagnostic
observation when its typed session correlation is valid; it is never a recovery,
retry, resume, or competing next action. Same-process records remain inspection-only
after exit.

## Risks / Trade-offs

- [A second call doubles HITL1 failure cost and wait time] -> Cap it at two calls,
  retain the existing 30-second invocation budget, and use exactly one 1-second
  cancellable backoff.
- [A provider outage persists] -> Stop after the bound, publish one exhaustion
  incident, and give a fresh-run command rather than looping indefinitely.
- [Retry could conceal authentication/configuration or local I/O defects] -> Retry
  only the narrow supported transport/status classifier; all other categories take
  the current fail-closed path.
- [New observations leak provider details] -> Use existing closed enums and bounded
  fields plus a vetted label/sanitized-authority/status projection; redaction/contract
  tests reject unsafe content and full URLs.
- [Retry changes terminal routing] -> Keep the existing terminal `blocked` route;
  retry is only a bounded pre-terminal node behavior.
- [A buffered journal reverses causality or invents a second diagnostic reference] ->
  flush buffered observations before terminal publication and accept the exact
  incident reference as publisher input.
- [The terminal points at a diagnostic file that does not contain its reference] ->
  carry typed diagnostic-record location and write the same reference to the support
  journal only when retained-session publication is unavailable.

## Migration Plan

1. Add contracts and deterministic tests before implementation at bridge, HITL1,
   run-experience/session, and CLI/TUI seams.
2. Implement the bounded policy, terminal-reference handoff, and event projection
   without changing retained schema version when optional fields remain absent for
   legacy runs.
3. Run focused tests, then `cd agent && UV_OFFLINE=1 make verify`; credentialed live
   testing is supplemental.
4. Rollback consists of reverting the downstream `agent/` implementation and its
   OpenSpec deltas. Existing bundles remain inspectable because new fields are
   optional and events are observational.

## Open Questions

- None for implementation. The two-call ceiling, 1-second backoff, classifier, typed
  recovery dispositions, safe service fields, and diagnostic-reference handoff are
  deliberately part of this deterministic policy rather than runtime configuration.
