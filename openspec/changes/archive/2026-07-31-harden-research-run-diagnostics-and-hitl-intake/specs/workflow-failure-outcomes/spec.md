## ADDED Requirements

### Requirement: Provider diagnostic reference identity retains observed timeout roles

The shared `workflow_outcomes.derive_provider_diagnostic_reference()` helper SHALL
remain the sole canonical identity owner for provider-diagnostic terminal references
used by all existing callers, including direct phase and controller-derived worker
incidents. When a recovery trigger or final provider observation carries a closed timeout
origin, the helper SHALL include that exact origin in its corresponding trigger or final
safe identity role. It SHALL not merge roles, infer an absent origin, or include raw
exceptions, provider bodies, prompts, credentials, full URLs, host paths, or request
payloads.

When neither observation carries an origin, the helper SHALL retain its exact current
version-one identity payload and resulting reference: it SHALL not add a null origin
field, change the payload version, or otherwise churn origin-absent references. HITL1,
topic planning, Wave2, and controller-derived worker incidents SHALL continue to use
this helper rather than define a local reference identity. (`WFO-001`)

#### Scenario: Distinct observed roles produce distinct safe references
- **WHEN** two otherwise identical provider-diagnostic terminals differ only in a
  trigger or final timeout origin
- **THEN** their references differ only through the corresponding safe role input, with
  no raw/provider material represented in either identity

#### Scenario: Origin-absent reference remains compatible
- **WHEN** the trigger and final observations both carry no timeout origin
- **THEN** the helper produces the exact current version-one reference for the same
  existing safe inputs
