> req: DRC-001, DRC-002, DRC-003, DRC-004, DRC-005, DRC-006, DRC-007, DRC-008, DRC-009, DRC-010, DRC-011, DRC-012, DRC-013, DRC-014

## MODIFIED Requirements

### Requirement: Contributor entry documents remain bounded information maps

Change Guidance SHALL include an information-map policy that assigns distinct roles
to
`deep_research_harness/AGENTS.md`, `deep_research_harness/CLAUDE.md`,
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
visualizer; the zero-credential fixture-graph demonstrations; deterministic fixture-graph
verification; and the configured-fixture local workbench. The table SHALL identify the
operator CLI as a local operator surface, not a versioned product CLI; the demo TUI as
a visualizer, not a current primary-user TUI; the fixture-graph demonstration as
presentation rather than research verification; and the local workbench as only the
configured fixture profile surface.
It SHALL direct exact local commands to `docs/local-operations.md`, composition and
authority questions to `docs/runtime-architecture.md`, and verification questions to
`docs/testing-and-evaluation.md`, without copying their detail into the README.

The deterministic Change Guidance checker SHALL use line count as the primary size signal. It
SHALL warn at 120 lines and reject more than 160 lines for
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
- **THEN** its first 80 lines include `## Reading Map` that routes setup, operation, architecture, testing, and coding work to their appropriate documents, and ordinary code changes need not load the rest of the README by default

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
- **WHEN** a reader compares the Harness README's fixture-graph, demo-TUI,
  and workbench entries
- **THEN** it does not mistake a fixture-graph demonstration for research verification, the demo TUI
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
- **THEN** `openspec/config.yaml` supplies the product boundary, truth discipline, and pointers needed to choose an owning spec and Focus Card without automatically injecting exhaustive DeerFlow/runtime facts or historical design material
