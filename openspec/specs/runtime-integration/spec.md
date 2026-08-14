# runtime-integration Specification

> req: RUI-001, RUI-002, RUI-003, RUI-004, RUI-005, RUI-006, RUI-007, RUI-008, RUI-009, RUI-010, RUI-011, RUI-012

## Purpose
The reflected Deep Research control tool, trusted runtime adaptation, isolated checkpoint namespaces, GraphHost lifecycle, and infrastructure-probe persistence.
## Requirements
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

### Requirement: Persistence guarantees match the selected backend

The probe SHALL describe memory and SQLite memory-mode connections as same-process
only, file-backed SQLite/Postgres as durable across provider reopen and Gateway
restart when correctly configured, and invalid or missing database connection data as
unavailable. Probe and doctor output SHALL NOT claim stronger durability than the
active resolved database backend provides.

A non-null legacy `checkpointer` section is retired input. The local runtime SHALL
reject it before GraphHost opens a generic provider or derives a provider-backed
claim, and doctor/diagnostics SHALL return the same bounded
`legacy_checkpointer_unsupported` configuration result without exposing its type,
connection, DSN, or secret. `database` is the sole local provider-classification
input. An emergency rollback is a separately approved hotfix that restores the
entire prior reader and its provider/diagnostic parity; it SHALL not rewrite a
configuration, silently choose a provider, or add support for another legacy shape.

#### Scenario: Memory revisits only in one process
- **WHEN** two probe actions use the same process-local memory GraphHost configured
  through `database`
- **THEN** the second action observes prior state and the response labels restart recovery unsupported

#### Scenario: Persistent provider survives reopen
- **WHEN** a file-backed SQLite or valid Postgres probe is written through
  `database`, its provider context is closed, and a fresh context reads the same
  namespace
- **THEN** the prior checkpoint is recovered without using outer lead-agent checkpoint state

#### Scenario: SQLite memory mode is not restart durable
- **WHEN** the effective SQLite database connection is `:memory:` or an equivalent
  memory-mode URI
- **THEN** GraphHost and doctor report same-process-only durability and never claim provider-reopen or Gateway-restart recovery

#### Scenario: Legacy provider overrides unified database
- **WHEN** AppConfig supplies any non-null legacy `checkpointer`, whether or not a
  `database` section is also present and even where the legacy type conflicts with
  the database backend
- **THEN** GraphHost opens no generic provider, doctor and GraphHost expose the same
  redacted `legacy_checkpointer_unsupported` result, and no legacy source determines
  durability or persistence behavior

### Requirement: Research lifecycle dispatch preserves runtime and resource boundaries

The reflected lifecycle SHALL expose no new Gateway command. It SHALL route `start`,
`resume`, `status`, `cancel`, and `refine` through the runtime-owned Bundle lifecycle
module after action validation and trusted-envelope construction. A local-profile
adapter uses the same entry point and may not recreate a session broker or a durable
dispatch lease. Read-only status, cancellation, and refinement admission that leaves a
direction pending SHALL not initialize a parent sandbox or graph. Graph work SHALL
construct fresh reduced dependencies only when the selected available Bundle must start
or continue graph execution.

For a new `start`, the reflected boundary SHALL validate a trusted non-interactive
policy as one closed typed action input before Bundle publication. The sole accepted
marker is `non_interactive=true`. A trusted `disable_clarification=true` value is
retired input and SHALL return the existing typed `INTERACTIVE_REQUIRED` denial before
Bundle publication, graph mutation, executor selection, sandbox initialization, or
policy checkpoint writing; it SHALL not fall back to ordinary interactive execution.
When trusted runtime composition supplies a `BundleGraphExecutor`, the controller may
carry canonical marked input only to the first
graph invocation for the new selected Bundle; the initial graph values are its sole
state-writing path. A later `resume`, `refine`, reprojection, or same-start replay
SHALL not carry runtime context as a graph-state writer. It SHALL read the selected
Bundle checkpoint and retain its existing policy value, if any. Policy admission SHALL
NOT instantiate or select a graph executor, so the existing uncomposed fallback/full-
fake lifecycle remains unchanged. Presentation adapters, caller input, and generic
GraphHost state SHALL not supply or replace this action input.

For a canonically marked input-bearing `resume` or `refine`, the reflected boundary
SHALL still apply the same closed-policy validation before Bundle or graph mutation. A
complete later policy may satisfy that validation but SHALL NOT become a controller or
graph action input; continuation consumes only the selected Bundle checkpoint.

