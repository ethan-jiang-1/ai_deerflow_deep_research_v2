# Spec Delta

> req: LDD-007, LDD-008

## ADDED Requirements

### Requirement: Node rerun at a stopped boundary is lifecycle-admitted, never a driver write

The debug driver SHALL accept a `rerun_node` command at a stopped boundary that
re-executes the most recently committed node with the same inputs. The command SHALL
carry the exact bundle id, expected cursor, and a unique command id under the existing
at-most-once discipline. All rollback of the node's committed outputs — trace tail,
work-unit accounting, evidence pointers — SHALL be admitted and written by the
lifecycle controller; the driver SHALL NOT write graph or Bundle state directly and a
refused rollback SHALL leave the session at its current boundary with a typed denial.
(`LDD-007`)

#### Scenario: A rerun re-executes the same node
- **WHEN** the operator reruns at a boundary where a node just committed
- **THEN** the node executes again with the same inputs, the trace gains a fresh visit
  for that node, and the journal records the rerun admission

#### Scenario: A refused rollback keeps the boundary intact
- **WHEN** the lifecycle cannot roll the committed tail back transactionally
- **THEN** the driver returns a typed denial, nothing is re-executed, and the session
  stays at the same boundary

### Requirement: drive_until auto-confirms HITL profile proposals under an explicit bounded policy

`drive_until` SHALL carry an explicit auto-HITL policy: when the drive meets a hitl1
profile-confirmation request, it MAY submit `确认` (confirm) as an operator-policy
answer through the existing semantic intake and continue. Single-step advances SHALL
never auto-answer, and HITL2 direction decisions SHALL always stop for the operator.
Every auto-answer SHALL be stated in the operator log as policy-submitted. When the
same request is auto-answered twice without acceptance, the drive SHALL stop and
surface the node's reply for a human answer. (`LDD-008`)

#### Scenario: A drive passes a complete proposal
- **WHEN** a drive with auto-HITL meets a complete profile proposal
- **THEN** it submits confirm as operator policy, the log states the auto-answer, and
  the drive continues to the next stop

#### Scenario: An incomplete proposal falls back to the human
- **WHEN** two consecutive auto-answers are not accepted
- **THEN** the drive stops at the HITL request and renders the node's reply and
  remaining rounds for a human answer

#### Scenario: Single steps never auto-answer
- **WHEN** the operator advances one boundary at a time
- **THEN** every HITL request waits for a human answer
