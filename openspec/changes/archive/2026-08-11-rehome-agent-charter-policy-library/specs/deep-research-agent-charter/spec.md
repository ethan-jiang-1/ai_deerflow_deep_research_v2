> req: DRC-001, DRC-005, DRC-009, DRC-010

## RENAMED Requirements

- FROM: `### Requirement: Control-placement guidance is externally routed and non-authoritative`
- TO: `### Requirement: Control-placement guidance is cross-cutting and non-authoritative`

## MODIFIED Requirements

### Requirement: A canonical Deep Research Agent Charter is discoverable

The project SHALL maintain `openspec/agent-charter/` as the permanent home for the
Deep Research Agent Charter. Its index SHALL route contributors to one relevant policy
in the canonical `openspec/policies/` library and SHALL distinguish durable charter
principles, focused policies, owning capability specifications, scoped operational
procedures, and current runtime facts. The Charter and every policy SHALL state that
they are design/admission guidance and do not create runtime authority. The Charter
tree SHALL contain only its routing index and durable principles; it SHALL not contain
a second nested policy directory or compatibility copy of policy prose. (`DRC-001`,
`DRC-005`)

#### Scenario: Contributor routes a local change without scanning the repository
- **WHEN** a contributor begins a Deep Research change affecting one owned module
- **THEN** the Charter index identifies the local-context policy in the canonical
  policy library and directs the contributor to the owning capability specification
  and local evidence seam rather than requiring an undifferentiated read of root
  DeerFlow documentation

#### Scenario: Charter and policy library are discoverable from OpenSpec root
- **WHEN** a contributor opens `openspec/` to begin a Deep Research change
- **THEN** it can discover `agent-charter/` as the one routing entry and `policies/`
  as the one complete policy library without traversing a governance subtree or
  choosing between duplicate policy homes

#### Scenario: A behavior proposal is placed in its owning contract
- **WHEN** a proposed policy would add a lifecycle action, state field, graph route,
  permission, or provider behavior
- **THEN** the Charter index directs the change to an owning capability delta and
  the policy does not claim to establish that behavior by itself

### Requirement: Charter policies preserve source-of-truth discipline and bounded recovery

The Charter SHALL route focused policies from the single `openspec/policies/` library
for authority/projections and control/recovery. Those policies SHALL direct changes to
use the existing owner of checkpointed control state, evidence ledger, sandbox
content, typed result, or external contract; they SHALL reject shadow control records,
silent fallback, unbounded retries, and invented recovery actions. The policy-library
index SHALL not become a second Charter, infer applicability, or grant runtime
authority. A policy that needs to alter an owning contract SHALL require a
corresponding capability change. (`DRC-005`)

#### Scenario: A diagnostic remains an observation
- **WHEN** a change retains a diagnostic summary or event record for inspection
- **THEN** the authority-and-projections policy directs it to remain a bounded
  projection and preserves the owning checkpoint or result contract as the only
  lifecycle authority

#### Scenario: A retry policy has a named owner and bound
- **WHEN** a change proposes automatic recovery from an external failure
- **THEN** the control-and-recovery policy requires the owning phase or contract to
  state the closed retryable category, invocation bound, terminal disposition, and
  nearest legal action instead of adding a presentation-layer retry loop

#### Scenario: A policy library does not become a second routing authority
- **WHEN** a contributor opens a policy directly from `openspec/policies/`
- **THEN** its trigger guides the contributor back through the Charter's selected
  policy route and does not create a second Charter, runtime controller, or policy
  applicability inference mechanism

### Requirement: Control-placement guidance is cross-cutting and non-authoritative

