> req: DRH-001, DRH-002, DRH-003, DRH-004, DRH-005, DRH-006, DRH-007, DRH-008

## Purpose

Defines the Deep Research Harness and Run Bundle lifecycle so each continuing
research Run has one authoritative, inspectable, independently deletable record.

## ADDED Requirements

### Requirement: Fresh Run Bundles have one opaque identity and publish atomically

The Deep Research Harness SHALL create a fresh opaque `bundle_id` for each admitted
new Deep Research Run. The same identifier SHALL name that Run's Bundle directory,
Run identity, and public control target while the Bundle is available. It SHALL not be
derived from a user, outer conversation, message, request text, checkpoint key, or
caller-supplied path. Before the Bundle becomes discoverable, the Harness SHALL create
its initial Bundle-local Research State and required content roots in a contained
staging location and atomically publish the complete Bundle. A partial directory SHALL
not be discoverable as a Run.

#### Scenario: Fresh start publishes one complete Bundle
- **WHEN** a trusted outer conversation starts Deep Research with no active available Bundle
- **THEN** the Harness returns one fresh opaque `bundle_id`, and scoped discovery finds one Bundle containing valid initial State and content roots

#### Scenario: Interrupted creation never publishes a partial Run
- **WHEN** Bundle initialization fails before atomic publication
- **THEN** scoped discovery selects no new Run and no partial directory is available for control or content writes

### Requirement: Bundle-local Research State is the sole durable lifecycle authority

Each Run Bundle SHALL contain the authoritative Research State for its own lifecycle,
current refinement round, pending interaction, admitted refinement, terminal facts,
evidence references, and legal control outcomes. A non-terminal available State,
including a State awaiting user input, SHALL mean active; a terminal current refinement
round SHALL mean ended. External checkpoints, session records, bindings, indices,
logs, diagnostics, and caches MAY retain observations but SHALL not establish Run
existence, status, authorization, or recovery.

#### Scenario: Suspended Bundle remains active
- **WHEN** an available Bundle-local State awaits a user interaction
- **THEN** the Harness reports the Run active and does not start a second active Bundle in that trusted conversation scope

#### Scenario: External observation conflicts with Bundle State
- **WHEN** an external session/checkpoint observation disagrees with an available Bundle-local State
- **THEN** lifecycle control follows the Bundle-local State and the observation cannot change it

### Requirement: Current Bundle Handle is transient and discovery is scoped

The current outer conversation MAY retain its `bundle_id` as a Current Bundle Handle
for a later control. A `refine` action without an explicit id MAY use that Handle only
when the selected Bundle-local State is active. The Handle SHALL be validated against
the contained Bundle and State before use and SHALL not prove existence, activity, or authority. When
the Handle is absent, the Harness SHALL inspect only Bundle directories and
Bundle-local State in the trusted conversation scope. It SHALL select exactly one
active Bundle; missing, malformed, unavailable, foreign, or ambiguous candidates SHALL
fail closed without global discovery, a durable active pointer, an index, or an
external checkpoint lookup.

The trusted scope may map to a private filesystem containment bucket derived only from
trusted runtime context. That bucket SHALL contain only Bundle directories and their
Bundle-local State; it SHALL not contain a manifest, active pointer, index, session
binding, or replacement State and SHALL not become a Run/public-control identity.

#### Scenario: Handle continues the same available Run
- **WHEN** a current conversation supplies its valid Current Bundle Handle for status or refinement of an active Bundle
- **THEN** the Harness controls the same Bundle only after validating its availability and Bundle-local State

#### Scenario: Absent Handle discovers one active Bundle only
- **WHEN** a current conversation has no Current Bundle Handle and exactly one active Bundle in its trusted scope
- **THEN** scoped discovery selects that Bundle without reading another scope, a session record, or an external checkpoint

#### Scenario: Ambiguous discovery fails closed
- **WHEN** scoped discovery finds more than one active or an unreadable candidate Bundle
- **THEN** it returns a bounded ambiguous or unavailable outcome and mutates neither candidate

### Requirement: One trusted conversation has at most one active Run Bundle

The Harness SHALL serialize fresh-start and refinement-round admission within the
trusted outer-conversation scope. It SHALL not publish or reactivate a second active
Bundle while an available Bundle-local State is non-terminal. Ended available Bundles
SHALL remain inspectable and SHALL not block a fresh independent Run. Coordination used
for this rule SHALL not become a durable registry, active pointer, or source of
lifecycle truth.

#### Scenario: Concurrent fresh starts preserve one active Bundle
- **WHEN** two fresh-start requests race in one trusted conversation scope
- **THEN** at most one Bundle becomes active and the other request receives a typed continuation or conflict outcome without publishing another active Bundle

#### Scenario: Ended Bundle permits a fresh Run
- **WHEN** all available Bundles in a trusted conversation scope have terminal current refinement rounds
- **THEN** a new fresh-start request can publish a distinct Bundle without deleting or reusing the ended Bundles

### Requirement: Refinements continue one Bundle at a durable safe point

