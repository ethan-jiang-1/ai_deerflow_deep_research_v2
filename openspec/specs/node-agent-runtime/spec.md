# node-agent-runtime Specification

> req: NOA-001, NOA-002, NOA-003, NOA-004, NOA-005, NOA-006, NOA-007, NOA-008, NOA-009, NOA-010, NOA-011, NOA-012, NOA-013, NOA-014, NOA-015

## Purpose
The bounded embedded node-agent runtime: parent-context bridge, explicit budgets, fail-closed tool/path policy, untrusted-source isolation, normalized results, and no self-initiated clarification.
## Requirements
### Requirement: LLM-Bearing Nodes inherit one parent runtime

The runtime-owned node-agent bridge SHALL implement a pure domain capability
protocol used by graph nodes. It SHALL resolve model/tools from
`TrustedRuntimeEnvelope`, seed an ephemeral child state/context with the already
validated parent sandbox and thread data, and invoke a bounded embedded
LLM-Bearing Node agent produced by the full-takeover factory. The agents layer
SHALL not import runtime; raw AppConfig, identity, host paths, sandbox internals,
and checkpoint identity SHALL not enter graph/node contracts, checkpoints, events,
or model-visible context. Each bound compiled child SHALL be created for one
`run_agent` request, invoked as a separate runnable with `checkpointer=None`, and
discarded after completion/cancellation; it SHALL never be cached across
actions/users/threads/attempts, mounted as a checkpoint-inheriting subgraph, or
create another sandbox lifecycle, thread namespace, or persistent controller.
(`NOA-001`)

#### Scenario: Parent context is preserved
- **WHEN** a fake node starts an embedded LLM-Bearing Node agent with a parent
  sandbox and thread-data fixture
- **THEN** authorized tools observe those same scoped values and no independent
  checkpointer or thread root is created

#### Scenario: Missing parent isolation fails
- **WHEN** a node requests an agent without validated parent sandbox/thread context
- **THEN** the factory refuses construction before a model or tool is invoked

### Requirement: LLM-Bearing Node execution has explicit budgets

Every node-agent policy SHALL specify a resolved model, exact tools, maximum model
calls, total tool calls, tool calls per model response, parallel tool-call limit,
total token budget, per-model-call output-token cap, per-tool-result size cap,
structured-result size cap, and wall-time budget. Before each text-only model call
the runtime SHALL use a deterministic no-network conservative upper bound over the
actual messages/tool schemas plus capped model output; non-text content SHALL
require an explicit conservative modality estimator or fail admission. It SHALL
then reconcile actual usage metadata. Missing usable token accounting SHALL
terminate with `usage_unavailable` before tool execution or another model call.
Tool results SHALL be bounded before re-entering model context. Exhausting any
budget SHALL stop the LLM-Bearing Node agent with a typed non-success finish reason
and cancel outstanding child work.

Every request-level tool-call limit SHALL be enforced cumulatively before tool
dispatch, including a model response that proposes parallel calls. If prior calls
plus the current response exceed the remaining request quota, middleware SHALL deny
the batch with a typed non-success result; the declared request limit SHALL never be
exceeded in observed dispatch accounting. (`NOA-002`)

#### Scenario: Work completes within budget
- **WHEN** a replay model returns a valid structured result within all configured limits
- **THEN** the adapter returns a successful normalized result with recorded usage and
  finish reason

#### Scenario: Budget exhaustion stops execution
- **WHEN** a fake model exceeds a declared model-call, tool-call, parallelism, token,
  tool-result, structured-result, or wall-time limit
- **THEN** execution terminates without another tool call and reports the exhausted
  budget as a failure

#### Scenario: Parallel response cannot cross request quota
- **WHEN** one tool call has already run under a two-call request limit and the next
  model response proposes two parallel calls
- **THEN** middleware rejects the response before either new call dispatches and
  observed request tool calls remain one

#### Scenario: Missing usage cannot disable the token budget
- **WHEN** a model response omits usable token accounting
- **THEN** the runtime emits terminal `usage_unavailable`, strips tool calls, and does
  not make another model request

### Requirement: Tool and path policy fails closed

