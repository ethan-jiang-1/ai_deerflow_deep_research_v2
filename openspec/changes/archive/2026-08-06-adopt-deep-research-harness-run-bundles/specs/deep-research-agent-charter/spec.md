> req: DRC-002, DRC-006, DRC-011

## ADDED Requirements

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
modified by this charter. (`DRC-002`)

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

#### Scenario: A detailed human question opens one focused document
- **WHEN** a reader needs runtime architecture, local-operation, or test-evidence detail after opening the root README
- **THEN** the Reading Map and docs index route it to one named focused document without requiring the root README to duplicate the other two references

#### Scenario: OpenSpec context stays a route rather than a reference manual
- **WHEN** an OpenSpec author starts a new Deep Research change
- **THEN** `openspec/config.yaml` supplies the product boundary, truth discipline, and pointers needed to choose an owning spec and Focus Card without automatically injecting exhaustive DeerFlow/runtime facts or historical design material
