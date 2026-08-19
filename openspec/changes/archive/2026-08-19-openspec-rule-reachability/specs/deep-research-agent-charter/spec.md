> req: DRC-010

## MODIFIED Requirements

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
agent confirms that the selected proposal declares `control-placement`. Apply
guidance SHALL direct the current agent to re-read the selected change's review
context and turn an actionable finding into an ordinary task. Archive guidance SHALL
direct the current agent to review the selected change's actual boundary, unresolved
tasks, and existing deterministic evidence before describing closeout.

When a change uses the delivered selected-change closeout-evidence capability, the
authoring route SHALL identify
`openspec/governance/selected-change-closeout.py` as its separate,
caller-declared and Git-verified boundary command. It SHALL state that the resulting
record is non-authoritative and that operation guidance remains advisory: neither
surface executes commands, creates or completes tasks, infers a finding, validates
semantic quality, nor blocks a native OpenSpec operation. (`DRC-010`)

The project SHALL maintain an independent canonical project governance gate that
combines the registered OpenSpec component checkers and MAY stop the
repository-managed archive agent workflow when any component checker exits non-zero.
This stopping authority SHALL derive solely from the deterministic component
checkers' exit statuses; it SHALL NOT derive from operation guidance or from
selected-change closeout evidence, which remain advisory and non-authoritative as
stated above. The gate SHALL NOT block or directly change a native `openspec
archive` invocation. Recovery from a stopped repository-managed workflow SHALL be
to fix the named finding and re-run the gate until it exits zero. (`DRC-010`)

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
- **THEN** the Change Guidance route distinguishes that evidence from operation
  guidance and preserves native archive, semantic judgment, and task-led finding
  ownership outside both surfaces

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

#### Scenario: A deterministic gate stop leaves guidance and native authority unchanged
- **WHEN** the canonical project governance gate exits non-zero during a
  repository-managed archive agent workflow
- **THEN** the workflow stops with the failing component checker named, the gate's
  stopping authority comes from the deterministic component checkers rather than
  from operation guidance or selected-change evidence, and a direct native
  `openspec archive` invocation is neither blocked nor modified; recovery is to fix
  the named finding and re-run the gate
