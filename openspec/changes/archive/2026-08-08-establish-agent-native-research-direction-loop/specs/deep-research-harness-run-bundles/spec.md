> req: DRH-005, DRH-007

## MODIFIED Requirements

### Requirement: Refinements continue one Bundle at a durable safe point

A Primary User SHALL be able to submit a Run Refinement through the distinct public
`refine` action's direction form, which requires bounded nonblank refinement text and
may name an available `bundle_id`. When the id is absent, the Harness SHALL use only a
valid Handle for an active Bundle or exactly one active Bundle found by trusted-scope
discovery. An ended Bundle requires an explicit `bundle_id`; a stale or ended Handle
SHALL not guess a later refinement round. `resume` SHALL remain only a correlated
response to a current pending interaction and SHALL not be interpreted as a refinement.

The same `refine` action SHALL expose one continuation form: `refinement` is omitted or
JSON `null`, never blank, and an explicit `bundle_id` is required. The form SHALL be
accepted only when that selected Bundle is available, terminal, and contains one pending Run
Refinement. It requests continuation of that existing durable direction; it SHALL NOT
create a new direction, accept caller-supplied operation identity, reconstruct hidden
direction text, mutate the profile, or use a Handle/discovery to select a target. The
sole post-CAS recovery exception is an explicit selected retry whose available active
Bundle State has no pending human or later direction, has one current refinement, and
whose Bundle-contained checkpoint proves that exact current token has one queued
`topic_planning` task. It MAY continue only that already-authorized task under the
execution exclusion; it creates no admission, direction, rerun update, or lifecycle
fact. Every other unavailable, active, suspended, no-pending, exhausted, or
scope-conflicted target SHALL be rejected without State or graph mutation. An omitted-text call without a
`bundle_id` SHALL be rejected by the public schema before lifecycle dispatch. The
direction form remains subject to the admission/replay rules below even if its text
matches the pending direction.

When any available terminal Bundle has no trusted-policy capacity for a future full
rerun, the Harness SHALL project `start` as its legal next action regardless of whether
its refinement projection is `none`, `applied`, `pending`, or `applied_with_pending`.
It SHALL preserve an existing pending fact for inspection, return the existing bounded
exhausted/blocked outcome to either refinement form, and never advertise a non-viable
same-Bundle continuation.

The Harness SHALL validate the target within trusted scope and durably admit at most
one pending Run Refinement for that Bundle. Re-delivery of the same trusted refinement
operation with the same canonical text SHALL be idempotent. It SHALL retain a private,
no-text replay receipt for every committed legal refinement operation through the
current full-rerun generation ceiling, so that re-delivery remains recognizable after a
later current-round refinement supersedes the prior direction text. Reuse of that
trusted operation identity with different text SHALL return the typed conflict, preserve
the first refinement byte-for-byte, and create no additional lifecycle effect. A
different trusted operation is not a replay merely because its canonical text matches
an earlier operation. A different operation submitted before the pending one is applied
SHALL return a typed conflict and preserve the first refinement; once no refinement is
pending, it MAY become a later independent direction subject to generation capacity. The
Harness SHALL NOT silently replace, merge, reorder, or discard a pending refinement. A
current-round applied refinement does not occupy the next pending slot, so a later
independent direction may become the one pending refinement without altering that
current round. A legacy text-only pending value remains readable; because it has no
trusted operation identity, a same-text delivery preserves its pending disposition
without rewriting State. A literal complete Bundle-State mapping written before this
change SHALL remain readable when every new optional direction/receipt field is absent,
default those fields without changing its revision or serializing a write merely to read
it, and remain otherwise subject to the existing unknown-key and incompatible-schema
failures.

For every already-published Bundle, refinement admission and every other Bundle-local
State read/validate/reducer/write sequence SHALL use the same short Bundle transition
exclusion. That includes RequestBundleStore/HITL1's permitted profile materialization
and resulting State projection, correlated-response consumption, cancellation/terminal
state, and graph-progress projection; read-only status remains outside it. HITL1 SHALL
re-reduce only its permitted profile/interaction fields from the latest State after a
lawful concurrent direction admission rather than discard either fact, and SHALL NOT
gain lifecycle authority. The State revision check remains a stale-write fence but SHALL
NOT be the sole cross-instance/process serialization mechanism. Fresh Bundle
staging/publication remains governed by its trusted-scope exclusion before a Bundle root
exists.

The Harness SHALL apply the pending refinement exactly once at the next declared
durable round boundary. Its pending-to-current Bundle-State transition SHALL be atomic
under shared Bundle-local coordination, after the required Bundle-contained checkpoint
preparation; this does not claim one filesystem transaction across the two records. The
transition SHALL advance the existing refinement-round and generation authorities and
authorize the existing full-rerun path in the same Bundle. It SHALL retain accepted
evidence, prior reports, and prior artifacts for inspection while invalidating only
derived projections owned by the new generation. It SHALL not mutate State beneath an
in-flight writer, consume the refinement before a round transition is committed, or
replace a pending human interaction.