The node-agent runtime SHALL expose only explicitly allowed tools and SHALL revalidate
the runtime tool name and path-bearing arguments before dispatch. Every allowed tool
SHALL have a typed ToolPolicySpec declaring path fields, effects, validator, and
cancellation class; unknown argument shapes and tools without an approved native
async/cancellable path SHALL be denied. Reads and writes SHALL stay within policy
roots; writes SHALL stay within the active attempt and SHALL never mutate graph phase,
gates, ledger, sibling attempts, package source, or host paths.

A bounded request tool window SHALL cap the number of tool calls that execute in one
agent run. When a model response requests more parallel tool calls than the remaining
window, the runtime SHALL keep only the first calls that fit the window and drop the
excess; it SHALL NOT fail the run, and the dropped calls SHALL NOT execute. After the
window is exhausted, later model turns SHALL have tools removed so the agent produces
its structured answer. Genuine policy violations — a non-allow-listed tool, a traversal
path, an ineligible spec, or a write outside the attempt root — SHALL still fail closed
before dispatch. (`NOA-003`)

#### Scenario: Allowed attempt write succeeds
- **WHEN** a fake file tool writes a canonical path within the active attempt write root
- **THEN** policy authorizes the call and records its scoped artifact reference

#### Scenario: Forged tool or path is denied
- **WHEN** a model requests an unlisted tool, traversal path, symlink escape, cross-attempt write, or gate/ledger mutation
- **THEN** middleware blocks execution, leaves the target unchanged, and returns a typed policy denial

#### Scenario: Eager over-request is truncated to the remaining window
- **WHEN** a model response requests more parallel tool calls than the remaining
  bounded request window
- **THEN** the runtime keeps only the first calls that fit the window, drops the
  excess without executing them, and does not fail the run

### Requirement: External source content remains untrusted data
The runtime SHALL keep package system/policy prompts separate from external source payloads. Source text SHALL only enter model context as delimited untrusted data or an artifact reference, and its instructions SHALL never grant tool, path, phase, gate, or ledger authority.

#### Scenario: Benign source remains data
- **WHEN** ReplayChatModel receives a normal source fixture
- **THEN** the source is present only in the untrusted data channel and the agent can produce output within its existing policy

#### Scenario: Prompt-injected source cannot escalate
- **WHEN** a source fixture asks the agent to ignore rules, call a forbidden tool, or mark a gate passed
- **THEN** the system prompt remains unchanged, forbidden actions are denied, and no control or ledger state changes

### Requirement: Results, progress, failure, and cancellation are normalized

The adapter SHALL validate structured model output and project stable redacted
progress events through the supported stream-writer API. Malformed output SHALL fail;
outer `CancelledError` SHALL propagate after child/provider cleanup and SHALL not
leave background work running.

The optional endpoint-authority observation SHALL derive only from the exact selected
model configuration's `base_url` field. It SHALL normalize only a safe HTTP(S)
authority and SHALL emit no observation for a missing, malformed,
credential-bearing, conflicting, or retired-alias value. `openai_api_base` and
`api_base` are retired observation aliases: their presence, whether alone or
alongside `base_url`, SHALL not select a model, change provider behavior, alter
lifecycle or retry policy, or cause model-object reflection. The observation remains
a projection only and SHALL not reveal a path, query, fragment, credential, raw
configuration, or endpoint authority beyond the existing safe normalization contract.

#### Scenario: Valid result and progress are projected
- **WHEN** a fake agent emits progress and a result matching the node output schema
- **THEN** the parent receives stable progress records and one validated normalized result without raw secrets or source bodies

#### Scenario: Cancellation cannot become success
- **WHEN** the outer task is cancelled while a fake embedded agent has child work in flight
- **THEN** child work is cancelled and awaited, cleanup completes, and no successful result is emitted

#### Scenario: Selected base URL produces a safe observation
- **WHEN** the exact selected model configuration contains a safe normalizable
  `base_url`
- **THEN** the node-agent result may carry only its normalized endpoint authority and
  no model, provider, retry, route, or lifecycle decision changes

#### Scenario: Retired alias produces no endpoint observation
- **WHEN** the selected model configuration contains `openai_api_base` or `api_base`,
  whether or not it also contains `base_url`
- **THEN** the result contains no endpoint-authority observation and the alias does
  not affect model creation, provider selection, or lifecycle behavior

#### Scenario: Unsafe base URL fails closed as an observation
- **WHEN** the selected `base_url` is malformed, contains userinfo, conflicts with a
  retired alias, or cannot normalize to a safe authority
- **THEN** the result contains no endpoint-authority observation and does not expose
  the rejected value or create another configuration reader

