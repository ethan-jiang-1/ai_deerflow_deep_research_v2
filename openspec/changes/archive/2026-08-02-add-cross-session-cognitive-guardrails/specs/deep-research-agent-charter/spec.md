## MODIFIED Requirements

### Requirement: Selected control-placement review has durable operation guidance

For an active Deep Research proposal whose `Triggered review policies` includes
`control-placement`, the OpenSpec authoring route SHALL require `tasks.md` to retain
one plan-review obligation and one archive-closeout-review obligation until each has
an owner, minimal correction or review action, and an honest deterministic or bounded
evidence done condition. The route SHALL not require those obligations solely because
the proposal selects another charter or external review policy.

`openspec/config.yaml` SHALL provide distinct `operations.apply.guidance` and
`operations.archive.guidance`. OpenSpec SHALL return those configured strings as
general operation guidance because configuration cannot inspect a Focus Card; each
entry SHALL state that its control-placement review applies only after the current
agent confirms that the selected proposal declares `control-placement`. Apply
guidance SHALL direct the current agent to re-read the selected change's review
context and turn an actionable finding into an ordinary task. Archive guidance SHALL
direct the current agent to review the selected change's actual boundary, unresolved
tasks, and existing deterministic evidence before describing closeout.

When a change uses the selected-change closeout-evidence capability, the authoring
route SHALL identify it as a separate, caller-declared and Git-verified boundary
contract. It SHALL state that the resulting record is non-authoritative and that
operation guidance remains advisory: neither surface executes commands, creates or
completes tasks, infers a finding, validates semantic quality, nor blocks a native
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
- **THEN** the charter route distinguishes that evidence from operation guidance and
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

### Requirement: Operation-guidance integration evidence stays bounded

The project SHALL retain deterministic, local evidence for the OpenSpec operation
guidance contract and for the selected-change boundary that a cross-session guardrail
consumes. The evidence SHALL cover configured guidance delivery, absence, and fresh
config-read behavior; the supported native archive path and observable side effects;
selected-change committed-range verification; historical replay through the
finding-to-task/resume loop; and the narrow input facts that the closeout-evidence
capability may consume. It SHALL preserve failures or unknowns as probe results
rather than treating advisory text or a review record as a fail-closed guarantee. The
evidence SHALL not create a semantic evaluator, fresh-session identity assertion,
automatic task writer, archive wrapper, or archive blocker. (`DRC-010`)

#### Scenario: A missing delivery or fresh-read mechanism remains an observed limitation
- **WHEN** a local operation-guidance probe cannot demonstrate delivery, fresh config
  reading, or a native archive side effect
- **THEN** the result is retained as a bounded failure or unknown rather than being
  converted into coordinator behavior or a successful closeout claim

#### Scenario: Boundary failure remains an observed limitation
- **WHEN** a caller cannot provide a valid committed selected-change range
- **THEN** the capability records `missing-boundary` without converting the shared
  worktree into a coverage claim or an archive decision

#### Scenario: Guardrail evidence consumes only observed integration facts
- **WHEN** a selected change records closeout evidence after its local probes complete
- **THEN** it uses the recorded delivery, archive, boundary, and replay facts without
  treating operation guidance as a coordinator or native archive authority
