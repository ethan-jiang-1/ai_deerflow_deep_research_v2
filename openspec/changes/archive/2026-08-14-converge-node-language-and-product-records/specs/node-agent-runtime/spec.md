> req: NOA-001, NOA-002, NOA-006, NOA-008, NOA-010, NOA-011

## RENAMED Requirements

- FROM: `### Requirement: Phase agents inherit one parent runtime`
- TO: `### Requirement: LLM-Bearing Nodes inherit one parent runtime`
- FROM: `### Requirement: Phase-agent execution has explicit budgets`
- TO: `### Requirement: LLM-Bearing Node execution has explicit budgets`
- FROM: `### Requirement: Phase execution policies are named and independently bounded`
- TO: `### Requirement: Node-agent execution policies are named and independently bounded`
- FROM: `### Requirement: Phase-agent bridge consumes the shared final prompt projection`
- TO: `### Requirement: Node-agent bridge consumes the shared final prompt projection`

## MODIFIED Requirements

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
