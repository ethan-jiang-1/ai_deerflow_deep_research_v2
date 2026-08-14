## ADDED Requirements

### Requirement: Fixture source is the sole credential-free execution composition

Credential-free demo roots SHALL explicitly compose the complete fixture catalog and
matching gate definitions through the existing generic composition seam, then execute
that recipe through its graph executor. Fixture source SHALL remain test/demo-only and
shall not gain production, root-tool, lifecycle-controller, or Bundle-discovery
authority. An incomplete catalog or executor SHALL fail before graph compilation or
lifecycle dispatch and shall not select a no-graph fallback. (`FSI-002`, `FSI-003`)

#### Scenario: Credential-free composition remains explicit and isolated
- **WHEN** a supported credential-free CLI or TUI starts with fixture source enabled
  for its child process
- **THEN** it uses the complete fixture catalog and executor, while production assembly
  and reflected runtime neither import nor discover fixture source

