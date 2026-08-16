# targeted-evidence-loop Specification

> req: TEL-001, TEL-002, TEL-003, TEL-004, TEL-005, TEL-006, TEL-007
## Purpose
Bounded gap-to-evidence loop with convergence gate, targeted workers, and critic integration.

## Requirements



### Requirement: Gap router converts synthesis gaps to targeted WorkSpecs
The gap router SHALL read the bounded gate-owned `unresolved_gaps` id projection derived from validated canonical synthesis gaps and SHALL produce one WorkIntent per gap id with scoped search dimensions. It SHALL NOT infer routing authority from a description, a finding flag, a caller-supplied gap body, or any checkpoint field not written by the current Wave2 gate. An empty projection SHALL pass through without error.

#### Scenario: Gaps become work intents
- **WHEN** the current Wave2 gate projects ids for validated canonical `search_required=true` gaps
- **THEN** one WorkIntent per gap is materialized

#### Scenario: Empty gaps pass through
- **WHEN** the current Wave2 gate has no searchable gap ids
- **THEN** the router returns empty intents and the node passes through

#### Scenario: Descriptive text cannot schedule work
- **WHEN** gap prose asks for more research but the current Wave2 gate does not project its id
- **THEN** the router does not materialize a WorkIntent

### Requirement: Targeted worker performs focused gap search
A bounded web worker SHALL search for evidence addressing one assigned gap. The initial request SHALL require and permit exactly one web search tool call, use its multiple returned candidates as the evidence set, and retain later model turns for its structured answer. Output SHALL include new source refs and a gap resolution status, and the worker SHALL NOT modify synthesis findings directly. If the first successful agent result cannot be parsed, validated as the targeted worker schema, or bound to the assigned gap id, the node SHALL make exactly one separate repair request with tools disabled, the assigned gap identity and stable validation failure metadata, and the bounded untrusted draft. A valid repair SHALL proceed through the existing materializer, validator, and ledger submit boundary. A failed, non-successful, wrong-gap, or schema-invalid repair SHALL fail closed without result/source artifact or ledger authority.

#### Scenario: Worker finds evidence for a gap
- **WHEN** worker searches for evidence addressing a gap and returns valid structured output
- **THEN** new sources are recorded with backing refs and gap status is updated without a repair call

#### Scenario: Prose answer is repaired once without tools
- **WHEN** the initial worker uses its exactly one allowed web search but its successful final answer is prose, schema-invalid, or names a different gap
- **THEN** one zero-tool repair request may convert the bounded draft into a valid response for the same assigned gap

#### Scenario: Invalid repair publishes no authority
- **WHEN** the single repair is non-successful, malformed, schema-invalid, or names a different gap
- **THEN** the work attempt fails without publishing source artifacts, a targeted result artifact, or a submission-ledger record

#### Scenario: Repair cannot perform more research
- **WHEN** the repair request executes
- **THEN** no web or filesystem tool is exposed and no tool call is dispatched

### Requirement: Convergence gate enforces round budget and fatigue
The convergence gate SHALL track round count per phase and SHALL enforce a maximum round budget. Repeated failures on the same gap SHALL trigger fatigue detection. Exhausted budget SHALL route exhausted.

#### Scenario: Round budget exhausted
- **WHEN** max rounds reached without resolving all gaps
- **THEN** gate routes exhausted with remaining gaps deferred

#### Scenario: Fatigue detected on repeated failure
- **WHEN** the same gap fails resolution across multiple rounds
- **THEN** the gap is marked deferred and does not consume further budget

### Requirement: Mixed-graph integration requires full real chain
Real targeted evidence loop SHALL require full real chain through wave2_synthesis. Full-fake targeted_evidence SHALL remain deterministic. Topology SHALL be unchanged.

#### Scenario: Full real chain compiles
- **WHEN** recipe selects targeted_evidence=real with full chain through wave2_synthesis
- **THEN** graph compiles and preserves topology shape

### Requirement: Targeted evidence retains classified invocation causes through work-unit failure

Targeted evidence SHALL normalize every non-successful worker or repair invocation
before it reaches the existing work-unit controller. It SHALL retain the applicable
closed worker category and safe provider observation when known, and it SHALL leave
retry, aggregation, target routing, and terminal projection with the existing
controller.

#### Scenario: A targeted worker timeout is not reduced to a generic worker error
- **WHEN** a targeted evidence worker receives a safe provider timeout result
- **THEN** it emits a classified work-attempt failure preserving the safe cause and
  does not write an accepted evidence artifact or advance the target loop

### Requirement: Targeted evidence capabilities remain gap-scoped and read-only by role

