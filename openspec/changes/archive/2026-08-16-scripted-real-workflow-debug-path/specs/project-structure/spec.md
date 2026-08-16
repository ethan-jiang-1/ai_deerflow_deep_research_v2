> req: PRS-019

## ADDED Requirements

### Requirement: Scripted-real debug command paths have canonical registration

The operator-only scripted-real debug surface SHALL live at the registered canonical
paths: the launcher and its composition at
`deep_research_harness/scripts/debug_scripted_real_workflow.py`, the non-production
scenario data modules beneath
`deep_research_harness/src_fake/deerflow_deep_research_fixtures/scripted_real/`, and
its deterministic contract evidence beneath `deep_research_harness/tests/`. The
fixture scenario modules SHALL import only the standard library and the existing
registered production contracts, never the production runtime composition authority;
the launcher SHALL own the scripted-real runtime composition in the presentation
layer. The production package `deep_research_harness/src/deerflow_deep_research/`
SHALL NOT discover or import the scenario scripts. The structure registry SHALL admit
exactly the new registered paths and SHALL continue to reject unregistered placement,
upstream source placement, and generic shared modules. (`PRS-019`)

#### Scenario: New debug surface follows the harness root
- **WHEN** structural governance inspects the scripted-real debug launcher, fixture
  scenario modules, and contract tests
- **THEN** it finds them beneath `deep_research_harness/` at their registered paths and
  rejects a production-package copy, an unregistered path, or upstream placement

#### Scenario: Production package does not discover the scenario scripts
- **WHEN** the production import boundaries are verified
- **THEN** `src/deerflow_deep_research/` has no import of the scripted-real scenario
  modules and the fixture scenario modules stay within the registered fixture
  production-contract allowlist
