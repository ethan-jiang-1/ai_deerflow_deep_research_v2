> req: DRC-001, DRC-005, DRC-006, DRC-009, DRC-010

## RENAMED Requirements

- FROM: `### Requirement: A canonical Deep Research Agent Charter is discoverable`
- TO: `### Requirement: A canonical Deep Research Change Guidance route is discoverable`
- FROM: `### Requirement: Charter policies preserve source-of-truth discipline and bounded recovery`
- TO: `### Requirement: Change Guidance policies preserve source-of-truth discipline and bounded recovery`

## MODIFIED Requirements

### Requirement: A canonical Deep Research Change Guidance route is discoverable

The project SHALL maintain `openspec/change-guidance/` as the permanent home for Deep
Research design/admission guidance. Its `README.md` SHALL be the sole routing index and
SHALL route contributors to every canonical policy under
`change-guidance/policies/` whose route-table trigger applies to the change, while the
change retains exactly one primary causal owner. The route SHALL distinguish durable
principles, the bounded node-edit information map, focused policies, owning capability
specifications, scoped operational procedures, and current runtime facts.

The Change Guidance route and every policy SHALL state that they are
design/admission guidance and do not create runtime authority. The root SHALL contain
one routing index, `principles.md`, `node-edit-map.md`, and the complete policy
directory. The policy directory SHALL contain only the ten canonical policy documents
and SHALL NOT contain a second index, duplicate route, or compatibility copy of policy
prose. (`DRC-001`, `DRC-005`)

#### Scenario: Contributor routes a local change without scanning the repository
- **WHEN** a contributor begins a Deep Research change affecting one owned module
- **THEN** the Change Guidance index identifies the local-context policy and directs
  the contributor to the owning capability specification and local evidence seam
  rather than requiring an undifferentiated read of root DeerFlow documentation

#### Scenario: Multiple applicable policy triggers are all selected
- **WHEN** one change affects both a participant-visible lifecycle output and a
  bounded retry or recovery path
- **THEN** its Change Guidance route selects both `participant-outcomes` and
  `control-and-recovery`, records them as canonical names on the same Focus Card
  field, and retains one primary causal owner for the change

#### Scenario: Multiple selected policies do not create runtime authority
- **WHEN** a contributor selects more than one triggered policy for a change
- **THEN** those policies remain design/admission guidance and the contributor still
  places any lifecycle action, state field, graph route, permission, or provider
  behavior in its owning capability delta rather than treating policy selection as
  runtime authority

#### Scenario: Charter and policy library are discoverable from OpenSpec root
- **WHEN** a contributor opens `openspec/` to begin a Deep Research change
- **THEN** `openspec/README.md` routes it to `change-guidance/README.md` as the sole
  guidance index and that index reaches the complete nested policy library without a
  second route

#### Scenario: A behavior proposal is placed in its owning contract
- **WHEN** a proposed policy would add a lifecycle action, state field, graph route,
  permission, or provider behavior
- **THEN** the Change Guidance index directs the change to an owning capability delta
  and the policy does not claim to establish that behavior by itself

### Requirement: Contributor entry documents remain bounded information maps

Change Guidance SHALL include an information-map policy that assigns distinct roles
to `deep_research_harness/AGENTS.md`, `deep_research_harness/CLAUDE.md`,
`deep_research_harness/README.md`, the task-scoped `deep_research_harness/docs/` map,
`openspec/README.md`, and `openspec/config.yaml`.
`deep_research_harness/AGENTS.md` SHALL route ordinary coding work to the smallest
relevant source, specification, and test context;
`deep_research_harness/CLAUDE.md` SHALL remain a thin import of that guide;
`deep_research_harness/README.md` SHALL introduce the product, provide an early human
reading map, and link to the docs index plus focused runtime-architecture,
local-operations, and testing-and-evaluation documents. The Harness README SHALL not
duplicate those detailed references. `openspec/README.md` SHALL remain a short
navigation map that distinguishes native OpenSpec workflow surfaces, Change Guidance,
and project governance without duplicating their contents. `openspec/config.yaml`
SHALL provide concise OpenSpec-authoring context rather than a project manual. Exact
structural paths SHALL remain in the machine-readable structure registry, not in a
default coding-agent entry document.

