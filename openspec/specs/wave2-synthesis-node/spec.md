# wave2-synthesis-node Specification

> req: WSN-001, WSN-002, WSN-003, WSN-004, WSN-005, WSN-006, WSN-007, WSN-008, WSN-009
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
with a typed `output.structured_invalid` incident; it SHALL NOT escape as an
uncaught exception. The wave2 gate budget SHALL resolve from the HITL-owned
profile intent fields in graph state: the minimal pair (`cost_tolerance=minimal`
and `time_budget=very_quick`) yields two evidence rounds, otherwise the default
one round stands. (`WSN-001`, `WSN-009`)

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
  `output.structured_invalid` incident and publishes no synthesis artifact

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

#### Scenario: A Wave2 provider failure blocks with its known cause
- **WHEN** the Wave2 synthesis invocation returns a known non-retryable provider
  failure and no legal gate repair applies
- **THEN** the lifecycle retains that category and `wave2_synthesis` phase in the
  terminal incident instead of surfacing an opaque graph exception

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
