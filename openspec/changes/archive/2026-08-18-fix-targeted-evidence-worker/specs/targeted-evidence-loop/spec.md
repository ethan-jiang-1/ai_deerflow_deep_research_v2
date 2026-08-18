## MODIFIED Requirements

### Requirement: Targeted worker performs focused gap search

A bounded web worker SHALL search for evidence addressing one assigned gap. The
initial request SHALL require and permit exactly one web search tool call, use
its multiple returned candidates as the evidence set, and retain later model
turns for its structured answer. The worker request SHALL carry the assigned
gap's bounded description as search context: the node SHALL join the
gate-projected gap ids against the canonical synthesis artifact's gap records
through the same bounded contained read readiness uses, and the description
(truncated to a bounded byte budget) SHALL appear in the request objective;
a gap id whose body is absent from the artifact SHALL still produce a request
that names the id without fabricating a description. The description is context
only — it SHALL NOT change gap routing, intent materialization, or any
authority derived from the gate's id projection (TEL-001's id-only routing
authority is unchanged). Output SHALL include new source refs and a gap
resolution status, and the worker SHALL NOT modify synthesis findings directly.
Before a candidate may pass the submission boundary, its `source_refs` SHALL be
canonical-ordered by `(source_id, canonical_url)` exactly as the work-unit
submission validator requires; the worker SHALL sort the accepted source set
into that order before building the candidate, so structurally valid targeted
results are admitted instead of failing `source_refs_not_canonical`. If the
first successful agent result cannot be parsed, validated as the targeted
worker schema, or bound to the assigned gap id, the node SHALL make exactly one
separate repair request with tools disabled, the assigned gap identity and
stable validation failure metadata, and the bounded untrusted draft. A valid
repair SHALL proceed through the existing materializer, validator, and ledger
submit boundary. A failed, non-successful, wrong-gap, or schema-invalid repair
SHALL fail closed without result/source artifact or ledger authority.

#### Scenario: Worker finds evidence for a gap
- **WHEN** worker searches for evidence addressing a gap and returns valid structured output
- **THEN** new sources are recorded with backing refs and gap status is updated without a repair call

#### Scenario: Worker output is canonically ordered before submission
- **WHEN** the worker's structured output lists sources in any order and the
  candidate is built for the submission boundary
- **THEN** `source_refs` are sorted by `(source_id, canonical_url)` before
  validation, and a result that would otherwise fail
  `source_refs_not_canonical` is admitted

#### Scenario: Assigned gap description reaches the worker as bounded context
- **WHEN** the current Wave2 gate projects a searchable gap id whose body exists
  in the canonical synthesis artifact
- **THEN** the worker request names the gap id and includes its bounded
  description in the objective, and no other checkpoint field changes routing

#### Scenario: Gap id without a body still searches honestly
- **WHEN** a gate-projected gap id has no description body in the canonical
  synthesis artifact
- **THEN** the worker request still names the id and instructs search without a
  fabricated description

#### Scenario: Prose answer is repaired once without tools
- **WHEN** the initial worker uses its exactly one allowed web search but its successful final answer is prose, schema-invalid, or names a different gap
- **THEN** one zero-tool repair request may convert the bounded draft into a valid response for the same assigned gap

#### Scenario: Invalid repair publishes no authority
- **WHEN** the single repair is non-successful, malformed, schema-invalid, or names a different gap
- **THEN** the work attempt fails without publishing source artifacts, a targeted result artifact, or a submission-ledger record

#### Scenario: Repair cannot perform more research
- **WHEN** the repair request executes
- **THEN** no web or filesystem tool is exposed and no tool call is dispatched