### Requirement: Clarification belongs only to graph HITL nodes

The node-agent factory SHALL omit `ask_clarification` and clarification middleware.
An LLM-Bearing Node agent SHALL not create a user interrupt; only a graph-owned HITL
node introduced by a later change can do so. (`NOA-006`)

#### Scenario: Node cognition cannot request clarification
- **WHEN** a model proposes an `ask_clarification` action during a node-agent run
- **THEN** the runtime denies the action without creating a graph interrupt or user-
  input artifact

#### Scenario: Normal node toolset has no clarification
- **WHEN** the node-agent factory assembles a normal direct branch toolset
- **THEN** the clarification tool and middleware are absent without changing its
  declared model, tool, budget, or graph-owned HITL behavior

#### Scenario: Fabricated clarification call is refused
- **WHEN** a direct node-agent model output fabricates an `ask_clarification` call
- **THEN** runtime enforcement rejects it without a user interrupt, candidate
  admission, retry, or graph lifecycle action

### Requirement: Node-agent failures retain a closed causal category for the parent graph

The existing bounded provider classification, redaction, cancellation, and graph-owned
failure-routing guarantees remain unchanged. The direct runtime dependency declaration
for `httpx>=0.28,<0.29` and `openai>=2.45,<3`, with matching lock metadata, SHALL live
under `deep_research_harness/`; the project-structure import policy continues to admit
those namespaces only for the raw-binding bridge. This root migration SHALL not make a
node-agent bridge a Bundle selector, State writer, checkpoint authority, or recovery
path. (`NOA-007`, `NOA-008`, `PRS-002`)

#### Scenario: Node-agent dependency metadata follows the Harness root
- **WHEN** structural validation checks the direct bridge dependencies after the move
- **THEN** it finds their declaration and lock metadata beneath
  `deep_research_harness/` without widening node-agent lifecycle authority

### Requirement: Node-agent execution policies are named and independently bounded

The runtime SHALL bind each distinct direct model-calling LLM-Bearing Node branch to
a named node-agent execution policy with explicit budgets and allowed tool names.
One branch's policy SHALL not grant its tools, budget, or recovery behavior to
another branch. (`NOA-008`)

#### Scenario: A node-agent budget expiry remains classified
- **WHEN** a node-agent invocation exhausts its wall-time budget
- **THEN** its typed failure retains the existing bounded budget classification and
  no raw exception text for the owning branch to handle

#### Scenario: A phase budget expiry remains classified
- **WHEN** a node-agent invocation exhausts its wall-time budget
- **THEN** its typed failure retains the existing bounded budget classification and
  no raw exception text for the owning branch to handle

#### Scenario: Topic planning no longer inherits the HITL1 wall-time budget
- **WHEN** real HITL1 and topic planning are assembled in one recipe
- **THEN** they receive distinct named node-agent policies and topic planning uses
  its existing 60-second bound without changing HITL1's configured bound

### Requirement: Semantic-intake invocations remain bounded zero-tool node work

The existing runtime node-agent bridge SHALL execute HITL1 semantic-intake requests as
independent zero-tool structured requests under the trusted HITL1 policy. The bridge
SHALL make at most one model call for each request and SHALL not interpret candidates,
retry, route, write checkpoint state, or grant action authority. HITL1 owns the
cross-request three-call semantic budget and recovery. (`NOA-009`)

#### Scenario: Semantic intake cannot receive tools
- **WHEN** HITL1 sends a semantic-intake request after a human reply
- **THEN** the trusted bridge receives `tools_enabled=false` and no tool policy or
  graph action is available to that invocation

### Requirement: Node-agent bridge consumes the shared final prompt projection

Before constructing an embedded LLM-Bearing Node child state, the node-agent bridge
SHALL obtain the shared final Node Cognitive Control Program projection from the
agents-owned renderer. The renderer SHALL validate the mandatory capability ref
before it returns the projection. The bridge SHALL reuse that projection as the
child's system and user messages and SHALL NOT reconstruct policy from request
fields, a legacy binding mode, runtime configuration, or a caller-supplied system
prompt. (`NOA-010`)

#### Scenario: Runtime uses the renderer's exact projection
- **WHEN** a direct branch is invoked through the bridge
- **THEN** its child receives the same ordered base/capability/assignment/untrusted
  projection reviewed by the catalog, without a second runtime policy source

