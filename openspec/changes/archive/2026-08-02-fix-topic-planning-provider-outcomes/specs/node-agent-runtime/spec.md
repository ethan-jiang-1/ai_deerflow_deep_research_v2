## MODIFIED Requirements

### Requirement: Node-agent failures retain a closed causal category for the parent graph

`RuntimeNodeAgentBridge` SHALL translate model resolver, tool resolver, agent
construction/invocation, provider timeout, policy stop, and structured-output
failure into a typed, bounded `NodeProblem` before returning control to a graph node.
`NodeProblem` SHALL contain only a closed run-failure category, direct-or-unknown
certainty, safe operation/phase attribution, an optional opaque diagnostic reference,
and the optional safe `ProviderObservation` defined below. It SHALL not contain raw
exception strings, provider bodies, credentials, paths, user input, tool output, or
model output.

`RuntimeNodeAgentBridge` SHALL remain a one-invocation boundary. Provider
classification, provider observation, configured-service label, and configured
endpoint-authority behavior SHALL be admitted only when the immutable named
`ExecutionPolicy` explicitly declares the closed model-service observation admission
and the request has `tools_enabled=false`. That admission value SHALL default to
denied. The existing HITL1 structured-brief policy and the existing topic-planning
structured-plan policy SHALL explicitly opt in; every other policy SHALL remain
denied unless a separately approved requirement changes its policy. The bridge SHALL
use the policy admission and request tool posture, not `NodeAgentContext.node_name` or
the policy-name string, to make that decision. A non-admitted zero-tool request and
every tools-enabled request SHALL retain its existing safe failure mapping without a
model-service observation or new retry eligibility under this requirement.
`ExecutionPolicy` SHALL reject an admission value that is not a
`ProviderObservationAdmission` member, including a raw string equal to one of that
enum's serialized values.

For an admitted zero-tool request, the bridge SHALL map its own wall-time expiry, a
direct public `httpx.TimeoutException`, or a direct public
`openai.APITimeoutError` to `provider.timeout` with a safe `no_response`
observation. It SHALL map `provider.unavailable` only from a direct
`ConnectionError`, direct `httpx.NetworkError`, direct public
`openai.APIConnectionError`, an allowlisted connection-related `OSError` errno
(`ECONNABORTED`, `ECONNREFUSED`, `ECONNRESET`, `ENETDOWN`, `ENETUNREACH`,
`EHOSTDOWN`, `EHOSTUNREACH`, or `ETIMEDOUT` when defined by the platform), or a
supported status (`408`, `429`, `500`, `502`, `503`, or `504`) carried directly by
public `httpx.HTTPStatusError` or public `openai.APIStatusError`.
`httpx.TimeoutException` and `openai.APITimeoutError` SHALL be evaluated before
their broader transport/connection classes. The generic `OSError` branch SHALL be
evaluated only after excluding a naked inner `TimeoutError`, even if that
`TimeoutError` carries `ETIMEDOUT`; the latter is unclassified rather than a provider
timeout or outage. The bridge SHALL map observed `401` or `403` from those direct
public status carriers to the existing authentication category, and SHALL fail closed
with the existing non-transient category for every other status or unclassified
exception.

For a direct `NodeAgentStop`, the bridge SHALL preserve the trusted non-success
finish reason and use this closed projection: `USAGE_UNAVAILABLE` maps to
`provider.usage_unavailable`, `BUDGET_EXHAUSTED` maps to `budget.exhausted`, and
`POLICY_DENIED` maps to `policy.denied`. An unsupported stop reason SHALL map
fail-closed to `internal.unexpected`. A node-agent stop SHALL never be projected as
`tool.execution_failed`. Existing non-stop tools-enabled result mappings, including
the required-tool-count validation, SHALL remain unchanged. Stop detail and the
original exception text SHALL not cross the bridge, create a provider observation, or
create retry eligibility.

The bridge SHALL treat the admitted `httpx` and OpenAI SDK classes as a closed direct
boundary: it SHALL NOT walk `__cause__` or `__context__`, inspect a response body,
header, request URL, or generic exception attribute. From a direct public status
carrier it SHALL read only `httpx.HTTPStatusError.response.status_code` or
`openai.APIStatusError.status_code`, validate it is in `[100, 599]`, and discard the
carrier. Every direct public `httpx.HTTPStatusError` or `openai.APIStatusError` from
an admitted zero-tool request, including an unsupported status, SHALL still carry its
bounded safe HTTP observation; that observation SHALL not make an unsupported status
retry-eligible or change its existing non-transient category. For an admitted request,
the bridge SHALL use an explicit deadline scope whose expired state distinguishes its
own wall-time expiry from a bare `TimeoutError` raised inside the invocation; only the
expired scope maps to `provider.timeout`. A naked inner `TimeoutError` is an
unclassified exception and SHALL not become retry-eligible.