Before its Reading Map, the Harness README SHALL publish one `## Entry Surfaces` table
with `Surface`, `Primary reader/user`, `Purpose`, `Actual composition`, and `Explicit
non-goal` columns. It SHALL let a reader distinguish the dedicated-Agent plus reflected
`deep_research` tool product route; the standalone operator CLI; the demo-TUI
visualizer; the zero-credential full-fake demonstrations; deterministic fixture-graph
verification; and the configured-fixture local workbench. The table SHALL identify the
operator CLI as a local operator surface, not a versioned product CLI; the demo TUI as
a visualizer, not a current primary-user TUI; full fake as presentation rather than
fixture-graph verification; and the local workbench as only the configured fixture
profile surface. It SHALL direct exact local commands to `docs/local-operations.md`,
composition and authority questions to `docs/runtime-architecture.md`, and
verification questions to `docs/testing-and-evaluation.md`, without copying their
detail into the README.

The deterministic Change Guidance checker SHALL use line count as the primary size
signal. It SHALL warn at 120 lines and reject more than 160 lines for
`deep_research_harness/AGENTS.md`, warn at 10 lines and reject more than 12 lines for
`deep_research_harness/CLAUDE.md`, warn at 140 lines and reject more than 180 lines for
`openspec/config.yaml`, and warn when `deep_research_harness/README.md` exceeds 200
lines without rejecting it. It SHALL require `## Reading Map` in the first 80 lines of
`deep_research_harness/README.md` and the stable docs-map links. The checker SHALL not
impose word-count quotas or claim that a line budget proves prose quality. (`DRC-006`)

#### Scenario: A coding-agent guide cannot silently become a handbook
- **WHEN** an edit makes `deep_research_harness/AGENTS.md` longer than 120 lines
- **THEN** Change Guidance governance emits an actionable warning, and it fails once
  the guide exceeds 160 lines while directing detail to the relevant authoritative
  source

#### Scenario: Human documentation remains discoverable without becoming default context
- **WHEN** a human or operator opens `deep_research_harness/README.md`
- **THEN** its first 80 lines include `## Reading Map` that routes setup, operation,
  architecture, testing, and coding work to their appropriate documents, and ordinary
  code changes need not load the rest of the README by default

#### Scenario: A first-time reader classifies an entry surface
- **WHEN** a first-time reader opens the Harness README to choose how to use Deep Research
- **THEN** the early `Entry Surfaces` table identifies every required surface with its
  reader, purpose, actual composition, and explicit non-goal before the reader needs a
  detailed operating or architecture reference

#### Scenario: Entry details stay with their focused owners
- **WHEN** a reader needs an exact command, a composition or authority explanation, or
  verification guidance after selecting an entry surface
- **THEN** the Harness README routes that question to local operations, runtime
  architecture, or testing and evaluation respectively without duplicating the focused
  document's detail

#### Scenario: Demo and verification routes are not conflated
- **WHEN** a reader compares the Harness README's full-fake, fixture-graph, demo-TUI,
  and workbench entries
- **THEN** it does not mistake full fake for fixture-graph verification, the demo TUI
  for a current primary-user TUI, or the configured fixture workbench for a general
  product surface

#### Scenario: A detailed human question opens one focused document
- **WHEN** a reader needs runtime architecture, local-operation, or test-evidence
  detail after opening the Harness README
- **THEN** the Reading Map and docs index route it to one named focused document
  without requiring the Harness README to duplicate the other two references

#### Scenario: OpenSpec root navigation preserves authority boundaries
- **WHEN** a contributor opens `openspec/README.md`
- **THEN** it can distinguish native workflow files, Change Guidance, and governance
  without treating the README as a specification, path registry, or runtime authority

#### Scenario: OpenSpec context stays a route rather than a reference manual
- **WHEN** an OpenSpec author starts a new Deep Research change
- **THEN** `openspec/config.yaml` supplies the product boundary, truth discipline, and
  pointers needed to choose an owning spec and Focus Card without automatically
  injecting exhaustive DeerFlow/runtime facts or historical design material

### Requirement: Change Guidance policies preserve source-of-truth discipline and bounded recovery

The Change Guidance index SHALL route focused policies from its single nested
`policies/` directory for authority/projections and control/recovery. Those policies
SHALL direct changes to use the existing owner of checkpointed control state, evidence
ledger, sandbox content, typed result, or external contract; they SHALL reject shadow
control records, silent fallback, unbounded retries, and invented recovery actions.
The policy directory SHALL not have a second index, infer applicability, or grant
runtime authority. A policy that needs to alter an owning contract SHALL require a
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
- **WHEN** a contributor opens a policy directly from
  `openspec/change-guidance/policies/`
