> req: RUI-006

## MODIFIED Requirements

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
policy as one closed typed action input before Bundle publication. The canonical marker
is `non_interactive=true`; the existing trusted `disable_clarification=true` marker is
a compatibility alias subject to the same validation. When trusted runtime composition
supplies a `BundleGraphExecutor`, the controller may carry that input only to the first
graph invocation for the new selected Bundle; the initial graph values are its sole
state-writing path. A later `resume`, `refine`, reprojection, or same-start replay
SHALL not carry runtime context as a graph-state writer. It SHALL read the selected
Bundle checkpoint and retain its existing policy value, if any. Policy admission SHALL
NOT instantiate or select a graph executor, so the existing uncomposed fallback/full-
fake lifecycle remains unchanged. Presentation adapters, caller input, and generic
GraphHost state SHALL not supply or replace this action input.

For a marked input-bearing `resume` or `refine`, the reflected boundary SHALL still
apply the same closed-policy validation before Bundle or graph mutation. A complete
later policy may satisfy that validation but SHALL NOT become a controller or graph
action input; continuation consumes only the selected Bundle checkpoint.

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
- **WHEN** a trusted non-interactive `start` supplies a complete closed policy and the
  selected Bundle has no graph checkpoint and trusted runtime composition supplies a
  `BundleGraphExecutor`
- **THEN** the policy enters graph state only with the initial graph invocation and no
  presentation adapter, caller argument, or generic checkpoint becomes its authority

#### Scenario: Policy admission does not compose graph work
- **WHEN** a trusted non-interactive `start` supplies a complete closed policy but the
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
- **WHEN** trusted runtime marks an input-bearing action non-interactive without a
  complete closed policy, or a checked-in IM transport cannot carry the legal input or
  control flow
- **THEN** the affected action returns the existing bounded denial before Bundle or
  graph mutation, while status and cancel remain dispatchable when their Bundle is
  available

#### Scenario: Lifecycle call with a sibling is refused
- **WHEN** the latest AIMessage has a missing or mismatched active tool-call id, two
  deep-research calls, or deep research beside any other tool call
- **THEN** the lifecycle action returns `exclusive_control_call_required` before
  RuntimeAdapter or Bundle mutation and makes no claim to control the sibling call
