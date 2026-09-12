> req: FCO-001, FCO-002

## MODIFIED Requirements

### Requirement: Credential-free CLI onboarding is fixture-graph onboarding

The credential-free CLI SHALL remain paste-safe, non-product, and unable to grant
fixture authority to a real Run. Its documented execution route SHALL be the fixed
fixture graph and its bounded Bundle lifecycle projection, not a no-graph
simulation. (`FCO-001`, `FCO-002`)

#### Scenario: Documented credential-free onboarding names graph proof
- **WHEN** a user follows the README's credential-free CLI sequence
- **THEN** it names the canonical Harness path and fixture-graph execution without a
  no-graph command, lifecycle, or real-control claim
