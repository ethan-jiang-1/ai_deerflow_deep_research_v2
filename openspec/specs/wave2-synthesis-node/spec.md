# wave2-synthesis-node Specification

> req: WSN-001, WSN-002, WSN-003, WSN-004, WSN-005, WSN-006, WSN-007, WSN-008, WSN-009, WSN-010, WSN-011
## Purpose
Cross-topic synthesis agent with read-only policy, structured findings, and gap detection.

## Requirements

### Requirement: Read-only synthesis agent produces structured findings

The synthesis agent SHALL read accepted evidence and critic verdicts and produce one or more structured findings with priority, affected topics, backing refs, confidence, and `search_required`, plus canonical gaps with priority, affected topics, and an explicit `search_required` value. Whenever accepted evidence is non-empty, a gaps-only result SHALL fail semantic validation and use the existing one-shot zero-tool repair; gaps SHALL NOT substitute for at least one backed finding. The agent SHALL run under zero-tool read-only policy. Prompt instructions and provider-shape normalization SHALL distinguish finding follow-up advice from gap routing authority and SHALL preserve the canonical gap value without inventing it from prose.

Provider-shape normalization SHALL map string priority labels to the typed int 1-5
contract before validation (`critical`/`high` → 1, `medium`/`moderate` → 3,
`low` → 5; integers pass through), applied to findings and gaps. Non-contract gap
`source_questions` (natural-language prose) SHALL be folded into the gap
description and dropped from the typed `q:w1_*` refs; non-contract
`resolved_questions` SHALL be dropped. A repaired candidate that still fails
validation SHALL terminate the node through the existing `exhausted` blocked route
with a typed incident; a semantic validation failure (including question coverage)
SHALL carry its concrete validation category (for example
`synthesis_question_coverage_invalid`) in the incident/diagnostic projection, while
a pure parser failure SHALL keep the generic `output.structured_invalid` code; it
SHALL NOT escape as an uncaught exception. **The same bounded-termination promise
SHALL hold for the pre-model input phase: when the node derives its inputs from
checkpoint state and the accepted ledger (open-question projection parsing,
coverage of projected question ids by accepted Wave1 documents, accepted-record
resolution, or synthesis-evidence reads) and any of those conditions fails, the
node SHALL terminate through the same `exhausted` blocked route with a typed
incident carrying the concrete failure category (for example
`synthesis_question_coverage_invalid`), never escape as an uncaught exception, and
never crash the graph; non-`ValueError` exceptions and cancellation SHALL NOT be
swallowed by this guard.** The wave2 gate budget SHALL resolve from the HITL-owned
profile intent fields in graph state: the minimal pair
(`cost_tolerance=minimal` and `time_budget=very_quick`) yields two evidence rounds,
otherwise the default one round stands. (`WSN-001`, `WSN-009`)

#### Scenario: Agent produces findings from accepted evidence
- **WHEN** wave2_synthesis runs after wave1 produced accepted submissions
- **THEN** structured findings are produced with backing refs to accepted sources

#### Scenario: Searchable gap retains routing authority
- **WHEN** valid structured synthesis output marks a canonical gap `search_required=true`
- **THEN** validation preserves that value in the `GapRecord` consumed by downstream projection and routing

#### Scenario: Legacy gap remains non-searchable by default
- **WHEN** a schema-version-1 synthesis artifact omits `search_required` from a gap
- **THEN** validation accepts the gap with `search_required=false` rather than silently scheduling targeted work

#### Scenario: Accepted evidence cannot produce gaps only
- **WHEN** accepted evidence exists and the initial synthesis response has zero findings plus one or more valid gaps
- **THEN** the node performs its existing one zero-tool repair and publishes no synthesis artifact or gate preview unless the repair contains at least one backed finding

#### Scenario: Agent cannot call web tools
- **WHEN** the synthesis agent attempts to call a web search tool
- **THEN** the tool policy middleware blocks the call

