## MODIFIED Requirements

### Requirement: Wave0 cognitive-program evidence is closed, deterministic, and non-live

The evaluation harness SHALL accept one closed `wave0_cognitive_program` case family
for versioned Wave0 source-intake cognitive evidence. Its fixture SHALL contain exactly
normal bounded retrieval handoff, adversarial retrieved instruction, retrieval
shortfall, malformed initial candidate with one repair, and post-candidate validation
rejection. Every scenario SHALL declare expected Wave0 capability ids, bounded
assignment fragments, forbidden control effects, and a non-empty unique set of
criterion IDs. Those IDs are Case-control-integrity metadata: deterministic registry
admission validates the selected Rubric's declared identity/version and the scenarios'
unique criterion-ID set before subject construction. They SHALL NOT carry criterion
prose, weights, thresholds, evaluator guidance, or a quality disposition into the Wave0
execution subject or model-facing input. The evaluator SHALL reject missing or duplicate scenario, capability,
runtime-control, or criterion-ID metadata, and SHALL bind the two Wave0 capability
resources and existing worker schema sources by project-relative sha256 controls.

The registered deterministic subject SHALL construct each declared scenario through
the production Wave0 node/controller boundary with fresh scenario-local dependencies,
the real runtime bridge, and scripted external model/tool adapters. It SHALL establish
only exact resource loading, runtime tool/candidate handoff, pre-candidate repair
placement, and deterministic source-admission non-bypassability. The family SHALL not be admitted to
the selected-live entrypoint. A selected-live request for it SHALL fail before creating
a run, manifest, review, provider call, or credentialed-live quality layer; neither
the deterministic family nor its review is a source-quality, release, lifecycle, or
route claim.

#### Scenario: Closed Wave0 corpus rejects incomplete controls
- **WHEN** a Wave0 cognitive-program case omits a required scenario or contains
  duplicate capability, runtime-control, or criterion-ID metadata
- **THEN** evaluation admission rejects the case before subject construction or any
  model, tool, artifact, ledger, or review activity

#### Scenario: Wave0 criterion IDs cannot become quality input
- **WHEN** a Wave0 case is admitted after its criterion IDs match the selected Rubric control
- **THEN** any retained criterion IDs are non-model control metadata and are not
  interpreted as scoring, quality instruction, or a verdict; the subject receives no
  criterion prose, weights, thresholds, evaluator guidance, or quality disposition
  from that Rubric

#### Scenario: Deterministic scenarios retain Wave0 admission boundaries
- **WHEN** the registered Wave0 cognitive-program subject executes every declared
  scenario with scripted external observations
- **THEN** each uses fresh production node/controller dependencies and the real runtime
  bridge with scripted external adapters, and establishes only its declared resource,
  tool/candidate, repair, or validation-isolation handoff without fabricated accepted
  coverage, source truth, retry, gate, route, or State authority

#### Scenario: Deterministic corpus cannot enter selected live evidence
- **WHEN** a caller selects the Wave0 cognitive-program case through the selected-live
  entrypoint
- **THEN** admission fails before a runs root, manifest, review, provider call, or
  credentialed-live evidence layer is created

### Requirement: Wave1 cognitive-program evidence is closed, deterministic, and non-live

The evaluation harness SHALL accept one closed `wave1_cognitive_program` case family
for versioned Wave1 extraction/repair cognitive evidence. Its fixture SHALL contain
exactly normal bounded retrieval handoff, adversarial retrieved instruction, accepted
Wave0-baseline duplicate containment, malformed initial candidate with one parser
repair, local-semantic candidate rejection with one repair, and post-candidate
submission-validation rejection. Each scenario SHALL bind only the Wave1 extraction or
repair capability ids needed by its branch, closed trusted assignment/baseline data,
bounded untrusted observations or draft, forbidden effects, and a non-empty unique set
of criterion IDs. Those IDs are Case-control-integrity metadata: deterministic registry
admission validates the selected Rubric's declared identity/version and the scenarios'
unique criterion-ID set before subject construction. They SHALL NOT carry criterion
prose, weights, thresholds, evaluator guidance, or a quality disposition into the
Wave1 execution subject or model-facing input.

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
  capability/runtime-control/criterion-ID identity, or declares a SourceDiagnostic,
  ClaimVerifier, provider, or web dependency
- **THEN** evaluation admission rejects the case before subject construction or any
  model, tool, artifact, ledger, review, or live-evidence activity

#### Scenario: Wave1 criterion IDs cannot become quality input
- **WHEN** a Wave1 case is admitted after its criterion IDs match the selected Rubric control
- **THEN** any retained criterion IDs are non-model control metadata and are not
  interpreted as scoring, quality instruction, or a verdict; the subject receives no
  criterion prose, weights, thresholds, evaluator guidance, or quality disposition
  from that Rubric

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

### Requirement: Wave2 cognitive-program evidence is closed, deterministic, and non-live

The evaluation harness SHALL accept one closed `wave2_cognitive_program` case family
for versioned Wave2 initial-synthesis and structured-repair evidence. Its fixture
SHALL contain exactly normal accepted-evidence synthesis, unsupported or
instruction-like evidence containment, honest-gap/uncertainty judgment paired with a
backed finding, malformed initial candidate with one repair, and invalid repaired
candidate non-publication. Each scenario SHALL bind only the needed Wave2 capability
id, closed trusted assignment/evidence data, bounded untrusted draft or evidence,
forbidden effects, and a non-empty unique set of criterion IDs. Those IDs are
Case-control-integrity metadata: deterministic registry admission validates the
selected Rubric's declared identity/version and the scenarios' unique criterion-ID set
before subject construction. They SHALL NOT carry criterion prose, weights, thresholds,
evaluator guidance, or a quality disposition into the Wave2 execution subject or
model-facing input.

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
  capability/runtime-control/criterion-ID identity, or declares a provider, web, targeted
  evidence, readiness, gate, or route dependency
- **THEN** evaluation admission rejects the case before subject construction or any
  model, tool, artifact, preview, gate, review, or live-evidence activity

#### Scenario: Wave2 criterion IDs cannot become quality input
- **WHEN** a Wave2 case is admitted after its criterion IDs match the selected Rubric control
- **THEN** any retained criterion IDs are non-model control metadata and are not
  interpreted as scoring, quality instruction, or a verdict; the subject receives no
  criterion prose, weights, thresholds, evaluator guidance, or quality disposition
  from that Rubric

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
