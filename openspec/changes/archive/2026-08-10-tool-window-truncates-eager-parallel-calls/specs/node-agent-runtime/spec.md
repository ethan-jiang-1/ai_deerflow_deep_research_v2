## MODIFIED Requirements

### Requirement: Tool and path policy fails closed

The node-agent runtime SHALL expose only explicitly allowed tools and SHALL revalidate
the runtime tool name and path-bearing arguments before dispatch. Every allowed tool
SHALL have a typed ToolPolicySpec declaring path fields, effects, validator, and
cancellation class; unknown argument shapes and tools without an approved native
async/cancellable path SHALL be denied. Reads and writes SHALL stay within policy
roots; writes SHALL stay within the active attempt and SHALL never mutate graph phase,
gates, ledger, sibling attempts, package source, or host paths.

A bounded request tool window SHALL cap the number of tool calls that execute in one
agent run. When a model response requests more parallel tool calls than the remaining
window, the runtime SHALL keep only the first calls that fit the window and drop the
excess; it SHALL NOT fail the run, and the dropped calls SHALL NOT execute. After the
window is exhausted, later model turns SHALL have tools removed so the agent produces
its structured answer. Genuine policy violations — a non-allow-listed tool, a traversal
path, an ineligible spec, or a write outside the attempt root — SHALL still fail closed
before dispatch. (`NOA-003`)

#### Scenario: Allowed attempt write succeeds
- **WHEN** a fake file tool writes a canonical path within the active attempt write root
- **THEN** policy authorizes the call and records its scoped artifact reference

#### Scenario: Forged tool or path is denied
- **WHEN** a model requests an unlisted tool, traversal path, symlink escape, cross-attempt write, or gate/ledger mutation
- **THEN** middleware blocks execution, leaves the target unchanged, and returns a typed policy denial

#### Scenario: Eager over-request is truncated to the remaining window
- **WHEN** a model response requests more parallel tool calls than the remaining
  bounded request window
- **THEN** the runtime keeps only the first calls that fit the window, drops the
  excess without executing them, and does not fail the run
