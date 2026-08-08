> req: RED-005

## MODIFIED Requirements

### Requirement: TUI exposes shared run inspection truth without local path inference

The local TUI SHALL use an adapter-injected broker's projections for discovered-session
status and operations instead of keeping a parallel lifecycle/session controller. It MAY
render the broker's validated bounded pending-input view for an authorized session, and
SHALL render unavailable or denied operations without raw scope, path, provider, or
checkpoint data. It SHALL not select or reconstruct a recipe for a stored session; the
profile-owned broker determines whether the session is compatible. It retains the safe
legacy inspect reference and may offer only broker-backed discover/open/status/cancel or
resume controls; it keeps the expected opaque request id in its safe view model and passes
raw answer text only to the broker. (`RED-005`)

#### Scenario: TUI shows the same paused-run reference as CLI
- **WHEN** the shared run experience projects a retained HITL-1 or HITL-2 session
- **THEN** the TUI presents the same reference and inspectability truth as the CLI without decoding a lifecycle `Command`

#### Scenario: TUI shows an unavailable operation without a recovery claim
- **WHEN** the broker denies or cannot resolve a selected session
- **THEN** the TUI renders only the bounded unavailable state and does not offer a
  fabricated resume path
