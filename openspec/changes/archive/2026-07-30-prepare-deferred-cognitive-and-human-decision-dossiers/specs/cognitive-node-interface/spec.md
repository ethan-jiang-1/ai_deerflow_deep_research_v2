> req: CNI-004

## MODIFIED Requirements

### Requirement: Deferred and conditional participation stays separately admitted

Deferred cognitive and conditional human-decision cards SHALL name the current fallback
or controller and the separately admitted activation behavior required later. They
SHALL not infer a model loop, interrupt, tool posture, or route. The project SHALL
retain exactly three non-runtime activation dossiers for HITL2, readiness, and final
delivery. Each dossier SHALL state its product responsibility, participation mode,
commitment state, source-audited current mechanism, trusted and untrusted input
boundary, candidate or choice boundary, deterministic admission owner, bounded failure
posture, lowest deterministic proof seam, and exact successor change. The HITL2 dossier
SHALL state the unresolved non-inferable preference or irreversible authorization trigger
and the user-visible outcome needed before `introduce-hitl2-human-decision-experience` may
propose an experience. Readiness and final-delivery dossiers SHALL state their
accepted-but-deferred bounded cognitive question without claiming a current prompt, tool,
model branch, or live judgment result. The exact successors SHALL be
`introduce-hitl2-human-decision-experience`, `activate-readiness-evidence-critic-loop`, and
`activate-final-report-composition-loop`, respectively.
No dossier SHALL create runtime behavior, implementation authority, or a future Scope
Card approval.

#### Scenario: Future activation is considered
- **WHEN** a maintainer considers readiness, delivery, or HITL2 activation
- **THEN** the card directs them to a separately admitted behavior change

#### Scenario: Three dossiers retain distinct commitments
- **WHEN** the dossier validator reads the deferred and conditional activation records
- **THEN** it finds one HITL2 `conditional/unresolved` record and separate readiness and
  final-delivery `accepted-but-deferred` records, each with its own authority and next change

#### Scenario: Dossier cannot invent an active program
- **WHEN** a dossier omits a user-approved HITL2 trigger or describes a deferred cognitive role
- **THEN** validation rejects an inferred interrupt, model call, prompt, tool posture, route, or
  claimed live judgment result
