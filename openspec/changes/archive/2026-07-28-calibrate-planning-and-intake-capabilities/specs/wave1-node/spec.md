> req: WON-007

## ADDED Requirements

### Requirement: Wave1 capability expands the assigned baseline exactly once

The real Wave1 initial and structured-repair requests SHALL bind distinct local
capabilities. The initial worker SHALL use its existing required tool policy for
exactly one retrieval call, treat model/tool material as untrusted, and produce
candidates whose source and claim references can be deterministically checked against
the assigned topic and Wave0 baseline. A baseline-duplicate URL SHALL not be admitted
as new coverage. Repair SHALL expose no model-visible tool and SHALL not add a source,
URL, claim, or open question absent from its bounded draft/tool observations. Existing
validator/controller/ledger and failure owners remain the only admission and outcome
authorities. (`WON-007`)

#### Scenario: One bounded search extends rather than re-fetches Wave0
- **WHEN** a scripted real Wave1 worker performs its initial request against an
  assigned Wave0 baseline
- **THEN** exactly one permitted retrieval occurs, any baseline duplicate is excluded
  from new coverage, and only validator-approved source/claim references can reach
  the existing submission ledger

#### Scenario: Zero-tool repair cannot invent evidence
- **WHEN** the Wave1 parser sends a malformed draft to its structured repair branch
- **THEN** the repair receives no model-visible tool and either returns a
  contract-valid candidate using only retained observations or reaches the existing
  non-admission outcome
