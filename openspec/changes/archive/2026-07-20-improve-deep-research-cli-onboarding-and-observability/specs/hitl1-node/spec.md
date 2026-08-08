> req: HIN-006

## ADDED Requirements

### Requirement: Real HITL-1 preserves brief-generation failure category through its blocked route

Real HITL-1 SHALL consume the typed NodeProblem returned by the runtime bridge when
brief generation cannot complete. It SHALL retain its existing bounded retry and
exhausted graph route, but SHALL not catch every bridge/model exception and convert
it to an indistinguishable None result. A directly known safe category and opaque
diagnostic reference may be recorded as the compact terminal incident when the
node routes blocked; raw error content shall not enter profile state, pending
interrupt, request bundle, or human prompt.

Malformed structured brief output SHALL be categorized as a safe output/validation
failure distinct from missing model configuration or provider timeout. A
non-interactive auto-profile path shall retain its current behavior and shall not
construct a failed brief solely to populate presentation diagnostics. (HIN-006)

#### Scenario: Real model configuration failure explains the blocked route
- **WHEN** a real interactive HITL-1 run cannot resolve a model before creating its
  brief
- **THEN** it reaches the existing blocked terminal route with a compact safe
  configuration category available to lifecycle projection instead of only
  gate_blocked with no causal explanation
