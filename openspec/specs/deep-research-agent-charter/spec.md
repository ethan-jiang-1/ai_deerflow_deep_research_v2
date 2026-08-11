# Deep Research Agent Charter Specification

> req: DRC-001, DRC-002, DRC-003, DRC-004, DRC-005, DRC-006, DRC-007, DRC-008, DRC-009, DRC-010, DRC-011

## Purpose

Defines the permanent design/admission charter, bounded contributor context, and
human/AI-facing information-map rules for the downstream Deep Research product.
## Requirements
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
- **THEN** the charter index directs the change to an owning capability delta and
  the policy does not claim to establish that behavior by itself

### Requirement: The module guide establishes a primary-module focus gate

The human-authored beginning of `deep_research_harness/AGENTS.md` SHALL contain a
concise primary-module focus gate before the generated structure block. It SHALL
identify `deep_research_harness/` as the Deep Research product boundary, link to the
charter index, route a contributor to one primary causal module, and require ordinary
work to start with that module's active capability specification and lowest responsible
evidence seam. It SHALL require adjacent modules and public DeerFlow interfaces to be
named before they are expanded into scope, together with a named interface, authority,
compatibility, or observed-failure question that justifies the expansion. It SHALL
reject general repository orientation, speculative future relevance, and upstream
implementation browsing as sufficient reasons to expand scope. When ownership remains
unclear after the local spec, implementation, and evidence seam, it SHALL direct the
contributor to clarify the Focus Card rather than scan unrelated host code.
`deep_research_harness/CLAUDE.md` SHALL be a thin Claude Code compatibility entrypoint
that imports the authoritative local `AGENTS.md` rather than copying or overriding its
guidance. Root `AGENTS.md` and `CLAUDE.md` remain upstream constraints and are not
modified by this charter. The local-context policy SHALL route a node-behavior
symptom first to the node's cognitive-program seam — its capability Markdown, prompt
builders, model-visible context, and structured feedback — before a deterministic
parser, materializer, gate, route, or bridge edit is admitted as the first
modification. A deterministic-guardrail or wiring edit for a node-behavior symptom
SHALL record the seam classification that shows the cognitive-program seam was
considered first. (`DRC-002`)

#### Scenario: A source change selects bounded context
- **WHEN** a contributor changes a file under `deep_research_harness/src/deerflow_deep_research/`
- **THEN** the guide directs it to one causal owner and relevant test before any broader source inspection, and treats a DeerFlow API or adjacent layer as an explicit contract only when the change needs it

#### Scenario: Speculative context expansion is not admitted
- **WHEN** a contributor cannot name an interface, authority, compatibility, or observed-failure question for another module or host source
- **THEN** the local focus gate directs it to continue from the primary module or clarify ownership, rather than browse `backend/`, `frontend/`, root material, or sibling changes for general orientation

#### Scenario: Root guidance remains outside the charter migration
- **WHEN** the charter governance check runs
- **THEN** it validates the downstream module-guide focus gate without requiring an edit to repository-root `AGENTS.md` or `CLAUDE.md`

#### Scenario: Claude Code receives the same local focus gate
- **WHEN** Claude Code begins a change from `deep_research_harness/`
- **THEN** `deep_research_harness/CLAUDE.md` imports the authoritative `AGENTS.md`, so it receives the same primary-module routing, context-expansion exclusions, and Focus Card rule without a copied local instruction set

#### Scenario: A node-behavior symptom routes to the cognitive program first
- **WHEN** a contributor starts from a wrong role, malformed candidate, or
  misaligned feedback symptom in an LLM-Bearing Node
- **THEN** the local-context policy directs the first inspection to the node's
  capability Markdown, prompt builder, and feedback path, and does not admit a
  parser, gate, route, or bridge edit as the first modification without a recorded
  seam classification

### Requirement: Contributor entry documents remain bounded information maps

The charter SHALL include an information-map policy that assigns distinct roles to
`deep_research_harness/AGENTS.md`, `deep_research_harness/CLAUDE.md`,
`deep_research_harness/README.md`, the task-scoped `deep_research_harness/docs/` map,
and `openspec/config.yaml`. `deep_research_harness/AGENTS.md` SHALL route ordinary
coding work to the smallest relevant source, specification, and test context;
`deep_research_harness/CLAUDE.md` SHALL remain a thin import of that guide;
`deep_research_harness/README.md` SHALL introduce the product, provide an early human
reading map, and link to the docs index plus focused runtime-architecture,
local-operations, and testing-and-evaluation documents. The root README SHALL not
duplicate those detailed references. `openspec/config.yaml` SHALL provide concise
OpenSpec-authoring context rather than a project manual. Exact structural paths SHALL
remain in the machine-readable structure registry, not in a default coding-agent entry
document.