When a text-bearing `refine` legally reactivates an ended Bundle without a pending
direction, when an explicit selected textless continuation legally consumes an ended
Bundle's pending direction, when its exact post-CAS queued task is retried, or when an
active Bundle synchronizes its `COMPLETED` current-round boundary, dispatch SHALL lazily
open that same Bundle's graph resources and invoke the existing full-rerun continuation.
It SHALL not create another Bundle, reuse request authority from an earlier invocation,
or treat a generic checkpoint as the lifecycle source. A failure before the round
commit SHALL leave the refinement pending or return the direct bounded denial; a
failure after a committed round SHALL project the committed generation and its owned
graph outcome rather than roll the Bundle back through a presentation layer.

Cancellation and any `STOPPED`, `CANCELLED`, or `BLOCKED` terminal projection SHALL NOT
be treated as a graph-owning refinement continuation merely because a pending direction
exists. They preserve the bounded pending fact and return the legal explicit selected
textless-continuation `refine` action for an available ended Bundle without opening graph
resources solely to apply it.

Every selected-Bundle graph invocation, including `start`, `resume`, and an authorized
refinement continuation, SHALL acquire the Bundle-local execution exclusion and re-read
that Bundle's checkpoint after acquiring it. It SHALL revalidate the selected Bundle
root before graph open/invocation and project root loss as unavailable without
recreating it. A waiting contender SHALL not invoke an already-completed or
no-longer-authorized graph task, while a separate short transition exclusion continues
to permit refinement admission during an active graph invocation. Neither exclusion is
a session broker, dispatch lease, or lifecycle source.

Typed store errors SHALL unwind through the runtime resource owner before a redacted
tool-boundary projection. No action may cache request authority, leak a host path, or
turn a provider or checkpoint reopen into Run recovery. (`RUI-006`)

#### Scenario: Lifecycle actions share one Bundle contract
- **WHEN** start, resume, status, cancel, and refine target the same available Bundle
- **THEN** each action observes one Bundle-local State contract and no action-specific
  external checkpoint or broker can reinterpret it

#### Scenario: Valid scripted start writes only initial graph values
- **WHEN** a trusted canonical non-interactive `start` supplies a complete closed policy and the
  selected Bundle has no graph checkpoint and trusted runtime composition supplies a
  `BundleGraphExecutor`
- **THEN** the policy enters graph state only with the initial graph invocation and no
  presentation adapter, caller argument, or generic checkpoint becomes its authority

#### Scenario: Retired marker fails before lifecycle mutation
- **WHEN** trusted runtime supplies `disable_clarification=true`, with or without a
  policy-shaped context, for `start`, `resume`, or `refine`
- **THEN** dispatch returns `INTERACTIVE_REQUIRED`, publishes no Bundle, writes no
  graph policy, selects no executor, and does not treat the action as interactive

#### Scenario: Policy admission does not compose graph work
- **WHEN** a trusted canonical non-interactive `start` supplies a complete closed policy but the
  lifecycle has no trusted-composed `BundleGraphExecutor`
- **THEN** dispatch retains the existing uncomposed fallback/full-fake lifecycle and
  does not create graph state or select a graph executor

#### Scenario: Later context cannot replace checkpointed policy
- **WHEN** an available Bundle already has graph state and a later lifecycle action has
  a different complete policy-shaped runtime context
- **THEN** the context passes the same closed validation, but the action re-reads and
  uses the Bundle checkpoint without replacing or adding the policy field from that
  later context

#### Scenario: Suspension and terminal results share one wire contract
- **WHEN** resume suspends, refine is admitted or applied, or any lifecycle action
  returns a non-suspended result
- **THEN** the tool exposes the shared bounded lifecycle-result fields, submitted-action
  code, and lawful pending-input/Bundle refinement projection, without internal scope,
  direction text, operation identity, or checkpoint data

#### Scenario: Pending refinement avoids graph initialization
- **WHEN** an active Bundle accepts a refinement but has not reached its legal round
  boundary
- **THEN** dispatch persists and reports the pending direction without initializing
  graph dependencies or a parent sandbox solely for admission

#### Scenario: Cancellation does not restart a queued direction
- **WHEN** cancellation or a stopped/blocked terminal projection observes an available
  Bundle with a pending refinement
- **THEN** dispatch preserves that pending fact, opens no graph solely to apply it, and
  exposes only the typed explicit selected textless-refine continuation

#### Scenario: Ended refinement lazily starts the same Bundle
- **WHEN** an explicit direction form without a pending direction, or a qualified
  selected textless continuation with one pending direction, legally targets an ended
  Bundle and graph resources are available
- **THEN** dispatch initializes only that Bundle's reduced graph dependencies, starts
  its full-rerun continuation, and returns the committed applied or owned graph outcome

