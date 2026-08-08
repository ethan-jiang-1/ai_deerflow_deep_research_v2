> req: EVH-028

## ADDED Requirements

### Requirement: Wave1 cognitive-program evidence is closed, deterministic, and non-live

The evaluation harness SHALL accept one closed `wave1_cognitive_program` case family
for versioned Wave1 extraction/repair cognitive evidence. Its fixture SHALL contain
exactly normal bounded retrieval handoff, adversarial retrieved instruction, accepted
Wave0-baseline duplicate containment, malformed initial candidate with one parser
repair, local-semantic candidate rejection with one repair, and post-candidate
submission-validation rejection. Each scenario SHALL bind only the Wave1 extraction or
repair capability ids needed by its branch, closed trusted assignment/baseline data,
bounded untrusted observations or draft, forbidden effects, and review criteria.

The case execution plan SHALL bind the two capability digests and Wave1 worker-schema
digest. Every scenario SHALL invoke fresh production Wave1 node/controller dependencies
and the real runtime bridge with scripted external adapters. The fixture and adapter
SHALL establish only declared deterministic handoff, method, tool-posture, and
authority-boundary evidence. They SHALL NOT claim source quality, provider behavior,
selected-live eligibility, release status, source/claim admission, critic outcome,
controller retry, gate, route, or State authority.

The `wave1_cognitive_program` case SHALL remain absent from selected-live admission.
A selected-live request for it SHALL fail before creating a runs root, manifest, review,
subject, provider invocation, or credentialed-live evidence layer.

#### Scenario: Closed Wave1 corpus rejects incomplete or over-broad controls
- **WHEN** a Wave1 cognitive-program case omits a required scenario, duplicates a
  capability/runtime-control/rubric identity, or declares a SourceDiagnostic,
  ClaimVerifier, provider, or web dependency
- **THEN** evaluation admission rejects the case before subject construction or any
  model, tool, artifact, ledger, review, or live-evidence activity

#### Scenario: Deterministic Wave1 scenarios preserve the extraction boundary
- **WHEN** the registered Wave1 cognitive-program subject executes every declared
  scenario with scripted external observations
- **THEN** each uses fresh production node/controller dependencies and the real runtime
  bridge with scripted adapters, and establishes only its declared exact-resource,
  bounded-prompt, baseline/repair, and post-validation-isolation facts

#### Scenario: Wave1 deterministic corpus cannot enter selected live evidence
- **WHEN** a caller selects the Wave1 cognitive-program case through the selected-live
  entrypoint
- **THEN** admission fails before a runs root, manifest, review, provider call, or
  credentialed-live evidence layer is created
