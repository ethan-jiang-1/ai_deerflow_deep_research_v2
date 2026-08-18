> req: WSN-001, WSN-010, WSN-011

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
SHALL NOT escape as an uncaught exception. The wave2 gate budget SHALL resolve from
the HITL-owned profile intent fields in graph state: the minimal pair
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

#### Scenario: The projected category never becomes lifecycle authority
- **WHEN** a terminal incident projects a concrete validation category
- **THEN** the projection does not select a route, grant recovery, or alter the
  lifecycle transition from the exhausted terminal

#### Scenario: Wave2 gate budget resolves from the profile intent
- **WHEN** the graph state carries the minimal profile intent pair and searchable
  gaps persist after one evidence round
- **THEN** the gate permits one more evidence round before exhausting, while runs
  without the minimal pair keep today's single-round behavior

## ADDED Requirements

### Requirement: Wave2 repair carries the full open-question disposition contract and concrete coverage findings

When a Wave2 initial or repaired candidate fails semantic validation, the node SHALL
enter its existing one zero-tool repair with the same open-question disposition
contract as the initial prompt: the full trusted id-and-text assignment of every
projected Wave1 open question, the closed disposition rule (each id referenced by
exactly one `search_required=true` gap `source_questions` or listed in
`resolved_questions`, never both or twice), and a trusted verification-detail item
naming the concrete failing projection — which projected question ids are missing
from both collections, duplicated, or foreign. The repair SHALL NOT receive raw
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