Only a synchronized `COMPLETED` terminal snapshot from an active current round SHALL
automatically consume its pending refinement. A `STOPPED`, `CANCELLED`, or `BLOCKED`
terminal outcome SHALL preserve an admitted pending refinement but SHALL NOT prepare,
commit, or continue a new round automatically. Its available ended Bundle may begin a
later round only through a later user-requested selected continuation form; this
preserves the user's stop/cancel intent and never silently discards the direction.

An explicit direction form for an available ended Bundle with no pending refinement,
or an explicit continuation form for its existing pending refinement, SHALL start its
next refinement round in that same Bundle when no different Bundle is active in the
trusted scope. If a different Bundle is active, the Harness SHALL return the typed
conflict or continuation outcome without mutating either Bundle. If the next round
cannot be committed because the Bundle is unavailable, the generation ceiling is
exhausted, or graph work cannot be opened, the result SHALL identify that bounded
outcome and SHALL not claim that the refinement was applied.

#### Scenario: Mid-run refinement is admitted without overwriting a writer
- **WHEN** a valid refinement arrives while the selected Bundle has an in-flight State writer
- **THEN** the refinement is durably recorded for the next round boundary, the in-flight State update remains intact, and the result identifies the refinement as pending rather than applied

#### Scenario: Bundle State writers cannot bypass refinement admission
- **WHEN** independently constructed runtime instances concurrently admit a refinement and consume a correlated response, materialize an otherwise lawful HITL1 profile/`profile_ref` projection, or commit a cancellation/terminal projection for the same available Bundle
- **THEN** each reducer runs through the shared Bundle transition exclusion, no revision is silently lost, the lawful profile facts, pending human subject, and admitted direction retain their independent facts, and a terminal outcome cannot be overwritten by a later stale State write

#### Scenario: Same refinement delivery is idempotent
- **WHEN** the same trusted refinement operation is delivered again before or after its first successful admission
- **THEN** the Bundle retains one pending or applied effect, does not advance its revision or round a second time, and returns the same bounded disposition

#### Scenario: Applied receipt preserves idempotency after a later round
- **WHEN** a prior legal refinement operation is re-delivered after its direction text is no longer the current round's direction
- **THEN** the retained private receipt returns its existing applied disposition without a new pending refinement, State revision, round, or graph effect

#### Scenario: Reused trusted operation with altered text fails closed
- **WHEN** the same trusted refinement operation identity is delivered with text that differs from its pending or current-round direction
- **THEN** the Harness returns the typed refinement conflict, preserves the first direction unchanged, and does not advance State, a round, or graph work

#### Scenario: A different second refinement cannot overwrite the first
- **WHEN** a Bundle already has one pending refinement and a different trusted operation, including one with identical text, is submitted before the first is applied
- **THEN** the Harness returns a typed refinement conflict, preserves the first pending refinement unchanged, and does not start or advance a round

#### Scenario: Text-bearing refinement cannot impersonate terminal continuation
- **WHEN** a terminal Bundle already holds one pending refinement and a different trusted operation supplies any refinement text, including matching text
- **THEN** the Harness applies the ordinary direction-form replay/conflict table, preserves the stored pending direction, and does not treat that call as an authorization to continue it

#### Scenario: Textless continuation has a narrow State predicate
- **WHEN** `refine` omits `refinement`
- **THEN** the public schema rejects a missing `bundle_id` or blank text before dispatch, while the Harness accepts an explicit id only for an available terminal Bundle with one pending refinement, except for a post-CAS retry whose current State/token and sole queued `topic_planning` task match exactly; active, suspended, no-pending, or unavailable targets outside that recovery return their typed bounded denial without State, profile, checkpoint, or graph mutation

#### Scenario: Post-CAS textless retry recovers only an authorized task
- **WHEN** the selected terminal continuation committed its pending direction but process interruption occurs before its queued `topic_planning` task starts
- **THEN** an explicit selected textless retry may run that exact current-token task once under the execution exclusion, returns `refinement_applied` with the committed projection, and cannot admit another direction or execute a mismatched/completed task

#### Scenario: Exhausted terminal capacity suppresses every same-Bundle refinement path
- **WHEN** an available terminal Bundle has no capacity for a future full rerun and its refinement projection is `none`, `applied`, `pending`, or `applied_with_pending`
- **THEN** `status` projects legal next action `start`; either text-bearing or textless `refine` returns the owned exhausted/blocked outcome without State, profile, checkpoint, or graph mutation, while any pending direction remains inspectable

#### Scenario: Current round permits one later pending direction
- **WHEN** a Bundle has a current-round applied refinement, no pending refinement, and generation capacity for a later round
- **THEN** an independent valid direction becomes the one pending refinement without changing the current-round direction or starting another round immediately

