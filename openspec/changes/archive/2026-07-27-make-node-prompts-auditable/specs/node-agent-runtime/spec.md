> req: NOA-010

## ADDED Requirements

### Requirement: Phase-agent bridge consumes the shared final prompt projection

Before constructing a phase-agent child state, `RuntimeNodeAgentBridge` SHALL obtain
the system-policy text and final human message from the agents-owned pure final-prompt
renderer using the current validated `NodeExecutionRequest` and attempt workspace. It
SHALL preserve the existing child sandbox/thread metadata, model and tool resolution,
budget enforcement, agent invocation, and result projection ownership. The renderer
and a deterministic prompt catalog SHALL not receive runtime envelope facts or gain
model, tool, route, checkpoint, or lifecycle authority. (`NOA-010`)

#### Scenario: Runtime message construction does not fork from the review projection
- **WHEN** the bridge executes a request corresponding to a canonical prompt-catalog
  case
- **THEN** its agent system policy and human message equal that case's shared rendered
  projection while its runtime-only metadata remains outside the catalog

#### Scenario: Canonical bridge capture proves source-faithful text
- **WHEN** a deterministic test runs one graph-owned canonical prompt case through
  the bridge with fake model and tool bindings that capture agent construction and
  child state
- **THEN** the captured system policy and first human message exactly equal the shared
  renderer's projection for that same case, without the catalog receiving any runtime
  envelope fact
