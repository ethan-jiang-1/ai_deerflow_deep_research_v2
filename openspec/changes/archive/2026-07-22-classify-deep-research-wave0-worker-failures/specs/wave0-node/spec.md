## ADDED Requirements

### Requirement: Real Wave0 maps trusted worker boundaries into diagnosis-only failures

Real Wave0 SHALL map only its trusted node-agent result, parser/repair, and typed
submission-validation boundaries to `WFC-001` categories before the shared work-unit
component creates the existing terminal attempt.  The lower-level submission boundary
SHALL continue to reject invalid candidates with its typed validation result; the
component SHALL catch only that typed rejection and route it through the existing
terminal/retry path.  Storage, checkpoint, ledger, and other infrastructure failures
SHALL preserve their existing propagation and SHALL NOT be relabeled as worker failure.
(`WAN-006`)

#### Scenario: Typed validation retries through the existing controller
- **WHEN** a real Wave0 candidate receives a typed deterministic submission-validation
  rejection
- **THEN** the component records `submission_validation` for that attempt and applies
  the existing retry/gate policy without appending a submission record

#### Scenario: Infrastructure failure is not disguised
- **WHEN** Wave0 storage or ledger infrastructure fails outside typed validation
- **THEN** it follows its existing infrastructure failure behavior and does not publish
  an invented worker category