Before its Reading Map, the root README SHALL publish one `## Entry Surfaces` table
with `Surface`, `Primary reader/user`, `Purpose`, `Actual composition`, and `Explicit
non-goal` columns. It SHALL let a reader distinguish the dedicated-Agent plus reflected
`deep_research` tool product route; the standalone operator CLI; the demo-TUI
visualizer; the zero-credential full-fake demonstrations; deterministic fixture-graph
verification; and the configured-fixture local workbench. The table SHALL identify the
operator CLI as a local operator surface, not a versioned product CLI; the demo TUI as
a visualizer, not a current primary-user TUI; full fake as presentation rather than
fixture-graph verification; and the local workbench as only the configured fixture
profile surface.
It SHALL direct exact local commands to `docs/local-operations.md`, composition and
authority questions to `docs/runtime-architecture.md`, and verification questions to
`docs/testing-and-evaluation.md`, without copying their detail into the README.

The deterministic charter checker SHALL use line count as the primary size signal. It
SHALL warn at 120 lines and reject more than 160 lines for
`deep_research_harness/AGENTS.md`, warn at 10 lines and reject more than 12 lines for
`deep_research_harness/CLAUDE.md`, warn at 140 lines and reject more than 180 lines for
`openspec/config.yaml`, and warn when `deep_research_harness/README.md` exceeds 200
lines without rejecting it. It SHALL require `## Reading Map` in the first 80 lines of
`deep_research_harness/README.md` and the stable docs-map links. The checker SHALL not
impose word-count quotas or claim that a line budget proves prose quality. (`DRC-006`)

#### Scenario: A coding-agent guide cannot silently become a handbook
- **WHEN** an edit makes `deep_research_harness/AGENTS.md` longer than 120 lines
- **THEN** charter governance emits an actionable warning, and it fails once the guide exceeds 160 lines while directing detail to the relevant authoritative source

#### Scenario: Human documentation remains discoverable without becoming default context
- **WHEN** a human or operator opens `deep_research_harness/README.md`
- **THEN** its first 80 lines include `## Reading Map` that routes setup, operation, architecture, testing, and coding work to their appropriate documents, and ordinary code changes need not load the rest of the README by default

#### Scenario: A first-time reader classifies an entry surface
- **WHEN** a first-time reader opens the root README to choose how to use Deep Research
- **THEN** the early `Entry Surfaces` table identifies every required surface with its
  reader, purpose, actual composition, and explicit non-goal before the reader needs a
  detailed operating or architecture reference

#### Scenario: Entry details stay with their focused owners
- **WHEN** a reader needs an exact command, a composition or authority explanation, or
  verification guidance after selecting an entry surface
- **THEN** the README routes that question to local operations, runtime architecture, or
  testing and evaluation respectively without duplicating the focused document's detail

#### Scenario: Demo and verification routes are not conflated
- **WHEN** a reader compares the README's full-fake, fixture-graph, demo-TUI, and
  workbench entries
- **THEN** it does not mistake full fake for fixture-graph verification, the demo TUI
  for a current primary-user TUI, or the configured fixture workbench for a general
  product surface

#### Scenario: A detailed human question opens one focused document
- **WHEN** a reader needs runtime architecture, local-operation, or test-evidence detail after opening the root README
- **THEN** the Reading Map and docs index route it to one named focused document without requiring the root README to duplicate the other two references

#### Scenario: OpenSpec context stays a route rather than a reference manual
- **WHEN** an OpenSpec author starts a new Deep Research change
- **THEN** `openspec/config.yaml` supplies the product boundary, truth discipline, and pointers needed to choose an owning spec and Focus Card without automatically injecting exhaustive DeerFlow/runtime facts or historical design material

### Requirement: Participant outcomes serve people and AI consumers from shared facts

The charter's participant-outcomes policy SHALL require any capability change that
exposes a lifecycle outcome to people or another AI to derive its human-readable and
machine-readable projections from the same owning typed facts. The policy SHALL
require a comprehensible, legal next action for a human and stable bounded fields for
an AI consumer, while preserving redaction and without creating a universal runtime
schema. The owning capability specification SHALL define exact fields and behavior.
(`DRC-003`)

#### Scenario: A recoverable provider failure is described safely
- **WHEN** an owning capability exposes a retryable provider failure
- **THEN** its participant contract can communicate the closed failure category,
  owner/phase, retry disposition, safe diagnostic reference, and allowed action
  without exposing raw exception text, credentials, full URLs, prompt content, or
  claiming unavailable resume behavior