#### Scenario: Invalid capability admission reaches no runtime resolver
- **WHEN** a request has a missing, invalid, unknown, or package-mismatched ref
- **THEN** prompt admission produces the existing bounded failure before the bridge
  resolves tools or a model, or constructs an embedded agent

#### Scenario: Runtime message construction does not fork from the review projection
- **WHEN** the bridge executes a request corresponding to a canonical prompt-catalog case
- **THEN** its child system policy and human message equal that case's shared rendered
  projection while runtime-only metadata remains outside the catalog

#### Scenario: Canonical bridge capture proves source-faithful text
- **WHEN** a deterministic test runs a graph-owned canonical prompt case through the
  bridge with fake model and tool bindings that capture construction and child state
- **THEN** captured policy and first human message exactly equal the shared renderer
  projection without the catalog receiving a runtime-envelope fact

### Requirement: Runtime execution admits capability posture before model-visible work

The node-agent bridge SHALL validate the rendered capability posture against the
request tool window before it resolves tools, a model, or an embedded agent. A
forbidden posture SHALL reject any nonzero tool request; a required posture SHALL
reject a disabled, empty, or out-of-policy window. A missing, invalid, unknown, or
package-mismatched capability ref SHALL fail at the same pre-resolver admission
boundary. The bridge SHALL not interpret capability policy as graph route, parser,
state writer, repair controller, or lifecycle authority. (`NOA-011`)

#### Scenario: A forbidden capability cannot enable a tool window
- **WHEN** a forbidden capability is paired with an enabled tool request
- **THEN** the bridge returns its typed non-success result before tool resolution,
  model construction, or tool dispatch

#### Scenario: A required capability cannot be bypassed
- **WHEN** a required capability is missing, invalid, package-mismatched, disabled,
  or has no eligible configured tool
- **THEN** the bridge returns its existing typed non-success result without a generic
  capability, a legacy renderer path, or a model invocation

#### Scenario: Required tool posture is mechanically aligned
- **WHEN** a required-tool request declares its capability and the trusted runtime
  supplies one matching allowed tool
- **THEN** the bridge binds that tool under its existing policy and records the
  bounded call window without exposing another configured tool

#### Scenario: Tool disagreement fails closed
- **WHEN** a capability forbids tools, has no permitted configured tool, or disagrees
  with its request window or node-agent execution policy
- **THEN** the bridge returns its typed non-success result without model invocation,
  tool dispatch, retry, or graph action

#### Scenario: Wave2 does not inherit HITL1 tool posture
- **WHEN** a mixed real recipe resolves `wave2_synthesis`
- **THEN** both synthesis catalog cases use their dedicated zero-tool policy and no
  model-visible tool, independently of HITL1's policy or budget

### Requirement: Branch review evidence distinguishes requested from enforced execution posture

Runtime review evidence SHALL identify each ledger branch's requested tool window
separately from bridge-enforced capability posture, actual eligible-tool intersection,
and bounded safe failure projection. A real bridge test with fake model/tool bindings
SHALL prove that distinction for the canonical case; a prompt or capability resource
alone SHALL not. It SHALL not change provider, tool, retry, route, checkpoint, or
lifecycle behavior.

#### Scenario: Tool posture is reviewed
- **WHEN** a branch requests a tool posture through local capability composition
- **THEN** deterministic evidence identifies the bridge enforcement seam without claiming that prompt text enforces it

### Requirement: Final report composition uses an independently bounded zero-tool bridge

The runtime SHALL assemble the final-delivery composer through a named dedicated
zero-tool execution policy with explicit one-invocation, token, result-size, and
wall-time bounds. Policy, provider, timeout, cancellation, and structured-output
failure SHALL retain the runtime's existing closed non-success result and SHALL not
grant retry, publication, route, or lifecycle authority to the bridge. (`NOA-013`)

#### Scenario: Composer cannot inherit another node's tool posture
- **WHEN** a real final-delivery recipe resolves its composer bridge
- **THEN** it receives its dedicated forbidden-tool policy and a failure produces no
  model-owned retry, artifact, route, or terminal result

### Requirement: Provider timeout diagnostics retain a closed observed origin

