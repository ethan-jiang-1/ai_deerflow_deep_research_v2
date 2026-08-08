> req: RUI-001, RUI-002, RUI-003, RUI-004, RUI-006, RUI-007, RUI-008, RUI-009, RUI-010, RUI-011

## ADDED Requirements

### Requirement: Reflected Deep Research controls use trusted scope and opaque Bundle identity

The reflected `deep_research` tool SHALL preserve its public tool name and trusted
runtime adaptation while routing Deep Research lifecycle actions through the Harness
Bundle lifecycle contract. It SHALL accept or project only the bounded `bundle_id`
control identity where an existing Run is targeted; it SHALL not accept, derive, or
expose `research_id`, a bundle directory, a checkpoint key, caller scope, or provider
configuration as lifecycle authority. A Current Bundle Handle may be passed only by
trusted conversation context and remains subject to Bundle validation. (`RUI-010`)

#### Scenario: Public control targets a Bundle without path authority
- **WHEN** a supported Deep Research control targets an available Run
- **THEN** the tool dispatches with trusted conversation scope and `bundle_id` facts only, without accepting a caller-supplied path, checkpoint, user, thread, or research identity

#### Scenario: Legacy identity input is rejected
- **WHEN** a tool request supplies `research_id`, session reference, bundle directory, or checkpoint identity
- **THEN** strict validation refuses it before runtime adaptation or filesystem access

### Requirement: Runtime integration cannot make an external checkpoint lifecycle authority

The runtime bridge SHALL bind Deep Research graph/checkpoint persistence to the selected
Run Bundle and SHALL not derive a Deep Research lifecycle namespace from outer
conversation identity. Generic checkpoint/provider infrastructure may remain available
for non-Deep-Research features, but it SHALL not recover, select, or authorize a Deep
Research Run after Bundle loss. The bridge SHALL return the Harness typed unavailable
outcome rather than a provider-derived resume result. (`RUI-011`)

#### Scenario: External provider data cannot resume a lost Bundle
- **WHEN** a generic checkpoint provider contains a prior Deep Research snapshot but the selected Bundle no longer exists
- **THEN** runtime dispatch returns unavailable without opening that snapshot as a Deep Research lifecycle source

#### Scenario: Full-real release execution remains at the Bundle boundary
- **WHEN** the selected EVH-024 release runner starts and continues a credentialed
  public Deep Research execution
- **THEN** it carries only the selected opaque `bundle_id` through trusted control
  context and reads lifecycle/output facts from that Bundle's State and contained
  artifacts, without compiling or inspecting a Deep Research GraphHost, external
  checkpoint, session, legacy identity, or workspace-derived path

## RENAMED Requirements

- FROM: `### Requirement: Reflected lifecycle results project pending interaction separately from checkpoint phase`
- TO: `### Requirement: Reflected lifecycle results project pending interaction separately from committed phase`
- FROM: `### Requirement: GraphHost owns topology but not live SQL resources`
- TO: `### Requirement: GraphHost owns topology but not Deep Research lifecycle persistence`

## MODIFIED Requirements

### Requirement: One reflected control tool exposes an infrastructure probe

DeerFlow SHALL continue to resolve
`deerflow_deep_research.tool:deep_research_tool` as the one `deep_research` tool. The
independent business-free `infra_probe` action SHALL retain its optional bounded URL-safe
opaque probe id, isolated topology/namespace, structured redacted result, and
server-generated id behavior. When omitted, the probe id SHALL retain at least 128 bits
of server CSPRNG entropy and no scope-derived identity/path text; a caller-supplied id
SHALL never become an internal checkpoint key without trusted scope/domain derivation.

The same strict tool surface SHALL dispatch the registered Deep Research lifecycle
actions `start`, `resume`, `status`, `cancel`, and `refine` using action-specific
validation. `start` SHALL accept neither a Bundle id nor refinement text. `resume`
SHALL consume only the current correlated `AcceptedHumanResponse` for an available
Bundle-local pending interaction; it SHALL not reinterpret arbitrary refinement text or
reactivate an ended Bundle. `refine` SHALL require one bounded non-empty refinement text
and MAY include one opaque `bundle_id`; without an explicit id it resolves only an
active Current Bundle Handle or scoped active discovery. An ended Bundle requires an
explicit target. `status` and `cancel` MAY target a bounded
`bundle_id` or use the same validated Handle/discovery rule. Every lifecycle target
shall be authorized only by trusted scope plus Bundle-local State. `research_id`, a
session reference, bundle directory, checkpoint identity, caller scope, provider
configuration, answer authority, and every unknown authority field SHALL remain
forbidden. Unknown bounded action names SHALL return redacted `action_unavailable`
before RuntimeAdapter, sandbox initialization, scope/path derivation, or persistence.

