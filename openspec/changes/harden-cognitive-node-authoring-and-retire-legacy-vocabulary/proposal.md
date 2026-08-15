## Why

Deep Research is a LangGraph application whose LLM-Bearing Nodes pair a Node Cognitive
Control Program with a Deterministic Control Boundary. Imported workflow vocabulary and
a too-small node edit map still let Coding Agents start from Python routing, parsing, or
tests and overlook the capability, prompt/context, feedback, and evaluation work that
actually shapes model behavior.

The project needs one current language and one enforced authoring route: every tracked
file must use the Deep Research/LangGraph model, and every Coding Agent must read the
node edit map before creating, changing, or reviewing an LLM-Bearing Node.

## What Changes

- Remove retired external workflow terminology from every tracked source, test,
  specification, OpenSpec archive, and backlog record; delete the non-authoritative
  imported workflow reference library rather than preserving it as a competing design
  input.
- Extend the current-language guard so zero literal residuals are checked across the
  complete working tree while planted violations remain detectable through test-only
  assembled tokens.
- Make `openspec/change-guidance/node-edit-map.md` the compact, current-only authoring
  gate for writing, changing, and reviewing an LLM-Bearing Node, with the required
  cognitive-first reading order and a clear Python/LangGraph control boundary.
- Route the Harness coding guide and Change Guidance root to that gate before LLM-node
  code navigation begins.
- Require the six LLM-Bearing Node reader projections to expose exact cognitive-program,
  prompt/context, feedback/repair, proof/evaluation, and deterministic-handoff routes
  without turning those projections into runtime configuration or duplicate specs.
- Audit every direct model-branch capability against the existing prompt catalog and
  cognitive-program evidence board, correcting only missing authoring/proof navigation;
  this change does not change a branch's runtime role, prompt semantics, tool posture,
  result, route, or lifecycle behavior.

## Change Focus

- **Primary module / causal owner:** `deep-research-agent-charter` -- it owns the contributor authoring route, current vocabulary, and guidance/entry-document boundaries.
- **Seam classification:** wiring -- this change aligns contributor routing, reader projections, documentation, and deterministic documentation guards; existing node handlers, prompt renderer, bridge, parser, materializer, gate, and graph remain the runtime owners.
- **Question:** How can every Coding Agent be forced onto the cognitive-program-first authoring path for LLM-Bearing Nodes while every tracked project record converges on current Deep Research/LangGraph terminology?
- **Necessary adjacent/external contracts:** `node-agent-reader-interface` -- which exact routes must six package-local reader projections expose?; `node-prompt-catalog` -- which existing canonical prompt/context source proves a reader link reaches the real rendered composition?; `cognitive-program-evidence` -- which existing twenty-branch ledger proves the complete capability/proof inventory?; `deerflow`: none -- no upstream interface, source, or behavior changes.
- **Evidence seam:** `test_node_language_contract.py`, `test_node_workflow_reader_interface.py`, Change Guidance governance contracts, link/inventory fixtures, and a tracked-file residual scan.
- **Not in scope:** runtime prompt or capability semantic changes; model, tool, bridge, parser, materializer, gate, route, state, lifecycle, or provider behavior; new LLM controllers; DeerFlow source; a second glossary or authoring handbook.
- **Triggered review policies:** local-context, agent-information-map, change-admission

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `deep-research-agent-charter`: Require a current-only, cognitively ordered LLM-node authoring route from the Harness guide and Change Guidance root; require a complete tracked-surface terminology guard without archive/backlog exceptions.
- `node-agent-reader-interface`: Require the six LLM-Bearing Node reader projections to direct cognitive work through capability, prompt/context, feedback/repair, and proof/evaluation before deterministic handoff owners.

## Impact

- Affected guidance and entry maps: `openspec/change-guidance/`,
  `deep_research_harness/AGENTS.md`, and `openspec/README.md` only where the canonical
  authoring route must be visible.
- Affected non-runtime node reader projections: the six LLM-Bearing Node
  `graph/nodes/*/workflow.md` files and their contract tests.
- Affected terminology records: current docs/specs/tests plus committed OpenSpec archive
  and backlog records; the imported `_backlog/_reference/dpt/` library is removed after
  link verification.
- No public API, persisted data, runtime behavior, or DeerFlow gitlink changes.