#### Scenario: Competing dispatches serialize one graph continuation
- **WHEN** two runtime dispatches target the same prepared Bundle-bound refinement
  continuation
- **THEN** one dispatch owns the graph invocation, the other re-reads its checkpoint
  after waiting, and neither creates a second Bundle, continuation task, or lifecycle
  application

#### Scenario: A removed Bundle cannot be opened through a held coordinator
- **WHEN** the selected Bundle is removed or replaced after dispatch acquired its
  graph-execution exclusion
- **THEN** dispatch opens no replacement graph store, invokes no pending task,
  releases the exclusion, and returns the existing redacted unavailable result

#### Scenario: Graph-open failure preserves pre-commit truth
- **WHEN** graph resources cannot be opened before a pending direction's round
  transition is committed
- **THEN** dispatch does not report the direction as applied, does not create
  replacement lifecycle State, and returns the direct bounded outcome with its legal
  next action

#### Scenario: Non-interactive and unsupported transport contexts fail before mutation
- **WHEN** trusted runtime marks an input-bearing action canonical non-interactive
  without a complete closed policy, supplies the retired marker, or a checked-in IM
  transport cannot carry the legal input or control flow
- **THEN** the affected action returns the existing bounded denial before Bundle or
  graph mutation, while status and cancel remain dispatchable when their Bundle is
  available

#### Scenario: Lifecycle call with a sibling is refused
- **WHEN** the latest AIMessage has a missing or mismatched active tool-call id, two
  deep-research calls, or deep research beside any other tool call
- **THEN** the lifecycle action returns `exclusive_control_call_required` before
  RuntimeAdapter or Bundle mutation and makes no claim to control the sibling call

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

### Requirement: Reflected refinement results distinguish admission from application

The reflected lifecycle result SHALL expose bounded typed refinement outcomes that let
human and AI consumers distinguish a direction that is durably pending, a direction
whose same-Bundle round was started and applied, a conflicting second direction, and a
direction that could not target an available Bundle. The result SHALL identify the
selected opaque Bundle, current lifecycle status and generation when available, and one
legal next action. It SHALL NOT expose refinement text, its digest or correlation, host
paths, checkpoint identity, prompt content, or trusted scope.

The reflected `refine` schema SHALL accept exactly two non-overlapping forms: a
direction form with bounded nonblank `refinement` text, and a continuation form with
that field omitted or JSON `null` and an explicit `bundle_id`. Blank text is invalid. The runtime SHALL
admit the continuation form only after its selected Bundle-local State proves an
available terminal Bundle with one pending direction; it SHALL not infer a target from a
Handle or active discovery, accept a caller operation key, or expose/reconstruct the
stored direction. After that record's CAS has committed, an explicit selected textless
retry MAY continue only the exact current token's one queued `topic_planning` task when
Bundle State has no pending human or later direction and the Bundle-contained checkpoint
matches; it admits no direction and creates no lifecycle fact. A failed ordinary
predicate returns the existing bounded invalid-transition, unavailable, active-Bundle,
or exhausted result without Bundle, profile, checkpoint, or graph mutation.

For every available selected Bundle, `BundleControlResult` SHALL contain a bounded
`refinement` projection derived only from Bundle-local State. Its `disposition` SHALL be
exactly `none`, `pending`, `applied`, or `applied_with_pending`; the latter SHALL report
the legal coexistence of a current applied direction and one later pending direction.
The projection's `current_round` SHALL be present only for the two applied dispositions
and SHALL be validated against the result's existing generation and the State's
monotonic round rules. An unavailable result SHALL omit the projection.

The result's `code` SHALL remain the submitted action's outcome, not a synonym for the
Bundle projection: `refinement_pending` means the submitted text-bearing operation is
pending, `refinement_applied` means that operation has an already committed round or a
qualified continuation committed/observed its selected stored pending record, and
`refinement_conflict` means a submitted text-bearing operation acquired no lifecycle
effect. Therefore a conflicting call MAY truthfully return `refinement_conflict`
together with a Bundle projection of `pending`, `applied`, or `applied_with_pending`.
Neither axis exposes text, digest, operation identity, receipt, token, path, or
checkpoint facts.

`status` SHALL project all applicable pending/current-round refinement facts without
inventing a lifecycle effect. A `refine` result SHALL not report its submitted operation
as applied until the durable round transition is committed. A typed conflict SHALL
preserve the first direction and derive its legal next action from the post-call Bundle
projection; unavailable or deleted Bundles SHALL retain the existing fresh-start-only
boundary.

