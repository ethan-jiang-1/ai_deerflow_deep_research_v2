> req: RED-011

## ADDED Requirements

### Requirement: The TUI offers attach projection for recoverable bundles

On startup, when the demo TUI's workspace contains recoverable bundles whose
projected legal next action is RESUME, the TUI SHALL present an attach
projection listing those bundles (bounded to the most recent, with the recorded
phase summary), and SHALL let the operator choose to continue, inspect, or
discard toward a fresh run. The projection is presentation only: it SHALL NOT
decide recovery semantics, SHALL NOT construct any human response, and SHALL
route the operator's choice through the existing lifecycle actions. When no
recoverable bundle exists, startup behavior SHALL be unchanged. (`RED-011`)

#### Scenario: Startup presents a recoverable bundle for attach
- **WHEN** the TUI starts and the workspace contains a suspended bundle whose
  projected legal next action is RESUME
- **THEN** the TUI presents the bundle (bounded list, phase summary) with
  continue / inspect / discard choices, and startup without operator choice
  does not itself mutate the bundle

#### Scenario: Continue routes through lifecycle, not TUI authority
- **WHEN** the operator chooses continue for a projected bundle
- **THEN** the TUI issues the choice through the existing lifecycle resume
  path, and the run continues from its durable checkpoint without the TUI
  constructing any response or route

#### Scenario: No recoverable bundle leaves startup unchanged
- **WHEN** the TUI starts with no bundle projecting RESUME
- **THEN** startup proceeds exactly as before with no attach projection
