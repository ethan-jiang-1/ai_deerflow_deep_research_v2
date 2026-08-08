# final-delivery-node Specification

> req: FID-001, FID-002, FID-003, FID-004, FID-005

## Purpose
Produce bounded final report artifacts, verify their evidence integrity, and complete the lifecycle idempotently.

## Requirements
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

#### Scenario: Admitted composer candidate is published
- **WHEN** the composer returns complete valid plan-entry orders
- **THEN** the deterministic final-delivery boundary publishes its two final artifacts
  without granting the composer publication or lifecycle authority

#### Scenario: Composer request is bounded
- **WHEN** real final delivery prepares a composition request
- **THEN** it includes only the approved plan projection and accepted evidence support
  and does not expose arbitrary checkpoint or sandbox content

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
their exact hashes, and validates their fixed artifact shapes. A missing, malformed,
unsupported, or failed composer candidate SHALL produce no final publication and SHALL
enter only the existing bounded self-repair path. Missing final artifacts SHALL route
only to `repair`; missing accepted evidence SHALL route only to `evidence_blocked` and
SHALL not call the immutable publisher. The composer SHALL not invent support, select a
route, or bypass the gate. (`FID-002`)

#### Scenario: Invalid candidate cannot publish an artifact
- **WHEN** candidate parsing, bounds validation, or composer execution fails
- **THEN** no report artifact is published and the existing repair owner determines the
  legal next action

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

### Requirement: Report bounded by report plan

Every admitted report conclusion and claim-citation-map entry SHALL be traceable to
the readiness-admitted writable-conclusion projection and its accepted backing
submission references. The deterministic renderer SHALL include every writable
conclusion's exact `conclusion_text`, every mandatory uncertainty's exact `limitation`,
and only the backing submission references carried in its corresponding
`backing_claim_ids`; the composer may only order their deterministically derived entry
identities. Mandatory uncertainties SHALL be preserved as uncertainties and SHALL NOT
be presented as conclusions. The composer SHALL not add, paraphrase, omit, or
strengthen a claim, or cite a reference outside its approved projection. (`FID-003`)

#### Scenario: Mandatory uncertainty remains visible
- **WHEN** the admitted readiness plan contains a mandatory uncertainty
- **THEN** the published report preserves it without promoting it to a conclusion

#### Scenario: Unsupported claim is rejected
- **WHEN** a candidate omits, duplicates, or names an unapproved plan entry
- **THEN** deterministic admission rejects it before publication

#### Scenario: Approved text and citation binding are rendered verbatim
- **WHEN** a complete layout candidate is admitted
- **THEN** the renderer, rather than the composer, copies each approved conclusion and
  limitation text and its approved backing submission references into the two artifacts

### Requirement: Completion follows final gate pass

The real final-delivery node SHALL not write a completed terminal fact before final
gate evaluation. Only the final gate's verified `pass` outcome SHALL write
`terminal_status=COMPLETED`, `phase_status=TERMINAL`, and the completed terminal reason.
Its `repair` and `evidence_blocked` outcomes SHALL remain non-terminal; its exhausted
outcome SHALL retain the existing blocked terminal disposition. (`FID-004`)

#### Scenario: Repair cannot retain optimistic completion
- **WHEN** a current final-delivery visit has no admissible fresh artifact pair
- **THEN** it routes to repair without a completed terminal fact, even if a prior visit
  left report references in the checkpoint

#### Scenario: Gate pass completes the lifecycle
- **WHEN** the real final gate verifies the current visit's paired artifacts and
  accepted evidence
- **THEN** the gate, rather than the composer or final node, records completion

### Requirement: Mixed-graph integration

Real final delivery SHALL require real readiness, its declared narrow
`final_delivery_bundle` read capability, and the publication bundle. The final-delivery
bundle SHALL expose only bounded report-plan/evidence reads and final-artifact
verification, not work-unit control or mutation. It SHALL read an immutable readiness
plan only when its canonical content reference is contained and hash-matched; an absent,
unreadable, or divergent plan SHALL invoke no composer or publisher. Missing declared
dependencies SHALL fail before request construction or model invocation. The runtime
dependency resolver SHALL select a final-delivery-specific zero-tool bridge/policy
rather than reuse an upstream node's bridge. Full-fake behavior and graph topology SHALL
remain unchanged. (`FID-005`)

#### Scenario: Real final_delivery requires real readiness
- **WHEN** final_delivery=real without readiness=real
- **THEN** recipe construction fails

#### Scenario: Missing declared dependency fails before model invocation
- **WHEN** real final delivery is built or graph-invoked without its declared narrow
  reader or publisher dependency
- **THEN** it fails before a composer request, model call, candidate, or artifact is created

#### Scenario: Plan read failure blocks composition before publication
- **WHEN** the readiness plan reference is missing, unreadable, outside its contained
  store path, or does not match its content hash
- **THEN** final delivery invokes neither composer nor publisher and the deterministic
  final gate receives a fresh no-publication view and owns the legal bounded outcome

#### Scenario: Final delivery receives its own bridge policy
- **WHEN** a runnable real-final-delivery recipe resolves final-delivery dependencies
- **THEN** the resolved bridge has the final-delivery-specific zero-tool policy and is
  not a readiness or upstream bridge

#### Scenario: Final delivery cannot gain work-unit control through its reader
- **WHEN** a real final-delivery factory receives its declared bundle capability
- **THEN** its protocol supports only the bounded final plan/evidence/artifact reads and
  cannot allocate work, mutate a submission ledger, or dispatch a worker
