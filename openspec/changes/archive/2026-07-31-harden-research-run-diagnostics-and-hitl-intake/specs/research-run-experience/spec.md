## ADDED Requirements

### Requirement: Provider terminal diagnostic location is verified publication truth

For a provider-diagnostic terminal, `ResearchRunExperience` SHALL report
`diagnostic_location=session_bundle` and `research_record_created=true` only when the
returned retained-session projection verifies that the exact terminal diagnostic
reference was published in its bundle. When that verification is absent or the bundle
publisher cannot publish the record, it SHALL use the existing exact-reference support
journal fallback and report `support_journal`, or report `unavailable` if that fallback
also fails. The fallback record SHALL retain the same role-bound timeout origins when
they were supplied. The shared terminal SHALL preserve the original category, phase,
recovery disposition, trigger/final timeout origins, and lifecycle authority; it SHALL
not create a replacement reference or turn inspection into retry/resume control.
(`RER-009`)

#### Scenario: Verified bundle record enables session-bundle location
- **WHEN** a provider terminal's returned session projection verifies the same opaque
  diagnostic reference as the terminal incident
- **THEN** the shared terminal reports `session_bundle` and record-created truth

#### Scenario: Stale reference cannot qualify a bundle as diagnostic storage
- **WHEN** a session is available but cannot verify the terminal's exact diagnostic
  record or carries a different reference
- **THEN** the shared terminal does not report `session_bundle` and follows the existing
  exact-reference fallback or unavailable outcome

#### Scenario: Safe timeout origins reach all shared participants in their roles
- **WHEN** a verified provider terminal carries a bridge-budget retry trigger and a
  provider-SDK-timeout final observation
- **THEN** the shared terminal exposes each exact closed origin through its existing
  trigger/final observation role for CLI/TUI and machine consumers without exposing raw
  diagnostic material

#### Scenario: Support-journal fallback retains observed origins
- **WHEN** a provider terminal carrying closed trigger/final timeout origins cannot
  verify bundle diagnostic publication but the exact-reference support journal succeeds
- **THEN** the support-journal record and the shared terminal retain those same origins
  in their roles without creating a replacement reference or exposing raw diagnostic
  material