The real targeted worker initial request SHALL bind its required local retrieval
capability and make exactly one permitted retrieval call for one gate-projected gap.
Its structured repair SHALL bind a distinct forbidden capability and SHALL receive
only the assigned gap, bounded draft, and validation facts; it SHALL not retrieve or
add a source, URL, title, fact, or gap identity absent from those observations.
SourceDiagnostic and ClaimVerifier SHALL each bind a distinct forbidden local
capability, receive only their assigned references and delimited untrusted material,
and return candidates that reference only that assignment. Existing work-unit
validation, controller, ledger, critic materializer, and gate owners SHALL remain the
only authorities that admit evidence, artifacts, outcomes, or routes. (`TEL-005`)

#### Scenario: One gate-projected gap permits one bounded retrieval
- **WHEN** a scripted real targeted worker receives one valid gate-projected gap
- **THEN** exactly one permitted retrieval occurs, the model cannot change the gap,
  findings, gate, or ledger, and only validator-approved same-gap source candidates
  reach the existing submission path

#### Scenario: Repair cannot invent targeted evidence
- **WHEN** the targeted worker's initial draft is malformed or names a different gap
- **THEN** its zero-tool repair either returns a contract-valid result constrained to
  the assigned gap and retained observations or follows the existing non-admission
  outcome without a source artifact or ledger record

#### Scenario: Critics cannot escape assigned references or read-only posture
- **WHEN** a scripted SourceDiagnostic or ClaimVerifier candidate names an unassigned
  source reference or attempts a tool call
- **THEN** the zero-tool runtime posture prevents dispatch and the existing validator
  or materializer rejects the out-of-scope candidate without writing critic, ledger,
  gate, or route authority

### Requirement: Targeted-evidence calibration preserves gap-scoped judgment boundaries

The targeted worker, its existing zero-tool repair, SourceDiagnostic, and ClaimVerifier SHALL make
model-visible the criteria for gap-scoped source/evidence candidates, provenance, counterevidence,
uncertainty, and honest non-resolution. The worker SHALL preserve its existing single gate-projected
gap and exactly-one retrieval posture. Its repair SHALL receive only the assigned gap, bounded draft,
retained observations, and closed validation facts; it SHALL not retrieve, add source/fact/gap
identity, or receive ledger, artifact, gate, retry, or route authority. Each critic SHALL receive
only assigned references and delimited untrusted material. Validator, controller, materializer,
ledger, convergence gate, and route owners SHALL remain the only authorities that admit candidates
or decide outcomes.

#### Scenario: Calibrated targeted worker remains one-gap and provenance-bounded
- **WHEN** a targeted worker receives one gap projected by the current Wave2 gate
- **THEN** it makes only its existing one retrieval and returns a candidate limited to that gap,
  observed source metadata, uncertainty, and resolution status without changing control state

#### Scenario: Repair and critics cannot broaden targeted evidence authority
- **WHEN** a repair, SourceDiagnostic, or ClaimVerifier receives malformed, incomplete, or
  out-of-scope untrusted material
- **THEN** its zero-tool candidate remains bounded to its gap or references, and invalid output
  produces no source/result/review artifact, ledger update, gate decision, or route authority

### Requirement: Targeted evidence node conforms to the work-unit gate-view protocol

The real targeted_evidence node SHALL return the reconciled `WorkUnitGateView` under
the reserved key on every visit. A visit with a non-empty gap projection SHALL
return the view built by its existing shared work-unit component; a gap-less visit
SHALL return the canonical empty drained view (no planned work, nothing to
reconcile) because the shared component's plan bound requires at least one intent.
It SHALL NOT derive routing authority from gap presence or absence, SHALL NOT
raise `work_unit_gate_view_inconsistent` for a visit routed with a non-empty or an
empty `unresolved_gaps` projection, and SHALL NOT build a view that claims planned
or accepted work for a gap-less visit. The reserved key SHALL follow the existing
work-unit kernel contract: the wrapper pops and type-checks it, and it SHALL never be
a `ResearchState` field or reach checkpoint serialization.

#### Scenario: A gap visit returns the reconciled view
- **WHEN** the Wave2 gate routes `evidence_needed` with non-empty `unresolved_gaps`
- **THEN** the targeted_evidence node returns the component-built `WorkUnitGateView` under the reserved key and the wrapper admits it without raising `work_unit_gate_view_inconsistent`

#### Scenario: An empty-gap visit returns a drained view
- **WHEN** targeted_evidence runs with an empty gap projection
- **THEN** the node returns the canonical empty drained `WorkUnitGateView` with no planned work and the wrapper admits it without raising `work_unit_gate_view_inconsistent`

#### Scenario: The reserved key never becomes checkpoint state
- **WHEN** the wrapper extracts the reserved key from the targeted_evidence result
- **THEN** the view is injected only into the in-memory gate mapping and is omitted from the final state update, matching the existing work-unit kernel contract
