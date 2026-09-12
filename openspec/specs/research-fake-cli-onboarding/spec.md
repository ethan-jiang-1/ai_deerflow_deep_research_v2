# research-fake-cli-onboarding Specification

> req: FCO-001, FCO-002

## Purpose

Provide a truthful, copyable credential-free Deep Research fixture-graph entry without
asking users to operate internal graph control flow.

## Requirements

### Requirement: Credential-free CLI onboarding is paste-safe and does not outsource graph control

`deep_research_harness/README.md` SHALL provide the existing repository-root quick
start and a separate sequence for users already in `deep_research_harness/`; neither
copyable command line may contain an inline shell comment. The credential-free fixture-graph CLI
retains its bounded graph-control and clear-fixture-label guarantees, while using the
same Bundle lifecycle vocabulary as the real entry surface. (`FCO-001`)

#### Scenario: Credential-free onboarding names the canonical module
- **WHEN** a user follows the documented module-local fixture-graph CLI sequence
- **THEN** every path and working-directory reference uses `deep_research_harness/`

### Requirement: Credential-free CLI mirrors Bundle lifecycle identity without granting fixture authority

The credential-free fixture-graph CLI SHALL use the same bounded `bundle_id` lifecycle result
shape as the real CLI for its deterministic fixture-graph runs. It SHALL label fixture behavior
as non-product, keep fixture state isolated, and SHALL not introduce a session,
checkpoint, path, or fake-run registry that can authorize a real Deep Research Run.
(`FCO-002`)

#### Scenario: Fixture output cannot supply a real control target
- **WHEN** a fixture-produced Bundle-like id is presented to the real lifecycle interface
- **THEN** real scoped validation treats it as unavailable unless it names an available real Bundle in the trusted scope

### Requirement: Credential-free CLI onboarding is fixture-graph onboarding

The credential-free CLI SHALL remain paste-safe, non-product, and unable to grant
fixture authority to a real Run. Its documented execution route SHALL be the fixed
fixture graph and its bounded Bundle lifecycle projection, not a no-graph
simulation. (`FCO-001`, `FCO-002`)

#### Scenario: Documented credential-free onboarding names graph proof
- **WHEN** a user follows the README's credential-free CLI sequence
- **THEN** it names the canonical Harness path and fixture-graph execution without a
  no-graph command, lifecycle, or real-control claim
