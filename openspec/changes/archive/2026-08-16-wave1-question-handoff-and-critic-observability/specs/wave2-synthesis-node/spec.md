> req: WSN-009

## Purpose

Give Wave1's `targeted_search` open questions a deterministic, traceable disposition
in synthesis: every projected question either becomes exactly one searchable gap that
the existing Wave2 gate routes to targeted evidence, or is explicitly resolved, with
a bounded repair and terminal path for incomplete coverage.

## ADDED Requirements

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
