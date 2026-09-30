# Spec Delta

> req: LDD-010

## ADDED Requirements

### Requirement: A drive may stop only where its typed condition holds

The driving surface SHALL let a stop policy carry a typed breakpoint condition
(`StopPolicy.condition`) over the Bundle's durable typed State fields. During a
drive, the condition SHALL be evaluated at each committed boundary against the
same durable State the drive loop already reads; when a condition is present,
a conditional breakpoint target SHALL stop only at a boundary where the named
node has visited AND the condition holds, and a target-free condition SHALL
stop at the first boundary where the condition holds. The condition evaluator
SHALL be a pure, total function: it SHALL return a boolean for any State and
SHALL never raise into the drive loop. Condition evaluation SHALL NOT widen
the drive's existing bounded iteration; a condition that never holds SHALL
end the drive at the same bound as any other drive, leaving the session at
its last committed boundary. (`LDD-010`)

#### Scenario: A conditional target stops only when the condition holds
- **WHEN** a drive targets a node with the condition `generation >= 2` and the
  node's boundary commits while `generation` is still below `2`
- **THEN** the drive continues past that boundary and stops at the first
  later boundary where the node has visited and `generation >= 2` holds

#### Scenario: A target-free condition stops at the first satisfying boundary
- **WHEN** a drive carries a condition without a node target and a committed
  boundary's State satisfies it
- **THEN** the drive stops at that boundary

#### Scenario: A never-satisfying condition stays bounded
- **WHEN** a drive carries a condition that no boundary satisfies
- **THEN** the drive terminates at its existing bounded iteration limit with
  the session at a committed boundary, without erroring or advancing forever

### Requirement: Condition contracts are closed and validated before driving

The breakpoint condition contract SHALL be closed: field names SHALL be
validated against the durable typed State field allowlist, operators SHALL be
a closed comparison set, and literals SHALL be str, int, bool, or none. A
condition that names an unknown field, uses an operator outside the closed
set, or carries an unparseable literal SHALL be rejected as a typed
parse-level denial before any drive begins — an invalid condition SHALL never
reach the drive loop. (`LDD-010`)

#### Scenario: An unknown field is denied at parse time
- **WHEN** a stop policy is built with a condition naming a field outside the
  typed State allowlist
- **THEN** the caller receives a typed denial naming the problem, and no
  drive is started with that condition

#### Scenario: A valid condition parses into a closed contract
- **WHEN** a condition names allowlisted fields with closed-set operators and
  parseable literals
- **THEN** the parsed condition contract evaluates deterministically against
  any State