A Primary User SHALL be able to submit a Run Refinement through the distinct public
`refine` action, which requires bounded refinement text and may name an available
`bundle_id`. When the id is absent, the Harness SHALL use only a valid Handle for an
active Bundle or exactly one active Bundle found by trusted-scope discovery. An ended
Bundle requires an explicit `bundle_id`; a stale/ended Handle SHALL not guess a later
refinement round. `resume` SHALL remain
only a correlated response to a current pending interaction and SHALL not be interpreted
as a refinement. The Harness SHALL validate the target within trusted scope and durably
admit the refinement into that Bundle. It SHALL apply the refinement only at the next
safe durable control point and SHALL not mutate State beneath an in-flight writer or
replace a pending interaction. An explicit refinement of an available ended Bundle
SHALL start its next refinement round in the same Bundle while retaining prior materials
for inspection only when no different Bundle is active in that trusted scope; otherwise
it SHALL return the typed conflict/continuation outcome without mutating either Bundle.

#### Scenario: Mid-run refinement is admitted without overwriting a writer
- **WHEN** a valid refinement arrives while the selected Bundle has an in-flight State writer
- **THEN** the refinement is durably recorded for the next safe control point and the in-flight State update remains intact

#### Scenario: Ended Bundle begins a later refinement round
- **WHEN** a Primary User explicitly refines an available ended Bundle
- **THEN** the Harness reactivates that same Bundle for a later round and retains the prior report and evidence inside it

#### Scenario: Ended Handle cannot select a later round implicitly
- **WHEN** a Current Bundle Handle names an available ended Bundle but `refine` omits a `bundle_id`
- **THEN** the Harness returns a bounded explicit-target outcome and does not reactivate or mutate that Bundle

#### Scenario: Pending interaction remains a distinct resume subject
- **WHEN** a selected active Bundle awaits a correlated human response and the Primary User submits `refine`
- **THEN** the Harness records the refinement for a later safe point and leaves the current pending interaction unchanged for `resume`

#### Scenario: Ended target cannot displace another active Bundle
- **WHEN** a Primary User explicitly refines an available ended Bundle while a different Bundle is active in the same trusted scope
- **THEN** the Harness returns its typed conflict/continuation outcome and does not reactivate or mutate the ended Bundle

### Requirement: Bundle loss makes only that Run unavailable and is never recovered

External deletion, removal, unreadability, or integrity failure of a Run Bundle SHALL
make that Run unavailable. The Harness SHALL not recreate that Bundle, write a
replacement State, infer a status, or recover it from an external checkpoint, session
binding, registry, index, cache, log, diagnostic, or artifact copy. A newly started
independent Run SHALL remain legal and SHALL not reuse the lost Bundle identity.

#### Scenario: Deleted ended Bundle cannot be reopened
- **WHEN** an ended Bundle is deleted and a later status, inspection, or refinement targets its `bundle_id`
- **THEN** the outcome is unavailable and no external record recreates or authorizes the deleted Run

#### Scenario: Active Bundle disappears during execution
- **WHEN** an active Bundle is removed before a later authoritative State or content write
- **THEN** the Run stops with an unavailable outcome and no replacement directory or State is published

### Requirement: Run Bundles are isolated by conversation scope and evaluation domain

The Harness SHALL authorize discovery, control, State, and content access only within
the trusted outer-conversation scope of the selected Bundle. A Deep Research Run Bundle
SHALL not discover, authorize, or mutate another conversation's Bundle. Cognitive
Evaluation Run Workspaces and Bundles SHALL use their separate domain/storage/discovery
contract and SHALL not be candidates for Deep Research Run discovery or lifecycle
control.

#### Scenario: Foreign Bundle handle reveals no lifecycle facts
- **WHEN** a caller presents a valid-looking `bundle_id` belonging to another trusted conversation scope
- **THEN** the Harness returns the bounded foreign/not-found outcome without exposing the Bundle's State, content, or existence details

#### Scenario: Evaluation Bundle is not a Deep Research candidate
- **WHEN** an evaluation Run Bundle exists beneath its configured evaluation store
- **THEN** Deep Research scoped discovery does not enumerate, select, or mutate it

### Requirement: Typed lifecycle results are the only public control projection

The Harness SHALL return one typed lifecycle result for fresh start, status, control,
refinement, ended, conflict, ambiguous, and unavailable outcomes. Where disclosure is
valid, the result SHALL expose the bounded `bundle_id`, availability/lifecycle fact,
and legal next action. Tool, graph, CLI, TUI, workbench, agent instruction, diagnostic,
and inspection surfaces SHALL project that result and SHALL not infer lifecycle facts
from a path, report, session reference, cache, or checkpoint key.

#### Scenario: Human and AI consumers receive the same Bundle fact
- **WHEN** an available or unavailable control result is rendered by two supported entry surfaces
- **THEN** both projections use the same typed `bundle_id`/availability fact and communicate only legal next actions for that outcome

#### Scenario: Presentation cannot resume a lost Run
- **WHEN** a retained diagnostic or presentation cache still refers to a deleted Bundle
- **THEN** it can at most report an observation and cannot turn the unavailable result into a control or resume action

### Requirement: Bundle-local State writes are versioned, atomic, and single-writer

The Harness SHALL validate Bundle-local State schema/version before use, apply durable
State changes atomically, and reject an incompatible or corrupt State without silently
resetting, auto-migrating, or replacing it. It SHALL preserve terminal monotonicity,
idempotent replay of the same admitted action, and a single authoritative writer for
each mutation. A stale or conflicting writer SHALL leave the last valid State intact
and return a bounded control outcome. (`DRH-008`)

#### Scenario: Conflicting State mutation cannot overwrite an admitted refinement
- **WHEN** a stale lifecycle writer attempts to commit after a newer safe-point State mutation
- **THEN** the Bundle retains the valid newer State and the stale writer cannot create a second State or partially overwrite the admitted refinement