The canonical frozen, extra-forbid `ProviderObservation` from
`domain/run_experience.py` SHALL retain its existing bounded configured-service label,
configured endpoint authority, response kind, optional HTTP status, and optional
closed timeout origin. The admitted zero-tool wall-time, direct `httpx`/OpenAI SDK
timeout or network, allowlisted `OSError`, and classified HTTP-response branches SHALL
carry that observation, as SHALL a non-retryable direct public HTTP response. The
legacy `PermissionError` authentication mapping may leave it absent because it has no
safe response fact and SHALL not fabricate `no_response`, a label, or an authority.
For the default resolver, a valid label is only the exact selected `ModelConfig.name`
matching `[A-Za-z0-9._-]{1,96}`: it SHALL select that configuration explicitly and
pass the same name to `create_chat_model`. A valid authority is only the normalized
`http` or `https` `scheme://host[:non-default-port]` form derived from the exact same
selected configuration's `base_url`, `openai_api_base`, or `api_base`: every present
candidate SHALL be absolute, have a valid host and port, and contain no user info. Its
path, query, and fragment SHALL be discarded before the lower-case authority is
normalized to at most 253 ASCII characters and compared with the other candidates.
All present candidates SHALL normalize to that one authority; otherwise the authority
is absent. The resolver SHALL return a frozen `ResolvedNodeModel` binding with those
possible values. A custom resolver may supply a label and authority only by returning
that explicit binding; an existing raw-model return remains valid but has neither. The
bridge SHALL not infer either value from a model object, provider class, model
attribute, config-list entry other than the exact selected configuration,
`ModelConfig.model`, or a provider-supplied display string. Timeout and connection
results use `no_response`; classified HTTP responses use `http_response` with their
status. Raw or full URLs, base URL paths, queries, fragments, user info, model
identifiers, provider bodies, credentials, and exception text SHALL never cross the
bridge.

`CancelledError` SHALL continue to propagate. The bridge SHALL preserve every
per-invocation execution budget and SHALL not issue provider retries itself. Graph
nodes SHALL receive enough typed information to choose their existing route and publish
a safe compact terminal incident when appropriate; they SHALL not need to catch all
exceptions and erase the causal category. Unknown exceptions SHALL map to
`internal.unexpected`, not an invented checkpoint inconsistency. Other closed failure
categories SHALL retain their existing mapping and SHALL not become retryable by
implication. The `deerflow_research/` runtime dependency declaration SHALL directly
require `httpx>=0.28,<0.29` and `openai>=2.45,<3`, with matching lock metadata; this
classifier SHALL not depend on an incidental transitive installation. The
`project-structure` mechanical import policy SHALL admit these two namespaces only for
this raw-binding bridge and SHALL reject them from every other runtime module or layer.
(`NOA-007`, `NOA-008`, `PRS-002`)

#### Scenario: Configuration error reaches a node without raw exception text
- **WHEN** the bridge cannot resolve a configured model for a real HITL-1 brief
- **THEN** HITL-1 receives a typed `configuration.model_missing` problem, may route to
  its declared blocked path, and a later lifecycle result can explain that safe
  category without exposing the resolver exception

#### Scenario: Closed node-agent stops retain their real category
- **WHEN** a zero-tool topic-planning invocation raises a trusted
  `NodeAgentStop` with `USAGE_UNAVAILABLE`, `BUDGET_EXHAUSTED`, or `POLICY_DENIED`
- **THEN** the result retains that finish reason and respectively exposes
  `provider.usage_unavailable`, `budget.exhausted`, or `policy.denied` with no provider
  observation, retry eligibility, raw detail, or `tool.execution_failed` category

#### Scenario: Unsupported node-agent stop fails closed
- **WHEN** a trusted `NodeAgentStop` has a non-success reason outside the three
  supported stop mappings
- **THEN** the bridge returns `internal.unexpected` without retaining the stop detail
  or inventing a tool or provider failure

#### Scenario: Existing non-stop tool result mapping remains outside stop projection
- **WHEN** a tools-enabled invocation fails the existing required-tool-count
  validation
- **THEN** it retains its existing non-stop tool result mapping, while a policy or
  budget `NodeAgentStop` is not given `tool.execution_failed`

#### Scenario: Cancellation remains cancellation
- **WHEN** the outer lifecycle task is cancelled while a child agent is active
- **THEN** `CancelledError` propagates after child cleanup and no failure category is
  published as a successful, blocked, or graph-cancelled result

#### Scenario: HITL1 admission remains explicit
- **WHEN** the existing HITL1 zero-tool policy invokes its admitted model service and
  reaches its wall-time limit
- **THEN** the bridge returns one `provider.timeout` problem with phase attribution, a
  vetted service label when available, `no_response`, no HTTP status, and no bridge
  retry

