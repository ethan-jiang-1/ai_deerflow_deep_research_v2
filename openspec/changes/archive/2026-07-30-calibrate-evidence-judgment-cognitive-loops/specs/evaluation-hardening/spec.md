> req: EVH-020

## ADDED Requirements

### Requirement: Evidence-judgment calibration has branch-specific judgment evidence

Test-owned evidence SHALL define a third dedicated twelve-case labeled calibration corpus: one
normal and one highest-risk case for each Wave2 synthesis, Wave2 synthesis repair, targeted worker,
targeted worker repair, targeted SourceDiagnostic, and targeted ClaimVerifier branch. It SHALL be
separate from the intake-and-planning and evidence-intake calibration corpora, canonical
`LIVE_CANARIES`, and the lane-neutral `ScenarioCase` registry. Each case SHALL declare a stable
case and branch identity, bounded trusted assignment, untrusted input boundary when present,
expected candidate constraints, criterion identifiers and quality rubric, permitted degradation,
nondeterministic boundary, and outer-attempt, model-call, tool-call, token, and timeout bounds no
wider than its existing branch request and declared live-runner policy. Rubrics SHALL evaluate only
whether a candidate is assignment-faithful, evidence-grounded, conservative about uncertainty,
provenance- or identity-bound where applicable, and decision-ready for its deterministic owner.
They SHALL not assert source truth, research quality, evidence acceptance, artifact publication,
gate correctness, route correctness, or a model judgment from a deterministic fixture.

Each branch SHALL retain separate lowest-seam deterministic proof of request composition,
runtime-enforced tool posture, repair or review containment, and non-admission. A selected
tool-bearing targeted-worker calibration SHALL require strict model and web credential preflight
and invoke only its generated branch request through a real model-and-web bridge. A selected
zero-tool Wave2, repair, or critic calibration SHALL require strict model credential preflight and
invoke only its generated branch request through a real model-only bridge. Generated tool posture
and resource bounds, a successful real bridge invocation, and production parsing SHALL be hard
invariants. A hard-invariant or execution failure SHALL remain the existing live-run failure and
SHALL not receive a rubric disposition. A typed rubric result SHALL resolve only through a closed
union of the three named calibration corpus indexes, require case identity to be globally unique,
and reject a branch or criterion tuple that does not match its resolved case. An older evidence-v1
report without a rubric result SHALL remain readable. Default deterministic verification SHALL not
execute or relabel this live evidence, and the existing two calibration corpus identities plus the
canonical live-canary count, identities, and deadline budget SHALL remain unchanged.

#### Scenario: Deterministic conformance does not claim evidence-judgment quality
- **WHEN** a fake-capability Wave2 or targeted-evidence case proves request composition, tool
  posture, repair/review bounds, and deterministic non-admission
- **THEN** its evidence is classified as deterministic conformance and does not pass the branch's
  labeled quality rubric or claim that a model made a useful synthesis or evidence judgment

#### Scenario: Selected live calibration preflights branch dependency posture strictly
- **WHEN** an operator explicitly selects a tool-bearing targeted-worker calibration without every
  required model and web credential, or a zero-tool Wave2, repair, or critic calibration without
  its required model credential
- **THEN** preflight fails before invocation without skipping, widening a tool posture, or recording
  a quality result

#### Scenario: Each selected live calibration reports only its bounded result
- **WHEN** an operator explicitly selects an evidence-judgment calibration case with valid
  credentials and all branch hard invariants succeed
- **THEN** the case evaluates only its named branch and rubric, records its stable case/branch
  identity and bounded typed result, and leaves evidence acceptance, artifact publication, ledger
  mutation, convergence-gate evaluation, and routing under their existing deterministic owners

#### Scenario: Failed branch mechanics do not receive a quality rubric
- **WHEN** a selected live branch violates its generated request's tool posture or resource bound,
  fails real bridge execution, or cannot parse through its production parser
- **THEN** the selected run fails without a `pass`, `limited`, or `inconclusive` rubric disposition;
  only a mechanically valid candidate can be evaluated for its labeled judgment criteria

#### Scenario: Closed calibration collections preserve prior report and canary governance
- **WHEN** default deterministic verification, typed evidence-v1 report validation, and canonical
  live-canary validation are checked
- **THEN** all three calibration corpora remain excluded from deterministic execution, a present
  rubric resolves only to its owning unique corpus case, older reports without a rubric remain
  readable, and canonical canaries retain their existing six cases and deadline budget

#### Scenario: Rubric disposition is not a hidden retrieval or retry
- **WHEN** a selected live calibration completes with all hard invariants but cannot satisfy or
  assess all declared criteria
- **THEN** it records `limited` or `inconclusive` under the stated rubric meanings without adding
  a model call, retrieval, production retry, lifecycle fact, or route claim