#### Scenario: Probe starts through the reflected tool
- **WHEN** a fake DeerFlow runtime invokes `infra_probe` with valid trusted context
- **THEN** the tool writes and reads one probe checkpoint and returns an opaque probe reference, backend durability class, and status using the unchanged probe contract

#### Scenario: Registered lifecycle action reaches trusted dispatch
- **WHEN** the tool receives an action-valid `start`, `resume`, `status`, `cancel`, or `refine` request
- **THEN** it adapts trusted runtime and dispatches only to that registered lifecycle handler without accepting caller identity, path, checkpoint, or provider authority

#### Scenario: Resume and refine retain distinct meanings
- **WHEN** a current Bundle is awaiting correlated human input and a caller submits a run-level refinement
- **THEN** `resume` accepts only the correlated response, while `refine` records the separate refinement for the Bundle lifecycle safe point without replacing the pending interaction

#### Scenario: Unsupported control action is refused
- **WHEN** the tool receives an unknown bounded action in an otherwise valid request
- **THEN** it returns typed `action_unavailable` without echoing the rejected value and without adapting runtime or touching sandbox/checkpoint state

#### Scenario: Extra authority field is schema-rejected
- **WHEN** `infra_probe` receives a lifecycle identity, `start` receives a caller-selected Bundle id or question text, `refine` omits refinement text, or any action receives a legacy/unknown authority field
- **THEN** strict validation emits only normalized field/code diagnostics and dispatch does not occur

### Requirement: Runtime authority comes only from trusted context

A runtime-owned Bundle lifecycle resolver SHALL require a trusted runtime envelope
created from current authenticated runtime context or a fixed local-profile adapter. It
SHALL derive only a containment scope from that trusted context, validate a supplied
Current Bundle Handle against scoped Bundle-local State, or inspect that scope's actual
Bundle directories and State when the Handle is absent. It SHALL not synthesize a
historical `ToolRuntime` or `thread_data`, reopen a historical session/binding/provider,
or accept caller-supplied scope, path, provider, recipe, or identity fields. It SHALL
reject missing, mismatched, unavailable, foreign, or ambiguous authority before opening
a provider, resolving content paths, or acquiring a sandbox. Startup-fingerprint drift
SHALL still return `restart_required` before sandbox initialization or Bundle access.
(`RUI-002`)

#### Scenario: Trusted runtime is adapted without inventing research scope
- **WHEN** runtime context and state contain one consistent effective user, thread, sandbox, and thread-data mapping
- **THEN** RuntimeAdapter emits only a runtime-owned envelope and no Bundle root or node-agent projection

#### Scenario: Forged cross-user fields are denied
- **WHEN** tool arguments include user, thread, host path, sandbox, checkpoint, legacy research identity, or any unknown field
- **THEN** schema validation rejects the invocation before RuntimeAdapter, scoped discovery, or filesystem access

#### Scenario: Missing explicit runtime identity fails closed
- **WHEN** a hand-built runtime has no non-empty `runtime.context["user_id"]` even though DeerFlow's generic helper could fall back to `default`
- **THEN** RuntimeAdapter rejects it before sandbox initialization, scope derivation, or Bundle access

#### Scenario: Startup sandbox drift fails before initialization
- **WHEN** live AppConfig sandbox values do not match the launcher-captured startup fingerprint
- **THEN** RuntimeAdapter returns typed `restart_required` before calling the sandbox initializer

### Requirement: Nested checkpoint namespaces are isolated

The independent `infra_probe` SHALL continue to derive its nested checkpoint key from a
versioned, domain-separated, collision-resistant encoding of effective user, outer
thread, and opaque probe id. The caller SHALL not provide that derived key, and the
probe graph SHALL not share the outer lead-agent checkpoint identity. Same-namespace
probe mutation SHALL remain serialized in the supported single-worker runtime; an
unsupported multi-worker topology SHALL fail readiness rather than claim cross-process
exclusion.

Deep Research durable lifecycle State SHALL not use a research checkpoint namespace at
all. Its trusted-scope containment bucket MAY be derived from the runtime envelope, but
is not a Run identity, public target, active pointer, index, or recovery source; it
contains only independently validated Bundle directories and their Bundle-local State.
The lifecycle module's scope coordination SHALL serialize Bundle admission without
becoming durable lifecycle authority. (`RUI-003`)

#### Scenario: Stable identity revisits the same probe
- **WHEN** the same effective user, outer thread, and probe id are used in a later action
- **THEN** namespace derivation returns the same internal key and the new probe invocation observes the prior visit marker without claiming Deep Research resume

#### Scenario: Cross-scope Bundle discovery is prevented
- **WHEN** two trusted conversations have distinct scope containment buckets
- **THEN** discovery cannot enumerate a Bundle from the other bucket even when a caller presents its valid-looking opaque id

