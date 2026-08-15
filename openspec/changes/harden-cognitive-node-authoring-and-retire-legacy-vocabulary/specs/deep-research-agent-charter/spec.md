## ADDED Requirements

### Requirement: LLM-node authoring follows one current-only cognitive route

The project SHALL maintain `openspec/change-guidance/node-edit-map.md` as the compact,
current-only first read before a Coding Agent creates, changes, or reviews an
LLM-Bearing Node or direct model branch. The map, the Change Guidance root, and the
Harness coding guide SHALL route that work in this order: the Node Cognitive Control
Contract and capability policy; the prompt builder and model-visible context; structured
output, feedback, and repair; focused deterministic proof and applicable cognitive
evaluation; then the separate deterministic admission, materialization, ledger, gate,
and Python/LangGraph route owners.

The map SHALL make the cognitive responsibility, trusted/untrusted input boundary,
bounded method/tool posture, useful candidate and uncertainty standard, feedback/repair
loop, and deterministic handoff reviewable without becoming a runtime resource,
permission, state authority, route authority, or second behavior specification. For a
deterministic or human-decision change, the map SHALL require the author to name why no
cognitive program is the causal owner; it SHALL not require a fabricated prompt surface.
The deterministic Change Guidance contract SHALL reject a missing or demoted authoring
route. (`DRC-012`)

#### Scenario: Coding Agent starts an LLM-node change from cognition
- **WHEN** a Coding Agent begins to create, change, or review an LLM-Bearing Node
- **THEN** the Harness guide and Change Guidance root direct it to the node edit map
  before node implementation navigation, and the map supplies the ordered cognitive
  review route before deterministic handoff owners

#### Scenario: Deterministic work is not forced into a prompt change
- **WHEN** a Coding Agent changes a deterministic or human-decision node
- **THEN** the node edit map directs it to the actual typed, domain, or graph owner
  after recording why no cognitive program owns the decision, without requiring a
  model capability or prompt

#### Scenario: A missing authoring route fails governance
- **WHEN** the guided LLM-node authoring route is absent from the node edit map, the
  Change Guidance root, or the Harness guide
- **THEN** the deterministic Change Guidance contract rejects the missing route before
  the affected document can claim charter conformance

### Requirement: Tracked project language contains no retired external workflow labels

Every tracked project text surface, including source, tests, current specifications,
guidance, OpenSpec archive, and backlog records, SHALL use the current Deep
Research/LangGraph vocabulary and SHALL contain no retired external workflow label.
The project SHALL retain no checked-out imported workflow reference library. The
deterministic language guard SHALL prove a zero-literal tracked-file scan while keeping
the prohibited token construction confined to test-only fragments so a planted violation
remains detectable without leaving a residual literal in the working tree.

The guard SHALL preserve the factual decision, requirement identifier, path, date, and
recorded validation outcome of a retained archive or closed record; terminology cleanup
does not reclassify historical behavior or create a compatibility term. (`DRC-013`)

#### Scenario: A residual label in any tracked record fails
- **WHEN** a prohibited external workflow label is planted in a current document,
  source/test surface, archived change, or closed backlog record
- **THEN** the deterministic language guard rejects the repository and identifies the
  tracked surface that contains the residual

#### Scenario: Zero-literal scan retains a real negative control
- **WHEN** the tracked-file residual scan runs on the completed repository
- **THEN** it finds no prohibited literal, while the language contract still rejects a
  fixture that assembles and writes the prohibited token into a tracked surface

#### Scenario: Imported reference material is retired without changing facts
- **WHEN** the terminology migration completes
- **THEN** the imported workflow reference library is absent, retained archive/closed
  records use current terminology, and their completed decision/evidence facts remain
  readable without introducing an alias or second glossary
