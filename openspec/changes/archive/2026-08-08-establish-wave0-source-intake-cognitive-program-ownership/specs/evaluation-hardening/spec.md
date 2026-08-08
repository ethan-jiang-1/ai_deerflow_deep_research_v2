> req: EVH-027

## ADDED Requirements

### Requirement: Wave0 cognitive-program evidence is closed, deterministic, and non-live

The evaluation harness SHALL accept one closed `wave0_cognitive_program` case family
for versioned Wave0 source-intake cognitive evidence. Its fixture SHALL contain exactly
normal bounded retrieval handoff, adversarial retrieved instruction, retrieval
shortfall, malformed initial candidate with one repair, and post-candidate validation
rejection. Every scenario SHALL declare expected Wave0 capability ids, bounded
assignment fragments, forbidden control effects, and rubric criteria. The evaluator
SHALL reject missing or duplicate scenario, capability, runtime-control, or rubric
data, and SHALL bind the two Wave0 capability resources and existing worker schema
sources by project-relative sha256 controls.

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
  duplicate capability, runtime-control, or rubric data
- **THEN** evaluation admission rejects the case before subject construction or any
  model, tool, artifact, ledger, or review activity

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