#### Scenario: A presentation projection cannot control the lifecycle
- **WHEN** a CLI, TUI, retained diagnostic, or another AI consumes a lifecycle
  projection
- **THEN** it receives the bounded projection from the owning result but cannot use
  that projection as a replacement checkpoint, transition authority, or permission

### Requirement: Active changes declare a bounded Focus Card

Every active OpenSpec change in this Deep Research planning home SHALL include a
`## Change Focus` section in its proposal with non-empty Primary module / causal
owner, Question, Necessary adjacent/external contracts, Evidence seam, and Not in scope
fields. The primary module / causal owner SHALL identify the smallest module that
owns the changed semantic decision; a presentation adapter alone is insufficient
when another module owns that decision. The change-admission policy SHALL require the
card before implementation. A non-`none` Necessary adjacent/external contracts entry
SHALL name the contract and the question it answers; it is not a list of potentially
useful places to browse. The deterministic charter checker SHALL reject a missing or
malformed card and required charter navigation/policy surfaces, including the stable
context-expansion gate anchors, but SHALL not infer semantic correctness from prose.
Every active proposal's Focus Card SHALL include a `Seam classification` field whose
value is exactly one of `cognitive-program`, `human-decision`,
`deterministic-guardrail`, or `wiring`, with a short rationale. The field names the
primary edit target of the change; it SHALL NOT be inferred from the first file
opened or from the presence or absence of a `run_agent` call. A `cognitive-program`
classification SHALL state the cognitive hypothesis and observable result that
justify the edit; `human-decision`, `deterministic-guardrail`, and `wiring` SHALL
name the deterministic owner that remains authoritative. The deterministic charter
checker SHALL reject a `Seam classification` that is missing, empty, outside the
closed value set, or lacks a short rationale, and SHALL NOT judge the semantic truth
of the classification. (`DRC-004`)

#### Scenario: Missing Focus Card fails governance
- **WHEN** an active proposal lacks one required Focus Card field
- **THEN** the charter checker fails with the proposal path and missing field before
  implementation can claim charter conformance

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
- **WHEN** an active proposal's Focus Card omits `Seam classification`, leaves it
  empty, uses a value outside the closed set, or supplies no rationale
- **THEN** the charter checker fails with the proposal path and missing or invalid
  field before implementation can claim charter conformance

#### Scenario: A cognitive-program classification carries its hypothesis
- **WHEN** a proposal classifies its seam as `cognitive-program` to adjust a node's
  capability policy, prompt composition, or feedback
- **THEN** the Focus Card records the bounded cognitive hypothesis and the
  observable result or evaluation that will show whether the edit worked, and names
  the deterministic owner that still admits the candidate

#### Scenario: A guardrail classification names the deterministic owner
- **WHEN** a proposal classifies its seam as `deterministic-guardrail` or `wiring`
  for an admission, gate, route, or evidence change
- **THEN** the Focus Card names the deterministic owner that remains authoritative
  and does not claim a cognitive quality improvement for the node

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

### Requirement: Workflow-affecting changes record a triggered outcome review

The Agent Charter SHALL provide a `workflow-outcome-review` policy for changes that
add or modify a model, tool, provider, worker, retry, terminal, diagnostic, or
lifecycle-projection path. `openspec/config.yaml` and its governance checker SHALL
require every active Deep Research proposal to record triggered charter policies in
its Change Focus. A proposal selecting `workflow-outcome-review` SHALL include a
bounded failure-outcome table naming the fact owner, recovery owner and bound,
terminal disposition, legal next action, and deterministic evidence seam. A proposal
selecting no policy SHALL state a short rationale. This record SHALL guide design and
review only; it SHALL not create runtime authority.

#### Scenario: A provider-recovery change is admitted with its outcome contract
- **WHEN** a proposal changes a phase's provider timeout or retry behavior
- **THEN** governance requires the workflow-outcome review record before the change
  is considered admission-complete

#### Scenario: A non-workflow documentation change remains bounded
- **WHEN** a proposal changes only human documentation and declares no triggered
  workflow policy with a rationale
- **THEN** governance accepts the bounded declaration without requiring a fabricated
  failure-outcome table

### Requirement: Human-interaction integrity is a routed recurring review policy

The charter SHALL route a focused human-interaction-integrity policy for a change that
adds or revises a human decision, semantic input, visible control, or interaction
recovery surface. The policy SHALL require reviewers to identify the semantic subject,
candidate interpretation authority, graph/action authority, visible legal controls,
adapter binding boundary, failure recovery, and lowest deterministic transcript seam.
It SHALL state that the policy is guidance only and that exact behavior belongs in an
owning capability specification. (`DRC-007`)

