> req: RWB-001, RWB-002, RWB-003, RWB-004

## ADDED Requirements

### Requirement: Local terminal workbench is bound to one configured durable profile

The downstream package SHALL provide one standalone terminal workbench entry point
that constructs its operation-enabled local profile before accepting a session
selection. It SHALL discover sessions only through that profile's authorized
`ResearchSessionOperationBroker` and SHALL render only opaque session references and
bounded broker facts. It SHALL not accept or derive a principal, profile, recipe,
provider, thread, research id, binding path, retained-root path, namespace, or
checkpoint from terminal input. Same-process-only and unavailable profiles SHALL
produce an explicit bounded unavailable state rather than a recovery claim. (`RWB-001`)

#### Scenario: Fresh local process discovers only fixed-profile sessions
- **WHEN** a fresh workbench process uses the configured file-SQLite local profile
- **THEN** it lists only broker-discovered opaque references for that profile and does
  not scan retained bundle directories or enumerate another profile's records

### Requirement: Workbench lifecycle controls delegate only to the existing broker

The terminal workbench SHALL obtain current status, pending input, resume, and cancel
behavior only from broker projections and broker methods. It SHALL retain an opaque
session reference and displayed expected request id only as a selection/correlation
value, and it SHALL pass a raw answer only from its interactive input directly to
broker resume. It SHALL not construct a lifecycle action, response envelope, graph
host, runtime envelope, sandbox, checkpoint provider, or parallel state controller.
Unavailable, stale, or denied selections SHALL remain bounded unavailable views and
shall not dispatch a lifecycle mutation. (`RWB-002`)

#### Scenario: Stale pending-input response cannot be dispatched by the workbench
- **WHEN** the selected session's current broker projection no longer matches the
  request id shown by the terminal
- **THEN** the workbench reports bounded unavailability without constructing a graph
  action, mutating a checkpoint, or exposing the submitted answer

### Requirement: Workbench timeline is a bounded read-only observation

For a selected session, the workbench SHALL first obtain an available broker projection,
then render a bounded timeline derived only from validated retained lifecycle-trace
records. Each entry SHALL contain only safe sequence, timestamp, action, status, phase,
generation, pending-input summary, terminal outcome, closed failure category, and opaque
diagnostic reference facts. The broker may use its established checkpoint-provider
verification while authorizing the selection. After that broker call, timeline rendering
SHALL not inspect or open an additional provider, acquire a sandbox, invoke a graph
node, infer a legal lifecycle transition, or replace the broker's checkpoint-derived
current status. A malformed, stale, oversized, or unavailable trace SHALL become a
bounded unavailable timeline. (`RWB-003`)

#### Scenario: Timeline read has no lifecycle side effect
- **WHEN** an owner opens a selected durable session's timeline
- **THEN** the workbench first obtains broker authorization, then reads only its
  contained retained observation and neither initializes a sandbox nor opens an
  additional checkpoint provider or invokes a graph node

### Requirement: Workbench remains a local non-product surface

The workbench SHALL identify itself as a standalone local operator surface and SHALL
document that it is not a Gateway, Web, upstream terminal, multi-user, or generic
production recovery interface. This change SHALL not add a Gateway route, Web page,
upstream terminal integration, caller-selected authority field, or generic filesystem
browser. Failure output SHALL omit raw identity, host path, provider, checkpoint,
binding, answer, diagnostic body, and artifact body data. (`RWB-004`)

#### Scenario: Unavailable profile does not become a product fallback
- **WHEN** the fixed local profile cannot establish its authorized operation access
- **THEN** the terminal shows only a bounded unavailable explanation and does not fall
  back to a Gateway endpoint, an upstream terminal client, or a filesystem scan