#### Scenario: A later operation may intentionally repeat earlier text
- **WHEN** a later trusted operation supplies the same canonical direction text as a prior current-round refinement or retained replay receipt, no refinement is pending, and generation capacity remains
- **THEN** the Harness treats it as a new direction, records it in the pending slot, and does not change the prior operation's receipt or current round

#### Scenario: Pending refinement survives process reopen
- **WHEN** a refinement is admitted, the process closes before the next legal round boundary, and the same Bundle is reopened
- **THEN** the Bundle still contains that one pending refinement and later applies it at most once

#### Scenario: Ended Bundle begins a later refinement round
- **WHEN** a Primary User explicitly submits a direction form to an available ended Bundle without a pending direction, or explicitly invokes the continuation form for its existing pending direction, and the next round can be committed
- **THEN** the Harness starts graph work for a later generation in that same Bundle, applies that one direction once, and retains the prior report and evidence inside it

#### Scenario: Ended Handle cannot select a later round implicitly
- **WHEN** a Current Bundle Handle names an available ended Bundle but `refine` omits a `bundle_id`
- **THEN** the Harness returns a bounded explicit-target outcome and does not reactivate or mutate that Bundle

#### Scenario: Pending interaction remains a distinct resume subject
- **WHEN** a selected active Bundle awaits a correlated human response and the Primary User submits `refine`
- **THEN** the Harness records the refinement for a later round boundary and leaves the current pending interaction unchanged for `resume`

#### Scenario: Refinement is applied once after the pending subject is resolved
- **WHEN** the correlated response is consumed and the current round later synchronizes `COMPLETED` with one pending refinement
- **THEN** the Harness commits one same-Bundle full-rerun transition, moves the refinement to the new current round, and does not consume the response or refinement twice

#### Scenario: Stop, cancel, or block does not restart a pending direction
- **WHEN** an active Bundle with an admitted pending refinement reaches `STOPPED`, `CANCELLED`, or `BLOCKED`
- **THEN** it retains the pending direction without preparing or starting another round, and only a later user-requested explicit selected textless continuation form may continue that available Bundle

#### Scenario: Explicit continuation consumes the stored terminal direction once
- **WHEN** a Primary User explicitly requests the continuation form for an available terminal Bundle with one pending direction and its next round is legal
- **THEN** the Harness uses that stored direction's existing trusted identity and token to prepare and commit one same-Bundle round, returns the applied outcome only after that commit, and neither creates another pending direction nor asks the user to reproduce redacted text

#### Scenario: Ended target cannot displace another active Bundle
- **WHEN** a Primary User explicitly submits a direction or continuation form for an available ended Bundle while a different Bundle is active in the same trusted scope
- **THEN** the Harness returns its typed conflict or continuation outcome and does not reactivate or mutate the ended Bundle

#### Scenario: Failed round start is not reported as applied
- **WHEN** the Harness cannot commit or begin the next same-Bundle round after a refinement was admitted
- **THEN** it preserves the authoritative pre-commit disposition, returns the bounded failure or waiting outcome, and does not project a successful application

### Requirement: One trusted conversation has at most one active Run Bundle

Fresh start publication and an explicit ended Bundle's terminal-to-active direction or
continuation commit SHALL serialize through one transient advisory exclusion on the validated trusted
scope directory. It SHALL be usable by independently constructed runtime instances and
processes, contain no lifecycle fact, active pointer, manifest, index, or replacement
State, and retain the existing scoped discovery authority. The ended-refinement path
SHALL re-check for another active Bundle while it owns that exclusion and before it
commits its selected Bundle active. A missing, replaced, or invalid selected Bundle
under the corresponding Bundle coordinator SHALL be unavailable and SHALL never be
recreated from a held descriptor, checkpoint, or scope record.

#### Scenario: Concurrent fresh starts preserve one active Bundle
- **WHEN** two fresh-start requests race in one trusted conversation scope
- **THEN** at most one Bundle becomes active and the other request receives a typed continuation or conflict outcome without publishing another active Bundle

#### Scenario: Ended Bundle permits a fresh Run
- **WHEN** all available Bundles in a trusted conversation scope have terminal current refinement rounds
- **THEN** a new fresh-start request can publish a distinct Bundle without deleting or reusing the ended Bundles

#### Scenario: Fresh start cannot race an ended refinement into two active Bundles
- **WHEN** independent runtime instances concurrently start a fresh Run and explicitly submit a direction or continuation form for an available ended Bundle in the same trusted scope
- **THEN** exactly one selected Bundle becomes active, the other action returns its typed conflict or continuation outcome, and no scope registry or replacement Bundle State is created

#### Scenario: Coordinator root loss is fail-closed
- **WHEN** the selected Bundle is removed or replaced while a scope or Bundle coordinator is waiting or held
- **THEN** the affected action releases its transient coordination, returns the typed unavailable outcome, and writes neither a new Bundle root nor State/checkpoint data through the detached descriptor
