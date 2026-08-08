> req: REG-021

## MODIFIED Requirements

### Requirement: Graph lifecycle actions use Bundle identity and safe refinement transitions

Start, status, control, cancellation, and refinement transitions SHALL resolve one
validated `bundle_id` through the Harness lifecycle contract. They SHALL preserve the
one-active rule, treat a suspended Bundle-local State as active, and keep a correlated
pending human response distinct from an independently admitted refinement. Their
projections SHALL not expose a conversation-derived research identity, host path, or
checkpoint locator.

The graph lifecycle SHALL define the refinement round boundary as a Bundle-contained
graph execution boundary at which the preceding graph write is durably committed, no
graph writer is in flight, and no current human subject is being replaced. At that
boundary, a shared Bundle-local coordination facility usable by independent runtime
instances SHALL provide a short transition exclusion for every published Bundle State
read/validate/reducer/write sequence, including the authoritative State revision check,
RequestBundleStore/HITL1's permitted profile materialization and resulting State
projection, response/cancellation/terminal mutations, graph-progress projection,
checkpoint preparation, Bundle-State commit, and continuation authorization. HITL1 SHALL
re-reduce only its permitted profile/interaction fields from current State after a lawful
concurrent direction write; the facility SHALL NOT grant that node lifecycle authority.
It SHALL be the cross-instance/process serializer; the State revision check remains a
stale-write fence, not the sole mutex. The facility also provides a separate execution
exclusion held across every selected-Bundle graph `ainvoke` and an immediate
terminal-boundary continuation owned by that same invocation. The execution exclusion SHALL serialize competing
continuations but SHALL NOT prevent an active Bundle from admitting one pending
refinement through the transition exclusion. Neither exclusion stores a lifecycle fact.
The facility SHALL remain contained in the validated selected Bundle and SHALL not
recover or recreate an unavailable Bundle. For an ended Bundle's terminal-to-active
commit only, the lifecycle SHALL first use the transient trusted-scope exclusion that
serializes it with fresh start; that exclusion stores no scope fact and is released
before graph execution.

Only a synchronized `COMPLETED` terminal graph snapshot is eligible for automatic
pending-refinement preparation/consumption. `STOPPED`, `CANCELLED`, and `BLOCKED`
snapshots preserve any pending direction but SHALL NOT prepare a checkpoint, commit a
new current round, or continue graph work. A later user-requested explicit selected
textless `refine` continuation remains the only path that may reactivate that available
ended Bundle with its existing pending direction.

Coordinator acquisition and release SHALL remain off the event loop, permit a cancelled
waiter to leave no State/checkpoint write, and revalidate the selected Bundle's
no-follow path and live directory identity after acquisition and before each durable
write or graph invocation. Loss or replacement of that Bundle SHALL be unavailable;
the lifecycle SHALL not write through a detached descriptor or recreate the root. The
lifecycle SHALL atomically move at most one pending refinement to the new current round
only as its Bundle-State transition, after preparing the separate Bundle-contained
checkpoint; it SHALL not imply a cross-file filesystem transaction. Preparation SHALL
submit only the typed output of the pure full-rerun compiler shared with the rerun node
to the compiled production graph's `aupdate_state(..., as_node="rerun")` writer/edge;
it SHALL not accept a hand-built alternative update. Checkpoint preparation SHALL not
invoke a graph node, model, tool, or provider or publish graph/topic/artifact facts
before that Bundle-State commit. The existing full-rerun transition then re-enters
`topic_planning` in the same Bundle and generation lineage. A stale graph writer or
replayed boundary SHALL not consume the refinement, advance the generation, or publish
the round twice.

An admitted refinement SHALL remain pending across a suspension until its correlated
human subject has been resolved and a legal round boundary is reached. An explicit
direction form for an available ended Bundle, or an explicit textless continuation form
for its existing pending direction, SHALL create only the graph work required to start
that Bundle's next round; an active graph invocation SHALL use its already bound
Bundle-contained graph store. The textless form is legal only for an explicit available
terminal target with one pending direction; it consumes that record and never admits or
reconstructs text. After its CAS commits, an explicit selected textless retry may only
continue the current record's exact queued `topic_planning` task when Bundle State has no
pending human or later direction and the Bundle-contained checkpoint proves the same
token; it remains no admission or new direction. When a checkpoint is prepared before the Bundle-State commit, a later
selected text-bearing `refine` SHALL first reconcile the pending operation's matching
token: the same trusted operation receives `refinement_applied`, while a different
operation receives `refinement_conflict` for its submitted action and the first round's
post-reconciliation `applied` Bundle projection. That recovery SHALL terminate the
different operation's admission attempt; it SHALL NOT fall through to ordinary admission
now that the pending slot has cleared. A qualified textless continuation MAY reconcile
only the selected pending record's matching token and returns `refinement_applied` only
when that exact record commits or is observed committed during its locked attempt; it
SHALL NOT enter ordinary direction admission. Before that commit, the preceding terminal
Bundle State remains authoritative with its pending direction and an explicit selected
`refine` next action only while capacity permits it; otherwise its legal next action is
`start` while the pending fact remains inspectable. `status` remains read-only. No
lifecycle action SHALL use an external checkpoint, session record, diagnostic, or prior conversation text to recover
or authorize the transition.

#### Scenario: Graph consumes an admitted refinement in the same Bundle
- **WHEN** a graph reaches the declared round boundary after a refinement was admitted for its active Bundle
- **THEN** it records one pending-to-applied round transition in that Bundle, enters the existing full-rerun path toward `topic_planning`, and does not create another active Run