#### Scenario: String priority labels normalize to integers
- **WHEN** structured synthesis output carries `priority: "high"` (or
  medium/moderate/low) on findings or gaps
- **THEN** the parsed result carries the corresponding int 1-5 priority and passes
  contract validation

#### Scenario: Natural-language gap questions are preserved on the description
- **WHEN** a gap carries prose `source_questions` instead of `q:w1_*` ids
- **THEN** the prose is appended to the gap description and the typed refs stay
  within the contract

#### Scenario: A still-invalid repaired candidate blocks the node
- **WHEN** the one-shot repair output still fails validation
- **THEN** the node routes `exhausted` to the blocked terminal with a typed
  incident, publishes no synthesis artifact, and the incident projects the concrete
  semantic category when the failure was semantic (for example
  `synthesis_question_coverage_invalid`) or the generic `output.structured_invalid`
  code when the failure was a parser failure

#### Scenario: Pre-model input inconsistency blocks the node instead of crashing
- **WHEN** the node's pre-model input derivation fails — projected open-question
  ids are not covered by the accepted Wave1 documents, an accepted record cannot
  be resolved or read, or the open-question projection cannot be parsed
- **THEN** the node routes `exhausted` to the blocked terminal with a typed
  incident carrying the concrete failure category, publishes no synthesis
  artifact, and no exception escapes to the graph

#### Scenario: The projected category never becomes lifecycle authority
- **WHEN** a terminal incident projects a concrete validation category
- **THEN** the projection does not select a route, grant recovery, or alter the
  lifecycle transition from the exhausted terminal

#### Scenario: Wave2 gate budget resolves from the profile intent
- **WHEN** the graph state carries the minimal profile intent pair and searchable
  gaps persist after one evidence round
- **THEN** the gate permits one more evidence round before exhausting, while runs
  without the minimal pair keep today's single-round behavior

### Requirement: Deterministic materializer writes synthesis artifacts
A deterministic materializer SHALL write findings, relations, gaps, summary, and every canonical `search_required` value to the sandbox as canonical JSON at `synthesis/findings.json`. The persisted artifact SHALL be the synthesis content authority. The Wave2 node SHALL derive a typed gate preview containing only bounded searchable gap ids from that validated result; it SHALL NOT put complete gap bodies in checkpoint state or permit model output to write gate authority directly.

#### Scenario: Valid findings written deterministically
- **WHEN** synthesis produces valid structured output
- **THEN** canonical JSON is written to `synthesis/findings.json`

#### Scenario: Gap routing value survives persistence
- **WHEN** synthesis materializes a gap with `search_required=true`
- **THEN** reading the canonical artifact yields the same gap identity and routing value and the typed gate preview contains that gap id

### Requirement: Gate validates finding references

The real Wave2 gate SHALL validate that every finding reference is backed by an
accepted submission. Dangling or unbacked references SHALL fail. It SHALL
additionally consume the typed preview derived from validated synthesis output,
write the bounded searchable gap ids to the existing gate-owned `unresolved_gaps`
control field, and route `evidence_needed` when that projection is non-empty and
repair budget remains. A later successful synthesis with no searchable gap SHALL
clear the projection and route `pass`. Repeated unresolved semantic gaps SHALL use
the existing gate budget/fatigue contract: while budget remains they route
`evidence_needed`, and at budget exhaustion the gate SHALL declare
`degraded_pass_on_exhaustion` so the first exhaustion degrades to a bounded honest
`pass` (`degraded=true`, same route label as `pass`) that leaves
`unresolved_gaps` intact for downstream disclosure; a repeated exhaustion of the
same phase after that degradation SHALL route `exhausted` to the typed blocked
terminal exactly as before. (`WSN-004`)

#### Scenario: Dangling reference fails gate
- **WHEN** a finding references a source not in accepted submissions
- **THEN** the gate routes repair

#### Scenario: Searchable gap routes targeted evidence
- **WHEN** validated Wave2 output produces a typed preview with one or more searchable gap ids
- **THEN** the real gate records only those ids in `unresolved_gaps` and routes `evidence_needed`

