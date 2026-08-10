> req: DRC-002, DRC-004

## MODIFIED Requirements

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
