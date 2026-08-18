## MODIFIED Requirements

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