### Requirement: Research lifecycle dispatch preserves runtime and resource boundaries

The reflected lifecycle SHALL expose no new Gateway command. It SHALL route `start`,
`resume`, `status`, `cancel`, and `refine` through the runtime-owned Bundle lifecycle
module after action validation and trusted-envelope construction. A local-profile
adapter uses the same entry point and may not recreate a session broker or a durable
dispatch lease. Read-only status, cancellation, and refinement admission that does not
consume graph work SHALL not initialize a parent sandbox; graph work SHALL construct
fresh reduced dependencies only when its selected available Bundle requires them.
Typed store errors SHALL unwind through the runtime resource owner before a redacted
tool-boundary projection. No action may cache request authority, leak a host path, or
turn a provider/checkpoint reopen into Run recovery. (`RUI-006`)

#### Scenario: Lifecycle actions share one Bundle contract
- **WHEN** start, resume, status, cancel, and refine target the same available Bundle
- **THEN** each action observes one Bundle-local State contract and no action-specific external checkpoint or broker can reinterpret it

#### Scenario: Suspension and terminal results share one wire contract
- **WHEN** resume suspends, refine is admitted, or any lifecycle action returns a non-suspended result
- **THEN** the tool exposes the shared bounded lifecycle-result fields and only the lawful pending-input/refinement projection, without internal scope or checkpoint data

#### Scenario: Non-interactive and unsupported transport contexts fail before mutation
- **WHEN** trusted runtime marks a request non-interactive or supplies a checked-in IM transport that cannot carry the legal input/control flow
- **THEN** the affected input-bearing action returns the existing bounded denial before Bundle mutation, while status and cancel remain dispatchable when their Bundle is available

#### Scenario: Lifecycle call with a sibling is refused
- **WHEN** the latest AIMessage has a missing or mismatched active tool-call id, two deep-research calls, or deep research beside any other tool call
- **THEN** the lifecycle action returns `exclusive_control_call_required` before RuntimeAdapter or Bundle mutation and makes no claim to control the sibling call

### Requirement: GraphHost owns topology but not Deep Research lifecycle persistence

`GraphHost` SHALL retain its generic request-independent topology, resource-lifetime,
and isolated `infra_probe` checkpoint behavior. It SHALL not compile, select, read, or
recover a Deep Research lifecycle graph from the configured generic checkpointer. The
Deep Research runtime may reuse graph composition facilities, but its lifecycle State
and any recoverable graph representation SHALL be bound to the selected Run Bundle
through the Harness lifecycle module. (`RUI-004`)

#### Scenario: Generic GraphHost checkpoint cannot become a Deep Research fallback
- **WHEN** a generic GraphHost provider has a snapshot for a former Deep Research action
- **THEN** the Deep Research runtime does not read or compile it after Bundle loss, while
  the independent `infra_probe` contract remains unchanged

### Requirement: Reflected lifecycle results project pending interaction separately from committed phase

The reflected Deep Research lifecycle result SHALL preserve a bounded committed phase
and pending-input projection derived from the current Bundle-local Research State. The
graph interrupt remains its in-invocation request delivery, but Bundle-local State owns
the durable request id, pending phase, generation, mode, and correlation truth. The
projection omits host paths, raw prompt context, external-checkpoint data, and caller
authority; it cannot itself consume a response or alter State. (`RUI-007`)

#### Scenario: Status projects Bundle-local pending input
- **WHEN** status reads an available suspended Bundle after the original interrupt delivery
- **THEN** it returns the bounded pending-input projection from Bundle-local State without
  reading a generic checkpoint or invoking a graph node

### Requirement: Reflected research uses an explicit real recipe and isolated recipe namespace

The default reflected `deep_research` host SHALL retain one explicit all-real recipe,
its no-fixture-public-entry boundary, and its stable implementation-mode projection.
It SHALL not use a research checkpoint namespace or expose a `research_id` as a
caller-visible identity. Each current lifecycle action obtains its selected Run through
the trusted-scope Bundle lifecycle module; a retired fixture checkpoint, session, or
legacy identity is at most inspection-only observation and never a real lifecycle
source. (`RUI-008`)

#### Scenario: Retired fixture state cannot select a real Bundle
- **WHEN** an old fixture checkpoint exists without an available selected Run Bundle
- **THEN** the public real host returns the typed unavailable/new-run outcome without
  opening that checkpoint or deriving a Bundle target

## REMOVED Requirements

### Requirement: Runtime captures and projects one trusted canonical bundle locator
**Reason**: A separately checkpointed physical locator duplicates Bundle identity and
leaks a lifecycle path into projections.
**Migration**: Project a bounded opaque `bundle_id`; resolve all physical paths only
inside the runtime-owned Bundle lifecycle module.
