> req: RUI-006, RUI-012

## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Research lifecycle dispatch preserves runtime and resource boundaries

The reflected lifecycle SHALL expose no new Gateway command. It SHALL route `start`,
`resume`, `status`, `cancel`, and `refine` through the runtime-owned Bundle lifecycle
module after action validation and trusted-envelope construction. A local-profile
adapter uses the same entry point and may not recreate a session broker or a durable
dispatch lease. Read-only status, cancellation, and refinement admission that leaves a
direction pending SHALL not initialize a parent sandbox or graph. Graph work SHALL
construct fresh reduced dependencies only when the selected available Bundle must
start or continue graph execution.

When a text-bearing `refine` legally reactivates an ended Bundle without a pending
direction, when an explicit selected textless continuation legally consumes an ended
Bundle's pending direction, when its exact post-CAS queued task is retried, or when an active Bundle synchronizes its `COMPLETED`
current-round boundary, dispatch SHALL lazily open that same Bundle's graph resources and
invoke the existing full-rerun continuation. It SHALL not create another Bundle, reuse
request authority from an earlier invocation, or treat a generic checkpoint as the
lifecycle source. A failure before the round commit SHALL leave the refinement pending or
return the direct bounded denial; a failure after a committed round SHALL project the
committed generation and its owned graph outcome rather than roll the Bundle back through
a presentation layer.

Cancellation and any `STOPPED`, `CANCELLED`, or `BLOCKED` terminal projection SHALL NOT
be treated as a graph-owning refinement continuation merely because a pending direction
exists. They preserve the bounded pending fact and return the legal explicit selected
textless-continuation `refine` action for an available ended Bundle without opening graph
resources solely to apply it.

Every selected-Bundle graph invocation, including `start`, `resume`, and an authorized
refinement continuation, SHALL acquire the Bundle-local execution exclusion and
re-read that Bundle's checkpoint after acquiring it. It SHALL revalidate the selected
Bundle root before graph open/invocation and project root loss as unavailable without
recreating it. A waiting contender SHALL not invoke an already-completed or
no-longer-authorized graph task, while a separate short transition exclusion continues
to permit refinement admission during an active graph invocation. Neither exclusion is
a session broker, dispatch lease, or lifecycle source.

Typed store errors SHALL unwind through the runtime resource owner before a redacted
tool-boundary projection. No action may cache request authority, leak a host path, or
turn a provider or checkpoint reopen into Run recovery. (`RUI-006`)

#### Scenario: Lifecycle actions share one Bundle contract
- **WHEN** start, resume, status, cancel, and refine target the same available Bundle
- **THEN** each action observes one Bundle-local State contract and no action-specific external checkpoint or broker can reinterpret it

#### Scenario: Suspension and terminal results share one wire contract
- **WHEN** resume suspends, refine is admitted or applied, or any lifecycle action returns a non-suspended result
- **THEN** the tool exposes the shared bounded lifecycle-result fields, submitted-action code, and lawful pending-input/Bundle refinement projection, without internal scope, direction text, operation identity, or checkpoint data

#### Scenario: Pending refinement avoids graph initialization
- **WHEN** an active Bundle accepts a refinement but has not reached its legal round boundary
- **THEN** dispatch persists and reports the pending direction without initializing graph dependencies or a parent sandbox solely for admission

#### Scenario: Cancellation does not restart a queued direction
- **WHEN** cancellation or a stopped/blocked terminal projection observes an available Bundle with a pending refinement
- **THEN** dispatch preserves that pending fact, opens no graph solely to apply it, and exposes only the typed explicit selected textless-refine continuation

#### Scenario: Ended refinement lazily starts the same Bundle
- **WHEN** an explicit direction form without a pending direction, or a qualified selected textless continuation with one pending direction, legally targets an available ended Bundle and graph resources are available
- **THEN** dispatch initializes only that Bundle's reduced graph dependencies, starts its full-rerun continuation, and returns the committed applied or owned graph outcome

#### Scenario: Competing dispatches serialize one graph continuation
- **WHEN** two runtime dispatches target the same prepared Bundle-bound refinement continuation
- **THEN** one dispatch owns the graph invocation, the other re-reads its checkpoint after waiting, and neither creates a second Bundle, continuation task, or lifecycle application

#### Scenario: A removed Bundle cannot be opened through a held coordinator
- **WHEN** the selected Bundle is removed or replaced after dispatch acquired its graph-execution exclusion
- **THEN** dispatch opens no replacement graph store, invokes no pending task, releases the exclusion, and returns the existing redacted unavailable result

#### Scenario: Graph-open failure preserves pre-commit truth
- **WHEN** graph resources cannot be opened before a pending direction's round transition is committed
- **THEN** dispatch does not report the direction as applied, does not create replacement lifecycle State, and returns the direct bounded outcome with its legal next action

#### Scenario: Non-interactive and unsupported transport contexts fail before mutation
- **WHEN** trusted runtime marks a request non-interactive or supplies a checked-in IM transport that cannot carry the legal input or control flow
- **THEN** the affected input-bearing action returns the existing bounded denial before Bundle mutation, while status and cancel remain dispatchable when their Bundle is available

#### Scenario: Lifecycle call with a sibling is refused
- **WHEN** the latest AIMessage has a missing or mismatched active tool-call id, two deep-research calls, or deep research beside any other tool call
- **THEN** the lifecycle action returns `exclusive_control_call_required` before RuntimeAdapter or Bundle mutation and makes no claim to control the sibling call