For each admitted provider timeout that the runtime bridge positively identifies as
either its own expired wall-time budget or the supported `openai.APITimeoutError`
branch, the bridge SHALL attach respectively only `bridge_wall_time_budget` or
`provider_sdk_timeout` to that typed `ProviderObservation`. The origin SHALL be absent
when neither cause was positively observed, including the separately handled
`httpx.TimeoutException`, a bare inner `TimeoutError`, and legacy/generic `no_response`
results; it SHALL not be inferred from category, timing, service label, or endpoint
authority. It SHALL contain no raw exception text, provider body, prompt, credential,
full URL, host path, or request payload. The existing provider failure category,
response observation, cancellation behavior, and retry eligibility SHALL remain
unchanged. (`NOA-001`)

#### Scenario: Bridge wall-time is not reported as an SDK timeout
- **WHEN** the bridge wall-time budget expires while a provider request is admitted
- **THEN** the typed provider timeout retains the closed bridge-budget origin and no
  raw exception detail

#### Scenario: SDK timeout remains distinguishable
- **WHEN** an admitted provider request raises the supported provider-SDK timeout
- **THEN** the typed provider timeout retains the distinct closed SDK-timeout origin
  while preserving the existing safe no-response observation

#### Scenario: Legacy or generic no-response does not invent an origin
- **WHEN** a legacy projected provider observation has no bridge-supplied timeout origin
- **THEN** downstream projection preserves the origin as absent and does not infer one
  from category, timestamp, service label, or endpoint authority

#### Scenario: Transport timeout does not claim an SDK origin
- **WHEN** the separately handled `httpx.TimeoutException` produces the existing
  admitted `provider.timeout` result
- **THEN** its origin remains absent while its existing category, safe no-response
  observation, and retry eligibility remain unchanged

### Requirement: Node-agent execution receives bound Bundle context without lifecycle authority

The runtime-owned node-agent bridge SHALL receive only ephemeral, runtime-bound context
for the selected Run Bundle. It MAY use contained artifact/evidence interfaces granted
by the parent graph, but SHALL not derive `bundle_id`, construct a Bundle path, select a
checkpoint, persist lifecycle State, or make a Bundle available/unavailable decision.
The parent Bundle lifecycle/graph control boundary remains the sole owner of those
facts. (`NOA-014`)

#### Scenario: Agent-facing context cannot redirect a Run Bundle
- **WHEN** a model/tool-facing node-agent request includes path-like or identity-like content
- **THEN** the bridge treats it as untrusted data and no Bundle selection, State write, or lifecycle action changes

### Requirement: Node-agent budget stops expose one closed diagnostic subreason

The runtime node-agent bridge SHALL map each known budget stop to one closed
budget-stop reason defined by `run-event-journal`: `request_content_unestimable`,
`model_call_limit`, `token_admission`, `per_call_output_cap`,
`total_token_budget`, `tool_calls_per_response`, `parallel_tool_calls`,
`total_tool_calls`, `bridge_wall_time`, or `unknown`. It SHALL carry only that safe
reason through a private per-invocation recording projection to the existing Event
Journal producer. It SHALL NOT expose middleware detail, exception text, request
content, model output, tool body, provider payload, credential, or endpoint through
the normalized result or Journal.

The bridge SHALL preserve the existing `NodeFinishReason`, normalized
`RunFailureCode`, provider-timeout origin, cancellation behavior, recovery ownership,
and parent graph result; it SHALL NOT add this attribution to `NodeProblem` or make it
part of a graph-facing node result contract. A budget-stop reason is diagnostic
attribution only; it SHALL NOT grant the bridge retry, route, checkpoint,
Bundle-selection, or lifecycle authority. (`NOA-015`)

#### Scenario: Middleware budget boundaries map to a closed reason
- **WHEN** a model-call, token-admission, output-cap, total-token, or tool-call bound
  stops a node-agent invocation
- **THEN** the existing safe result category remains unchanged and the Journal producer
  receives the matching allowed budget-stop reason with no raw middleware detail

#### Scenario: Bridge wall time remains a timeout with bounded attribution
- **WHEN** the bridge's existing wall-time deadline expires
- **THEN** its existing timeout category and origin remain unchanged while the Journal
  can retain only `bridge_wall_time` as the associated budget-stop reason

#### Scenario: A non-budget result cannot gain a budget reason
- **WHEN** a node-agent invocation succeeds, is cancelled, fails provider recovery, or
  fails another policy or structured-output boundary
- **THEN** it retains the existing normalized behavior and no budget-stop reason is
  published unless the bridge has a known budget stop
