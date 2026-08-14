> req: DRC-004

## MODIFIED Requirements

### Requirement: Active changes declare a bounded Focus Card

Every active OpenSpec change in this Deep Research planning home SHALL use exactly
one admission form in its proposal. An ordinary change SHALL include exactly one
`## Change Focus` section with non-empty Primary module / causal owner, Question,
Necessary adjacent/external contracts, Evidence seam, and Not in scope fields. The
primary module / causal owner SHALL identify the smallest module that owns the
changed semantic decision; a presentation adapter alone is insufficient when another
module owns that decision. The change-admission policy SHALL require the card before
implementation. A non-`none` Necessary adjacent/external contracts entry SHALL name
the contract and the question it answers; it is not a list of potentially useful
places to browse.

A declared program change SHALL instead include exactly one `## Program Focus` and
at least two `### Workstream Focus: <stable-id>` records, where `<stable-id>` matches
`[a-z][a-z0-9-]*`. Program Focus SHALL have
non-empty Program outcome, Candidate / obligation budget, Declared workstream order,
Program decision authority, Shared archive invariant, Program failure / recovery,
Split / expansion rule, and Not in scope fields. The program decision authority
approves only program scope, order, and archive closure; it SHALL NOT become a
runtime fact authority, runtime writer, shared implementation owner, or substitute
for a workstream's semantic decision authority.

Each Workstream Focus SHALL use a unique stable ID and a distinct non-empty Primary
module / causal owner. It SHALL retain the complete Focus Card fields, plus non-empty
Candidate / obligation IDs, Target / retirement, Surface grade, Decision authority,
and Negative path / recovery fields. Its Candidate / obligation IDs SHALL be a
unique non-empty comma-separated list. The declared program budget SHALL be a unique
comma-separated list whose set exactly equals the union of all workstream IDs; every
declared workstream SHALL have one matching record and no undeclared workstream
record SHALL be admitted. A workstream SHALL select its applicable policies and
retain each required review record under its own level-four canonical review heading;
a program-level or another workstream's review record SHALL NOT satisfy that route.

The deterministic charter checker SHALL reject a missing, malformed, mixed, or
unclosed ordinary/program admission form and required charter navigation/policy
surfaces, including the stable context-expansion gate anchors, but SHALL not infer
semantic correctness from prose or certify implementation diff scope. Every active
proposal's Focus Card or Workstream Focus SHALL include a `Seam classification`
field whose value is exactly one of `cognitive-program`, `human-decision`,
`deterministic-guardrail`, or `wiring`, with a short rationale. The field names the
primary edit target of the ordinary change or workstream; it SHALL NOT be inferred
from the first file opened or from the presence or absence of a `run_agent` call. A
`cognitive-program` classification SHALL state the cognitive hypothesis and
observable result that justify the edit; `human-decision`,
`deterministic-guardrail`, and `wiring` SHALL name the deterministic owner that
remains authoritative. The deterministic charter checker SHALL reject a Seam
classification that is missing, empty, outside the closed value set, or lacks a
short rationale, and SHALL NOT judge the semantic truth of the classification.
(`DRC-004`)

#### Scenario: Missing Focus Card fails governance
- **WHEN** an ordinary active proposal lacks one required Focus Card field
- **THEN** the charter checker fails with the proposal path and missing field before
  implementation can claim charter conformance

#### Scenario: An ordinary change remains single-owner
- **WHEN** an active ordinary proposal contains a Program Focus or more than one
  Change Focus
- **THEN** the charter checker rejects the mixed or widened form before the change
  can use a program label to bypass the single-owner admission boundary

#### Scenario: A bounded program closes its declared registration
- **WHEN** an active program proposal declares a complete unique Candidate / obligation
  budget, ordered workstreams with distinct owners, and one complete matching
  Workstream Focus for each registered stable ID
- **THEN** the charter checker accepts the proposal grammar while leaving semantic
  owner, cutover, and archive-scope review to the declared apply/archive reviewers

#### Scenario: An unclosed program fails governance
- **WHEN** a program budget and its workstream union differ, an ID or workstream
  owner is duplicated, a mandatory program/workstream field is absent, or a
  workstream is missing from or added outside the declared registration
- **THEN** the charter checker rejects the active proposal before implementation

#### Scenario: A workstream owns its policy review
- **WHEN** a program Workstream Focus selects a policy that requires a review record
- **THEN** the charter checker requires the canonical level-four review heading and
  complete table inside that workstream, and rejects a program-level or sibling
  workstream table as a substitute

#### Scenario: Program recovery does not permit partial archival
- **WHEN** a program workstream cannot close its declared evidence or cutover within
  the frozen scope
- **THEN** the Program Focus keeps the change active for approved forward repair, or
  rollback of that workstream and its dependents, and otherwise returns the decision
  to plan-level re-scope or whole-program rollback rather than allowing partial archive

#### Scenario: A focused change avoids unnecessary upstream discovery
- **WHEN** a change does not call DeerFlow APIs
- **THEN** its Necessary external contracts field may state `none`, and the
  contributor need not inspect or alter unrelated DeerFlow implementation details

#### Scenario: A newly necessary contract has a causal admission
- **WHEN** implementation or the evidence seam exposes a contract not listed in the
  Focus Card
- **THEN** the contributor records the named contract and the question it must answer
  before widening the change's reading scope, or resolves the ownership ambiguity
  before implementation continues

#### Scenario: A missing seam classification fails governance
- **WHEN** an active ordinary proposal's Focus Card or program workstream Focus omits
  Seam classification, leaves it empty, uses a value outside the closed set, or
  supplies no rationale
- **THEN** the charter checker fails with the proposal path and missing or invalid
  field before implementation can claim charter conformance

#### Scenario: A cognitive-program classification carries its hypothesis
- **WHEN** a proposal classifies its Focus Card or Workstream Focus as
  `cognitive-program` to adjust a node's capability policy, prompt composition, or
  feedback
- **THEN** that focus record stores the bounded cognitive hypothesis and the
  observable result or evaluation that will show whether the edit worked, and names
  the deterministic owner that still admits the candidate

#### Scenario: A guardrail classification names the deterministic owner
- **WHEN** a proposal classifies its Focus Card or Workstream Focus as
  `deterministic-guardrail` or `wiring` for an admission, gate, route, or evidence
  change
- **THEN** that focus record names the deterministic owner that remains authoritative
  and does not claim a cognitive quality improvement for the node
