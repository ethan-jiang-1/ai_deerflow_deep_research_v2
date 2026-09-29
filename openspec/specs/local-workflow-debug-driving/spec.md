# local-workflow-debug-driving Specification

> req: LDD-001, LDD-002, LDD-003, LDD-004, LDD-005, LDD-006, LDD-007, LDD-008

## Purpose

Own the local workflow-debugger driving surface: at-most-once boundary commands
over the one real graph, an expiring control lease that fences writers while
observers read, fixed start compositions, stop policies, attach/detach/restart
recovery, and the topology guard. Driving composes the existing lifecycle and
executor; it never becomes a second lifecycle authority.

## Requirements

### Requirement: Closed debug commands drive one exact Bundle at-most-once

The debug driver SHALL expose a closed command set — `advance_one`,
`drive_until`, `pause_request`, `answer`, `cancel`, `detach` — where every
mutation carries the exact `bundle_id`, an `expected_cursor`, and a unique
`command_id`. A command whose cursor is stale SHALL receive a typed stale
denial; a replayed `command_id` SHALL receive a typed duplicate denial with the
original effect (at-most-once); a command against a Bundle holding another
writer's live control SHALL receive a typed busy denial. `answer` SHALL reuse
the existing typed human-response correlation; `cancel` SHALL reuse lifecycle
cancel; `pause_request` SHALL take effect only at the next committed boundary
and never claim a model/tool call was interrupted. Session snapshots SHALL
report exact bundle, generation, cursor, drive mode, stop policy, pause state,
and control ownership. A session snapshot SHALL also report the Bundle's pending human request as a
bounded projection carried from the Bundle's own checkpoint interrupt - the
request id, phase, mode, node-authored title and guidance, and advertised
options - so an operator can see exactly what a HITL stop is asking without
the caller rebuilding a prompt.
(`LDD-001`)

#### Scenario: Double-submit commits one boundary
- **WHEN** the same `advance_one` command id, or two commands sharing one
  expected cursor, race against the driver
- **THEN** at most one boundary commits, one caller sees success, and the other
  receives a typed duplicate or stale denial

#### Scenario: Pause honesty during a long node
- **WHEN** `pause_request` arrives while a node is executing
- **THEN** the session reports pause-requested, the node runs to its boundary,
  and the drive stops at the next committed boundary without fabricating an
  interruption

### Requirement: An expiring control lease fences writers while observers read

Intentional boundary pauses SHALL hold a runtime-owned, Bundle-local, expiring
debug control lease with an owner identity, generation, TTL, and heartbeat.
While the lease is live, natural `ContinueRun` admission and a second debug
driver SHALL receive typed busy/status denials, and observer inspection SHALL
remain unaffected. Takeover SHALL be legal only when the lease is stale AND no
live execution exclusion exists, and SHALL compare-and-swap the exact lease
generation and cursor; TTL expiry alone SHALL never authorize a second writer.
An execution fence SHALL cover the whole invocation through checkpoint commit
and SHALL stay live/renewed across long model calls. Detach at a committed
boundary SHALL release the lease, leaving cursor, State, and lifecycle status
unchanged. (`LDD-002`)

#### Scenario: Natural resume is fenced, not redefined
- **WHEN** natural `ContinueRun` targets a Bundle whose live debug lease is
  held
- **THEN** admission returns a typed busy/status denial and the lease owner
  keeps exclusive drive

#### Scenario: Stale lease with no live exclusion allows CAS takeover
- **WHEN** the lease TTL expired, no execution exclusion is live, and an
  attacher presents the exact lease generation and cursor
- **THEN** the attach succeeds by CAS and the old owner can no longer write

#### Scenario: Long node outlives TTL without a second writer
- **WHEN** a node invocation runs longer than the control TTL
- **THEN** the live execution fence keeps second writers busy until the
  boundary commits, regardless of TTL expiry

### Requirement: Step and run advance the one real graph with per-boundary commits

