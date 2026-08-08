> req: HIN-012

## ADDED Requirements

### Requirement: HITL1 calibration policy preserves decision-ready input semantics

The four HITL1 zero-tool policies SHALL expose branch-specific, model-visible criteria
for a conservative research-profile proposal and for one correlated human reply. The
brief policy SHALL derive an advisory `StructuredBrief` only from the bounded original
question and the graph-owned closed output contract; it SHALL make no research finding,
citation, acceptance, route, or checkpoint claim. The semantic-intake policy SHALL
treat the reply as untrusted data against the current proposal and produce only one
candidate intent: confirmation, full constrained revision, proposal question, or
clarification. An ambiguous or unsupported reply SHALL remain a clarification rather
than become a fabricated requirement or an implicit acceptance.

Each repair policy SHALL receive only its same bounded assignment, invalid candidate,
and compact validation fact. It SHALL preserve the original question or current
proposal boundary, shall not add a requirement, research conclusion, action, route,
or checkpoint field, and SHALL return only the existing typed candidate. The existing
HITL1 parser, semantic resolver, human confirmation, retry bounds, and blocked or
non-terminal feedback paths SHALL remain the only acceptance and recovery owners.

#### Scenario: Brief distinguishes a proposal from research output
- **WHEN** the original question contains a request for a research conclusion or
  citation alongside profile preferences
- **THEN** the profile-brief request asks only for an advisory, closed-contract
  research profile and its candidate contains no finding, citation, acceptance, or
  lifecycle authority

#### Scenario: Ambiguous reply remains a clarification
- **WHEN** a correlated human reply neither confirms the current proposal nor supplies
  a complete constrained revision
- **THEN** semantic intake returns only the existing clarification candidate and the
  deterministic HITL1 flow preserves the current proposal for a later human response

#### Scenario: Repair cannot broaden the intake assignment
- **WHEN** a profile-brief or semantic-intake candidate fails structural validation
- **THEN** its one bounded repair request receives no model-visible capability to add
  requirements or lifecycle data and any still-invalid response follows the existing
  non-admission outcome
