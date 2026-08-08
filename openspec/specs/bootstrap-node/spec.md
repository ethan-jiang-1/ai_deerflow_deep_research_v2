# bootstrap-node Specification

> req: BON-001, BON-002, BON-003, BON-004, BON-005, BON-006, BON-007

## Purpose

The real bootstrap node owns atomic establishment of the minimal research bundle directory and
its schema/version marker, pure binding validation, deterministic failure/recovery handling, and
research-scoped establishment that preserves start/resume/status/cancel lifecycle invariants. It
performs no research model call; identity derivation and start/idempotency/conflict semantics
remain owned by the lifecycle handler (REG-004).
## Requirements

### Requirement: Harness publishes a Run Bundle before Bootstrap establishes contained content

The Harness lifecycle module SHALL atomically publish the minimal valid Run Bundle and
its initial Bundle-local State before any graph route is discoverable. The real Bootstrap
node SHALL then atomically establish only its required `request/` bootstrap content
inside that preselected Bundle. A versioned marker, when retained, SHALL bind the
opaque `bundle_id`, start-message correlation, request digest, and State schema version;
it SHALL not carry a legacy research identity or select a root. Bootstrap SHALL reuse
the shared-workspace capability's bounded POSIX lock, same-directory replace, and
durability sync, and SHALL fail closed with `work_unit_storage_unavailable` on an
unsupported provider before writing. A partial bootstrap write SHALL not be treated as a
discoverable or active Run and SHALL not create evidence, work-spec, or DPT control
files. (`BON-001`)

#### Scenario: Bootstrap content binds the selected Bundle identity
- **WHEN** real Bootstrap runs for a freshly published Bundle with valid initial State
- **THEN** it writes any required request marker beneath that Bundle and the marker's `bundle_id`, start correlation, request digest, and schema version equal the selected Bundle State before it routes

#### Scenario: Partial bootstrap content is not mistaken for Run authority
- **WHEN** bootstrap content creation is interrupted or its marker is missing/mismatched
- **THEN** the node fails closed or performs its bounded contained repair; discovery never treats the partial content as a new active or completed Run

#### Scenario: Unsupported workspace fails closed before any write
- **WHEN** the shared-workspace capability is unavailable for the selected Bundle's provider/mount
- **THEN** bootstrap raises `work_unit_storage_unavailable` before creating a replacement directory or marker

### Requirement: Bootstrap binding-validation determines the route

The real Bootstrap node SHALL run a pure binding validation that compares any
Bundle-contained bootstrap marker to the selected Bundle-local State and determines the
Bootstrap route from that validation, replacing the fake fixture pass. The validation
SHALL produce typed `FailureCode` values from the closed gate-kernel registry and SHALL
perform no research model, web, MCP, ACP, or DeerFlow `task` subagent call. Bootstrap
shall remain non-gated, SHALL NOT consult `fixture_plan`, and on a successful binding
shall route `needs_input` to `hitl1` without emitting `profile_complete`.
(`BON-002`)

#### Scenario: Bound marker routes to HITL1 with no model call
- **WHEN** a retained Bootstrap marker and Bundle State agree on Bundle identity, start correlation, request digest, and schema version
- **THEN** Bootstrap routes `needs_input` to `hitl1` and makes no research model call

#### Scenario: Marker divergence is rejected and fails closed
- **WHEN** read-back content diverges from the selected Bundle State after Bootstrap writes
- **THEN** validation produces a typed `FailureCode` and Bootstrap fails closed rather than routing onward

### Requirement: Bootstrap failure is deterministic and fail-closed

Bootstrap failure SHALL perform deterministic cleanup and bounded retry with typed failure codes
and SHALL never invoke a research LLM or publish an inconsistent bundle or route. Recoverable
establishment failures (partial directory, transient lock contention, or a stale/mismatched
marker found on entry) SHALL be cleaned up and retried internally up to a bound. A divergence
or unsupported marker `schema_version` that persists AFTER a fresh establish indicates
corruption (the marker was just written bound to this checkpoint) and SHALL fail closed to a
terminal `BLOCKED` lifecycle with `route=exhausted` so the topology routes to `END`; exhausted
retries likewise fail closed.

#### Scenario: Recoverable failure is retried without a model call
- **WHEN** a recoverable failure occurs (partial directory, transient lock contention, or a stale/mismatched marker found on entry)
- **THEN** the bootstrap cleans up and retries internally up to a bound, succeeds, and makes no research LLM call

