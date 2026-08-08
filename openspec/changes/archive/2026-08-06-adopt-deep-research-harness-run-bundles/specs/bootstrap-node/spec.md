> req: BON-001, BON-002, BON-004, BON-006, BON-007

## ADDED Requirements

### Requirement: Bootstrap consumes a preselected Run Bundle and cannot create a second authority

Bootstrap SHALL receive one runtime-selected Run Bundle reference and SHALL establish
only the Bundle-contained bootstrap content required by its node contract. It SHALL not
derive a research identity, choose a Bundle directory, select an external checkpoint,
or publish a parallel lifecycle marker. Its writes SHALL be contained in the selected
Bundle and SHALL fail closed when that Bundle is unavailable. (`BON-007`)

#### Scenario: Bootstrap cannot write after Bundle loss
- **WHEN** the selected Bundle disappears before Bootstrap performs an authoritative content write
- **THEN** Bootstrap reports the lifecycle unavailable outcome and creates no replacement root or marker

## RENAMED Requirements

- FROM: `### Requirement: Bootstrap atomically establishes the research bundle`
- TO: `### Requirement: Harness publishes a Run Bundle before Bootstrap establishes contained content`
- FROM: `### Requirement: Bootstrap establishes the checkpoint-selected canonical bundle root`
- TO: `### Requirement: Bootstrap resolves contained paths through the runtime-bound Bundle reference`

## MODIFIED Requirements

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

### Requirement: Bootstrap resolves contained paths through the runtime-bound Bundle reference

Bootstrap SHALL receive a runtime-bound selected Bundle reference and resolve all
contained paths through that reference. It SHALL not compute a root from `research_id`,
accept a caller locator, select an external checkpoint root, migrate a legacy root, or
copy content into a replacement directory. It SHALL reject malformed identity, symlink,
path escape, and cross-Bundle marker conditions before routing. (`BON-006`)

#### Scenario: Bootstrap writes only through the selected Bundle reference
- **WHEN** Bootstrap receives a valid selected Bundle
- **THEN** it writes required bootstrap content under that Bundle's private contained root and exposes no physical locator
