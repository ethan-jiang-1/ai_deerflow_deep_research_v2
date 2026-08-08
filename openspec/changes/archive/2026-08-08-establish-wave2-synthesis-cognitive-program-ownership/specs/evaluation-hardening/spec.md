> req: EVH-029

## ADDED Requirements

### Requirement: Wave2 cognitive-program evidence is closed, deterministic, and non-live

The evaluation harness SHALL accept one closed `wave2_cognitive_program` case family
for versioned Wave2 initial-synthesis and structured-repair evidence. Its fixture
SHALL contain exactly normal accepted-evidence synthesis, unsupported or
instruction-like evidence containment, honest-gap/uncertainty judgment paired with a
backed finding, malformed initial candidate with one repair, and invalid repaired
candidate non-publication.
Each scenario SHALL bind only the needed Wave2 capability id, closed trusted
assignment/evidence data, bounded untrusted draft or evidence, forbidden effects,
and review criteria.

The case execution plan SHALL bind both Wave2 capability digests and the
`SynthesisResult` schema digest. Every scenario SHALL use fresh production Wave2
node dependencies and the real zero-tool runtime bridge with scripted adapters. The
fixture and adapters SHALL establish only exact-resource, bounded-prompt,
accepted-evidence, repair, and deterministic-admission evidence. They SHALL NOT
claim provider quality, selected-live eligibility, artifact admission, gap routing,
gate outcome, lifecycle, or State authority.

Where a valid scripted candidate passes the real node's existing internal
materializer/preview path, its scenario adapter SHALL use a fresh contained Bundle
dependency and SHALL NOT record that write, preview, or any later gate result as a
corpus proof claim. An invalid repaired candidate MAY establish its required
non-publication fact by observing the absence of that write. This distinction does
not alter the production materializer, preview, gate, or lifecycle owner.

The `wave2_cognitive_program` family SHALL remain absent from selected-live
admission. A selected-live request for it SHALL fail before creating a runs root,
manifest, review, subject, provider invocation, or credentialed-live evidence layer.
(`EVH-029`)

#### Scenario: Closed Wave2 corpus rejects incomplete or over-broad controls
- **WHEN** a Wave2 cognitive-program case omits a required scenario, duplicates a
  capability/runtime-control/rubric identity, or declares a provider, web, targeted
  evidence, readiness, gate, or route dependency
- **THEN** evaluation admission rejects the case before subject construction or any
  model, tool, artifact, preview, gate, review, or live-evidence activity

#### Scenario: Deterministic Wave2 scenarios preserve the cognitive boundary
- **WHEN** the registered Wave2 cognitive-program subject executes every declared
  scenario with scripted accepted evidence and model output
- **THEN** each uses fresh production node dependencies and the real zero-tool bridge,
  and establishes only its declared resource, prompt, grounding, repair, deterministic
  admission, and invalid-candidate non-publication facts; a successful internal write,
  preview, or gate result is not a corpus claim

#### Scenario: Honest uncertainty remains distinct from a gaps-only rejection
- **WHEN** the closed Wave2 corpus supplies accepted evidence to its honest-gap scenario
- **THEN** that candidate contains at least one finding backed by the assigned evidence
  together with the bounded gap, while a gaps-only candidate follows the existing
  repair or invalid-repair path and cannot substitute for the uncertainty scenario

#### Scenario: Wave2 deterministic corpus cannot enter selected live evidence
- **WHEN** a caller selects the Wave2 cognitive-program case through the selected-live
  entrypoint
- **THEN** admission fails before a runs root, manifest, review, provider call, or
  credentialed-live evidence layer is created