#### Scenario: Post-establish divergence terminates fail-closed
- **WHEN** a fresh establish completes but the read-back marker still diverges from the checkpoint, or retries are exhausted
- **THEN** the bootstrap sets `terminal_status=BLOCKED` with `route=exhausted` toward `END` and publishes no inconsistent bundle or route

#### Scenario: No research surface is invoked on failure
- **WHEN** bootstrap establishment or validation fails
- **THEN** no research LLM, web, MCP, ACP, or DeerFlow `task` subagent call is made

### Requirement: Bootstrap preserves lifecycle invariants and keeps establishment research-scoped

Bootstrap SHALL not weaken the lifecycle module's start/resume/status/cancel/refine
invariants: duplicate same-command delivery reprojects instead of publishing another
Bundle, a different start while an active Bundle exists returns the typed
continuation/conflict result, and an already-ended Bundle is not re-established by
Bootstrap. Its own contained store SHALL be scoped to the preselected `bundle_id`
alone, SHALL not read, write, or bind another Bundle, and SHALL fail closed when a
marker schema or Bundle identity disagrees with Bundle-local State. Trusted-scope
isolation is supplied by the lifecycle module and is not reimplemented by Bootstrap.
(`BON-004`)

#### Scenario: Bootstrap is Bundle-scoped
- **WHEN** Bootstrap writes content for Bundle A
- **THEN** it touches only Bundle A's contained paths and never reads, writes, or binds Bundle B

### Requirement: Real bootstrap integrates into the mixed implementation map

The real bootstrap factory SHALL be selectable by the existing per-node fake/real implementation
map (REG-001) while preserving the normalized topology and all-fake recipe. The lifecycle
handlers SHALL be able to run a mixed graph, so `ResearchGraphRecipe` SHALL accept an
`implementation_modes` override (default all-fake). The mixed-graph end-to-end run SHALL report
`implementation_mode=mixed`; it SHALL not use `full_fake` merely because the selected prefix
produces no final research report.

#### Scenario: Mixed map selects the real bootstrap
- **WHEN** the implementation map selects `real` for bootstrap and `fake` for every other phase
- **THEN** the graph compiles, the real bootstrap factory is selected (not the unavailable sentinel), and the normalized node order and all non-bootstrap edges are unchanged

#### Scenario: Lifecycle handlers can run the mixed graph
- **WHEN** `ResearchGraphRecipe` is created with `implementation_modes` setting `bootstrap=real` and every other phase `fake`
- **THEN** the lifecycle handlers compile and run the mixed graph, select the real bootstrap factory, report `implementation_mode=mixed`, and leave the default recipe all-fake

#### Scenario: Full-fake map is unchanged
- **WHEN** the implementation map selects `fake` for every phase
- **THEN** the fake bootstrap is selected and the full-fake lifecycle end-to-end path is unchanged

#### Scenario: Mixed end-to-end reports mixed
- **WHEN** the mixed graph runs end-to-end through bootstrap and the remaining fake phases
- **THEN** bootstrap establishes the bundle and routes to `hitl1`, every remaining fake phase completes without a research model call, and the lifecycle result reports `implementation_mode=mixed`

### Requirement: Bootstrap resolves contained paths through the runtime-bound Bundle reference

Bootstrap SHALL receive a runtime-bound selected Bundle reference and resolve all
contained paths through that reference. It SHALL not compute a root from `research_id`,
accept a caller locator, select an external checkpoint root, migrate a legacy root, or
copy content into a replacement directory. It SHALL reject malformed identity, symlink,
path escape, and cross-Bundle marker conditions before routing. (`BON-006`)

#### Scenario: Bootstrap writes only through the selected Bundle reference
- **WHEN** Bootstrap receives a valid selected Bundle
- **THEN** it writes required bootstrap content under that Bundle's private contained root and exposes no physical locator

### Requirement: Bootstrap consumes a preselected Run Bundle and cannot create a second authority

Bootstrap SHALL receive one runtime-selected Run Bundle reference and SHALL establish
only the Bundle-contained bootstrap content required by its node contract. It SHALL not
derive a research identity, choose a Bundle directory, select an external checkpoint,
or publish a parallel lifecycle marker. Its writes SHALL be contained in the selected
Bundle and SHALL fail closed when that Bundle is unavailable. (`BON-007`)

#### Scenario: Bootstrap cannot write after Bundle loss
- **WHEN** the selected Bundle disappears before Bootstrap performs an authoritative content write
- **THEN** Bootstrap reports the lifecycle unavailable outcome and creates no replacement root or marker