Legal next action SHALL be derived from the post-call lifecycle status together with that
projection and the same trusted immutable rerun policy, not from the submitted action
code alone. A pending direction with a visible human subject requires `resume`; one in
an active Bundle without a subject requires `status`; a terminal Bundle with `pending`
or `applied_with_pending` and legal remaining capacity requires the explicit selected
textless `refine` continuation because that is the only recovery/continuation entry that
may reconcile it; and a terminal Bundle with `none` or `applied` and legal remaining
capacity allows only a text-bearing `refine` direction form. Every terminal Bundle with
no legal remaining capacity SHALL project `start`; it retains any inspectable pending
fact and returns the owned exhausted/blocked outcome to either refinement form. `status`
SHALL never acquire a recovery role.

#### Scenario: Active refinement reports pending honestly
- **WHEN** `refine` durably admits a direction but the selected Bundle has not reached its round boundary
- **THEN** its code is `refinement_pending`, its Bundle projection is `pending` or `applied_with_pending`, it preserves the current Bundle status and generation, and it does not claim graph work or planning changed

#### Scenario: Started round reports applied honestly
- **WHEN** an ended or active Bundle commits its next same-Bundle refinement round
- **THEN** its code is `refinement_applied`, its Bundle projection is `applied`, and it exposes the committed new generation without exposing the direction text or internal graph locator

#### Scenario: Terminal continuation reports only the stored direction's effect
- **WHEN** an explicit selected textless `refine` continuation commits or observes the exact pending record it selected under lifecycle coordination
- **THEN** its code is `refinement_applied`, its Bundle projection is `applied`, and it does not claim that the caller submitted a new direction or reveal the stored direction text

#### Scenario: No-text refine outside the terminal-pending predicate is rejected
- **WHEN** `refine` omits `refinement` for an explicit active, suspended, unavailable, no-pending, or illegal-capacity target
- **THEN** it returns its bounded denial without creating a direction, writing a profile, preparing a checkpoint, or opening graph work

#### Scenario: No-text refine requires a public explicit target
- **WHEN** `refine` supplies omitted or `null` `refinement` without `bundle_id`
- **THEN** the reflected tool returns its ordinary invalid-arguments shape before trusted-envelope construction or Bundle lifecycle dispatch

#### Scenario: Exhausted terminal Bundle does not advertise a retry loop
- **WHEN** an available terminal Bundle's refinement projection is `none`, `applied`, `pending`, or `applied_with_pending` and the trusted rerun policy permits no future full generation
- **THEN** `status` projects legal next action `start`, preserves any pending fact for inspection, and either refinement form returns the existing exhausted/blocked outcome without State, checkpoint, or graph mutation

#### Scenario: Different pending direction returns typed conflict
- **WHEN** `refine` receives a different direction while one direction is already pending
- **THEN** its code is `refinement_conflict`, its Bundle projection still reports the first direction's pending or applied-with-pending facts, it leaves that direction authoritative, and it names only the legal next action

#### Scenario: Applied and later pending direction are both visible
- **WHEN** a Bundle has a current applied refinement and independently admits one later pending refinement
- **THEN** its available result projects `applied_with_pending` and the current round without identifying either direction or either operation

#### Scenario: Pre-commit reconciliation distinguishes the retried operation from a competitor
- **WHEN** `refine` reconciles a prepared pending direction after its checkpoint write but before its Bundle-State commit
- **THEN** the original text-bearing trusted operation returns `refinement_applied` with `applied`; a different text-bearing operation returns `refinement_conflict` with that same first round's `applied` Bundle projection and legal next action; a qualified textless continuation may reconcile only its selected pending record and returns `refinement_applied` only for that record's committed token; reconciliation does not continue normal admission of a different text-bearing operation in that call, and neither result exposes direction text, token, digest, or checkpoint facts

#### Scenario: Post-CAS textless retry is bounded graph recovery
- **WHEN** a selected textless continuation's current refinement committed before its queued task started, and a later explicit selected textless retry finds the same State/token and queued `topic_planning` task
- **THEN** the result is `refinement_applied` with the existing applied projection after one execution-excluded task continuation; it creates no new admission, operation receipt, direction, generation, or graph task, and an active/suspended/mismatched/no-task request remains denied

#### Scenario: Status reflects direction disposition without mutation
- **WHEN** `status` observes a Bundle with a pending or current-round applied refinement
- **THEN** it returns `pending`, `applied`, or `applied_with_pending` from Bundle-local State without consuming a direction or opening graph work

#### Scenario: Unavailable refinement exposes no recoverable internals
- **WHEN** `refine` targets a deleted, foreign, corrupt, or otherwise unavailable Bundle
- **THEN** the result retains the existing unavailable and fresh-start-only contract and exposes no refinement, path, checkpoint, or remembered conversation facts
