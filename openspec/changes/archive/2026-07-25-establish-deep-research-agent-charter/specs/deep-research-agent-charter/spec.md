> req: DRC-001, DRC-002, DRC-003, DRC-004, DRC-005, DRC-006

## ADDED Requirements

### Requirement: A canonical Deep Research Agent Charter is discoverable

The project SHALL maintain `openspec/governance/agent-charter/` as the permanent
home for the Deep Research Agent Charter. Its index SHALL route contributors to a
single relevant policy and SHALL distinguish durable charter principles, focused
policies, owning capability specifications, scoped operational procedures, and
current runtime facts. The charter and every policy SHALL state that they are
design/admission guidance and do not create runtime authority. (`DRC-001`,
`DRC-005`)

#### Scenario: Contributor routes a local change without scanning the repository
- **WHEN** a contributor begins a Deep Research change affecting one owned module
- **THEN** the charter index identifies the local-context policy and directs the
  contributor to the owning capability specification and local evidence seam rather
  than requiring an undifferentiated read of root DeerFlow documentation

#### Scenario: A behavior proposal is placed in its owning contract
- **WHEN** a proposed policy would add a lifecycle action, state field, graph route,
  permission, or provider behavior
- **THEN** the charter index directs the change to an owning capability delta and
  the policy does not claim to establish that behavior by itself

### Requirement: The module guide establishes a primary-module focus gate

The human-authored beginning of `agent/AGENTS.md` SHALL contain a concise
primary-module focus gate before the generated structure block. It SHALL identify
`agent/` as the Deep Research product boundary, link to the charter index, route a
contributor to one primary causal module, and require ordinary work to start with
that module's active capability specification and lowest responsible evidence seam.
It SHALL require adjacent modules and public DeerFlow interfaces to be named before
they are expanded into scope, together with a named interface, authority,
compatibility, or observed-failure question that justifies the expansion. It SHALL
reject general repository orientation, speculative future relevance, and upstream
implementation browsing as sufficient reasons to expand scope. When ownership remains
unclear after the local spec, implementation, and evidence seam, it SHALL direct the
contributor to clarify the Focus Card rather than scan unrelated host code.
`agent/CLAUDE.md` SHALL be a thin Claude Code compatibility entrypoint that imports
the authoritative local `AGENTS.md` rather than copying or overriding its guidance.
Root `AGENTS.md` and `CLAUDE.md` remain upstream constraints and are not modified by
this charter. (`DRC-002`)

#### Scenario: A source change selects bounded context
- **WHEN** a contributor changes a file under `agent/src/deerflow_deep_research/`
- **THEN** the guide directs it to one causal owner and relevant test before any
  broader source inspection, and treats a DeerFlow API or adjacent layer as an
  explicit contract only when the change needs it

#### Scenario: Speculative context expansion is not admitted
- **WHEN** a contributor cannot name an interface, authority, compatibility, or
  observed-failure question for another module or host source
- **THEN** the local focus gate directs it to continue from the primary module or
  clarify ownership, rather than browse `backend/`, `frontend/`, root material, or
  sibling changes for general orientation

#### Scenario: Root guidance remains outside the charter migration
- **WHEN** the charter governance check runs
- **THEN** it validates the downstream module-guide focus gate without requiring an
  edit to repository-root `AGENTS.md` or `CLAUDE.md`

#### Scenario: Claude Code receives the same local focus gate
- **WHEN** Claude Code begins a change from `agent/`
- **THEN** `agent/CLAUDE.md` imports the authoritative `AGENTS.md`, so it receives
  the same primary-module routing, context-expansion exclusions, and Focus Card rule
  without a copied local instruction set

### Requirement: Contributor entry documents remain bounded information maps

The charter SHALL include an information-map policy that assigns distinct roles to
`agent/AGENTS.md`, `agent/CLAUDE.md`, `agent/README.md`, the task-scoped
`agent/docs/` map, and `openspec/config.yaml`. `agent/AGENTS.md` SHALL route ordinary
coding work to the smallest relevant source, specification, and test context;
`agent/CLAUDE.md` SHALL remain a thin import of that guide; `agent/README.md` SHALL
introduce the product, provide an early human reading map, and link to the docs index
plus focused runtime-architecture, local-operations, and testing-and-evaluation
documents. The root README SHALL not duplicate those detailed references.
`openspec/config.yaml` SHALL provide concise OpenSpec-authoring context rather than a
project manual. Exact structural paths SHALL remain in the machine-readable structure
registry, not in a default coding-agent entry document.

The deterministic charter checker SHALL use line count as the primary size signal. It
SHALL warn at 120 lines and reject more than 160 lines for `agent/AGENTS.md`, warn at
10 lines and reject more than 12 lines for `agent/CLAUDE.md`, warn at 140 lines and
reject more than 180 lines for `openspec/config.yaml`, and warn when
`agent/README.md` exceeds 200 lines without rejecting it. It SHALL require
`## Reading Map` in the first 80 lines of `agent/README.md` and the stable docs-map
links. The checker SHALL not impose word-count quotas or claim that a line budget
proves prose quality. (`DRC-006`)

#### Scenario: A coding-agent guide cannot silently become a handbook
- **WHEN** an edit makes `agent/AGENTS.md` longer than 120 lines
- **THEN** charter governance emits an actionable warning, and it fails once the
  guide exceeds 160 lines while directing detail to the relevant authoritative source

#### Scenario: Human documentation remains discoverable without becoming default context
- **WHEN** a human or operator opens `agent/README.md`
- **THEN** its first 80 lines include `## Reading Map` that routes setup, operation,
  architecture, testing, and coding work to their appropriate documents, and ordinary
  code changes need not load the rest of the README by default

#### Scenario: A detailed human question opens one focused document
- **WHEN** a reader needs runtime architecture, local-operation, or test-evidence
  detail after opening the root README
- **THEN** the Reading Map and docs index route it to one named focused document
  without requiring the root README to duplicate the other two references

#### Scenario: OpenSpec context stays a route rather than a reference manual
- **WHEN** an OpenSpec author starts a new Deep Research change
- **THEN** `openspec/config.yaml` supplies the product boundary, truth discipline,
  and pointers needed to choose an owning spec and Focus Card without automatically
  injecting exhaustive DeerFlow/runtime facts or historical design material

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
(`DRC-004`)

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

### Requirement: Charter policies preserve source-of-truth discipline and bounded recovery

The charter SHALL include focused policies for authority/projections and
control/recovery. They SHALL direct changes to use the existing owner of checkpointed
control state, evidence ledger, sandbox content, typed result, or external contract;
they SHALL reject shadow control records, silent fallback, unbounded retries, and
invented recovery actions. A policy that needs to alter an owning contract SHALL
require a corresponding capability change. (`DRC-005`)

#### Scenario: A diagnostic remains an observation
- **WHEN** a change retains a diagnostic summary or event record for inspection
- **THEN** the policy directs it to remain a bounded projection and preserves the
  owning checkpoint or result contract as the only lifecycle authority

#### Scenario: A retry policy has a named owner and bound
- **WHEN** a change proposes automatic recovery from an external failure
- **THEN** the policy requires the owning phase or contract to state the closed
  retryable category, invocation bound, terminal disposition, and nearest legal
  action instead of adding a presentation-layer retry loop