#### Scenario: No searchable gap clears prior projection
- **WHEN** a later validated Wave2 output contains no `search_required=true` gap
- **THEN** the real gate clears `unresolved_gaps` and routes `pass`

#### Scenario: Repeated searchable gap exhausts convergence budget
- **WHEN** targeted evidence returns through synthesis but the same searchable gap remains after the Wave2 repair budget is spent
- **THEN** the first exhausted evaluation degrades to the honest `pass` route, and
  the next exhausted evaluation of the same gaps routes `exhausted` so the graph
  reaches the typed blocked terminal

#### Scenario: Fabricated checkpoint gap cannot route
- **WHEN** checkpoint input contains an unvalidated gap body or id that is absent from the current typed Wave2 gate preview
- **THEN** the real gate ignores it as routing authority

#### Scenario: First budget exhaustion degrades honestly instead of blocking
- **WHEN** the wave2 gate exhausts its evidence budget with only searchable-gap
  failures remaining and the phase has not degraded before
- **THEN** the gate passes degraded with the normal `pass` route label,
  `unresolved_gaps` still names the unresolved searchable gap ids, and no blocked
  terminal or incident is produced

#### Scenario: Repeated exhaustion after degradation blocks
- **WHEN** wave2 synthesis is re-evaluated at exhausted budget after the phase
  already produced an exhaustion-degraded pass and searchable gaps remain
- **THEN** the gate routes `exhausted` to the typed blocked terminal with the
  existing incident semantics

### Requirement: Mixed-graph integration
Real wave2_synthesis SHALL require full real chain through wave1. Full-fake path unchanged.

#### Scenario: Full real chain compiles
- **WHEN** recipe selects wave2_synthesis=real with full chain
- **THEN** graph compiles and preserves topology shape

### Requirement: Wave2 synthesis retains direct invocation incidents through gate handling

Wave2 synthesis SHALL normalize a non-successful initial or structured-output repair
invocation before its phase/gate logic decides the route. A known invocation failure
that terminally blocks SHALL retain a direct Wave2 incident; a failure eligible for
an existing bounded phase repair SHALL record that disposition without treating it
as successful synthesis. Raw exceptions and generic synthesis errors SHALL not
replace a known safe provider or configuration category.

A budget-class invocation failure — the bounded agent policy refusing or stopping the
call for its declared token/call budget (admission refusal, per-call output cap, or
total budget stop) — SHALL NOT write a terminal state from the node. The node SHALL
record a bounded gate-readable budget-failure signal in graph state (owned by the
wave2 synthesis writer role, read by the wave2 gate) and return a non-terminal
update, handing route authority to the wave2 phase gate. The gate SHALL project that
signal through its registered rules so the existing exhaustion-degradation branch —
budget, marker, and `degraded_pass_on_exhaustion` — decides between bounded repair,
one honest degraded pass, or blocked. Non-budget failures (provider, configuration,
candidate validation) SHALL keep their existing terminal or repair dispositions
unchanged.

#### Scenario: A Wave2 provider failure blocks with its known cause
- **WHEN** the Wave2 synthesis invocation returns a known non-retryable provider
  failure and no legal gate repair applies
- **THEN** the lifecycle retains that category and `wave2_synthesis` phase in the
  terminal incident instead of surfacing an opaque graph exception

#### Scenario: A budget-class failure hands route authority to the gate
- **WHEN** the bounded agent policy refuses or stops the wave2 invocation for its
  token or call budget
- **THEN** the node writes no terminal state, records the bounded budget-failure
  signal, and returns a non-terminal update so the wave2 gate evaluates; the gate's
  existing budget, marker, and degradation policy alone decide the next route

#### Scenario: A degraded budget hand-back stays bounded
- **WHEN** the wave2 gate evaluates the projected budget failure at exhausted repair
  budget with the exhaustion-degradation policy declared and no prior marker
