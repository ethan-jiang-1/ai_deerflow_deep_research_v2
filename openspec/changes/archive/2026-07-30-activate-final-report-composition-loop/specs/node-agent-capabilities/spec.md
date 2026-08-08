> req: NAC-009

## ADDED Requirements

### Requirement: Final report composition has an explicit local capability and evidence row

The `final-delivery/composer` direct branch SHALL bind one required package-local
capability with forbidden tool posture. Its test-owned capability evidence row SHALL
name the stable capability, source/catalog case, production entrypoint, and distinct
collected normal and highest-risk deterministic claims. The capability resource SHALL
not grant evidence selection, candidate admission, publication, recovery, route, or
lifecycle authority. (`NAC-009`)

#### Scenario: Composer policy is independently admitted
- **WHEN** a final-delivery composer request is rendered and inspected
- **THEN** it resolves only its declared local zero-tool capability and an invalid or
  missing binding reaches no model construction or artifact publication