`advance_one` SHALL execute the current logical node on the same recipe,
compile path, and durable saver/thread used by ordinary runs, with
`interrupt_after` applied per invocation, and SHALL commit at most one logical
node boundary per command. `drive_until` SHALL advance continuously until the
stop policy matches a breakpoint (a named node's post-commit), a formal HITL
request, a failure, a terminal, or a pause request. Start compositions SHALL
be fixed: Start Step = open start plus exactly one `advance_one` of bootstrap;
Start Run = open start plus `drive_until`; both SHALL surface the exact Bundle
handle before the first provisional row and SHALL be idempotent under retry.
All modes SHALL produce the same trace frame kinds as ordinary runs.
(`LDD-003`)

#### Scenario: Fixture step-through reaches terminal in bounded boundaries
- **WHEN** a fixture run is stepped from bootstrap to terminal
- **THEN** at least nine committed boundaries appear, one node per step, with
  no skipped or repeated node

#### Scenario: Mode switches share one execution truth
- **WHEN** an operator switches step → run → pause → step within one session
- **THEN** every mode uses the same saver/thread semantics and the timeline
  remains a single ordered frame sequence

#### Scenario: Post-node breakpoint stops after the named commit
- **WHEN** `drive_until` targets a breakpoint after a named node
- **THEN** the drive stops immediately after that node's commit and before the
  next node starts

### Requirement: Attach, detach, and restart recover without advancing

`open_attach` SHALL accept only a lifecycle-verified recoverable Bundle,
rebuild the session at the durable cursor without advancing, and classify
candidates as live-owned (busy/read-only) versus takeover-eligible using lease
and execution-exclusion truth. Restart after boundary death SHALL restore the
same cursor via CAS and SHALL NOT advance; started-without-outcome visits
SHALL project uncertain until lifecycle recovery converges. Detach SHALL be
refused while a node is in flight (typed busy), and process death SHALL follow
crash/recovery semantics rather than fabricating detach or cancel.
(`LDD-004`)

#### Scenario: Attach restores the exact cursor without advancing
- **WHEN** an operator attaches to a recoverable Bundle after a process death
- **THEN** the session resumes at the durable cursor and the first command —
  not the attach — performs the next boundary

#### Scenario: In-flight detach is refused
- **WHEN** detach is requested while a node is executing
- **THEN** the driver returns typed busy and the lease stays with the owner

### Requirement: Topology guard pins one logical visit per superstep

The driver SHALL enforce that the current top-level graph executes at most one
logical node visit per superstep; when the guard cannot hold, step contracts
SHALL fail closed rather than silently advancing multiple nodes. (`LDD-005`)

#### Scenario: Guard blocks multi-visit supersteps
- **WHEN** a composition would execute two logical nodes within one superstep
- **THEN** the driver refuses step semantics with a typed failure instead of
  drifting the contract

### Requirement: Session snapshots carry the parsed HITL prompt card and the node's last feedback

A debug session snapshot's pending-request projection SHALL carry, in addition to the
carried request id, phase, mode, node-authored title, and advertised options, a
presentation-ready typed prompt card parsed from the node-authored context when that
context follows the published hitl1 context schema: the goal summary, proposed
dimensions, missing fields, recognized fields, remaining accepted-answer rounds,
remaining unrecognized-retry rounds, the localized guidance, and a bounded answer
example. The projection SHALL NOT require any caller to parse machine JSON, and SHALL
leave the card absent when the context does not follow the published schema (no
fabricated card, while title, mode, and options remain carried).

The projection SHALL also carry the node's most recent typed feedback for the pending
conversation: taken from the checkpoint interrupt's own interaction projection when it
carries feedback, and otherwise from the Bundle's durable state interaction feedback
when present. The feedback is a carried projection, never lifecycle authority.
(`LDD-006`)

#### Scenario: A schema-following context becomes a typed card
- **WHEN** a session stops at a hitl1 request whose node-authored context follows the
  published context schema
- **THEN** the snapshot's pending-request projection carries the parsed card fields
  (goal, proposed dimensions, missing fields, remaining rounds, guidance, example)
  alongside the carried title, mode, and options

#### Scenario: Feedback follows the interaction projection first, durable state second
- **WHEN** the checkpoint interrupt carries an interaction projection with feedback,
  or carries none while the Bundle's durable state records interaction feedback
- **THEN** the projection reports that feedback as the node's last feedback, and
  reports none when neither channel has one

#### Scenario: An unparsed context stays honest
- **WHEN** the pending request's context does not follow the published schema
- **THEN** the projection carries no prompt card and does not fabricate card fields,
  while the title, mode, and advertised options remain carried as before

### Requirement: Node rerun at a stopped boundary is lifecycle-admitted, never a driver write

The debug driver SHALL accept a `rerun_node` command at a stopped boundary that
re-executes the most recently committed node with the same inputs. The command SHALL
carry the exact bundle id, expected cursor, and a unique command id under the existing
at-most-once discipline. All rollback of the node's committed outputs — trace tail,
work-unit accounting, evidence pointers — SHALL be admitted and written by the
lifecycle controller; the driver SHALL NOT write graph or Bundle state directly and a
refused rollback SHALL leave the session at its current boundary with a typed denial.
(`LDD-007`)

#### Scenario: A rerun re-executes the same node
- **WHEN** the operator reruns at a boundary where a node just committed
- **THEN** the node executes again with the same inputs, the trace gains a fresh visit
  for that node, and the journal records the rerun admission

#### Scenario: A refused rollback keeps the boundary intact
- **WHEN** the lifecycle cannot roll the committed tail back transactionally
- **THEN** the driver returns a typed denial, nothing is re-executed, and the session
  stays at the same boundary

### Requirement: drive_until auto-confirms HITL profile proposals under an explicit bounded policy

`drive_until` SHALL carry an explicit auto-HITL policy: when the drive meets a hitl1
profile-confirmation request, it MAY submit `确认` (confirm) as an operator-policy
answer through the existing semantic intake and continue. Single-step advances SHALL
never auto-answer, and HITL2 direction decisions SHALL always stop for the operator.
Every auto-answer SHALL be stated in the operator log as policy-submitted. When the
same request is auto-answered twice without acceptance, the drive SHALL stop and
surface the node's reply for a human answer. (`LDD-008`)

#### Scenario: A drive passes a complete proposal
- **WHEN** a drive with auto-HITL meets a complete profile proposal
- **THEN** it submits confirm as operator policy, the log states the auto-answer, and
  the drive continues to the next stop

#### Scenario: An incomplete proposal falls back to the human
- **WHEN** two consecutive auto-answers are not accepted
- **THEN** the drive stops at the HITL request and renders the node's reply and
  remaining rounds for a human answer

#### Scenario: Single steps never auto-answer
- **WHEN** the operator advances one boundary at a time
- **THEN** every HITL request waits for a human answer