- **THEN** its trigger guides the contributor back through the Change Guidance index
  and does not create a second route, runtime controller, or policy applicability
  inference mechanism

### Requirement: Control-placement guidance is cross-cutting and non-authoritative

Deep Research Change Guidance SHALL route `control-placement` from the canonical
`change-guidance/policies/` directory for a change that adds or changes a gate,
validator, readiness check, candidate admission, retry/fallback/recovery, next-action
diagnostic, durable control fact, checkpoint/state writer, or cognitive/control
boundary between a Node Agent, a human decision, and a deterministic owner. The sole
Change Guidance index SHALL classify it as cross-cutting review guidance alongside the
other routed policies. It SHALL distinguish the policy from Change Guidance routing,
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
- **THEN** the Change Guidance index identifies `control-placement` as the focused
  cross-cutting review policy without treating the policy as runtime authority

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
names, or `none: <short rationale>` when no review policy applies. A proposal
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

The deterministic Change Guidance checker SHALL validate only canonical policy
lookup, exact guidance/policy member availability, Focus Card field shape, conditional
record shape, closed posture values, and the `human-decision` policy combination. It
SHALL not infer whether a proposal ought to select the policy, inspect source code,
judge the truth of a review row, or grant runtime authority. (`DRC-009`)

#### Scenario: A complete selected control-placement review is accepted
- **WHEN** an active proposal selects `control-placement` and supplies one or more
  complete rows with valid postures in the exact table format
- **THEN** the Change Guidance checker accepts its control-placement record while
  preserving the proposal's separate selected-review validation

#### Scenario: A malformed selected control-placement review fails closed
- **WHEN** an active proposal selects `control-placement` but the canonical policy is
  unavailable, the Focus Card field is malformed, the review is missing, its header
  differs, a cell is empty, or a posture is not closed
- **THEN** the Change Guidance checker reports deterministic conformance failure
  without attempting to infer or repair the missing semantic decision

#### Scenario: Human-decision posture requires the existing interaction review
- **WHEN** a selected control-placement review contains a `human-decision` row but
  `human-interaction-integrity` is absent from Triggered review policies
- **THEN** the Change Guidance checker rejects the proposal while leaving the owning
  human interaction contract responsible for any actual input schema, control, state
  effect, or route

#### Scenario: Existing conditional reviews remain distinct
- **WHEN** an active proposal selects control-placement together with
  `node-agent-workflow-integrity` or `workflow-outcome-review`
- **THEN** the Change Guidance checker requires every corresponding review record and
  does not treat the Control Placement Review as a substitute for candidate handoff or
  failure/recovery behavior

#### Scenario: Archived proposals remain historical records
- **WHEN** the Change Guidance migration is applied to the active planning home
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
agent confirms that the selected proposal declares `control-placement`. Apply
guidance SHALL direct the current agent to re-read the selected change's review
context and turn an actionable finding into an ordinary task. Archive guidance SHALL
direct the current agent to review the selected change's actual boundary, unresolved
tasks, and existing deterministic evidence before describing closeout.

When a change uses the delivered selected-change closeout-evidence capability, the
authoring route SHALL identify
`openspec/governance/closeout-evidence/selected_change_closeout.py` as its separate,
caller-declared and Git-verified boundary command. It SHALL state that the resulting
record is non-authoritative and that operation guidance remains advisory: neither
surface executes commands, creates or completes tasks, infers a finding, validates
semantic quality, nor blocks a native OpenSpec operation. (`DRC-010`)

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

### Requirement: Operation-guidance integration evidence stays bounded

The project SHALL retain deterministic, local evidence for the OpenSpec operation
guidance contract and for the selected-change boundary that the closeout-evidence
capability consumes. The evidence SHALL cover configured guidance delivery, absence,
and fresh config-read behavior; the supported native archive path and observable side
effects; selected-change committed-range verification; historical replay through the
finding-to-task/resume loop; and the narrow input facts that the closeout-evidence
capability may consume. It SHALL preserve failures or unknowns as probe results rather
than treating advisory text or a review record as a fail-closed guarantee. The
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
