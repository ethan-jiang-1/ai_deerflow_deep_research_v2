> req: WOU-009

## ADDED Requirements

### Requirement: Work-unit and content roots use the canonical bundle locator

The work-unit projection, storage probe, deterministic bundle helpers, and `ContentRef`
validation SHALL derive research and attempt roots from the checkpoint-selected canonical
bundle locator plus controller-assigned work and attempt ids. They SHALL reject a
malformed locator, root mismatch, symlink/path escape, or an artifact whose path belongs
to another locator even when its `research_id` suffix appears valid. For a compatible old
checkpoint with no locator they SHALL derive only legacy `r_<research-id>` roots. This
changes no work, attempt, ledger, or lifecycle identity. (`WOU-009`)

#### Scenario: Attempt content follows one new bundle root
- **WHEN** a Wave0 work attempt runs for locator `202607220359_r_abc`
- **THEN** its spec, result, cache, evidence ledger, diagnostics probe, and `ContentRef` all remain under that one root

#### Scenario: Locator mismatch fails containment
- **WHEN** a candidate or stored reference targets another timestamped root for the same research id
- **THEN** validation rejects it before ledger publication or content reference acceptance