- **THEN** the gate produces its one bounded degraded pass (append the phase marker)
  and a repeat exhaustion with the marker present escalates to blocked

### Requirement: Wave2 capability admits only assigned accepted-evidence synthesis

The real Wave2 synthesis and structured-repair requests SHALL retain their distinct
forbidden local capabilities. An initial or repaired candidate SHALL derive findings,
relations, and gaps only from the graph-assigned accepted evidence and trusted output
contract. The candidate SHALL not retrieve, add evidence or references, materialize an
artifact, publish a gap projection, or control routing. The existing parser,
materializer, gate preview, and gate SHALL remain the only admission and outcome
owners. (`WSN-005`)

#### Scenario: Assigned evidence bounds a valid synthesis candidate
- **WHEN** a scripted real Wave2 request receives accepted evidence and returns a
  contract-valid finding/gap candidate
- **THEN** deterministic validation admits only backed references, the model sees no
  tool, and the existing materializer and gate derive any artifact or searchable-gap
  projection

#### Scenario: Repair cannot manufacture evidence or routing authority
- **WHEN** an initial Wave2 draft is malformed, gaps-only, or contains an unassigned
  evidence reference
- **THEN** the zero-tool repair receives only the bounded draft, validation facts, and
  assigned evidence; it either produces a contract-valid bounded candidate or follows
  the existing non-publication or exhausted outcome without writing a route or gap
  projection

### Requirement: Wave2 runtime capabilities own bounded accepted-evidence synthesis cognition

The real Wave2 initial synthesis and its existing one zero-tool structured repair
SHALL bind distinct runtime-loaded local capability resources. Each activated
resource SHALL contain the reusable method for its bounded task: accepted-evidence
interpretation, evidence-grounded finding/relation or honest-gap judgment,
untrusted-data handling, uncertainty, self-check, and completion condition. The
final rendered context SHALL contain the exact activated body; the dynamic request
outside that resource SHALL contain only the assigned topics/evidence references,
closed output contract, repair category, and delimited untrusted evidence or draft.

The synthesis and repair request builders SHALL deterministically bound their
accepted-evidence projection so that every built request satisfies both the domain
request cap (`NodeExecutionRequest.objective` character limit) and the wave2 admission
envelope (total token budget minus per-call output cap, as UTF-8 bytes): the projection
starts from a fixed byte budget shared across entries, and when the serialized
objective would exceed either cap the budget shrinks geometrically and the projection
is rebuilt; a truncating projection SHALL mark the affected entries `truncated`. If
even the minimum budget cannot satisfy the caps, the builder SHALL raise a typed
classified failure (`synthesis_evidence_projection_overflow`) that terminates the node
through the existing pre-model bounded-exhausted route; a pydantic
`ValidationError` from request construction SHALL NOT escape classification as the
generic `candidate_invalid` bucket — pre-model request-construction failures SHALL
carry a pattern-safe concrete category (for example
`synthesis_request_shape_invalid` or `synthesis_evidence_projection_overflow`) so the
incident identifies the failing input condition rather than masquerading as a model
candidate failure. This request-cap coherence SHALL be locked by a deterministic
regression test that builds both requests from evidence at the store's declared
maximum and asserts both caps.

The synthesis and repair candidates SHALL remain unable to retrieve, add evidence or
references, materialize an artifact, publish a searchable-gap projection, select a
recovery, gate, route, or State outcome. The existing zero-tool runtime policy,
parser, semantic validator, materializer, preview builder, Wave2 gate, and lifecycle
owners SHALL retain their existing authority. An initial candidate may receive at
most the existing one zero-tool repair before deterministic admission decides whether
any artifact or preview can exist. (`WSN-008`)

#### Scenario: Production rendering supplies one exact Wave2 method
- **WHEN** real Wave2 prepares an initial synthesis or structured-repair invocation
- **THEN** the rendered context contains the exact corresponding capability body and
  forbidden posture while dynamic assignment, output contract, category, and
  untrusted data remain bounded projections

