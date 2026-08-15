## ADDED Requirements

### Requirement: LLM-node reader projections expose the cognitive authoring order

The Wave2 synthesis, HITL1, topic-planning, Wave0, Wave1, and targeted-evidence
`workflow.md` reader projections SHALL identify the ordered route a Coding Agent uses
before changing model-bearing behavior: the Node Cognitive Control Contract and local
capability; prompt builder and model-visible context; structured output, feedback, and
repair; focused deterministic proof and applicable cognitive evaluation; and the
separate deterministic admission, materialization, ledger, gate, and route owners.

Each projection SHALL retain its current local symptom navigation and non-runtime
boundary. It SHALL link to the exact local sources that answer its route rather than
copy a prompt or implementation detail. It SHALL state that a deterministic symptom is
handled by its named deterministic owner only after the cognitive program is considered
or explicitly rejected as the causal owner. The five non-model node projections SHALL
not be required to carry this LLM-node order. (`NRI-004`)

#### Scenario: Reader starts from a model-bearing behavior symptom
- **WHEN** a Coding Agent opens any one of the six LLM-Bearing Node reader projections
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
