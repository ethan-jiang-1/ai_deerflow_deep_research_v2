## MODIFIED Requirements

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