The Deep Research Agent Charter SHALL route `control-placement` from the canonical
`openspec/policies/` library for a change that adds or changes a gate, validator,
readiness check, candidate admission, retry/fallback/recovery, next-action diagnostic,
durable control fact, checkpoint/state writer, or cognitive/control boundary between a
Node Agent, a human decision, and a deterministic owner. The policy-library index
SHALL classify it as cross-cutting review guidance alongside, rather than outside of,
the Charter-routed policy set. It SHALL distinguish itself from Charter routing,
deterministic governance checks, and the delivered selected-change closeout-evidence
capability. It SHALL state that it creates no runtime route, state write, permission,
retry, model role, lifecycle action, semantic evaluator, automatic task writer, or
archive coordinator/blocker.

The policy SHALL use only the closed design postures `advisory`, `bounded-repair`,
`human-decision`, and `non-bypassable`. It SHALL direct an author to identify a
cognitive candidate or human judgment, the direct fact and its deterministic
owner/evaluator, protected invariant or legal recovery, reused/avoided control, and
the lowest responsible deterministic evidence seam. A `human-decision` posture SHALL
also select the existing `human-interaction-integrity` policy rather than creating a
waiver or human-action contract. (`DRC-009`)

#### Scenario: A changed admission boundary has a focused review route
- **WHEN** a change moves comparison, acceptance, retry, or other control admission
  between a candidate/human surface and a deterministic owner
- **THEN** the Charter index and policy-library index identify `control-placement` as
  the focused cross-cutting review policy without treating the policy as runtime
  authority

#### Scenario: A durable fact has a handoff-aware evidence expectation
- **WHEN** a selected control-placement review names a direct fact that crosses a
  producer/consumer boundary or is persisted for later consumption
- **THEN** the policy directs its deterministic evidence seam to cover the real
  handoff or the write/reload/direct-consumer chain rather than a hand-built consumer
  fixture or presentation-only assertion

#### Scenario: A human choice remains a typed capability decision
- **WHEN** a selected review uses the `human-decision` posture
- **THEN** the proposal also selects `human-interaction-integrity`, and the policy
  does not claim that human text or review prose can bypass an invariant or create a
  lifecycle effect

### Requirement: Selected control-placement records are mechanically bounded

Every active Deep Research proposal SHALL use one Focus Card list item named
`Triggered review policies` to declare a comma-separated list of canonical policy
library names, or `none: <short rationale>` when no review policy applies. A proposal
selecting `control-placement` SHALL contain exactly one complete
`## Control Placement Review` table with this header, separator, and at least one row:

```text
| Changed decision or fact | Cognitive candidate or human judgment | Direct fact and deterministic owner/evaluator | Design posture | Protected invariant or legal recovery | Reuse or complexity removed/avoided | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- |
```

Every table cell SHALL be non-empty. `Design posture` SHALL be one of the closed
postures named by the control-placement policy. A change with both a human input and a
non-bypassable invariant SHALL use distinct rows. Existing Node Agent and Workflow
Outcome Review requirements SHALL remain independently enforced whenever their
selected policies require them.

The deterministic charter checker SHALL validate only canonical policy lookup,
declared policy document availability, Focus Card field shape, conditional record
shape, closed posture values, and the `human-decision` policy combination. It SHALL
not infer whether a proposal ought to select the policy, inspect source code, judge
the truth of a review row, or grant runtime authority. (`DRC-009`)

#### Scenario: A complete selected control-placement review is accepted
- **WHEN** an active proposal selects `control-placement` and supplies one or more
  complete rows with valid postures in the exact table format
- **THEN** the charter checker accepts its control-placement record while preserving
  the proposal's separate selected-review validation

#### Scenario: A malformed selected control-placement review fails closed
- **WHEN** an active proposal selects `control-placement` but the policy-library
  document is unavailable, the Focus Card field is malformed, the review is missing,
  its header differs, a cell is empty, or a posture is not closed
- **THEN** the charter checker reports deterministic conformance failure without
  attempting to infer or repair the missing semantic decision

#### Scenario: Human-decision posture requires the existing interaction review
- **WHEN** a selected control-placement review contains a `human-decision` row but
  `human-interaction-integrity` is absent from Triggered review policies
