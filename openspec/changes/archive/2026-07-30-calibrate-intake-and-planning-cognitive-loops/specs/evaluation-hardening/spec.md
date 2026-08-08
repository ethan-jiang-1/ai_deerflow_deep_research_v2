> req: EVH-018

## ADDED Requirements

### Requirement: Intake and planning calibration has branch-specific judgment evidence

Test-owned calibration evidence SHALL define a dedicated labeled corpus with exactly
one normal and one highest-risk case for each current zero-tool branch: HITL1 profile
brief, profile-brief repair, semantic intake, semantic-intake repair, topic planning,
and topic-plan repair (twelve cases total). It SHALL be separate from both the
canonical `LIVE_CANARIES` collection and the lane-neutral `ScenarioCase` registry.
Every case SHALL name its stable case and branch identity, bounded trusted assignment,
untrusted input boundary when present, expected candidate constraints, explicit
criterion identifiers and quality rubric, nondeterministic boundary, and permitted
degradation. The rubrics SHALL evaluate only whether a candidate is conservative,
faithful to its bounded assignment, and decision-ready; they SHALL not assert source
truth, research quality, human acceptance, topic-registry publication, route
correctness, or a model judgment from deterministic fixtures. A `pass` SHALL mean all
declared criteria were assessable and satisfied; `limited` SHALL mean an assessable
candidate failed one or more declared criteria; `inconclusive` SHALL mean a successful
live run supplied insufficient admissible candidate evidence to assess a declared
criterion. A hard-invariant or execution failure SHALL remain the existing live-run
failure rather than receive a fabricated rubric disposition.

Each branch SHALL retain separate lowest-seam deterministic proof that its rendered
request, zero-tool posture, repair bound, and deterministic non-admission boundary
are intact. Each quality case SHALL execute only through an explicitly selected
`requires_llm` test and SHALL report stable case and branch identity, criterion ids,
a typed `pass`, `limited`, or `inconclusive` rubric disposition, hard-invariant
outcomes, attempts, bounded redacted diagnostics, and available cost/latency fields.
Each case SHALL declare outer attempt, model-call, tool-call, token, and timeout
bounds no wider than its existing zero-tool branch policy. A present typed rubric
result SHALL contain the complete declared criterion ids, a case id equal to the
report scenario id, and a branch id that resolves to that corpus case.
The typed rubric result SHALL be optional on the evidence-v1 live-report contract:
an existing evidence-v1 archive report without it SHALL remain readable as no rubric
result, and a new report with it SHALL validate the typed fields. Missing credentials
in that selected lane SHALL remain a strict preflight failure; the default
deterministic verification selection SHALL not execute or relabel a live calibration
as deterministic evidence. The canonical `LIVE_CANARIES` count, identities, and
deadline budget SHALL remain unchanged.

#### Scenario: Deterministic conformance does not claim judgment quality
- **WHEN** a fake-capability HITL1 or topic-planning case proves request composition,
  repair bounds, and candidate non-admission
- **THEN** its evidence is classified as deterministic conformance and does not pass
  the branch's labeled quality rubric or claim that a model made a useful judgment

#### Scenario: Each selected live calibration reports its bounded result
- **WHEN** an operator explicitly selects an intake or planning calibration case with
  valid live credentials
- **THEN** the case evaluates only its named branch and rubric, records its stable
  case/branch identity, criterion ids, and bounded typed result, and leaves profile
  acceptance, topic publication, and routing under their existing deterministic owners

#### Scenario: Unselected live calibration does not weaken offline verification
- **WHEN** the normal deterministic verification command is run without live-lane
  selection
- **THEN** all twelve calibration cases remain excluded by `requires_llm` while their
  separate deterministic composition and non-admission evidence still runs

#### Scenario: Calibration does not alter canonical live-canary governance
- **WHEN** the canonical live-canary collection and deadline validator are checked
- **THEN** they retain their six fixed cases, identities, and existing deadline budget,
  while the twelve intake/planning calibration cases remain in their separate
  test-only collection

#### Scenario: Rubric disposition is not a hidden test retry
- **WHEN** a selected live calibration completes with all hard invariants but cannot
  satisfy or assess all of its declared criteria
- **THEN** it records `limited` or `inconclusive` under the stated rubric meanings
  without adding a model retry, changing any production lifecycle fact, or claiming
  a `pass`

#### Scenario: A pre-rubric evidence-v1 archive remains readable
- **WHEN** a stored evidence-v1 live report lacks the optional typed rubric result
- **THEN** archive scanning accepts it as an evidence-v1 report with no rubric result
  rather than reclassifying it, fabricating a disposition, or rejecting the archive
