> req: DRC-014

## ADDED Requirements

### Requirement: Deep Research product context is separately discoverable and non-authoritative

The project SHALL maintain `openspec/product/deep-research.md` as the sole canonical
OpenSpec entry for the properties that distinguish the Deep Research product from
other DeerFlow/LangGraph agent workflows. It SHALL be a concise product-context map:
it SHALL identify the research-specific question or outcome, evidence and uncertainty
posture, product-local workflow orientation, and the exact existing owners a reader
must open for product definitions, runtime facts, approved behavior, and proof.
The existing information-map policy and deterministic Change Guidance checker SHALL
warn at 60 lines and reject the map above 80 lines.

`openspec/README.md`, `openspec/config.yaml`, and the Change Guidance index SHALL
make the product route discoverable while retaining their bounded native-workflow,
authoring-context, and generic-policy roles. The product route SHALL not define or
override vocabulary owned by `deep_research_harness/CONTEXT.md`; required behavior
owned by an approved specification or active delta; current runtime facts owned by
code, typed contracts, and tests; or a node's exact authoring route owned by
`openspec/change-guidance/node-edit-map.md`. It SHALL not create a `platform/`
directory, a second glossary, a global authoring handbook, or runtime Markdown
configuration. (`DRC-014`)

#### Scenario: Reader finds Deep Research-specific orientation without loading generic guidance as a handbook
- **WHEN** a contributor needs to understand what makes this repository a Deep
  Research product rather than another agent workflow
- **THEN** `openspec/` routes the contributor to `product/deep-research.md`, which
  identifies the product-specific concerns and directs detailed questions to their
  existing authorities without copying those authorities' content

#### Scenario: Generic authoring route remains bounded
- **WHEN** a contributor opens the OpenSpec context, Change Guidance index, or a
  generic governance navigation document for a normal change
- **THEN** that entry keeps its native workflow, policy-routing, or checker-navigation
  role and links to product context only when Deep Research-specific orientation is
  needed, without becoming a product handbook

#### Scenario: Product context cannot claim product behavior or runtime authority
- **WHEN** the product-context document describes a research-specific concern
- **THEN** it routes the reader to the product glossary, owning capability contract,
  implementation, or evidence seam and does not claim to establish a node role,
  graph route, state write, model invocation, tool permission, recovery behavior, or
  current runtime fact

#### Scenario: Product context remains a reading map
- **WHEN** the product-context document grows beyond its concise navigation role
- **THEN** the Change Guidance checker warns at 60 lines and rejects it above 80 lines,
  directing detailed material to its existing owner rather than accepting a handbook
