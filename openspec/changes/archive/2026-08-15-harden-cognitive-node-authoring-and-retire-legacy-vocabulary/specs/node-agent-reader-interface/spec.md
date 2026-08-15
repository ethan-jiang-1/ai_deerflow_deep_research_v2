## MODIFIED Requirements

### Requirement: LLM-bearing nodes provide node-local, non-runtime reader interfaces

The Wave2 synthesis, HITL1, topic-planning, Wave0, Wave1, targeted-evidence, readiness,
and final-delivery node packages SHALL each colocate one `workflow.md` reader
projection. Each projection SHALL state that code, typed contracts, approved
specifications, and tests remain the authority, and SHALL not be loaded, rendered, or
interpreted by the runtime. It SHALL identify that node's bounded cognitive job and
distinguish it from the deterministic admission, materialization, human-interaction,
ledger, gate, and route owners relevant to that package. It SHALL direct readers to the
current owning source/specification/test surfaces rather than reproduce local
implementation as a second line-by-line workflow.

The eight projections SHALL participate in cognitive-node-interface's all-node
inventory and static shape validation. That validation does not make Markdown runtime
configuration, an executable schema, or a second behavior authority.

#### Scenario: Reader opens a package-local projection
- **WHEN** a maintainer begins an investigation from any one of the eight LLM-bearing
  node packages
- **THEN** the maintainer can identify the bounded model job, the applicable
  deterministic owners, and the authoritative source/specification/test surfaces
  without treating `workflow.md` as runtime configuration or a second behavior
  authority

#### Scenario: Existing projections enter the shared inventory
- **WHEN** all-node reader validation runs
- **THEN** the eight LLM-bearing projections are checked alongside bootstrap, HITL2,
  and rerun without inferring a model branch or new runtime behavior

### Requirement: Package-local obligations coexist with the cognitive-node interface

This capability SHALL retain ownership of NRI-001/NRI-002's eight LLM-bearing
package-local reader obligations. cognitive-node-interface SHALL own their fixed
identity shape and the eleven-node inventory. Neither capability is runtime
configuration or execution authority.

#### Scenario: Detailed active-node navigation remains available
- **WHEN** a maintainer investigates an existing active node symptom
- **THEN** its card retains exact source and deterministic-seam navigation while
  presenting cognitive-node identity fields first

## ADDED Requirements

### Requirement: LLM-node reader projections expose the cognitive authoring order

The Wave2 synthesis, HITL1, topic-planning, Wave0, Wave1, targeted-evidence, readiness,
and final-delivery `workflow.md` reader projections SHALL identify the ordered route a
Coding Agent uses before changing model-bearing behavior: the Node Cognitive Control
Contract and local capability; prompt builder and model-visible context; structured
output, feedback, and repair; focused deterministic proof and applicable cognitive
evaluation; and the separate deterministic admission, materialization, ledger, gate,
and route owners.

Each projection SHALL retain its current local symptom navigation and non-runtime
boundary. It SHALL link to the exact local sources that answer its route rather than
copy a prompt or implementation detail. It SHALL state that a deterministic symptom is
handled by its named deterministic owner only after the cognitive program is considered
or explicitly rejected as the causal owner. Bootstrap, HITL2, and rerun SHALL not be
required to carry this LLM-node order. (`NRI-004`)

#### Scenario: Reader starts from a model-bearing behavior symptom
- **WHEN** a Coding Agent opens any one of the eight LLM-Bearing Node reader projections
  for a role, context, candidate, feedback, or repair symptom
- **THEN** the projection directs it through the exact local cognitive-program,
  prompt/context, feedback/repair, and proof/evaluation sources before the separate
  deterministic handoff owners

#### Scenario: Reader explains a deterministic-first exception
- **WHEN** a Coding Agent opens an LLM-Bearing Node reader projection for a typed
  admission, materialization, ledger, gate, or route symptom
- **THEN** the projection identifies the deterministic owner and explains that the
  cognitive program was considered or is not the causal owner, without claiming that a
  model chooses the effect

#### Scenario: Missing cognitive route fails the reader contract
- **WHEN** a required LLM-Bearing Node reader projection omits an exact local
  cognitive-program, prompt/context, feedback/repair, proof/evaluation, or
  deterministic-handoff route
- **THEN** the deterministic reader-interface contract rejects the projection without
  treating Markdown as runtime configuration or a second behavior authority