#### Scenario: Suspended graph keeps its current human subject
- **WHEN** a refinement is admitted while the graph is suspended on a correlated human subject
- **THEN** the graph leaves that subject and its response correlation unchanged, reports the refinement as waiting, and applies it only after a later legal round boundary

#### Scenario: User terminal intent does not auto-reactivate a Bundle
- **WHEN** an active graph with a pending direction projects `STOPPED` or `CANCELLED`, or projects `BLOCKED`
- **THEN** the projection preserves that pending direction but performs no rerun preparation or continuation; only a later user-requested explicit selected textless `refine` continuation with legal remaining capacity may reactivate the available ended Bundle

#### Scenario: Boundary replay is exactly once
- **WHEN** process restart or checkpoint replay revisits a graph boundary whose refinement round was already committed
- **THEN** the graph observes the committed generation and applied refinement and neither consumes nor starts that round again

#### Scenario: Prepared checkpoint reconciles the first pending operation before a later request
- **WHEN** a process stops after preparing the matching rerun checkpoint but before the pending-to-current Bundle-State commit, and a selected `refine` later arrives
- **THEN** the lifecycle commits only the prepared first operation's matching token without another generation update; the same text-bearing operation returns `refinement_applied` with `applied`, while a different text-bearing operation returns `refinement_conflict` with the same `applied` Bundle projection and cannot enter ordinary admission or replace the first direction in that call; a qualified textless continuation may reconcile only the selected pending record and returns `refinement_applied` only for that record's committed token

#### Scenario: Pre-commit preparation never makes status a hidden recovery path
- **WHEN** the matching rerun checkpoint is prepared but its Bundle-State commit has not occurred
- **THEN** `status` reports the preceding terminal State and pending direction without reconciliation, while the typed legal next action remains explicit selected `refine` and the textless continuation predicate stays at the lifecycle boundary

#### Scenario: Stale graph writer loses to committed refinement state
- **WHEN** a graph writer based on an older Bundle revision attempts to commit after a refinement boundary was committed
- **THEN** the stale write is rejected and cannot restore the pending refinement, erase the applied direction, or overwrite the new generation

#### Scenario: Stale graph projection cannot overwrite the committed round
- **WHEN** a graph snapshot carries a Bundle identity, generation, or round token that does not match the committed current refinement round
- **THEN** graph-progress synchronization makes no Bundle-State write and cannot replace the committed applied direction, generation, or pending refinement

#### Scenario: Terminal State defeats a late graph projection
- **WHEN** cancellation or another lawful terminal State transition commits while a graph invocation still holds an older snapshot
- **THEN** its later graph-progress projection makes no Bundle-State write and cannot restore an active status, pending subject, or refinement fact

#### Scenario: Competing continuation does not execute a graph task twice
- **WHEN** two independently constructed runtime instances attempt to continue the same prepared refinement round
- **THEN** only the holder of the selected Bundle's execution exclusion may invoke its pending graph task, and the other re-reads the checkpoint after acquiring that exclusion without creating a second node/model/tool/artifact effect or refinement round

#### Scenario: Refinement admission races eligible terminal projection safely
- **WHEN** a valid refinement is admitted immediately before or after the current graph invocation projects its `COMPLETED` terminal snapshot
- **THEN** one transition path preserves the pending direction, prepares and commits one matching refinement token, and the Bundle starts no more than one next-round continuation; when the terminal projector already owns execution, it continues that queued task without re-acquiring the execution exclusion

#### Scenario: Ended refinement starts Bundle-contained graph work
- **WHEN** an explicit direction form legally reactivates an available ended Bundle, or a qualified textless continuation legally consumes its pending direction
- **THEN** graph execution opens that Bundle's contained graph store, commits the full-rerun transition, and makes observable progress in the new round without consulting an external lifecycle checkpoint

#### Scenario: Textless continuation cannot become an implicit recovery route
- **WHEN** `refine` omits text for an explicit target that is active, suspended, unavailable, terminal without a pending direction, or otherwise cannot legally start another round
- **THEN** lifecycle returns its bounded denial without preparing a checkpoint, admitting a direction, changing a profile, or invoking graph work, except for an active post-CAS current record whose exact token has its one queued `topic_planning` task; that exception only invokes the already-authorized task under execution exclusion. An omitted-text call without a `bundle_id` is rejected by the public schema before lifecycle dispatch

#### Scenario: Post-CAS continuation recovers one exact queued task
- **WHEN** an explicit selected textless continuation finds a current refinement after its CAS but before graph continuation, and the selected Bundle checkpoint has exactly that token's queued `topic_planning` task
- **THEN** it invokes that task once under the execution exclusion, retains the committed generation/refinement, and rejects every mismatch or completed task without an admission or second round

#### Scenario: Missing Bundle prevents refinement recovery
- **WHEN** a former graph checkpoint or conversation record exists but the selected Bundle becomes unavailable before the refinement boundary
- **THEN** the graph returns the typed unavailable outcome without consuming the pending direction, recreating State, or starting replacement graph work

#### Scenario: Coordinator cancellation and root loss release without a write
- **WHEN** a contender is cancelled while waiting for the selected Bundle coordinator, or the selected Bundle is removed or replaced after coordination is acquired
- **THEN** it releases its transient exclusion, performs no State/checkpoint/graph invocation write, and returns cancellation or the typed unavailable outcome without recreating the Bundle
