> req: RED-002, RED-008

## ADDED Requirements

### Requirement: Demo TUI projects the shared Bundle lifecycle contract without local inference

The demo TUI SHALL render the same typed Bundle lifecycle outcome, bounded `bundle_id`,
and legal controls as the shared run experience. It SHALL remain a non-product demo and
shall not derive state from a session reference, path, report, external checkpoint, or
fixture-local cache. (`RED-008`)

#### Scenario: Demo TUI does not treat retained output as a resumable Run
- **WHEN** a demo retains output for a Bundle that is no longer available
- **THEN** it renders the shared unavailable observation and submits no resume/control action for that Bundle

## MODIFIED Requirements

### Requirement: Demo remains bounded and explicitly non-product

The demo SHALL launch from `deep_research_harness/` through the canonical
`make demo-tui` and `make demo-tui-fake` targets. It retains its existing real/fake
preflight, explicit non-product boundary, deterministic fake-pilot coverage, and
no-upstream-change constraint. Real mode loads `deep_research_harness/.env` when
present; fake mode remains credential-free. It SHALL project the shared Bundle
lifecycle result and never treat retained demo output as a recoverable session.
(`RED-002`)

#### Scenario: Demo TUI uses the renamed environment file
- **WHEN** real demo TUI mode starts from the downstream module
- **THEN** it reads only `deep_research_harness/.env` when present and does not require
  an old-root compatibility directory
