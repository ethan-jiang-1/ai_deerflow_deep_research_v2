> req: EVH-019

## ADDED Requirements

### Requirement: Evidence-intake calibration has branch-specific judgment evidence

Test-owned evidence SHALL define a dedicated labeled calibration corpus with exactly
one normal and one highest-risk case for each existing evidence-intake branch: Wave0
source intake, Wave0 source-intake repair, Wave1 evidence extraction, Wave1
evidence-extraction repair, Wave1 SourceDiagnostic, and Wave1 ClaimVerifier (twelve
cases total). It SHALL be separate from the existing intake-and-planning calibration
corpus, canonical `LIVE_CANARIES`, and the lane-neutral `ScenarioCase` registry.
Each case SHALL declare a stable case and branch identity, bounded trusted assignment,
untrusted input boundary when present, expected candidate constraints, criterion
identifiers and quality rubric, permitted degradation, nondeterministic boundary, and
outer attempt, model-call, tool-call, token, and timeout bounds no wider than its
existing branch request and declared live-runner policy. Rubrics SHALL evaluate only
whether a candidate is assignment-faithful, conservative about source/evidence
uncertainty, provenance- or identity-bound where applicable, and decision-ready for
its deterministic owner. They SHALL not assert source truth, research quality,
evidence acceptance, artifact publication, gate correctness, route correctness, or a
model judgment from a deterministic fixture.

For selected live execution, the generated request's declared tool posture and
resource bounds, a successful real bridge invocation, and parsing through the
production branch parser SHALL be hard invariants. Wave1 worker and repair cases
SHALL additionally apply their existing local pre-persistence semantic validator
before rubric evaluation. A hard-invariant or execution failure SHALL remain the
existing live-run failure and SHALL not receive a rubric disposition. Critic cases
SHALL use only a deterministic test-owned fixture of the prompt's accepted-assignment
projection; that fixture SHALL not claim a `SubmissionRecord`, review artifact,
accepted evidence, or full-pipeline execution.

Each branch SHALL retain separate lowest-seam deterministic proof of request
composition, runtime-enforced tool posture, repair or review boundary, and
non-admission. Repair-branch proof SHALL exercise only the existing pre-persistence
repair seam: Wave0 parser/typed-structural output failure or Wave1 parser/local
semantic failure. A post-candidate `SubmissionValidationFailure`, its codes, and
later artifact validation SHALL remain controller evidence and SHALL not construct a
repair request. A selected live tool-bearing worker calibration SHALL require strict
model and web credential preflight and invoke its generated branch request through a
real model-and-web bridge. A selected zero-tool repair or critic calibration SHALL
require strict model credential preflight and invoke only its generated zero-tool
branch request through a real model bridge. The selected runner SHALL not use a fake
capability as judgment-quality evidence, expand or execute `LIVE_CANARIES`, or imply
a full-pipeline evaluation. Each selected live case SHALL report its stable case and
branch identity, complete criterion identifiers, a typed `pass`, `limited`, or
`inconclusive` rubric disposition, hard-invariant outcomes, bounded redacted
diagnostics, and available cost/latency fields. A hard-invariant or execution failure
SHALL remain the existing live-run failure rather than receive a fabricated rubric
disposition. Default deterministic verification SHALL not execute or relabel this
live evidence, and the prior intake-and-planning corpus and canonical live-canary
count, identities, and deadline budget SHALL remain unchanged. When a typed rubric
result is present, evidence-v1 report validation SHALL resolve it only through a
closed union of the two named calibration corpus indexes, require case identity to be
globally unique across those collections, and reject a branch or criterion tuple that
does not match its resolved case. An older evidence-v1 report without a rubric result
SHALL remain readable.

#### Scenario: Deterministic conformance does not claim evidence judgment quality
- **WHEN** a fake-capability Wave0 or Wave1 case proves request composition, tool
  posture, repair/review bounds, and deterministic non-admission
- **THEN** its evidence is classified as deterministic conformance and does not pass
  the branch's labeled quality rubric or claim that a model made a useful source or
  evidence judgment

#### Scenario: Selected live calibration preflights the branch tool posture strictly
- **WHEN** an operator explicitly selects a tool-bearing evidence-intake calibration
  without every required model and web credential, or a zero-tool calibration without
  its required model credential
- **THEN** preflight fails before invocation without skipping, widening a tool
  posture, or recording a quality result

#### Scenario: Each selected live calibration reports its bounded result
- **WHEN** an operator explicitly selects an evidence-intake calibration case with
  valid credentials
- **THEN** the case evaluates only its named branch and rubric, records its stable
  case/branch identity and bounded typed result, and leaves evidence acceptance,
  review-artifact publication, gate evaluation, and routing under their existing
  deterministic owners

#### Scenario: Selected live execution uses the branch-appropriate dependency seam
- **WHEN** an operator selects a tool-bearing worker case or a zero-tool repair or
  critic case with valid credentials
- **THEN** the runner invokes only that generated branch request through the required
  real model-and-web or real model-only bridge, respectively, without using a fake
  capability, expanding canonical canaries, or asserting a full-pipeline result

#### Scenario: Failed branch mechanics do not receive a quality rubric
- **WHEN** a selected live branch violates its generated request's tool posture or
  resource bound, fails real bridge execution, cannot parse through its production
  parser, or (for a Wave1 worker or repair) fails local semantic validation
- **THEN** the selected run fails without a `pass`, `limited`, or `inconclusive`
  rubric disposition; only a mechanically valid candidate can be evaluated for its
  labeled judgment criteria

#### Scenario: Separate calibration collections preserve existing governance
- **WHEN** default deterministic verification, the previous intake-and-planning
  calibration corpus, and canonical live-canary validation are checked
- **THEN** neither calibration corpus is executed as deterministic evidence, their
  stable identities remain disjoint, typed report validation resolves each rubric
  result only to its owning corpus, and canonical canaries retain their existing six
  cases and deadline budget

#### Scenario: Rubric disposition is not a hidden retrieval or retry
- **WHEN** a selected live calibration completes with all hard invariants but cannot
  satisfy or assess all declared criteria
- **THEN** it records `limited` or `inconclusive` under the stated rubric meanings
  without adding a model call, retrieval, production retry, lifecycle fact, or route
  claim

#### Scenario: Post-candidate validation is not a repair-calibration input
- **WHEN** a constructed Wave0 or Wave1 candidate receives a post-candidate
  submission-validation failure
- **THEN** deterministic controller evidence observes the existing terminal/retry
  path without invoking a repair prompt, exposing validation codes to a model, or
  treating that failure as a live judgment-calibration case
