# final-delivery-node Delta

> req: FID-001, FID-002

## MODIFIED Requirements

### Requirement: Writer produces report and claim-citation map

The real final-delivery node SHALL invoke one bounded zero-tool report composer per
non-degenerate visit. Trusted code SHALL derive its read-only request solely from the
admitted readiness report plan and accepted evidence projection. The composer SHALL
return one closed typed layout candidate containing only complete, duplicate-free orders
of deterministically derived writable-conclusion and mandatory-uncertainty entry
identities; it SHALL receive no raw checkpoint, writable path, tool, publication
handle, route instruction, or lifecycle authority. The deterministic parser SHALL
first normalize the delivered text — accepting the JSON object delivered bare, inside
a fenced code block, or embedded in surrounding prose — and SHALL then admit, through
the existing deterministic evaluator, only complete permutations. A deterministic
renderer SHALL produce `report.md` and `claim-citation-map.json` from the exact
admitted plan text and backing submission references before the publisher writes
either artifact. Full-fake final delivery SHALL remain fixture-controlled.
(`FID-001`)

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
delivery solely because the composer's ordering was unavailable or inadmissible.

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
- **WHEN** the full-fake graph reaches final delivery
- **THEN** it does not invoke the composer and retains its declared fixture outcome

### Requirement: Integrity gate verifies report and evidence

The real final integrity gate SHALL deterministically verify the fresh current-visit
published report and claim-citation-map content references plus accepted-evidence
presence before accepting completion. Its typed final-attempt gate view SHALL be
validated against the node's current proposed result, so prior checkpointed
`report_refs` cannot satisfy a failed current visit. A published view SHALL exist only
after the declared reader re-reads both publisher-returned contained paths, verifies
their exact hashes, and validates their fixed artifact shapes.

A structural failure — an unreadable or divergent readiness plan, an accepted-evidence
read failure, a rendering failure, a publication failure, or a failed post-publication
re-read/hash/shape verification — SHALL produce no final publication and SHALL enter
only the existing bounded self-repair path; a visit that exhausted that repair budget
SHALL retain the existing blocked terminal disposition. A composer layout failure —
invocation, parse, or admission — SHALL NOT produce a work-failure view when the
plan-order degradation publishes and verifies in the same visit. Missing accepted
evidence SHALL route only to `evidence_blocked` and SHALL not call the immutable
publisher. The composer SHALL not invent support, select a route, or bypass the gate.
(`FID-002`)

#### Scenario: An inadmissible candidate publishes via degradation without a repair round
- **WHEN** a non-degenerate visit's composer delivery fails parsing or admission after
  normalization and the plan-order layout publishes and verifies
- **THEN** the fresh gate view carries the verified artifact pair, no repair round is
  consumed, and the run can complete through the final gate

#### Scenario: Invalid candidate cannot publish an artifact
- **WHEN** a composer delivery fails parsing or admission after normalization
- **THEN** that candidate itself publishes nothing; only the separately admitted
  plan-order degradation candidate reaches the renderer and publisher, and the
  rejected delivery's canonical validation fact is retained

#### Scenario: A structural failure cannot publish an artifact
- **WHEN** plan or evidence reading, rendering, publication, or post-publication
  verification fails
- **THEN** no report artifact is published for that attempt and the existing repair
  owner determines the legal next action

#### Scenario: Missing evidence remains a gate outcome
- **WHEN** a fresh final-attempt view has no accepted evidence
- **THEN** the integrity gate routes to `evidence_blocked` rather than asking the
  composer to fabricate citation support

#### Scenario: Fixture disposition cannot replace final verification
- **WHEN** real final delivery reaches its gate with missing report artifacts or
  accepted evidence
- **THEN** deterministic artifact/evidence checks select `repair` or
  `evidence_blocked` without relying on a fixture route sequence

#### Scenario: Publication is re-read before a pass view exists
- **WHEN** the publisher returns the two final content references
- **THEN** the declared reader re-reads and hash-checks both contained artifacts and a
  malformed, missing, or divergent result reaches only the fresh `repair` view
