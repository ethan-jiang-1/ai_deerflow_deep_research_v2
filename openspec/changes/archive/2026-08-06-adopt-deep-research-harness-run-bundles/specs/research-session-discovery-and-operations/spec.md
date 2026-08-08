> req: RDO-001, RDO-002, RDO-003, RDO-004, RDO-005, RDO-006, RDO-007

## ADDED Requirements

### Requirement: Scoped Run Bundle discovery and operations use Bundle-local authority

Supported local discovery, open, status, control, and refinement operations SHALL use
the same trusted conversation scope and Bundle lifecycle contract as the public tool.
They SHALL validate a supplied `bundle_id` or perform bounded scoped discovery of
Bundle directories and Bundle-local State. They SHALL not enumerate raw foreign paths,
use a private session index, recreate historical runtime context, inspect an external
checkpoint, or resolve a session reference. A missing, foreign, corrupt, or ambiguous
candidate SHALL return a redacted typed outcome with its legal next action. (`RDO-007`)

#### Scenario: Local operation finds an active Bundle without an index
- **WHEN** a supported local operation has trusted scope but no Current Bundle Handle
- **THEN** it selects exactly one active available Bundle from scoped directories/State or returns a bounded no-selection outcome

#### Scenario: Operation cannot cross scope through an opaque id
- **WHEN** a local caller supplies another scope's `bundle_id`
- **THEN** the operation exposes no Bundle facts and performs no provider, graph, or content access

## RENAMED Requirements

- FROM: `### Requirement: Authorized local discovery projects bounded owned sessions`
- TO: `### Requirement: Authorized local discovery projects bounded Bundle facts`
- FROM: `### Requirement: Trusted runtime resolution precedes a cross-session operation`
- TO: `### Requirement: Trusted runtime resolution precedes a scoped Bundle operation`
- FROM: `### Requirement: Operations retain checkpoint and pending-interrupt authority`
- TO: `### Requirement: Operations use Bundle-local State and pending-interaction authority`
- FROM: `### Requirement: Authorized broker resume preserves typed advertised responses`
- TO: `### Requirement: Authorized resume preserves typed advertised responses`
- FROM: `### Requirement: Broker binds visible controls under its existing lock`
- TO: `### Requirement: Bundle State writer resolves visible controls at its safe boundary`

## MODIFIED Requirements

### Requirement: Authorized local discovery projects bounded Bundle facts

The runtime SHALL provide local discovery only through the same trusted-scope Bundle
lifecycle resolver as the public tool. It SHALL validate a Current Bundle Handle or scan
only actual Bundle directories and Bundle-local State beneath the current trusted scope;
it SHALL not use an owner/profile index, retained manifest, raw path, or another
principal/profile's data. It SHALL discover no more than the one legal active Bundle and
shall return bounded active/ended/unavailable/ambiguous facts without creating,
repairing, or pruning a Bundle. (`RDO-001`)

#### Scenario: Foreign and unknown Bundles are indistinguishable
- **WHEN** discovery or open receives a foreign, unknown, corrupt, or deleted opaque Bundle id
- **THEN** it returns the same bounded unavailable or denied projection without a path, owner, provider, or existence hint

### Requirement: Trusted runtime resolution precedes a scoped Bundle operation

The operation boundary SHALL receive trusted runtime scope from a runtime adapter or
fixed local-profile adapter, never from CLI/TUI arguments. It SHALL resolve only a
selected Bundle within that scope and SHALL not synthesize a historical `ToolRuntime`,
rebuild context from a session manifest, or take AppConfig, host paths, provider
connection, sandbox id, user, thread, recipe, or implementation map from caller input
or retained data. Read-only status/inspection SHALL not initialize a sandbox or graph
capabilities. (`RDO-002`)

#### Scenario: Read-only open does not initialize a sandbox
- **WHEN** an authorized principal opens or reads status for an available Bundle
- **THEN** it uses the read-only Bundle verifier and does not initialize a parent sandbox or construct graph invocation capabilities

### Requirement: Operations use Bundle-local State and pending-interaction authority

`open` and `status` SHALL be read-only. `resume`, `cancel`, and `refine` SHALL
revalidate Bundle-local State through the lifecycle module and invoke only its typed
control path. `resume` SHALL derive the current pending request from Bundle-local State,
compare the correlated expected request id, validate the submitted typed response against
that request, and repeat correlation/response-kind checks under the Bundle State writer.
`refine` SHALL submit its separate bounded refinement through the same boundary and
shall not replace a pending response. A manifest, binding, caller phase, retained cursor,
or external checkpoint SHALL NOT be lifecycle authority. (`RDO-003`)

#### Scenario: Stale response remains rejected after local open
- **WHEN** an available Bundle receives a response not correlated with its latest Bundle-local pending interaction
- **THEN** resume rejects it without State mutation or graph-node invocation

#### Scenario: A refinement remains distinct from a response
- **WHEN** a local caller submits a valid refinement while a Bundle awaits an input response
- **THEN** the operation admits it only for the next safe control point and leaves the current pending interaction unchanged

### Requirement: Discovery and operation outputs fail closed and remain redacted

All discovery and operation outputs SHALL fail closed for unavailable, stale, malformed,
or unauthorized Bundles. They SHALL expose only opaque Bundle identity when disclosure
is valid, bounded lifecycle/availability facts, legal next actions, and whitelisted
contained artifact references. For an authorized suspended Bundle, they MAY expose the
validated bounded `HumanInputRequest` display fields derived from Bundle-local pending
State so the owner can answer it. They SHALL never expose raw scope, provider, host path,
State payload, unvalidated prompt data, raw answer, diagnostic body, or artifact body.
(`RDO-004`)

#### Scenario: Ambiguity fails before content/provider access
- **WHEN** scoped discovery finds more than one active or an unreadable candidate
- **THEN** it returns bounded ambiguity/unavailability without opening an external provider, resolving a content path, acquiring a sandbox, or invoking a graph

### Requirement: Authorized resume preserves typed advertised responses

Any local adapter SHALL accept one frozen typed resume-response contract, project only
the current Bundle-local pending request's bounded advertised controls, and pass the
response unchanged to the lifecycle verifier. It SHALL not interpret localized phrases,
infer controls from text, expand the public tool schema, or use retained
manifest/trace/artifact facts as action authority. The same adapter SHALL submit a
refinement only through the separate `refine` action and never translate it into a
pending response. (`RDO-005`)

#### Scenario: Local response is revalidated at the Bundle boundary
- **WHEN** an authorized workbench submits `accept_suggestion` for the currently projected HITL1 request
- **THEN** the lifecycle module revalidates request/message correlation and advertised-action validity before it reaches HITL1

### Requirement: Bundle State writer resolves visible controls at its safe boundary

Visible controls SHALL be projected from the current Bundle-local pending request and
resolved only by the runtime-owned lifecycle State writer at its safe control boundary.
A local adapter lock may serialize its own display work but SHALL not authorize a
transition, persist a Run record, or replace the Bundle State writer. Stale, unknown, or
unadvertised controls SHALL be denied without State mutation or graph invocation.
(`RDO-006`)

#### Scenario: Stale visible control remains unavailable
- **WHEN** a workbench submits a previously displayed control after another response changed the pending interaction
- **THEN** it returns its bounded unavailable result and does not invoke a graph node