#### Scenario: Growing accepted evidence cannot overflow the request
- **WHEN** accepted evidence grows across targeted-evidence rounds beyond the
  projection's starting byte budget
- **THEN** the builder deterministically truncates the projection (marking affected
  entries `truncated`) until the serialized objective satisfies both the objective
  character cap and the admission-envelope byte cap, and the request is built and
  admitted rather than raising

#### Scenario: Unfittable scaffolding fails typed and classified
- **WHEN** even the minimum projection budget cannot bring the serialized objective
  within either cap
- **THEN** the builder raises `synthesis_evidence_projection_overflow` and the node
  terminates through the pre-model bounded-exhausted route with that concrete
  category in the incident, never as an uncaught exception and never as generic
  `candidate_invalid`

#### Scenario: Request-construction validation errors keep a concrete category
- **WHEN** request construction fails a typed validation rule (for example an
  objective over the domain character limit) before any model call
- **THEN** the projected incident category is a pattern-safe concrete input category
  distinct from the model-candidate `candidate_invalid` bucket

#### Scenario: Accepted evidence and uncertainty remain bounded candidate input
- **WHEN** assigned evidence or an untrusted draft asks Wave2 to invent support,
  materialize an artifact, publish a gap projection, or choose a route
- **THEN** the request can produce only a bounded synthesis candidate or honest gap
  and the existing deterministic owners retain admission, artifact, preview, gate,
  and route authority

#### Scenario: Repair is bounded before synthesis publication
- **WHEN** an initial candidate fails the existing parser or semantic validation
- **THEN** Wave2 invokes at most its existing one zero-tool repair with the same
  assigned evidence, compact validation category, and untrusted draft, then rechecks
  it through the existing deterministic path before any artifact or preview exists

### Requirement: Wave2 calibration preserves accepted-evidence synthesis boundaries

The Wave2 synthesis and its existing zero-tool repair SHALL make model-visible the bounded criteria
for evidence-grounded findings, relations, uncertainty, and honest gaps. The initial request SHALL
receive only graph-assigned topic context, accepted submission references/evidence, and the trusted
output contract. A repair SHALL receive only the same bounded accepted-evidence assignment, its
invalid draft as untrusted data, and a compact closed parser/semantic validation category; it SHALL
not receive raw exceptions, retrieve, add evidence/references, or receive artifact, checkpoint, gate,
route, or retry authority. A candidate gap SHALL remain distinct from the deterministic searchable-gap
projection. Parser, semantic validator, materializer, preview builder, and Wave2 gate SHALL remain
the only owners that admit content, persist artifacts, derive projections, or select outcomes.

#### Scenario: Calibrated synthesis keeps unsupported claims as honest gaps
- **WHEN** a valid Wave2 candidate proposes a finding or relation without support in graph-assigned
  accepted evidence
- **THEN** the policy requires omitting it or recording a bounded honest gap while deterministic
  validation and materialization remain the only admission path

#### Scenario: Repair cannot convert feedback into new evidence or routing authority
- **WHEN** the existing Wave2 repair receives an invalid initial draft
- **THEN** it uses only the same accepted-evidence assignment, bounded draft, and compact category
  with no tools, and invalid repair publishes neither a synthesis artifact nor searchable-gap
  projection or route

### Requirement: Wave2 synthesis uses only accepted evidence in its selected Run Bundle

Wave2 SHALL obtain accepted evidence, synthesis State, gaps, and materialized content
only through the selected runtime-bound Run Bundle interfaces. It SHALL not derive a
research identity, use an external checkpoint/session as a content source, or write
synthesis artifacts outside that Bundle. Bundle loss SHALL prevent further synthesis
materialization for that Run. (`WSN-007`)

#### Scenario: Synthesis cannot materialize into a replacement root
- **WHEN** the selected Bundle becomes unavailable after a synthesis candidate is produced
- **THEN** Wave2 does not publish that candidate to a new directory or external lifecycle store

