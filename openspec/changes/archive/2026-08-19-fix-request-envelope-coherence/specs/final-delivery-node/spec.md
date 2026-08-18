## MODIFIED Requirements

### Requirement: Writer produces report and claim-citation map

The real final-delivery node SHALL invoke one bounded zero-tool report composer per
visit. Trusted code SHALL derive its read-only request solely from the admitted
readiness report plan and accepted evidence projection. The composer SHALL return one
closed typed layout candidate containing only complete, duplicate-free orders of
deterministically derived writable-conclusion and mandatory-uncertainty entry
identities; it SHALL receive no raw checkpoint, writable path, tool, publication
handle, route instruction, or lifecycle authority. A deterministic parser/evaluator
SHALL admit only those complete permutations, then a deterministic renderer SHALL
produce `report.md` and `claim-citation-map.json` from the exact admitted plan text and
backing submission references before the publisher writes either artifact. Full-fake
final delivery SHALL remain fixture-controlled. (`FID-001`)

The composer node policy's admission envelope SHALL be coherent with the request
builder's declared maximum input: the builder's full evidence projection budget
(`MAX_FINAL_DELIVERY_EVIDENCE_BYTES`) plus the report-plan projection plus request
scaffolding, the trusted system prompt, and the per-call output token cap SHALL
together stay within the policy's `total_token_budget`, so a builder-maximal request is
admissible before the network and is never refused as `token_admission` by
construction. This coherence SHALL be locked by a deterministic regression test that
builds a builder-maximal request and asserts the envelope inequality against the
assembled policy.

#### Scenario: Admitted composer candidate is published
- **WHEN** the composer returns complete valid plan-entry orders
- **THEN** the deterministic final-delivery boundary publishes its two final artifacts
  without granting the composer publication or lifecycle authority

#### Scenario: Composer request is bounded
- **WHEN** real final delivery prepares a composition request
- **THEN** it includes only the approved plan projection and accepted evidence support
  and does not expose arbitrary checkpoint or sandbox content

#### Scenario: Builder-maximal projection stays admissible
- **WHEN** the composer request is built with evidence filling the builder's full
  evidence-projection budget alongside an admitted plan projection and the assembled
  node policy is inspected
- **THEN** the projected request bytes plus the trusted system prompt plus the
  per-call output cap do not exceed the policy's total token budget, so the call
  reaches the provider instead of being refused by admission control

#### Scenario: Full-fake delivery remains fixture-controlled
- **WHEN** the full-fake graph reaches final delivery
- **THEN** it does not invoke the composer and retains its declared fixture outcome
