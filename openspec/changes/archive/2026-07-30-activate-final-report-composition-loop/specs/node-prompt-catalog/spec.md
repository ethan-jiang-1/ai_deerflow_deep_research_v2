> req: NPC-007

## ADDED Requirements

### Requirement: Final report composition has a deterministic catalog projection

The prompt catalog SHALL project the final-delivery composer with its stable case ID,
local capability, ordered base/capability/assignment/untrusted-data layers, and
forbidden requested tool posture. The projection SHALL remain a generated review
artifact and SHALL not select a prompt, evidence, parser, publisher, route, or
lifecycle result. (`NPC-007`)

#### Scenario: Composer projection is reviewable without runtime authority
- **WHEN** the catalog renders the final-delivery composer case
- **THEN** reviewers can inspect its bounded composition inputs and zero-tool posture
  without invoking a model, resolving runtime dependencies, or accessing evidence