#### Scenario: Topic-planning timeout is admitted by policy rather than node name
- **WHEN** the explicitly admitted topic-planning zero-tool policy directly raises
  `httpx.ReadTimeout`
- **THEN** the bridge returns one `provider.timeout` problem with a vetted
  `no_response` observation after one invocation, without consulting the node name or
  issuing a retry

#### Scenario: Supported transient HTTP response reaches the graph unchanged
- **WHEN** an admitted bounded zero-tool invocation raises a direct public
  `httpx.HTTPStatusError` or `openai.APIStatusError` with status `503`
- **THEN** the bridge returns one `provider.unavailable` problem with the safe `503`
  status and no raw provider detail, after at most that one invocation

#### Scenario: OpenAI SDK transport wrapper is classified without introspection
- **WHEN** an admitted bounded zero-tool invocation directly raises public
  `openai.APITimeoutError` or `openai.APIConnectionError`
- **THEN** the bridge returns respectively `provider.timeout` or `provider.unavailable`
  with `no_response`, without reading a wrapped cause, response body, header, URL, or
  generic exception attribute

#### Scenario: HTTP authentication remains explicit but is not retried
- **WHEN** an admitted bounded zero-tool invocation raises a direct public
  `httpx.HTTPStatusError` or `openai.APIStatusError` with status `401` or `403`
- **THEN** the bridge returns the existing authentication category with the safe HTTP
  observation and does not label the result retry-eligible

#### Scenario: Custom resolver cannot infer a service label
- **WHEN** a custom model resolver returns a raw model rather than an explicit
  `ResolvedNodeModel` service-label/authority binding
- **THEN** a classified provider result carries no configured-service label or endpoint
  authority and the bridge does not inspect the model object, its class, or a
  configuration-list entry to invent either

#### Scenario: Configured endpoint authority strips optional URL components
- **WHEN** the exact selected model configuration has
  `base_url=https://api.example.test/v1?tenant=private#fragment` and a direct provider
  response has status `503`
- **THEN** the bridge carries only `https://api.example.test` with the safe status,
  never `/v1`, the query, fragment, user info, credential, or raw configured value

#### Scenario: Ambiguous or unsafe endpoint configuration is omitted
- **WHEN** the selected model configuration has conflicting endpoint aliases or an
  endpoint with user info, an unsupported scheme, or an invalid host or port
- **THEN** a classified provider result may retain its safe label and status/no-response
  fact but carries no endpoint authority

#### Scenario: Generic local OSError is not misclassified as provider outage
- **WHEN** an invocation raises an `OSError` whose errno is not in the supported
  connection-related allowlist
- **THEN** the bridge returns its existing non-transient failure category and does not
  label the result `provider.unavailable` for graph recovery

#### Scenario: Unsupported HTTP status remains visible but non-retryable
- **WHEN** an admitted bounded zero-tool invocation raises a public
  `httpx.HTTPStatusError` with an unsupported status such as `400`
- **THEN** the bridge returns its existing non-transient category with the safe `400`
  observation and does not label the result retry-eligible

#### Scenario: Tool HTTP failure is not labelled as a model service
- **WHEN** a tools-enabled node-agent invocation raises a direct HTTP transport or
  status error
- **THEN** the bridge preserves its existing safe failure mapping without attaching a
  configured model-service observation or making the result newly retry-eligible

#### Scenario: A denied zero-tool policy does not inherit provider admission
- **WHEN** a trusted non-admitted zero-tool policy invokes a direct transport or public
  status error
- **THEN** the bridge preserves that request's existing failure mapping and attaches no
  configured model-service observation or new retry eligibility

#### Scenario: Inner timeout is not mistaken for the bridge deadline
- **WHEN** the invoked agent or a tool raises a bare `TimeoutError`, including one
  whose errno is `ETIMEDOUT`, before the bridge's wall-time deadline expires
- **THEN** the bridge returns its existing non-transient unclassified category and does
  not label the result `provider.timeout` or eligible for graph recovery

#### Scenario: Bridge does not hide cancellation in a retry
- **WHEN** an outer lifecycle task is cancelled while a provider invocation is in flight
- **THEN** `CancelledError` propagates after child cleanup, no retry is issued, and no
  provider terminal incident is fabricated

#### Scenario: Direct classifier namespaces stay inside the raw-binding bridge
- **WHEN** architecture governance scans a direct `httpx` or `openai` import
- **THEN** it accepts the import only in `runtime/node_agent_bridge.py` and rejects the
  same import from every other runtime module or layer

#### Scenario: Authentication and unknown failures remain non-transient
- **WHEN** a provider authentication failure, unsupported HTTP response, or
  unclassified invocation exception occurs
- **THEN** the bridge returns its existing closed category and does not label it as
  timeout or unavailable for graph recovery