#### Scenario: An interaction change has a review route
- **WHEN** a contributor changes a human-input or visible-control surface
- **THEN** the charter index directs that contributor to the focused policy without
  making charter prose a runtime controller

### Requirement: Node-agent workflow changes carry a bounded integrity review

The Deep Research Agent Charter SHALL route a
`node-agent-workflow-integrity` policy for a change that adds, removes, or
materially changes a node's LLM-bearing cognitive role, node-local capability policy,
tool posture, output-admission boundary, repair semantics, or model/non-model
classification. The policy SHALL direct the change author to distinguish the
deterministic graph/node handler, bounded Node Agent, runtime bridge, and
parser/evaluator/materializer owners. It SHALL state that the policy creates no
runtime route, state writer, tool permission, model invocation, or recovery behavior;
those remain in an owning capability specification and executable contract.

When a proposal's `Triggered review policies` field includes
`node-agent-workflow-integrity`, the proposal SHALL contain exactly one
`## Node Agent Review` table with the following header, separator, and at least one
complete row:

```text
| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

Each `Classification` value SHALL be exactly `node-agent` or `no-agent`. The
deterministic charter checker SHALL reject a selected policy with a missing,
malformed, incomplete, or invalid-classification record. It SHALL not infer policy
applicability or judge the semantic truth of a review row. The OpenSpec authoring
context SHALL route node-agent changes to this policy without turning root
`config.yaml`, `openspec/config.yaml`, the review table, or a prompt projection into
runtime authority. (`DRC-008`)

#### Scenario: A node-agent capability change records its bounded handoff
- **WHEN** a proposal changes a node's LLM-bearing capability policy and selects
  `node-agent-workflow-integrity`
- **THEN** it contains one complete Node Agent Review row naming the bounded job,
  input authority boundary, tool enforcer, candidate-result admission owner, failure
  owner/bound, and deterministic evidence seam

#### Scenario: An intentionally deterministic node is explicitly classified
- **WHEN** a proposal changes a relevant node but retains deterministic execution
  and selects `node-agent-workflow-integrity`
- **THEN** its Node Agent Review row uses `no-agent` and names the bounded rationale
  without requiring a fabricated model capability

#### Scenario: An incomplete selected review fails closed
- **WHEN** an active proposal selects `node-agent-workflow-integrity` but omits the
  review, uses a different table header, leaves a required cell empty, or uses an
  unsupported classification
- **THEN** the charter checker fails before the proposal can claim governance
  conformance

#### Scenario: Role review and failure review remain distinct
- **WHEN** a proposal selects both `node-agent-workflow-integrity` and
  `workflow-outcome-review`
- **THEN** the charter checker requires both review records, preserving the existing
  failure/recovery table rather than treating role guidance as a recovery contract

#### Scenario: Governance does not grant runtime authority
- **WHEN** a reviewer reads a valid Node Agent Review record
- **THEN** the record identifies the owning capability and deterministic admission
  boundary but does not itself create a graph route, state write, tool permission,
  provider call, retry, or result acceptance

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
  handoff or the write/reload/direct-consumer chain rather than a hand-built
  consumer fixture or presentation-only assertion

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
agent confirms that the selected proposal declares `control-placement`. Apply
guidance SHALL direct the current agent to re-read the selected change's review
context and turn an actionable finding into an ordinary task. Archive guidance SHALL
direct the current agent to review the selected change's actual boundary, unresolved
tasks, and existing deterministic evidence before describing closeout.

When a change uses the delivered selected-change closeout-evidence capability, the
authoring route SHALL identify it as a separate, caller-declared and Git-verified boundary
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

### Requirement: Downstream agent entry documents route from the canonical Harness root

The bounded Deep Research coding guide, Claude compatibility entrypoint, README reading
map, focused documentation, and OpenSpec authoring route SHALL live and link beneath
`deep_research_harness/` after the structural move. They SHALL continue to direct an
agent to one primary owner, active spec/delta, and lowest responsible test seam without
turning the guide, public skill, SOUL, or diagnostic text into lifecycle authority. The
structure registry remains the exact path inventory, and agent instructions SHALL use
the canonical Harness/Run Bundle/`bundle_id` vocabulary without claiming recovery of a
deleted Bundle. (`DRC-011`)

#### Scenario: Coding agent starts from one canonical downstream guide
- **WHEN** a coding agent opens the downstream entry guide after the move
- **THEN** it reaches the Focus Gate and canonical structure locator under `deep_research_harness/` without following an old-root compatibility document