### Requirement: Synthesis disposes projected Wave1 questions with deterministic coverage

When the gate-owned `wave1_open_questions` projection is non-empty, the real
synthesis node SHALL resolve each projected question's text from the accepted Wave1
result documents through a bounded store read of that same accepted evidence, SHALL
include the resolved id-and-text assignment in its trusted prompt context, and the
deterministic materializer SHALL admit a synthesis result only when every projected
question id is disposed exactly once: referenced by exactly one gap record with
`search_required=true` through the bounded `source_questions` refs, or listed in the
bounded `resolved_questions` collection. A question id SHALL NOT appear in both
collections or in two gaps, and no `q:w1_` id absent from the projection SHALL be
admitted. A projected id whose text cannot be resolved from the accepted Wave1
result documents SHALL fail deterministically with the same typed coverage error and
SHALL NOT be fabricated, summarized, or rephrased from any other source.

The resolution read SHALL treat the projected question ids as globally unique across
all accepted Wave1 result documents: when two accepted documents project the same
`q:w1_` id with different question texts (a repair-rerun collision), the read SHALL
fail deterministically with a typed `wave1_open_question_id_collision` error that
reaches the same pre-model bounded-exhausted route instead of silently discarding
either text; the same id resolved to byte-identical text in two documents SHALL
deduplicate silently as harmless idempotence. Question ids SHALL NOT be renamed or
namespaced by the projection, because gap `source_questions` reference the
model-minted ids and renaming would break the coverage contract.

Gap records SHALL carry `source_questions` as a sorted, unique, bounded tuple of
`q:w1_` ids (at most 16 per gap), and the synthesis result SHALL carry
`resolved_questions` as a sorted, unique, bounded tuple of `q:w1_` ids (at most 64).
Both fields SHALL default to the empty tuple so artifacts written before this change
remain valid, and neither field SHALL be readable as a route, gate verdict, or
lifecycle fact.

A coverage failure SHALL raise a typed deterministic error, enter the existing
one-shot structured synthesis repair with a closed validation category, and on
repair failure reach the existing exhausted terminal through the existing failure
owner. When the projection is empty or absent, synthesis behavior SHALL be
unchanged, and the existing `wave2_searchable_gaps` gate rule SHALL remain the sole
route authority for gap work.

#### Scenario: Every projected question becomes one searchable gap
- **WHEN** synthesis references each projected question from exactly one `search_required=true` gap
- **THEN** the materializer admits the result and the existing Wave2 gate preview routes those gap ids to `evidence_needed` through the unchanged `unresolved_gaps` projection

#### Scenario: Question text is resolved from accepted evidence only
- **WHEN** the node builds the synthesis assignment from a non-empty `wave1_open_questions` projection
- **THEN** each projected id's text comes verbatim from the accepted Wave1 result documents, and a projected id absent from those documents fails deterministically without any fabricated or summarized text

#### Scenario: A cross-document id collision fails typed instead of dropping text
- **WHEN** two accepted Wave1 result documents carry the same `q:w1_` id with
  different question texts
- **THEN** the resolution read raises the typed `wave1_open_question_id_collision`
  error, the node terminates through the pre-model bounded-exhausted route with
  that concrete category in its pattern-safe projected form
  (`input.wave1_open_question_id_collision`), and neither question text is
  silently discarded

#### Scenario: An identical duplicate id deduplicates silently
- **WHEN** two accepted Wave1 result documents carry the same `q:w1_` id with
  byte-identical question text
- **THEN** the resolution read returns one entry for the id and synthesis proceeds
  unchanged

#### Scenario: An explicitly resolved question creates no gap
- **WHEN** synthesis lists a projected question in `resolved_questions` and no gap references it
- **THEN** the materializer admits the result without a searchable gap for that question, and the gate may pass when no other searchable gaps remain

