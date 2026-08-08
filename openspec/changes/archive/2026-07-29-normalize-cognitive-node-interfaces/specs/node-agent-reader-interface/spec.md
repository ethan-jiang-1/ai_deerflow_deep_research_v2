> req: NRI-001, NRI-002, NRI-003

## MODIFIED Requirements

### Requirement: LLM-bearing nodes provide node-local, non-runtime reader interfaces

The Wave2 synthesis, HITL1, topic-planning, Wave0, Wave1, and targeted-evidence
node packages SHALL each colocate one `workflow.md` reader projection. Each
projection SHALL state that code, typed contracts, approved specs, and tests remain
the authority, and SHALL not be loaded, rendered, or interpreted by the runtime. It
SHALL identify that node's bounded cognitive job and distinguish it from the
deterministic admission, materialization, human-interaction, ledger, gate, and route
owners relevant to that package. It SHALL direct readers to the current owning
source/specification/test surfaces rather than reproduce local implementation as a
second line-by-line workflow.

The six projections SHALL participate in the all-node cognitive-node-interface
inventory and its static validation. This shared check SHALL validate reader
coverage/shape only; it does not convert any projection into runtime configuration,
an executable Markdown schema, or a second behavior authority.

#### Scenario: Reader opens a package-local projection
- **WHEN** a maintainer begins an investigation from any one of the six
  LLM-bearing node packages
- **THEN** the maintainer can identify the bounded model job, the applicable
  deterministic owners, and the authoritative source/specification/test surfaces
  without treating `workflow.md` as runtime configuration or a second behavior
  authority

#### Scenario: Existing readers enter the shared inventory
- **WHEN** the all-node reader inventory is checked
- **THEN** the six existing projections are checked alongside five non-active-current
  node projections without inferring a model branch or new runtime behavior

## ADDED Requirements

### Requirement: Package-local reader obligations coexist with the cognitive-node interface

node-agent-reader-interface SHALL remain the owner of the six package-local reader
obligations in NRI-001 and NRI-002. cognitive-node-interface SHALL own their common
product-responsibility-first shape and the complete eleven-node inventory. Neither
capability is runtime configuration or execution authority; current direct branch
discovery cannot reduce the reader population to six documents, and a deferred or
conditional responsibility cannot claim an active model loop.

#### Scenario: Existing detailed navigation remains available
- **WHEN** a maintainer investigates an active HITL1, topic-planning, Wave0, Wave1,
  Wave2, or targeted-evidence symptom
- **THEN** the projection retains NRI-002's exact source and deterministic-seam
  navigation while presenting the cognitive-node identity fields first

