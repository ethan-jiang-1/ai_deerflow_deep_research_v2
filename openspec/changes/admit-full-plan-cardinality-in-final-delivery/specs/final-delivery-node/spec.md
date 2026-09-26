# Spec Delta

## MODIFIED Requirements

### Requirement: Writer produces report and claim-citation map

The real final-delivery node SHALL invoke one bounded zero-tool report composer per
non-degenerate visit. Trusted code SHALL derive its read-only request solely from
the admitted readiness report plan and accepted evidence projection. The composer SHALL
return one closed typed layout candidate containing only complete, duplicate-free orders
of deterministically derived writable-conclusion and mandatory-uncertainty entry
identities; it SHALL receive no raw checkpoint, writable path, tool, publication
handle, route instruction, or lifecycle authority. The deterministic parser SHALL
first normalize the delivered text — accepting the JSON object delivered bare, inside
a fenced code block, or embedded in surrounding prose — and SHALL then admit, through
the existing deterministic evaluator, only complete permutations. A deterministic
renderer SHALL produce `report.md` and `claim-citation-map.json` from the exact
admitted plan text and backing submission references before the publisher writes
either artifact. Fixture final delivery SHALL remain fixture-controlled.
(`FID-001`)

The layout candidate's order fields SHALL admit every entry identity of the admitted
plan: no fixed cardinality bound below the plan contract's own bounds SHALL reject a
complete plan-order or composer-delivered permutation, and the deterministic
plan-order layout SHALL construct for an admitted plan of any legal cardinality. A
delivery that parses as a well-formed JSON object but fails the typed layout
validation SHALL carry the closed concrete category `final_layout_schema_invalid`
with a bounded structured detail rather than collapsing into the generic layout
shape code, so the recorded validation fact and any repair feedback name the failing
field.

For a degenerate plan — at most one writable conclusion and at most one mandatory
uncertainty — the complete legal layout is mathematically unique, and the node SHALL
construct the layout candidate deterministically without invoking the composer: the
candidate carries the derived entry identities in plan order, then passes through the
same parser/evaluator admission, renderer, and publisher path as a composer-produced
candidate. The composer model call SHALL remain the path for every non-degenerate
plan; degenerate rendering SHALL NOT add, reorder beyond the unique order, or
paraphrase plan content, and a degenerate-plan visit SHALL NOT fail for a model echo
mismatch because no model echo is requested.

For a non-degenerate visit whose composer does not yield an admitted layout candidate
— because the invocation failed or because the delivered text, after normalization,
still fails parsing or admission — the node SHALL degrade that visit to the
deterministic plan-order layout candidate: the derived entry identities in plan order,
passing through the same parser/evaluator admission, renderer, and publisher path as a
composer-produced candidate. A layout degradation SHALL NOT itself produce a work
failure, consume a repair round, or prevent publication, and SHALL leave the rendered
artifact content exactly as the admitted plan text and backing references dictate. The
composer's ordering contribution is advisory: no visit SHALL fail, block, or lose its
delivery solely because the composer's ordering was unavailable or inadmissible. A
failure of rendering, publication, or artifact read-back SHALL leave one bounded
closed-code validation fact in the journal before the visit's work-failure
disposition, so a terminal delivery block never depends on offline reproduction to
name its cause.

#### Scenario: Admitted composer candidate is published
- **WHEN** the composer returns complete valid plan-entry orders
- **THEN** the deterministic final-delivery boundary publishes its two final artifacts
  without granting the composer publication or lifecycle authority

#### Scenario: A fenced or prose-embedded candidate is normalized and admitted
- **WHEN** the composer delivers the closed layout JSON inside a code fence or
  embedded in surrounding prose
- **THEN** the deterministic parser normalizes the delivery, admits the complete
  permutation, and the visit publishes without a repair round

#### Scenario: An inadmissible candidate degrades to the plan-order layout
- **WHEN** a non-degenerate visit's composer candidate fails parsing or admission
  after normalization
- **THEN** the node constructs the plan-order layout candidate, publishes through the
  same admission, rendering, and publication path, and records the canonical
  validation fact of the rejected delivery

#### Scenario: A failed composer invocation degrades to the plan-order layout
- **WHEN** a non-degenerate visit's composer invocation fails
- **THEN** the node still publishes via the plan-order layout candidate in the same
  visit, and the invocation failure remains the existing invocation fact

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

#### Scenario: A degenerate plan renders without a model call
- **WHEN** the admitted plan has at most one writable conclusion and at most one
  mandatory uncertainty
- **THEN** the node deterministically constructs the unique complete layout candidate,
  no composer request is built or invoked, and the same admission, rendering, and
  publication path publishes the two artifacts

#### Scenario: Full-fake delivery remains fixture-controlled
- **WHEN** the fixture graph reaches final delivery
- **THEN** it does not invoke the composer and retains its declared fixture outcome

#### Scenario: A full-cardinality plan delivers end to end
- **WHEN** the admitted plan carries more mandatory-uncertainty or writable-conclusion
  entries than any fixed small bound (for example nine uncertainties and seven
  conclusions)
- **THEN** the layout candidate contracts admit the complete plan-order and
  composer-delivered orders, the deterministic plan-order layout constructs without
  error, and the visit publishes its two artifacts instead of blocking

#### Scenario: Schema-invalid delivery keeps a concrete category
- **WHEN** the composer delivers a well-formed JSON object that fails the typed layout
  validation (for example a missing or wrongly typed order field)
- **THEN** the recorded validation fact and repair feedback carry the closed
  `final_layout_schema_invalid` category with a bounded detail naming the failing
  field, not the collapsed generic layout shape code

#### Scenario: A read-back failure leaves a closed-code fact
- **WHEN** rendering, publication, or artifact read-back raises before the visit's
  artifacts are admitted
- **THEN** the journal records one bounded closed-code validation fact for that
  failure before the visit takes its work-failure disposition