#### Scenario: Incomplete or conflicting coverage is rejected
- **WHEN** a projected question id is missing from both collections, appears in both, appears in two gaps, or a foreign `q:w1_` id appears
- **THEN** the materializer raises a typed deterministic coverage error before persistence

#### Scenario: Coverage failure is bounded by one repair then the exhausted terminal
- **WHEN** a coverage error occurs and the existing structured repair also fails coverage
- **THEN** the node reaches the existing exhausted terminal without publishing a partial synthesis result

#### Scenario: An empty projection keeps synthesis unchanged
- **WHEN** the checkpointed `wave1_open_questions` projection is empty or absent
- **THEN** the prompt receives no question assignment, the coverage validator is a no-op, and existing synthesis behavior is unchanged

#### Scenario: Old synthesis artifacts remain valid
- **WHEN** a persisted synthesis artifact omits `source_questions` and `resolved_questions`
- **THEN** validation treats both as empty tuples and rejects nothing written before this change

### Requirement: Wave2 repair carries the full open-question disposition contract and concrete coverage findings

When an initial Wave2 candidate fails deterministic semantic validation, the one-shot
structured repair request SHALL receive the full trusted open-question
id-and-text assignment the initial request received, plus a trusted monotone
encoding of the failing coverage detail — the projected question ids missing from
both `gap[].source_questions` and `resolved_questions`, duplicated, or foreign —
naming the concrete failing projection. The repair SHALL NOT receive raw
exceptions, retrieve or add evidence, or receive artifact, checkpoint, gate, route,
or retry authority; a repaired candidate SHALL be rechecked through the existing
deterministic validator before any artifact, preview, or route exists. (`WSN-010`)

#### Scenario: A coverage-class repair receives the complete question contract
- **WHEN** an initial Wave2 candidate fails with `synthesis_question_coverage_invalid`
- **THEN** the repair request receives the full trusted open-question id-and-text
  assignment plus the concrete missing/duplicated/foreign question ids as trusted
  verification detail, and revalidation uses the unchanged deterministic validator

#### Scenario: The repair cannot widen its input authority
- **WHEN** a coverage-class repair receives the question contract and verification detail
- **THEN** the repair remains zero-tool and its candidate is admitted only by the
  existing parser/semantic validator before materialization or any gate preview

#### Scenario: A non-coverage semantic failure still carries its concrete detail
- **WHEN** an initial Wave2 candidate fails a non-coverage semantic check (for
  example a backing-ref or findings requirement)
- **THEN** the repair receives the concrete failing check as trusted validation
  detail alongside the bounded draft and assigned accepted evidence

### Requirement: Wave2 output contract distinguishes synthesis shape from Wave1 claim verdicts

The Wave2 initial synthesis request SHALL present its trusted output contract with a
concrete minimal example object of the required findings/relations/gaps shape and an
explicit negative contrast stating that the candidate SHALL be return
findings/relations/gaps, NOT a Wave1 claim-verdict list (`claims[]` with
`claim_id`/`verdict`/`support_refs`/`counter_refs`/`reason`). The same concrete
output contract SHALL be carried by the structured repair request. The parser and
semantic validator SHALL remain the only admission owners; a candidate in the
Wave1 claim-verdict shape SHALL fail deterministic validation exactly as today.
(`WSN-011`)

#### Scenario: The initial prompt shows a concrete synthesis example
- **WHEN** the initial Wave2 request is rendered with a non-empty output contract
- **THEN** the expected-output contract includes at least one concrete minimal
  findings/relations/gaps example object and an explicit "not a claims verdict list"
  contrast

#### Scenario: The repair prompt shows the same concrete example
- **WHEN** a Wave2 repair request is rendered
- **THEN** the expected-output contract includes the same concrete
  findings/relations/gaps example object and negative contrast as the initial request

#### Scenario: A claim-verdict-shaped candidate still fails deterministically
- **WHEN** a candidate carries a `claims[]` Wave1-verdict shape absent from the
  synthesis contract
- **THEN** deterministic validation rejects it exactly as today and the existing
  repair path handles it
