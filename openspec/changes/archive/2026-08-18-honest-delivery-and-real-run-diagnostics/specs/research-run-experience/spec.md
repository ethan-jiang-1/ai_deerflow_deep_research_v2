## MODIFIED Requirements

### Requirement: Provider terminal diagnostic location is verified publication truth

For a blocked terminal, `ResearchRunExperience` SHALL report
`diagnostic_location=bundle_journal` and `research_record_created=true` only when
the returned retained-session projection verifies that the exact terminal
diagnostic reference was published in its available Bundle. This verified-publication
rule SHALL apply to every blocked terminal that carries a diagnostic reference —
provider-diagnostic terminals and gate/controller blocked terminals alike; the
availability truth is a property of the published reference, not of the incident's
failure class. When that verification is absent or the Bundle publisher cannot
publish the record, it SHALL report `diagnostic_location=unavailable` and
`research_record_created=false`. It SHALL NOT use an exact-reference support journal
fallback or any external diagnostic, Journal, or Support Handoff as a supported
reader or participant presentation. The shared terminal SHALL preserve the original
category, phase, recovery disposition, trigger/final timeout origins, and lifecycle
authority; it SHALL not create a replacement reference or turn inspection into
retry/resume control. A blocked terminal whose diagnostic reference is verified as
published SHALL never render as journal-unavailable in any shared participant
surface. This requirement does not assert secure erasure or the absence of
physical residual bytes after Bundle loss. (`RER-009`)

#### Scenario: Verified bundle record enables session-bundle location
- **WHEN** a provider terminal's returned session projection verifies the same opaque
  diagnostic reference as the terminal incident
- **THEN** the shared terminal reports `bundle_journal` and record-created truth

#### Scenario: A gate-blocked terminal reports its published journal truth
- **WHEN** a gate-derived blocked incident carries a diagnostic reference and the
  retained-session projection verifies that exact reference as published in the
  available Bundle
- **THEN** the shared terminal reports `diagnostic_location=bundle_journal` and
  `research_record_created=true`, and CLI/TUI journal-availability rendering shows
  the journal as created rather than unavailable

#### Scenario: Stale reference cannot qualify a bundle as diagnostic storage
- **WHEN** a session is available but cannot verify the terminal's exact diagnostic
  record or carries a different reference
- **THEN** the shared terminal does not report `bundle_journal`, reports
  `unavailable`, and performs no external diagnostic fallback, regardless of the
  incident's failure class

#### Scenario: Safe timeout origins reach all shared participants in their roles
- **WHEN** a verified provider terminal carries a bridge-budget retry trigger and a
  provider-SDK-timeout final observation
- **THEN** the shared terminal exposes each exact closed origin through its existing
  trigger/final observation role for CLI/TUI and machine consumers without exposing raw
  diagnostic material

#### Scenario: Support-journal fallback retains observed origins
- **WHEN** a provider terminal carrying closed trigger/final timeout origins cannot
  verify Bundle diagnostic publication
- **THEN** the shared terminal reports `unavailable`, preserves the terminal's existing
  lifecycle authority and legal action, and neither writes nor reads an external
  diagnostic, Journal, or Support Handoff
