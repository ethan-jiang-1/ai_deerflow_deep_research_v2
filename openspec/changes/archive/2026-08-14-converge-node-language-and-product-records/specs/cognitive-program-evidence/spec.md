> req: CPE-001, CPE-004

## MODIFIED Requirements

### Requirement: Every active direct branch has an individual evidence ledger row

The active logical-node owners SHALL maintain one test-owned cognitive-program
evidence row for each current direct model branch. The row IDs SHALL equal both the
canonical prompt-catalog case IDs and `COHORT_EVIDENCE` case IDs exactly. Each row
SHALL record product responsibility, bounded question, trusted/untrusted input
boundary, mandatory capability ref, catalog and final-render seam, requested tool
window, bridge-enforcement seam, feedback disposition and recipient when one
exists, candidate/admission owner, guardrail evidence, classified evidence links,
and evaluation disposition. A node aggregate, grouped row, owner count, or catalog
count SHALL not close a missing branch row; the ledger SHALL remain a review
projection and SHALL not select a prompt, tool, route, model, candidate, or
lifecycle result. (`CPE-001`)

#### Scenario: Branch inventory is reviewed
- **WHEN** maintainers review active cognitive evidence
- **THEN** they can establish exact twenty-branch coverage, including
  `readiness/critic`, `final-delivery/composer`, `wave1/source-diagnostic`, and
  `wave1/claim-verifier`, and identify the ref, composition, feedback, and guardrail
  proof plus the evaluation disposition for each branch

### Requirement: Complete evidence board keeps node identity and branch proof separate

The project SHALL maintain one compact, test-owned cognitive-program evidence board
whose node rows equal the eleven logical topology nodes exactly and whose branch rows
equal the twenty canonical prompt-catalog and capability-inventory cases exactly.
Each node row SHALL state, in separate fields, its specific product responsibility,
participation mode, commitment state, source-audited current operating mechanism,
deterministic authority owner, and audit-only direct model-branch IDs. It SHALL also
record the bounded cognitive, conditional human-decision, or controller hypothesis;
selected collected node proof; live-evaluation applicability; and a known limitation
or an explicit none disposition. Node proof links SHALL be classified as
`cognitive-program`, `human-decision`, `deterministic-guardrail`, or `wiring` and
SHALL resolve to their declared node owner. A `human-decision` node link MAY prove
only HITL2's conditional admission precondition and no-current-interaction boundary;
it SHALL not claim an implemented choice. (`CPE-004`)

The board SHALL retain one branch-review wrapper for each of the twenty existing
branch-ledger rows. Each wrapper SHALL name its exact branch ID, a known limitation,
and exact calibration-case/central-live-claim pairs. The pair set SHALL equal all
forty-one unique cases in the four current calibration registries exactly and SHALL
span every branch. Every pair SHALL resolve to a calibration case whose `branch_id`
equals the wrapper branch and to the unique collected live claim whose
`scenario_case_id` equals that case. Collection SHALL prove only selector provenance
and evaluation applicability; it SHALL not claim that live execution occurred,
passed, or established model quality.

The board SHALL join the topology, reader projection, branch ledger, workflow
coverage, node conformance, calibration registries, central evidence claims, and
requirement impacts without copying any of their execution authority. It SHALL
reject missing, duplicate, stale, or grouped node, branch, or calibration-case rows;
a generic category or Charter `node-agent`/`no-agent` binary used as product identity;
a direct branch not supported by current source/catalog discovery; an active-loop
claim without branch and workflow evidence; an under-specified active cognitive
program; an unknown, uncollected, wrong-owner, or wrongly classified proof mapping;
and an evaluation case or claim joined to the wrong branch. Active-branch closing
proof SHALL remain `cognitive-program`, `deterministic-guardrail`, or `wiring`;
`human-decision` SHALL be rejected for active-branch proof, and
`obsolete-duplicate` SHALL remain non-closing.

#### Scenario: Exact node and branch sets close independently
- **WHEN** the evidence board is validated against the current topology, prompt
  catalog, and capability inventory
- **THEN** all eleven logical nodes and all twenty direct branches are present as
  individual rows, and neither denominator can substitute for the other

#### Scenario: Participation and current mechanism remain honest
- **WHEN** a reviewer compares the conditional HITL2 row, intentional bootstrap/rerun
  controller rows, and active readiness/final-delivery rows
- **THEN** commitment and participation remain distinct from current branch evidence,
  and no absent/present model branch or Charter binary determines product identity

#### Scenario: Active cognitive proof is complete
- **WHEN** an active direct branch is included in the board
- **THEN** its cognitive hypothesis, model-visible composition, deterministic
  guardrail/admission, loop or feedback disposition, evaluation applicability, exact
  calibration-case/central-claim links, and known limitation are reviewable at that
  exact branch rather than inherited from an owner aggregate

#### Scenario: Collected evaluation metadata is not a quality result
- **WHEN** a branch's calibration selector and central live claim are collected
- **THEN** the board establishes the exact declared evaluation seam but does not
  report a live execution, disposition, or model-quality outcome

#### Scenario: Mis-scoped calibration input cannot self-certify
- **WHEN** the board is given an empty, partial, or self-consistent substitute for
  the four validated calibration registries
- **THEN** the exact forty-one-case union and branch join fail rather than presenting
  incomplete evaluation applicability as current coverage

#### Scenario: Evidence board cannot become workflow authority
- **WHEN** the board is read, validated, or rendered
- **THEN** no prompt, capability, tool permission, candidate, route, state, artifact,
  recovery, or lifecycle result is selected or created
