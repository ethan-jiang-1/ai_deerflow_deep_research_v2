> req: EVH-013

## ADDED Requirements

### Requirement: Profile-brief capability evidence uses independent lifecycle claims

The capability evidence matrix SHALL add one row each for `hitl1/brief` and
`hitl1/brief-repair`, with distinct collected central claims for advisory proposal
success and malformed-output repair/exhaustion. Each claim SHALL exercise the real
HITL1 node seam with fake capabilities, retain deterministic authenticity, and prove
that neither result grants acceptance, route, or checkpoint authority. (`EVH-013`)

#### Scenario: Profile success remains advisory
- **WHEN** a scripted valid brief reaches the real HITL1 first-proposal seam
- **THEN** it yields a proposal only and the matrix records a collected success claim
  distinct from its repair-risk claim

#### Scenario: Exhausted repair cannot publish authority
- **WHEN** malformed brief output and its one repair both fail validation
- **THEN** the matrix's risk claim proves the existing exhausted/non-success path with
  no accepted profile, route, or checkpoint authority
