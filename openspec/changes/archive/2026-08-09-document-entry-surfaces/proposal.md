## Why

The root README distinguishes several local commands, but its current entry table does
not give a first-time reader enough information to choose the product route, a local
operator surface, a demo visualizer, or a deterministic verification route. The
previous stages have established those contracts; this change makes their documented
entry points scannable without turning the README into a second operations manual.

## What Changes

- Replace the shallow root-README entry table with an early `Entry Surfaces` map that
  identifies each reader, purpose, actual composition, and explicit non-goal.
- Route exact commands to local operations, composition and authority questions to
  runtime architecture, and verification questions to the testing reference rather
  than duplicating those documents.
- Distinguish the dedicated-Agent/reflected-tool product route from the standalone
  operator CLI, which is not a versioned product CLI; the demo-TUI visualizer;
  full-fake presentation; fixture-graph verification; and the configured-fixture local
  workbench.
- Add deterministic documentation-contract evidence for the table's required routes,
  wording, and non-goal boundaries while preserving existing command evidence.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `deep-research-agent-charter`: Require the human README information map to present
  the supported entry surfaces and route each reader to the existing detail owner
  without becoming a second command, runtime, or testing authority.

## Impact

- Primary module: `deep_research_harness/README.md`, with focused static documentation
  contracts in the existing Harness test suite.
- Adjacent documentation contracts: `docs/local-operations.md` answers exact local
  command use; `docs/runtime-architecture.md` answers composition and lifecycle
  authority; `docs/testing-and-evaluation.md` answers deterministic and supplemental
  verification posture.
- The change consumes the accepted current behavior from the archived Stage 1--4
  changes, including their final entry-environment evidence, without treating archived
  material or the README as a runtime authority.
- No package behavior, command grammar, graph route, profile, provider, public tool,
  DeerFlow framework, `backend/`, or `frontend/` behavior changes.

## Change Focus

- **Primary module / causal owner:** `deep_research_harness/README.md`, the human
  product and operator entry map that selects the next focused document without owning
  command execution, composition, lifecycle state, or verification truth.
- **Question:** How can the README let a first-time reader distinguish the current
  product route, standalone operator CLI that is not a versioned product CLI, demo
  visualizer, full-fake and fixture-graph verification routes, and configured local
  workbench in one scan, while delegating details to their existing owners?
- **Necessary adjacent/external contracts:** `deep-research-agent-charter` answers the
  bounded human-information-map requirement; `docs/local-operations.md` answers exact
  operator commands; `docs/runtime-architecture.md` answers actual composition and
  authority boundaries; `docs/testing-and-evaluation.md` answers verification meaning;
  the archived Stage 1--4 changes provide historical evidence references but do not
  define current behavior.
- **Evidence seam:** static README/document-contract tests verify the early table's
  required columns, named entry surfaces, non-goal language, and links to the three
  focused document owners; existing command contracts continue to verify the exact
  command strings that the map routes readers toward.
- **Not in scope:** changing any command, model/provider requirement, full-fake or
  fixture recipe, public tool authority, Run Bundle lifecycle, workbench scope, docs'
  detailed operational content, or DeerFlow source.
- **Triggered review policies:** agent-information-map
