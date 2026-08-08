## RENAMED Requirements

- FROM: `### Requirement: Wave2 provides a node-local, non-runtime reader interface`
- TO: `### Requirement: LLM-bearing nodes provide node-local, non-runtime reader interfaces`
- FROM: `### Requirement: Wave2 reader interface routes consequential symptoms to owners`
- TO: `### Requirement: Reader interfaces route consequential symptoms to current owners`

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

#### Scenario: Reader opens a package-local projection
- **WHEN** a maintainer begins an investigation from any one of the six
  LLM-bearing node packages
- **THEN** the maintainer can identify the bounded model job, the applicable
  deterministic owners, and the authoritative source/specification/test surfaces
  without treating `workflow.md` as runtime configuration or a second behavior
  authority

#### Scenario: Projection does not require a shared documentation mechanism
- **WHEN** the six node-local projections are reviewed together
- **THEN** each may use its own concise navigation shape, while no parser, Markdown
  schema, generated inventory, checker, shared documentation module, or runtime
  registration is required for any projection

### Requirement: Reader interfaces route consequential symptoms to current owners

Each node reader projection SHALL provide symptom-driven navigation to its exact
source owner and narrow deterministic proof seam for the facts that could otherwise
cause a wrong first edit. It SHALL distinguish the capability Markdown body that may
enter rendered policy from capability metadata and runtime tool enforcement where
that distinction is relevant. It SHALL not assign human acceptance, candidate
admission, artifact publication, ledger update, critic materialization, gate result,
or executable routing authority to a model.

The HITL1 projection SHALL distinguish advisory profile-brief generation from
semantic interpretation of a correlated human reply, and SHALL identify the
graph/domain owner that accepts a proposal and publishes a profile. The topic-planning
projection SHALL distinguish the confirmed-profile plan candidate from deterministic
topic materialization and its bounded repair/exhausted path. The Wave0 projection
SHALL distinguish permitted retrieval and zero-tool repair from worker-controller,
submission-validator, ledger, and gate authority. The Wave1 projection SHALL
distinguish caller-supplied baseline classification from top-level baseline loading,
validator/controller, critic, and gate authority. When current source leaves the
top-level baseline loading or critic/open-question gate enforcement incomplete, it
SHALL label that fact as an implemented limitation and SHALL NOT represent an
injected-subgraph baseline test as full-node evidence. The targeted-evidence projection SHALL distinguish
gate-projected gap work, same-gap worker/repair admission, and read-only critic
materialization; it SHALL state that its `route="next"` update is not an executable
branch choice because the graph builder unconditionally returns the node to Wave2.

#### Scenario: Reader investigates HITL1 proposal semantics
- **WHEN** a reader receives a natural reply to a checkpointed HITL1 proposal and
  needs to determine whether it can accept or revise the profile
- **THEN** the reader can identify the semantic candidate builder, correlated human
  interaction owner, and narrow proof seam without assigning acceptance, profile
  publication, or route authority to the model

#### Scenario: Reader investigates a topic-planning repair or block
- **WHEN** a confirmed-profile plan is invalid, uncovered, or repeatedly invalid
- **THEN** the reader can identify the planner request, deterministic materializer,
  bounded repair/exhaustion owner, and proof seam without changing the checkpoint
  profile, graph wiring, or a model-generated topic id

#### Scenario: Reader investigates a Wave0 or Wave1 evidence-admission symptom
- **WHEN** a retrieval worker, zero-tool repair, source floor, baseline duplicate,
  or critic requirement produces an unexpected evidence outcome
- **THEN** the reader can identify the worker/repair request owner and the separate
  validator/controller/ledger/gate owner without treating model text as accepted
  evidence or a route decision

#### Scenario: Reader investigates a Wave1 baseline duplicate in a full node run
- **WHEN** a Wave0-baseline URL is treated as new during a top-level real Wave1 run
- **THEN** the reader identifies `wave1/node.py::build_real` as the first baseline
  loading owner, identifies the direct `_wave1_worker` test as injected-subgraph
  evidence only, and labels the missing top-level load as an implemented limitation
  rather than proposing a prompt, ledger, or graph-edge change

#### Scenario: Reader investigates targeted evidence return behavior
- **WHEN** a gate-projected gap, targeted repair, or read-only critic result reaches
  the targeted-evidence node
- **THEN** the reader can identify the gap/worker/critic admission owners and the
  graph builder's unconditional return to Wave2 without treating the node's
  `route="next"` update as a model or handler-controlled executable route