- **THEN** the charter checker rejects the proposal while leaving the owning human
  interaction contract responsible for any actual input schema, control, state
  effect, or route

#### Scenario: Existing conditional reviews remain distinct
- **WHEN** an active proposal selects control-placement together with
  `node-agent-workflow-integrity` or `workflow-outcome-review`
- **THEN** the charter checker requires every corresponding review record and does
  not treat the Control Placement Review as a substitute for candidate handoff or
  failure/recovery behavior

#### Scenario: Archived proposals remain historical records
- **WHEN** the policy-library migration is applied to the active planning home
- **THEN** archived change artifacts remain unmodified and the checker evaluates only
  active proposals against the current admission contract

### Requirement: Selected control-placement review has durable operation guidance

For an active Deep Research proposal whose `Triggered review policies` includes
`control-placement`, the OpenSpec authoring route SHALL require `tasks.md` to retain
one plan-review obligation and one archive-closeout-review obligation until each has
an owner, minimal correction or review action, and an honest deterministic or bounded
evidence done condition. The route SHALL not require those obligations solely because
the proposal selects another policy from the unified policy library.

`openspec/config.yaml` SHALL provide distinct `operations.apply.guidance` and
`operations.archive.guidance`. OpenSpec SHALL return those configured strings as
general operation guidance because configuration cannot inspect a Focus Card; each
entry SHALL state that its control-placement review applies only after the current
agent confirms that the selected proposal declares `control-placement`. Apply guidance
SHALL direct the current agent to re-read the selected change's review context and
turn an actionable finding into an ordinary task. Archive guidance SHALL direct the
current agent to review the selected change's actual boundary, unresolved tasks, and
existing deterministic evidence before describing closeout.

When a change uses the delivered selected-change closeout-evidence capability, the
authoring route SHALL identify it as a separate, caller-declared and Git-verified
boundary contract. It SHALL state that the resulting record is non-authoritative and
that operation guidance remains advisory: neither surface executes commands, creates
or completes tasks, infers a finding, validates semantic quality, nor blocks a native
OpenSpec operation. (`DRC-010`)

#### Scenario: A selected control-placement change is resumed for apply
- **WHEN** an agent receives apply instructions for an active proposal that selects
  `control-placement`
- **THEN** the operation guidance routes it to the selected review and its durable
  plan-review task, and any newly actionable finding remains an ordinary unfinished
  task rather than an implied completed review

#### Scenario: A selected control-placement change reaches archive review
- **WHEN** an agent receives archive instructions for an active proposal that selects
  `control-placement`
- **THEN** the operation guidance directs attention to the selected change's actual
  boundary, unresolved closeout work, and existing deterministic evidence without
  claiming that the guidance itself accepted or blocked archive

#### Scenario: Verified boundary evidence has a separate authority boundary
- **WHEN** a selected control-placement change records closeout evidence through a
  caller-declared, Git-verified range
- **THEN** the Charter route distinguishes that evidence from operation guidance and
  preserves native archive, semantic judgment, and task-led finding ownership outside
  both surfaces

#### Scenario: Another selected policy does not create cross-session task ceremony
- **WHEN** an active proposal selects a policy other than `control-placement`
- **THEN** the authoring route does not require the control-placement plan-review or
  archive-closeout-review obligations solely from that other policy selection

#### Scenario: Shared guidance does not create a non-selected obligation
- **WHEN** an apply or archive instruction returns the configured operation guidance
  for a proposal that does not select `control-placement`
- **THEN** the current agent treats the guidance as inapplicable to that review and
  does not create a control-placement obligation solely because the shared string was
  delivered

#### Scenario: Guidance delivery cannot become operation authority
- **WHEN** operation guidance is absent, malformed, ignored, or followed without a
  finding
- **THEN** it neither changes native apply/archive state nor claims that a task,
  checker, semantic review, or archive transition was executed
