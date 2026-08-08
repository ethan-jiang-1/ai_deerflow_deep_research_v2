> req: DRC-008

## ADDED Requirements

### Requirement: Node-agent workflow changes carry a bounded integrity review

The Deep Research Agent Charter SHALL route a
`node-agent-workflow-integrity` policy for a change that adds, removes, or
materially changes a node's LLM-bearing cognitive role, node-local capability policy,
tool posture, output-admission boundary, repair semantics, or model/non-model
classification. The policy SHALL direct the change author to distinguish the
deterministic graph/node handler, bounded Node Agent, runtime bridge, and
parser/evaluator/materializer owners. It SHALL state that the policy creates no
runtime route, state writer, tool permission, model invocation, or recovery behavior;
those remain in an owning capability specification and executable contract.

When a proposal's `Triggered charter policies` field includes
`node-agent-workflow-integrity`, the proposal SHALL contain exactly one
`## Node Agent Review` table with the following header, separator, and at least one
complete row:

```text
| Surface | Classification | Bounded cognitive question or no-agent rationale | Input authority boundary | Tool posture and runtime enforcer | Candidate result and deterministic admission owner | Failure owner and bound | Deterministic evidence seam |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

Each `Classification` value SHALL be exactly `node-agent` or `no-agent`. The
deterministic charter checker SHALL reject a selected policy with a missing,
malformed, incomplete, or invalid-classification record. It SHALL not infer policy
applicability or judge the semantic truth of a review row. The OpenSpec authoring
context SHALL route node-agent changes to this policy without turning root
`config.yaml`, `openspec/config.yaml`, the review table, or a prompt projection into
runtime authority. (`DRC-008`)

#### Scenario: A node-agent capability change records its bounded handoff
- **WHEN** a proposal changes a node's LLM-bearing capability policy and selects
  `node-agent-workflow-integrity`
- **THEN** it contains one complete Node Agent Review row naming the bounded job,
  input authority boundary, tool enforcer, candidate-result admission owner, failure
  owner/bound, and deterministic evidence seam

#### Scenario: An intentionally deterministic node is explicitly classified
- **WHEN** a proposal changes a relevant node but retains deterministic execution
  and selects `node-agent-workflow-integrity`
- **THEN** its Node Agent Review row uses `no-agent` and names the bounded rationale
  without requiring a fabricated model capability

#### Scenario: An incomplete selected review fails closed
- **WHEN** an active proposal selects `node-agent-workflow-integrity` but omits the
  review, uses a different table header, leaves a required cell empty, or uses an
  unsupported classification
- **THEN** the charter checker fails before the proposal can claim governance
  conformance

#### Scenario: Role review and failure review remain distinct
- **WHEN** a proposal selects both `node-agent-workflow-integrity` and
  `workflow-outcome-review`
- **THEN** the charter checker requires both review records, preserving the existing
  failure/recovery table rather than treating role guidance as a recovery contract

#### Scenario: Governance does not grant runtime authority
- **WHEN** a reviewer reads a valid Node Agent Review record
- **THEN** the record identifies the owning capability and deterministic admission
  boundary but does not itself create a graph route, state write, tool permission,
  provider call, retry, or result acceptance
