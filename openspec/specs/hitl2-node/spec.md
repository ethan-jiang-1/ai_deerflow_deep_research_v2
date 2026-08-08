# hitl2-node Specification

> req: HIT-001, HIT-002, HIT-003
## Purpose
Autonomous continuation node with a deterministic diagnostic brief builder and
fixture-controlled test routes.

## Requirements



### Requirement: Deterministic brief builder generates decision brief from accepted findings

The retained HITL2 brief helper SHALL remain pure and bounded: it may summarize only
accepted findings, synthesis gaps, and critic verdicts already present in checkpoint
state and SHALL not fabricate facts, call an LLM, or read sandbox files. It SHALL NOT
own ordinary routing. The HITL2 boundary validator SHALL instead confirm that state
reached HITL2 through the existing Wave2-pass path, then select only the existing
`proceed` route. Wave2 and readiness
retain all quality-gate authority.

#### Scenario: Ordinary validated state produces an autonomous route
- **WHEN** HITL2 runs after a passing Wave2 synthesis
- **THEN** it validates the bounded predecessor and routes autonomously without a
  `PendingResearchInterrupt`

#### Scenario: Untrusted predecessor fails closed
- **WHEN** the candidate state is malformed or names an unknown HITL2 predecessor
- **THEN** the validator fails closed without inventing a route or human prompt

### Requirement: HITL2 retains autonomous continuation without a human interrupt

HITL2 SHALL not use the interrupt/resume pipeline. The fake factory SHALL consume its
configured fixture route as test control without a `PendingResearchInterrupt`; the
real factory SHALL apply the validated autonomous `proceed` route. Ordinary route
names SHALL NOT be shown as user decisions. A future human-decision feature MUST
define a separate typed authority marker, trusted producer, bounded prompt,
response-binding rules, and options contract in its own reviewed change before it may
restore an HITL2 interrupt.

#### Scenario: Fixture routing remains graph-testable without an interrupt
- **WHEN** a deterministic fake fixture selects any existing HITL2 route
- **THEN** the graph takes that route without a pending input or a user-attributed
  terminal reason

### Requirement: Mixed-graph integration requires full real chain

Real HITL2 SHALL require `wave2_synthesis=real` (which transitively requires the
full chain through wave0, wave1, and targeted_evidence). Selecting `hitl2=real`
without `wave2_synthesis=real` SHALL fail before graph invocation. Full-fake HITL2
SHALL remain deterministic fixture control without an interrupt. Topology SHALL be
unchanged.

#### Scenario: Real HITL2 requires real wave2_synthesis
- **WHEN** a recipe selects `hitl2=real` without `wave2_synthesis=real`
- **THEN** recipe construction fails with a typed dependency error

#### Scenario: Full-fake HITL2 remains fixture-controlled without an interrupt
- **WHEN** the full-fake graph reaches HITL2
- **THEN** it consumes its configured fixture route without a pending input, while
  preserving the declared graph edge and fixture-specific terminal attribution
