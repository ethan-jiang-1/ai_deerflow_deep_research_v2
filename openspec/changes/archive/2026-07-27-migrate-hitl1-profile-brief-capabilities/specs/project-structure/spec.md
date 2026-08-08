> req: PRS-013

## ADDED Requirements

### Requirement: HITL1 profile capability paths are registered locally

The project structure registry SHALL register the HITL1 package declaration and the
two exact local resources `capabilities/hitl1-profile-brief.md` and
`capabilities/hitl1-profile-brief-repair.md`, together with their focused inventory
and real-node evidence paths. The registration SHALL not add a capability location to
another node package or permit a global prompt directory, graph-to-agents import, or
upstream placement. (`PRS-013`)

#### Scenario: Second-cohort local paths pass architecture governance
- **WHEN** architecture governance inspects the HITL1 second cohort
- **THEN** it finds only the registered HITL1 local declaration/resources and rejects
  an escaping, global, reverse, or upstream capability path
